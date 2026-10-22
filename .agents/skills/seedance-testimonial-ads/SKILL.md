---
name: seedance-testimonial-ads
description: Write Seedance real testimonial and customer story ad prompts from authorized evidence. Use for sourced customer accounts, not invented reviews, synthetic UGC or UI explainers.
---

# Seedance Testimonial Ads

Shape an authorized customer's actual account without manufacturing testimony.
Remain an independent prompt-only leaf. Never contact customers, acquire media,
generate, render, publish or modify production records. The caller owns those
actions and their authorization. A credible-looking face is not evidence.

## Scope and inputs

Distinguish real testimony from a presenter explaining features. A synthetic
presenter is not an actual customer. Without an identified underlying customer
and authorized account, return a gap or propose a non-testimonial concept,
not a believable invented review.

Collect the following within the requested scope:

- Source account, customer identity reference and exact approved quotation.
- Recording/transcript locators, date, context and surrounding qualifications.
- Permission to use the quote, name, affiliation and original media separately.
- Likeness/voice and synthetic-representation rights, if relevant.
- Relationship to the brand, compensation/incentive and disclosure context.
- Product identity, claim evidence, result conditions and typical-result context.
- Runtime, ratio, placement, language, CTA and exact-copy constraints.
- Generation count, native-cut/continuous-take locks and audio route.
- Requested edit scope, review_mode, approval_mode and existing decisions.

Keep private customer details in caller-controlled evidence, not reusable
examples or public prompt text. Use stable evidence IDs; public attribution
must match permission, not whatever personal details the source contains.
A public review, purchase record or logo alone does not grant reuse rights.
If consent or evidence is absent, ask for it and provide an unfinished
structure without invented quotes, identities or reference bindings.

Read [evaluation cases](references/evaluation-cases.md) for the hypothetical
worked package and when testing or revising this skill.

## 1. Select a truthful representation route

| Route | What the viewer receives | Boundary |
| --- | --- | --- |
| Original customer footage/audio | Actual recorded account | Preserve meaning and authorized edit scope |
| Approved quotation with neutral narration | A sourced quote or attributed summary | Do not impersonate the customer or imply original recording |
| Authorized synthetic reenactment | Synthetic delivery of an actual account | Underlying testimony and representation rights both required |
| Illustrative B-roll with original testimony | Real voice/account over an illustration | B-roll must not masquerade as captured evidence of results |

Prefer retained original testimony when the user supplies it for that purpose.
Do not regenerate an entire interview simply because B-roll is requested.
For synthetic reenactment, keep portrayal explicit in the handoff and resolve
necessary disclosure under applicable delivery policy. An AI label never
makes a fabricated underlying account acceptable.
If a requested route lacks consent, offer an authorized alternative as a
proposal; do not silently change voice, attribution or representation.

## 2. Build a quote-to-claim ledger

```text
testimony_id / private source reference / customer identity evidence
recording or transcript locator / exact quotation / surrounding context
usage permission / attribution scope / likeness and voice scope / dates
relationship and incentive / disclosure requirement or unresolved decision
claim_id / substantiation / conditions / typical-result context
edit permission / approved excerpt / omitted context / status
```

Separate three questions: Did this person say it? May it be used here? Is the
claim supportable as an ad? A yes to one does not answer the others.
Preserve "for my setup," "sometimes" and other limiting language. A customer's
result is not proof that everyone will obtain it. Do not invent typicality,
timeframes, savings, sample sizes, dissatisfaction or an "honest con."
Regulated or comparative claims need appropriate evidence and review.
Price and availability claims need freshness checks before delivery.

Use complete meaning units when excerpting. Do not join separate answers into
an endorsement the customer never made. Preserve negation, causal uncertainty
and who experienced the result. Quotation marks require exact words.
Label summaries as summaries and obtain authorization where the use requires
it; translations need meaning and usage confirmation, not invented fluency.

## 3. Build the customer story from evidence

Find the hook and viewer relevance in the authorized account's specificity,
not a scripted conversion arc. Select its meaningful detail, context and bounded
payoff without embellishing words, emotion or results. A strong quiet quote
can be complete; do not demand conflict, a reversal or a louder performance.
If the available account is generic, request a better authorized excerpt or
report that limitation. Never manufacture evidence to raise creative intensity.
Keep permission bookkeeping outside the prompt while preserving portrayal limits.

Use `documented context -> actual action -> bounded experience -> next action`
only when each part exists. A strong quote can stand alone; do not force an
invented problem or conversion arc around it.
Let the customer's own relevant specificity carry the story.
Do not script fake interviewer surprise or a before/after personality change.

```text
beat_id / testimony_id / source locator / exact quote or attributed summary
evidence type / supported claim_ids / context that must remain
picture role / real evidence versus illustration / state_in -> state_out
speaker identity and representation route / audio owner
attribution and disclosure owner / open consent or substantiation issue
```

For illustration, show only supplied supported activities or mechanisms.
Generated footage of a smiling customer, dashboard, skin, revenue chart or
finished project is not evidence that the reported outcome happened.
Real before/after evidence needs provenance and comparable conditions;
never synthesize either side or alter it to strengthen the claim.

## 4. Plan evidence-led coverage without manufacturing sincerity

```text
shot_id / source_id / approximate window / testimony beat and picture role
subject position / eyeline target / hands and prop state / end state
size / angle / lens intent / camera path or static reason
named light source / key side / quality / continuity anchors
reference roles / permitted performance changes / sound / handles
```

For an authorized reenactment, match the authorized account's delivery range
with concrete behavior, rather than imposing universal quietness or enthusiasm.
Do not add tears, hesitation, accents, hardship or "spontaneous" reactions as
evidence of sincerity. Match only the authorized portrayal.
For original footage, performance is source material, not a prompt to rewrite.
Coverage can protect an approved excerpt but cannot hide a meaning-changing cut.

Keep generation count separate from editorial shot count. Preserve requested
continuous takes and native-cut limits. The caller verifies model durations
and supported reference roles at runtime; prompt timing is approximate.
Frame-exact edits, captions and audio synchronization belong to post.
Do not increase generations or add retries to make a testimonial fit.

Budget speech from an actual read or source timing with onset, pauses and tail.
If the approved quote is longer than the locked runtime, propose a permitted
excerpt or runtime change; never accelerate unnaturally or rewrite silently.
If only B-roll is generated, the generation duration need not equal the full
source interview duration, but must cover the requested edit windows.

## 5. Return a complete prompt and edit handoff

For each generated source provide subject/bindings, visible action and states,
environment, visual style and named lighting, camera/cuts and audio.
Carry the exact authorized quote, speaker and language into native-dialogue
prompts only when that route is explicitly selected and authorized.
For original voice plus B-roll, write a picture-only prompt without a new
speaker or invented lip movement.
Keep unresolved permissions and bindings outside the prompt and label the
package provisional until resolved.

Separate request intent: selected model, ratio, duration, generation count,
reference order, cuts and audio route. For original/post-audio work specify
`generate_audio: false` when supported; any authorized route returning audio
needs explicit mute/discard so the real voice is not doubled.
The caller validates actual API fields, permissions and capability availability.
Do not disguise a rejected real-person reference or imply consent from access.

```text
edit span / source media and range / testimony_id / quote locator
meaning-preserving cut / retained qualifiers / picture truth status
dialogue source and sync / B-roll handles / music rights and mix owner
exact attribution / CTA destination / captions / disclosure decision status
placement template / safe-zone status / identity and printed-label checks
```

Keep overlays, CTA, graphic logos, ratings, captions and UI in deterministic
post. Ratings or badges require their own evidence; they are not decorative
trust cues. Inspect printed products against selected authorized references;
use real imagery/compositing if exact markings cannot be preserved.
Do not invent a universal safe zone or omit required context to fit one.
Paid-ad disclosure stays a user decision; brand affiliation and incentive
disclosures remain separate from synthetic-content disclosure.

## 6. Make bounded revisions and inspect evidence

For a quote-only revision, show the old and proposed excerpt with its source
locator, omitted context and permission status. For B-roll changes, preserve
the source testimony and attribution. For performance-only changes, preserve
words, identity, route and all consent limits.
Do not turn a scoped "warmer delivery" request into a fabricated life story.

Check every spoken claim and factual image against evidence and authorization.
Check omitted context, attribution accuracy, approved quote completeness,
synthetic-versus-original clarity and unaltered real result evidence.
Listen to compare actual words, pauses and speaker identity; playback is needed
for lip-sync and product stability. Transcripts alone cannot verify vocal
similarity or sincerity. Report pass, fail or untested with locators.

Honor review_mode independently of approval_mode; default adds no mandatory
draft or approval gate. Strict production checks are caller-owned.
Rights and claim gaps cannot be approved away by a creative review mode.
Return source/permission gaps, representation route, ledger, shot/source plan,
complete prompts, edit/audio/graphics handoff and observable QA.
No checklist predicts persuasion, conversion or legal/platform acceptance.
Optional caller composition may use film-production for execution,
seedance-prompt-25 for model grammar, or authorized-avatar, audio and caption
specialists. These are prose hints only, not sibling commands or dependencies.
