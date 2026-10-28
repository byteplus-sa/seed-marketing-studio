# Framing

Focused reference for `seedance-shot-design`. Read [the entrypoint](../SKILL.md)
for the procedure and the variety rules, and [shot plan
format](shot-plan-format.md) for the `framing` field.

- [Source and status](#source-and-status)
- [What framing decides](#what-framing-decides)
- [Framing types](#framing-types)
- [Choosing a framing](#choosing-a-framing)
- [Framing in the plan](#framing-in-the-plan)
- [Failure shapes](#failure-shapes)

## Source and status

The framing types and their jobs follow the StudioBinder article "Camera
Framing Techniques" (SC Lannom, 2025-05-20, accessed 2026-10-17:
https://www.studiobinder.com/blog/types-of-camera-shot-frames-in-film/). The
mapping to plan fields, the variety rule and the wording notes are this
workspace's own craft heuristics. None is a verified Seedance control: the
model's official vocabulary names shot sizes, `low angle`, `overhead view` and
`first-person view`, and the other terms below are common film language that the
model may or may not honour. Check framing in a 480p draft before relying on it
in a final render.

## What framing decides

Framing is the placement and position of subjects in the frame, not merely where
the camera points. Three decisions carry it:

| Decision | Meaning | Plan field |
| --- | --- | --- |
| Size | Scale controls readable detail and the subject's relationship to the surroundings | `size` |
| Relationship | Several featured subjects in one frame are read as related (romantic, hostile, allied) | `framing`, `featured` |
| Balance | A balanced frame holds elements on both the left and right sides; an unbalanced one reads as tension or isolation | `composition` |

A subject is *featured* when the shot is about it: in focus, in the plane the
viewer reads. A foreground shoulder that only gives perspective is not featured.

## Framing types

`featured` counts the subjects the shot is about. Size is chosen independently of
the framing type.

| Framing | Featured | Job | Use when | Wording notes |
| --- | --- | --- | --- | --- |
| Single | 1 | Isolate one subject's face, body or reaction | A performance beat needs one readable face; any size works | Say that only the subject is in frame |
| Dirty single (over-the-shoulder single) | 1 | Keep a relationship alive while showing one person | A dialogue or confrontation where the listener's presence must stay felt | Name the foreground character's side of frame and keep that character soft and unfeatured |
| Two-shot | 2 | Let a performance play out in one take; show two people as related | Comedy timing, intimacy, a pair reacting together, a release after singles | Name who is screen-left and screen-right |
| Three-shot | 3 | Show a trio without paying for three singles | Adventure, family, any small group | Name the left-to-right order |
| Group shot | 4 or more | Place an ensemble in one space | Establishing a crowd, a family table, a team | Name the grouping and the front or center subject |
| Over-the-shoulder (OTS) | 1 featured, 1 foreground | Orient the scene and connect two characters emotionally; it echoes what one of them sees | Conversation scenes | The foreground shoulder and back of the head sit soft at one side of frame |
| Over-the-hip (OTH) | 1 featured, 1 foreground | Like OTS, but a hip in the foreground; supplied height differences may express a relationship | A beat whose source blocking supports hip-level foreground framing | Describe the foreground hip and hand as soft and the featured subject as sharp; preserve source heights and blocking |
| Point of view (POV) | 0 or more | Show exactly what a character, or an object such as a bullet or a rolling ball, sees | A reveal that the viewer must read as the character's discovery | No part of the looker is visible except hands or limbs they would see |
| Insert | 0 | Direct attention to a detail, or show the viewer something the characters miss (dramatic irony) | A prop, a screen, a hand, a note, an environmental clue | The detail fills the frame; no face unless the beat needs it |

Notes on the types:

- Name screen positions as frame-left and frame-right. The model reads "her
  left" as the character's own side, so a hand or a shoulder is named by both
  anatomy and frame side ("her right hand, frame-left").
- A single can be framed at any size. Only the count of featured subjects makes
  it a single.
- A dirty single technically has two people in the frame. It remains a single
  because only one is featured.
- A looker/POV/reaction sandwich is an optional way to establish viewpoint.
  Source context or a continuous viewpoint can also make ownership readable;
  no extra looker or reaction shot is required.
- An insert is only as useful as how it presents the information. Choose the
  detail, its size and its move for what the viewer must learn, and keep it to
  props and details the canon approves (the prop threshold applies).

## Choosing a framing

Decide the framing from the beat, then confirm the size. These patterns are
optional, not framing-variety or turn quotas. Repeated singles, a held group
shot and intentional stillness are valid when relationships remain readable.

| Beat | Framing | Why |
| --- | --- | --- |
| One character's private reaction | Single, close-up | Isolation and readable cues |
| Confrontation, one side dominates | Dirty single or OTH on the weaker side | The pressure stays in frame |
| Two people playing a joke or an intimate moment | Two-shot, held | The timing needs both in the same take |
| A small group reacts together | Three-shot | Avoids three equal singles |
| A character discovers something | Looker, POV, reaction | The viewer shares the discovery |
| A detail the characters cannot see | Insert | Dramatic irony |
| Orienting a new space with its people | Group shot or wide | Places everyone |

Choose size for the evidence and spatial relationship the beat needs. A small
subject in a wide can carry the scene through isolation or sustained attention;
importance does not require a close-up.

## Framing in the plan

- Every shot in a scene with two or more characters carries a `framing` value
  and its `featured` subjects. Other scenes may omit it.
- Framing type is checked by V10 for readable relationships, not a minimum
  number of changes under V1. A single and a two-shot may share size, angle,
  move and key side when that supports the beat.
- Establish readable POV ownership through source context or optional
  looker/reaction coverage; preserve shot-count and blocking locks.
- Use an unbalanced frame on purpose and record it in `composition`.

## Failure shapes

| Shape | Why it reads as flat or confusing | Repair |
| --- | --- | --- |
| Clean singles hide the needed relationship | Required listener or spatial evidence is missing | Adjust only the obscured beat; a dirty single, OTS or two-shot is an option, not a mandatory mix |
| A two-shot where one subject faces away and is not featured | It reads as a dirty single with a dead foreground | Name the intended framing and soften the foreground subject |
| POV ownership is unreadable | Source context and staging do not establish whose view it is | Clarify the owner and spatial context; consider looker coverage only within source locks |
| Three singles obscure a shared response | The group response needs to be seen together | Consider a three-shot; add a single only for a beat that needs it, without inventing a turn |
| Foreground framing hides a required response | The intended relationship is unreadable | Adjust framing within locks; an OTH does not require inventing a height difference or power imbalance |
| A critical cue is unreadable in the wide | Scale or occlusion hides required evidence | Use readable spatial or body cues within locks; retain a sustained wide when it serves the scene |
