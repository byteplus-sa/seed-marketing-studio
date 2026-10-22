---
name: seedance-musical-ads
description: Write prompt-only musical and sound-led Seedance ads built around sonic product identity, authorized music and cue ownership. Use for jingles or product-sound choreography, not general music videos, dubbing or generation.
---

# Seedance Musical Ads

Make the product recognizable through an audible signature and a visual
relationship to it. A musical ad sells an evidenced proposition; it is not
an unrelated music video with a logo added at the end.

This is an independent prompt-only leaf. Return treatments, complete prompts
and edit/audio handoffs. Never invoke or require sibling skills, generate or
download media, replace a soundtrack, edit production state, render or publish.
The caller owns capability verification, rights, execution and approvals.

## Inputs and loading

Read the supplied brief, references and existing locks. Resolve:

- Product identity, supported facts, desired audience reaction and next action.
- Exact approved copy, lyrics, language, pronunciation and prohibited wording.
- Requested form: product-sound motif, jingle, sung demonstration, rhythmic
  action, soundscape-led reveal or a custom sound-led proposition.
- Audio source, authorized recording/composition/lyrics and campaign use;
  existing sonic logo or sound mark, performer and voice consent where needed.
- Available listening evidence, measured cue map, selected master span,
  sample rate/duration and any supplied tempo metadata.
- Runtime, ratio, placement, reveal deadline and finishing hold.
- Native or supplied-master audio, optional visible singing/lip sync,
  separate-audio authorization, allowed editing and generation count.
- Requested output scope and what must remain unchanged during a revision.

Missing audio does not block an untimed concept. Missing required lyrics,
rights or claim evidence blocks a ready-to-submit label. Ask for consequential
gaps; mark the rest provisional. Do not invent file bindings, a language,
market, song, singer, beat map or evidence of having listened.

Read [worked example](references/worked-example.md) for a complete package.
Read [evaluation cases](references/evaluation-cases.md) when revising or
testing this skill. Both are hypothetical, not evidence for a real product.

## 1. Find the sonic product identity

Choose the product's audible anchor before choosing a genre. It may be:

| Anchor | Advertising relationship |
| --- | --- |
| Real mechanism | A latch, switch or movement reveals a supported function |
| Material contact | A touch, fold or set-down makes texture noticeable |
| Use ritual | A repeated action connects recognition to everyday context |
| Authorized sound mark | The established motif provides brand recognition |
| Invented musical metaphor | A clearly designed sound expresses the concept |

Distinguish recorded product sound from designed Foley or a proposed motif.
Do not present a synthetic click as proof of actual acoustic performance.
For a silent product or service, a musical metaphor is valid; it must not
invent a physical mechanism, operational result or sensory claim.

Write a sonic proposition: "When [event] sounds, [visual action] reveals
[supported quality or non-factual feeling], ending on [next action]."
Define timbre, attack, decay, density, silence and recurrence. Explain why
the motif belongs to this product rather than adding generic cut whooshes.
Avoid imitating a named artist or copying an unlicensed recognizable jingle.

## 2. Establish the audio authority

Select one route and allocate ownership per sound layer.

| Route | Prompt intent | Final ownership |
| --- | --- | --- |
| Native sound-led ad | Direct original native music/Foley/voice as requested | Native audio is a candidate requiring listening |
| Authorized supplied master | Picture follows the measured master events | Preserve the original master unchanged; post owns exact soundtrack |
| Requested separate audio | Return a separate original sound/lyric brief only within explicit scope | Caller creates/selects audio, then measures it before dependent picture |
| Hybrid | Name exactly which native ambience or effects may supplement a master | Post owns the mix and removes duplicates |

Do not turn a sound-led request into separate lip-sync audio production by
default. Visible singing/lip sync is opt-in, and authorization to create a
separate vocal track is a distinct decision. A voice-over or off-screen jingle
does not require a visible singing performer.

Keep an authorized master, its source span and hash as the delivery authority.
Do not replace, resynthesize, stretch, truncate lyrics or loop it without
permission. Derivatives preserve the untouched source and record every edit.
Timing conditioning does not guarantee faithful audio reproduction.

For exact-master picture, express silent-generation intent and
`generate_audio: false` only if supported. If an authorized route returns
audio anyway, assign muting/discarding that stream to post. Do not stack the
master with native music accidentally. Native tests may request
`generate_audio: true` when supported and explicitly selected.

Direct `@Audio N` binding is conditional on verified current reference roles
and parameter combinations. Do not invent a timing-carrier workaround when
the role is unsupported; mark the requirement unresolved. Keep provider
parameters separate from the prose prompt.

## 3. Build a cue map from evidence

Distinguish three evidence classes in every timing record:

1. Perceived: actual native/tool audio perception or documented human listening,
   identifying timbre, phrase boundary, silence or accent.
2. Measured: time in the selected master, source offset, duration and frame
   mapping at the chosen edit fps, with method and uncertainty.
3. Proposed: a desired visual or native-generated sound event, not a measurement.

ASR is a transcript aid, not listening proof. A waveform peak alone does not
identify a snare, a word, musical intent or intelligibility. A genre name does
not establish BPM. Preserve supplied tempo as supplied unless verified;
rubato, irregular accents and silence do not need a forced beat grid.
Without the track or reliable cue evidence, use event-relative direction and
mark synchronization unresolved rather than inventing exact cue times.

For each cue record source time, edit time, evidence, sound event, visual
event, lead/simultaneous/trail relationship and native/post owner.
Convert verified events to edit frames with a recorded rounding convention;
retain original timestamps. A frame target is editorial, not a guarantee
that a generated action will occur at that frame.

## 4. Design the advertising arc

Connect hook, viewer motivation, development, payoff and product role through
sound. Explain how the motif changes: layering, call-and-response, timbral
contrast, interruption or a return with changed meaning. Repeating one click
under static product coverage is not automatically musical development.
Let sound cause or organize visible action without cutting on every beat.
Silence and a quiet return are valid resolutions; crescendo is not mandatory.
Keep rights and measurement bookkeeping in the handoff, carrying only the
selected audible/visible events and essential constraints into the prompt.

Let a first distinctive sound create curiosity, reveal its product connection,
develop the motif and resolve into a recognizable finish. This is adaptable,
not a required four-shot pattern. Hold through an accent when counterpoint
serves the message; not every beat needs a cut.

For each shot state purpose, subject state, action, start/end composition,
size, angle, lens intent, camera path and named light source with key side.
Explain static framing when it lets a mechanism or mouth remain readable.
Make the sonic hook visible enough to connect with the product.

Maintain the approved reveal deadline and allow time for exact post copy.
Keep overlay text, logo, CTA, price, lyric captions and exact UI in
deterministic post. Inspect on-product markings against the selected source;
conditioning alone cannot guarantee them.

Lyrics and spoken lines preserve approved wording. Map each factual line,
including sung efficacy, speed, price or comparative language, to its source
and conditions. A rhyme is not permission to strengthen a claim. Visual
results and designed sound can also imply unsupported performance.
Unsubstantiated lines stay out of production wording; offer claim-free
alternatives explicitly as proposals, not silent replacements of locked copy.

## 5. Write complete prompts

Use subject, action/event, environment, visual style, camera/cuts and audio.
Declare real ordered reference roles only when the caller supplies them.
Carry the per-shot facts into each prompt, not only into a planning table.

Keep native audio direction mutually coherent: use requested music in
parentheses, exact sung/spoken words in braces and sound effects in angle
brackets, or a clear silent-picture instruction for a post-owned soundtrack.
Do not request native singing and silence in the same prompt.

For opted-in visible performance, state speaker identity, exact words,
verified phrase windows, mouth visibility and delivery. Missing timing
permits an ordered lyric draft, not fabricated measured intervals.
Replacing a soundtrack does not repair mismatched visible mouth movement.

Separate source-generation segments from editorial shots. Preserve an
explicit generation count or unbroken take. Native cuts and native cue timing
are approximate; do not promise exact sync by adding more prompt timestamps.
Choose source durations and handles from the actual action and supported
limits. Do not authorize extra takes, samples or automatic drafts here.

## 6. Hand off the sound-led edit

Return this contract for a full package:

```text
sonic proposition / product anchor / real sound or designed metaphor
evidence and rights gaps / exact lyric-to-fact map / selected source roles
audio route / unchanged master identity and source span / separate-audio scope
cue map with original times, edit frames, evidence and uncertainty
shot sequence / source-generation count and durations / full prompts
per-layer native/post ownership / muting and mix instructions
exact graphics inventory / caption words and timing authority
acceptance criteria / observed limitations / unresolved decisions
```

The caller uses the existing shot-plan fields when needed rather than making
a competing plan. Keep provider source IDs distinct from internal shot IDs;
carry timing and audio ownership alongside that record.

For a narrow change, return only the revised prompt/cue rows and affected
handoff fields. Preserve the authorized master, approved words, count, visual
direction and unrelated cues. A changed lyric or master invalidates dependent
timing; flag remeasurement instead of carrying stale timestamps forward.

## Self-check and caller boundary

Check that the motif is product-specific, claims are supported, missing
evidence stays visible, master ownership is explicit and exact graphics stay
in post. Confirm the prompt agrees with its audio parameter intent.

Actual QA requires playback plus listening, transcript comparison where
useful, cue alignment and visible mouth review when opted in. Record a
failure's phrase/frame and propose a bounded repair; do not claim success
from ASR, stills, a provider response or a prompt alone.

Current `review_mode` and `approval_mode` govern downstream production.
No forced drafts, review reports, new approval policy or paid generation
comes from this leaf. Rights, budget and disclosure remain separate.

Optional prose hints for the caller: `seedance-music-video` covers a song-led
artist film; `seed-audio-prompt` covers original audio wording;
`seedance-motion-design` covers exact-graphic-led messaging;
`film-production` covers execution. These are not dependencies or instructions
to load or invoke siblings.
