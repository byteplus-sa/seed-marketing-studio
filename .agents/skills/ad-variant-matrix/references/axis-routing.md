# Axis routing

Focused reference for [ad-variant-matrix](../SKILL.md). Read it before writing
the first prompt for a row. Each section names the specialist that owns the
prompt; this file only fixes what the matrix passes in and what a row must
preserve.

- [Shared source preparation](#shared-source-preparation)
- [Hook](#hook)
- [Talent, product, outfit, location](#talent-product-outfit-location)
- [Language](#language)
- [Market](#market)
- [Ratio](#ratio)
- [Project paths](#project-paths)
- [Rows that change several axes](#rows-that-change-several-axes)
- [Shared operations](#shared-operations)

## Shared source preparation

Do this once per hero, before any row prompt:

1. Confirm the hero file still hashes to `hero.sha256`; `register` refuses
   when `hero.take_file` or `hero.decision_ref` is missing from the project or
   the hash no longer matches.
2. Inspect it per the
   [video-to-video inputs contract](../../../contracts/video-to-video-inputs.md):
   duration, frame rate, ratio, audio streams, cuts and a recorded rights
   decision. Make the muted master that swap rows bind as `@Video 1`.
3. Run `source-subject-map` once on the hero. Every swap row cites the same
   subject, object and cut IDs; an unresolved ambiguity blocks every swap row.
4. Record the hero's opening-beat length (normally 0–2 s, at most 3 s) and the
   cut where the hero's body begins. Hook rows replace exactly that span in
   Studio; the generated opening itself is longer (see [Hook](#hook)).

## Hook

**Route:** regenerate the opening beat only, then splice it onto the hero.

- Take the hook entry by ID from the `ugc-ad-modes` hook library
  (`references/hooks.md`) and write the opening as a new Seedance 2.5 shot with
  `seedance-prompt-25` grammar, at the hero's ratio and with the same talent,
  wardrobe, product and setting references as the hero.
- Seedance 2.5 generates 4–30 s per request, so a 0–3 s opening cannot be
  generated at its span length. Generate at the **4 s minimum** (`--param
  duration=4`, which the planner adds to hook steps) and direct the hook
  action into the first part of the clip so the cut point lands cleanly.
- **Trim in Studio** to the recorded span so the hero's body and timing stay
  unchanged; the surplus seconds are discarded, never stretched over the body.
- Place the trimmed opening in the variant's Studio shot
  (`scenes/variant-<kebab-name>/`) before the hero's body from the recorded
  cut onward. Check the seam (eyeline, product side,
  light direction, ambient sound) and recut by frames rather than regenerating
  when it only needs a trim.
- A hook never changes product facts, locked copy, supported claims or the
  CTA. A hook row and a reference-ad recreation are mutually exclusive.

## Talent, product, outfit, location

**Route:** `source-subject-map` on the hero (once, shared by every swap row),
then Object Swap on the muted hero master with `seedance-object-swap`. It
keeps motion, framing, cuts and timing and replaces one element class. A swap
is a source-preserving edit, so its register command records that exemption
instead of requiring the shot-plan rules.

| Axis | Target reference | Notes |
| --- | --- | --- |
| `talent` | Virtual Portrait or authorized `asset://` views | Prepare with `seedance-virtual-portrait`; never a raw photo of a real person |
| `product` | Official or authorized packshot of the new product | Labels must match the product card; check the label side at every contact |
| `outfit` | Garment packshot, flat lay or mannequin view | One garment on one person |
| `location` | Location sheet or plate | Environment behind kept subjects |

- Parameters follow the swap route: `@Video 1` is the muted master,
  `generate_audio: false`, ratio and duration omitted (locked to the input),
  explicit `resolution: "480p"` and boolean `draft: true` for every new 2.5 draft.
- Sound returns in post: the hero's audio track, re-cut if the swap changed
  any timing.

## Language

**Route:** re-voice the locked script, then captions per language.

- Translate the **locked** script only; a translation that changes a claim,
  offer or CTA is a new script and needs its own approval.
- Write delivery direction with `seedance-prompt-25-dialogue` when a new
  native-speech take is needed, or re-voice the hero's soundtrack with
  `audio-dubbing` when the picture stays.
- The dub is audio: mux it onto the hero picture in post and place the muxed
  take in the variant's Studio shot. It has no draft/final resolution step.
- Make per-language captions with `ad-captions` from the locked translated
  script and the measured timing; burn-in or sidecar is decided per placement
  in delivery.
- On-screen supers in another language are re-laid out in Studio, never
  generated into footage.

## Market

**Route:** hand the row to `ad-localize`; the planner adds no provider step.

A market value is a market ID in kebab-case (at most 48 characters), the
folder name of its market card at
`projects/<campaign>/markets/<market-id>/market.json`.

| Concern | `variant_matrix.py` | `ad-localize` |
| --- | --- | --- |
| Which markets to test | Expands one row per market ID, named with that ID | — |
| Adaptation level (captions only, voice, talent, cultural, full transcreation) | Never chooses it | Records the user's per-element levels in `projects/<campaign>/markets/<market-id>/inventory.md`; the market card holds the market facts and only `level_default` |
| Language | Refuses a row that also changes `language` (`matrix.market_language`) | Sets the market's language and script from the card |
| Prompts, review, registry | Prints no command; lists the row under `localize` with the card, the inventory and a reminder | Plans, reviews and registers its own paid operations per element level |
| Cost | Reports an optional `market` unit cost as an estimate, or unknown | Reports available estimates for the chosen levels |
| Project | Names the localized project in the row's `localize` entry (see [Project paths](#project-paths)) | Builds that localized project |
| Delivery | Names the per-ratio project in the row's `delivery` entry | Hands the localized master to `ad-delivery-formats` |

- A market-only row has no Studio shot in the campaign project. A row that also
  changes a generated axis (for example hook) produces that variant here first;
  `ad-localize` then adapts the selected take into its own variant-specific
  localized project.
- Claims, offers and CTAs that differ by market are script changes with their
  own support and approval inside `ad-localize`; the matrix never varies them.
- When known, set the `market` unit cost from the expected level. When the
  level changes in `ad-localize`, update the forecast with the available figure;
  unknown prices do not block the work.

## Ratio

**Route:** `ad-delivery-formats`.

- A reframe in Studio is not a provider step and has no registry entry. The
  `ratio` unit cost defaults to `0` and `cost` prints a `ratio_cost_note`
  saying so; set `--unit-cost ratio=<usd>` only to estimate native
  regeneration. It is charged once per delivery project.
- Native regeneration per ratio is a new generation for composition-critical
  hero shots; the planner prints no command for it, so prepare, review and
  register it like any other generation and cost it with the `ratio` unit.
- Supers, CTA and captions are placed per ratio inside the placement's
  published safe zone.

## Project paths

Every market or ratio row names the project it builds or renders into. One
Studio project renders one canvas, so two different variants never share one.

| Row changes | `localize.project` | `delivery.project` |
| --- | --- | --- |
| ratio only | — | `projects/<campaign>-<ratio>` |
| market only | `projects/<campaign>-<market-id>` | — (the localized project is the deliverable at the hero ratio) |
| market and ratio | `projects/<campaign>-<market-id>` | `projects/<campaign>-<market-id>-<ratio>` |
| generated axes and ratio | — | `projects/<campaign>-<variant-key>-<ratio>` |
| generated axes and market | `projects/<campaign>-<variant-key>-<market-id>` | — |
| generated axes, market and ratio | `projects/<campaign>-<variant-key>-<market-id>` | `projects/<campaign>-<variant-key>-<market-id>-<ratio>` |

- `<variant-key>` joins the row's changed generated values (hook, talent,
  product, outfit, location, language) in axis order, each lowercased to
  kebab-case; ratios render as `4x5`. For example `hook-a` in market `south`
  at `4:5` delivers into `projects/<campaign>-hook-a-south-4x5`.
- Rows that differ only by ratio share their localized project: the per-ratio
  cuts reframe the same localized master.
- A row that keeps the hero's ratio has no `delivery` entry: its own Studio
  shot or localized project already renders at that ratio.
- The market card stays keyed by market ID under the campaign. When several
  variants are localized for one market, each keeps its own inventory,
  translation sheet and review record under
  `markets/<market-id>/<variant-key>/` (see `ad-localize`).
- `plan` refuses any remaining clash, for example a slug collision between a
  variant key and a market ID, with `matrix.unique_projects`. Rename a value
  rather than overriding the gate.

## Rows that change several axes

Only full-factorial matrices produce these. The planner orders steps as:
swaps (or one Motion Transfer) → hook → language → market → ratio. Market and
language never share a row; the planner refuses it.

- **Talent and location together** become one Motion Transfer with
  `seedance-motion-recast`, because two whole-subject changes are not an
  Object Swap. The row costs one `motion-recast` unit, not the talent and
  location units added together, because it is one provider operation.
- **Two other swap classes** (for example product and outfit) run as
  sequential swaps, the second using the inspected output of the first as its
  master. The first swap is the single-swap row's operation (see
  [Shared operations](#shared-operations)); the combined row registers only
  the second.
- A step that fails QA stops the later steps of that row and of every row that
  reuses it; other rows continue.

## Shared operations

A full factorial repeats work: the talent row, the talent-and-ratio row, the
talent-and-market row and the talent-market-ratio row all need the same
talent swap. The planner registers and charges that work once.

- **Lineage key.** Each step's `operation_key` joins the route and changed
  values of that step and every earlier step in the row, for example
  `object-swap:product=sku-b>object-swap:outfit=outfit-b`. Market and ratio
  values enter the key only at their own step, so generated work is keyed on
  the generated values alone.
- **Owner.** The first row in plan order with a key owns it
  (`steps[].owner`). That is always the row that changes exactly the key's
  axes, so every variant row owns exactly its last step.
- **Reuse.** A row's `base_variant` names the row whose selected take it
  starts from (the hero when nothing is reused). Only rows that own a
  generated step (hook, swap, recast, dub) get a Studio shot; `register`
  prints commands only for owned provider steps, and an operation's `after`
  names the variant whose selected take is its source.

| Row changes | Owns | Reuses (`base_variant`) |
| --- | --- | --- |
| talent | talent swap, Studio shot | hero |
| talent and ratio | reframe into its delivery project | talent row |
| talent and market | market adaptation into its localized project | talent row |
| talent, market and ratio | reframe into its delivery project | talent-and-market row |
| product and outfit | outfit swap, Studio shot | product row (`after`) |

- **Cost.** One unit per unique operation: a market adaptation once per
  localized project, a reframe once per delivery project. A row's
  `estimated_cost_usd` counts only what it owns; `operations_estimate` lists
  every unique operation with its owner, unit cost and `used_by` rows; the
  total uses these deduplicated figures. Missing prices yield unknown forecasts,
  not a generation gate.
- **Localize hand-off.** `register` lists each localized project once, under
  its owning row; rows that reuse it only reframe the localized master.
