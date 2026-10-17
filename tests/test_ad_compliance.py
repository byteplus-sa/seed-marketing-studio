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
CHECKLIST_INDEX = ROOT / ".agents/skills/prompt-review/references/review-checklists.md"
SHARED_LIBRARY = ROOT / ".agents/contracts/shared-library.md"
AD_PLATFORMS = ROOT / ".agents/contracts/ad-platforms.md"
PROMPT_STAGES = ("ad_copy", "narrative_video", "static_image")
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


class RuleCitationTests(unittest.TestCase):
    def test_contract_owned_rules_are_cited_in_their_owner_file(self) -> None:
        rules = rules_by_id()
        for rule_id, owner in (
            ("library.pin_current", SHARED_LIBRARY),
            ("talent.authorized", SHARED_LIBRARY),
            ("delivery.safe_zone_unpublished", AD_PLATFORMS),
            ("delivery.specs_reverify", AD_PLATFORMS),
            ("brand.no_generated_logo", CONTRACT),
        ):
            with self.subTest(rule_id=rule_id):
                self.assertIn(rule_id, rules)
                self.assertIn(f"`{rule_id}`", owner.read_text())

    def test_rules_reviewed_on_prompts_apply_to_prompt_stages(self) -> None:
        rules = rules_by_id()
        for rule_id in ("ad.disclosure_recorded", "ad.safe_zone"):
            with self.subTest(rule_id=rule_id):
                self.assertTrue(set(PROMPT_STAGES).issubset(rules[rule_id]["applies_to"]))
                self.assertIn("ad_delivery", rules[rule_id]["applies_to"])

    def test_logo_rule_allows_only_reference_carried_marks(self) -> None:
        summary = rules_by_id()["brand.no_generated_logo"]["summary"]
        self.assertIn("post overlays", summary)
        self.assertIn("bound acquired product reference", summary)
        self.assertIn("defect", summary)


class ReviewChecklistTests(unittest.TestCase):
    def setUp(self) -> None:
        self.checklist = CHECKLIST.read_text()

    def test_checklist_disclaims_legal_advice(self) -> None:
        self.assertIn("Not legal advice; re-verify", self.checklist)

    def test_missing_inputs_use_reviewer_status_not_a_check_status(self) -> None:
        self.assertIn("`reviewer_status: incomplete`", self.checklist)
        self.assertNotIn("checks `incomplete`", self.checklist)

    def test_untraceable_logo_request_is_critical(self) -> None:
        item = self.checklist.split("9. **Marks and logos")[1].split("## ")[0]
        self.assertIn("CRITICAL", item)
        self.assertNotIn("MAJOR", item)
        self.assertIn("`brand.no_generated_logo`", item)

    def test_index_lists_the_ad_checklist(self) -> None:
        self.assertIn("[Ad compliance](checklist-ad-compliance.md)", CHECKLIST_INDEX.read_text())

    def test_product_shot_prompts_route_to_seedream_checklists(self) -> None:
        row = next(
            line for line in PROMPT_REVIEW.read_text().splitlines()
            if "`prompt_product_*`" in line
        )
        self.assertIn("`checklist-seedream.md`", row)


class ReferenceDataTests(unittest.TestCase):
    def setUp(self) -> None:
        self.contract = CONTRACT.read_text()

    def row(self, rule: str) -> str:
        return next(line for line in self.contract.splitlines() if line.startswith(f"| `{rule}`"))

    def test_reference_data_is_marked_non_exhaustive(self) -> None:
        self.assertIn("Non-exhaustive; other jurisdictions (e.g. EU, India)", self.contract)

    def test_meta_row_keeps_the_source_conflict_visible(self) -> None:
        row = self.row("meta-ai-info")
        self.assertIn("meta.com/en-gb/help/artificial-intelligence/355108217670024", row)
        self.assertIn("about.fb.com/news/2025/02/gen-ai-transparency-metas-ads-products", row)
        self.assertIn("**not** labelled", row)
        self.assertIn("may carry no Meta label", row)

    def test_new_york_row_cites_the_statute_and_its_exemptions(self) -> None:
        row = self.row("us-ny-gbl-396-b")
        self.assertIn("nysenate.gov/legislation/bills/2025/S8420/amendment/A", row)
        self.assertNotIn("for New York audiences", row)
        self.assertIn("not recognizable as any identifiable natural performer", row)
        self.assertIn("expressive works", row)
        self.assertIn("publish or broadcast", row)

    def test_google_row_says_the_label_does_not_ensure_compliance(self) -> None:
        row = self.row("google-ai-label")
        self.assertIn("does not by itself ensure compliance", row)
        self.assertIn("Google's own AI", row)

    def test_perishable_window_points_to_product_intake_default(self) -> None:
        self.assertIn("24 hours by default unless the brief records another window", self.contract)

    def test_campaigns_record_their_own_library_acceptance(self) -> None:
        library = SHARED_LIBRARY.read_text()
        self.assertIn("never inherits the library entry's approval", library)
        self.assertIn("quotes the user's own chat words", library)
        self.assertNotIn("whose own approval record stands", library)


if __name__ == "__main__":
    unittest.main()
