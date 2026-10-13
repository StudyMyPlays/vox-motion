---
name: vox-motion
description: >
  Produce a complete narrated motion-graphics explainer video end-to-end with
  Higgsfield MCP: trend/topic research, fact-checked script, a locked style
  key, animated clips, documentary voiceover, and one final assembled MP4.
  Two house styles: Vox-style Mixed Media collage (flat editorial, burned
  subtitles) and cinematic paper-diorama documentary (sepia newsprint worlds,
  censor-bar cutouts, letterpress props, fake-oner FPV energy). Use this
  skill whenever the user asks for a "Vox-style video", "motion graphics
  explainer", "animated explainer", "data-driven video", "cinematic paper /
  newspaper collage documentary", "make a video about X", "make a video
  about something trending/viral", a video "like the AI bubble reference",
  or just "run the vox pipeline" — even when no topic is given (the skill
  finds a trending topic itself). Also use it for faceless narrated
  shorts/YouTube videos on geopolitics, money, or power via Higgsfield. Not
  for interactive web animation, live-action editing, or single stills.
---

# Vox Motion

Turn one request — a topic, or nothing at all — into a finished Vox-style
explainer video: bold editorial collage visuals, a documentary narrator, tight
fact-driven writing, one final MP4. The pipeline runs on the Higgsfield MCP
`video-explainer` workflow with the **Mixed Media** preset as the default look.

**The Vox look, in one line:** archival photo cutouts with paper edges drifting
over flat color fields and textured paper, halftone accents, hand-drawn circles
and underlines, abstract growing charts and maps, snappy camera pushes — a
motion-designed magazine spread, never a filmed scene.

**Two house styles** — pick per brief, each with its own reference file:

- **Mixed Media collage** (default; [references/vox-prompts.md](references/vox-prompts.md))
  — flat, bright, playful-editorial; no text in clips, subtitles burned at
  assembly. Best for data stories, "why X" explainers, shorts.
- **Paper-diorama documentary** ([references/diorama-doc.md](references/diorama-doc.md))
  — cinematic sepia newsprint dioramas, censor-bar cutout figures, one
  burnt-orange accent, letterpress text ON props, fake-oner FPV camera. Best
  for geopolitics, money, power, anything the user wants "cinematic" or
  high-energy. Comes with a ready style key and a registry of reusable prop
  assets.

Local helpers need only Python 3.10+ (and ffmpeg for the fallback assembler):

```bash
VOX_MOTION="<absolute directory containing this SKILL.md>"
```

## Operating mode

This skill is built to run **hands-off**. The user delegates everything:
topic discovery, script, voice, assets, assembly. That means:

- If the user gave a topic, angle, duration, or voice preference — honor it.
  Everything they didn't specify, decide yourself using the defaults below.
- Right before submitting the first **paid** generation, post one short plan
  message (topic, angle, block count, voice, estimated credits) so the user
  can interrupt — then **proceed immediately without waiting for approval**,
  unless the user asked to be consulted.
- Never stop mid-pipeline to ask a question you can answer with a default.
  Delivering loose clips instead of an assembled MP4 is a failure.

Deviation note: the underlying Higgsfield `video-explainer` workflow asks the
user to pick style and voice interactively. This skill intentionally
pre-answers those questions (Mixed Media preset, auto-picked documentary
voice) because the user has delegated the whole run. Only show the preset
gallery / voice picker if the user explicitly asks to choose.

## Defaults

| Setting    | Default                                | Override when… |
|------------|----------------------------------------|----------------|
| Style      | Mixed Media preset, id `80e4dd7b-cd65-42d4-b191-b58d62558602` | user names another preset, asks for cinematic/diorama, or supplies reference images |
| Aspect     | 9:16 vertical (shorts/TikTok/Reels) — pass `aspect_ratio: "9:16"` explicitly on every clip; the style key alone does NOT set framing (verified: `gemini_omni` defaults to 16:9 regardless of a vertical key) | user says YouTube/landscape → 16:9 |
| Duration   | 1 minute → N = 6 blocks (N = minutes × 6, each block = one 10s clip) | user gives a length (1–10 min) |
| Character  | Faceless (no mascot)                   | user asks for a host/mascot |
| Language   | English narration                      | user asks otherwise (prompts stay English regardless) |
| Voice      | Auto-pick a deep, measured documentary narrator from `list_voices` | user wants to choose → show the picker and wait |
| Subtitles  | ON, font `anton` (bold condensed — fits the editorial look). Costs 0.05 credit per voiced block — mention it in the plan message. | user says no subtitles |

## Four sources of truth

Each fact lives in exactly one file under `run/`; everything else points to it:

1. `run/brief.md` — topic, angle, style, aspect, N, and the **Sources** list.
2. `run/script.md` — the N narration blocks (`Block 1 …`), nothing else.
3. `run/prompts.md` — the N block prompts plus any recurring subject profiles.
4. `run/manifest.json` — style key, voice pair, and every job id per block
   (shape: [assets/run-manifest.example.json](assets/run-manifest.example.json)).

## Pipeline

| Phase | What happens | Tools |
|---|---|---|
| T Topic | use the given topic, or research what's trending and pick one | WebSearch / WebFetch |
| R Research | gather verified facts, numbers, names; keep a Sources list | WebSearch / WebFetch |
| 1 Style key | resolve the Mixed Media preset into a style-reference media_id (free) | `resolve_explainer_preset` (or `generate_image` for 16:9) |
| 2 Script | N narration blocks, Vox formula, ~20–24 words each | reasoning (free) + `script_check.py` |
| 3 Block prompts | N labeled video prompts in the house visual language | reasoning (free) + `prompt_lint.py` |
| 4 Clips | N × 10s clips, style key attached to every one | `generate_video` (`gemini_omni` / `seedance_2_0`) |
| 5 Voice | one narrator, N takes, same voice_id on every block | `list_voices` + `generate_audio` (`seed_audio`) |
| 6 Assemble | stitch clips + takes into one MP4, burn subtitles | `explainer_video` |

Phases T, R, 2, 3 are free; 1 (preset branch), 4, 5 cost credits.

**Job model:** every `generate_*` call submits an async job and returns a job
id. Poll with `job_status { jobId, sync: true }` where the server exposes it;
if not, check completion via the tool-result/notification stream or
`show_generations`. A completed job id is reused directly as a
`medias[].value` on later generations and as `video`/`audio` in Phase 6 —
you rarely need the raw URLs. Use `get_cost: true` on one `generate_video`
call before Phase 4 to estimate total spend for the plan message.

## Main flow

### T. Topic

**Topic given** → use it, go to Phase R.

**No topic** → find one that's popular *right now*:

1. WebSearch 2–3 angles: `trending topics this week <current month year>`,
   `most searched questions this week`, plus one vertical the user cares
   about if known (tech, money, science, sports…).
2. A good Vox-able topic has: a **"why/how" question** at its core, at least
   one **surprising number or reversal**, strong **visual potential** (maps,
   charts, objects, archival imagery), and broad appeal. "Why X is suddenly
   everywhere", "The real reason X costs so much", "How X quietly changed Y"
   are the shape you want.
3. Avoid: breaking tragedies and active disasters, raw celebrity gossip with
   no data angle, anything you can't verify with two independent sources.
4. Pick the strongest candidate yourself and state it in the plan message
   (with one runner-up in case the user swaps).

### R. Research

Never script from memory. WebSearch the chosen topic, fetch the 2–3 best
sources, and collect: the hook stat, 3–5 concrete facts/numbers/dates, the
counterintuitive turn, and who/what/where specifics that make blocks vivid.
Cross-check every number against a second source. Keep a short **Sources**
list in `run/brief.md` and include it in the final delivery message. No
fabricated quotes, no invented numbers — a vague true line beats a specific
false one.

### 1. Style key

**Mixed Media, 9:16 (default):** call `resolve_explainer_preset` with preset
id `80e4dd7b-cd65-42d4-b191-b58d62558602`. The returned `media_id` IS the
style key — attach it as `medias: [{ value: <media_id>, role: "image" }]` on
**every** clip in Phase 4. This branch is free.

**Mixed Media, 16:9:** the preset key would force vertical framing, so
generate your own landscape key with `generate_image`, model
`nano_banana_pro`, `aspect_ratio: "16:9"`, using the STYLE KEY prompt in
[references/vox-prompts.md](references/vox-prompts.md). Poll to completion;
that job id becomes the style key. (Costs one image generation.)

**Diorama:** reuse the ready key and prop registry in
[references/diorama-doc.md](references/diorama-doc.md); regenerate only if
the user asks.

### 2. Script

Design the through-line object and question hook first, then write the N
blocks with the Vox formula (cold open → stakes → evidence → turn → kicker).
Rules, tone and word budget: [references/story-engine.md](references/story-engine.md).
Start from [assets/script-template.md](assets/script-template.md), then:

```bash
python3 "$VOX_MOTION/scripts/script_check.py" run/script.md --blocks N
```

Fix every error before moving on; warnings are lines likely to land outside
the 9.0–10.5s take window.

### 3. Block prompts

One prompt per block, translating that block's line into the house style:
Mixed Media → labeled template + collage style rules in
[references/vox-prompts.md](references/vox-prompts.md); diorama → fake-oner
shape in [references/diorama-doc.md](references/diorama-doc.md). For
`seedance_2_0` prompts, also follow
[references/seedance-prompting.md](references/seedance-prompting.md)
(reference binding, sound-design brackets, checklist).

```bash
python3 "$VOX_MOTION/scripts/prompt_lint.py" run/prompts.md --style mixed   # or diorama
```

### 4. Clips

**Engine choice:**

- `gemini_omni` — 30 cr/clip, fast, workhorse for Mixed Media collage. Also
  the only engine that renders recognizable politician likenesses from
  descriptions (see moderation map in `references/diorama-doc.md`).
- `seedance_2_0` — 45 cr (720p std) / 90 cr (1080p), ref-grade cinematic:
  executes in-prompt cuts ("Shot 1 … Cut to shot 2"), real speed ramps and
  FPV moves, native SFX sound design (`generate_audio: true`) that survives
  under the voiceover. Default for the diorama style and any "make it
  impressive" brief; call template in `references/diorama-doc.md`.

Submit N `generate_video` jobs — style key on every single one (plus any
reusable prop assets as extra `image_references`):

```
generate_video
  model: "gemini_omni"
  prompt: <Block N video prompt>
  duration: 10
  resolution: "720p"
  aspect_ratio: "9:16"        # or "16:9" — always explicit
  medias: [ { value: "<style key media_id or job id>", role: "image" } ]
```

Pass `aspect_ratio` explicitly ("9:16" or "16:9") — despite what the base
workflow claims, the key image does not reliably set framing; a real run with
a 9:16 key still produced 16:9 clips. Also expect the server to intercept the
first submission with a `preset_recommendation` notice (it pattern-matches
collage prompts to its "3D RENDER" preset): decline it by resubmitting with
`declined_preset_id` from the notice's `retry_literal_with` — never accept a
photoreal/3D preset. Submit in batches, record every job id against its block
number in `run/manifest.json`, re-submit only failed blocks. If a clip
renders photoreal/live-action, strengthen the STYLE and NEGATIVE lines and
re-run that block — two identical failures means the prompt is wrong, not
the seed.

### 5. Voiceover

Pick one documentary narrator with `list_voices`, voice every block with the
same `voice_id`/`voice_type` via `generate_audio` (`seed_audio`), then
**verify every take's real `durationSec` is 9.0–10.5s** before assembling.
Call shape, pacing traps and fixes: [references/voiceover.md](references/voiceover.md).

### 6. Assemble (automatic, mandatory)

The moment all clips and takes are done, assemble — in the same run, without
being asked. First read the finished clips' actual `width`/`height` from
their job records and pass THOSE — if the clips rendered in a different
aspect than planned, the assembly must match the clips, not the plan.

```
explainer_video
  params:
    width: 720            # 1280 for 16:9 — always the clips' real size
    height: 1280          # 720 for 16:9
    subtitles: { font: "anton" }   # omit if user said subtitles off
    items:
      - { video: "<clip 1 job id>", audio: "<voice 1 job id>" }
      …
      - { video: "<clip N job id>", audio: "<voice N job id>" }
```

Blocks are fixed 10s windows: short takes are centered, slight overruns are
sped up pitch-safely, video is never stretched — total = N × 10s exact.
Poll the returned job to completion, then present the final MP4 with
`job_display`. If `explainer_video` is unavailable, use
`scripts/assemble_fallback.py` (see [references/qa.md](references/qa.md)).

## QA and failure handling

Gates before paid generation, before assembly and before delivery, plus every
known failure and its fix (off-style clips, long takes, moderation, preset
interceptions, assembly rejects): [references/qa.md](references/qa.md).

## Delivery

Final message: the video, the topic + angle in one sentence, the full script
(so the user can reuse it), and the Sources list. Keep `run/` (brief, script,
prompts, manifest) so any block can be re-generated later. Then offer — don't
run unasked — the `youtube-seo` skill for titles/description/tags if the
video is headed to YouTube.
