# Production Defaults

Read [the entrypoint](../SKILL.md). Load this reference when planning a project's
stage flow, before the first paid video submission, at assembly, and whenever a
take needs a fix. These defaults come from observed production runs; they are
not provider guarantees. Explicit user instructions may override creative
defaults, but not the native Draft requirement for new Seedance 2.5 generations.
Exact tool parameters live in the `ark-mcp` Seedance reference; this file says
when to use them.

## Review depth

Read the independent `review_mode` and `approval_mode` in `project.md`.
Default mode uses minimal preflight and actual final sanity, one generated
image and draft-first video. Do not load strict checklists or create
mandatory craft reports. The detailed review procedures below are strict-mode
or explicitly requested guidance; preserve capability, hash, reference, rights,
claims, disclosure, native-human and registry requirements in both.

## 1. Draft first, then final

Both modes start every new Seedance 2.5 generation with explicit
`resolution: "480p"` and boolean `draft: true`, including edits and variants.
A delivery target alone does not skip this pass. Resolve schema or transport
conflicts without dropping the flag; other models without native Draft use a
plain 480p test.

1. Freeze and review the full request (prompt, ordered references, duration,
   ratio, `generate_audio`, task type) and submit it with `resolution: "480p"`
   and `draft: true`. **Edit inputs only before the Draft.**
2. Inspect the Draft's playback, motion, continuity, shot plan and audio, and
   record a passing selection under the project's approval mode. For
   multi-shot work, review the draft assembly too.
3. Promote with `draft_task_id`. The promotion reuses prompt, references,
   seed, duration and audio settings, and carries only `draft_task_id`,
   `resolution` and `watermark` (plus optional chaining fields). It costs about
   five times the Draft at 1080p, so promote only selected drafts.
4. Re-inspect the final, including a fresh speech-to-text pass: the final
   soundtrack is not byte-identical to the Draft's, and words or timing can
   move.

A plain 480p request from another model without native Draft cannot be promoted;
its final is a new paid request that may change picture, timing or audio, and it needs its
own registration and review. When a fix requires a prompt change, write a new
Draft rather than promoting the old one.

## 2. Choose the audio route at the brief

Record one audio route in the brief and carry it into every shot request:

| Route | When | Request setting | Sound built |
| --- | --- | --- | --- |
| Native dialogue | Characters speak on camera and lip sync matters | `generate_audio: true` | In the clip; patch words in post when needed |
| Picture only, post audio | Ambience-only, score-driven, music-video or wordless spots | `generate_audio: false` | Seed Audio score, ambience and SFX in post |
| Separate lip-sync audio | Only when the user asks for it | Audio reference bound per the alignment contract | Before the shot |
| Silent | The deliverable is silent | `generate_audio: false` | None |

An explicit request for an original native soundscape, musical ad or
one-generation audiovisual draft uses native audio when supported. Preserve
that scope; do not substitute silent footage or add separate audio generation.
Choose sound density, contrast and recurrence for the idea, not "no music"
as a default for fictional or claim-free products.

With native audio on, a "no music, no spoken words" line often does not hold:
in observed ambient-only runs, speech, chants or score leaked into about two
thirds of clips. Do not rely on a negative audio line for a piece whose sound
must stay ambient or score-led; generate the picture silent and build the bed
in post. Say in the brief that post beds are laid to the cut and are not
frame-synced to on-screen action unless SFX are placed by timestamp.

Plan sound and editorial intent before generation in the existing brief or
scene notes: anticipation, what a cut reveals or withholds, and the purpose of
silence, texture or an accent. A sound-led reveal can guide picture without
requiring finished audio early. Final assets and cue positions follow the
measured edit and actual listening; this does not change audio-route, rights
or spend authorization.

## 3. Cinematic structure for ads and TVCs

A long source is not inherently a continuous take or stock footage. Distinguish
provider generations from internal shots and honor the user's count. For an ad:

- Establish the hook, viewer motivation, development, payoff and product
  connection. New camera angles without new meaning are not development.
- Choose internal shot count from that argument and the runtime. One source
  may contain native cuts. Separate short sequences are an option for
  independent edit control only within the approved source count.
- Give every shot a lens intent, a purposeful move or hold, a named light source
  and depth layers (foreground, subject, background), carried from the
  `seedance-shot-design` plan.
- A sequence may include a standout image if useful; no `wow` count is required.
- Use concrete action and intent instead of mood words alone; state the
  motivated move or hold. Gentle or abrupt performance can be appropriate.
  A static shot carries its recorded reason.
- About 0.8 s per shot and about 7 shots per clip are provisional generation
  heuristics, not provider limits or guaranteed merge/drop thresholds. Preserve
  requested rhythm and source timing without automatic retiming or shot removal.
  Offer assembly for precise cuts or omitted action, within authorization and
  generation scope; return genuine feasibility conflicts rather than changing locks.
- Set ratio as a request parameter, never as a sentence in the prompt. 21:9 is
  an accepted Seedance 2.5 ratio for a scope look.

## 4. Storyboards are planning and review only

Never bind a storyboard grid, contact sheet or board panel as a Seedance
reference. Observed: panel numbers, corner labels and the sketch or watercolour
look leaked into the video, and output-copyright rejections rose; takes came out
clean once the board was removed. Translate the board's staging into prompt
text and bind only element references (characters, locations, props, locked
screens). Audit every take with frame samples plus top-left corner crops before
selection.

## 5. People in video inputs

Extension (`omni_reference_task_type: extend`) and video-to-video with clips
that contain generated or real people are rejected with a privacy error unless
the identities are registered `asset://` Virtual Portrait assets. Plan for it:

- Without Virtual Portrait assets, cover long actions with short single-pass
  clips at natural duration, held together by a locked blocking map and
  matching first frames, then assemble.
- With assets, follow the video-to-video inputs contract: bind identities as
  `asset://` references, submit a muted source (`generate_audio: false`), and
  add original or new audio in post.
- A last-frame-only request is rejected; use first and last frames together.

## 6. Text, overlays and labels

Generated footage stays text-free. Titles, captions, CTAs, logos, packshot copy
and end cards are deterministic overlays added in post. Do not add
"AI-generated", "fictional" or similar labels to reels or clips by default; add
one only when the user, platform or brief requires it.

## 7. Assembly defaults

Technical assembly uses **conform, trim, crop, overlays, end card and mix**.
It also needs artistic acceptance against the brief, not just clean joins.
Inspect full-speed playback and listen when audio is in scope. In existing
review evidence, cite timestamps for the intended attention, revealed or
withheld information, rhythm and payoff (including a deliberate unresolved
ending). Recheck sound hierarchy, silence, anticipation and release, and ensure
trims preserve accepted performance and exact copy. Neither movement nor
stillness is a quality proxy. Unavailable playback/listening stays unresolved;
a critical artistic failure blocks selection until a scoped repair passes.
Keep evidence short in default mode and detailed in strict; no new runtime or
mandatory report is required.

- **No grade.** Keep the original Seedance colours that matched the approved
  drafts. Add a grade, grain, halation, vignette or a capture-format look only
  when the brief records one. A look such as camcorder or MiniDV is a post
  treatment; the prompt word alone produced clean cinema.
- Decode 10-bit HEVC finals as limited-range BT.709, tag outputs BT.709 and
  dither to 8-bit. Avoid FFmpeg `vignette` inside a high-bit-depth chain; it
  drops to 8-bit YUV and shifts hues.
- Render each clip to an **exact-length lossless intermediate** in whole frames,
  pad or trim its audio to the same length, join with the concat demuxer and
  encode once. The concat filter needs `setsar=1`. Read the video-stream
  duration, not the container duration.
- Check frame edges: the model sometimes draws rounded black side bars; a small
  centre punch-in on that clip removes them.
- Normalize to the delivery loudness target from the alignment contract, then
  place the result in Studio and render it there.

## 8. Review and fix loop

Run these checks before a take passes, and use the narrowest fix.

- **Words:** `speech_to_text` on the local file is the authority for spoken
  words. A model summary is not evidence. Accent and pronunciation verdicts need
  a native listener; `seed_audio_understand` cannot judge accent and can
  mislabel music.
- **Speech timing:** lines land 0.5–1.5 s late and later after long pre-line
  action, and speech fills to the clip end. Trimming a clip's head does not
  lengthen the tail after the last word; fix a short tail with a retake that
  shortens pre-line action, a freeze-hold, or a recorded waiver.
- **Word-scoped audio fixes:** patch only the wrong word windows; never re-dub a
  whole track. Transcribe with word times, splice pitch- and loudness-matched
  replacements with short fades, and prove that samples outside each window are
  identical. A replacement whose pitch differs from the speaker by more than
  about 10% is heard as a voice change; leaving a mild mispronunciation can be
  the better choice.
- **Re-voicing keeps the source soundtrack:** when a model re-voices a clip,
  send the original video with its audio, name the words to fix, take the full
  audio back, normalize to the original loudness and mux it over the untouched
  picture (copy the video stream and confirm its hash is unchanged). Measure the
  original first: loudness over time, its own transcript and its non-voice
  sounds, then confirm they survive.
- **Music beds:** provider audits reject a share of music generations; diagnose
  each rejection before revising or retrying. Tempo and arc timing are only roughly obeyed, so measure and
  pad or splice in assembly. Short lines truncate unless the prompt states the
  clip length and trailing silence.
- **Retakes:** fix hard-gate failures within the requested scope with one targeted
  change per retake, written as a revision (locked decisions, delta,
  acceptance, known rejections, invalidation scope).

Compare the actual take to its creative argument as well as its technical
contract. A decoded file with stable props may still miss its reveal, contain
blank performance or repeat an empty action. Record that limitation; technical
success is not creative acceptance. Missing perception stays untested, and a
weak take never authorizes an automatic retry or upscaling.
