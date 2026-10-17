# Ad platform placements

**Platform specs are dated data, not rules of nature.** Every value below was
read from the cited official page on **2026-10-17**. Platforms change these
pages without notice: re-verify a placement against its source before a paid
delivery and update both this file and
[ad-platforms.json](ad-platforms.json) in the same change. The JSON is the
machine-readable copy; it validates against
[ad-platforms.schema.json](schemas/ad-platforms.schema.json).

## How to read the status

| Status | Meaning |
| --- | --- |
| `verified` | Ratio, resolution, duration and safe zone were read on the official page |
| `partial` | Some values are published; missing ones are `null`, never estimated |
| `unverified` | The official page was not readable; every value must be confirmed before use |

**A `null` safe zone means unpublished.** Tools return "unpublished, use the
platform template" for it and never invent margins. Lay out against the
platform's own downloadable template or preview instead.

## Placements

| ID | Platform | Placement | Ratio (accepted) | Resolution | Duration | Safe zone (top / bottom / sides) | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `tiktok-in-feed` | TikTok | In-feed auction ad (non-Spark) | **9:16** (16:9, 1:1) | min 540×960; no recommended value | up to 600 s | **Template files only**, no numbers | partial |
| `meta-instagram-reels` | Meta | Instagram Reels | **9:16** | 1440×2560 recommended; min width 500 px | 0–900 s | **14% / 35% / 6%** | verified |
| `meta-instagram-stories` | Meta | Instagram Stories | **9:16** | 1440×2560 recommended; min width 250 px | 1–3600 s; under 16 s plays whole | **14% / 35% / 6%** | verified |
| `meta-feed` | Meta | Facebook and Instagram Feed | 4:5 (1:1) | unverified | unverified | unverified | unverified |
| `youtube-shorts` | YouTube | Shorts ads | **9:16** (16:9, 1:1) | not stated | up to 180 s; first 60 s play in feed; 10–60 s recommended | Right-hand panel and CTA card; no numbers | partial |
| `youtube-skippable-in-stream` | YouTube | Skippable in-stream | 16:9 (not stated) | not stated | no max; under 180 s recommended; skip at 5 s | not published | partial |
| `youtube-bumper` | YouTube | Bumper | 16:9 (not stated) | not stated | max 6 s | not published | partial |

## Conflicts kept visible

- **TikTok duration:** the June 2026 in-feed page allows **up to 10 minutes**;
  older TikTok spec pages list **5–60 s**. The current page is recorded; check
  again before delivery.
- **TikTok safe zone:** published **only as downloadable templates** (standard
  left-to-right, Arabic right-to-left, each with and without an anchor). The
  zone depends on ratio, ad-caption length and extra formats, so no fractions
  are recorded.
- **Meta feed:** the feed spec pages were behind a login on 2026-10-17. 4:5 and
  1:1 are widely cited but **unverified**.
- **YouTube Shorts resolution:** 1080×1920 is often quoted but is **not stated**
  on the cited page.
- **YouTube in-stream and bumper ratio:** the format page lists lengths, not
  ratios. 16:9 is the conventional landscape player ratio; confirm it.
- **YouTube bumper minimum:** the table reads "6 seconds (>=5 seconds
  minimum)"; the minimum is left `null` because the wording is ambiguous.

## Placement notes

- **TikTok in-feed:** 16:9 needs at least 960×540 and 1:1 at least 640×640;
  at most 500 MB; bitrate at least 516 kbps. The ad caption is platform text
  (white, fixed font) and is not part of the video.
- **Instagram Reels:** minimum width 250 px under 30 s, 500 px at 30 s or more.
  Captions optional but recommended; sound strongly recommended; no licensed
  music.
- **Instagram Stories:** 16 s or longer may split into up to three cards;
  aspect ratio tolerance 1%.
- **YouTube Shorts:** CTA button at 3 s (Performance Max, App, Demand Gen) or
  10 s (Video View, Video Reach); horizontal assets get blurred bands; the page
  asks for AI labels where regulation requires them.
- **YouTube skippable in-stream:** brand and hook should land before the 5 s
  skip.

## Using the data

- **Safe-zone math:** `uv run python .agents/skills/ad-delivery-formats/scripts/safe_zones.py zones --placement <id> --size WxH`
  prints the title-safe rectangle in pixels. Margins round inward so the
  rectangle never exceeds the published zone.
- **Several placements, one cut:** pass `--placement` more than once; the
  result is the intersection, and the ratios must match.
- **Ratio tolerance:** a `--size` whose ratio differs from the placement by
  more than 1% is rejected rather than stretched.
- **Captions and supers** sit inside the safe rectangle; platform UI text
  (ad caption, primary text, headline) is set in the ad manager, not burned in.

## Sources

| Placement | Official source (read 2026-10-17) |
| --- | --- |
| TikTok in-feed | [TikTok Ads Manager: Auction In-Feed Ads (last updated June 2026)](https://ads.tiktok.com/resources/help/article/tiktok-auction-in-feed-ads?redirected=1) |
| Instagram Reels | [Meta Ads Guide: Instagram Reels video](https://www.facebook.com/business/ads-guide/update/video/instagram-reels) |
| Instagram Stories | [Meta Ads Guide: Instagram Stories video](https://www.facebook.com/business/ads-guide/update/video/instagram-story) |
| YouTube Shorts | [Google Ads Help 16041697: Shorts ads asset specs](https://support.google.com/google-ads/answer/16041697) |
| YouTube in-stream and bumper | [Google Ads Help 2375464: About video ad formats](https://support.google.com/google-ads/answer/2375464) |
