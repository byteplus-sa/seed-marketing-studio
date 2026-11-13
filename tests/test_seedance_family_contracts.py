import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / ".agents/skills"


class MarketingContractTests(unittest.TestCase):
    def test_slot_mapping_preserves_selected_native_master_silence_and_mixed_owners(self):
        text = (ROOT / "template-factory/references/slot-mapping.md").read_text()
        for phrase in ("wordless", "purposeful silence", "exact master", "opt-in", "Mixed"):
            self.assertIn(phrase, text)
        self.assertNotIn("Native only for on-camera dialogue", text)

    def test_strict_restyle_retains_denied_probes_fractional_spans_and_words_only(self):
        text = (ROOT / "prompt-review/references/checklist-seedance-edits.md").read_text().split("## Seedance 2.5 restyle")[1]
        for phrase in ("denied probe", "fractional", "words-only", "unresolved", "audio tail"):
            self.assertIn(phrase, text)
        self.assertNotIn("whole-second source duration", text)
        self.assertNotIn("the request is a 480p probe", text)

    def test_motion_owner_rejects_planning_boards_but_accepts_independent_clean_keyframes(self):
        text = (ROOT / "seedance-motion-design/SKILL.md").read_text()
        for phrase in ("planning-only", "independent selection", "current hashes", "source lineage", "leakage QA"):
            self.assertIn(phrase, text)
        self.assertNotIn("<approved storyboard / keyframe>", text)
        self.assertNotIn("Approved storyboard panels / keyframes", text)

    def test_preview_policy_owners_name_exact_legacy_and_profile_mechanics(self):
        repo = ROOT.parents[1]
        paths = [
            repo / "AGENTS.md", repo / ".agents/contracts/routing.md",
            repo / ".agents/contracts/production-policy.md",
            ROOT / "film-production/SKILL.md",
            ROOT / "film-production/references/production-defaults.md",
            ROOT / "seedance-prompt-25/references/parameter-reference.md",
        ]
        for path in paths:
            with self.subTest(path=path):
                text = path.read_text()
                self.assertIn("exact legacy", text.lower())
                self.assertIn("verified operation profile", text.lower())

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
