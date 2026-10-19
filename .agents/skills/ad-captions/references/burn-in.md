# Burn-in and Readability

Read [the entrypoint](../SKILL.md).

## Layer contract

`--composition-dir` writes one HyperFrames sub-composition per language. Each
cue is a timed `div` (`data-start`, `data-duration`) positioned inside the safe
rectangle, so the runtime shows it only during its window. The report prints a
host snippet per language; add it to the cut's `studio/index.html` as a
graphics clip and render through the project's Studio commands. The layer is
plain HTML and CSS with an empty paused timeline; add motion only if the brand
asks for it, and keep it seek-safe.

## Safe rectangle

| Case | What to pass |
| --- | --- |
| Placement with a published zone (`meta-instagram-reels`, `meta-instagram-stories`) | `--placement ID --size WxH` |
| Several placements sharing one cut | The intersection from `safe_zones.py zones` (compose with `ad-delivery-formats`) as `--safe-rect` |
| Unpublished zone (`tiktok-in-feed`, `youtube-shorts`, landscape YouTube, unverified feed) | `--safe-rect` measured on the platform's own template at the cut size, with the template name and date recorded in the delivery notes |

A size whose ratio differs from the placement by more than 1% is rejected.

## Readability defaults

- **Size:** default font size is 4.5% of the frame's short side (49 px at
  1080 wide). Raise it for dense scripts only after shortening lines.
- **Contrast:** white text on a 70% black box by default; brand colors may
  replace them when contrast stays high on every frame the cue covers.
- **Typeface:** the brand caption face from the brand kit, loaded from a
  project-local file via `--font-src` (relative to the Studio project; the
  file must exist, or the script refuses rather than silently falling back),
  with a sans-serif fallback for missing glyphs. Check that
  the face covers every script shipped (CJK, Arabic, Devanagari); otherwise use
  a covering fallback face for that language.
- **Position:** bottom of the safe rectangle by default. Use `--anchor top`
  when a super, price or product owns the lower area; never stack captions over
  the CTA.
- **Width estimate:** the script warns when an estimated line (0.55 em per
  Latin character, 1 em per CJK character, plus box padding) exceeds the safe
  width. It is an estimate; confirm with a Studio snapshot.

## Checks before sign-off

- `--font-family` accepts Unicode letters, combining marks and numbers, plus
  spaces and `_-. '()` punctuation, up to 240 characters. The emitted family is
  a quoted, escaped CSS string, not a CSS declaration or a fallback list.
  `--font-src` accepts Unicode local filenames, including spaces and punctuation,
  and emits a percent-encoded URL. Pass the actual filename, not a pre-encoded
  URL. Absolute paths, `..` components, URL schemes, backslashes, control
  characters, missing files, direct symlinks and symlink escapes remain refused.
- Play one cue per language in Studio, including every right-to-left and CJK
  language; confirm punctuation side and that no line starts with closing
  punctuation.
- Shrink a snapshot to about 25% and read the caption.
- Confirm the caption never overlaps the product label, logo or CTA in the
  safe-zone contact sheet.
