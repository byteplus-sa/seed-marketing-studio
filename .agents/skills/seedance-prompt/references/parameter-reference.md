# Parameter Reference

Focused reference for `seedance-prompt`. Read [the entrypoint](../SKILL.md) for
mode selection and caller responsibilities.

## Historical Snapshot Scope

The tables below preserve legacy 2.5 guide and MCP binding information, not
current executable guarantees. Limits, token syntax and parameter behavior apply
only when verified for the exact model, operation, transport and schema revision.
They do not transfer to Flash, Premium or other models by name. The caller owns
the execution profile and saved model default; this leaf does not change either.

- [Quick reference card](#quick-reference-card)
- [Draft mode](#draft-mode)
- [Guide disclaimer](#guide-disclaimer)

## Quick reference card

### Model IDs

| Variant | Model ID |
|---|---|
| Seedance 2.5 (historical binding) | `dreamina-seedance-2-5-260628` |
| Seedance 2.0 Standard (legacy) | `dreamina-seedance-2-0-260128` |
| Seedance 2.0 Fast (legacy) | `dreamina-seedance-2-0-fast-260128` |
| Seedance 2.0 Mini (legacy) | `dreamina-seedance-2-0-mini-260615` |

**Historical MCP tools:** `seedance_2_5_create_task`, `seedance_get_task`,
`seedance_list_tasks` / `seedance_cancel_or_delete_task`. These are retained
compatibility names, not aliases for the imported unified server.
Current destination exposure, ordinary generation versus native promotion,
Flash and Premium differences belong to the project
[execution profile](../../../contracts/seedance-execution-profiles.md).
Do not change the selected model or transport to resolve a support gap.

Confirm the selected exact ID and availability on the
[Model list](https://docs.byteplus.com/en/docs/ModelArk/1330310) before execution.
Do not replace an unavailable ID with a newer release automatically.

### Historical 2.5 reference limits

| Material | Max | Recommended |
|---|---|---|
| Images | 30 (each ≤ 4K) | 1–8 subjects |
| Videos | 10 (combined ≤ 30s) | 1–5 subjects, 5–10s each |
| Audio | 10 (combined ≤ 30s) | Only what's directly relevant |
| **Total** | **50** | — |

### Documented 2.5 audio syntax

| Content | Syntax |
|---|---|
| Music | `()` |
| Sound Effects | `<>` |
| Dialogue | `{}` |
| Subtitles | `【】` (provider syntax; workspace footage stays text-free, so subtitles are a post layer) |

### Parameter auto-lock summary

| Task | Aspect Ratio | Duration |
|---|---|---|
| Video editing | Locked to input | Locked to ~input (±0.3s) |
| First/last-frame | Locked to first image | Settable |
| Video extension | Locked to input | Settable |

### Camera techniques

| Technique | What to Specify |
|---|---|
| One-take shot | Subjects, spaces, events in order |
| Dolly zoom | Subject size; bg closer or farther |
| Aerial view | Height, direction, area to reveal |
| FPV | Flight path, speed, turns |
| Bullet time | Action to freeze; orbit direction |
| Handheld camera | Subject; amount of shake |
| Bounce speed ramp | Acceleration/deceleration points; final state |

### Reproducibility
- `seed`: not exposed by the Seedance 2.5 `seedance_2_5_create_task` tool; reproduce a look by reusing the approved prompt and references. Draft promotion reuses the draft's seed.
- `camera_fixed`: not exposed by the historical Seedance 2.5
  `seedance_2_5_create_task` tool (checked 2026-10-06); the 2.0 REST API
  documented it separately. State the requested locked camera and its reason;
  do not infer transport exposure.
- `return_last_frame`: historically used for continuity chaining where supported.

### Output duration
- 4–30s per generation (up from 4–15s in 2.0).
- Historical output resolutions were 480p, 720p, 1080p and separately enabled
  Premium 4K. Current exact operation profiles override executable settings;
  ordinary generation and native promotion limits remain separate.
  A requested 4K gap is unresolved; 2.0/Premium are unselected alternatives
  only after explicit model choice and verification.
- Multi-round extensions up to 180s (beta).

### Execution and review boundaries
- Draft first, then promote the selected draft (see [Draft mode](#draft-mode)).
  Both review modes require explicit `resolution: "480p"` and boolean
  `draft: true` for every new generation on exact legacy native bindings listed
  in the execution-profile contract, without a skip-draft exception.
  Resolve schema or transport conflicts without dropping the native flag.
- Keep resolution in request parameters, separate from prompt text and Studio
  canvas dimensions. Final requests and outputs need fresh request review and QA
  under the workspace production policy.
- Confirm current billing rules on the [Pricing page](https://docs.byteplus.com/en/docs/ModelArk/1544106).

### Exact selection, not a model ladder

Keep the supplied exact model, including a selected 2.0 Standard, Fast or Mini.
A requested 4K target, lower cost or faster iteration does not authorize model
substitution. Missing support remains unresolved; alternatives need explicit
selection and current evidence. An ordinary preview is not native Draft or a
promotion source. No prompt-writing task implies generation or extra trials.

### Languages
- Native language, accent and lip-sync support are exact-model/operation facts.
  Keep missing evidence unresolved rather than inheriting a language list.
- Preserve the supplied language, register and exact words. The caller may
  compose `seedance-prompt-25-dialogue` for delivery and word-scoped repairs;
  a market pack is opt-in, and separate lip-sync audio requires explicit scope.

### Consistency rules
- Follow applicable element locks before authorized execution. Prompt-only
  writing can return missing reference slots without generating assets.
- Storyboards are optional planning and review artifacts. Generate video from canonical Element references (R2V) or text-to-video, with the board's staging written into the prompt.
- Reuse the same reference bundle across every shot in a scene.
- Preserve a written locked-decisions and requested-delta record for every retry.
- Change only one of {prompt wording, reference bundle, motion design} per retry when practical.

### Storyboards are not video inputs

A storyboard grid, board or panel is never bound to a Seedance request
(`references.no_board_binding`): panel numbers and the sketch or watercolour
medium leak into the video, and output-copyright rejections rise. Translate
the approved board into shot lines and bind the canonical character, location
and prop references instead.

| Need | Mode | Reference rule |
|---|---|---|
| Reproduce an exact opening frame | First-frame | A clean full-frame keyframe in the final medium, with no marks |
| Lock start and end states | First + last frame | Two clean keyframes that share one aspect ratio |
| Keep identities while following a planned composition | R2V | Canonical Element references only; the composition is written as text |
| No storyboard at all | R2V or T2V | Canonical Element references (R2V) or text only (T2V) |

These modes are mutually exclusive. Do not combine first/last-frame roles with
an R2V bundle unless the live model explicitly confirms that combination. Record
the chosen mode, ordered reference roles, paths, hashes, selected variants, and
approval states in the shot manifest before submission.

## Draft mode

The historical Seedance 2.5 tool documents a two-step draft (`draft`,
`draft_task_id`; checked 2026-10-17). These steps apply to the exact legacy
native bindings in the workspace execution-profile contract. Confirm the
current tool schema before relying on them; prompt-only work makes no calls.

1. **Draft.** Submit the full request with boolean `draft: true` and explicit
   `resolution: "480p"`. Prompt, references, duration, ratio, `generate_audio` and task type
   are frozen here; make every change before this call.
2. **Review and select** the draft under the project's approval mode: motion,
   shot plan, continuity, speech timing and audio.
3. **Final.** Call again with only `draft_task_id` plus output settings
   (resolution `1080p`, or `4k` on 2.5 Premium, or omitted, `watermark`, `return_last_frame`, expiry,
   priority). The provider reuses the draft's model, prompt, media, duration,
   ratio, seed, audio setting and task type, so those fields must be omitted.
   Omitted output settings take model defaults, not the draft's values, so set
   `watermark: false` again. A draft can be promoted for about seven days.
4. **Re-check the final.** Picture and soundtrack are not byte-identical to the
   draft; inspect playback, dialogue words and audio again before placing it.

Other models use their verified operation profile for native or ordinary
preview controls, or optional absent preview. An ordinary preview is a paid
generation, never a native promotion source. Its separately reviewed and
registered final binds required selected-preview lineage and ordinary-final
intent without disabling the prerequisite. Every final needs fresh picture
and audio inspection. This is not a fallback for exact legacy native bindings.

## Guide disclaimer

The examples in this skill illustrate prompt-writing techniques only. Actual
generation results may vary depending on the input materials, task complexity,
and generation parameters.
