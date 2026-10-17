# QA Contact Sheet

Read [the entrypoint](../SKILL.md).

## What goes on the sheet

One row per delivered cut; columns are the frames that carry the message:

| Column | Frame |
| --- | --- |
| Hook | The first frame and the frame at the hook's declared end |
| Product | The first frame where the product is identifiable |
| Supers | Every frame where a super, price or claim first appears |
| Captions | One frame per caption cue that sits lowest or longest |
| End card | The CTA and logo lock-up frame |

Snapshot each frame from the rendered cut (`studio_project.py hf <project>
snapshot ...`), then composite the SVG from `safe_zones.py overlay` on top with
the element boxes passed as `--box`. The sheet is a review aid only; decisions
are recorded through the project's validated writers.

## Pass criteria

- **Inside the safe rectangle:** logo, product label, CTA, price, supers and
  caption block pass `safe_zones.py check`.
- **Product identifiable** in its column, not cut by the crop, and not hidden by
  a caption.
- **Legible at thumbnail size:** shrink the sheet to about 25% and read the CTA.
- **Same copy as the approved script** on every cut; no line reflowed into a
  different meaning.
- **Duration** within the placement's bounds from `ad-platforms.json`.
- **Unpublished safe zones** (`tiktok-in-feed`, `youtube-shorts`, landscape
  YouTube placements, unverified feed) are checked against the platform's own
  template or preview, and the sheet notes which template and date were used.

## Recording

**One QA folder per deliverable:** `projects/<campaign>/delivery/qa/<deliverable-id>/`,
in the campaign project even when the cut renders in a ratio project. The
contact sheet, overlays and the `ad-creative-check` evidence for that cut all
live there, with the render hash of the cut.

The deliverable id is the variant name plus the placement:
`{campaign}_{concept}_{axis-values}_v{nn}_<placement>`, for example
`lumo-launch_stays-hot_hook-a_9x16_v01_meta-instagram-reels`. Placements that
share one cut get one id each, all pointing at the same render. Use the same id
as the ratio project's `render --name`.

A failing item is fixed in the per-ratio overlay or crop and the cut
re-rendered; never patch a delivered file outside Studio.
