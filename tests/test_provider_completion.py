import copy
import json
import subprocess
import sys
import unittest
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime, timedelta
from pathlib import Path
from unittest.mock import patch

import test_native_draft
from test_seedance_capability_profiles import profile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / ".agents/scripts"))
import operation_store
import validate_request


class ProviderCompletionTests(unittest.TestCase):
    setUp = test_native_draft.NativeDraftTests.setUp
    argv = test_native_draft.NativeDraftTests.argv
    write_selection = test_native_draft.NativeDraftTests.write_selection

    def cli(self, script, arguments):
        result = subprocess.run(
            [sys.executable, "-B", str(ROOT / ".agents/scripts" / script), *arguments],
            capture_output=True, text=True, check=False, timeout=30,
        )
        self.assertEqual(result.stderr, "", result.stderr)
        return result.returncode, json.loads(result.stdout)

    def prepare(self, version=2):
        if version == 2:
            (self.root / "project.md").write_text("---\nreview_mode: default\n---\n")
            (self.root / "studio").mkdir()
        evidence = profile()
        evidence.update(
            model=self.caps["model"], parameters=self.caps["parameters"],
            reference_roles=[], max_references=0,
            preview={
                "support": "verified", "kind": "native_draft",
                "params": {"resolution": "480p", "draft": True},
            },
            promotion={"support": "verified", "max_age_seconds": 3600, "resolutions": ["1080p"]},
        )
        self.caps = evidence
        (self.root / "caps.json").write_text(json.dumps(evidence))
        arguments = [
            *self.argv({"resolution": "480p", "draft": True}),
            "--schema-version", str(version), "--operation-id", "cup-draft",
            "--capabilities", "caps.json", "--expected-provider", "fixture-provider",
            "--expected-tool-schema-revision", "fixture-r1", "--write", "--register",
        ]
        code, result = self.cli("prepare_request.py", arguments)
        self.assertEqual(code, 0, result)
        self.receipt = self.root / result["path"]
        self.frozen_receipt = self.receipt.read_bytes()
        self.original = self.record()
        self.arguments = arguments

    def record(self):
        return operation_store.read_registry(self.root / "task_ids.json")["tasks"][0]

    def transition(self, expected, new, **kwargs):
        operation_store.transition_operation(self.root, "cup-draft", expected, new, **kwargs)

    def acknowledge(self):
        self.transition("prepared", "submitting")
        self.transition(
            "submitting", "acknowledged",
            provider_task_id="selected-task", provider_status="running",
        )

    def promotion(self):
        arguments = list(self.arguments)
        arguments[arguments.index("cup_t01")] = "cup_final"
        arguments[arguments.index("cup-draft")] = "cup-final"
        arguments[arguments.index("cup_t01.mp4")] = "cup_final.mp4"
        arguments[arguments.index('resolution="480p"')] = 'resolution="1080p"'
        arguments[arguments.index("draft=true")] = 'draft_task_id="selected-task"'
        return self.cli("prepare_request.py", arguments)

    def assert_frozen(self):
        self.assertEqual(self.receipt.read_bytes(), self.frozen_receipt)
        record = self.record()
        for key in ("request_sha256", "prompt_sha256", "params", "references", "review_status"):
            self.assertEqual(record[key], self.original[key])
        self.assertEqual(
            record["extensions"]["execution_profile"],
            self.original["extensions"]["execution_profile"],
        )
        self.assertEqual(
            record["request_sha256"],
            validate_request.compute_request_hash(
                (self.root / record["prompt_file"]).read_bytes(), record["references"],
                record["model"], record["operation"], record["params"],
                approval_mode=record.get("approval_mode"),
                project_sha256=record.get("project_sha256"),
                execution_profile=validate_request.execution_profile(record),
            ),
        )

    def test_real_cli_lifecycle_selection_and_promotion_preserve_frozen_hashes(self):
        self.prepare()
        completed_at = (datetime.now(UTC) - timedelta(seconds=5)).isoformat()
        for expected, new, flags in (
            ("prepared", "submitting", []),
            ("submitting", "acknowledged", ["--provider-task-id", "selected-task", "--provider-status", "running"]),
            ("acknowledged", "terminal", ["--provider-status", "succeeded", "--provider-completed-at", completed_at]),
        ):
            code, result = self.cli("operation_store.py", [
                "transition", "--project", str(self.root), "--operation-id", "cup-draft",
                "--expected-status", expected, "--new-status", new, *flags,
            ])
            self.assertEqual(code, 0, result)
        self.assertEqual(self.record()["extensions"]["provider_completed_at"], completed_at)
        code, rejected = self.promotion()
        self.assertEqual(code, 1, rejected)
        self.write_selection(self.record())
        code, promoted = self.promotion()
        self.assertEqual(code, 0, promoted)
        code, result = self.cli("operation_store.py", [
            "transition", "--project", str(self.root), "--operation-id", "cup-final",
            "--expected-status", "prepared", "--new-status", "submitting",
        ])
        self.assertEqual(code, 0, result)
        self.assert_frozen()

    def test_invalid_and_future_completion_evidence_never_mutates_registry(self):
        self.prepare()
        self.acknowledge()
        before = (self.root / "task_ids.json").read_bytes()
        for value in ("", " ", "invalid", "2026-99-01T00:00:00Z", "2026-01-01",
                      "2026-01-01T00:00:00", 123, False, {}, [],
                      (datetime.now(UTC) + timedelta(hours=1)).isoformat()):
            with self.subTest(value=value), self.assertRaises((ValueError, TypeError)):
                self.transition(
                    "acknowledged", "terminal", provider_status="succeeded",
                    provider_completed_at=value,
                )
            self.assertEqual((self.root / "task_ids.json").read_bytes(), before)

    def test_missing_completion_time_stays_missing_until_evidence_reconciliation(self):
        for version in (1, 2):
            with self.subTest(version=version):
                self.setUp()
                self.prepare(version)
                self.acknowledge()
                self.transition("acknowledged", "terminal", provider_status="succeeded")
                self.assertNotIn("provider_completed_at", self.record()["extensions"])
                self.write_selection(self.record())
                code, result = self.promotion()
                self.assertEqual(code, 1, result)
                self.assertIn("recorded provider completion time", str(result))
                completed_at = (datetime.now(UTC) - timedelta(seconds=5)).isoformat()
                self.transition("terminal", "terminal", provider_completed_at=completed_at)
                code, result = self.promotion()
                self.assertEqual(code, 0, result)
                self.assert_frozen()

    def test_old_completion_is_preserved_but_cannot_promote(self):
        self.prepare()
        self.acknowledge()
        completed_at = (datetime.now(UTC) - timedelta(hours=2)).isoformat()
        self.transition(
            "acknowledged", "terminal", provider_status="succeeded",
            provider_completed_at=completed_at,
        )
        self.write_selection(self.record())
        code, result = self.promotion()
        self.assertEqual(code, 1, result)
        self.assertIn("expired", str(result))
        self.assertEqual(self.record()["extensions"]["provider_completed_at"], completed_at)
        self.assert_frozen()

    def test_failed_completion_evidence_does_not_authorize_promotion(self):
        self.prepare()
        self.acknowledge()
        self.transition(
            "acknowledged", "terminal", provider_status="failed",
            provider_completed_at=(datetime.now(UTC) - timedelta(seconds=5)).isoformat(),
        )
        self.write_selection(self.record())
        code, result = self.promotion()
        self.assertEqual(code, 1, result)
        self.assertIn("successful native Draft", str(result))

    def test_completion_requires_terminal_state_and_provider_identity(self):
        self.prepare()
        completed_at = (datetime.now(UTC) - timedelta(seconds=5)).isoformat()
        before = (self.root / "task_ids.json").read_bytes()
        with self.assertRaises(ValueError):
            self.transition("prepared", "submitting", provider_completed_at=completed_at)
        self.assertEqual((self.root / "task_ids.json").read_bytes(), before)
        self.transition("prepared", "submitting")
        before = (self.root / "task_ids.json").read_bytes()
        for fields in ({}, {"provider_task_id": ""}, {"provider_task_id": " "},
                       {"provider_task_id": "selected-task", "provider_status": ""}):
            with self.subTest(fields=fields), self.assertRaises(ValueError):
                self.transition("submitting", "terminal", provider_completed_at=completed_at, **fields)
            self.assertEqual((self.root / "task_ids.json").read_bytes(), before)

    def test_terminal_reconciliation_is_idempotent_and_rejects_conflicts(self):
        self.prepare()
        self.acknowledge()
        completed_at = (datetime.now(UTC) - timedelta(seconds=5)).isoformat()
        self.transition(
            "acknowledged", "terminal", provider_status="succeeded",
            provider_completed_at=completed_at,
        )
        before = (self.root / "task_ids.json").read_bytes()
        self.transition("terminal", "terminal", provider_completed_at=completed_at)
        self.assertEqual((self.root / "task_ids.json").read_bytes(), before)
        for changes in (
            {},
            {"provider_completed_at": (datetime.now(UTC) - timedelta(seconds=1)).isoformat()},
            {"provider_completed_at": completed_at, "provider_task_id": "different-task"},
            {"provider_completed_at": completed_at, "provider_status": "failed"},
        ):
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                self.transition("terminal", "terminal", **changes)
            self.assertEqual((self.root / "task_ids.json").read_bytes(), before)
        self.assert_frozen()

    def test_concurrent_conflicting_completion_has_one_winner(self):
        self.prepare()
        self.acknowledge()
        self.transition("acknowledged", "terminal", provider_status="succeeded")
        times = [(datetime.now(UTC) - timedelta(seconds=seconds)).isoformat() for seconds in (5, 10)]

        def attempt(timestamp):
            try:
                self.transition("terminal", "terminal", provider_completed_at=timestamp)
                return timestamp
            except ValueError:
                return None

        with ThreadPoolExecutor(max_workers=2) as workers:
            winners = [value for value in workers.map(attempt, times) if value is not None]
        self.assertEqual(len(winners), 1)
        self.assertEqual(self.record()["extensions"]["provider_completed_at"], winners[0])

    def test_failed_completion_write_preserves_record(self):
        self.prepare()
        self.acknowledge()
        before = (self.root / "task_ids.json").read_bytes()
        with (
            patch.object(operation_store.os, "replace", side_effect=OSError("injected failure")),
            self.assertRaises(OSError),
        ):
            self.transition(
                "acknowledged", "terminal", provider_status="succeeded",
                provider_completed_at=(datetime.now(UTC) - timedelta(seconds=5)).isoformat(),
            )
        self.assertEqual((self.root / "task_ids.json").read_bytes(), before)
        self.assertEqual(list(self.root.glob(".task_ids-*.tmp")), [])

    def test_completion_retains_timezone_and_expires_at_exact_promotion_boundary(self):
        self.prepare()
        self.acknowledge()
        completed = datetime.now(UTC) - timedelta(seconds=5)
        completed_at = completed.isoformat().replace("+00:00", "Z")
        self.transition(
            "acknowledged", "terminal", provider_status="succeeded",
            provider_completed_at=completed_at,
        )
        self.assertEqual(self.record()["extensions"]["provider_completed_at"], completed_at)
        self.write_selection(self.record())
        code, result = self.promotion()
        self.assertEqual(code, 0, result)
        request = json.loads((self.root / result["path"]).read_text())
        with patch.object(validate_request, "datetime", wraps=datetime) as clock:
            clock.now.return_value = completed + timedelta(seconds=3599)
            self.assertEqual(validate_request.draft_promotion_findings(self.root, request), [])
            clock.now.return_value = completed + timedelta(seconds=3600)
            self.assertIn("expired", str(validate_request.draft_promotion_findings(self.root, request)))
        self.assert_frozen()

    def test_cli_invalid_completion_reports_failure_without_mutation(self):
        self.prepare()
        self.acknowledge()
        before = copy.deepcopy(self.record())
        code, result = self.cli("operation_store.py", [
            "transition", "--project", str(self.root), "--operation-id", "cup-draft",
            "--expected-status", "acknowledged", "--new-status", "terminal",
            "--provider-status", "succeeded", "--provider-completed-at", "invalid",
        ])
        self.assertEqual(code, 1, result)
        self.assertFalse(result["ok"])
        self.assertEqual(self.record(), before)


if __name__ == "__main__":
    unittest.main()
