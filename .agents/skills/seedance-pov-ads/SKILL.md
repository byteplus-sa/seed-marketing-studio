---
name: seedance-pov-ads
description: Write Seedance POV and first-person ad prompts with embodied camera and hand continuity. Use for viewer-as-participant ads, not selfie testimonials, UI tutorials or source-preserving edits.
---

# Seedance POV Ads

Build an ad around what a participant notices, reaches for and changes.
The viewpoint determines available evidence and possible action, not just a
wide-angle look. Own the interaction sequence, prompt and editorial handoff.
Remain a prompt-only leaf; do not generate, acquire media, load or invoke
sibling skills, render, approve results or publish.

## Inputs and Scope

Resolve the following before calling a package complete:

- Participant role, task and intended viewer reaction.
- Selected product references, canonical identity and supported operation.
- Viewpoint owner, camera attachment, dominant hand and mirroring intent.
- Available workspace, product starting position and reachable destination.
- Runtime, ratio, placement, reveal deadline, exact copy and audio intent.
- Explicit source generation count, native cuts or continuous-take requirement.
- Approved directorial axes, authorized likeness and permitted revision span.

Ask about missing viewpoint or operating steps when they determine the action.
Offer a provisional observation-only treatment if operation is unknown. Never
invent mechanisms, selected files, personal experience or product outcomes.
First-person perspective does not authorize a first-person testimonial.
Do not assume a market, gender, skin tone, handedness or body measurements.

## Reference Loading

- Read [worked example](references/worked-example.md) for a complete package.
- Read [evaluation cases](references/evaluation-cases.md) when testing or
  changing viewpoint, anatomy or interaction rules.

Examples are hypothetical and carry no actual capture or inspection evidence.
Do not reuse their participant, product, timing or setting as defaults.

## 1. Lock the Viewpoint Owner

State who or what carries the camera before writing any hand action:

| Viewpoint | Camera behavior | What must not be implied |
| --- | --- | --- |
| Eye-level first person | Follows the participant's head and gaze direction with plausible neck motion | A third-person face shot or camera floating ahead of the body |
| Chest-mounted | Moves with the torso; hands may enter higher in the frame | Every gaze shift also tilts the camera |
| Object-mounted | Rigidly follows a named object with a fixed attachment and offset | The viewer sees through the user's eyes |
| Observer overhead | Looks down on the task from an external support | First-person sight merely because hands are visible |

Choose one owner per continuous take. Label intentional viewpoint changes at
cuts; never glide from eyes into a product or detach a chest camera without a
declared change of treatment. Selfie direct address is not eye POV.
For mirrors, distinguish physical reflection from an intentionally mirrored
delivery image. Account for any reflected wearer and authorization scope.

## 2. Build a Perception-Action Loop

Connect hook, participant motivation, development, payoff and product role
before detailing fingers. Give the viewer something to anticipate, choose,
discover or complete. Hands moving a product between two empty surfaces are
only handling coverage unless the brief makes that movement meaningful.
Let gaze and reachable action reveal information; camera shake is not embodied
involvement. Retain calm movement where it aids perception.
Keep contact bookkeeping outside the prompt while preserving essential grip,
support, anatomy, identity and viewpoint facts in its action wording.

Use notice -> orient -> reach -> contact -> manipulate -> release -> inspect
as a reasoning tool, not a mandatory seven-shot structure.
Make one supported interaction the payoff. Combine phases when simple; leave
enough time for contact to be read instead of hiding it behind a cut.

The opening should give the participant a reason to look. The final state
should show what actually changed, not an unsupported benefit. A latch opening
can demonstrate access; it cannot establish durability or user satisfaction.
Keep a stable landmark so the viewer understands camera movement versus motion
of the product. Frame the destination before an important placement action.

Plan information order. An eye POV can glance at a handle before reaching.
A chest view may need the participant to turn their torso. An object-mounted
view may obscure the product it advertises; solve recognition with supported
framing or a declared cut, not a disembodied duplicate hero object.

## 3. Map Hands, Reach and Object State

Create a contact ledger:

```text
participant_id / viewpoint owner / mirror state / body orientation
camera height and offset / attachment / permitted rotation and translation
anatomical hand / frame entry side / target / grip or finger contact
other hand location / occupied or free / object support
object count and pose / action / contact window / release / end support
visible landmark / near clearance / occlusion interval / unknown views
```

Use anatomical left/right plus frame side on every handling beat. In a normal
unmirrored forward view, the participant's right hand usually enters frame-right;
verify actual staging rather than copying a selfie convention.
Keep wrist orientation, fingers, thumb placement and elbow reach plausible.
An occupied hand cannot also stabilize a second item unless the grip allows it.
Hands do not multiply when an object crosses the camera or a cut occurs.

Show the approach before contact and a supported resting state before release.
Distinguish grip change from teleportation between hands. Keep counted parts
and removable pieces accounted for even while occluded. Avoid aiming the lens
through the wrist, torso, tabletop or product.

Do not infer a hidden underside or reverse face from the action. Constrain the
path to selected views or request evidence. Preserve canonical descriptors and
all visible product parts; a new viewpoint does not license redesign.

## 4. Specify the Shot or Take

Use a compact state contract for each shot or phase:

```text
shot_id / source_id / approximate window / participant intent
viewpoint owner and mount / starting gaze and landmark
product state in / anatomical hand and frame side / primary action
contact and occlusion / camera path and clearance / product state out
size / angle / lens intent / focus target and depth
named light source and world position / key side / reflection constraints
continuity boundary / sound cue / native or post ownership
```

Keep the camera's movement independent from a hand's path. Eye movement alone
does not move the camera through space; a step translates it, a head tilt
rotates it. Choose restrained head motion if readability or comfort needs it.
Do not promise that a camera treatment prevents motion sickness.
Record the reason for held framing or constant light and preserve locked axes.

Source count is not shot count. Keep an explicit count even when several native
shots fit inside one source. A continuous-take request means no cuts, concealed
joins or teleportation; reduce complexity by agreement if the action cannot fit.
Do not add source generations, retries, extensions or drafts without scope.
Keep supported source durations separate from editorial windows and handles.
Prompt timing is approximate; frame-exact cuts, retiming and audio sync are post.

## 5. Write Prompt and Finishing Instructions

Supply complete subject, action, environment, visual style, camera and audio
direction for each source. Open with viewpoint owner and mount, then describe
the interaction in causal order. Include hand ledger facts in the prompt.
Bind only selected references by their actual ordered roles. A planning board
is not a product identity reference.

State request intent separately: generation count, duration, ratio, requested
supported target and audio behavior. The caller checks live parameter support.
For silence or post-only sound, use `generate_audio: false` when supported.
If an authorized route returns audio anyway, mute/discard before the post mix.
Native breath, speech or contact sounds require actual listening later.

Exact overlays, logos, CTA, prices and captions belong to deterministic post,
not generated video. Product printing remains canonical and needs inspection
against acquired references. Never replace missing text with invented marks.
If a screen or label must be exact throughout, propose a tracked approved layer
with correct occlusion and perspective, or an exact-image route.

Give the editor contact windows to preserve, safe trimming handles, hand state
at every join, sound ownership and a final resting view for supplied copy.
Use verified placement safe zones; unknown margins are not universal defaults.
Do not crop the critical hand or target to create room for the CTA.
Exact synchronization depends on inspected footage and measured sound, not
prompt timestamps. Generic SFX are stylized, not actual product recordings.

## 6. Return and Check

Return viewpoint decision, interaction proposition, evidence gaps, contact
ledger, source/shot plan, full prompts, request intent and post handoff.
For a bounded revision, retain viewpoint, identity, copy and unmodified states;
report any contact or timing dependency that crosses the requested boundary.

Follow the caller's current independent `review_mode` and `approval_mode`.
Absent fields mean `default` and `approve_for_me` for new actions only;
invalid values block production. Default needs minimal preflight and actual
final sanity, not an automatic draft. Strict keeps detailed review and Seedance
480p draft-first unless explicitly overridden. Honor explicit generation counts
and surface conflicts. Inspected in-scope agent selection is permitted under
`approve_for_me`; `ask_for_approval` waits for the user's choice.
Neither grants consent, budget or publication. Paid-ad disclosure remains a
user-recorded decision. This prompt-only leaf does not demand production locks.

Acceptance checks cover viewpoint attachment, reachable action, stable anatomy,
counted objects, contact and support, recognition and supported claims.
Playback, not just frames, establishes temporal continuity; audio needs listening.
Unknowns stay untested. Never claim actual first-person capture, user experience,
efficacy, sales ranking, conversion gain or platform acceptance from generated
imagery. Preserve consenting likeness when a reflection or body reference is used.

## Composition Hints

The caller may pair `seedance-ugc-ads` with an evidenced how-to script,
`seedance-shot-design` or axis specialists with camera wording, and
`seedance-prompt-25` with final grammar. UI-led explanations, source-preserving
edits and exact finishing have separate capabilities.
These are prose hints only; this leaf has no sibling loading dependency and
does not reproduce their catalogs or execute production.
