# Production Stage Contracts

Use these contracts to determine the next safe stage. A later stage may begin
only when its entry evidence exists. Keep unavailable future departments as
explicit gaps rather than fabricating their outputs.

## Stage checkpoint for every stage

The project's stage ledger is `studio/stages.json`, kept only by
`uv run python .agents/scripts/studio_project.py stage <project> {show|start|complete|reopen|skip}`.
It holds the eight stages in fixed order (`brief-development`,
`scene-breakdown`, `canon-elements`, `storyboard-visual-plan`,
`audio-preparation`, `shot-generation`, `assembly-review`, `delivery`) and is
never hand-written. `studio_project.py init` creates an empty Studio project and
`sync` creates it from the shot manifests: an outline frame for each planned shot and a built frame for
each take, without deleting prior frames, variants or decisions. Exact
generation prompts stay in their immutable snapshot files, referenced from the
manifests.

Read independent `review_mode` and `approval_mode` from `project.md` at
start/resume and before each operation or stage decision. Missing means default
and approve_for_me for new actions; invalid values fail. Default uses minimal
preflight and final sanity, draft-first video, and no mandatory
prompt-review craft reports or strict checklist loading. The detailed QA below
applies in strict mode or when requested; retain actual compliance, rights,
reference locks, capabilities, hashes and registry safety in both.
Record the effective modes,
decision actor, reason, review outcome, current selection or stage lock, and
unresolved gaps in the relevant manifest. `status` checks takes and Studio
assets only; it does not read review, decision or scene files, so re-run
mode-appropriate preflight or reopen the stage when those files change.

The expensive HyperFrames check runs at `delivery` in both review modes;
strict also runs it at `shot-generation` and `assembly-review`. Default skips
only that intermediate check, recording `check_ran: false` and `check_ok: false`.
Status, placed takes, provenance, selections, locks and freshness still gate
stage completion.

Every stage exit additionally requires:

1. `studio_project.py stage <project> complete <stage-id>` passes. Its
   per-stage requirements (valid `project.md`, clean `status`, placed takes and
   a mode-appropriate passing `check`, no pending selection, `picture`/`audio`/`final_master`
   locks, a current delivery-level `render`) are the stage-exit table in the
   production policy. Only `storyboard-visual-plan` and `audio-preparation` may
   be skipped with `--reason`;
2. the stage's inputs, outputs, prompts, bindings, review evidence and
   mode-authorized decisions or pending recommendations are in the manifests;
3. the project has been opened in Studio for visual review after the latest
   material edit;
4. `handoff.md` records the completed stage, current selections, operations
   still in flight with their registry IDs, open defects, and the next action.

`handoff.md` is plain Markdown for resuming work, not an approval record. Keep
it short and overwrite it at each exit rather than appending history.

A pre-Studio canvas project with `showcase.json` keeps its canvas checkpoint instead
(`generate_showcase.py <project> --check --stage <stage-id>`). The
stage-specific required outputs below describe what the matching stage must
expose in the manifests; Studio frames exist for shot video takes only. A CLI/OS-player review does
not replace this checkpoint.

## 1. Brief and development

Entry: user intent or an existing `project.md`.

Required output: `review_mode`, `approval_mode`, audience, format, runtime, aspect ratio,
delivery resolution, story objective, tone, creative constraints, known rights
constraints and unresolved questions recorded in `project.md`.
Confirmed directorial defaults (structure, energy level, camera and light
stance, lens, grade, pacing, acting, staging, medium, audio) from
`brief-intake` persisted as a `locked` block in `project.md` frontmatter. The
brief also records:

- the **creative premise, attention and payoff** for new vague work: what the
  viewer notices or feels, what sustains attention, and why the ending matters.
  Offer compact alternatives when materially different premises remain open;
  preserve a settled idea for scoped work instead of expanding its workflow;
- **sound and editorial intent before generation**: what is heard before seen,
  what the edit reveals or withholds, and the role of silence or a sound accent.
  Final assets are not required early; timing is provisional until measured;
- **artistic acceptance** tied to the brief, using a small relevant set of
  observable criteria rather than generic "cinematic" polish or activity counts;
- the **audio route**: native dialogue or explicitly requested native soundscape,
  picture only with score, ambience and
  SFX built in post, opt-in separate lip-sync audio, or silent;
- the **look intent**: ungraded original model colours unless a grade or a
  capture-format look is requested, in which case it is a post treatment;
- the **on-screen copy** (titles, captions, CTA, end card) that post will add,
  and any label the user or platform requires;
- for ads and TVCs, the **creative argument**: hook, viewer motivation,
  development, payoff and product connection; internal shot timing separately
  from authorized provider source count, and any intended memorable moment;
- for ads and TVCs, the **coverage intent**: sequence count and length fitted
  to approved beats and generation scope, including purposeful holds. Standout images,
  timing contrast and turns are optional, not per-sequence requirements.

The brief is the `brief-development` stage source; `stage complete` checks that
`project.md` is a valid record.

Exit: the production objective, constraints, and directorial defaults are clear
enough to break down. When the brief cites brand ads or other footage for
visual or motion inspiration, record the reference URL or local path and treat
local media acquisition and native video/image inspection as unresolved until
decodable media and a capable reviewer are available. Prefer native/local
inspection; use available MCP understanding tools when needed, under privacy
and explicit offline constraints. No upload or cloud call is required when native
inspection suffices. Scripts and
article text alone do not satisfy that gap.

## 2. Scene and production breakdown

New or materially revised character performance needs `acting-direction`
before coverage and a source-bound `## Performance plan` in the scene file.
Carry beat IDs, intentions, listening tasks, registration/response timing and
critical acceptance into shot notes, then `seedance-acting-console` encoding.
The [performance contract](../../../contracts/performance-direction.md) owns
applicability: source-preserving edits inherit performance; static assets do
not acquire acting requirements. Quiet holds and intentional stillness override
the optional cinematic cadence below without adding paid generations.

Entry: an accepted brief and available story or script material. Draft scene
and shot breakdown may precede canonical asset generation; it identifies which
assets are required and does not make a prompt ready for production submission.
If the brief borrows grammar from cited reference footage, that media must
already be locally decodable and inspected through native video/image tools
or a capable permitted understanding tool,
with timestamped frames and local timing measurements, before treating
visual/motion claims as breakdown evidence. Missing perception stays unresolved;
reference audio needs native/local audio perception, an available
audio-understanding tool, or human listening. MCP or local ASR/separation may
assist; local-only tools are not required.

Required output: scene list, cast, locations, props, dialogue, sound needs,
continuity states, delivery assumptions, and scene-level acceptance criteria.
For every narrative, ad, micro-drama, music-video or showcase scene it also
requires a shot plan from `seedance-shot-design` in the scene file's
`## Shot plan` section: per shot, duration, size, angle, camera move, lens
intent and a named light source with key side, the energy level, and where each
confirmed project axis appears. Ads and TVCs derive internal shots from their
creative argument and source count. One generation may contain native cuts;
an explicit continuous take may not. Coverage follows approved intent,
readability and generation scope; short sequences are optional, with no required
cadence, variety, turn, hold or standout count. About 0.8 s per shot and about
7 shots per clip are provisional generation heuristics, not provider limits
or guaranteed merge/drop thresholds. Preserve requested rhythm and source
timing without automatic retiming or shot removal. Offer assembly for precise
cuts or omitted action within generation authorization; return genuine
feasibility conflicts rather than changing locks. A long action with
people that would need extension is planned as short single passes held by a
blocking map unless `asset://` Virtual Portrait identities are available. The plan is `draft` until the scene's locations
are approved in Stage 3 and is revalidated before Stage 6. A scene that is exempt
(user lock, static-by-design format, an explicit per-shot camera plan from another skill, plate
for cutdown, source-preserving edit, extension continuation, or no video shot)
records its `static_reason` instead. The `scene-breakdown` stage lists
every scene/shot manifest (each shot becomes an outline frame in the Studio
storyboard), its shot plan section, and its required production-input inventory.

Exit: every planned scene has observable action, a draft shot plan or a recorded
exemption, and an inventory of required production inputs, with missing
approvals recorded as unresolved.

## 3. Canon and elements

Entry: breakdown identifies recurring characters, locations, or props.

Required output: one flat `elements/<element-id>/` folder per reusable element,
manifest, reference files, hashes, variants, and lifecycle states. Generated
sheets carry prompt snapshots; acquired brand/product/logo assets carry
provenance and `generation: none`; deterministic screens/cards/posters carry an
editable HTML entrypoint with local CSS/SVG dependencies, a render record, and
`generation: deterministic_html`
instead of a model prompt or provider task. **Before locking
the element list**, walk every beat of every scene/shot against the tracked
element-identification contract — verify that visible characters, settings,
props, screen/UI surfaces, brand/title cards, and recurring audio have been
identified and assigned the appropriate treatment. Recurring/identity-critical on-camera characters
and recurring/geography-critical spaces need canonical references; incidental
people/settings may use descriptors or scene direction. Screen-only callers use
a locked UI with text-directed movement/dialogue, not character sheets as static
screen content. Apply the prop threshold rather than turning every visible object
into a generation requirement. For authorized real brands, logos, and labeled
products, prefer official or authorized web/user downloads over Seedream; generate
only when no usable real asset exists or a stylized substitute is requested.
Use a deterministic HTML entrypoint with local CSS/SVG dependencies for exact
typography, screen/UI, product lineup, price/CTA, and poster geometry. Use
Seedream for synthesized image content; a
hybrid binds the selected image as a hashed input and finishes exact copy/layout
deterministically.
Generic containers, jars, cases, labels and generated screens tend to grow
invented lettering: give a story prop a reference sheet, and describe recurring
non-sheet props positively as plain ("plain white ceramic jug, smooth solid
surface") or leave them out.
Record missing required references before dependent tasks are submitted.
The `canon-elements` manifests record every variant (acquired, generated, or
deterministically rendered), its prompt or provenance/render record,
recommendation/selection state and downstream role. Studio's Assets panel shows
only the locked (selected, approved) elements, copied as
`LOCKED_<element>_<vNN>.<ext>`; candidates and rejected samples stay in
`elements/`. `studio_project.py lock-element` records the decision and does this
copy; `sync-elements` repairs it and rewrites the static candidates page
(`review/elements.html`).

Exit: every required canonical element has an approved selected variant, or the
dependent scene is explicitly marked unresolved. The element list has been
cross-checked against the Element identification checklist and no gaps remain.
An approved selected variant may be a downloaded packshot/logo, generated
sheet, or deterministic graphic — all satisfy exit when the file hash, passing
review, and mode-authorized decision are recorded. An agent decision cannot
replace an explicit user lock.

## 4. Storyboard and visual plan

Entry: scene objective, geography, continuity state, and approved relevant canon
exist before dependent panel generation. A text-only visual plan may be drafted
earlier and stays draft until its input requirements are satisfied.

Required output: beat/panel plan that follows the scene's shot plan, bound
element references, prompts, generated panels or prompt package, continuity
review, and provenance. Boards are planning and review artifacts: their staging
is translated into shot prompt text and they are never bound as Seedance
references. Record these together in the `storyboard-visual-plan` manifests;
Studio shows shot takes only.

Exit: required panels have a mode-authorized approval and all source element
hashes remain current, or the stage is skipped because the shot plan already
carries the staging.

## 5. Audio preparation (optional — requested lip-sync audio or beat-led music)

Entry: exact dialogue and planned scene duration exist and the user has
explicitly requested lip-synced dialogue audio, or a music track exists that the
cut must follow.

Required output: exact audio prompt, local audio file, duration, transcript or
dialogue timing, media inspection, SHA-256, and manifest linkage.
Expose the audio player, prompt and timing evidence in `audio-preparation`.

Exit: audio duration fits the planned video and dialogue mappings are verified.

When the user has not requested lip-synced audio, skip this stage and proceed
directly to shot generation. Seedance's native audio handles dialogue by
default. A music track that the cut must follow (music video, beat-led spot)
may be prepared here so shot durations can be planned to it. Score and ambience
for a picture-only project are otherwise built after picture lock, at
assembly, to the cut's measured length.

Skipping audio preparation does not skip early sound intent. Use the existing
brief/scene notes to reserve meaningful sound events and silence; no extra
generation or separate lip-sync track is implied. For sound-led work, use the
supplied cue structure to guide picture and refine final cues against the
measured edit rather than discovering the entire sound idea after picture lock.

## 6. Shot generation

Applicable performance prompts require `acting.plan_bound` with real source,
plan and request evidence in both review modes. Default checks this scoped rule
without loading blanket craft checklists. Actual-take acceptance includes
registration, listening, response, exact delivery and product/prop continuity.
Missing critical performance blocks selection or promotion; no passing take
means a bounded revision within generation scope or an unresolved stage.

Entry: shot objective, the scene's revalidated shot plan (or recorded exemption), selected
video mode, approved inputs, reference roles, prompt snapshot target, duration,
and any requested audio (if Stage 5 was completed) exist. In strict mode the
`prompt-review` gate has passed for every prompt being submitted.
Default requires only minimal preflight unless explicit rules demand a report.
Review inline; use a sub-agent only
when the user explicitly requests sub-agent prompt review for the project or
specific generation. The ordered `references:` array is verified 1:1
against `shot.md` (same files, same order, same `@Image N` / `@Video N` /
`@Audio N` bindings); the request's `generate_audio` matches the brief's audio
route; no storyboard image is bound; and every new Seedance 2.5 generation uses
explicit `resolution: "480p"` and boolean `draft: true` in both review modes.
Resolve schema or transport mismatches without dropping the flag. Other models
without native Draft use a plain 480p test.
Initialize Studio at the delivery target, not the draft resolution. Seedance
2.5 has no skip-draft exception; keep approval authority separate.

Required output: task registry entry, local media, exact prompt snapshot,
provider metadata, actual media properties, cost fields, SHA-256, semantic QA
including a comparison of the take against its shot plan, frame samples with
top-left corner crops for leaked text, a speech-to-text diff for every locked
line, and `review` status. When using drafts, resolution is raised only after the current pass is
approved (final-candidate gate); a native Draft is promoted by its
`draft_task_id` without changing its inputs. For multi-shot productions, review the draft
assembly and record picture/audio decisions before generating final takes.
Each final request is separately registered and reviewed against its complete
request hash; each final output needs fresh playback, audio and creative QA and
a mode-authorized selection before it replaces the draft in Studio. A plain
480p output requested without `draft: true` cannot be promoted.
The `shot-generation` stage records every take, exact prompt, ordered element
bindings, metadata, inspection result and selection state. When a style/grammar
reference pin (or other watchable reference video) exists, that pin and each
generated take must be playable for review: each take is viewable in its Studio
frame, and the pin is recorded in the manifest and played from its file. A pre-Studio canvas
project instead lists them in one `kind: "takes"` group using
`groups[].takes[].media` objects (`{ "type": "video", "src": "…" }`); follow
`showcase-html` production-canvas and schema.

Exit: a passing take has a hash-bound, mode-authorized selection. In
`ask_for_approval`, the recommendation remains pending until the user chooses.
If no take passes, make a bounded correction within the requested scope or leave the
shot blocked.

## 7. Assembly and review

Recheck accepted performance beats in the actual edit: trimming must not remove
registration, the listener's response, exact copy or the intended held duration.
Inspect playback and listen; transcript correctness alone is insufficient.

Apply the brief's artistic acceptance to actual full-speed playback with sound
when in scope. Record timestamps and beat IDs in existing review evidence for
what captures attention, what the edit reveals or withholds, and whether the
intended payoff, sustained observation or unresolved ending lands. Assess actor
intensity, camera energy and edit rhythm separately; neither quiet nor energetic
work passes merely for matching a movement count. Check sound hierarchy,
anticipation, silence and release against the intended response, then align
final cues to measured picture. Unavailable playback/listening is unresolved,
not a pass. Critical artistic failures need a bounded repair within locks and
generation scope or a blocked selection, not promotion of the least-bad take.
Default mode keeps this evidence concise; strict retains detailed review.
No new runtime, rule ID, report format or approval gate is introduced.

Entry: approved takes and any requested audio assets exist.

Required output: ordered edit, review render, transition and continuity review,
audio presence check, technical decode QA, artistic playback evidence and
outstanding notes. Technical assembly uses conform, trim, crop, overlays, end card and mix with no grade, from
exact-length intermediates encoded once; post beds for picture-only projects
are built here to the measured cut. Audio defects are fixed word by word, and
re-voicing keeps the source soundtrack (see
[production defaults](production-defaults.md)). The `assembly-review` stage
keeps its approved inputs and comparison renders together.

Exit: picture and audio have separate mode-authorized locks bound to the exact
artifact and passing review hashes. Audio lock is required when audio is in
scope. In `ask_for_approval`, wait for explicit user locks. Full editorial,
color, and sound-post department contracts are future work tracked in the
lifecycle specification.

## 8. Delivery

Entry: approved picture and audio plus a known delivery target.

Required output: inspected master, review proxy if needed, caption or localization
status, delivery metadata, hashes, and archive pointers. On-screen text comes
only from post overlays; add no AI or fictional label unless the user, platform
or brief requires one.
The `delivery` stage exposes those files and final approval evidence.

Exit: inspect the actual local master, then record a mode-authorized final
master lock bound to its file and review hashes. In `ask_for_approval`, wait for
the user's explicit acceptance. Publishing, sending, or external delivery needs
separate authorization in either mode.
Recheck the brief's artistic criteria in this final master, including sound,
exact copy and accepted performance after trims and overlays; prior draft
acceptance or successful render status does not establish final quality.
