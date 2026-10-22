# Worked Example

Read for a complete match-cut package. This is hypothetical craft direction:
all source files, permissions, coordinates and timings are assumptions or
targets, not verified generated footage.

## Brief and identity

Fictional product: Halo pendant lamp with a smooth circular white diffuser.
Message: find a recurring circle in an everyday space, then recognize the
lamp. No lumen, energy-saving, comfort or durability claim.

Requested package: 10 seconds, 16:9, 30 fps, exactly two 6-second source
generations if supported, two internal editorial shots, one shape match hard
cut at 5 seconds. No literal morph, dissolve or extra generation. Quiet
post-owned sound from an already authorized 10-second master. Full product
reveal by 7 seconds, exact CTA from 8-10 seconds.

Assumed inputs:

| ID | Hypothetical selected material | Role |
| --- | --- | --- |
| P1 | Authorized lamp underside and three-quarter photographs | Product identity, proportions and visible material |
| F1 | Product card says "Circular white diffuser" | Only shape/material fact used |
| E1 | Approved simple room reference | Wall tone and tabletop context |
| B1 | Logo file and exact "Explore Halo" CTA | Deterministic post |
| A1 | Authorized 10-second score | Unchanged final master, no measured beat claim |

The opening circle is a plain paper disc lying on a table, not the lamp
becoming paper or a claim that paper is its material. Transition meaning:
recognition through a repeated shape. Explain this as an editorial visual
association, not a physical transformation.

## Source ledger

Use half-open time intervals. At 30 fps, source frame indices start at zero.
Keep original sources; the editor uses derived spans without overwriting them.

| Source | Planned length | Used source interval | Final interval | Handle budget |
| --- | --- | --- | --- | --- |
| S1 | 6 s / 180 frames | [0.5,5.5) / [15,165) | [0,5) / [0,150) | 0.5 s each side |
| S2 | 6 s / 180 frames | [0.5,5.5) / [15,165) | [5,10) / [150,300) | 0.5 s each side |

There are two provider sources, not two sources per endpoint. Final cut is
between edit frames 149 and 150. Outgoing source frame 164 and incoming
source frame 15 are the nominal pair; actual usable frames require inspection.
Keep the static match readable across S1 source 4.8-6.0 seconds and S2 source
0-1.2 seconds so the editor has limited alignment freedom.

## Endpoint contract M1

Coordinates normalized to the full 1920 x 1080 frame; origin top-left,
x right and y down; in-plane rotation clockwise in degrees.

| Property | S1 outgoing | S2 incoming |
| --- | --- | --- |
| Anchor | Outer edge of paper disc | Outer edge of lamp diffuser |
| Center | (0.50, 0.48) | (0.50, 0.48) |
| Bounding dimensions | width 0.25, height 0.444444 | width 0.25, height 0.444444 |
| Pixel dimensions | 480 x 480 | 480 x 480 |
| Orientation | 0 degrees, plane parallel to sensor | 0 degrees, diffuser plane parallel to sensor |
| Perspective | Overhead perpendicular view | Underside perpendicular view |
| Light | Soft area source image-left, shadow right | Soft area source image-left, comparable edge highlight |
| Exposure | White with visible edge, no blown highlight | Same edge readability, practical lamp initially off |
| Motion | Subject and camera stationary at endpoint | Subject and camera stationary at endpoint |
| Occlusion | Entire rim unobstructed | Entire rim unobstructed |

The normalized height differs from width because the frame is not square.
Equal normalized width/height would produce an ellipse, not a circular match.
The physical camera directions change deliberately at the cut; the projected
contour, light direction and screen position are the matching authorities.

Proposed editorial tolerance: anchor centers within 1% of frame width and
height; contour diameter within 2% after at most a 2% uniform rescale.
These are project-specific targets requiring visual acceptance, not API
precision claims. For symmetric circles rotation is visually underdetermined;
the light-side anchor and shadow orientation still must match.

Authorized post operations: source trim within available holds, translation
within that 1% tolerance and uniform rescale up to 2%, without cropping the
rim. No nonuniform distortion, optical-flow retime, added morph or score edit.
Editor owns frame-exact placement; Seedance owns source picture only.

## Complete source prompts

### S1, paper circle

Ordered references: E1 as `@Image 1` for room/table context only.

```text
[Material Roles]
@Image 1 supplies the tabletop and room palette, not product identity.

[Subject + Action]
A single plain white paper disc rests flat on the tabletop. A slow overhead
camera approach discovers its circular outline, then stops and holds it.
The last 1.2 seconds keep the complete disc unobstructed and motionless.

[Scene and Environment]
An uncluttered tabletop, one disc only, physically supported with a subtle
contact shadow. The paper remains paper throughout the source.

[Visual Style]
A large soft area light image-left casts a soft shadow to image-right.
The camera looks perpendicular to the disc, with moderate lens perspective
and the entire rim in focus. White retains detail rather than clipping.

[Camera Movement/Cut]
One 6-second source, no internal cuts. Move slowly closer over the early
portion, settling before 4.8 seconds. At the final held endpoint the disc
center is (0.50,0.48) in the full frame; its bounding width is 0.25 and height
0.444444 of the frame. The plane is parallel to the sensor, rotation 0 degrees,
and both subject and camera have zero screen-space motion during the hold.
These are composition targets for the editor to inspect.

[Audio]
Silent picture; an unchanged authorized score is added in post.
Exact branding and typography belong to deterministic post layers.
```

### S2, product reveal

Ordered references: P1 as `@Image 1` for lamp identity, E1 as `@Image 2`
for room context. A storyboard grid is not an input.

```text
[Material Roles]
@Image 1 defines the Halo lamp geometry, white diffuser and visible mounting.
@Image 2 defines room context only.

[Subject + Action]
Begin directly underneath the stationary lamp with its circular diffuser
filling the matched opening composition. Hold this view for 1.2 seconds.
Then pull back and arc gently toward a three-quarter view to reveal the whole
lamp and its mounting. Settle by source time 2.5 seconds and retain a clear
upper-right area for the finishing graphic through the end.

[Scene and Environment]
The lamp remains fixed to its mounting in the approved simple room.
The practical lamp is off; this shot claims shape and material, not brightness.
The camera has clear travel space and never intersects the lamp or ceiling.

[Visual Style]
Soft area light image-left keeps the rim highlight and right-side shading
comparable to the preceding disc. Moderate lens perspective, the complete
diffuser edge in focus at the opening, with the product readable on retreat.

[Camera Movement/Cut]
One 6-second source, no internal cuts or visible transformation. The opening
held diffuser center is (0.50,0.48), bounding width 0.25 and height 0.444444 of
the full frame, plane parallel to the sensor, rotation 0 degrees. Subject
and camera are motionless until 1.2 seconds. Then execute the described
pullback/arc and settle. The editor makes a hard shape match cut into this
source; the lamp never turns into or grows out of paper.

[Audio]
Silent picture; post owns the existing authorized score.
Exact logo and CTA remain deterministic post graphics.
```

## Editorial and production handoff

Picture: inspect the nominal pair plus neighboring handle frames, choose a
valid pair within scope and cut at edit frame 150. Compare contour overlays,
center, diameter, light and normal-speed continuity. Two plausible endpoint
stills alone do not prove a successful transition.

Audio: preserve A1 unchanged and mute any returned source audio. The 5-second
cut is a design time, not a claimed measured musical accent. If beat sync
becomes required, measure/listen first and revise only the permitted edit.

Graphics: exact B1 logo and "Explore Halo" appear at edit frame 240 and hold
through frame 299. Layout uses the requested placement's verified safe zone;
missing placement data stays unresolved. No text is generated into either shot.

Parameters remain separate: two supported 6-second requests, 16:9, requested
supported resolution, silent-picture intent and `generate_audio: false` only
when supported. Current review and approval modes govern production; the
fixed two-generation cap is not expanded by an automatic draft-first recipe.
If mode requirements and the cap cannot both be met, ask before submission.

Acceptance: recognize the lamp by frame 210, retain P1 geometry, keep a hard
cut rather than a morph, match the readable rim within the agreed tolerance,
preserve A1 and show exact copy. No assertion of a passed take is made.

Failure: if S2 opens obliquely with an ellipse, a 2% rescale cannot repair
perspective. Report the mismatch and keep both sources. Propose either an
authorized alternate cut using existing coverage or a changed production
budget; do not silently add S3 or call the ellipse a successful metamorphosis.

For a literal-morph request instead, this package is insufficient: specify
the intermediate topology/material change, continuous camera and product
identity boundary, and obtain permission for the changed mechanism. Do not
reuse these hard-cut prompts under a new title.
