import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / ".agents/skills"


class AudioFinalizationPolicyTests(unittest.TestCase):
    def test_effect_presets_do_not_disable_native_sound_by_default(self):
        for path in (SKILLS / "seedance-effects-studio/references").glob("effects-*.md"):
            with self.subTest(path=path.name):
                text = " ".join(path.read_text().split()).lower()
                for phrase in ("`generate_audio` false", "`generate_audio: false`",
                               "native audio is off", "native audio stays off",
                               "generate_audio stays false"):
                    self.assertFalse(phrase in text, f"{path.name}: {phrase}")

    def test_native_audio_needs_no_finishing_pass(self):
        text = (ROOT / ".agents/contracts/audio-video-alignment.md").read_text()
        self.assertIn("Native generated audio is sufficient unchanged", text)
        self.assertIn("Finalization alone does not authorize audio modification", text)
        for phrase in ("Normalize every delivered master", "pad short audio", "-16 LUFS"):
            self.assertNotIn(phrase, text)

    def test_retired_muted_source_rule_has_no_alias(self):
        rules = json.loads((ROOT / ".agents/contracts/rules.json").read_text())["rules"]
        self.assertNotIn("v2v.muted_source", {rule["id"] for rule in rules})
        for path in (SKILLS / "prompt-review/references").glob("*"):
            if path.is_file():
                self.assertNotIn("v2v.muted_source", path.read_text())

    def test_native_source_route_is_not_an_exception_or_mute_recipe(self):
        paths = [
            ROOT / ".agents/contracts/video-to-video-inputs.md",
            SKILLS / "seedance-motion-recast/SKILL.md",
            SKILLS / "seedance-motion-recast/references/audio-and-lipsync.md",
            SKILLS / "seedance-object-swap/SKILL.md",
            SKILLS / "seedance-restyle/SKILL.md",
            SKILLS / "seedance-restoration/SKILL.md",
        ]
        for path in paths:
            with self.subTest(path=path):
                text = " ".join(path.read_text().split()).lower()
                self.assertIn("native", text)
                for phrase in (
                    "submit only a muted", "submit the muted master",
                    "every recast submits", "silent output. sound is added in post.",
                    "native audio generation is not part",
                ):
                    self.assertNotIn(phrase, text)

    def test_hyperframes_carve_is_not_a_render_requirement(self):
        for relative in ("hyperframes-audio/SKILL.md", "general-video/SKILL.md"):
            text = " ".join((SKILLS / relative).read_text().split()).lower()
            with self.subTest(path=relative):
                self.assertIn("explicitly requested", text)
                for phrase in ("carve by default", "carve the bed before verifying",
                               "only then render", "is carved by default"):
                    self.assertNotIn(phrase, text)


class AvatarAudioDeliveryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        path = SKILLS / "seedance-avatar-news/scripts/render_short.py"
        spec = importlib.util.spec_from_file_location("avatar_delivery", path)
        cls.module = importlib.util.module_from_spec(spec)
        with patch.dict(sys.modules, {"PIL": MagicMock()}):
            spec.loader.exec_module(cls.module)

    def test_delivery_copies_optional_soundtrack_without_filters_or_tail_limit(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            config = root / "edl.json"
            words = root / "words.json"
            words.write_text('{"words":[]}')
            config.write_text(json.dumps({
                "stt": str(words), "take": str(root / "take.mp4"),
                "out": str(root / "out.mp4"), "end": 1.0, "segments": [],
            }))
            with (
                patch.object(sys, "argv", ["render_short.py", str(config)]),
                patch.object(self.module, "validate", return_value=[]),
                patch.object(self.module, "build_cues", return_value=[]),
                patch.object(self.module, "build_graphics", return_value=([], "header.png")),
                patch.object(self.module, "build_segments", return_value="picture.mp4"),
                patch.object(self.module, "run") as run,
                patch("builtins.print"),
            ):
                self.module.main()
            command = run.call_args.args[0]
            self.assertIn("1:a?", command)
            self.assertEqual(command[command.index("-c:a") + 1], "copy")
            for option in ("-af", "-ar", "-b:a", "-shortest", "-t", "-frames:v"):
                self.assertNotIn(option, command)


if __name__ == "__main__":
    unittest.main()
