# Ad Compliance Checklist

Claims, testimonials, brand copy and disclosure for any ad prompt or ad copy:
hooks, scripts, voiceover, supers, captions, and the Seedance, Seedream or Seed
Audio prompt of an ad deliverable. Stack it on the prompt type's own checklist
and apply the universal items in [the index](review-checklists.md#universal--all-prompts)
first.

Source contract: `.agents/contracts/ad-compliance.md` (provenance label only;
the rule catalog named in `rule-provenance.json` owns the rule IDs).

Not legal advice; re-verify. The contract's legal and platform rows are dated
working data; route an unclear case to the user and their counsel.

## Review inputs

Collect, in addition to the usual review input:

- `facts`: the product `facts.json` (schema
  `.agents/contracts/schemas/product-facts.schema.json`) with each fact's
  `status`.
- `brand_kit`: the pinned brand kit (schema
  `.agents/contracts/schemas/brand-kit.schema.json`), or an explicit statement
  that none exists.
- `paid`: whether the deliverable is a paid ad, and its placement.

A missing facts file or brand kit never passes the dependent checks: set
`reviewer_status: incomplete` (or record `fail` with the missing input as
evidence). Do not infer facts from the prompt itself.

## Claims

1. **Claims map to supported facts (`ad.claims_supported`).** List every
   checkable statement in the spoken lines, supers, captions and visual
   direction (results, speed, quantity, ingredients, price, offer, ratings,
   awards, origin). Each one cites a fact with `status: supported`, or a
   current `perishable` fact for price, offer or availability. A claim with no
   fact, or with a `needs-substantiation` fact, is CRITICAL.

2. **Wording stays within the fact (`ad.claims_supported`).** Paraphrase does
   not strengthen the fact: "up to" stays "up to", "helps" does not become
   "cures", a range does not become its best value. Strengthened wording is
   CRITICAL.

3. **Comparatives carry conditions and source (`ad.claims_supported`).**
   "Faster", "longer-lasting", "No. 1", "better than" and similar need a
   supported fact naming the basis, `conditions`, source and
   `substantiation`, and the conditions appear on screen when the claim
   depends on them. Missing conditions is CRITICAL.

4. **Visuals do not imply unsupported results (`ad.claims_supported`).** A
   before-and-after, transformation, counter, rating stars or result shot in
   the visual direction needs the same supported fact as a spoken claim.
   MAJOR, or CRITICAL when it shows a measurable result.

5. **Perishable facts are current (`ad.claims_supported`).** Price, offer and
   availability facts carry `status: perishable` and a retrieval time inside
   the freshness window product intake documents (24 hours by default unless
   the brief records another window); stale or undated ones are MAJOR.

## Testimonials

6. **No fabricated testimonial (`ad.no_fabricated_testimonial`).** A
   first-person endorsement ("I've used it for a month", "it changed my
   routine") from a generated or hired performer is framed as a dramatization
   or demonstration, not as a real customer's history. An invented customer
   name, age, location, review count, star rating or "verified buyer" badge is
   CRITICAL. Pass when the line describes only what the performer does on
   screen, or when the testimonial is supplied, authorized, real and quoted
   verbatim with consent recorded.

## Brand copy

7. **No banned words (`brand.copy_rules`).** No `copy_rules.banned_words`
   entry appears in lines, supers or captions (whole word, case-insensitive,
   simple plurals). Any hit is MAJOR.

8. **Required lines present (`brand.copy_rules`).** Each
   `copy_rules.required_lines` entry whose `when` condition holds appears
   verbatim in the deterministic copy plan. Missing is MAJOR.

9. **Marks and logos stay out of generated media (`brand.copy_rules`,
   `brand.no_generated_logo`).** The generation prompt does not ask the model
   to render a free-standing, corner or end-card logo, trademark mark,
   required line or disclosure label; those are finished in post. An
   on-product mark passes only when a bound acquired product reference carries
   it and the prompt preserves it from that reference. Any requested logo or
   mark not traceable to a reference is CRITICAL. Also check `video.text_free`
   for video prompts.

## Disclosure and placement

10. **Disclosure is a recorded decision (`ad.disclosure_recorded`).** At prompt
    review, pass when no prompt bakes a disclosure label or AI wording into
    generated media; the decision itself is checked before paid delivery.
    A label decided by the agent rather than the user is CRITICAL. For
    internal reels and other non-paid work, record `not_applicable` with the
    reason "internal deliverable, label-free".

11. **Copy plan respects the safe zone (`ad.safe_zone`).** When the prompt or
    copy plan places a CTA, offer, logo or required line, its position is
    inside the target placement's safe zone and sized to read with the sound
    off. A prompt that relies on generated on-screen copy instead is MAJOR.
    `not_applicable` when the prompt places no copy.

## Recording

Add one check per rule ID above when the deliverable is an ad, even if the
caller did not list it as required. Record `fail` for a CRITICAL or MAJOR
finding; a MINOR finding records `pass` with the note in its evidence.
