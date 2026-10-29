---
name: seedance-match-cut-ads
description: Write prompt-only Seedance match-cut and metamorphosis ad sequences with matched endpoints and explicit edit ownership. Use for shape or action matches and literal morphs, not generic montages, source swaps or execution.
---

# Seedance Match-Cut Ads

Build an advertising sequence around a deliberate correspondence between
images. Own the match logic, endpoint direction, prompts and editorial
handoff, not generation or assembly.

This is an independent prompt-only leaf. Never invoke or require siblings,
generate media, manipulate source files, edit production state, render or
publish. The caller verifies capabilities, rights, approvals and outputs.

## Inputs and reference loading

Resolve from the brief and existing locks:

- Product, selected identity references and available views.
- Audience reaction, supported proposition, exact copy and next action.
- Runtime, aspect, fps, placement, reveal deadline and finishing hold.
- Desired correspondence: shape, action, camera motion or literal morph.
- Which identities, materials, settings and physical rules may change.
- Native generation count, allowed native cuts, source durations and handles.
- Permitted editorial trims, crops, retiming, transitions and compositing.
- Audio route, authorized master or cue evidence, and synchronization needs.
- Whether this is exploration, a full prompt package or a narrow repair.

Ask when the distinction between a cut and a morph affects the requested
result. Without selected references, return a provisional identity-free
treatment, not invented bindings or a generation-ready claim.
Do not infer a market, brand, claim, count or permission to change product form.

Read [worked example](references/worked-example.md) for a complete package
with endpoint arithmetic and source-to-edit mapping.
Read [evaluation cases](references/evaluation-cases.md) when changing or
testing this skill. Example coordinates and timings are hypothetical targets,
not measured footage or guaranteed model behavior.

## 1. Name the transition mechanism

| Mechanism | What changes | What must correspond |
| --- | --- | --- |
| Shape match cut | A hard cut connects separate objects or scenes | Silhouette/feature, screen position, scale and orientation |
| Action match cut | A hard cut continues a gesture across shots | Action phase, contact, limb/prop direction and velocity |
| Motion match cut | Separate shots share camera/subject movement | Screen-space vector, rate, framing and blur relationship |
| Literal morph | One object visibly transforms continuously | Defined topology/material progression and recognizable endpoints |
| Occlusion handoff | A covering object hides the edit | Cover extent, travel direction and reveal timing |

A cut on shape or action is not a continuous transformation. Do not use
"morph seamlessly" as shorthand for all five. For a hybrid sequence, label
each boundary separately. A literal morph may be wholly synthetic but still
needs a controlled identity and contact story.

If the user says "metamorphosis" ambiguously, offer the concrete distinction
and recommend the mechanism that serves their intent. Do not replace a
locked morph with a cut, or a locked cut with a dissolve, without a decision.

## 2. Build the commercial correspondence

Before endpoint arithmetic, connect the hook, viewer motivation, development,
payoff and product role. Each match should make a new association legible:
contrasting contexts, an unexpected continuation or a product-linked pattern
that resolves. Matching circles solely because they are circular is a geometry
exercise unless that recognition serves the brief. A calm two-image association
can work; additional transitions are not a substitute for meaning.
Keep calculation and task bookkeeping in the handoff; carry the essential
endpoint targets, identity and action into the creative prompt.

Write why each match matters to the buyer: a repeated shape reveals the
product, an action links contexts, or a declared fantasy expresses a feeling.
Avoid a series of unrelated visual tricks. Give each pair a recognizable
anchor and the sequence one supported proposition.

Distinguish a visual metaphor from a factual demonstration. A substance
turning into a product can imply ingredients; damage vanishing can imply
repair efficacy; an object becoming lighter can imply a performance claim.
Label fantasy clearly where needed and avoid unsupported implications.
Keep factual spoken and visible claims tied to selected evidence.

Set the reveal deadline and readable final hold. Reserve copy, CTA, logo,
price, captions, charts and exact UI for deterministic post, not generated
transition surfaces. Product markings still require fidelity checks.
When exact identity throughout is mandatory, propose authorized photography
or compositing instead of promising a generated morph preserves it.

## 3. Specify each pair of endpoints

Use normalized image coordinates with origin at top-left, x right, y down.
Separate target values from measured output and state the delivery canvas.
Define an anchor feature rather than saying "same framing."

For each outgoing/incoming pair record:

```text
boundary_id / mechanism / outgoing shot / incoming shot / meaning
anchor feature / center (x,y) / bounding width and height / visible contour
in-plane rotation / facing direction / perspective and camera elevation
subject state / action phase / contact and occlusion / depth ordering
key source and side / softness / shadow direction / exposure relationship
subject screen-space vector and rate / camera vector and rate / blur
outgoing endpoint window / incoming endpoint window / usable handles
target cut time/frame / permitted edit operations / picture and audio owner
tolerances and verification method / fixed constraints / unresolved gaps
```

Specify scale as a fraction of the full frame, not an ambiguous "close-up."
Use degrees with a stated clockwise convention for rotation. A circular
shape still has orientation when a seam, highlight or asymmetric rim is visible.
Match key-light direction, shadow edge and highlight placement enough to
support the illusion; name intentional changes instead of hiding them.

For action matches, align the same physical phase, such as fingers just
contacting a handle, rather than merely naming the same action. Keep grip,
support and occlusion plausible. For motion matches, compare image-space
movement; "both cameras pan right" need not produce matching screen motion.

Define tolerances suited to the shot and approved editorial freedom, not
universal numerical guarantees. A proposed two-frame cut window or crop limit
is a design target until the caller inspects actual coverage.

## 4. Assign source coverage and edit ownership

Create separate ledgers for source generations and editorial shots. Retain
the user's fixed generation count exactly. One source can contain multiple
native shots; one native generation is not automatically one continuous take.

Record source ID, planned duration, internal shots, selected reference roles,
usable source spans and each endpoint's entry/exit handles. Count handles
inside generated duration. Do not silently add paid seconds or separate
generations because independent endpoint control would be easier.

Prompt timing is approximate. Frame-exact hard cuts, alignment, crop,
permitted retiming and final sound cue placement belong to the editor.
Native cuts within a fixed single generation have less independent control;
state that limitation and ask to simplify only when necessary.

For a literal morph, decide whether Seedance owns the full continuous change
or deterministic post owns an explicitly scoped effect. Describe initial,
intermediate and final states, allowed topology changes, anchor stability and
the time available to read both endpoints. Do not imply code can recover
missing surfaces or turn a bad transition into a faithful product.

Preserve an explicit unbroken-take request. If an exact cut or extra coverage
conflicts with it, surface the conflict rather than inventing hidden edits.
Capability-dependent first/last-frame conditioning is only a proposal until
the caller verifies the selected model, roles, aspect and duration limits.
Boards/grids remain planning artifacts, never assumed identity references.

## 5. Write full source prompts

For each source, declare actual reference bindings when available, then
subject, action/event, environment, visual style, camera/cuts and audio.
Repeat the pair's defining endpoint constraints in both relevant prompts.
Do not leave endpoint facts only in an external table.

Give each internal shot its purpose, size, angle, lens intent, camera start
and end, named key-light source and subject action. Explain a static camera
when stable geometry is the intended mechanism. Preserve confirmed axes and
avoid adding a grade without scope.

For a hard match cut, direct separate recognizable scenes and a clean cut.
For a morph, direct the visible transformation and its intermediate material
behavior. Carry required handle states into the wording; label timestamps as
targets rather than assertions of exact output.

Keep exact graphics in post. State audio ownership explicitly: native event
sound, silence or an authorized post master. With post-owned audio, express
`generate_audio: false` only when supported; any returned native track is
muted/discarded by the editor unless separately selected. Measured music
cues may guide the cut; absent audio supports only proposed timing.

## 6. Return the format-specific handoff

```text
proposition / mechanism per boundary / reality and claims boundary
ordered reference roles / identity anchors / missing evidence
source-generation ledger with fixed count, duration and handles
editorial shot plan / paired endpoint table / complete source prompts
source-to-edit spans and cut frames / explicit trim, crop and retime limits
picture, morph and audio owners / exact deterministic graphics inventory
acceptance criteria / failure alternatives requiring decisions
```

Map to an existing production shot-plan record rather than designing a second
sequence. Keep native internal shot IDs distinct from provider source IDs,
and attach the endpoint and edit tables to that record. The caller applies
current supported parameters; this leaf does not submit the package.

For a narrow revision, change only the affected endpoint, cue or prompt span.
If one endpoint changes, recheck its paired endpoint and dependent edit
window. Preserve the fixed count, accepted mechanism, product, source masters
and unrelated shots. Do not rebuild the campaign for a scale adjustment.

## 7. Evaluate honestly

Prompting cannot guarantee matched outputs, even with identical coordinates
or selected endpoint images. Distinguish designed correspondence from
verified continuity in every response.

The caller compares frames around the boundary for position, scale,
orientation, silhouette, light and occlusion, then plays the transition at
normal speed to check motion phase, blur, identity and perceptual continuity.
Stills alone cannot prove an action match. Listen for duplicated transients,
an unintended audio cut or drift against the preserved master.

If usable handles do not overlap, record the measured discrepancy. Propose
only permitted crop/trim/retiming, a simpler cut or a separately authorized
replacement. A locked transition is not silently abandoned. Keep the fixed
generation count; no automatic extra attempts to force a match.
Do not claim frame-exact placement or acceptable product identity from the
prompt, a contact sheet or provider success.

Current `review_mode` and `approval_mode` govern downstream review and
selection. Prompt-only work generates nothing and adds no approval gates.
Every new Seedance 2.5 generation requires `resolution: "480p"` and boolean
`draft: true` in both review modes. Promote only selected native Drafts.
Surface source-count conflicts before generation; never bypass drafts or
silently expand scope.
Rights, supported claims, generation scope and paid-ad disclosure remain separate.

Optional prose hints for the caller: `seedance-kinetic-ads` covers a broader
fast-cut sequence; `seedance-object-swap` covers a kept source with one
replacement; `seedance-motion-design` covers graphic-led explanation;
`film-production` and installed HyperFrames capabilities cover execution.
These hints never require loading or invoking sibling skills.
