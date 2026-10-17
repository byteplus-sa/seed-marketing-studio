# Brand kit consumers

Load this when a downstream step needs brand values. Every consumer first
confirms the campaign pin still matches:

```bash
uv run python .agents/skills/brand-kit/scripts/brand_kit.py pin library/brands/<brand-id>/brand.json --expect <pinned-sha256>
```

A mismatch stops the step until the campaign re-pins deliberately and the
dependent outputs are revalidated. `brand_kit.py show` prints the consumer view
used below.

| Consumer | Reads | Never |
| --- | --- | --- |
| Deterministic graphics (`html-graphic-render`, `static-ad-batch`) | `palette`, `typography` files and families, `logos` files with `min_height_px`, `clear_space_ratio`, `allowed_backgrounds`; `cta_style`; `copy_rules.trademark_marks` and `copy_rules.required_lines` (static-ad-batch applies both) | Recolor or redraw a logo; substitute an unlicensed font file |
| HyperFrames supers, lower-thirds, end cards | Same as deterministic graphics; brand fonts load from `assets/fonts/` by local path | Burn brand text into generated footage |
| Seedream and Seedance prompts | `imagery.style_sentence` in the style or visual-style line; `imagery.avoid` as observable positive direction; on-product marks only as carried by a bound acquired product reference | Name the brand, ask for a free-standing, corner or end-card logo, or describe a mark or label text the bound reference does not carry |
| Script and caption writing | `voice`, `cta_style.verbs`, `copy_rules` | Exceed the supported product facts; voice never licenses a claim |
| `prompt-review` | `copy_rules.banned_words` and `copy_rules.required_lines` for every generation-bound prompt and every spoken or on-screen line | Treat a missing required line as optional when its `when` condition applies |
| Delivery and compliance | `disclosure.ai_label_text` and `disclosure.placement` only when the deliverable's recorded disclosure decision requires a label | Add an AI label by default to internal reviews or reels |

## Deterministic graphics

- Copy the needed logo and font files from the library into the project's
  graphic source folder (or reference them by a project-confined path) and
  record their SHA-256 in the render record; they must equal the kit's hashes.
- Respect `min_height_px` at delivery size and `clear_space_ratio` (clear space
  = ratio x logo height on every side).
- Use `allowed_backgrounds` to pick the logo role: `inverse` or `mono` on dark
  or photo backgrounds only when the kit lists that role.
- CTA buttons follow `cta_style.shape` and `cta_style.case`; text color and
  fill come from palette roles `primary`, `text` and `background`.
- Apply `copy_rules.trademark_marks` to the first prominent mention of each
  product name.

## Generative prompts

**One logo rule (`brand.no_generated_logo`)** covers every consumer:

- **Free-standing, corner and end-card logos and wordmarks are always post
  overlays** made from the kit's `logos` files, never generated.
- **On-product marks are allowed only when a bound acquired product reference
  carries them.** The prompt preserves them from that reference and never
  spells them out; QA checks every readable mark letter for letter against that
  reference.
- **A generated logo, wordmark or mark not traceable to a bound reference is a
  defect**, even when it looks right.

Brand identity in footage otherwise comes from style, not from asking the model
to draw a mark (see the element identification contract). Insert the style
sentence verbatim:

```text
Style: <imagery.style_sentence>
```

If `imagery.style_sentence` is null, write the visual style from the brief and
note that the brand kit has no imagery guidance; do not invent one into the kit.

## Prompt review checks

For each prompt or script line:

1. **Banned words**: case-insensitive whole-word match against
   `copy_rules.banned_words` in spoken lines, on-screen copy and prompt text
   that could surface as speech or text. A hit is a MAJOR finding.
2. **Required lines**: for each `required_lines[]` whose `when` condition
   applies to the deliverable (for example a price is shown), the exact `text`
   must appear in the planned post overlay or end card. Missing is a MAJOR
   finding; it is added in post, never generated into footage.
3. **Logo requests** (`brand.no_generated_logo`): any request to generate a
   free-standing, corner or end-card logo or wordmark, or a mark not carried by
   a bound acquired product reference, is a CRITICAL finding. Preserving the
   on-product mark of a bound acquired reference is allowed.
4. **Pin**: the reviewed prompt records the kit pin it used; a different
   current pin invalidates the review.

## Disclosure

The kit only stores the wording and placement. Whether a label is needed is a
per-deliverable decision recorded in the delivery record (platform labels,
jurisdiction rules). The agent asks when the decision is missing and never
assumes either way.
