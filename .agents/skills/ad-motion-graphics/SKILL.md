---
name: ad-motion-graphics
description: Orchestrator for explainer and motion-graphics ads using agent-authored HyperFrames with optional Seedance plates or hypermotion inserts. Use for ad plan/design/code/preview/check/render, not generic animation or isolated Seedance wording.
---

# Ad Motion Graphics

Own the advertising explanation and its coordinated delivery, not a new
animation engine. Plan, design, code, preview, check and render an exact,
editable HyperFrames composition when execution is requested. A fully
deterministic film is a first-class result; Seedance is optional.

## Scope and stop points

- For a prompt-only, concept or specification request, return the design
  specification and requested prompts only. Do not scaffold, acquire assets,
  install anything, generate media, open a server or render.
- For an execution request, act only through its authorized endpoint. A
  request to preview does not authorize publishing or paid generation.
- For a narrow revision, preserve the existing project, assets, timing and
  locks outside the named change. Do not restart intake.
- Generic HyperFrames authoring stays with its installed capabilities;
  isolated Seedance motion-design wording stays with `seedance-motion-design`.
  This orchestrator adds the ad proposition, evidence and layer handoff.
- A reference-edit clone, music-led film, caption-only edit or narrative
  production is not automatically an explainer because it contains text.
  Route by the requested deliverable, not a tool mentioned in the brief.

## Inputs

Read the current brief and supplied material before asking. Resolve:

| Input | Needed decision |
| --- | --- |
| Audience, message, next action | What the viewer should understand and do |
| Product facts and source material | What may be demonstrated or claimed |
| Brand kit, copy, logo and fonts | Exact identity, wording and usage rights |
| UI recordings/screens and version | Which real states and actions exist |
| Data with sources, units and dates | Which chart relationships are truthful |
| Duration, ratio, fps, placement | Time budget, canvas and verified safe zone |
| Existing project and locks | What must remain unchanged |
| Audio and optional generation scope | Native/post ownership, authorization and count |
| Requested endpoint and project modes | Spec, build, preview or local render |

Ask about consequential gaps. Without sources, produce a clearly provisional
claim-free explanation; do not invent UI, metrics, permissions or references.
Do not label unverified copy production-ready. No market is inferred.

## Loading and authority

Read [the worked example](references/worked-example.md) for a full handoff.
Read [evaluation cases](references/evaluation-cases.md) when changing or testing
this skill. Examples are fictional, not reusable campaign facts.

Workspace adapters, resolved from the repository root:

- Read `.agents/contracts/production-policy.md` on execution/resume and
  `.agents/contracts/ad-compliance.md` for campaign facts and delivery.
- Read the installed `hyperframes` entrypoint for routing. Before code, read
  installed `hyperframes-core` and its matching composition, sub-composition
  and determinism references; use `hyperframes-studio` for timeline layout.
- Read installed `hyperframes-creative` for design and `hyperframes-animation`
  for the selected runtime and motion rules. Add keyframe/audio domains only
  when those operations are needed.
- Read installed `hyperframes-registry` before named-effect discovery and
  wiring; read `hyperframes-cli` and its matching command references before
  preview, snapshots or validation.
- These are declared workspace adapters, not files copied into this bundle.
  If the owning workflow is absent, report the missing dependency and request
  reviewed vendoring; do not reconstruct it or install another release.

The production policy overrides vendored install, upgrade, usage, feedback,
publish and unconditional approval instructions. Read `review_mode` and
`approval_mode` independently; invalid values block execution.
Prompt-only and fully deterministic work require no Seedance generation.
Every new Seedance 2.5 generation requires `resolution: "480p"` and boolean
`draft: true` in both review modes. Promote only selected native Drafts.
Surface source-count conflicts before generation; never bypass drafts or
silently expand scope. Review depth follows the selected review mode.
Neither mode supplies rights, extra generation scope or a paid-ad disclosure decision.

## 1. Plan the explanation

Connect the hook, viewer motivation, development, payoff and product role
before selecting effects. Motion should change a relationship the viewer can
understand: grouping, routing, comparison, transformation or a resolved choice.
An attractive shape moving between two positions is not automatically an
explanation. Use contrast and anticipation while preserving reading time.
Exact-copy and evidence records belong in the design handoff, not a Seedance
plate prompt. Retain all essential safety, identity and scope constraints.

Write the proposition as an observable change in understanding, not an effect:
viewer problem -> demonstrated mechanism -> supported outcome -> next action.
Offer distinct treatments only when direction is open. Keep a settled brief.

Choose screen-led, diagram-led, data-led, typography-led or hybrid treatment.
For an agentic process, show actual inputs, tool boundaries, review/approval
steps and outputs supported by documentation or recordings. Distinguish an
illustrative conceptual sequence from a recording of a working product.
Do not imply autonomous execution, instantaneous latency or success rates
without evidence. Mark editorial time compression when it would mislead.

Create a beat table with start/end, viewer question, focal element, action,
settled end state, evidence ID and layer owner. Assign motion a job such as
directing attention, explaining a relationship or making the next action clear.
Make space for reading and recognition; fast movement is not comprehension.

## 2. Design and classify every layer

| Layer | Owner and evidence |
| --- | --- |
| Copy, CTA, logo, exact UI, charts and numbers | Deterministic HTML with local CSS/SVG and approved assets |
| Actual product operation | Authorized capture or faithful source-backed reconstruction |
| Abstract process or relationship | Authored vectors; label a conceptual diagram where needed |
| Photographic atmosphere | Acquired media or optional text-free Seedance plate |
| Hypermotion product insert | Optional generated coverage with approved product identity |
| Sound and captions | Explicit native/post ownership and measured timing when required |

Keep product labels legible and faithful throughout, not just on the end card.
If generation cannot preserve mandatory identity, propose acquired product
imagery or compositing; an accurate final logo does not repair earlier drift.
Keep generation prompts free of overlay copy and exact interface requirements.

Charts retain source units, denominators, period, baseline and uncertainty.
No invented counters, reviews or before/after outcomes. Preserve required
qualifiers. Apply brand copy rules and the dated placement contract; Studio
preview safe boxes are not evidence of a platform's safe zone.

Lock the visual design before motion: typography, hierarchy, alignment,
palette, spacing and reading holds. Plan each move's start/end, duration,
easing, overlap and reason. Hypermotion belongs in a bounded insert; return
to a stable explanation frame before presenting essential copy.

## 3. Discover and prepare

For execution, reuse the one existing Studio project or initialize it through
the pinned wrapper. A pre-Studio `showcase.json` project is not migrated here.
Keep source evidence, design and production state in the owning project.

Search registry effects by intent before hand-authoring a named effect:

```bash
uv run python .agents/scripts/studio_project.py hf "$PROJECT" catalog --query "reveal a headline one line at a time" --json
```

Inspect results and existing installed files; do not invent item names.
Reuse a compatible local item. Record misses locally. A project-local `add`
requires an approved dependency choice and inspection of affected files;
never auto-install global skills or enable download-backed search silently.
In spec-only mode record the discovery requirement without creating a project.

Use approved local assets and fonts, with source and content hashes. Freeze
UI/data evidence before code. Do not pass untrusted HTML, scripts or arbitrary
URLs directly into a composition; validate paths and sanitize source material.

## 4. Code and integrate

Author deterministic HyperFrames, not prompts asking a model to draw a UI.
Retain one `studio/index.html`; place scenes in `studio/compositions/`.
Use the installed root/host/template contract and one paused, seek-safe
timeline per composition. Register the matching composition ID after building
the timeline. Use explicit tween endpoints; let HyperFrames own media seeks
and timed clip visibility. Keep assets local and visual state independent of
wall clocks, live APIs, input events and unseeded randomness.

For substantial independent work, delegate with exact file ownership, stable
inputs and acceptance criteria. Workers may author non-overlapping scene
files or return patches; no worker edits shared root wiring, assets, manifests,
stage ledger or registry, and none submits paid work independently.
The coordinator integrates serially, reviews all changes, owns shared-state
updates and runs assembled checks. Without delegation tools, work serially.
Do not delegate prompt review without its separately required authorization.

Keep one caption track and separate graphics/audio/video kinds. Preserve
existing shot frames on the timeline. Deterministic-only graphics need no
fake provider tasks or fabricated video shots; follow the wrapper's actual
stage evidence and report any unsupported case instead of bypassing it.

Optional Seedance inserts use current supported capabilities, selected
references, natural source durations and a distinct source-to-edit map.
Freeze/register requests before authorized submission through existing
production tooling. Preserve explicit generation count; reconcile ambiguous
submissions. This skill adds no second submission or selection system.

## 5. Preview, check and render

Use only the pinned `studio_project.py` entrypoints. See the worked example
for exact syntax; never substitute bare or latest-version HyperFrames.

Run early `hf ... lint` after structural work. Inspect scene midpoints,
transitions, copy holds and the finish in snapshots and actual playback.
Scrub backward and forward to expose non-seek-safe animation. Check source
truth, reading time, fonts, dimensions, overflow and intended alpha.
Listen when audio exists; transcripts and waveforms are not listening proof.

For projects with real shot manifests, run `sync` after material
manifest/take/assembly changes. The current wrapper rejects zero-shot `sync`;
author deterministic-only compositions directly and inspect `status` instead.
If a required stage cannot accept their evidence, report the unsupported
lifecycle case without fabricating manifests or claiming delivery complete.
Apply the policy's mode-dependent checks and selections. Delivery always
requires a passing wrapper `check` with a real browser pass.
Open the loopback preview using its returned `studioUrl`; verify it works.
Record actual observations and unresolved defects, never a synthetic pass.

Only render when requested and the current approval mode permits it. Use
`render --name ... --quality delivery` for the final local file, not
`record-render`. Recheck actual streams, duration, sound and opening/ending.
Record required picture/audio/final-master locks through existing writers;
complete stages only through `stage ... complete`. Changed source invalidates
render freshness. Do not publish, upload or send feedback without that scope.

## Handoff and acceptance

Return the format-specific package:

```text
intent and endpoint / project and effective modes / unresolved decisions
evidence ledger / approved exact-copy inventory / UI and data limitations
beat table / design tokens / registry discoveries and dependency decisions
layer map / composition IDs and files / optional source-to-edit insert map
audio ownership / generation count and authorization / scoped worker ownership
preview and check evidence / render path and hashes when actually produced
acceptance against sources, legibility, timing and delivery / next action
```

A spec handoff ends at specification/prompts and labels execution unperformed.
A production handoff names the single editable project and actual verification
coverage. Never imply that automated checks establish ad performance, legal
approval, perceptual quality or successful publishing.
