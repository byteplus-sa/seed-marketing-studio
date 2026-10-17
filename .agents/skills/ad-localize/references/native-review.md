# Native Review

Read [the entrypoint](../SKILL.md). Rule `localize.native_review`: L3, L4 and
L5 need a recorded native-speaker or local reviewer sign-off before
final-resolution generation and before delivery. The record format is the
[native-review schema](../../../contracts/schemas/native-review.schema.json).

## Who signs

- **The reviewer or the user decides.** `decided_by` is `reviewer` or `user`;
  the agent never signs off, in either approval mode, and never writes
  `evidence` in its own words.
- `evidence` quotes the reviewer's or the user's own words.
- `reviewer_role` equals the card's `reviewer.role`, and `market_id` equals
  the card's `market_id`.

## What it binds

| Field | Binds | Stale when |
| --- | --- | --- |
| `reviewed[]` | `translation.md` and `inventory.md` (both required) plus any other reviewed file, by SHA-256, paths relative to the card folder | any listed file changes |
| `card_fields_sha256` | the card's `languages`, `casting_notes`, `settings_notes`, `props_wardrobe_notes`, `gestures_and_taboos`, `legal_lines` and `currency` | any of those card fields changes |

A stale sign-off blocks `market_card.py gate` at `final` and `delivery`; get a
new sign-off on the changed material.

## Matrix variants

A localized matrix variant has its own folder,
`markets/<market-id>/<variant-key>/`, with its own `inventory.md`,
`translation.md` and `decisions/native_review.json`. Its record sets
`variant` to the variant key and lists paths relative to the variant folder.
Run `fingerprint` and `gate` with `--variant <variant-key>`. The market's own
record has no `variant` (or `null`); neither record covers the other, and one
variant's record never covers another variant.

## Writing the record

1. Ask the reviewer to review the translation sheet, the inventory and the
   card notes, and record their reply verbatim.
2. Print the hashes to bind:

   ```bash
   uv run python .agents/skills/ad-localize/scripts/market_card.py fingerprint projects/<campaign>/markets/<market-id>/market.json
   ```

   `review_fields_sha256` goes in `card_fields_sha256`; `files` gives the
   SHA-256 of `translation.md` and `inventory.md`.
3. Write `markets/<market-id>/decisions/native_review.json`, then set the
   card's `reviewer.status` to `signed_off`, `reviewer.decision_ref` to
   `decisions/native_review.json` and `reviewer.evidence` to the same quote.
   These reviewer fields do not return an approved card to draft.
4. Run `gate --level <L> --stage final`.

## Example (invented market)

```json
{
  "schema_version": 1,
  "market_id": "north-coast",
  "reviewer_role": "native_speaker",
  "reviewer_name": null,
  "decided_by": "reviewer",
  "evidence": "Reviewer: the lines read naturally and the casting notes are fine.",
  "reviewed": [
    {"path": "translation.md", "sha256": "0000000000000000000000000000000000000000000000000000000000000000"},
    {"path": "inventory.md", "sha256": "1111111111111111111111111111111111111111111111111111111111111111"}
  ],
  "card_fields_sha256": "2222222222222222222222222222222222222222222222222222222222222222",
  "decided_at": "2026-10-17T10:00:00Z"
}
```

The hashes above are placeholders; a real record uses the `fingerprint`
output.
