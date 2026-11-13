import copy
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
        options = variant_matrix.parser().parse_args([
            "register", "matrix.json", "--project", str(self.root),
            "--audio-model", "fixture-audio", "--audio-operation", "voice",
            "--capabilities", "caps.json",
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


if __name__ == "__main__":
    unittest.main()
