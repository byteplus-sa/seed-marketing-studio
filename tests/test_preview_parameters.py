import copy
import json
import shlex
import subprocess
import sys
import unittest
from pathlib import Path

import test_variant_matrix as fixtures

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / ".agents/scripts"))
import prepare_request
import variant_matrix


class PreviewParameterTests(unittest.TestCase):
    setUp = fixtures.VariantMatrixTests.setUp
    approve_hero_for_brief = fixtures.VariantMatrixTests.approve_hero_for_brief
    write = fixtures.VariantMatrixTests.write

    def evidence(self, values):
        path = self.project / "capabilities/video.json"
        evidence = json.loads(path.read_text())
        evidence["preview"]["params"].update(values)
        evidence["parameters"].update({key: {} for key in values})
        path.write_text(json.dumps(evidence))
        return evidence

    def test_preview_parameter_round_trip_retains_exact_json_types(self):
        values = {
            "boolean_string": "true", "false_string": "false", "null_string": "null",
            "integer_string": "123", "float_string": "1.0", "array_string": "[1, false]",
            "object_string": '{"enabled":true}', "quoted_string": '"quoted"',
            "empty_string": "", "whitespace": "  null  ", "escaped": 'a="b"\\c\n',
            "long_string": "x" * 10000, "empty_array": [], "empty_object": {},
            "null_value": None, "boolean_value": True, "integer_value": 123,
            "float_value": 1.0, "large_integer": 10 ** 100,
            "nested": {"values": [True, False, None, "null", 1, 1.0, {"text": "[1]"}]},
        }
        evidence = self.evidence(values)
        options = variant_matrix.parser().parse_args([
            "register", "matrix.json", "--project", str(self.project), *fixtures.VIDEO_FLAGS,
        ])
        options.stage = "draft"
        options.execution_profile = {"evidence": evidence}
        original = copy.deepcopy(evidence)
        for route in ("object-swap", "hook-opening", "motion-recast"):
            with self.subTest(route=route):
                expected = dict(evidence["preview"]["params"])
                if route == "hook-opening":
                    expected["duration"] = 4
                encoded = variant_matrix.step_params(route, options)
                self.assertEqual(
                    json.dumps(prepare_request.parse_params(encoded), sort_keys=True),
                    json.dumps(expected, sort_keys=True),
                )
                self.assertEqual(evidence, original)
        self.assertEqual(variant_matrix.step_params("language-dub", options), [])
        self.assertEqual(variant_matrix.step_params("ratio-reframe", options), [])

    def test_real_matrix_commands_preserve_json_looking_preview_strings(self):
        self.approve_hero_for_brief("---\nreview_mode: default\n---\n")
        (self.project / "studio").mkdir()
        values = {
            "style": "true", "label": "null", "variant": "123",
            "payload": '{"enabled":true}',
            "nested": {"enabled": True, "values": [None, "1", 1, False]},
        }
        evidence = self.evidence(values)
        evidence["parameters"].update({key: {"const": value} for key, value in values.items()})
        (self.project / "capabilities/video.json").write_text(json.dumps(evidence))
        matrix_path = self.write(fixtures.base_matrix(axes={"hook": ["hook-callout"]}))
        result = subprocess.run(
            [sys.executable, "-B", str(ROOT / ".agents/scripts/variant_matrix.py"),
             "register", str(matrix_path), "--project", str(self.project), *fixtures.VIDEO_FLAGS],
            capture_output=True, text=True, check=False, timeout=30,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        operations = [operation for row in json.loads(result.stdout)["operations"].values() for operation in row]
        self.assertEqual(len(operations), 1)
        operation = operations[0]
        expected = {**evidence["preview"]["params"], "duration": 4}
        for key in ("hash_command", "register_command"):
            command = shlex.split(shlex.join(operation[key]))
            self.assertEqual(
                json.dumps(prepare_request.parse_params(fixtures.params(command)), sort_keys=True),
                json.dumps(expected, sort_keys=True),
            )
        command = operation["hash_command"]
        prompt = self.project / fixtures.option_values(command, "--prompt")[0]
        prompt.parent.mkdir(parents=True, exist_ok=True)
        prompt.write_text("A ceramic cup turns slowly.\n")
        prepared = subprocess.run(
            [sys.executable, "-B", str(ROOT / command[3]), *command[4:]],
            capture_output=True, text=True, check=False, timeout=30,
        )
        self.assertEqual(prepared.returncode, 0, prepared.stdout + prepared.stderr)
        request = json.loads(prepared.stdout)["request"]
        self.assertEqual(json.dumps(request["params"], sort_keys=True), json.dumps(expected, sort_keys=True))
        review = self.project / fixtures.option_values(operation["register_command"], "--review")[0]
        review.write_text(json.dumps({
            "schema_version": 1, "request_sha256": request["request_sha256"],
            "reviewer_status": "complete", "checks": [
                {"rule_id": rule, "status": "pass", "evidence": "Synthetic compiler contract only"}
                for rule in sorted(fixtures.required_rules(operation["register_command"]))
            ],
        }))
        command = operation["register_command"]
        registered = subprocess.run(
            [sys.executable, "-B", str(ROOT / command[3]), *command[4:]],
            capture_output=True, text=True, check=False, timeout=30,
        )
        self.assertEqual(registered.returncode, 0, registered.stdout + registered.stderr)
        self.assertEqual(json.loads(registered.stdout)["request_sha256"], request["request_sha256"])
        persisted = json.loads((self.project / "task_ids.json").read_text())["tasks"][0]
        self.assertEqual(json.dumps(persisted["params"], sort_keys=True), json.dumps(expected, sort_keys=True))


if __name__ == "__main__":
    unittest.main()
