---
name: seedream-product-shot
description: >-
  Write Seedream prompts for commercial product shots from named presets
  (studio-white, color-pop, editorial, macro-detail, in-use, faceless-hands,
  flat-lay, lifestyle, hero-plinth and marketplace dark, pastel and surreal-3d
  backgrounds), bound to the approved product reference, with label-legibility,
  brand-color and white-background QA. Use for packshots, marketplace images,
  ad backgrounds with the product and lifestyle stills of an approved product.
  Do not use for product identity sheets, exact labels, copy or layouts, or
  products with no approved reference.
---

# Seedream Product Shot

Turn an approved product reference into a commercial still with a named preset.
Product identity comes from the reference images, never from the prompt alone:
this skill does not redraw logos or label text. When a label must be legible,
the exact label reaches the final image through a deterministic composite, not
through generation. This is a leaf capability: it returns a prompt package or a
composite plan and runs QA on candidates; it does not submit generation,
render graphics, or approve a result.

**Logo and label rule (`product_shot.no_generated_label`):** free-standing,
corner and end-card logos and wordmarks are always post overlays from the brand
kit. On-product marks are allowed only when the bound acquired product
reference carries them, and QA checks them letter for letter against that
reference. A generated logo, label or mark not traceable to the bound reference
is a defect.

Compose with: `seedream-prop-asset` for the identity sheet this skill binds,
`seedream-prompt` for imagery outside these presets, `html-graphic-render` for
composites and exact copy, and `static-ad-batch` when the shot becomes the
background plate of a static ad. Mentions are hints, not instructions to load
those skills.

## Source authority

- [Seedream 4.0-5.0 API Tutorial](https://docs.byteplus.com/en/docs/ModelArk/1824121)
- [Seedream 4.0-4.5 Prompt Guide](https://docs.byteplus.com/en/docs/ModelArk/1829186)
- Workspace [element identification](../../contracts/element-identification.md),
  [asset naming](../../contracts/asset-naming.md) and
  [production policy](../../contracts/production-policy.md)

The presets are optional creative heuristics written for this workspace. They
are not platform rules and carry no measured conversion evidence.

## Inputs

| Input | Rule |
| --- | --- |
| Product reference | Required. The selected, hash-bound product card image or prop sheet view in `elements/<product-id>/`, or an authorized packshot. No reference means no prompt: hand back a request to acquire or sheet the product first. |
| Preset id | One of the ids below. Unknown ids are refused, not guessed. |
| Delivery size and ratio | From the brief or the destination; defaults per preset. |
| Label legibility | Does the label have to be readable in the delivery? Decides the route. |
| Brand palette | Optional. Hex values and roles from the approved brand kit. Backdrop colors come only from the kit or the brief, never invented. |
| Brand imagery sentence | Optional. The kit's imagery style sentence goes into Style word for word. |
| Supported facts | Required for `in-use`: the shown operation must be a supported fact. |
| People | `in-use`, `faceless-hands` and `lifestyle` may show people. The brief sets who; a recurring person needs an approved character reference; real people follow the workspace rights rules. |

## Choose the route

| Situation | Route |
| --- | --- |
| A clean authorized packshot with alpha exists and the preset is `studio-white` | No generation. Composite the packshot on `#FFFFFF` with the deterministic renderer, then run the white-background check. |
| Label must be legible and the product faces camera | **Plate + composite.** Generate the set as an empty plate (the product slot left clear, light direction and shadow area described), then place the authorized packshot deterministically. |
| Label must be legible but no clean packshot exists | Stop and ask for one. Do not let Seedream write the label. |
| Label need not be readable (turned, partial, soft focus, small in frame) | **Generated I2I.** Bind the reference; QA fails any readable text that differs from the reference. |

Every generated route is Image-to-Image with the product reference first. Never
run a product shot as Text-to-Image.

## Presets

Load [presets](references/presets.md) for the prompt block of the chosen preset.
Each preset fixes background, lighting, composition, default ratio and route.

| Id | Use | Default ratio, size | Default route |
| --- | --- | --- | --- |
| `studio-white` | Marketplace main image, catalog | 1:1, `2048x2048` | Composite, else generated |
| `color-pop` | Social feed, brand-color backdrop | 4:5, `1728x2160` | Plate + composite |
| `editorial` | Magazine still life with styled props | 4:5, `1728x2160` | Generated |
| `macro-detail` | Material, texture or mechanism close-up | 1:1, `2048x2048` | Generated |
| `in-use` | The product doing a supported job | 4:5, `1728x2160` | Generated |
| `faceless-hands` | Hands holding or operating, no face | 4:5, `1728x2160` | Generated |
| `flat-lay` | Top-down arrangement with companions | 1:1, `2048x2048` | Plate + composite |
| `lifestyle` | Product placed in the audience's setting | 16:9, `2816x1584` | Generated |
| `hero-plinth` | Product on a sculpted plinth, premium light | 4:5, `1728x2160` | Plate + composite |
| `marketplace-dark` | Dark seamless secondary image | 1:1, `2048x2048` | Plate + composite |
| `marketplace-pastel` | Soft pastel seamless secondary image | 1:1, `2048x2048` | Plate + composite |
| `marketplace-surreal-3d` | Stylized 3D scene with soft geometric forms | 1:1, `2048x2048` | Generated |

Sizes sit inside the documented Seedream pixel range; confirm the live limits
before submission. A static-ad plate takes the ratio of the ad it backs.

## Prompt rules

- **References first.** `@Image 1` is the product reference. Bind it where it
  controls the output: "Use the exact shape, proportions, materials, colors and
  label layout of the product in @Image 1."
- **Copy the approved product descriptor word for word** into Subject. Count:
  "one product only" unless the brief asks for a set.
- **No new text.** Never quote label copy, slogans, prices or logos in the
  prompt. Add "no added text, letters, numbers or logos beyond the product's own
  label" to Constraints.
- **Brand color in words and hex.** "a saturated red seamless backdrop, hex
  `#D7261E`". Measure it after generation; models drift.
- **Plates leave the slot clear.** Describe the empty surface, the light
  direction and where the contact shadow will fall, at the size the product
  will occupy, so the composite reads as one photograph.
- **Supported action only.** `in-use` shows an operation listed as supported in
  the product facts. An imagined result (glowing skin, a spotless floor) is a
  claim and needs its own supported fact.
- **No market assumed.** Settings, hands and people follow the brief.
- **Ad-ready space.** When the shot will carry copy later, reserve the empty
  area in Composition ("upper third left clear for copy").

## Selection set

Default to **three stochastic samples** per selection set with identical prompt,
references and parameters except the seed. An explicit count or a requested
creative alternative overrides the default. A deterministic composite produces
one render per version and never takes the three-sample default.

## Submission boundary

The caller owns authorization, request preflight, prompt-review and submission.
This skill returns one of: a prompt package (prompt, ordered references with
roles, size, sample count, route), a composite plan for the deterministic
renderer, or a stop with the missing input named. A provider success sets
`review`, not `approved`.

## QA

Load [shot QA](references/shot-qa.md) after generation or compositing and
before selection. It covers identity, label legibility, color match against the
brand palette, hands and anatomy, invented text, margins and the
white-background check.

The bundled checker measures the border of an 8-bit RGB or RGBA PNG:

```bash
uv run python .agents/skills/seedream-product-shot/scripts/white_background_check.py \
  projects/example/elements/glow-mug/product_glow-mug_studio-white_t01_v01.png \
  --tolerance 3 --min-share 0.99
```

It prints JSON (border share within tolerance of the target, transparent
pixels, mean border color) and exits 0 on pass, 1 on fail, 2 on an unreadable
or unsupported PNG (16-bit, palette, grayscale, interlaced). Use `--target
'#RRGGBB'` to measure a brand-color or dark backdrop. Convert JPEG candidates to
PNG before checking.

**Marketplace rules change and differ.** This skill records no verified
marketplace specification. Before delivering a marketplace image, read the
target marketplace's current image rules (background value, product fill,
shadows, props, text) and set the check's tolerance and threshold from them.

## Files

Save beside the product element, `projects/<project>/elements/<product-id>/`:

- `product_<product-id>_<preset>_t<NN>_v<NN>.png` for each sample;
- `prompt_product_<product-id>_<preset>_v<NN>.md` as the exact prompt snapshot;
- `plate_<product-id>_<preset>_t<NN>_v<NN>.png` for an empty plate, and the
  composite as a deterministic render with its own render record;
- the white-background JSON beside the image it measured.

## Quick defaults

- Model: `dola-seedream-5-0-pro-260628`, Image-to-Image
- Format: `png`; watermark false where supported
- Prompt optimization: `standard`
- Samples: three
