# Column mapping

Focused reference for [ad-performance-loop](../SKILL.md). Read it when writing
`map.json` for a new export.

Ad platforms name their export columns differently and change them over time,
and the names depend on the interface language and the report's settings. The
mapping therefore names the **exact header text of the user's own file**; the
skill ships no per-platform header list. Open the export, copy the headers,
and confirm with the user which column means what when two look similar (for
example "Clicks (all)" versus "Link clicks").

## Fields

| Field | Meaning | Needed for |
| --- | --- | --- |
| `ad_name` | The ad's name as uploaded | Required; joins to variant names |
| `impressions` | Times the ad was shown | Hook rate, CTR, fatigue windows |
| `views_3s` | Video plays of at least 3 seconds | Hook rate |
| `clicks` | The click metric the user cares about | CTR, CVR |
| `spend` | Amount spent in the account currency | CPA |
| `conversions` | The conversion event the user optimizes for | CVR, CPA |
| `date` | Day or window start of the row | Fatigue |
| `reach` | Unique accounts reached | Frequency (impressions / reach) |
| `frequency` | Frequency as exported | Fatigue when reach is absent |

Only `ad_name` is required. A mapped header that is missing from the export is
listed in `missing_columns`, and every KPI that needs it is reported as not
ranked.

## map.json

```json
{
  "columns": {
    "ad_name": "Ad name",
    "date": "Day",
    "impressions": "Impressions",
    "reach": "Reach",
    "views_3s": "3-second video plays",
    "clicks": "Link clicks",
    "spend": "Amount spent",
    "conversions": "Purchases"
  },
  "date_format": "%Y-%m-%d",
  "decimal": ".",
  "delimiter": ",",
  "currency": "USD"
}
```

- `decimal`: `.` (default) or `,` for exports that write `1.234,50`.
  Thousands separators, spaces, apostrophes and currency symbols or codes are
  removed before parsing; `(12.00)` reads as negative.
- `date_format`: a Python `strptime` pattern; an ISO date at the start of the
  cell is accepted as a fallback. Unreadable dates are reported in `issues`
  and the row still counts for ranking.
- `delimiter`: optional; detected among comma, semicolon and tab otherwise.
- `currency`: a label carried into the ranking; no conversion is done. Do not
  mix currencies in one ingest.
- Empty cells and `-`, `--`, `n/a` are missing values, not zero.

## Joining ad names to variants

1. An ad name equal to a variant name matches it.
2. Otherwise an ad name that contains exactly one variant name as a whole
   token (bounded by non-alphanumeric characters) matches it, so platform
   suffixes such as ` - Copy` are tolerated.
3. An ad name containing two or more variant names is listed in
   `ambiguous_ads` and left unmatched.
4. Anything else is listed in `unmatched_ads`; its rows are kept and ranked
   under the raw ad name with `matched: false`.

Rows for the same variant across several ads or days are summed before rates
are computed, so a rate is never an average of averages.
