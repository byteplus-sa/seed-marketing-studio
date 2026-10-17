# Product-Shot QA

Focused reference for `seedream-product-shot`. Load it after generation or
compositing and before selection. A prompt instruction is not evidence that the
image obeyed it; inspect every sample at delivery size and at thumbnail size.

## Identity

- Shape, proportions, cap or closure, materials and colors match `@Image 1`.
- Exactly the requested count; no duplicate or ghost product, no extra variant.
- Nothing cropped: the product sits inside the frame with the preset's margin.
- Scale is plausible for the stated real-world size and any hands in frame.

## Label legibility

Rule `product_shot.no_generated_label`: an on-product label or mark passes only
when the bound acquired product reference carries it and it matches that
reference letter for letter. Free-standing, corner and end-card logos are post
overlays from the brand kit, never part of a product shot. Any mark not
traceable to the bound reference is a defect.

Record one outcome per sample:

| Outcome | Result |
| --- | --- |
| Readable on-product label carried by the bound acquired reference, matching it letter for letter at delivery size | Pass |
| Label turned away, soft, partial or too small to read, and the brief accepts that | Pass, noted |
| Any readable or near-readable text that differs from the reference, or a mark the reference does not carry: misspelling, invented words, warped or added logo, pseudo-letters | **Fail** |
| Label must be legible but the sample was generated | Fail the route: re-plan as plate + composite with the authorized packshot |

Never repair a label by prompting Seedream again for the text. Composite the
authorized packshot or label area deterministically, as a new versioned render.

## Color match

- **Product colors** match the reference under neutral light; a backdrop color
  must not tint the product body.
- **Backdrop against the brand palette:** run the checker with the kit hex as
  target, for example `--target '#D7261E' --tolerance 12`. Generated backdrops
  drift; record the measured mean border color beside the result. A sample far
  from the kit color fails or becomes a plate to recolor deterministically.
- Never invent a hex the kit does not hold. If the brief asks for a color the
  kit lacks, ask for it.

## White background

1. Run `scripts/white_background_check.py` on the PNG. Defaults: border 1% of
   the shorter side, tolerance 3 per channel, pass at 99% of border pixels.
2. Read the JSON: `matching_share`, `transparent_pixels` (an alpha border is not
   white), and `mean_border_rgb` (a light gray backdrop shows up here).
3. Inspect the image anyway: the check measures only the border. Shadow bands,
   floor lines, vignettes and halos around the product need the eye.
4. Set tolerance, threshold, shadow and fill-share rules from the **current**
   rules of the target marketplace. This workspace holds no verified
   marketplace specification; re-verify before every delivery.

## Hands and people

- Exactly the stated number of hands, five fingers each, a grip that could hold
  the product's weight, no mirrored or merged hands.
- Fingers do not cover the label face unless the preset says so.
- Faces appear only where the preset and brief allow; a recurring person matches
  their approved reference.

## Text and marks elsewhere

- No added text, logos, watermarks or signage anywhere in the frame: only the
  bound reference's own on-product marks may appear.
- Companion objects, plinths and surfaces are plain.

## Composition and use

- The preset's reserved copy area is actually empty.
- The product reads at thumbnail size.
- For `in-use`, the shown operation matches a supported fact and no
  unsupported result is pictured.

## Record

Write the outcome per sample (pass, pass-noted, fail with reason), the checker
JSON where it ran, and the hashes of the reference and the sample. Provider
success sets `review`; selection follows the project approval mode.
