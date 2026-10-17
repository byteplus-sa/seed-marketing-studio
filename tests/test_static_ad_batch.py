from __future__ import annotations

import copy
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / ".agents/skills/static-ad-batch/scripts/static_batch.py"
SPEC = importlib.util.spec_from_file_location("static_batch", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)

BRAND: dict[str, Any] = {
    "schema_version": 1,
    "brand_id": "lumo",
    "name": "Lumo",
    "status": "approved",
    "logos": [{"role": "primary", "file": "assets/logo.svg"}],
    "palette": [
        {"name": "blue", "hex": "#2E6FD8", "role": "primary"},
        {"name": "sun", "hex": "#F2B705", "role": "accent"},
        {"name": "paper", "hex": "#FAF7F0", "role": "background"},
        {"name": "ink", "hex": "#14171F", "role": "text"},
    ],
    "typography": [
        {"role": "headline", "family": "Lumo Display", "file": "assets/head.woff2"},
        {"role": "body", "family": "Lumo Text", "file": "assets/body.woff2"},
    ],
    "copy_rules": {"banned_words": ["miracle"]},
    "cta_style": {"verbs": ["Shop now"]},
}
FACTS = {
    "facts": [
        {"fact_id": "heat-6h", "claim": "Keeps drinks hot for 6 hours", "status": "supported"},
        {"fact_id": "lock", "claim": "Lid locks with one click", "status": "supported"},
        {"fact_id": "typical", "claim": "Open cup: about 2 hours", "status": "supported"},
        {"fact_id": "rating", "claim": "4.7 average from 1,240 reviews", "status": "supported"},
        {"fact_id": "offer", "claim": "20% off this week", "status": "supported"},
        {"fact_id": "taste", "claim": "Makes coffee taste better", "status": "needs-substantiation"},
    ]
}
ANGLE: dict[str, Any] = {
    "id": "stays-hot",
    "type": "demonstration",
    "headline": "Hot at hour six",
    "claims": ["heat-6h", "lock"],
    "cta": "Shop now",
    "problem": "Cold coffee by noon?",
    "comparison": {
        "ours_label": "Lumo",
        "alternative_label": "Open cup",
        "rows": [{"attribute": "Heat", "ours": "heat-6h", "alternative": "typical"}],
    },
    "proof": "rating",
    "offer": "offer",
    "terms": "Ends Sunday.",
}


class StaticAdBatchTests(unittest.TestCase):
    def setUp(self) -> None:
        directory = tempfile.TemporaryDirectory(prefix="static-ad-batch-test-")
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)
        (self.root / "brand/assets").mkdir(parents=True)
        (self.root / "brand/assets/logo.svg").write_text(
            "<svg xmlns='http://www.w3.org/2000/svg'/>", encoding="utf-8"
        )
        (self.root / "brand/assets/head.woff2").write_bytes(b"wOF2-head")
        (self.root / "brand/assets/body.woff2").write_bytes(b"wOF2-body")
        (self.root / "product").mkdir()
        (self.root / "product/pack.png").write_bytes(b"\x89PNG\r\n\x1a\nfake")
        self.brand = copy.deepcopy(BRAND)
        self.facts = copy.deepcopy(FACTS)
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

    def run_plan(self, overwrite: bool = False) -> dict[str, Any]:
        (self.root / "brand/brand.json").write_text(json.dumps(self.brand), encoding="utf-8")
        (self.root / "product/facts.json").write_text(json.dumps(self.facts), encoding="utf-8")
        spec_path = self.root / "spec.json"
        spec_path.write_text(json.dumps(self.spec), encoding="utf-8")
        return MODULE.plan(spec_path, None, overwrite)

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
        self.assertEqual(command[command.index("--require-local-font") + 1], "Lumo Display")
        self.assertIn("claim_1=Keeps drinks hot for 6 hours", command)
        self.assertEqual(job["claims"][0]["ref"], "heat-6h")

    def test_unsupported_claim_is_refused(self) -> None:
        self.spec["angles"][0]["claims"] = ["heat-6h", "taste"]
        with self.assertRaisesRegex(ValueError, "needs-substantiation"):
            self.run_plan()
        self.assertFalse((self.root / "statics").exists())

    def test_unknown_claim_and_unsupported_offer_are_refused(self) -> None:
        self.spec["angles"][0]["claims"] = ["Best mug ever"]
        with self.assertRaisesRegex(ValueError, "not in the product facts"):
            self.run_plan()
        self.spec["angles"][0]["claims"] = ["heat-6h"]
        self.facts["facts"][4]["status"] = "needs-substantiation"
        with self.assertRaisesRegex(ValueError, "only supported claims"):
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

    def test_pinned_hash_mismatch_and_banned_word_are_refused(self) -> None:
        self.spec["brand_kit_sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "pin"):
            self.run_plan()
        del self.spec["brand_kit_sha256"]
        self.spec["angles"][0]["headline"] = "A Miracle mug"
        with self.assertRaisesRegex(ValueError, "banned word"):
            self.run_plan()

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
        (self.root / "brand/brand.json").write_text(json.dumps(self.brand), encoding="utf-8")
        (self.root / "product/facts.json").write_text(json.dumps(self.facts), encoding="utf-8")
        (self.root / "spec.json").write_text(json.dumps(self.spec), encoding="utf-8")
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "plan", str(self.root / "spec.json")],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn("type must be one of", result.stderr)


if __name__ == "__main__":
    unittest.main()
