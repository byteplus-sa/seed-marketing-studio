---
name: ad-variant-matrix
description: >-
  Orchestrator that turns one approved hero ad into a planned variant test
  matrix: one axis at a time by default (full factorial only on request) across
  hook, talent, product, outfit, location, language and ratio. Routes each axis
  to its specialist (new opening beat spliced in Studio, object swap, dubbing
  with captions, per-ratio delivery), names every variant
  {campaign}_{concept}_{axis-values}_v{nn}, previews cost, and refuses rows over
  the budget or variant cap. Every row still passes prompt-review and registry
  registration; nothing is submitted by the planner. Use to multiply a winning
  ad into testable variants. Not for writing the hero ad, separate concept
  tests, or reading performance results.
---

# Ad Variant Matrix

This skill is an **explicitly-marked orchestrator**. It plans and sequences
variant production around one approved hero ad and delegates every prompt,
edit and render to the specialist skills named below. It never calls a
provider itself and never bypasses prompt-review, the registry or the approval
mode.

**Key rule: change one axis per variant unless the user explicitly asks for a
full factorial.** One change per row is what makes a result attributable.

## When to use

| Request | Use |
| --- | --- |
| "Make variants of this approved ad", "test three hooks and two talents" | this skill |
| Several different hero concepts compared against each other | a concept test (see [testing guidance](references/testing-guidance.md)); build each hero first, then one matrix per concept |
| Write or revise the hero ad itself | `ugc-ad-modes` or `film-production` |
| Rank exported results and plan the next round | compose with `ad-performance-loop` |

## Inputs and preconditions

1. **An approved hero take.** Its shot ID, take, SHA-256 and the decision
   record that approved it under the project's `approval_mode`. A candidate in
   `review` is not a hero.
2. **The hero's current value for every axis** that will vary (for example
   `hook: hook-demo-first`, `talent: vp-a`, `ratio: 9:16`). Values are IDs:
   hook IDs from the `ugc-ad-modes` hook library, element IDs for talent,
   product, outfit and location, language codes, ratios.
3. **Approved references for every new value**: Virtual Portrait `asset://`
   views for talent, official or authorized packshots for products, garment
   and location sheets. A missing or unapproved reference blocks only the rows
   that need it.
4. **Unit cost per axis** in USD from current pricing for the route and
   resolution, or the user's stated figure. Never guess a price; ask.
5. **Budget and cap**: `budget_usd` and `max_variants`. Ask when either is
   missing; do not default to "no limit".

## Procedure

```mermaid
flowchart LR
  H[Approved hero take] --> M[matrix.json]
  M --> P[plan: rows + names]
  P --> C{cost: under budget and cap?}
  C -->|no| R[Reduce axes or values, or ask for budget]
  C -->|yes| A{approval mode}
  A --> W[Per row: specialist prompt]
  W --> PR[prompt-review bound to request hash]
  PR --> REG[prepare_request.py --write --register]
  REG --> S[Submit 480p draft]
  S --> Q[QA and select under approval mode]
  Q --> D[Delivery per ratio]
```

1. **Write the matrix** at `projects/<campaign>/variants/matrix.json`
   following `.agents/contracts/schemas/variant-matrix.schema.json`. Start with
   `status: draft`.
2. **Plan.** `uv run python .agents/scripts/variant_matrix.py plan <matrix>`
   expands rows in a deterministic order (hero first, then axes in the fixed
   order hook, talent, product, outfit, location, language, ratio) and checks
   unique names, the variant cap and empty matrices. A warning above five
   variants means the rows belong in more than one ad group.
3. **Cost.** `variant_matrix.py cost <matrix> --unit-cost hook=<usd> ...`
   sums the unit costs of each row's changed axes. It exits 1 over
   `budget_usd` or `max_variants`, or when a changed axis has no unit cost.
   Show the per-row and total estimate before any spend.
4. **Approve the matrix.** In `approve_for_me` the agent may set `status:
   approved` once the plan and cost pass and the hero hash is bound. In
   `ask_for_approval` show the rows, names and total, and wait for the user's
   chat confirmation. The approval covers the plan only; each generated take is
   still selected separately.
5. **Prepare registration.** `variant_matrix.py register <matrix> --project
   projects/<campaign> --unit-cost ...` refuses a draft matrix or an unbound
   hero and prints, per provider step, the `prepare_request.py` hash command
   and register command, with prompt, review and output paths under
   `variants/<name>/`. It is a dry plan: it writes nothing and submits nothing.
6. **Produce each row** through the route below. For every provider step:
   write the prompt with the specialist skill, freeze it at the printed path,
   run the hash command, run `prompt-review` inline bound to that hash, resolve
   CRITICAL and MAJOR findings, run the register command, then submit. Steps
   within a row run in their `after` order; independent rows may run in
   parallel with explicit file ownership.
7. **QA and select** each variant under the approval mode, then place it in
   Studio and record the selection. Rows that fail QA keep their name; a retake
   is a new take, not a new variant name.
8. **Deliver** each selected variant per placement with `ad-delivery-formats`
   and run `ad-creative-check` before paid upload.

## Routing per axis

Read [axis routing](references/axis-routing.md) before writing the first row
prompt. Summary:

| Axis | Route | Specialists | Provider step |
| --- | --- | --- | --- |
| `hook` | Regenerate the opening beat only, then splice it onto the hero in Studio | `ugc-ad-modes` hook library, `seedance-prompt-25` | yes |
| `talent`, `product`, `outfit`, `location` | Object Swap on the muted hero master; keeps motion, framing, cuts and timing | `seedance-object-swap` (with `source-subject-map`) | yes |
| `talent` + `location` in one row | Motion Transfer instead of two swaps | `seedance-motion-recast` | yes |
| `language` | Re-voice the locked script, then per-language captions | `audio-dubbing`, `seedance-prompt-25-dialogue`, `ad-captions` | yes (audio) |
| `ratio` | Reframe or native regeneration per placement | `ad-delivery-formats` | none for a reframe |

Two swap classes in one factorial row (for example product and outfit) run as
**sequential** swaps with inspection between them, never one combined edit.

## Matrix file

```json
{
  "schema_version": 1,
  "status": "draft",
  "campaign": "spring-launch",
  "concept": "morning-ritual",
  "hero": {
    "shot_id": "s01_sh010",
    "take": "t03",
    "sha256": "<64-hex of the approved hero take>",
    "decision_ref": "decisions/s01_sh010_t03.json",
    "values": {"hook": "hook-demo-first", "talent": "vp-a", "language": "en", "ratio": "9:16"}
  },
  "axes": {
    "hook": ["hook-problem-callout", "hook-product-interrupt"],
    "talent": ["vp-b"],
    "language": ["es"],
    "ratio": ["4:5", "1:1"]
  },
  "strategy": "one_axis_at_a_time",
  "max_variants": 8,
  "budget_usd": 40,
  "version": 1
}
```

- `hero.values` may also hold **fixed axes** that do not vary; they stay in
  every name so a later round can tell which winner it kept.
- `naming` is optional. The default joins campaign, concept, every hero-value
  axis in fixed order and `v{nn}`; ratios render as `9x16`. A custom pattern
  may use only `{campaign}`, `{concept}`, `{nn}` and axis placeholders, and
  must keep names unique.
- `unit_cost_usd` may record agreed unit costs; `--unit-cost` overrides it.
- Platform ad names must contain the variant name unchanged so
  `ad-performance-loop` can join results.

## Gates

- **No hero, no matrix.** A hero that is not approved, or whose file hash no
  longer matches `hero.sha256`, stops the matrix.
- **Budget and cap refuse, they do not trim.** When `cost` exits 1, propose
  which axis or values to drop, or ask for a higher budget. Never silently
  drop rows.
- **Every row is a normal generation.** Prompt-review, frozen prompts, request
  hashes, registry registration before submission, 480p drafts first and the
  approval mode apply to each provider step exactly as for any other shot.
- **Facts and CTA never vary by accident.** A hook row changes the opening
  beat only; a language row translates the locked script; no row invents a
  claim, offer or testimonial. Check rows against
  `.agents/contracts/ad-compliance.md`.
- **Real people stay authorized.** Talent rows use Virtual Portrait or
  authorized `asset://` references per `seedance-virtual-portrait`.
- **Text stays in post.** Supers, captions and CTAs are added per ratio in
  Studio, never prompted into generated footage.

## Testing guidance

Read [testing guidance](references/testing-guidance.md) when the user asks how
many variants to make, how to split ad groups, or whether to run a concept
test or a variation test. It records the dated official guidance and the
practitioner conventions this skill follows.

## Output

- `variants/matrix.json` (approved) and the plan, cost and register outputs
  saved beside it as `plan.json`, `cost.json` and `register.json`.
- Per variant: `variants/<name>/prompt_<asset>.md`, its review, request,
  registry entry, take and QA notes.
- A short summary for the user: rows, names, estimated total versus budget,
  rows blocked and why, and the next action. Update `handoff.md` before any
  long wait.
