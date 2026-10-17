---
name: ad-captions
description: >-
  Write per-language ad captions (SRT, WebVTT) named
  <master-stem>.<language-code>.srt from the locked ad script and measured
  speech timing, and optionally a HyperFrames caption layer placed inside a
  placement's safe zone in brand typography for sound-off viewing. Caption text
  follows the locked script, never the heard words. Wraps by grapheme cluster
  so CJK, Indic, Thai with word breaks and right-to-left scripts are never
  split inside a word; enforces line length, reading speed and cue duration;
  resolves overlaps; refuses to invent margins for unpublished safe zones. Use
  for any market or language after speech QA on the cut. Does not translate,
  transcribe, generate media or render the master.
---

# Ad Captions

Turn the locked script plus measured timing into one caption file per language,
and, when the ad needs open captions, a deterministic HyperFrames layer that
Studio burns into each placement's cut. **Most viewers meet a feed ad with the
sound off**, so captions carry the spoken message; supers, price and CTA are a
separate layer and are not captions.

## Input and output

Input: one timing JSON per clip (or per cut) with each spoken line's `start_s`,
`end_s` and locked text per language; the master stem; the languages to ship;
for burn-in, the cut size and either a placement id or a measured safe
rectangle. See [input format](references/input-format.md).

Output: `<master-stem>.<language-code>.srt` (and `.vtt` on request), optionally
`compositions/captions-<language-code>.html` per language, plus a JSON report
with cue counts, SHA-256 per file, host snippets and every warning.

## Rules

1. **Locked words, not heard words.** Text comes from the locked script or its
   approved translation. Speech-to-text supplies timing only. When the take says
   a different word, fix the take or record a defect; never edit the caption to
   match it. Claims, prices and product names in captions must match the
   approved script exactly.
2. **Generated footage stays text-free.** Captions reach the picture only as a
   Studio overlay; never prompt a model to render them.
3. **Timing is measured.** Use heard start and end times on the final timeline,
   not planned seconds; apply the clip's Studio start as the offset.
4. **One file per language.** Codes are lowercase BCP 47 tags (`en`, `pt-br`,
   `zh-hans`). Existing files are not overwritten unless `--overwrite` is
   passed on purpose.
5. **Never split a word or grapheme cluster.** Breaks fall at spaces, U+200B
   and between CJK characters (not before closing or after opening
   punctuation). Scripts written without spaces, such as Thai, need U+200B at
   word boundaries in the locked text; otherwise an overlong run is split and
   reported.
6. **Right-to-left text** gets a leading U+200F per line in sidecars and
   `dir="rtl"` in the burn-in layer. Check mixed digits and Latin brand names
   in the target player; TikTok publishes a separate right-to-left safe-zone
   template.
7. **Limits are conservative defaults, not platform rules.** Defaults: 32
   characters per line (16 for `zh` and `ko`, 13 for `ja`), two lines, 17
   characters per second (9 for `zh`, 7 for `ja`, 12 for `ko`), cues 1 to 7 s,
   40 ms between cues. Override per language with flags when the brand or
   platform sets other numbers.
8. **Burn-in stays inside the safe zone.** The layer is laid out from
   [ad-platforms.json](../../contracts/ad-platforms.json) (verified 2026-10-17;
   re-verify before paid delivery). For a placement whose safe zone is
   unpublished, the script refuses until a rectangle measured from the
   platform's own template is passed with `--safe-rect`.
9. **Warnings are defects to look at.** Reading speed over the limit, a cue
   below the minimum, a trimmed overlap, a split run and an estimated line wider
   than the safe rectangle are reported. Fix the text, timing, line limit or
   font size rather than silencing them.

## Sound-off readability

Read [burn-in and readability](references/burn-in.md) before building a burn-in
layer. In short: brand typeface with a legible fallback, at least about 4.5% of
the frame's short side, high contrast on a solid or translucent box, two lines
at most, bottom of the safe rectangle unless a super or product sits there, and
a check at thumbnail size.

## Workflow

1. Confirm the cut's speech QA passed and the script is locked.
2. Write the timing JSON with times from the final timeline.
3. Pick the Studio project that renders the cut: the campaign project for the
   master ratio, or the per-ratio project `projects/<campaign>-<ratio>/` that
   `ad-delivery-formats` sets up (its own `project.md`, hash-pinned shot
   manifests, `init` and `sync` already run, so `studio/compositions/`
   exists). Run from the repository root:

```bash
uv run python .agents/skills/ad-captions/scripts/make_captions.py \
  --input projects/<campaign>/captions/hero.json \
  --master-stem <master-stem> --language en es --format both \
  --out-dir projects/<campaign>/captions/out --master-duration-s <duration> \
  --composition-dir projects/<campaign>-9x16/studio/compositions \
  --size 1080x1920 --placement meta-instagram-reels \
  --font-family "Brand Sans" --font-src assets/fonts/brand-sans.woff2
```

4. Read the report. Add each host snippet to the Studio `index.html` timeline as
   a graphics clip, then snapshot and play at least one cue per language,
   including every right-to-left or CJK language.
5. Deliver sidecars beside the master and record their hashes; the burn-in
   layer ships inside the Studio render.

## Script reference

`scripts/make_captions.py` is stdlib-only. Caption flags: `--input`
(repeatable), `--master-stem`, `--language`, `--out-dir`, `--format`
(`srt`, `vtt`, `both`), `--offset-s`, `--master-duration-s`, `--max-chars`,
`--max-lines`, `--min-duration-s`, `--max-duration-s`, `--max-cps`,
`--min-gap-s`, `--max-chars-for LANG=N`, `--max-cps-for LANG=N`,
`--overlap trim|error`, `--rtl-marks auto|on|off`, `--overwrite`. Burn-in
flags: `--composition-dir` (turns burn-in on; must be an existing Studio
`compositions/` folder), `--composition-prefix`,
`--size WxH`, `--placement ID` or `--safe-rect X,Y,W,H`, `--platforms`,
`--font-family`, `--font-src` (an existing regular font file, given relative to
the Studio project, the parent of `--composition-dir`),
`--font-size`, `--text-color`, `--box-color` (`#RRGGBB` or `#RRGGBBAA`),
`--anchor bottom|top`. It exits 2 with a one-line error and writes nothing for
invalid input, missing or blank language text, a line id repeated across
inputs, a line too short to give each cue any time, a cue past the master duration,
an unpublished safe zone without `--safe-rect`, a missing composition folder, a
missing, symlinked or out-of-project font file, or an existing target.

## Boundaries

This leaf does not translate (the caller supplies approved text per language),
does not transcribe (use speech-to-text on the cut), does not choose
placements, and does not render. Compose with `ad-delivery-formats` for
per-ratio cuts and safe-zone QA, and with `audio-dubbing` when a language also
needs a dubbed voice.
