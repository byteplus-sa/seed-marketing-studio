# View layouts

Load this reference when the view plan has a third view, or a three-quarter view
of an object whose flanks differ (vehicles, machines, tools, bags, furniture).
The two-view default and single views are in `SKILL.md`.

## Single row or stacked

Use stacked for vehicles and other long objects where per-view detail matters;
use a single row for compact objects whose views remain readable at a third
of the sheet width. Inspect scale, margins, all identity-critical features and
background continuity in the actual result. These are layout heuristics, not
model-wide measured performance laws. Whichever you pick, swap "object" for
its noun in the blocks below.

## Flanks

Image models mix up left and right and ignore "the opposite side", so
cover both flanks as a turntable turn. Choose the near flank: the one that
carries more identity (the door and handle side, the sidecar side), or the left
when neither does. The front three-quarter shows the front end and the near
flank. The rear three-quarter is the same pose turned half a revolution on a
turntable, so it shows the rear end and the other flank. The side profile shows
the near flank with the front end pointing the same way as in the front view.
Give each in object terms and in frame terms. When the flanks mirror (a taxi),
still name the second flank in Subject ("Right flank: the same brass door
handles and running board as the left flank") and label the side view "Left
flank (side view)" so object terms match Composition:

| Near flank | Front view | Rear view | Side profile |
|---|---|---|---|
| left | from its front left: front end at the left of the frame, left flank on the right | from its rear right: rear end at the left of the frame, right flank on the right | left flank, front end at the left |
| right | from its front right: front end at the right of the frame, right flank on the left | from its rear left: rear end at the right of the frame, left flank on the left | right flank, front end at the right |

## Composition blocks

Three views (side added):

```text
Composition:
Three views side by side in one horizontal row on one continuous background, separated by empty space only: left, the whole object in a front three-quarter view from its front left and slightly above eye level, the front end at the left of the frame and the left flank on the right; center, a full side profile of its left flank, square to the object, the front end at the left, both wheels on that flank fully visible; right, the same object turned half a revolution on a turntable, in a rear three-quarter view from its rear right at the same height, the rear end at the left of the frame and the right flank on the right. All three views drawn at the same scale, the object the same height in each view, each with a clear margin of at least 6% of the sheet on every side; same framing and lighting.
```

Three views, long object:

```text
Composition:
Three views on one continuous background, separated by empty space only. Top row, two views with even spacing: left, the whole object in a front three-quarter view from its front left and slightly above eye level, the front end at the left of the frame and the left flank on the right; right, the same object turned half a revolution on a turntable, in a rear three-quarter view from its rear right at the same height, the rear end at the left of the frame and the right flank on the right. Beneath them, centered: a full side profile of its left flank, square to the object, the front end at the left, both wheels on that flank fully visible. All three views drawn at the same scale, the object the same height in each view, with a clear margin of at least 6% of the sheet to the canvas edge and to the next view; same lighting.
```

For a right near flank, mirror the frame terms using the table above.

## QA notes

Check each flank by a landmark, preferring a feature that does not mirror (the
front fender, the grille end) over door handles. For a mirror-symmetric object,
decide each flank from which end points where in the frame and say so. The table
is a request, and the model can still render both three-quarter views from the
same corner.

Measure scale as height including roof furniture such as a lamp box, and
cross-check using stable landmarks such as wheel size. A strict colour mask can
miss pale or transparent details; visually inspect the complete silhouette.
Account for perspective rather than imposing a universal numerical tolerance.

## Historical sample evidence

One car, three runs, not a family-wide benchmark: the turntable wording put the rear
three-quarter on the opposite flank in both later runs (the earlier "opposite
side" wording did not), and one continuous background removed the faint
rectangles of the earlier panel wording. Margins landed at 55-80% of the 6%
request. Width targets were not needed: scale was already within 8.3% without
them. Single-row height spread was 3.3% versus 6.6-8.3% stacked, with margins
4.1% versus 3.5%, but per-view pixel area was roughly 0.4-0.6 of stacked.
The row dropped one door per flank and introduced a gradient/shadow band;
stacked kept both doors and a flat background. A strict colour mask understated
height by up to 18% after missing a pale roof lamp.

These observations explain the earlier heuristic, not guaranteed behavior for
another object, model, prompt or transport. Evaluate the new candidate against
its own view plan and identity requirements.
