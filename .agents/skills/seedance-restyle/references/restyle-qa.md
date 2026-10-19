# Restyle QA

Focused reference for `seedance-restyle`. Read [the entrypoint](../SKILL.md)
for routing and caller responsibilities.

- [Picture checks](#picture-checks)
- [Audio checks after mux](#audio-checks-after-mux)
- [Failures and repairs](#failures-and-repairs)

## Picture checks

Play the silent output at full speed, then step through it beside the source.
Record each item as pass, fail or not applicable.

- **Medium coverage.** Every person, prop, surface, sky and effect is in the
  style. No photographic patches, especially faces, hands and backgrounds.
- **Style stability.** Line weight, texture scale and palette hold across the
  clip and across cuts; no frame-to-frame crawl beyond the style's intended
  boil.
- **Content kept.** Subject count, screen positions, actions, key props and set
  layout match the content inventory.
- **Identity cues.** Each person keeps hair shape, wardrobe colours and
  silhouette on every appearance; anchored characters match their Virtual
  Portrait.
- **Motion and timing.** Poses at each beat, contacts, camera path and cut times
  match the source. Stepped styles still hit beat poses.
- **No lettering.** No generated text, logos or signage copy; source text
  surfaces show abstract shapes.
- **Same place.** The background reads as the source's own place in the new
  medium; no different city, landscape or interior has been substituted.
- **Technical.** Clean decode and no audio stream for the silent route. Compare
  actual duration, frame timestamps, playback speed and cut boundaries with the
  approved source span. Do not assume an 8n+1 frame guarantee or a blanket
  duration tolerance. A mismatch needs review against the agreed target, not
  an automatic trim or retime. Check for unintended black side bars.

## Audio checks after mux

Apply after the post-audio route is muxed, following the
[video-to-video inputs contract](../../../contracts/video-to-video-inputs.md#post-audio).

- The final duration matches the agreed picture timeline; any authorized
  padding or trim is recorded on a derivative, with originals preserved.
- Two or three sync points land on the picture.
- Listen in full and inspect on-screen speech against the redrawn mouths.
  Judge sync against the agreed target, not assumed tolerance for a drawn
  style. Propose a scoped timing repair or new take for visible drift;
  re-voicing requires authorization and is not by itself a lip-sync fix.

## Failures and repairs

Change one variable per retry: wording, style reference, anchor or route.

| Symptom | Likely cause | Repair |
| --- | --- | --- |
| Output stays photographic | Incomplete medium coverage in this output | Check the medium lock and conflicting references; consider a supported alternative route after review |
| Subject redrawn but requested background surfaces stay photographic | Wording, references or route may be contributing | Name the missed surfaces; optionally propose an approved same-place environment image or supported route change. Honor a no-image request |
| The scene moved to a different place (city became sea) | The prompt named a new location, or the environment image shows another place | Describe the source's own place in the environment image and the prompt; name no different location unless the user asked for one |
| Extra chair, ashtray or cup appears | The environment image holds objects the shot lacks | Name each in the Environment Reference Role as not to be used; remove them from the image |
| Hair or face colour changes toward a style frame | A style frame carries a different look | Say the source owns identity and keep hair colour in the scope; prefer an environment image to person-bearing frames |
| Faces stay photographic inside a drawn world | Face protection or photoreal anchor | Remove photoreal wording; use a medium-matched anchor |
| Layout or subjects change | Style image read as content | Use a style image with different content, or drop it |
| Style drifts between cuts | Fragment too long or conflicting | Shorten to the medium lock; one style only |
| Extra people or props appear | Count not stated | State per-cut counts in the scope |
| Lettering appears on signs | Text surfaces not given a disposition | State abstract shapes for each text surface |
| Stepped cadence misses key poses | Stop-motion timing over fast action | Add the cadence note and name the beat poses |
