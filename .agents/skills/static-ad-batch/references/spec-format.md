# Static Batch Spec Format

Focused reference for `static-ad-batch`. Read [the entrypoint](../SKILL.md)
first. Paths in the spec are relative to the asset root (the spec's folder by
default, or `--asset-root`). Font and logo paths inside the brand kit are
relative to the kit file.

## Fields

| Field | Required | Rule |
| --- | --- | --- |
| `campaign` | yes | Lowercase kebab-case; first token of every file name |
| `language` | yes | BCP 47 tag from the brief, written to `<html lang>` |
| `version` | no | Integer 1-99, default 1; becomes `vNN` |
| `brand_kit` | yes | Path to the approved `brand.json` |
| `brand_kit_sha256` | yes | Campaign pin from `brand_kit.py pin` (canonical JSON hash). The planner re-computes it before each run; a missing pin or a mismatch stops the plan |
| `facts` | yes | Path to `facts.json`: a list of facts or `{"facts": [...]}` |
| `perishable_max_age_hours` | no | Number greater than zero, default 24 (the product-intake freshness window). A `perishable` offer fact older than this, undated, or dated in the future stops the plan. Record a different window only when the brief sets one |
| `product` | yes | `{"name", "image"}`; the name is alt text only |
| `background_plate` | no | Text-free plate image, drawn full-bleed with `object-fit: cover` |
| `output_dir` | yes | Folder for entrypoints, stylesheet, contact sheet, manifest |
| `layouts` | yes | Default layouts for every angle |
| `ratios` | yes | Any of `1:1`, `4:5`, `9:16`, `16:9` |
| `angles` | yes | List of angle objects (below) |

## Angle object

| Field | Used by | Rule |
| --- | --- | --- |
| `id` | all | Kebab-case, unique; second token of the file name |
| `type` | all | `demonstration`, `objection-handling`, `discovery`, `experience` or `quantified-comparison` |
| `layouts` | optional | Overrides the spec layouts for this angle |
| `headline` | all | Exact copy, one line, at most 240 characters |
| `cta` | all | Exact copy; a warning is raised when it is not a kit CTA verb |
| `claims` | hero-product, problem-solution | 1-3 fact references |
| `problem` | problem-solution | The audience problem, phrased as a question or observation, not a product claim |
| `comparison` | comparison | `ours_label`, `alternative_label`, 1-4 `rows` of `attribute`, `ours` (fact ref), `alternative` (fact ref) |
| `proof` | social-proof | One fact reference holding real, approved evidence (rating with count, a sourced review) |
| `offer` | offer | One fact reference for the price or discount: `supported`, or `perishable` and retrieved within `perishable_max_age_hours` |
| `terms` | offer, optional | Exact terms line supplied by the brief |

A fact reference matches a fact's `fact_id` (product-facts schema) or its exact `claim` text. The fact's
`claim` text is what appears on the ad. Any status other than `supported`
stops the plan, except a fresh `perishable` fact used as the `offer`;
`needs-substantiation` is always refused. Comparison cells on both sides are fact references because a
statement about an alternative needs the same substantiation as one about the
product.

## Worked spec

Invented brand, neutral setting:

```json
{
  "campaign": "lumo-launch",
  "language": "en",
  "brand_kit": "brand/brand.json",
  "brand_kit_sha256": "<pin printed by brand_kit.py pin>",
  "facts": "elements/lumo-mug/facts.json",
  "perishable_max_age_hours": 24,
  "product": {"name": "Lumo travel mug", "image": "elements/lumo-mug/prop_lumo-mug_packshot_v01.png"},
  "background_plate": "elements/lumo-mug/plate_lumo-mug_color-pop_t02_v01.png",
  "output_dir": "statics",
  "layouts": ["hero-product", "offer"],
  "ratios": ["1:1", "4:5", "9:16"],
  "angles": [
    {
      "id": "stays-hot",
      "type": "demonstration",
      "headline": "Hot at hour six",
      "claims": ["f01", "f02"],
      "cta": "Shop now",
      "offer": "f03",
      "terms": "Ends Sunday. While stocks last."
    },
    {
      "id": "vs-open-cup",
      "type": "quantified-comparison",
      "layouts": ["comparison"],
      "headline": "Six hours, not two",
      "cta": "Get yours",
      "comparison": {
        "ours_label": "Lumo",
        "alternative_label": "Open cup",
        "rows": [{"attribute": "Heat", "ours": "f01", "alternative": "f04"}]
      }
    }
  ]
}
```

This plans 2 x 3 + 1 x 3 = 9 ads and one contact-sheet page.

## Errors

The planner exits 2 with one message and writes nothing when it refuses. Typical
messages: `Claim 'x' has status 'needs-substantiation'`, `Perishable claim 'f03'
is stale`, `Spec brand_kit_sha256 is required`, `Brand kit SHA-256 differs from
the campaign pin`, `Font headline has no recorded SHA-256`, `Font body has no
recorded license`, `Brand kit is missing required tokens: palette.text,
logos.primary`, `Brand kit status must be approved`, `uses the banned word`,
`escapes the asset root`, `Refusing to overwrite existing files`.
