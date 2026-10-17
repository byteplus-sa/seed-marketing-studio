# Translation and Transcreation

Read [the entrypoint](../SKILL.md). Translation keeps the meaning, claims and
beats of the approved ad; transcreation rewrites a line so it works in the
target language while keeping its job and its facts.

- [Translation sheet](#translation-sheet)
- [Statuses](#statuses)
- [Register](#register)
- [Length](#length)
- [Glossary and locked terms](#glossary-and-locked-terms)
- [CTA and claim wording](#cta-and-claim-wording)
- [Numbers, prices, dates and units](#numbers-prices-dates-and-units)
- [Right-to-left and CJK](#right-to-left-and-cjk)
- [When L1 subtitles are enough](#when-l1-subtitles-are-enough)
- [When to transcreate](#when-to-transcreate)

## Translation sheet

`markets/<market-id>/translation.md` has one row per inventoried spoken line
and on-screen string. The source column is the locked text and is never
edited.

| Column | Content |
| --- | --- |
| `id` | the inventory id, for example `s01_sh010_l02` or `super_03` |
| `kind` | `spoken`, `voice-over`, `caption`, `super`, `cta`, `price`, `offer`, `legal`, `end-card`, `disclosure` |
| `level` | the element's level from the `inventory.md` level table (`L1` to `L5`); it decides which statuses the row may reach |
| `speaker` / `addressee` | spoken rows only |
| `source` | locked source text, verbatim |
| `target` | proposed target text |
| `register` | the register kept for this speaker pair or this brand voice |
| `fit` | spoken: estimated seconds against the measured window; on-screen: characters or rendered width against the layout box |
| `facts` | fact ids from the target market's facts file for every claim, price or offer in the row |
| `terms` | glossary or locked terms in the row |
| `status` | see below |
| `notes` | alternatives, transcreation reasons, unverified items |

Alternatives go in `notes`; the accepted text goes in `target`.

## Statuses

| Status | Meaning | Who sets it |
| --- | --- | --- |
| `draft` | Proposed by the agent or a tool | agent |
| `agent_accepted` | Accepted for production under `approve_for_me`, rows whose `level` is L1 or L2 only, after the agent's semantic check | agent, with a decision record |
| `user_approved` | The user accepted the text in chat | user's words |
| `native_checked` | A native speaker or local reviewer confirmed it | reviewer's or user's words |

Rows below `native_checked` are reported as **unverified** in every handoff
and delivery note. Rows whose `level` is L3, L4 or L5 must be
`native_checked` through the reviewer sign-off before final-resolution
generation and delivery; they never stop at `agent_accepted`. A change
to a row after sign-off returns it to `draft` and makes the sign-off stale.

## Register

- Keep the brand voice from the brand kit (`voice.tone`, `do`, `dont`) and
  express it with the target language's own means, not by copying sentence
  shapes.
- Keep the formality of each speaker pair: presenter to viewer, two friends,
  expert to customer. The target language may mark it with pronouns, verb
  forms or honorifics; record the choice per pair and keep it across lines.
- Do not borrow register, slang or idioms from another market's example. If
  the user named a variety, use it; if not, ask.
- Slang, humor, religious or political references, taboo words and dialect
  choices stay `unverified` until the reviewer confirms them.

## Length

- **Spoken.** A line must fit its measured window at natural speed. Estimate
  the target line's duration and compare it with the source line; a line that
  needs more than about 15 percent more time is rewritten shorter, never sped
  up. One breath per line.
- **Captions.** Reading speed and line limits come from `ad-captions`; fix
  the text rather than silence a warning.
- **On-screen.** Many languages run longer than the source; plan the layout
  box for the target text, then check the render for overflow at the smallest
  ratio. Shorten copy before shrinking type below the readable minimum.

## Glossary and locked terms

- Brand names, product names, trademarks and their marks stay as the brand kit
  records them unless the user supplies a market form.
- Taglines and required lines locked by the brand kit are translated only
  when the brand supplies the target wording; otherwise they stay in the
  source language or are left out, and the user decides.
- Keep a short glossary in `markets/<market-id>/translation.md` (term, target
  form, source of the decision) and reuse it across the campaign's ads.
- Banned words from the brand kit are checked in the target language too; ask
  for target-language banned words when the kit has none.

## CTA and claim wording

- The CTA keeps one action and one destination. Use the brand kit's
  `cta_style` verbs in their accepted target form; the platform's button text
  is set in the ad manager, not burned in.
- A claim stays within its fact in the target market's facts file. Translation
  may simplify but never strengthen: a qualifier such as "up to", "may" or
  "from" survives in the target language, and conditions shown on screen are
  translated with it.
- A claim that the target market's facts do not support is cut, rewritten to
  a supported claim, or held for evidence (`localize.claims_market_scoped`).
  Regulated categories often need market-specific substantiation; route
  unclear cases to the user and their counsel.
- No translated line may turn a dramatization into a testimonial: no invented
  names, ratings or "verified buyer" framing.

## Numbers, prices, dates and units

Write prices with the card's `currency` format from the `price_source` fact;
never convert a currency yourself. Write numbers and dates with
`number_and_date_formats`, and units per `units`; converting a measurement
changes a claim, so the converted value must exist as a fact. Perishable
prices are re-checked within the freshness window before delivery.

## Right-to-left and CJK

- **Right-to-left.** Set `direction: rtl` on the card. Captions get a leading
  right-to-left mark per line in sidecars and `dir="rtl"` in burn-in layers
  (`ad-captions` does both). Check Latin brand names, numbers, prices and
  percent signs inside right-to-left lines in the target player, because
  bidirectional ordering can move them. Mirror a super's layout only when the
  brand kit allows it; logo placement follows the brand kit.
- **CJK and scripts without spaces.** Line breaks fall between characters or
  at supplied word boundaries; Thai and similar scripts need word-boundary
  marks in the locked text. Character limits per line are lower; use the
  per-language limits in `ad-captions`.
- **Fonts.** The brand typeface may not cover the target script. Use a
  licensed fallback with full coverage, record it in the render, and check
  every rendered string for missing glyphs.

## When L1 subtitles are enough

Recommend L1 when most viewers meet the ad with the sound off, the spoken
part is short or not the main carrier of the message, the audience is used to
subtitles, the target language is not natively supported for speech, the
budget is small, or no reviewer is available yet. Recommend L2 or higher when
the voice carries the persuasion (testimonial-style presenter, voice-over-led
demo), when sound-on placements dominate, or when the user asks for spoken
audio. The user decides.

## When to transcreate

Transcreate a line when a literal translation loses its job: wordplay, a hook
built on a phrase, a rhyme, a cultural reference, or a CTA idiom. Inside L1 and
L2 a transcreated line must still fit the same window and the same facts, and
it is shown to the user as an alternative in `notes` before it replaces the
literal version. When the hook, angle or structure itself does not travel,
recommend L5 rather than stretching L1 or L2.
