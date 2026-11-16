from __future__ import annotations

import contextlib
import hashlib
import importlib.util
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Any

import test_native_draft
import test_seedance_capability_profiles

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / ".agents/skills/prompt-review/scripts/record_review.py"
SPEC = importlib.util.spec_from_file_location("record_review", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)
validation = MODULE.validation


class RecordReviewTests(unittest.TestCase):
    def setUp(self) -> None:
        self.directory = tempfile.TemporaryDirectory(prefix="record-review-test-")
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name) / "demo"
        (self.root / "elements/hero").mkdir(parents=True)
        (self.root / "requests").mkdir()
        (self.root / "project.md").write_text(
            "---\napproval_mode: approve_for_me\n---\n"
        )
        (self.root / "elements/hero/char_hero_v01.png").write_bytes(b"hero")
        (self.root / "prompt_s01_sh010_t01_v01.md").write_text("@Image 1 waves.\n")
        references = [
            {
                "path": "elements/hero/char_hero_v01.png",
                "sha256": hashlib.sha256(b"hero").hexdigest(),
                "role": "reference_image",
                "binding": "@Image 1",
                "approval_evidence": {
                    "manifest": "elements/hero/character.md",
                    "field": "selected_variant",
                },
            }
        ]
        prompt = (self.root / "prompt_s01_sh010_t01_v01.md").read_bytes()
        params = {"duration": 5}
        self.hash = validation.compute_request_hash(
            prompt, references, "fixture-model", "generate", params
        )
        request = {
            "schema_version": 1,
            "operation_id": "fixture-s01-sh010-t01-v01",
            "asset_id": "s01_sh010_t01_v01",
            "transport": "ark-mcp",
            "model": "fixture-model",
            "operation": "generate",
            "prompt_file": "prompt_s01_sh010_t01_v01.md",
            "prompt_sha256": hashlib.sha256(prompt).hexdigest(),
            "request_sha256": self.hash,
            "references": references,
            "params": params,
            "submission_status": "prepared",
            "provider_task_id": None,
            "provider_status": None,
            "review_status": "not_started",
            "cost": {"estimated": None, "confirmed": None, "currency": "USD"},
        }
        (self.root / "requests/request_s01_sh010_t01_v01.json").write_text(
            json.dumps(request)
        )
        self.input = Path(self.directory.name) / "reviewer.txt"

    def review(
        self, request_hash: str, rule: str = "asset.visible_consistency"
    ) -> dict[str, Any]:
        return {
            "schema_version": 1,
            "request_sha256": request_hash,
            "reviewer_status": "complete",
            "checks": [{"rule_id": rule, "status": "pass", "evidence": "Checked"}],
        }

    def run_cli(self, *extra: str, text: str) -> tuple[int, dict[str, Any]]:
        self.input.write_text(text)
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            code = MODULE.main(
                ["--project", str(self.root), "--input", str(self.input), *extra]
            )
        return code, json.loads(output.getvalue())

    def fenced(self, *reviews: dict[str, Any]) -> str:
        blocks = "\n".join(
            f"```json\n{json.dumps(review, indent=2)}\n```" for review in reviews
        )
        return f"Review notes {{brace}} follow.\n\n{blocks}\n\nNo CRITICAL findings.\n"

    def test_extracts_matching_review_from_fenced_prose(self) -> None:
        text = self.fenced(self.review("0" * 64), self.review(self.hash))
        code, result = self.run_cli(
            "--request",
            "requests/request_s01_sh010_t01_v01.json",
            "--required-rule",
            "asset.visible_consistency",
            text=text,
        )
        self.assertEqual(code, 0, result)
        self.assertEqual(result["review"], self.review(self.hash))
        self.assertFalse((self.root / "reviews").exists())

    def test_raw_json_input(self) -> None:
        review = self.review(self.hash)
        self.assertEqual(MODULE.extract_review(json.dumps(review), self.hash), review)

    def test_mismatched_hash_is_rejected(self) -> None:
        code, result = self.run_cli(
            "--request",
            "requests/request_s01_sh010_t01_v01.json",
            "--write",
            text=self.fenced(self.review("0" * 64)),
        )
        self.assertEqual(code, 1)
        self.assertIn("request hash", result["findings"][0]["message"])
        self.assertFalse((self.root / "reviews").exists())

    def test_missing_required_rule_is_rejected(self) -> None:
        code, result = self.run_cli(
            "--request",
            "requests/request_s01_sh010_t01_v01.json",
            "--required-rule",
            "references.ordered_bindings",
            "--write",
            text=self.fenced(self.review(self.hash)),
        )
        self.assertEqual(code, 1)
        self.assertIn(
            "Missing required rule: references.ordered_bindings",
            [finding["message"] for finding in result["findings"]],
        )
        self.assertFalse((self.root / "reviews").exists())

    def test_write_path_and_no_overwrite(self) -> None:
        args = ("--request", "requests/request_s01_sh010_t01_v01.json", "--write")
        code, result = self.run_cli(*args, text=self.fenced(self.review(self.hash)))
        self.assertEqual(code, 0, result)
        self.assertEqual(result["path"], "reviews/review_s01_sh010_t01_v01.json")
        path = self.root / result["path"]
        self.assertEqual(json.loads(path.read_text()), self.review(self.hash))
        self.assertEqual(
            result["review_sha256"], hashlib.sha256(path.read_bytes()).hexdigest()
        )
        code, _ = self.run_cli(*args, text=self.fenced(self.review(self.hash)))
        self.assertEqual(code, 0)
        original = path.read_bytes()
        code, result = self.run_cli(
            *args,
            text=self.fenced(self.review(self.hash, "narrative.observable_event")),
        )
        self.assertEqual(code, 1)
        self.assertIn("overwrite", result["findings"][0]["message"])
        self.assertEqual(path.read_bytes(), original)

    def test_stale_request_file_is_rejected(self) -> None:
        (self.root / "prompt_s01_sh010_t01_v01.md").write_text("@Image 1 bows.\n")
        code, result = self.run_cli(
            "--request",
            "requests/request_s01_sh010_t01_v01.json",
            text=self.fenced(self.review(self.hash)),
        )
        self.assertEqual(code, 1)
        self.assertIn("stale", result["findings"][0]["message"])

    def test_request_path_must_stay_in_project(self) -> None:
        code, _ = self.run_cli(
            "--request", "../outside.json", text=self.fenced(self.review(self.hash))
        )
        self.assertEqual(code, 1)

    def test_text_only_audio_by_hash_and_asset(self) -> None:
        audio_hash = "a" * 64
        code, result = self.run_cli(
            "--request-sha256",
            audio_hash,
            "--asset",
            "amb_market_v01",
            "--write",
            text=self.fenced(self.review(audio_hash)),
        )
        self.assertEqual(code, 0, result)
        self.assertTrue((self.root / "reviews/review_amb_market_v01.json").is_file())
        code, _ = self.run_cli(
            "--request-sha256",
            audio_hash,
            "--asset",
            "../escape",
            text=self.fenced(self.review(audio_hash)),
        )
        self.assertEqual(code, 1)


class PreparedRequestReviewTests(unittest.TestCase):
    def cli(self, script, arguments):
        result = subprocess.run(
            [sys.executable, "-B", str(ROOT / script), *arguments],
            capture_output=True, text=True, check=False, timeout=30,
        )
        self.assertEqual(result.stderr, "", result.stderr)
        return result.returncode, json.loads(result.stdout)

    def prepared(self, kind, version=1):
        fixture = test_native_draft.NativeDraftTests()
        fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        if version == 2:
            (fixture.root / "project.md").write_text(
                "---\nreview_mode: default\napproval_mode: approve_for_me\n---\n"
            )
        if kind == "final":
            fixture.profiled_source(native=False)
            source = json.loads((fixture.root / "task_ids.json").read_text())["tasks"][0]
            arguments = fixture.argv({"resolution": "1080p"}, source["model"])
            arguments += [
                "--ordinary-final-source", source["operation_id"],
                "--ordinary-final-decision", "decisions/select-draft.json",
            ]
        elif kind == "preview":
            fixture.caps = test_seedance_capability_profiles.profile()
            arguments = fixture.argv({"resolution": "720p"}, fixture.caps["model"])
        else:
            arguments = fixture.argv({"resolution": "480p", "draft": True})
        if kind != "legacy":
            (fixture.root / "caps.json").write_text(json.dumps(fixture.caps))
            arguments += [
                "--capabilities", "caps.json", "--expected-provider", "fixture-provider",
                "--expected-tool-schema-revision", "fixture-r1",
            ]
        arguments[arguments.index("--asset") + 1] = f"review-{kind}-v{version}"
        code, result = self.cli(".agents/scripts/prepare_request.py", [*arguments, "--write"])
        self.assertEqual(code, 0, result)
        receipt = fixture.root / result["path"]
        request = json.loads(receipt.read_text())
        self.assertEqual(request["schema_version"], version)
        self.assertEqual(validation.validate_request(fixture.root, request, fixture.caps), [])
        return fixture.root, receipt, request

    def record(self, root, receipt, request, *, explicit=False, evidence="Synthetic contract only"):
        input_path = root / "reviewer.json"
        input_path.write_text(json.dumps({
            "schema_version": 1, "request_sha256": request["request_sha256"],
            "reviewer_status": "complete",
            "checks": [{"rule_id": "asset.visible_consistency", "status": "pass",
                        "evidence": evidence}],
        }))
        identity = (
            ["--request-sha256", request["request_sha256"], "--asset", request["asset_id"]]
            if explicit else ["--request", receipt.relative_to(root).as_posix()]
        )
        return self.cli(
            ".agents/skills/prompt-review/scripts/record_review.py",
            ["--project", str(root), *identity, "--input", str(input_path), "--write"],
        )

    def test_actual_prepared_profiles_and_ordinary_finals_record_write_once(self):
        for kind in ("preview", "final"):
            for version in (1, 2):
                with self.subTest(kind=kind, version=version):
                    root, receipt, request = self.prepared(kind, version)
                    original_receipt = receipt.read_bytes()
                    code, result = self.record(root, receipt, request)
                    self.assertEqual(code, 0, result)
                    self.assertEqual(result["request_sha256"], request["request_sha256"])
                    review_path = root / result["path"]
                    original_review = review_path.read_bytes()
                    self.assertEqual(self.record(root, receipt, request)[0], 0)
                    code, result = self.record(root, receipt, request, evidence="Different evidence")
                    self.assertEqual(code, 1, result)
                    self.assertIn("overwrite", result["findings"][0]["message"])
                    self.assertEqual(receipt.read_bytes(), original_receipt)
                    self.assertEqual(review_path.read_bytes(), original_review)

    def test_actual_unprofiled_receipts_preserve_historical_hashes(self):
        for version in (1, 2):
            with self.subTest(version=version):
                root, receipt, request = self.prepared("legacy", version)
                self.assertIsNone(validation.execution_profile(request))
                digest = validation.compute_request_hash(
                    (root / request["prompt_file"]).read_bytes(), request["references"],
                    request["model"], request["operation"], request["params"],
                    approval_mode=request.get("approval_mode"),
                    project_sha256=request.get("project_sha256"),
                )
                self.assertEqual(digest, request["request_sha256"])
                self.assertEqual(self.record(root, receipt, request)[0], 0)
                self.assertEqual(self.record(root, receipt, request, explicit=True)[0], 0)

    def test_profile_intent_prompt_and_reference_digest_tampering_write_nothing(self):
        mutations = (
            "destination", "evidence", "intent", "remove-profile", "remove-intent",
            "prompt", "reference",
        )
        for mutation in mutations:
            with self.subTest(mutation=mutation):
                root, receipt, request = self.prepared("final")
                binding = request["extensions"]["execution_profile"]
                if mutation == "destination":
                    binding["destination"]["provider"] = "other-provider"
                elif mutation == "evidence":
                    binding["evidence"]["profile_id"] = "other-profile"
                elif mutation == "intent":
                    binding["ordinary_final"]["decision_sha256"] = "0" * 64
                elif mutation == "remove-profile":
                    del request["extensions"]["execution_profile"]
                elif mutation == "remove-intent":
                    del binding["ordinary_final"]
                elif mutation == "prompt":
                    (root / request["prompt_file"]).write_text("Changed creative intent.\n")
                else:
                    request["references"] = [{
                        "path": "frame.png", "sha256": "0" * 64,
                        "role": "reference_image", "binding": "@Image 1",
                        "approval_evidence": {"manifest": "frame.md", "field": "selected_variant"},
                    }]
                receipt.write_text(json.dumps(request))
                original = receipt.read_bytes()
                code, result = self.record(root, receipt, request)
                self.assertEqual(code, 1, result)
                self.assertIn("stale", result["findings"][0]["message"])
                self.assertFalse((root / "reviews").exists())
                self.assertEqual(receipt.read_bytes(), original)
                self.assertEqual(self.record(root, receipt, request, explicit=True)[0], 0)


if __name__ == "__main__":
    unittest.main()
