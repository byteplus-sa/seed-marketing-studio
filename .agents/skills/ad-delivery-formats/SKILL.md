---
name: ad-delivery-formats
description: >-
  Turn one finished ad master into per-placement cuts (9:16, 4:5, 1:1, 16:9 and
  others) using dated platform specs from the ad-platforms contract. Chooses
  native regeneration per ratio for composition-critical hero shots, otherwise
  a per-ratio HyperFrames Studio reframe with a subject-aware crop; lays out
  supers, CTA and captions deterministically inside each placement's safe zone;
  and checks every cut with a safe-zone overlay contact sheet. Reports
  unpublished safe zones instead of inventing margins. Use when an approved ad
  must ship to several placements or ratios. Not for writing the ad, generating
  the master, or caption timing.
---

# Ad Delivery Formats

Deliver one approved master to every requested placement without losing the
product, the logo or the call to action. **Text is never cropped from the
master**: each ratio gets its own deterministic layout of supers, CTA and
captions. **Specs are dated data**: read them from
[ad-platforms.md](../../contracts/ad-platforms.md) and
[ad-platforms.json](../../contracts/ad-platforms.json), verified 2026-10-17,
and re-verify a placement against its source before a paid delivery.

## 1. Build the delivery list

For each requested placement, record a row before any work:

| Field | Source |
| --- | --- |
| Placement id | `ad-platforms.json` (`meta-instagram-reels`, `tiktok-in-feed`, ...) |
| Ratio and size | The placement's `aspect_ratio` and `recommended_resolution`, or the master's delivery size when none is published |
| Duration bounds | `duration.min_s` / `max_s` / `recommended`; a master longer than the bound needs a cutdown, not a speed-up |
| Safe zone | `safe_zones.py zones`; `unpublished` means lay out against the platform template |
| Status | `verified`, `partial` or `unverified`; an `unverified` row needs the user to confirm the spec or accept the risk |

**Group placements that share a ratio into one cut** and lay out against the
intersection of their safe zones (`--placement` repeated). A request for an
unknown placement is answered with the known ids, not a guessed spec.

## 2. Choose regenerate or reframe per ratio

| Situation | Route |
| --- | --- |
| Hero shot whose composition carries the idea (product reveal, framed logo, two-subject blocking) and the target ratio would cut a subject | **Native generation in that ratio** with the same approved references and prompt; it re-enters prompt-review, the 480p draft rule and the registry like any shot |
| Single subject with room around it, or a ratio change the crop can absorb | **Reframe** in a per-ratio Studio project (below) |
| Landscape master to vertical where the subject would fill less than about a third of the frame width | Prefer regeneration; a blurred-band letterbox is a last resort the user must accept |
| Shot already generated in the target ratio | Reuse it |

Record the route and its reason per shot. **Never re-generate to fix text**:
text belongs to the deterministic layer.

## 3. Reframe with a subject-aware crop

Read [reframe recipe](references/reframe-recipe.md) when reframing. In short:

1. Sample frames of each shot and ask `seed_understand` for normalized subject
   boxes (product, face, hands, logo) per sampled time. Treat the boxes as
   approximate and spot-check them on the frames.
2. Create **one Studio project per delivered ratio** at
   `projects/<campaign>-<ratio>/`, because `render` renders one canvas per
   project. It needs its own `project.md` (the campaign brief copied with the
   same `approval_mode` and a pin of the master's path and hash) and one shot
   manifest per master shot whose take is a byte copy of the master's selected
   take, pinned by hash. Then `init --aspect <ratio> --resolution <short-side>p`,
   `sync --take <shot>=<file>` and `record-selection` per shot. Place the
   master's approved shots, never the flattened master render. Exact files,
   commands and stage exits are in the recipe.
3. Wrap each shot's video in a crop wrapper and keyframe its position so the
   union of the subject boxes stays inside the safe rectangle; hold the crop
   still unless the subject moves, and ease any move.
4. Never scale a source up beyond the point where its short side drops below the
   target size without recording the softness; prefer regeneration instead.

## 4. Lay out text per ratio

Supers, price, CTA, logo lock-up and captions are **HyperFrames overlays** built
for that ratio, positioned from `safe_zones.py zones` pixel rectangles. Use the
brand typography and the approved copy; copy changes only through the approved
script. Caption files come from the captions step (compose with `ad-captions`)
and are burned in through the same safe rectangle. Platform UI text (ad caption,
primary text, headline) is set in the ad manager and is never burned in.

## 5. QA with an overlay contact sheet

Read [QA contact sheet](references/qa-contact-sheet.md) before sign-off.

```bash
uv run python .agents/skills/ad-delivery-formats/scripts/safe_zones.py \
  overlay --placement meta-instagram-reels --size 1080x1920 \
  --box logo=80,300,280,120 --box cta=120,1120,840,110 \
  --out projects/<campaign>/delivery/qa/<deliverable-id>/overlay.svg
```

For each cut, snapshot the hook frame, the product-reveal frame, every frame
with a super and the end card; composite the overlay on top; and confirm with
`check` that the logo, product, CTA and caption boxes pass. A failing box is a
layout fix in the overlay composition, not a crop of the master.

## Script reference

`scripts/safe_zones.py` is stdlib-only and reads
`.agents/contracts/ad-platforms.json` (override with `--platforms`).

| Command | Output | Exit |
| --- | --- | --- |
| `zones --placement ID [--placement ID] [--size WxH]` | Margins in fractions and pixels and the title-safe `safe_rect` | 0 published, 3 unpublished |
| `check --placement ID --box [LABEL=]X,Y,W,H ...` | Per-box `inside`, `overflow_px`, `outside_frame` and the `violations` list | 0 pass, 1 violation, 3 unpublished |
| `overlay --placement ID --size WxH --out FILE.svg [--box ...] [--overwrite]` | An SVG with the unsafe area tinted, the safe rectangle dashed and boxes outlined | 0 written, 3 unpublished (no file) |

Margins round inward. A size whose ratio differs from the placement by more than
1%, mixed ratios across placements, unknown ids, malformed boxes and a
`--platforms` file that does not match
[the ad-platforms schema](../../contracts/schemas/ad-platforms.schema.json)
exit 2 with a one-line error naming the field. Overlay output must end in `.svg` and stay under the current
directory.

## Boundaries

This leaf does not write the ad, generate or approve the master, time captions,
or decide platform disclosure. Compose with `ad-captions` for caption files,
`html-graphic-render` for static cards, and the project's Studio commands for
render and stage exit. Renders follow the production policy: `render` is the
only authority for final files.
