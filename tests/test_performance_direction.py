from __future__ import annotations

import copy
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / ".agents/scripts"))

import operation_store
import validate_request as validation
import validate_workspace as workspace
import variant_matrix

SOURCE = "e302ab982bc6714597983733d371e6bbbff0248c"
RULE = "acting.plan_bound"
SKILLS = ("acting-direction", "scene-craft", "blocking-map", "seedance-acting-console")


def read(relative):
    return (ROOT / relative).read_text()


class PerformanceAdoptionTests(unittest.TestCase):
    def test_complete_bundles_aliases_and_pinned_provenance(self):
        catalog = json.loads(read(".agents/catalog/skills.json"))["skills"]
        lock = json.loads(read("skills-lock.json"))["skills"]
        for name in (*SKILLS, "seedance-lens-presets"):
            with self.subTest(skill=name):
                entry = ROOT / ".agents/skills" / name / "SKILL.md"
                metadata, findings = workspace.validate_skill(entry)
                self.assertEqual(findings, [])
                self.assertEqual(catalog[name]["description"], metadata["description"])
                self.assertIn(SOURCE, catalog[name]["overlay_notes"])
                self.assertIn(SOURCE, lock[name]["sourceNotes"])
                self.assertEqual(lock[name]["computedHash"], hashlib.sha256(entry.read_bytes()).hexdigest())
                self.assertIsNone(catalog[name]["upstream_hash"])
                self.assertTrue(workspace.load_evaluations(entry.parent / "evals/evals.json"))
                alias = ROOT / ".claude/skills" / name
                self.assertTrue(alias.is_symlink())
                self.assertEqual(alias.readlink(), Path("../../.agents/skills") / name)
        self.assertTrue((ROOT / ".agents/skills/acting-direction/references/performance-plan.md").is_file())
        self.assertTrue((ROOT / ".agents/skills/seedance-lens-presets/references/anamorphic-treatment.md").is_file())

    def test_excluded_bundle_rules_and_retired_routes_are_absent(self):
        forbidden = ("seedance-fight-choreography", "fight.readable_exchange",
                     "tig-scene-engine", "tig-blocking-map")
        paths = [ROOT / "AGENTS.md", ROOT / "README.md", ROOT / "skills-lock.json"]
        paths.extend(path for path in (ROOT / ".agents").rglob("*")
                     if path.is_file() and path.suffix in {".md", ".json", ".yaml", ".py"})
        for token in forbidden:
            with self.subTest(token=token):
                self.assertFalse((ROOT / ".agents/skills" / token).exists())
                self.assertFalse((ROOT / ".claude/skills" / token).is_symlink())
                self.assertEqual([str(path.relative_to(ROOT)) for path in paths if token in path.read_text()], [])

    def test_performance_is_integrated_without_importing_cinema_departments(self):
        for relative in (
            "AGENTS.md", ".agents/contracts/production-policy.md",
            ".agents/skills/film-production/SKILL.md",
            ".agents/skills/prompt-review/SKILL.md",
            ".agents/skills/ad-localize/SKILL.md",
            ".agents/skills/ad-variant-matrix/SKILL.md",
            ".agents/skills/seedance-prompt-25/SKILL.md",
        ):
            with self.subTest(path=relative):
                self.assertIn(RULE, read(relative))
        rules = json.loads(read(".agents/contracts/rules.json"))["rules"]
        owned = [rule for rule in rules if rule["owner_path"] == ".agents/contracts/performance-direction.md"]
        self.assertEqual([rule["id"] for rule in owned], [RULE])
        for name in ("editorial-review", "production-localize", "story-development", "sound-post"):
            self.assertFalse((ROOT / ".agents/skills" / name).exists())

    def test_contract_keeps_marketing_locks_and_scoped_non_applicability(self):
        contract = " ".join(read(".agents/contracts/performance-direction.md").split())
        for token in ("may_change", "must_preserve", "exact copy", "CTA", "supported",
                      "library.pin_current", "L3", "L5", "localize.native_review",
                      "budget", "deterministic", "review_mode", "approval_mode",
                      "not_applicable", "--required-rule", "SHA-256"):
            self.assertIn(token, contract)
        self.assertIn("Source-preserving edits inherit performance", contract)
        self.assertIn("intentional stillness", contract)
        self.assertIn('resolution: "480p"', contract)
        self.assertIn("draft: true", contract)

    def test_source_evals_cover_preservation_quiet_work_and_conditional_optics(self):
        for name, terms in {
            "acting-direction": ("observational", "relight", "unconscious"),
            "seedance-acting-console": ("source-preserving", "Spanish", "unconscious"),
            "scene-craft": ("observational", "framework"),
            "seedance-lens-presets": ("21:9", "deep-focus", "blue"),
        }.items():
            cases = workspace.load_evaluations(ROOT / ".agents/skills" / name / "evals/evals.json")
            for term in terms:
                self.assertTrue(any(term.lower() in case["prompt"].lower() and case["assertions"] for case in cases))

    def test_coverage_examples_and_evals_allow_intentional_stillness(self):
        directory = ".agents/skills/seedance-shot-design"
        for relative in ("SKILL.md", "references/coverage-patterns.md",
                         "references/shot-plan-format.md", "references/worked-repairs.md"):
            text = read(f"{directory}/{relative}")
            self.assertIn("intentional stillness", text.lower(), relative)
        cases = workspace.load_evaluations(ROOT / directory / "evals/evals.json")
        for case in cases:
            combined = " ".join([case["expected_output"], *case["assertions"]]).lower()
            self.assertNotIn("exactly one", combined)
            self.assertNotIn("at least two of", combined)
            self.assertNotIn("within 20%", combined)
        quiet = [case for case in cases if "performance_hold" in case["prompt"]]
        self.assertTrue(quiet)
        self.assertTrue(any("no turn" in case["prompt"].lower() for case in quiet))


class PerformanceGateTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="marketing-performance-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / "studio").mkdir()
        (self.root / "project.md").write_text("---\napproval_mode: approve_for_me\n---\n")
        prompt = b"Presenter waits for the listener, keeping the exact approved line.\n"
        (self.root / "prompt.md").write_bytes(prompt)
        self.request = {
            "schema_version": 2, "operation_id": "performance-fixture-v01",
            "asset_id": "s01_sh010_t01_v01", "transport": "ark-mcp",
            "model": "dreamina-seedance-2-5-260628", "operation": "generate",
            "approval_mode": "approve_for_me",
            "project_sha256": hashlib.sha256((self.root / "project.md").read_bytes()).hexdigest(),
            "prompt_file": "prompt.md", "prompt_sha256": hashlib.sha256(prompt).hexdigest(),
            "references": [], "params": {"resolution": "480p", "draft": True, "duration": 5},
            "submission_status": "prepared", "provider_task_id": None,
            "provider_status": None, "review_status": "not_started",
            "cost": {"estimated": None, "confirmed": None, "currency": "USD"},
        }
        self.request["request_sha256"] = validation.compute_request_hash(
            prompt, [], self.request["model"], "generate", self.request["params"],
            approval_mode="approve_for_me", project_sha256=self.request["project_sha256"],
        )
        self.caps = {
            "model": self.request["model"], "source": "synthetic offline fixture",
            "verified_at": "2026-10-27T00:00:00Z", "operations": ["generate"],
            "parameters": {"resolution": {"enum": ["480p"]}, "draft": {"const": True},
                           "duration": {"type": "integer"}},
            "reference_roles": [], "max_references": 0,
        }
        self.review = {
            "schema_version": 1, "request_sha256": self.request["request_sha256"],
            "reviewer_status": "complete",
            "checks": [{"rule_id": RULE, "status": "pass", "evidence": "Synthetic plan-bound check."}],
        }

    def test_real_registration_preserves_request_and_never_submits(self):
        before = copy.deepcopy(self.request)
        operation_store.prepare_operation(self.root, self.request, self.caps, self.review, [RULE])
        tasks = json.loads((self.root / "task_ids.json").read_text())["tasks"]
        self.assertEqual(tasks, [before])
        self.assertEqual(self.request, before)
        self.assertIsNone(tasks[0]["provider_task_id"])

    def test_missing_failed_empty_stale_duplicate_and_incomplete_reviews_block(self):
        for defect in ("absent", "missing", "fail", "not_applicable", "empty", "stale", "duplicate", "incomplete"):
            with self.subTest(defect=defect):
                review = copy.deepcopy(self.review)
                if defect == "absent":
                    review = None
                elif defect == "missing":
                    review["checks"] = []
                elif defect in ("fail", "not_applicable"):
                    review["checks"][0]["status"] = defect
                elif defect == "empty":
                    review["checks"][0]["evidence"] = " "
                elif defect == "stale":
                    review["request_sha256"] = "0" * 64
                elif defect == "duplicate":
                    review["checks"] *= 2
                else:
                    review["reviewer_status"] = "incomplete"
                with self.assertRaises(ValueError):
                    operation_store.prepare_operation(self.root, self.request, self.caps, review, [RULE])
                self.assertFalse((self.root / "task_ids.json").exists())

    def test_preservation_non_applicability_is_not_a_required_pass(self):
        self.review["checks"][0].update(status="not_applicable", evidence="Product-only swap keeps source performance.")
        self.assertEqual(validation.validate_review(self.review, self.request["request_sha256"], []), [])
        self.assertTrue(validation.validate_review(self.review, self.request["request_sha256"], [RULE]))

    def test_variant_performance_scope_is_independent_of_camera_and_review_depth(self):
        for mode in ("default", "strict"):
            for exemption in (None, "static-by-design format: ugc"):
                self.assertIn(RULE, variant_matrix.step_rules("hook-opening", exemption, mode, "character"))
                self.assertNotIn(RULE, variant_matrix.step_rules("hook-opening", exemption, mode, "non-performance"))
            for route in ("object-swap", "motion-recast", "language-dub"):
                self.assertNotIn(RULE, variant_matrix.step_rules(route, "source preserved", mode, "character"))


if __name__ == "__main__":
    unittest.main()
