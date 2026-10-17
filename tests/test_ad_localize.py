from __future__ import annotations

import ast
import contextlib
import hashlib
import importlib.util
import io
import json
import re
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Any

from ruamel.yaml import YAML

ROOT = Path(__file__).resolve().parents[1]
SKILL_DIR = ROOT / ".agents/skills/ad-localize"
SCRIPT = SKILL_DIR / "scripts/market_card.py"
SPEC = importlib.util.spec_from_file_location("market_card", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)

MARKET_FIELDS = (
    "languages",
    "subtitle_languages",
    "casting_notes",
    "settings_notes",
    "props_wardrobe_notes",
    "gestures_and_taboos",
    "units",
    "legal_lines",
    "placements",
)
PENDING_REVIEWER = {
    "role": "native_speaker",
    "name": None,
    "status": "pending",
    "decision_ref": None,
    "evidence": None,
}


def run(*argv: str) -> tuple[int, dict[str, Any]]:
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        code = MODULE.main(list(argv))
    return code, json.loads(buffer.getvalue())


def rule_ids(document: dict[str, Any], key: str = "findings") -> list[str]:
    return [finding["rule_id"] for finding in document[key]]


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


class MarketCardTestCase(unittest.TestCase):
    def setUp(self) -> None:
        directory = tempfile.TemporaryDirectory(prefix="ad-localize-test-")
        self.addCleanup(directory.cleanup)
        self.campaign = Path(directory.name) / "projects" / "trail-bottle-launch"
        self.campaign.mkdir(parents=True)

    def init_card(self, market_id: str = "north-coast") -> Path:
        code, document = run("init", str(self.campaign), market_id, "--label", "North Coast")
        self.assertEqual(code, 0, document)
        return Path(document["card"])

    def complete_card(self, **overrides: Any) -> Path:
        path = self.init_card()
        card = json.loads(path.read_text())
        card.update(
            {
                "languages": [
                    {"code": "es-419", "variety": "neutral regional", "register": "informal", "direction": "ltr"}
                ],
                "subtitle_languages": ["es-419"],
                "casting_notes": "User: one presenter in their thirties, outdoor guide look",
                "settings_notes": "User: keep the trailhead",
                "props_wardrobe_notes": "User: plain rain shell",
                "gestures_and_taboos": "User: no thumbs-up close-up",
                "currency": {"code": "XTS", "symbol": "¤", "format": "{symbol} {amount}"},
                "number_and_date_formats": {"number": "1.234,56", "date": "DD/MM/YYYY"},
                "units": "metric",
                "facts_ref": "projects/trail-bottle-launch-north-coast/elements/trail-bottle/facts.json",
                "price_source": "f07",
                "legal_lines": [{"text": "Synthetic legal line", "when": "price shown", "source": "user"}],
                "ai_disclosure": {"jurisdictions": ["US-NY"], "decision_refs": []},
                "placements": ["meta-instagram-reels"],
                "level_default": "L1",
                "missing": [],
            }
        )
        card.update(overrides)
        path.write_text(json.dumps(card, indent=2, ensure_ascii=False))
        return path

    def edit(self, path: Path, **changes: Any) -> None:
        card = json.loads(path.read_text())
        card.update(changes)
        path.write_text(json.dumps(card, indent=2, ensure_ascii=False))

    def fingerprint(self, path: Path) -> dict[str, Any]:
        code, document = run("fingerprint", str(path))
        self.assertEqual(code, 0, document)
        return document

    def approve(self, path: Path, mode: str = "approve_for_me", actor: str = "agent") -> None:
        decision = path.parent / "decisions/card_approval.json"
        decision.write_text(json.dumps({"decision": "approved"}))
        card_sha256 = self.fingerprint(path)["card_sha256"]
        self.edit(
            path,
            status="approved",
            approval={
                "mode": mode,
                "actor": actor,
                "decision_ref": "decisions/card_approval.json",
                "decided_at": "2026-10-17T10:00:00Z",
                "card_sha256": card_sha256,
            },
        )

    def write_inventory(self, path: Path, rows: list[tuple[str, str]]) -> None:
        lines = ["# Inventory", "", "| id | kind | level | route |", "| --- | --- | --- | --- |"]
        lines.extend(f"| {element} | super | {level} | overlay |" for element, level in rows)
        (path.parent / "inventory.md").write_text("\n".join(lines) + "\n")

    def sign_off(self, path: Path, evidence: str = "Reviewer: the Spanish reads naturally.", **record_overrides: Any) -> Path:
        card_dir = path.parent
        (card_dir / "translation.md").write_text("| id | level | source | target |\n")
        if not (card_dir / "inventory.md").exists():
            (card_dir / "inventory.md").write_text("| id | level |\n")
        fingerprint = self.fingerprint(path)
        record = {
            "schema_version": 1,
            "market_id": "north-coast",
            "reviewer_role": "native_speaker",
            "reviewer_name": None,
            "decided_by": "reviewer",
            "evidence": evidence,
            "reviewed": [
                {"path": name, "sha256": sha256_text((card_dir / name).read_text())}
                for name in ("translation.md", "inventory.md")
            ],
            "card_fields_sha256": fingerprint["review_fields_sha256"],
            "decided_at": "2026-10-17T11:00:00Z",
        }
        record.update(record_overrides)
        record_path = card_dir / "decisions/native_review.json"
        record_path.write_text(json.dumps(record))
        card = json.loads(path.read_text())
        card["reviewer"] = {
            "role": "native_speaker",
            "name": None,
            "status": "signed_off",
            "decision_ref": "decisions/native_review.json",
            "evidence": evidence,
        }
        path.write_text(json.dumps(card))
        return record_path

    def gate(self, path: Path, level: str, stage: str = "final", *extra: str) -> tuple[int, dict[str, Any]]:
        return run("gate", str(path), "--level", level, "--stage", stage, *extra)


class InitTests(MarketCardTestCase):
    def test_init_scaffolds_a_valid_draft_with_every_market_value_unknown(self) -> None:
        path = self.init_card()
        self.assertEqual(path, self.campaign / "markets/north-coast/market.json")
        self.assertTrue((path.parent / "decisions").is_dir())
        card = json.loads(path.read_text())
        self.assertEqual(card["campaign"], "trail-bottle-launch")
        self.assertEqual(card["status"], "draft")
        self.assertEqual(card["reviewer"]["status"], "none")
        self.assertIsNone(card["level_default"])
        for field in MARKET_FIELDS:
            self.assertIsNone(card[field], field)
            self.assertIn(field, card["missing"])
        code, document = run("validate", str(path))
        self.assertEqual(code, 0, document)
        self.assertEqual(document["findings"], [])

    def test_init_refuses_an_existing_card(self) -> None:
        self.init_card()
        code, document = run("init", str(self.campaign), "north-coast")
        self.assertEqual(code, 1)
        self.assertIn("already exists", document["error"])

    def test_init_refuses_a_non_kebab_market_id(self) -> None:
        code, document = run("init", str(self.campaign), "North_Coast")
        self.assertEqual(code, 1)
        self.assertIn("kebab-case", document["error"])
        self.assertFalse((self.campaign / "markets").exists())

    def test_init_refuses_a_missing_campaign_directory(self) -> None:
        code, document = run("init", str(self.campaign.parent / "absent"), "north-coast")
        self.assertEqual(code, 1)
        self.assertIn("not a campaign project directory", document["error"])


class ValidateTests(MarketCardTestCase):
    def test_complete_card_is_valid(self) -> None:
        code, document = run("validate", str(self.complete_card()))
        self.assertEqual(code, 0, document)
        self.assertEqual(document["findings"], [])

    def test_malformed_language_tags_are_rejected_as_bcp47(self) -> None:
        for bad in ("english", "en_US", "e", "es-"):
            with self.subTest(code=bad):
                path = self.complete_card()
                self.edit(
                    path,
                    languages=[{"code": bad, "variety": None, "register": None, "direction": "ltr"}],
                    missing=["languages.0.register", "languages.0.variety"],
                )
                code, document = run("validate", str(path))
                self.assertEqual(code, 1)
                self.assertIn("market.bcp47", rule_ids(document))
                path.unlink()
                path.parent.joinpath("decisions").rmdir()
                path.parent.rmdir()

    def test_bad_subtitle_language_is_rejected_as_bcp47(self) -> None:
        path = self.complete_card(subtitle_languages=["es-419", "spanish_latam"])
        code, document = run("validate", str(path))
        self.assertEqual(code, 1)
        self.assertIn("market.bcp47", rule_ids(document))

    def test_valid_language_tags_with_script_and_region_pass(self) -> None:
        path = self.complete_card(
            languages=[
                {"code": "zh-Hant-TW", "variety": "v", "register": "r", "direction": "ltr"},
                {"code": "sr-Latn", "variety": "v", "register": "r", "direction": "ltr"},
                {"code": "ar", "variety": "v", "register": "r", "direction": "rtl"},
            ],
            subtitle_languages=["zh-Hant-TW", "ar"],
        )
        code, document = run("validate", str(path))
        self.assertEqual(code, 0, document)

    def test_right_to_left_language_marked_ltr_is_rejected(self) -> None:
        path = self.complete_card(
            languages=[{"code": "ar", "variety": "v", "register": "r", "direction": "ltr"}]
        )
        code, document = run("validate", str(path))
        self.assertEqual(code, 1)
        self.assertIn("market.direction", rule_ids(document))

    def test_script_subtag_decides_direction(self) -> None:
        path = self.complete_card(
            languages=[{"code": "pa-Arab", "variety": "v", "register": "r", "direction": "ltr"}]
        )
        code, document = run("validate", str(path))
        self.assertEqual(code, 1)
        self.assertIn("market.direction", rule_ids(document))

    def test_left_to_right_language_marked_rtl_is_a_warning(self) -> None:
        path = self.complete_card(
            languages=[{"code": "en", "variety": "v", "register": "r", "direction": "rtl"}]
        )
        code, document = run("validate", str(path))
        self.assertEqual(code, 0, document)
        warnings = [f for f in document["findings"] if f["rule_id"] == "market.direction"]
        self.assertEqual([w["severity"] for w in warnings], ["warning"])

    def test_unknown_placement_id_is_rejected(self) -> None:
        path = self.complete_card(placements=["meta-instagram-reels", "billboard-network"])
        code, document = run("validate", str(path))
        self.assertEqual(code, 1)
        finding = next(f for f in document["findings"] if f["rule_id"] == "market.placement_known")
        self.assertEqual(finding["path"], "placements.1")

    def test_signed_off_reviewer_without_decision_ref_is_rejected(self) -> None:
        path = self.complete_card(
            reviewer={
                "role": "native_speaker",
                "name": None,
                "status": "signed_off",
                "decision_ref": None,
                "evidence": "Reviewer: approved.",
            }
        )
        code, document = run("validate", str(path))
        self.assertEqual(code, 1)
        paths = [f["path"] for f in document["findings"] if f["rule_id"] == "market.reviewer_record"]
        self.assertEqual(paths, ["reviewer.decision_ref"])

    def test_signed_off_reviewer_without_quoted_evidence_is_rejected(self) -> None:
        path = self.complete_card(
            reviewer={
                "role": "local_reviewer",
                "name": None,
                "status": "signed_off",
                "decision_ref": "decisions/native_review.json",
                "evidence": None,
            }
        )
        code, document = run("validate", str(path))
        self.assertEqual(code, 1)
        self.assertIn("market.reviewer_record", rule_ids(document))

    def test_reviewed_level_default_without_reviewer_warns_in_draft(self) -> None:
        path = self.complete_card(level_default="L3")
        code, document = run("validate", str(path))
        self.assertEqual(code, 0, document)
        flagged = [f for f in document["findings"] if f["rule_id"] == "localize.native_review"]
        self.assertEqual([f["severity"] for f in flagged], ["warning"])

    def test_reviewed_level_default_without_reviewer_blocks_approved_card(self) -> None:
        path = self.complete_card(level_default="L4")
        self.approve(path)
        code, document = run("validate", str(path))
        self.assertEqual(code, 1)
        flagged = [f for f in document["findings"] if f["rule_id"] == "localize.native_review"]
        self.assertEqual([f["severity"] for f in flagged], ["error"])

    def test_low_level_default_needs_no_reviewer(self) -> None:
        path = self.complete_card(level_default="L2")
        self.approve(path)
        code, document = run("validate", str(path))
        self.assertEqual(code, 0, document)
        self.assertNotIn("localize.native_review", rule_ids(document))

    def test_silent_unknown_value_must_be_listed_in_missing(self) -> None:
        path = self.complete_card(casting_notes=None)
        code, document = run("validate", str(path))
        self.assertEqual(code, 1)
        finding = next(f for f in document["findings"] if f["rule_id"] == "market.missing_listed")
        self.assertEqual(finding["path"], "casting_notes")

    def test_price_without_facts_file_or_currency_is_rejected(self) -> None:
        path = self.complete_card(
            facts_ref=None,
            currency={"code": None, "symbol": None, "format": None},
            missing=["currency.code", "currency.format", "currency.symbol", "facts_ref"],
        )
        code, document = run("validate", str(path))
        self.assertEqual(code, 1)
        paths = sorted(f["path"] for f in document["findings"] if f["rule_id"] == "market.price_fact")
        self.assertEqual(paths, ["currency.code", "facts_ref"])

    def test_market_id_must_match_its_directory(self) -> None:
        path = self.complete_card(market_id="south-coast")
        code, document = run("validate", str(path))
        self.assertEqual(code, 1)
        self.assertIn("market.id_matches_directory", rule_ids(document))

    def test_campaign_must_match_its_directory(self) -> None:
        path = self.complete_card(campaign="other-campaign")
        code, document = run("validate", str(path))
        self.assertEqual(code, 1)
        self.assertIn("market.campaign_matches_directory", rule_ids(document))

    def test_approved_card_needs_an_approval_record(self) -> None:
        path = self.complete_card(status="approved")
        code, document = run("validate", str(path))
        self.assertEqual(code, 1)
        self.assertIn("market.schema", rule_ids(document))

    def test_invalid_json_and_symlinked_card_are_errors(self) -> None:
        path = self.init_card()
        path.write_text("{not json")
        code, document = run("validate", str(path))
        self.assertEqual(code, 1)
        self.assertIn("not valid JSON", document["error"])
        link = path.parent / "linked.json"
        link.symlink_to(path)
        code, document = run("validate", str(link))
        self.assertEqual(code, 1)
        self.assertIn("not a regular file", document["error"])


class GateTests(MarketCardTestCase):
    def test_l1_final_passes_on_an_approved_card_without_reviewer(self) -> None:
        path = self.complete_card()
        self.approve(path)
        code, document = run("gate", str(path), "--level", "L1", "--stage", "final")
        self.assertEqual(code, 0, document)
        self.assertEqual(document["output_project"], "projects/trail-bottle-launch-north-coast")

    def test_l3_draft_is_allowed_before_sign_off(self) -> None:
        path = self.complete_card(level_default="L3")
        code, document = run("gate", str(path), "--level", "L3", "--stage", "draft")
        self.assertEqual(code, 0, document)

    def test_l3_final_is_blocked_without_sign_off(self) -> None:
        path = self.complete_card(
            level_default="L3",
            reviewer={"role": "native_speaker", "name": None, "status": "pending", "decision_ref": None, "evidence": None},
        )
        self.approve(path)
        code, document = run("gate", str(path), "--level", "L3", "--stage", "final")
        self.assertEqual(code, 1)
        self.assertEqual(rule_ids(document, "blockers"), ["localize.native_review"])

    def test_l3_final_passes_with_a_hash_bound_sign_off(self) -> None:
        path = self.complete_card(level_default="L3", reviewer=PENDING_REVIEWER)
        self.approve(path)
        self.sign_off(path)
        code, document = run("gate", str(path), "--level", "L3", "--stage", "final")
        self.assertEqual(code, 0, document)

    def test_sign_off_goes_stale_when_a_reviewed_file_changes(self) -> None:
        path = self.complete_card(level_default="L5", reviewer=PENDING_REVIEWER)
        self.approve(path)
        self.sign_off(path)
        (path.parent / "translation.md").write_text("| id | source | target |\n| l01 | a | b |\n")
        code, document = run("gate", str(path), "--level", "L5", "--stage", "final")
        self.assertEqual(code, 1)
        self.assertTrue(any("stale" in b["message"] for b in document["blockers"]))

    def test_sign_off_record_outside_the_card_directory_is_refused(self) -> None:
        path = self.complete_card(level_default="L3", reviewer=PENDING_REVIEWER)
        self.approve(path)
        self.sign_off(path)
        card = json.loads(path.read_text())
        card["reviewer"]["decision_ref"] = "../../../outside.json"
        path.write_text(json.dumps(card))
        code, document = run("gate", str(path), "--level", "L3", "--stage", "final")
        self.assertEqual(code, 1)
        self.assertEqual(rule_ids(document, "blockers"), ["localize.native_review"])

    def test_draft_card_blocks_final(self) -> None:
        path = self.complete_card()
        code, document = run("gate", str(path), "--level", "L2", "--stage", "final")
        self.assertEqual(code, 1)
        self.assertEqual(rule_ids(document, "blockers"), ["market.card_approved"])

    def test_cultural_level_needs_its_fields(self) -> None:
        path = self.complete_card(
            settings_notes=None, legal_lines=None, missing=["legal_lines", "settings_notes"]
        )
        code, document = run("gate", str(path), "--level", "L4", "--stage", "draft")
        self.assertEqual(code, 1)
        paths = sorted(b["path"] for b in document["blockers"])
        self.assertEqual(paths, ["legal_lines", "settings_notes"])

    def test_delivery_needs_placements_and_jurisdictions(self) -> None:
        path = self.complete_card(
            placements=None,
            ai_disclosure={"jurisdictions": None, "decision_refs": []},
            missing=["ai_disclosure.jurisdictions", "placements"],
        )
        self.approve(path)
        code, document = run("gate", str(path), "--level", "L1", "--stage", "delivery")
        self.assertEqual(code, 1)
        self.assertEqual(set(rule_ids(document, "blockers")), {"market.delivery_fields"})

    def test_show_lists_final_blockers_per_level(self) -> None:
        path = self.complete_card(
            subtitle_languages=["es-419"],
            languages=[{"code": "es-419", "variety": "v", "register": "r", "direction": "ltr"}],
        )
        self.approve(path)
        code, document = run("show", str(path))
        self.assertEqual(code, 0, document)
        self.assertEqual(document["caption_codes"], ["es-419"])
        self.assertEqual(document["final_gate"]["L1"], [])
        self.assertTrue(document["final_gate"]["L3"])

    def test_invalid_card_cannot_be_gated(self) -> None:
        path = self.complete_card(placements=["unknown-placement"])
        code, document = run("gate", str(path), "--level", "L1")
        self.assertEqual(code, 1)
        self.assertIn("market.placement_known", rule_ids(document))


class ReviewRecordTests(MarketCardTestCase):
    def signed_card(self, level: str = "L3") -> Path:
        path = self.complete_card(level_default=level, reviewer=PENDING_REVIEWER)
        self.approve(path)
        return path

    def assert_review_blocked(self, path: Path, fragment: str, level: str = "L3") -> None:
        code, document = self.gate(path, level)
        self.assertEqual(code, 1, document)
        self.assertIn("localize.native_review", rule_ids(document, "blockers"))
        messages = " ".join(b["message"] for b in document["blockers"])
        self.assertIn(fragment, messages)

    def test_record_that_omits_the_translation_sheet_is_refused(self) -> None:
        path = self.signed_card()
        record_path = self.sign_off(path)
        record = json.loads(record_path.read_text())
        record["reviewed"] = [entry for entry in record["reviewed"] if entry["path"] != "translation.md"]
        record_path.write_text(json.dumps(record))
        self.assert_review_blocked(path, "translation.md")

    def test_record_that_omits_the_inventory_is_refused(self) -> None:
        path = self.signed_card()
        record_path = self.sign_off(path)
        record = json.loads(record_path.read_text())
        record["reviewed"] = [entry for entry in record["reviewed"] if entry["path"] != "inventory.md"]
        record_path.write_text(json.dumps(record))
        self.assert_review_blocked(path, "inventory.md")

    def test_record_for_another_market_is_refused(self) -> None:
        path = self.signed_card()
        self.sign_off(path, market_id="south-coast")
        self.assert_review_blocked(path, "market_id")

    def test_record_from_another_reviewer_role_is_refused(self) -> None:
        path = self.signed_card()
        self.sign_off(path, reviewer_role="local_reviewer")
        self.assert_review_blocked(path, "reviewer_role")

    def test_agent_decided_record_is_refused(self) -> None:
        path = self.signed_card()
        self.sign_off(path, decided_by="agent")
        self.assert_review_blocked(path, "decided_by")

    def test_record_without_decided_by_is_refused(self) -> None:
        path = self.signed_card()
        record_path = self.sign_off(path)
        record = json.loads(record_path.read_text())
        del record["decided_by"]
        record_path.write_text(json.dumps(record))
        self.assert_review_blocked(path, "decided_by")

    def test_record_with_blank_evidence_is_refused(self) -> None:
        path = self.signed_card()
        self.sign_off(path, evidence="Reviewer: fine.")
        record_path = path.parent / "decisions/native_review.json"
        record = json.loads(record_path.read_text())
        record["evidence"] = "   "
        record_path.write_text(json.dumps(record))
        self.assert_review_blocked(path, "evidence")

    def test_card_edit_to_a_reviewed_field_makes_the_sign_off_stale(self) -> None:
        for field, value in (
            ("casting_notes", "User: two presenters"),
            ("legal_lines", [{"text": "Another line", "when": "always", "source": "user"}]),
            ("currency", {"code": "XTS", "symbol": "¤", "format": "{amount} {symbol}"}),
        ):
            with self.subTest(field=field):
                path = self.signed_card()
                self.sign_off(path)
                self.edit(path, **{field: value})
                self.approve(path)
                self.assert_review_blocked(path, "stale")
                for child in sorted(path.parent.rglob("*"), reverse=True):
                    child.rmdir() if child.is_dir() else child.unlink()
                path.parent.rmdir()

    def test_card_edit_outside_the_reviewed_fields_keeps_the_sign_off(self) -> None:
        path = self.signed_card()
        self.sign_off(path)
        self.edit(path, placements=["meta-instagram-reels"], units="mixed")
        self.approve(path)
        code, document = self.gate(path, "L3")
        self.assertEqual(code, 0, document)

    def test_record_schema_is_published(self) -> None:
        schema = json.loads((ROOT / ".agents/contracts/schemas/native-review.schema.json").read_text())
        self.assertEqual(schema["properties"]["decided_by"]["enum"], ["user", "reviewer"])
        self.assertIn("card_fields_sha256", schema["required"])


class LevelTests(MarketCardTestCase):
    def test_lower_requested_level_is_raised_to_the_card_default(self) -> None:
        path = self.complete_card(level_default="L3", reviewer=PENDING_REVIEWER)
        self.approve(path)
        code, document = self.gate(path, "L1")
        self.assertEqual(code, 1, document)
        self.assertEqual(document["level"], "L3")
        self.assertEqual(document["requested_level"], "L1")
        self.assertIn("localize.native_review", rule_ids(document, "blockers"))

    def test_higher_requested_level_is_kept(self) -> None:
        path = self.complete_card(level_default="L1")
        self.approve(path)
        code, document = self.gate(path, "L4")
        self.assertEqual(code, 1, document)
        self.assertEqual(document["level"], "L4")

    def test_inventory_override_allows_a_lower_level_for_that_element(self) -> None:
        path = self.complete_card(level_default="L3", reviewer=PENDING_REVIEWER)
        self.write_inventory(path, [("super-01", "L1"), ("presenter", "L3")])
        self.approve(path)
        code, document = self.gate(path, "L1", "final", "--element", "super-01")
        self.assertEqual(code, 0, document)
        self.assertEqual(document["level"], "L1")

    def test_inventory_level_above_the_request_wins(self) -> None:
        path = self.complete_card(level_default="L1")
        self.write_inventory(path, [("presenter", "L3")])
        self.approve(path)
        code, document = self.gate(path, "L1", "final", "--element", "presenter")
        self.assertEqual(code, 1, document)
        self.assertEqual(document["level"], "L3")
        self.assertIn("localize.native_review", rule_ids(document, "blockers"))

    def test_element_missing_from_the_inventory_is_blocked(self) -> None:
        path = self.complete_card(level_default="L3", reviewer=PENDING_REVIEWER)
        self.write_inventory(path, [("presenter", "L3")])
        self.approve(path)
        code, document = self.gate(path, "L1", "final", "--element", "super-09")
        self.assertEqual(code, 1, document)
        self.assertIn("market.level_override", rule_ids(document, "blockers"))
        self.assertEqual(document["level"], "L3")

    def test_missing_inventory_with_element_is_blocked(self) -> None:
        path = self.complete_card(level_default="L3", reviewer=PENDING_REVIEWER)
        self.approve(path)
        code, document = self.gate(path, "L1", "final", "--element", "super-01")
        self.assertEqual(code, 1, document)
        self.assertIn("market.level_override", rule_ids(document, "blockers"))

    def test_malformed_inventory_levels_are_blocked(self) -> None:
        for rows in ([("super-01", "L9")], [("super-01", "L1"), ("super-01", "L2")]):
            with self.subTest(rows=rows):
                path = self.complete_card(level_default="L3", reviewer=PENDING_REVIEWER)
                self.write_inventory(path, rows)
                self.approve(path)
                code, document = self.gate(path, "L1", "final", "--element", "super-01")
                self.assertEqual(code, 1, document)
                self.assertIn("market.level_override", rule_ids(document, "blockers"))
                for child in sorted(path.parent.rglob("*"), reverse=True):
                    child.rmdir() if child.is_dir() else child.unlink()
                path.parent.rmdir()

    def test_inventory_table_parser_reads_id_and_level_columns(self) -> None:
        text = "Intro\n\n| `id` | kind | `level` |\n|---|---|---|\n| super-01 | super | L1 |\n| s01_sh010_l02 | spoken | l2 |\n"
        self.assertEqual(MODULE.inventory_levels(text), {"super-01": "L1", "s01_sh010_l02": "L2"})


class CardIntegrityTests(MarketCardTestCase):
    def test_subtitle_languages_unknown_blocks_l1(self) -> None:
        path = self.complete_card(subtitle_languages=None, missing=["subtitle_languages"])
        code, document = self.gate(path, "L1", "draft")
        self.assertEqual(code, 1, document)
        self.assertEqual([b["path"] for b in document["blockers"]], ["subtitle_languages"])

    def test_empty_subtitle_languages_satisfies_l1(self) -> None:
        path = self.complete_card(subtitle_languages=[])
        code, document = self.gate(path, "L1", "draft")
        self.assertEqual(code, 0, document)

    def test_facts_ref_must_live_in_the_localized_project(self) -> None:
        path = self.complete_card(facts_ref="projects/trail-bottle-launch/elements/trail-bottle/facts.json")
        code, document = run("validate", str(path))
        self.assertEqual(code, 1, document)
        finding = next(f for f in document["findings"] if f["rule_id"] == "market.price_fact")
        self.assertEqual(finding["path"], "facts_ref")

    def write_facts(self, status: str, fact_id: str = "f07") -> None:
        facts = Path(self.campaign.parent) / "trail-bottle-launch-north-coast/elements/trail-bottle/facts.json"
        facts.parent.mkdir(parents=True, exist_ok=True)
        facts.write_text(
            json.dumps(
                {
                    "facts": [
                        {"fact_id": fact_id, "kind": "price", "claim": "Price", "quote": "¤ 10", "status": status}
                    ]
                }
            )
        )

    def test_price_source_must_be_a_perishable_fact_when_the_facts_file_exists(self) -> None:
        path = self.complete_card()
        self.write_facts("supported")
        code, document = run("validate", str(path))
        self.assertEqual(code, 1, document)
        finding = next(f for f in document["findings"] if f["rule_id"] == "market.price_fact")
        self.assertEqual(finding["path"], "price_source")

    def test_price_source_absent_from_the_facts_file_is_rejected(self) -> None:
        path = self.complete_card()
        self.write_facts("perishable", fact_id="f01")
        code, document = run("validate", str(path))
        self.assertEqual(code, 1, document)
        self.assertIn("market.price_fact", rule_ids(document))

    def test_perishable_price_fact_passes(self) -> None:
        path = self.complete_card()
        self.write_facts("perishable")
        code, document = run("validate", str(path))
        self.assertEqual(code, 0, document)

    def test_ask_for_approval_needs_the_user_as_actor(self) -> None:
        path = self.complete_card()
        self.approve(path, mode="ask_for_approval", actor="agent")
        code, document = run("validate", str(path))
        self.assertEqual(code, 1, document)
        self.assertIn("market.schema", rule_ids(document))

    def test_ask_for_approval_by_the_user_passes(self) -> None:
        path = self.complete_card()
        self.approve(path, mode="ask_for_approval", actor="user")
        code, document = run("validate", str(path))
        self.assertEqual(code, 0, document)

    def test_approval_decision_record_must_exist(self) -> None:
        path = self.complete_card()
        self.approve(path)
        (path.parent / "decisions/card_approval.json").unlink()
        code, document = run("validate", str(path))
        self.assertEqual(code, 1, document)
        finding = next(f for f in document["findings"] if f["rule_id"] == "market.approval_record")
        self.assertEqual(finding["path"], "approval.decision_ref")

    def test_approval_without_card_hash_is_rejected(self) -> None:
        path = self.complete_card()
        self.approve(path)
        card = json.loads(path.read_text())
        del card["approval"]["card_sha256"]
        path.write_text(json.dumps(card))
        code, document = run("validate", str(path))
        self.assertEqual(code, 1, document)
        self.assertIn("market.schema", rule_ids(document))

    def test_card_edited_after_approval_returns_to_draft_at_the_gate(self) -> None:
        path = self.complete_card()
        self.approve(path)
        self.edit(path, settings_notes="User: change the trailhead")
        code, document = self.gate(path, "L1")
        self.assertEqual(code, 1, document)
        self.assertEqual(rule_ids(document, "blockers"), ["market.card_approved"])
        self.assertIn("changed after approval", document["blockers"][0]["message"])

    def test_recording_review_status_keeps_the_approval(self) -> None:
        path = self.complete_card()
        self.approve(path)
        card = json.loads(path.read_text())
        card["reviewer"].update({"role": None, "status": "none"})
        card["ai_disclosure"]["decision_refs"] = ["projects/x/delivery/disclosure_a.json"]
        path.write_text(json.dumps(card))
        code, document = self.gate(path, "L1")
        self.assertEqual(code, 0, document)

    def test_card_outside_a_markets_folder_is_rejected(self) -> None:
        path = self.complete_card()
        other = self.campaign / "elsewhere/north-coast"
        other.mkdir(parents=True)
        moved = other / "market.json"
        moved.write_text(path.read_text())
        code, document = run("validate", str(moved))
        self.assertEqual(code, 1, document)
        self.assertIn("market.campaign_matches_directory", rule_ids(document))

    def test_init_refuses_a_symlinked_markets_folder(self) -> None:
        outside = self.campaign.parent / "outside"
        outside.mkdir()
        (self.campaign / "markets").symlink_to(outside, target_is_directory=True)
        code, document = run("init", str(self.campaign), "north-coast")
        self.assertEqual(code, 1, document)
        self.assertIn("symlink", document["error"])
        self.assertEqual(list(outside.iterdir()), [])

    def test_init_refuses_a_symlinked_card_folder(self) -> None:
        outside = self.campaign.parent / "outside"
        outside.mkdir()
        (self.campaign / "markets").mkdir()
        (self.campaign / "markets/north-coast").symlink_to(outside, target_is_directory=True)
        code, document = run("init", str(self.campaign), "north-coast")
        self.assertEqual(code, 1, document)
        self.assertEqual(list(outside.iterdir()), [])

    def test_market_id_is_limited_to_48_characters(self) -> None:
        code, document = run("init", str(self.campaign), "a" * 49)
        self.assertEqual(code, 1, document)
        code, document = run("init", str(self.campaign), "a" * 48)
        self.assertEqual(code, 0, document)
        schema = json.loads((ROOT / ".agents/contracts/schemas/market-card.schema.json").read_text())
        self.assertEqual(schema["$defs"]["marketId"]["maxLength"], 48)

    def test_deeply_nested_json_is_a_clean_error(self) -> None:
        path = self.init_card()
        path.write_text("[" * 100000 + "]" * 100000)
        code, document = run("validate", str(path))
        self.assertEqual(code, 1)
        self.assertIn("too deeply nested", document["error"])


def captions_constant(name: str) -> Any:
    source = (ROOT / ".agents/skills/ad-captions/scripts/make_captions.py").read_text()
    for node in ast.parse(source).body:
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == name for t in node.targets):
            if isinstance(node.value, ast.Call):
                return ast.literal_eval(node.value.args[0])
            return ast.literal_eval(node.value)
    raise AssertionError(name)


class LanguageTagTests(MarketCardTestCase):
    def test_rtl_lists_match_ad_captions(self) -> None:
        self.assertEqual(set(MODULE.RTL_LANGUAGES), set(captions_constant("RTL_LANGUAGES")))
        self.assertEqual({s.lower() for s in MODULE.RTL_SCRIPTS}, set(captions_constant("RTL_SCRIPTS")))

    def test_card_tags_are_accepted_by_ad_captions(self) -> None:
        captions_pattern = re.compile(captions_constant("LANGUAGE_PATTERN"))
        schema = json.loads((ROOT / ".agents/contracts/schemas/market-card.schema.json").read_text())
        card_pattern = re.compile(schema["$defs"]["bcp47"]["pattern"])
        for tag in ("es-419", "zh-Hant-TW", "sr-Latn", "sl-rozaj", "de-CH-1996", "zh-yue-HK", "en-x-priv", "de-u-co-phonebk", "en-a-bbb"):
            with self.subTest(tag=tag):
                if card_pattern.fullmatch(tag):
                    self.assertTrue(captions_pattern.match(tag))
        for tag in ("en-x-priv", "de-u-co-phonebk"):
            self.assertIsNone(card_pattern.fullmatch(tag))

    def test_sindhi_is_right_to_left(self) -> None:
        path = self.complete_card(languages=[{"code": "sd", "variety": "v", "register": "r", "direction": "ltr"}])
        code, document = run("validate", str(path))
        self.assertEqual(code, 1, document)
        self.assertIn("market.direction", rule_ids(document))

    def test_deprecated_hebrew_and_yiddish_codes_are_rejected(self) -> None:
        for code_value, replacement in (("iw", "he"), ("ji", "yi")):
            with self.subTest(code=code_value):
                path = self.complete_card(
                    languages=[{"code": code_value, "variety": "v", "register": "r", "direction": "rtl"}],
                    subtitle_languages=[code_value],
                )
                code, document = run("validate", str(path))
                self.assertEqual(code, 1, document)
                flagged = [f for f in document["findings"] if f["rule_id"] == "market.bcp47"]
                self.assertEqual(
                    sorted(f["path"] for f in flagged), ["languages.0.code", "subtitle_languages.0"]
                )
                self.assertTrue(all(replacement in f["message"] for f in flagged))
                for child in sorted(path.parent.rglob("*"), reverse=True):
                    child.rmdir() if child.is_dir() else child.unlink()
                path.parent.rmdir()

    def test_script_detection_ignores_subtags_after_a_singleton(self) -> None:
        self.assertEqual(MODULE.expected_direction("en-x-arab"), (None, False))
        self.assertEqual(MODULE.expected_direction("ar-u-latn"), ("rtl", True))
        self.assertEqual(MODULE.expected_direction("pa-Arab-u-nu-latn"), ("rtl", True))


class VariantTests(MarketCardTestCase):
    def variant_card(self) -> Path:
        path = self.complete_card(level_default="L3", reviewer=PENDING_REVIEWER)
        self.approve(path)
        return path

    def variant_sign_off(self, path: Path, variant: str = "hook-a", **record_overrides: Any) -> Path:
        variant_dir = path.parent / variant
        (variant_dir / "decisions").mkdir(parents=True, exist_ok=True)
        (variant_dir / "translation.md").write_text(f"| id | level | source | target |\n| {variant} | L3 | a | b |\n")
        if not (variant_dir / "inventory.md").exists():
            (variant_dir / "inventory.md").write_text("| id | level |\n| --- | --- |\n| presenter | L3 |\n")
        code, fingerprint = run("fingerprint", str(path), "--variant", variant)
        self.assertEqual(code, 0, fingerprint)
        record = {
            "schema_version": 1,
            "market_id": "north-coast",
            "variant": variant,
            "reviewer_role": "native_speaker",
            "reviewer_name": None,
            "decided_by": "user",
            "evidence": "User: our reviewer approved the hook-a lines.",
            "reviewed": [{"path": name, "sha256": sha} for name, sha in fingerprint["files"].items()],
            "card_fields_sha256": fingerprint["review_fields_sha256"],
            "decided_at": "2026-10-17T12:00:00Z",
        }
        record.update(record_overrides)
        record_path = variant_dir / "decisions/native_review.json"
        record_path.write_text(json.dumps(record))
        return record_path

    def test_variant_sign_off_passes_its_own_gate(self) -> None:
        path = self.variant_card()
        self.variant_sign_off(path)
        code, document = self.gate(path, "L3", "final", "--variant", "hook-a")
        self.assertEqual(code, 0, document)
        self.assertEqual(document["variant"], "hook-a")
        self.assertEqual(document["output_project"], "projects/trail-bottle-launch-hook-a-north-coast")

    def test_one_variant_sign_off_does_not_cover_another(self) -> None:
        path = self.variant_card()
        self.variant_sign_off(path, "hook-a")
        (path.parent / "hook-b").mkdir()
        code, document = self.gate(path, "L3", "final", "--variant", "hook-b")
        self.assertEqual(code, 1, document)
        self.assertIn("localize.native_review", rule_ids(document, "blockers"))

    def test_variant_sign_off_does_not_cover_the_base_market(self) -> None:
        path = self.variant_card()
        self.variant_sign_off(path)
        code, document = self.gate(path, "L3")
        self.assertEqual(code, 1, document)
        self.assertIn("localize.native_review", rule_ids(document, "blockers"))

    def test_record_naming_another_variant_is_refused(self) -> None:
        path = self.variant_card()
        record_path = self.variant_sign_off(path, "hook-a")
        record = json.loads(record_path.read_text())
        record["variant"] = "hook-b"
        record_path.write_text(json.dumps(record))
        code, document = self.gate(path, "L3", "final", "--variant", "hook-a")
        self.assertEqual(code, 1, document)
        self.assertIn("variant", " ".join(b["message"] for b in document["blockers"]))

    def test_base_record_without_variant_is_refused_for_a_variant(self) -> None:
        path = self.variant_card()
        record_path = self.variant_sign_off(path)
        record = json.loads(record_path.read_text())
        del record["variant"]
        record_path.write_text(json.dumps(record))
        code, document = self.gate(path, "L3", "final", "--variant", "hook-a")
        self.assertEqual(code, 1, document)

    def test_variant_inventory_edit_makes_its_sign_off_stale(self) -> None:
        path = self.variant_card()
        self.variant_sign_off(path)
        (path.parent / "hook-a/inventory.md").write_text("| id | level |\n| --- | --- |\n| presenter | L4 |\n")
        code, document = self.gate(path, "L3", "final", "--variant", "hook-a")
        self.assertEqual(code, 1, document)
        self.assertTrue(any("stale" in b["message"] for b in document["blockers"]))

    def test_variant_inventory_overrides_the_level_for_that_variant(self) -> None:
        path = self.variant_card()
        variant_dir = path.parent / "hook-a"
        variant_dir.mkdir()
        (variant_dir / "inventory.md").write_text("| id | level |\n| --- | --- |\n| super-01 | L1 |\n")
        code, document = self.gate(path, "L1", "final", "--variant", "hook-a", "--element", "super-01")
        self.assertEqual(code, 0, document)
        code, document = self.gate(path, "L1", "final", "--element", "super-01")
        self.assertEqual(code, 1, document)
        self.assertIn("market.level_override", rule_ids(document, "blockers"))

    def test_missing_variant_folder_is_blocked(self) -> None:
        path = self.variant_card()
        code, document = self.gate(path, "L1", "draft", "--variant", "hook-z")
        self.assertEqual(code, 1, document)
        self.assertEqual(rule_ids(document, "blockers"), ["market.variant_dir"])

    def test_invalid_or_symlinked_variant_is_an_error(self) -> None:
        path = self.variant_card()
        for key in ("../hook-a", "Hook_A", "decisions"):
            with self.subTest(key=key):
                code, document = self.gate(path, "L1", "draft", "--variant", key)
                self.assertEqual(code, 1, document)
                self.assertIn("error", document)
        outside = self.campaign.parent / "outside"
        outside.mkdir()
        (path.parent / "hook-a").symlink_to(outside, target_is_directory=True)
        code, document = self.gate(path, "L1", "draft", "--variant", "hook-a")
        self.assertEqual(code, 1, document)
        self.assertIn("symlink", document["error"])

    def test_facts_in_a_variant_project_are_market_scoped(self) -> None:
        path = self.complete_card(
            facts_ref="projects/trail-bottle-launch-hook-a-north-coast/elements/trail-bottle/facts.json"
        )
        code, document = run("validate", str(path))
        self.assertEqual(code, 0, document)
        self.edit(path, facts_ref="projects/trail-bottle-launch-hook-a-south-coast/elements/trail-bottle/facts.json")
        code, document = run("validate", str(path))
        self.assertEqual(code, 1, document)
        self.assertIn("market.price_fact", rule_ids(document))


class SkillStructureTests(unittest.TestCase):
    def skill_text(self) -> str:
        return "\n".join(
            path.read_text() for path in [SKILL_DIR / "SKILL.md", *sorted((SKILL_DIR / "references").glob("*.md"))]
        )

    def test_frontmatter_names_the_skill_and_declares_an_orchestrator(self) -> None:
        text = (SKILL_DIR / "SKILL.md").read_text()
        match = re.match(r"\A---\s*\n(.*?)\n---", text, re.DOTALL)
        assert match is not None
        metadata = YAML(typ="safe").load(match.group(1))
        self.assertEqual(metadata["name"], "ad-localize")
        self.assertTrue(metadata["description"].startswith("Orchestrator"))
        self.assertLessEqual(len(metadata["description"]), 1024)
        self.assertLess(len(text.splitlines()), 300)

    def test_skill_cites_its_rule_ids(self) -> None:
        text = (SKILL_DIR / "SKILL.md").read_text()
        for rule in (
            "localize.native_review",
            "localize.source_untouched",
            "localize.claims_market_scoped",
            "localize.market_card_sourced",
        ):
            self.assertIn(f"`{rule}`", text)

    def test_relative_links_resolve(self) -> None:
        for document in [SKILL_DIR / "SKILL.md", *(SKILL_DIR / "references").glob("*.md")]:
            for target in re.findall(r"\]\(([^)#]+)(?:#[^)]*)?\)", document.read_text()):
                if "://" in target:
                    continue
                with self.subTest(document=document.name, target=target):
                    self.assertTrue((document.parent / target).exists())

    def test_evals_cover_the_five_required_scenarios(self) -> None:
        document = json.loads((SKILL_DIR / "evals/evals.json").read_text())
        self.assertEqual(document["skill_name"], "ad-localize")
        evals = document["evals"]
        self.assertEqual(len(evals), 5)
        self.assertEqual(len({case["id"] for case in evals}), 5)
        for case in evals:
            self.assertTrue(case["prompt"].strip())
            self.assertTrue(case["expected_output"].strip())
            self.assertEqual(case["files"], [])
            self.assertGreaterEqual(len(case["expectations"]), 4)
        joined = json.dumps(evals).lower()
        for marker in ("subtitles", "dub", "vp-amara", "clinically", "don't have any"):
            self.assertIn(marker, joined)

    def test_openai_metadata_uses_the_skill_invocation(self) -> None:
        metadata = YAML(typ="safe").load((SKILL_DIR / "agents/openai.yaml").read_text())
        interface = metadata["interface"]
        self.assertEqual(interface["display_name"], "Ad Localize")
        self.assertIn("$ad-localize", interface["default_prompt"])

    def test_skill_text_sets_no_default_market(self) -> None:
        text = self.skill_text()
        self.assertIn("No market is built in", text)
        self.assertIsNone(
            re.search(r"default (market|language|locale|currency|country)\b", text, re.IGNORECASE)
        )
        self.assertIsNone(re.search(r"^\s*(market|language|locale)\s*[:=]\s*\w", text, re.MULTILINE))

    def test_documented_example_card_validates(self) -> None:
        text = (SKILL_DIR / "references/market-card.md").read_text()
        block = re.search(r"```json\n(.*?)\n```", text, re.DOTALL)
        assert block is not None
        card = json.loads(block.group(1))
        with tempfile.TemporaryDirectory(prefix="ad-localize-doc-") as directory:
            card_dir = Path(directory) / card["campaign"] / "markets" / card["market_id"]
            card_dir.mkdir(parents=True)
            findings = MODULE.validate_card(card, card_dir)
        self.assertEqual(MODULE.blocking(findings), [])

    def test_documented_sign_off_record_matches_its_schema(self) -> None:
        text = (SKILL_DIR / "references/native-review.md").read_text()
        block = re.search(r"```json\n(.*?)\n```", text, re.DOTALL)
        assert block is not None
        schema = json.loads((ROOT / ".agents/contracts/schemas/native-review.schema.json").read_text())
        errors = list(MODULE.Draft202012Validator(schema).iter_errors(json.loads(block.group(1))))
        self.assertEqual(errors, [])

    def test_final_requests_require_the_native_review_rule(self) -> None:
        text = (SKILL_DIR / "SKILL.md").read_text()
        self.assertIn("--required-rule localize.native_review", text)

    def test_market_values_on_screen_are_l1_not_l4(self) -> None:
        text = (SKILL_DIR / "SKILL.md").read_text()
        l4_row = next(line for line in text.splitlines() if line.startswith("| L4 "))
        for word in ("pricing", "CTA", "legal"):
            self.assertNotIn(word, l4_row)
        levels = (SKILL_DIR / "references/levels.md").read_text()
        self.assertNotIn("L4 when the value itself changes", levels)

    def test_l2_language_check_uses_seed_audio_support(self) -> None:
        levels = (SKILL_DIR / "references/levels.md").read_text()
        l2 = levels[levels.index("## L2 Voice"):levels.index("## L3 Talent")]
        self.assertIn("audio-dubbing", l2)
        self.assertNotIn("seedance-prompt-25-dialogue", l2)
        evals = json.loads((SKILL_DIR / "evals/evals.json").read_text())["evals"]
        self.assertNotIn("seedance-prompt-25-dialogue", " ".join(evals[1]["expectations"]))

    def test_swaps_take_the_muted_text_free_selected_takes(self) -> None:
        corpus = self.skill_text() + (SKILL_DIR / "evals/evals.json").read_text()
        self.assertNotIn("muted source master", corpus)
        self.assertIn("muted, text-free selected take of each shot", corpus)

    def test_variant_layout_is_documented(self) -> None:
        corpus = self.skill_text()
        self.assertIn("--variant <variant-key>", corpus)
        self.assertIn("projects/<campaign>-<variant-key>-<market-id>", corpus)
        self.assertIn("markets/<market-id>/<variant-key>/", corpus)

    def test_translation_sheet_has_a_level_column(self) -> None:
        text = (SKILL_DIR / "references/translation-and-transcreation.md").read_text()
        self.assertIn("| `level` |", text)

    def test_symlink_points_into_agents(self) -> None:
        link = ROOT / ".claude/skills/ad-localize"
        self.assertTrue(link.is_symlink())
        self.assertEqual(link.resolve(), SKILL_DIR.resolve())


if __name__ == "__main__":
    unittest.main()
