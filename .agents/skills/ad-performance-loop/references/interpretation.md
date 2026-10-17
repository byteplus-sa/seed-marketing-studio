# Interpretation

Focused reference for [ad-performance-loop](../SKILL.md). Read it before
presenting a ranking, a fatigue flag or a next-round recommendation.

**Verified on 2026-10-17. Re-verify platform statements against their sources
before relying on them.**

## Metric definitions

| KPI | Formula | Better | Not ranked when |
| --- | --- | --- | --- |
| `hook_rate` | 3-second views / impressions | higher | either column missing, zero impressions |
| `ctr` | clicks / impressions | higher | either column missing, zero impressions |
| `cvr` | conversions / clicks | higher | either column missing, zero clicks |
| `cpa` | spend / conversions | lower | either column missing, zero conversions |

Frequency is impressions / reach when reach is mapped (summing per-row reach
overstates unique reach across days, so treat it as a trend signal), or the
impression-weighted mean of an exported frequency column.

## Benchmarks

- **Hook rate has no official benchmark.** Published figures come from
  vendors and disagree widely. Never present one as a target or a platform
  standard.
- Compare variants against each other and against the hero in the same
  account, audience, placement and dates.

## Comparable groups

- `rank` and `next-matrix` group variants by their plan's `market` and
  `ratio` values before ranking. A market change usually means a different
  audience and often a different language; a ratio change usually means a
  different placement. Hook or talent variants are only compared with
  variants that share both.
- A group label reads `market=<value>,ratio=<value>`, with `-` when the plan
  has no value for that axis, so a campaign that never varied market or ratio
  has a single group. Ads that match no variant rank in `unmatched`.
- Other axes (for example `language`) are not grouped automatically. When the
  export mixes audiences the plan does not record, say so and filter the
  export before ingesting.
- `--across-groups` puts everything in one `all` group. Use it only on an
  explicit request, and present the result as indicative, not as a winner for
  each market or placement.

## Fatigue

- TikTok's
  [creative best practices](https://ads.tiktok.com/help/article/creative-best-practices?lang=en)
  recommend refreshing ad group creatives when delivery results show a
  consistently declining trend (accessed 2026-10-17). Other platforms publish
  their own guidance, some behind an advertiser login.
- The skill's rule is deliberately simple and explainable: latest window
  versus previous window, frequency up while CTR or hook rate down. Report it
  as "possible fatigue" with the two windows' numbers.
- One noisy window can flip the flag. When volumes are small, widen
  `--window-days` and say so.
- `next-matrix` repeats the fatigue check for the winner. A fatigued winner
  ranks on totals that include its better early windows; show both windows and
  ask whether to build the next round on it or refresh it first.

## Choosing the next test

1. Keep the winner's value on every axis already tested; the draft matrix does
   this from the winner's plan values.
2. Test one new axis next, chosen with the user. A usual order is the
   opening (hook) first, then talent or product presentation, then language
   and placement versions, but the user's question decides.
3. When no variant clearly beats the hero on the chosen KPI, say so; the next
   round may be a new concept test rather than another variation round.
4. When the winner differs by KPI (for example the best hook rate is not the
   best CPA), show both and let the user pick the KPI that matches the
   campaign goal.

## Reporting template

- Data: file name, date range, rows ingested, rows skipped, issues.
- Joins: matched variants, unmatched ads, ambiguous ads, variants without data.
- Ranking: KPI, direction, impression floor, then per comparable group: rank,
  variant, impressions, KPI value and the supporting counts.
- Fatigue: flagged variants with their two windows.
- Next: the drafted matrix path, the kept values and the new axis.
