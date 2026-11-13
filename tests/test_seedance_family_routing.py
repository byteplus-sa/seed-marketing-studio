import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / ".agents/skills"


class MarketingRoutingTests(unittest.TestCase):
    def test_shared_craft_names_neutral_leaf_and_retains_source_basis(self):
        for name in ("seedance-camera-presets", "seedance-acting-console",
                     "seedance-animation-styles", "seedance-pacing-presets",
                     "seedance-shot-design", "seedance-music-video"):
            with self.subTest(skill=name):
                text = (ROOT / name / "SKILL.md").read_text()
                self.assertIn("`seedance-prompt`", text)
                self.assertIn("selected model", text)

    def test_review_selects_model_before_genre_or_ugc(self):
        text = (ROOT / "prompt-review/SKILL.md").read_text()
        self.assertIn("checklist-seedance-family.md", text)
        self.assertNotIn("against the Seedance 2.5 + Universal checklists", text)
        checklist = (ROOT / "prompt-review/references/checklist-seedance-family.md").read_text()
        self.assertIn("acting.plan_bound", checklist)
        self.assertIn("unknown", checklist)


if __name__ == "__main__":
    unittest.main()
