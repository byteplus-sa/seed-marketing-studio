# Long pins, multi-clip takes, and multi-pin batches

Read this when a pin is longer than about 20 s or has more than about 25 beats,
when its video exceeds one reliable clip, or when one run handles several pins.

## Windowed analysis for long pins

A long, dense pin can exceed the host's visual context. Plan bounded local
inspection windows before analysis:

1. Measure picture duration and hard cuts first (step 2).
2. Prefer windows of about 5-8 s aligned to confirmed hard cuts. Use as many
   as the duration requires. If a long continuous shot has no cut, use
   overlapping context around window edges and assign each beat to one owner;
   do not invent a cut at a context boundary.
3. Inspect every window with the same checklist, preferring native/local
   perception and using available understanding tools when needed. With host sub-agent
   support, delegate independent windows to native agents with unique output
   files, read-only media, explicit pin-absolute offsets and image/video input
   requirements. Otherwise work sequentially with saved checkpoints.
4. Merge the windows in order, renumber the beats, and reconcile any element
   names that differ between windows.
5. Record window spans, inspected frame paths, reviewer/runtime, uncertainty
   and completion in `analysis-windows.vNN.json`. The main agent checks gap-free
   coverage and overlap consistency, reconciles boundary action and element IDs,
   and validates the merged breakdown before freezing it.

Resume completed windows from saved evidence after interruption. Native
analysis needs no provider tasks or IDs. For optional provider tools, retain
actual task IDs/results under their contracts and reconcile ambiguous
submissions before retrying. Do not resubmit completed windows.

## Splitting video into clips

Seedance 2.5 bills per output second, so several shorter clips cost about the
same as one long clip covering the same duration. Prefer the split that keeps
each clip reliable:

| Budget per clip | Guidance |
| --- | --- |
| Hard cuts | About 7 shots per clip and 0.8 s per shot are provisional generation heuristics, not provider limits or guaranteed merge/drop thresholds. Preserve the pin's requested rhythm and source timing without automatic retiming or shot removal. Offer assembly for precise cuts or omitted action; return genuine feasibility conflicts rather than changing locks. |
| Duration | Preserve exact fractional pin spans, cuts and audio tails within verified limits; unsupported durations remain unresolved. Rounding, padding or trimming needs explicit scope and separate provenance. |
| Split points | Split only on measured hard cuts. Do not split inside a whip, match cut, or continuous camera move. |

Timing rules at clip boundaries:

- Write every stage timestamp in clip-local time, and list the trim point the
  edit will use.
- A whip, fade, or other transition that must survive the edit must peak or
  finish before the trim point. A whip that crosses into the next clip needs
  both halves: the outgoing clip ends in blur and the incoming clip opens in
  blur that resolves within about 0.3 s.
- Put the final fade to black in post (FFmpeg), not in the prompt, so the trim
  cannot cut it.
- Do not plan native extension to join clips that contain people: extension and
  video inputs with generated or real people are rejected unless the
  identities are `asset://` Virtual Portrait assets. Join independent clips at
  hard cuts, matching first frames and a shared state ledger instead.

Continuity across clips:

- Give each clip a one-line state ledger at the top of its prompt. Say what the
  subject looks like at the clip's start, for example "base layer only; no
  toppings yet". For build or assembly sequences, state each stage explicitly.
- Generated clips can still show later-stage items early. Check this in QA. A
  re-order of whole shots in the edit is often cheaper than a retake. Record the
  edit list and the reason on the scene manifest.

## Continuous audio across clips

Resolve sound ownership from the current brief: requested native sound,
unchanged supplied/post master, purposeful silence, or named mixed layers.
Genre alone never chooses picture-only or a new bed. Separate music generation
and native-audio assembly are opt-in alternatives. Seam reliability is unknown
until playback/listening verifies the actual clips; earlier leakage or tempo
drift is not a family guarantee. Measure the selected master and each seam.
Only authorized edits may loop, crossfade, pad or splice; preserve source tails
and record derivative spans. Rejection requires diagnosis and reconciliation,
not repeated submissions.

## Assembling the clips

- For authorized trims, render exact-length compatible lossless intermediates;
  preserve fractional source spans and audio tails, join with the concat
  demuxer, and encode once. The concat filter needs `setsar=1`.
- Read video-stream durations, not container durations.
- Keep original colours. Choose conform from actual stream metadata:
  pixel format, range, primaries, transfer and matrix, not a model-family name.
  Limited-range BT.709 recipes apply only to matching measured streams;
  unknown or conflicting tags require investigation, not assumed BT.709.
  Apply a look only when authorized and keep untouched masters.

## Multi-pin batches

When one run handles several pins:

- When the host supports sub-agents, give each pin its own native analysis
  sub-agent with explicit media inputs and perception capabilities. Otherwise
  process pins sequentially. Each analysis worker owns only
  `templates/<pin-id>/` and never edits the Studio project (or pre-Studio
  canvas `showcase.json`, `index.html`),
  `project.md`, or `ref_cache.json`.
- Native analysis does not write the provider registry. The main agent owns
  optional tool submissions, uploads and task records to prevent duplicates.
  Every generation registry
  write, by any agent, goes through the lock in
  `.agents/scripts/operation_store.py`: `registry_lock`, `read_registry`,
  `replace_registry`, or `prepare_operation`.
  `.agents/scripts/prepare_request.py --register` does this for you.
- Upload each shared element reference once, and record the object keys in
  `ref_cache.json` from the main agent.
- A pin that is fully deterministic, such as a flat motion graphic rebuilt from
  official cutouts, can go straight to a HyperFrames build from the breakdown's
  measured timing table. Only its music and effects enter prompt review.
