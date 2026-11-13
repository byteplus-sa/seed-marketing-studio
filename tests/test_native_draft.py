import copy
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from datetime import UTC, datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / ".agents/scripts"))
import operation_store
import prepare_request
import validate_request
from test_seedance_capability_profiles import profile


class NativeDraftTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory(prefix="native-draft-test-")
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        (self.root / "project.md").write_text("# Legacy brief\n")
        (self.root / "prompt.md").write_text("A plain ceramic cup turns slowly.\n")
        self.caps = {
            "model": "dreamina-seedance-2-5-260628",
            "source": "offline fixture",
            "verified_at": "2026-10-22T00:00:00Z",
            "operations": ["generate", "edit", "extend", "generate_variations"],
            "parameters": {
                "resolution": {"enum": ["480p", "720p", "1080p"]},
                "draft": {"type": "boolean"},
                "draft_task_id": {"type": "string"},
            },
            "reference_roles": [],
            "max_references": 0,
        }

    def argv(self, params, model=None):
        return [
            "--project",
            str(self.root),
            "--asset",
            "cup_t01",
            "--prompt",
            "prompt.md",
            "--model",
            model or self.caps["model"],
            "--operation",
            "generate",
            "--expected-output",
            "cup_t01.mp4",
            *[
                item
                for key, value in params.items()
                for item in ("--param", f"{key}={json.dumps(value)}")
            ],
        ]

    def request(self, params, model=None):
        return prepare_request.build_request(
            self.root, prepare_request.parser().parse_args(self.argv(params, model))
        )

    def test_new_requests_require_boolean_native_draft_in_both_modes(self):
        for mode in ("default", "strict"):
            (self.root / "project.md").write_text(f"---\nreview_mode: {mode}\n---\n")
            for model in (
                "dreamina-seedance-2-5-260628",
                "seedance-2.5",
                "byteplus-seedance-2-5-premium-261001",
            ):
                self.caps["model"] = model
                for params in (
                    {},
                    {"resolution": "480p"},
                    {"draft": True},
                    {"resolution": "1080p", "draft": True},
                    *[
                        {"resolution": "480p", "draft": value}
                        for value in (False, None, "true", 1)
                    ],
                ):
                    with self.subTest(mode=mode, model=model, params=params):
                        request = self.request(params)
                        before = copy.deepcopy(request)
                        findings = validate_request.validate_request(
                            self.root, request, self.caps
                        )
                        self.assertIn(
                            "seedance.draft_promotion",
                            {finding.rule_id for finding in findings},
                        )
                        self.assertEqual(request, before)

    def test_native_requests_pass_for_each_operation_and_transport(self):
        for mode in ("default", "strict"):
            (self.root / "project.md").write_text(f"---\nreview_mode: {mode}\n---\n")
            for operation in self.caps["operations"]:
                for transport in ("ark-mcp", "arkcli", "curl"):
                    args = prepare_request.parser().parse_args(
                        self.argv({"resolution": "480p", "draft": True})
                    )
                    args.operation = operation
                    args.transport = transport
                    request = prepare_request.build_request(self.root, args)
                    self.assertEqual(
                        validate_request.validate_request(
                            self.root, request, self.caps
                        ),
                        [],
                    )

    def test_schema_mismatch_blocks_without_dropping_native_flag(self):
        request = self.request({"resolution": "480p", "draft": True})
        self.caps["parameters"].pop("draft")
        findings = validate_request.validate_request(self.root, request, self.caps)
        self.assertIn("model.supported_mode", {f.rule_id for f in findings})
        self.assertIn("transport", " ".join(f.message for f in findings))
        self.assertIs(request["params"]["draft"], True)

    def test_other_models_use_plain_480p_without_invented_draft(self):
        for model in ("seedance-2-0-fast", "seedance-2-50", "other-video-model"):
            self.caps["model"] = model
            request = self.request({"resolution": "480p"})
            self.assertEqual(
                validate_request.validate_request(self.root, request, self.caps), []
            )
            self.assertNotIn("draft", request["params"])

    def test_promotion_remains_distinct_from_new_generation(self):
        self.selected_draft()
        request = self.request(
            {"draft_task_id": "selected-task", "resolution": "1080p"}
        )
        self.assertEqual(
            validate_request.validate_request(self.root, request, self.caps), []
        )
        for task_id in ("", " ", None, 1):
            request = self.request({"draft_task_id": task_id, "resolution": "1080p"})
            self.assertIn(
                "seedance.draft_promotion",
                {
                    f.rule_id
                    for f in validate_request.validate_request(
                        self.root, request, self.caps
                    )
                },
            )

    def selected_draft(self):
        draft = self.request({"resolution": "480p", "draft": True})
        draft.update(
            submission_status="terminal",
            provider_task_id="selected-task",
            provider_status="succeeded",
            review_status="approved",
        )
        output = self.root / "cup_t01.mp4"
        output.write_bytes(b"offline video fixture")
        digest = hashlib.sha256(output.read_bytes()).hexdigest()
        review = {
            "schema_version": 1,
            "artifact_path": "cup_t01.mp4",
            "artifact_sha256": digest,
            "status": "pass",
            "inspection_method": "fixture playback",
            "coverage": "whole fixture",
            "checks": [
                {"criterion": "fixture", "status": "pass", "evidence": "fixture"}
            ],
            "observations": ["offline fixture only"],
            "limitations": [],
            "recommendation": "select",
        }
        review_bytes = json.dumps(review).encode()
        (self.root / "review.json").write_bytes(review_bytes)
        decision = {
            "schema_version": 1,
            "decision_id": "select-draft",
            "decision_type": "variant_selection",
            "asset_id": draft["asset_id"],
            "subject_path": "cup_t01.mp4",
            "selected_variant": "cup_t01.mp4",
            "selected_sha256": digest,
            "actor": "agent",
            "approval_mode": "approve_for_me",
            "project_sha256": hashlib.sha256(
                (self.root / "project.md").read_bytes()
            ).hexdigest(),
            "result": "approved",
            "review_path": "review.json",
            "review_sha256": hashlib.sha256(review_bytes).hexdigest(),
            "upstream_sha256": {"prompt.md": draft["prompt_sha256"]},
            "reason": "offline fixture",
            "decided_at": "2026-10-22T00:00:00Z",
        }
        (self.root / "decisions").mkdir(exist_ok=True)
        (self.root / "decisions/select-draft.json").write_text(json.dumps(decision))
        self.write_registry(draft)
        return draft

    def write_registry(self, draft):
        (self.root / "task_ids.json").write_text(
            json.dumps({"schema_version": 1, "tasks": [draft]})
        )

    def profiled_source(self, native=True):
        source = self.selected_draft()
        evidence = profile()
        evidence.update(
            model=source["model"] if native else "fixture-video",
            reference_roles=[], max_references=0,
            parameters={
                "resolution": {"enum": ["360p", "480p", "720p", "1080p"]},
                "draft": {"type": "boolean"},
                "draft_task_id": {"type": "string"},
            },
        )
        if native:
            evidence["preview"] = {
                "support": "verified", "kind": "native_draft",
                "params": {"resolution": "480p", "draft": True},
            }
            evidence["promotion"] = {
                "support": "verified", "max_age_seconds": 3600,
                "resolutions": ["1080p"],
            }
        else:
            source["model"] = evidence["model"]
            source["params"] = {"resolution": "720p"}
        binding = {
            "destination": {key: evidence[key] for key in validate_request.DESTINATION_FIELDS},
            "evidence": evidence,
        }
        source["extensions"]["execution_profile"] = binding
        source["extensions"]["provider_completed_at"] = datetime.now(UTC).isoformat()
        self.rehash(source)
        self.write_registry(source)
        self.caps = evidence
        (self.root / "caps.json").write_text(json.dumps(evidence))
        return source

    def rehash(self, request):
        request["request_sha256"] = validate_request.compute_request_hash(
            (self.root / request["prompt_file"]).read_bytes(),
            request["references"], request["model"], request["operation"], request["params"],
            approval_mode=request.get("approval_mode"),
            project_sha256=request.get("project_sha256"),
            execution_profile=validate_request.execution_profile(request),
        )

    def final_request(self, source):
        args = self.argv({"resolution": "1080p"}, source["model"])
        args += [
            "--capabilities", "caps.json", "--expected-provider", "fixture-provider",
            "--expected-tool-schema-revision", "fixture-r1",
            "--ordinary-final-source", source["operation_id"],
            "--ordinary-final-decision", "decisions/select-draft.json",
        ]
        request = prepare_request.build_request(self.root, prepare_request.parser().parse_args(args))
        request.update(operation_id="cup-final", asset_id="cup-final")
        return request

    def test_profile_omission_on_either_promotion_side_is_rejected(self):
        source = self.profiled_source()
        request = self.request({"draft_task_id": "selected-task", "resolution": "1080p"})
        self.assertTrue(validate_request.prepared_evidence_findings(self.root, request))
        request["extensions"]["execution_profile"] = copy.deepcopy(source["extensions"]["execution_profile"])
        self.rehash(request)
        self.assertEqual(validate_request.validate_request(self.root, request, self.caps), [])
        del source["extensions"]["execution_profile"]
        self.rehash(source)
        self.write_registry(source)
        self.assertTrue(validate_request.prepared_evidence_findings(self.root, request))

    def test_profile_omission_and_operation_mismatch_cannot_begin_submission(self):
        source = self.profiled_source()
        request = self.request({"draft_task_id": "selected-task", "resolution": "1080p"})
        request.update(operation_id="cup-final", asset_id="cup-final")
        for binding, operation in (
            (None, "generate"),
            (source["extensions"]["execution_profile"], "edit"),
        ):
            changed = copy.deepcopy(request)
            changed["operation"] = operation
            if binding is not None:
                changed["extensions"]["execution_profile"] = copy.deepcopy(binding)
            self.rehash(changed)
            with self.assertRaises(ValueError):
                operation_store.prepare_operation(self.root, changed, self.caps, None, [])
            (self.root / "task_ids.json").write_text(json.dumps({"schema_version": 1, "tasks": [source, changed]}))
            before = (self.root / "task_ids.json").read_bytes()
            with self.assertRaises(ValueError):
                operation_store.transition_operation(self.root, "cup-final", "prepared", "submitting")
            self.assertEqual(before, (self.root / "task_ids.json").read_bytes())

    def test_nonlegacy_native_controls_and_selected_source_follow_evidence(self):
        source = self.profiled_source()
        source["model"] = "fixture-native"
        binding = source["extensions"]["execution_profile"]
        binding["destination"]["model"] = source["model"]
        binding["evidence"]["model"] = source["model"]
        binding["evidence"]["preview"]["params"]["resolution"] = "360p"
        source["params"]["resolution"] = "360p"
        self.rehash(source)
        self.write_registry(source)
        request = self.request({"draft_task_id": "selected-task", "resolution": "1080p"}, source["model"])
        request["extensions"]["execution_profile"] = copy.deepcopy(binding)
        self.rehash(request)
        self.assertEqual(validate_request.validate_request(self.root, request, binding["evidence"]), [])
        source["params"] = {"resolution": "360p"}
        self.rehash(source)
        self.write_registry(source)
        self.assertTrue(validate_request.prepared_evidence_findings(self.root, request))

    def test_required_ordinary_preview_allows_separate_final_and_rechecks_selection(self):
        source = self.profiled_source(native=False)
        request = self.final_request(source)
        self.assertEqual(validate_request.validate_request(self.root, request, self.caps), [])
        operation_store.prepare_operation(self.root, request, self.caps, None, [])
        (self.root / "decisions/select-draft.json").unlink()
        before = (self.root / "task_ids.json").read_bytes()
        with self.assertRaisesRegex(ValueError, "ordinary|selection|file"):
            operation_store.transition_operation(self.root, "cup-final", "prepared", "submitting")
        self.assertEqual(before, (self.root / "task_ids.json").read_bytes())

    def test_ordinary_final_requires_unchanged_source_and_current_bound_evidence(self):
        source = self.profiled_source(native=False)
        request = self.final_request(source)
        for field, value in (
            ("params", {"resolution": "1080p", "draft": True}),
            ("prompt_sha256", "0" * 64),
            ("operation", "edit"),
        ):
            changed = copy.deepcopy(request)
            changed[field] = value
            self.rehash(changed)
            self.assertTrue(validate_request.prepared_evidence_findings(self.root, changed), field)
        for field, value in (
            ("request_sha256", "0" * 64),
            ("provider_status", "failed"),
            ("submission_status", "acknowledged"),
        ):
            self.write_registry({**source, field: value})
            self.assertTrue(validate_request.prepared_evidence_findings(self.root, request), field)
        self.write_registry(source)
        binding = request["extensions"]["execution_profile"]
        binding["evidence"]["valid_until"] = (datetime.now(UTC) - timedelta(seconds=1)).isoformat()
        self.rehash(request)
        self.assertTrue(validate_request.prepared_evidence_findings(self.root, request))

    def test_ordinary_final_intent_cannot_disable_prerequisite_or_change_duration(self):
        source = self.profiled_source(native=False)
        binding = source["extensions"]["execution_profile"]
        binding["evidence"]["parameters"]["duration"] = {"type": "number"}
        binding["evidence"]["preview"]["params"]["duration"] = 7.25
        source["params"]["duration"] = 7.25
        self.rehash(source)
        self.write_registry(source)
        (self.root / "caps.json").write_text(json.dumps(self.caps))
        request = self.final_request(source)
        request["params"]["duration"] = 7.25
        self.rehash(request)
        self.assertEqual(validate_request.validate_request(self.root, request, self.caps), [])
        changed = copy.deepcopy(request)
        changed["params"]["duration"] = 8
        self.rehash(changed)
        self.assertTrue(validate_request.prepared_evidence_findings(self.root, changed))
        for intent in (None, {}, {"kind": "ordinary_final"}):
            changed = copy.deepcopy(request)
            if intent is None:
                del changed["extensions"]["execution_profile"]["ordinary_final"]
            else:
                changed["extensions"]["execution_profile"]["ordinary_final"] = intent
            self.rehash(changed)
            self.assertTrue(validate_request.prepared_evidence_findings(self.root, changed))
        (self.root / "decisions/select-draft.json").write_text("{}")
        self.assertTrue(validate_request.prepared_evidence_findings(self.root, request))

    def test_promotion_rejects_unknown_plain_unselected_failed_or_wrong_model_source(
        self,
    ):
        source = self.selected_draft()
        request = self.request(
            {"draft_task_id": "selected-task", "resolution": "1080p"}
        )
        for delta in (
            {"provider_task_id": "different-task"},
            {"params": {"resolution": "480p"}},
            {"params": {"resolution": "720p", "draft": True}},
            {"review_status": "rejected"},
            {"provider_status": "failed"},
            {"submission_status": "acknowledged", "provider_status": "running"},
            {"model": "seedance-2-0"},
        ):
            with self.subTest(delta=delta):
                self.write_registry({**source, **delta})
                self.assertIn(
                    "seedance.draft_promotion",
                    {
                        f.rule_id
                        for f in validate_request.validate_request(
                            self.root, request, self.caps
                        )
                    },
                )
        self.write_registry(source)
        (self.root / "decisions/select-draft.json").unlink()
        self.assertTrue(
            validate_request.validate_request(self.root, request, self.caps)
        )

    def test_promotion_rejects_changed_prompt_references_and_stale_selection(self):
        source = self.selected_draft()
        request = self.request(
            {"draft_task_id": "selected-task", "resolution": "1080p"}
        )
        for field, value in (
            ("prompt_sha256", "0" * 64),
            (
                "references",
                [
                    {
                        "path": "other.png",
                        "sha256": "0" * 64,
                        "role": "reference_image",
                        "binding": "@Image 1",
                        "approval_evidence": {
                            "manifest": "other.md",
                            "field": "selected_variant",
                        },
                    }
                ],
            ),
        ):
            changed = {**request, field: value}
            findings = validate_request.prepared_evidence_findings(self.root, changed)
            self.assertIn("seedance.draft_promotion", {f.rule_id for f in findings})
        (self.root / "cup_t01.mp4").write_bytes(b"changed")
        self.assertTrue(
            validate_request.validate_request(self.root, request, self.caps)
        )
        self.assertEqual(source["params"], {"resolution": "480p", "draft": True})

    def test_promotion_rejects_creative_parameters_even_with_selected_native_source(
        self,
    ):
        self.selected_draft()
        for key, value in (
            ("draft", True),
            ("duration", 8),
            ("ratio", "9:16"),
            ("generate_audio", False),
            ("prompt", "new creative input"),
            ("images", []),
            ("videos", []),
            ("audios", []),
            ("omni_reference_task_type", "edit"),
        ):
            with self.subTest(parameter=key):
                request = self.request(
                    {
                        "draft_task_id": "selected-task",
                        "resolution": "1080p",
                        key: value,
                    }
                )
                self.assertIn(
                    "seedance.draft_promotion",
                    {
                        f.rule_id
                        for f in validate_request.prepared_evidence_findings(
                            self.root, request
                        )
                    },
                )

    def test_promotion_source_is_rechecked_before_submitting(self):
        self.selected_draft()
        request = self.request(
            {"draft_task_id": "selected-task", "resolution": "1080p"}
        )
        request["operation_id"] = "cup-final"
        request["asset_id"] = "cup-final"
        operation_store.prepare_operation(self.root, request, self.caps, None, [])
        (self.root / "decisions/select-draft.json").unlink()
        before = (self.root / "task_ids.json").read_bytes()
        with self.assertRaisesRegex(ValueError, "selection"):
            operation_store.transition_operation(
                self.root, "cup-final", "prepared", "submitting"
            )
        self.assertEqual((self.root / "task_ids.json").read_bytes(), before)

    def test_prepare_cli_smoke_rejects_plain_480p_before_writing(self):
        script = ROOT / ".agents/scripts/prepare_request.py"
        for params, expected in (
            ({"resolution": "480p"}, 1),
            ({"resolution": "480p", "draft": True}, 0),
        ):
            result = subprocess.run(
                [sys.executable, str(script), *self.argv(params), "--write"],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
            if expected:
                self.assertFalse((self.root / "requests").exists())
            else:
                written = json.loads(
                    (self.root / "requests/request_cup_t01.json").read_text()
                )
                self.assertEqual(written["params"], params)
        self.assertFalse((self.root / "task_ids.json").exists())

    def test_registration_and_submission_reject_pending_plain_480p(self):
        request = self.request({"resolution": "480p"})
        with self.assertRaisesRegex(ValueError, "draft"):
            operation_store.prepare_operation(self.root, request, self.caps, None, [])
        path = self.root / "task_ids.json"
        path.write_text(json.dumps({"schema_version": 1, "tasks": [request]}))
        before = path.read_bytes()
        with self.assertRaisesRegex(ValueError, "draft"):
            operation_store.transition_operation(
                self.root, request["operation_id"], "prepared", "submitting"
            )
        self.assertEqual(path.read_bytes(), before)

    def test_adoption_preserves_historical_params_and_hash(self):
        request = self.request({"resolution": "720p"})
        before = copy.deepcopy(request)
        operation_store.adopt_submitted_operation(
            self.root, request, self.caps, None, [], "old-task", "succeeded", True
        )
        record = operation_store.read_registry(self.root / "task_ids.json")["tasks"][0]
        self.assertEqual(record["params"], before["params"])
        self.assertEqual(record["request_sha256"], before["request_sha256"])
        self.assertEqual(record["submission_status"], "terminal")
        self.assertEqual(request, before)


if __name__ == "__main__":
    unittest.main()
