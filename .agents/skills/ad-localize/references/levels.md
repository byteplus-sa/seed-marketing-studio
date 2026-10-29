# Levels

Read [the entrypoint](../SKILL.md). Choose a level per inventoried element,
record it with its route and estimate in the `inventory.md` level table, and
recommend the cheapest level that meets the user's goal. The user decides; a recommendation
never forces a level, and the agent never raises or lowers a level the user
stated.

- [Choosing](#choosing)
- [Element to minimum level](#element-to-minimum-level)
- [Recording levels in inventory.md](#recording-levels-in-inventorymd)
- [Cost estimate](#cost-estimate)
- [L1 Captions and text](#l1-captions-and-text)
- [L2 Voice](#l2-voice)
- [L3 Talent](#l3-talent)
- [L4 Cultural adaptation](#l4-cultural-adaptation)
- [L5 Full transcreation](#l5-full-transcreation)
- [Upgrading later](#upgrading-later)

## Choosing

| User goal | Recommend |
| --- | --- |
| Feed placements watched mostly with the sound off; the message is carried by captions and supers | L1 |
| The audience must hear the message in its language; picture stays | L2 + L1 |
| The presenter or cast should be someone the user cast for this market | L3 + L2 + L1 |
| Prices, currency, CTA or legal lines differ in the market | L1 with the market's values |
| Settings, props, wardrobe, product variant or music differ in the market | L4 for those elements, plus the lower levels the rest need |
| The angle, joke, hook or story does not travel; the user wants a native-feeling ad | L5 |
| Budget is tight, the language is not natively supported, or no reviewer is available | L1 now, upgrade later |

Mixing is normal: L1 for every string including the market price card, L2
for the voice-over, L4 for one setting shot. Record the reason per element.

**Market values on screen are L1.** Re-rendering a price, currency, CTA or
legal line with the market's values is L1 text work, still subject to
`localize.claims_market_scoped`. L4 is reserved for picture, setting, product
and soundtrack changes. Never force a deeper level than the change needs.

## Element to minimum level

| Element | Minimum level that can change it | Route |
| --- | --- | --- |
| Caption sidecar, burned caption | L1 | `ad-captions` |
| Super, CTA, end card, offer, price, currency, legal line, disclosure label | L1, also when the value changes for the market | `html-graphic-render` or a HyperFrames overlay |
| Spoken line, voice-over | L2 | `audio-dubbing` or `seed-audio-prompt` |
| Presenter, one character | L3 | `seedance-object-swap` (character class) |
| Whole cast | L3 | `seedance-motion-recast` |
| Setting | L4 | `seedance-object-swap` (location class), or recast when cast and setting both change |
| Prop, wardrobe | L4 | `seedance-object-swap` (prop or outfit class), one class per pass |
| Product SKU, packaging | L4 | `product-intake` for the market packshot, then `seedance-object-swap` (product class) |
| Gesture, action, blocking | L5 for that beat (or a recast that maps the beat to new motion when the source motion is acceptable) | new shot through `seedance-prompt-25` |
| Music bed | L4 | a new bed through `seed-audio-prompt`, or a licensed track the user supplies |
| Script, hook, angle, structure | L5 | `brief-intake`, `seedance-ugc-ads`, `seedance-prompt-25` |

A swap keeps the source motion, so it cannot remove a gesture or an action.
Performance is inherited at L1-L4 unless the inventoried change explicitly
authorizes new acting at the appropriate level. For new L5 character beats,
derive a source-bound performance plan before coverage and encode only the
authorized delta. Keep target copy, CTA, product identity and market facts
locked. Apply `acting.plan_bound` when relevant; L3-L5 human sign-off remains
a separate final-generation and delivery gate.

## Recording levels in inventory.md

**Per-element levels live in `inventory.md`, not on the market card.** The
card's `level_default` applies to every element without a row. Write one
Markdown table whose header has an `id` and a `level` column; other columns are
free:

```markdown
| id | kind | level | route | estimate | reason |
| --- | --- | --- | --- | --- | --- |
| super-01 | super | L1 | html-graphic-render | none | sound-off placement |
| s01_sh010_l02 | spoken | L2 | audio-dubbing | per line | voice carries the hook |
| presenter | presenter | L3 | seedance-object-swap | per shot | user's casting notes |
```

- `id` is unique; `level` is `L1` to `L5`. A duplicate id or another level
  value blocks the gate.
- `market_card.py gate --level <L> --element <id>` gates that element at the
  stricter of `--level` and its row's level. When the id has no row the gate
  blocks. Without `--element`, the gate uses the strictest of `--level`, the
  card's `level_default` and the highest level any row in `inventory.md`
  records, so a lower level never passes by omission.
- Level choices follow the approval mode. A user-stated level is never raised
  or lowered by the agent.
- `inventory.md` is part of the reviewer sign-off at L3 to L5, so editing a
  level after sign-off makes the sign-off stale.

## Cost estimate

Estimate per element before any spend and show the total against the budget.

| Level | Provider steps | Unit cost source |
| --- | --- | --- |
| L1 | none; deterministic renders and a Studio render | local compute only |
| L2 | one audio operation per generation segment (dub) or per changed line (re-voice), plus any audio separation task | current Seed Audio and separation pricing, or the user's figure |
| L3 | one swap or recast per shot that shows the talent, at 480p draft and again at final | current Seedance pricing for the operation, duration and resolution |
| L4 | one swap per changed element class per shot, drafts and finals; product intake is free | as L3 |
| L5 | a full production: element sheets, shots, drafts, finals, audio | sum of the production plan |

Never guess a price. A retake is a new scoped decision with its own estimate.
When `ad-variant-matrix` planned the market row with a single `market` unit,
replace that estimate with this per-element one and tell the user if it
exceeds the matrix budget.

## L1 Captions and text

**Changes:** subtitle sidecars, burned captions, and every on-screen string
re-rendered in the target language. **Stays:** picture, audio, timing.

1. Translate every caption line and string; get the text accepted per the
   approval gates. Every claim, price and offer row maps to a fact in the
   target market's facts file (`localize.claims_market_scoped`).
2. Sidecars: run `ad-captions` from the locked target text and the timing
   measured on the source master. Captions follow locked words, never heard
   words, so a subtitle of a source-language voice says what the voice says.
3. On-screen text: rebuild each super, CTA, price, legal line and end card as
   a deterministic layer in the localized Studio project, laid out per ratio
   inside the safe zone, in the brand typeface or a licensed fallback that
   covers the target script. Place it over the source's text-free takes.
   Prices come only from the market's perishable price fact (`price_source`),
   within its freshness window, in the card's currency format; numbers, units
   and dates follow the card; legal lines are verbatim from the card where
   their `when` condition holds.
4. Render a new master with `studio_project.py render` when anything is
   burned in; sidecar-only delivery needs no render and records the master
   hash its timing was measured against.

**QA:** text rows complete; reading speed and line length warnings resolved;
each language viewed in a real player; layout inside the safe zone; numbers,
currency and dates per the card; legal lines verbatim; claim map against the
market facts. **Lip-sync verdict:** `not_applicable`.

## L2 Voice

**Changes:** spoken audio, plus L1 text. **Stays:** picture, music, effects
and room tone.

Pick one route per voice:

| Route | Use when | Skill |
| --- | --- | --- |
| Dub keeping the voices | The same voices should speak the new language | `audio-dubbing` (Seed Audio 1.0 voice cloning with the source as reference) |
| New voice-over | Off-screen narration; a new voice suits the market | `seed-audio-prompt` (text-to-audio) |
| Line-scoped re-voice | Only some lines change, or a few words are wrong | `seed-audio-prompt` (text and audio to audio) per line window |

1. Check that Seed Audio supports the target language for the chosen route,
   using `audio-dubbing` (its preparation checklist, language reference and the
   current Seed Audio API reference), and record the result. An unsupported
   language is told to the user before any spend; offer L1 instead.
2. Fit each translated line to its window at natural speed. Preserve locked
   target words and pauses; return overruns for authorized retiming, splitting
   or a separately approved text revision, never silent shortening or speeding up.
3. Keep the source soundtrack: use the source project's separate music and
   effects stems when they exist, otherwise separate the delivered mix with
   the audio separation tool and keep the background stem. Never ship a
   dialogue-only track over a cut that had music or effects.
4. Every audio operation is prompt-reviewed, registered and saved locally with
   hashes. Fix wrong words with a word-scoped patch, never a second full dub.
5. Place the new audio in the localized Studio project and render a new
   master; loudness-match to the delivery target.

**QA:** speech-to-text diff per line against the locked target text; a
listening pass; soundtrack continuity across every replaced line; video
stream MD5 equal to the source. **Lip-sync verdict:** `approximate` for
on-camera speech (source mouths, new language), `not_applicable` for
off-screen voice-over. Say so; it is a known limit, not a defect to hide.

## L3 Talent

**Changes:** the presenter or cast, plus L2 and L1 as chosen. **Stays:**
motion, camera, cuts and timing.

1. Casting comes from `casting_notes`, written by the user. Never pick an
   identity from assumptions about the market's people, skin tone, body type
   or dress; ask when the notes are empty.
2. Identities are only authorized, `Active` Virtual Portraits or approved
   `library/talent` entries, pinned and accepted for this campaign per the
   shared library contract. A real person needs a valid authorization on the
   account; otherwise offer an invented Virtual Portrait.
3. One character: `seedance-object-swap` (character class). Whole cast:
   `seedance-motion-recast` with a disposition for every visible subject.
   Both take the muted, text-free selected take of each shot and add audio in
   post.
4. Voice: a new face with the source voice is a mismatch to flag. Re-voice
   through L2 with a voice suited to the new character, or keep the source
   voice only when the user chooses it. When a shot is regenerated with
   Seedance speaking the target language, check native support with
   `seedance-prompt-25-dialogue` first and record the result.
5. Drafts at 480p may run before the reviewer signs off; final-resolution
   requests wait for `market_card.py gate --level L3 --stage final`.

**QA:** identity against the bound asset on every take; no residue of the
source person; hands, product contact and eyelines intact; speech QA as L2.
**Lip-sync verdict:** `approximate` with a re-voice over the kept mouth
motion; the swap does not re-time mouths.

## L4 Cultural adaptation

**Changes:** picture, setting, product and soundtrack: settings, props,
wardrobe, product variant or packaging, and the music bed, as the card and the
user's notes direct. **Stays:** everything not inventoried for change. Prices,
CTA and legal lines with market values are L1 work, not L4.

1. Settings, props and wardrobe follow `settings_notes`,
   `props_wardrobe_notes` and `gestures_and_taboos` from the user. Build new
   location, prop and garment references through the normal element flow and
   swap one class per pass with inspection between passes.
2. Product: acquire the market's own packshot with `product-intake` in the
   localized project; never generate a market SKU's label.
3. Music: a new bed through `seed-audio-prompt`, or a licensed track the
   user supplies, keeping dialogue and effects.
4. Claims: every regulated or measurable claim the new picture or product
   shows needs a fact supported for this market
   (`localize.claims_market_scoped`). A claim substantiated only for the
   source market is cut, rewritten to a claim the market facts support, or
   held until the user supplies market evidence.
5. Disclosure: for a paid deliverable, ask which jurisdictions it targets and
   record one disclosure decision per deliverable, listing its jurisdictions,
   in the localized project's `delivery/`.

**QA:** each changed element against its reference; continuity across shots;
claim map against the market facts; soundtrack continuity; L1 and L2 checks
for text and voice.

## L5 Full transcreation

**Changes:** script, angle, hook and shots. **Stays:** the brand kit, the
product's identity and the market's supported facts.

1. Write a new brief for the market with `brief-intake` from the same brand
   and the market's facts; choose an angle and hook with `seedance-ugc-ads`.
2. The script is written in, or transcreated into, the target language and
   accepted by the user; register, claims and CTA follow the translation
   reference. Check native speech support for the language with
   `seedance-prompt-25-dialogue` and record the result before any shot speaks.
3. Produce it as a new hero ad in the localized project through the normal
   production flow: shot plan, element locks, `seedance-prompt-25` prompts
   with the dialogue layer from `seedance-prompt-25-dialogue`, prompt-review,
   registry, 480p drafts, review and selection.
4. Final-resolution generation and delivery wait for the reviewer sign-off.
   Get the script reviewed before drafts when possible, to avoid paying for
   drafts of lines the reviewer will change.

**QA:** the full production QA of a new ad, plus speech QA in the target
language and the claim map. **Lip-sync verdict:** `native` only when the
take was generated speaking the target language and was checked by eye.

## Upgrading later

A level can rise per element after launch. Keep every earlier localized
version: a new level is a new master version in the same localized project,
with its own render record, and its own reviewer sign-off when it is L3 or
higher.
