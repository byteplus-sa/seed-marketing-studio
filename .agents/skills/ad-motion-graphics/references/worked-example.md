# Worked Example

Read for a complete explainer handoff, including deterministic source and the
pinned local execution loop. This is a hypothetical specification, not an
executed production, measured result or capability test.

## Brief and evidence

Fictional brief: explain assigning a task in Relayboard, 10 seconds, 16:9,
1920 x 1080, 30 fps, silent internal review, no generated media. The desired
reaction is "I understand that a person selects an owner." End with "Explore
Relayboard." This is a conceptual diagram, explicitly not reconstructed UI.
No quantified productivity claim, public placement or autonomous agent claim.

Assume the caller supplied and approved these fictional inputs for this
example; a real run must inspect them and compute real hashes:

| ID | Assumed supplied evidence | Permitted use |
| --- | --- | --- |
| F1 | Product guide says "Choose an owner for a task" | Show manual assignment, not automatic execution |
| C1 | Approved copy sheet | "Assign an owner", "Task", "Owner", "Explore Relayboard", "Conceptual workflow" |
| B1 | Approved monochrome logo and local regular font | Exact post logo and type |
| R1 | User says silent internal review only | No audio, disclosure record or publishing action |

Output endpoint is specification and code example only. No asset acquisition,
project creation, registry query or render has occurred. The proposed modes
for a future new project are `review_mode: default` and
`approval_mode: approve_for_me`; execution must read actual project state.

## Design and beat plan

Use a dark charcoal field, warm white type, one muted cyan owner token,
strong alignment and a single movement from task to owner. These are
hypothetical approved design tokens, not a reusable brand default.
The 120-pixel inset is this internal composition's design choice, not a
platform safe zone. A paid placement needs its own dated specification.

| Time | Viewer question | Visible event and end state | Owner |
| --- | --- | --- | --- |
| 0-2 s | What can I do? | "Assign an owner" enters; task and owner cards become readable | Deterministic |
| 2-6 s | How are they related? | A connector grows toward the owner; the owner token settles | Deterministic, F1 conceptual relationship |
| 6-10 s | What next? | CTA and exact logo enter, then hold | Deterministic, C1/B1 |

One scene, one sub-composition, zero provider generations. No fabricated shot
manifest is needed. The coordinator owns all files; delegation would add no
value here. In a larger version, workers would own distinct composition files
while the coordinator alone owns root wiring, assets and stage state.

## Discovery decision

On future execution, inspect existing project effects and query "draw a
connector between two cards" through the wrapper's `hf ... catalog --query`
surface before adopting a named effect. Record the result and compatibility.
No discovery result is asserted here. The source below is a hand-authored
illustration; use it in production only after discovery establishes that a
compatible reusable item is not a better fit. Do not install anything merely
to reproduce this example.

## Deterministic source contract

Future project-relative files:

```text
studio/index.html
studio/compositions/assign-owner.html
studio/assets/brand-regular.woff2
studio/assets/brand-logo.svg
```

The font/logo paths represent approved local assets, not included sample
assets. Resolve their real paths and hashes before build. Preserve the
wrapper-created root and GSAP runtime setup; bundle the existing pinned
runtime locally if required by offline rendering, without upgrading it.
Set the root's static `data-duration` to `10` and its dimensions/fps to the
brief. Keep its existing `main` timeline registration.

Mount this host under the existing root, leaving any required shot frames
intact in a real mixed-media project:

```html
<div id="assign-owner-host" data-composition-id="assign-owner"
  data-composition-src="compositions/assign-owner.html"
  data-start="0" data-duration="10" data-track-index="1"
  data-track-kind="graphics" data-width="1920" data-height="1080"></div>
```

Complete sub-composition source, using the installed template/timeline
contract. Asset paths resolve from the assembled Studio root:

```html
<!doctype html>
<html lang="en">
<body>
<template>
  <style>
    @font-face {
      font-family: "Brand";
      src: url("assets/brand-regular.woff2") format("woff2");
      font-weight: 400;
    }
    #root { position: absolute; inset: 0; color: #f4f1e8; font-family: "Brand"; }
    .assign-owner-field { position: absolute; inset: 0; background: #132129; }
    .assign-owner-layout { position: absolute; inset: 120px; display: grid; gap: 48px; }
    #assign-owner-title { font-size: 88px; font-weight: 400; margin: 0; }
    .assign-owner-flow { display: flex; align-items: center; gap: 48px; }
    .assign-owner-card { padding: 48px; border: 2px solid #f4f1e8; font-size: 64px; }
    #assign-owner-line { display: block; width: 240px; height: 8px; background: #b6dbdb; }
    #assign-owner-token { background: #b6dbdb; color: #132129; }
    #assign-owner-cta { font-size: 64px; }
    #assign-owner-note { font-size: 32px; }
    #assign-owner-logo { display: block; width: 240px; height: 80px; object-fit: contain; }
  </style>
  <div id="root" data-composition-id="assign-owner"
    data-width="1920" data-height="1080" data-duration="10">
    <div class="assign-owner-field"></div>
    <section class="assign-owner-layout">
      <h1 id="assign-owner-title">Assign an owner</h1>
      <div class="assign-owner-flow">
        <div class="assign-owner-card">Task</div>
        <div id="assign-owner-line"></div>
        <div id="assign-owner-token" class="assign-owner-card">Owner</div>
      </div>
      <div id="assign-owner-cta">Explore Relayboard</div>
      <div id="assign-owner-note">Conceptual workflow</div>
      <img id="assign-owner-logo" src="assets/brand-logo.svg" alt="Relayboard">
    </section>
  </div>
  <script>
    (() => {
      const timeline = gsap.timeline({ paused: true });
      timeline.fromTo("#assign-owner-title",
        { y: 32, opacity: 0 }, { y: 0, opacity: 1, duration: 0.8, ease: "power2.out" }, 0);
      timeline.fromTo("#assign-owner-line",
        { scaleX: 0, transformOrigin: "left center" },
        { scaleX: 1, duration: 2.4, ease: "power2.inOut" }, 2);
      timeline.fromTo("#assign-owner-token",
        { y: 24, opacity: 0.4 }, { y: 0, opacity: 1, duration: 1.2, ease: "power2.out" }, 4.4);
      timeline.fromTo("#assign-owner-cta",
        { opacity: 0 }, { opacity: 1, duration: 0.8 }, 6);
      timeline.fromTo("#assign-owner-logo",
        { opacity: 0 }, { opacity: 1, duration: 0.8 }, 6);
      window.__timelines["assign-owner"] = timeline;
    })();
  </script>
</template>
</body>
</html>
```

No generation prompt is needed. Optional future product inserts would be a
new scoped decision, with text-free prompts, source durations and edit spans;
they are not hidden dependencies of this deterministic explanation.

## Future execution and validation

The following are real wrapper command forms, not commands run by this
example. `PROJECT` must name the authorized project, and commands run from
the repository root. Never apply these to an unrelated production project.

```bash
uv run python .agents/scripts/studio_project.py init "$PROJECT" --aspect 16:9 --resolution 1080p
uv run python .agents/scripts/studio_project.py hf "$PROJECT" catalog --query "draw a connector between two cards" --json
uv run python .agents/scripts/studio_project.py hf "$PROJECT" lint
uv run python .agents/scripts/studio_project.py hf "$PROJECT" snapshot --at 1,4,7,9.5
uv run python .agents/scripts/studio_project.py status "$PROJECT"
uv run python .agents/scripts/studio_project.py check "$PROJECT"
uv run python .agents/scripts/studio_project.py hf "$PROJECT" preview --no-open --json
uv run python .agents/scripts/studio_project.py render "$PROJECT" --name explainer-v01 --quality delivery
```

This is not an unattended command batch: author between initialization and
lint, inspect snapshots/playback, resolve findings, and observe the requested
endpoint and current modes before rendering. Use the returned preview URL.
Run `init` only for a new Studio project, not on every revision.
Write valid `project.md` and inspect the existing stage lifecycle; no fake
takes, manual ledger changes or unrelated installs are implied.

Do not run `sync` for this zero-shot example: the current wrapper rejects
projects without shot manifests. In a mixed-media project, run it only after
real shot manifests exist and material manifest/take/assembly changes occur.
Author deterministic compositions directly in the initialized Studio project.
The command forms above are not proof that every stage supports zero shots;
inspect actual `status`, `check` and stage results. If a required lifecycle gate
cannot accept deterministic-only evidence, report that limitation and keep
delivery incomplete rather than fabricating shots or bypassing the gate.

Use `record-lock "$PROJECT" --decision "$DECISION"` for required reviewed
picture/final-master decisions and `stage "$PROJECT" complete "$STAGE"`
only when that stage's real evidence exists. If silent audio-preparation is
skipped, use the supported `stage ... skip audio-preparation --reason ...`
path. `record-render` is not a final-delivery substitute.

Acceptance: exact C1 copy, correct B1 assets, F1 relationship without
autonomy claims, mounted scene, readable holds, repeatable seeking, expected
dimensions/fps/duration and silent output. The real render requires playback,
decode/stream inspection and a fresh delivery check.

Current example status: source illustration only; no project, preview,
browser check, hashes, render, QA pass or publication exists.
