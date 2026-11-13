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
Flash's exact imported declaration does not authorize invented duration,
Draft or preview values. Unknown profile requirements block execution, not
creative prompt-only writing. No silently dropped Draft flag.

Native promotion needs the exact registered successful full-source native task,
unchanged prompt/references, matching transport/operation/profile, actual
hash-bound selection and unexpired evidence/source. Version 2 requires
`promotion.support: verified`, `max_age_seconds`, supported `resolutions` and
`extensions.provider_completed_at` on the source. Reinspect actual finals.
Historical plain tasks never become native Draft through a new profile.

## Variant Compiler

`variant_matrix.py register` accepts the same independent provider/revision/
transport options. It derives hook duration from verified `duration.minimum_s`
and preview fields from the frozen profile, not model names. A prompt-only
`plan` leaves generation duration unresolved. Audio/delivery rows get no video
controls. Shared lineage, costs and `max_variants` remain unchanged.
The matrix cannot emit native promotions because it has no per-row selected
task identity; hand off each actual selected task for individual preparation.

## Imported Compatibility

The imported unified `seedance_create_task` and `gen_task_get` names remain
unchanged. Historical separate 2.5/Premium names in retained adapters describe
their original binding only. Current regular 2.5 ordinary 4K declarations do
not imply 4K native promotion; imported promotion and Flash limits remain
distinct. Resolve account, tool and provider exposure through current evidence.
No model activation, generation, default migration or fallback is implicit.
