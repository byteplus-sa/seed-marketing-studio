---
name: reference-edit-rebuild
description: >-
  Plan a reference video edit rebuilt with the user's own characters, products
  or clothing. Measures the reference into an edit decision list (shot order,
  cut times, beat grid, motion inventory, text), maps up to five assets to
  slots, and splits the rebuild into two layers: a footage layer (varied
  generated shots of the character for people-led formats, animated asset
  layers for product and motion-graphics formats) and a deterministic
  HyperFrames type-and-effects layer. Keeps the cut grid in the assembly, sets
  a version count, reports available costs, and tracks per-segment refinements. Use for
  "make this edit with my product", aura-farming, fashion and product-launch
  formats. Planning only. Not for style recipes (template-factory), recasting
  one clip (seedance-motion-recast), one-element swaps (seedance-object-swap)
  or single shot prompts (seedance-prompt-25).
---

# Reference Edit Rebuild

The reference edit supplies **structure**: shot order, shot length, cut
placement on the music, pacing, transitions, motion design and on-screen text
timing. The user's assets supply **who and what appears**. This skill turns
that split into a Rebuild Plan that a production run can execute segment by
segment and refine without rebuilding the whole edit.

**Two layers, chosen by format.**

- **Footage layer.** For people-led formats (aura farming, fashion, character
  edits) the footage is **many short generated shots of the same character**:
  different setups, angles and light, each filling the frame and moving. One
  static cutout repeated across beats looks cheap; do not build a people-led
  edit from it. For product, logo and motion-graphics formats the footage layer
  is the supplied assets animated as layers (cutouts, crops, screenshots).
- **Type-and-effects layer.** Always code-built in HyperFrames: words on the
  beat, masks, flashes, split screens, insets, grain, timed to the beat grid.
  Deterministic, exact, cheap and editable per segment.

See the [quality bar](references/quality-bar.md) before routing.

It is a prompt-and-plan leaf. It never calls MCP tools, the Ark API or any
generator. Composition hints below are prose for the caller.

## Boundary

| Need | Use |
| --- | --- |
| Same edit structure and motion design, new subjects, per-segment control and targeted fixes | this skill |
| Reusable style or motion recipe from a pin, new content | `template-factory` |
| One clip, keep performance and camera, rebuild cast and world | `seedance-motion-recast` |
| One clip, replace one named element, keep source pixels | `seedance-object-swap` |
| One clip, same cast in a new medium | `seedance-restyle` |
| One static exact graphic | `html-graphic-render` |
| Animated composition, timeline, keyframes, render | `hyperframes` skills (this skill plans, they build) |
| One shot prompt | `seedance-prompt-25` |

Choose this skill when the deliverable is a **multi-shot edit** that must keep
the reference's cut rhythm. If the reference is a single take of 30 s or less
and nothing else needs to be kept, recast or swap is simpler.

## Input contract

- **Reference edit**: an uploaded file or a link to the media file itself. A
  social profile or page URL is not a reference; acquire the file first. Record
  source, SHA-256, duration, fps, aspect ratio and audio presence.
- **Rights record**: owner or permission for the reference footage, its music,
  characters and logos. Unknown rights means grammar-only mode (see rule 1).
- **Assets**: up to five photos or approved elements of characters, products
  or clothing, each with a role and SHA-256. More than five needs an explicit
  user decision recorded as a plan limit.
- **Instructions** (optional): priorities such as a hero product shot, an
  element to keep unchanged, platform, length and version count.

## Output contract

A **Rebuild Plan** returned to the caller:

1. `edl.json` summary: segments with start, end, cut type, shot size, camera,
   subject slots, motion inventory, text events and beat alignment
   ([EDL contract](references/edit-decision-list.md)).
2. Slot map: every visible reference subject mapped to an asset, removed or
   kept as an extra ([slot assignment](references/slot-assignment-and-refinement.md)).
3. Route table: one production route per segment with the reason
   ([segment routing](references/segment-routing.md)).
4. Audio route: keep, replace or silent, with the rights basis.
5. Generation windows, draft resolution, version count and credit estimate.
6. Refinement ledger with hashes, ready for targeted fixes.

## Workflow

1. **Intake and rights.** Record the reference, rights decision and assets.
   Stop on an unusable link or unknown rights that the user will not resolve.
2. **Measure before describing.** Build the EDL from measured cuts (ffmpeg
   scene detection), picture duration and a frame strip, then add model
   analysis per segment. Measured times win over described times.
3. **Beat grid.** When music drives the cuts, extract beat and downbeat times
   and attach each cut to the nearest beat with its offset in milliseconds.
4. **Slot assignment.** Map reference subjects to assets. Every visible
   subject gets a disposition. Prepare each asset as a layer (cutout with
   alpha, crop, safe margins). In generated segments, a person's identity
   image or a video that shows people, bound into Seedance, is a Virtual
   Portrait `asset://` reference per the
   [video-to-video inputs contract](../../contracts/video-to-video-inputs.md).
5. **Motion inventory.** For each segment, list the reference's motion design
   as animatable properties: position, scale, rotation, opacity, mask reveals,
   easing, parallax, type animation, shape and gradient behavior, camera-like
   moves and transitions, with timings. This is the template the layers inherit. Use the
   [edit patterns](references/observed-patterns.md) as vocabulary for common
   treatments and their HyperFrames equivalents.
6. **Route each segment** ([segment routing](references/segment-routing.md)).
   People-led formats default to `fresh_generation` shots (first frame from a
   Seedream still made with the locked identity references, then Seedance
   image-to-video); product and graphics formats default to `motion_layout`.
   Plan a shot list of 5-8 distinct setups, each generated once at natural
   length and cut to many short appearances; the EDL stays the cut authority.
7. **Audio decision.** Keep the reference track only with a recorded rights
   basis; otherwise brief a replacement conformed to the beat grid. Generated
   shots under a music bed run with `generate_audio: false`, because native
   audio leaks music and speech into the cut. A meme or UGC segment that needs
   its own sync sound gets an explicit question (native or post sound) rather
   than a silent default.
8. **Cost reporting.** Layers cost no credits. Generated shots draft at 480p
   first, with native `draft: true` for Seedance 2.5. Report available
   estimates per shot or unknown; estimates never gate generation. Promote
   only selected shots under the project approval mode, respecting existing
   authorization. Estimated and confirmed costs stay separate.
9. **Hand off** the plan. After takes exist, run the assembly check below and
   keep the refinement ledger current.

## Hard rules

1. **Rights first.** Rebuild the reference itself only when the user owns it or
   holds permission, including its music, footage, characters and logos. With
   unknown rights, extract grammar only: de-identify, drop its taglines,
   typography and trade dress, and hand off to `template-factory`.
2. **The cut grid lives in the assembly.** Seedance stretches or shifts dense
   timelines, so cut times are enforced when the takes are trimmed and
   assembled, not promised in a prompt. Never claim a generated clip hits a
   cut time; measure it and retime in the edit.
3. **Match the footage layer to the format.** People-led edits need varied
   generated shots; product and graphics edits use the supplied assets as
   layers. A 0.4 s segment is never its own generation: generate a 4-5 s shot
   per setup and cut it into short appearances at the EDL times. Do not
   compress the plan into an unsupported duration.
4. **Exact graphics are deterministic.** On-screen text, UI, logos, captions
   and number counters are rendered with HTML/HyperFrames. Keep generated
   footage text-free. Never use Seedream or Seedance to reproduce a supplied
   product photo; place the photo itself.
5. **Every visible subject has a disposition**: mapped, removed or kept extra.
   Never write "replace everyone".
6. **Identity from approved elements only.** Real brands, logos and packshots
   come from authorized downloads before any Seedream fallback. A real,
   identifiable person as the target is out of scope; offer an invented
   Virtual Portrait character.
7. **Refine by segment.** A correction invalidates only the segments it
   touches and their dependents. Unchanged takes keep their hashes and are not
   resubmitted.
8. **No duplicate generation.** Never submit the same paid segment twice.
   Report available costs without requiring a cap or spending approval.
9. **Deliver source with the render.** A motion-layout rebuild ships the
   HyperFrames project beside the render so segments stay editable; generated
   takes are flat clips and are labeled as such.

## Assembly check

Before delivery, compare the assembled edit with the EDL:

| Check | Pass condition |
| --- | --- |
| Shot order | Same sequence of segments |
| Cut times | Each cut within 2 frames of the EDL, or a recorded reason |
| Beat alignment | Each music-driven cut within its recorded beat offset |
| Subject slots | Each slot shows its assigned asset, no residual reference subject |
| Text events | Appear at EDL times, exact copy, legible at thumbnail size |
| Audio | Route matches the rights decision, no baked music or speech in silent routes |
| Motion | Easing, travel and timing of each layer match the motion inventory within tolerance |
| Layer fidelity | Supplied photos are unaltered pixels, cut cleanly, no halos or stretched edges |
| Duration, ratio, fps | Match the reference unless the user changed them |

## Design basis

These are workspace design choices, each with its reason:

1. **Measured EDL over described structure.** A claim that a rebuild matches
   the reference's shot order, timing and track is only checkable against
   measured cuts and beats.
2. **Format-based routing.** Product and graphics segments become animated
   layers in a code-built composition; people-led formats use varied generated
   shots, because one static cutout repeated across beats reads as cheap next
   to a reference reel. Type and effects are always code-built.
3. **Refinement ledger by segment and dependency**, so a correction
   regenerates only the affected shots.
4. **Cut grid enforced in assembly**, because Seedance timelines drift.
5. **Five-asset default** as a plan limit that keeps slot mapping reviewable,
   not a model limit.
