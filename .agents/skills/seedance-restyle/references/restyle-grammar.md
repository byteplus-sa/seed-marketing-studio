# Restyle Grammar

Focused reference for `seedance-restyle`. Read [the entrypoint](../SKILL.md) for
routing, rules and caller responsibilities.

- [Authority split](#authority-split)
- [Route A: full-frame edit](#route-a-full-frame-edit)
- [Route B: reference](#route-b-reference)
- [A different place, only when requested](#a-different-place-only-when-requested)
- [Style reference images](#style-reference-images)
- [Identity anchors](#identity-anchors)
- [Hypothetical example: product demo to claymation](#hypothetical-example-product-demo-to-claymation)

## Authority split

| Input | Owns | Supplies none of |
| --- | --- | --- |
| `@Video 1` muted master | Subjects and their count, their screen positions, actions, poses, props, the furniture they use, camera path, cuts, timing, and which place the scene is in | Rendering medium, surface texture, grade |
| Optional environment `@Image N` | How the same place looks in the target medium: surface, palette and texture | People, a different place, changed geometry or props the shot lacks |
| Style `@Image N` | Medium, palette, line quality, texture, light quality | Subjects, layout, characters, text |
| Identity anchor `@Image N` | One character's design in the target medium | Pose, background, lighting of the sheet |
| Text | The style block, content inventory, guards | Motion already in `@Video 1` |

Describe content only as an inventory that pins who and what must survive.
Retelling every move conflicts with the video.

**The place stays the same.** Describe the background in the target medium
without naming another location. An environment image can help when selected
for the current request or an observed failure; it is not mandatory. The source
owns layout, moving-camera parallax and timing even when an image is bound.

## Route A: full-frame edit

```text
[Edit Goal]
Edit @Video 1. Redraw the entire frame in <style name>, including <subjects>,
<props> and <background surfaces in the source's place>. Keep every subject,
action, prop, set layout, camera movement and timing from @Video 1.

[Source Video Role]
@Video 1 is the sole editing master. It defines <subject inventory>, <key
props>, <the furniture the subject uses>, <the source camera path>, <their>
poses and actions, and event order.

[Edit Scope]
Redraw <each background element> in <medium>, in the same positions as the
source. <Subject>, <wardrobe
and accessories> and <props> are also rendered in <medium>. Exactly <N> people
appear in the foreground; <background extras>. <Source text surface> shows
<abstract shapes>; no lettering appears anywhere.

[Timeline Inheritance]
Every pose, gesture and contact keeps the timing and screen position of
@Video 1: <beats with times>. <Cadence note for stepped styles.>

[Content to Preserve]
Keep <identity cues>, <props>, <furniture position>, <source camera path> and the
whole performance from @Video 1.

[Style]
<catalog fragment or custom recipe>

[Audio]
Silent output. Sound is added in post.
```

Optional blocks, added before `[Edit Scope]`:

```text
[Environment Reference Role]    (only with a selected environment image)
@Image <N> guides the appearance of <source background surfaces> in <medium>.
Keep the place, geometry and parallax from @Video 1. Use no people or extra
objects from the image. <Name specific conflicting objects only if present.>

[Style Reference Role]          (only with style images)
@Image <N> defines only the visual style: <medium, palette, line, texture,
light quality>. Use none of its subjects, layout or characters.

[Identity Anchors]              (only with anchors)
@Image <N> defines <Name>'s design in <style>: <hair shape, wardrobe colours>.
<Name> is <observable descriptor in @Video 1>.
```

## Route B: reference

Consider when the current request or reviewed output warrants an alternative,
and only with verified reference-route support. Preserve the source duration and
ratio; do not round or adapt the source without current evidence and approval.
This route does not guarantee exact output duration. Renumber optional image
bindings to match the selected inputs.

```text
Create a new video using @Video 1 as the strict visual and temporal reference.
Follow the output dimensions and duration selected in the generation settings.

[Timeline fidelity: highest priority]
Each output moment corresponds to the same moment in @Video 1 at the same
playback speed, from the first frame to the last. Keep <source camera path>, the
screen positions, and every pose, gesture and contact in the same order and at
the same time as in @Video 1.

[Reference content]
@Video 1 defines the subject count, identity cues, wardrobe, props, place,
layout, motion, timing, screen positions and camera. Redraw these in <medium>
rather than retaining photographic surfaces.
- 0:00 to 0:NN: <what happens>
- 0:NN to 0:NN: <what happens>

[World]
<The source's place and its background surfaces> are rendered in <medium>,
in the source layout. The only objects on <surface> are <the source's objects>,
one of each. Add an Environment Reference Role only if an image is selected.

[Characters and props]
<The subject> is a <medium> figure with <hair>, <accessories>, <wardrobe>, and a
hand-modelled face. <Props> are <medium>. Exactly <N> people appear in the
foreground; <background extras>. No lettering appears anywhere.

[Style]
<catalog fragment or custom recipe>

[Audio]
Silent output. Sound is added in post.
```

## A different place, only when requested

When the user explicitly asks for a different location, add this block. Use it
only on request, never to restyle the background of the same scene:

```text
[Location Change]
The background and the overall location both change. <The source's street,
buildings, plant, bench and sky> of @Video 1 are all removed, and no part of the
original <location> remains. In their place is a different location: <the new
place in the target medium, left to right and near to far>. Every part of the
new location is modelled <medium>.
```

## Style reference images

- One to three images, user-owned or approved generated frames, each with
  SHA-256. One image per frame; no collage or mood board.
- Prefer frames whose content differs from the source, so the model reads them
  as style rather than layout.
- No people's faces in style images; when a style image needs a character,
  use an identity anchor instead.
- Never use frames from copyrighted productions or name a studio, artist or
  franchise.
- When the style images and the catalog fragment disagree, the images win;
  shorten the fragment to the medium only.

## Identity anchors

Restyle keeps identity as shapes and colours. For a recurring character that
must look the same across takes:

1. Design the character in the target medium with Seedream and approve it.
2. Register the approved views as a Virtual Portrait subject named for the
   medium (`"Mara (claymation)"`), per the
   [video-to-video inputs contract](../../../contracts/video-to-video-inputs.md).
3. Bind it after the style images and map it to the source subject by
   observable descriptor.

A single-take restyle without recurring characters needs no anchors.

## Hypothetical example: product demo to claymation

Constructed prompt-only example; no generated result or measured improvement
is claimed. Assume an authorized six-second tabletop demo: a hand opens one
plain storage case, places a cable inside and closes it. A shelf and lamp are
visible behind the table. The camera moves slowly right. The brief asks for
claymation throughout and no additional images; saved source audio returns in
post. Timing cues below are supplied events, not measurements.

```text
[Edit Goal]
Edit @Video 1. Redraw the hand, case, cable, table, shelf, lamp and room as
plasticine claymation. Keep the same content, layout, camera path and timing.

[Source Video Role]
@Video 1 is the sole editing master. It defines one hand, one case and one
cable, the set geometry, rightward camera movement and event order.

[Edit Scope]
The entire frame shares a matte clay surface with hand-shaped edges and tool
marks, including the shelf, lamp and room. Keep the case's recognizable shape
and plain surface. No lettering appears; campaign copy is added in post.

[Timeline Inheritance]
The case opens, the cable enters and the lid closes at the source moments.
The slightly stepped cadence keeps hand contacts and the lid closure on time.

[Content to Preserve]
Keep the hand silhouette, product proportions, object count and positions,
background layout, camera parallax and the full source timeline.

[Style]
Plasticine claymation throughout, with visible tool marks, a matte sheen and
slightly stepped motion. Preserve the source lamp's motivated light direction.

[Audio]
Silent output. Sound is added in post.
```

Package: verify the current edit schema and source binding requirements, use
explicit `resolution: "480p"`, boolean `draft: true` and `generate_audio: false`,
resolving schema or transport conflicts without dropping the flag, and preserve the original
source. Do not round or trim its frame count. Review medium coverage, geometry,
contacts and actual timing before muxing the authorized source audio.

If a reviewed draft leaves the shelf photographic, first name that missed
surface in a scoped repair. An environment image can be offered if the user
changes the no-image constraint; inspect and approve it before binding. Neither
the prompt nor an image guarantees a passing result.
