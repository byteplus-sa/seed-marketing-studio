---
name: seedance-ugc-ads
description: Write Seedance UGC ad prompts joining nine modes, 45 motion presets, hooks, settings and formulas. Use for creator ads, named presets or narrow revisions. Not for generation or non-UGC specialist ads.
---

# Seedance UGC Ads

Join a supported product truth to a visible event. This prompt-only leaf handles
mode-only direction, preset-only motion and full ads without invoking or loading
sibling skills. Return prose prompts and handoff notes, never generate, upload,
submit, render, approve or publish media.

Modes, presets and formulas are optional creative heuristics, not platform
ranking rules, API requirements or demonstrated conversion gains. Examples and
evaluation scenarios are hypothetical, never evidence of customer experience.

## Choose the Scope

Read supplied instructions, references and locked copy first.

| Request | Deliver |
| --- | --- |
| Mode only | Reusable texture, story, camera/light and audio direction for that mode |
| Named preset only | Motion, camera, audio, reference roles, flags and separate suggested parameters; no forced persuasion brief or CTA |
| Full UGC ad | One coherent supported angle, mode, optional preset, opening, demonstration/payoff and requested CTA |
| Hook, setting, motion or copy revision | Only the requested change; preserve all other locks and identify real dependencies |
| Exploration | Three materially different angles unless another count is requested |

A settled single prompt never needs extra alternatives. Do not force a preset
onto every ad or an ad onto every preset. A missing mode or preset can remain
unselected when unnecessary. Unknown facts remain unknown.

Specific non-UGC requests are better served by `seedance-product-demo-ads` for
product demonstrations, `seedance-story-ads` for narrative spots,
`seedance-testimonial-ads` for evidence-led testimonials and
`seedance-fashion-ads` for editorial garment ads. These are prose routing hints
for the caller, not dependencies or instructions to load another skill. Retain
all nine modes below for explicitly requested legacy modes and UGC hybrids.
Source-preserving edits beyond a named preset, reference-edit reconstruction,
static graphics and actual production are outside this leaf's scope.

## Establish the Persuasion Brief

For a full ad, extract the product facts and sources, audience and objection,
demonstrable action, experience evidence, requested CTA and destination, runtime,
ratio, audio, identity references, language/register and forbidden changes.
Do not assume a market, language, culture or brand. Label inferred objections as
hypotheses. Mode-only and preset-only work need only the inputs relevant to their
requested block.

Keep a ledger `claim -> supplied source -> supported scope -> usable wording`.
Claims include visible results, comparisons, prices, offers, limitations and
availability, not just dialogue. Preserve approved wording and conditions.
Ask a focused question when missing input materially blocks the requested result;
otherwise provide useful neutral staging and identify the narrow gap outside
spoken lines. Missing operating instructions or product references are not
permission to invent a mechanism, label or reference binding.

A synthetic presenter is not evidence of product use. Never invent purchase or
use histories, savings, efficacy, drawbacks, review counts, body measurements or
sizing advice. An "honest con" or skeptic-to-convert story needs actual evidence.
Real testimony needs supplied authorization, wording and typical-result context.
An obviously fictional dramatization must never masquerade as a real customer,
and its claims still need support. A fictional brief does not authorize a fake
verified review. Generated imagery illustrates; it does not substantiate results.

Known mechanisms permit neutral lines such as "Here is how the lid opens."
Unknown prices, offers, URLs, stock pressure and codes stay out of usable copy.
For deliverables, the workspace [ad compliance contract](../../contracts/ad-compliance.md)
owns fact status, offer freshness, brand copy and disclosure requirements.
Prompt-only drafts need no production locks; they must not imply readiness
where evidence, rights or references are unresolved.

## Select Mode and Angle

For a full ad, connect hook, viewer motivation, development, payoff and product
role before expanding technical direction. Give the creator a specific
perspective and a reason to address this viewer: curiosity, a practical question
or a playful challenge, not an invented purchase history. Let phrasing, emphasis
and interaction carry personality. A steady phone is compatible with lively
behavior; neutral feature recitation is not the default voice.
Do not impose this development pass on preset-only or narrow revision requests.

Read the requested section of [mode recipes](references/mode-recipes.md), or its
custom recipe when none fits. Preserve these mode IDs:

- `ugc`: casual presenter-led content;
- `ugc-how-to`: intelligible steps in a real use context;
- `ugc-unboxing`: packaging and product discovery;
- `product-showcase`: product-as-hero without a presenter;
- `product-review`: evidenced assessment or neutral feature comparison;
- `tv-spot`: polished story or demonstration for the supplied placement;
- `wild-card`: one experimental idea with coherent texture;
- `ugc-virtual-try-on`: casual garment demonstration;
- `virtual-try-on`: editorial garment presentation, also called Pro Virtual Try-On.

Choose a provisional mode only when useful, explaining the assumption. For a
hybrid, state its dominant texture and purposeful secondary influence.
Phone-shot modes may use a steady camera with `format_static_by_design`;
a selected moving preset or requested coverage overrides that default.
Polished modes and multi-shot presets carry a per-shot plan with duration,
size, angle, camera move, lens intent, named light source and visible action.
A static camera or constant light needs a reason, not gratuitous movement.

Choose an angle that pays off the viewer's question:

| Angle | Opening and payoff | Evidence boundary |
| --- | --- | --- |
| Demonstration | Known mechanism in use | Operation, not invented efficacy |
| Objection handling | Uncertainty answered by a feature | Hypothesis labeled; comparisons sourced |
| Discovery | Overlooked supplied detail and use case | No invented experience or result |
| Experience | Actual approved account | No synthetic endorsement posed as real |
| Quantified comparison | Supplied comparison under its conditions | Number, timeframe, denominator and source |

Alternatives differ in viewer question, opening image and payoff, not synonyms.
A silent review or product-only legacy mode needs no presenter or forced speech.

## Select Motion

Match preset names or stable IDs case-insensitively. For a description without a
name, state a plausible match as an assumption; ask when ambiguity changes the
result. If none fits, say so and offer a clearly labeled custom direction or
nearest alternative. Never invent a canonical preset ID.

Read shared rules at the top of [motion presets](references/motion-presets.md),
then the resolved category section only:

| Category | Presets | Library |
| --- | --- | --- |
| Emotion / reaction | Angry Mode, Crying, Happy, Happy Mode, Shocked, Saint Glow, Sunglasses | [People/product](references/motion-presets.md) |
| Selfie / posing | Selfie, Selfie Outfit, Selfie Posing, Static Posing, Fix and pose, Group Photo | [People/product](references/motion-presets.md) |
| Outfit / fashion | Outfit Check, Outfit Switch, Clothes Rain, Hair Style, Sand Cut | [People/product](references/motion-presets.md) |
| Eating / product | Eating, Eating Zoom, Plate Check | [People/product](references/motion-presets.md) |
| VFX spectacle | Atomic, Explosion, Firework, Northern Lights, Aquarium, Color Rain, Money Rain, Pizza Fall, Cotton Cloud, Gas Transformation, Beast Appearance, Giant Grab | [Spectacle](references/motion-presets-spectacle.md) |
| Action / movement | Handheld Run, Pool Jump, Ballet, Motor Ride, Beach Ride, Train Rush, Peak Moment | [Action/story](references/motion-presets-action-story.md) |
| Lifestyle / timelapse | Morning routine, Timelapse Glam, Timelapse Human | [Action/story](references/motion-presets-action-story.md) |
| Multi-shot story | Yacht, BTS | [Action/story](references/motion-presets-action-story.md) |

Each recipe retains its ID, grammar, references, motion block, camera block,
audio, suggested duration, flags and optional persuasion hint. A hint is not a
supported claim. Preserve the defining motion and all applicable flags while
adapting incidental setting, props, hands and timing to explicit instructions.
If the core effect cannot fit a lock, surface the conflict instead of pretending
it is the unchanged preset.

Read [execution constraints](references/execution-constraints.md) for parameter
notes, edit/extension inputs, chains, counts and flagged presets. The caller
verifies current capability support; this leaf never claims a submission ran.
Existing-footage variants inherit source action, occlusion, duration and ratio,
not a fresh-generation timeline. Missing authorized people references remain
unresolved; a fresh-generation alternative is a proposal, never a silent rewrite.

## Join Persuasion and Motion

Load only entries needed for the requested axes:

- [Hooks](references/hooks.md) for named openings, alternatives or hook-only swaps.
- [Settings](references/settings.md) for a requested location or an open location choice.
- [Script formulas](references/script-formulas.md) for PAS, AIDA, three reasons or timed structure.
- [Worked repairs](references/worked-repairs.md) for unsupported claims, repetitive angles, testimony or staging defects.

Name selected IDs. Check hook and setting **Valid modes**; report a mismatch and
offer a compatible choice rather than silently changing a requested mode.
Formula allocations and preset timestamps must become one timeline, not two
overlapping scripts. Match each beat's persuasive job to one visible event and
end state; use the preset's action as that event where compatible.

One hook fills the opening 0-2 s beat, at most 3 s. It does not add another
opening ahead of the preset or force competing gestures into the same interval.
Retiming must preserve enough time for the defining action and payoff. A hook
must lead into a supported demonstration, never invent one. In a reference-ad
recreation the reference's opening is the hook; do not stack a library hook.
A setting changes where, not product properties. Surreal effects are conceptual
staging, not evidence of efficacy.

Honor exact requested structure, count, runtime, silence and framing over recipe
defaults. If those constraints conflict, explain the smallest necessary choice
and ask; do not silently extend, truncate or rewrite locked dialogue. For long
or dense arcs, propose natural-duration scenes with explicit continuity, not a
mandatory number of generations.

## Make the Prompt Executable

Keep claim ledgers, review modes, cost and task bookkeeping in the handoff.
The creative prompt needs the actual action, performance, sound and essential
identity/continuity constraints, not every planning field repeated as prose.
Necessary safety and scope exclusions stay; do not suppress expression merely
to make the scene easier to constrain.

Use only the sections the scope needs: visual texture, subject/reference roles,
environment, timestamped action and end states, camera, and audio. For a full
ad, integrate these into one prompt rather than returning disconnected libraries.
Bind supplied media explicitly, for example `@Image 1` defines product shape,
color, material and printed label; do not claim a missing file is attached.
Parameter suggestions such as duration, ratio, resolution and watermark belong
in separate handoff notes, not the creative prompt. Action timestamps remain
in the prompt. A proposed fresh UGC ratio is 9:16 unless specified otherwise.

- **Speech:** Count actual words, not the brief's asserted count. About 2.2
  words/s is an English planning estimate only. Allow onset (initially
  0.5-1.5 s), pauses and at least 0.4 s tail; use measured or
  native-language-informed delivery to establish fit. Without it, timing is
  provisional. Retiming or splitting precedes authorized copy rewrites.
  Keep the final three seconds to one or two state changes.
- **Counts:** For a fixed inventory, show every item from frame one and restate
  count, identity and position at each beat, including held or inserted items.
  For intentional entrances or multiplication, state starting count, exact
  additions and final positions; do not require future arrivals at frame one.
  No unexplained spares or duplicated products. Group Photo stays generation-only
  with identity and full-frame count QA in the caller's handoff.
- **Hands and props:** Name anatomy plus frame side on each handling beat,
  resolving mirror/selfie orientation. Keep unreferenced recurring props plain,
  with nothing printed, or omit them. Branded, recurring or critical products
  need the relevant reference; never invent packaging or accessories.
- **Camera and performance:** Give purposeful framing, named light and physically
  observable cues. One primary event per beat; a fixed phone is compatible with
  casual UGC. Do not stack a preset camera move with an incompatible mode default.
  Preserve product, garment and face identity through movement.
- **Audio:** Honor silence, native dialogue, voiceover or supplied music.
  Keep speech intelligible; optional music needs a usable source, not invented
  licensing. Separate lip-sync audio is opt-in; drafts keep identical dialogue
  and the caller checks actual timing before video. Do not prescribe universal
  broadcast loudness or claim an uninspected track passed QA.

Keep generated footage free of overlay text. Captions, prices, CTA cards,
graphic logos, end cards, UI and lower-thirds are deterministic finishing layers,
not video-generation instructions. Acquired on-product labels may remain through
their bound reference, but fidelity still needs inspection. Preserve safe visual
space for the actual placement; do not invent universal margins.

Close a full ad with the requested action and actual destination. If none is
supplied, propose a truthful next step without inventing a URL or offer; do not
force this onto preset-only or mode-only output.

## Policy and Handoff

Current AGENTS.md governs older recipe lore. `review_mode` and `approval_mode`
are independent. Missing values mean `default` and `approve_for_me` for new
actions only; invalid values need correction.

- `default` uses minimal preflight and actual final sanity without a mandatory
  prompt-review report; `strict` retains detailed prompt/output checks.
- Every new Seedance 2.5 generation requires `resolution: "480p"` and boolean
  `draft: true` in both review modes. Promote only selected native Drafts.
  Surface source-count conflicts before generation; never bypass drafts or
  silently expand scope. Prompt-only work generates nothing.
- `approve_for_me` permits the caller's inspected, recorded agent decision.
  `ask_for_approval` waits for the user's explicit selection in either review mode.

This leaf performs none of those production operations and never turns a
recommendation into approval. Rights, consent, reference locks, budget, supported
claims and required human evidence remain independent boundaries.
Paid-ad disclosure is the user's per-deliverable decision before delivery,
not implied by creative approval. Do not burn an "AI-generated" or "fictional"
label into footage by default, and do not infer that a platform labels it.

The caller may compose this output with `seedance-prompt-25` for extended grammar
or an axis specialist for deeper direction. These are optional prose hints only;
the ordinary mode, preset and full-ad requests are self-contained here.

## Check Before Returning

- Correct requested scope, exact locks, IDs and count of alternatives.
- Every spoken or visible claim within evidence; no invented testimonial or con.
- Hook, setting, mode and preset form one feasible action and persuasion timeline.
- Counted items, hands, props, identity bindings and defining preset flags retained.
- Dialogue has plausible onset, pauses and tail; conflicts and unknowns explicit.
- One accurate CTA when requested; all overlay text assigned to finishing.
- No generation, sibling loading, fabricated inspection or assumed approval.

## Offline Evaluation

[Merged cases](evals/evals.json) cover full ads, preset-only work, unsupported
testimony, missing inputs, narrow revisions, counts/timing, mode-only work and
unknown presets. [Mode cases](evals/ad-modes.json) retain 15 legacy numeric IDs;
[motion cases](evals/motion-presets.json) retain nine. IDs are suite-scoped.
Use their semantic expectations for offline prompt assessment; structural checks
alone do not establish creative quality or generated-media performance.
