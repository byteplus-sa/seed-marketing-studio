from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / ".agents/contracts/ad-compliance.md"
RULES = ROOT / ".agents/contracts/rules.json"
CHECKLIST = ROOT / ".agents/skills/prompt-review/references/checklist-ad-compliance.md"
PROMPT_REVIEW = ROOT / ".agents/skills/prompt-review/SKILL.md"
PROVENANCE = ROOT / ".agents/skills/prompt-review/references/rule-provenance.json"
CREATIVE_CHECK = ROOT / ".agents/skills/ad-creative-check/SKILL.md"
AD_RULES = (
    "ad.claims_supported",
    "ad.no_fabricated_testimonial",
    "ad.disclosure_recorded",
    "brand.copy_rules",
    "ad.safe_zone",
)
RULE_KEYS = {"id", "severity", "applies_to", "owner_path", "summary", "exceptions"}


def rules_by_id() -> dict[str, dict]:
    return {rule["id"]: rule for rule in json.loads(RULES.read_text())["rules"]}


class AdComplianceRuleTests(unittest.TestCase):
    def test_ad_rules_exist_with_the_catalog_shape(self) -> None:
        rules = rules_by_id()
        for rule_id in AD_RULES:
            with self.subTest(rule_id=rule_id):
                rule = rules[rule_id]
                self.assertEqual(set(rule), RULE_KEYS)
                self.assertIn(rule["severity"], ("error", "warning"))
                self.assertTrue(rule["applies_to"])
                self.assertTrue(rule["summary"].strip())
                self.assertIsInstance(rule["exceptions"], list)

    def test_ad_rule_owners_resolve_to_files(self) -> None:
        rules = rules_by_id()
        for rule_id in AD_RULES:
            with self.subTest(rule_id=rule_id):
                self.assertTrue((ROOT / rules[rule_id]["owner_path"]).is_file())

    def test_rule_ids_stay_unique(self) -> None:
        identifiers = [rule["id"] for rule in json.loads(RULES.read_text())["rules"]]
        self.assertEqual(len(identifiers), len(set(identifiers)))

    def test_owner_contract_and_checklist_name_every_rule(self) -> None:
        contract = CONTRACT.read_text()
        checklist = CHECKLIST.read_text()
        for rule_id in AD_RULES:
            with self.subTest(rule_id=rule_id):
                self.assertIn(f"`{rule_id}`", contract)
                self.assertIn(f"`{rule_id}`", checklist)

    def test_prompt_review_routes_to_the_checklist_and_registers_the_rules(self) -> None:
        skill = PROMPT_REVIEW.read_text()
        self.assertIn("`checklist-ad-compliance.md`", skill)
        provenance = set(json.loads(PROVENANCE.read_text())["rule_ids"])
        self.assertTrue(set(AD_RULES).issubset(provenance))
        for rule_id in AD_RULES:
            self.assertIn(f"`{rule_id}`", skill)


class AdComplianceContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.contract = CONTRACT.read_text()

    def test_legal_data_is_dated_sourced_and_not_legal_advice(self) -> None:
        self.assertIn("2026-10-17", self.contract)
        self.assertIn("Not legal advice", self.contract)
        self.assertIn("re-verify", self.contract.lower())
        rows = [
            line for line in self.contract.splitlines()
            if re.match(r"^\| `(us|tiktok|meta|google)-", line)
        ]
        self.assertGreaterEqual(len(rows), 5)
        for row in rows:
            with self.subTest(row=row[:40]):
                self.assertRegex(row, r"\(https://[^)\s]+\)")

    def test_disclosure_is_asked_per_paid_deliverable_and_internal_reels_stay_label_free(self) -> None:
        self.assertIn("The agent asks, never assumes", self.contract)
        self.assertIn("Internal reels stay label-free", self.contract)
        self.assertIn('"decided_by": "user"', self.contract)

    def test_schema_references_name_sibling_contract_files(self) -> None:
        self.assertIn(".agents/contracts/schemas/product-facts.schema.json", self.contract)
        self.assertIn(".agents/contracts/schemas/brand-kit.schema.json", self.contract)

    def test_creative_check_disclaims_performance_prediction(self) -> None:
        text = CREATIVE_CHECK.read_text()
        self.assertIn("This is not a prediction", text)
        self.assertIn("name: ad-creative-check", text)


if __name__ == "__main__":
    unittest.main()
