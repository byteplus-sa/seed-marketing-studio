# Ad Compliance

This contract covers what an ad may say and show, and what a paid ad must
record before delivery: claims, comparatives, testimonials, synthetic-performer
and platform AI disclosure, and brand copy rules. It applies to ad scripts,
generation prompts, on-screen supers, voiceover and the finished cut of every
ad deliverable. Rights and real-person authorization stay with the
[production policy](production-policy.md) and
[element identification](element-identification.md); this contract adds no
exception to them.

**Not legal advice.** The legal and platform facts below are working data
verified on 2026-10-17 from the listed sources. Laws, platform policies and
their effective dates change: re-verify every row against its source before a
deliverable relies on it, and route an unclear case to the user and their
counsel rather than deciding it.

- [Inputs](#inputs)
- [Claims and comparatives](#claims-and-comparatives)
- [Testimonials and synthetic performers](#testimonials-and-synthetic-performers)
- [Disclosure decision per paid deliverable](#disclosure-decision-per-paid-deliverable)
- [Brand copy rules](#brand-copy-rules)
- [Placement safe zone](#placement-safe-zone)
- [Rights and real people](#rights-and-real-people)
- [Legal and platform reference data](#legal-and-platform-reference-data)
- [Rule IDs](#rule-ids)

## Inputs

| Input | Location | Schema |
| --- | --- | --- |
| Product facts | `elements/<product-id>/facts.json` in the campaign | `.agents/contracts/schemas/product-facts.schema.json` |
| Brand kit | the campaign's pinned brand kit (`brand.json`) | `.agents/contracts/schemas/brand-kit.schema.json` |
| Disclosure decision | `delivery/disclosure_<deliverable-id>.json` in the campaign | [Shape below](#disclosure-decision-per-paid-deliverable) |
| Placement specs and safe zones | [Ad platforms](ad-platforms.md) | `.agents/contracts/schemas/ad-platforms.schema.json` |

A missing input is a gap to report, never a value to invent. Without a facts
file no product claim is `supported`; without a brand kit the copy rules are
unchecked and say so.

## Claims and comparatives

**Every on-screen or spoken claim maps to a `supported` fact** (`ad.claims_supported`).

- A claim is any statement a viewer could check: efficacy, results, speed,
  quantity, ingredients or materials, price, offer, availability, awards,
  ratings, counts of users or reviews, certifications and origin.
- Each claim in a script, prompt, super or voiceover cites the fact it relies
  on. Facts with `status: supported` may reach a deliverable;
  `needs-substantiation` facts stay out until the user supplies evidence.
- Wording stays within the fact. Paraphrase may simplify but never strengthen
  ("helps reduce" does not become "eliminates"; "up to 30%" does not become
  "30%").
- Price, offer and availability facts carry `status: perishable` and their
  retrieval time. They reach a deliverable only when retrieved within the
  freshness window the product card export uses, and are re-checked against
  the source before delivery.
- **Comparatives** ("faster than", "No. 1", "lasts twice as long", "better
  than the leading brand") need a supported fact that names the comparison
  basis, its `conditions` (test, sample, period, market), its source and its
  `substantiation`. The
  conditions appear on screen when the claim depends on them. Without them the
  comparative is cut or rewritten as a non-comparative supported claim.
- Puffery that no viewer could verify ("a morning you'll love") is not a claim,
  but it may not imply a measurable result.
- Generated media must not show a result the facts do not support, such as a
  before-and-after transformation or an on-screen counter.

## Testimonials and synthetic performers

**No fabricated testimonial presented as a real customer** (`ad.no_fabricated_testimonial`).

- A first-person endorsement ("I use it every day", "it fixed my skin") spoken
  or shown by an AI-generated or hired performer is a dramatization unless a
  real, identified customer gave that testimonial. It must not be framed as a
  real customer's experience: no invented name, age, location, review stars,
  "verified buyer" badge or review count.
- Real testimonials are used only from supplied, authorized sources, with the
  speaker's consent recorded, and keep the speaker's wording and typical-result
  context.
- An AI avatar or synthetic performer is allowed as a presenter, demonstrator
  or dramatized user. It is not allowed as evidence that a real person had the
  experience. When the format is creator-style, the script states what the
  performer does on screen rather than claiming a prior personal history.
- Endorsement claims still follow [claims and comparatives](#claims-and-comparatives).

## Disclosure decision per paid deliverable

**Every paid deliverable records a disclosure decision before delivery** (`ad.disclosure_recorded`).

- **The agent asks, never assumes.** Before a paid deliverable leaves the
  workspace, ask the user where it will run (platforms and placements), which
  jurisdictions it targets, and confirm whether it contains a synthetic
  performer or significantly AI-generated imagery or audio. Present the
  applicable rows from the [reference data](#legal-and-platform-reference-data)
  and record the user's decision. `approve_for_me` does not cover this
  decision: it is a legal and platform-policy choice, so the record quotes the
  user's own words.
- **Internal reels stay label-free.** Showreels, review cuts, pitch reels and
  other internal or non-paid deliverables carry no AI label, and this contract
  never adds one. Record nothing for them; if one later becomes a paid ad, it
  becomes a new paid deliverable that needs its own decision.
- **One decision per deliverable.** A change of platform, placement,
  jurisdiction, performer or AI-generated content invalidates the decision.
  Reusing a decision across deliverables requires each deliverable to list it.
- **Label text and placement** come from the brand kit `disclosure` block when
  the user chooses to disclose. A label added in post is deterministic overlay
  copy, never generated into the video. A platform-applied label (for example a
  disclaimer toggle in an ads manager) is recorded as a delivery instruction for
  the person uploading the ad.

Record shape (`delivery/disclosure_<deliverable-id>.json`):

```json
{
  "schema_version": 1,
  "deliverable_id": "glow-serum_hook-question_9x16_15s_v01",
  "paid": true,
  "platforms": ["tiktok-in-feed", "meta-instagram-reels"],
  "jurisdictions": ["US-NY"],
  "synthetic_performer": true,
  "significantly_ai_generated": true,
  "applicable_rules": [
    {"rule": "us-ny-gbl-396-b", "applies": true, "verified_on": "2026-10-17"},
    {"rule": "tiktok-aigc-disclaimer", "applies": true, "verified_on": "2026-10-17"},
    {"rule": "meta-ai-info", "applies": true, "verified_on": "2026-10-17"}
  ],
  "decision": "disclose",
  "label_text": "Features an AI-generated performer",
  "placement": "end-card",
  "platform_settings": ["Enable the AI-generated content disclaimer in the ads manager"],
  "decided_by": "user",
  "user_quote": "Yes, disclose on the end card and turn on the platform labels.",
  "decided_at": "2026-10-17T10:00:00Z"
}
```

`decision` is `disclose`, `not_required` (the user confirmed no rule applies)
or `declined` (the user chose not to disclose where a rule may apply; the agent
states the risk once and records the user's words). `unknown` facts stay
`null` and leave the deliverable blocked.

## Brand copy rules

**Copy obeys the brand kit** (`brand.copy_rules`).

- No banned word from `copy_rules.banned_words` appears in a script, prompt,
  super, caption or voiceover. Match whole words, case-insensitively, including
  simple plurals.
- Each `copy_rules.required_lines` entry appears verbatim whenever its `when`
  condition holds (for example a price shown on screen).
- Trademark marks from `copy_rules.trademark_marks` appear on the first
  on-screen use of the mark in deterministic copy. Generated media never
  renders a logo, mark or required line; those are finished in post.
- Voice `do` and `dont` guidance and `cta_style` verbs shape the copy; a
  departure needs a recorded user instruction.

## Placement safe zone

**CTA, offer, logo and required lines sit inside the placement safe zone** (`ad.safe_zone`).

Safe-zone values come from [ad platforms](ad-platforms.md) for the target
placement and are re-verified there. A placement whose safe zone is
unpublished is laid out against the platform's own template and checked by a
person. Copy is laid out per ratio, never cropped
from another master, and stays readable with the sound off. The
[ad creative check](../skills/ad-creative-check/SKILL.md) records the frame
evidence.

## Rights and real people

Real people, voices, likeness, logos, music, footage and testimonials keep the
existing authorization rules in the [production policy](production-policy.md)
and [element identification](element-identification.md). A creative selection
or disclosure decision never grants rights or consent by inference.

## Legal and platform reference data

All rows: `verified_on: 2026-10-17`. Re-verify before use. Not legal advice.

| ID | Applies to | Summary | Source |
| --- | --- | --- | --- |
| `us-ftc-16-cfr-465` | Reviews and testimonials in US commerce (effective 2024-10-21) | Prohibits fake consumer reviews and testimonials, including ones attributed to people who do not exist or are AI-generated, and misrepresenting a testimonial as a real customer's experience. AI avatars are not banned as such; presenting an avatar's testimonial as a real customer's is. | [FTC rule Q&A](https://www.ftc.gov/business-guidance/resources/consumer-reviews-testimonials-rule-questions-answers); [16 CFR Part 465](https://www.ecfr.gov/current/title-16/chapter-I/subchapter-D/part-465) |
| `us-ny-gbl-396-b` | Ads for New York audiences that knowingly include a synthetic performer (effective 2026-06-09) | Requires a conspicuous disclosure. Audio-only and translation-only uses are exempt. Civil penalties of $1,000 for a first violation and $5,000 for each later one. | [Cooley, 2026-01-29](https://www.cooley.com/news/insight/2026/2026-01-29-new-york-enacts-synthetic-performer-disclosure-law-for-advertisements-including-those-using-generative-ai) |
| `tiktok-aigc-disclaimer` | TikTok ads with fully or significantly AI-generated media | The AI-generated content disclaimer is mandatory; for in-feed ads the label shows for the whole ad. | [TikTok ad disclaimers, Sep 2025](https://ads.tiktok.com/help/article/about-ad-disclaimers-in-tiktok-ads-manager) |
| `meta-ai-info` | Meta ads with images or video created or significantly edited with AI | Meta shows an "AI info" label (in the ad menu or at the top of the ad); detection extends to some outside AI tools through industry signals. Political and social-issue ads must self-disclose digitally created or altered photorealistic media. | [Meta help: AI-generated images in ads](https://www.meta.com/en-gb/help/artificial-intelligence/355108217670024/) |
| `google-ai-label` | Google and YouTube ads | An advertiser AI-content label setting is rolling out from 2026-07-09; election ads need an altered or synthetic content disclosure. | [Google Ads policy](https://support.google.com/adspolicy/answer/17257106) |

## Rule IDs

| Rule ID | Owner | Checked by |
| --- | --- | --- |
| `ad.claims_supported` | this contract | prompt-review ad checklist; ad creative check |
| `ad.no_fabricated_testimonial` | this contract | prompt-review ad checklist |
| `ad.disclosure_recorded` | this contract | ad creative check before paid delivery |
| `brand.copy_rules` | this contract | prompt-review ad checklist; ad creative check |
| `ad.safe_zone` | this contract | ad creative check |
