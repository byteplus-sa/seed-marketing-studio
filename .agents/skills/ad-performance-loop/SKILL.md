---
name: ad-performance-loop
description: >-
  Import a user-exported ad-platform results CSV, join rows to ad variant names,
  compute hook rate (3-second views per impression), CTR, conversion rate and
  CPA, rank variants by the user's chosen KPI within that account, flag
  creative fatigue when frequency rises while CTR or hook rate falls, and draft
  the next variant matrix that keeps the winner and tests one new axis. Handles
  configurable column mapping, missing columns, zero impressions, currency
  symbols, thousands separators and unknown ad names, which are reported
  rather than dropped. Use after a variant test has run and the user supplies
  an export. No platform API access, no external benchmarks, no media
  generation.
---

# Ad Performance Loop

Turn an exported results file into a ranked, explainable read of which
variants won, which are fatiguing, and what to test next. This leaf reads files
the user supplies; it never connects to an ad platform and never generates
media. Compose with `ad-variant-matrix`, which plans and names the variants
this skill joins on and turns the drafted next matrix into rows.

**Key rule: compare variants within one account, one audience and one time
range.** No hook rate, CTR or CPA is "good" or "bad" by an outside number here;
vendor benchmarks disagree and none is official.

## Inputs

| Input | Required | Notes |
| --- | --- | --- |
| Results CSV exported by the user | yes | Comma, semicolon or tab separated; UTF-8 with or without BOM |
| Column mapping (`map.json`) | yes | Maps fields to the export's own header names; see [column mapping](references/column-mapping.md) |
| Variant plan (`plan.json` from `variant_matrix.py plan`) | for joins and the next matrix | Supplies variant names and their axis values |
| The matrix that produced the variants | for `next-matrix` | Campaign, concept, budget and cap carry over |
| KPI | yes | `hook_rate`, `ctr`, `cvr` or `cpa`; ask when the user has not chosen |

Ask which KPI matters when the user has not said. Suggest `cpa` for a
conversion goal, `ctr` for traffic, and `hook_rate` for testing openings, but
let the user decide.

## Procedure

```mermaid
flowchart LR
  CSV[User export] --> I[ingest + map.json + plan.json]
  I --> M[metrics.json]
  M --> R[rank --kpi]
  M --> F[fatigue]
  R --> N[next-matrix --axis]
  N --> D[draft matrix.json]
  D --> V[ad-variant-matrix plan/cost]
```

Script: `.agents/skills/ad-performance-loop/scripts/performance_loop.py`,
run with `uv run python`. Every command prints JSON with `ok`.

1. **Ingest.** `performance_loop.py ingest <export.csv> --map map.json
   --variants projects/<campaign>/variants/plan.json --out
   projects/<campaign>/performance/metrics.json`. Read the summary: mapped
   columns that are missing from the export, unreadable values (`issues`),
   skipped rows, ads whose names match no variant, ads whose names match more
   than one, and variants with no data. **Report every one of these to the
   user**; never drop them silently.
2. **Rank.** `performance_loop.py rank metrics.json --kpi <kpi>
   [--min-impressions N]`. Entities are variants (or raw ad names when
   unmatched). An entity is not ranked when an input column is missing, its
   denominator is zero (no impressions, clicks or conversions) or it is below
   the impression floor; the reason is printed. Agree the floor with the user
   before ranking when volumes are small.
3. **Check fatigue.** `performance_loop.py fatigue metrics.json
   [--window-days 7]`. Rows are bucketed into date windows from the earliest
   date; a variant is `fatigued` when, in its latest window versus the
   previous one, frequency rose while CTR or hook rate fell. Without a date,
   reach or frequency column the status is `insufficient_data`, never a guess.
4. **Draft the next round.** `performance_loop.py next-matrix metrics.json
   --matrix variants/matrix.json --kpi <kpi> --axis <axis>=<v1>,<v2>
   [--hero-value <current value>] --out variants/round-02/matrix.json`. The
   draft keeps the winner's values for every axis already tested, varies one
   new axis, bumps `version`, and is `status: draft` with an empty hero hash.
   It refuses to overwrite an existing file.
5. **Hand off.** Bind the draft's hero to the approved winning take (shot,
   take, SHA-256, decision), then plan and cost it with `ad-variant-matrix`.

## Reading the results honestly

Read [interpretation](references/interpretation.md) before presenting a
ranking. In short:

- Present the KPI, its direction, the impression floor, and how many rows and
  days each variant has. Small differences on small volumes are not winners.
- Show `unmatched_ads`, `ambiguous_ads` and `variants_without_data` beside
  the ranking.
- Hook rate counts 3-second views over impressions; it is only meaningful for
  video ads and only when the export's 3-second view column is mapped.
- Do not call a result statistically significant; this skill computes no
  significance test. Suggest letting a close race run longer instead.
- A fatigue flag is a prompt to refresh creatives, not proof of fatigue.

## Boundaries

- No platform API, login or scraping; the user exports the file.
- No invented data: missing values stay missing and are reported.
- No external benchmark is presented as official.
- Exports can contain account data. Keep them under the project folder, never
  in the repository, and do not paste raw rows into shared documents.
