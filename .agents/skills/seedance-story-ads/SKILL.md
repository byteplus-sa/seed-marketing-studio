---
name: seedance-story-ads
description: Write Seedance entertainment-first short story ad prompts. Use for character-led branded narratives, not deadpan mockumentary, real testimonials or exact UI explainers.
---

# Seedance Story Ads

Build a short story whose product role belongs to the causal action.
Remain an independent prompt-only leaf. Never generate, acquire, render,
publish or modify production state. The caller owns production and approvals.
Entertainment-first describes emphasis, not a license to miss a locked reveal
deadline or a claim that stories outperform other ad formats.

## Scope and inputs

Use this capability for character-led tension, discovery and a meaningful
payoff. Understated comedy built around an observing documentary camera has a
different owner: deadpan ads. Real customer accounts belong to testimonial
work. A sequence of feature shots without a character problem is a demo.

Read supplied material and identify:

- Audience reaction, genre/register, one message and intended next action.
- Product/service identity, selected references, supported facts and limits.
- Fixed character goal, established problem, stakes and existing story canon.
- Product role, reveal deadline, brand constraints and exact approved copy.
- Runtime, ratio, placement, generation count, native-cut/continuous-take locks.
- Cast/likeness/voice rights, environment, language and sound route.
- Permitted fiction, forbidden implications and any actual reference footage.
- Revision scope, review_mode, approval_mode and existing selections.

When foundations are missing, ask only what changes the story materially.
Offer an explicitly hypothetical premise for exploration, not invented canon
or a generation-ready package with fabricated references. Do not infer market,
culture, genre or cast from the operator. Do not invent testimonials or offers.
Reference-derived shot claims require inspected footage; articles and titles
alone do not establish an ad's staging or cut times.

Read [evaluation cases](references/evaluation-cases.md) for a hypothetical
worked package and when evaluating or changing this skill.

## 1. Establish the causal engine

Use these bespoke dramatic definitions consistently, not the textbook meanings:

- **Goal:** the single, unchanging thing the hero fights for, fixing something
  already established and reaching the resolving result as fast as possible.
  The hero is never wrong about the major goal; every scene goal must be a
  causal link toward it. Remove a scene to test whether the chain still holds.
- **Obstacle:** a strong circumstance that jeopardizes a stage or the whole
  goal, not merely a cost. Name exactly what is at risk and local/global scale.
  Obstacle plus stakes makes the necessary move non-optional.
- **Tactic:** a reasonable guess forced by that threat on current, incomplete
  knowledge. The hero may misread circumstances, not be arbitrarily foolish.
  Each failed tactic returns information and reshapes the next move; failure
  without learning is wheel-spinning.
- **Reversal:** a turn against expectation, through one's action flipping
  against its intention, hidden agency being revealed, or the situation
  turning opposite to the tactic's intention.
- **Value Shift:** the audience's changed verdict on a character, triggered
  by a reversal, not the character's mood or a product becoming more valuable.
  Name before-verdict and after-verdict. A turn without this reappraisal is
  inert, not a functioning reversal.

A sequence opens when a specific jeopardy threatens a stage/sub-goal and ends
when it resolves or defeats the hero into a new path. Each resolved sequence,
including nested resolving units, needs a reversal with an audience reappraisal.
A single scene can be pure escalation; an unfinished excerpt is not a failed
resolved sequence. Build a deepening verdict trajectory, not random flip-flops.
Unknown story context limits the judgment; do not invent missing evidence.

## 2. Give the product a causal role

Write `established trouble -> reasonable attempt -> new information ->
changed action -> payoff and audience reappraisal`.
Choose a product role: a supported tool in the attempt, a revealing object,
or a setting/service that enables a documented activity.
The character makes the consequential choice; the product does not magically
solve an unrelated relationship, illness or financial problem.

Test the brand connection: if any unrelated object could replace the product
without changing the action or meaning, strengthen the supported connection.
Do not repair a weak connection by adding a late slogan alone.
For an entertainment-first brief, let behavior pose the opening question.
Product visibility may be early or delayed according to the actual brief.

Map every factual implication to `claim_id / source / wording / conditions /
status / story beat`. Include visual results and comparisons, not only speech.
Keep fictional events distinguishable from factual capability. A whimsical
world can contain fiction without suggesting unproved efficacy.
Generated before/after scenes are not proof; jokes and disclaimers do not
substantiate claims. Keep unsupported numbers, personal histories and awards out.

## 3. Record knowledge, behavior and staging

```text
sequence_id / jeopardy opens and resolves / fixed goal / stakes
beat_id / established evidence or proposed fiction / obstacle and scale
character knowledge before / tactic / returned information / next move
reversal form / audience verdict before -> after / supporting behavior
product role / claim_ids / reveal state / continuity in and out
```

Mark intended audience verdicts as interpretations, not observed audience
research. Show the behavior that enables the reading. A whispered "I'm kind"
does not replace a consequential action. Avoid adding a new character,
unseen doorway or unexplained ability to rescue a weak causal link.
Track who can see or hear the new information and when.

Translate each beat into shootable coverage:

```text
shot_id / source_id / approximate window / causal job
featured character / position / eyeline / prop possession / state_in
visible action / partner response / state_out / knowledge change
size / angle / lens intent / camera path and reason
named light source / key side / quality / motivated changes
reference roles / dialogue / audio owner / transition and handles
```

Use contrast where it clarifies the story: wide for geography, closer for a
decisive action or reappraisal. Do not demand a close-up on every beat.
Give a static camera or repeated framing a reason; preserve requested restraint.
State enough visible end-state detail to support the next shot's continuity.
Distinguish actor movement from camera movement and maintain screen direction.

## 4. Fit the request without changing its unit of work

Keep editorial shots and generated source segments separate. Preserve the
requested generation count, ratio and continuous take. Native cuts inside one
generation are possible only under the selected runtime capabilities; they
do not authorize additional generations. A continuous scene can change meaning
through blocking and eyelines without cutting.

Choose durations from capabilities verified by the caller at runtime.
Prompt timestamps are approximate; frame-exact cuts, beat hits and freeze
frames belong to post. Plan handles for edits without claiming exact timing.
If the story cannot fit locked runtime or speech, explain the conflict and
offer a smaller causal unit or authorized runtime/copy change. Do not silently
drop the payoff, speed up dialogue or split into more paid work.

Respect language and exact dialogue. Allow delivery, reaction and final tail
using measured or language-informed timing, not a universal speaking rate.
Separate native dialogue from any requested audio-first or existing soundtrack
route; do not introduce lip-sync production by default.

## 5. Write the prompt and editorial package

Provide complete per-source prose with subject/bindings, action, environment,
visual style, camera/cuts and audio. Carry knowledge-changing behavior, eyelines,
prop states, named light and end states into the prompt, not just the table.
State literal visible actions rather than asking the model to "show a reversal."
Use authorized words with speaker and language; exclude planning terminology
from dialogue unless the actual script calls for it.

Separate request intent: model selection, ratio, runtime, generation count,
allowed cuts, ordered reference roles and audio route. The caller resolves
live-supported parameters. For silent/post-audio work specify
`generate_audio: false` when supported; otherwise flag the authorized
mute/discard route. Never mix generated and supplied speech unintentionally.

Return an edit handoff with source windows, state-matched boundaries, reaction
holds, sound cues, exact post copy, CTA destination and reference provenance.
All added overlays, CTA, graphic logos, captions and UI are deterministic post.
Inspect printed product markings against selected references throughout.
For exact product appearance propose authorized imagery/compositing rather
than claiming references guarantee fidelity. Use actual placement templates;
unknown safe zones remain unverified.

Protect likeness, voice, footage, music and brand rights. A fictional character
is not a real customer and cannot supply actual-use evidence. Do not disguise
privacy-rejected references. Paid-delivery disclosure is the user's separate
decision under applicable policy, not an invented label or automatic approval.

## 6. Repair and check

For a narrow change state the weakest causal link and smallest affected beat.
Preserve locked goal, facts, casting, ending, count and unrelated shots.
Trace consequences to knowledge, next tactic and adjacent edit boundaries.
Proposed facts stay hypothetical until accepted; do not rewrite history.

Check observable geography, readable action, information order, product reveal
and continuity. Verify each resolved unit has a supported reversal and an
intended before/after character verdict. Do not call a product reveal alone
a value shift. Check claim scope, exact-copy separation and dialogue fit.
Motion needs playback; sound needs listening. Mark absent media untested.
No craft check predicts virality, conversion or platform approval.

Honor review_mode independently of approval_mode; default adds no mandatory
draft or review gate. Strict production checks are caller-owned, as are
rights and disclosure decisions. Return only the needed package or revision.
Optional caller composition may use film-production for execution,
tig-scene-engine for deeper scene audits, seedance-prompt-25 for model grammar,
and acting, camera or exact-graphics specialists. These are prose hints only.
