# Voiceover (Phase 5)

## Pick the voice once

1. Call `list_voices`. Auto-pick a **deep, measured, documentary** narrator,
   with calm authority rather than ad-read energy. Note its exact `voice_id`
   and `voice_type` in `run/manifest.json`. Show the picker and wait only if
   the user asked to choose.
2. Make one `generate_audio` call per block, with the same voice every time:

```
generate_audio
  model: "seed_audio"
  voice_type: "<preset|element>"
  voice_id: "<from list_voices>"
  prompt: "<Block N line, plain text>"
```

If a take runs long, you have two levers: raise `speech_rate` (-50..100) a
notch, or shorten the line and re-voice. Record each take's job id against
its block.

## Verify every take's real duration before assembling

Read `durationSec` from the completed job (`show_generations`). Target
**9.0–10.5s** per take.

- The assembler **centers short takes**. A 7s take starts about 1.5s late,
  which reads as desync.
- It **speed-compresses long takes**. A 13s take gets squeezed by 30%,
  which reads as rushed.

TTS pacing is wildly unpredictable. Narrator voices pause about 0.7s at
every period. Choppy, name-heavy lines read at about 1.8 words/s, while one
flowing comma-joined sentence reads at about 2.5 words/s. The same word
count can differ by 4+ seconds.

- Prefer single flowing sentences.
- Expect 1–2 rounds of re-voicing, and keep the best take per block.
- A slight overrun beats a late start.

`scripts/script_check.py` estimates each block at both speeds before you
spend credits. Treat a block that can land outside 9.0–10.5s at either speed
as the first one to rewrite.
