from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / ".agents/skills/static-ad-batch/scripts/static_batch.py"
SPEC = importlib.util.spec_from_file_location("static_batch", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)

NOW = datetime(2026, 10, 17, 12, 0, tzinfo=UTC)
PAGE = "https://lumo.example/products/travel-mug"
SCHEMAS = ROOT / ".agents/contracts/schemas"
LOGO_BYTES = b"<svg xmlns='http://www.w3.org/2000/svg'/>"
HEAD_BYTES = b"wOF2-head"
BODY_BYTES = b"wOF2-body"
LICENSE = "Brand-supplied for advertising use"


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


BRAND: dict[str, Any] = {
    "schema_version": 1,
    "brand_id": "lumo",
    "name": "Lumo",
    "source": {
        "method": "user_files",
        "urls": [],
        "retrieved_at": "2026-10-17T09:00:00Z",
        "authorized_by": "User states they own the brand",
    },
    "logos": [
        {
            "role": "primary",
            "file": "assets/logo.svg",
            "sha256": digest(LOGO_BYTES),
            "source": "user_supplied",
        }
    ],
    "palette": [
        {"name": "blue", "hex": "#2E6FD8", "role": "primary"},
        {"name": "sun", "hex": "#F2B705", "role": "accent"},
        {"name": "paper", "hex": "#FAF7F0", "role": "background"},
        {"name": "ink", "hex": "#14171F", "role": "text"},
    ],
    "typography": [
        {
            "role": "headline",
            "family": "Lumo Display",
            "weight": 700,
            "file": "assets/head.woff2",
            "sha256": digest(HEAD_BYTES),
            "source": "user_supplied",
            "license": LICENSE,
        },
        {
            "role": "body",
            "family": "Lumo Text",
            "weight": 400,
            "file": "assets/body.woff2",
            "sha256": digest(BODY_BYTES),
            "source": "user_supplied",
            "license": LICENSE,
        },
    ],
    "voice": {"tone": ["warm"], "reading_level": "plain", "do": [], "dont": []},
    "copy_rules": {"banned_words": ["miracle", "cheap"], "required_lines": [], "trademark_marks": {}},
    "cta_style": {"shape": "pill", "case": "sentence", "verbs": ["Shop now"]},
    "imagery": {"style_sentence": "Soft window light on pale wood.", "avoid": []},
    "disclosure": {"ai_label_text": None, "placement": None},
    "missing": ["disclosure.ai_label_text", "disclosure.placement"],
    "status": "approved",
    "approval": {
        "mode": "approve_for_me",
        "actor": "agent",
        "decision_ref": "decisions/approve_v01.md",
        "decided_at": "2026-10-17T10:00:00Z",
    },
}


def fact(fact_id: str, kind: str, claim: str, status: str, **extra: Any) -> dict[str, Any]:
    return {
        "fact_id": fact_id,
        "kind": kind,
        "claim": claim,
        "quote": claim,
        "source_url": PAGE,
        "retrieved_at": "2026-10-17T09:30:00Z",
        "status": status,
        **extra,
    }


EVIDENCE = "Lab report LR-12 supplied by the user"
FACTS: dict[str, Any] = {
    "schema_version": 1,
    "product_id": "lumo-mug",
    "product_name": "Lumo mug",
    "brand_id": "lumo",
    "source": {"method": "product_page", "urls": [PAGE], "parse_status": "parsed"},
    "facts": [
        fact("f01", "performance", "Keeps drinks hot for 6 hours", "supported", substantiation=EVIDENCE),
        fact("f02", "feature", "Lid locks with one click", "supported"),
        fact("f03", "comparison", "Open cup: about 2 hours", "supported", substantiation=EVIDENCE),
        fact("f04", "other", "4.7 average from 1,240 reviews", "supported", substantiation=EVIDENCE),
        fact("f05", "offer", "20% off this week", "perishable"),
        fact("f06", "performance", "Makes coffee taste better", "needs-substantiation"),
    ],
    "images": [],
}
ANGLE: dict[str, Any] = {
    "id": "stays-hot",
    "type": "demonstration",
    "headline": "Hot at hour six",
    "claims": ["f01", "f02"],
    "cta": "Shop now",
    "problem": "Cold coffee by noon?",
    "comparison": {
        "ours_label": "Lumo",
        "alternative_label": "Open cup",
        "rows": [{"attribute": "Heat", "ours": "f01", "alternative": "f03"}],
    },
    "proof": "f04",
    "offer": "f05",
    "terms": "Ends Sunday.",
}


def schema_errors(document: Any, name: str) -> list[str]:
    schema = json.loads((SCHEMAS / name).read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    return [error.message for error in validator.iter_errors(document)]


def canonical_pin(document: dict[str, Any]) -> str:
    payload = json.dumps(document, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


class StaticAdBatchTests(unittest.TestCase):
    def setUp(self) -> None:
        directory = tempfile.TemporaryDirectory(prefix="static-ad-batch-test-")
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)
        (self.root / "brand/assets").mkdir(parents=True)
        (self.root / "brand/assets/logo.svg").write_bytes(LOGO_BYTES)
        (self.root / "brand/assets/head.woff2").write_bytes(HEAD_BYTES)
        (self.root / "brand/assets/body.woff2").write_bytes(BODY_BYTES)
        (self.root / "product").mkdir()
        (self.root / "product/pack.png").write_bytes(b"\x89PNG\r\n\x1a\nfake")
        self.brand = copy.deepcopy(BRAND)
        self.facts = copy.deepcopy(FACTS)
        self.pin_brand = True
        self.spec: dict[str, Any] = {
            "campaign": "lumo-launch",
            "language": "en",
            "brand_kit": "brand/brand.json",
            "facts": "product/facts.json",
            "product": {"name": "Lumo mug", "image": "product/pack.png"},
            "output_dir": "statics",
            "layouts": ["hero-product", "offer"],
            "ratios": ["1:1", "4:5", "9:16", "16:9"],
            "angles": [copy.deepcopy(ANGLE), dict(copy.deepcopy(ANGLE), id="no-spill")],
        }

    def write_inputs(self) -> Path:
        (self.root / "brand/brand.json").write_text(json.dumps(self.brand), encoding="utf-8")
        (self.root / "product/facts.json").write_text(json.dumps(self.facts), encoding="utf-8")
        spec = dict(self.spec)
        if self.pin_brand:
            spec.setdefault("brand_kit_sha256", canonical_pin(self.brand))
        spec_path = self.root / "spec.json"
        spec_path.write_text(json.dumps(spec), encoding="utf-8")
        return spec_path

    def run_plan(self, overwrite: bool = False) -> dict[str, Any]:
        return MODULE.plan(self.write_inputs(), None, overwrite, now=NOW)

    def offer_only(self) -> None:
        self.spec["layouts"] = ["offer"]
        self.spec["angles"] = [copy.deepcopy(ANGLE)]

    def test_fixtures_match_the_brand_kit_and_product_facts_schemas(self) -> None:
        self.assertEqual(schema_errors(BRAND, "brand-kit.schema.json"), [])
        self.assertEqual(schema_errors(FACTS, "product-facts.schema.json"), [])

    def test_plan_expands_every_angle_layout_and_ratio(self) -> None:
        result = self.run_plan()
        self.assertEqual(len(result["jobs"]), 2 * 2 * 4)
        self.assertEqual(len(result["shell_commands"]), 16 + 1)
        for job in result["jobs"]:
            self.assertTrue((self.root / job["html"]).is_file())
        self.assertTrue((self.root / "statics/static_lumo-launch_v01.css").is_file())
        self.assertTrue((self.root / "statics/batch_lumo-launch_v01.json").is_file())

    def test_job_names_follow_campaign_angle_layout_ratio_version(self) -> None:
        names = [job["name"] for job in self.run_plan()["jobs"]]
        self.assertEqual(names[0], "lumo-launch_stays-hot_hero-product_1x1_v01")
        self.assertEqual(names[3], "lumo-launch_stays-hot_hero-product_16x9_v01")
        self.assertEqual(names[4], "lumo-launch_stays-hot_offer_1x1_v01")
        self.assertEqual(names[-1], "lumo-launch_no-spill_offer_16x9_v01")
        self.assertEqual(len(set(names)), len(names))

    def test_version_and_angle_layout_override_change_the_grid(self) -> None:
        self.spec["version"] = 3
        self.spec["angles"][1]["layouts"] = ["comparison"]
        jobs = self.run_plan()["jobs"]
        self.assertEqual(len(jobs), 2 * 4 + 1 * 4)
        self.assertTrue(all(job["name"].endswith("_v03") for job in jobs))
        self.assertIn("lumo-launch_no-spill_comparison_9x16_v03", [j["name"] for j in jobs])

    def test_commands_bind_exact_copy_size_and_required_font(self) -> None:
        job = self.run_plan()["jobs"][1]
        command = job["command"]
        self.assertIn(".agents/skills/html-graphic-render/scripts/render_html.py", command)
        self.assertEqual(command[command.index("--width") + 1], "1080")
        self.assertEqual(command[command.index("--height") + 1], "1350")
        self.assertEqual(command[command.index("--require-local-font") + 1], "brand-headline")
        self.assertIn("claim_1=Keeps drinks hot for 6 hours", command)
        self.assertEqual(job["claims"][0]["ref"], "f01")

    def test_unsupported_claim_is_refused(self) -> None:
        self.spec["angles"][0]["claims"] = ["f01", "f06"]
        with self.assertRaisesRegex(ValueError, "needs-substantiation"):
            self.run_plan()
        self.assertFalse((self.root / "statics").exists())

    def test_unknown_claim_is_refused(self) -> None:
        self.spec["angles"][0]["claims"] = ["Best mug ever"]
        with self.assertRaisesRegex(ValueError, "not in the product facts"):
            self.run_plan()

    def test_fresh_perishable_offer_is_accepted_and_recorded(self) -> None:
        self.offer_only()
        result = self.run_plan()
        offer = result["jobs"][0]["claims"][0]
        self.assertEqual(offer["status"], "perishable")
        self.assertEqual(offer["retrieved_at"], "2026-10-17T09:30:00Z")
        self.assertEqual(result["perishable_max_age_hours"], 24)
        self.assertIn("offer=20% off this week", result["jobs"][0]["command"])

    def test_stale_perishable_offer_is_refused_unless_the_window_allows_it(self) -> None:
        self.offer_only()
        self.facts["facts"][4]["retrieved_at"] = "2026-10-16T09:00:00Z"
        with self.assertRaisesRegex(ValueError, "stale"):
            self.run_plan()
        self.assertFalse((self.root / "statics").exists())
        self.spec["perishable_max_age_hours"] = 48
        self.assertEqual(self.run_plan()["perishable_max_age_hours"], 48)

    def test_perishable_offer_without_a_valid_retrieval_time_is_refused(self) -> None:
        self.offer_only()
        for value in ("2026-10-17T09:30:00", "2026-10-18T09:30:00Z", "yesterday"):
            with self.subTest(retrieved_at=value):
                self.facts["facts"][4]["retrieved_at"] = value
                with self.assertRaisesRegex(ValueError, "retrieved_at"):
                    self.run_plan()

    def test_perishable_fact_outside_the_offer_layout_is_refused(self) -> None:
        self.spec["angles"][0]["claims"] = ["f01", "f05"]
        with self.assertRaisesRegex(ValueError, "only supported claims"):
            self.run_plan()

    def test_unsubstantiated_offer_is_refused(self) -> None:
        self.offer_only()
        self.facts["facts"][4]["status"] = "needs-substantiation"
        with self.assertRaisesRegex(ValueError, "needs-substantiation"):
            self.run_plan()

    def test_invalid_perishable_window_is_refused(self) -> None:
        for value in (0, -1, True, "24", None):
            with self.subTest(value=value):
                self.spec["perishable_max_age_hours"] = value
                with self.assertRaisesRegex(ValueError, "perishable_max_age_hours"):
                    self.run_plan()

    def test_missing_brand_tokens_are_refused_and_listed(self) -> None:
        self.brand["palette"] = [p for p in self.brand["palette"] if p["role"] != "text"]
        self.brand["typography"] = self.brand["typography"][:1]
        self.brand["logos"] = []
        with self.assertRaises(ValueError) as caught:
            self.run_plan()
        message = str(caught.exception)
        for token in ("palette.text", "typography.body", "logos.primary"):
            self.assertIn(token, message)

    def test_invalid_hex_counts_as_missing_and_draft_kit_is_refused(self) -> None:
        self.brand["palette"][2]["hex"] = "paper"
        with self.assertRaisesRegex(ValueError, "palette.background"):
            self.run_plan()
        self.brand = copy.deepcopy(BRAND)
        self.brand["status"] = "draft"
        with self.assertRaisesRegex(ValueError, "approved"):
            self.run_plan()

    def test_missing_or_mismatched_campaign_pin_is_refused(self) -> None:
        self.pin_brand = False
        with self.assertRaisesRegex(ValueError, "brand_kit_sha256 is required"):
            self.run_plan()
        self.spec["brand_kit_sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "campaign pin"):
            self.run_plan()

    def test_font_or_logo_without_a_matching_recorded_hash_is_refused(self) -> None:
        cases = [
            ("typography", 0, None, "Font headline has no recorded SHA-256"),
            ("typography", 1, "f" * 64, "Font body SHA-256 differs"),
            ("logos", 0, None, "Logo has no recorded SHA-256"),
            ("logos", 0, "f" * 64, "Logo SHA-256 differs"),
        ]
        for section, index, value, message in cases:
            with self.subTest(section=section, value=value):
                self.brand = copy.deepcopy(BRAND)
                self.brand[section][index]["sha256"] = value
                with self.assertRaisesRegex(ValueError, message):
                    self.run_plan()

    def test_changed_font_bytes_are_refused(self) -> None:
        (self.root / "brand/assets/head.woff2").write_bytes(HEAD_BYTES + b"edited")
        with self.assertRaisesRegex(ValueError, "Font headline SHA-256 differs"):
            self.run_plan()

    def test_font_without_a_license_is_refused_for_every_used_role(self) -> None:
        for role_index, value in ((0, None), (1, "  ")):
            with self.subTest(role_index=role_index):
                self.brand = copy.deepcopy(BRAND)
                self.brand["typography"][role_index]["license"] = value
                with self.assertRaisesRegex(ValueError, "license"):
                    self.run_plan()
        self.brand = copy.deepcopy(BRAND)
        cta = dict(self.brand["typography"][1], role="cta", license=None)
        self.brand["typography"].append(cta)
        with self.assertRaisesRegex(ValueError, "Font cta has no recorded license"):
            self.run_plan()

    def test_roles_sharing_a_family_get_distinct_font_faces(self) -> None:
        self.brand["typography"][1]["family"] = "Lumo Display"
        result = self.run_plan()
        css = (self.root / result["stylesheet"]).read_text(encoding="utf-8")
        self.assertEqual(css.count("@font-face"), 2)
        self.assertIn("font-family: 'brand-headline';", css)
        self.assertIn("font-family: 'brand-body';", css)
        self.assertIn("font-weight: 700;\n  src: url('../brand/assets/head.woff2')", css)
        self.assertIn("font-weight: 400;\n  src: url('../brand/assets/body.woff2')", css)
        self.assertIn("--font-headline: 'brand-headline';", css)
        self.assertIn("--font-body: 'brand-body';", css)
        self.assertIn("--font-cta: 'brand-body';", css)
        fonts = json.loads((self.root / "statics/batch_lumo-launch_v01.json").read_text())[
            "inputs"
        ]["fonts"]
        self.assertEqual(fonts["body"]["family"], "Lumo Display")
        self.assertEqual(fonts["body"]["alias"], "brand-body")

    def test_banned_words_and_their_simple_plurals_are_refused(self) -> None:
        self.brand["copy_rules"]["banned_words"] = ["miracle", "glass"]
        for headline in ("A Miracle mug", "Small miracles daily", "No more glasses"):
            with self.subTest(headline=headline):
                self.spec["angles"][0]["headline"] = headline
                with self.assertRaisesRegex(ValueError, "banned word"):
                    self.run_plan()

    def test_words_that_only_contain_a_banned_word_are_allowed(self) -> None:
        self.spec["angles"][0]["headline"] = "Miraculous glassware"
        self.spec["angles"][1]["headline"] = "Miraculous glassware"
        self.assertEqual(len(self.run_plan()["jobs"]), 16)

    def test_template_fill_escapes_html_in_copy(self) -> None:
        self.spec["angles"][0]["headline"] = '<script>alert("x")</script> & more'
        job = self.run_plan()["jobs"][0]
        document = (self.root / job["html"]).read_text(encoding="utf-8")
        self.assertNotIn("<script>", document)
        self.assertIn(
            "&lt;script&gt;alert(&quot;x&quot;)&lt;/script&gt; &amp; more", document
        )
        self.assertEqual(job["copy"]["headline"], '<script>alert("x")</script> & more')

    def test_fill_template_rejects_unknown_placeholders(self) -> None:
        self.assertEqual(MODULE.fill_template("<p>{{a}}</p>", {"a": "<b>"}), "<p>&lt;b&gt;</p>")
        with self.assertRaisesRegex(ValueError, "missing_key"):
            MODULE.fill_template("<p>{{missing_key}}</p>", {})

    def test_paths_outside_the_asset_root_are_refused(self) -> None:
        self.spec["product"]["image"] = "../outside.png"
        with self.assertRaisesRegex(ValueError, "escapes the asset root"):
            self.run_plan()
        self.spec["product"]["image"] = "product/pack.png"
        self.spec["output_dir"] = "../elsewhere"
        with self.assertRaisesRegex(ValueError, "output_dir escapes"):
            self.run_plan()

    def test_existing_outputs_need_a_new_version_or_overwrite(self) -> None:
        first = self.run_plan()
        with self.assertRaisesRegex(ValueError, "Refusing to overwrite"):
            self.run_plan()
        second = self.run_plan(overwrite=True)
        self.assertEqual(first["jobs"], second["jobs"])

    def test_invalid_grid_values_are_refused(self) -> None:
        cases = [
            ("ratios", ["1:1", "3:2"], "unsupported values"),
            ("layouts", ["hero-product", "hero-product"], "duplicates"),
            ("campaign", "Lumo Launch", "kebab-case"),
            ("language", "english language", "BCP 47"),
        ]
        for key, value, message in cases:
            with self.subTest(key=key):
                original = self.spec[key]
                self.spec[key] = value
                with self.assertRaisesRegex(ValueError, message):
                    self.run_plan()
                self.spec[key] = original

    def test_command_line_reports_errors_with_exit_code_two(self) -> None:
        self.spec["angles"][0]["type"] = "you-need-this"
        spec_path = self.write_inputs()
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "plan", str(spec_path)],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn("type must be one of", result.stderr)


if __name__ == "__main__":
    unittest.main()
