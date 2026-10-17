# Static Ad Layouts

Focused reference for `static-ad-batch`. Load it before editing a template or
adding a layout. Read [the entrypoint](../SKILL.md) first.

## Template contract

Templates live in `assets/templates/`. The planner fills `{{placeholders}}`;
every value is HTML-escaped except the few blocks the planner builds itself
(`plate`, `claims`, `rows`, `terms`, `legal`), whose text is escaped while
building. An unknown placeholder stops the plan.

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
| `legal` | `<p class="legal" data-copy-key="legal_N">` per applicable brand required line, or nothing |

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
- Every layout template keeps a `{{legal}}` slot in its footer. A custom
  template without it is refused whenever a brand required line applies.

## Brand copy rules

The planner applies the pinned kit's `copy_rules` to deterministic copy, as
the brand-kit consumer contract requires.

**Required lines.** Each `required_lines[]` entry whose `when` condition maps
to the ad's layout is rendered verbatim in the `{{legal}}` slot as
`legal_N` and passed to the renderer as exact copy. A line identical to the
offer `terms` is not repeated. Matching ignores case, repeated spaces and a
trailing period:

| `when` | Layouts |
| --- | --- |
| `always` | every layout |
| `offer shown`, `price shown`, `discount shown`, `promotion shown` | `offer` |
| `comparison shown` | `comparison` |
| `review shown`, `rating shown`, `testimonial shown` | `social-proof` |

Any other condition is not guessed: the plan adds one warning per line, and
the agent decides whether it applies and finishes it in post or as offer
terms. A malformed entry (missing or multi-line `text` or `when`) stops the
plan. Add a condition to `REQUIRED_LINE_CONDITIONS` in the script, with a
test, only when its meaning is unambiguous for a layout.

**Trademark marks.** For each `trademark_marks` name, the planner appends the
mark (`®`, `™` or `℠`) to the first whole-word, case-sensitive mention in the
ad's copy, read in the order headline, other copy, then CTA and terms. A
mention that already carries a mark is left alone, and later mentions stay
plain. Each job records what changed in `trademark_marks_applied`; the
`claims` entries keep the fact text unchanged. Any other mark value stops the
plan. Required lines stay verbatim and are never marked.

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
