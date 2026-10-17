from __future__ import annotations

import contextlib
import hashlib
import importlib.util
import io
import json
import sys
import tempfile
import unittest
from itertools import pairwise
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / ".agents/skills/ad-captions/scripts/make_captions.py"
SPEC = importlib.util.spec_from_file_location("make_captions", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)

CaptionError = MODULE.CaptionError
RLM = "\u200f"
ZWSP = "\u200b"


def make_line(line_id, start_s, end_s, **text):
    return MODULE.Line(
        line_id, "Speaker", round(start_s * 1000), round(end_s * 1000), text
    )


def settings_for(language="en", **overrides):
    return MODULE.resolve_settings(language, **overrides)


def build(lines, language="en", overlap="trim", **overrides):
    return MODULE.build_cues(
        lines, language, settings_for(language, **overrides), overlap=overlap
    )


class TimestampAndRenderTests(unittest.TestCase):
    def test_srt_block_has_index_comma_timestamps_and_trailing_newline(self):
        cues, warnings = build([make_line("a", 1.0, 3.5, en="Hello there.")])
        self.assertEqual(
            MODULE.render_srt(cues),
            "1\n00:00:01,000 --> 00:00:03,500\nHello there.\n",
        )
        self.assertEqual(warnings, [])

    def test_timestamp_rolls_over_hours_minutes_and_seconds(self):
        self.assertEqual(MODULE.format_timestamp(3_723_456, ","), "01:02:03,456")
        self.assertEqual(MODULE.format_timestamp(0, "."), "00:00:00.000")

    def test_webvtt_has_header_dot_timestamps_and_escapes_markup(self):
        cues, _ = build([make_line("a", 0.5, 2.5, en="Tom & Jerry <run>")])
        document = MODULE.render_vtt(cues)
        self.assertTrue(
            document.startswith("WEBVTT\n\n00:00:00.500 --> 00:00:02.500\n")
        )
        self.assertIn("Tom &amp; Jerry &lt;run&gt;", document)

    def test_cues_are_numbered_in_time_order_even_if_input_is_not(self):
        cues, _ = build(
            [
                make_line("late", 4.0, 6.0, en="Second."),
                make_line("early", 0.0, 2.0, en="First."),
            ]
        )
        self.assertEqual([cue.lines[0] for cue in cues], ["First.", "Second."])
        self.assertTrue(MODULE.render_srt(cues).startswith("1\n00:00:00,000"))


class GraphemeTests(unittest.TestCase):
    def test_combining_marks_stay_with_their_base(self):
        self.assertEqual(MODULE.grapheme_clusters("éa"), ["é", "a"])
        self.assertEqual(len(MODULE.grapheme_clusters("كَتَبَ")), 3)

    def test_virama_conjunct_is_one_cluster(self):
        self.assertEqual(len(MODULE.grapheme_clusters("क्ष")), 1)

    def test_zero_width_space_is_a_break_opportunity_and_is_dropped(self):
        tokens = MODULE.tokenize("ab" + ZWSP + "cd")
        self.assertEqual([token.text for token in tokens], ["ab", "cd"])
        self.assertEqual(tokens[1].glue, "")


class WrappingTests(unittest.TestCase):
    def test_cjk_wraps_by_character_without_orphaned_punctuation(self):
        text = "你早就知道了，却从来没有对我说过一个字，一个字都没有。"
        cues, _ = build([make_line("a", 0, 6, zh=text)], "zh")
        self.assertEqual(len(cues), 1)
        rendered = cues[0].lines
        self.assertEqual("".join(rendered), text)
        self.assertEqual(len(rendered), 2)
        for line in rendered:
            self.assertLessEqual(len(line), 16)
            self.assertNotIn(line[0], "，。！？、")

    def test_cjk_punctuation_is_not_pushed_to_the_next_line_start(self):
        for body in (
            "一二三四五六七八九十甲乙丙丁戊己",
            "一二三四五六七八九十甲乙丙丁戊",
        ):
            text = body + "，庚辛。"
            cues, _ = build([make_line("a", 0, 6, zh=text)], "zh")
            for cue in cues:
                for line in cue.lines:
                    self.assertNotIn(line[0], "，。")

    def test_arabic_wraps_at_spaces_only_and_marks_each_line_right_to_left(self):
        text = "كنتَ تعرف طوال الوقت، ولم تقل لي كلمة واحدة أبداً."
        cues, _ = build([make_line("a", 0, 5, ar=text)], "ar", max_chars=24)
        original_words = set(text.split())
        rendered = [line for cue in cues for line in cue.lines]
        self.assertGreater(len(rendered), 1)
        for line in rendered:
            self.assertTrue(line.startswith(RLM))
            self.assertLessEqual(len(MODULE.grapheme_clusters(line)) - 1, 24)
            self.assertTrue(set(line.lstrip(RLM).split()) <= original_words)

    def test_left_to_right_language_gets_no_direction_marks(self):
        cues, _ = build([make_line("a", 0, 3, en="Not here.")])
        self.assertNotIn(RLM, cues[0].lines[0])

    def test_rtl_detection_covers_codes_and_script_subtags(self):
        self.assertTrue(MODULE.is_right_to_left("ar"))
        self.assertTrue(MODULE.is_right_to_left("he-IL"))
        self.assertTrue(MODULE.is_right_to_left("ku-Arab"))
        self.assertFalse(MODULE.is_right_to_left("en"))

    def test_balanced_two_line_wrap(self):
        cues, _ = build(
            [make_line("a", 0, 4, en="You knew all along and never said a word")],
            max_chars=24,
        )
        first, second = cues[0].lines
        self.assertLessEqual(abs(len(first) - len(second)), 6)

    def test_unbroken_run_longer_than_a_line_is_split_with_a_warning(self):
        text = "ก" * 30
        cues, warnings = build([make_line("a", 0, 6, th=text)], "th", max_chars=10)
        self.assertEqual("".join(line for cue in cues for line in cue.lines), text)
        self.assertTrue(any("U+200B" in warning for warning in warnings))


class SplittingAndTimingTests(unittest.TestCase):
    def test_overlong_text_splits_into_contiguous_cues_covering_the_span(self):
        words = [f"alpha{number:02d}" for number in range(16)]
        cues, _ = build(
            [make_line("a", 0, 8, en=" ".join(words))], max_chars=20, max_lines=2
        )
        self.assertEqual(len(cues), 4)
        self.assertEqual(cues[0].start_ms, 0)
        self.assertEqual(cues[-1].end_ms, 8000)
        spoken = " ".join(" ".join(cue.lines) for cue in cues).split()
        self.assertEqual(spoken, words)
        for cue in cues:
            self.assertLessEqual(len(cue.lines), 2)
            for line in cue.lines:
                self.assertLessEqual(len(line), 20)
        for earlier, later in pairwise(cues):
            self.assertLessEqual(earlier.end_ms, later.start_ms)

    def test_cue_longer_than_max_duration_is_split_by_time(self):
        cues, _ = build(
            [make_line("a", 0, 20, en="one two three four five six")],
            max_duration_s=7.0,
        )
        self.assertEqual(len(cues), 3)
        for cue in cues:
            self.assertLessEqual(cue.end_ms - cue.start_ms, 7000)

    def test_short_cue_is_extended_to_minimum_duration(self):
        cues, _ = build([make_line("a", 0, 0.3, en="Hi.")])
        self.assertEqual(cues[0].end_ms, 1000)

    def test_extension_stops_before_the_next_cue_and_warns(self):
        cues, warnings = build(
            [
                make_line("a", 0, 0.3, en="Hi."),
                make_line("b", 0.6, 3.0, en="Hello again, friend."),
            ]
        )
        self.assertEqual(cues[0].end_ms, 560)
        self.assertTrue(any("minimum" in warning for warning in warnings))

    def test_line_too_short_for_its_text_raises_a_caption_error(self):
        words = " ".join(f"word{number:02d}" for number in range(20))
        with self.assertRaisesRegex(CaptionError, "a: .*no duration"):
            build([make_line("a", 1.0, 1.001, en=words)])

    def test_reading_speed_over_limit_is_reported(self):
        _, warnings = build(
            [make_line("a", 0, 1, en="This sentence is far too long for one second.")],
            max_chars=60,
            max_duration_s=1.0,
        )
        self.assertTrue(any("cps" in warning for warning in warnings))


class OverlapTests(unittest.TestCase):
    lines = (
        make_line("a", 0, 2.0, en="First line here."),
        make_line("b", 1.5, 3.5, en="Second line."),
    )

    def test_trim_policy_ends_the_earlier_cue_before_the_later_one(self):
        cues, warnings = build(list(self.lines))
        self.assertEqual(cues[0].end_ms, 1460)
        self.assertEqual(cues[1].start_ms, 1500)
        self.assertTrue(any("trimmed" in warning for warning in warnings))

    def test_error_policy_rejects_overlap(self):
        with self.assertRaisesRegex(CaptionError, "overlap"):
            build(list(self.lines), overlap="error")

    def test_simultaneous_starts_cannot_be_trimmed(self):
        with self.assertRaisesRegex(CaptionError, "cannot trim"):
            build(
                [
                    make_line("a", 1.0, 3.0, en="Both talk."),
                    make_line("b", 1.0, 3.0, en="At once."),
                ]
            )


class ValidationTests(unittest.TestCase):
    def test_missing_language_names_the_line_and_language(self):
        with self.assertRaisesRegex(CaptionError, "a .*no fr text"):
            build([make_line("a", 0, 2, en="Hello.")], "fr")

    def test_blank_language_text_is_rejected(self):
        with self.assertRaisesRegex(CaptionError, "no en text"):
            build([make_line("a", 0, 2, en="   ")])

    def test_text_of_only_zero_width_spaces_is_rejected(self):
        with self.assertRaisesRegex(CaptionError, "no en text"):
            build([make_line("a", 0, 2, en=ZWSP)])

    def test_invalid_language_code_is_rejected(self):
        with self.assertRaisesRegex(CaptionError, "invalid language code"):
            MODULE.normalize_language("en/../x")

    def test_cue_after_master_duration_is_rejected(self):
        with self.assertRaisesRegex(CaptionError, "master duration"):
            MODULE.build_cues(
                [make_line("a", 9.0, 12.0, en="Too late.")],
                "en",
                settings_for("en"),
                master_duration_ms=10_000,
            )

    def test_cjk_defaults_are_narrower_than_latin(self):
        self.assertEqual(settings_for("zh-Hans").max_chars, 16)
        self.assertEqual(settings_for("en").max_chars, 32)
        self.assertEqual(settings_for("zh", chars_for={"zh": 12}).max_chars, 12)
        self.assertEqual(settings_for("en", max_chars=40).max_chars, 40)


class InputFileTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name)

    def write(self, document, name="dialogue.json"):
        path = self.directory / name
        path.write_text(json.dumps(document), encoding="utf-8")
        return path

    def document(self, **overrides):
        document = {
            "schema_version": 1,
            "lines": [
                {
                    "id": "s01-l01",
                    "speaker": "Ana",
                    "start_s": 1.0,
                    "end_s": 3.0,
                    "text": {"en": "Hello.", "es": "Hola."},
                }
            ],
        }
        document.update(overrides)
        return document

    def test_file_offset_and_cli_offset_both_shift_timestamps(self):
        path = self.write(self.document(offset_s=10))
        lines = MODULE.load_lines(path, extra_offset_ms=2500)
        self.assertEqual((lines[0].start_ms, lines[0].end_ms), (13_500, 15_500))

    def test_offset_that_moves_a_line_before_zero_is_rejected(self):
        path = self.write(self.document(offset_s=-5))
        with self.assertRaisesRegex(CaptionError, "before zero"):
            MODULE.load_lines(path)

    def test_end_before_start_is_rejected(self):
        document = self.document()
        document["lines"][0]["end_s"] = 0.5
        with self.assertRaisesRegex(CaptionError, "end after it starts"):
            MODULE.load_lines(self.write(document))

    def test_speaker_is_optional_for_voiceover_lines(self):
        document = self.document()
        del document["lines"][0]["speaker"]
        lines = MODULE.load_lines(self.write(document))
        self.assertEqual(lines[0].speaker, "voice")

    def test_blank_speaker_and_missing_text_are_rejected(self):
        document = self.document()
        document["lines"][0]["speaker"] = "  "
        with self.assertRaisesRegex(CaptionError, "speaker"):
            MODULE.load_lines(self.write(document))
        document = self.document()
        document["lines"][0]["text"] = {}
        with self.assertRaisesRegex(CaptionError, "text object"):
            MODULE.load_lines(self.write(document, "other.json"))

    def test_wrong_schema_version_and_bad_json_are_rejected(self):
        with self.assertRaisesRegex(CaptionError, "schema_version"):
            MODULE.load_lines(self.write(self.document(schema_version=2)))
        broken = self.directory / "broken.json"
        broken.write_text("{", encoding="utf-8")
        with self.assertRaisesRegex(CaptionError, "invalid JSON"):
            MODULE.load_lines(broken)

    def test_default_ids_from_different_files_keep_the_minimum_gap(self):
        first = self.document()
        del first["lines"][0]["id"]
        first["lines"][0].update(start_s=0.0, end_s=1.0)
        second = self.document()
        del second["lines"][0]["id"]
        second["lines"][0].update(start_s=1.0, end_s=3.0)
        lines = MODULE.load_lines(self.write(first, "a.json")) + MODULE.load_lines(
            self.write(second, "b.json")
        )
        self.assertNotEqual(lines[0].line_id, lines[1].line_id)
        cues, _ = MODULE.build_cues(lines, "en", settings_for("en"))
        self.assertEqual(cues[0].end_ms, 960)
        self.assertEqual(cues[1].start_ms, 1000)

    def test_duplicate_line_ids_are_rejected(self):
        with self.assertRaisesRegex(CaptionError, "duplicate line id 'same'"):
            build(
                [
                    make_line("same", 0, 1.0, en="One."),
                    make_line("same", 1.0, 2.0, en="Two."),
                ]
            )

    def test_string_seconds_are_rejected(self):
        document = self.document()
        document["lines"][0]["start_s"] = "1.0"
        with self.assertRaisesRegex(CaptionError, "number of seconds"):
            MODULE.load_lines(self.write(document))


class CommandLineTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name)
        self.source = self.directory / "dialogue.json"
        self.source.write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "lines": [
                        {
                            "id": "l1",
                            "speaker": "Ana",
                            "start_s": 0.5,
                            "end_s": 3.0,
                            "text": {
                                "en": "You knew.",
                                "ar": "كنتَ تعرف.",
                                "zh": "你早就知道了。",
                            },
                        },
                        {
                            "id": "l2",
                            "speaker": "Ben",
                            "start_s": 3.5,
                            "end_s": 5.0,
                            "text": {
                                "en": "Not here.",
                                "ar": "ليس هنا.",
                                "zh": "别在这里。",
                            },
                        },
                    ],
                },
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )
        self.out = self.directory / "out"

    def run_cli(self, *extra):
        arguments = [
            "--input",
            str(self.source),
            "--master-stem",
            "brand_hero_9x16_v01",
            "--out-dir",
            str(self.out),
            *extra,
        ]
        stdout, stderr = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            code = MODULE.main(arguments)
        return code, stdout.getvalue(), stderr.getvalue()

    def test_round_trip_writes_named_sidecars_with_matching_hashes(self):
        code, stdout, _ = self.run_cli(
            "--language", "en", "ar", "zh", "--format", "both", "--offset-s", "2"
        )
        self.assertEqual(code, 0)
        report = json.loads(stdout)
        self.assertEqual(len(report["files"]), 6)
        names = sorted(path.name for path in self.out.iterdir())
        self.assertEqual(
            names,
            [
                f"brand_hero_9x16_v01.{language}.{extension}"
                for language in ("ar", "en", "zh")
                for extension in ("srt", "vtt")
            ],
        )
        english = (self.out / "brand_hero_9x16_v01.en.srt").read_text(encoding="utf-8")
        self.assertEqual(
            english,
            "1\n00:00:02,500 --> 00:00:05,000\nYou knew.\n\n"
            "2\n00:00:05,500 --> 00:00:07,000\nNot here.\n",
        )
        for entry in report["files"]:
            digest = hashlib.sha256(Path(entry["path"]).read_bytes()).hexdigest()
            self.assertEqual(entry["sha256"], digest)
        arabic = (self.out / "brand_hero_9x16_v01.ar.srt").read_text(encoding="utf-8")
        self.assertIn(RLM + "كنتَ تعرف.", arabic)

    def test_existing_sidecar_is_not_overwritten_without_the_flag(self):
        self.assertEqual(self.run_cli("--language", "en")[0], 0)
        code, _, stderr = self.run_cli("--language", "en")
        self.assertEqual(code, 2)
        self.assertIn("exists", stderr)
        self.assertEqual(self.run_cli("--language", "en", "--overwrite")[0], 0)

    def test_missing_language_fails_with_a_clear_message_and_writes_nothing(self):
        code, stdout, stderr = self.run_cli("--language", "fr")
        self.assertEqual(code, 2)
        self.assertEqual(stdout, "")
        self.assertIn("no fr text", stderr)
        self.assertEqual(list(self.out.glob("*")), [])

    def test_master_stem_with_a_path_separator_is_rejected(self):
        arguments = [
            "--input",
            str(self.source),
            "--master-stem",
            "../escape",
            "--language",
            "en",
            "--out-dir",
            str(self.out),
        ]
        stderr = io.StringIO()
        with (
            contextlib.redirect_stderr(stderr),
            contextlib.redirect_stdout(io.StringIO()),
        ):
            code = MODULE.main(arguments)
        self.assertEqual(code, 2)
        self.assertIn("invalid master stem", stderr.getvalue())

    def test_per_language_limit_override_is_applied(self):
        code, _, _ = self.run_cli("--language", "en", "--max-chars-for", "en=5")
        self.assertEqual(code, 0)
        english = (self.out / "brand_hero_9x16_v01.en.srt").read_text(encoding="utf-8")
        for line in english.splitlines():
            if line and not line[0].isdigit():
                self.assertLessEqual(len(line), 9)


PLATFORMS = {
    "schema_version": 1,
    "verified_on": "2026-10-17",
    "reverify_before_use": True,
    "placements": [
        {
            "id": "vertical-published",
            "aspect_ratio": "9:16",
            "safe_zone": {
                "top": 0.1,
                "bottom": 0.2,
                "left": 0.05,
                "right": 0.05,
                "source": "synthetic",
            },
        },
        {
            "id": "vertical-template-only",
            "aspect_ratio": "9:16",
            "safe_zone": {
                "top": None,
                "bottom": None,
                "left": None,
                "right": None,
                "source": "template files only",
            },
        },
    ],
}


class BurnInTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name)
        self.platforms = self.directory / "platforms.json"
        self.platforms.write_text(json.dumps(PLATFORMS), encoding="utf-8")
        self.source = self.directory / "script.json"
        self.source.write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "lines": [
                        {
                            "id": "vo-01",
                            "start_s": 0.5,
                            "end_s": 2.5,
                            "text": {
                                "en": "Fresh & <cold> all day.",
                                "ar": "بارد طوال اليوم.",
                            },
                        },
                        {
                            "id": "vo-02",
                            "start_s": 3.0,
                            "end_s": 4.5,
                            "text": {"en": "Shop now.", "ar": "تسوّق الآن."},
                        },
                    ],
                },
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )
        self.out = self.directory / "out"
        self.compositions = self.directory / "studio" / "compositions"

    def run_cli(self, *extra, languages=("en",)):
        arguments = [
            "--input",
            str(self.source),
            "--master-stem",
            "brand_hero_9x16_v01",
            "--out-dir",
            str(self.out),
            "--language",
            *languages,
            "--composition-dir",
            str(self.compositions),
            "--platforms",
            str(self.platforms),
            *extra,
        ]
        stdout, stderr = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            code = MODULE.main(arguments)
        return code, stdout.getvalue(), stderr.getvalue()

    def written_files(self):
        return sorted(path for path in self.directory.rglob("*") if path.is_file())

    def test_published_placement_positions_cues_inside_the_safe_rect(self):
        code, stdout, _ = self.run_cli(
            "--size", "1080x1920", "--placement", "vertical-published"
        )
        self.assertEqual(code, 0)
        report = json.loads(stdout)
        self.assertEqual(
            report["safe_rect"], {"x": 54, "y": 192, "width": 972, "height": 1344}
        )
        layer = (self.compositions / "captions-en.html").read_text(encoding="utf-8")
        self.assertIn("left: 54px; width: 972px; bottom: 384px;", layer)
        self.assertIn('data-composition-id="captions-en"', layer)
        self.assertIn('data-start="0.5" data-duration="2"', layer)
        self.assertIn("Fresh &amp; &lt;cold&gt; all day.", layer)
        self.assertIn("<template>", layer)
        self.assertIn(
            'data-composition-src="compositions/captions-en.html"',
            report["host_snippets"][0],
        )
        self.assertIn('data-duration="4.5"', report["host_snippets"][0])
        kinds = sorted(entry["format"] for entry in report["files"])
        self.assertEqual(kinds, ["hyperframes", "srt"])
        for entry in report["files"]:
            digest = hashlib.sha256(Path(entry["path"]).read_bytes()).hexdigest()
            self.assertEqual(entry["sha256"], digest)

    def test_top_anchor_and_master_duration_drive_layer_geometry(self):
        code, stdout, _ = self.run_cli(
            "--size",
            "1080x1920",
            "--placement",
            "vertical-published",
            "--anchor",
            "top",
            "--master-duration-s",
            "6",
        )
        self.assertEqual(code, 0)
        layer = (self.compositions / "captions-en.html").read_text(encoding="utf-8")
        self.assertIn("top: 192px;", layer)
        self.assertIn('data-duration="6"', json.loads(stdout)["host_snippets"][0])

    def test_right_to_left_layer_sets_direction_and_language(self):
        code, _, _ = self.run_cli(
            "--size",
            "1080x1920",
            "--placement",
            "vertical-published",
            languages=("ar",),
        )
        self.assertEqual(code, 0)
        layer = (self.compositions / "captions-ar.html").read_text(encoding="utf-8")
        self.assertIn('lang="ar" dir="rtl"', layer)
        self.assertIn(RLM + "بارد طوال اليوم.", layer)

    def test_unpublished_safe_zone_is_refused_and_nothing_is_written(self):
        code, stdout, stderr = self.run_cli(
            "--size", "1080x1920", "--placement", "vertical-template-only"
        )
        self.assertEqual(code, 2)
        self.assertEqual(stdout, "")
        self.assertIn("unpublished", stderr)
        self.assertIn("--safe-rect", stderr)
        self.assertEqual(self.written_files(), [self.platforms, self.source])

    def test_measured_safe_rect_unlocks_an_unpublished_placement(self):
        code, stdout, _ = self.run_cli(
            "--size",
            "1080x1920",
            "--placement",
            "vertical-template-only",
            "--safe-rect",
            "60,250,960,1100",
        )
        self.assertEqual(code, 0)
        self.assertEqual(
            json.loads(stdout)["safe_rect"],
            {"x": 60, "y": 250, "width": 960, "height": 1100},
        )

    def test_size_with_the_wrong_ratio_is_rejected(self):
        code, _, stderr = self.run_cli(
            "--size", "1080x1350", "--placement", "vertical-published"
        )
        self.assertEqual(code, 2)
        self.assertIn("does not match", stderr)

    def test_unknown_placement_and_missing_layout_inputs_are_rejected(self):
        code, _, stderr = self.run_cli("--size", "1080x1920", "--placement", "nope")
        self.assertEqual(code, 2)
        self.assertIn("unknown placement", stderr)
        code, _, stderr = self.run_cli("--size", "1080x1920")
        self.assertEqual(code, 2)
        self.assertIn("--placement or --safe-rect", stderr)
        code, _, stderr = self.run_cli("--placement", "vertical-published")
        self.assertEqual(code, 2)
        self.assertIn("--size", stderr)

    def test_safe_rect_outside_the_frame_is_rejected(self):
        code, _, stderr = self.run_cli(
            "--size", "1080x1920", "--safe-rect", "100,100,1000,500"
        )
        self.assertEqual(code, 2)
        self.assertIn("inside the frame", stderr)

    def test_font_source_traversal_and_bad_colors_are_rejected(self):
        for flag, value, message in (
            ("--font-src", "../fonts/x.woff2", "font source"),
            ("--font-src", "/abs/x.woff2", "font source"),
            ("--font-src", "assets/fonts/x.exe", "font source"),
            ("--text-color", "red", "color"),
            ("--box-color", "#12345", "color"),
            ("--font-family", 'Brand"; }', "font family"),
        ):
            code, _, stderr = self.run_cli(
                "--size", "1080x1920", "--placement", "vertical-published", flag, value
            )
            self.assertEqual(code, 2, value)
            self.assertIn(message, stderr)
        self.assertFalse(self.compositions.exists())

    def test_brand_font_is_loaded_from_a_project_local_file(self):
        code, _, _ = self.run_cli(
            "--size",
            "1080x1920",
            "--placement",
            "vertical-published",
            "--font-family",
            "Brand Sans",
            "--font-src",
            "assets/fonts/brand-sans.woff2",
            "--text-color",
            "#FFEE00",
        )
        self.assertEqual(code, 0)
        layer = (self.compositions / "captions-en.html").read_text(encoding="utf-8")
        self.assertIn(
            '@font-face { font-family: "Brand Sans"; src: url("assets/fonts/brand-sans.woff2"); }',
            layer,
        )
        self.assertIn("color: #FFEE00;", layer)

    def test_line_wider_than_the_safe_width_is_warned(self):
        code, stdout, _ = self.run_cli(
            "--size",
            "1080x1920",
            "--safe-rect",
            "400,300,280,1000",
            "--font-size",
            "60",
        )
        self.assertEqual(code, 0)
        warnings = json.loads(stdout)["warnings"]
        self.assertTrue(any("safe width" in warning for warning in warnings))

    def test_failure_in_a_later_language_writes_no_files(self):
        code, _, stderr = self.run_cli(
            "--size",
            "1080x1920",
            "--placement",
            "vertical-published",
            languages=("en", "fr"),
        )
        self.assertEqual(code, 2)
        self.assertIn("no fr text", stderr)
        self.assertFalse(self.out.exists())
        self.assertFalse(self.compositions.exists())

    def test_existing_layer_is_not_overwritten_without_the_flag(self):
        arguments = ("--size", "1080x1920", "--placement", "vertical-published")
        self.assertEqual(self.run_cli(*arguments)[0], 0)
        code, _, stderr = self.run_cli(*arguments)
        self.assertEqual(code, 2)
        self.assertIn("exists", stderr)
        self.assertEqual(self.run_cli(*arguments, "--overwrite")[0], 0)

    def test_repository_platform_data_resolves_a_published_placement(self):
        layout = MODULE.resolve_layout(
            "1080x1920", "meta-instagram-reels", None, MODULE.DEFAULT_PLATFORMS
        )
        self.assertEqual(
            (layout.x, layout.y, layout.safe_width, layout.safe_height),
            (65, 269, 950, 979),
        )


if __name__ == "__main__":
    unittest.main()
