<!-- TODO: add assets/readme/hero image and a demo MP4 once a showcase run exists. -->

# Vox Motion

Vox Motion is an agent skill for **narrated Vox-style explainer videos**.
Archival photo cutouts drift over flat color fields and textured paper.
Halftone accents, hand-drawn circles and underlines, and growing charts and
maps keep the frame moving, while a calm documentary narrator carries the
story. Each run produces one finished MP4.

Tell the agent a topic, or nothing at all. It finds the story, checks the
facts, writes the script, generates every clip and voice take through the
Higgsfield MCP, and assembles the final video.

## Install

Give your agent the repository URL:

```text
Install the Skill at https://github.com/StudyMyPlays/vox-motion.
```

Or install it from the command line, then have your agent reload its Skills:

```bash
npx skills add StudyMyPlays/vox-motion
```

Generation runs on the **Higgsfield MCP**, so connect it to your agent
first. The local helper scripts need only Python 3.10+, plus ffmpeg for the
fallback assembler.

## Scope

Vox Motion is for **faceless, narrated explainers** built from motion-graphic
collage:

- "Why X" data stories
- Money, power and geopolitics pieces
- Trend breakdowns
- Shorts, Reels and YouTube videos

Out of scope:

- Interactive web animation (use something like
  [oil-motion](https://github.com/oil-oil/oil-motion) for that)
- Editing live-action footage
- On-camera presenters with lip-sync
- Single illustrations

## Two house styles

| Style | Looks like | Best for | Text in clips |
|---|---|---|---|
| **Mixed Media collage** (default) | Flat, bright editorial collage, halftone cutouts, marker annotations, abstract charts and maps | Data stories, "why X" explainers, shorts | None. Subtitles are burned in at assembly |
| **Paper-diorama documentary** | Sepia newsprint dioramas, censor-bar cutout figures, one burnt-orange accent, tungsten light, fake-oner FPV camera | Geopolitics, money, power, anything "cinematic" | One letterpress label per scene, on a prop |

The diorama style ships with a ready style key and a registry of reusable
prop assets, so objects stay consistent from clip to clip.

## How it works

```
Topic (given, or found trending)
  ↓
Research: verified facts, every number checked against a second source
  ↓
Style key: one locked reference image attached to every clip
  ↓
Script: N blocks × ~22 words (cold open → stakes → evidence → turn → kicker)
  ↓
Block prompts: one per 10s clip, in the house visual language
  ↓
Clips (gemini_omni / seedance_2_0) + one narrator voicing every block
  ↓
Assembly: fixed 10s windows, subtitles burned in → one MP4
```

Every block is exactly one 10-second clip plus one voice take, so a 1-minute
video is 6 blocks, and the total length is always N × 10s. Short takes are
centered, slight overruns are sped up pitch-safely, and video is never
stretched.

Three ideas set it apart from a slideshow of pretty frames:

- **A through-line object.** One physical metaphor, such as a burning fuse,
  travels through every block and pays off in the finale.
- **A question hook answered last.** The question sits on a prop in block 1,
  and the kicker answers it.
- **Fake-oner seams.** In the diorama style, each clip starts and ends in
  motion blur, so the cuts read as one unbroken shot.

## Quick start

No topic at all:

```text
Run the vox pipeline. Find something trending and make me a 1-minute short.
```

A topic and a platform:

```text
Use vox-motion to make a 2-minute YouTube explainer about why container
shipping got so cheap.
```

The cinematic style:

```text
Use vox-motion, diorama style, high energy: why do nuclear treaties keep expiring?
```

The skill runs hands-off. Right before the first paid generation, it posts
one short plan (topic, angle, block count, voice and estimated credits) and
then keeps going unless you interrupt.

## What the agent decides

Anything you don't specify falls back to a default:

| Setting | Default |
|---|---|
| Style | Mixed Media preset |
| Aspect | 9:16 vertical; 16:9 if you say YouTube or landscape |
| Length | 1 minute, which is 6 blocks |
| Voice | A deep, measured documentary narrator |
| Subtitles | On, in the bold condensed `anton` font |
| Character | Faceless |

## Deliverables

- The final assembled MP4.
- The topic and angle in one sentence.
- The full script, so you can reuse it.
- A Sources list for every fact.
- The `run/` folder:
  - `brief.md`
  - `script.md`
  - `prompts.md`
  - `manifest.json`, with every job id, so any single block can be
    regenerated later.

## Quality checks

Before spending credits, the agent runs two local checks:

- `scripts/script_check.py` checks block count and word budget, flags digits
  that should be spelled out and any stage directions, and estimates how
  long each line takes to read.
- `scripts/prompt_lint.py` checks the required labeled lines, the text fence,
  the no-speech rule and known moderation triggers.

Before assembling, it checks:

- Every clip stays on-style: no photoreal or 3D frames, and no garbled
  lettering.
- Clips match the planned aspect ratio.
- Every voice take lands in the 9.0–10.5s window.
- Block *i*'s audio lands on clip *i*.

Known failures and their fixes are documented in
[`references/qa.md`](references/qa.md). They include moderation flags,
preset interceptions, long takes and assembly rejects.

## First run

1. Connect the Higgsfield MCP to your agent.
2. Ask for a video.

The research, script and prompt phases are free. The style key (16:9 only),
clips and voice takes cost Higgsfield credits. The plan message shows the
estimate before anything is spent.

If `explainer_video` is unavailable, `scripts/assemble_fallback.py` rebuilds
the same 10s-window assembly locally with ffmpeg. It does not burn in
subtitles.

## Technical docs

You never need to run anything by hand. The details live in:

- [`SKILL.md`](SKILL.md): the full pipeline the agent follows.
- [`references/vox-prompts.md`](references/vox-prompts.md): the Mixed Media
  vocabulary, block template, collage style rules and worked examples.
- [`references/diorama-doc.md`](references/diorama-doc.md): the diorama
  style key, prop registry, fake-oner prompt shape and moderation map.
- [`references/story-engine.md`](references/story-engine.md): the story
  engine and the Vox script formula.
- [`references/voiceover.md`](references/voiceover.md): narrator choice and
  take timing.
- [`references/seedance-prompting.md`](references/seedance-prompting.md):
  condensed Seedance prompt rules for clip prompts.
- [`references/qa.md`](references/qa.md): gates and failure handling.
- [`assets/`](assets/): the script and prompt templates, and an example
  run manifest.

Run the tests with `python3 -m unittest discover -s tests`.

## License

[MIT](LICENSE)
