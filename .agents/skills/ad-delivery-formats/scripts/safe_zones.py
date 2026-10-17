from __future__ import annotations

import argparse
import json
import math
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from xml.sax.saxutils import escape

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[4]
DEFAULT_PLATFORMS = ROOT / ".agents/contracts/ad-platforms.json"
SCHEMA_PATH = ROOT / ".agents/contracts/schemas/ad-platforms.schema.json"
MAX_REPORTED_ERRORS = 5
RATIO_TOLERANCE = 0.01
MAX_SIDE = 16384
SIDES = ("top", "bottom", "left", "right")
SIZE_PATTERN = re.compile(r"^([1-9]\d{0,4})x([1-9]\d{0,4})$")
RATIO_PATTERN = re.compile(r"^([1-9]\d*):([1-9]\d*)$")
LABEL_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9 ._-]{0,39}$")
EXIT_OK = 0
EXIT_VIOLATION = 1
EXIT_INVALID = 2
EXIT_UNPUBLISHED = 3


class SafeZoneError(ValueError):
    pass


@dataclass(frozen=True)
class Rect:
    x: int
    y: int
    width: int
    height: int

    @property
    def right(self) -> int:
        return self.x + self.width

    @property
    def bottom(self) -> int:
        return self.y + self.height

    def as_dict(self) -> dict[str, int]:
        return {"x": self.x, "y": self.y, "width": self.width, "height": self.height}


@dataclass(frozen=True)
class Box:
    label: str
    rect: Rect


@dataclass(frozen=True)
class Resolution:
    ids: list[str]
    aspect_ratio: str
    margins: dict[str, float] | None
    unpublished: list[dict[str, str]]


def schema_errors(document: Any) -> list[str]:
    validator = Draft202012Validator(
        json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    )
    errors = sorted(validator.iter_errors(document), key=lambda item: list(item.path))
    return [
        f"{'/'.join(str(part) for part in error.absolute_path) or '<root>'}: {error.message}"
        for error in errors
    ]


def load_document(path: Path) -> tuple[dict[str, dict[str, Any]], str]:
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise SafeZoneError(f"{path}: invalid JSON: {error}") from error
    errors = schema_errors(document)
    if errors:
        shown = "; ".join(errors[:MAX_REPORTED_ERRORS])
        more = len(errors) - MAX_REPORTED_ERRORS
        suffix = f"; and {more} more" if more > 0 else ""
        raise SafeZoneError(
            f"{path}: does not match the ad-platforms schema: {shown}{suffix}"
        )
    placements: dict[str, dict[str, Any]] = {}
    for entry in document["placements"]:
        if entry["id"] in placements:
            raise SafeZoneError(f"{path}: duplicate placement id {entry['id']}")
        placements[entry["id"]] = entry
    return placements, str(document.get("verified_on", ""))


def parse_ratio(text: str) -> float:
    match = RATIO_PATTERN.match(text)
    if not match:
        raise SafeZoneError(f"invalid aspect ratio {text!r}")
    return int(match[1]) / int(match[2])


def parse_size(text: str) -> tuple[int, int]:
    match = SIZE_PATTERN.match(text)
    if not match:
        raise SafeZoneError(f"size must look like 1080x1920, got {text!r}")
    width, height = int(match[1]), int(match[2])
    if width > MAX_SIDE or height > MAX_SIDE:
        raise SafeZoneError(f"size {text} exceeds {MAX_SIDE} px per side")
    return width, height


def parse_box(text: str, index: int) -> Box:
    label, separator, numbers = text.rpartition("=")
    if not separator:
        label, numbers = f"box-{index}", text
    if not LABEL_PATTERN.match(label):
        raise SafeZoneError(f"invalid box label {label!r}")
    parts = numbers.split(",")
    if len(parts) != 4 or not all(
        re.fullmatch(r"-?\d+", part.strip()) for part in parts
    ):
        raise SafeZoneError(
            f"box must be [label=]x,y,w,h in integer pixels, got {text!r}"
        )
    x, y, width, height = (int(part) for part in parts)
    if width <= 0 or height <= 0:
        raise SafeZoneError(f"box {label} needs a positive width and height")
    return Box(label, Rect(x, y, width, height))


def safe_zone_margins(placement: dict[str, Any]) -> dict[str, float] | None:
    zone = placement.get("safe_zone")
    if not isinstance(zone, dict):
        raise SafeZoneError(f"{placement['id']}: safe_zone must be an object")
    values = [zone.get(side) for side in SIDES]
    if all(value is None for value in values):
        return None
    if not all(
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and 0 <= value < 0.5
        for value in values
    ):
        raise SafeZoneError(
            f"{placement['id']}: safe-zone sides must all be fractions in [0, 0.5) or all null"
        )
    return {side: float(zone[side]) for side in SIDES}


def resolve(placements: dict[str, dict[str, Any]], ids: list[str]) -> Resolution:
    unknown = [identifier for identifier in ids if identifier not in placements]
    if unknown:
        raise SafeZoneError(
            f"unknown placement {unknown[0]!r}; known: {', '.join(sorted(placements))}"
        )
    chosen = [placements[identifier] for identifier in dict.fromkeys(ids)]
    ratio_text = chosen[0]["aspect_ratio"]
    ratio = parse_ratio(ratio_text)
    for placement in chosen[1:]:
        other = parse_ratio(placement["aspect_ratio"])
        if abs(other - ratio) / ratio > RATIO_TOLERANCE:
            raise SafeZoneError(
                f"{placement['id']} is {placement['aspect_ratio']} but {chosen[0]['id']} is "
                f"{ratio_text}; one cut cannot serve both"
            )
    margins: dict[str, float] = {side: 0.0 for side in SIDES}
    unpublished: list[dict[str, str]] = []
    for placement in chosen:
        placement_margins = safe_zone_margins(placement)
        if placement_margins is None:
            unpublished.append(
                {
                    "placement": placement["id"],
                    "source": placement["safe_zone"].get("source", ""),
                }
            )
            continue
        for side in SIDES:
            margins[side] = max(margins[side], placement_margins[side])
    return Resolution(
        [placement["id"] for placement in chosen],
        ratio_text,
        None if unpublished else margins,
        unpublished,
    )


def frame_size(
    placements: dict[str, dict[str, Any]], resolution: Resolution, size_text: str | None
) -> tuple[int, int]:
    if size_text is None:
        for identifier in resolution.ids:
            recommended = placements[identifier].get("recommended_resolution")
            if recommended:
                return int(recommended[0]), int(recommended[1])
        raise SafeZoneError(
            f"{', '.join(resolution.ids)} publish no recommended resolution; pass --size WxH"
        )
    width, height = parse_size(size_text)
    expected = parse_ratio(resolution.aspect_ratio)
    if abs(width / height - expected) / expected > RATIO_TOLERANCE:
        raise SafeZoneError(
            f"size {width}x{height} is not {resolution.aspect_ratio} within "
            f"{RATIO_TOLERANCE:.0%}; render the placement ratio instead of stretching"
        )
    return width, height


def margins_in_pixels(
    width: int, height: int, margins: dict[str, float]
) -> dict[str, int]:
    return {
        "top": math.ceil(round(margins["top"] * height, 6)),
        "bottom": math.ceil(round(margins["bottom"] * height, 6)),
        "left": math.ceil(round(margins["left"] * width, 6)),
        "right": math.ceil(round(margins["right"] * width, 6)),
    }


def safe_rect(width: int, height: int, margins: dict[str, float]) -> Rect:
    pixels = margins_in_pixels(width, height, margins)
    inner_width = width - pixels["left"] - pixels["right"]
    inner_height = height - pixels["top"] - pixels["bottom"]
    if inner_width <= 0 or inner_height <= 0:
        raise SafeZoneError("safe zone leaves no usable area")
    return Rect(pixels["left"], pixels["top"], inner_width, inner_height)


def box_report(box: Box, safe: Rect, width: int, height: int) -> dict[str, Any]:
    overflow = {
        "top": max(0, safe.y - box.rect.y),
        "bottom": max(0, box.rect.bottom - safe.bottom),
        "left": max(0, safe.x - box.rect.x),
        "right": max(0, box.rect.right - safe.right),
    }
    outside_frame = (
        box.rect.x < 0
        or box.rect.y < 0
        or box.rect.right > width
        or box.rect.bottom > height
    )
    return {
        "label": box.label,
        "box": box.rect.as_dict(),
        "inside": not any(overflow.values()),
        "overflow_px": overflow,
        "outside_frame": outside_frame,
    }


def overlay_svg(
    width: int, height: int, safe: Rect, boxes: list[Box], title: str
) -> str:
    stroke = max(2, round(min(width, height) / 270))
    font = max(14, round(min(width, height) / 40))
    unsafe = (
        f"M0 0H{width}V{height}H0Z "
        f"M{safe.x} {safe.y}V{safe.bottom}H{safe.right}V{safe.y}Z"
    )
    header = (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}">'
    )
    outline = (
        f'<rect x="{safe.x}" y="{safe.y}" width="{safe.width}" height="{safe.height}" '
        f'fill="none" stroke="#00e676" stroke-width="{stroke}" '
        f'stroke-dasharray="{stroke * 4} {stroke * 3}"/>'
    )
    caption = (
        f'<text x="{safe.x + stroke * 2}" y="{min(height - stroke, safe.bottom + font + stroke * 2)}" fill="#00e676" '
        f'font-family="sans-serif" font-size="{font}">{escape(title)}</text>'
    )
    parts = [
        header,
        f"<title>{escape(title)}</title>",
        f'<path d="{unsafe}" fill="#ff2d55" fill-opacity="0.35" fill-rule="evenodd"/>',
        outline,
        caption,
    ]
    for box in boxes:
        inside = box_report(box, safe, width, height)["inside"]
        color = "#00b0ff" if inside else "#ff1744"
        parts.append(
            f'<rect x="{box.rect.x}" y="{box.rect.y}" width="{box.rect.width}" '
            f'height="{box.rect.height}" fill="none" stroke="{color}" stroke-width="{stroke}"/>'
        )
        parts.append(
            f'<text x="{box.rect.x + stroke}" y="{box.rect.y - stroke}" fill="{color}" '
            f'font-family="sans-serif" font-size="{font}">{escape(box.label)}</text>'
        )
    parts.append("</svg>")
    return "\n".join(parts) + "\n"


def unpublished_result(resolution: Resolution) -> dict[str, Any]:
    names = ", ".join(entry["placement"] for entry in resolution.unpublished)
    return {
        "status": "unpublished",
        "placements": resolution.ids,
        "unpublished": resolution.unpublished,
        "message": (
            f"Safe zone unpublished for {names}: use the platform template; "
            "no margins are invented"
        ),
    }


def published_result(
    resolution: Resolution,
    margins: dict[str, float],
    size: tuple[int, int],
    verified_on: str,
) -> tuple[dict[str, Any], Rect]:
    width, height = size
    safe = safe_rect(width, height, margins)
    return {
        "status": "published",
        "placements": resolution.ids,
        "aspect_ratio": resolution.aspect_ratio,
        "size": [width, height],
        "margins_fraction": margins,
        "margins_px": margins_in_pixels(width, height, margins),
        "safe_rect": safe.as_dict(),
        "verified_on": verified_on,
        "reverify_before_use": True,
    }, safe


def output_path(text: str) -> Path:
    path = Path(text)
    if path.suffix != ".svg":
        raise SafeZoneError("overlay output must end in .svg")
    base = Path.cwd().resolve()
    target = (base / path).resolve()
    if not target.is_relative_to(base):
        raise SafeZoneError(f"overlay output {text} must stay inside {base}")
    return target


def run(arguments: argparse.Namespace) -> tuple[dict[str, Any], int]:
    placements, verified_on = load_document(Path(arguments.platforms))
    resolution = resolve(placements, arguments.placement)
    boxes = [
        parse_box(text, index)
        for index, text in enumerate(getattr(arguments, "box", None) or [], 1)
    ]
    if resolution.margins is None:
        return unpublished_result(resolution), EXIT_UNPUBLISHED
    width, height = frame_size(placements, resolution, arguments.size)
    result, safe = published_result(
        resolution, resolution.margins, (width, height), verified_on
    )
    if arguments.command == "check":
        if not boxes:
            raise SafeZoneError("check needs at least one --box")
        reports = [box_report(box, safe, width, height) for box in boxes]
        violations = [report["label"] for report in reports if not report["inside"]]
        result.update(
            status="pass" if not violations else "fail",
            boxes=reports,
            violations=violations,
        )
        return result, EXIT_OK if not violations else EXIT_VIOLATION
    if arguments.command == "overlay":
        target = output_path(arguments.out)
        if target.exists() and not arguments.overwrite:
            raise SafeZoneError(
                f"{arguments.out} exists; pass --overwrite or choose a new path"
            )
        title = f"{' + '.join(resolution.ids)} safe zone {width}x{height}"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(
            overlay_svg(width, height, safe, boxes, title), encoding="utf-8"
        )
        result["overlay"] = str(target)
    return result, EXIT_OK


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Safe-zone rectangles, checks and SVG overlays from ad-platforms.json"
    )
    parser.add_argument("--platforms", default=str(DEFAULT_PLATFORMS))
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("zones", "check", "overlay"):
        command = commands.add_parser(name)
        command.add_argument("--placement", action="append", required=True)
        command.add_argument("--size", required=name == "overlay")
        if name != "zones":
            command.add_argument(
                "--box", action="append", default=[], metavar="[LABEL=]X,Y,W,H"
            )
        if name == "overlay":
            command.add_argument("--out", required=True)
            command.add_argument("--overwrite", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    try:
        result, code = run(build_parser().parse_args(argv))
    except (OSError, SafeZoneError) as error:
        print(f"error: {error}", file=sys.stderr)
        return EXIT_INVALID
    print(json.dumps(result, indent=2, sort_keys=True))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
