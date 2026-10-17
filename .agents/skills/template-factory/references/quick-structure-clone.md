# Quick structure clone

A light mode for "same structure as this ad, with my product". It keeps the
reference ad's **hook, pacing, scene jobs and CTA flow** and maps them onto a
product card, then writes one Seedance prompt per beat. It skips keyframes,
the storyboard, the per-beat motion breakdown and the reusable recipe.

## When to use it, and when not

| Use quick structure clone | Use the full factory or another route |
| --- | --- |
| One ad for one product, structure is what matters | A reusable template or style recipe is wanted (full factory) |
| Reference ad up to about 30 s and about 12 beats | Longer or denser pins (full factory, windowed analysis) |
| Motion can be re-staged freely | Exact motion grammar must match the reference (full factory) |
| Product, CTA and supported facts are known | A music-led montage whose cut grid must be rebuilt shot by shot (compose with `reference-edit-rebuild`) |

A quick structure clone **is** a reference-ad recreation: the reference's own
opening is the hook. Do not add a hook from the `ugc-ad-modes` hook library on
top of it.

## Inputs

- **Reference ad:** watchable media resolved exactly as pipeline step 1 (pin
  intake), with source URL, SHA-256 and storage scope in `ref_cache.json`.
- **Product card:** the product manifest and its supported facts. When a
  `product-intake` card exists (`element.md` plus `facts.json`), only claims with
  `status: supported` may reach a prompt or a super. Without a card, use only
  facts the user supplied.
- **Product reference:** an official or user-supplied packshot, or an approved
  prop sheet, per [element identification](../../../contracts/element-identification.md).
- **CTA** and destination from the brief; a brand kit when one is pinned.

## Steps

1. **Rights check first.** The reference supplies structure only. Keep analysis
   in de-identify mode; follow
   [competitor or category reference pins](../SKILL.md#competitor-or-category-reference-pins):
   never bind the reference video or its frames, never carry over its
   taglines, typography, trade dress, music or recognizable talent, and give
   original talent distinct wardrobe and colours.
2. **Measure.** Probe picture duration and detect hard cuts with `ffmpeg`.
3. **Beat sheet.** One `seed_understand` call on the reference returns, per
   beat: start and end seconds, the beat's job (hook, problem, demonstration,
   proof, payoff, CTA or another plain label), shot size and camera, pace (cuts
   inside the beat), the role of on-screen text (never its words) and the audio
   role (speech, music, effect, silence). Correct the boundaries against the
   measured cuts and write `templates/<pin-id>/beat-sheet.md` with a table:

   ```markdown
   | Beat | Start–end (s) | Job | Shot and camera | Pace | Text role | Audio role | Product mapping |
   ```

   Record the reference SHA-256 at the top. The beat sheet is this mode's
   `scene-breakdown` evidence; it is not a `VideoBreakdown` and does not go
   through `validate_breakdown.py`.
4. **Map onto the product card.** Fill the "Product mapping" column for every
   beat with a supported fact or a demonstrable action. A beat whose job needs
   evidence the card does not have (a testimonial, a number, a comparison)
   becomes a neutral demonstration or is flagged unresolved; never invent the
   evidence. The CTA beat uses the brief's CTA verbatim.
5. **One Seedance prompt per beat.** Write each beat, or a run of adjacent
   short beats grouped into one natural-duration clip, as a Seedance 2.5
   prompt (compose with `seedance-prompt-25`, and with `ugc-ad-modes` for the
   mode texture). Bind only the product reference and approved elements. Keep
   every clip text-free; supers, prices and the CTA card are finishing layers
   (`html-graphic-render` overlays).
6. **Review and submit.** Every prompt passes `prompt-review` inline. Prepare
   and register each request with `prepare_request.py --register`, submit a
   480p native Draft, review it, then promote the selected Draft. Approval
   follows the project's approval mode.
7. **Assemble** the takes in Studio to the beat sheet's cut times, retiming in
   the edit rather than regenerating, and add overlays and audio in post.

## Stage mapping

| Work | Stage | Exit evidence |
| --- | --- | --- |
| Reference intake, rights check, product card | `brief-development` | reference hash, product card, CTA |
| Beat sheet and product mapping | `scene-breakdown` | `beat-sheet.md` with reference hash and every beat mapped or flagged |
| Product reference | `canon-elements` | approved product reference with hash |
| Storyboard | `storyboard-visual-plan` | skipped with `--reason "quick structure clone"` |
| Per-beat clips | `shot-generation` | reviewed prompts, registered requests, Studio frame per take |
| Assembly, delivery | `assembly-review`, `delivery` | as the production policy requires |

## Still required

Skipping stages never skips gates: rights and de-identification checks,
`prompt-review` for every generation-bound prompt, registry entries before any
paid submission, draft-first review, hash-bound selections, and the Studio
stage-exit checks all apply as in the full factory.
