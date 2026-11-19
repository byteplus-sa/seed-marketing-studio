import re
import shutil
import struct
import subprocess
import tempfile
import unittest
import wave
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / ".agents/skills/lark-showcase-aigc"


def text(path):
    return " ".join(path.read_text().lower().split())


class ShowcaseSkillContractsTests(unittest.TestCase):
    def test_exact_prompts_are_exempt_from_cleanup_and_manual_wrapping(self):
        content = text(SKILL / "references/guide-prompt-cleanup-rules.md")
        self.assertIn("exact prompt cells are exempt", content)
        self.assertIn("never insert line breaks", content)
        self.assertIn("do not normalize whitespace", content)
        self.assertIn("report native wrapping as unresolved", content)
        self.assertNotIn("manual soft-wrapping", content)

    def test_all_layout_callers_preserve_native_wrapping(self):
        paths = (
            "references/guide-table-first-layout-default.md",
            "references/guide-project-showcase-layout.md",
        )
        for relative in paths:
            with self.subTest(path=relative):
                content = text(SKILL / relative)
                self.assertIn("native wrap", content)
                self.assertNotIn("soft-wrapped at authoring time", content)
                self.assertNotIn("whitespace normalization", content)

    def test_layout_depends_on_requested_mode_and_available_storyboards(self):
        for relative in ("SKILL.md", "references/guide-project-showcase-layout.md"):
            with self.subTest(path=relative):
                content = text(SKILL / relative)
                self.assertIn("showcase-only", content)
                self.assertIn("matching generated boards exist", content)
                self.assertIn("no explanatory material", content)
                self.assertIn("only when requested", content)

    def test_video_upload_recovery_has_a_document_bound_receipt(self):
        content = text(SKILL / "references/guide-playable-video-delivery.md")
        for clause in (
            "source sha-256", "document id", "target", "receipt",
            "before retrying", "unknown", "do not upload again",
            "served", "same hash", "acceptance",
        ):
            with self.subTest(clause=clause):
                self.assertIn(clause, content)

    def test_assembly_durations_are_not_claimed_as_sync_proof(self):
        content = text(ROOT / ".agents/skills/ffmpeg-scene-transitions/SKILL.md")
        self.assertIn("matching durations do not prove synchronization", content)
        self.assertIn("segment-level", content)
        self.assertIn("full-speed playback and listening", content)
        self.assertIn("1,024", content)
        self.assertIn("never apply", content)
        self.assertNotIn("this proves the drift fix", content)

    def test_crossfade_contact_samples_are_inside_the_transition(self):
        content = (ROOT / ".agents/skills/ffmpeg-scene-transitions/SKILL.md").read_text()
        self.assertIn("offset_i + transition_duration/2", content)
        section = content.split("**Boundary contact sheet", 1)[1].split(
            "## Troubleshooting", 1
        )[0]
        samples = [float(value) for value in re.findall(r"-ss ([0-9.]+)", section)]
        self.assertEqual(len(samples), 3)
        for sample, offset, duration in zip(
            samples, (29.74, 59.28, 88.83), (0.3, 0.5, 0.5), strict=True
        ):
            with self.subTest(offset=offset):
                self.assertAlmostEqual(sample, offset + duration / 2)
                self.assertGreater(sample, offset)
                self.assertLess(sample, offset + duration)


@unittest.skipUnless(shutil.which("ffmpeg"), "ffmpeg is not installed")
class AssemblyEvidenceSmokeTests(unittest.TestCase):
    def test_equal_audio_durations_can_hide_a_shifted_event(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "source.wav"
            rendered = Path(directory) / "rendered.wav"
            sample_rate = 48000
            samples = [0] * sample_rate
            samples[12000:12048] = [12000] * 48
            with wave.open(str(source), "wb") as writer:
                writer.setnchannels(1)
                writer.setsampwidth(2)
                writer.setframerate(sample_rate)
                writer.writeframes(struct.pack(f"<{len(samples)}h", *samples))
            subprocess.run(
                [
                    "ffmpeg", "-v", "error", "-i", str(source),
                    "-af", "adelay=25:all=1,atrim=0:1",
                    "-c:a", "pcm_s16le", str(rendered),
                ],
                check=True, capture_output=True,
            )
            with wave.open(str(rendered), "rb") as reader:
                self.assertEqual(reader.getnframes(), sample_rate)
                output = struct.unpack(
                    f"<{sample_rate}h", reader.readframes(sample_rate)
                )
            first_event = next(index for index, sample in enumerate(output) if sample)
            self.assertEqual(first_event - 12000, 1200)
            self.assertAlmostEqual((first_event - 12000) / sample_rate, 0.025)

    def test_corrected_crossfade_midpoint_contains_both_neighboring_scenes(self):
        with tempfile.TemporaryDirectory() as directory:
            rendered = Path(directory) / "dissolve.mp4"
            subprocess.run(
                [
                    "ffmpeg", "-v", "error",
                    "-f", "lavfi", "-i", "color=red:s=64x64:r=24:d=2",
                    "-f", "lavfi", "-i", "color=blue:s=64x64:r=24:d=2",
                    "-filter_complex",
                    (
                        "[0:v]settb=AVTB[first];[1:v]settb=AVTB[second];"
                        "[first][second]xfade=duration=0.5:offset=1.5[out]"
                    ),
                    "-map", "[out]", "-c:v", "libx264", str(rendered),
                ],
                check=True, capture_output=True,
            )
            for time, mixing in ((1.5 + 0.5 / 2, True), (1.5 - 0.5 / 2, False)):
                frame = subprocess.run(
                    [
                        "ffmpeg", "-v", "error", "-ss", str(time),
                        "-i", str(rendered), "-frames:v", "1",
                        "-f", "rawvideo", "-pix_fmt", "rgb24", "pipe:1",
                    ],
                    check=True, capture_output=True,
                ).stdout
                self.assertEqual(len(frame), 64 * 64 * 3)
                red, _, blue = frame[:3]
                with self.subTest(time=time):
                    if mixing:
                        self.assertGreater(red, 80)
                        self.assertGreater(blue, 80)
                    else:
                        self.assertGreater(red, 200)
                        self.assertLess(blue, 20)


if __name__ == "__main__":
    unittest.main()
