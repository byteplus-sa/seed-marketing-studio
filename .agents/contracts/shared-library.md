# Shared library

Brand kits and approved talent are reused across campaigns. They live once in a
workspace-level `library/` and each campaign **pins** the exact version it uses
by SHA-256 in its `project.md`. The library is local production state, like
`projects/`: it is never committed or published.

## Layout

```
library/
  brands/<brand-id>/
    brand.json          # brand-kit schema
    assets/             # logo files, fonts/ (hashed in brand.json)
    decisions/          # approval decision records
  talent/<talent-id>/
    talent.json         # talent entry (format below)
    refs/               # approved source images the assets were registered from
    decisions/          # approval and authorization records
```

IDs are lowercase kebab-case and equal their directory names. This workspace
`library/` is distinct from `projects/<project>/library/`, which holds a
project's reusable music, SFX and ambience.

`library/` stays local and uncommitted. It holds client identity files, font
files under license terms, authorization evidence and account-scoped asset IDs;
none of these belong in a public repository.

## Brand kits

The record format is the
[brand-kit schema](schemas/brand-kit.schema.json); building, validating and
approving a kit follows the `brand-kit` skill. Summary:

- Values come from the brand's own site, user-supplied files or manual input;
  unknown values stay null and are listed in `missing`.
- Logos and fonts are acquired (brand-owned or user-supplied), stored under
  `assets/` with SHA-256 and source; fonts carry a license.
- A kit is `draft` until approved under the approving project's
  `approval_mode`, with `approval.decision_ref` pointing into `decisions/`.
  That library approval makes the entry eligible for pinning; it never
  approves the kit for another campaign (see
  [campaign acceptance](#campaign-acceptance)).
- Any edit returns the kit to `draft` until re-approved and changes its pin.

## Talent

A talent entry is an approved, reusable on-camera identity: an invented
character registered as a Virtual Portrait, a preset digital character, or a
real person **only** with a valid authorization on the account. It follows the
Advanced Creation Rights rules in the `seedance-virtual-portrait` skill and its
[registration ledger](../skills/seedance-virtual-portrait/references/registration-and-ledger.md).

```json
{
  "schema_version": 1,
  "talent_id": "river-host",
  "display_name": "River (invented host)",
  "route": "virtual_portrait | digital_character | real_person",
  "identity_descriptor": "exact canonical descriptor copied into prompts",
  "account_scope": "provider account and project name the assets belong to",
  "group_id": "group id or null",
  "assets": [
    {
      "asset_id": "asset-...",
      "uri": "asset://asset-...",
      "view": "front close-up | full body | video | audio",
      "source_path": "refs/front_closeup_v01.png",
      "source_sha256": "64 lowercase hex",
      "status": "Active",
      "registered_at": "ISO-8601"
    }
  ],
  "authorization": {
    "kind": "invented_character | real_person_authorization",
    "evidence": "decisions/authorization.md or the user's chat statement, quoted",
    "scope": "permitted uses, territories and media as stated",
    "expires_at": "ISO-8601 or null",
    "recorded_at": "ISO-8601"
  },
  "status": "draft | approved",
  "approval": {"mode": "approve_for_me | ask_for_approval", "actor": "agent | user", "decision_ref": "decisions/...", "decided_at": "ISO-8601"}
}
```

Rules:

- **Talent binds only authorized, Active assets** (`talent.authorized`):
  every bound asset is `Active` and its authorization valid and in scope.
- **Never a real person without authorization.** A real, identifiable face,
  likeness or voice enters the roster only with a recorded, valid
  authorization on the account, and never in an AIGC Virtual Portrait group.
  Without one, offer an invented Virtual Portrait or a preset digital
  character.
- An invented character records `authorization.kind: invented_character` and
  the approved source sheet it was registered from; it must not resemble a
  real person.
- Asset IDs are account-scoped. A campaign on another account or project name
  cannot reuse them; it registers its own assets from the same approved
  sources.
- Check each asset is still `Active` and the authorization unexpired and in
  scope before binding it in a new campaign. A creative approval never extends
  authorization scope.
- Changing a source image needs a new asset and a new entry version, which
  changes the pin.

## Pinning in a campaign

A campaign records the library entries it uses in `project.md` frontmatter:

```yaml
library_pins:
  brands:
    acme-home:
      path: library/brands/acme-home/brand.json
      sha256: <output of brand_kit.py pin>
      pinned_at: 2026-10-17T10:00:00Z
      acceptance_ref: decisions/library_acme-home_acceptance.json
  talent:
    river-host:
      path: library/talent/river-host/talent.json
      sha256: <SHA-256 of talent.json bytes>
      pinned_at: 2026-10-17T10:00:00Z
      acceptance_ref: decisions/library_river-host_acceptance.json
```

- **Brand pin** = the canonical SHA-256 printed by
  `brand_kit.py pin` (sorted-key, compact UTF-8 JSON of `brand.json`). It
  covers asset bytes transitively because `brand.json` records each asset's
  hash and `validate` checks them.
- **Talent pin** = the SHA-256 of the `talent.json` file bytes.
- Production generation and delivery use **approved** entries only. A
  prompt-only draft may pin a draft brand kit and says so.
- **Pins stay current** (`library.pin_current`): before each use, a consumer
  re-computes the pin and compares it with `project.md`
  (`brand_kit.py pin --expect <sha256>` for brands). A mismatch stops the
  step.
- Re-pinning is a deliberate, recorded campaign change: update `project.md`,
  then revalidate dependent prompts, deterministic renders and reviews that
  used the old values. Never re-pin silently to clear a mismatch.

## Campaign acceptance

**Each campaign records its own mode-authorized acceptance of every pinned
library entry; it never inherits the library entry's approval or another
campaign's.** This applies the
[element identification](element-identification.md) rule that an approval is
never copied across projects.

- Under `ask_for_approval`, the acceptance is a user decision whose record
  quotes the user's own chat words.
- Under `approve_for_me`, the acceptance is an agent decision record bound to
  the pinned SHA-256, written after the agent inspects the entry for this
  campaign's brief.
- The record lives in the campaign (`acceptance_ref` in the pin) and names the
  pin it accepts. A re-pin needs a new acceptance.
- The library entry's own approval record stays where it is: it shows the
  entry is eligible, not that this campaign accepted it.
- Talent acceptance is a creative decision only; it never extends the
  authorization scope checked under `talent.authorized`.

## Git policy

`library/` must be listed in the repository's ignore rules next to
`/projects`, and nothing under it is staged by default. Share a kit with
another workspace by handing over the folder through an authorized channel,
not by committing it.
