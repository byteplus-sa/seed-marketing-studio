---
name: brand-kit
description: >-
  Build, validate and pin a machine-readable brand kit (logos, palette,
  typography, voice, copy rules, CTA style, imagery sentence, disclosure text)
  from the brand's own website, user-supplied files or manual input, stored once
  in the shared library and pinned by SHA-256 per campaign. Never invents a
  value: unknowns stay null and listed. Use when a campaign needs brand
  identity, a kit is created or updated, or a kit must be checked before use.
  Does not generate media, write ad copy or approve rights.
---

# Brand Kit

One brand record that every prompt, graphic and review step reads. This leaf
skill extracts, records and validates; it does not write prompts, render
graphics or generate media. Compose with `html-graphic-render`, HyperFrames
compositions, Seedream/Seedance prompt skills and `prompt-review`, which read
the kit as described in [consumers](references/consumers.md).

**Three non-negotiables:**

1. **Never invent a value.** A hex, font, logo, banned word or tone that the
   source does not show stays `null` (or an empty list) and its dotted path is
   listed in `missing`. A plausible guess is still an invention.
2. **Extracted values are draft.** A kit stays `status: draft` until it is
   approved under the project approval mode with a recorded decision.
3. **Generated media never renders the logo.** Logos, exact type and CTA
   geometry go through deterministic graphics in post; generative prompts
   receive only `imagery.style_sentence`.

## Where the kit lives

The kit lives in the workspace shared library and is reused across campaigns:

```
library/brands/<brand-id>/
  brand.json        # validated against the brand-kit schema
  assets/           # logos, fonts/, each hashed in brand.json
  decisions/        # approval decision records referenced by approval.decision_ref
```

`brand_id` equals the directory name (lowercase kebab-case). A campaign pins
the kit in its `project.md` by the canonical SHA-256 from `brand_kit.py pin`.
The layout, pin format and Git policy are in the
[shared library contract](../../contracts/shared-library.md). The record format
is the [brand-kit schema](../../contracts/schemas/brand-kit.schema.json).

## Workflow

1. **Confirm authority and inputs.** Ask which brand, and whether the user is
   authorized to use its identity (brand owner, agency of record, or an
   explicit statement). Record that statement in `source.authorized_by`; never
   infer it. Collect the brand's own URLs and any supplied files (guidelines
   PDF, logo pack, font files, tone document).
2. **Reuse first.** If `library/brands/<brand-id>/brand.json` exists, validate
   it and reuse it. Update only fields that changed; an update is a new draft
   until re-approved, and every campaign pinned to the old hash must re-pin
   deliberately.
3. **Scaffold** a new kit:

   ```bash
   uv run python .agents/skills/brand-kit/scripts/brand_kit.py init library/brands acme-home --name "Acme Home"
   ```

   The scaffold is a valid draft with every unknown already listed in
   `missing`.
4. **Extract** following [extraction](references/extraction.md): read the
   brand's own pages and supplied files, download logos and fonts only from
   brand-owned or user-supplied sources into `assets/`, and record each file's
   SHA-256, source and font license. Remove a path from `missing` only when you
   fill it with a sourced value.
5. **Validate** after every edit:

   ```bash
   uv run python .agents/skills/brand-kit/scripts/brand_kit.py validate library/brands/acme-home/brand.json
   ```

   Exit 1 prints JSON findings. Fix every `error`; review every `warning`.
6. **Inspect visibly.** Open each logo and render a palette/type swatch (for
   example with `html-graphic-render`) and compare it with the source pages.
   A hash proves the bytes, not that the right file was chosen.
7. **Approve** under the project's `approval_mode`. In `approve_for_me`, the
   agent may approve after validation and visible inspection, writing a
   decision record under `decisions/`. In `ask_for_approval`, present the
   summary (`brand_kit.py show`) and the `missing` list, and wait for the
   user's words in chat. Then set `status: approved` and fill `approval` (mode,
   actor, decision_ref, decided_at). Approval of creative values never grants
   trademark or font rights by inference.
8. **Pin** in the campaign:

   ```bash
   uv run python .agents/skills/brand-kit/scripts/brand_kit.py pin library/brands/acme-home/brand.json
   uv run python .agents/skills/brand-kit/scripts/brand_kit.py pin library/brands/acme-home/brand.json --expect <sha256>
   ```

   `pin` refuses an invalid kit and, without `--allow-draft`, a draft kit.
   Prompt-only drafting may pin a draft with `--allow-draft`; production
   generation and delivery need an approved kit. `--expect` exits 1 when the
   kit no longer matches the campaign pin, so consumers can check before use.

## Script reference

| Command | Purpose | Exit 1 when |
| --- | --- | --- |
| `init <library-root> <brand-id> [--name N]` | Scaffold `brand.json` draft and `assets/` | Invalid id or the kit already exists |
| `validate <brand.json>` | Schema, file existence, SHA-256 match, hex format, font license, missing list | Any `error` finding |
| `pin <brand.json> [--expect SHA] [--allow-draft]` | Print the canonical SHA-256 (sorted-key compact UTF-8 JSON) | Invalid kit, unapproved kit, or pin mismatch |
| `show <brand.json>` | Consumer view: palette, fonts, logos, copy rules, style sentence, disclosure, missing | Invalid kit |

Finding rule IDs: `brand.schema`, `brand.hex`, `brand.missing_listed`,
`brand.file_contained`, `brand.file_exists`, `brand.file_hash`,
`brand.font_license`, `brand.id_matches_directory`, `brand.palette_unique`,
`brand.logo_primary`. A stored font file without a license is always an error;
a family named without a file and license is a warning in a draft and an
error once approved.

## Field guidance

| Field | Rule |
| --- | --- |
| `logos[]` | Brand-owned download or user file; SVG preferred; `source` is the HTTPS page or `user_supplied`; record `min_height_px`, `clear_space_ratio` and backgrounds only when the guidelines state them |
| `palette[]` | Hex values read from guidelines, CSS custom properties or the logo file; never eyedropped from a compressed photo; uppercase or lowercase six-digit hex |
| `typography[]` | Family as declared; a file only when its license permits rendering ads; license names the actual terms |
| `voice` | Tone words and do/don't lines quoted or closely paraphrased from the brand's own guidance; empty when none exists |
| `copy_rules` | Banned words, required lines with the condition that triggers them, trademark marks per product name |
| `cta_style` | Shape, case and verbs observed on the brand's own CTAs |
| `imagery.style_sentence` | One observable sentence describing the brand's photography or illustration (light, palette mood, framing, texture); no logo, no text |
| `disclosure` | AI label wording and placement used **only** when a paid deliverable's recorded disclosure decision requires it; internal reviews and reels stay unlabeled unless asked |

## Failure handling

- **Site unreadable** (blocked, script-rendered, login or region gate): do not
  guess from memory. Ask for the guidelines PDF, logo pack or screenshots, or
  leave the fields missing.
- **Conflicting values** (two reds across pages): prefer the guidelines
  document, then the site's CSS variables; note the conflict for approval.
- **Unlicensed or unknown font**: keep the family name, leave `file` and
  `license` null, list them in `missing`, and let renders use a named
  fallback the user approves.
- **Brand not authorized**: stop building an identity kit; offer a
  de-identified style kit for an invented brand instead.
