import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / ".agents/skills"


class StreamProfileContractTests(unittest.TestCase):
    def test_known_decode_recipe_is_conditional_on_actual_metadata(self):
        text = (ROOT / "color-grade-palettes/SKILL.md").read_text()
        for field in ("color_range", "color_primaries", "color_transfer", "color_space", "pix_fmt"):
            self.assertIn(field, text)
        self.assertIn("unknown", text)
        self.assertIn("conflicting", text)
        self.assertNotIn("Seedance 2.5 finals are 10-bit HEVC", text)

    def test_factory_does_not_choose_decode_from_family_name(self):
        text = (ROOT / "template-factory/references/long-pins-and-multi-clip.md").read_text()
        self.assertIn("actual stream metadata", text)
        self.assertIn("unknown", text)


if __name__ == "__main__":
    unittest.main()
