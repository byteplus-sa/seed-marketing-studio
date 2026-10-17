from __future__ import annotations

import contextlib
import copy
import importlib.util
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path
from xml.etree import ElementTree

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / ".agents/contracts/ad-platforms.json"
CONTRACT_DOC = ROOT / ".agents/contracts/ad-platforms.md"
SCHEMA = ROOT / ".agents/contracts/schemas/ad-platforms.schema.json"
SCRIPT = ROOT / ".agents/skills/ad-delivery-formats/scripts/safe_zones.py"
SPEC = importlib.util.spec_from_file_location("safe_zones", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)

SVG = "{http://www.w3.org/2000/svg}"


def load_contract():
    return json.loads(CONTRACT.read_text(encoding="utf-8"))


def schema_errors(document):
    validator = Draft202012Validator(json.loads(SCHEMA.read_text(encoding="utf-8")))
    return list(validator.iter_errors(document))


def run_cli(*arguments):
    stdout, stderr = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
        code = MODULE.main(list(arguments))
    return code, stdout.getvalue(), stderr.getvalue()


class ContractDataTests(unittest.TestCase):
    def test_schema_is_valid_draft_2020_12(self):
        Draft202012Validator.check_schema(
            json.loads(SCHEMA.read_text(encoding="utf-8"))
        )

    def test_repository_data_matches_the_schema(self):
        self.assertEqual(schema_errors(load_contract()), [])

    def test_every_placement_is_dated_and_sourced_unless_unverified(self):
        document = load_contract()
        self.assertTrue(document["reverify_before_use"])
        for placement in document["placements"]:
            self.assertEqual(placement["verified_on"], document["verified_on"])
            if placement["status"] != "unverified":
                self.assertTrue(placement["source_url"].startswith("https://"))
            self.assertIn(
                placement["aspect_ratio"], placement["accepted_aspect_ratios"]
            )

    def test_placement_ids_are_unique_and_listed_in_the_human_table(self):
        ids = [placement["id"] for placement in load_contract()["placements"]]
        self.assertEqual(len(ids), len(set(ids)))
        table = CONTRACT_DOC.read_text(encoding="utf-8")
        for identifier in ids:
            self.assertIn(f"`{identifier}`", table)

    def test_known_conflicts_stay_visible(self):
        placements = {item["id"]: item for item in load_contract()["placements"]}
        self.assertTrue(placements["tiktok-in-feed"]["conflicts"])
        self.assertIsNone(placements["tiktok-in-feed"]["safe_zone"]["top"])
        self.assertEqual(placements["meta-feed"]["status"], "unverified")
        self.assertEqual(
            placements["meta-instagram-reels"]["safe_zone"]["bottom"], 0.35
        )

    def test_schema_rejects_a_partly_published_safe_zone(self):
        document = load_contract()
        document["placements"][1]["safe_zone"]["top"] = None
        self.assertTrue(schema_errors(document))

    def test_schema_rejects_out_of_range_fractions_and_insecure_sources(self):
        document = load_contract()
        bad_fraction = copy.deepcopy(document)
        bad_fraction["placements"][1]["safe_zone"]["bottom"] = 0.5
        self.assertTrue(schema_errors(bad_fraction))
        bad_source = copy.deepcopy(document)
        bad_source["placements"][1]["source_url"] = "http://example.com"
        self.assertTrue(schema_errors(bad_source))
        missing_date = copy.deepcopy(document)
        del missing_date["placements"][0]["verified_on"]
        self.assertTrue(schema_errors(missing_date))

    def test_schema_rejects_unknown_fields_and_bad_ratios(self):
        document = load_contract()
        extra = copy.deepcopy(document)
        extra["placements"][0]["score"] = 9
        self.assertTrue(schema_errors(extra))
        ratio = copy.deepcopy(document)
        ratio["placements"][0]["aspect_ratio"] = "9x16"
        self.assertTrue(schema_errors(ratio))


REELS_MARGINS = {"top": 0.14, "bottom": 0.35, "left": 0.06, "right": 0.06}


class SafeZoneMathTests(unittest.TestCase):
    def test_reels_rectangle_at_1080x1920_rounds_inward(self):
        rect = MODULE.safe_rect(1080, 1920, REELS_MARGINS)
        self.assertEqual(
            rect.as_dict(), {"x": 65, "y": 269, "width": 950, "height": 979}
        )

    def test_reels_rectangle_at_recommended_size(self):
        rect = MODULE.safe_rect(1440, 2560, REELS_MARGINS)
        self.assertEqual(
            rect.as_dict(), {"x": 87, "y": 359, "width": 1266, "height": 1305}
        )

    def test_exact_fraction_does_not_round_up_by_float_noise(self):
        pixels = MODULE.margins_in_pixels(
            1000, 1000, {"top": 0.1, "bottom": 0.3, "left": 0.07, "right": 0.0}
        )
        self.assertEqual(pixels, {"top": 100, "bottom": 300, "left": 70, "right": 0})

    def test_zero_margins_keep_the_full_frame(self):
        rect = MODULE.safe_rect(640, 640, dict.fromkeys(MODULE.SIDES, 0.0))
        self.assertEqual(rect.as_dict(), {"x": 0, "y": 0, "width": 640, "height": 640})

    def test_tiny_frame_without_usable_area_is_an_error(self):
        with self.assertRaisesRegex(MODULE.SafeZoneError, "no usable area"):
            MODULE.safe_rect(
                1, 1, {"top": 0.49, "bottom": 0.49, "left": 0.49, "right": 0.49}
            )

    def test_box_overflow_is_reported_per_side(self):
        safe = MODULE.Rect(65, 269, 950, 979)
        box = MODULE.Box("cta", MODULE.Rect(40, 1200, 1000, 100))
        report = MODULE.box_report(box, safe, 1080, 1920)
        self.assertFalse(report["inside"])
        self.assertEqual(
            report["overflow_px"], {"top": 0, "bottom": 52, "left": 25, "right": 25}
        )
        self.assertFalse(report["outside_frame"])

    def test_box_partly_off_frame_is_flagged(self):
        safe = MODULE.Rect(65, 269, 950, 979)
        report = MODULE.box_report(
            MODULE.Box("logo", MODULE.Rect(-10, 300, 100, 50)), safe, 1080, 1920
        )
        self.assertTrue(report["outside_frame"])

    def test_box_parsing_accepts_labels_and_rejects_bad_input(self):
        self.assertEqual(
            MODULE.parse_box("logo=1,2,3,4", 1),
            MODULE.Box("logo", MODULE.Rect(1, 2, 3, 4)),
        )
        self.assertEqual(MODULE.parse_box("1,2,3,4", 7).label, "box-7")
        for text in ("1,2,3", "a,b,c,d", "x=1,2,0,4", "<svg>=1,2,3,4"):
            with self.assertRaises(MODULE.SafeZoneError):
                MODULE.parse_box(text, 1)


class CommandLineTests(unittest.TestCase):
    def test_zones_prints_pixels_for_a_published_placement(self):
        code, stdout, _ = run_cli(
            "zones", "--placement", "meta-instagram-reels", "--size", "1080x1920"
        )
        self.assertEqual(code, 0)
        result = json.loads(stdout)
        self.assertEqual(result["status"], "published")
        self.assertEqual(
            result["safe_rect"], {"x": 65, "y": 269, "width": 950, "height": 979}
        )
        self.assertEqual(result["verified_on"], "2026-10-17")
        self.assertTrue(result["reverify_before_use"])

    def test_zones_defaults_to_the_recommended_resolution(self):
        code, stdout, _ = run_cli("zones", "--placement", "meta-instagram-stories")
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(stdout)["size"], [1440, 2560])

    def test_unpublished_placement_returns_template_guidance_not_numbers(self):
        code, stdout, _ = run_cli(
            "zones", "--placement", "tiktok-in-feed", "--size", "1080x1920"
        )
        self.assertEqual(code, MODULE.EXIT_UNPUBLISHED)
        result = json.loads(stdout)
        self.assertEqual(result["status"], "unpublished")
        self.assertIn("use the platform template", result["message"])
        self.assertNotIn("safe_rect", result)
        self.assertNotIn("margins_px", result)

    def test_mixed_published_and_unpublished_placements_report_unpublished(self):
        code, stdout, _ = run_cli(
            "zones",
            "--placement",
            "meta-instagram-reels",
            "--placement",
            "youtube-shorts",
        )
        self.assertEqual(code, MODULE.EXIT_UNPUBLISHED)
        self.assertEqual(
            [entry["placement"] for entry in json.loads(stdout)["unpublished"]],
            ["youtube-shorts"],
        )

    def test_placements_of_different_ratios_cannot_share_a_cut(self):
        code, _, stderr = run_cli(
            "zones",
            "--placement",
            "meta-instagram-reels",
            "--placement",
            "youtube-bumper",
        )
        self.assertEqual(code, MODULE.EXIT_INVALID)
        self.assertIn("cannot serve both", stderr)

    def test_size_with_a_different_ratio_is_rejected(self):
        code, _, stderr = run_cli(
            "zones", "--placement", "meta-instagram-reels", "--size", "1080x1350"
        )
        self.assertEqual(code, MODULE.EXIT_INVALID)
        self.assertIn("not 9:16", stderr)

    def test_unknown_placement_lists_known_ids(self):
        code, _, stderr = run_cli("zones", "--placement", "billboard")
        self.assertEqual(code, MODULE.EXIT_INVALID)
        self.assertIn("meta-instagram-reels", stderr)

    def test_bad_size_strings_are_rejected(self):
        for size in ("1080", "0x1920", "1080x1920x3", "99999x99999"):
            code, _, _ = run_cli(
                "zones", "--placement", "meta-instagram-reels", "--size", size
            )
            self.assertEqual(code, MODULE.EXIT_INVALID, size)

    def test_check_passes_and_fails_with_exit_codes(self):
        base = ("check", "--placement", "meta-instagram-reels", "--size", "1080x1920")
        code, stdout, _ = run_cli(*base, "--box", "cta=100,1000,800,200")
        self.assertEqual(code, MODULE.EXIT_OK)
        self.assertEqual(json.loads(stdout)["status"], "pass")
        code, stdout, _ = run_cli(
            *base, "--box", "cta=100,1000,800,200", "--box", "logo=20,40,200,80"
        )
        self.assertEqual(code, MODULE.EXIT_VIOLATION)
        result = json.loads(stdout)
        self.assertEqual(result["status"], "fail")
        self.assertEqual(result["violations"], ["logo"])

    def test_check_without_boxes_is_an_error(self):
        code, _, stderr = run_cli(
            "check", "--placement", "meta-instagram-reels", "--size", "1080x1920"
        )
        self.assertEqual(code, MODULE.EXIT_INVALID)
        self.assertIn("--box", stderr)

    def test_platform_file_errors_are_reported(self):
        with tempfile.TemporaryDirectory() as directory:
            broken = Path(directory) / "broken.json"
            broken.write_text("{", encoding="utf-8")
            code, _, stderr = run_cli(
                "--platforms", str(broken), "zones", "--placement", "x"
            )
            self.assertEqual(code, MODULE.EXIT_INVALID)
            self.assertIn("invalid JSON", stderr)
            document = load_contract()
            document["placements"].append(copy.deepcopy(document["placements"][0]))
            duplicate = Path(directory) / "duplicate.json"
            duplicate.write_text(json.dumps(document), encoding="utf-8")
            code, _, stderr = run_cli(
                "--platforms",
                str(duplicate),
                "zones",
                "--placement",
                document["placements"][0]["id"],
            )
            self.assertEqual(code, MODULE.EXIT_INVALID)
            self.assertIn("duplicate", stderr)

    def custom_platforms(self, directory, change):
        document = load_contract()
        placement = next(
            entry
            for entry in document["placements"]
            if entry["id"] == "meta-instagram-reels"
        )
        change(placement)
        path = Path(directory) / "custom.json"
        path.write_text(json.dumps(document), encoding="utf-8")
        return path

    def test_custom_placement_without_aspect_ratio_is_a_clean_error(self):
        with tempfile.TemporaryDirectory() as directory:
            path = self.custom_platforms(
                directory, lambda placement: placement.pop("aspect_ratio")
            )
            code, stdout, stderr = run_cli(
                "--platforms", str(path), "zones", "--placement", "meta-instagram-reels"
            )
        self.assertEqual(code, MODULE.EXIT_INVALID)
        self.assertEqual(stdout, "")
        self.assertIn("aspect_ratio", stderr)
        self.assertIn("does not match the ad-platforms schema", stderr)

    def test_custom_string_resolution_is_named_in_the_error(self):
        with tempfile.TemporaryDirectory() as directory:
            path = self.custom_platforms(
                directory,
                lambda placement: placement.update(recommended_resolution="1080x1920"),
            )
            code, _, stderr = run_cli(
                "--platforms", str(path), "zones", "--placement", "meta-instagram-reels"
            )
        self.assertEqual(code, MODULE.EXIT_INVALID)
        self.assertIn("recommended_resolution", stderr)

    def test_custom_placement_without_a_safe_zone_is_a_clean_error(self):
        with tempfile.TemporaryDirectory() as directory:
            path = self.custom_platforms(
                directory, lambda placement: placement.pop("safe_zone")
            )
            code, _, stderr = run_cli(
                "--platforms", str(path), "zones", "--placement", "meta-instagram-reels"
            )
        self.assertEqual(code, MODULE.EXIT_INVALID)
        self.assertIn("safe_zone", stderr)


class OverlayTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name)

    def overlay(self, *extra, out="qa/reels.svg"):
        with contextlib.chdir(self.directory):
            return run_cli(
                "overlay",
                "--placement",
                "meta-instagram-reels",
                "--size",
                "1080x1920",
                "--out",
                out,
                *extra,
            )

    def test_overlay_is_valid_svg_with_safe_rect_and_boxes(self):
        code, stdout, _ = self.overlay(
            "--box", "cta=100,1000,800,200", "--box", "logo=20,40,200,80"
        )
        self.assertEqual(code, 0)
        path = self.directory / "qa/reels.svg"
        self.assertEqual(json.loads(stdout)["overlay"], str(path.resolve()))
        root = ElementTree.fromstring(path.read_text(encoding="utf-8"))
        self.assertEqual(root.tag, f"{SVG}svg")
        self.assertEqual((root.get("width"), root.get("height")), ("1080", "1920"))
        rects = root.findall(f"{SVG}rect")
        self.assertEqual(
            (
                rects[0].get("x"),
                rects[0].get("y"),
                rects[0].get("width"),
                rects[0].get("height"),
            ),
            ("65", "269", "950", "979"),
        )
        self.assertEqual(len(rects), 3)
        strokes = {rect.get("stroke") for rect in rects[1:]}
        self.assertEqual(strokes, {"#00b0ff", "#ff1744"})
        self.assertEqual(root.find(f"{SVG}path").get("fill-rule"), "evenodd")
        labels = [text.text for text in root.findall(f"{SVG}text")]
        self.assertIn("cta", labels)
        self.assertIn("logo", labels)

    def test_overlay_for_unpublished_placement_writes_nothing(self):
        with contextlib.chdir(self.directory):
            code, stdout, _ = run_cli(
                "overlay",
                "--placement",
                "tiktok-in-feed",
                "--size",
                "1080x1920",
                "--out",
                "tiktok.svg",
            )
        self.assertEqual(code, MODULE.EXIT_UNPUBLISHED)
        self.assertEqual(json.loads(stdout)["status"], "unpublished")
        self.assertFalse((self.directory / "tiktok.svg").exists())

    def test_overlay_refuses_paths_outside_the_working_directory_and_non_svg(self):
        code, _, stderr = self.overlay(out="../escape.svg")
        self.assertEqual(code, MODULE.EXIT_INVALID)
        self.assertIn("must stay inside", stderr)
        code, _, stderr = self.overlay(out="sheet.png")
        self.assertEqual(code, MODULE.EXIT_INVALID)
        self.assertIn(".svg", stderr)

    def test_overlay_does_not_overwrite_without_the_flag(self):
        self.assertEqual(self.overlay()[0], 0)
        code, _, stderr = self.overlay()
        self.assertEqual(code, MODULE.EXIT_INVALID)
        self.assertIn("exists", stderr)
        self.assertEqual(self.overlay("--overwrite")[0], 0)

    def test_overlay_needs_a_size(self):
        arguments = ["overlay", "--placement", "meta-instagram-reels", "--out", "a.svg"]
        with (
            contextlib.chdir(self.directory),
            contextlib.redirect_stderr(io.StringIO()),
            self.assertRaises(SystemExit),
        ):
            MODULE.main(arguments)


if __name__ == "__main__":
    unittest.main()
