# Seedance Execution Profiles

Project-owned destination policy complements the unchanged imported `ark-mcp`
bundle. Imported declarations and configured discovery are not account
activation, current schema exposure or verified execution support. Do not
rewrite imported bindings or resolve conflicts by selecting another model,
transport, resolution or preview route without explicit scope.

## Versioned Evidence

Legacy capability records remain readable. Opt-in `schema_version: 2` covers
one exact operation and requires `profile_id`, `provider`, `model`, `operation`,
`transport`, `tool_schema_revision`, `source`, `verified_at`, `valid_until`,
explicit `support`, self-contained `parameters`, `required_parameters` when
needed, roles/counts, `modality_limits` and `parameter_constraints`.
Support is `verified`, `unsupported` or `unknown`, never an inferred boolean.
Constraints are self-contained JSON Schema clauses; remote references are rejected.
The verified interval must include the current execution time.

Resolve expected provider and schema revision from the intended destination
independently of the evidence being checked. Preparation requires
`--capabilities <project-relative-json> --expected-provider <provider>
--expected-tool-schema-revision <revision>`; existing `--model`, `--operation`
and `--transport` complete the identity. Those expectations are not read from
the capability record. Freeze both destination and evidence in
`extensions.execution_profile`. New profile-bearing hashes include that object;
hash algorithms and historical fixture fields without a profile stay unchanged.

Preparation/registration reject findings before request or registry writes.
The existing submitting transition rechecks the persisted profile's destination,
schema, validity, parameters and preview controls through
`prepared_evidence_findings`. Tampering invalidates the hash. Already-submitted
legacy adoption retains historical parameters and hashes, not permission to
generate again. Ambiguous acceptance reconciles the existing task.

## Preview Mechanics

`workspace_policy.preview_required` is separate from `preview.support`, `kind`
and exact `params`. Kind is `native_draft`, `ordinary`, `none` or `unknown`.
Exact retained bindings are `dreamina-seedance-2-5-260628`, `seedance-2.5`,
`seedance-2-5`, `byteplus-seedance-2-5-premium-261001` and
`dreamina-seedance-2-5-premium-261001`. They retain mandatory boolean native
`draft: true` and explicit `resolution: "480p"` in both review modes.
They are exact compatibility identities, not regex patterns or promises that
an alias is exposed by today's server.

Other models require their verified operation profile for matrix execution.
Ordinary previews use only evidenced controls and are non-promotable.
An evidenced `preview: {support: unsupported, kind: none, params: {}}` is valid
only when `workspace_policy.preview_required` is false and the operation itself
is verified. Unknown preview support is not evidenced absence. Required preview
and exact legacy native policy remain enforced.
Flash's exact imported declaration does not authorize invented duration,
Draft or preview values. Unknown profile requirements block execution, not
creative prompt-only writing. No silently dropped Draft flag.

Native promotion needs the exact registered successful full-source native task,
unchanged prompt/references, matching transport/operation/profile, actual
hash-bound selection and unexpired evidence/source. Version 2 requires
`promotion.support: verified`, `max_age_seconds`, supported `resolutions` and
`extensions.provider_completed_at` on the source. Reinspect actual finals.
Historical plain tasks never become native Draft through a new profile.
Nonlegacy native controls and selected-source eligibility come from the verified
native preview parameters, including boolean `draft: true` and its evidenced
resolution, not an arbitrary 480p predicate. Profile parity applies whenever
either promotion side is profiled; wholly unprofiled history keeps its hash rules.

## Ordinary Finals

Use `prepare_request.py --ordinary-final-source <registered-operation-id>
--ordinary-final-decision <decisions/id.json>` with the same independently
resolved destination and evidence. Preparation freezes an `ordinary_final`
object inside `extensions.execution_profile`, so existing profile-aware hash
consumers bind intent and lineage without changing no-profile hash algorithms:
`kind: ordinary_final`, `source_operation_id`, `source_request_sha256`,
`decision_path` and `decision_sha256`.

The selected source must be one registered successful terminal ordinary preview
with the exact destination/evidence, prompt, references, creative parameters and
current source digest. Validate decision identity, artifact/review/upstream
hashes and project policy. Validate final controls independently against the
operation schema. The final has a new registry identity, review and authorization;
submission rechecks the persisted selection and source. Missing, stale, failed,
unselected or changed sources block before writes. Intent does not disable
`preview_required` and does not authorize changed creative inputs. Neither
ordinary previews nor ordinary finals carry `draft` or `draft_task_id`.

## Variant Compiler

`variant_matrix.py register` accepts the same independent provider/revision/
transport options. It derives hook duration from verified `duration.minimum_s`
and preview fields from the frozen profile, not model names. A prompt-only
`plan` leaves generation duration unresolved. Audio/delivery rows get no video
controls. Resolve evidence and independent destination per executable operation:
video uses `--capabilities`, `--expected-provider`,
`--expected-tool-schema-revision`; audio can use `--audio-capabilities`,
`--audio-expected-provider`, `--audio-expected-tool-schema-revision`.
Audio-only invocations may use the common flags for their audio destination;
mixed operations require separate matching evidence. Each operation's emitted
hash and register commands reuse identical capability, destination and transport
flags. Audio has no video controls or video prerequisite. Delivery has no
provider command. Shared lineage, costs and `max_variants` remain unchanged.
The matrix cannot emit native promotions because it has no per-row selected
task identity; hand off each actual selected task for individual preparation.
For required ordinary previews, `--stage final` needs
`--ordinary-final-selection <row-name>=<source-operation-id>:<decision-path>`
for each executable row. Preserve source creative parameters and references in
the actual final command; compile-time validation never replaces final preflight.
Optional absent-preview operations emit no invented preview parameters.

## Imported Compatibility

The imported unified `seedance_create_task` and `gen_task_get` names remain
unchanged. Historical separate 2.5/Premium names in retained adapters describe
their original binding only. Current regular 2.5 ordinary 4K declarations do
not imply 4K native promotion; imported promotion and Flash limits remain
distinct. Resolve account, tool and provider exposure through current evidence.
No model activation, generation, default migration or fallback is implicit.
