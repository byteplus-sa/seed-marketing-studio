import contextlib
import hashlib
import io
import json
import shlex
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / ".agents/scripts"))
import operation_store
import prepare_request
import studio_project
import test_native_draft
import test_seedance_capability_profiles
import variant_matrix
from test_seedance_capability_profiles import profile

HERO_BYTES = b"approved hero take"
HERO_HASH = hashlib.sha256(HERO_BYTES).hexdigest()
HERO_DECISION = "decisions/s01_sh010_t03.json"
HERO_TAKE_FILE = "scenes/s01_sh010/s01_sh010_t03_final.mp4"
FACTORIAL_NOTE = "User asked for every combination of the listed values."


def base_matrix(**overrides):
    if overrides.get("strategy") == "full_factorial":
        overrides.setdefault("notes", FACTORIAL_NOTE)
    matrix = {
        "schema_version": 1,
        "status": "approved",
        "campaign": "spring-launch",
        "concept": "morning-ritual",
        "hero": {
            "shot_id": "s01_sh010",
            "take": "t03",
            "sha256": HERO_HASH,
            "decision_ref": HERO_DECISION,
            "take_file": HERO_TAKE_FILE,
            "values": {"hook": "hook-demo-first", "talent": "vp-a", "ratio": "9:16"},
        },
        "axes": {
            "hook": ["hook-demo-first", "hook-callout", "hook-interrupt"],
            "talent": ["vp-b"],
            "ratio": ["4:5", "1:1"],
        },
        "strategy": "one_axis_at_a_time",
        "max_variants": 12,
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
VIDEO_FLAGS = [
    "--video-model",
    "video-model-a",
    "--video-operation",
    "video_create_task",
    "--capabilities",
    "capabilities/video.json",
    "--expected-provider",
    "fixture-provider",
    "--expected-tool-schema-revision",
    "fixture-r1",
]
AUDIO_FLAGS = [
    "--audio-model", "audio-model-a", "--audio-operation", "audio_dub",
    "--audio-capabilities", "capabilities/audio.json",
]
COMMON_RULES = {
    "ad.claims_supported",
    "ad.no_fabricated_testimonial",
    "brand.copy_rules",
    "library.pin_current",
    "ad.variant_one_axis",
    "ad.variant_count_gate",
}
SHOT_RULES = {"shot.plan_bound", "shot.variety", "shot.axis_carry"}


def option_values(command, flag):
    return [command[i + 1] for i, item in enumerate(command) if item == flag]


def params(command):
    return option_values(command, "--param")


def required_rules(command):
    return set(option_values(command, "--required-rule"))


def swap_matrix(**overrides):
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
        **overrides,
    )
    matrix["hero"]["values"] = {
        "talent": "vp-a",
        "location": "loc-studio",
        "product": "sku-a",
        "outfit": "outfit-a",
        "language": "en",
    }
    return matrix


def market_matrix(**overrides):
    axes = {
        "hook": ["hook-callout"],
        "market": ["market-b", "market-c"],
        "ratio": ["4:5"],
    }
    matrix = base_matrix(**{"axes": axes, **overrides})
    matrix["hero"]["values"] = {
        "hook": "hook-demo-first",
        "market": "market-a",
        "ratio": "9:16",
    }
    return matrix


MARKET_COSTS = [
    "--unit-cost",
    "hook=3",
    "--unit-cost",
    "market=5",
    "--unit-cost",
    "ratio=0",
]


class VariantMatrixTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory(prefix="variant-matrix-test-")
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.project = self.root / "project"
        decision = self.project / HERO_DECISION
        decision.parent.mkdir(parents=True)
        decision.write_text('{"decision": "approved"}')
        (self.project / "project.md").write_text("---\nreview_mode: strict\n---\n")
        take = self.project / HERO_TAKE_FILE
        take.parent.mkdir(parents=True)
        take.write_bytes(HERO_BYTES)
        evidence = profile()
        evidence.update(
            model="video-model-a", operation="video_create_task",
            operations=["video_create_task"],
            parameters={
                "resolution": {"enum": ["480p", "720p", "1080p"]},
                "duration": {"type": "number", "minimum": 4},
            },
            preview={"support": "verified", "kind": "ordinary", "params": {"resolution": "480p"}},
            duration={"support": "verified", "minimum_s": 4},
            workspace_policy={"preview_required": False},
        )
        capabilities = self.project / "capabilities/video.json"
        capabilities.parent.mkdir()
        capabilities.write_text(json.dumps(evidence))
        (capabilities.parent / "audio.json").write_text(json.dumps({
            "model": "audio-model-a", "source": "offline audio fixture",
            "verified_at": "2026-10-22T00:00:00Z", "operations": ["audio_dub"],
            "parameters": {}, "reference_roles": [], "max_references": 0,
        }))

    def project_files(self):
        return sorted(path for path in self.project.rglob("*"))

    def test_audio_only_and_mixed_commands_reuse_exact_operation_bindings_offline(self):
        (self.project / "project.md").write_text("---\nreview_mode: default\n---\n")
        (self.project / "studio").mkdir()
        audio = profile()
        audio.update(
            model="audio-model-a", operation="audio_dub", operations=["audio_dub"],
            transport="curl", parameters={}, reference_roles=[], max_references=0,
            workspace_policy={"preview_required": False},
            preview={"support": "unsupported", "kind": "none", "params": {}},
        )
        (self.project / "capabilities/audio.json").write_text(json.dumps(audio))
        video = json.loads((self.project / "capabilities/video.json").read_text())
        video["transport"] = "curl"
        (self.project / "capabilities/video.json").write_text(json.dumps(video))
        for mixed in (False, True):
            matrix = base_matrix(axes={"language": ["es"]})
            matrix["hero"]["values"] = {"language": "en"}
            if mixed:
                matrix["axes"]["hook"] = ["hook-callout"]
                matrix["hero"]["values"]["hook"] = "hook-demo-first"
            code, result = self.register(
                matrix, *VIDEO_FLAGS, *AUDIO_FLAGS, "--transport", "curl",
                "--audio-expected-provider", "fixture-provider",
                "--audio-expected-tool-schema-revision", "fixture-r1",
                "--take", "t02" if mixed else "t01",
            )
            self.assertEqual(code, 0, result)
            for operations in result["operations"].values():
                for operation in operations:
                    command = operation["hash_command"]
                    expected = "capabilities/audio.json" if operation["route"] == "language-dub" else "capabilities/video.json"
                    for key in ("hash_command", "register_command"):
                        self.assertEqual(option_values(operation[key], "--capabilities"), [expected])
                        self.assertEqual(option_values(operation[key], "--transport"), ["curl"])
                    prompt = self.project / option_values(command, "--prompt")[0]
                    prompt.parent.mkdir(parents=True, exist_ok=True)
                    prompt.write_text("Offline fixture intent.\n")
                    prepared, findings = prepare_request.run(prepare_request.parser().parse_args(command[4:]))
                    self.assertEqual(findings, [])
                    request = prepared["request"]
                    if operation["route"] == "language-dub":
                        self.assertEqual(request["params"], {})
                        self.assertEqual(request["extensions"]["execution_profile"]["evidence"], audio)
                    review_file = self.project / option_values(operation["register_command"], "--review")[0]
                    review_file.write_text(json.dumps({
                        "schema_version": 1, "request_sha256": request["request_sha256"],
                        "reviewer_status": "complete",
                        "checks": [{"rule_id": rule, "status": "pass", "evidence": "Synthetic offline contract check only"} for rule in operation["required_rules"]],
                    }))
                    registered, findings = prepare_request.run(prepare_request.parser().parse_args(operation["register_command"][4:]))
                    self.assertEqual(findings, [])
                    self.assertEqual(registered["request_sha256"], request["request_sha256"])
                    operation_store.transition_operation(self.project, registered["registered"], "prepared", "submitting")

    def test_optional_no_preview_matrix_emits_only_supported_execution_controls(self):
        path = self.project / "capabilities/video.json"
        evidence = json.loads(path.read_text())
        evidence["preview"] = {"support": "unsupported", "kind": "none", "params": {}}
        path.write_text(json.dumps(evidence))
        code, result = self.register(base_matrix(axes={"hook": ["hook-callout"]}), *VIDEO_FLAGS)
        self.assertEqual(code, 0, result)
        _, operation = self.hook_operation(result)
        self.assertEqual(operation["params"], ["duration=4"])

    def test_required_ordinary_matrix_final_runs_emitted_commands_and_blocks_stale_selection(self):
        fixture = test_native_draft.NativeDraftTests()
        fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        source = fixture.profiled_source(native=False)
        (fixture.root / "studio").mkdir()
        evidence = fixture.caps
        evidence["parameters"]["duration"] = {"type": "number", "minimum": 2.5}
        evidence["reference_roles"] = ["first_frame"]
        evidence["max_references"] = 1
        evidence["modality_limits"]["Image"] = 1
        (fixture.root / "frame.png").write_bytes(b"synthetic selected still fixture")
        (fixture.root / "frame.md").write_text("---\nselected_variant: frame.png\n---\n")
        (fixture.root / "prompt.md").write_text("@Image 1 defines the opening composition.\n")
        source["references"] = prepare_request.build_references(
            fixture.root, ["frame.png:first_frame:frame.md:selected_variant"]
        )
        source["prompt_sha256"] = hashlib.sha256((fixture.root / "prompt.md").read_bytes()).hexdigest()
        decision_path = fixture.root / "decisions/select-draft.json"
        decision = json.loads(decision_path.read_text())
        decision["upstream_sha256"] = {
            "prompt.md": source["prompt_sha256"],
            "frame.png": source["references"][0]["sha256"],
        }
        decision_path.write_text(json.dumps(decision))
        source["params"]["duration"] = 2.5
        fixture.rehash(source)
        fixture.write_registry(source)
        (fixture.root / "caps.json").write_text(json.dumps(evidence))
        matrix = base_matrix(axes={"hook": ["hook-callout"]})
        matrix["hero"].update(
            take_file="cup_t01.mp4", decision_ref="decisions/select-draft.json",
            sha256=hashlib.sha256((fixture.root / "cup_t01.mp4").read_bytes()).hexdigest(),
        )
        path = self.write(matrix)
        row = variant_matrix.expand(matrix)[1]
        flags = [
            "register", str(path), "--project", str(fixture.root),
            "--video-model", "fixture-video", "--video-operation", "generate",
            "--capabilities", "caps.json", "--expected-provider", "fixture-provider",
            "--expected-tool-schema-revision", "fixture-r1", "--stage", "final",
            "--final-resolution", "1080p", "--hook-performance", "non-performance",
        ]
        _, findings = variant_matrix.run(variant_matrix.parser().parse_args(flags))
        self.assertTrue(variant_matrix.blocking(findings))
        flags += ["--ordinary-final-selection", f"{row['name']}={source['operation_id']}:decisions/select-draft.json"]
        result, findings = variant_matrix.run(variant_matrix.parser().parse_args(flags))
        self.assertFalse(variant_matrix.blocking(findings), findings)
        [operation] = result["operations"][row["name"]]
        command = operation["hash_command"]
        for command_key in ("hash_command", "register_command"):
            self.assertEqual(
                option_values(operation[command_key], "--ref"),
                ["frame.png:first_frame:frame.md:selected_variant"],
            )
        prompt = fixture.root / option_values(command, "--prompt")[0]
        prompt.parent.mkdir(parents=True)
        prompt.write_bytes((fixture.root / source["prompt_file"]).read_bytes())
        prepared, findings = prepare_request.run(prepare_request.parser().parse_args(command[4:]))
        self.assertEqual(findings, [])
        self.assertEqual(prepared["request"]["references"], source["references"])
        review = fixture.root / option_values(operation["register_command"], "--review")[0]
        review.write_text(json.dumps({
            "schema_version": 1, "request_sha256": prepared["request_sha256"],
            "reviewer_status": "complete", "checks": [
                {"rule_id": rule, "status": "pass", "evidence": "Synthetic contract check, no playback claim"}
                for rule in operation["required_rules"]
            ],
        }))
        registered, findings = prepare_request.run(prepare_request.parser().parse_args(operation["register_command"][4:]))
        self.assertEqual(findings, [])
        self.assertEqual(registered["request_sha256"], prepared["request_sha256"])
        operation_store.transition_operation(fixture.root, registered["registered"], "prepared", "submitting")
        (fixture.root / "cup_t01.mp4").write_bytes(b"stale source")
        _, findings = variant_matrix.run(variant_matrix.parser().parse_args(flags))
        self.assertTrue(variant_matrix.blocking(findings))

    def test_audio_destination_mismatch_and_missing_mixed_evidence_emit_no_commands(self):
        matrix = base_matrix(axes={"language": ["es"], "hook": ["hook-callout"]})
        matrix["hero"]["values"] = {"language": "en", "hook": "hook-demo-first"}
        flags = [*VIDEO_FLAGS, "--audio-model", "audio-model-a", "--audio-operation", "audio_dub"]
        code, result = self.register(matrix, *flags)
        self.assertEqual(code, 1, result)
        self.assertNotIn("operations", result)
        audio = profile()
        audio.update(
            model="audio-model-a", operation="audio_dub", operations=["audio_dub"],
            parameters={}, reference_roles=[], max_references=0,
            workspace_policy={"preview_required": False},
            preview={"support": "unsupported", "kind": "none", "params": {}},
        )
        (self.project / "capabilities/audio.json").write_text(json.dumps(audio))
        for flag, value in (
            ("--audio-expected-provider", "wrong-provider"),
            ("--audio-expected-tool-schema-revision", "wrong-revision"),
            ("--transport", "curl"),
        ):
            code, result = self.register(matrix, *VIDEO_FLAGS, *AUDIO_FLAGS, flag, value)
            self.assertEqual(code, 1, result)
            self.assertNotIn("operations", result)

    def ordinary_final_fixture(self, value):
        fixture = test_native_draft.NativeDraftTests()
        fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        source = fixture.profiled_source(native=False)
        (fixture.root / "studio").mkdir()
        parameter_type = {
            str: "string", bool: "boolean", int: "integer", float: "number",
            type(None): "null", list: "array", dict: "object",
        }[type(value)]
        fixture.caps["parameters"]["style"] = {"type": parameter_type}
        source["params"]["style"] = value
        fixture.rehash(source)
        fixture.write_registry(source)
        (fixture.root / "caps.json").write_text(json.dumps(fixture.caps))
        matrix = base_matrix(axes={"hook": ["hook-callout"]})
        decision = json.loads((fixture.root / "decisions/select-draft.json").read_text())
        matrix["hero"].update(
            take_file="cup_t01.mp4", decision_ref="decisions/select-draft.json",
            sha256=decision["selected_sha256"],
        )
        matrix_path = fixture.root / "matrix.json"
        matrix_path.write_text(json.dumps(matrix))
        row = variant_matrix.expand(matrix)[1]
        flags = [
            "register", str(matrix_path), "--project", str(fixture.root),
            "--video-model", source["model"], "--video-operation", source["operation"],
            "--capabilities", "caps.json", "--expected-provider", "fixture-provider",
            "--expected-tool-schema-revision", "fixture-r1", "--stage", "final",
            "--final-resolution", "1080p", "--hook-performance", "non-performance",
            "--ordinary-final-selection",
            f"{row['name']}={source['operation_id']}:decisions/select-draft.json",
        ]
        return fixture, source, row, flags

    def offline_cli(self, script, arguments):
        result = subprocess.run(
            [sys.executable, "-B", str(ROOT / script), *arguments],
            capture_output=True, text=True, check=False, timeout=30,
        )
        self.assertEqual(result.stderr, "", result.stderr)
        return result.returncode, json.loads(result.stdout)

    def test_ordinary_final_emitted_cli_roundtrips_all_json_types_and_quoted_strings(self):
        values = (
            "cinematic", "true", "null", "123", "[1]", '{"v":1}', "",
            "a 'quoted' \"string\" \\ path\n$(no-command); key=value",
            "x" * 10000, 123, 1.25, True, False, None, [], [1, "true"],
            {"v": 1, "nested": [None, False, "null"]},
        )
        for value in values:
            with self.subTest(value=value):
                fixture, source, row, flags = self.ordinary_final_fixture(value)
                original_source = json.loads((fixture.root / "task_ids.json").read_text())["tasks"][0]
                code, result = self.offline_cli(".agents/scripts/variant_matrix.py", flags)
                self.assertEqual(code, 0, result)
                [operation] = result["operations"][row["name"]]
                for command_key in ("hash_command", "register_command"):
                    command = operation[command_key]
                    quoted = shlex.join(command)
                    self.assertEqual(shlex.split(quoted), command)
                    parsed = prepare_request.parse_params(params(shlex.split(quoted)))
                    self.assertEqual(parsed, {**source["params"], "resolution": "1080p"})
                    self.assertIs(type(parsed["style"]), type(value))
                command = operation["hash_command"]
                prompt = fixture.root / option_values(command, "--prompt")[0]
                prompt.parent.mkdir(parents=True)
                prompt.write_bytes((fixture.root / source["prompt_file"]).read_bytes())
                code, prepared = self.offline_cli(command[3], command[4:])
                self.assertEqual(code, 0, prepared)
                self.assertEqual(prepared["request"]["params"]["style"], value)
                self.assertIs(type(prepared["request"]["params"]["style"]), type(value))
                review = fixture.root / option_values(operation["register_command"], "--review")[0]
                review.write_text(json.dumps({
                    "schema_version": 1, "request_sha256": prepared["request_sha256"],
                    "reviewer_status": "complete",
                    "checks": [
                        {"rule_id": rule, "status": "pass",
                         "evidence": "Synthetic offline contract check; no media inspection"}
                        for rule in operation["required_rules"]
                    ],
                }))
                command = operation["register_command"]
                code, registered = self.offline_cli(command[3], command[4:])
                self.assertEqual(code, 0, registered)
                self.assertEqual(registered["request_sha256"], prepared["request_sha256"])
                tasks = operation_store.read_registry(fixture.root / "task_ids.json")["tasks"]
                self.assertEqual(len(tasks), 2)
                self.assertEqual(tasks[0], original_source)
                self.assertEqual(tasks[1]["params"], prepared["request"]["params"])
                self.assertIs(type(tasks[1]["params"]["style"]), type(value))
                operation_store.transition_operation(
                    fixture.root, registered["registered"], "prepared", "submitting"
                )

    def test_ordinary_final_changed_or_unsupported_values_fail_without_writes(self):
        fixture, _, row, flags = self.ordinary_final_fixture("true")
        code, result = self.offline_cli(".agents/scripts/variant_matrix.py", flags)
        self.assertEqual(code, 0, result)
        [operation] = result["operations"][row["name"]]
        command = operation["hash_command"]
        prompt = fixture.root / option_values(command, "--prompt")[0]
        prompt.parent.mkdir(parents=True)
        prompt.write_bytes((fixture.root / "prompt.md").read_bytes())
        code, prepared = self.offline_cli(command[3], command[4:])
        self.assertEqual(code, 0, prepared)
        review = fixture.root / option_values(operation["register_command"], "--review")[0]
        review.write_text(json.dumps({
            "schema_version": 1, "request_sha256": prepared["request_sha256"],
            "reviewer_status": "complete",
            "checks": [
                {"rule_id": rule, "status": "pass", "evidence": "Synthetic contract only"}
                for rule in operation["required_rules"]
            ],
        }))
        before = {path: path.read_bytes() for path in fixture.root.rglob("*") if path.is_file()}
        for value in ("changed", True, None, 123, [], {}):
            with self.subTest(value=value):
                command = list(operation["register_command"])
                index = next(index for index, item in enumerate(command) if item.startswith("style="))
                command[index] = f"style={json.dumps(value)}"
                code, rejected = self.offline_cli(command[3], command[4:])
                self.assertEqual(code, 1, rejected)
                expected_rule = "seedance.draft_promotion" if isinstance(value, str) else "model.supported_mode"
                self.assertIn(expected_rule, self.rule_ids(rejected))
                self.assertEqual(
                    before, {path: path.read_bytes() for path in fixture.root.rglob("*") if path.is_file()}
                )
        fixture.caps["parameters"]["style"] = {"type": "boolean"}
        (fixture.root / "caps.json").write_text(json.dumps(fixture.caps))
        before = {path: path.read_bytes() for path in fixture.root.rglob("*") if path.is_file()}
        code, rejected = self.offline_cli(".agents/scripts/variant_matrix.py", flags)
        self.assertEqual(code, 1, rejected)
        self.assertNotIn("operations", rejected)
        self.assertIn("model.supported_mode", self.rule_ids(rejected))
        self.assertEqual(
            before, {path: path.read_bytes() for path in fixture.root.rglob("*") if path.is_file()}
        )

    def emitted_identity_fixture(self, value, style_schema=None):
        fixture = test_seedance_capability_profiles.OrdinaryFinalIdentityTests()
        fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        source = fixture.selected_preview({"style": value}, version=2, style_schema=style_schema)
        matrix = base_matrix(axes={"hook": ["hook-callout"]})
        decision = json.loads((fixture.root / "decisions/select-preview.json").read_text())
        matrix["hero"].update(
            take_file="cup.mp4", decision_ref="decisions/select-preview.json",
            sha256=decision["selected_sha256"],
        )
        matrix_path = fixture.root / "matrix.json"
        matrix_path.write_text(json.dumps(matrix))
        row = variant_matrix.expand(matrix)[1]
        code, result = fixture.cli(".agents/scripts/variant_matrix.py", [
            "register", str(matrix_path), "--project", str(fixture.root),
            "--video-model", source["model"], "--video-operation", source["operation"],
            "--capabilities", "caps.json", "--expected-provider", "fixture-provider",
            "--expected-tool-schema-revision", "fixture-r1", "--stage", "final",
            "--final-resolution", "1080p", "--hook-performance", "non-performance",
            "--ordinary-final-selection",
            f"{row['name']}={source['operation_id']}:decisions/select-preview.json",
        ])
        self.assertEqual(code, 0, result)
        [operation] = result["operations"][row["name"]]
        prompt = fixture.root / option_values(operation["hash_command"], "--prompt")[0]
        prompt.parent.mkdir(parents=True)
        prompt.write_bytes((fixture.root / source["prompt_file"]).read_bytes())
        return fixture, source, operation

    def test_emitted_nested_json_identity_records_registers_and_reaches_submitting(self):
        for value in (
            {"enabled": True, "nested": [False, {"value": 1}]},
            [0, {"enabled": 1}, None, "true"], {}, [],
        ):
            with self.subTest(value=value):
                fixture, source, operation = self.emitted_identity_fixture(value)
                command = operation["hash_command"]
                self.assertEqual(shlex.split(shlex.join(command)), command)
                code, prepared = fixture.cli(command[3], [*command[4:], "--write"])
                self.assertEqual(code, 0, prepared)
                request = json.loads((fixture.root / prepared["path"]).read_text())
                self.assertEqual(
                    json.dumps(request["params"]["style"], sort_keys=True),
                    json.dumps(source["params"]["style"], sort_keys=True),
                )
                review_path = fixture.record(request, prepared["path"], operation["required_rules"])
                command = list(operation["register_command"])
                command[command.index("--review") + 1] = review_path
                code, registered = fixture.cli(command[3], command[4:])
                self.assertEqual(code, 0, registered)
                self.assertEqual(registered["request_sha256"], request["request_sha256"])
                operation_store.transition_operation(
                    fixture.root, registered["registered"], "prepared", "submitting",
                )
                tasks = operation_store.read_registry(fixture.root / "task_ids.json")["tasks"]
                self.assertEqual(tasks[0], source)
                self.assertEqual(tasks[1]["submission_status"], "submitting")

    def test_emitted_nested_substitutions_and_restrictive_schema_block_without_writes(self):
        cases = (
            ({"enabled": True}, {"enabled": 1}, None),
            ({"enabled": 1}, {"enabled": True}, None),
            ([False, {"enabled": True}], [0, {"enabled": 1}], None),
            ([0, {"enabled": 1}], [False, {"enabled": True}], None),
            ({"enabled": True}, {"enabled": 1}, {
                "type": "object", "properties": {"enabled": {"type": "boolean"}},
                "required": ["enabled"], "additionalProperties": False,
            }),
        )
        for original, changed, schema in cases:
            with self.subTest(original=original, changed=changed, schema=schema):
                fixture, source, operation = self.emitted_identity_fixture(original, schema)
                command = list(operation["hash_command"])
                parameter_index = next(index for index, item in enumerate(command) if item.startswith("style="))
                command[parameter_index] = f"style={json.dumps(changed)}"
                before = fixture.snapshot()
                code, rejected = fixture.cli(command[3], [*command[4:], "--write"])
                self.assertEqual(code, 1, rejected)
                rule = "model.supported_mode" if schema else "seedance.draft_promotion"
                self.assertIn(rule, self.rule_ids(rejected))
                self.assertEqual(before, fixture.snapshot())
                candidate = prepare_request.build_request(
                    fixture.root, prepare_request.parser().parse_args(command[4:]),
                )
                (fixture.root / "candidate.json").write_text(json.dumps(candidate))
                review_path = fixture.record(candidate, "candidate.json", operation["required_rules"])
                command = list(operation["register_command"])
                command[parameter_index] = f"style={json.dumps(changed)}"
                command[command.index("--review") + 1] = review_path
                before = fixture.snapshot()
                code, rejected = fixture.cli(command[3], command[4:])
                self.assertEqual(code, 1, rejected)
                self.assertIn(rule, self.rule_ids(rejected))
                self.assertEqual(before, fixture.snapshot())
                self.assertEqual(
                    operation_store.read_registry(fixture.root / "task_ids.json")["tasks"][0], source,
                )

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

    def test_default_mode_omits_blanket_craft_rules_but_keeps_draft_first(self):
        (self.project / "project.md").write_text("---\ntitle: Fixture\n---\n")
        code, result = self.run_cli(
            "register",
            self.write(base_matrix()),
            "--project",
            self.project,
            *UNIT_COSTS,
            *VIDEO_FLAGS,
            "--final-resolution",
            "720p",
        )
        self.assertEqual(code, 0, result)
        self.assertEqual(result["review_mode"], "default")
        self.assertEqual(result["stage"], "draft")
        for operations in result["operations"].values():
            for operation in operations:
                command = operation["register_command"]
                self.assertIn("resolution=480p", params(command))
                self.assertNotIn("draft=true", params(command))
                self.assertFalse(SHOT_RULES & required_rules(command))
                self.assertNotIn("video.text_free", required_rules(command))
                self.assertNotIn("ad.variant_budget_gate", required_rules(command))
                self.assertTrue(
                    {
                        "ad.claims_supported",
                        "ad.no_fabricated_testimonial",
                        "brand.copy_rules",
                        "library.pin_current",
                    }
                    <= required_rules(command)
                )

    def test_default_mode_can_draft_before_delivery_target_is_known(self):
        (self.project / "project.md").write_text("# Legacy brief\n")
        code, result = self.run_cli(
            "register",
            self.write(base_matrix()),
            "--project",
            self.project,
            *UNIT_COSTS,
            *VIDEO_FLAGS,
        )
        self.assertEqual(code, 0, result)
        self.assertEqual(result["stage"], "draft")

    def test_seedance_native_draft_flags_reach_every_emitted_video_command(self):
        for mode in ("default", "strict"):
            (self.project / "project.md").write_text(f"---\nreview_mode: {mode}\n---\n")
            for model in ("seedance-2.5", "dreamina-seedance-2-5-premium-261001"):
                flags = [
                    model if flag == "video-model-a" else flag for flag in VIDEO_FLAGS
                ]
                code, result = self.register(
                    base_matrix(), *UNIT_COSTS, *flags, "--final-resolution", "1080p"
                )
                self.assertEqual(code, 0, result)
                for operations in result["operations"].values():
                    for operation in operations:
                        for key in ("hash_command", "register_command"):
                            self.assertIn("resolution=480p", params(operation[key]))
                            self.assertIn("draft=true", params(operation[key]))

    def test_seedance_non_draft_stages_require_native_promotion_handoff(self):
        flags = [
            "seedance-2-5" if flag == "video-model-a" else flag for flag in VIDEO_FLAGS
        ]
        for stage in ("production", "final"):
            code, result = self.register(
                base_matrix(),
                *UNIT_COSTS,
                *flags,
                "--stage",
                stage,
                "--final-resolution",
                "1080p",
            )
            self.assertEqual(code, 1, result)
            self.assertIn("seedance.draft_promotion", self.rule_ids(result))
            self.assertNotIn("operations", result)

    def test_native_matrix_hash_command_prepares_boolean_draft_without_provider(self):
        (self.project / "project.md").write_text("---\nreview_mode: default\n---\n")
        flags = [
            "seedance-2-5" if flag == "video-model-a" else flag for flag in VIDEO_FLAGS
        ]
        code, result = self.register(base_matrix(), *UNIT_COSTS, *flags)
        self.assertEqual(code, 0, result)
        _, operation = self.hook_operation(result)
        command = operation["hash_command"]
        prompt = self.project / option_values(command, "--prompt")[0]
        prompt.parent.mkdir(parents=True, exist_ok=True)
        prompt.write_text("A plain ceramic cup turns slowly.\n")
        prepared = subprocess.run(
            [sys.executable, str(ROOT / command[3]), *command[4:]],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(prepared.returncode, 0, prepared.stdout + prepared.stderr)
        request = json.loads(prepared.stdout)["request"]
        self.assertEqual(request["params"]["resolution"], "480p")
        self.assertIs(request["params"]["draft"], True)
        self.assertEqual(request["params"]["duration"], 4)
        self.assertFalse((self.project / "task_ids.json").exists())

    def test_native_recast_and_swap_use_draft_but_audio_has_no_video_parameters(self):
        flags = [
            "seedance-2-5" if flag == "video-model-a" else flag for flag in VIDEO_FLAGS
        ]
        costs = [
            item
            for axis in (
                "talent",
                "location",
                "product",
                "outfit",
                "language",
                "motion-recast",
            )
            for item in ("--unit-cost", f"{axis}=1")
        ]
        code, result = self.register(
            swap_matrix(budget_usd=1000), *costs, *flags, *AUDIO_FLAGS
        )
        self.assertEqual(code, 0, result)
        routes = set()
        for operations in result["operations"].values():
            for operation in operations:
                routes.add(operation["route"])
                for key in ("hash_command", "register_command"):
                    values = params(operation[key])
                    if operation["route"] == "language-dub":
                        self.assertEqual(values, [])
                    else:
                        self.assertIn("resolution=480p", values)
                        self.assertIn("draft=true", values)
        self.assertTrue({"motion-recast", "object-swap", "language-dub"} <= routes)

    def test_invalid_review_mode_refuses_variant_commands(self):
        (self.project / "project.md").write_text("---\nreview_mode: quick\n---\n")
        code, result = self.run_cli(
            "register",
            self.write(base_matrix()),
            "--project",
            self.project,
            *UNIT_COSTS,
            *VIDEO_FLAGS,
        )
        self.assertEqual(code, 1, result)
        self.assertNotIn("operations", result)

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

    def test_cost_over_legacy_budget_is_reported_without_refusal(self):
        code, result = self.run_cli(
            "cost", self.write(base_matrix(budget_usd=10)), *UNIT_COSTS
        )
        self.assertEqual(code, 0, result)
        self.assertEqual(result["total_estimated_usd"], 12)
        self.assertNotIn("budget_usd", result)

    def test_no_budget_or_prices_allows_plan_cost_and_registration(self):
        for mode in ("default", "strict"):
            (self.project / "project.md").write_text(f"---\nreview_mode: {mode}\n---\n")
            for command in ("plan", "cost", "register"):
                with self.subTest(mode=mode, command=command):
                    flags = (
                        ["--project", self.project, *VIDEO_FLAGS]
                        if command == "register" else []
                    )
                    code, result = self.run_cli(command, self.write(base_matrix()), *flags)
                    self.assertEqual(code, 0, result)
                    self.assertEqual(result["variant_count"], 5)
                    if command != "plan":
                        self.assertIsNone(result["total_estimated_usd"])
                        self.assertEqual(result["unknown_cost_keys"], ["hook", "talent"])
                        self.assertEqual(result["rows"][0]["estimated_cost_usd"], 0)
                    if command == "register":
                        self.assertTrue(result["operations"])

    def test_legacy_budget_values_are_inert(self):
        for value in (0, -1, None, "obsolete", {"cap": 0}, 0.004):
            with self.subTest(value=value):
                code, result = self.register(
                    base_matrix(budget_usd=value), *UNIT_COSTS, *VIDEO_FLAGS
                )
                self.assertEqual(code, 0, result)
                self.assertEqual(result["total_estimated_usd"], 12)
                self.assertNotIn("budget_usd", result)

    def test_json_prices_reject_invalid_values_but_allow_unknown(self):
        for value in (-1, "invalid", True, float("nan"), float("inf")):
            with self.subTest(value=value):
                code, result = self.run_cli(
                    "cost", self.write(base_matrix(unit_cost_usd={"hook": value}))
                )
                self.assertEqual(code, 1, result)
        code, result = self.run_cli(
            "cost", self.write(base_matrix(unit_cost_usd={"hook": None}))
        )
        self.assertEqual(code, 0, result)
        self.assertIsNone(result["total_estimated_usd"])

    def test_forecast_overflow_is_unknown_not_a_generation_gate(self):
        code, result = self.register(
            base_matrix(unit_cost_usd={"hook": 1e308, "talent": 1e308}),
            *VIDEO_FLAGS,
        )
        self.assertEqual(code, 0, result)
        self.assertIsNone(result["total_estimated_usd"])
        self.assertTrue(result["operations"])

    def test_enormous_json_price_is_rejected_without_crashing(self):
        for command in ("plan", "cost", "register"):
            with self.subTest(command=command):
                code, result = self.run_cli(
                    command,
                    self.write(base_matrix(unit_cost_usd={"hook": 10**1000})),
                    *(["--project", self.project] if command == "register" else []),
                )
                self.assertEqual(code, 1, result)
                self.assertIn("cost.unit_invalid", self.rule_ids(result))

    def test_unrepresentable_forecast_totals_are_unknown(self):
        for amounts in ([10**1000], [10**1000, 1.0], [1e308, 1e308]):
            with self.subTest(amounts=amounts):
                self.assertIsNone(variant_matrix.estimated_total(amounts))
        self.assertEqual(variant_matrix.estimated_total([10**300, 1.0]), 1e300)

    def test_variants_over_max_are_refused_in_plan_and_cost(self):
        path = self.write(base_matrix(max_variants=3))
        plan_code, plan = self.run_cli("plan", path)
        cost_code, cost = self.run_cli("cost", path, *UNIT_COSTS)
        self.assertEqual((plan_code, cost_code), (1, 1))
        self.assertIn("matrix.max_variants", self.rule_ids(plan))
        self.assertIn("matrix.max_variants", self.rule_ids(cost))

    def test_large_factorial_is_rejected_before_expansion_for_every_command(self):
        matrix = base_matrix(
            strategy="full_factorial",
            axes={
                axis: ["base", *(f"value-{number}" for number in range(9))]
                for axis in variant_matrix.AXES
            },
        )
        matrix["hero"]["values"] = {axis: "base" for axis in variant_matrix.AXES}
        path = self.write(matrix)
        for command in ("plan", "cost", "register"):
            with self.subTest(command=command):
                flags = (
                    ["--project", str(self.project)] if command == "register" else []
                )
                with mock.patch.object(
                    variant_matrix, "expand", side_effect=AssertionError("expanded")
                ) as expand:
                    code, result = self.run_cli(command, path, *flags)
                expand.assert_not_called()
                self.assertEqual(code, 1)
                self.assertEqual(result["variant_count"], 99_999_999)
                self.assertEqual(result["rows"], [])
                self.assertEqual(self.rule_ids(result), {"matrix.max_variants"})
                self.assertNotIn("operations", result)

    def test_one_axis_limit_is_checked_before_expansion(self):
        with mock.patch.object(
            variant_matrix, "expand", side_effect=AssertionError("expanded")
        ):
            code, result = self.run_cli("plan", self.write(base_matrix(max_variants=4)))
        self.assertEqual(code, 1)
        self.assertEqual(result["variant_count"], 5)

    def test_variant_cap_excludes_the_hero_and_allows_exact_boundary(self):
        for strategy, count in (("one_axis_at_a_time", 5), ("full_factorial", 17)):
            with self.subTest(strategy=strategy):
                code, result = self.run_cli(
                    "plan",
                    self.write(base_matrix(strategy=strategy, max_variants=count)),
                )
                self.assertEqual(code, 0)
                self.assertEqual(result["variant_count"], count)
                self.assertEqual(len(result["rows"]), count + 1)

    def test_missing_unit_cost_is_unknown_rather_than_assumed_zero(self):
        code, result = self.run_cli(
            "cost", self.write(base_matrix()), "--unit-cost", "hook=3"
        )
        self.assertEqual(code, 0, result)
        self.assertIn("cost.unit_missing", self.rule_ids(result))
        self.assertIsNone(result["total_estimated_usd"])
        self.assertEqual(result["unknown_cost_keys"], ["talent"])
        costs = {tuple(row["changed_axes"]): row["estimated_cost_usd"] for row in result["rows"]}
        self.assertIsNone(costs[("talent",)])
        self.assertEqual(costs[("hook",)], 3)

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
        code, result = self.run_cli("plan", self.write(swap_matrix()))
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

    def test_object_swap_maps_source_subjects_before_the_swap(self):
        _, result = self.run_cli("plan", self.write(swap_matrix()))
        row = next(r for r in result["rows"] if r["changed_axes"] == ["product"])
        skills = row["steps"][0]["skills"]
        self.assertLess(
            skills.index("source-subject-map"), skills.index("seedance-object-swap")
        )

    def test_combined_talent_and_location_cost_one_recast_not_two_swaps(self):
        path = self.write(swap_matrix(budget_usd=1000))
        costs = [
            "--unit-cost",
            "talent=6",
            "--unit-cost",
            "location=6",
            "--unit-cost",
            "product=6",
            "--unit-cost",
            "outfit=6",
            "--unit-cost",
            "language=2",
        ]
        code, result = self.run_cli("cost", path, *costs)
        self.assertEqual(code, 0, result)
        self.assertIsNone(result["total_estimated_usd"])
        self.assertIn("cost.unit_missing", self.rule_ids(result))
        code, result = self.run_cli(
            "cost", path, *costs, "--unit-cost", "motion-recast=9"
        )
        self.assertEqual(code, 0, result)
        by_change = {tuple(row["changed_axes"]): row for row in result["rows"]}
        recast = by_change[("talent", "location")]
        self.assertEqual(recast["estimated_cost_usd"], 9)
        dubbed = by_change[("talent", "location", "language")]
        self.assertEqual(dubbed["estimated_cost_usd"], 2)
        self.assertEqual(dubbed["base_variant"], recast["name"])
        self.assertEqual(by_change[("product", "outfit")]["estimated_cost_usd"], 6)
        self.assertEqual(by_change[("talent",)]["estimated_cost_usd"], 6)
        recasts = [
            operation
            for operation in result["operations_estimate"]
            if operation["axes"] == ["talent", "location"]
        ]
        self.assertEqual(len(recasts), 1)
        self.assertIn(dubbed["name"], recasts[0]["used_by"])

    def test_matrix_may_record_a_recast_unit_cost_but_no_unknown_key(self):
        costs = {"talent": 1, "location": 1, "product": 1, "outfit": 1}
        matrix = swap_matrix(
            budget_usd=1000, unit_cost_usd={**costs, "language": 1, "motion-recast": 4}
        )
        code, result = self.run_cli("cost", self.write(matrix))
        self.assertEqual(code, 0, result)
        self.assertEqual(result["unit_cost_usd"]["motion-recast"], 4)
        matrix["unit_cost_usd"]["recast"] = 4
        code, result = self.run_cli("plan", self.write(matrix))
        self.assertEqual(code, 1)
        self.assertIn("schema.valid", self.rule_ids(result))

    def test_hook_rows_generate_the_minimum_duration_and_trim_in_studio(self):
        _, result = self.run_cli("plan", self.write(base_matrix()))
        row = next(r for r in result["rows"] if r["changed_axes"] == ["hook"])
        step = row["steps"][0]
        self.assertIsNone(step["generate_duration_s"])
        self.assertIn("trim", step["studio_note"].lower())

    def test_hook_rows_use_the_consolidated_ugc_skill(self):
        code, result = self.run_cli("plan", self.write(base_matrix()))
        self.assertEqual(code, 0, result)
        rows = [row for row in result["rows"] if row["changed_axes"] == ["hook"]]
        self.assertTrue(rows)
        for row in rows:
            self.assertEqual(
                row["steps"][0]["skills"],
                ["seedance-ugc-ads", "seedance-prompt"],
            )

    def test_ratio_change_is_not_a_provider_operation(self):
        code, result = self.run_cli("plan", self.write(base_matrix()))
        self.assertEqual(code, 0)
        ratio_rows = [row for row in result["rows"] if row["changed_axes"] == ["ratio"]]
        self.assertTrue(ratio_rows)
        for row in ratio_rows:
            self.assertEqual(row["steps"][0]["route"], "ratio-reframe")
            self.assertFalse(row["steps"][0]["provider_operation"])

    def test_ratio_rows_route_to_a_per_ratio_delivery_project_not_a_studio_shot(self):
        _, result = self.run_cli("plan", self.write(base_matrix()))
        ratio_row = next(r for r in result["rows"] if r["changed_axes"] == ["ratio"])
        self.assertIsNone(ratio_row["studio"])
        self.assertEqual(ratio_row["delivery"]["skill"], "ad-delivery-formats")
        self.assertEqual(ratio_row["delivery"]["aspect"], ratio_row["values"]["ratio"])
        campaign = base_matrix()["campaign"]
        ratio = ratio_row["values"]["ratio"].replace(":", "x")
        self.assertEqual(
            ratio_row["delivery"]["project"], f"projects/{campaign}-{ratio}"
        )
        hook_row = next(r for r in result["rows"] if r["changed_axes"] == ["hook"])
        self.assertNotIn("aspect", hook_row["studio"]["frontmatter"])

    def test_register_prints_prepare_request_commands_and_writes_nothing(self):
        before = self.project_files()
        code, result = self.run_cli(
            "register",
            self.write(base_matrix()),
            "--project",
            self.project,
            *UNIT_COSTS,
            *VIDEO_FLAGS,
        )
        self.assertEqual(code, 0, result)
        self.assertTrue(result["dry_run"])
        self.assertEqual(self.project_files(), before)
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

    def test_sequential_swap_row_builds_on_the_single_swap_row(self):
        matrix = base_matrix(
            strategy="full_factorial",
            axes={"product": ["sku-b"], "outfit": ["outfit-b"]},
        )
        matrix["hero"]["values"] = {"product": "sku-a", "outfit": "outfit-a"}
        code, result = self.register(
            matrix, "--unit-cost", "product=5", "--unit-cost", "outfit=5", *VIDEO_FLAGS
        )
        self.assertEqual(code, 0, result)
        by_change = {tuple(row["changed_axes"]): row for row in result["rows"]}
        product = by_change[("product",)]
        both = by_change[("product", "outfit")]
        [product_swap] = result["operations"][product["name"]]
        [outfit_swap] = result["operations"][both["name"]]
        self.assertIsNone(product_swap["after"])
        self.assertEqual(outfit_swap["after"], product["name"])
        self.assertEqual(both["base_variant"], product["name"])
        self.assertEqual(outfit_swap["asset"], f"{both['name']}_t01_draft")
        self.assertEqual(result["total_estimated_usd"], 5 * 3)
        self.assertEqual(both["estimated_cost_usd"], 5)

    def test_register_refuses_draft_or_unbound_hero(self):
        matrix = base_matrix(status="draft")
        matrix["hero"]["sha256"] = None
        code, result = self.register(matrix, *UNIT_COSTS, *VIDEO_FLAGS)
        self.assertEqual(code, 1)
        self.assertNotIn("operations", result)
        self.assertTrue({"matrix.status", "matrix.hero_hash"} <= self.rule_ids(result))

    def test_register_allows_cost_above_legacy_budget(self):
        code, result = self.register(
            base_matrix(budget_usd=1), *UNIT_COSTS, *VIDEO_FLAGS
        )
        self.assertEqual(code, 0, result)
        self.assertTrue(result["operations"])

    def test_unreadable_matrix_is_reported(self):
        path = self.root / "matrix.json"
        path.write_text("{not json")
        code, result = self.run_cli("plan", path)
        self.assertEqual(code, 1)
        self.assertIn("input.readable", self.rule_ids(result))
        code, result = self.run_cli("plan", self.root / "missing.json")
        self.assertEqual(code, 1)

    def bind_fixture_profile(self, extra):
        if "--video-model" in extra:
            model = extra[extra.index("--video-model") + 1]
            if variant_matrix.is_seedance_25(model):
                path = self.project / "capabilities/video.json"
                evidence = json.loads(path.read_text())
                evidence["model"] = model
                evidence["parameters"]["draft"] = {"type": "boolean"}
                evidence["preview"] = {
                    "support": "verified", "kind": "native_draft",
                    "params": {"resolution": "480p", "draft": True},
                }
                evidence["workspace_policy"]["preview_required"] = True
                path.write_text(json.dumps(evidence))

    def register(self, matrix, *extra):
        self.bind_fixture_profile(extra)
        return self.run_cli(
            "register",
            self.write(matrix),
            "--project",
            self.project,
            *extra,
        )

    def hook_operation(self, result):
        row = next(r for r in result["rows"] if r["changed_axes"] == ["hook"])
        [operation] = result["operations"][row["name"]]
        return row, operation

    def test_register_refuses_placeholder_model_and_operation(self):
        code, result = self.register(base_matrix(), *UNIT_COSTS)
        self.assertEqual(code, 1)
        self.assertIn("register.placeholder", self.rule_ids(result))
        self.assertNotIn("operations", result)
        code, result = self.register(
            base_matrix(),
            *UNIT_COSTS,
            "--video-model",
            "<video-model-id>",
            "--video-operation",
            "op",
            "--capabilities",
            "caps.json",
        )
        self.assertEqual(code, 1)
        self.assertIn("register.placeholder", self.rule_ids(result))

    def test_register_requires_audio_flags_only_for_language_rows(self):
        costs = ["--unit-cost", "language=2"]
        matrix = base_matrix(axes={"language": ["es"]})
        matrix["hero"]["values"] = {"language": "en"}
        code, result = self.register(matrix, *costs, *VIDEO_FLAGS)
        self.assertEqual(code, 1)
        self.assertIn("register.placeholder", self.rule_ids(result))
        code, result = self.register(matrix, *costs, *VIDEO_FLAGS, *AUDIO_FLAGS)
        self.assertEqual(code, 0, result)

    def test_register_commands_are_480p_drafts_with_required_rules(self):
        code, result = self.register(base_matrix(), *UNIT_COSTS, *VIDEO_FLAGS)
        self.assertEqual(code, 0, result)
        _, operation = self.hook_operation(result)
        for key in ("hash_command", "register_command"):
            command = operation[key]
            self.assertIn("resolution=480p", params(command), key)
            self.assertIn("duration=4", params(command), key)
            self.assertTrue(COMMON_RULES | SHOT_RULES <= required_rules(command), key)
        self.assertEqual(operation["stage"], "draft")

    def test_source_preserving_swaps_record_the_shot_rule_exemption(self):
        code, result = self.register(
            swap_matrix(budget_usd=1000),
            "--unit-cost",
            "talent=1",
            "--unit-cost",
            "location=1",
            "--unit-cost",
            "product=1",
            "--unit-cost",
            "outfit=1",
            "--unit-cost",
            "language=1",
            "--unit-cost",
            "motion-recast=1",
            *VIDEO_FLAGS,
            *AUDIO_FLAGS,
        )
        self.assertEqual(code, 0, result)
        row = next(r for r in result["rows"] if r["changed_axes"] == ["product"])
        [swap] = result["operations"][row["name"]]
        rules = required_rules(swap["register_command"])
        self.assertTrue(COMMON_RULES <= rules)
        self.assertFalse(SHOT_RULES & rules)
        self.assertIn("source-preserving", swap["shot_rule_exemption"])
        self.assertIn("resolution=480p", params(swap["register_command"]))
        self.assertNotIn("duration=4", params(swap["register_command"]))
        dub_row = next(r for r in result["rows"] if r["changed_axes"] == ["language"])
        [dub] = result["operations"][dub_row["name"]]
        self.assertFalse(
            any(p.startswith("resolution=") for p in params(dub["register_command"]))
        )
        self.assertTrue(COMMON_RULES <= required_rules(dub["register_command"]))

    def test_static_by_design_hook_omits_shot_rules_and_records_why(self):
        _, result = self.register(
            base_matrix(), *UNIT_COSTS, *VIDEO_FLAGS, "--static-by-design", "ugc"
        )
        _, operation = self.hook_operation(result)
        self.assertFalse(SHOT_RULES & required_rules(operation["register_command"]))
        self.assertIn("ugc", operation["shot_rule_exemption"])

    def test_character_hook_requires_acting_in_both_modes_even_with_static_camera(self):
        for mode in ("default", "strict"):
            for approval in ("approve_for_me", "ask_for_approval"):
                (self.project / "project.md").write_text(
                    f"---\nreview_mode: {mode}\napproval_mode: {approval}\n---\n"
                )
                flags = ["seedance-2.5" if flag == "video-model-a" else flag for flag in VIDEO_FLAGS]
                self.bind_fixture_profile(flags)
                before = {path: path.read_bytes() for path in self.project_files() if path.is_file()}
                code, result = self.register(
                    base_matrix(), *UNIT_COSTS, *flags, "--static-by-design", "ugc"
                )
                self.assertEqual(code, 0, result)
                _, hook = self.hook_operation(result)
                for key in ("hash_command", "register_command"):
                    self.assertIn("acting.plan_bound", required_rules(hook[key]))
                    self.assertIn("draft=true", params(hook[key]))
                    self.assertIn("resolution=480p", params(hook[key]))
                self.assertIn("acting-direction", hook["skills"])
                self.assertLess(hook["skills"].index("acting-direction"), hook["skills"].index("seedance-acting-console"))
                self.assertLess(hook["skills"].index("seedance-acting-console"), hook["skills"].index("seedance-prompt"))
                self.assertFalse(SHOT_RULES & required_rules(hook["register_command"]))
                self.assertEqual(before, {path: path.read_bytes() for path in self.project_files() if path.is_file()})
                for operations in result["operations"].values():
                    for operation in operations:
                        if operation["route"] != "hook-opening":
                            self.assertNotIn("acting.plan_bound", operation["required_rules"])

    def test_non_performance_hook_omits_acting_without_omitting_campaign_gates(self):
        for mode in ("default", "strict"):
            (self.project / "project.md").write_text(f"---\nreview_mode: {mode}\n---\n")
            code, result = self.register(
                base_matrix(), *UNIT_COSTS, *VIDEO_FLAGS,
                "--hook-performance", "non-performance",
            )
            self.assertEqual(code, 0, result)
            _, hook = self.hook_operation(result)
            self.assertNotIn("acting.plan_bound", hook["required_rules"])
            self.assertNotIn("acting-direction", hook["skills"])
            self.assertIn("Non-performance", hook["performance_scope"])
            self.assertTrue(set(variant_matrix.COMPLIANCE_RULES) <= set(hook["required_rules"]))

    def test_invalid_hook_performance_scope_is_rejected_before_writing(self):
        before = self.project_files()
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as raised:
            self.register(base_matrix(), *UNIT_COSTS, *VIDEO_FLAGS, "--hook-performance", "unknown")
        self.assertEqual(raised.exception.code, 2)
        self.assertEqual(self.project_files(), before)

    def test_asset_ids_carry_take_and_stage_so_finals_and_retakes_register(self):
        _, draft = self.register(base_matrix(), *UNIT_COSTS, *VIDEO_FLAGS)
        row, first = self.hook_operation(draft)
        self.assertEqual(first["asset"], f"{row['name']}_t01_draft")
        _, retake = self.register(
            base_matrix(), *UNIT_COSTS, *VIDEO_FLAGS, "--take", "t02"
        )
        self.assertEqual(
            self.hook_operation(retake)[1]["asset"], f"{row['name']}_t02_draft"
        )
        code, final = self.register(
            base_matrix(),
            *UNIT_COSTS,
            *VIDEO_FLAGS,
            "--stage",
            "final",
            "--final-resolution",
            "1080p",
        )
        self.assertEqual(code, 0, final)
        _, operation = self.hook_operation(final)
        self.assertEqual(operation["asset"], f"{row['name']}_t01_final")
        self.assertIn("resolution=1080p", params(operation["register_command"]))
        self.assertNotIn("resolution=480p", params(operation["register_command"]))
        assets = {
            op["asset"]
            for result in (draft, retake, final)
            for ops in result["operations"].values()
            for op in ops
        }
        self.assertEqual(len(assets), 3 * 3)

    def test_final_stage_needs_a_resolution_and_skips_audio_steps(self):
        code, result = self.register(
            base_matrix(), *UNIT_COSTS, *VIDEO_FLAGS, "--stage", "final"
        )
        self.assertEqual(code, 1)
        self.assertIn("register.final_resolution", self.rule_ids(result))
        matrix = base_matrix(axes={"language": ["es"]})
        matrix["hero"]["values"] = {"language": "en"}
        code, result = self.register(
            matrix,
            "--unit-cost",
            "language=2",
            *VIDEO_FLAGS,
            *AUDIO_FLAGS,
            "--stage",
            "final",
            "--final-resolution",
            "1080p",
        )
        self.assertEqual(code, 0, result)
        self.assertEqual(sum(map(len, result["operations"].values())), 0)

    def test_invalid_take_is_refused(self):
        code, result = self.register(
            base_matrix(), *UNIT_COSTS, *VIDEO_FLAGS, "--take", "../t1"
        )
        self.assertEqual(code, 1)
        self.assertIn("input.readable", self.rule_ids(result))

    def test_variant_paths_live_in_a_studio_discoverable_shot_folder(self):
        _, result = self.register(base_matrix(), *UNIT_COSTS, *VIDEO_FLAGS)
        project = self.root / "project"
        for row in result["rows"]:
            if row["studio"] is None:
                continue
            studio = row["studio"]
            self.assertRegex(studio["shot_id"], r"^variant-[a-z0-9]+(?:-[a-z0-9]+)*$")
            self.assertEqual(studio["directory"], f"scenes/{studio['shot_id']}")
            self.assertEqual(studio["manifest"], f"{studio['directory']}/shot.md")
            for operation in result["operations"][row["name"]]:
                command = operation["register_command"]
                for flag in ("--prompt", "--expected-output", "--review"):
                    [value] = option_values(command, flag)
                    self.assertTrue(value.startswith(studio["directory"] + "/"), value)
            manifest = project / studio["manifest"]
            manifest.parent.mkdir(parents=True)
            lines = [
                f"{key}: '{value}'" for key, value in studio["frontmatter"].items()
            ]
            manifest.write_text("---\n" + "\n".join(lines) + "\n---\n")
        shots = studio_project.discover_shots(project)
        expected = {
            row["studio"]["shot_id"]
            for row in result["rows"]
            if row["studio"] is not None
        }
        self.assertTrue(expected)
        self.assertEqual({shot.shot_id for shot in shots}, expected)

    def test_shot_folder_collisions_are_refused(self):
        matrix = base_matrix(
            strategy="full_factorial",
            naming="{campaign}_{hook}_{talent}",
            axes={"hook": ["x", "x-y"], "talent": ["y-z", "z"]},
        )
        matrix["hero"]["values"] = {"hook": "h", "talent": "t"}
        code, result = self.run_cli("plan", self.write(matrix))
        self.assertEqual(code, 1)
        self.assertNotIn("matrix.unique_names", self.rule_ids(result))
        self.assertIn("matrix.unique_shot_ids", self.rule_ids(result))

    def test_market_axis_expands_in_fixed_order_after_language_and_before_ratio(self):
        self.assertEqual(variant_matrix.AXES[-3:], ("language", "market", "ratio"))
        code, result = self.run_cli("plan", self.write(market_matrix()))
        self.assertEqual(code, 0, result)
        changed = [row["changed_axes"] for row in result["rows"]]
        self.assertEqual(changed, [[], ["hook"], ["market"], ["market"], ["ratio"]])
        self.assertEqual(
            [
                row["values"]["market"]
                for row in result["rows"]
                if row["changed_axes"] == ["market"]
            ],
            ["market-b", "market-c"],
        )

    def test_market_names_include_the_market_id(self):
        _, result = self.run_cli("plan", self.write(market_matrix()))
        names = [row["name"] for row in result["rows"]]
        self.assertEqual(
            names[0], "spring-launch_morning-ritual_hook-demo-first_market-a_9x16_v01"
        )
        self.assertIn(
            "spring-launch_morning-ritual_hook-demo-first_market-b_9x16_v01", names
        )

    def test_market_values_must_be_kebab_case_ids(self):
        for bad in ("Market_B", "market:b", "market.b"):
            matrix = market_matrix()
            matrix["axes"]["market"] = [bad]
            code, result = self.run_cli("plan", self.write(matrix))
            self.assertEqual(code, 1, bad)
            self.assertIn("schema.valid", self.rule_ids(result))
        matrix = market_matrix()
        matrix["hero"]["values"]["market"] = "Market A"
        code, result = self.run_cli("plan", self.write(matrix))
        self.assertEqual(code, 1)
        self.assertIn("schema.valid", self.rule_ids(result))

    def test_market_ids_are_limited_to_48_characters(self):
        matrix = market_matrix(axes={"market": ["m" * 48]})
        code, result = self.run_cli("plan", self.write(matrix))
        self.assertEqual(code, 0, result)
        matrix = market_matrix(axes={"market": ["m" * 49]})
        code, result = self.run_cli("plan", self.write(matrix))
        self.assertEqual(code, 1)
        self.assertIn("schema.valid", self.rule_ids(result))

    def test_market_rows_route_to_ad_localize_without_a_provider_operation(self):
        _, result = self.run_cli("plan", self.write(market_matrix()))
        row = next(r for r in result["rows"] if r["changed_axes"] == ["market"])
        [step] = row["steps"]
        self.assertEqual(step["route"], "market-adapt")
        self.assertEqual(step["skills"], ["ad-localize"])
        self.assertFalse(step["provider_operation"])
        self.assertEqual(step["cost_key"], "market")
        self.assertIn(
            "projects/spring-launch/markets/market-b/market.json", step["note"]
        )

    def test_market_only_rows_have_no_studio_shot_and_a_localize_entry(self):
        _, result = self.run_cli("plan", self.write(market_matrix()))
        row = next(r for r in result["rows"] if r["changed_axes"] == ["market"])
        self.assertIsNone(row["studio"])
        self.assertEqual(
            row["localize"],
            {
                "skill": "ad-localize",
                "market_id": "market-b",
                "variant_key": None,
                "card": "projects/spring-launch/markets/market-b/market.json",
                "inventory": "projects/spring-launch/markets/market-b/inventory.md",
                "project": "projects/spring-launch-market-b",
            },
        )
        self.assertIsNone(row["delivery"])
        hero = result["rows"][0]
        self.assertIsNone(hero["localize"])
        hook_row = next(r for r in result["rows"] if r["changed_axes"] == ["hook"])
        self.assertIsNone(hook_row["localize"])
        self.assertIsNone(hook_row["delivery"])

    def test_market_and_ratio_row_delivers_to_a_market_ratio_project(self):
        matrix = market_matrix(
            strategy="full_factorial",
            axes={
                "market": ["market-b"],
                "ratio": ["4:5"],
            },
        )
        code, result = self.run_cli("plan", self.write(matrix))
        self.assertEqual(code, 0, result)
        row = next(
            r for r in result["rows"] if r["changed_axes"] == ["market", "ratio"]
        )
        self.assertIsNone(row["studio"])
        self.assertEqual(row["localize"]["project"], "projects/spring-launch-market-b")
        self.assertEqual(
            row["delivery"]["project"], "projects/spring-launch-market-b-4x5"
        )
        self.assertEqual(
            [step["route"] for step in row["steps"]], ["market-adapt", "ratio-reframe"]
        )
        market_row = next(r for r in result["rows"] if r["changed_axes"] == ["market"])
        self.assertEqual(row["base_variant"], market_row["name"])
        self.assertEqual(
            [step["owner"] for step in row["steps"]], [market_row["name"], row["name"]]
        )

    def test_market_with_a_generated_axis_reuses_the_generated_variant_shot(self):
        matrix = market_matrix(
            strategy="full_factorial",
            axes={
                "hook": ["hook-callout"],
                "market": ["market-b"],
            },
        )
        _, result = self.run_cli("plan", self.write(matrix))
        hook_row = next(r for r in result["rows"] if r["changed_axes"] == ["hook"])
        row = next(r for r in result["rows"] if r["changed_axes"] == ["hook", "market"])
        self.assertIsNone(row["studio"])
        self.assertIsNotNone(hook_row["studio"])
        self.assertEqual(row["base_variant"], hook_row["name"])
        self.assertEqual(row["localize"]["market_id"], "market-b")
        self.assertEqual(
            [step["route"] for step in row["steps"]], ["hook-opening", "market-adapt"]
        )
        self.assertEqual(row["steps"][0]["owner"], hook_row["name"])

    def test_factorial_market_rows_with_a_generated_axis_get_variant_projects(self):
        matrix = market_matrix(
            strategy="full_factorial",
            max_variants=50,
            axes={
                "hook": ["hook-a", "hook-b"],
                "market": ["south"],
                "ratio": ["9:16", "4:5"],
            },
        )
        code, result = self.run_cli("plan", self.write(matrix))
        self.assertEqual(code, 0, result)
        self.assertNotIn("matrix.unique_projects", self.rule_ids(result))
        by_values = {
            (
                row["values"]["hook"],
                row["values"]["market"],
                row["values"]["ratio"],
            ): row
            for row in result["rows"]
        }
        hook_a = by_values[("hook-a", "south", "9:16")]
        self.assertEqual(
            hook_a["localize"]["project"], "projects/spring-launch-hook-a-south"
        )
        self.assertIsNone(hook_a["delivery"])
        self.assertEqual(
            hook_a["localize"]["card"],
            "projects/spring-launch/markets/south/market.json",
        )
        self.assertEqual(hook_a["localize"]["variant_key"], "hook-a")
        self.assertEqual(
            hook_a["localize"]["inventory"],
            "projects/spring-launch/markets/south/hook-a/inventory.md",
        )
        self.assertIn(
            "projects/spring-launch-hook-a-south", hook_a["steps"][-1]["note"]
        )
        hook_b = by_values[("hook-b", "south", "4:5")]
        self.assertEqual(
            hook_b["delivery"]["project"], "projects/spring-launch-hook-b-south-4x5"
        )
        market_only = by_values[("hook-demo-first", "south", "9:16")]
        self.assertEqual(
            market_only["localize"]["project"], "projects/spring-launch-south"
        )
        self.assertIsNone(market_only["delivery"])
        market_ratio = by_values[("hook-demo-first", "south", "4:5")]
        self.assertEqual(
            market_ratio["delivery"]["project"], "projects/spring-launch-south-4x5"
        )
        self.assertEqual(
            hook_a["localize"]["project"],
            by_values[("hook-a", "south", "4:5")]["localize"]["project"],
        )
        moved = [
            row
            for row in result["rows"]
            if {"market", "ratio"} & set(row["changed_axes"])
        ]
        delivery = [row["delivery"]["project"] for row in moved if row["delivery"]]
        self.assertEqual(len(delivery), len(set(delivery)))
        localized = {row["localize"]["project"] for row in moved if row["localize"]}
        self.assertEqual(len(localized), 3)
        for path in [*delivery, *localized]:
            self.assertRegex(path, r"^projects/[a-z0-9]+(?:-[a-z0-9]+)*$")

    def test_factorial_ratio_rows_with_a_generated_axis_get_variant_projects(self):
        matrix = base_matrix(
            strategy="full_factorial",
            axes={"hook": ["hook-a", "hook-b"], "ratio": ["4:5"]},
        )
        code, result = self.run_cli("plan", self.write(matrix))
        self.assertEqual(code, 0, result)
        delivery = {
            (row["values"]["hook"], row["values"]["ratio"]): row["delivery"]["project"]
            for row in result["rows"]
            if row["delivery"]
        }
        self.assertEqual(
            delivery[("hook-a", "4:5")], "projects/spring-launch-hook-a-4x5"
        )
        self.assertEqual(
            delivery[("hook-b", "4:5")], "projects/spring-launch-hook-b-4x5"
        )
        self.assertEqual(
            delivery[("hook-demo-first", "4:5")], "projects/spring-launch-4x5"
        )
        self.assertNotIn(("hook-a", "9:16"), delivery)

    def test_factorial_swap_and_ratio_rows_name_every_changed_generated_value(self):
        matrix = base_matrix(
            strategy="full_factorial",
            axes={"hook": ["hook-a"], "talent": ["vp.b"], "ratio": ["1:1"]},
        )
        _, result = self.run_cli("plan", self.write(matrix))
        row = next(
            r
            for r in result["rows"]
            if r["changed_axes"] == ["hook", "talent", "ratio"]
        )
        self.assertEqual(
            row["delivery"]["project"], "projects/spring-launch-hook-a-vp-b-1x1"
        )

    def test_remaining_project_path_collisions_are_refused(self):
        matrix = market_matrix(
            strategy="full_factorial",
            max_variants=50,
            axes={"hook": ["x"], "market": ["y", "x-y"]},
        )
        matrix["hero"]["values"]["hook"] = "h"
        code, result = self.run_cli("plan", self.write(matrix))
        self.assertEqual(code, 1)
        self.assertIn("matrix.unique_projects", self.rule_ids(result))
        finding = next(
            f for f in result["findings"] if f["rule_id"] == "matrix.unique_projects"
        )
        self.assertIn("projects/spring-launch-x-y", finding["message"])

    def test_ratio_value_slug_collisions_are_refused(self):
        matrix = base_matrix(axes={"ratio": ["4:5", "4x5"]})
        code, result = self.run_cli("plan", self.write(matrix))
        self.assertEqual(code, 1)
        self.assertIn("matrix.unique_projects", self.rule_ids(result))

    def test_market_steps_point_at_the_inventory_for_per_element_levels(self):
        _, result = self.run_cli("plan", self.write(market_matrix()))
        row = next(r for r in result["rows"] if r["changed_axes"] == ["market"])
        self.assertIn(
            "projects/spring-launch/markets/market-b/inventory.md",
            row["steps"][0]["note"],
        )
        self.assertNotIn("level chosen there", row["steps"][0]["note"])

    def test_a_row_changing_market_and_language_is_refused(self):
        matrix = market_matrix(
            strategy="full_factorial",
            axes={
                "language": ["es"],
                "market": ["market-b"],
            },
        )
        matrix["hero"]["values"]["language"] = "en"
        code, result = self.run_cli("plan", self.write(matrix))
        self.assertEqual(code, 1)
        self.assertIn("matrix.market_language", self.rule_ids(result))
        finding = next(
            f for f in result["findings"] if f["rule_id"] == "matrix.market_language"
        )
        self.assertIn("ad-localize", finding["message"])

    def test_separate_market_and_language_rows_are_allowed_one_axis_at_a_time(self):
        matrix = market_matrix(axes={"language": ["es"], "market": ["market-b"]})
        matrix["hero"]["values"]["language"] = "en"
        code, result = self.run_cli("plan", self.write(matrix))
        self.assertEqual(code, 0, result)
        self.assertNotIn("matrix.market_language", self.rule_ids(result))

    def test_market_rows_allow_unknown_unit_cost(self):
        path = self.write(market_matrix())
        code, result = self.run_cli(
            "cost", path, "--unit-cost", "hook=3", "--unit-cost", "ratio=0"
        )
        self.assertEqual(code, 0, result)
        self.assertIsNone(result["total_estimated_usd"])
        finding = next(
            f for f in result["findings"] if f["rule_id"] == "cost.unit_missing"
        )
        self.assertIn("market", finding["message"])
        code, result = self.run_cli("cost", path, *MARKET_COSTS)
        self.assertEqual(code, 0, result)
        self.assertEqual(result["total_estimated_usd"], 3 + 5 * 2 + 0)
        self.assertIn("ad-localize", result["market_estimate_note"])
        self.assertIn("level", result["market_estimate_note"])

    def test_market_unit_cost_may_come_from_the_matrix(self):
        matrix = market_matrix(unit_cost_usd={"hook": 3, "market": 7, "ratio": 0})
        code, result = self.run_cli("cost", self.write(matrix))
        self.assertEqual(code, 0, result)
        self.assertEqual(result["unit_cost_usd"]["market"], 7)

    def test_cost_without_market_rows_has_no_market_note(self):
        _, result = self.run_cli("cost", self.write(base_matrix()), *UNIT_COSTS)
        self.assertNotIn("market_estimate_note", result)

    def test_register_prints_no_commands_for_market_rows_but_lists_localize(self):
        code, result = self.register(market_matrix(), *MARKET_COSTS, *VIDEO_FLAGS)
        self.assertEqual(code, 0, result)
        market_rows = [r for r in result["rows"] if r["changed_axes"] == ["market"]]
        for row in market_rows:
            self.assertEqual(result["operations"][row["name"]], [])
        localize = {entry["variant"]: entry for entry in result["localize"]}
        self.assertEqual(set(localize), {row["name"] for row in market_rows})
        entry = localize[market_rows[0]["name"]]
        self.assertEqual(entry["skill"], "ad-localize")
        self.assertEqual(
            entry["card"], "projects/spring-launch/markets/market-b/market.json"
        )
        self.assertIn("registers its own", entry["reminder"])

    def test_register_for_a_market_only_matrix_needs_no_model_flags(self):
        matrix = market_matrix(axes={"market": ["market-b"]})
        code, result = self.register(matrix, "--unit-cost", "market=5")
        self.assertEqual(code, 0, result)
        self.assertEqual(sum(map(len, result["operations"].values())), 0)
        self.assertEqual(len(result["localize"]), 1)

    def test_register_without_market_rows_has_no_localize_list(self):
        _, result = self.register(base_matrix(), *UNIT_COSTS, *VIDEO_FLAGS)
        self.assertNotIn("localize", result)

    def reuse_matrix(self):
        matrix = market_matrix(
            strategy="full_factorial",
            axes={"talent": ["vp-b"], "market": ["market-b"], "ratio": ["4:5"]},
        )
        matrix["hero"]["values"] = {
            "talent": "vp-a",
            "market": "market-a",
            "ratio": "9:16",
        }
        return matrix

    def test_factorial_registers_one_talent_swap_for_its_market_and_ratio_rows(self):
        code, result = self.register(
            self.reuse_matrix(),
            "--unit-cost",
            "talent=6",
            "--unit-cost",
            "market=5",
            *VIDEO_FLAGS,
        )
        self.assertEqual(code, 0, result)
        rows = {tuple(row["changed_axes"]): row for row in result["rows"]}
        talent = rows[("talent",)]
        shots = [row["studio"]["shot_id"] for row in result["rows"] if row["studio"]]
        self.assertEqual(shots, [talent["studio"]["shot_id"]])
        swaps = [op for ops in result["operations"].values() for op in ops]
        self.assertEqual([op["asset"] for op in swaps], [f"{talent['name']}_t01_draft"])
        for change in (("talent", "ratio"), ("talent", "market")):
            self.assertEqual(rows[change]["base_variant"], talent["name"])
            self.assertEqual(result["operations"][rows[change]["name"]], [])
        self.assertEqual(
            rows[("talent", "market", "ratio")]["base_variant"],
            rows[("talent", "market")]["name"],
        )
        self.assertEqual(result["total_estimated_usd"], 6 + 5 * 2)
        self.assertEqual(rows[("talent", "ratio")]["estimated_cost_usd"], 0)
        self.assertEqual(rows[("talent", "market")]["estimated_cost_usd"], 5)
        self.assertEqual(
            {entry["variant"] for entry in result["localize"]},
            {rows[("market",)]["name"], rows[("talent", "market")]["name"]},
        )

    def test_unique_operation_breakdown_counts_each_paid_step_once(self):
        code, result = self.run_cli(
            "cost",
            self.write(self.reuse_matrix()),
            "--unit-cost",
            "talent=6",
            "--unit-cost",
            "market=5",
        )
        self.assertEqual(code, 0, result)
        operations = result["operations_estimate"]
        self.assertEqual(len(operations), result["variant_count"])
        self.assertEqual(
            len({op["operation_key"] for op in operations}), len(operations)
        )
        self.assertEqual(
            round(sum(op["unit_cost_usd"] for op in operations), 2),
            result["total_estimated_usd"],
        )
        self.assertEqual(
            round(sum(row["estimated_cost_usd"] for row in result["rows"]), 2),
            result["total_estimated_usd"],
        )
        [swap] = [op for op in operations if op["route"] == "object-swap"]
        self.assertEqual(len(swap["used_by"]), 4)
        markets = [op for op in operations if op["route"] == "market-adapt"]
        self.assertEqual(len(markets), 2)

    def test_legacy_budget_does_not_change_the_deduplicated_total(self):
        matrix = self.reuse_matrix()
        matrix["budget_usd"] = 16
        code, result = self.run_cli(
            "cost",
            self.write(matrix),
            "--unit-cost",
            "talent=6",
            "--unit-cost",
            "market=5",
        )
        self.assertEqual(code, 0, result)
        matrix["budget_usd"] = 15.99
        code, result = self.run_cli(
            "cost",
            self.write(matrix),
            "--unit-cost",
            "talent=6",
            "--unit-cost",
            "market=5",
        )
        self.assertEqual(code, 0, result)
        self.assertEqual(result["total_estimated_usd"], 16)

    def test_every_variant_row_adds_exactly_one_new_operation(self):
        matrix = swap_matrix()
        matrix["axes"]["hook"] = ["hook-a"]
        matrix["hero"]["values"]["hook"] = "hook-demo-first"
        matrix["max_variants"] = 100
        code, result = self.run_cli("plan", self.write(matrix))
        self.assertEqual(code, 0, result)
        for row in result["rows"][1:]:
            owned = [s for s in row["steps"] if s["owner"] == row["name"]]
            self.assertEqual(owned, row["steps"][-1:], row["name"])

    def test_ratio_rows_cost_zero_by_default_with_a_note(self):
        costs = ["--unit-cost", "hook=3", "--unit-cost", "talent=6"]
        code, result = self.run_cli("cost", self.write(base_matrix()), *costs)
        self.assertEqual(code, 0, result)
        self.assertEqual(result["unit_cost_usd"]["ratio"], 0)
        self.assertEqual(result["total_estimated_usd"], 3 * 2 + 6)
        self.assertIn("not a provider operation", result["ratio_cost_note"])
        code, result = self.run_cli(
            "cost", self.write(base_matrix()), *costs, "--unit-cost", "ratio=2"
        )
        self.assertEqual(result["total_estimated_usd"], 3 * 2 + 6 + 2 * 2)
        matrix = base_matrix(axes={"hook": ["hook-callout"]})
        _, result = self.run_cli("cost", self.write(matrix), *costs)
        self.assertNotIn("ratio_cost_note", result)

    def test_full_factorial_requires_notes_recording_the_request(self):
        for notes in (None, "", "   "):
            matrix = base_matrix(strategy="full_factorial", max_variants=20)
            if notes is None:
                matrix.pop("notes")
            else:
                matrix["notes"] = notes
            code, result = self.run_cli("plan", self.write(matrix))
            self.assertEqual(code, 1, notes)
            self.assertIn("matrix.factorial_request", self.rule_ids(result))
        code, result = self.run_cli(
            "plan", self.write(base_matrix(strategy="full_factorial", max_variants=20))
        )
        self.assertEqual(code, 0, result)
        code, result = self.run_cli("plan", self.write(base_matrix()))
        self.assertNotIn("matrix.factorial_request", self.rule_ids(result))

    def test_register_requires_the_hero_decision_record_in_the_project(self):
        matrix = base_matrix()
        del matrix["hero"]["decision_ref"]
        code, result = self.register(matrix, *UNIT_COSTS, *VIDEO_FLAGS)
        self.assertEqual(code, 1)
        self.assertIn("matrix.hero_decision", self.rule_ids(result))
        self.assertNotIn("operations", result)
        code, result = self.run_cli("plan", self.write(matrix))
        self.assertEqual(code, 0, result)
        outside = self.root / "outside.json"
        outside.write_text("{}")
        (self.project / "decisions" / "link.json").symlink_to(outside)
        (self.project / "decisions" / "folder").mkdir()
        for ref in (
            "decisions/missing.json",
            "../outside.json",
            str(outside),
            "decisions/link.json",
            "decisions/folder",
        ):
            matrix["hero"]["decision_ref"] = ref
            code, result = self.register(matrix, *UNIT_COSTS, *VIDEO_FLAGS)
            self.assertEqual(code, 1, ref)
            self.assertIn("matrix.hero_decision", self.rule_ids(result), ref)

    def test_register_hashes_the_hero_take_against_the_bound_sha256(self):
        matrix = base_matrix()
        del matrix["hero"]["take_file"]
        code, result = self.register(matrix, *UNIT_COSTS, *VIDEO_FLAGS)
        self.assertEqual(code, 1)
        self.assertIn("matrix.hero_take", self.rule_ids(result))
        matrix["hero"]["take_file"] = "../escape.mp4"
        (self.root / "escape.mp4").write_bytes(HERO_BYTES)
        code, result = self.register(matrix, *UNIT_COSTS, *VIDEO_FLAGS)
        self.assertIn("matrix.hero_take", self.rule_ids(result))
        matrix["hero"]["take_file"] = HERO_TAKE_FILE
        (self.project / HERO_TAKE_FILE).write_bytes(b"re-exported hero take")
        code, result = self.register(matrix, *UNIT_COSTS, *VIDEO_FLAGS)
        self.assertEqual(code, 1)
        self.assertIn("matrix.hero_hash_mismatch", self.rule_ids(result))
        self.assertNotIn("operations", result)
        (self.project / HERO_TAKE_FILE).write_bytes(HERO_BYTES)
        code, result = self.register(matrix, *UNIT_COSTS, *VIDEO_FLAGS)
        self.assertEqual(code, 0, result)

    def test_skill_cites_the_variant_rules(self):
        text = (ROOT / ".agents/skills/ad-variant-matrix/SKILL.md").read_text()
        for rule in ("ad.variant_one_axis", "ad.variant_count_gate"):
            self.assertIn(rule, text)


if __name__ == "__main__":
    unittest.main()
