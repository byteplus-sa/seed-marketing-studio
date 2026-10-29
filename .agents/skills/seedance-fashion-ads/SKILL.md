---
name: seedance-fashion-ads
description: Write Seedance editorial fashion film ad prompts with garment-led movement and continuity. Use for fashion campaigns, not sizing advice, wardrobe swaps in footage or generic camera presets.
---

# Seedance Fashion Ads

Make the garment's line, construction and movement carry an editorial idea.
Own the fashion treatment, coverage contract, complete prompt and post handoff.
Remain a prompt-only leaf. Do not generate, acquire assets, invoke or load
sibling skills, render, approve production results or publish.

## Inputs and Scope

Resolve these from the brief and selected references:

- Garment identity, visible views, construction, colour and styling locks.
- Wearer identity and authorized likeness scope, or an explicitly invented cast.
- Intended reaction, supported product facts, audience and one requested action.
- Runtime, ratio, placement, recognition deadline and exact approved copy.
- Source generation count, native cuts versus continuous take, and post latitude.
- Setting, movement restrictions, audio route and confirmed directorial axes.
- Requested output scope, including which span may change in a revision.

Do not infer size, body measurements, comfort, fabric composition or fit advice
from an image. Rendered drape is a visual treatment, not a sizing simulation.
Ask about consequential gaps. A claim-free provisional treatment is useful
without assets; label it provisional and do not invent selected @Image bindings.
Preserve canonical identity wording verbatim where applicable.

Fashion here means a garment-led editorial proposition, not every clip of a
person in clothes. A neutral try-on needs clear observation rather than a new
campaign concept. Source-preserving wardrobe replacement is a different task.

## Reference Loading

- Read [worked example](references/worked-example.md) for a complete package.
- Read [evaluation cases](references/evaluation-cases.md) when testing or
  modifying the method, especially garment continuity and scoped repairs.

These hypothetical references establish no real campaign, asset approval,
performance evidence or default brand, cast, market or colour.

## 1. Find the Garment's Editorial Argument

Connect hook, viewer desire, development, payoff and garment role before
construction checks. Choose an attitude and physical phrase: claiming space,
breaking a formation, resisting a rhythm or inviting a closer look. Let body,
cloth and environment develop it together. A short step followed by a neutral
pose is not a universal editorial idea. Quiet tension is valid when deliberate;
do not prescribe runway spectacle or frantic cutting to every garment.
Keep the continuity ledger in the handoff and translate only its essential
anchors into the prompt, leaving room for expressive behavior.

Choose one visible relationship: a seam echoed by architecture, a rigid line
contrasted with a relaxed gesture, or a moving hem settling into a silhouette.
Write the proposition as garment feature -> staged action -> readable payoff.
The environment supports that relationship instead of hiding the product.

Choose an emotional distance deliberately: observed, intimate or performative.
Translate it into behavior, such as a wearer pausing at a threshold before
stepping forward. Do not rely on "luxury" or an expensive-looking location.
An editorial film need not include a runway, model stare, macro or outfit change.

For exploration, offer distinct relationships, not a list of camera presets.
For a settled brief, develop its one direction without extra variants.
Treat apparent slimming, body reshaping and before/after appearance as claims,
not harmless styling. Never manufacture superiority or sales rankings.

## 2. Build a Garment Continuity Ledger

Record each visible construction anchor and its evidence:

```text
garment_id / selected reference roles / canonical descriptors
silhouette and hem length / panels and seams / closures and their state
sleeves and cuffs / collar or neckline / pockets / print alignment
wearer identity / worn layers / accessories / tuck and fastening state
known front-side-back views / unsupported views = unknown
allowed fabric motion / prohibited topology changes
```

Keep two sleeves, the same fastening count and the same seam connectivity
through pose changes when those are established by the references. A fold may
hide a button temporarily; it may not delete it or move it to another panel.
Distinguish cloth occlusion from altered cut. Keep fit, body proportions and
garment ease consistent with the approved wearer reference.

Do not complete an unseen back, lining or closure by plausible invention.
Constrain the turn to evidenced views or request additional evidence. A
different colourway or styling state is a separate proposal, not continuity.
Preserve consenting real-person likeness without inferring consent from a photo.
Authorization and provider identity handling remain caller-owned boundaries.

## 3. Choreograph Cloth Through the Body

Choose a movement that reveals the garment without changing it:

1. Establish a readable resting silhouette and fastening state.
2. Apply one body action that explains the fabric motion.
3. Let the fabric lag, fold or settle according to supplied visual evidence.
4. Finish in a state where construction can be compared with the opening.

Describe feet, weight transfer, shoulders and hands before adding cloth motion.
A planted pivot differs from a walking turn. A sleeve follows its arm; it does
not detach or inflate independently. Name which hand contacts which seam or
lapel, and keep the other hand accounted for.

Avoid using wind to excuse random fabric expansion. If wind is requested,
state direction, affected loose sections and what remains fastened. Preserve
layer order and prevent a hand from passing through cloth during a gesture.
Do not make the wearer tug the garment to imply a fit result without evidence.

## 4. Design Coverage Around Construction

Use whole silhouette, construction detail and movement consequence only where
they serve the argument. A detail should explain the whole, not merely interrupt
it. Keep the hem or featured sleeve within frame during its important action.
Protect perspective from unintentionally changing limb or garment proportions.

Write each shot or continuous-take phase with this contract:

```text
shot_id / source_id / approximate window / editorial purpose
wearer position, facing and weight / garment state in
body action / cloth response / contact and occlusion / state out
size and framing / angle / lens intent / camera start-path-end
named light source, world position and key side / texture to reveal
visible identity anchors / unknown views avoided / continuity to next beat
audio cue / native or post boundary / room for finishing copy
```

A held camera may best expose cloth motion; record that reason. Keep a named
light source fixed in world space across connected views and explain constant
light when chosen. Do not introduce a grade or change confirmed axes by default.
Reconcile with an existing shot plan rather than replacing its locked decisions.

Separate editorial shot count from source generation count. One source can
contain several native shots if allowed. An explicit continuous take gets one
unbroken path with no hidden cut, not a montage called seamless.
Preserve the requested generation count; never add coverage, retries or drafts
to solve timing without authorization. If unsupported duration or crowded action
conflicts with the request, surface the tradeoff rather than silently splitting.
Prompt times are approximate; frame-exact cuts and beat hits belong to post.

## 5. Write the Prompt and Post Handoff

Return complete subject, action, environment, visual style, camera and audio
direction for every proposed source. Put garment anchors and body/cloth causality
inside the prompt, not only in a table. Bind actual selected references in order
by role; planning boards are not identity references.

Separate request intent from prompt prose: source count, duration, ratio,
requested supported target and audio behavior. The caller verifies live model
capabilities. For silence or post-only audio, specify `generate_audio: false`
when supported; an authorized route returning audio must discard or mute it.
Requested native sound needs actual listening later, not imagined approval.

Keep generated footage free of added overlay text, logos, CTA and captions.
Exact graphics use deterministic post layers with supplied assets and copy.
Inspect printed or embroidered branding on the garment against its acquired
reference; conditioning does not guarantee lettering or pattern fidelity.
When exact garment imagery is mandatory, propose approved photography or
compositing with adequate views and cloth occlusion, not a fidelity guarantee.
Do not silently erase canonical branding to make a defect disappear.

Give post the intended cuts, matching garment states, handles, sound ownership,
closing hold and verified placement safe-zone source. Unknown margins remain
unknown. Do not claim frame-exact model staging or authentic recorded fabric
foley. Timing changes require checking both cloth continuity and sound cues.

## 6. Return, Review and Revise

A full package contains the proposition, evidence gaps, continuity ledger,
shot/source plan, complete prompts, separate request intent, post handoff and
observable acceptance criteria. A bounded revision changes only its named span
and identifies any necessary downstream consequences.

Inherit current project policy without introducing a production gate here:
`review_mode` and `approval_mode` are independent. Missing values mean `default`
and `approve_for_me` for new actions only; invalid values block production.
Default has minimal preflight and actual final sanity; strict retains detailed
review. Every new Seedance 2.5 generation requires `resolution: "480p"` and
boolean `draft: true` in both review modes. Promote only selected native Drafts.
Surface source-count conflicts before generation; never bypass drafts or
silently expand scope. Prompt-only work generates nothing.
`approve_for_me` permits inspected in-scope agent selections;
`ask_for_approval` waits for the user. Neither grants rights, generation scope or release.
Paid-ad disclosure remains the user's recorded decision, not an automatic label.
Prompt-only drafting does not require production locks or fabricated approvals.

Acceptance checks cover stable garment topology and fit, consenting likeness,
body/cloth causality, visible construction, supported claims and readable finish.
Playback is required for continuity; stills cannot prove cloth motion. Report
missing evidence as untested. Never invent testimonials or efficacy evidence,
claim real capture, or predict sales, conversion or platform acceptance.

## Composition Hints

The caller may pair this with `seedance-ugc-ads` for neutral try-on persuasion,
`seedance-shot-design` or axis specialists for wording, `seedance-prompt-25`
for grammar, and exact-graphic or production capabilities for finishing.
These are prose hints only, not dependencies or instructions to load siblings.
This leaf owns garment-led editorial structure, not those catalogs or execution.
