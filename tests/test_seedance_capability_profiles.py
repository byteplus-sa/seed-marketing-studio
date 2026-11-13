import copy
import hashlib
import json
import os
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
import variant_matrix


def profile():
    now = datetime.now(UTC)
    return {
        "schema_version": 2,
        "profile_id": "synthetic-video-r1",
        "provider": "fixture-provider",
        "model": "fixture-video",
        "operation": "generate",
        "transport": "ark-mcp",
        "tool_schema_revision": "fixture-r1",
        "source": "synthetic contract, not live support",
        "verified_at": now.isoformat(),
        "valid_until": (now + timedelta(hours=1)).isoformat(),
        "support": "verified",
        "operations": ["generate"],
        "parameters": {
            "resolution": {"enum": ["720p", "1080p"]},
            "duration": {"type": "number", "minimum": 2.5},
        },
        "reference_roles": ["reference_image"],
        "max_references": 2,
        "modality_limits": {"Image": 1, "Video": 0, "Audio": 0},
        "parameter_constraints": [],
        "preview": {
            "support": "verified",
            "kind": "ordinary",
            "params": {"resolution": "720p"},
        },
        "workspace_policy": {"preview_required": True},
        "duration": {"support": "verified", "minimum_s": 2.5},
        "promotion": {"support": "unsupported"},
    }


class CapabilityProfileTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory(prefix="marketing-profile-")
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        (self.root / "project.md").write_text("# Synthetic brief\n")
        (self.root / "prompt.md").write_text("A cup turns.\n")
        self.evidence = profile()
        (self.root / "caps.json").write_text(json.dumps(self.evidence))

    def args(self):
        return [
            "--project", str(self.root), "--asset", "cup_t01",
            "--prompt", "prompt.md", "--model", "fixture-video",
            "--operation", "generate", "--expected-output", "cup.mp4",
            "--capabilities", "caps.json",
            "--expected-provider", "fixture-provider",
            "--expected-tool-schema-revision", "fixture-r1",
            "--param", "resolution=720p",
        ]

    def request(self):
        return prepare_request.build_request(
            self.root, prepare_request.parser().parse_args(self.args())
        )

    def test_exact_legacy_policy_excludes_flash_and_near_matches(self):
        for model in (
            "dreamina-seedance-2-5-flash-261115",
            "dreamina-seedance-2-5-unknown",
            "x-seedance-2-5-premium-y",
        ):
            self.assertEqual(validate_request.native_draft_findings(
                {"model": model, "params": {"resolution": "480p"}}
            ), [])

    def test_valid_profile_is_persisted_and_hash_bound(self):
        request = self.request()
        self.assertEqual(validate_request.validate_request(
            self.root, request, self.evidence
        ), [])
        changed = copy.deepcopy(request)
        changed["extensions"]["execution_profile"]["destination"]["provider"] = "other"
        findings = validate_request.prepared_evidence_findings(self.root, changed)
        self.assertIn("request.current_hash", {f.rule_id for f in findings})

    def test_optional_absent_preview_does_not_negate_verified_execution(self):
        self.evidence["preview"] = {"support": "unsupported", "kind": "none", "params": {}}
        self.evidence["workspace_policy"]["preview_required"] = False
        (self.root / "caps.json").write_text(json.dumps(self.evidence))
        request = self.request()
        self.assertEqual(validate_request.validate_request(self.root, request, self.evidence), [])
        for support in ("unsupported", "unknown"):
            evidence = copy.deepcopy(self.evidence)
            evidence["workspace_policy"]["preview_required"] = True
            evidence["preview"]["support"] = support
            request["extensions"]["execution_profile"]["evidence"] = evidence
            self.assertTrue(validate_request.capability_findings(request, evidence))

    def test_each_destination_dimension_is_independently_checked(self):
        request = self.request()
        for field in ("model", "provider", "operation", "transport", "tool_schema_revision"):
            evidence = copy.deepcopy(self.evidence)
            evidence[field] = "wrong"
            self.assertTrue(validate_request.capability_findings(request, evidence), field)

    def test_absent_expectation_cannot_self_certify(self):
        request = self.request()
        del request["extensions"]["execution_profile"]["destination"]["provider"]
        self.assertTrue(validate_request.capability_findings(request, self.evidence))

    def test_expired_unknown_and_remote_profiles_fail(self):
        request = self.request()
        for field, value in (
            ("valid_until", "2000-01-01T00:00:00Z"),
            ("support", "unknown"),
            ("parameters", {"resolution": {"$ref": "https://invalid.example/schema"}}),
            ("preview", {"support": "unknown", "kind": "ordinary", "params": {}}),
        ):
            evidence = copy.deepcopy(self.evidence)
            evidence[field] = value
            self.assertTrue(validate_request.capability_findings(request, evidence), field)

    def test_modality_and_conditional_constraints_apply(self):
        request = self.request()
        request["references"] = [
            {"role": "reference_image", "binding": f"@Image {number}"}
            for number in (1, 2)
        ]
        self.assertTrue(validate_request.capability_findings(request, self.evidence))
        request["references"] = []
        evidence = copy.deepcopy(self.evidence)
        evidence["parameter_constraints"] = [{"not": {"required": ["resolution"]}}]
        self.assertTrue(validate_request.capability_findings(request, evidence))

    def test_preparation_cli_mismatch_writes_nothing(self):
        argv = self.args()
        argv[argv.index("fixture-provider")] = "wrong-provider"
        before = {p.relative_to(self.root): p.read_bytes() for p in self.root.rglob("*") if p.is_file()}
        result = subprocess.run(
            [sys.executable, "-B", str(ROOT / ".agents/scripts/prepare_request.py"),
             *argv, "--write", "--register"],
            capture_output=True, text=True, check=False,
        )
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertFalse(json.loads(result.stdout)["ok"])
        self.assertEqual(before, {p.relative_to(self.root): p.read_bytes() for p in self.root.rglob("*") if p.is_file()})

    def test_submitting_rechecks_persisted_expiry_without_registry_write(self):
        request = self.request()
        expired = request["extensions"]["execution_profile"]
        expired["evidence"]["valid_until"] = "2000-01-01T00:00:00Z"
        request["request_sha256"] = validate_request.compute_request_hash(
            b"A cup turns.\n", [], request["model"], request["operation"], request["params"],
            execution_profile=expired,
        )
        (self.root / "task_ids.json").write_text(json.dumps({
            "schema_version": 1, "tasks": [request],
        }))
        before = (self.root / "task_ids.json").read_bytes()
        with self.assertRaises(ValueError):
            operation_store.transition_operation(
                self.root, request["operation_id"], "prepared", "submitting"
            )
        self.assertEqual(before, (self.root / "task_ids.json").read_bytes())

    def test_profile_drives_matrix_duration_and_preview_not_model_name(self):
        options = variant_matrix.parser().parse_args([
            "register", "matrix.json", "--project", str(self.root),
            "--video-model", "fixture-video", "--video-operation", "generate",
        ])
        options.stage = "draft"
        options.execution_profile = {
            "destination": {key: self.evidence[key] for key in (
                "model", "provider", "operation", "transport", "tool_schema_revision"
            )},
            "evidence": self.evidence,
        }
        self.assertEqual(variant_matrix.step_params("hook-opening", options),
                         ["resolution=720p", "duration=2.5"])
        self.assertEqual(variant_matrix.step_params("language-dub", options), [])
        self.assertEqual(variant_matrix.step_params("ratio-reframe", options), [])

    def test_profile_native_final_without_selected_task_is_blocked(self):
        options = variant_matrix.parser().parse_args([
            "register", "matrix.json", "--project", str(self.root),
            "--video-model", "fixture-video", "--video-operation", "generate",
            "--capabilities", "caps.json", "--stage", "final",
            "--final-resolution", "1080p",
        ])
        options.execution_profile = {
            "evidence": {**self.evidence, "preview": {
                "support": "verified", "kind": "native_draft",
                "params": {"resolution": "480p", "draft": True},
            }},
        }
        rows = [{"name": "v", "role": "variant", "steps": [{
            "owner": "v", "route": "hook-opening", "provider_operation": True,
        }]}]
        self.assertIn("seedance.draft_promotion", {
            f.rule_id for f in variant_matrix.option_findings(rows, options)
        })

    def test_delivery_routes_bypass_video_options_and_profiles(self):
        options = variant_matrix.parser().parse_args([
            "register", "matrix.json", "--project", str(self.root), "--stage", "final",
        ])
        for route in variant_matrix.DELIVERY_ROUTES:
            rows = [{"name": "v", "role": "variant", "steps": [{
                "owner": "v", "route": route, "provider_operation": True,
            }]}]
            self.assertEqual(variant_matrix.matrix_profile_findings(rows, options), [], route)
            self.assertEqual(variant_matrix.option_findings(rows, options), [], route)
            self.assertEqual(variant_matrix.step_params(route, options), [], route)

    def test_audio_routes_require_audio_options_but_not_video_profiles(self):
        audio = profile()
        audio.update(
            model="fixture-audio", operation="voice", operations=["voice"],
            parameters={}, reference_roles=[], max_references=0,
            preview={"support": "unsupported", "kind": "none", "params": {}},
            workspace_policy={"preview_required": False},
        )
        (self.root / "audio.json").write_text(json.dumps(audio))
        options = variant_matrix.parser().parse_args([
            "register", "matrix.json", "--project", str(self.root),
            "--audio-model", "fixture-audio", "--audio-operation", "voice",
            "--capabilities", "audio.json", "--expected-provider", "fixture-provider",
            "--expected-tool-schema-revision", "fixture-r1",
        ])
        rows = [{"name": "v", "role": "variant", "steps": [{
            "owner": "v", "route": "language-dub", "provider_operation": True,
        }]}]
        self.assertEqual(variant_matrix.matrix_profile_findings(rows, options), [])
        self.assertEqual(variant_matrix.option_findings(rows, options), [])
        self.assertEqual(variant_matrix.step_params("language-dub", options), [])

    def test_mixed_delivery_and_video_still_require_video_profile(self):
        options = variant_matrix.parser().parse_args([
            "register", "matrix.json", "--project", str(self.root),
        ])
        rows = [{"name": "v", "role": "variant", "steps": [
            {"owner": "v", "route": route, "provider_operation": True}
            for route in ("ratio-reframe", "hook-opening")
        ]}]
        self.assertTrue(variant_matrix.matrix_profile_findings(rows, options))
        self.assertIn("register.placeholder", {
            finding.rule_id for finding in variant_matrix.option_findings(rows, options)
        })

    def test_matrix_blocks_unknown_duration_and_unsupported_preview_parameters(self):
        options = variant_matrix.parser().parse_args([
            "register", "matrix.json", "--project", str(self.root),
            "--video-model", "fixture-video", "--video-operation", "generate",
            "--capabilities", "caps.json", "--expected-provider", "fixture-provider",
            "--expected-tool-schema-revision", "fixture-r1", "--stage", "draft",
        ])
        rows = [{"name": "v", "role": "variant", "steps": [{
            "owner": "v", "route": "hook-opening", "provider_operation": True,
        }]}]
        for field, value in (
            ("duration", {"support": "unknown"}),
            ("parameters", {"resolution": {"enum": ["1080p"]}}),
        ):
            evidence = {**self.evidence, field: value}
            (self.root / "caps.json").write_text(json.dumps(evidence))
            self.assertTrue(variant_matrix.matrix_profile_findings(rows, options), field)


class OrdinaryFinalIdentityTests(unittest.TestCase):
    setUp = CapabilityProfileTests.setUp
    args = CapabilityProfileTests.args

    def cli(self, script, arguments):
        command = [sys.executable, "-B", str(ROOT / script), *arguments]
        result = subprocess.run(
            command, capture_output=True, text=True, check=False, timeout=30,
        )
        if log_path := os.environ.get("MKT_RR01_COMMAND_LOG"):
            with Path(log_path).open("a") as handle:
                handle.write(json.dumps({
                    "command": command, "returncode": result.returncode,
                    "stdout": result.stdout, "stderr": result.stderr,
                }) + "\n")
        self.assertEqual(result.stderr, "", result.stderr)
        return result.returncode, json.loads(result.stdout)

    def snapshot(self):
        return {
            path.relative_to(self.root).as_posix(): path.read_bytes() if path.is_file() else None
            for path in self.root.rglob("*")
        }

    def record(self, request, relative, rules=("model.supported_mode",)):
        input_path = self.root / "review-input.json"
        input_path.write_text(json.dumps({
            "schema_version": 1, "request_sha256": request["request_sha256"],
            "reviewer_status": "complete", "checks": [
                {"rule_id": rule, "status": "pass", "evidence": "Synthetic offline contract only"}
                for rule in rules
            ],
        }))
        code, recorded = self.cli(".agents/skills/prompt-review/scripts/record_review.py", [
            "--project", str(self.root), "--request", relative,
            "--input", str(input_path), "--write",
            *[item for rule in rules for item in ("--required-rule", rule)],
        ])
        self.assertEqual(code, 0, recorded)
        return recorded["path"]

    def selected_preview(self, creative, version=1, style_schema=None):
        if version == 2:
            (self.root / "project.md").write_text("---\nreview_mode: default\n---\n")
        (self.root / "studio").mkdir(exist_ok=True)
        self.evidence["parameters"].update({
            "style": {} if style_schema is None else style_schema,
            "watermark": {"type": "boolean"},
            "return_last_frame": {"type": "boolean"},
            "priority": {"type": "string"},
            "execution_expires_after": {"type": "integer"},
            "safety_identifier": {"type": "string"},
        })
        (self.root / "caps.json").write_text(json.dumps(self.evidence))
        arguments = [
            *self.args(), "--schema-version", str(version),
            *[item for key, value in creative.items() for item in ("--param", f"{key}={json.dumps(value)}")],
        ]
        code, prepared = self.cli(".agents/scripts/prepare_request.py", [*arguments, "--write"])
        self.assertEqual(code, 0, prepared)
        source = json.loads((self.root / prepared["path"]).read_text())
        review_path = self.record(source, prepared["path"])
        code, registered = self.cli(".agents/scripts/prepare_request.py", [
            *arguments, "--write", "--register", "--review", review_path,
        ])
        self.assertEqual(code, 0, registered)
        operation_id = registered["registered"]
        operation_store.transition_operation(self.root, operation_id, "prepared", "submitting")
        operation_store.transition_operation(
            self.root, operation_id, "submitting", "acknowledged",
            provider_task_id="synthetic-preview-task", provider_status="running",
        )
        operation_store.transition_operation(
            self.root, operation_id, "acknowledged", "terminal", provider_status="succeeded",
        )
        output_bytes = b"synthetic artifact; no provider or playback"
        (self.root / "cup.mp4").write_bytes(output_bytes)
        artifact_hash = hashlib.sha256(output_bytes).hexdigest()
        review = {
            "schema_version": 1, "artifact_path": "cup.mp4", "artifact_sha256": artifact_hash,
            "status": "pass", "inspection_method": "synthetic temporal fixture, not actual inspection",
            "coverage": "synthetic contract only",
            "checks": [{"criterion": "fixture", "status": "pass", "evidence": "synthetic"}],
            "observations": ["Synthetic artifact only"],
            "limitations": ["No real media inspection"], "recommendation": "select",
        }
        review_bytes = json.dumps(review).encode()
        (self.root / "artifact-review.json").write_bytes(review_bytes)
        (self.root / "decisions").mkdir(exist_ok=True)
        (self.root / "decisions/select-preview.json").write_text(json.dumps({
            "schema_version": 1, "decision_id": "select-preview",
            "decision_type": "variant_selection", "asset_id": source["asset_id"],
            "subject_path": "cup.mp4", "selected_variant": "cup.mp4",
            "selected_sha256": artifact_hash, "actor": "agent", "approval_mode": "approve_for_me",
            "project_sha256": hashlib.sha256((self.root / "project.md").read_bytes()).hexdigest(),
            "result": "approved", "review_path": "artifact-review.json",
            "review_sha256": hashlib.sha256(review_bytes).hexdigest(),
            "upstream_sha256": {"prompt.md": source["prompt_sha256"]},
            "reason": "Synthetic selection only", "decided_at": datetime.now(UTC).isoformat(),
        }))
        self.assertEqual(validate_request.decision_findings(
            self.root, json.loads((self.root / "decisions/select-preview.json").read_text()),
            require_current_project=True,
        ), [])
        return operation_store.read_registry(self.root / "task_ids.json")["tasks"][0]

    def final_arguments(self, source, creative, asset="cup_final", outputs=None):
        arguments = self.args()
        arguments[arguments.index("cup_t01")] = asset
        arguments[arguments.index("cup.mp4")] = f"{asset}.mp4"
        arguments[arguments.index("resolution=720p")] = "resolution=1080p"
        return [
            *arguments, "--schema-version", str(source["schema_version"]),
            "--ordinary-final-source", source["operation_id"],
            "--ordinary-final-decision", "decisions/select-preview.json",
            *[item for key, value in {**creative, **(outputs or {})}.items()
              for item in ("--param", f"{key}={json.dumps(value)}")],
        ]

    def register_final(self, arguments):
        code, prepared = self.cli(".agents/scripts/prepare_request.py", [*arguments, "--write"])
        self.assertEqual(code, 0, prepared)
        request = json.loads((self.root / prepared["path"]).read_text())
        review_path = self.record(request, prepared["path"])
        code, registered = self.cli(".agents/scripts/prepare_request.py", [
            *arguments, "--review", review_path, "--write", "--register",
        ])
        self.assertEqual(code, 0, registered)
        self.assertEqual(registered["request_sha256"], request["request_sha256"])
        return request, review_path

    def test_matching_nested_identity_and_supported_output_changes_reach_submitting(self):
        values = [
            None, "", [], {}, [False, {"enabled": True}],
            {"nested": {"enabled": True, "values": [None, "1", 1, 1.0]}},
            {"text": "x" * 10000, "number": 10 ** 100},
        ]
        for version in (1, 2):
            for value in values:
                with self.subTest(version=version, value=value):
                    self.setUp()
                    source = self.selected_preview({"style": value}, version)
                    final_value = dict(reversed(list(value.items()))) if isinstance(value, dict) else value
                    request, _ = self.register_final(self.final_arguments(
                        source, {"style": final_value}, outputs={
                            "watermark": False, "return_last_frame": True, "priority": "normal",
                            "execution_expires_after": 300, "safety_identifier": "synthetic",
                        },
                    ))
                    operation_store.transition_operation(
                        self.root, request["operation_id"], "prepared", "submitting",
                    )
                    tasks = operation_store.read_registry(self.root / "task_ids.json")["tasks"]
                    self.assertEqual(tasks[0], source)
                    self.assertEqual(tasks[1]["submission_status"], "submitting")

    def test_changed_json_identity_blocks_prepare_register_and_submitting_without_writes(self):
        pairs = [
            ({"style": {"enabled": True}}, {"style": {"enabled": 1}}),
            ({"style": {"enabled": 1}}, {"style": {"enabled": True}}),
            ({"style": [False, {"enabled": True}]}, {"style": [0, {"enabled": 1}]}),
            ({"style": [0, {"enabled": 1}]}, {"style": [False, {"enabled": True}]}),
            ({"style": {"nested": [{"value": False}]}}, {"style": {"nested": [{"value": 0}]}}),
            ({"style": "true"}, {"style": True}),
            ({"style": None}, {}),
            ({}, {"style": None}),
            ({"style": {"value": None}}, {"style": {}}),
            ({"style": [1, 2]}, {"style": [2, 1]}),
            ({"style": []}, {"style": {}}),
            ({"style": {"value": 1}}, {"style": {"value": 2}}),
            ({"style": {"value": 1}}, {"style": {"value": 1.0}}),
            ({"style": "unchanged"}, {"style": "changed"}),
        ]
        for version in (1, 2):
            for original, changed in pairs:
                with self.subTest(version=version, original=original, changed=changed):
                    self.setUp()
                    source = self.selected_preview(original, version)
                    arguments = self.final_arguments(source, changed)
                    before = self.snapshot()
                    code, rejected = self.cli(".agents/scripts/prepare_request.py", [*arguments, "--write"])
                    self.assertEqual(code, 1, rejected)
                    self.assertIn("seedance.draft_promotion", {f["rule_id"] for f in rejected["findings"]})
                    self.assertEqual(before, self.snapshot())
                    candidate = prepare_request.build_request(
                        self.root, prepare_request.parser().parse_args(arguments),
                    )
                    (self.root / "candidate.json").write_text(json.dumps(candidate))
                    review_path = self.record(candidate, "candidate.json")
                    before = self.snapshot()
                    code, rejected = self.cli(".agents/scripts/prepare_request.py", [
                        *arguments, "--review", review_path, "--write", "--register",
                    ])
                    self.assertEqual(code, 1, rejected)
                    self.assertIn("seedance.draft_promotion", {f["rule_id"] for f in rejected["findings"]})
                    self.assertEqual(before, self.snapshot())
                    valid, _ = self.register_final(self.final_arguments(source, original, asset="valid_final"))
                    candidate["operation_id"] = valid["operation_id"]
                    candidate["asset_id"] = valid["asset_id"]
                    candidate["extensions"]["expected_output"] = valid["extensions"]["expected_output"]
                    registry = operation_store.read_registry(self.root / "task_ids.json")
                    registry["tasks"][1] = candidate
                    operation_store.replace_registry(self.root / "task_ids.json", registry)
                    before = self.snapshot()
                    with self.assertRaisesRegex(ValueError, "changed creative parameters"):
                        operation_store.transition_operation(
                            self.root, valid["operation_id"], "prepared", "submitting",
                        )
                    self.assertEqual(before, self.snapshot())
                    self.assertEqual(
                        operation_store.read_registry(self.root / "task_ids.json")["tasks"][0], source,
                    )

    def test_restrictive_nested_schema_and_unsupported_output_controls_write_nothing(self):
        for changed in (
            {"style": {"enabled": 1}},
            {"style": {"enabled": True}, "watermark": 1},
            {"style": {"enabled": True}, "fps": 60},
        ):
            with self.subTest(changed=changed):
                self.setUp()
                source = self.selected_preview({"style": {"enabled": True}}, version=2, style_schema={
                    "type": "object", "properties": {"enabled": {"type": "boolean"}},
                    "required": ["enabled"], "additionalProperties": False,
                })
                arguments = self.final_arguments(source, changed)
                for flags in (["--write"], ["--write", "--register"]):
                    before = self.snapshot()
                    code, rejected = self.cli(".agents/scripts/prepare_request.py", [*arguments, *flags])
                    self.assertEqual(code, 1, rejected)
                    self.assertIn("model.supported_mode", {f["rule_id"] for f in rejected["findings"]})
                    self.assertEqual(before, self.snapshot())
                valid, _ = self.register_final(self.final_arguments(
                    source, {"style": {"enabled": True}}, asset="valid_final",
                ))
                candidate = prepare_request.build_request(
                    self.root, prepare_request.parser().parse_args(
                        self.final_arguments(source, changed, asset="valid_final"),
                    ),
                )
                registry = operation_store.read_registry(self.root / "task_ids.json")
                registry["tasks"][1] = candidate
                operation_store.replace_registry(self.root / "task_ids.json", registry)
                before = self.snapshot()
                with self.assertRaises(ValueError):
                    operation_store.transition_operation(
                        self.root, valid["operation_id"], "prepared", "submitting",
                    )
                self.assertEqual(before, self.snapshot())

    def test_recorder_rejects_stale_nested_digest_without_writing(self):
        for version in (1, 2):
            with self.subTest(version=version):
                self.setUp()
                source = self.selected_preview({"style": {"enabled": True}}, version)
                arguments = self.final_arguments(source, {"style": {"enabled": True}})
                request = prepare_request.build_request(
                    self.root, prepare_request.parser().parse_args(arguments),
                )
                request["params"]["style"]["enabled"] = 1
                (self.root / "stale.json").write_text(json.dumps(request))
                before = self.snapshot()
                code, rejected = self.cli(".agents/skills/prompt-review/scripts/record_review.py", [
                    "--project", str(self.root), "--request", "stale.json",
                    "--input", str(self.root / "review-input.json"), "--write",
                ])
                self.assertEqual(code, 1, rejected)
                self.assertIn("input.readable", {f["rule_id"] for f in rejected["findings"]})
                self.assertIn("stale", rejected["findings"][0]["message"])
                self.assertEqual(before, self.snapshot())


if __name__ == "__main__":
    unittest.main()
