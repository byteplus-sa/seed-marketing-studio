import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / ".agents/skills"


class MarketingEvidenceTests(unittest.TestCase):
    def test_focus_observation_does_not_override_prompt_only_intent(self):
        text = (ROOT / "seedance-lens-presets/SKILL.md").read_text()
        self.assertIn("six", text)
        self.assertIn("prompt-only", text)
        self.assertIn("unknown", text)
        self.assertNotIn("**Post only**", text)
        self.assertNotIn("no prompted focus pull away", text)

    def test_light_observation_is_not_family_timing_guarantee(self):
        text = (ROOT / "seedance-lighting-presets/SKILL.md").read_text()
        self.assertIn("0.1 s", text)
        self.assertIn("historical observation", text)
        self.assertIn("unknown", text)


if __name__ == "__main__":
    unittest.main()
