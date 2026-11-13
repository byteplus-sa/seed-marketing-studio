import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / ".agents/skills"


class MarketingContractTests(unittest.TestCase):
    def test_vfx_preserves_fractional_timing_and_denied_probe_scope(self):
        text = (ROOT / "seedance-vfx-pipeline/references/recast-and-variants.md").read_text()
        self.assertIn("fractional duration", text)
        self.assertIn("Optional probe", text)
        self.assertNotIn("Set to the whole-second source length", text)
        self.assertNotIn("Batch total = variants × (probe + final)", text)

    def test_factory_preserves_sound_ownership_without_genre_switch(self):
        text = (ROOT / "template-factory/SKILL.md").read_text()
        self.assertIn("Sound ownership", text)
        self.assertIn("purposeful silence", text)
        self.assertNotIn("native audio often leaks speech or score", text)
        self.assertNotIn("0.5–1.2 s", text)

    def test_optional_conditioning_never_promotes_board_or_flag_alone(self):
        text = (ROOT / "template-factory/SKILL.md").read_text()
        self.assertIn("Optional conditioning", text)
        self.assertIn("control_only", text)
        self.assertIn("current hashes", text)
        self.assertIn("planning-only", text)


if __name__ == "__main__":
    unittest.main()
