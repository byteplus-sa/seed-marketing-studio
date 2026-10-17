---
name: ad-creative-check
description: >-
  Run an honest pre-spend checklist on a finished ad cut: product identifiable
  by its declared reveal time, logo legible and undistorted against the brand
  kit, a visible change in the opening seconds, CTA and offer inside the
  placement safe zone and readable with the sound off, every claim supported,
  speech intelligible, loudness on target, and a recorded disclosure decision
  for paid delivery. Samples frames with FFmpeg, uses video understanding and
  speech-to-text as evidence, and writes a pass, fail or needs-human report
  with timestamps and frame paths. Use before an ad is uploaded or a variant is
  promoted to paid spend. Not a virality, hook-rate or performance prediction,
  not prompt review, and not a fix or approval step.
---

# Ad Creative Check

A pre-spend quality gate for one finished ad cut. Each item is a yes-or-no
question a viewer could verify from the frames, the soundtrack and the
project's records. The report says what passed, what failed, what needs a
person to look, and where in the cut the evidence is.

**This is not a prediction.** It gives no virality score, hook-rate estimate,
"winning ad" ranking or performance forecast, and never implies one. Ad
performance is measured on the platform by comparing variants within one
account; a passing check only means the cut meets its own brief and the
[ad compliance](../../contracts/ad-compliance.md) contract.

This is a leaf capability. It reads a rendered cut and project records,
writes a check folder, and changes nothing else: it does not edit the cut,
regenerate media, approve a variant, decide a disclosure or upload an ad.

## Inputs

| Input | Source | Missing means |
| --- | --- | --- |
| Final cut | the newest delivery render of the deliverable | stop: nothing to check |
| Deliverable ID and placement | the delivery plan; placement IDs from [ad platforms](../../contracts/ad-platforms.md) | ask |
| Declared reveal time | the hook or script (`reveal_time_s`); default 2.0 s | use the default and say so |
| Brand kit | the campaign's pinned `brand.json` and its logo files | `logo_legible` and `brand_copy` are `needs_human` |
| Product facts | `elements/<product-id>/facts.json` | `claims_supported` fails for any claim |
| Locked script and supers | the script or copy plan | `speech_intelligible` compares against what was heard only, and says so |
| Loudness target | the delivery record; default from the [audio contract](../../contracts/audio-video-alignment.md): -16 LUFS integrated, peaks at or below -1.5 dBFS, checked here as true peak at or below -1.5 dBTP (stricter, so it also meets the contract); the ±1 LU integrated tolerance is a workspace heuristic, not part of the contract | use the default and say so |
| Paid flag and disclosure record | `delivery/disclosure_<deliverable-id>.json` | a paid deliverable fails `disclosure_recorded` |

Check the cut's SHA-256 against the render record before starting. A check
belongs to one exact file; a re-render needs a new check.

## The checks

| ID | Rule | Passes when | Evidence |
| --- | --- | --- | --- |
| `product_reveal` | | The product is identifiable (shape, pack and colour match the product card) at or before `reveal_time_s` | first timestamp and frame showing it |
| `logo_legible` | | The logo matches the brand kit file: correct proportions, colours and orientation, readable at phone size, not warped, cropped or mirrored | timestamps and frames for every logo appearance |
| `opening_change` | | A visible motion, cut or strong contrast change happens within the first `opening_window_s` (default 2.0 s) | timestamp and the frames either side of it |
| `cta_safe_zone` | `ad.safe_zone` | CTA, offer, logo and required lines sit inside the placement safe zone | frames with the zone drawn or measured |
| `sound_off_readable` | `ad.safe_zone` | The offer and CTA are understandable from on-screen copy alone, at phone size, for long enough to read | frames and on-screen durations |
| `claims_supported` | `ad.claims_supported` | Every on-screen and spoken claim maps to a `supported` (or current `perishable`) fact; comparatives show their conditions | claim list with timestamps and fact IDs |
| `brand_copy` | `brand.copy_rules` | No banned word on screen or in speech; required lines and marks present where their condition holds | timestamps of copy and transcript lines |
| `speech_intelligible` | | The transcript matches the locked lines word for word, with no clipped, slurred or mispronounced key words (product name, offer, CTA) | transcript excerpts with timestamps |
| `loudness_target` | | Integrated loudness within tolerance of the target and true peak at or below the ceiling | `measured` values |
| `disclosure_recorded` | `ad.disclosure_recorded` | Paid: a user decision record exists for this deliverable. Unpaid: `not_applicable`, and the cut carries no AI label | the record path |

Status values: `pass`, `fail`, `needs_human` (the evidence is ambiguous or a
required input is missing) and `not_applicable` (with the reason in
`evidence`; not allowed for `product_reveal`, `opening_change` or
`loudness_target`). The detailed criteria and question wording for each check
are in [check procedure](references/check-procedure.md); load it before the
first check.

## Procedure

1. **Set up the check folder** in the campaign:
   `delivery/qa/<deliverable-id>/`, the same folder as the cut's safe-zone
   contact sheet. The deliverable id is the variant name plus the placement,
   `{campaign}_{concept}_{axis-values}_v{nn}_<placement>`. Everything the
   report cites lives inside it.
2. **Sample frames.** Run
   `uv run python .agents/skills/ad-creative-check/scripts/creative_check.py frames <cut> --out delivery/qa/<deliverable-id>/frames --every 0.5`
   and a dense opening pass with `--every 0.25 --until 3 --out delivery/qa/<deliverable-id>/opening`.
   The command prints each frame's path and time. Look at the frames yourself.
3. **Ask the video model.** Run `seed_understand` (through `ark-mcp`) on the
   cut with the questions in the check procedure. Upload the cut with
   `media_upload` when it has no public HTTPS URL. Save the answers as
   `understanding.md` in the check folder. Model answers are evidence, never
   the verdict: confirm each one against the frames.
4. **Transcribe speech.** Run `speech_to_text` on the cut's audio and compare
   with the locked script. Save `transcript.json`.
5. **Measure loudness** with the FFmpeg command in the check procedure.
6. **Map claims and copy.** List every claim and line from the frames and the
   transcript; match each to `facts.json` and the brand kit copy rules.
7. **Check the disclosure record** for a paid deliverable. If none exists,
   the check fails and you ask the user for the decision; never write one on
   their behalf.
8. **Fill `checks.json`** (schema:
   [checks.schema.json](references/checks.schema.json)) with one entry per
   check, timestamps in seconds from the start of the cut and frame paths
   relative to the check folder.
9. **Validate and summarize:**
   `uv run python .agents/skills/ad-creative-check/scripts/creative_check.py report delivery/qa/<deliverable-id>/checks.json --out delivery/qa/<deliverable-id>/report.json`.
   Exit 0 means every check passed or does not apply, 1 means a `fail` or
   `needs_human` remains, and 2 means the checklist is invalid (the errors
   are listed). Fix the checklist, not the evidence.

## Judging honestly

- **Unsure is `needs_human`, not `pass`.** Small logos, fast cuts, low light,
  partially occluded packs and accents the transcript struggles with are
  exactly where a model answer is weakest.
- **One frame is not proof of absence.** A `fail` for "product not shown by
  2 s" cites the dense opening frames, not a single sample.
- **Do not grade taste.** Pacing, music choice and whether the hook "feels
  strong" are not checks here; brief and creative review own them.
- **Report what you saw.** Timestamps come from frame times or the transcript,
  never from the script's intended timing.

## Output

`checks.json` (the filled checklist), `report.json` (the validated summary
with `verdict`, counts and per-check rule IDs, timestamps and frames), the
sampled frames, `understanding.md` and `transcript.json`, all in the check
folder. Hand the report back to the caller; failures go to the stage that
owns the fix.

## Compose with other skills

- `ad-delivery-formats` produces the per-ratio masters and safe-zone overlay
  sheets this check reads.
- `prompt-review` checks the same compliance rules on prompts and copy before
  generation; this check covers the finished cut.
- `brand-kit` and `product-intake` own the brand kit and the facts file.
- `ffmpeg` covers frame and loudness commands beyond the ones here.
