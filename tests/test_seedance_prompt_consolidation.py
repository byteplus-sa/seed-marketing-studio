import json
import re
import unittest
from pathlib import Path

from ruamel.yaml import YAML

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / ".agents/skills"
PROMPT = SKILLS / "seedance-prompt"
RETIRED = ("seedance-prompt-20", "seedance-prompt-25")
RETIRED_TOKEN = re.compile(r"seedance-prompt-(?:20|25)(?![a-z0-9-])")


class SeedancePromptConsolidationTests(unittest.TestCase):
    def test_only_generic_entrypoint_and_resolving_alias_remain(self):
        self.assertTrue((PROMPT / "SKILL.md").is_file())
        alias = ROOT / ".claude/skills/seedance-prompt"
        self.assertTrue(alias.is_symlink())
        self.assertEqual(alias.resolve(), PROMPT.resolve())
        for name in RETIRED:
            with self.subTest(skill=name):
                self.assertFalse((SKILLS / name).exists())
                retired_alias = ROOT / ".claude/skills" / name
                self.assertFalse(retired_alias.exists())
                self.assertFalse(retired_alias.is_symlink())
        self.assertTrue((SKILLS / "seedance-prompt-25-dialogue/SKILL.md").is_file())

    def test_active_callers_and_metadata_cannot_reintroduce_retired_skills(self):
        paths = [ROOT / "AGENTS.md", ROOT / "README.md", ROOT / "skills-lock.json"]
        paths.extend(path for path in (ROOT / ".agents").rglob("*")
                     if path.is_file() and path.suffix in {".md", ".json", ".yaml"})
        offenders = [str(path.relative_to(ROOT)) for path in paths
                     if RETIRED_TOKEN.search(path.read_text())]
        self.assertEqual(offenders, [])
        for relative in ("skills-lock.json", ".agents/catalog/skills.json"):
            skills = json.loads((ROOT / relative).read_text())["skills"]
            self.assertIn("seedance-prompt", skills)
            self.assertTrue(set(RETIRED).isdisjoint(skills))
        readme = (ROOT / "README.md").read_text()
        self.assertEqual(readme.count("| **seedance-prompt** |"), 1)
        count = len(list(SKILLS.glob("*/SKILL.md")))
        self.assertIn(f"**{count} skills**", readme)

    def test_all_mode_references_ship_in_the_generic_bundle(self):
        expected = {
            "audio-performance-camera", "keyframes-storyboards-blockouts",
            "parameter-reference", "reference-inputs", "repair-examples",
            "scene-action", "shot-staging", "transitions-and-one-click",
            "video-editing", "video-extension", "worked-examples",
            "model-boundaries",
        }
        self.assertEqual({path.stem for path in (PROMPT / "references").glob("*.md")},
                         expected)

    def test_generic_evals_retain_all_adapter_cases_without_id_collisions(self):
        documents = [json.loads(path.read_text())
                     for path in (PROMPT / "evals").glob("*.json")]
        cases = [case for document in documents for case in document["evals"]]
        self.assertTrue(all(document["skill_name"] == "seedance-prompt"
                            for document in documents))
        self.assertGreaterEqual(len(cases), 43)
        self.assertEqual(len(cases), len({case["id"] for case in cases}))
        historical_ids = {*range(1, 13), *range(1001, 1008),
                          *range(2501, 2515), *range(201, 211)}
        self.assertTrue(historical_ids.issubset({case["id"] for case in cases}))
        prompts = " ".join(case["prompt"] for case in cases).lower()
        for phrase in ("forest-boundary", "coarse 3d blockout", "extend it backward",
                       "7.37", "hidden behind", "not that one"):
            self.assertIn(phrase, prompts)
        for case in cases:
            with self.subTest(case=case["id"]):
                self.assertTrue(case["expected_output"].strip())
                self.assertGreaterEqual(len(case.get("expectations", case.get("assertions", []))), 3)

    def test_references_do_not_restore_automatic_model_or_language_routing(self):
        parameters = (PROMPT / "references/parameter-reference.md").read_text()
        self.assertNotIn("### Cost ladder", parameters)
        self.assertNotIn("Fall back to", parameters)
        for model in ("dreamina-seedance-2-0-260128",
                      "dreamina-seedance-2-0-fast-260128",
                      "dreamina-seedance-2-0-mini-260615",
                      "dreamina-seedance-2-5-260628"):
            self.assertIn(model, parameters)
        audio = (PROMPT / "references/audio-performance-camera.md").read_text()
        self.assertNotIn("Seedance 2.5 natively supports these languages", audio)
        self.assertIn("exact model", audio)
        self.assertIn("acting.plan_bound", audio)

    def test_edit_and_extension_modes_preserve_source_and_denied_probe_scope(self):
        for name in ("video-editing", "video-extension"):
            with self.subTest(mode=name):
                text = (PROMPT / f"references/{name}.md").read_text().lower()
                for phrase in ("fractional", "audio tail", "retim", "unresolved",
                               "probe", "exact model"):
                    self.assertIn(phrase, text)
        editing = (PROMPT / "references/video-editing.md").read_text()
        for phrase in ("sole editing master", "Timeline Inheritance",
                       "Background replacement", "Audio editing"):
            self.assertIn(phrase, editing)
        extension = (PROMPT / "references/video-extension.md").read_text()
        self.assertIn("### Forward extension", extension)
        self.assertIn("### Backward extension", extension)

    def test_disclosure_baseline_survives_current_path_migration(self):
        data = json.loads((ROOT / "tests/fixtures/prompt_disclosure_inventory.json").read_text())
        entry = next(skill for skill in data["skills"] if skill["skill"] == "seedance-prompt")
        self.assertEqual(entry["before_lines"], 1336)
        self.assertEqual(entry["before_bytes"], 62913)
        self.assertEqual(entry["entry_bytes"], (PROMPT / "SKILL.md").stat().st_size)
        loading = entry["representative_path"]
        self.assertEqual(loading["loaded_bytes"],
                         sum((ROOT / path).stat().st_size for path in loading["files"]))

    def test_legacy_review_does_not_reimpose_retired_grammar_or_split_scope(self):
        text = (SKILLS / "prompt-review/references/checklist-seedance-legacy.md").read_text()
        general = text.split("## Seedance VFX (video-to-video)", 1)[0]
        for requirement in (
            "Every shot repeats applicable",
            "Uses `Shot 1 / Shot 2 / Shot 3` format",
            "**Per-shot description order.**",
            "Requested beats fit the duration or the scene is split.",
            "Same 6-field format",
        ):
            with self.subTest(requirement=requirement):
                self.assertNotIn(requirement, general)
        for safeguard in (
            "stable", "source", "authorization", "unresolved",
            "references.no_board_binding", "dialogue.speech_budget",
            "Boundary behavior", "Known rejections",
        ):
            with self.subTest(safeguard=safeguard):
                self.assertIn(safeguard.lower(), general.lower())

    def test_eval_summaries_match_capability_and_scoped_look_expectations(self):
        cases = {case["id"]: case for case in json.loads(
            (PROMPT / "evals/evals.json").read_text()
        )["evals"]}
        for identifier in (1005, 2505, 2509):
            with self.subTest(case=identifier):
                self.assertRegex(cases[identifier]["expected_output"].lower(),
                                 r"verif|evidence|support")
        self.assertNotIn("one grade for the whole clip", cases[2508]["expected_output"])
        self.assertNotIn("one grade once", " ".join(cases[2508]["expectations"]))
        self.assertIn("locked", " ".join(cases[2508]["expectations"]).lower())
        self.assertNotIn("budget authorization", " ".join(cases[2511]["expectations"]))

    def test_migrated_guidance_preserves_selection_and_exact_operation_boundaries(self):
        review = (SKILLS / "prompt-review/references/checklist-seedance-25.md").read_text()
        for directive in (
            "plan the defocus in post (MINOR)",
            "A last-frame-only request is rejected; use first + last.",
            "the prompt aligns with the reference or the reference is replaced.",
        ):
            with self.subTest(directive=directive):
                self.assertNotIn(directive, review)
        examples = (PROMPT / "references/worked-examples.md").read_text().lower()
        self.assertIn("exact legacy", examples)
        self.assertIn("verified", examples)
        keyframes = (PROMPT / "references/keyframes-storyboards-blockouts.md").read_text().lower()
        self.assertIn("redraw", keyframes)
        self.assertIn("planning origin", keyframes)
        audio = (PROMPT / "references/audio-performance-camera.md").read_text()
        self.assertNotIn("also compose with it", audio)
        self.assertIn("opt-in", audio)

    def test_public_summaries_describe_the_complete_unified_capability(self):
        catalog = json.loads((ROOT / ".agents/catalog/skills.json").read_text())
        summary = catalog["skills"]["seedance-prompt"]["readme_summary"]
        interface = YAML(typ="safe").load(
            (PROMPT / "agents/openai.yaml").read_text()
        )["interface"]
        for text in (summary, interface["short_description"], interface["default_prompt"]):
            with self.subTest(text=text):
                for phrase in ("2.5-based", "reference", "edit", "extension"):
                    self.assertIn(phrase, text.lower())
        self.assertIn(f"| **seedance-prompt** | {summary} |", (ROOT / "README.md").read_text())
        for path in (PROMPT / "evals").glob("*.json"):
            for case in json.loads(path.read_text())["evals"]:
                text = " ".join([
                    case["expected_output"],
                    *case.get("expectations", case.get("assertions", [])),
                ]).lower()
                with self.subTest(case=case["id"]):
                    self.assertNotIn("handoff to the source-video edit capability", text)
                    self.assertNotIn("source-video edits are out of scope", text)


if __name__ == "__main__":
    unittest.main()
