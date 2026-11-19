import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE_POLICIES = (
    ".agents/skills/seedream-character-sheet/SKILL.md",
    ".agents/skills/seedance-virtual-portrait/SKILL.md",
    ".agents/skills/seedance-virtual-portrait/references/registration-and-ledger.md",
    ".agents/contracts/video-to-video-inputs.md",
    ".agents/skills/seedance-motion-recast/SKILL.md",
)


def normalized_text(relative_path):
    return " ".join((ROOT / relative_path).read_text().lower().split())


class VirtualPortraitContractTests(unittest.TestCase):
    def test_registration_sources_keep_the_approved_three_panel_sheet_unchanged(self):
        for relative_path in SOURCE_POLICIES:
            with self.subTest(path=relative_path):
                text = normalized_text(relative_path)
                self.assertIn("approved three-panel character sheet", text)
                self.assertIn("unchanged", text)

    def test_local_sources_do_not_require_separate_views_or_ban_turnarounds(self):
        for relative_path in SOURCE_POLICIES:
            for obsolete_rule in (
                "one image per view",
                "separate images per view",
                "never a collage",
                "never collages",
                "never a collage or turnaround strip",
            ):
                with self.subTest(path=relative_path, rule=obsolete_rule):
                    self.assertNotIn(obsolete_rule, normalized_text(relative_path))

    def test_registration_does_not_trigger_character_sheet_cleanup(self):
        for relative_path in (
            ".agents/skills/seedream-character-sheet/SKILL.md",
            ".agents/skills/seedream-character-sheet-cleanup/SKILL.md",
        ):
            with self.subTest(path=relative_path):
                text = normalized_text(relative_path)
                self.assertIn(
                    "virtual portrait registration does not require cleanup", text
                )

    def test_sheet_panels_are_views_of_one_subject_not_separate_people(self):
        text = normalized_text(
            ".agents/skills/seedance-virtual-portrait/references/registration-and-ledger.md"
        )
        self.assertIn("three views of the same character", text)
        self.assertIn("one subject per group", text)
        self.assertIn("one source image", text)

    def test_ledger_records_sheet_identity_and_preserves_activation_and_hashes(self):
        relative_path = (
            ".agents/skills/seedance-virtual-portrait/references/registration-and-ledger.md"
        )
        text = (ROOT / relative_path).read_text()
        ledger = json.loads(text.split("```json\n", 1)[1].split("```", 1)[0])
        asset = ledger["assets"][0]
        self.assertIn("three-panel character sheet", asset["view"])
        self.assertIn("source_path", asset)
        self.assertIn("source_sha256", asset)
        self.assertEqual(asset["status"], "Active")
        self.assertIn("project_name", ledger)
        self.assertIn("a changed source needs a new asset", " ".join(text.split()))
        self.assertIn("Wait for", text)

    def test_provider_rejection_stops_instead_of_authorizing_source_processing(self):
        text = normalized_text(
            ".agents/skills/seedance-virtual-portrait/references/registration-and-ledger.md"
        )
        self.assertIn("report the exact error and stop", text)
        self.assertIn("do not silently process or replace the sheet", text)

    def test_existing_valid_portrait_registrations_do_not_need_replacement(self):
        text = normalized_text(
            ".agents/skills/seedance-virtual-portrait/references/registration-and-ledger.md"
        )
        self.assertIn("existing valid registrations remain reusable", text)
        self.assertIn("does not require replacing them", text)

    def test_character_sheet_default_still_preserves_back_front_and_face_authority(self):
        text = (ROOT / ".agents/skills/seedream-character-sheet/SKILL.md").read_text()
        default = text.split("## Default production rule", 1)[1].split(
            "## Why this layout", 1
        )[0]
        self.assertLess(default.index("Back full-body"), default.index("Front full-body"))
        self.assertLess(default.index("Front full-body"), default.index("Face close-up"))
        self.assertIn("close-up panel is the face authority", text)


if __name__ == "__main__":
    unittest.main()
