from __future__ import annotations

import argparse
import json
import re
import struct
import sys
import zlib
from pathlib import Path
from typing import Any

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
COLOR_TYPES = {2: ("rgb", 3), 6: ("rgba", 4)}
COLOR_TYPE_NAMES = {0: "grayscale", 3: "palette", 4: "grayscale with alpha"}
MAX_PIXELS = 50_000_000
HEX_COLOR = re.compile(r"#?([0-9A-Fa-f]{6})")


class PngError(ValueError):
    pass


def parse_hex(value: str) -> tuple[int, int, int]:
    match = HEX_COLOR.fullmatch(value.strip())
    if not match:
        raise ValueError(f"Target color must be a six-digit hex value: {value!r}")
    digits = match.group(1)
    red, green, blue = (int(digits[index : index + 2], 16) for index in (0, 2, 4))
    return red, green, blue


def read_chunks(content: bytes) -> tuple[tuple[int, ...], bytes]:
    if content[:8] != PNG_SIGNATURE:
        raise PngError("Not a PNG file: signature mismatch")
    position = 8
    header: tuple[int, ...] | None = None
    compressed = bytearray()
    while True:
        if position + 8 > len(content):
            raise PngError("Truncated PNG: missing IEND chunk")
        length = struct.unpack(">I", content[position : position + 4])[0]
        chunk_type = content[position + 4 : position + 8]
        end = position + 12 + length
        if end > len(content):
            raise PngError(f"Truncated PNG: {chunk_type!r} chunk is incomplete")
        data = content[position + 8 : position + 8 + length]
        position = end
        if header is None:
            if chunk_type != b"IHDR" or length != 13:
                raise PngError("Invalid PNG: the first chunk must be a 13-byte IHDR")
            header = struct.unpack(">IIBBBBB", data)
        elif chunk_type == b"IDAT":
            compressed.extend(data)
        elif chunk_type == b"IEND":
            break
    if not compressed:
        raise PngError("Invalid PNG: no IDAT image data")
    return header, bytes(compressed)


def validate_header(header: tuple[int, ...]) -> tuple[int, int, str, int]:
    width, height, bit_depth, color_type, compression, filtering, interlace = header
    if width < 1 or height < 1:
        raise PngError("Invalid PNG: width and height must be positive")
    if width * height > MAX_PIXELS:
        raise PngError(f"PNG exceeds the {MAX_PIXELS}-pixel safety limit")
    if bit_depth != 8:
        raise PngError(
            f"Unsupported PNG bit depth {bit_depth}; convert to 8-bit RGB or RGBA"
        )
    if color_type not in COLOR_TYPES:
        name = COLOR_TYPE_NAMES.get(color_type, f"type {color_type}")
        raise PngError(
            f"Unsupported PNG color type ({name}); convert to 8-bit RGB or RGBA"
        )
    if compression != 0 or filtering != 0:
        raise PngError("Unsupported PNG compression or filter method")
    if interlace != 0:
        raise PngError("Interlaced PNG is not supported; save it non-interlaced")
    mode, channels = COLOR_TYPES[color_type]
    return width, height, mode, channels


def paeth(left: int, above: int, upper_left: int) -> int:
    estimate = left + above - upper_left
    left_distance = abs(estimate - left)
    above_distance = abs(estimate - above)
    upper_left_distance = abs(estimate - upper_left)
    if left_distance <= above_distance and left_distance <= upper_left_distance:
        return left
    if above_distance <= upper_left_distance:
        return above
    return upper_left


def unfilter_row(
    filter_type: int, raw: bytes, previous: bytearray, channels: int
) -> bytearray:
    if filter_type == 0:
        return bytearray(raw)
    if filter_type == 2:
        return bytearray((value + above) & 255 for value, above in zip(raw, previous))
    if filter_type not in (1, 3, 4):
        raise PngError(f"Invalid PNG: unknown row filter type {filter_type}")
    row = bytearray(raw)
    for index in range(len(row)):
        left = row[index - channels] if index >= channels else 0
        if filter_type == 1:
            predictor = left
        elif filter_type == 3:
            predictor = (left + previous[index]) >> 1
        else:
            upper_left = previous[index - channels] if index >= channels else 0
            predictor = paeth(left, previous[index], upper_left)
        row[index] = (row[index] + predictor) & 255
    return row


def decode_png(path: Path) -> tuple[int, int, str, int, list[bytearray]]:
    header, compressed = read_chunks(path.read_bytes())
    width, height, mode, channels = validate_header(header)
    try:
        decoded = zlib.decompress(compressed)
    except zlib.error as error:
        raise PngError(
            f"Invalid PNG: image data does not decompress ({error})"
        ) from error
    stride = width * channels
    if len(decoded) != height * (stride + 1):
        raise PngError("Invalid PNG: image data length does not match the header")
    rows: list[bytearray] = []
    previous = bytearray(stride)
    for offset in range(0, len(decoded), stride + 1):
        row = unfilter_row(
            decoded[offset], decoded[offset + 1 : offset + 1 + stride], previous, channels
        )
        rows.append(row)
        previous = row
    return width, height, mode, channels, rows


def border_columns(width: int, border: int, full_row: bool) -> range | list[int]:
    if full_row or 2 * border >= width:
        return range(width)
    return [*range(border), *range(width - border, width)]


def measure_border(
    rows: list[bytearray],
    width: int,
    channels: int,
    border: int,
    target: tuple[int, int, int],
    tolerance: int,
) -> dict[str, Any]:
    height = len(rows)
    total = matching = transparent = 0
    sums = [0, 0, 0]
    for y, row in enumerate(rows):
        full_row = y < border or y >= height - border
        for x in border_columns(width, border, full_row):
            start = x * channels
            red, green, blue = row[start], row[start + 1], row[start + 2]
            opaque = channels == 3 or row[start + 3] == 255
            total += 1
            sums[0] += red
            sums[1] += green
            sums[2] += blue
            if not opaque:
                transparent += 1
            elif (
                abs(red - target[0]) <= tolerance
                and abs(green - target[1]) <= tolerance
                and abs(blue - target[2]) <= tolerance
            ):
                matching += 1
    return {
        "border_pixels": total,
        "matching_pixels": matching,
        "matching_share": round(matching / total, 6),
        "transparent_pixels": transparent,
        "mean_border_rgb": [round(value / total, 2) for value in sums],
    }


def check(
    path: Path,
    border: int | None,
    tolerance: int,
    min_share: float,
    target: str,
) -> dict[str, Any]:
    if not 0 <= tolerance <= 255:
        raise ValueError("Tolerance must be between 0 and 255")
    if not 0 < min_share <= 1:
        raise ValueError("Minimum share must be greater than 0 and at most 1")
    target_rgb = parse_hex(target)
    if not path.is_file():
        raise ValueError(f"PNG not found: {path}")
    width, height, mode, channels, rows = decode_png(path)
    shorter = min(width, height)
    border_px = border if border is not None else max(1, round(shorter * 0.01))
    if border_px < 1 or border_px > (shorter + 1) // 2:
        raise ValueError(
            f"Border must be between 1 and {(shorter + 1) // 2} pixels for this image"
        )
    stats = measure_border(rows, width, channels, border_px, target_rgb, tolerance)
    return {
        "file": str(path),
        "width": width,
        "height": height,
        "color_type": mode,
        "border_px": border_px,
        "target": "#{:02X}{:02X}{:02X}".format(*target_rgb),
        "tolerance": tolerance,
        **stats,
        "min_share": min_share,
        "passed": stats["matching_share"] >= min_share,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Report the share of border pixels within a tolerance of white "
            "(or another target color) in an 8-bit RGB or RGBA PNG"
        )
    )
    parser.add_argument("png", type=Path)
    parser.add_argument("--border", type=int)
    parser.add_argument("--tolerance", type=int, default=3)
    parser.add_argument("--min-share", type=float, default=0.99)
    parser.add_argument("--target", default="#FFFFFF")
    return parser


def main() -> int:
    arguments = build_parser().parse_args()
    try:
        result = check(
            arguments.png,
            arguments.border,
            arguments.tolerance,
            arguments.min_share,
            arguments.target,
        )
    except (OSError, ValueError) as error:
        print(str(error), file=sys.stderr)
        return 2
    print(json.dumps(result, sort_keys=True))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
