# Execution Constraints

Cross-cutting Seedance 2.5 constraints that every preset recipe inherits.
This is a prompt-only handoff reference, not an instruction to load a sibling
skill or operate tools. The caller verifies current operation support before
using the parameter notes; this file resolves the four flagged presets in
detail. All parameters below are tool/API values, never prompt text.

## Parameter map

| Parameter | Value and notes |
|---|---|
| `duration` | Integer seconds, 4–30; `-1` for auto. Integer only — no sub-second values. |
| `resolution` | Every new Seedance 2.5 generation uses explicit `resolution: "480p"` and boolean `draft: true` in both modes, with no skip-draft exception. Resolve schema or transport conflicts without dropping the flag; promote only selected native Drafts. For a 4K request follow the 4K routing in [routing.md](../../../contracts/routing.md). |
| `ratio` | `9:16` default for UGC unless the request says otherwise. Locked to the first image on first/last-frame tasks and auto-derived from the source on edit tasks — never set it there. |
| Locked camera | Locked-off selfie/posing and spectacle demos state the lock in the prompt and record `format_static_by_design`; the Seedance 2.5 tool exposes no `camera_fixed` field. |
| `generate_audio` | Enables native audio when supported. The caller checks for leaked music, chants or stray speech. For silence or muted-source edits, propose `false`; a separate ambience bed is an optional finishing choice, not a sibling invocation. |
| `watermark` | Propose `false` only when the operation supports it, unless requested otherwise. |
| `return_last_frame` | `true` chains a scene into the next one's `first_frame` — used by multi-shot and long lifestyle recipes. |
| `priority` | 0–9; leave unset unless the caller specifies. |

## Task types

`omni_reference_task_type` accepts `auto`, `reference`, `edit`, and `extend`
on 2.5.

- **R2V recipes omit it** — the provider auto-detects from the prompt and
  media. Do not set `reference` on recipes; its behavior beyond auto-detection
  is undocumented.
- **Structured edits use `edit`** (subject replacement, outfit switch, hair
  style, creature integration over footage). `edit_video` is a 2.0-only value
  and is rejected by 2.5 with `InvalidParameter.TaskTypeConstraint`.
- **Continuation uses `extend`** (beta; ratio is locked to the source and
  stripped client-side).
- **Footage with people.** `edit` and `extend` reject a source video that shows
  a realistic person, generated or real, with `PrivacyInformation` before any
  cost, unless each person is bound as an `asset://` Virtual Portrait or
  authorized asset. Carry that input constraint into the handoff; preserve any
  documented current account exception and never infer consent from an asset
  scheme. The caller prepares the source muted (`generate_audio: false`) with
  sound in post. Without valid assets, offer the fresh-generation variant,
  not a silent conversion of an edit request; long arcs can use new single-pass
  clips instead of `extend`. Never claim rejection, cost or inspection for a
  task that has not run.

## Reference and duration caps

- Seedance 2.5 accepts up to 30 images, 10 videos, and 10 audios (50 materials
  total). Recipes use 1–4; extra slots stay available for the caller's own
  references.
- Edit tasks: source video under 20s with 1–5 references recommended. Output
  duration locks to the source (~±0.3s) and ratio derives from the source.
- Modes are mutually exclusive: never mix first/last-frame roles with an R2V
  reference bundle in one task.

## Flagged presets — resolutions

Four presets map to no single direct provider mode. Their canonical
resolutions:

### Group Photo — subject multiplication
Duplicates are forbidden inside edit tasks ("never a second or duplicated
copy" of a subject), so the multiply gag is **generation-only**: a single-pass
R2V describing the staged appearance of identical figures at timestamps.
Identity drift across figures is the main failure mode — QA every figure
against the identity reference. The reliable alternative for a real group
photo is distinct references per person.

### Gas Transformation — disintegration
No direct disintegration mode exists. Two supported approximations:
1. **Staged single-pass** — the dissolve into smoke is written as an explicit
   end state ("by @9s only smoke remains"), with the dissolution spreading
   across named body regions at timestamps.
2. **Object-morph transition grammar** — "corresponding shapes, materials,
   transformation process," used when the vanish bridges two states.
QA the final frame: it must read as the intended vanish, not a corrupt frame.

### Timelapse Human — frozen subject, moving crowd
No crowd-freeze or timelapse-speed parameter exists. Approximation: state the
subject's stillness explicitly ("stands perfectly still, motionless for the
full duration") while background pedestrians move constantly at fast frequency
with motion blur, on a locked-off camera stated in the prompt. QA that the subject
actually holds — any subject drift breaks the effect.

### Morning routine — over-30s arc
Two supported paths:
1. **Compress** the arc into a ≤30s staged version when no longer runtime is
   locked. If the user explicitly needs more than 30s, offer compression only
   as an alternative requiring agreement.
2. **Chain** natural-duration scenes via `return_last_frame: true` → `first_frame`,
   with matched aspect ratios and wardrobe continuity. Allocate enough scenes
   to preserve the requested total runtime and every required stage; three
   10s scenes do not satisfy a request for more than 30s.

## Cross-cutting QA

- **Phone screens (selfie presets).** Avoid the picture-in-picture prior:
  describe the screen or mirror image positively, or attach a deterministic
  mockup as `@Image N`; never expect a rendered UI.
- **Labels and packaging (eating/product).** A branded item takes its prop
  reference and its label is inspected in the take. Unreferenced cups, jars,
  tubes, cases, slates and neck labels invent lettering: describe them plain
  ("smooth surface, nothing printed") or leave them out. Overlay text (prices,
  captions, CTA) is a finishing layer (FFmpeg or HyperFrames).
- **Counts (group, rain, clones).** Counts drop or overshoot. State the exact
  number and each position at every timestamp. Fixed inventory stays visible
  from frame one; staged entrances and multiplication state starting count,
  exact additions and final count instead. Never mention unexplained spares.
  The caller counts on a full-size frame; this leaf does not claim that QA ran.
- **Hands.** The model reads left/right as the subject's own side; name each
  hand by anatomy plus frame side ("his right hand, frame-left").
- **Spoken lines.** Presets are mostly non-verbal; when a line is added, budget
  measured delivery or a native-language-informed read with pauses, onset and
  tail. Words / 2.2 is an English planning estimate, not a universal rejection
  rule. Initially allow 0.5-1.5 s onset and at least 0.4 s tail, then verify
  actual delivery; without evidence, fit is provisional. Preserve approved
  text; propose retiming or splitting before an authorized rewrite.
- **Spatial continuity (action).** Name the start point, travel axis,
  boundary, and end state; never demand impossible movement frequencies.
- **Keyframe chains (multi-shot).** First and last images must share an aspect
  ratio; ordered multi-keyframe images are preferred over grids.
- **High-burst creative caution, not a provider limit.** Explosions, splashes
  and jumps follow approved intent, with readable trajectories, contact and
  recovery. Reducing debris or slowing action is an optional repair for a
  demonstrated readability or continuity failure, not a default energy cap.
- **Generation parameters stay in the API.** Duration, resolution, ratio, and
  watermark never go in the prompt text.
