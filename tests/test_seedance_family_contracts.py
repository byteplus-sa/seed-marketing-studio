import json
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
            ROOT / "seedance-prompt/references/parameter-reference.md",
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

    def test_factory_rejects_board_origin_after_redraw_regeneration_or_approval(self):
        text = " ".join((ROOT / "template-factory/SKILL.md").read_text().lower().split())
        optional = text.split("**optional conditioning:**", 1)[1].split("7. **video**", 1)[0]
        for phrase in (
            "board-origin derivatives",
            "crops, redraws and regeneration from panel prompts",
            "remain planning-only",
            "approval or a new render does not change their origin",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, optional)
        self.assertNotIn("a clean final-medium derivative can be selected", optional)

    def test_factory_independent_conditioning_retains_evidence_and_prompt_only_scope(self):
        text = " ".join((ROOT / "template-factory/SKILL.md").read_text().lower().split())
        optional = text.split("**optional conditioning:**", 1)[1].split("7. **video**", 1)[0]
        representation = text.split("## intentional conditioning representation", 1)[1]
        for section in (optional, representation):
            for phrase in ("independently authored non-board production stills", "independent animated blockouts"):
                with self.subTest(section=section, phrase=phrase):
                    self.assertIn(phrase, section)
        for phrase in ("mode-authorized approval", "current hashes", "source lineage", "rights", "consent", "exact-role support", "artifact-specific qa"):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, optional)
        self.assertIn("prompt-only work creates no assets", optional)
        self.assertIn("board-origin derivatives remain ineligible", representation)
        self.assertIn("flipping the flag alone never grants approval", representation)

    def test_factory_board_eval_rejects_derivative_laundering_without_forbidding_independent_inputs(self):
        data = json.loads((ROOT / "template-factory/evals/evals.json").read_text())
        case = next(case for case in data["evals"] if case["id"] == 8)
        output = case["expected_output"].lower()
        assertions = " ".join(case["assertions"]).lower()
        self.assertIn("board-origin derivatives remain planning-only", output)
        self.assertIn("independently authored non-board", output)
        for phrase in ("crops", "redraws", "panel prompts", "approval", "new render"):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, assertions)
        self.assertNotIn("permits a separately selected clean derivative", output)

    def test_root_policy_keeps_board_origin_ineligible_and_independent_inputs_conditional(self):
        text = " ".join((ROOT.parents[1] / "AGENTS.md").read_text().lower().split())
        self.assertIn("boards and board-origin derivatives remain planning-only", text)
        self.assertIn("independently authored non-board stills and independent animated blockouts", text)
        self.assertNotIn("derivative boards require current source hashes and explicit selection before video use", text)


if __name__ == "__main__":
    unittest.main()
