# Seedance talking-head templates

Inputs: the likeness binding approved at gate 2 (an authorized `asset://`
reference, or the character sheet as `reference_image` where that route is
sanctioned), `audios: [voice clip URL]`, `generate_audio: true`,
`resolution: "480p"` with `draft: true` for the first take, `watermark: false`,
and `duration` from measured or language-aware speech timing, including onset
and final-word tail, within current tool limits. Submit the `seedance_2_5_create_task` tool through
`ark_job_submit`, poll with `seedance_get_task`, and promote the selected draft
by `draft_task_id`. Only send the likeness after the consent and real-likeness
gates are recorded.

These are optional framing recipes, not a default market or performance.
Resolve language, accent, setting, wardrobe, delivery, gestures and final
expression from the current campaign brief and approved talent. News pacing,
statistics, smiles and studio styling apply only when requested.

## A. Locked take for split-screen (ratio 1:1)

Choose the source crop and safe area from the actual destination layout.

```
[Character]
<Name> corresponds to @Image 1. Use only his face, hairstyle, skin tone, build and outfit: <outfit list>. Do not use the grey backdrop or the multi-panel layout of @Image 1. All three panels of @Image 1 show the same one man; the output contains only one person, <Name>, throughout.

[Scene]
<Approved setting and backdrop>. <Approved visible microphone or accessories, if any>.

[Shot]
<Name> delivers <requested subject and performance> straight to camera in one continuous take, in a centered medium close-up. Use <brief-selected gestures tied to exact script words, with anatomical and frame sides>. Keep gestures inside the delivery crop and lips synchronized with the dialogue. After the last word, hold <brief-selected final expression and pose> to the end.

[Style and camera]
Soft frontal key light slightly above eye level with gentle falloff into the dark background, clean 50mm-equivalent look, neutral slightly cool studio grade with natural skin tones. Static locked-off medium close-up at eye level, no camera movement, no cuts.

[Audio reference]
@Audio 1 defines <Name>'s voice timbre, accent and pacing only; do not reuse any words from @Audio 1.

[Audio]
Dialogue language: <requested language and accent>. <Name> says with <brief-selected delivery, emphasis and pauses>: {<full approved script>}
Close lavalier-mic studio voice over quiet room tone. A clean, text-free frame.
```

## B. Vertical take with camera beats (ratio 9:16)

Use for remix edits that go full-screen on the presenter. Add a `[Timeline]`
with 4–5 timestamped beats covering the full duration: medium waist-up →
slow push-in to chest-up on the pivot line → ease back → hold for the closer.
Tie one gesture to one quoted word per beat, keep gestures inside the frame
edges, and end the last beat with a held pose. Add: "Single continuous take,
vertical framing, <Name> centered and facing the camera throughout." and
"Close lavalier-mic studio voice with quiet room tone. No background music."

## Notes

- Measure intended delivery in its language, including pauses, onset and final
  tail. Word counts are language-specific estimates, not permission to alter
  approved dialogue. Keep active gestures visible through the delivery crop.
- Adapt pronouns to the presenter; the templates use one example presenter.
- Wardrobe and accessories come through the sheet, but the lav mic does not
  reliably appear from text alone. If it matters, QA it and say it twice
  (scene + subject).
- Resolve current cost, supported dimensions and Draft/promotion capabilities
  from the selected tool. Keep estimates separate from measured output and
  confirmed billing; do not reuse another production's timings or token counts.
