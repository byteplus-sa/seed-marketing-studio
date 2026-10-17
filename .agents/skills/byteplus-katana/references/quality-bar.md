# Quality Bar

Learned by putting a first build next to a strong reference aura edit reel.
The first build was judged ugly; these are the differences that mattered.

| Reference aura edit | Cheap-looking build |
| --- | --- |
| A different cinematic video shot on almost every beat: overhead, close-up, low-angle walk, night | One static cutout repeated on several beats |
| The character fills the frame; photographic light (golden hour, sodium night, flare) | Small figure centred in empty space |
| Photographic backgrounds with grain | Flat red, yellow or white cards |
| Words on the beat in mixed fonts and colours: red condensed, heavy white sans, cream italic serif; arcs and perspective | One condensed font with thick black meme outlines everywhere |
| Restrained effects on footage: negative or thermal invert, split screen with a thin coloured divider, a circle-cut face with curved text, an inset close-up | Pill badges, concentric clip-art rings, counters |

## Checklist before building

- At least five distinct generated setups for a people-led edit (vary size,
  angle, time of day, action), each 4-5 s and moving.
- First frames from Seedream with the locked identity cutouts as references;
  inspect identity on every still before animating.
- Seedance image-to-video with a first frame: **omit `ratio`**; the provider
  rejects it and the output follows the first-frame image.
- Type: three families at most, no outlines, soft shadows, tight tracking for
  condensed type; one word or short phrase per beat, each landing on its cut
  frame.
- Global finish follows the reference: add grain, vignette or an RGB split on
  flash frames only when the reference shows them, as HyperFrames layers. Keep
  the generated takes in their original colours; no grade by default.
- A meme caption uses the platform-native style (white rounded box, black
  sans, sentence case), not outlined impact type.
- Draft at 480p, review the edit, then promote only the shots that made the
  cut to the delivery resolution. Re-check each promoted shot, because the
  final render is a new picture, not an upscale of the draft.

## Generated-shot lessons

Observed in a follow-up live build (2026-10-16); generic rules for
`fresh_generation` shots.

- **Physical outcomes need frame locks.** When a shot must end in a specific
  state (who wins, what lands where), lock it with a first and last frame pair
  from Seedream; a last frame alone is rejected. Read the result by the
  direction of motion and conventional signals (a raised winner's arm, a
  slumped loser), not by the end position of one hand, and zoom-check hands.
- **Name arms in camera terms.** In side views the models default to both
  near-camera arms; say which arm is nearest the camera for each person, and
  name hands by anatomy plus frame side.
- **Two identity references can add a second character.** Seedream given two
  characters' references may draw both when only one is asked for; inspect
  every still before animating.
- **Mirroring in post flips handedness.** A horizontal flip turns a right-handed
  action left-handed; regenerate instead when handedness matters.
