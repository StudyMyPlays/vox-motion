# Seedance Prompting (condensed for Vox clips)

Read this when writing Phase 4 clip prompts for the `seedance_2_0` engine,
which is the default for the diorama style and for any "make it impressive"
brief. It is condensed from the official **Dreamina Seedance 2.5 Prompt
Guide** (ByteDance, 31 July 2026; assembled by
[@twoclipping](https://x.com/twoclipping)). It keeps only the parts that
matter for narrated collage explainers. The guide's edit, extend, storyboard,
blockout and one-click sections were dropped: this pipeline generates every
block fresh.

Seedance is unusually literal. It does what you ask, but only if you say
which reference is which, what must not change, and how the frame should look
when each beat ends. Most bad output comes from an underspecified prompt, not
from the model.

**Higgsfield note.** Dreamina's `@Image 1` / `@Video 1` handles map to the
`medias` you attach on `generate_video`. Through Higgsfield, name each
attachment by what it is, for example "the attached style key" or "the paper
missile from the reference image" (see `diorama-doc.md`). Apply the same
binding and exclusion rules below. Aspect ratio and duration are call
parameters and never go in the prompt.

## Rules for every Vox clip

**The core formula.** Only the first part is required. Every part you drop
becomes a decision the model makes without you.

```
Subject + Action/Event + Scene & Environment + Visual Style + Camera + Audio
```

In this pipeline:

- **Visual style** is the house STYLE tokens, verbatim
  (`vox-prompts.md` or `diorama-doc.md`).
- **Audio** is diegetic sound design only. Narration is added at assembly, so
  clips never contain dialogue or subtitles.

**Bind every reference individually.** The most common failure is writing
"the references define the three leaders". That never says which image is
which leader. Write one line per reference instead:

```
<Leader A> corresponds to the first reference image. Use only the
appearance, red tie and suit.
```

**Always write exclusions.** If a reference contains a background, a person,
or a composition you don't want carried over, say so. For example: `Do not
use the image background.` `Do not use the people in the image.`

**Write mappings in the prompt, not in the image.** Text labels inside a
reference are not read as instructions.

**Style isn't a mood word.** "Cinematic" leaves the model free. "Warm
tungsten light, macro tilt-shift, film grain, distressed letterpress" does
not.

**Never put generation parameters in the prompt.** Aspect ratio, duration
and resolution go on the call.

## Text to video

| Element | What it carries |
| --- | --- |
| Subject + action | Who or what is doing what. The foundation. |
| Scene and environment | Location, spatial relationships, background state. |
| Visual style | Lighting, colour, materials, texture, mood. Use the STYLE tokens. |
| Camera movement / cut | Shot size, angle, movement, focus subject, transitions. |
| Audio | Ambience, sound effects, music. No speech in this pipeline. |

```
<Subject> performs <primary action or event> in <scene and environment>.
The visuals feature <visual style>.
Use <shot size, camera angle, camera movement, or cuts>.
Audio includes <ambience, sound effects, or music>.
```

A diorama-style example:

```
A single burnt-orange paper fuse burns across an aged sepia newsprint
canyon, its spark racing past monochrome cutout figures with black censor
bars over their eyes.

Cinematic vintage paper diorama, distressed letterpress, warm tungsten
light, macro tilt-shift shallow depth of field, film grain.

Begin on an extreme macro of the spark, speed-ramp into a low FPV chase
along the fuse, then whip up into a wide overhead of the whole canyon.

<Fuse crackle> <Paper wind rushing past the lens> (Low sub-bass drone).
No speech.
```

## Reference roles

After attaching references, state exactly what each one contributes, and
what it must not contribute.

```
The style key defines <surface, palette, print texture, lighting>.
Do not use its composition or any figures in it.
The <prop> from the reference image defines its shape, material and colour.
Do not use the image background.
<Subject> completes <primary action> in <scene>.
```

**Several views of one object.** Say so explicitly, or you get several
objects:

```
The two reference images show the front and side of the same paper missile.
The output must contain only one missile throughout.
```

**What breaks it:**

1. Missing exclusions. If a reference has a background or a person you
   don't want carried over, say so.
2. Mappings that live only in image labels. Write them in the prompt.
3. Several views of one object without a count. Four views become four
   objects.

## Multi-reference (style key + props + cutouts)

With several materials, the goal isn't to show every reference in every
clip. The goal is to define what each one is and select the right ones for
each block.

1. **Name and map each subject individually.** One line per reference: what
   to use, and what not to use.
2. **Profile recurring subjects.** For a cutout or prop that appears across
   several blocks, keep one profile in `run/prompts.md`: its appearance
   source, the scenes it appears in, and its exclusions. Paste the same
   wording into every block that uses it.
3. **Select by block.** Each block prompt lists only the references that
   block needs, plus the style key, which is always attached.

```
[Characters]
<Leader A> corresponds to the cutout reference. Use only the appearance,
red tie and suit. Black censor bar over the eyes.
Do not interchange <Leader A>, <Leader B> and <Leader C>'s appearances,
positions or props.

[Props]
<Powder Keg> corresponds to the keg reference and keeps the letterpress
label "WHO BLINKS?". It belongs only to the final scene.
```

Separate view images hold better than a collage once more than five
subjects need multiple angles.

## Audio syntax (sound design only)

The Vox pipeline uses only music and sound effects inside clips. Narration
is added at assembly, and captions are burned in at assembly.

| Content | Syntax | Use in this pipeline |
| --- | --- | --- |
| Music | `( )` | `(Low sub-bass drone with a slow heartbeat pulse)` or `(No music)` |
| Sound effects | `< >` | `<Guillotine slam with a dust whump>` |
| Dialogue | `{ }` | **Never.** End every clip prompt with `No speech.` |
| Subtitles | `【 】` | **Never.** Real captions are burned in at Phase 6. |

Give each sound effect its own bracket; don't stack five into one. Aim for 3
to 5 concrete diegetic events per 10s clip, each tied to a visible action,
such as a slam, a stamp, a rip or a fuse crackle.

## Timestamps & pacing

A 10s block usually needs no timestamps, because one continuous fake-oner
move with impacts every ~3s is enough. Use them only to pin a key beat, such
as the stamp landing or the reveal.

| Pattern | Example |
| --- | --- |
| Time range | `0-3 seconds… 3-7 seconds… 7-10 seconds…` |
| Exact time point | `At 5 seconds, the camera whip-pans left and completes the transition.` |
| Relative timing | `Two seconds after the stamp lands, the page tears open.` |

```
<start>-<end> seconds: <event>. End state: <observable state>.
<start>-<end> seconds: <event>. End state: <observable state>.
```

**What breaks it:**

1. Overlapping ranges. Keep them consecutive: `0-5` / `5-10`, never
   `0-5` / `4-9`.
2. Treating a range as an edit point. A range is a time budget, and actions
   may land slightly before or after a boundary.
3. Too little content in a range, such as `0-8 seconds: she stands there.`
   The model invents motion to fill the time.
4. Too much content in a range. The model cuts excessively or drops events.
5. Demanding a frequency, such as "three actions in one second".

## First & last frame

You rarely need this, because blocks are generated in parallel and joined by
fake-oner blur. Use it when one block has to land on an exact composition,
such as the reveal shot or a crane-up silhouette. Declare each anchor on its
own line:

```
The first reference image is the first frame. It defines the opening
composition, subject position, prop state and camera direction.
The second reference image is the last frame. It defines the ending
composition, subject position, prop state and camera direction.
<Describe one continuous action>. The video begins from the first frame and
reaches the last frame through that action. Keep <identity, prop count,
scene layout, camera direction> continuous between them.
```

**What breaks it:**

1. Combining both anchors in one sentence. Describe each one separately.
2. Anchors with different aspect ratios. The output ratio locks to the first
   frame, and a mismatched last frame gets stretched.
3. Letting other references override the anchors. They supplement only
   their stated attributes.

## Seamless transitions (fake-oner seams)

The house fake-oner hides every block boundary in motion blur. When a
specific seam needs more than blur, pick one of these bridge methods and
write it into the end of block N and the start of block N+1:

| Method | What to specify |
| --- | --- |
| Dive or reverse movement | Camera direction, speed change, and when the next scene begins |
| Foreground occlusion | When the foreground object fills the frame, and what composition follows |
| Object morph | The matching shapes and materials, and how one becomes the other |
| Push/pull or focus change | Camera move, focus target, and the continuous spatial relationship |

Collage examples: a torn page fills the lens and becomes the next block's
paper sky. A circular stamp becomes a map pin. The fuse spark becomes a
pulsing location dot.

**The arrival state is required.** Say where the transition lands, not just
how it starts.

## Emotional direction

Collage cutouts don't act much, but when a block needs a reaction, write
observable cues, not adjectives. Two to four cues are enough. For example:

```
After the stamp lands, the cutout statesman's paper shoulders sag, the
halftone hand slowly lowers the pen, and the camera holds on the cutout as the
other figures turn away.
```

## Cinematography terms

These can be written directly: shot sizes from extreme wide to extreme
close-up, and the moves push in, pull out, pan, lateral move, follow shot,
orbit, dive, dolly out and tilt up. Low angle, overhead and first-person
also work directly.

Terms that need more detail:

| Term | Also specify |
| --- | --- |
| One-take shot | The subjects, spaces and events the camera passes through, in order |
| FPV | Flight path, speed, and turns |
| Bounce speed ramp | Where the action accelerates, decelerates or rebounds, and its final resting state |
| Dolly zoom | The subject size to hold, and whether the background moves closer or farther |
| Bullet time | The action to freeze or slow down, and the camera's orbit direction |
| Rack focus | Which layer goes soft and which goes sharp. For paper layers, name both layers |

For a niche or ambiguous term, keep the term and translate it into a visible
change:

```
Term + target subject + visual change + foreground/background relationship
+ direction or speed
```

For example: `Whip-pan transition: at 5 seconds, move the camera rapidly
left; cut when the foreground torn page fully covers the frame, then continue
left at the same speed into the next scene.`

## Limits

| Material | Hard cap | Works best |
|---|---|---|
| Images | 30, each 4K or smaller | 1–8 distinct subjects |
| Videos | 10, ≤ 30s combined | 1–5 subjects, 5–10s each |
| Audio | 10, ≤ 30s combined | only clips the task needs |
| Total | 50 materials | |

For Vox clips, attach the style key plus no more than 3 to 4 prop or cutout
references per block. Stability drops as the material count grows.

First-frame generation locks the aspect ratio to the first image. Every
other clip takes `aspect_ratio` from the call, so set it explicitly on each
one (see SKILL.md Defaults).

## Pre-submission checklist

1. Does the prompt open with the house STYLE tokens, verbatim?
2. Is the subject and primary action or event clear?
3. Does every attached reference say what to use **and** what not to use?
4. Is every recurring cutout or prop named, and worded the same in every
   block?
5. Is there one continuous camera move that begins and ends in motion blur
   (diorama style)?
6. Is there an impact every ~3s and at least one speed ramp?
7. Are 3 to 5 sound effects bracketed, with `No speech.` and no `{ }` or
   `【 】`?
8. Is the text fence present: `No text anywhere except "<LABEL>"` for
   diorama, or the full NEGATIVE line for Mixed Media?
9. Are there no named politicians, and no "mushroom cloud" (see the
   moderation map in `diorama-doc.md`)?
10. Are aspect ratio, duration and resolution set on the call and absent
    from the prompt?

## What it will not promise

1. Timestamps allocate time to events. They aren't frame-accurate edit
   points.
2. Multi-reference selects and combines the right materials. It doesn't
   make every material appear at once.
3. Text, numbers and signs that must be exactly right need post-production.
   This is why Mixed Media bans in-clip text and diorama allows one short
   label per scene.
4. Seamless transitions aim for visual and audio continuity, not
   pixel-identical joins.
