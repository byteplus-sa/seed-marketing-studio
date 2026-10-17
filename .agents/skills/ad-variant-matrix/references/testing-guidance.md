# Testing guidance

Focused reference for [ad-variant-matrix](../SKILL.md). Read it when the user
asks how many variants to make, how to group them, or which kind of test to
run.

**Verified on 2026-10-17. Re-verify every platform statement against its
source before relying on it; platform guidance changes without notice.**

## Official guidance (TikTok)

Source: TikTok Ads Manager help,
[Creative best practices for performance ads](https://ads.tiktok.com/help/article/creative-best-practices?lang=en),
accessed 2026-10-17.

- **3–5 different creatives per ad group** and **3–5 diversified ad groups
  per campaign**.
- **Creatives with big differences** are better, especially while testing
  and in the ad group's exploration stage.
- **Refresh creatives** when delivery shows a consistently declining trend;
  add the new creatives to the existing ad group rather than creating a new
  one.

Other platforms publish their own creative and fatigue guidance; some of it is
behind an advertiser login. Do not transfer one platform's numbers to another.

## Concept tests versus variation tests

Keep the two separate; mixing them makes results unreadable.

| | Concept test | Variation test (this skill) |
| --- | --- | --- |
| Question | Which idea works? | Which version of the winning idea works? |
| Creatives | Substantially different heroes: angle, mode, script structure | One hero with one axis changed per row |
| When | Exploring a new product, audience or offer | After a concept has a winner |
| How to build | One hero per concept through the normal production flow | One matrix per winning concept |

- The official "big differences while exploring" advice applies to **concept
  tests**. A one-axis matrix deliberately produces small differences, so run
  it after exploration, not instead of it.
- A matrix holds one concept. Several concepts mean several matrices with
  different `concept` IDs.

## Sizing a matrix

- One-axis-at-a-time size is `sum over axes of (values - 1)`, plus the hero.
  Full factorial size is the product of every axis's value count, which grows
  fast: three hooks, two talents and three ratios is 18 rows.
- More than five variants will not fit one ad group at 3–5 creatives; the
  planner warns, and the rows should be grouped by axis across ad groups.
- Ratio variants of the same creative are placement versions, not separate
  creative tests; group them with their creative.

## Naming

Practitioner convention (not an official standard): put every tested
attribute in the ad name in a fixed order so exported results can be joined
and filtered, for example `{campaign}_{concept}_{hook}_{talent}_{ratio}_v{nn}`.
This skill's planner enforces unique names and keeps fixed axes in the name.
Upload ads with the variant name unchanged (a platform may append copy
suffixes; the performance loop tolerates surrounding text but not edits inside
the name).

## What this skill does not claim

- No expected lift, hook rate, CTR or CPA is promised for any axis or value.
- No vendor benchmark is presented as official. Results are compared within
  one account and audience by `ad-performance-loop`.
