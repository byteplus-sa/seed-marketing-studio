# Brand kit extraction

Load this before filling a kit from a website or supplied files. Every value
needs a source you could show the user; anything else stays in `missing`.

## Source priority

| Priority | Source | Use for |
| --- | --- | --- |
| 1 | User-supplied brand guidelines, logo pack, font files | Everything they state; they override the website |
| 2 | Brand-owned press, media or brand-assets page | Official logo files, usage rules, approved colors |
| 3 | Brand-owned site pages (home, about, product, footer) | CSS colors, font families, CTA style, tone, required legal lines |
| 4 | The brand's own social profile images | Logo cross-check only, never as the stored file |

Never use third-party logo aggregators, wikis, search-result thumbnails, or a
model's memory of the brand. They are often outdated, recolored or traced.

## What to read from a site

| Field | Where to look | Verification |
| --- | --- | --- |
| `name` | Site title, footer legal line | Matches the legal or trading name the user uses |
| `logos[]` | Header `<img>`/inline SVG, press or brand-assets page, favicon set | Open the downloaded file; compare visibly with the live header |
| `palette[]` | CSS custom properties (`--brand-*`, `--color-primary`), button and link styles, SVG `fill` values | Same hex appears in more than one place, or the guidelines state it |
| `typography[]` | `font-family` declarations, `@font-face` sources, font-service links | Family name only unless a license permits downloading the file |
| `voice` | About page, mission copy, product descriptions, guidelines tone section | Quote or closely paraphrase; do not summarize into adjectives the source never used |
| `copy_rules.banned_words` | Guidelines only | Never inferred from absence on the site |
| `copy_rules.required_lines` | Footer legal lines, product disclaimers, guidelines | Record the trigger in `when` (for example "price shown") |
| `copy_rules.trademark_marks` | Product names as written on the brand's pages (`®`, `™`) | Same mark on more than one brand page |
| `cta_style` | Primary buttons: border radius (pill vs rect), letter case, verbs | Observe at least two CTAs |
| `imagery.style_sentence` | Hero and product photography on brand pages | Describe light, palette mood, framing and texture you can see; no logo, no text, no brand name |

Record `source.urls` (every page read), `source.retrieved_at` (UTC ISO-8601),
and `source.method` (`website`, `user_files`, `manual` or `mixed`).

## Acquisition-first for logos and fonts

1. Download only from a brand-owned HTTPS URL or a user-supplied file into
   `assets/` (logos) and `assets/fonts/` (fonts). Use descriptive names such as
   `assets/logo_primary.svg`, `assets/logo_mono_white.png`,
   `assets/fonts/brandsans-bold.woff2`.
2. Compute SHA-256 and record it with the file's `source` (the page URL, or
   `user_supplied`):

   ```bash
   shasum -a 256 library/brands/acme-home/assets/logo_primary.svg
   ```

3. Prefer vector (SVG) over raster; keep the original bytes. Do not recolor,
   trace, upscale or crop a logo into a "new" file. A needed variant (mono,
   inverse) comes from the brand's own pack; if it is absent, list it as
   missing rather than making one.
4. Fonts need a license before a file is stored. Record the actual terms in
   `license` (for example an open font license name, or "brand-supplied for
   agency use per user statement"). A web font served to the browser is not a
   license to embed it in ads. Without one, keep only the family name and list
   `typography.N.file` and `typography.N.license` in `missing`.
5. Never generate a logo, wordmark or brand font with an image model, and never
   ask Seedream or Seedance to reproduce one.

## Verification before approval

- Run `brand_kit.py validate`; every error fixed.
- Visibly compare each logo with the brand's live header and guidelines.
- Render a swatch sheet (palette chips with hex labels, each font role in its
  family) through a deterministic HTML render and inspect it; a font that
  silently fell back is a defect.
- Read `missing` aloud in the approval summary so the approver sees what was
  not found.
- Re-extraction later is a new draft: changed hashes mean the pin changes and
  campaigns re-pin deliberately.

## Manual input

When the user dictates values, record `source.method: manual` and
`source.authorized_by` with their statement. Ask for files for logos and fonts;
a described logo is not a logo file.
