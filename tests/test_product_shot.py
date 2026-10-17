from __future__ import annotations

import importlib.util
import json
import struct
import subprocess
import sys
import tempfile
import unittest
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / ".agents/skills/seedream-product-shot/scripts/white_background_check.py"
SPEC = importlib.util.spec_from_file_location("white_background_check", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)

Pixel = tuple[int, ...]


def chunk(kind: bytes, data: bytes) -> bytes:
    crc = zlib.crc32(kind + data) & 0xFFFFFFFF
    return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", crc)


def paeth(left: int, above: int, upper_left: int) -> int:
    estimate = left + above - upper_left
    distances = (
        abs(estimate - left),
        abs(estimate - above),
        abs(estimate - upper_left),
    )
    if distances[0] <= distances[1] and distances[0] <= distances[2]:
        return left
    if distances[1] <= distances[2]:
        return above
    return upper_left


def filter_row(filter_type: int, row: bytes, previous: bytes, channels: int) -> bytes:
    output = bytearray()
    for index, value in enumerate(row):
        left = row[index - channels] if index >= channels else 0
        above = previous[index]
        upper_left = previous[index - channels] if index >= channels else 0
        predictor = {
            0: 0,
            1: left,
            2: above,
            3: (left + above) // 2,
            4: paeth(left, above, upper_left),
        }[filter_type]
        output.append((value - predictor) & 255)
    return bytes([filter_type]) + bytes(output)


def encode_png(
    pixels: list[list[Pixel]],
    color_type: int = 2,
    bit_depth: int = 8,
    interlace: int = 0,
    filters: tuple[int, ...] = (0,),
) -> bytes:
    height = len(pixels)
    width = len(pixels[0])
    channels = 4 if color_type == 6 else 3
    previous = bytes(width * channels)
    raw = bytearray()
    for y, row_pixels in enumerate(pixels):
        row = bytes(value for pixel in row_pixels for value in pixel)
        raw.extend(filter_row(filters[y % len(filters)], row, previous, channels))
        previous = row
    header = struct.pack(">IIBBBBB", width, height, bit_depth, color_type, 0, 0, interlace)
    return (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", header)
        + chunk(b"IDAT", zlib.compress(bytes(raw)))
        + chunk(b"IEND", b"")
    )


def canvas(width: int, height: int, background: Pixel) -> list[list[Pixel]]:
    return [[background for _ in range(width)] for _ in range(height)]


def paint(
    pixels: list[list[Pixel]], box: tuple[int, int, int, int], color: Pixel
) -> list[list[Pixel]]:
    left, top, right, bottom = box
    for y in range(top, bottom):
        for x in range(left, right):
            pixels[y][x] = color
    return pixels


class WhiteBackgroundCheckTests(unittest.TestCase):
    def setUp(self) -> None:
        directory = tempfile.TemporaryDirectory(prefix="product-shot-test-")
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)

    def write(self, name: str, content: bytes) -> Path:
        path = self.root / name
        path.write_bytes(content)
        return path

    def check(self, path: Path, **values: object) -> dict[str, object]:
        options: dict[str, object] = {
            "border": None,
            "tolerance": 3,
            "min_share": 0.99,
            "target": "#FFFFFF",
        }
        options.update(values)
        return MODULE.check(path, **options)

    def test_white_backdrop_with_centered_dark_product_passes(self) -> None:
        pixels = paint(canvas(40, 30, (255, 255, 255)), (10, 8, 30, 22), (20, 30, 40))
        result = self.check(self.write("pass.png", encode_png(pixels)), border=4)
        self.assertTrue(result["passed"])
        self.assertEqual(result["matching_share"], 1.0)
        self.assertEqual(result["border_pixels"], 40 * 30 - 32 * 22)

    def test_near_white_within_tolerance_passes_and_outside_fails(self) -> None:
        path = self.write("near.png", encode_png(canvas(12, 12, (252, 253, 254))))
        self.assertTrue(self.check(path, tolerance=3)["passed"])
        self.assertFalse(self.check(path, tolerance=2)["passed"])

    def test_light_gray_backdrop_fails_with_mean_color_reported(self) -> None:
        path = self.write("gray.png", encode_png(canvas(16, 16, (236, 236, 236))))
        result = self.check(path)
        self.assertFalse(result["passed"])
        self.assertEqual(result["matching_share"], 0.0)
        self.assertEqual(result["mean_border_rgb"], [236.0, 236.0, 236.0])

    def test_product_touching_the_edge_lowers_the_share_below_threshold(self) -> None:
        pixels = paint(canvas(20, 20, (255, 255, 255)), (0, 5, 20, 15), (90, 10, 10))
        result = self.check(self.write("crop.png", encode_png(pixels)), border=2)
        self.assertFalse(result["passed"])
        self.assertLess(result["matching_share"], 0.99)

    def test_all_png_row_filters_decode_to_the_same_pixels(self) -> None:
        pixels = [
            [((x * 37 + y * 11) % 256, (x * 5) % 256, (y * 29) % 256) for x in range(9)]
            for y in range(10)
        ]
        expected = [bytearray(v for pixel in row for v in pixel) for row in pixels]
        path = self.write("filters.png", encode_png(pixels, filters=(0, 1, 2, 3, 4)))
        width, height, mode, channels, rows = MODULE.decode_png(path)
        self.assertEqual((width, height, mode, channels), (9, 10, "rgb", 3))
        self.assertEqual(rows, expected)

    def test_rgba_transparent_border_is_not_counted_as_white(self) -> None:
        pixels = canvas(10, 10, (255, 255, 255, 0))
        path = self.write("alpha.png", encode_png(pixels, color_type=6, filters=(4,)))
        result = self.check(path)
        self.assertFalse(result["passed"])
        self.assertEqual(result["transparent_pixels"], result["border_pixels"])

    def test_opaque_rgba_white_passes(self) -> None:
        path = self.write(
            "opaque.png", encode_png(canvas(10, 10, (255, 255, 255, 255)), color_type=6)
        )
        self.assertTrue(self.check(path)["passed"])

    def test_brand_color_target_measures_a_colored_backdrop(self) -> None:
        path = self.write("pop.png", encode_png(canvas(12, 12, (215, 40, 30))))
        self.assertTrue(self.check(path, target="#D7281E", tolerance=2)["passed"])
        self.assertFalse(self.check(path)["passed"])

    def test_unsupported_variants_raise_clear_errors(self) -> None:
        cases = [
            ("deep.png", encode_png(canvas(4, 4, (255, 255, 255)), bit_depth=16), "bit depth 16"),
            ("palette.png", encode_png(canvas(4, 4, (255, 255, 255)), color_type=3), "palette"),
            ("gray.png", encode_png(canvas(4, 4, (255, 255, 255)), color_type=0), "grayscale"),
            ("interlaced.png", encode_png(canvas(4, 4, (255, 255, 255)), interlace=1), "Interlaced"),
            ("fake.png", b"GIF89a not a png", "signature"),
            ("short.png", encode_png(canvas(4, 4, (255, 255, 255)))[:40], "Truncated"),
        ]
        for name, content, message in cases:
            with self.subTest(name=name), self.assertRaisesRegex(ValueError, message):
                self.check(self.write(name, content))

    def test_invalid_options_are_rejected(self) -> None:
        path = self.write("ok.png", encode_png(canvas(4, 4, (255, 255, 255))))
        with self.assertRaisesRegex(ValueError, "Border"):
            self.check(path, border=3)
        with self.assertRaisesRegex(ValueError, "hex"):
            self.check(path, target="white")
        with self.assertRaisesRegex(ValueError, "Tolerance"):
            self.check(path, tolerance=300)
        with self.assertRaisesRegex(ValueError, "not found"):
            self.check(self.root / "missing.png")

    def test_command_line_exit_codes_and_json_output(self) -> None:
        passing = self.write("cli-pass.png", encode_png(canvas(8, 8, (255, 255, 255))))
        failing = self.write("cli-fail.png", encode_png(canvas(8, 8, (0, 0, 0))))
        broken = self.write("cli-broken.png", b"not a png")
        results = {
            path.name: subprocess.run(
                [sys.executable, str(SCRIPT), str(path)],
                capture_output=True,
                text=True,
                check=False,
            )
            for path in (passing, failing, broken)
        }
        self.assertEqual(results["cli-pass.png"].returncode, 0)
        self.assertTrue(json.loads(results["cli-pass.png"].stdout)["passed"])
        self.assertEqual(results["cli-fail.png"].returncode, 1)
        self.assertFalse(json.loads(results["cli-fail.png"].stdout)["passed"])
        self.assertEqual(results["cli-broken.png"].returncode, 2)
        self.assertIn("signature", results["cli-broken.png"].stderr)


if __name__ == "__main__":
    unittest.main()
