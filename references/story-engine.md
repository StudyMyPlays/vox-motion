# Story Engine & Script Formula

Read this before Phase 2 (script) and Phase 3 (block prompts). It decides
whether the video lands or reads as a slideshow.

## Story engine (what separates a banger from postcards)

A sequence of pretty, disconnected scenes reads as a museum slideshow. These
are the things that make the reference-grade videos hit:

- **One through-line object.** A single physical metaphor travels through
  every block and escalates: a burning fuse crossing all scenes, or a
  balloon being pumped toward a needle. The viewer holds it the whole
  runtime, and the finale pays it off. Design this object before writing any
  block.
- **A question hook, answered last.** Put the question on a prop ("WHO
  PAYS?", "WHO BLINKS?") in block 1 or the finale. The narration withholds
  the answer until the kicker.
- **Fake-oner.** Write every clip as one continuous FPV camera move that
  begins and ends in full motion blur (a dive, whip, flare or fall). Hard
  cuts between blocks then read as one unbroken shot. Blocks generate in
  parallel and need no frame-matching.
- **An impact every ~3 seconds** (a slam, stamp, shockwave or snap) and at
  least one speed ramp per block, going from a slow-mo beat into a whip.
  Alternate extreme macro and wide diorama, and whiplash the scale: a giant
  face, then ant-sized figures, then a colossal prop.
- **One reveal shot** the whole video is remembered by. For example, a crowd
  arranged into a meaningful silhouette, or a reveal that is only visible
  when the camera cranes up.

The fake-oner and impact rules are written for the diorama style. Mixed
Media keeps the through-line object and the question hook, but swaps FPV
energy for snappy collage motion (see `vox-prompts.md`).

## Script (Vox formula)

Write N blocks, labeled `Block 1 … Block N`, one per 10s clip. Each block
is **~20–24 words**, about 8–9s spoken. The hard ceiling is about 9.5s: a
slight overrun gets a pitch-safe speed-up at assembly, and a big one needs a
shorter line. Use plain spoken text only, with no stage directions and no
parentheticals. Spell numbers out ("seventy percent", "twenty twenty-four").

Structure the N blocks like a Vox piece:

- **Block 1: cold open.** State the most surprising fact or question flat.
  No greeting, no "in this video".
- **Block 2: stakes.** Why this is weird, or why it matters to the viewer.
- **Middle blocks: evidence.** One idea per block, each anchored to a
  concrete number, date, place or comparison from Phase R. Escalate.
- **Block N−1: the turn.** The counterintuitive reveal, the "but here's the
  thing".
- **Block N: resolution and kicker.** Land the answer, and end on a line
  that reframes the opening fact.

Tone: curious, precise, a little wry. Use short declarative sentences. The
narrator explains and never hypes.

For TTS pacing, prefer one flowing, comma-joined sentence over several
choppy ones. See `voiceover.md` for why. Start from
[`assets/script-template.md`](../assets/script-template.md) and run
`scripts/script_check.py` on the result before any paid step.

## Block prompts (Phase 3)

Write N video prompts, one per block. Each one visually translates its
narration line into the house style. Use the labeled template in
`vox-prompts.md` (Mixed Media) or the fake-oner shape in `diorama-doc.md`.
Two rules are easy to forget:

- **No readable text anywhere in Mixed Media clips.** AI-generated lettering
  garbles, so typography beats become abstract highlight bars, redaction
  blocks, circles and underlines. Real captions are burned in server-side
  in Phase 6. The diorama style allows exactly one short letterpress label
  per scene, fenced in the negative.
- **No one speaks on screen.** The `AUDIO:` line is ambient sound, effects
  or music only. Narration is added per block at assembly.

Run `scripts/prompt_lint.py` on `run/prompts.md` before Phase 4.
