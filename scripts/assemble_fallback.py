#!/usr/bin/env python3
"""Local fallback for Phase 6 when Higgsfield's explainer_video is unavailable.

Reproduces the same timing contract: every block is a fixed window (10s by
default), block i's voice take lands on clip i, short takes are centered,
slight overruns are sped up pitch-safely (atempo), and video is never
stretched (trimmed, or the last frame is held). Clip-native SFX is kept
under the voice. No subtitles are burned — that stays a server-side feature.

Usage:
  assemble_fallback.py --manifest run/manifest.json -o final/video.mp4
  assemble_fallback.py --clip a.mp4 --voice a.mp3 --clip b.mp4 --voice b.mp3 -o out.mp4

Requires ffmpeg and ffprobe on PATH.
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

MAX_SPEEDUP = 1.35  # beyond this the take reads as rushed; shorten the line instead


def probe(path: Path) -> dict:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration:stream=codec_type,width,height",
         "-of", "json", str(path)],
        check=True, capture_output=True, text=True,
    ).stdout
    data = json.loads(out)
    streams = data.get("streams", [])
    video = next((s for s in streams if s.get("codec_type") == "video"), {})
    return {
        "duration": float(data.get("format", {}).get("duration", 0.0)),
        "width": video.get("width"),
        "height": video.get("height"),
        "has_audio": any(s.get("codec_type") == "audio" for s in streams),
    }


def voice_filter(duration: float, window: float) -> tuple[str, list[str]]:
    """Audio filter that fits a take into the window, plus any warnings."""
    warnings: list[str] = []
    if duration <= window:
        delay_ms = int(round((window - duration) / 2 * 1000))
        if duration < window - 2.0:
            warnings.append(f"take is {duration:.1f}s; it will start {delay_ms / 1000:.1f}s late (reads as desync)")
        chain = f"adelay={delay_ms}|{delay_ms}"
    else:
        tempo = duration / window
        if tempo > MAX_SPEEDUP:
            warnings.append(f"take is {duration:.1f}s; needs {tempo:.2f}x speed-up, shorten the line and re-voice")
        chain = f"atempo={tempo:.4f}"
    return f"{chain},apad,atrim=0:{window}", warnings


def render_block(clip: Path, voice: Path, out: Path, window: float, size: tuple[int, int],
                 clip_audio_volume: float) -> list[str]:
    clip_info, voice_info = probe(clip), probe(voice)
    vf, warnings = voice_filter(voice_info["duration"], window)
    width, height = size
    hold = max(0.0, window - clip_info["duration"])
    video_chain = (
        f"[0:v]scale={width}:{height}:force_original_aspect_ratio=decrease,"
        f"pad={width}:{height}:(ow-iw)/2:(oh-ih)/2,setsar=1,fps=30,"
        f"tpad=stop_mode=clone:stop_duration={hold:.3f},trim=0:{window},setpts=PTS-STARTPTS[v]"
    )
    voice_chain = f"[1:a]aformat=sample_rates=48000:channel_layouts=stereo,{vf}[vo]"
    if clip_info["has_audio"] and clip_audio_volume > 0:
        bed = (f"[0:a]aformat=sample_rates=48000:channel_layouts=stereo,volume={clip_audio_volume},"
               f"apad,atrim=0:{window}[bed]")
        mix = "[vo][bed]amix=inputs=2:duration=first:normalize=0[a]"
        graph = ";".join([video_chain, voice_chain, bed, mix])
    else:
        graph = ";".join([video_chain, voice_chain.replace("[vo]", "[a]")])
    subprocess.run(
        ["ffmpeg", "-y", "-v", "error", "-i", str(clip), "-i", str(voice),
         "-filter_complex", graph, "-map", "[v]", "-map", "[a]",
         "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "veryfast", "-crf", "18",
         "-c:a", "aac", "-b:a", "192k", "-t", str(window), str(out)],
        check=True,
    )
    return warnings


def load_pairs(args: argparse.Namespace) -> list[tuple[Path, Path]]:
    if args.manifest:
        manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
        base = args.manifest.parent
        items = sorted(manifest["items"], key=lambda item: item["block"])
        return [(base / item["clip_file"], base / item["voice_file"]) for item in items]
    if len(args.clip) != len(args.voice):
        raise SystemExit("error: pass the same number of --clip and --voice files")
    return [(Path(c), Path(v)) for c, v in zip(args.clip, args.voice)]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--manifest", type=Path, help="run/manifest.json with items[].clip_file/voice_file")
    parser.add_argument("--clip", action="append", default=[], help="clip file, in block order")
    parser.add_argument("--voice", action="append", default=[], help="voice take, in block order")
    parser.add_argument("-o", "--output", type=Path, required=True)
    parser.add_argument("--window", type=float, default=10.0, help="seconds per block")
    parser.add_argument("--size", help="WIDTHxHEIGHT; default: the first clip's real size")
    parser.add_argument("--clip-audio-volume", type=float, default=0.35,
                        help="level of clip-native SFX under the voice (0 to drop)")
    args = parser.parse_args(argv)

    for tool in ("ffmpeg", "ffprobe"):
        if not shutil.which(tool):
            print(f"error: {tool} not found on PATH", file=sys.stderr)
            return 2
    pairs = load_pairs(args)
    if not pairs:
        print("error: no blocks to assemble", file=sys.stderr)
        return 2
    for clip, voice in pairs:
        for path in (clip, voice):
            if not path.exists():
                print(f"error: missing {path}", file=sys.stderr)
                return 2

    if args.size:
        width, height = (int(v) for v in args.size.lower().split("x"))
    else:
        first = probe(pairs[0][0])
        width, height = first["width"], first["height"]

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        parts: list[Path] = []
        for i, (clip, voice) in enumerate(pairs, start=1):
            part = Path(tmp) / f"block-{i:02d}.mp4"
            for warning in render_block(clip, voice, part, args.window, (width, height), args.clip_audio_volume):
                print(f"Block {i}: warn: {warning}")
            parts.append(part)
        listing = Path(tmp) / "concat.txt"
        listing.write_text("".join(f"file '{p}'\n" for p in parts), encoding="utf-8")
        subprocess.run(
            ["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", str(listing),
             "-c", "copy", "-movflags", "+faststart", str(args.output)],
            check=True,
        )
    total = probe(args.output)["duration"]
    print(f"wrote {args.output} ({len(pairs)} blocks, {total:.2f}s, {width}x{height})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
