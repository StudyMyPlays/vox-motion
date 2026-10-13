#!/usr/bin/env python3
"""Lint Vox block prompts before submitting paid clip generations.

Each prompt starts with a ``Block N`` line (inside or outside a code fence)
and runs until the next one. Rules follow references/vox-prompts.md
(``--style mixed``) and references/diorama-doc.md (``--style diorama``).

Errors (exit 1) are things that reliably waste credits: missing labeled
lines, a missing text fence or no-speech line, dialogue/subtitle brackets,
known moderation triggers. Warnings flag likely drift.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

BLOCK_RE = re.compile(r"^\s*(?:[#>*_\-\s]*)Block\s+(\d+)\s*\**\s*$", re.I)
COMMENT_RE = re.compile(r"<!--.*?-->", re.S)

MIXED_LABELS = ("STYLE REFERENCE:", "SCENE:", "MOTION:", "AUDIO:", "NEGATIVE:")
MIXED_NEGATIVE_TERMS = ("readable text", "letters", "words", "numbers", "captions",
                        "subtitles", "photorealism", "live-action", "3d render", "lip-sync")
DIORAMA_STYLE_MARKERS = ("paper diorama", "non-photorealistic")
MODERATION_ERRORS = {
    "mushroom cloud": "flags nsfw; swap the image, keep the idea (e.g. an hourglass)",
}
PARAM_WORDS = re.compile(r"\b(?:aspect ratio|16:9|9:16|1:1|\d+\s*seconds? long|resolution|720p|1080p)\b", re.I)
TEXT_ASKS = re.compile(r"\b(?:headline|caption|title card|text reading|label reading|words? reading|spelled|lettering that says)\b", re.I)
SPEECH_ASKS = re.compile(r"\b(?:says|speaks|talks|lip-?sync(?:s|ing)?|dialogue|narrates)\b", re.I)
QUOTED = re.compile(r"\"([^\"]+)\"|“([^”]+)”")


@dataclass
class Prompt:
    number: int
    body: str = ""
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


def parse_prompts(source: str) -> list[Prompt]:
    source = COMMENT_RE.sub("", source)
    prompts: list[Prompt] = []
    for raw in source.splitlines():
        line = raw.rstrip()
        match = BLOCK_RE.match(line)
        if match:
            prompts.append(Prompt(int(match.group(1))))
            continue
        if line.strip().startswith("```") or not prompts:
            continue
        if line.lstrip().startswith("#"):
            continue
        prompts[-1].body += line.strip() + "\n"
    return prompts


def _label_value(body: str, label: str, labels: tuple[str, ...]) -> str:
    """Text after ``label`` up to the next known label."""
    start = body.find(label)
    if start < 0:
        return ""
    start += len(label)
    ends = [body.find(other, start) for other in labels if other != label]
    ends = [e for e in ends if e >= 0]
    return body[start:min(ends) if ends else len(body)].strip()


def _common(prompt: Prompt) -> None:
    flat = " ".join(prompt.body.split())
    low = flat.lower()
    if not flat:
        prompt.errors.append("empty prompt")
        return
    for term, why in MODERATION_ERRORS.items():
        if term in low:
            prompt.errors.append(f"'{term}' {why}")
    if "{" in flat or "}" in flat:
        prompt.errors.append("dialogue braces { } found; clips carry no speech")
    if "【" in flat or "】" in flat:
        prompt.errors.append("subtitle brackets found; captions are burned at assembly")
    if PARAM_WORDS.search(flat):
        prompt.warnings.append("generation parameters (aspect/duration/resolution) belong on the call, not in the prompt")


def lint_mixed(prompt: Prompt) -> None:
    body = prompt.body
    for label in MIXED_LABELS:
        if label not in body:
            prompt.errors.append(f"missing '{label}' line")
    style = _label_value(body, "STYLE REFERENCE:", MIXED_LABELS).lower()
    if style and "non-photorealistic" not in style:
        prompt.errors.append("STYLE REFERENCE must include the house STYLE tokens (non-photorealistic, no live-action)")
    audio = _label_value(body, "AUDIO:", MIXED_LABELS).lower()
    if audio and not ("no voice" in audio or "no narration" in audio):
        prompt.errors.append("AUDIO must end with 'no voice, no narration'")
    negative = " ".join(_label_value(body, "NEGATIVE:", MIXED_LABELS).lower().split())
    missing = [t for t in MIXED_NEGATIVE_TERMS if t not in negative]
    if negative and missing:
        prompt.errors.append(f"NEGATIVE line is not the fixed list; missing: {', '.join(missing)}")
    visual = " ".join((_label_value(body, "SCENE:", MIXED_LABELS) + " "
                       + _label_value(body, "MOTION:", MIXED_LABELS)).split())
    if TEXT_ASKS.search(visual):
        prompt.errors.append("SCENE/MOTION asks for readable text; use abstract bars, circles, underlines instead")
    if QUOTED.search(visual):
        prompt.warnings.append("quoted string in SCENE/MOTION may render as garbled lettering")
    if SPEECH_ASKS.search(visual):
        prompt.warnings.append("SCENE/MOTION mentions speech; no one speaks on screen")


def lint_diorama(prompt: Prompt) -> None:
    flat = " ".join(prompt.body.split())
    low = flat.lower()
    for marker in DIORAMA_STYLE_MARKERS:
        if marker not in low:
            prompt.errors.append(f"missing STYLE token '{marker}'; open with the diorama STYLE tokens")
    if "no speech" not in low:
        prompt.errors.append("missing 'No speech.' after the sound design")
    fence = re.search(r"no text anywhere except\s*[\"“]([^\"”]+)[\"”]", flat, re.I)
    if not fence and "no text anywhere" not in low:
        prompt.errors.append("missing text fence: No text anywhere except \"<LABEL>\"")
    allowed = {fence.group(1).strip().lower()} if fence else set()
    labels = {(a or b).strip() for a, b in QUOTED.findall(flat)}
    stray = sorted(l for l in labels if l.lower() not in allowed)
    if stray:
        prompt.errors.append(f"quoted text not covered by the fence: {stray}; one label per scene")
    for label in labels:
        if len(label.split()) > 3:
            prompt.warnings.append(f"label '{label}' is long; keep props to 1–2 words or a number")
    if "fpv" not in low and "continuous" not in low:
        prompt.warnings.append("no continuous/FPV camera move; fake-oner seams will show")
    if "sound design" not in low:
        prompt.warnings.append("no 'Sound design:' line; seedance native SFX is part of the look")


def lint(source: str, style: str, expected_blocks: int | None = None) -> tuple[list[Prompt], list[str]]:
    prompts = parse_prompts(source)
    problems: list[str] = []
    if not prompts:
        return prompts, ["no 'Block N' prompts found"]
    numbers = [p.number for p in prompts]
    if numbers != list(range(1, len(prompts) + 1)):
        problems.append(f"prompts must be numbered 1..N in order, found {numbers}")
    if expected_blocks is not None and len(prompts) != expected_blocks:
        problems.append(f"expected {expected_blocks} prompts, found {len(prompts)}")
    for p in prompts:
        _common(p)
        (lint_mixed if style == "mixed" else lint_diorama)(p)
    return prompts, problems


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("prompts", type=Path, help="run/prompts.md")
    parser.add_argument("--style", choices=("mixed", "diorama"), default="mixed")
    parser.add_argument("--blocks", type=int, help="expected block count N")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    prompts, problems = lint(args.prompts.read_text(encoding="utf-8"), args.style, args.blocks)
    error_count = len(problems) + sum(len(p.errors) for p in prompts)
    if args.json:
        print(json.dumps({"ok": error_count == 0, "problems": problems,
                          "prompts": [{"block": p.number, "errors": p.errors, "warnings": p.warnings}
                                      for p in prompts]}, indent=2))
    else:
        for p in prompts:
            status = "ERROR" if p.errors else ("warn" if p.warnings else "ok")
            print(f"Block {p.number:>2}  {status}")
            for msg in p.errors:
                print(f"    error: {msg}")
            for msg in p.warnings:
                print(f"    warn:  {msg}")
        for msg in problems:
            print(f"error: {msg}")
        print(f"{len(prompts)} prompt(s), {error_count} error(s)")
    return 1 if error_count else 0


if __name__ == "__main__":
    sys.exit(main())
