# Reframe Recipe

Read [the entrypoint](../SKILL.md).

## 1. Subject boxes from seed_understand

**Boxes are measured, then checked.** For each shot, sample frames at the cut
start, every 0.5 to 1 s, and at any marked action. Ask `seed_understand` for a
JSON list per frame:

```json
{"time_s": 1.5, "subjects": [
  {"label": "product", "box": [0.42, 0.31, 0.18, 0.40]},
  {"label": "face", "box": [0.20, 0.12, 0.14, 0.18]}
]}
```

`box` is `[x, y, width, height]` as fractions of the source frame. Save the
list as `projects/<campaign>/delivery/<shot-id>_subjects.json` with the source
hash. Open two or three frames and confirm the boxes; a model box can be off by
several percent, so pad each by 3 to 5% of the frame before cropping. Labels
come from the brief's priorities: product and logo first, then face, then hands.

## 2. Crop window math

For a source `Sw×Sh` and target ratio `r = Tw/Th`:

- **Window size:** the largest window of ratio `r` inside the source:
  `Ww = min(Sw, Sh × r)`, `Wh = Ww / r`. A smaller window (punch-in) is allowed
  while `Wh` stays at or above the target height; below that, record the
  softness or regenerate.
- **Window position:** centre it on the union of the padded priority boxes,
  then clamp to the source edges.
- **Safe-zone fit:** map the target safe rectangle (from `safe_zones.py zones`)
  back into source pixels through the window; the union box must sit inside it.
  When it cannot, the shot needs regeneration in the target ratio or a
  different priority (for example product over face) recorded with a reason.

## 3. Studio composition per ratio

One Studio project per delivered ratio keeps each render a single canvas:

```bash
uv run python .agents/scripts/studio_project.py init projects/<campaign>-4x5 \
  --aspect 4:5 --resolution 1080p
```

Place the same approved takes as the master (the shot list and takes must match
the master's locks). Inside each shot frame, wrap the video in a non-timed crop
wrapper and keyframe `x`, `y` and `scale` with GSAP on that wrapper:

- hold the window still while the subject holds;
- move with an eased tween only when the subject leaves the safe rectangle;
- never move during a held product beat or a logo reveal;
- reuse the master's cut points; reframing never retimes a cut.

Overlay compositions (supers, CTA, captions, end card) are separate graphics
tracks laid out from the target safe rectangle in pixels.

## 4. When to stop reframing

- The union of priority boxes is wider than the safe rectangle.
- Two subjects interact across the frame and the crop would drop one.
- The crop window falls below the target height by more than about 15%.

Each is a regeneration case. Regeneration reuses the approved references and
prompt with only the ratio changed, goes through prompt-review and the 480p
draft rule, and is registered before submission.
