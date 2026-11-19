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
    "seedance-drama-ads",
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
        for name in ("ugc-ad-modes", "ugc-motion-presets", "seedance-story-ads"):
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
            ROOT / ".agents/catalog/integrity.json",
            ROOT / "skills-lock.json",
            *(ROOT / ".agents/contracts").glob("*.md"),
            *(ROOT / "tests/fixtures").glob("*.json"),
            *(ROOT / ".agents/scripts").glob("*.py"),
            *SKILLS.rglob("*.md"),
            *SKILLS.rglob("*.json"),
            *SKILLS.rglob("*.yaml"),
        ]
        legacy = re.compile(r"\b(?:ugc-(?:ad-modes|motion-presets)|seedance-story-ads)\b")
        offenders = [
            str(path.relative_to(ROOT))
            for path in paths
            if legacy.search(path.read_text())
        ]
        self.assertEqual(offenders, [])

    def test_drama_skill_lock_points_to_the_canonical_entrypoint(self):
        lock = json.loads((ROOT / "skills-lock.json").read_text())["skills"]
        self.assertNotIn("seedance-story-ads", lock)
        entry = lock["seedance-drama-ads"]
        self.assertEqual(
            entry["skillPath"], ".agents/skills/seedance-drama-ads/SKILL.md"
        )
        self.assertTrue((ROOT / entry["skillPath"]).is_file())

    def test_drama_skill_leaves_creative_form_open(self):
        text = (SKILLS / "seedance-drama-ads/SKILL.md").read_text()
        normalized = " ".join(text.split())
        for retired in (
            "## Short-drama creative default",
            "### Reject a mood film before coverage",
            "Use spoken interaction as the starting audio proposal",
            "Reject music-and-slow-movement padding",
        ):
            with self.subTest(retired=retired):
                self.assertNotIn(retired, normalized)
        self.assertIn("Create beautiful, original stories around any product", normalized)
        self.assertIn(
            "Do not prescribe conflict, dialogue, physical action, twists or a "
            "product-solving payoff as defaults", normalized
        )
        self.assertIn(
            "A product may have a functional, emotional, symbolic or incidental role",
            normalized,
        )

    def test_drama_caller_boundary_binds_preview_policy_to_exact_destination(self):
        text = (SKILLS / "seedance-drama-ads/SKILL.md").read_text()
        boundary = " ".join(text.split("## Caller boundary", 1)[1].lower().split())
        self.assertNotIn("every new seedance 2.5 generation requires", boundary)
        for phrase in (
            "selected exact model",
            "provider",
            "operation",
            "transport",
            "schema revision",
            "exact legacy native bindings",
            "seedance-execution-profiles.md",
            'resolution: "480p"',
            "draft: true",
            "both review modes",
            "unknown",
            "unresolved",
            "prompt-only",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, boundary)

    def test_drama_caller_boundary_keeps_preview_kinds_and_final_lineage_distinct(self):
        text = (SKILLS / "seedance-drama-ads/SKILL.md").read_text()
        boundary = " ".join(text.split("## Caller boundary", 1)[1].lower().split())
        for phrase in (
            "verified operation profile",
            "non-promotable ordinary preview",
            "optional evidenced absent preview",
            "required ordinary preview",
            "hash-bound selection",
            "separately registered final",
            "native promotion",
            "verified support",
            "never invent",
            "never silently switch",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, boundary)

    def test_drama_reference_removes_the_puzzle_handoff_template(self):
        text = (
            SKILLS / "seedance-drama-ads/references/evaluation-cases.md"
        ).read_text()
        for retired in (
            "Hypothetical worked example",
            "quiet puzzle",
            "finishing the shared puzzle",
            "You should place it.",
            "Complete source prompt:",
        ):
            with self.subTest(retired=retired):
                self.assertNotIn(retired, text)
        for case in (
            "Open creative brief",
            "Requested dialogue",
            "Requested physical action",
            "Story fit without a formula",
            "Creative reset versus narrow repair",
        ):
            with self.subTest(case=case):
                self.assertIn(case, text)

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

    def test_format_handoffs_preserve_native_drafts_in_both_review_modes(self):
        for name in sorted(AD_SKILLS):
            with self.subTest(skill=name):
                text = (SKILLS / name / "SKILL.md").read_text()
                self.assertIn('resolution: "480p"', text)
                self.assertIn("draft: true", text)
                self.assertIn("both review modes", text)

    def test_format_references_do_not_allow_review_mode_draft_bypasses(self):
        bypasses = (
            r"draft-first unless",
            r"draft default unless",
            r"no mandatory draft",
            r"explicit draft override",
            r"default.{0,100}no automatic draft",
        )
        for name in sorted(AD_SKILLS):
            for path in (SKILLS / name).rglob("*.md"):
                with self.subTest(path=path.relative_to(ROOT)):
                    text = " ".join(path.read_text().split())
                    for pattern in bypasses:
                        self.assertNotRegex(text, pattern)


if __name__ == "__main__":
    unittest.main()
