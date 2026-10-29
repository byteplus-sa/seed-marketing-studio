---
name: seedance-shot-design
description: >-
  Design the shot plan for a Seedance scene before any prompt is written: shot
  count and duration, the job of each shot, size, framing (single, two-shot,
  group, over-the-shoulder, over-the-hip, point of view, insert), angle, camera
  move, lens intent, named light sources and key side, the contrast between
  neighboring shots, and a variety check (V1-V10) at a chosen energy level
  (restrained, standard, kinetic). Use for narrative, ad, micro-drama,
  music-video and showcase clips when camera and light are not already locked,
  when a scene reads flat or static, or when the user asks for a shot list,
  coverage, shot framing, or more dynamic camera work and lighting. Returns a shot plan record and the
  per-shot facts a Seedance 2.5 prompt carries. Not for static assets,
  source-preserving edits (object swap, restyle, recast), or task submission.
---

# Seedance Shot Design

A Seedance prompt may read flat because the idea does not develop, even when
camera and light are specified. Establish what changes for the viewer first,
then make coverage decisions explicit, one shot at a
time, before the prompt is written. It is planning only: it never calls a tool,
never generates media, and never replaces the grammar owned by the prompt
skill.

## Why clips read flat

Diagnose the actual missing contribution before applying these craft heuristics.
Camera variety alone cannot rescue an empty premise.
These are coverage problems to investigate, not proven causes of every flat
performance. A held setup, soft light or subtle action can be intentional.
Preserve the approved scene and its performance plan; more cuts or camera
movement cannot substitute for acting intent.

| Cause | What the plan does instead |
| --- | --- |
| An object is handled but nothing develops | Identify curiosity, motivation and payoff; return a weak premise for development rather than disguise it with moves |
| A setup hides the intended beat | Adjust framing or staging; add coverage only when the beat needs it (V1) |
| No camera-move statement, so the model holds a neutral frame | Every shot states its move with a start and an end, or records a `static_reason` (V3, V6) |
| Vague movement with no purpose or speed | Name the intended movement or hold; gentle and abrupt choices are both valid |
| Camera, lens and light presets used only when the user names them | The plan assigns them by default at the chosen energy level; a user lock still wins |

### Cinematic sequence bar

Separate editorial structure from provider source count. One generation can
contain several native shots; one continuous take cannot. Preserve both the
authorized generation count and any no-cuts lock. Derive internal shots from
the hook, development and payoff within the supported duration. Separate
short sources offer independent edit control only when that scope is available.

When an approved ad, trailer or showcase benefits from segmented coverage,
one optional structure builds the piece as
sequences of about 5 s, each generated as its own clip of 2-3 shots, and cut
them together in assembly. A 30 s spot is about six such sequences. Each shot
carries its action or sustained task, lens intent, a motivated move or hold and
a named light source. Depth layers are optional when they serve the idea, and each
sequence may have a `wow` shot if a standout image serves the brief. A single
30 s pass with many beats can overload a prompt. Choose count from readable
beats, source locks and generation scope, not a mandatory six-clip or standout quota.

## Boundary

| Need | Where it lives |
| --- | --- |
| Resolve a named move or a framing type into canonical Camera phrasing | `seedance-camera-presets` |
| Resolve focal length, aperture or depth of field | `seedance-lens-presets` |
| Resolve a named light setup into recipes and phrases | `seedance-lighting-presets` |
| Speed ramps and montage rhythm | `seedance-pacing-presets` |
| When cuts land on a song (cut timing, beat contract) | `seedance-music-video` owns the timing; this skill plans what each shot is |
| Character geometry and blocking | `blocking-map` |
| Dramatic structure of the scene | `scene-craft` |
| Performance intentions, triggers and listening | `acting-direction`; consume the supplied plan |
| Six-part formula, per-shot prompt block, references, audio syntax | `seedance-prompt-25` |

These are prose pointers for the calling agent. This skill decides *which*
choices a shot needs; the preset skills decide *how* each one is worded.

## When a plan is not needed

Record an exemption instead of a plan. The exemption reason is the plan. An
agent cannot choose an exemption to avoid the work: a `proposed`, `defaulted`
or `agent_confirmed` axis is not a user lock. A user lock fixes only what it
names; the plan still fills the rest.

| `static_reason` | Applies to |
| --- | --- |
| `user_lock` | The user, or a `user_confirmed` lock, fixed the camera or light |
| `format_static_by_design` | A format whose mode is a fixed frame: the `ugc`, `ugc-how-to`, `ugc-unboxing`, `product-review` and `ugc-virtual-try-on` modes, named UGC presets whose camera block is locked-off, talking-head, avatar and news-desk takes, frame-break. The `product-showcase`, `tv-spot`, `wild-card` and `virtual-try-on` modes take a plan |
| `skill_owned_camera` | Another skill supplies an explicit per-shot camera plan (a reverse-engineered pin plan). Derive the plan from it; V1-V3 are advisory. A music-video genre lock is vocabulary only and does not exempt: plan the shots |
| `plate_for_cutdown` | A source plate generated to be cut later; name the cut target |
| `source_preserved` | An edit, swap, recast or restyle that must keep the source camera |
| `extension_continuation` | Extending or continuing an existing take |
| `no_video_shot` | Audio-only work, static graphics and deterministic renders: no shot exists |

In a static-by-design format, variety may come only from light, a product
insert or B-roll the format allows; ask before leaving the format.

Two further reasons are not exemptions. They justify one held shot inside a
plan: `performance_hold` (stillness is the beat; quote the beat or cue that needs
it) and `contrast_hold` (a deliberate hold right after a moving shot).

## Input and output contract

Input: the scene beats and intended viewer reaction, location and light facts
(draft until canon is approved, then revalidated), runtime and aspect ratio,
any confirmed `directorial_axes` or `locked` block recorded in `project.md`,
and any user locks.
For character performance, consume the caller's beat IDs, intentions, listener
tasks, registration/response timing and critical acceptance criteria. Missing
material input goes back to the caller; this leaf does not invoke other skills
or invent character motivations.

Output: a shot plan record per [shot plan format](references/shot-plan-format.md)
and the per-shot facts the Seedance 2.5 prompt carries.
Carry relevant performance beats and readable evidence in existing shot notes,
not provider parameters. Reconcile cues with crop, camera side, occlusion, scale
and duration. Preserve sustained holds and exact dialogue; return conflicts
instead of changing timing, product demonstrations, copy or CTA.

## Procedure

1. **Read locks and axes.** A `user_confirmed` camera or light choice is an
   input, not a suggestion. A confirmed project axis must reach the shots, and
   the plan records where. Fill only the gaps.
2. **Choose the energy level** from the intended reaction and format, never
   from genre alone. Separately describe performance intensity, action density,
   camera energy, editing rhythm and sound dynamics when they differ. These
   are creative choices, not numerical scores or new required schema fields.

   | Level | Fits | Typical shot length | Camera | Light |
   | --- | --- | --- | --- | --- |
   | Restrained | Attention, intimacy, anticipation or deliberate understatement | 3-10 s | Purposeful holds or slow moves | Source and contrast chosen for the idea, not automatically soft daylight |
   | Standard | Moderate energy when the intended response calls for it | 2-6 s | Motivated moves or holds as the beat needs, with no moving-shot minimum | A named key side per shot; contrast only when useful |
   | Kinetic | Action, sport, chase, music video, high-energy ad | 1-3 s | Tracking, whip, handheld, crash zoom, orbit or FPV per beat | Hard contrast, rim or backlight, flicker, colored practicals |

   Energy describes amplitude, not a quota for size, angle or light changes.
   The lengths above are examples, not cadence requirements. Actor energy,
   camera energy and edit rhythm are independent choices. Kinetic dialogue
   is valid when the brief supports it; verify readability of words, required
   lip-sync, physical action and listener responses at the planned scale and
   speed. Stillness can carry intense intent without extra movement.
3. **Give every beat a job:** establish, reveal, emphasize, connect, escalate,
   hold or release. A shot with no job is cut or merged into its neighbor.
4. **Set the shot count and lengths** from the beats. About 7 shots per clip
   and about 0.8 s per shot are provisional generation-planning heuristics
   from workspace reviews, not provider limits or guaranteed merge/drop
   thresholds. Preserve requested rhythm and source timing; do not remove,
   merge, lengthen or split shots automatically to satisfy a count. Offer
   assembly for frame-accurate precision or omitted action: generate source
   clips at natural lengths and trim to the requested edit. A prompt-only
   approximation remains provisional; return genuine feasibility conflicts or
   missing timing inputs rather than silently altering locks. Choose lengths
   for the beats; regular timing is valid, and a turn is optional under the
   selected scene framework.
   One shot across a long clip needs a recorded one-take or
   `static_reason`. Size dialogue shots from measured delivery or a
   native-language-informed read with pauses. About 2.2 words/s is an English
   estimate, not a universal gate. Allow for onset (initially 0.5-1.5 s) and
   a final tail (initially at least 0.4 s), then verify actual delivery.
   Without evidence, timing is provisional. Preserve language and locked text;
   propose retiming or splitting before authorized rewrites. Judge closing beats
   by readability of the intended action, words and response, not a state-change
   count. Simplify a crowded ending only for demonstrated failure and within
   source locks; do not insert holds or remove approved actions by default. For a spot of
   about 15 s or more, consider the optional cinematic sequence bar above.
5. **Declare the scene's light sources** with world positions, the event that
   switches each on, and any in-scene cue that switches it off, dims it or makes
   it flicker. Then give every shot a source, a key side relative to the
   lens, a quality and a contrast. Assign each shot a size, a framing (who is
   featured and how the subjects relate, per [framing](references/framing.md)),
   an angle, a move with start and end, a lens intent as a visible result, and
   depth layers when useful to the idea. Dialogue may use a held frame or
   energetic coverage; choose size, framing, angle and speed for readability,
   not the mere presence of speech.
   Plan an attention shift inside one frame with staging or a move, not a
   prompted rack focus: Seedance drafts keep a face sharp, so a focus pull away
   from a face is added in post (see the lens preset skill).
6. **Check the coverage rules below** against the intended response and actual
   readability. Optional variety heuristics need no waiver to omit. Record
   each shot's purpose; mark a turn only when the selected scene contains one.
7. **Tell one light story per scene.** The sources stay fixed in the room. A cut
   changes which side of a source the camera sees, or a motivated event adds or
   removes a source (a door opens, a lamp is switched on, the room lights go
   out). A light cue may land inside a shot, even during a move, when the plan
   records its time and trigger; a timed cue is one of the most reliable
   controls in Seedance 2.5 drafts. A shot never invents a source or a cue the
   scene did not declare. Silhouette may carry speech if speaker attribution
   and the intended performance remain readable. Visible lip-sync requires
   visible lips; do not reveal a deliberately concealed face to satisfy it.
8. **Write the plan** per [shot plan format](references/shot-plan-format.md).
   Choose recurring structures from
   [coverage patterns](references/coverage-patterns.md).

## Variety rules

V1-V3, V5, V9 and framing-pattern suggestions in V10 are optional coverage
heuristics. Intentional stillness,
repeated framing and regular rhythm are valid when they serve the approved
scene. Record the observable purpose without requiring a heuristic waiver; do not
add motion, cuts or light changes merely to meet a quota. The cinematic
sequence bar is also optional: preserve authorized source count, no-cuts locks
and quiet performance rather than adding paid generations.

| Rule | Check |
| --- | --- |
| V1 Neighbor contrast | Change size, angle, movement or key side when it reveals something the beat needs. Deliberate repeated framing is valid; no minimum number of differing axes applies. |
| V2 Angle range | Choose eye-level, low, high, overhead, first-person or over-the-shoulder for the viewpoint the scene needs; no non-eye-level shot is required. |
| V3 Motion intent | Choose a motivated move or purposeful hold for each shot. Record `static_reason` for holds; sustained attention may justify repeated `performance_hold` shots. No minimum moving-shot fraction or maximum number of holds applies. |
| V4 Light named | Every shot names a declared source and a key side. "Cinematic lighting" and "soft fill" without a source and a side are not light facts. |
| V5 Turn emphasized | If the scene has a selected turn, make its change readable through performance or composition; timing or camera contrast is optional. |
| V6 Move coherence | One or two moves is a planning heuristic, not a cap. Preserve coherent requested choreography; name each move's subject, start and end, distinguish simultaneous components from ordered phases, and check readability and incompatible directions. Shot density is assessed separately under step 4, also without a count cap. |
| V7 Readable performance | A move never stands in for a cue that cannot be read at that size; match shot size to the cues the beat needs. |
| V8 Screen direction | Travel and confrontation state the axis and restate it after each cut; a deliberate axis crossing is named. |
| V9 Timing intent | Match lengths to the intended rhythm and readable performance. Uneven timing is one option; regular timing and locked song-map cuts need no invented turn or contrast. |
| V10 Framing intent | In multi-character scenes, name framing and featured subjects so relationships and relevant listeners are readable. Clean singles, shared frames or a held group shot are choices, not coverage quotas. Establish a point of view's owner where needed; use an over-the-hip when the height relationship serves the beat. |

## Inputs and limits

Storyboard grids and boards are planning and review aids and are never bound
as Seedance references: panel numbers and the sketch look leak into the video.
Blockout images are not bound by default. The plan's facts live in the prompt
text, beside the bound character, location and prop references. A first-frame
image fixes the opening size and angle of its shot, so V1 counts from the next
shot. A single location plate may not show the planned reverse or contre-jour
view: check that the plate supports each planned side, plan only supported
views, or request an approved extra view before Stage 6.

## Evidence and limits

A recorded plan (or exemption) is a workspace requirement under the
`shot.plan_bound`, `shot.variety` and `shot.axis_carry` rules. The V1-V10
thresholds are craft heuristics and optional artistic technique, drawn from the
failure shape of earlier workspace prompts: equal-length wide, medium,
two-shot, wide ladders with no move and no light change, and project axes that
never reached the shot lines. They are not measured video-quality gains.
Cut timestamps are a time budget, not frame-accurate cut points, and the model
may merge or reorder cuts; a timed light cue lands far closer to its stated
time. Judge the take by watching it. A 480p Draft
(`draft=true`) is the cheap way to check shot structure and motion before a
final render.

## Checklist

Before returning a plan, confirm:

1. Every shot has a job, duration, size, angle, move (or `static_reason`), lens
   intent, source and key side, and framing in multi-character scenes.
   A turn is annotated only when applicable.
2. Required shot facts are present and optional V1-V10 techniques serve the
   brief; no variety, turn, hold or standout quota is used as a pass condition.
3. Locks and confirmed axes are carried, not overwritten.
4. The shot count and lengths fit the duration, the energy level and any
   dialogue.
5. No shot stacks competing moves, and no shot invents a light source or an
   undeclared light cue.
6. Short cuts retain requested rhythm; the provisional 0.8 s heuristic does
   not trigger automatic retiming. Offer assembly for precision or omitted
   action, naming source clips at natural lengths when that route is selected.
   Return genuine feasibility conflicts; do not promise exact in-prompt cuts.
7. Sequence count and timing serve the approved beats and generation scope; the optional
   cinematic sequence example does not override holds or source-count locks.
   A single generation is not mislabeled as a mandatory continuous take.
8. No shot relies on a prompted focus pull away from a face; that defocus is
   planned for post.
9. The plan names where it is stored and which prompt carries it.

Worked cases are hypothetical teaching repairs in
[worked repairs](references/worked-repairs.md).
