from __future__ import annotations

import contextlib
import hashlib
import importlib.util
import io
import json
import os
import sys
import tempfile
import unittest
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / ".agents/skills/product-intake/scripts/product_facts.py"
SPEC = importlib.util.spec_from_file_location("product_facts", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)

NOW = datetime(2026, 10, 17, 12, 0, tzinfo=UTC)
PAGE = "https://trailblend.example/products/insulated-bottle"
IMAGE_BYTES = b"\x89PNG\r\n\x1a\nsynthetic-front"


def run(*argv: str) -> tuple[int, dict[str, Any]]:
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        code = MODULE.main(list(argv), now=NOW)
    return code, json.loads(buffer.getvalue())


def fact(fact_id: str, kind: str, status: str, **extra: Any) -> dict[str, Any]:
    return {
        "fact_id": fact_id,
        "kind": kind,
        "claim": f"claim {fact_id}",
        "quote": f"verbatim {fact_id}",
        "source_url": PAGE,
        "retrieved_at": "2026-10-17T09:30:00Z",
        "status": status,
        **extra,
    }


class ProductFactsTestCase(unittest.TestCase):
    def setUp(self) -> None:
        directory = tempfile.TemporaryDirectory(prefix="product-intake-test-")
        self.addCleanup(directory.cleanup)
        self.card = Path(directory.name) / "elements" / "trailblend-bottle"
        self.card.mkdir(parents=True)
        (self.card / "ref_01_front.png").write_bytes(IMAGE_BYTES)
        self.path = self.card / "facts.json"
        self.write(self.document())

    def document(self) -> dict[str, Any]:
        return {
            "schema_version": 1,
            "product_id": "trailblend-bottle",
            "product_name": "TrailBlend Insulated Bottle 750 ml",
            "brand_id": "trailblend",
            "source": {"method": "product_page", "urls": [PAGE], "parse_status": "parsed"},
            "facts": [
                fact("f01", "specification", "supported", conditions="lid closed"),
                fact("f02", "performance", "needs-substantiation"),
                fact("f03", "price", "perishable"),
                fact("f04", "availability", "perishable", retrieved_at="2026-10-10T09:00:00Z"),
            ],
            "images": [
                {
                    "file": "ref_01_front.png",
                    "source": "https://trailblend.example/cdn/front.png",
                    "sha256": hashlib.sha256(IMAGE_BYTES).hexdigest(),
                    "retrieved_at": "2026-10-17T09:31:00Z",
                    "view": "front",
                }
            ],
        }

    def write(self, document: Any) -> None:
        self.path.write_text(json.dumps(document, indent=2))

    def rules(self) -> list[str]:
        code, result = run("validate", str(self.path))
        self.assertEqual(code, int(not result["ok"]))
        return [finding["rule_id"] for finding in result["findings"]]

    def with_fact(self, index: int, **changes: Any) -> None:
        document = self.document()
        document["facts"][index].update(changes)
        self.write(document)


class ValidateTests(ProductFactsTestCase):
    def test_well_formed_card_passes(self) -> None:
        self.assertEqual(self.rules(), [])

    def test_user_supplied_fact_with_source_ref_passes(self) -> None:
        document = self.document()
        del document["facts"][0]["source_url"]
        document["facts"][0]["source_ref"] = "user_supplied: spec-sheet.pdf p.2"
        document["source"] = {"method": "user_supplied", "urls": [], "parse_status": "failed"}
        self.write(document)
        self.assertEqual(self.rules(), [])

    def test_fact_without_any_source_is_rejected(self) -> None:
        document = self.document()
        del document["facts"][0]["source_url"]
        self.write(document)
        self.assertIn("facts.source", self.rules())

    def test_fact_without_quote_is_rejected(self) -> None:
        for quote in (None, ""):
            with self.subTest(quote=quote):
                document = self.document()
                if quote is None:
                    del document["facts"][0]["quote"]
                else:
                    document["facts"][0]["quote"] = quote
                self.write(document)
                self.assertIn("facts.schema", self.rules())

    def test_price_and_offer_must_be_perishable(self) -> None:
        for kind in ("price", "availability", "offer"):
            with self.subTest(kind=kind):
                self.with_fact(2, kind=kind, status="supported")
                self.assertIn("facts.perishable", self.rules())

    def test_supported_performance_claim_needs_substantiation(self) -> None:
        self.with_fact(1, status="supported")
        self.assertIn("facts.substantiation", self.rules())
        self.with_fact(1, status="supported", substantiation="Lab report LR-12 supplied by user")
        self.assertEqual(self.rules(), [])

    def test_unknown_status_is_rejected(self) -> None:
        self.with_fact(0, status="verified")
        self.assertIn("facts.schema", self.rules())

    def test_future_or_offsetless_retrieval_time_is_rejected(self) -> None:
        self.with_fact(0, retrieved_at="2026-10-18T09:00:00Z")
        self.assertIn("facts.retrieved_at", self.rules())
        self.with_fact(0, retrieved_at="2026-10-17T09:00:00")
        self.assertIn("facts.retrieved_at", self.rules())

    def test_duplicate_fact_ids_are_rejected(self) -> None:
        self.with_fact(1, fact_id="f01")
        self.assertIn("facts.unique", self.rules())

    def test_image_hash_mismatch_and_missing_image_are_reported(self) -> None:
        (self.card / "ref_01_front.png").write_bytes(IMAGE_BYTES + b"edited")
        self.assertIn("facts.image_hash", self.rules())
        (self.card / "ref_01_front.png").unlink()
        self.assertIn("facts.image_exists", self.rules())

    def test_image_outside_the_card_is_rejected(self) -> None:
        document = self.document()
        document["images"][0]["file"] = "../ref_01_front.png"
        self.write(document)
        rules = self.rules()
        self.assertIn("facts.schema", rules)
        self.assertIn("facts.image_contained", rules)

    def test_symlinked_image_is_rejected(self) -> None:
        outside = self.card.parent / "elsewhere.png"
        outside.write_bytes(IMAGE_BYTES)
        image = self.card / "ref_01_front.png"
        image.unlink()
        image.symlink_to(outside)
        self.assertIn("facts.image_exists", self.rules())

    def test_generated_or_unsourced_image_is_rejected(self) -> None:
        document = self.document()
        document["images"][0]["source"] = "seedream"
        self.write(document)
        self.assertIn("facts.schema", self.rules())

    def test_product_id_must_match_directory(self) -> None:
        document = self.document()
        document["product_id"] = "other-bottle"
        self.write(document)
        self.assertIn("facts.product_directory", self.rules())

    def test_validating_from_inside_the_card_directory_matches_product_id(self) -> None:
        previous = Path.cwd()
        self.addCleanup(os.chdir, previous)
        os.chdir(self.card)
        code, result = run("validate", "facts.json")
        self.assertEqual(code, 0)
        self.assertEqual(result["findings"], [])

    def test_claim_dropping_a_quoted_qualifier_warns_without_failing(self) -> None:
        cases = [
            ("Keeps drinks cold for up to 24 hours.", "Keeps drinks cold for 24 hours"),
            ("Prices from 32.00 per bottle", "Priced at 32.00"),
            ("Starting at 29.00", "Priced at 29.00"),
            ("As low as 25.00 in the bundle", "25.00 in the bundle"),
            ("Approximately 450 g empty", "Weighs 450 g empty"),
            ("Results may vary with use", "Results vary with use"),
        ]
        for quote, claim in cases:
            with self.subTest(quote=quote):
                self.with_fact(0, quote=quote, claim=claim)
                code, result = run("validate", str(self.path))
                self.assertEqual(code, 0)
                self.assertTrue(result["ok"])
                warnings = [
                    finding
                    for finding in result["findings"]
                    if finding["rule_id"] == "facts.claim_qualifier"
                ]
                self.assertEqual(len(warnings), 1)
                self.assertEqual(warnings[0]["severity"], "warning")
                self.assertEqual(warnings[0]["path"], "facts.0.claim")

    def test_claim_keeping_its_qualifier_or_non_price_from_does_not_warn(self) -> None:
        cases = [
            ("Keeps drinks cold for up to 24 hours.", "Keeps drinks cold for up to 24 hours"),
            ("Prices from 32.00 per bottle", "From 32.00"),
            ("Made from recycled steel", "Made of recycled steel"),
            ("Mayfield steel body", "Steel body"),
        ]
        for quote, claim in cases:
            with self.subTest(quote=quote):
                self.with_fact(0, quote=quote, claim=claim)
                self.assertNotIn("facts.claim_qualifier", self.rules())

    def test_empty_card_from_failed_parse_is_valid(self) -> None:
        document = self.document()
        document.update(
            facts=[],
            images=[],
            product_name=None,
            source={"method": "product_page", "urls": [PAGE], "parse_status": "failed"},
        )
        self.write(document)
        self.assertEqual(self.rules(), [])

    def test_malformed_input_exits_one_without_crashing(self) -> None:
        self.path.write_text("{broken")
        code, result = run("validate", str(self.path))
        self.assertEqual(code, 1)
        self.assertIn("not valid JSON", result["error"])
        self.write({"facts": "none", "images": [3]})
        self.assertIn("facts.schema", self.rules())
        code, _ = run("validate", str(self.card / "absent.json"))
        self.assertEqual(code, 1)


class SupportedTests(ProductFactsTestCase):
    def claims(self, *extra: str) -> list[str]:
        code, result = run("supported", str(self.path), *extra)
        self.assertEqual(code, 0)
        return [claim["fact_id"] for claim in result["claims"]]

    def test_only_supported_claims_are_printed_by_default(self) -> None:
        self.assertEqual(self.claims(), ["f01"])

    def test_printed_claim_keeps_quote_conditions_and_source(self) -> None:
        _, result = run("supported", str(self.path))
        claim = result["claims"][0]
        self.assertEqual(claim["quote"], "verbatim f01")
        self.assertEqual(claim["conditions"], "lid closed")
        self.assertEqual(claim["source_url"], PAGE)

    def test_recent_perishable_facts_are_included_within_the_window(self) -> None:
        self.assertEqual(self.claims("--max-age-hours", "24"), ["f01", "f03"])
        self.assertEqual(self.claims("--max-age-hours", "240"), ["f01", "f03", "f04"])

    def test_needs_substantiation_is_never_printed(self) -> None:
        self.assertNotIn("f02", self.claims("--max-age-hours", "100000"))

    def test_invalid_record_prints_no_claims(self) -> None:
        self.with_fact(2, status="supported")
        code, result = run("supported", str(self.path))
        self.assertEqual(code, 1)
        self.assertNotIn("claims", result)

    def test_non_positive_window_is_rejected(self) -> None:
        code, result = run("supported", str(self.path), "--max-age-hours", "0")
        self.assertEqual(code, 1)
        self.assertIn("greater than zero", result["error"])


if __name__ == "__main__":
    unittest.main()
