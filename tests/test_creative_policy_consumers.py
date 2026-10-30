import json
import unittest
from pathlib import Path

SKILLS = Path(__file__).resolve().parents[1] / ".agents" / "skills"
INTAKE = SKILLS / "brief-intake"


class CreativePolicyConsumerTests(unittest.TestCase):
    def text(self, path: Path) -> str:
        return " ".join(path.read_text(encoding="utf-8").lower().split())

    def test_intake_keeps_wordless_native_sound_available(self):
        text = self.text(INTAKE / "SKILL.md")
        for concept in ("ownership", "native", "diegetic", "wordless"):
            with self.subTest(concept=concept):
                self.assertTrue(concept in text, f"Intake is missing {concept}")
        self.assertNotIn(
            "`picture_only` when the sound is ambience, score or a wordless arc",
            text,
        )
        self.assertNotIn(
            "prefer `picture_only` for ambience-only and score-driven pieces", text
        )

    def test_intake_retains_control_silence_and_unresolved_ownership(self):
        text = self.text(INTAKE / "SKILL.md")
        for concept in (
            "exact master",
            "controlled post",
            "purposeful silence",
            "unwanted",
            "supported",
        ):
            with self.subTest(concept=concept):
                self.assertTrue(concept in text, f"Intake is missing {concept}")
        self.assertRegex(text, r"ownership[^.]*unresolved[^.]*ask")
        self.assertIn("separate lip-sync audio remains opt-in", text)

    def test_requested_native_sound_led_draft_keeps_its_generation_scope(self):
        text = self.text(INTAKE / "SKILL.md")
        self.assertIn(
            "an explicitly requested original native soundscape or one-generation "
            "sound-led draft uses `native`; do not silently mute it or add an audio "
            "generation.",
            text,
        )

    def test_confirmed_audio_examples_keep_their_explicit_choices(self):
        text = self.text(INTAKE / "SKILL.md")
        self.assertIn(
            'approval_evidence: "user accepted silent picture with a post ambience bed."',
            text,
        )
        self.assertIn("locked: audio_mode: picture_only", text)

    def test_wordless_eval_does_not_reward_automatic_post_audio(self):
        data = json.loads((INTAKE / "evals/evals.json").read_text(encoding="utf-8"))
        cases = [case for case in data["evals"] if "wordless TVC" in case["prompt"]]
        self.assertTrue(cases)
        for case in cases:
            text = " ".join(
                [case["expected_output"], *case["expectations"]]
            ).lower()
            for concept in ("ownership", "native", "picture_only", "control", "ask"):
                with self.subTest(case=case["id"], concept=concept):
                    self.assertTrue(concept in text, f"Eval is missing {concept}")

    def test_worked_audio_repair_is_conditional_on_control(self):
        text = self.text(INTAKE / "references/worked-repairs.md")
        heading = "## an ad brief that leaves sound and structure to the edit"
        repair = text.split(heading, 1)[1].split("## ", 1)[0]
        for concept in ("ownership", "native", "when", "control"):
            with self.subTest(concept=concept):
                self.assertTrue(concept in repair, f"Audio repair is missing {concept}")
        self.assertNotIn("audio route `picture_only`: generate silent picture", repair)

    def test_shot_template_allows_scoped_looks_and_preserves_palette_locks(self):
        text = self.text(
            SKILLS / "seedance-prompt-25/references/shot-staging.md"
        ).split("## per-shot template", 1)[1].split("## carrying a shot plan", 1)[0]
        self.assertNotIn("one grade once", text)
        self.assertNotIn("<one grade for the clip>", text)
        for concept in ("brief-derived", "transition", "scope", "locked palette"):
            with self.subTest(concept=concept):
                self.assertTrue(concept in text, f"Shot template is missing {concept}")

    def test_music_template_allows_ordered_events_and_sustained_states(self):
        text = self.text(
            SKILLS / "seedance-music-video/references/output-templates.md"
        )
        self.assertNotRegex(text, r"<one (?:action|event)\b")
        for concept in ("critical", "ordered actions", "reveals", "sustained state"):
            with self.subTest(concept=concept):
                self.assertTrue(concept in text, f"Music template is missing {concept}")
        self.assertIn("for preservation-only edits, retain source camera", text)


if __name__ == "__main__":
    unittest.main()
