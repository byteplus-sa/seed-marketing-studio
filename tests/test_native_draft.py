import copy
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / ".agents/scripts"))
import operation_store
import prepare_request
import validate_request


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
