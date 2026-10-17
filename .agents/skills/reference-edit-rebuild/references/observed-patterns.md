# Edit Patterns

Common structures in reference aura, meme, fashion and product edits, with
their HyperFrames equivalents. Use them as a vocabulary for the motion
inventory, not as a spec; the measured reference always wins.

## Common edit formats

| Format | Typical length, size | Structure |
| --- | --- | --- |
| Aura or character reel | 10-15 s, 16:9 or 9:16 | One character in many poses and crops, a cut about every 0.5 s, bold type slammed over the subject, negative-flash frames, collage backgrounds, a circular-mask face close-up, a wide shot that resolves into a black-and-white high-contrast cutout with type curved behind and around the figure |
| Fashion lookbook | 10-15 s, 9:16 | Sticker-outlined cutouts, a lineup of the same figure with bracket markup and a question caption, look counters such as `LOOK 06 / 15`, then short walking-person footage with type slams |
| Palette or colorway | about 11 s, 9:16 | One standing figure cutout, a sequence of palette cards with stepped counters, colored paper shapes behind the figure, the garment color changing per palette |
| Mirror or glass lookbook | about 15 s | Model cutouts on glass-panel and mirror layouts with lookbook captions |
| Explainer-style edit | up to 30 s, 4:3 | Kinetic type, magnifier and bracket callouts, glitch collage over mixed imagery |
| Dark cinematic edit | about 11 s | X-ray figure, keyhole vignette, street and stair footage of a person; reads as generated footage rather than layers |
| Product hype edit | 10-15 s | Photos of one product with kinetic type on the beat, crops and flashes; generated shots only where the product must move in a scene |

## Reading

- Most of each edit is layered motion design: cutouts, crops, type, color
  shapes, masks, flashes, counters and fast cuts on a beat.
- Person-in-motion shots (walking, dribbling) and cinematic street footage are
  generated. This matches the routing split: people-led shots are generated,
  product and graphics segments are layers.
- Outfit color changes in a palette edit can be image edits or color shifts of
  one cutout; decide per project and record it as an asset decision.

## Vocabulary and HyperFrames mapping

| Observed treatment | Build as |
| --- | --- |
| Cut every 0.3–0.6 s on the beat | Timeline segments from the beat grid; no easing between cuts |
| Type slam over the subject | Large display type, scale or translate keyframes with a fast ease-out, text in front of or behind the cutout |
| Type curved around or behind a cutout | SVG `textPath` or CSS 3D transform behind the alpha layer |
| Negative or invert flash | CSS `filter: invert(1)` for one to three frames |
| Black-and-white high-contrast treatment | CSS `grayscale` plus `contrast` on the layer |
| Collage or magazine background | Tiled or scattered image layers with slow drift |
| Circular or keyhole mask | `clip-path: circle()` with animated radius |
| Sticker outline around a cutout | Dilated alpha as a white stroke layer under the cutout |
| Counters and captions (`LOOK 06 / 15`, `palette 02/04`) | Deterministic HTML text, stepped by the EDL |
| Colored paper shapes behind a figure | Flat SVG shapes with parallax offsets |
| Palette or colorway variants | One shared layout with swapped color tokens; garment recolor is a separate asset decision |
| Glitch, shake, scan lines | Short displacement or channel-offset passes, 2–6 frames |

Frame size follows the reference. These edits run from 9:16 to 4:3 and 16:9,
and from about 10 to 30 s.

## Limits of this vocabulary

- Sub-0.5 s details need frame-accurate measurement of the actual reference.
- Beat alignment must be measured from the reference audio.
- How a user's own photos hold up in a treatment shows only in a test build.

## Build lessons from live tests

- **Measure the generated bed.** A prompt asking for 128 BPM and a drop at
  1.9 s produced an irregular roll with the drop near 5.3 s. Cut to measured
  low-band onsets, not to the prompted tempo.
- **Keep curved type clear of the subject.** Text arced behind a cutout is
  hidden by the head and clipped at the frame edges (the layout check reports
  `text_occluded` at 93-100 %). Arc it above the head inside the safe margins,
  or leave a gap around the head.
- **Slam text on the cut frame.** Start each type slam at full opacity on the
  cut frame, or the first frame of every cut reads as empty.
- **Silent takes need muted video clips.** A generated take with no audio
  stream must be marked muted in the composition or the render refuses.
- **Low-resolution crops.** A 480p draft holds up at about 1.8x crop with
  added grain and contrast; beyond that, regenerate at a higher resolution.
