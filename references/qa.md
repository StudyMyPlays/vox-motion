# QA & Failure Handling

## Gate before paid generation (Phases 4–5)

- [ ] `run/brief.md` has the topic, the angle and at least two independent
      sources per number.
- [ ] `python3 scripts/script_check.py run/script.md` passes: N blocks, each
      20–24 words, numbers spelled out, no stage directions.
- [ ] `python3 scripts/prompt_lint.py run/prompts.md --style mixed|diorama`
      passes: one prompt per block, and the STYLE, text-fence and no-speech
      lines are present.
- [ ] A one-line plan message is posted with the topic, angle, block count,
      voice and estimated credits (from `get_cost: true`).

## Gate before assembly (Phase 6)

- [ ] Every clip is terminal and on-style: not photoreal, not 3D, no
      garbled lettering.
- [ ] Every clip has the planned aspect ratio, and the clips' real
      `width`/`height` are recorded for the assembly call.
- [ ] Every voice take is 9.0–10.5s (`durationSec`).
- [ ] `run/manifest.json` maps block i → clip i and voice i, in order.

## Gate before delivery

- [ ] One assembled MP4, N × 10s long, with subtitles if they're on.
- [ ] The final message includes the video, a one-sentence topic and angle,
      the full script, and the Sources list.

## Failure handling

- **A clip drifts off-style.** Re-attach the key, tighten the STYLE and
  NEGATIVE lines, and rerun that block only. Two identical failures mean the
  prompt is wrong, not the seed.
- **A voice take runs over ~9.5s.** Shorten the line or raise
  `speech_rate`, and re-voice that block only.
- **`voice_id`/`voice_type` errors.** You skipped `list_voices`. Call it and
  reuse one exact pair everywhere.
- **Assembly rejects an id.** The job isn't terminal yet. Poll it, then
  retry assembly with all N items in order. Block N's audio always lands on
  clip N.
- **A video job's status is `failed` or `nsfw` with no error text.** This
  is moderation, not bad luck. Check the moderation map in
  `diorama-doc.md`:
  - Named politicians and close-up recognizable faces fail on seedance.
    Route those blocks to gemini_omni, or drop to mid-shot descriptions.
  - "Mushroom cloud" and similar terms get flagged nsfw. Swap the image and
    keep the idea.
- **A `preset_recommendation` notice intercepts a submission.** Decline it.
  Resubmit with `declined_preset_id` from `retry_literal_with`, and never
  accept a photoreal or 3D preset.
- **`gemini_omni` is rejected.** Confirm the current video model id with
  `models_explore(type: 'video')`. Never silently switch to a photoreal
  model.
- **The user wants isolated deliverables** (an SFX-only track, single clips,
  stills). Raw clips have no voice, because narration exists only in the
  assembly. Extracting per-clip audio or frames locally with ffmpeg gives
  clean voiceless assets.
- **`explainer_video` is unavailable.** Download the clips and takes, then
  run `scripts/assemble_fallback.py`. It reproduces the same fixed 10s
  windows locally, but has no burned subtitles.
