---
name: seedance-music-video
description: >-
  Write Seedance 2.5 music-video prompts from a song, artist brief, or requested
  format. Map song sections, beat density, performer intent, camera, lyric timing,
  native versus supplied audio, and natural scene duration into the six-part
  formula. Cover rap, dance, performance, narrative, abstract, vertical, and custom
  formats. Use for song-driven visual direction, lyric/performance videos, or
  music-video revisions. This prompt-only leaf does not generate media; the caller
  composes only requested specialist axes and owns review and submission.
---

# Seedance Music Video

Write ready-to-use Seedance 2.5 prompts for music videos. The music is the
fixed brief: every visual decision is planned backward from the track's
sections, beats, and energy. Make the format, the song map, the beat contract,
and the genre lock visible in the prompt, not just the scene content.


## Input and output contract

Input: song structure, desired format, performer locks, beat contract, and audio intent.

Output: a music-video direction block or complete video prompt.

## Procedure and reference loading

Use output-templates for the requested deliverable, specialized-formats for rap/vertical/custom format details, and the core workflow below for song/beat/audio decisions.

Read only the mode-specific resources needed for the request. Reference paths
mentioned in prose are relative to this skill directory unless a link says otherwise.

- [Output Templates](references/output-templates.md) — Output formats.
- [Specialized Formats](references/specialized-formats.md) — Format-specific rules; Custom-format procedure.
- [Hypothetical repairs](references/music-repairs.md) — Read when pacing, lyric timing or a revision fails the intended musical relationship.

## Submission boundary

This leaf returns a prompt package. The caller owns authorization, prompt
review, submission and approval under the workspace production policy; missing
inputs stay unresolved rather than invented.

## Source basis

- Official Seedance 2.5 prompt guide, launch blog, and ModelArk docs — audio
  bracket syntax, `@Audio N` timing-authority contract, the one-take singer
  example, timestamp grammar, and limitations. See `seedance-prompt-25`.
- Music-video craft and beat-sync practice — format taxonomy, song-section
  energy mapping, and section-relative cut density (sources below).
- Genre conventions — per-genre visual recipes, vertical-vs-landscape norms.

Treat recipes as creative guidance, not model capability evidence. Verify audio
reference roles, parameter combinations and duration limits for the current
request. Keep take-specific observations in the owning campaign's review record.

Key third-party sources (accessed 2026-08-20):
[AI music-video production workflows](https://www.creativeainews.com/articles/how-to-make-ai-music-video-2026/),
[Beat-synced 30s edits](https://aitoolsguidebook.com/en/articles/ai-music-video-tutorial/),
and [music-video section-arc planning](https://blog.celtx.com/how-to-write-a-music-video-script/).
The recipes generalize these principles rather than copying published prompts.

## Format & genre bank

Read `references/music-video-recipes.md` after identifying the user's format
and genre. Use one genre recipe plus the matching format rule; do not paste the
whole bank into a prompt.

Formats: `performance`, `narrative`, `conceptual`, `lyric`, `visualizer`, `hybrid`.
(Here and throughout, `visualizer` means a music / audio-reactive visualizer,
not a data or code visualizer.)
Genres: `hip-hop-trap`, `edm`, `pop`, `indie-dream-pop`, `rock`, `rnb-soul`,
`country`, `classical-acoustic`, `abstract-visualizer`, plus a custom template.

## Core principle

The song is the brief. The music drives the video, not the other way around.
Do not write a story first and then smear a song over it — map each song
section to a visual assignment, and let the track's energy, tempo, and vocal
set the pacing, framing, and cut density.

For every prompt, define:

```text
format                 which video type this is (and its direct/indirect address)
song map               each section → visual assignment, energy, and end state
performance ratio      how much screen time is performer vs atmosphere per section
beat contract          which audio events the cuts and camera land on
audio treatment        native audio, or audio-first master used as timing authority
genre lock             one recipe controlling palette, lighting, camera, and rhythm
exclusions             only contradictions that would break the format or genre
```

## Prompting workflow

### 1. Resolve the format

Map the user's request to one format. The format decides the address mode,
which shots matter, and where the performer sits in the frame:

- **Performance** — the artist lip-syncs to camera (direct address); energy and
  mouth-to-vocal sync carry it. Close-ups, medium shots, full-body dance.
- **Narrative** — a short film; the song is the score (indirect address);
  characters never address the camera. Lyric relation can be literal
  (illustration), emotional (amplification), or deliberately detached
  (disjuncture).
- **Conceptual** — no plot; one governing visual rule, image, or metaphor that
  encodes the track, executed with mechanical rigor.
- **Lyric** — the lyrics are the primary visual, but the generated footage
  stays text-free: the clip supplies clean imagery with reserved negative space,
  and the words are set in post (HyperFrames or FFmpeg) on ASR word times.
- **Visualizer** — abstract, audio-reactive imagery with no performer and no
  lyrics; the visuals "image the sound" (waveforms, particles, geometry).
- **Hybrid** — combines performance with narrative or concept. One possible
  arrangement places performance in choruses and narrative in verses; choose
  their allocation from the actual song and intended audience effect.

When the format is unspecified, recommend one from the intended audience effect
and supplied track evidence, with a brief reason. Mark the recommendation
provisional when these inputs are missing. Narrative intimacy, a held conceptual
image, performance energy and a hybrid are alternatives, not genre assignments;
choose only what serves this brief.

### 2. Map the song to a visual plan

Start with the available evidence: listen to the supplied track when accessible,
using a supported media tool; otherwise use the user's section map and label it
as supplied. If neither exists, provide a **provisional treatment**, not invented
BPM, timestamps, lyrics or claims of having heard the song. Ask for audio only
when exact synchronization depends on it; continue untimed creative work.

Record audible changes (density, vocal delivery, texture, silence, accents and
phrase boundaries) separately from proposed visual choices. A genre or section
name does not establish its energy. A chorus may become quieter; a through-composed
track may have no chorus at all.

| Relationship | When it serves the brief | Visual choice |
| --- | --- | --- |
| Escalation | Audible build or requested release | Increase scale, movement or cut density on the supported change |
| Restraint | Intimacy, quiet refrain or sustained tension | Hold framing; let a small performance change carry the section |
| Repetition | Ritual, obsession or a deliberately stable hook | Repeat the composition or action with intentional continuity |
| Counterpoint | Requested emotional tension between image and sound | Hold calm imagery against dense sound, with a clear intended effect |
| Departure | Actual texture change or requested structural contrast | Change one visual rule without inventing a bridge |

Give each section one primary assignment and an end state. Choose its relationship
from the audible evidence and the audience effect; keep repeated hooks unchanged
when repetition is the point. Recipe energy arcs are **creative heuristics**, not
API rules or requirements for every song. Preserve a requested continuous take.

### 3. Set the audio contract

Choose the audio intent from the current request, then verify the selected
tool/model supports its reference roles and parameter combination. State the
chosen mode and any unresolved capability requirement explicitly.

**Native audio (default).** Seedance co-generates audio and video in one pass.
Use the bracket syntax in the Audio slot and inside `{...}` for sung or spoken
lines. Choose exactly one of these patterns — they are mutually exclusive, do
not combine them:

```
(Soft, rhythmic piano music plays in the background)
{the exact sung line}
<the kick hits on each downbeat>
```

```
Keep only the singer's voice and the room ambience.
```

```
No audio at all.
```

Inspect native audio for unwanted music, speech or missing ambience; wording is
direction, not a guarantee. For exact supplied-master delivery, prefer silent
picture when supported and add the authorized master in post. Native ambience
or a separately created bed are alternatives chosen from the brief and actual
review, not rejected because of another production's takes. State whether a bed
is general ambience or needs event-level sync. Re-check final audio and picture
even when a draft passed.

**Supplied-master timing.** When the user asks to follow an existing authorized
song or requests lip-synced vocals, reuse that master. Creating a separate vocal
track needs explicit scope; do not replace an existing master by default. Check
the selected segment's duration and phrase timing against the planned picture.
Use direct `reference_audio` / `@Audio N` when current capability evidence
supports it. A black-sync video carrier is an optional alternative only when
its audio-conditioning role is supported and selected for this request; it is
not required by an older take. For edits, keep the source scene as `@Video 1`,
not a timing carrier. If the needed binding or mixed roles are unverified, return
the treatment with that requirement unresolved.

Example for a verified direct audio binding:

```
@Audio 1 is the exact soundtrack and timing authority. Preserve its music,
vocals, and pauses; do not add dialogue, narration, music, subtitles, or
captions.
Follow the spoken and musical beats in @Audio 1.
Match <performer>'s visible mouth only to <performer>'s voice in @Audio 1.
```

Keep approved sung lines verbatim in `{...}`. When a separate vocal track is
authorized, its prompt and the video prompt use the same words. Missing lyrics
stay unresolved. A timing reference does not guarantee copied audio or exact
lip-sync; preserve the original master and mux it onto reviewed picture for
exact soundtrack fidelity.

**Hybrid audio (reference + native generation).** Use a timing reference with
`generate_audio: true` only when that combination is supported and requested.
Review both the generated soundtrack and visible performance against the
master; do not promise lyric coverage, timing or fidelity. For exact delivery,
retain the authorized master for post.

### 3a. Generated audio is a candidate

Do not infer audio fidelity from the prompt, a reference binding or provider
success. Inspect the returned streams and listen. Keep the supplied master
unchanged for deterministic assembly when exact fidelity matters; replacing the
soundtrack does not by itself repair visible mouth timing.

### 3b. Timestamped lyric timeline (for performance videos with lip-sync)

When complete lyric coverage and timed performance are requested, per-line cues
can make the intended timing explicit. Use verified intervals from the current
audio, or label an untimed draft. This hypothetical format example is not a
measured performance or a guarantee against dropped lyrics:

```
[2-4 seconds] { We fold the daylight into gold, }
[5-7 seconds] { and let the quiet story unfold. }
[7-8 seconds] { The morning starts again. }
```

Add an explicit mandate:

```
The performer performs every line below in full, in order, at its timestamp.
No line may be skipped, shortened, mumbled, or reordered.
```

**When to use this technique:**
- Rap or fast-paced vocal delivery where individual phrases need timing cues
- Any performance video where complete lyric coverage is a hard requirement
- When the audio reference has dense, continuous vocals with no long pauses

**When NOT needed:**
- Ballads with long pauses between lines
- Videos where the visual story matters more than lyric accuracy
- Native audio where the model has space to breathe

**How to get the timestamps (ASR-to-timeline procedure):**

1. Run speech recognition (ASR) on the audio master
2. Extract word-level `start_time_ms` and `end_time_ms` from the result
3. Group words into lyric lines at natural phrase boundaries (commas, periods,
   bar changes)
4. For each line, take the first word's start time and the last word's end
   time
5. Preserve the raw word/line timings as evidence without rounding. Check ASR
   against listening; uncertain words or boundaries remain marked uncertain.
6. If simpler prompt windows help, derive a separate display interval that contains
   the verified phrase (for example floor the start and ceil the end). Do not
   snap offbeat vocals to a grid or replace evidence with rounded timings.
7. Use verified exact intervals or the separately labeled simplified windows as
   `[X-Ys] { line }` slots. Untimed drafts may use ordered lyric cues; do not invent
   measured timings without the audio.

Hypothetical ASR-to-timeline conversion:

```
# ASR returns word-level timestamps:
"we" start=17170ms  "carry" start=17530ms  "the" start=17810ms
"morning" start=18170ms  "home" start=18890ms end=19730ms

# Verified phrase interval: 17.170–19.730s; retain as evidence.
# Separate simplified prompt window:
[17-20 seconds] { we carry the morning home, }
```

### 3c. Post-generation lyric verification (for audio-first / native audio)

The caller verifies actual audio and visible performance after generation:

1. Inspect returned streams; extract audio when present (`ffmpeg -vn`). A
   requested silent output has no generated lyric track to transcribe.
2. Use ASR as a transcript aid and compare it against approved lyrics.
3. Listen to verify the words, delivery and musical continuity. ASR alone
   cannot certify these or lip-sync.
4. Review visible mouth timing against the intended master during every
   designated performance phrase, including the end.
5. If lyrics or timing fail, record the affected phrase and propose a scoped
   repair. Master muxing restores soundtrack fidelity only; a mouth mismatch
   needs timing repair or a reviewed retake within authorization.

This step is especially important for:
- Rap and fast vocal delivery
- Long verses
- Native audio generation

### 3d. Rap and fast vocal delivery

Dense delivery can make missing words or timing drift harder to notice. Review
the actual phrases; do not rank risk or prescribe repairs from genre alone.

Specific guidance for rap:
- Use per-line timing when complete timed coverage is requested and audio evidence
  exists; otherwise supply ordered lyric cues and mark timing unresolved
- Set the "no line may be skipped, shortened, mumbled, or reordered" mandate
- Compare ASR with listening and visual mouth timing to verify coverage
- Split a verse only when its measured duration, performance or a reviewed
  failure calls for separate clips; preserve an approved continuous take
- Include a delivery cue: "jaw opening fully on vowels, lips stay in frame
  throughout"

### 4. Set the beat and cut-density contract

The beat grid gives the timing; emotion and story decide what lands on it.
Timestamps are a **time budget, not frame-accurate** — direct the beats in the
prompt, then snap the final cut to the audio master in post.

Build frame-exact rapid cuts in post from sufficient coverage. In-prompt shot
timing is approximate; do not infer a universal minimum shot length, generation
count or quality ceiling from earlier takes. Choose coverage and clip durations
from the current song, requested continuous takes, campaign placement and
supported limits. Give each shot a readable action, lens intent and motivated
light; camera movement or stillness should serve the intended effect.

In-prompt, name each audio event, the visual event it triggers, and their
relationship (simultaneous, leads, or trails):

```
Each direction change lands on a downbeat.
At 5 seconds the camera crash-zooms on the kick.
The chorus cuts land on the beat; the final pose holds on the last hit.
```

For assembly, place markers at the **actual chosen audible events**: a breath,
snare, silence, phrase ending or downbeat. Whole-bar cuts are an optional regular-grid
technique, not suitable for every track. There is no universal early-frame offset:
review synchronization against the master and adjust for the intended perception.
Counterpoint may deliberately hold across an accent; label that relationship.
Irregular meter, rubato and continuous takes do not require grid-aligned cuts.
Use verified timestamps only where precision is requested; event-relative cues
remain valid. Re-check mouth timing for any lip-synced performance.

### 5. Right-size the scenes

Plan each section at its natural duration within current supported limits,
not a fixed generation block size.
One song section, one primary event, one visible end state per generation.
Chain approved sections through supported frame/reference modes with a shared
reference bundle, or assemble in post. Choose a continuous take when requested
or justified by performance continuity. Verify extension and identity-asset
requirements before proposing that route; retain rights and consent records.

When the user asks for a lyric video, keep the imagery simple, text-free and
legible, with a stated calm zone (for example the lower third or a dim sky)
where type will sit. The words, their pops on the beat and the kinetic timing
are built in post from ASR word times; nothing is lettered by the model.

**Assembly handoff.** Preserve original picture and audio masters. Use derived
clips at the delivery frame rate for approved cuts; record their source spans
and any authorized padding, trim or retiming. Measure video and audio stream
durations, check sync against audible events, and mux the authorized master
over the reviewed cut. Choose compatible intermediates and an assembly method
for the actual streams. Keep the approved colours unless a grade is requested.

### 6. Direct the performer

For lip-sync, give the exact line and a delivery cue, and specify the camera
angle to the mouth:

```
The singer looks into the lens and performs in energetic American English,
jaw opening fully on vowels: {I am still the one you know}
```

For acting, use observable cues, not mood words alone — see
`seedance-acting-console`. For a one-take performance, state
`one continuous unbroken shot, no cuts` and list the spaces and events the
camera passes through in order.

### 7. Compose with the six-part formula

Assemble the treatment into the `seedance-prompt-25` formula:

> **Subject + Action or Event + Scene and Environment + Visual Style + Camera Movement/Cut + Audio**

Chain the Visual Style slot as lighting → lens → grade → look. Keep the genre
lock in the Visual Style slot, the beat contract in the Camera/Cut and Audio
slots, and the sung lines in `{...}`. Do not describe the same action twice.

### 8. End with a style seal

Close with one compact sentence that reinforces the genre lock, the palette,
the motion cadence, the beat contract, and the tone. The seal prevents the look
from drifting across the section chain and during later shots.

## Partner-skill routing

This skill owns the music-video layer: format, song map, beat contract, audio
contract, and genre lock. Other axes belong to their owning preset skills — see
the workspace's canonical axis→skill table (including
`seed-audio-prompt` / `seed-audio-commercial` for an original music or vocal
master, and `seedream-storyboard` / `film-production` for storyboard and
multi-scene production). A storyboard is a planning and review artifact only:
never bind a board or grid as a Seedance reference, because panel numbers and
its sketch look leak into the video. Bind performer, location and prop element
references and write the staging in the prompt. Never let two skills fight:

**Guardrail:** the genre lock supplies the default palette, lighting and camera
vocabulary, and this skill owns when cuts land on the song. Plan what each shot
is (size, angle, move, light source and key side) with `seedance-shot-design`
inside those cuts, usually at kinetic energy; when the user names a specific
axis, compose it with its owning preset skill. Keep exactly one grade per clip,
one dominant lighting direction per shot. One or two camera moves is a planning
heuristic, not a cap on coherent requested choreography; check readability,
endpoints and incompatible simultaneous directions while preserving the beat contract.
Do not stack a second grade or camera treatment on top of a genre recipe.

## Rights and safety

- Use original or explicitly authorized music. Record permissions for the
  current song, recording, lyrics and intended campaign use; do not infer rights
  from a file being supplied or from a previous production. Reuse valid recorded
  authorization within scope. Do not write artist-name or copycat prompts.
- Voice-cloning a real, named artist's voice requires written consent from the
  artist or estate.
- Keep `watermark: false` where the tool supports it; enable the AIGC watermark only when the
  user explicitly requests it.
- Preserve a supplied authorized master. Generate a new original track only
  when requested; generation alone does not establish distribution rights.

## Exclusion rules

- Do not use a blanket "no music" — it contradicts the point of a music video;
  use it only inside a specific ambient scene that must stay silent.
- Do not use exclusions as a substitute for positive audio and beat direction.
- Exclude only likely contradictions: a real artist's face or voice, readable
  logos, an unwanted second vocal, or a second genre's palette leaking in.
- Avoid direct imitation of living artists or directors; describe observable
  craft traits (one governing visual rule, structural bookends, contained
  staging).
- Keep genre recipes stereotype-safe: default to positive, progressive
  performer framing; do not reproduce objectifying legacy tropes.

## Self-check

Before returning the prompt, verify:

1. The format is named and its address mode is respected.
2. The song map assigns one primary event and a visible end state per section.
3. The beat contract names the audio events and their visual relationship.
4. Restraint, repetition, counterpoint or escalation is justified by the supplied
   track/brief; no chorus, bridge or energy change is invented.
5. The audio treatment and any timing-reference binding are explicit and
   supported for this request; black-sync is never forced from an old take.
6. Lip-sync lines appear verbatim in `{...}` and match the audio-first master.
7. Dense vocal coverage uses per-line cues; required timing is verified from audio
   or explicitly unresolved. Raw evidence and simplified prompt windows stay separate.
8. Generated sound and visible mouth timing require listening and playback.
   Exact delivery preserves the authorized master in post; ambience routes
   follow the request and observed output rather than an inherited workaround.
9. Each proposed generation uses a live-supported natural duration, or is an
   explicit continuous one-take.
10. The genre lock is a single recipe, not a mixture.
11. The style seal is compact and does not contradict the format or genre.
12. Frame-exact cuts, lyrics and overlay text are assigned to the edit without
    imposing a universal shot-length floor or fixed generation count.
13. The response contains the prompt, not an unrelated production workflow.
