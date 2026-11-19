# Audio and Lip-Sync

Focused reference for `seedance-motion-recast`. Read [the entrypoint](../SKILL.md)
for mode selection, gates and caller responsibilities.

- [Native audio](#native-audio)
- [Requested audio routes](#requested-audio-routes)
- [Re-voicing over the kept soundtrack](#re-voicing-over-the-kept-soundtrack)
- [Speaker ownership](#speaker-ownership)
- [Preparing source audio](#preparing-source-audio)
- [Lip-sync QA](#lip-sync-qa)

## Native audio

Native generated audio is sufficient unchanged. Bind the selected source with
its sound when input support is verified, and describe the brief's sound intent.
The [video-to-video inputs contract](../../../contracts/video-to-video-inputs.md#audio-scope)
owns capability checks. Unknown support stays unresolved; do not mute, extract
or mux automatically. Native output does not guarantee exact source audio.

## Requested audio routes

Use these only when explicitly requested. Silence uses supported silent-output
controls without adding a bed. An exact master requires verified preservation.

| Route | Use when | Source | Lips |
| --- | --- | --- | --- |
| **Original** | The user requires the exact source soundtrack | Verified preservation or scoped stream-copy attachment | New mouths follow the source mouth motion |
| **New** | The brief asks for new music, SFX, ambience or voice | Seed Audio or an approved library track | No on-screen speech, or a re-voiced line |
| **Mixed** | Keep the source dialogue, replace the bed (or the reverse) | Separated stems plus new audio | Kept dialogue follows the source mouth motion |
| **Re-voiced** | New words, language or voice | Post voice overlay through `audio-dubbing` | Check sync; lip-sync work is opt-in |

Voice rules:

- Keeping a real person's recorded voice, or cloning its timbre for a new
  character, requires that person's recorded voice consent, separate from
  footage rights. See the
  [production policy](../../../contracts/production-policy.md).
- Separate lip-sync audio is opt-in. When the user asks for it, follow the
  [audio-video alignment contract](../../../contracts/audio-video-alignment.md).
- When lips are off-screen or not the focus, a voice overlay in post avoids
  re-rendering the mouth.

## Re-voicing over the kept soundtrack

A Re-voiced or Mixed route changes words or a voice, not the whole sound.
Keep the source's music, ambience and effects unless the brief replaces them.

1. Inspect the source and record protected picture, words and non-voice sounds.
2. Honor the user's repair extent. A defect does not automatically select word
   surgery, fades, pitch matching or a full dub. Offer a retake or repair as
   appropriate; apply only the explicitly authorized audio change.
3. Verify protected soundtrack layers after re-voicing. Do not normalize the
   returned audio automatically.
4. If attachment is requested, prefer compatible stream copy and verify
   picture hashes, sync and independent tails; disclose required transcoding.

## Speaker ownership

Speech windows come from the subject map or your own inspection. Map each
window to one named character. A line whose speaker is removed or turned into a
background extra needs an explicit decision: cut the line, give it to a mapped
character, or keep it off-screen.

## Preparing source audio

1. Keep the original source and soundtrack. Extract a diagnostic or editing
   derivative only when that selected capability needs it; record its hash.
2. For an explicitly requested Mixed route, separate voice and background with the VOD voice
   separation tool. Record the task ID, output hashes and time range.
3. Preserve independent audio tails. A partial probe is not permission to trim
   the delivery soundtrack; any audio edit uses its specifically approved span.
4. Transcribe kept dialogue with speech-to-text and keep the word timings as the
   reference for lip-sync QA.

## Lip-sync QA

Apply to the actual output when any character speaks on screen:

- Transcribe the final audio with `speech_to_text` and diff it against the
  intended lines; the transcript is the authority for words. Kept dialogue
  matches the source; replaced or translated lines match the approved script.
  Accent and pronunciation verdicts need a native listener, not a model.
- Each line comes from the mapped character's mouth, never from a removed
  subject or an extra.
- Step through close frames on plosives (p, b, m) and open vowels; mouth shapes
  land on the audible sounds.
- Measure the audio-to-mouth offset at two or three syllables. An offset that
  grows across the clip suggests a duration mismatch between picture and audio.
- Listen in full. Loudness readings and waveforms do not replace listening.
- Report visible drift and obtain a scoped repair or retake decision rather
  than accepting or re-voicing it silently.
