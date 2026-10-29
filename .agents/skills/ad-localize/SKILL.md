---
name: ad-localize
description: >-
  Orchestrator that adapts an approved ad to another market at the depth the
  user chooses, per element: L1 translated captions and re-rendered on-screen
  text, L2 voice (dub keeping voices or a line-scoped re-voice that keeps the
  source soundtrack), L3 talent replaced through authorized Virtual Portraits,
  L4 cultural adaptation of settings, props, wardrobe, product and soundtrack,
  or L5 full transcreation into a new hero ad. Keeps a market card
  of user-supplied facts, an inventory of every spoken line and on-screen text,
  a translation sheet with review statuses, market-scoped claims, a recorded
  native or local reviewer sign-off before final generation at L3 to L5, an
  honest lip-sync verdict, and a new version in its own project without
  touching the source. No market is built in. Use to localize, translate, dub,
  recast or transcreate a finished ad for another market or language. Not for
  writing a first ad, a caption file alone (ad-captions) or ratio cuts alone
  (ad-delivery-formats).
---

# Ad Localize

This is an **orchestrator**. It owns the level choice, the market card, the
translation sheet, the gates and the handoffs for adapting one approved ad to
one target market. Leaf skills stay independent: this skill names them as prose
hints and the caller loads only the ones the chosen levels need. Stage,
approval, Studio, registry and submission rules come from `AGENTS.md` and the
[production policy](../../contracts/production-policy.md); claims, testimonial
and disclosure rules from [ad compliance](../../contracts/ad-compliance.md);
brand and talent pins from the [shared library](../../contracts/shared-library.md).
This skill does not relax any of them.

Read and copy `review_mode` independently of `approval_mode`. Default uses
minimal preflight and actual final sanity, one image and draft-first video;
strict retains detailed review and sampling. Do not load
strict craft checklists in default. Applicable claims, rights, disclosure and
native-human evidence remain required in both modes. Never fabricate a user
quote or reviewer approval to complete a record.

**No market is built in.** Language, variety, register, casting, settings,
currency, legal lines, jurisdictions and placements come from the user or a
cited source. Never infer a market from the user's name, location, account or
the language of the request. Unknown values stay `null` on the card and are
listed in `missing`.

## Rules

| Rule ID | Rule |
| --- | --- |
| `localize.source_untouched` | The source campaign's masters, takes, manifests, renders, locks and locked lines never change. The only addition there is `markets/<market-id>/`; every new file goes to the localized project. |
| `localize.native_review` | L3, L4 and L5 need a recorded native-speaker or local reviewer sign-off (`reviewer.status: signed_off` with a hash-bound `decision_ref`) before final-resolution generation and before delivery. The agent never signs off, in either approval mode. |
| `localize.claims_market_scoped` | Every claim, price and offer in the localized ad resolves to a `supported` (or current `perishable`) fact in the target market's own facts file. A fact supported for the source market is not valid in the new one until it is sourced or substantiated there. |
| `localize.market_card_sourced` | Every card value is user-supplied or sourced; nothing is filled from assumptions about a market. |

Existing rules still apply to every localized deliverable:
`ad.claims_supported`, `ad.no_fabricated_testimonial`, `ad.disclosure_recorded`,
`ad.safe_zone`, `brand.copy_rules`, `library.pin_current` and `talent.authorized`.

## Inputs and outputs

Input: the approved source campaign (`project.md`, shot manifests, the selected
text-free takes, the delivered master and its render record, locks, the locked
script and supers, the pinned brand kit, the product facts), the target market
as the user describes it, the levels the user wants per element, and
any glossary or locked target-language wording.

Output, never an overwrite of the source:

```
projects/<campaign>/markets/<market-id>/
  market.json        # market card, schema market-card.schema.json
  inventory.md       # every spoken line and on-screen element; per-element level table
  translation.md     # translation sheet
  decisions/         # level choices, reviewer sign-off, card approval
  <variant-key>/     # one per localized matrix variant: inventory.md,
                     # translation.md, decisions/native_review.json
projects/<campaign>-<market-id>/            # localized version: project.md, studio/,
                                            # elements/, captions/, delivery/
projects/<campaign>-<market-id>-<ratio>/    # per-ratio cut, when combined with ad-delivery-formats
projects/<campaign>-<variant-key>-<market-id>[-<ratio>]/  # localized matrix variant
```

`market-id` is lowercase kebab-case, equals the card folder, and is the value
the `market` axis of `ad-variant-matrix` uses. A matrix market row points at
this card and this localized project; the matrix plans the row and this skill
plans, reviews and registers its own operations.

**Matrix variants.** When several matrix variants (for example `hook-a` and
`hook-b`) are localized for the same market, their lines and text differ, so
each gets its own inventory, translation sheet and sign-off at
`markets/<market-id>/<variant-key>/`, while the market card stays at
`markets/<market-id>/market.json`. The variant key is the kebab-case of the
variant's changed generated values in axis order, as the matrix prints it.
Gate and fingerprint a variant with `--variant <variant-key>`; its output goes
to `projects/<campaign>-<variant-key>-<market-id>[-<ratio>]`. One variant's
sign-off never covers another variant or the market's own record.

## Adaptation levels

Follow the [performance contract](../../contracts/performance-direction.md)
without expanding the selected level. L1 text and L2 voice retain picture
performance. L3 talent and L4 source-preserving swaps inherit action, expression,
pauses and blocking; do not add acting improvements. Newly authored or materially
changed character performance, normally L5 for that beat, uses
`acting-direction` before coverage and `seedance-acting-console` for cue encoding.
Store `## Performance plan` in the localized scene or shot, preserve locked
target copy/CTA and supported market claims, and require `acting.plan_bound`
when applicable in both review modes. This never replaces
`localize.native_review`, campaign pins or the budget gate.

The user picks one level for the whole ad or a level per element. **Recommend
the cheapest level that satisfies the user's goal; never force one.** Levels
compose: L3 talent with L2 voice and L1 text is a normal plan. Read
[levels](references/levels.md) before choosing; it holds routes, costs, what
changes, what stays and QA per level.

| Level | Changes | Routed through | Provider cost |
| --- | --- | --- | --- |
| L1 Captions and text | Subtitle sidecars, burned captions, supers, CTA, end card, price, currency, legal lines, written with the market's values | `ad-captions`, `html-graphic-render`, HyperFrames overlays in Studio | none |
| L2 Voice | Dub keeping voices, or new voice-over or line-scoped re-voice; source soundtrack kept; plus L1 | `audio-dubbing`, `seed-audio-prompt`, `ark-mcp` | audio per line or segment |
| L3 Talent | Presenter or cast replaced; plus L2 or L1 as chosen | `seedance-object-swap` (one character), `seedance-motion-recast` (whole cast), `seedance-virtual-portrait` | one edit per shot, 480p draft then final |
| L4 Cultural | Settings, props, wardrobe, product SKU or packaging, soundtrack | swaps or recast, `product-intake`, `seed-audio-prompt` | one edit per changed element per shot |
| L5 Transcreation | New script, angle and shots from the same brand and product facts | `brief-intake`, `seedance-ugc-ads`, `seedance-prompt-25`, `seedance-prompt-25-dialogue` | a full new production, draft first |

L1 is a first-class option, not a fallback. **Re-rendered on-screen text with
market values (price, currency, CTA, legal lines) is L1**, still subject to
`localize.claims_market_scoped`; L4 is reserved for picture, setting, product
and soundtrack changes. Never force a deeper level. A gesture or action that
must change cannot be fixed by a swap, which keeps motion; it needs a recast of
the beat or an L5 shot.

**Per-element levels live in `inventory.md`, not on the card.** The card's
`level_default` covers every element without a row; the inventory's level
table (format in [levels](references/levels.md#recording-levels-in-inventorymd))
records each element's level and lets one element sit below the default.

## Workflow

1. **Scope.** Ask what the user wants the audience to experience, which
   elements must change, placements, whether the ad is paid and where,
   and whether a native speaker or local reviewer is available. Ask only what
   would change the result.
2. **Market card.** Create it and fill it from the user's answers and cited
   sources only. Read [market card](references/market-card.md).

   ```bash
   uv run python .agents/skills/ad-localize/scripts/market_card.py init projects/<campaign> <market-id> --label "<user's name for it>"
   uv run python .agents/skills/ad-localize/scripts/market_card.py validate projects/<campaign>/markets/<market-id>/market.json
   ```

   Approve the card under the project's `approval_mode` once the values the
   chosen levels need are present (`show` lists them per level).
3. **Inventory.** In `inventory.md`, list every element a viewer can see or
   hear: each spoken line (speaker, addressee, window), voice-over, caption,
   super, CTA, price, offer, legal line, end card, logo lock-up, presenter,
   other cast, setting, props, wardrobe, gestures, product SKU and music. Read
   them from the manifests, the Studio timeline and the final render, not from
   the plan.
4. **Choose a level per element with available cost estimates.** Record level, route,
   provider steps and the estimate per element in the `inventory.md` level
   table, and the total when known. Unit costs come from current pricing for the route and resolution
   or from the user's figure; never guess a price. Missing estimates are unknown
   and do not block generation or require spending approval. Under `ask_for_approval`
   show the plan and wait; under `approve_for_me` record the agent decision.
   A user-stated level is never raised or lowered by the agent.
5. **Translate.** Fill `translation.md` for every spoken line and every
   on-screen string, keeping register, speakable length, glossary terms and
   claim wording. Read
   [translation and transcreation](references/translation-and-transcreation.md).
6. **Check claims for the market.** Build or reuse the target market's facts
   with `product-intake` in the localized project and set `facts_ref` and
   `price_source`. Cut or hold any claim that is not supported there
   (`localize.claims_market_scoped`).
7. **Set up the localized project.** `projects/<campaign>-<market-id>/` gets
   its own `project.md` (the source brief, the same `approval_mode` and
   `review_mode`, the market
   card path and SHA-256, the source master path and SHA-256, the chosen levels)
   and its own Studio project. It places byte copies of the source's
   **text-free** selected takes, pinned by hash, never the flattened master,
   so localized text is never laid over source-language text.
8. **Produce through the routed skills** in the order text, voice, talent,
   cultural, transcreation, as the plan needs. Every generation-bound prompt
   is frozen, checked with mode-appropriate preflight and registered with
   `prepare_request.py --register`. Strict uses inline `prompt-review`.
   Both modes start every new Seedance 2.5 generation with explicit
   `resolution: "480p"` and boolean `draft: true`; no skip-draft exception
   applies. Resolve schema or transport conflicts without dropping the flag.
   Other models without native Draft use a plain 480p test.
   Run
   `market_card.py gate --level <L> [--element <id>] --stage final` before any
   final-resolution request; the gate uses the stricter of `--level` and the
   card's `level_default` unless the element has its own row in `inventory.md`,
   and without `--element` it also takes the highest level `inventory.md`
   records.
   L3 to L5 stop there until the reviewer signs off, including direct-to-target
   default production. **Every L3 to L5
   final-resolution request passes `--required-rule localize.native_review` to
   `prepare_request.py`**, and that review check is `pass` only with the passing
   gate output as its evidence.
9. **QA** per the checklist below; provider success is `review`, not approval.
10. **Deliver.** Render the localized master with `studio_project.py render`,
    close stages as the policy requires, run `gate --stage delivery`, then
    `ad-delivery-formats` per ratio and `ad-creative-check` per deliverable.
    Update `handoff.md` in the localized project.

## Approval gates

| Item | Gate |
| --- | --- |
| L1 subtitles and text, L2 dubs | Follow the project `approval_mode`. Under `approve_for_me` the agent may accept target text for production (`agent_accepted`) and select passing takes; the text stays **unverified** in every report until a native speaker confirms it (`native_checked`). |
| L3 casting, L4 cultural changes, L5 new scripts | **Require** a native-speaker or local reviewer sign-off decided by the reviewer or the user (never the agent) and quoting their words, bound to the SHA-256 of `inventory.md`, `translation.md` and the reviewed card fields, before final-resolution generation and before delivery. 480p drafts may run before it. A change to any of them makes the sign-off stale. Record format: [native review](references/native-review.md). |
| Talent | Only authorized, `Active` Virtual Portraits or approved `library/talent` entries pinned and accepted for this campaign. Casting follows the user's `casting_notes`, never a stereotype of the market. |
| Real voices | Cloning or keeping a real person's voice needs that person's recorded consent; prefer voices of invented characters. |
| Paid delivery | One disclosure decision record per deliverable, listing every target jurisdiction it covers, asked and recorded per [ad compliance](../../contracts/ad-compliance.md#disclosure-decision-per-paid-deliverable). The source market's decision never carries over. Internal reels stay label-free. |

## QA checklist

Record pass, fail, needs-human or not applicable with evidence per element.
Level-specific checks are in [levels](references/levels.md).

- **Source untouched.** Source campaign files and hashes unchanged; the
  localized master is a new render with its own record.
- **Text.** Every inventoried line and string has a target row; no unrecorded
  merge, drop or addition; glossary, names, marks and register match the
  sheet; numbers, prices, dates and units follow the card; legal lines are
  verbatim. Rows not `native_checked` are listed as unverified.
- **Claims.** Each claim maps to a fact in the target market's facts file;
  perishable facts are within their freshness window.
- **Captions and supers.** Sidecars named `<master-stem>.<language-code>.srt`
  from the locked target text; burned text inside the safe zone; right-to-left
  and CJK lines viewed in a real player; no text baked into generated video.
- **Speech (L2, L3, L5).** Speech-to-text diff of every line against the locked
  target text, word by word; a listening pass for pronunciation, accent,
  register and speaker identity, which a transcript cannot certify.
- **Soundtrack (L2).** Music, effects and room tone intact across each replaced
  line; loudness matched; video stream identical to the source (MD5) when the
  picture did not change.
- **Picture (L3 to L5).** Identity against the bound asset, wardrobe, product,
  setting, continuity and the opening window re-checked on every new take.
- **Lip-sync verdict.** Exactly one per spoken shot: `native` (generated with
  the target-language speech and checked by eye), `approximate` (new voice over
  source mouth motion) or `not_applicable` (L1, off-screen voice). Never claim
  sync that was not viewed.
- **Records.** Every paid operation registered with its prompt snapshot and
  any required review; estimated and confirmed cost; disclosure records for paid
  deliverables; `handoff.md` lists levels, unverified items and open defects.

## Specialist hints (prose, not directives)

`ad-captions` writes sidecars and burn-in layers; `html-graphic-render`
renders static cards and supers; `audio-dubbing` dubs with the source voices
and is where L2 audio routes check Seed Audio language support;
`seed-audio-prompt` writes Seed Audio 1.0 voice-over and re-voice prompts;
`seedance-prompt-25-dialogue` checks native language support for L3 and L5
shots where Seedance speaks and writes dialogue direction, and its market pack
template describes optional language-specific packs; `seedance-object-swap` and `seedance-motion-recast`
replace talent, props, products and settings; `seedance-virtual-portrait`
binds authorized identities; `product-intake` sources the market's facts;
`brief-intake`, `seedance-ugc-ads` and `seedance-prompt-25` write an L5 ad;
`ad-delivery-formats` cuts ratios; `ad-creative-check` runs the pre-spend
check; `prompt-review` handles strict or explicitly required/requested review.

## References

| Need | Reference |
| --- | --- |
| Level ladder, routes, cost drivers, what changes, QA per level | [Levels](references/levels.md) |
| Filling, validating and gating the market card | [Market card](references/market-card.md) |
| Reviewer sign-off record and its hashes | [Native review](references/native-review.md) |
| Translation sheet, register, length, glossary, CTA and claims, RTL and CJK | [Translation and transcreation](references/translation-and-transcreation.md) |
| Card and sign-off record formats | [market-card.schema.json](../../contracts/schemas/market-card.schema.json), [native-review.schema.json](../../contracts/schemas/native-review.schema.json) |
