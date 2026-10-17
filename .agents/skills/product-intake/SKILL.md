---
name: product-intake
description: >-
  Turn a product page URL or user-supplied product images into a reusable,
  sourced product card under elements/<product-id>/: an element.md
  manifest, facts.json with every claim's source URL, verbatim quote, retrieval
  time and status (supported, needs-substantiation, perishable), and acquired
  reference images with SHA-256. Use before writing ad scripts, prop sheets,
  packshots or supers for a real product. Falls back to user-supplied material
  when a page cannot be read; never invents facts or images. Does not generate
  media or write copy.
---

# Product Intake

Build one product card that scripts, prop sheets, packshots and supers can
trust. This leaf skill reads, records and validates; it does not write ad copy,
generate images or approve rights. Compose with `brand-kit` (brand identity),
`seedream-prop-asset` (identity sheet when no usable real image exists) and the
ad-writing skills, which may only use claims that `product_facts.py supported`
prints.

**Rules that never bend:**

1. **Every fact has a verbatim quote and a source.** No quote, no fact.
2. **Only `supported` facts reach copy.** `needs-substantiation` facts stay out
   of scripts, supers, captions and spoken lines until evidence is supplied.
3. **Price, availability and offers are `perishable`** with a retrieval time;
   they are re-verified before any deliverable that shows them.
4. **Parse failure falls back to the user**, not to memory or a model. A page
   that cannot be read yields a card built from user-supplied images and
   statements, or an honest partial card.
5. **Images are acquired, not generated.** Download from the brand's product
   page or take user files; record source and SHA-256.

**Rule `facts.supported_only`:** scripts, supers and captions use only
`supported` facts, or `perishable` facts re-verified within the freshness
window.

**Freshness window:** 24 hours from `retrieved_at` unless the brief records
another window. Record the window used in the deliverable's manifest (for
example a static batch spec's `perishable_max_age_hours`) or in `element.md`;
other skills point here rather than restating a default.

## Card location and contents

```
projects/<campaign>/elements/<product-id>/
  element.md        # element manifest (prop rules, identity, variants, selection)
  facts.json        # validated against the product-facts schema
  ref_01_front.png  # acquired images, hashed in facts.json
  ref_02_back.png
```

`product-id` is lowercase kebab-case and equals the directory name. The record
format is the [product-facts schema](../../contracts/schemas/product-facts.schema.json);
field-by-field examples and status rules are in
[card format](references/card-format.md). Load it before writing a card.

## Workflow

1. **Scope and authority.** Confirm the product, the campaign, and that the
   user may advertise it (own brand, client, or retailer with permission). A
   real brand's packaging and marks stay subject to the element
   identification contract's acquisition and rights rules.
2. **Reuse first.** Look for an existing card for the same product in this
   campaign or a sibling project. Reuse images whose source URL still resolves
   to the same SHA-256; re-check perishable facts; never copy another
   project's approval.
3. **Read the page.** Fetch the product page with the available web reading
   tool. Record every URL in `source.urls` and set `source.parse_status`:
   `parsed`, `partial` (some sections unreadable) or `failed`.
4. **Extract facts.** For each statement worth using, add a fact with
   `fact_id`, `kind`, a short `claim`, the exact `quote`, `source_url` (or
   `source_ref` for a user file), UTC `retrieved_at` and `status`. Classify
   status with the table in [card format](references/card-format.md).
   Efficacy, performance and comparison statements are `needs-substantiation`
   unless the user supplies evidence, recorded in `substantiation`.
5. **Acquire images.** Download product images from the brand's page (or take
   user files) into the card as `ref_NN_<view>.<ext>`, keep the original
   bytes, and record `source`, `sha256`, `retrieved_at` and `view`. Prefer the
   largest clean packshot per view; never upscale, retouch or composite into a
   new "reference".
6. **Write `element.md`** (the manifest name Studio reads) with the element frontmatter from
   [card format](references/card-format.md): identity descriptor from what the
   images show and supported facts state, prop threshold reason, `generation:
   none`, `variants`, `selected_variant: null`, `status: review`, and the
   `facts.json` SHA-256.
7. **Validate:**

   ```bash
   uv run python .agents/skills/product-intake/scripts/product_facts.py validate projects/<campaign>/elements/<product-id>/facts.json
   ```

   Exit 1 prints JSON findings; fix every one.
8. **Inspect and select.** Open each image; confirm it is the right product,
   variant and color, with readable labels and no retailer overlays or
   watermarks. Promote the chosen packshot under the project approval mode as
   described in the element identification contract.
9. **Hand off claims.** Give copywriting steps only the output of:

   ```bash
   uv run python .agents/skills/product-intake/scripts/product_facts.py supported projects/<campaign>/elements/<product-id>/facts.json
   uv run python .agents/skills/product-intake/scripts/product_facts.py supported projects/<campaign>/elements/<product-id>/facts.json --max-age-hours 24
   ```

   The second form adds perishable facts retrieved within the freshness window
   (24 hours by default), for a deliverable that shows a price or offer right
   after re-verification.

## Script reference

| Command | Prints | Exit 1 when |
| --- | --- | --- |
| `validate <facts.json>` | `{"ok", "findings"}`; warnings such as a dropped qualifier do not fail | Schema error, missing source, price/availability/offer not perishable, supported performance or comparison claim without substantiation, future or offset-less retrieval time, duplicate IDs, image missing, outside the card, or hash mismatch, product_id not matching its directory |
| `supported <facts.json> [--max-age-hours H]` | Claims usable in copy, with quote, conditions and source | The file is invalid (no claims are printed from an invalid record) |

Rule IDs: `facts.schema`, `facts.source`, `facts.perishable`,
`facts.substantiation`, `facts.retrieved_at`, `facts.unique`,
`facts.image_contained`, `facts.image_exists`, `facts.image_hash`,
`facts.product_directory`, and the warning `facts.claim_qualifier` (the claim
drops "up to", "as low as", "from" before a number, "starting at", "may" or
"approximately" that its quote carries).

## Failure handling

| Situation | Response |
| --- | --- |
| Page blocked, script-rendered, login or region gated | `parse_status: failed`; ask for product images, a spec sheet or the user's own statements; record them with `source_ref` and `user_supplied` |
| Partial page (no specs tab) | `parse_status: partial`; record what was read and ask only for facts the brief needs |
| Retailer listing instead of the brand's page | Record it, but treat marketplace-written claims as `needs-substantiation` and avoid retailer-watermarked images |
| Only lifestyle images, no clean packshot | Keep them as evidence; suggest a prop identity sheet from the approved images rather than inventing views |
| Conflicting facts across pages | Keep both with their quotes; mark the conflicting claim `needs-substantiation` until the user resolves it |
| User asks to "add some benefits" | Add only quoted, sourced facts; propose wording for missing benefits as an unresolved note, not a fact |
