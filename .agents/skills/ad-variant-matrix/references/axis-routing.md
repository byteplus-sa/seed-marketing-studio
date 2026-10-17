# Axis routing

Focused reference for [ad-variant-matrix](../SKILL.md). Read it before writing
the first prompt for a row. Each section names the specialist that owns the
prompt; this file only fixes what the matrix passes in and what a row must
preserve.

- [Shared source preparation](#shared-source-preparation)
- [Hook](#hook)
- [Talent, product, outfit, location](#talent-product-outfit-location)
- [Language](#language)
- [Ratio](#ratio)
- [Rows that change several axes](#rows-that-change-several-axes)

## Shared source preparation

Do this once per hero, before any row prompt:

1. Confirm the hero file still hashes to `hero.sha256`.
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
  `resolution: 480p` for the draft.
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

## Ratio

**Route:** `ad-delivery-formats`.

- A reframe in Studio is not a provider step and has no registry entry; give
  it a unit cost of `0` unless native regeneration is chosen.
- Native regeneration per ratio is a new generation for composition-critical
  hero shots; record it as its own row step and cost it.
- Supers, CTA and captions are placed per ratio inside the placement's
  published safe zone.

## Rows that change several axes

Only full-factorial matrices produce these. The planner orders steps as:
swaps (or one Motion Transfer) → hook → language → ratio.

- **Talent and location together** become one Motion Transfer with
  `seedance-motion-recast`, because two whole-subject changes are not an
  Object Swap. The row costs one `motion-recast` unit, not the talent and
  location units added together, because it is one provider operation.
- **Two other swap classes** (for example product and outfit) run as
  sequential swaps, the second using the inspected output of the first as its
  master. Each step has its own asset ID, prompt, review and registry entry.
- A step that fails QA stops the later steps of that row; other rows continue.
