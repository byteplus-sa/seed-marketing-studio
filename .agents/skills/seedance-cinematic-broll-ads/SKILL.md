---
name: seedance-cinematic-broll-ads
description: Write Seedance cinematic B-roll ad treatments and prompts. Use for product montages, lifestyle, craft or voiceover-led B-roll ads, not kinetic ads, UI explainers or source edits.
---

# Seedance Cinematic B-Roll Ads

Build a commercial whose images carry a selling idea through observation,
texture, use and atmosphere. Own the treatment, purposeful coverage, prompt
package and editorial handoff. Remain a prompt-only leaf: do not acquire or
generate media, invoke sibling skills, render, approve or publish.
The caller owns capabilities, references, production state and execution.

## Scope and inputs

Treat B-roll as the visual storytelling layer, whether it supports narration
or carries the entire ad. Do not require a presenter or an A-roll interview.
Cinematic does not mean slow throughout, dark, glossy, shallow-focus or
letterboxed. Derive the look and pace from the subject and intended feeling.

Read supplied material and existing decisions. Resolve only consequential gaps:

- Product, service or experience; audience; desired feeling; one selling idea.
- Supported facts, approved copy, brand rules and intended next action.
- Selected identity references, available views and fidelity requirements.
- Runtime, ratio, placement, recognition deadline and finishing hold.
- People, setting, treatment, music, voiceover and silence constraints.
- Source-generation count/budget, permitted native cuts and post work.
- Exploration, full prompt package or a bounded revision.

Do not invent claims, durations, market, language, prices, reference bindings
or rights. With an empty brief, ask for the subject and intended message.
With incomplete inputs, offer a clearly provisional, claim-free treatment and
list what prevents generation-ready prompts. Preserve locked choices.

Read [worked example](references/worked-example.md) for a full package or a
concrete demonstration. Read [evaluation cases](references/evaluation-cases.md)
when testing or modifying this skill. Examples are fictional and never defaults.

## 1. Choose a visual proposition

Write one sentence connecting an observable quality to the intended feeling:

> Let the viewer notice [specific quality or activity] through [visual motif
> or relationship], so [subject] becomes associated with [intended feeling].

Select an organizing mode, not a compulsory shot recipe:

| Mode | What carries the ad | Main guard |
| --- | --- | --- |
| Product-detail montage | Form, finish, texture and selected whole-product views | Details must resolve into recognizable identity |
| Lifestyle atmosphere | A specific routine, place or human interaction | The product must participate, not disappear behind scenery |
| Craft/process portrait | Verified making, preparation or finishing actions | Do not invent manufacturing methods, origin or handmade status |
| Voiceover-led B-roll | A clear visual response to each approved thought | Pictures must support rather than exaggerate the spoken claim |

Offer two distinct propositions during exploration; develop one when direction
is settled. Generalize by material, scale, action and audience intent rather
than industry packs. An intangible offer can show verified activities or
explicitly identified metaphor, not fabricated testimonials or outcomes.

Mark each proposed image as observation, supported demonstration or metaphor.
A generated demonstration illustrates a supplied claim; it cannot substantiate
that claim. Ingredient imagery, durability tests, before/after changes and
process depictions can imply factual claims without any written words.

## 2. Build coverage with a reason to cut

Give every shot a job: orient, reveal, invite tactile attention, connect to
use, support a claim, or resolve into brand recognition and next action.
Remove shots that repeat information without a deliberate rhythmic purpose.
Use an adaptable arc of intrigue, recognition, deepening and resolution;
do not impose four shots or defer recognition beyond the agreed deadline.

Choose coverage relationships that make the next image meaningful:

- Whole to detail: establish identity, then reveal a distinctive material.
- Detail to use: connect a texture or component to an actual interaction.
- Action to rest: let a gesture finish before the viewer inspects its result.
- Environment to subject: make a place relevant through a visible activity.
- Motif return: repeat a shape, gesture or light pattern at a new scale.

Plan changes in shot size, angle, depth, action and motion without forcing
every cut to be spectacular. Include readable whole-product coverage.
Keep a tactile detail in focus long enough to perceive it. Use normal-speed
human actions where intention or mechanics matter; specify slow motion only
for a purposeful event. A held camera can contain active subject motion.

Define each shot using this compact record:

```text
shot_id / job / claim or visual-proposition connection
editorial window / source_id / required entry and exit handles
subject identity, state, position / visible action / observable end state
size / angle / lens intent / focus target / foreground and background
camera start -> feasible path -> end / reason for movement or hold
named light source, world position, quality / screen-relative key side
continuity in and out / selected reference roles
transition out and match requirements / audio cue / native or post owner
```

Keep editorial shots separate from source generations. A brief insert may
need a longer source with a stable entry, usable action and settled exit.
Preserve an explicit generation cap: one generated segment may contain
several native shots. Do not turn every editorial cut into a provider request
or misread one generation as one unbroken take. Source durations and request
parameters are resolved against current capabilities by the caller.
Label native cut timestamps approximate; exact final timing belongs in post.

## 3. Direct concrete cinematic images

Name the visible event instead of writing only "beautiful cinematic B-roll."
Specify material response, contact, focus and a camera destination. Give one
dominant camera move per shot and keep its path physically accessible.
Do not move both camera and subject without stating which reveals the detail.

Use named, positioned light sources. Preserve their world positions across
connected angles and update their apparent screen side when cameras move.
Explain intentional lighting changes. Hold product hue, material and finish
consistent; do not add a grade unless requested.

Keep close-focus geometry plausible. Thin focus must not hide the feature
or label that the shot needs to communicate. A macro texture must belong to
the actual selected product, not a generic beautiful substitute.

Preserve geometry, part count, marks, scale, hand contact, support, reflections,
wardrobe and action state across connected coverage. Independent generations
do not guarantee continuity. Do not invent an unseen rear face for an orbit:
request a suitable view or constrain the camera to established geometry.
Separate reference roles for identity, location and visual treatment.
Boards and panel grids are planning artifacts, not identity references.

Default to physically plausible photographed-looking action. Label any
requested synthetic metaphor and its entry/exit boundaries; do not silently
introduce levitation, morphing or an impossible camera path. Photorealistic
generation is not evidence of real capture.

## 4. Plan the edit and sound

Cut on new information, a completed gesture, a motivated sound or a visual
relationship. Use hard cuts, match cuts or dissolves according to the idea;
do not default every boundary to a dissolve or every accent to a whoosh.
Specify the outgoing state, incoming state, matching position/scale/vector,
source handles and edit owner for any continuity-dependent transition.

Use pacing contrast: inspection needs room, a short detail can punctuate,
and the final recognition/CTA needs a readable hold. Preserve an explicit
continuous-take request with one feasible progression, not a hidden montage.
When a locked transition cannot be supported, request a decision about new
coverage versus changing the transition. Do not silently replace it.

For voiceover, map each approved phrase to its visual support and leave
breathing room. Estimate timing provisionally until a real delivery exists.
If measured speech exceeds runtime, surface the copy/runtime tradeoff.
Do not delete words, translate, clone a voice or rush delivery by assumption.

Separate music, ambience, contact sounds and speech ownership. Prefer
material-specific cues; label designed foley as designed, not authentic
recordings. Without an inspected track, do not invent BPM or claim beat sync.
Let ambience or music bridge cuts where that strengthens continuity.

For picture-only/post-audio or silent intent, carry `generate_audio: false`
in request intent when supported. Prompt prose alone cannot mute a model.
If an authorized alternative returns audio, explicitly discard or mute it
before post mixing. Native sound is a separate requested route, not an
automatic duplicate soundtrack.

## 5. Package prompts and exact graphics

For every source segment, write a complete prompt containing reference roles,
subject, actions and end states, environment, visual style, per-shot camera,
lens and lighting, and requested audio. Carry the shot facts into the actual
prompt, not just a planning table. Use separate timed shot blocks for native
multi-shot segments. Do not fabricate selected @Image or asset bindings.

Keep added logos, captions, taglines, prices and CTA outside generated footage.
Specify deterministic post graphics, layout space and the agreed finishing
hold. Use verified placement safe zones; unknown margins remain unresolved.
Product markings still require QA. References do not guarantee exact labels;
pixel-exact product requirements need approved photography/render/compositing
with suitable views, not a promise that prompt wording will solve fidelity.

Return only the scope requested. A full package contains:

1. Proposition, mode, treatment and unresolved assumptions.
2. Reference roles, supported facts and identity/continuity anchors.
3. Ordered shot records and source-segment grouping.
4. Complete source prompts and separate request intent.
5. Edit, sound and exact-graphics handoff.
6. Observable acceptance criteria and untested items.

Check purposeful coverage, timely recognition, claim support, feasible action,
lighting and identity continuity, audio ownership and readable resolution.
Treat all footage checks as proposed until media is inspected. Stills cannot
prove motion or audio quality; require playback and listening for those.
Do not predict virality, conversion or platform approval.

## Composition boundary

Keep this leaf independent. These are prose handoffs for the caller:

- `seedance-kinetic-ads` owns fast-cut spectacle and hypermotion; energy alone
  does not exclude an otherwise observation-led cinematic montage.
- `seedance-cgi-advertising` owns product-world CGI concepts.
- `seedance-product-demo-ads` owns stepwise mechanisms and problem-solution
  proof; this skill may include a supported use moment without becoming a tutorial.
- `seedance-motion-design` owns text/UI-led explanations.
- `template-factory` owns measured reference analysis. Require actual inspected
  footage for reference-derived timing, not campaign names or articles.
- `seedance-shot-design` and directorial-axis specialists supply general
  coverage vocabulary; `seedance-prompt-25` is the caller's final grammar authority.
- `film-production` owns execution, Studio state and downstream review.

When entering an existing production plan, map these shot facts into its
current shot_plan rather than create a second competing sequence. Preserve
confirmed axes, source IDs and user overrides. Carry energy, axis_carry,
world-positioned light sources, per-shot duration/job/size/framing/featured
subject/angle/move/lens/depth/light/contrast and applicable static reasons.
Fit required turn and wow fields to the real reveal or tactile payoff; do not
add spectacle to satisfy a label. Keep source IDs distinct from edit-shot IDs.
The caller owns validation, review mode, approvals, rights and generation.
