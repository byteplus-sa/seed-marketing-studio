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

    def test_next_matrix_can_test_a_market_axis(self):
        path, _ = self.ingest()
        out = self.root / "market" / "matrix.json"
        code, result = self.run_cli(
            "next-matrix",
            path,
            "--matrix",
            self.write("matrix.json", MATRIX),
            "--kpi",
            "ctr",
            "--axis",
            "market=market-north,market-south",
            "--hero-value",
            "market-home",
            "--out",
            out,
        )
        self.assertEqual(code, 0, result)
        draft = json.loads(out.read_text())
        self.assertEqual(draft["axes"], {"market": ["market-north", "market-south"]})
        self.assertEqual(draft["hero"]["values"]["market"], "market-home")

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

    def test_abbreviated_scientific_and_percent_values_are_never_misparsed(self):
        self.assertEqual(loop.parse_number("1.2E+05", "."), 120000)
        self.assertEqual(loop.parse_number("3e2", "."), 300)
        self.assertEqual(loop.parse_number("1,2E+05", ","), 120000)
        for bad in ("1.5K", "2.3M", "1B", "3%", "12abc", "x12", "1,2,3", "12,34"):
            with self.assertRaises(ValueError, msg=bad):
                loop.parse_number(bad, ".")
        with self.assertRaisesRegex(ValueError, "abbreviated"):
            loop.parse_number("1.5K", ".")
        with self.assertRaisesRegex(ValueError, "percent"):
            loop.parse_number("3%", ".")

    def test_only_known_currency_marks_are_stripped(self):
        self.assertEqual(loop.parse_number("USD 12.50", ".", "USD"), 12.5)
        self.assertEqual(loop.parse_number("12.50 EUR", ".", "EUR"), 12.5)
        self.assertEqual(loop.parse_number("£1,000", "."), 1000)
        with self.assertRaisesRegex(ValueError, "currency"):
            loop.parse_number("EUR 12.50", ".", "USD")
        with self.assertRaises(ValueError):
            loop.parse_number("USD 12.50", ".")

    def test_abbreviated_cells_become_issues_not_wrong_numbers(self):
        export = HEADER + f"{HERO},2026-10-01,1.5K,1000,300,3%,$1,0\n"
        _, metrics = self.ingest(export=export)
        record = metrics["records"][0]
        self.assertIsNone(record["impressions"])
        self.assertIsNone(record["clicks"])
        self.assertEqual(
            {i["field"] for i in metrics["issues"]}, {"impressions", "clicks"}
        )

    def test_frequency_uses_reach_only_when_every_row_has_it(self):
        full = [
            {"impressions": 100, "reach": 50, "frequency": None},
            {"impressions": 100, "reach": 50, "frequency": None},
        ]
        self.assertEqual(loop.aggregate(full)["frequency"], 2)
        partial = [
            {"impressions": 100, "reach": 50, "frequency": None},
            {"impressions": 900, "reach": None, "frequency": None},
        ]
        self.assertIsNone(loop.aggregate(partial)["frequency"])
        mixed = [
            {"impressions": 100, "reach": 50, "frequency": 2.0},
            {"impressions": 300, "reach": None, "frequency": 4.0},
        ]
        self.assertEqual(loop.aggregate(mixed)["frequency"], 3.5)

    def test_longest_variant_name_wins_over_a_contained_shorter_name(self):
        names = ["acme_hook", "acme_hook-callout", "acme_other"]
        self.assertEqual(
            loop.match_variant("acme_hook-callout - Copy", names),
            ("acme_hook-callout", ["acme_hook-callout"]),
        )
        variant, found = loop.match_variant("acme_hook vs acme_other", names)
        self.assertIsNone(variant)
        self.assertEqual(found, ["acme_hook", "acme_other"])

    def test_default_impression_floor_keeps_tiny_ads_out_of_the_ranking(self):
        export = HEADER + (
            f"{HERO},2026-10-01,5000,4000,1000,50,$50,5\n"
            f"{CALLOUT},2026-10-01,1,1,1,1,$1,1\n"
        )
        path, _ = self.ingest(export=export)
        _, ranking = self.run_cli("rank", path, "--kpi", "ctr")
        self.assertEqual(ranking["min_impressions"], loop.DEFAULT_MIN_IMPRESSIONS)
        self.assertEqual([e["key"] for e in ranking["ranked"]], [HERO])
        tiny = next(e for e in ranking["not_ranked"] if e["key"] == CALLOUT)
        self.assertIn("impressions", tiny["reason"])
        _, lowered = self.run_cli("rank", path, "--kpi", "ctr", "--min-impressions", 0)
        winner = lowered["ranked"][0]
        self.assertEqual(winner["key"], CALLOUT)
        self.assertTrue(winner["low_volume"])
        self.assertFalse(lowered["ranked"][1]["low_volume"])

    def test_floor_without_an_impressions_column_says_why(self):
        columns = {k: v for k, v in MAPPING["columns"].items() if k != "impressions"}
        path, _ = self.ingest(mapping={"columns": columns})
        _, ranking = self.run_cli("rank", path, "--kpi", "cpa")
        self.assertEqual(ranking["ranked"], [])
        reasons = {e["key"]: e["reason"] for e in ranking["not_ranked"]}
        self.assertIn("missing impressions", reasons[HERO])
        self.assertIn("missing impressions", reasons[CALLOUT])
        self.assertEqual(reasons["Mystery ad"], "zero conversions")
        _, unfloored = self.run_cli(
            "rank", path, "--kpi", "cpa", "--min-impressions", 0
        )
        self.assertEqual(unfloored["ranked"][0]["key"], CALLOUT)
        self.assertTrue(unfloored["ranked"][0]["low_volume"])

    def test_next_matrix_warns_when_the_winner_is_low_volume(self):
        export = HEADER + f"{CALLOUT},2026-10-01,10,10,5,5,$1,1\n"
        path, _ = self.ingest(export=export)
        code, result = self.run_cli(
            "next-matrix",
            path,
            "--matrix",
            self.write("matrix.json", MATRIX),
            "--kpi",
            "ctr",
            "--axis",
            "hook=hook-x",
            "--min-impressions",
            0,
            "--out",
            self.root / "draft.json",
        )
        self.assertEqual(code, 0, result)
        self.assertTrue(any("low volume" in w for w in result["warnings"]))

    def test_round_trip_plan_cost_ingest_next_matrix_cost(self):
        matrix = dict(
            MATRIX,
            naming="{campaign}_{concept}_{hook}_{talent}_{outfit}_{ratio}_v{nn}",
            unit_cost_usd={"hook": 2, "talent": 5, "outfit": 4, "ratio": 0},
        )
        matrix["hero"] = dict(
            MATRIX["hero"], values=dict(MATRIX["hero"]["values"], outfit="outfit-a")
        )
        matrix_path = self.write("matrix.json", matrix)
        code, plan = self.variant_cli("plan", matrix_path)
        self.assertEqual(code, 0, plan)
        code, cost = self.variant_cli("cost", matrix_path)
        self.assertEqual(code, 0, cost)
        names = [row["name"] for row in plan["rows"]]
        export = HEADER + "".join(
            f"{name} - ad,2026-10-01,{5000 + 1000 * i},4000,900,{40 + 20 * i},$50,4\n"
            for i, name in enumerate(names)
        )
        path, metrics = self.ingest(export=export, plan=plan)
        self.assertEqual(metrics["unmatched_ads"], [])
        out = self.root / "round-02" / "matrix.json"
        code, result = self.run_cli(
            "next-matrix",
            path,
            "--matrix",
            matrix_path,
            "--kpi",
            "ctr",
            "--axis",
            "outfit=outfit-b,outfit-c",
            "--out",
            out,
        )
        self.assertEqual(code, 0, result)
        draft = json.loads(out.read_text())
        self.assertEqual(draft["naming"], matrix["naming"])
        self.assertEqual(draft["unit_cost_usd"], matrix["unit_cost_usd"])
        code, second = self.variant_cli("cost", out)
        self.assertEqual(code, 0, second)
        self.assertEqual(second["total_estimated_usd"], 8)
        self.assertTrue(all("_outfit-" in row["name"] for row in second["rows"]))

    def test_next_matrix_refuses_custom_naming_without_the_new_axis(self):
        path, _ = self.ingest()
        matrix = dict(
            MATRIX, naming="{campaign}_{concept}_{hook}_{talent}_{ratio}_v{nn}"
        )
        code, result = self.run_cli(
            "next-matrix",
            path,
            "--matrix",
            self.write("matrix.json", matrix),
            "--kpi",
            "ctr",
            "--axis",
            "outfit=outfit-b",
            "--hero-value",
            "outfit-a",
            "--out",
            self.root / "draft.json",
        )
        self.assertEqual(code, 1)
        self.assertIn("{outfit}", result["error"])

    def variant_cli(self, *argv):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            code = variant_matrix.main([str(item) for item in argv])
        return code, json.loads(output.getvalue())


if __name__ == "__main__":
    unittest.main()
