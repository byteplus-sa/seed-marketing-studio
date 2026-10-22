# Worked Example

Read for a full sound-led prompt package. All inputs, rights records and cue
measurements below are fictional assumptions for this example. They are not
observations of a real track or facts about a real product.

## Hypothetical brief

Product: Arc case, a small charcoal storage case with one hinged lid and one
front latch. Audience intent: recognize the satisfaction of closing it.
Proposition: make the latch click the sonic identity of the reveal, without
claiming waterproofing, durability, noise performance or storage capacity.

Requested deliverable: 8-second, 9:16 ad direction, 30 fps edit, two source
generations maximum, each planned at 6 seconds if the chosen capability
supports it. No visible singing and no separate audio generation. Product
reveal by 2 seconds; final copy from 6 to 8 seconds.

Assumed supplied inputs:

| ID | Fictional supplied material | Authority |
| --- | --- | --- |
| P1 | Selected front and open-case identity sheet | Shape, hinge, latch and material only |
| F1 | Product card says "Hinged lid with front latch" | This visible mechanism, no acoustic specification |
| A1 | Authorized original 8-second music/Foley master | Exact final soundtrack, unchanged |
| L1 | Approved off-screen sung line "Make room for your day" | Exact creative lyric, no measurable claim |
| B1 | Approved logo and "Explore Arc" copy | Deterministic post graphics |
| R1 | Rights record covers recording, composition, lyric and campaign use | Reuse within that scope, no voice cloning |

The lyric is in the existing master; creating another vocal is not authorized.
The designed click is Foley, not documentary evidence of the product's sound.
No real files, hashes or approvals exist in this documentation example.

## Sonic proposition and measured-cue assumption

"A dry latch click starts the rhythm, the case closure reveals its source,
and one warm tonal resolution leaves the product still for recognition."

Assume a human listened to the fictional A1 master and an editor measured
these events in its selected 0-8 second span. Preserve these as hypothetical
evidence in this example, never as reusable timestamps for another song.
No BPM is asserted; the useful events are not a uniform grid.

| Cue | Master/edit time | Frame at 30 fps | Assumed evidence | Picture relationship |
| --- | --- | --- | --- | --- |
| C1 | 0.800 s | 24 | Heard dry Foley click; onset measured | Simultaneous latch contact target |
| C2 | 2.400 s | 72 | Heard low tonal accent; onset measured | Cut to product-wide view |
| C3 | 3.200-4.900 s | 96-147 | Heard/checked L1 phrase | Hold product; no mouth performance |
| C4 | 6.000 s | 180 | Heard resolving chord | Deterministic CTA enters |

Use nearest-frame rounding with half frames rounded up; retain original
times and record uncertainty when measurements are real. Here all values land
on exact frames. These are editorial targets, not Seedance timing promises.

## Source and edit plan

| Source | Generation intent | Planned final use | Shot and endpoint |
| --- | --- | --- | --- |
| S1 | 6 s, close whole-case action, silent picture | Source 1.2-3.6 s -> edit 0-2.4 s | Closure contact target at source 2.0 s, frame 60 |
| S2 | 6 s, single product-wide move, silent picture | Source 0.2-5.8 s -> edit 2.4-8 s | Gentle approach then hold for the CTA |

S1 leaves 1.2 seconds before and 2.4 after its used span. S2 leaves 0.2
seconds on either side. If actual actions miss these target spans, the
editor inspects usable coverage and proposes only authorized trims; no third
generation or arbitrary master retime is permitted.

Source S1: close whole-case view, slightly elevated front three-quarter angle,
moderate lens perspective, locked camera because latch contact must remain
readable. The latch is foregrounded but the full case is visible from the
opening, meeting the 2-second reveal deadline. A large softbox frame-left
gives a soft highlight; one restrained right-side bounce reveals the material.

Source S2: medium product shot at front three-quarter angle, moderate lens
perspective, slow forward camera travel ending in a hold. Same left softbox
and surface, with no added grade. Maintain full product recognition while
the slower approach creates contrast with the hand action in S1.

## Complete prompts

The ordered reference list for each source contains P1 as `@Image 1`.
There is no audio conditioning reference in this version: the editor owns
exact-master placement. Supplying A1 to the model would require a verified
supported role and an explicit decision, not an invented binding.

### S1

```text
[Material Roles]
@Image 1 defines the Arc case silhouette, charcoal material, single hinged
lid and single front latch. Preserve these identity features.

[Subject + Action]
A hand closes the lid of the case and presses its front latch into contact.
Show the complete case from the opening frame, with the latch foregrounded.
Target the contact at source time 2 seconds, leaving readable action before
and after it. The hand withdraws and the closed case remains supported.

[Scene and Environment]
A plain matte tabletop, with clear separation between fingers, latch and lid.
The hand applies force plausibly; the hinge remains attached.

[Visual Style]
Softbox frame-left with a soft right bounce; restrained reflections reveal
the charcoal material. Close product framing with moderate perspective and
enough depth of field to retain the case outline and contact point.

[Camera Movement/Cut]
One locked, slightly elevated front three-quarter view for 6 seconds.
Stillness makes the small mechanical action readable. No internal cut.

[Audio]
Silent picture. The unchanged authorized master is added in post.
Exact logo, CTA and any lyric captions are deterministic post layers.
```

### S2

```text
[Material Roles]
@Image 1 defines the same closed Arc case, its hinge, latch and material.

[Subject + Action]
The closed case rests on the same tabletop. Its complete silhouette is visible.
A gentle camera approach gives the product presence, then settles to leave
clear space above it for the finishing graphic.

[Scene and Environment]
Use the same plain tabletop and uncluttered background as S1.
The case stays supported and stationary, with its latch facing the viewer.

[Visual Style]
The same large softbox frame-left and soft right bounce shape the charcoal
surface. Medium product framing, moderate lens perspective, readable depth.

[Camera Movement/Cut]
One slow forward move over the first 3 seconds of the 6-second source, followed
by a stable hold. Keep the case fully in frame and the upper graphic area clear.

[Audio]
Silent picture. Post owns the complete authorized music, Foley and off-screen
sung line. All exact logo, lyric and CTA typography stays in post.
```

## Handoff and acceptance

Request intent: two 6-second silent-picture sources, 9:16, chosen supported
resolution; `generate_audio: false` only if verified supported. Current
review and approval modes choose the production path; this package adds no
draft, sample, retry or paid submission.

The editor preserves A1 unchanged and mutes any returned source audio.
Only A1 supplies the click, music and lyric, preventing doubled transients.
Exact CTA "Explore Arc" and B1 logo occupy the selected placement's verified
safe zone from frame 180 through frame 239. A missing placement template
blocks a final layout claim, not this creative prompt draft.

The actual lyric-to-fact review records L1 as non-measurable creative wording
and F1 as the only depicted mechanism. Never add "secure forever" to rhyme.
No caption timing is inferred from ASR alone; approved words and verified
phrase timing govern any requested captions.

The caller must inspect action timing, identity and readable contact, listen
to the final master, verify cue alignment and confirm the final word is intact.
ASR may support coverage checking but cannot prove listening or sonic quality.
No lip-sync check applies because no mouth performance was requested.

Failure example: if contact occurs 0.2 seconds late, preserve A1 and the
two-generation cap. Inspect a permissible source trim and its handles.
If the action cannot align without breaking identity or runtime, report the
miss and request a decision; do not resynthesize the master or add a take.

Delivered here: a hypothetical prompt/edit package only. Generation,
listening, frame inspection, placement validation and final QA are unperformed.
