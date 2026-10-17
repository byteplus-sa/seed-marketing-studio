# Product card format

Load this before writing or editing a product card. The examples use an
invented product.

## Status classification

| Statement on the source | `kind` | `status` |
| --- | --- | --- |
| Name, capacity, dimensions, materials, included items, care instructions | `name`, `specification`, `material`, `usage` | `supported` when quoted from the brand's own page or the user's spec sheet |
| A visible feature the camera can show ("flip-top lid with carry loop") | `feature` | `supported` |
| Colors and sizes offered | `variant` | `supported`; check each against images |
| Certifications and standards ("BPA-free", a test standard) | `certification` | `supported` only when the brand states it; the claim keeps its exact wording |
| Efficacy, results, durations of effect ("keeps drinks cold for 24 hours") | `performance` | `needs-substantiation` unless the user supplies evidence; then `supported` with `substantiation` and `conditions` |
| Comparatives and superlatives ("lighter than other bottles", "best") | `comparison` | `needs-substantiation` unless substantiated, with the comparison basis in `conditions` |
| Price, sale price, stock, shipping time, promo codes, bundles | `price`, `availability`, `offer` | always `perishable` |
| Reviews, star ratings, review counts, testimonials | `other` | `needs-substantiation`; real reviews also need permission before use |

A brand stating a performance claim on its own page does not make it safe to
repeat in an ad; the advertiser still needs substantiation. Keep the claim, its
quote and source, and wait for evidence.

`conditions` carries the scope a claim holds under ("with the lid closed, at
room temperature"). Copy that uses a claim keeps its conditions.

## facts.json example

```json
{
  "schema_version": 1,
  "product_id": "trailblend-bottle",
  "product_name": "TrailBlend Insulated Bottle 750 ml",
  "brand_id": "trailblend",
  "source": {
    "method": "product_page",
    "urls": ["https://trailblend.example/products/insulated-bottle"],
    "parse_status": "parsed"
  },
  "facts": [
    {
      "fact_id": "f01",
      "kind": "specification",
      "claim": "Holds 750 ml",
      "quote": "Capacity: 750 ml (25 fl oz)",
      "source_url": "https://trailblend.example/products/insulated-bottle",
      "retrieved_at": "2026-10-17T09:30:00Z",
      "status": "supported"
    },
    {
      "fact_id": "f02",
      "kind": "performance",
      "claim": "Keeps drinks cold for 24 hours",
      "quote": "Double-wall insulation keeps drinks cold for up to 24 hours.",
      "source_url": "https://trailblend.example/products/insulated-bottle",
      "retrieved_at": "2026-10-17T09:30:00Z",
      "status": "needs-substantiation",
      "conditions": "lid closed; ambient conditions not stated"
    },
    {
      "fact_id": "f03",
      "kind": "price",
      "claim": "Priced at 32.00",
      "quote": "32.00",
      "source_url": "https://trailblend.example/products/insulated-bottle",
      "retrieved_at": "2026-10-17T09:30:00Z",
      "status": "perishable"
    }
  ],
  "images": [
    {
      "file": "ref_01_front.png",
      "source": "https://trailblend.example/cdn/bottle-sage-front.png",
      "sha256": "<64 lowercase hex>",
      "retrieved_at": "2026-10-17T09:31:00Z",
      "view": "front, sage color"
    }
  ]
}
```

A user-supplied fact replaces `source_url` with `source_ref` (for example
`"user_supplied: spec-sheet.pdf p.2"`) and the quote is the exact sentence from
that file or the user's chat message. A user-supplied image uses
`"source": "user_supplied"`.

Image files are plain names beside `facts.json`, matching
`ref_NN_<view>.<ext>` (png, jpg, jpeg or webp).

## element.md example

```markdown
---
element_id: trailblend-bottle
category: prop
element_type: product
name: TrailBlend Insulated Bottle 750 ml
brand_id: trailblend
prop_threshold: branded
source: web_download
generation: none
facts_file: facts.json
facts_sha256: <sha256 of facts.json>
identity_descriptor: >-
  matte sage-green double-wall steel bottle, straight cylinder, brushed steel
  flip-top lid with a black carry loop, small white wordmark on the front
variants:
  - prop_trailblend-bottle_front_v01.png
selected_variant: null
status: review
---

# TrailBlend Insulated Bottle 750 ml

- Threshold: branded and recurring across all hero shots, so a locked
  reference is required.
- Views on file: front (ref_01), back (ref_02). No side view on the page.
- Open questions: substantiation for f02; current price before any price super.
```

Rules for `element.md`:

- `element_id` equals the folder name; `category: prop` and the prop threshold
  reason follow the element identification contract.
- `identity_descriptor` describes only what the selected images show and
  supported facts state. It is copied word for word into later prompts.
- `source` is `web_download` or `user_supplied`; `generation: none`.
- The promoted packshot is a byte-identical copy of the chosen `ref_NN_*`
  file under the canonical `prop_<product-id>_<view>_v<NN>.<ext>` name, listed
  in `variants`. Its SHA-256 equals the ref's recorded hash.
- `facts_sha256` changes whenever `facts.json` changes; downstream scripts that
  used older facts are revalidated.
- `selected_variant` and `status: approved` are set only by a
  mode-authorized decision after visible inspection.
