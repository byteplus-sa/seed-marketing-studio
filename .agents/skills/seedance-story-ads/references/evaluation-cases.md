# Offline Evaluation Cases

Use these synthetic cases for reasoning and prompt-handoff checks only.
No example grants production permission, establishes real claims or predicts
audience response. Evaluate semantics; keyword matching is insufficient.

## Hypothetical worked example

The quiet puzzle example below teaches a causal unit, not a default setting
or intensity. Contrast it with this separately authorized fictional premise:
a stagehand must deliver the actor's cue card before an entrance. The expected
hook is empty, ruling out the first search. A colleague blocks the doorway;
the stagehand reaches around, expecting obstruction. The colleague reveals the
card from an approved zip pouch and hands it over, having kept it ready.
The audience reappraises the apparent blocker as a helper. A cue light and
audible stage introduction establish why the entrance cannot wait.

The pouch remains a supported storage object, not a magical solution. One
source can contain the search, confrontation and handoff as internal shots.
Native dialogue and sound are optional according to the brief, not new tasks.

**Weak/repair test:** Looking under three identical empty boxes adds no useful
information after the first search. Remove repetition and make the next action
respond to the returned information. Do not force a reversal into every shot
or invent higher stakes when the user has locked a quiet friendship story.

Brief: a 15-second 16:9 friendship story, one source generation with native
cuts allowed. Product is an unbranded zip pouch. Selected R1 supplies its views;
F1 supports only zipper opening and small-item storage. Fictional characters
A and B have selected authorized identity references R2 and R3. The story and
the short line below are proposed fiction, not a testimonial. CTA is "Explore
the pouch" with supplied destination D1. Runtime support remains to be checked.

Engine: A's fixed goal is finishing the shared puzzle. The missing final
piece locally jeopardizes completion. A looks under the nearby empty puzzle
lid, a reasonable search that rules it out. A then gestures toward B's pouch.
B covers it briefly; A expects obstruction. B opens it and offers the saved
piece to A, revealing helpful hidden agency. The intended audience verdict
on B changes from possessive to thoughtful. A places the piece. This one
resolved sequence has a reversal tied to a character reappraisal.

| Shot | State and action | Camera/light | Product and knowledge |
| --- | --- | --- | --- |
| S1, about 0-5 s | A frame-left checks empty lid; B frame-right rests hand on pouch | Fixed medium two-shot, normal lens, soft window frame-left | Pouch visible; lid search returns no piece |
| S2, about 5-11 s | A gestures; B opens pouch and offers one piece, saying "You should place it." | Closer two-shot with hands visible, same window | Supported zipper action; hidden helpful intent revealed |
| S3, about 11-15 s | A places the piece, B watches | Medium view from same side, same light | Puzzle complete; open pouch stays at B's right |

Complete source prompt:

> Subject: fictional friends A and B from selected @Image 2 and @Image 3 sit
> frame-left and frame-right at a puzzle table. The zip pouch in @Image 1
> retains its silhouette, color and single zipper. Action: in an opening
> medium two-shot A notices one empty puzzle position and checks beneath the
> nearby lid; nothing is there. B rests a hand on the pouch at B's right.
> Around the middle, cut closer on both people and their hands as A gestures
> toward it. B briefly covers the pouch, then opens the zipper, takes out one
> final piece and offers it to A with gentle attention rather than a smirk.
> B says in English, "You should place it." Cut back to the same-side medium
> view as A places it and B watches. End with the completed puzzle and open
> pouch still visible. Environment: quiet room, plain table, no extra puzzle
> pieces or printed props. Visual style: naturalistic, soft window light
> frame-left throughout. Camera: normal-lens perspective, stable eyelines,
> native cuts at approximate beat boundaries, no axis crossing. Audio: native
> authorized fictional dialogue, zipper and piece contact, quiet room tone,
> no music. No added captions, CTA, graphic logos or UI.

Request intent: G1 only, requested 15 s and 16:9 if supported, native cuts,
ordered R1/R2/R3 bindings and native audio. Edit handoff: protect the failed
search, reveal and piece placement; exact cut points are post-owned. Add exact
CTA with D1 only in post after checking the placement template. No product
claim about repairing relationships. Review action/knowledge order and
reference fidelity by playback and speech by listening; currently untested.

## 1. Positive causal story

Input: the worked brief with selected identities, facts, line and reveal deadline.
Pass: return one complete source prompt, coherent geography, supported pouch
action and intended reappraisal of B grounded in B's behavior.
Fail: call the pouch opening itself a value shift or add efficacy claims.

## 2. Missing canon

Input: "Make the next scene resolve it" with an excerpt ending during a search,
but no established goal, prior information or conclusion.
Pass: ask for consequential context; assess the supplied local action only.
An unfinished excerpt is not declared a failed resolved sequence.
Fail: invent a backstory or insist that each individual shot needs a reversal.

## 3. Unsupported emotional cure

Input: "The supplement instantly cures the character's panic, bringing the
family together" with only a packaging reference.
Pass: flag the implied health claim and offer a claim-free fictional action
or a supported product role, keeping unapproved alternatives provisional.
Fail: hide the efficacy implication behind "it's just a story."

## 4. Narrow tactic repair

Input: keep cast, fixed goal, ending and count; repair a repeated search that
returns no information.
Pass: identify that weak link, propose the smallest information-returning
action and trace its consequence to the next tactic.
Fail: change the major goal, invent accepted canon or rewrite all dialogue.

## 5. Routing negative

Input A: a solemn fake employee interview with a delayed camera reframe as
the entire joke. Input B: an authorized customer's exact recorded account.
Pass: distinguish deadpan documentary grammar from testimony ownership.
Fail: impose a dramatic reversal on B or invent customer experience for A.

## 6. Single continuous take

Input: exactly one silent continuous take; a short story with three beats.
Pass: use blocking and visible information changes without cuts, preserve
count and silence, and verify the requested duration at runtime.
Fail: three source generations, compulsory voiceover or exact native cut promises.

## 7. Locked words exceed duration

Input: approved speech measures 24 seconds, runtime is locked to 12 seconds.
Pass: surface the conflict and propose an authorized excerpt or duration
change; retain the existing script until the choice is made.
Fail: promise double-speed natural speech or discard the character payoff.

## 8. Review and observation limits

Input: default review_mode, fixed source count, contact sheet only, exact logo
and an uninspected soundtrack.
Pass: no generation or approval implied by this review; logo goes to deterministic post, printed
markings still need inspection, and motion/audio stay untested.
Fail: claim beat sync or stable product motion from stills, or add a paid probe.
