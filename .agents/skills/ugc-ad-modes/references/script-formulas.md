# Script formulas

Read one formula when a brief names a structure (PAS, AIDA, "three reasons")
or asks for one to fit a placement length. Formulas are **starting
allocations**, not rules; a user-requested structure wins, and a hook from the
[hook library](hooks.md) fills the opening beat.

## Rules for every formula

- **Timings are allocations, not edit points.** Seedance tends to stretch dense
  beat timelines by about 0.5–1.2 s; leave slack and retime in the edit.
- **Word budget:** about 2.2 spoken words per second for native speech, with the
  CTA line ending at least 0.4 s before the clip end: roughly 12 words in 6 s,
  25–30 in 15 s and 60 across 30 s. A voiceover added in post can run faster.
- **30 s is several generations.** Build it from natural-duration clips of
  about 5–10 s, split on beat boundaries, then assemble.
- **Every beat has one visible event** and every claim stays within supplied,
  supported facts. Proof beats need real evidence; testimonial beats need
  approved testimony or a clearly fictional dramatization.
- **On-screen text, brand cards and the CTA card are finishing layers.**
- **Placement anchors** (verified on 2026-10-17; re-verify before use): a
  YouTube bumper is at most 6 s, and a skippable in-stream ad can be skipped
  at 5 s, so brand and hook land before 5 s
  ([Google Ads Help 2375464](https://support.google.com/google-ads/answer/2375464)).
  TikTok advises hooking viewers in the first 3 s
  ([Video Advertising Guide](https://ads.tiktok.com/business/en/guides/video-advertising-guide)).
- **Evidence labels:** `official` means a platform publishes the structure;
  `practitioner` means vendor or creator guidance with low confidence. No
  formula has an official performance ranking; compare variants within one
  account.

Each table gives start–end seconds per beat. "Not recommended" means the
formula's beats cannot each show a visible event in that length; use
Hook → Proposition → CTA instead.

### Hook, Proposition, CTA <!-- id: formula-hook-proposition-cta -->
- **Evidence:** official (TikTok creative guidance: hook, selling points, clear CTA).
- **Use when:** any length, and always for a 6 s bumper.

| Beat | 6 s bumper | 15 s | 30 s |
| --- | --- | --- | --- |
| Hook | 0–2 | 0–3 | 0–3 |
| Proposition (one to three supported selling points) | 2–4.5 | 3–11 | 3–24 |
| CTA | 4.5–5.6 | 11–14.6 | 24–29.6 |

### Direct-Response Six Beat <!-- id: formula-dr-six-beat -->
- **Evidence:** practitioner. The source figure of about 60 words in under
  20 s exceeds the native-speech budget; trim to the budget or use voiceover.
- **Use when:** a product solves a clear problem and proof is supplied.

| Beat | 6 s bumper | 15 s | 30 s |
| --- | --- | --- | --- |
| Hook | not recommended | 0–2 | 0–3 |
| Problem | not recommended | 2–4 | 3–7 |
| Solution (product enters) | not recommended | 4–7 | 7–13 |
| Value (supported feature in use) | not recommended | 7–10 | 13–19 |
| Proof (supplied evidence only) | not recommended | 10–12.5 | 19–25 |
| CTA | not recommended | 12.5–14.6 | 25–29.6 |

### Problem, Agitate, Solve <!-- id: formula-pas -->
- **Evidence:** practitioner.
- **Use when:** the problem is concrete and recognizable. Agitation stays
  truthful; no exaggerated harm, fear or health claims.

| Beat | 6 s bumper | 15 s | 30 s |
| --- | --- | --- | --- |
| Problem | 0–2 | 0–3 | 0–4 |
| Agitate | merged into Problem | 3–6 | 4–10 |
| Solve (supported demonstration) | 2–4.5 | 6–12 | 10–24 |
| CTA | 4.5–5.6 | 12–14.6 | 24–29.6 |

### Attention, Interest, Desire, Action <!-- id: formula-aida -->
- **Evidence:** practitioner.
- **Use when:** discovery of a product the audience does not yet know.

| Beat | 6 s bumper | 15 s | 30 s |
| --- | --- | --- | --- |
| Attention (hook) | 0–2 | 0–2.5 | 0–3 |
| Interest (what it is) | 2–3.5 | 2.5–7 | 3–12 |
| Desire (supported benefit shown) | 3.5–4.5 | 7–12 | 12–24 |
| Action (CTA) | 4.5–5.6 | 12–14.6 | 24–29.6 |

### Testimonial <!-- id: formula-testimonial -->
- **Evidence:** practitioner; testimonial law applies (FTC 16 CFR 465 bans fake
  and AI-generated reviews from people who do not exist; see the
  [FTC Q&A](https://www.ftc.gov/business-guidance/resources/consumer-reviews-testimonials-rule-questions-answers)).
- **Use when:** a real, approved testimonial is supplied with its scope, or the
  dramatization is clearly fictional to the viewer. Otherwise use Demonstration.

| Beat | 6 s bumper | 15 s | 30 s |
| --- | --- | --- | --- |
| Quote hook (approved words) | not recommended | 0–3 | 0–4 |
| Context (who and when, as supplied) | not recommended | 3–6 | 4–10 |
| Experience with the product on screen | not recommended | 6–12 | 10–24 |
| CTA | not recommended | 12–14.6 | 24–29.6 |

### Failed Alternative <!-- id: formula-failed-alternative -->
- **Evidence:** practitioner.
- **Use when:** the product replaces a common workaround. Keep the alternative
  generic; never show or name an identifiable competitor without authorized,
  substantiated comparison.

| Beat | 6 s bumper | 15 s | 30 s |
| --- | --- | --- | --- |
| Problem | not recommended | 0–3 | 0–4 |
| Failed alternative | not recommended | 3–6 | 4–10 |
| Product | not recommended | 6–10 | 10–18 |
| Result (observable, supported) | not recommended | 10–12.5 | 18–25 |
| CTA | not recommended | 12.5–14.6 | 25–29.6 |

### Three Reasons <!-- id: formula-three-reasons -->
- **Evidence:** practitioner. Pairs with the List Promise hook.
- **Use when:** three distinct supported features exist; use fewer reasons
  rather than inventing one.

| Beat | 6 s bumper | 15 s | 30 s |
| --- | --- | --- | --- |
| Hook (count promise) | not recommended | 0–2 | 0–3 |
| Reason one | not recommended | 2–5.5 | 3–10 |
| Reason two | not recommended | 5.5–9 | 10–17 |
| Reason three | not recommended | 9–12.5 | 17–24 |
| CTA | not recommended | 12.5–14.6 | 24–29.6 |

### Us Versus Them <!-- id: formula-us-vs-them -->
- **Evidence:** practitioner; comparison claims must be substantiated.
- **Use when:** a supplied, substantiated comparison exists. "Them" is a
  generic usual way unless an authorized comparison names the other product.

| Beat | 6 s bumper | 15 s | 30 s |
| --- | --- | --- | --- |
| Hook | not recommended | 0–2 | 0–3 |
| The usual way | not recommended | 2–6 | 3–10 |
| The product's way | not recommended | 6–11 | 10–21 |
| Proof of the difference (supplied) | not recommended | 11–13 | 21–26 |
| CTA | not recommended | 13–14.6 | 26–29.6 |
