---
name: seedance-kinetic-ads
description: Write Seedance fast-cut, multi-angle vertical ad prompts across products, with cinematic realism, CGI or hybrid treatments. Use for kinetic or hypermotion ads, not UI explainers or source edits.
---

# Seedance Kinetic Ads

Design an ad whose energy comes from relationships between shots, not a list
of impressive camera names. Own the product-led creative treatment, sequence
design, prompt package and edit/sound handoff. Remain a prompt-only leaf:
never generate, acquire media, invoke sibling skills, render or publish.
The caller owns production, current model capabilities, approvals and budget.

## Scope and inputs

Generalize by visible attributes, useful actions and audience intent, never
by industry packs. A small object, a large object, a wearable, a consumable,
an experience or a service may all fit. For an intangible offer, identify
observable evidence or a clearly labelled metaphor; do not invent a physical
product. Text/UI-led explanations belong to motion design.

Read the brief, supplied references and existing decisions. Resolve:

- Subject and selected identity references, available views and fidelity needs.
- Audience reaction, one message, supported facts and intended next action.
- Runtime, ratio, placement, reveal deadline and any locked copy.
- Generation count, per-request duration, native cuts and permitted post work.
- Treatment, energy, setting, human involvement and requested audio.
- Scope: treatment exploration, full prompt package or a bounded revision.

Default to cinematic realism when treatment is unspecified. For a vertical
request without a ratio, propose 9:16; preserve an explicit different ratio.
Do not invent a duration, market, price, claim, brand asset or selected image.
Missing inputs permit a provisional claim-free treatment, not fabricated
reference bindings or a generation-ready label. Ask only about consequential
gaps; prompt-only help does not require production approvals.

When real ads are cited, distinguish general aesthetic discussion from
reference analysis. Do not claim to have inspected an ad from brand names,
articles or transcripts. A reference-derived shot or timing claim requires
actual footage inspection and measured timing through the caller.

## Reference loading

- Read [worked example](references/worked-example.md) when returning a full
  package or adapting the same sequence between treatments.
- Read [evaluation cases](references/evaluation-cases.md) when testing or
  changing this skill.

Examples are hypothetical craft demonstrations, not brand campaigns, measured
performance results or model capability guarantees. Do not inherit their
subject, timing, setting, palette or audio as defaults.

## 1. Establish the visual proposition

Write one sentence linking a visible quality or supported use to a feeling:

> Reveal [quality or action] through [visual relationship], building toward
> [signature moment], then let the viewer recognize [subject and next action].

Choose the visual relationship before selecting camera moves. Use scale,
texture, precision, repetition, contrast, movement or interaction as needed.
A shape match can link different scenes; a repeated gesture can link use and
detail. Neither requires a fantastical world.

For exploration, offer two genuinely distinct propositions. For a settled
brief, develop one. Do not equate premium with black-and-gold styling, glossy
surfaces or slow motion. Derive design from the selected subject and brand.
Treat apparent performance, before/after changes and ingredient imagery as
potential claims, even when no words are spoken.

## 2. Declare the treatment and reality boundary

| Treatment | Direction | Boundary |
| --- | --- | --- |
| Cinematic realism | Photographed-looking action, motivated light, plausible camera access and physical behaviour | No magical transformations, unsupported levitation or impossible camera travel by default |
| CGI | Deliberately constructed imagery, controlled product animation, material worlds or impossible events when requested | State which physical rules may change; CGI may also be photorealistic and physically plausible |
| Hybrid | Photographed-looking scenes plus declared synthetic shots or transitions | Mark entry and exit of each synthetic event and the identity/lighting facts that carry across |

Cinematic describes visual treatment, not proof of real capture. CGI-looking
Seedance output is not an editable 3D scene or a validated simulation.
Supporting CGI does not make every ad surreal. Even an impossible world needs
consistent internal rules, contact, occlusion and material response.

For realism, state camera clearance, support/contact, light sources, reflection
behaviour and object weight where relevant. A low tracking move must not pass
through a solid surface. A macro shot must retain credible scale and focus.
Preserve natural anatomy, grips and applied forces for human interactions.
For CGI/hybrid, enumerate allowed departures and everything that stays real.
Never silently switch treatments to hide a generation defect.

## 3. Build the sequence from contrast

Use an adaptable attention arc: opening event, recognition, escalation,
signature moment and release. Beats can overlap or be omitted when justified;
this is not a mandatory five-shot template. Assign a product reveal deadline
and a readable finishing hold suited to the brief.

Design coverage with these reusable relationships:

| Relationship | Job |
| --- | --- |
| Context to detail | Establish the subject, then reward attention with texture or mechanism |
| Detail to whole | Turn an intriguing fragment into a recognizable product |
| Action to consequence | Connect an interaction to its supported visible result |
| Low to overhead | Change spatial understanding, not just camera height |
| Motion to hold | Give a fast approach weight through a controlled landing |
| Scene to scene | Carry a shape, action or motion vector into a new setting |

Select only relationships that serve the proposition. Avoid an obligatory
macro, orbit or aerial when the subject does not benefit from it.

Give each shot a purpose and one primary event. Contrast neighboring shots in
at least two meaningful dimensions such as size family, angle, motion or
motivated light relationship; record a reason for deliberate repetition.
Reconcile with an existing shot plan rather than creating a competing one.
Vary shot length unless a locked rhythm dictates otherwise. Place one
signature moment where the contrast is strongest; constant maximum speed
removes emphasis. A hold is allowed when it makes identity or action readable.

Vary settings only when they add meaning. Preserve subject scale, orientation,
state, wardrobe and travel direction across connected shots; explicitly mark
intentional discontinuities. A new location needs enough context to be read,
not simply another background.

For vertical frames, plan foreground, subject and background depth. Keep the
essential action visible during lateral travel, and leave layout room for
later copy. Use the chosen placement's verified safe zone; never invent
unpublished platform margins.

## 4. Specify shootable shots and editorial boundaries

Record each shot in this compact contract:

```text
shot_id / purpose / provisional edit window / source segment
subject state and screen position / visible event / end state
size / angle / lens intent / foreground and background
camera start -> path, direction and speed -> end
named light source / key side / quality / motivated changes
continuity in and out / selected reference roles
treatment / allowed departures from reality
transition out / sound cue / native or post ownership
```

Use one dominant camera move, with at most one compatible secondary move.
Give every move a destination and reason. Separate subject motion from camera
motion; rotating both without intent can obscure geometry. Name a light
source and its position rather than writing only "cinematic lighting."
Preserve the requested palette; do not apply a grade by default.

Separate the final edit from generation segments. A sub-second insert may
come from a longer, usable generated action with entry/exit handles. Choose
segment durations from supported capabilities and natural actions, not final
cut lengths. Do not squeeze a dense rapid montage into one overloaded prompt.
Keep related actions together where continuity helps; split where independent
control or repair matters. Prompt timestamps are approximate, not frame-exact.
Preserve an explicit continuous-take request instead of silently assembling it.

One provider generation is not one continuous take. When the user limits
generation count, retain that number of source segments and put the allowed
native shots inside each segment's prompt. A request for three 30-second
multi-shot tests means three source generations, not eighteen short clips
and not three unbroken takes. Keep native cut timing approximate, reduce
overloaded staging by agreement, and disclose control limits. Never spend
extra generated seconds or add retries to enforce frame-exact cuts.

For each boundary, declare:

```text
outgoing shot and state / incoming shot and state
mechanism / matching shape, scale and screen position
motion vector / occlusion or correspondence point
timing target / source handles needed / picture and audio owner
```

Use clean hard cuts as readily as transitions. A whip needs compatible exit
and entry movement; a wipe needs covering foreground; a shape match needs
matched position and scale. Independent generations do not guarantee a match.
Make precise cut points, repeated beat hits, freeze frames and exact retiming
editorial operations. If handles fail to match, propose a clean cut or scoped
replacement rather than calling an accidental morph intentional.
If the transition is locked, a fallback is a proposal requiring a decision,
not permission to replace it. Surface incompatible runtime, dialogue or
layout requirements for a decision; never silently drop approved content.

## 5. Preserve identity and separate exact graphics

Bind available selected references by explicit roles: product identity,
person, environment or supported control role. Keep ordered bindings consistent
with the caller's actual files. A board or panel grid is a planning artifact,
not a video identity reference.

List identity anchors such as silhouette, proportions, component count,
surface finish, colour and functional state. Only supplied evidence can
establish unseen sides. For a full orbit from a single front view, request
additional views or constrain framing; do not promise exact reconstruction.
Preserve authorized human likeness and voice scope through the caller.

Reserve added logos, titles, captions, prices and CTA layouts for deterministic
post layers. Printed product markings still require inspection; a reference
does not guarantee lettering fidelity. When exact product appearance is
mandatory throughout, specify approved photography, a suitable product-render
route or compositing with appropriate views and occlusion. A correct end card
cannot compensate for a visibly altered product earlier in the ad.

## 6. Write the prompt and sound handoff

Write complete prompts using explicit subject, action, environment, visual
style, camera/cuts and requested audio direction. Carry each shot's facts into
the prompt rather than leaving them only in a planning table. Keep exact
post graphics out of generated footage. Leave request parameters separate;
the caller resolves the selected model's live-supported fields.

Direct sound by audible material and event: dry clicks, cloth movement,
surface contact, air displacement or an appropriate tonal accent. Do not
attach the same whoosh to every cut. Specify music build, interruption and
release when music is requested; honor silence or an existing soundtrack.
Keep native audio and post sound ownership explicit to prevent duplication.

When a track is available, align the edit to measured accents. Without it,
label cue timing provisional; never invent BPM or claim beat synchronization.
Protect dialogue intelligibility and allocate time from the approved words
and actual delivery when available. Do not force fast cuts across a performance
that needs a readable face. Refit sound cues after picture timing changes.

Carry the chosen audio route into request intent, not just prose. For silent
or picture-only/post-audio routes, request `generate_audio: false` when
supported. For an authorized alternative that returns audio, explicitly
discard or mute that track before the post mix; do not mix both by accident.
A native-audio test may request `generate_audio: true` explicitly, with its
own observed audio QA; never substitute that route silently.

## 7. Return and check

For a full package, return:

1. Proposition, treatment and assumptions, including the reality boundary.
2. Ordered reference roles, identity anchors and missing evidence.
3. Shot sequence and source-segment plan with reveal and finishing moments.
4. Complete per-segment prompts, without unresolved generation bindings.
5. Edit/sound handoff, exact-graphics split and separate request intent.
6. Observable acceptance criteria and unresolved decisions.

For a single prompt or scoped revision, return only what is needed. Preserve
approved direction and change the smallest affected span.

Check the plan for recognition, purposeful variety, coherent screen direction,
plausible physics or explicit CGI exceptions, feasible transition endpoints,
supported claims, exact-branding boundaries and a readable finish. Check
footage only when actually available. Playback is needed for motion, product
stability and transitions; listening is needed for audio. Still frames cannot
prove temporal or sonic quality. Report untested as untested, not passed.
No checklist predicts virality, conversion or ad-platform approval.

## Composition boundary

When a caller uses the existing production shot-plan record, convert this
sequence into that record rather than designing a replacement sequence:

- Put `energy`, `axis_carry`, world-positioned `sources` and any motivated
  light cues in the scene's `shot_plan`. Preserve confirmed axes and record
  any user-authorized override, including a fixed native-generation count.
- Map each editorial shot to `id`, `duration_s`, `job`, `size`, `framing`,
  `featured`, `angle`, `angle_reason`, `move`, `move_reason`, `lens_intent`,
  `depth_layers`, `light` and `contrast_with_previous`. Mark exactly one
  scene `turn`, one `wow` per source clip, and applicable `static_reason`
  values for holds; explain intentionally constant lighting.
- Keep provider source IDs separate from editorial shot IDs. Each source's
  shot manifest carries its slice; a single-pass multi-shot test has one
  source manifest with several internal shots, not several provider tasks.
- Keep transition and treatment records alongside the mapped plan. The
  caller reconciles any heuristic conflict against explicit user constraints,
  validates the plan and applies `seedance-prompt-25` as final prompt grammar
  authority. This leaf does not load or invoke that skill.

These are optional prose handoffs for the caller, not skill dependencies:

- `seedance-shot-design` and camera/lens/light/pacing specialists provide
  general coverage and axis wording; this skill owns the kinetic ad sequence.
- `seedance-cgi-advertising` provides a deeper product-world metaphor when
  needed; this skill retains the sequence and treatment boundary.
- `seedance-motion-design` owns text, UI and graphic-led messaging.
- `template-factory` owns measured reference reverse-engineering.
- `film-production` owns multi-scene execution and Studio state; the existing
  audio, exact-graphic and ad-check capabilities handle their respective layers.

Do not replace those capabilities with parallel implementations or introduce
new submission, review-mode, approval or disclosure rules inside this leaf.
