import json
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / ".agents/scripts"))
import template_gallery
import validate_workspace

SKILLS = ROOT / ".agents/skills"
AD_SKILLS = {
    "seedance-ugc-ads",
    "seedance-product-demo-ads",
    "seedance-story-ads",
    "ad-motion-graphics",
    "seedance-testimonial-ads",
    "seedance-musical-ads",
    "seedance-match-cut-ads",
    "seedance-fashion-ads",
    "seedance-pov-ads",
    "seedance-deadpan-ads",
    "seedance-handcrafted-ads",
    "seedance-practical-illusion-ads",
}
PRESET_IDS = {
    "angry-mode",
    "crying",
    "happy",
    "happy-mode",
    "shocked",
    "saint-glow",
    "sunglasses",
    "selfie",
    "selfie-outfit",
    "selfie-posing",
    "static-posing",
    "fix-and-pose",
    "group-photo",
    "outfit-check",
    "outfit-switch",
    "clothes-rain",
    "hair-style",
    "sand-cut",
    "eating",
    "eating-zoom",
    "plate-check",
    "atomic",
    "explosion",
    "firework",
    "northern-lights",
    "aquarium",
    "color-rain",
    "money-rain",
    "pizza-fall",
    "cotton-cloud",
    "gas-transformation",
    "beast-appearance",
    "giant-grab",
    "handheld-run",
    "pool-jump",
    "ballet",
    "motor-ride",
    "beach-ride",
    "train-rush",
    "peak-moment",
    "morning-routine",
    "timelapse-glam",
    "timelapse-human",
    "yacht",
    "bts",
}


class AdSkillLibraryTests(unittest.TestCase):
    def test_requested_skills_are_loadable_and_registered_once(self):
        catalog = json.loads((ROOT / ".agents/catalog/skills.json").read_text())[
            "skills"
        ]
        readme = (ROOT / "README.md").read_text()
        for name in sorted(AD_SKILLS):
            with self.subTest(skill=name):
                path = SKILLS / name / "SKILL.md"
                self.assertTrue(path.is_file())
                metadata, findings = validate_workspace.validate_skill(path)
                self.assertEqual(findings, [])
                self.assertEqual(metadata["description"], catalog[name]["description"])
                self.assertEqual(readme.count(f"| **{name}** |"), 1)
                link = ROOT / ".claude/skills" / name
                self.assertTrue(link.is_symlink())
                self.assertEqual(link.resolve(), path.parent)

    def test_new_entrypoints_use_plain_single_line_metadata(self):
        for name in sorted(AD_SKILLS):
            with self.subTest(skill=name):
                text = (SKILLS / name / "SKILL.md").read_text()
                description = text.splitlines()[2]
                self.assertTrue(description.startswith("description: "))
                value = description.removeprefix("description: ")
                self.assertFalse(value.startswith(("'", '"', ">", "|")))
                self.assertNotRegex(value, r": |[<>]")
                self.assertLess(len(text.splitlines()), 500)
                self.assertTrue(text.split("---", 2)[2].strip())

    def test_motion_graphics_is_the_only_new_orchestrator(self):
        catalog = json.loads((ROOT / ".agents/catalog/skills.json").read_text())[
            "skills"
        ]
        for name in sorted(AD_SKILLS):
            with self.subTest(skill=name):
                expected = "orchestrator" if name == "ad-motion-graphics" else "leaf"
                self.assertEqual(catalog[name]["kind"], expected)

    def test_full_consolidation_removes_legacy_entrypoints(self):
        for name in ("ugc-ad-modes", "ugc-motion-presets"):
            self.assertFalse((SKILLS / name).exists())
            self.assertFalse((ROOT / ".claude/skills" / name).is_symlink())

    def test_all_45_motion_presets_survive_under_the_canonical_skill(self):
        entries = [
            entry
            for entry in template_gallery.scan(SKILLS)
            if entry.skill == "seedance-ugc-ads"
            and Path(entry.source).name.startswith("motion-presets")
        ]
        self.assertEqual({entry.entry_id for entry in entries}, PRESET_IDS)
        self.assertEqual(len(entries), 45)
        self.assertEqual(template_gallery.duplicates(entries), [])

    def test_no_active_runtime_document_routes_to_legacy_names(self):
        paths = [
            ROOT / "README.md",
            ROOT / ".agents/catalog/skills.json",
            ROOT / "skills-lock.json",
            *(ROOT / ".agents/scripts").glob("*.py"),
            *SKILLS.rglob("*.md"),
            *SKILLS.rglob("*.json"),
            *SKILLS.rglob("*.yaml"),
        ]
        legacy = re.compile(r"\bugc-(?:ad-modes|motion-presets)\b")
        offenders = [
            str(path.relative_to(ROOT))
            for path in paths
            if legacy.search(path.read_text())
        ]
        self.assertEqual(offenders, [])

    def test_new_capabilities_ship_evaluation_cases(self):
        for name in sorted(AD_SKILLS):
            with self.subTest(skill=name):
                skill = SKILLS / name
                machine_cases = skill / "evals/evals.json"
                prose_cases = skill / "references/evaluation-cases.md"
                if machine_cases.is_file():
                    self.assertGreaterEqual(
                        len(validate_workspace.load_evaluations(machine_cases)), 5
                    )
                else:
                    self.assertTrue(prose_cases.is_file())
                    self.assertIn(
                        "(references/evaluation-cases.md)",
                        (skill / "SKILL.md").read_text(),
                    )


if __name__ == "__main__":
    unittest.main()
