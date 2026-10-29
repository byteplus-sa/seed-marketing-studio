---
name: film-production
description: Orchestrate an AI-assisted film, commercial, music video, or narrative production across brief, development, canon, storyboard, audio, shot generation, review, assembly, and delivery while maintaining one HyperFrames Studio project through every stage. Use when a request spans multiple scenes or modalities, asks to create or continue a film project, requires coordination between deterministic HTML-entrypoint graphics, Seedream, Seed Audio, Seedance, HyperFrames, or FFmpeg, or needs the next safe production step rather than a single prompt. Do not use for an isolated image, audio, video, or editing request that one specialist skill can complete independently.
---

# Film Production

Manage one coherent production run while keeping specialist skills modular. Read
the project's `project.md` and existing manifests first, inspect the existing
project before creating anything, and advance only as far as the available
evidence and mode-authorized decisions permit.

The workspace `AGENTS.md` and the
[production policy](../../contracts/production-policy.md) own approval modes,
Studio commands, stage gates, prompt review, registration and submission
recovery. This skill owns the sequencing: which stage comes next, which
specialist runs it, and which production defaults make the result better.

## Core operating model

- Act as the single manager communicating with the user.
- Treat project files and manifests as production memory; do not rely on chat
  history alone.
- Keep the project's HyperFrames Studio project (`projects/<project>/studio/`)
  in step with the manifests through `studio_project.py` for every stage
  review and handoff. A project with a `showcase.json` is a pre-Studio canvas
  project and keeps its canvas checkpoint instead.
- Delegate modality work to the narrowest applicable specialist skill. In
  strict mode run prompt review inline unless the user asks for a sub-agent.
  Default mode uses minimal preflight and final sanity without loading strict
  checklists; explicit required rules still need genuine evidence.
- Prefer a deterministic workflow when the next action is known. Use agentic
  judgment for creative choices, contradiction resolution, and review.
- Provider success is `review`, never approval. A poll timeout resumes the
  recorded task; it never triggers a second submission.
- Never silently replace user writing, approved canon, selected variants, or
  unrelated project state.

## Start or resume a run

1. Resolve the project directory. Search before creating a project, scene,
   element, shot, or same-purpose artifact.
2. Read `project.md`, `handoff.md` when present, `task_ids.json`,
   `studio/stages.json` (`showcase.json` for a pre-Studio canvas project),
   relevant element, scene and shot manifests, prompt snapshots, and the latest
   review decisions. Manifests and the registry win over `handoff.md`. A new
   Studio project starts with `review_mode: default` and
   `approval_mode: approve_for_me` in `project.md`,
   `studio_project.py init <project>`, then
   `studio_project.py stage <project> start brief-development`.
3. **Never hand-write Studio state** (`stages.json`, `provenance.json`,
   storyboard frames, compositions, render records) or a `showcase.json`. A
   scaffold delegated to a sub-agent names the exact command and prohibits
   hand-authoring.
4. Determine the current stage from recorded artifacts and lifecycle states,
   not from filenames.
5. Identify contradictions, missing inputs, stale dependencies, pending provider
   tasks, and decision gates. Read both independent modes; missing fields use
   default/approve_for_me for new actions and invalid values fail. Recheck
   before each operation or decision.
6. State the current stage, the next safe objective, required specialist
   skills, and any user decision needed before spending credits.

Read [stage contracts](references/stage-contracts.md) for entry evidence,
required outputs and exit conditions, and
[handoff contracts](references/handoff-contracts.md) before moving an artifact
between modalities.

## Route specialist work

<!-- markdownlint-disable MD013 -->

| Production need | Primary skill |
| --- | --- |
| Brief intake, directorial defaults, audio route, look intent | `brief-intake` |
| Brand-ad / reference-video inspiration | `template-factory` for native-first reverse-engineering or its quick structure-clone mode; native/local inspection with permitted MCP fallbacks for lighter analysis. Preserve product facts, campaign pins, rights and disclosure decisions |
| Character identity asset | `seedream-character-sheet` |
| Character sheet cleanup | `seedream-character-sheet-cleanup` |
| Authorized face or voice asset (`asset://` Virtual Portrait) | `seedance-virtual-portrait` |
| Location identity asset | `seedream-location-asset` |
| Prop or product identity asset (acquire an authorized real brand or product first) | `seedream-prop-asset` |
| Exact static typography, poster, title/end card, UI, product grid, price/CTA treatment, or transparent overlay | `html-graphic-render` |
| General image generation or edit | `seedream-prompt` or `seedream-edit` |
| Storyboard for planning and review | `seedream-storyboard` |
| Scene geography and crowd blocking | `blocking-map` |
| Scene writing under the selected framework | `scene-craft` |
| Source-bound performance intent before coverage | `acting-direction` |
| Seedance encoding of supplied performance beats | `seedance-acting-console` |
| Score, ambience, SFX or dialogue audio | `seed-audio-prompt` |
| Narrative audio commercial | `seed-audio-commercial` |
| Per-shot coverage, camera, lens intent and light for a scene | `seedance-shot-design` |
| Seedance 2.5 video prompt | `seedance-prompt-25` |
| Non-English or multilingual video dialogue | `seedance-prompt-25-dialogue` with `seedance-prompt-25` |
| Seedance 2.0 video prompt | `seedance-prompt-20` |
| Footage-driven VFX prompt | `seedance-vfx-prompt` |
| End-to-end Seedance 2.0 VFX shot | `seedance-vfx-pipeline` |
| Model submission, polling, artifact access, speech-to-text | `ark-mcp` |
| Animated exact graphics or timed overlays | appropriate HyperFrames skill |
| Assembly, media transforms, captions, word-scoped audio patches | appropriate HyperFrames or FFmpeg skill; the result is placed in Studio and rendered with `studio_project.py render` |
| Studio project, stage gates, review and selection | `studio_project.py` with the `hyperframes-studio` conventions; pre-Studio canvas projects use `showcase-html` |

<!-- markdownlint-enable MD013 -->

If the needed lifecycle role does not exist, keep the work at its current stage
and record the gap. Do not disguise a generic prompt as a completed production
department workflow.

## Production defaults

Read [production defaults](references/production-defaults.md) before the first
paid video submission and again at assembly. In short:

1. **Mode-aware sampling, draft-first video.** Default produces one image;
   strict uses three. Both start every new Seedance 2.5 generation with explicit
   `resolution: "480p"` and boolean `draft: true`; other models without native
   Draft use a plain 480p test. Explicit image counts win; new 2.5 generations
   have no skip-draft exception. Resolve schema or transport conflicts
   without dropping the native flag. Promotion requires unchanged inputs.
2. **Audio route from the brief.** Native dialogue keeps native audio.
   Ambience-only, score-driven and wordless pieces generate picture with
   `generate_audio: false` and build the bed in post, because a "no music" line
   does not reliably hold. Explicit native soundscape or single-generation
   sound-led requests override that preference without adding audio tasks.
3. **Idea-led coverage for ads and TVCs.** Develop the hook, viewer motivation,
   progression, payoff and product connection before shot detail. Record
   internal shots separately from source generations; preserve an explicit
   one-generation request while allowing native cuts unless a continuous take
   is locked. Each shot contributes new information, feeling or sensory detail.
   Choose count and duration from readable action, listening and the approved
   generation scope. Each shot carries lens
   intent, a motivated move or hold and named light. Short sequences, variety,
   turns and standout images are optional, not cadence or hold quotas.
4. **Storyboards plan; they are never bound** as Seedance references. Bind
   element references and write staging in the prompt.
5. **People in video inputs** (extension, video-to-video) need `asset://`
   Virtual Portrait identities; otherwise use short single passes and a
   blocking map.
6. **Text-free footage.** Overlays, end cards and any required labels are added
   in post; no AI or fictional labels by default.
7. **Ungraded assembly** in original colours, exact-length intermediates, one
   final encode.
8. **Narrow fixes.** Word-scoped audio patches, re-voicing that keeps the
   source soundtrack, and speech-to-text as the word authority.

## Run one stage at a time

For the active stage:

1. Record the stage objective and observable acceptance criteria.
2. Confirm every input path, selected variant, lifecycle state, and SHA-256.
3. Invoke only the specialists needed for that stage.
4. Persist exact prompts beside generated media and update the owning manifest.
   Deterministic static graphics persist their editable HTML entrypoint, local
   dependencies, input/font hashes, render record and PNG instead.
5. Inspect every actual output: images visibly, video temporally, audio by
   listening plus speech-to-text where words matter. Reject hard-gate failures
   and rank passing candidates against the brief's recorded criteria.
6. Record the decision under the project's approval mode: an agent decision in
   `approve_for_me`, or a recommendation and the user's chat answer in
   `ask_for_approval`. Choose takes with `studio_project.py candidates`, a swap
   in Studio (or `place`), then `record-selection`.
7. Run `studio_project.py sync` after every material change and open the
   project in Studio for visual review of shot takes.
8. Exit with `studio_project.py stage <project> complete <stage-id>`; skip
   out-of-scope `storyboard-visual-plan` or `audio-preparation` with
   `stage <project> skip <stage-id> --reason TEXT`; reopen a completed stage
   when an upstream input changes. Update `handoff.md` at every exit.
9. Advance only when the stage exit contract is satisfied.

At the brief/development stage, run `brief-intake` before writing the brief's
required output. It proposes directing defaults derived from the idea, and the
brief must also record the audio route, the look intent (ungraded original
colours unless a look is requested), the on-screen copy that will be added in
post, and, for ads and TVCs, coverage intent. Resolve a new vague brief's compact
premise, attention and payoff; offer alternatives only for genuinely open ideas
or requested exploration. Scoped specialist prompts do not gain a mandatory
development workflow. Plan sound and editorial intent before generation,
without requiring final audio assets early. Persist the
mode-authorized confirmed set as a `locked` block in `project.md`.
For a batch, compare the concepts before prompt expansion: hook, setting,
performer intention, product role, development and sound should differ where
the formats demand it. Preserve intentional campaign unity; do not accept
the same object-handling exercise under different format names.
Keep this brief-level reasoning compact in default mode, not a new report or
approval gate. Never improve apparent creativity by inventing product claims.

At scene breakdown, run `acting-direction` before shot design for new or
materially revised character performance. Store `## Performance plan` in the
scene file, then use `seedance-acting-console` to encode the relevant beats.
Follow the [performance contract](../../contracts/performance-direction.md):
require `acting.plan_bound` when applicable in both review modes, using focused
evidence in default. Preserve exact ad copy, CTA, supported claims, product
identity, campaign pins, generation scope, source-preserving edits and localization gates.
Inspect registration, listening, response and exact delivery in actual takes
and again in the final edit. Static assets need no acting plan; sustained
attention and intentional stillness need no new emotional turn.

At the scene breakdown stage, run `seedance-shot-design` for every narrative,
ad, micro-drama, music-video or showcase scene before any shot prompt is
written, and store the plan in the scene file's `## Shot plan` section. The
plan stays `draft` until the scene's locations are approved, then is
revalidated before shot generation. An exempt scene records its
`static_reason`. The plan carries the project's confirmed camera, lens,
lighting, pacing and energy axes into the shot lines or records a scene
override. At shot generation, inspect each take against its plan: a missing
planned cut, move or light change is a defect only against the approved intent,
not a motion quota. Quiet holds and sustained performance can carry a sequence.
The cinematic cadence above is an optional planning heuristic; preserve approved
coverage, intentional stillness and the authorized generation count.

## Approval and cost reporting

Approval modes, decision evidence and lock rules are defined once in the
production policy. The orchestration-specific rules are:

- Do not require a run budget, known price or spending approval before
  in-scope generation. Promote only selected drafts.
- A tie between passing candidates uses stable operation ID and
  variation-index order. Do not promote the least-bad output merely to advance.
- Rights, real-person likeness or voice consent, external delivery and
  publishing need their own scope in
  either mode. An approval to generate never approves its result.
- Record estimated and confirmed cost separately; report unknown when
  unavailable without blocking generation. Legacy budget fields are inert.
- In default mode, keep candidate/final sanity evidence short and factual when
  the selection or stage-lock writer needs it. Auto-approve passing in-scope
  work as the agent under `approve_for_me`; never invent a user quote, rights
  grant, disclosure decision or native human sign-off.

## Handle revisions

Write every revision as:

- **Locked decisions:** properties that must remain unchanged;
- **Requested delta:** the single intended change where practical;
- **Acceptance criteria:** observable evidence of success;
- **Known rejections:** previously rejected outcomes that must not return;
- **Invalidation scope:** dependent artifacts that return to `review` if inputs
  change.

Prefer a bounded edit over full regeneration after composition or performance is
approved: a post repair, a word-scoped audio patch, or one corrected shot.
Preserve rejected history and never overwrite source media.

## Finish the run

Report the stage reached, artifacts created or changed, Studio project path and
stage-exit evidence, review status, provider tasks still running, costs when
known, unresolved risks, and the next production decision. A production run is
complete only when its active stage exit contract is satisfied; the local film
is complete only after its inspected master has a mode-authorized final lock.
External delivery or publishing remains a separate action.

Submission recovery (register before submitting, record the task ID at once,
reconcile `submission_unknown`, never resubmit through a second transport)
follows `AGENTS.md` and the production policy.
