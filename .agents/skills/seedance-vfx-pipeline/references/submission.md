# Submission

Focused reference for `seedance-vfx-pipeline`. Read [the entrypoint](../SKILL.md) for
mode selection and caller responsibilities.

- [Step 3 — Submit via MCP](#step-3--submit-via-mcp)
- [Step 4 — Poll for completion](#step-4--poll-for-completion)

## Step 3 — Submit via MCP

Persist the exact prompt snapshot and prepared operation in `task_ids.json`
before submission. Bind the completed review to its request hash, model, edit
mode, and change contract. Submit through the selected tool only after preflight.
Resolve the selected exact operation first. The example shows the retained native 2.5 edit route. Supply only accepted reference roles and replace placeholders with the selected model and approved inputs.

```json
{
  "input": {
    "tool_name": "seedance_create_task",
    "arguments": {"input": {
      "model": "<selected exact model>",
      "prompt": "<approved prompt>",
      "videos": [{"kind": "url", "url": "<authorized source>", "role": "reference_video"}],
      "omni_reference_task_type": "edit", "resolution": "480p", "draft": true
    }}
  }
}
```

Use the [execution profile](../../../contracts/seedance-execution-profiles.md) for model-specific resolution, duration and edit controls. Keep source ratio and duration locked when required. Ordinary output resolution, native Draft and promotion have separate capability evidence.

- **Audio controls** follow the brief and verified model/operation support.
  Native audio is sufficient unchanged for VFX, Object Swap, Motion Transfer
  and Restyle. Do not require silent input or a post soundtrack, per the
  [video-to-video inputs contract](../../../contracts/video-to-video-inputs.md).
- **`return_last_frame = true`** — returns the last frame image, enabling
  shot chaining for multi-shot VFX sequences.
- **`safety_identifier`** — set to `<project>-<scene>-<shot>` for
  traceability.

Save the Ark job ID from `ark_job_submit` immediately. Poll that job with `ark_job_get`. A completed create result can contain several `tasks[]` entries; store each accepted provider task ID with its registered operation before polling, and record variation-specific errors or ambiguous acceptance separately.

## Step 4 — Poll for completion

Poll known provider IDs together in the foreground, respecting the returned polling interval:

```json
{"input":{"task_ids":["<provider task ID>"],"persist_output":false}}
```

Call `gen_task_get` with that input. Read each task’s status and errors by ID. Once terminal, persist successful outputs by submitting this job and retrieving its result by job ID:

```json
{"input":{"tool_name":"gen_task_get","arguments":{"input":{"task_ids":["<successful provider task ID>"],"persist_output":true}}}}
```

Record per-task outputs and inspect the returned artifacts. On a timeout, recover the known job or task. Retry only retrieval or persistence for an already generated output. A failed, cancelled or expired task requires a separately authorized new operation to generate again.
