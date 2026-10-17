# Edit Decision List

The EDL is the structural source of truth for a rebuild. It records what the
reference does, measured first and interpreted second. Load it before routing.

## Measurement order

1. `ffprobe`: picture duration, fps, dimensions, audio stream presence. Use the
   video-stream duration, not the container duration.
2. `ffmpeg` scene detection for hard cuts; record each cut time. Dissolves,
   whip pans and speed ramps hide from scene detection, so confirm them on a
   5–8 fps frame strip.
3. Model analysis per segment (shot size, camera, subject, action, text) after
   the cut list is fixed, so the model describes segments rather than inventing
   them.
4. Beat grid when music is present: beat and downbeat times from audio
   analysis, then each cut's offset to the nearest beat in milliseconds.

Correct model boundaries to the measured cuts and record every correction.

## Segment shape

```json
{
  "schema_version": "1.0",
  "reference": {
    "sha256": "…",
    "duration_s": 12.48,
    "fps": 30,
    "aspect_ratio": "9:16",
    "has_audio": true,
    "rights": "owned | permitted | unknown"
  },
  "segments": [
    {
      "id": "seg-001",
      "start_s": 0.0,
      "end_s": 0.9,
      "entry": "hard_cut | dissolve | whip | match_cut | speed_ramp | continuous",
      "shot_size": "close-up",
      "camera": "static | push-in | whip pan | orbit …",
      "subject_slots": ["slot-a"],
      "action": "observable action in one sentence",
      "motion": [
        {"layer": "hero", "property": "scale", "from": 0.8, "to": 1.0,
         "start_s": 0.0, "end_s": 0.5, "easing": "expo.out"},
        {"layer": "title", "property": "mask_reveal", "direction": "left_to_right",
         "start_s": 0.2, "end_s": 0.6, "easing": "power3.out"}
      ],
      "text_events": [{"start_s": 0.2, "end_s": 0.8, "role": "title"}],
      "beat": {"index": 4, "offset_ms": -18},
      "route": null
    }
  ]
}
```

- `motion` is the segment's **motion inventory**: each animated layer with
  property, values, timing and easing, estimated from a frame strip at 24–30 fps
  (step through the segment, not just keyframes). It is what a layered rebuild
  reproduces; record uncertainty rather than inventing values.
- `route` stays `null` until segment routing assigns it.
- Segment IDs are stable. Merging or splitting a segment creates new IDs and
  invalidates dependents.
- Describe subjects by role (`slot-a`, `hero product`), never by the
  reference's real people or brands.

## Tolerances

| Item | Default tolerance |
| --- | --- |
| Cut time | 2 frames at the reference fps |
| Beat offset | Keep the reference offset ±40 ms |
| Segment duration | ±5 % or 2 frames, whichever is larger |

A looser tolerance needs a recorded reason, for example a generated clip whose
hold was clone-padded to land the cut.

## Long references

For more than about 20 s or 25 segments, window the analysis on hard cuts and
merge afterwards. The long-pin rules in `template-factory` apply when that
skill is available; otherwise keep windows to 15–20 s and carry a state ledger
(subject positions and held props) across window boundaries.
