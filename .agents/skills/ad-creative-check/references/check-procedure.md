# Check Procedure

Detailed criteria, model questions and commands for each check. Paths are
relative to the campaign folder; the check folder is
`delivery/qa/<deliverable-id>/`, shared with the cut's safe-zone contact
sheet. Deliverable ids are `{campaign}_{concept}_{axis-values}_v{nn}_<placement>`.

## Video understanding questions

Send one `seed_understand` request on the whole cut and ask for timestamps in
seconds. Keep questions neutral: ask what is visible, not whether the ad is
good. Replace the bracketed parts from the product card and brand kit.

```text
Watch this ad and answer each question with timestamps in seconds.
1. When is [product description from the product card] first clearly
   identifiable on screen? Describe its pack, colour and position.
2. List every appearance of a logo. For each: timestamp, position, size
   relative to the frame, and whether it looks stretched, cropped, mirrored,
   blurred or recoloured.
3. What changes on screen in the first 2 seconds (cut, camera move, subject
   motion, colour or brightness change)? Give the time of each change.
4. Transcribe all on-screen text with its start and end time and position.
5. List every statement about the product's results, speed, quantity,
   ingredients, price, offer, ratings or comparisons, spoken or on screen.
```

Treat each answer as a lead to confirm in the sampled frames. When the model
and the frames disagree, the frames win; when the frames cannot settle it,
the status is `needs_human`.

## Per-check criteria

### product_reveal

- Identifiable means a viewer who knows the product card would recognize it:
  the pack shape, main colour and label layout agree with the card's
  reference images. A hand-held blur or a silhouette is not a reveal.
- Use the dense opening frames. Record the first frame where it is
  identifiable; `pass` needs that time at or before `reveal_time_s`.

### logo_legible

- Compare each logo appearance with the brand kit logo file side by side:
  aspect ratio, colours, orientation and letterforms. Any warp, mirror,
  recolour, misspelling or crop is `fail`.
- Legible means readable when the frame is viewed about 360 px wide, the size
  of a phone feed thumbnail. This is a workspace heuristic, not a platform
  rule.
- Rule `brand.no_generated_logo`: free-standing, corner and end-card logos
  and wordmarks must be post overlays from the brand kit; one rendered inside
  generated footage is `fail` even when it looks right. An on-product mark is
  allowed only when a bound acquired product reference carries it; check it
  letter for letter against that reference. A logo or mark not traceable to a
  reference is `fail`.
- `not_applicable` only when the brief deliberately shows no logo.

### opening_change

- A cut, a clear camera move, subject motion across the frame, or a strong
  brightness or colour change counts. Compression shimmer or a slow drift
  does not.
- Cite the frames either side of the change.

### cta_safe_zone

- Take the safe zone for the placement from the ad platforms contract. Draw
  or measure the zone on the frames that hold a CTA, offer, logo or required
  line; every element sits fully inside.
- An unpublished safe zone (a `null` in the contract) is `needs_human`:
  compare against the platform's own template.

### sound_off_readable

- The offer and CTA are stated in on-screen copy, not only in voiceover.
- Each line stays on screen long enough to read: as a workspace heuristic,
  about 0.3 s per word plus 0.5 s, never under 1.5 s.
- Contrast and size hold at phone size over the actual background.

### claims_supported

- List every claim with its timestamp and source (on screen, spoken, or
  implied by a visual such as a before-and-after).
- Match each to a fact ID in `facts.json`. `pass` needs every claim matched to
  a `supported` fact, or a `perishable` fact inside its freshness window,
  with wording no stronger than the fact. Comparatives also show their
  conditions on screen when the claim depends on them.
- No claims at all is a `pass` with that stated in the evidence.

### brand_copy

- Search the on-screen text and the transcript for each banned word (whole
  word, case-insensitive, simple plurals).
- Check each required line whose `when` condition holds, and the trademark
  mark on the first on-screen use of each mark.

### speech_intelligible

- Run `speech_to_text` on the cut. Compare the transcript with the locked
  lines word by word. A missing, swapped or garbled product name, offer or
  CTA word is `fail`; a garbled filler word is noted in the evidence.
- Listen to any span the transcript marks as low confidence before passing.
- `not_applicable` only for a cut with no speech.

### loudness_target

Measure with FFmpeg and record `input_i` and `input_tp`:

```bash
ffmpeg -nostdin -hide_banner -i <cut> -af loudnorm=I=-16:TP=-1.5:print_format=json -f null -
```

Record them as `measured.integrated_lufs` and `measured.true_peak_dbtp`. The
report recomputes the result against `loudness_target` and rejects a status
that disagrees with the numbers.

The default target follows the audio-video alignment contract: -16 LUFS
integrated with peaks at or below -1.5 dBFS. `loudnorm` reports true peak, which
is never below the sample peak, so the check requires `true_peak_dbtp` at or
below -1.5; passing it also meets the contract's -1.5 dBFS ceiling. The ±1 LU
integrated tolerance (`tolerance_lu`) is a workspace heuristic, not a contract
value; a delivery record may set its own.

### disclosure_recorded

- Paid deliverable: `pass` needs `disclosure_record` pointing at the decision
  record, copied or linked into the check folder, for the same
  `deliverable_id`, with `decided_by: user`, the user's quoted words and a
  decision of `disclose`, `not_required` or `declined`. When the decision is
  `disclose`, also confirm the label appears as decided.
- Unpaid or internal deliverable (showreel, review cut, pitch reel):
  `not_applicable`, and the cut carries no AI label.

## Filled checklist example

```json
{
  "schema_version": 1,
  "deliverable_id": "glow-serum_hook-question_9x16_15s_v01_meta-instagram-reels",
  "video": "projects/glow-serum-9x16/studio/renders/glow-serum_hook-question_9x16_15s_v01_meta-instagram-reels.mp4",
  "video_sha256": "<64 hex characters>",
  "duration_s": 15.0,
  "paid": true,
  "placement": "meta-instagram-reels",
  "reveal_time_s": 1.5,
  "checks": [
    {
      "id": "product_reveal",
      "status": "pass",
      "evidence": "Bottle identifiable in the creator's hand, label facing camera.",
      "timestamps": [1.25],
      "frames": ["opening/frame_00005.png"]
    },
    {
      "id": "loudness_target",
      "status": "pass",
      "evidence": "loudnorm measurement",
      "measured": {"integrated_lufs": -16.3, "true_peak_dbtp": -1.8}
    },
    {
      "id": "disclosure_recorded",
      "status": "pass",
      "evidence": "User chose end-card disclosure and platform labels.",
      "disclosure_record": "disclosure_glow-serum_hook-question_9x16_15s_v01_meta-instagram-reels.json"
    }
  ]
}
```

The real checklist lists all ten checks exactly once.
