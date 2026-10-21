from __future__ import annotations

import contextlib
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / ".agents/scripts"))

import operation_store
import prepare_request
import validate_request


class ReviewModeTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory(prefix="review-mode-")
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        (self.root / "studio").mkdir()
        (self.root / "project.md").write_text(
            "---\napproval_mode: approve_for_me\n---\n"
        )
        (self.root / "prompt.md").write_text("A blue ceramic bowl on a table.\n")
        self.capabilities = {
            "model": "fixture-model",
            "source": "synthetic test schema",
            "verified_at": "2026-10-20T00:00:00Z",
            "operations": ["generate"],
            "parameters": {},
            "reference_roles": [],
            "max_references": 0,
        }
        (self.root / "capabilities.json").write_text(json.dumps(self.capabilities))

    def mode(self, value, approval="approve_for_me"):
        (self.root / "project.md").write_text(
            f"---\napproval_mode: {approval}\nreview_mode: {value}\n---\n"
        )

    def argv(self, *extra):
        return [
            "--project",
            str(self.root),
            "--asset",
            "bowl",
            "--prompt",
            "prompt.md",
            "--model",
            "fixture-model",
            "--operation",
            "generate",
            "--expected-output",
            "bowl.png",
            *extra,
        ]

    def run_prepare(self, *extra):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            code = prepare_request.main(self.argv(*extra))
        return code, json.loads(output.getvalue())

    def request(self):
        code, result = self.run_prepare()
        self.assertEqual(code, 0, result)
        return result["request"]

    def register(self, *extra):
        return self.run_prepare(
            "--write", "--register", "--capabilities", "capabilities.json", *extra
        )

    def review(self, request):
        return {
            "schema_version": 1,
            "request_sha256": request["request_sha256"],
            "reviewer_status": "complete",
            "checks": [
                {
                    "rule_id": "asset.visible_consistency",
                    "status": "pass",
                    "evidence": "Synthetic prompt names one blue bowl consistently.",
                }
            ],
        }

    def validate_cli(self, request, *extra):
        path = self.root / "request.json"
        path.write_text(json.dumps(request))
        result = subprocess.run(
            [
                sys.executable,
                str(ROOT / ".agents/scripts/validate_request.py"),
                "--project",
                str(self.root),
                "--request",
                str(path),
                "--capabilities",
                str(self.root / "capabilities.json"),
                *extra,
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        return result.returncode, json.loads(result.stdout)

    def test_missing_mode_prepares_digest_bound_request_and_registers_without_review(
        self,
    ):
        request = self.request()
        self.assertEqual(request["schema_version"], 2)
        self.assertEqual(
            request["project_sha256"],
            validate_request.project_mode_snapshot(self.root)[1],
        )
        self.assertEqual(self.validate_cli(request)[0], 0)
        code, result = self.register()
        self.assertEqual(code, 0, result)
        record = json.loads((self.root / "task_ids.json").read_text())["tasks"][0]
        self.assertEqual(record["review_status"], "not_started")
        self.assertFalse((self.root / "reviews").exists())
        operation_store.transition_operation(
            self.root, record["operation_id"], "prepared", "submitting"
        )

    def test_plain_legacy_brief_defaults_for_new_preparations(self):
        (self.root / "project.md").write_text("# Legacy brief\n")
        self.assertEqual(self.request()["schema_version"], 1)
        code, result = self.register()
        self.assertEqual(code, 0, result)

    def test_explicit_review_mode_alone_selects_v2(self):
        (self.root / "project.md").write_text("---\nreview_mode: default\n---\n")
        self.assertEqual(self.request()["schema_version"], 2)
        code, result = self.register()
        self.assertEqual(code, 0, result)

    def test_explicit_review_mode_cannot_use_v1_registration_or_transition(self):
        (self.root / "project.md").write_text("# Legacy brief\n")
        request = self.request()
        operation_store.prepare_operation(
            self.root, request, self.capabilities, None, []
        )
        before = (self.root / "task_ids.json").read_bytes()
        for mode in ("default", "strict"):
            with self.subTest(mode=mode):
                (self.root / "project.md").write_text(
                    f"---\nreview_mode: {mode}\n---\n"
                )
                with self.assertRaisesRegex(ValueError, "version-2"):
                    operation_store.transition_operation(
                        self.root, request["operation_id"], "prepared", "submitting"
                    )
                with self.assertRaisesRegex(ValueError, "version-2"):
                    operation_store.prepare_operation(
                        self.root, request, self.capabilities, self.review(request), []
                    )
                self.assertEqual((self.root / "task_ids.json").read_bytes(), before)

    def test_review_and_approval_modes_are_independent(self):
        self.mode("default", "ask_for_approval")
        request = self.request()
        self.assertEqual(request["approval_mode"], "ask_for_approval")
        operation_store.prepare_operation(
            self.root, request, self.capabilities, None, []
        )

    def test_strict_requires_report_and_accepts_real_complete_report(self):
        self.mode("strict")
        request = self.request()
        self.assertEqual(self.validate_cli(request)[0], 1)
        code, result = self.register()
        self.assertEqual(code, 1, result)
        with self.assertRaises(ValueError):
            operation_store.prepare_operation(
                self.root, request, self.capabilities, None, []
            )
        self.assertFalse((self.root / "task_ids.json").exists())
        (self.root / "review.json").write_text(json.dumps(self.review(request)))
        code, result = self.register("--review", "review.json")
        self.assertEqual(code, 0, result)

    def test_invalid_mode_fails_before_writes(self):
        for mode in ("fast", "null", "true", "[]", "{}", '""'):
            with self.subTest(mode=mode):
                self.mode(mode)
                code, result = self.register()
                self.assertEqual(code, 1, result)
                self.assertIn("review mode", json.dumps(result).lower())
                self.assertFalse((self.root / "requests").exists())

    def test_explicit_required_rule_demands_report_even_in_default(self):
        request = self.request()
        rule = "asset.visible_consistency"
        self.assertEqual(self.validate_cli(request, "--required-rule", rule)[0], 1)
        code, result = self.register("--required-rule", rule)
        self.assertEqual(code, 1, result)
        with self.assertRaises(ValueError):
            operation_store.prepare_operation(
                self.root, request, self.capabilities, None, [rule]
            )
        (self.root / "review.json").write_text(json.dumps(self.review(request)))
        code, result = self.register("--required-rule", rule, "--review", "review.json")
        self.assertEqual(code, 0, result)

    def test_supplied_bad_reviews_are_never_ignored(self):
        request = self.request()
        for defect in (
            "failed",
            "stale",
            "incomplete",
            "empty",
            "null",
            "missing-rule",
        ):
            with self.subTest(defect=defect):
                report = self.review(request)
                if defect == "failed":
                    report["checks"][0]["status"] = "fail"
                elif defect == "stale":
                    report["request_sha256"] = "0" * 64
                elif defect == "incomplete":
                    report["reviewer_status"] = "incomplete"
                elif defect == "empty":
                    report["checks"] = []
                elif defect == "null":
                    report = None
                required = (
                    ["--required-rule", "ad.claims_supported"]
                    if defect == "missing-rule"
                    else []
                )
                (self.root / "review.json").write_text(json.dumps(report))
                code, result = self.register("--review", "review.json", *required)
                self.assertEqual(code, 1, result)
                code, result = self.validate_cli(
                    request, "--review", str(self.root / "review.json"), *required
                )
                self.assertEqual(code, 1, result)
                self.assertFalse((self.root / "task_ids.json").exists())

    def test_mode_change_invalidates_pending_request_and_report(self):
        self.mode("strict")
        request = self.request()
        report = self.review(request)
        operation_store.prepare_operation(
            self.root, request, self.capabilities, report, []
        )
        before = (self.root / "task_ids.json").read_bytes()
        self.mode("default")
        with self.assertRaises(ValueError):
            operation_store.transition_operation(
                self.root, request["operation_id"], "prepared", "submitting"
            )
        self.assertEqual((self.root / "task_ids.json").read_bytes(), before)
        updated = self.request()
        self.assertNotEqual(request["request_sha256"], updated["request_sha256"])
        with self.assertRaises(ValueError):
            operation_store.prepare_operation(
                self.root, updated, self.capabilities, report, []
            )

    def test_mode_is_rechecked_under_registry_lock(self):
        request = self.request()
        original = operation_store.registry_lock

        @contextlib.contextmanager
        def changed_mode(root):
            with original(root) as path:
                self.mode("strict")
                yield path

        with (
            patch.object(operation_store, "registry_lock", changed_mode),
            self.assertRaises(ValueError),
        ):
            operation_store.prepare_operation(
                self.root, request, self.capabilities, None, []
            )
        self.assertFalse((self.root / "task_ids.json").exists())

    def test_default_still_checks_capabilities_and_duplicate_identity(self):
        request = self.request()
        bad = {**self.capabilities, "model": "unsupported"}
        with self.assertRaises(ValueError):
            operation_store.prepare_operation(self.root, request, bad, None, [])
        operation_store.prepare_operation(
            self.root, request, self.capabilities, None, []
        )
        with self.assertRaises(ValueError):
            operation_store.prepare_operation(
                self.root, request, self.capabilities, None, []
            )

    def test_cli_smoke_registers_without_review_and_rejects_stale_mode(self):
        result = subprocess.run(
            [
                sys.executable,
                str(ROOT / ".agents/scripts/prepare_request.py"),
                *self.argv(
                    "--write", "--register", "--capabilities", "capabilities.json"
                ),
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        record = json.loads((self.root / "task_ids.json").read_text())["tasks"][0]
        code, output = self.validate_cli(record)
        self.assertEqual(code, 0, output)
        self.mode("strict")
        code, output = self.validate_cli(record)
        self.assertEqual(code, 1, output)
        self.assertTrue(
            any(
                finding["rule_id"] == "approval.current_mode"
                for finding in output["findings"]
            )
        )

    def test_mode_documentation_keeps_storyboard_layouts_and_focused_compliance(self):
        storyboard = ROOT / ".agents/skills/seedream-storyboard"
        for relative in (
            "SKILL.md",
            "references/context-and-preflight.md",
            "references/review-and-selection.md",
            "references/generation-and-persistence.md",
        ):
            text = (storyboard / relative).read_text()
            self.assertIn("default", text.lower())
            self.assertIn("strict", text.lower())
        self.assertIn("| 3 | 1×3 or 3×1 |", (storyboard / "SKILL.md").read_text())
        readme = (ROOT / "README.md").read_text()
        for rule in (
            "ad.claims_supported",
            "ad.no_fabricated_testimonial",
            "brand.copy_rules",
            "library.pin_current",
        ):
            self.assertIn(rule, readme)
        self.assertIn("explicit native", readme)


if __name__ == "__main__":
    unittest.main()
