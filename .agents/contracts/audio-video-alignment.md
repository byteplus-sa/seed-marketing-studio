# Audio-video alignment

Native generated audio is sufficient unchanged. Preserve supplied audio and
source masters too. Finalization alone does not authorize audio modification.
Do not normalize, EQ, compress, limit, duck, carve, fade, splice, pad, trim,
time-stretch, replace or re-voice a soundtrack merely to finish a video.
Do not suppress native sound to create a post-production requirement.

Explicitly requested silence, exact supplied masters, separate lip-sync audio
and audio edits remain scoped capabilities. Apply only the requested changes;
`approve_for_me` and a generic "finalize" instruction do not expand audio scope.
Generate each scene at its natural supported duration. Verify native input and
output audio support for the selected model, operation and transport; unknown
support stays unresolved, not a reason to mute, extract or mux automatically.

## Requested synchronization

Separate Seed Audio dialogue is opt-in when the user requests lip-synced
dialogue audio. Only then apply these alignment steps:

1. Preserve exact dialogue in both audio and video prompts; bind the chosen audio reference in each applicable shot.
2. Inspect actual audio duration and line timing before submission. If the requested alignment cannot fit, report the conflict and obtain a scoped decision. Do not silently pad picture or trim sound.
3. Persist the audio path, SHA-256, verified duration, and dialogue-to-shot alignment in the owning manifest. The generation request contains the same ordered audio reference.
4. Use second-level prompt timing when explicitly requested or necessary for the requested synchronization/editing operation. Ordinary prompt composition does not add per-shot seconds by default.
5. Replacing audio invalidates dependent review hashes. Preserve old snapshots/takes; obtain a new review for the changed request.
6. Provider success places output in `review`. Inspect lip sync, dialogue placement, audio streams and decode integrity. Record a hash-bound audio/video review; a mode-authorized agent decision or explicit user decision may approve only a passing take.

## Inspection and transport

Read-only `ffprobe`, decode-to-null, loudness measurement, ASR and actual
listening remain available. Report defects and missing inspection capability;
measurements alone never prove an audible pass or authorize repair.

Preserve independent picture and audio tails, including the last word. Unequal
durations are not permission to use padding, truncation, fades or `-shortest`.
For explicitly requested assembly or exact-master attachment, prefer compatible
stream-copy transport; disclose required transcoding or timeline changes and
obtain approval before applying them. Preserve originals and record derivative
hashes, actual timing and the authorized recipe. No delivery loudness target or
showreel gain matching is imposed by default.

Studio rendering, provenance, inspection and final-master locks remain separate
delivery requirements. They do not require an audio-processing pass, nor do they
guarantee byte-identical audio through an encoding renderer. An exact-master
requirement must be verified and any renderer conflict reported, not waived.
