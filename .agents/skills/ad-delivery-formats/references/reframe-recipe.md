# Reframe Recipe

Read [the entrypoint](../SKILL.md).

## 1. Subject boxes from seed_understand

**Boxes are measured, then checked.** For each shot, sample frames at the cut
start, every 0.5 to 1 s, and at any marked action. Ask `seed_understand` for a
JSON list per frame:

```json
{"time_s": 1.5, "subjects": [
  {"label": "product", "box": [0.42, 0.31, 0.18, 0.40]},
  {"label": "face", "box": [0.20, 0.12, 0.14, 0.18]}
]}
```

`box` is `[x, y, width, height]` as fractions of the source frame. Save the
list as `projects/<campaign>/delivery/<shot-id>_subjects.json` with the source
hash. Open two or three frames and confirm the boxes; a model box can be off by
several percent, so pad each by 3 to 5% of the frame before cropping. Labels
come from the brief's priorities: product and logo first, then face, then hands.

## 2. Crop window math

For a source `Sw×Sh` and target ratio `r = Tw/Th`:

- **Window size:** the largest window of ratio `r` inside the source:
  `Ww = min(Sw, Sh × r)`, `Wh = Ww / r`. A smaller window (punch-in) is allowed
  while `Wh` stays at or above the target height; below that, record the
  softness or regenerate.
- **Window position:** centre it on the union of the padded priority boxes,
  then clamp to the source edges.
- **Safe-zone fit:** map the target safe rectangle (from `safe_zones.py zones`)
  back into source pixels through the window; the union box must sit inside it.
  When it cannot, the shot needs regeneration in the target ratio or a
  different priority (for example product over face) recorded with a reason.

## 3. Studio project per ratio

**`render` always renders the root composition at the project's one canvas
size**, so each delivered ratio is its own Studio project beside the campaign:
`projects/<campaign>-<ratio>/` (for example `projects/<campaign>-4x5`). It is a
full project, not a folder of crops: `studio_project.py` needs a `project.md`
and shot manifests there, and every stage exits through its own ledger.

### 3.1 Files to create

| Path in the ratio project | Content |
| --- | --- |
| `project.md` | A copy of the campaign's `project.md` body with the **same `approval_mode`**, plus a `delivery` block pinning `master_project: projects/<campaign>`, `master_project_md_sha256`, `aspect`, `resolution` and the `placements` this cut serves. The brief is edited only in the campaign; when its hash changes, re-copy and revalidate the ratio project |
| `scenes/scene-NN/<shot-id>/shot.md` | One per master shot, **same shot ids and order** as the master. Frontmatter: `shot_id`, `title`, `aspect` (`"4:5"`), `resolution` (`1080p`), `duration_s`, `route` (`reframe`, `regenerate` or `reuse`), `master_take` (`project`, `path`, `sha256` of the master's selected take) and `takes` (`filename`, `duration_s`) |
| `scenes/scene-NN/<shot-id>/<take file>` | For `reframe` and `reuse`: a **byte copy** of the master's selected take (same filename; its SHA-256 must equal `master_take.sha256`). Not a symlink: take paths must resolve inside the project. For `regenerate`: the native-ratio take, generated and registered in this project |

### 3.2 Commands

From the repository root, with `P=projects/<campaign>-4x5`:

```bash
uv run python .agents/scripts/studio_project.py init $P --aspect 4:5 --resolution 1080p
uv run python .agents/scripts/studio_project.py sync $P \
  --take s01_sh010=<take file> --take s01_sh020=<take file>
uv run python .agents/scripts/studio_project.py status $P
uv run python .agents/scripts/studio_project.py record-selection $P s01_sh010 \
  --decision <decision.json>
```

- `init` fixes the canvas from `--aspect` and `--resolution` (4:5 at 1080p is
  1080x1350, 9:16 is 1080x1920, 1:1 is 1080x1080, 16:9 is 1920x1080); the root
  composition's size is authoritative afterwards.
- `sync --take` builds one frame per shot from the copied take. A shot without
  `--take`, `selected_variant` or `active_take` stays an outline.
- `record-selection` per shot writes the selection through the validated
  writer. The review is recorded in this project for the copied file and
  cites `master_take`; the decision is an agent decision under
  `approve_for_me` or the user's quoted words under `ask_for_approval`, the
  same mode as the campaign. `status` then reports no `selection_pending`.

### 3.3 Crop inside each frame

Open the project in Studio
(`uv run python .agents/scripts/studio_project.py hf $P preview --no-open --json`). Inside each
shot frame, wrap the video in a non-timed crop wrapper and keyframe `x`, `y`
and `scale` with GSAP on that wrapper; keep the `<video>` element and its
`assets/` source, which `status` and `place` read:

- hold the window still while the subject holds;
- move with an eased tween only when the subject leaves the safe rectangle;
- never move during a held product beat or a logo reveal;
- reuse the master's cut points; reframing never retimes a cut.

Overlay compositions (supers, CTA, captions, end card) are separate graphics
compositions in this project's `studio/compositions/`, laid out from the
target safe rectangle in pixels; `status` lists them as informational
`orphan_frame` entries. Audio the master places outside the takes (music bed,
voiceover) is copied from the campaign's locked audio file into this
project's `studio/assets/` and placed at the same start time.

### 3.4 Stage exits and render

The ratio project walks its own ledger with
`studio_project.py stage $P complete <stage-id>`: `brief-development`,
`scene-breakdown` and `canon-elements` pass once `project.md` is valid and
`status` is clean; `storyboard-visual-plan` is skipped with
`stage $P skip storyboard-visual-plan --reason "reframe of the approved master"`;
keep `audio-preparation` unless the cut is silent, so `assembly-review` needs
both a `picture` lock and an `audio` lock on the copied audio. Then:

```bash
uv run python .agents/scripts/studio_project.py check $P
uv run python .agents/scripts/studio_project.py render $P \
  --name <deliverable-id> --quality delivery
```

`<deliverable-id>` follows the variant name plus the placement (see the
[QA contact sheet](qa-contact-sheet.md)). Lock `final_master` on that render
with `record-lock`, then complete `delivery`. A changed master take, brief or
locked audio invalidates the ratio project: re-copy, re-sync and reopen the
affected stage.

## 4. When to stop reframing

- The union of priority boxes is wider than the safe rectangle.
- Two subjects interact across the frame and the crop would drop one.
- The crop window falls below the target height by more than about 15%.

Each is a regeneration case. Regeneration reuses the approved references and
prompt with only the ratio changed, goes through prompt-review and the 480p
draft rule, and is registered before submission.
