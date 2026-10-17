---
name: static-ad-batch
description: >-
  Plan a grid of static ads as selling angle x layout x ratio, with exact copy
  from supported product facts, brand-kit palette, type and logo, five starter
  HTML templates (hero-product, problem-solution, comparison, social-proof,
  offer) and ratios 1:1, 4:5, 9:16 and 16:9, rendered by the deterministic HTML
  renderer with a contact sheet and per-file provenance. Use for batches of
  static social or display ads. Do not use for video, single bespoke posters,
  or copy that lacks supported facts or an approved brand kit.
---

# Static Ad Batch

Expand a spec into one HTML entrypoint per ad, named
`{campaign}_{angle}_{layout}_{ratio}_v{NN}`, plus a shared stylesheet, a
contact sheet and a batch manifest. Every word on the ad is exact DOM text,
every claim maps to a `supported` product fact, and every color, typeface and
logo comes from the approved brand kit. Seedream is used only for an optional
text-free background or lifestyle plate. This is a leaf capability: the planner
writes files and prints render commands; it does not render, generate imagery,
or approve a result.

Compose with: `ugc-ad-modes` for the angle table and persuasion brief,
`seedream-product-shot` or `seedream-prompt` for the plate, and
`html-graphic-render` for rendering and its render records. Mentions are hints,
not instructions to load those skills.

## Inputs

| Input | Rule |
| --- | --- |
| Brand kit | `brand.json` with `status: approved`, palette roles `primary`, `background`, `text` (optional `accent`), typography roles `headline` and `body` (optional `cta`) with local font files, and a `primary` logo file. Shape: `.agents/contracts/schemas/brand-kit.schema.json`. A campaign may pin it with `brand_kit_sha256`. |
| Product facts | `facts.json` from product intake. Only facts with `status: supported` can appear. Shape: `.agents/contracts/schemas/product-facts.schema.json`. |
| Product image | The approved packshot, preferably with true alpha. Never a generated label. |
| Angles | From the `ugc-ad-modes` angle table: `demonstration`, `objection-handling`, `discovery`, `experience`, `quantified-comparison`. Each angle is a different viewer question, not a synonym. |
| Plate | Optional, text-free, selected and hash-bound. Leaves room for copy. |
| Language | A BCP 47 tag from the brief. No market or language is assumed. |

Missing inputs stop the plan with a clear error; the planner never invents a
color, font, claim or logo.

## Procedure

1. **Gather approved inputs.** Brand kit, facts, packshot, optional plate. A
   draft kit or unreviewed facts go back to their owners first.
2. **Write the angles.** For each angle pick claim references from the facts,
   a headline and a CTA. A headline is creative copy that must not assert
   anything beyond the referenced supported claims; review it like any claim.
   Prefer CTA verbs from the kit.
3. **Write the spec.** Load [spec format](references/spec-format.md) for fields,
   layout requirements and a worked spec.
4. **Plan.**

   ```bash
   uv run python .agents/skills/static-ad-batch/scripts/static_batch.py \
     plan projects/example/static_batch.json --asset-root projects/example
   ```

   The asset root must contain the spec's brand kit, facts, packshot, plate and
   output folder; for a shared brand library outside the project, pass a root
   that covers both. The planner refuses unsupported or unknown claims, missing
   brand tokens, a draft or re-pinned kit, banned words from the kit, unknown
   layouts or ratios, paths outside the root, and existing outputs (raise
   `version` or pass `--overwrite` for a repair).
5. **Render.** Run each printed command from the repository root. Each passes
   the exact copy as `--copy KEY=TEXT` and the headline family as
   `--require-local-font`, so the renderer fails on copy drift or font
   fallback, and writes `render_<name>.json` beside each PNG.
6. **Contact sheet.** Render the `contact_*` commands last; they reference the
   ad PNGs.
7. **QA and record.** Inspect each ad at delivery and thumbnail size, then
   record the batch manifest and render records in the project. Ads enter
   `review`; selection follows the project approval mode.

## Layouts and ratios

Load [layouts](references/layouts.md) before editing templates or adding a
layout. Templates live in `assets/templates/`: one HTML file per layout, the
shared `static-ad.css` with brand tokens as CSS variables, and
`contact-sheet.html`. Copy them into a project only when a campaign needs a
custom variant, and keep `{{placeholders}}` and `data-copy-key` nodes intact.

| Ratio | Canvas | Token |
| --- | --- | --- |
| 1:1 | 1080 x 1080 | `1x1` |
| 4:5 | 1080 x 1350 | `4x5` |
| 9:16 | 1080 x 1920 | `9x16` |
| 16:9 | 1920 x 1080 | `16x9` |

Canvas sizes are workspace defaults, not platform rules. Placement specs and
safe zones change; re-verify them for the target placement before delivery.

## Outputs

In the spec's `output_dir`:

- `{campaign}_{angle}_{layout}_{ratio}_v{NN}.html` per ad, then `.png` and
  `render_*.json` after rendering;
- `static_{campaign}_v{NN}.css`, the brand stylesheet;
- `contact_{campaign}_pNN_v{NN}.html`, twelve angle-layout rows per page;
- `batch_{campaign}_v{NN}.json`, the manifest: input hashes (kit, facts,
  packshot, plate, logo, fonts, templates, stylesheet), per-job copy, claim
  sources, sizes and render commands, plus warnings such as perishable offers
  or a CTA outside the kit's verbs.

Record the batch as `source: deterministic_render`, `generation:
deterministic_html`. A plate keeps its own prompt, review, task and selection
evidence. Deterministic ads do not take the three-sample default.

## QA

Before selection, check each rendered ad:

1. Copy matches the spec letter for letter; every claim traces to a supported
   fact with a source; perishable offers were re-checked.
2. Brand fonts loaded; no fallback, overflow or clipped text; the logo is
   undistorted and on an allowed background.
3. The product is whole, unobstructed and readable at thumbnail size.
4. Copy and CTA sit inside the placement's safe zone; 9:16 uses the stricter
   layout in [layouts](references/layouts.md).
5. The plate carries no text and does not fight the copy for contrast.
6. Disclosure or legal lines the brief or kit requires are present.
