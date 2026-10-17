import contextlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / ".agents/scripts"))
import variant_matrix

HERO_HASH = "a" * 64


def base_matrix(**overrides):
    matrix = {
        "schema_version": 1,
        "status": "approved",
        "campaign": "spring-launch",
        "concept": "morning-ritual",
        "hero": {
            "shot_id": "s01_sh010",
            "take": "t03",
            "sha256": HERO_HASH,
            "values": {"hook": "hook-demo-first", "talent": "vp-a", "ratio": "9:16"},
        },
        "axes": {
            "hook": ["hook-demo-first", "hook-callout", "hook-interrupt"],
            "talent": ["vp-b"],
            "ratio": ["4:5", "1:1"],
        },
        "strategy": "one_axis_at_a_time",
        "max_variants": 12,
        "budget_usd": 40,
    }
    matrix.update(overrides)
    return matrix


UNIT_COSTS = [
    "--unit-cost",
    "hook=3",
    "--unit-cost",
    "talent=6",
    "--unit-cost",
    "ratio=0",
]


class VariantMatrixTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory(prefix="variant-matrix-test-")
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)

    def write(self, matrix):
        path = self.root / "matrix.json"
        path.write_text(json.dumps(matrix))
        return path

    def run_cli(self, *argv):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            code = variant_matrix.main([str(item) for item in argv])
        return code, json.loads(output.getvalue())

    def rule_ids(self, result):
        return {finding["rule_id"] for finding in result["findings"]}

    def test_one_axis_at_a_time_changes_exactly_one_axis_per_variant(self):
        code, result = self.run_cli("plan", self.write(base_matrix()))
        self.assertEqual(code, 0)
        rows = result["rows"]
        self.assertEqual(len(rows), 1 + 2 + 1 + 2)
        self.assertEqual(rows[0]["role"], "hero")
        self.assertEqual(rows[0]["changed_axes"], [])
        for row in rows[1:]:
            self.assertEqual(len(row["changed_axes"]), 1)
        self.assertEqual(result["variant_count"], 5)

    def test_hero_value_listed_in_axis_is_not_planned_twice(self):
        code, result = self.run_cli("plan", self.write(base_matrix()))
        self.assertEqual(code, 0)
        hooks = [row["values"]["hook"] for row in result["rows"]]
        self.assertEqual(hooks.count("hook-demo-first"), 4)
        self.assertEqual(
            [row["name"] for row in result["rows"]].count(result["rows"][0]["name"]), 1
        )

    def test_full_factorial_is_the_product_of_levels_including_the_hero(self):
        matrix = base_matrix(strategy="full_factorial", max_variants=20)
        code, result = self.run_cli("plan", self.write(matrix))
        self.assertEqual(code, 0)
        self.assertEqual(len(result["rows"]), 3 * 2 * 3)
        self.assertEqual(sum(row["role"] == "hero" for row in result["rows"]), 1)

    def test_names_are_unique_deterministic_and_follow_the_convention(self):
        path = self.write(base_matrix(version=2))
        first = self.run_cli("plan", path)[1]
        second = self.run_cli("plan", path)[1]
        self.assertEqual(first, second)
        names = [row["name"] for row in first["rows"]]
        self.assertEqual(len(names), len(set(names)))
        self.assertEqual(
            names[0], "spring-launch_morning-ritual_hook-demo-first_vp-a_9x16_v02"
        )
        for name in names:
            self.assertRegex(name, r"^[A-Za-z0-9][A-Za-z0-9_-]*$")

    def test_hero_values_outside_axes_stay_fixed_in_every_name(self):
        matrix = base_matrix(axes={"hook": ["hook-callout"]})
        matrix["hero"]["values"]["outfit"] = "outfit-a"
        code, result = self.run_cli("plan", self.write(matrix))
        self.assertEqual(code, 0)
        self.assertEqual(
            [row["name"] for row in result["rows"]],
            [
                "spring-launch_morning-ritual_hook-demo-first_vp-a_outfit-a_9x16_v01",
                "spring-launch_morning-ritual_hook-callout_vp-a_outfit-a_9x16_v01",
            ],
        )
        self.assertEqual(result["rows"][1]["changed_axes"], ["hook"])

    def test_unknown_axis_is_rejected(self):
        matrix = base_matrix()
        matrix["axes"]["music"] = ["upbeat"]
        code, result = self.run_cli("plan", self.write(matrix))
        self.assertEqual(code, 1)
        self.assertIn("schema.valid", self.rule_ids(result))

    def test_axis_without_hero_value_is_rejected(self):
        matrix = base_matrix()
        matrix["axes"]["language"] = ["es"]
        code, result = self.run_cli("plan", self.write(matrix))
        self.assertEqual(code, 1)
        self.assertIn("matrix.hero_values", self.rule_ids(result))

    def test_naming_without_an_axis_collides_and_is_refused(self):
        matrix = base_matrix(naming="{campaign}_{concept}_{hook}_v{nn}")
        code, result = self.run_cli("plan", self.write(matrix))
        self.assertEqual(code, 1)
        self.assertIn("matrix.unique_names", self.rule_ids(result))

    def test_unknown_naming_placeholder_is_refused(self):
        matrix = base_matrix(naming="{campaign}_{angle}_{hook}_{talent}_{ratio}_v{nn}")
        code, result = self.run_cli("plan", self.write(matrix))
        self.assertEqual(code, 1)
        self.assertIn("matrix.naming", self.rule_ids(result))

    def test_matrix_with_no_change_from_hero_is_refused(self):
        matrix = base_matrix(axes={"hook": ["hook-demo-first"]})
        matrix["hero"]["values"] = {"hook": "hook-demo-first"}
        code, result = self.run_cli("plan", self.write(matrix))
        self.assertEqual(code, 1)
        self.assertIn("matrix.empty", self.rule_ids(result))

    def test_cost_sums_changed_axis_unit_costs(self):
        code, result = self.run_cli("cost", self.write(base_matrix()), *UNIT_COSTS)
        self.assertEqual(code, 0)
        self.assertEqual(result["total_estimated_usd"], 3 * 2 + 6 + 0 * 2)
        self.assertEqual(result["rows"][0]["estimated_cost_usd"], 0)

    def test_matrix_unit_costs_apply_and_cli_overrides_them(self):
        matrix = base_matrix(unit_cost_usd={"hook": 1, "talent": 1, "ratio": 1})
        code, result = self.run_cli(
            "cost", self.write(matrix), "--unit-cost", "talent=9"
        )
        self.assertEqual(code, 0)
        self.assertEqual(result["total_estimated_usd"], 1 * 2 + 9 + 1 * 2)

    def test_cost_over_budget_is_refused(self):
        code, result = self.run_cli(
            "cost", self.write(base_matrix(budget_usd=10)), *UNIT_COSTS
        )
        self.assertEqual(code, 1)
        self.assertIn("matrix.budget", self.rule_ids(result))

    def test_variants_over_max_are_refused_in_plan_and_cost(self):
        path = self.write(base_matrix(max_variants=3))
        plan_code, plan = self.run_cli("plan", path)
        cost_code, cost = self.run_cli("cost", path, *UNIT_COSTS)
        self.assertEqual((plan_code, cost_code), (1, 1))
        self.assertIn("matrix.max_variants", self.rule_ids(plan))
        self.assertIn("matrix.max_variants", self.rule_ids(cost))

    def test_missing_unit_cost_is_refused_rather_than_assumed_zero(self):
        code, result = self.run_cli(
            "cost", self.write(base_matrix()), "--unit-cost", "hook=3"
        )
        self.assertEqual(code, 1)
        self.assertIn("cost.unit_missing", self.rule_ids(result))

    def test_invalid_unit_cost_arguments_are_refused(self):
        path = self.write(base_matrix())
        for item in ("hook=-1", "hook=nan", "music=2", "hook"):
            code, result = self.run_cli("cost", path, "--unit-cost", item)
            self.assertEqual(code, 1, item)
            self.assertIn("input.readable", self.rule_ids(result))

    def test_more_than_five_creatives_warns_without_blocking(self):
        matrix = base_matrix()
        matrix["axes"]["hook"].extend(["hook-pov", "hook-before-after"])
        code, result = self.run_cli("plan", self.write(matrix))
        self.assertEqual(code, 0)
        self.assertIn("matrix.ad_group_size", self.rule_ids(result))

    def test_routes_follow_axis_and_swap_rules(self):
        matrix = base_matrix(
            strategy="full_factorial",
            max_variants=50,
            axes={
                "talent": ["vp-b"],
                "location": ["loc-kitchen"],
                "product": ["sku-b"],
                "outfit": ["outfit-b"],
                "language": ["es"],
            },
        )
        matrix["hero"]["values"] = {
            "talent": "vp-a",
            "location": "loc-studio",
            "product": "sku-a",
            "outfit": "outfit-a",
            "language": "en",
        }
        code, result = self.run_cli("plan", self.write(matrix))
        self.assertEqual(code, 0)
        by_change = {tuple(row["changed_axes"]): row for row in result["rows"]}
        recast = by_change[("talent", "location")]["steps"]
        self.assertEqual([step["route"] for step in recast], ["motion-recast"])
        swaps = by_change[("product", "outfit")]["steps"]
        self.assertEqual(
            [step["route"] for step in swaps], ["object-swap", "object-swap"]
        )
        dub = by_change[("language",)]["steps"][0]
        self.assertEqual(dub["route"], "language-dub")
        self.assertIn("audio-dubbing", dub["skills"])

    def test_ratio_change_is_not_a_provider_operation(self):
        code, result = self.run_cli("plan", self.write(base_matrix()))
        self.assertEqual(code, 0)
        ratio_rows = [row for row in result["rows"] if row["changed_axes"] == ["ratio"]]
        self.assertTrue(ratio_rows)
        for row in ratio_rows:
            self.assertEqual(row["steps"][0]["route"], "ratio-reframe")
            self.assertFalse(row["steps"][0]["provider_operation"])

    def test_register_prints_prepare_request_commands_and_writes_nothing(self):
        project = self.root / "project"
        code, result = self.run_cli(
            "register", self.write(base_matrix()), "--project", project, *UNIT_COSTS
        )
        self.assertEqual(code, 0)
        self.assertTrue(result["dry_run"])
        self.assertFalse(project.exists())
        operations = result["operations"]
        self.assertNotIn(result["rows"][0]["name"], operations)
        hook_row = next(
            row for row in result["rows"] if row["changed_axes"] == ["hook"]
        )
        [operation] = operations[hook_row["name"]]
        self.assertIn(".agents/scripts/prepare_request.py", operation["hash_command"])
        self.assertNotIn("--register", operation["hash_command"])
        self.assertEqual(operation["register_command"][-2:], ["--write", "--register"])
        ratio_row = next(
            row for row in result["rows"] if row["changed_axes"] == ["ratio"]
        )
        self.assertEqual(operations[ratio_row["name"]], [])

    def test_register_chains_sequential_operations_in_one_row(self):
        matrix = base_matrix(
            strategy="full_factorial",
            axes={"product": ["sku-b"], "outfit": ["outfit-b"]},
        )
        matrix["hero"]["values"] = {"product": "sku-a", "outfit": "outfit-a"}
        _, result = self.run_cli(
            "register",
            self.write(matrix),
            "--project",
            self.root / "project",
            "--unit-cost",
            "product=5",
            "--unit-cost",
            "outfit=5",
        )
        both = next(row for row in result["rows"] if len(row["changed_axes"]) == 2)
        first, second = result["operations"][both["name"]]
        self.assertIsNone(first["after"])
        self.assertEqual(second["after"], first["asset"])
        self.assertNotEqual(first["asset"], second["asset"])

    def test_register_refuses_draft_or_unbound_hero(self):
        matrix = base_matrix(status="draft")
        matrix["hero"]["sha256"] = None
        code, result = self.run_cli(
            "register", self.write(matrix), "--project", self.root, *UNIT_COSTS
        )
        self.assertEqual(code, 1)
        self.assertNotIn("operations", result)
        self.assertTrue({"matrix.status", "matrix.hero_hash"} <= self.rule_ids(result))

    def test_register_refuses_over_budget(self):
        code, result = self.run_cli(
            "register",
            self.write(base_matrix(budget_usd=1)),
            "--project",
            self.root,
            *UNIT_COSTS,
        )
        self.assertEqual(code, 1)
        self.assertNotIn("operations", result)

    def test_unreadable_matrix_is_reported(self):
        path = self.root / "matrix.json"
        path.write_text("{not json")
        code, result = self.run_cli("plan", path)
        self.assertEqual(code, 1)
        self.assertIn("input.readable", self.rule_ids(result))
        code, result = self.run_cli("plan", self.root / "missing.json")
        self.assertEqual(code, 1)


if __name__ == "__main__":
    unittest.main()
