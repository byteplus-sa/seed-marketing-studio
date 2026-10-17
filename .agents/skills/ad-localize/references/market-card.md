# Market Card

Read [the entrypoint](../SKILL.md). The card records what the user told you,
or what a cited source says, about one target market. It is the only place
this skill reads market facts from. The record format is the
[market-card schema](../../../contracts/schemas/market-card.schema.json).

**Rule `localize.market_card_sourced`:** every value is user-supplied or
sourced. Never infer a value from the user's name, location, account, the
language of the request, or general beliefs about a country or culture.
Unknown values stay `null` and are listed in `missing`; the validator rejects a
silent `null`.

## Location and commands

`projects/<campaign>/markets/<market-id>/market.json`, with `decisions/` beside
it. `market_id` equals the folder name and `campaign` the campaign folder.

| Command | Prints | Exit 1 when |
| --- | --- | --- |
| `init <campaign-dir> <market-id> [--label TEXT]` | the new card path | the campaign folder is missing or a symlink, `markets/` or the card folder is a symlink or escapes the campaign, an id is not kebab-case or longer than 48 characters, or the card exists |
| `validate <market.json>` | `{"ok", "findings"}` | schema error, malformed or deprecated language tag (`iw`, `ji`), writing direction that contradicts the tag, unknown placement id, unlisted unknown value, a card outside `<campaign>/markets/<market-id>/`, a `signed_off` reviewer without role, `decision_ref` or `evidence`, a price without its facts file or currency code, a `facts_ref` outside the localized project's `elements/`, a `price_source` that is not a perishable fact in an existing facts file, a missing approval decision record, or an approved card defaulting to L3 to L5 with no reviewer |
| `show <market.json>` | the consumer view, the localized project path, caption codes, and per level the blockers before final generation | the card is invalid |
| `fingerprint <market.json> [--variant KEY]` | `card_sha256` for the approval, `review_fields_sha256` and the SHA-256 of `translation.md` and `inventory.md` for a sign-off | the card is unreadable or the variant key is invalid |
| `gate <market.json> --level L1..L5 [--element ID] [--variant KEY] [--stage draft\|final\|delivery]` | `{"ok", "requested_level", "level", "output_project", "blockers"}` | a field the effective level needs is unknown; the variant folder is missing; `--element` has no valid row in `inventory.md`; for `final` and `delivery` the card is not approved or changed after approval, or, at L3 to L5, the reviewer sign-off is missing, unreadable, for another market, variant or reviewer role, not decided by the reviewer or the user, or stale; for `delivery` placements or jurisdictions are unknown |

**Effective level.** The gate checks the stricter of `--level` and the card's
`level_default`. A lower level passes only for an element whose row in the
`inventory.md` level table records it (`--element`); see
[levels](levels.md#recording-levels-in-inventorymd). With `--variant`, the
inventory, translation sheet and sign-off come from
`markets/<market-id>/<variant-key>/` and the output project is
`projects/<campaign>-<variant-key>-<market-id>`.

Run from the repository root with
`uv run python .agents/skills/ad-localize/scripts/market_card.py`.

## Fields

| Field | Fill from | Notes |
| --- | --- | --- |
| `label` | the user's name for the market | free text, shown in reports |
| `languages[]` | the user | `code` is a BCP 47 tag (`es-419`, `pt-BR`, `zh-Hant-TW`, `ar`) with language, script, region and variant subtags only (no `-u-` or `-x-` extensions, so `ad-captions` accepts every tag; use `he` and `yi`, not `iw` and `ji`); `variety` and `register` are the user's words, for example "neutral regional", "informal second person"; `direction` is `ltr` or `rtl` and must agree with the tag's script |
| `subtitle_languages[]` | the user | BCP 47 tags; `[]` means no sidecars, `null` means not yet asked. Sidecar file names use the lowercase tag |
| `casting_notes` | the user, in their words | who should appear and how. Never written by the agent from assumptions about the market |
| `settings_notes`, `props_wardrobe_notes`, `gestures_and_taboos` | the user or a source they point to | what to change and what to avoid; quote the source when there is one |
| `currency` | the user or the market's own price page | `code` ISO 4217, `symbol`, `format` (for example `{symbol}{amount}` with the separators the user gave) |
| `number_and_date_formats` | the user or a style guide they supply | `number` (decimal and grouping) and `date` patterns |
| `units` | the user | `metric`, `imperial` or `mixed` |
| `facts_ref` | the localized project's product card | `projects/<campaign>-<market-id>/elements/<product-id>/facts.json` (or a localized variant's `projects/<campaign>-<variant-key>-<market-id>/elements/…`), built with `product-intake` from sources valid for this market; never the source campaign's facts |
| `price_source` | that facts file | the `fact_id` of a fact with status `perishable`; requires `facts_ref` and `currency.code` |
| `legal_lines[]` | the user, the brand or their counsel | exact `text`, the `when` condition, and `source`; `[]` means the user confirmed none |
| `ai_disclosure.jurisdictions` | the user | ISO 3166 codes such as a country or `country-subdivision`; `decision_refs` lists one disclosure decision record per deliverable, each listing the jurisdictions it covers |
| `placements[]` | the user | ids from [ad-platforms.json](../../../contracts/ad-platforms.json) only |
| `reviewer` | the user | `role` `native_speaker` or `local_reviewer`, `name` or `null`, `status` `none`, `pending` or `signed_off`, `decision_ref`, `evidence` |
| `level_default` | the user's choice | `L1` to `L5` or `null`; per-element levels live in the `inventory.md` level table, not on the card |
| `status`, `approval` | the approval mode | `approved` needs an `approval` record with `mode`, `actor` (`user` under `ask_for_approval`), an existing `decision_ref` relative to the card folder, `decided_at` and `card_sha256` from `fingerprint` |

## Example (invented market)

```json
{
  "schema_version": 1,
  "market_id": "north-coast",
  "campaign": "trail-bottle-launch",
  "label": "North Coast (invented example)",
  "languages": [{"code": "es-419", "variety": "neutral regional, as the user asked", "register": "informal, second person", "direction": "ltr"}],
  "subtitle_languages": ["es-419"],
  "casting_notes": "User: one presenter in their thirties, outdoor guide look, no uniform",
  "settings_notes": "User: keep the trailhead; replace the parking sign with a blank wooden post",
  "props_wardrobe_notes": null,
  "gestures_and_taboos": "User: no thumbs-up close-up",
  "currency": {"code": "XTS", "symbol": "¤", "format": "{symbol} {amount}"},
  "number_and_date_formats": {"number": "1.234,56", "date": "DD/MM/YYYY"},
  "units": "metric",
  "facts_ref": "projects/trail-bottle-launch-north-coast/elements/trail-bottle/facts.json",
  "price_source": "f07",
  "legal_lines": [{"text": "<exact line the user supplied>", "when": "price shown", "source": "user, brand legal team"}],
  "ai_disclosure": {"jurisdictions": null, "decision_refs": []},
  "placements": ["meta-instagram-reels"],
  "reviewer": {"role": "native_speaker", "name": null, "status": "pending", "decision_ref": null, "evidence": null},
  "level_default": "L3",
  "missing": ["ai_disclosure.jurisdictions", "props_wardrobe_notes"],
  "status": "draft",
  "approval": null
}
```

`XTS` is the ISO 4217 code reserved for testing; a real card uses the code the
user or the market's price page gives.

## Approval and change

- Approve the card under the campaign's `approval_mode` once the fields the
  chosen levels need are present (`show` lists the blockers per level). The
  approval covers the card's completeness and consistency, not its cultural
  correctness, which only the reviewer can confirm.
- Any edit other than recording the reviewer's status, name, decision record
  and evidence, or a disclosure record reference, returns the card to `draft`:
  the gate compares `approval.card_sha256` with the current card and blocks
  until it is re-approved with a fresh `fingerprint`.
- A change to languages, casting, settings, props and wardrobe, gestures,
  legal lines or currency after a reviewer signed off makes the sign-off stale
  (`card_fields_sha256`), and so does a change to `inventory.md` or
  `translation.md`; see [native review](native-review.md).
- The reviewer sign-off is recorded only from the reviewer's or the user's own
  words. Under `approve_for_me` the agent still cannot set `signed_off`.
