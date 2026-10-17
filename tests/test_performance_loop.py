import contextlib
import importlib.util
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / ".agents/skills/ad-performance-loop/scripts/performance_loop.py"
SPEC = importlib.util.spec_from_file_location("performance_loop", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
loop = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = loop
SPEC.loader.exec_module(loop)
sys.path.insert(0, str(ROOT / ".agents/scripts"))
import variant_matrix

HERO = "acme_launch_hook-demo_vp-a_9x16_v01"
CALLOUT = "acme_launch_hook-callout_vp-a_9x16_v01"
TALENT = "acme_launch_hook-demo_vp-b_9x16_v01"
PLAN = {
    "rows": [
        {
            "name": HERO,
            "values": {"hook": "hook-demo", "talent": "vp-a", "ratio": "9:16"},
        },
        {
            "name": CALLOUT,
            "values": {"hook": "hook-callout", "talent": "vp-a", "ratio": "9:16"},
        },
        {
            "name": TALENT,
            "values": {"hook": "hook-demo", "talent": "vp-b", "ratio": "9:16"},
        },
    ]
}
MAPPING = {
    "columns": {
        "ad_name": "Ad name",
        "date": "Day",
        "impressions": "Impressions",
        "reach": "Reach",
        "views_3s": "3s views",
        "clicks": "Clicks",
        "spend": "Spend",
        "conversions": "Purchases",
    },
    "currency": "USD",
}
HEADER = "Ad name,Day,Impressions,Reach,3s views,Clicks,Spend,Purchases\n"
EXPORT = HEADER + (
    f'{HERO},2026-10-01,"10,000",8000,"2,500",120,$150.00,6\n'
    f'{HERO},2026-10-08,"10,000",5000,"2,000",80,$150.00,3\n'
    f'{CALLOUT} - copy,2026-10-01,"9,000",8000,"3,600",140,$140.00,7\n'
    f'{CALLOUT} - copy,2026-10-08,"9,000",8000,"3,700",150,$140.00,8\n'
    "Mystery ad,2026-10-01,0,0,0,0,$0.00,0\n"
)
MATRIX = {
    "schema_version": 1,
    "status": "approved",
    "campaign": "acme",
    "concept": "launch",
    "hero": {
        "shot_id": "s01_sh010",
        "take": "t01",
        "sha256": "b" * 64,
        "values": {"hook": "hook-demo", "talent": "vp-a", "ratio": "9:16"},
    },
    "axes": {"hook": ["hook-callout"], "talent": ["vp-b"]},
    "strategy": "one_axis_at_a_time",
    "max_variants": 6,
    "budget_usd": 30,
}


class PerformanceLoopTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory(prefix="performance-loop-test-")
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)

    def write(self, name, content):
        path = self.root / name
        path.write_text(content if isinstance(content, str) else json.dumps(content))
        return path

    def run_cli(self, *argv):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            code = loop.main([str(item) for item in argv])
        return code, json.loads(output.getvalue())

    def ingest(self, export=EXPORT, mapping=MAPPING, plan=PLAN):
        args = [
            "ingest",
            self.write("export.csv", export),
            "--map",
            self.write("map.json", mapping),
        ]
        if plan is not None:
            args += ["--variants", self.write("plan.json", plan)]
        args += ["--out", self.root / "metrics.json"]
        code, result = self.run_cli(*args)
        self.assertEqual(code, 0, result)
        return self.root / "metrics.json", json.loads(
            (self.root / "metrics.json").read_text()
        )

    def test_numbers_with_currency_and_separators_are_parsed(self):
        self.assertEqual(loop.parse_number("$1,234.50", "."), 1234.5)
        self.assertEqual(loop.parse_number("1.234,50 €", ","), 1234.5)
        self.assertEqual(loop.parse_number("1 234", "."), 1234)
        self.assertEqual(loop.parse_number("(12.00)", "."), -12)
        self.assertIsNone(loop.parse_number("", "."))
        self.assertIsNone(loop.parse_number("--", "."))
        for bad in ("abc", "nan", "inf", "1.2.3"):
            with self.assertRaises(ValueError, msg=bad):
                loop.parse_number(bad, ".")

    def test_ingest_joins_variants_and_reports_unknown_ads(self):
        _, metrics = self.ingest()
        variants = {
            record["ad_name"]: record["variant"] for record in metrics["records"]
        }
        self.assertEqual(variants[HERO], HERO)
        self.assertEqual(variants[f"{CALLOUT} - copy"], CALLOUT)
        self.assertIsNone(variants["Mystery ad"])
        self.assertEqual(metrics["unmatched_ads"], ["Mystery ad"])
        self.assertEqual(metrics["variants_without_data"], [TALENT])
        self.assertEqual(len(metrics["records"]), 5)

    def test_ad_name_matching_two_variants_is_reported_as_ambiguous(self):
        export = HEADER + f"{HERO} vs {CALLOUT},2026-10-01,100,90,10,1,$1,0\n"
        _, metrics = self.ingest(export=export)
        self.assertEqual(
            metrics["ambiguous_ads"][f"{HERO} vs {CALLOUT}"], sorted([HERO, CALLOUT])
        )
        self.assertEqual(metrics["unmatched_ads"], [])

    def test_missing_columns_are_reported_and_block_only_dependent_kpis(self):
        mapping = {"columns": dict(MAPPING["columns"], clicks="Link clicks")}
        path, metrics = self.ingest(mapping=mapping)
        self.assertEqual(metrics["missing_columns"], ["clicks"])
        code, ranking = self.run_cli("rank", path, "--kpi", "ctr")
        self.assertEqual(code, 0)
        self.assertEqual(ranking["ranked"], [])
        self.assertIn(
            "missing clicks", {entity["reason"] for entity in ranking["not_ranked"]}
        )
        _, hook = self.run_cli("rank", path, "--kpi", "hook_rate")
        self.assertEqual(hook["ranked"][0]["key"], CALLOUT)

    def test_unreadable_values_are_recorded_as_issues(self):
        export = HEADER + f"{HERO},not-a-date,lots,1,1,1,$1,0\n"
        _, metrics = self.ingest(export=export)
        fields = {issue["field"] for issue in metrics["issues"]}
        self.assertEqual(fields, {"impressions", "date"})
        self.assertIsNone(metrics["records"][0]["impressions"])

    def test_semicolon_export_with_bom_and_decimal_comma(self):
        export = (
            "﻿"
            + HEADER.replace(",", ";")
            + (f"{HERO};2026-10-01;1.000;800;250;12;15,50 €;2\n")
        )
        mapping = dict(MAPPING, decimal=",")
        _, metrics = self.ingest(export=export, mapping=mapping)
        record = metrics["records"][0]
        self.assertEqual((record["impressions"], record["spend"]), (1000, 15.5))

    def test_empty_ad_names_are_skipped_with_a_reason(self):
        export = HEADER + ",2026-10-01,5,5,5,5,$5,5\n"
        _, metrics = self.ingest(export=export)
        self.assertEqual(
            metrics["skipped_rows"], [{"line": 2, "reason": "empty ad name"}]
        )

    def test_rank_computes_rates_and_excludes_zero_impressions(self):
        path, _ = self.ingest()
        code, ranking = self.run_cli("rank", path, "--kpi", "hook_rate")
        self.assertEqual(code, 0)
        first = ranking["ranked"][0]
        self.assertEqual(first["key"], CALLOUT)
        self.assertAlmostEqual(first["hook_rate"], 7300 / 18000)
        self.assertAlmostEqual(first["ctr"], 290 / 18000)
        self.assertAlmostEqual(first["cpa"], 280 / 15)
        mystery = next(e for e in ranking["not_ranked"] if e["key"] == "Mystery ad")
        self.assertEqual(mystery["reason"], "zero impressions")
        self.assertIn("No external", ranking["note"])

    def test_cpa_ranks_lowest_first_and_min_impressions_filters(self):
        path, _ = self.ingest()
        _, ranking = self.run_cli("rank", path, "--kpi", "cpa")
        self.assertEqual(ranking["direction"], "lower")
        self.assertEqual([e["key"] for e in ranking["ranked"]], [CALLOUT, HERO])
        _, filtered = self.run_cli(
            "rank", path, "--kpi", "cpa", "--min-impressions", 19000
        )
        self.assertEqual([e["key"] for e in filtered["ranked"]], [HERO])

    def test_fatigue_flags_rising_frequency_with_falling_rates(self):
        path, _ = self.ingest()
        code, report = self.run_cli("fatigue", path)
        self.assertEqual(code, 0)
        status = {entity["key"]: entity["status"] for entity in report["entities"]}
        self.assertEqual(status[HERO], "fatigued")
        self.assertEqual(status[CALLOUT], "stable")
        self.assertEqual(status["Mystery ad"], "insufficient_data")

    def test_fatigue_without_reach_or_dates_reports_insufficient_data(self):
        columns = {k: v for k, v in MAPPING["columns"].items() if k != "reach"}
        path, _ = self.ingest(mapping={"columns": columns})
        _, report = self.run_cli("fatigue", path)
        hero = next(e for e in report["entities"] if e["key"] == HERO)
        self.assertEqual(hero["status"], "insufficient_data")
        columns.pop("date")
        path, _ = self.ingest(mapping={"columns": columns})
        _, report = self.run_cli("fatigue", path)
        self.assertEqual(report["entities"], [])
        self.assertIn(HERO, report["undated"])

    def test_next_matrix_keeps_winner_values_and_tests_one_new_axis(self):
        path, _ = self.ingest()
        out = self.root / "next" / "matrix.json"
        code, result = self.run_cli(
            "next-matrix",
            path,
            "--matrix",
            self.write("matrix.json", MATRIX),
            "--kpi",
            "ctr",
            "--axis",
            "outfit=outfit-b,outfit-c",
            "--hero-value",
            "outfit-a",
            "--out",
            out,
        )
        self.assertEqual(code, 0, result)
        draft = json.loads(out.read_text())
        self.assertEqual(result["winner"], CALLOUT)
        self.assertEqual(draft["status"], "draft")
        self.assertEqual(draft["axes"], {"outfit": ["outfit-b", "outfit-c"]})
        self.assertEqual(draft["hero"]["values"]["hook"], "hook-callout")
        self.assertIsNone(draft["hero"]["sha256"])
        self.assertEqual(draft["version"], 2)
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            plan_code = variant_matrix.main(["plan", str(out)])
        plan = json.loads(output.getvalue())
        self.assertEqual(plan_code, 0, plan)
        self.assertEqual(plan["variant_count"], 2)
        code, refused = self.run_cli(
            "next-matrix",
            path,
            "--matrix",
            self.root / "matrix.json",
            "--kpi",
            "ctr",
            "--axis",
            "outfit=outfit-b",
            "--hero-value",
            "outfit-a",
            "--out",
            out,
        )
        self.assertEqual(code, 1)
        self.assertIn("Refusing to overwrite", refused["error"])

    def test_next_matrix_refusals(self):
        path, _ = self.ingest()
        matrix = self.write("matrix.json", MATRIX)
        cases = [
            (["--axis", "outfit=outfit-b"], "--hero-value"),
            (["--axis", "music=a"], "known axis"),
            (["--axis", "hook=a,a"], "unique"),
        ]
        for extra, message in cases:
            code, result = self.run_cli(
                "next-matrix",
                path,
                "--matrix",
                matrix,
                "--kpi",
                "ctr",
                "--out",
                self.root / "draft.json",
                *extra,
            )
            self.assertEqual(code, 1, extra)
            self.assertIn(message, result["error"])
        no_plan, _ = self.ingest(plan=None)
        code, result = self.run_cli(
            "next-matrix",
            no_plan,
            "--matrix",
            matrix,
            "--kpi",
            "ctr",
            "--axis",
            "hook=hook-x",
            "--out",
            self.root / "draft.json",
        )
        self.assertEqual(code, 1)
        self.assertIn("No matched variant", result["error"])

    def test_invalid_mapping_and_missing_ad_column_fail(self):
        export = self.write("export.csv", EXPORT)
        bad = self.write(
            "bad.json", {"columns": {"ad_name": "Ad name", "likes": "Likes"}}
        )
        code, result = self.run_cli("ingest", export, "--map", bad)
        self.assertEqual(code, 1)
        self.assertIn("Unknown mapping fields", result["error"])
        missing = self.write("missing.json", {"columns": {"ad_name": "Campaign"}})
        code, result = self.run_cli("ingest", export, "--map", missing)
        self.assertEqual(code, 1)
        self.assertIn("Ad name column not found", result["error"])
        code, result = self.run_cli(
            "rank", self.write("junk.json", {"x": 1}), "--kpi", "ctr"
        )
        self.assertEqual(code, 1)


if __name__ == "__main__":
    unittest.main()
