# Static Ad Layouts

Focused reference for `static-ad-batch`. Load it before editing a template or
adding a layout. Read [the entrypoint](../SKILL.md) first.

## Template contract

Templates live in `assets/templates/`. The planner fills `{{placeholders}}`;
every value is HTML-escaped except the few blocks the planner builds itself
(`plate`, `claims`, `rows`, `terms`), whose text is escaped while building. An
unknown placeholder stops the plan.

| Placeholder | Source |
| --- | --- |
| `lang`, `stylesheet`, `ratio_class` | Spec language, shared stylesheet name, `ratio-1x1` etc. |
| `logo_src`, `brand_name` | Kit primary logo (relative URL), kit name (alt text) |
| `product_src`, `product_name` | Spec product image and name (alt text) |
| `plate` | Full-bleed `<img class="plate">` or nothing |
| `headline`, `cta`, `problem`, `proof`, `offer` | Exact copy |
| `claims` | `<li class="claim" data-copy-key="claim_N">` items |
| `ours_label`, `alternative_label`, `rows` | Comparison table header and rows (`row_N_attribute`, `row_N_ours`, `row_N_alternative`) |
| `terms` | `<p class="terms" data-copy-key="terms">` or nothing |

Rules for editing:

- Every visible string is plain text in one element with a unique
  `data-copy-key`; the renderer fails if any key lacks a `--copy` value.
- No scripts, remote URLs, data URLs, animation or transitions; the renderer
  rejects them.
- Brand values enter only through the CSS variables `--brand-primary`,
  `--brand-accent`, `--brand-background`, `--brand-text`, `--font-headline`,
  `--font-body` and `--font-cta`. Do not hard-code brand colors in a template.
  The font variables hold per-role aliases (`brand-headline`, `brand-body`,
  `brand-cta`), not the kit family names.
- Sizes scale from `--unit` (1% of the shorter canvas side), so one template
  serves every ratio.

## Layouts

| Layout | Reading order | Needs |
| --- | --- | --- |
| `hero-product` | logo, headline, 1-3 claims, product, CTA | claims |
| `problem-solution` | logo, problem line, headline as the answer, claims, product, CTA | problem, claims |
| `comparison` | logo, headline, two-column table, product, CTA | comparison rows of supported facts on both sides |
| `social-proof` | logo, proof quote, headline, product, CTA | one supported proof fact |
| `offer` | logo, headline, offer, product, CTA, terms | one supported offer fact, or a perishable one inside the freshness window; optional terms |

Portrait and square canvases stack the areas; 16:9 puts copy left and the
product right.

## Safe zones

The default inset is 6% of the shorter side on every edge. The 9:16 layout
keeps copy inside **14% top, 35% bottom and 6% sides**, the Instagram Reels and
Stories ad safe zone published in the Meta Ads Guide
([Reels](https://www.facebook.com/business/ads-guide/update/video/instagram-reels),
[Stories](https://www.facebook.com/business/ads-guide/update/video/instagram-story);
verified_on: 2026-10-17). Other placements publish different or no pixel
values. Platform specs change: re-verify the target placement before delivery
and adjust the stylesheet in a new version when they differ.

## Adding a layout

1. Add `assets/templates/<layout>.html` following an existing template.
2. Add the layout id to `LAYOUTS` and its copy rules to `layout_content` in
   `scripts/static_batch.py`; any new claim-bearing field must resolve through
   the supported-fact lookup.
3. Add tests for the new field's refusal path.
