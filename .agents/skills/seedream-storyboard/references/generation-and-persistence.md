# Generation And Persistence

Focused reference for `seedream-storyboard`. Read [the entrypoint](../SKILL.md) for
mode selection and caller responsibilities.

- [10. Generate variants when requested or authorized](#10-generate-variants-when-requested-or-authorized)
- [11. Persist every generated result locally](#11-persist-every-generated-result-locally)
- [Downloading artifacts](#downloading-artifacts)
- [Manifest and metadata](#manifest-and-metadata)

### 10. Generate variants when requested or authorized

For actual image creation:

- use `seedream_generate_image` for a single panel, a single-image grid, or a
  sequence-capable batch of separate images;
- use `seedream_generate_image_variations` for independent alternatives;
- use `seedream_edit_image` for point- or bounding-box-guided corrections;
- set `persist: true`;
- use the lowest suitable size for the requested target; default mode has no
  automatic draft-first pass;
- set `watermark: false` unless the user requires a visible watermark;
- use `prompt_optimization: standard` only when the selected model and tool
  expose it. `fast` needs verified support (documented for Pro, not 5.5);
  latency preference alone does not authorize it.
- Upload and pass the resolved local Element files as ordered reference inputs;
  keep their `@Image N` indices identical in the prompt, request, and manifest.

In default review mode, generate one sample: `p010 v01` for a one-panel board,
`board v01` for a whole-grid asset, or one sample per requested separate panel.
Preserve the requested panel count and layout, including three-panel grids.

Strict mode defaults to three samples of a single panel or whole grid:
`v01`, `v02`, `v03`. For separate images, use three samples for hero and
high-risk panels and one initial sequence for ordinary continuity panels.
Explicit requested count wins in either mode. Samples keep prompt, references
and effective parameters identical except supported seed variation; creative
alternatives change only requested axes with their own provenance. Samples
are candidates, not extra narrative panels.

### 11. Persist every generated result locally

Never rely only on a provider URL. Use durable artifact persistence and save the
actual file under:

```text
projects/<project>/scenes/scene-NN/
```

For individual panels (one-panel board, separate-images mode, or a panel
promoted from a grid):

```text
<scene>_sh<NNN>_p<NNN>_t<NN>_v<NN>.<ext>
```

Example:

```text
s01_sh010_p020_t01_v01.png
prompt_s01_sh010_p020_t01_v01.md
```

For a single-image grid (the whole board in one file):

```text
<scene>_sh<NNN>_board_t<NN>_v<NN>.<ext>
```

Example:

```text
s01_sh010_board_t01_v01.png
prompt_s01_sh010_board_t01_v01.md
```

The `board` token indicates the composite grid image containing all panels;
individual panel prompts are recorded in the same prompt snapshot under their
panel numbers.

### Downloading artifacts

For background jobs, submit through `ark_job_submit` with `persist: true`.
Do not pass `output_path` or `output_dir` through `ark_job_submit`. Record the
job ID, poll `ark_job_get` to a terminal state, and inspect the actual
`ArtifactRef` and `persistence_error` before claiming storage succeeded.
Export the durable artifact separately with `seed_media_export_artifact` to
the intended project file, then verify file existence, bytes, and hash.

Only a client with confirmed native task augmentation may call the tool
directly with an allowed absolute `output_path` (or `output_dir` where its
schema supports it). Inspect terminal task and persistence state, then verify
the reported local file; negotiation is not proof it was written.

If persistence failed but a provider URL exists, report the failure and recover
that result promptly without regenerating. A failed export is an export retry,
not a generation retry. If submission state is unknown, reconcile it before any
resubmission or transport change. Never hand-decode large Base64 tool output,
which may be truncated.

### Manifest and metadata

The prompt snapshot must contain the exact submitted prompt and parameters, with
its SHA-256 in the manifest. A video keyframe is never this panel file or a crop
of it. When a shot needs one, the caller authors a new full-colour, text-free
keyframe prompt from the element references and the panel's staging text, and
saves it under the project keyframe naming convention:

```text
s01_kf01_v01.png
```

Do not overwrite the storyboard source panel.

Record:

- model and model ID;
- ordered reference list and role of each image;
- prompt file and hash;
- size, format, watermark, supported seed/optimization fields, and actual count;
- output path, byte size, and hash;
- provider artifact ID when available;
- generated variants;
- requested delta and acceptance criteria;
- status;
- `source_assets` with each path, role, selected variant, approval state, and
  SHA-256;
- `video_handoff` with eligibility, the staging text to carry into the shot
  prompt, the element references to bind (paths and hashes from
  `source_assets`), `bind_board: false`, and any invalidation reason.

Set a newly generated output to `review`, not `approved`.
Set `video_handoff.eligible: true` only after a mode-authorized panel approval
and after verifying that all recorded source-asset variants and hashes still
match. Eligibility means the staging is approved for translation into prompt
text; the board file itself is never a video input. A changed character,
location, or prop returns the dependent panel to `review`; do not silently
carry stale staging into motion generation.

Use this minimum `source_assets` record for every visible canonical Element:

```yaml
source_assets:
  - element_id: grandma-maria
    element_type: character
    role: character_identity
    path: elements/grandma-maria/ref_01_front.png
    selected_variant: ref_01_front.png
    status: approved
    sha256: "..."
    prompt_token: "@Image 1"
```
