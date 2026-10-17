from __future__ import annotations

import argparse
import hashlib
import html
import json
import math
import re
import sys
import unicodedata
from dataclasses import dataclass, replace
from itertools import pairwise
from pathlib import Path
from typing import Any

SCHEMA_VERSION = 1
DEFAULT_MAX_CHARS = 32
DEFAULT_MAX_CPS = 17.0
LANGUAGE_DEFAULTS = {
    "zh": (16, 9.0),
    "ja": (13, 7.0),
    "ko": (16, 12.0),
}
RTL_LANGUAGES = {"ar", "he", "fa", "ur", "ps", "sd", "ug", "yi", "dv", "ckb"}
RTL_SCRIPTS = {"arab", "hebr", "thaa", "syrc", "nkoo"}
RIGHT_TO_LEFT_MARK = "\u200f"
ZERO_WIDTH_SPACE = "\u200b"
ZERO_WIDTH_JOINER = "\u200d"
ZERO_WIDTH_NON_JOINER = "\u200c"
LANGUAGE_PATTERN = re.compile(r"^[A-Za-z]{2,3}(-[A-Za-z0-9]{2,8})*$")
STEM_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
NO_LINE_START = set("、。，．！？：；）］｝】」』》〉”’ー々ゝゞ,.!?:;)]}%…‥")
NO_LINE_END = set("（［｛【「『《〈“‘([{")
UNBROKEN_PAIRS = set("…—‥─")
CLAUSE_END = set(".!?…。！？؟;:,，、؛،")
IDEOGRAPHIC_RANGES = (
    (0x3000, 0x30FF),
    (0x3400, 0x4DBF),
    (0x4E00, 0x9FFF),
    (0xF900, 0xFAFF),
    (0xFF00, 0xFFEF),
    (0x20000, 0x2FFFF),
)
FORMATS = ("srt", "vtt")
DEFAULT_PLATFORMS = (
    Path(__file__).resolve().parents[4] / ".agents/contracts/ad-platforms.json"
)
SAFE_SIDES = ("top", "bottom", "left", "right")
RATIO_TOLERANCE = 0.01
MAX_SIDE = 16384
SIZE_PATTERN = re.compile(r"^([1-9]\d{0,4})x([1-9]\d{0,4})$")
RECT_PATTERN = re.compile(r"^(\d{1,5}),(\d{1,5}),([1-9]\d{0,4}),([1-9]\d{0,4})$")
RATIO_PATTERN = re.compile(r"^([1-9]\d*):([1-9]\d*)$")
COLOR_PATTERN = re.compile(r"^#[0-9A-Fa-f]{6}(?:[0-9A-Fa-f]{2})?$")
FONT_FAMILY_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9 _-]{0,63}$")
FONT_SRC_PATTERN = re.compile(
    r"^(?!/)(?!.*\.\.)[A-Za-z0-9._/-]+\.(?:woff2|woff|ttf|otf)$"
)
COMPOSITION_ID_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
WIDE_FACTOR = 1.0
NARROW_FACTOR = 0.55
LINE_HEIGHT = 1.25
DEFAULT_FONT_SHARE = 0.045
HORIZONTAL_PADDING_EM = 0.8


class CaptionError(ValueError):
    pass


@dataclass(frozen=True)
class Line:
    line_id: str
    speaker: str
    start_ms: int
    end_ms: int
    text: dict[str, str]


@dataclass(frozen=True)
class Settings:
    max_chars: int
    max_lines: int
    min_duration_ms: int
    max_duration_ms: int
    max_cps: float
    min_gap_ms: int


@dataclass(frozen=True)
class Layout:
    width: int
    height: int
    x: int
    y: int
    safe_width: int
    safe_height: int


@dataclass(frozen=True)
class Typography:
    family: str
    src: str | None
    size_px: int
    color: str
    box_color: str
    anchor: str


@dataclass(frozen=True)
class Token:
    text: str
    glue: str
    width: int


@dataclass(frozen=True)
class Cue:
    start_ms: int
    end_ms: int
    lines: tuple[str, ...]
    source_id: str = ""

    @property
    def characters(self) -> int:
        return sum(
            len(grapheme_clusters(line.replace(RIGHT_TO_LEFT_MARK, "")))
            for line in self.lines
        )


def seconds_to_ms(value: Any, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise CaptionError(f"{label} must be a number of seconds")
    if not math.isfinite(value):
        raise CaptionError(f"{label} must be finite")
    return round(value * 1000)


def base_language(language: str) -> str:
    return language.lower().split("-")[0]


def normalize_language(language: str) -> str:
    if not LANGUAGE_PATTERN.match(language):
        raise CaptionError(f"invalid language code {language!r}")
    return language.lower()


def is_right_to_left(language: str) -> bool:
    parts = language.lower().split("-")
    return parts[0] in RTL_LANGUAGES or any(part in RTL_SCRIPTS for part in parts[1:])


def extends_cluster(cluster: str, char: str) -> bool:
    code = ord(char)
    if unicodedata.category(char) in {"Mn", "Mc", "Me"}:
        return True
    if char in (ZERO_WIDTH_JOINER, ZERO_WIDTH_NON_JOINER):
        return True
    if (
        0x1F3FB <= code <= 0x1F3FF
        or 0x1160 <= code <= 0x11FF
        or 0xD7B0 <= code <= 0xD7FF
    ):
        return True
    last = cluster[-1]
    if last == ZERO_WIDTH_JOINER or unicodedata.combining(last) == 9:
        return True
    regional = 0x1F1E6 <= code <= 0x1F1FF
    return regional and len(cluster) == 1 and 0x1F1E6 <= ord(last) <= 0x1F1FF


def grapheme_clusters(text: str) -> list[str]:
    clusters: list[str] = []
    for char in text:
        if clusters and extends_cluster(clusters[-1], char):
            clusters[-1] += char
        else:
            clusters.append(char)
    return clusters


def is_ideographic(cluster: str) -> bool:
    code = ord(cluster[0])
    return any(low <= code <= high for low, high in IDEOGRAPHIC_RANGES)


def may_break_between(previous: str, current: str) -> bool:
    if not (is_ideographic(previous) or is_ideographic(current)):
        return False
    if current[0] in NO_LINE_START or previous[0] in NO_LINE_END:
        return False
    return not (previous[0] == current[0] and current[0] in UNBROKEN_PAIRS)


def split_word(word: str) -> list[str]:
    clusters = grapheme_clusters(word)
    pieces = [clusters[0]]
    for previous, current in pairwise(clusters):
        if may_break_between(previous, current):
            pieces.append(current)
        else:
            pieces[-1] += current
    return pieces


def tokenize(text: str) -> list[Token]:
    tokens: list[Token] = []
    for index, word in enumerate(text.split()):
        for part_index, part in enumerate(word.split(ZERO_WIDTH_SPACE)):
            if not part:
                continue
            for piece_index, piece in enumerate(split_word(part)):
                glue = " " if index and not part_index and not piece_index else ""
                tokens.append(Token(piece, glue, len(grapheme_clusters(piece))))
    if tokens:
        tokens[0] = Token(tokens[0].text, "", tokens[0].width)
    return tokens


def split_oversize_tokens(
    tokens: list[Token], max_chars: int
) -> tuple[list[Token], int]:
    result: list[Token] = []
    split_count = 0
    for token in tokens:
        if token.width <= max_chars:
            result.append(token)
            continue
        split_count += 1
        clusters = grapheme_clusters(token.text)
        for offset in range(0, len(clusters), max_chars):
            piece = "".join(clusters[offset : offset + max_chars])
            glue = token.glue if offset == 0 else ""
            result.append(Token(piece, glue, len(grapheme_clusters(piece))))
    return result, split_count


def span_width(tokens: list[Token], start: int, stop: int) -> int:
    width = sum(token.width for token in tokens[start:stop])
    return width + sum(len(token.glue) for token in tokens[start + 1 : stop])


def lines_needed(tokens: list[Token], max_chars: int) -> int:
    count = 1
    width = 0
    for token in tokens:
        if width == 0:
            width = token.width
            continue
        candidate = width + len(token.glue) + token.width
        if candidate > max_chars:
            count += 1
            width = token.width
        else:
            width = candidate
    return count


def wrap_tokens(
    tokens: list[Token], max_chars: int, max_lines: int
) -> list[str] | None:
    total = len(tokens)
    needed = lines_needed(tokens, max_chars)
    if needed > max_lines:
        return None
    memo: dict[tuple[int, int], tuple[float, tuple[int, ...]]] = {}

    def best(start: int, lines_left: int) -> tuple[float, tuple[int, ...]]:
        key = (start, lines_left)
        if key in memo:
            return memo[key]
        outcome: tuple[float, tuple[int, ...]] = (math.inf, ())
        if lines_left == 1:
            width = span_width(tokens, start, total)
            if width <= max_chars:
                outcome = (float((max_chars - width) ** 2), (total,))
        else:
            for stop in range(start + 1, total):
                width = span_width(tokens, start, stop)
                if width > max_chars:
                    break
                rest_cost, rest_stops = best(stop, lines_left - 1)
                cost = (max_chars - width) ** 2 + rest_cost
                if cost < outcome[0]:
                    outcome = (cost, (stop, *rest_stops))
        memo[key] = outcome
        return outcome

    _, stops = best(0, needed)
    lines: list[str] = []
    start = 0
    for stop in stops:
        lines.append(
            "".join(token.glue + token.text for token in tokens[start:stop]).strip()
        )
        start = stop
    return lines


def prefer_clause_boundary(tokens: list[Token], start: int, stop: int) -> int:
    full = span_width(tokens, start, stop)
    for candidate in range(stop, start, -1):
        if span_width(tokens, start, candidate) * 2 < full:
            break
        if tokens[candidate - 1].text[-1] in CLAUSE_END:
            return candidate
    return stop


def capacity_chunks(tokens: list[Token], settings: Settings) -> list[list[Token]]:
    chunks: list[list[Token]] = []
    start = 0
    while start < len(tokens):
        stop = start + 1
        while (
            stop < len(tokens)
            and lines_needed(tokens[start : stop + 1], settings.max_chars)
            <= settings.max_lines
        ):
            stop += 1
        if stop < len(tokens):
            stop = prefer_clause_boundary(tokens, start, stop)
        chunks.append(tokens[start:stop])
        start = stop
    return chunks


def split_by_weight(tokens: list[Token], parts: int) -> list[list[Token]]:
    parts = max(1, min(parts, len(tokens)))
    total = span_width(tokens, 0, len(tokens))
    groups: list[list[Token]] = []
    start = 0
    for part in range(1, parts):
        target = total * part / parts
        stop = start + 1
        limit = len(tokens) - (parts - part)
        while stop < limit and span_width(tokens, 0, stop) < target:
            stop += 1
        groups.append(tokens[start:stop])
        start = stop
    groups.append(tokens[start:])
    return groups


def allocate_times(
    chunks: list[list[Token]], start_ms: int, end_ms: int
) -> list[tuple[int, int, list[Token]]]:
    weights = [span_width(chunk, 0, len(chunk)) for chunk in chunks]
    total_weight = sum(weights)
    span = end_ms - start_ms
    allocated: list[tuple[int, int, list[Token]]] = []
    cumulative = 0
    chunk_start = start_ms
    for chunk, weight in zip(chunks, weights):
        cumulative += weight
        chunk_end = start_ms + round(span * cumulative / total_weight)
        allocated.append((chunk_start, chunk_end, chunk))
        chunk_start = chunk_end
    return allocated


def cues_for_line(
    line: Line, language: str, settings: Settings, rtl_marks: bool
) -> tuple[list[Cue], list[str]]:
    warnings: list[str] = []
    tokens, split_count = split_oversize_tokens(
        tokenize(line.text[language]), settings.max_chars
    )
    if split_count:
        warnings.append(
            f"{line.line_id} [{language}]: {split_count} unbroken run(s) longer than "
            f"{settings.max_chars} characters were split; add spaces or U+200B at word boundaries"
        )
    if not tokens:
        raise CaptionError(f"line {line.line_id} has no {language} text")
    cues: list[Cue] = []
    for chunk_start, chunk_end, chunk in allocate_times(
        capacity_chunks(tokens, settings), line.start_ms, line.end_ms
    ):
        duration = chunk_end - chunk_start
        parts = math.ceil(duration / settings.max_duration_ms)
        groups = split_by_weight(chunk, parts) if parts > 1 else [chunk]
        for group_start, group_end, group in allocate_times(
            groups, chunk_start, chunk_end
        ):
            rendered = wrap_tokens(group, settings.max_chars, settings.max_lines)
            if rendered is None:
                raise CaptionError(
                    f"{line.line_id} [{language}]: text cannot be wrapped"
                )
            if rtl_marks:
                rendered = [RIGHT_TO_LEFT_MARK + text for text in rendered]
            group_end = min(group_end, group_start + settings.max_duration_ms)
            cues.append(Cue(group_start, group_end, tuple(rendered), line.line_id))
    return cues, warnings


def resolve_overlaps(
    cues: list[Cue], settings: Settings, policy: str, warnings: list[str]
) -> list[Cue]:
    ordered = sorted(cues, key=lambda cue: (cue.start_ms, cue.end_ms))
    for index in range(len(ordered) - 1):
        current, following = ordered[index], ordered[index + 1]
        overlapping = current.end_ms > following.start_ms
        crowded = current.end_ms > following.start_ms - settings.min_gap_ms
        same_line = current.source_id == following.source_id
        if not crowded or (same_line and not overlapping):
            continue
        if overlapping and policy == "error":
            raise CaptionError(
                f"cues overlap: {current.source_id} ends at {current.end_ms} ms but "
                f"{following.source_id} starts at {following.start_ms} ms"
            )
        new_end = following.start_ms - settings.min_gap_ms
        if new_end <= current.start_ms:
            if overlapping:
                raise CaptionError(
                    f"cannot trim {current.source_id}: {following.source_id} starts at "
                    f"{following.start_ms} ms, too close to its start {current.start_ms} ms"
                )
            continue
        if overlapping:
            warnings.append(
                f"{current.source_id} trimmed to {new_end} ms to clear {following.source_id}"
            )
        ordered[index] = replace(current, end_ms=new_end)
    return ordered


def extend_for_reading(
    cues: list[Cue], settings: Settings, ceiling_ms: int | None, warnings: list[str]
) -> list[Cue]:
    result: list[Cue] = []
    for index, cue in enumerate(cues):
        wanted = max(
            settings.min_duration_ms,
            math.ceil(cue.characters * 1000 / settings.max_cps),
        )
        wanted = min(wanted, settings.max_duration_ms)
        limit = (
            cues[index + 1].start_ms - settings.min_gap_ms
            if index + 1 < len(cues)
            else ceiling_ms
        )
        new_end = cue.start_ms + wanted
        if limit is not None:
            new_end = min(new_end, limit)
        if new_end > cue.end_ms:
            cue = replace(cue, end_ms=new_end)
        duration = cue.end_ms - cue.start_ms
        if duration < settings.min_duration_ms:
            warnings.append(
                f"{cue.source_id}: cue lasts {duration} ms, below the {settings.min_duration_ms} ms minimum"
            )
        if cue.characters * 1000 > settings.max_cps * duration:
            warnings.append(
                f"{cue.source_id}: reading speed {cue.characters * 1000 / duration:.1f} cps "
                f"exceeds {settings.max_cps:g}"
            )
        result.append(cue)
    return result


def build_cues(
    lines: list[Line],
    language: str,
    settings: Settings,
    *,
    overlap: str = "trim",
    master_duration_ms: int | None = None,
    rtl_marks: bool | None = None,
) -> tuple[list[Cue], list[str]]:
    language = normalize_language(language)
    use_marks = is_right_to_left(language) if rtl_marks is None else rtl_marks
    for line in lines:
        if not line.text.get(language, "").strip():
            raise CaptionError(
                f"line {line.line_id} ({line.speaker}) has no {language} text"
            )
    warnings: list[str] = []
    cues: list[Cue] = []
    for line in lines:
        line_cues, line_warnings = cues_for_line(line, language, settings, use_marks)
        cues.extend(line_cues)
        warnings.extend(line_warnings)
    cues = resolve_overlaps(cues, settings, overlap, warnings)
    cues = extend_for_reading(cues, settings, master_duration_ms, warnings)
    if master_duration_ms is not None:
        late = [cue for cue in cues if cue.end_ms > master_duration_ms]
        if late:
            raise CaptionError(
                f"{late[0].source_id} ends at {late[0].end_ms} ms, after the master "
                f"duration {master_duration_ms} ms"
            )
    return cues, warnings


def format_timestamp(milliseconds: int, separator: str) -> str:
    hours, remainder = divmod(milliseconds, 3_600_000)
    minutes, remainder = divmod(remainder, 60_000)
    seconds, millis = divmod(remainder, 1000)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}{separator}{millis:03d}"


def render_srt(cues: list[Cue]) -> str:
    blocks = []
    for number, cue in enumerate(cues, 1):
        start = format_timestamp(cue.start_ms, ",")
        end = format_timestamp(cue.end_ms, ",")
        blocks.append(f"{number}\n{start} --> {end}\n" + "\n".join(cue.lines))
    return "\n\n".join(blocks) + "\n"


def escape_vtt(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def render_vtt(cues: list[Cue]) -> str:
    blocks = []
    for cue in cues:
        start = format_timestamp(cue.start_ms, ".")
        end = format_timestamp(cue.end_ms, ".")
        body = "\n".join(escape_vtt(text) for text in cue.lines)
        blocks.append(f"{start} --> {end}\n{body}")
    return "WEBVTT\n\n" + "\n\n".join(blocks) + "\n"


def parse_line(entry: Any, index: int, offset_ms: int, source: str) -> Line:
    if not isinstance(entry, dict):
        raise CaptionError(f"{source}: lines[{index}] must be an object")
    line_id = str(entry.get("id") or f"line-{index + 1:03d}")
    label = f"{source}: {line_id}"
    speaker = entry.get("speaker", "voice")
    if not isinstance(speaker, str) or not speaker.strip():
        raise CaptionError(f"{label} speaker must be a nonempty string when given")
    start_ms = seconds_to_ms(entry.get("start_s"), f"{label} start_s") + offset_ms
    end_ms = seconds_to_ms(entry.get("end_s"), f"{label} end_s") + offset_ms
    if start_ms < 0:
        raise CaptionError(f"{label} starts before zero after the offset")
    if end_ms <= start_ms:
        raise CaptionError(f"{label} must end after it starts")
    raw_text = entry.get("text")
    if not isinstance(raw_text, dict) or not raw_text:
        raise CaptionError(f"{label} needs a text object keyed by language code")
    text: dict[str, str] = {}
    for key, value in raw_text.items():
        if not isinstance(value, str):
            raise CaptionError(f"{label} text for {key!r} must be a string")
        text[normalize_language(key)] = value.strip()
    return Line(line_id, speaker.strip(), start_ms, end_ms, text)


def load_lines(path: Path, extra_offset_ms: int = 0) -> list[Line]:
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise CaptionError(f"{path}: invalid JSON: {error}") from error
    if (
        not isinstance(document, dict)
        or document.get("schema_version") != SCHEMA_VERSION
    ):
        raise CaptionError(
            f"{path}: expected an object with schema_version {SCHEMA_VERSION}"
        )
    entries = document.get("lines")
    if not isinstance(entries, list) or not entries:
        raise CaptionError(f"{path}: lines must be a nonempty list")
    offset_ms = extra_offset_ms + seconds_to_ms(
        document.get("offset_s", 0), f"{path} offset_s"
    )
    return [
        parse_line(entry, index, offset_ms, path.name)
        for index, entry in enumerate(entries)
    ]


def resolve_settings(
    language: str,
    *,
    max_chars: int | None = None,
    max_lines: int = 2,
    min_duration_s: float = 1.0,
    max_duration_s: float = 7.0,
    max_cps: float | None = None,
    min_gap_s: float = 0.04,
    chars_for: dict[str, int] | None = None,
    cps_for: dict[str, float] | None = None,
) -> Settings:
    language = normalize_language(language)
    default_chars, default_cps = LANGUAGE_DEFAULTS.get(
        base_language(language), (DEFAULT_MAX_CHARS, DEFAULT_MAX_CPS)
    )
    chars_for = chars_for or {}
    cps_for = cps_for or {}
    chars = chars_for.get(language, chars_for.get(base_language(language)))
    cps = cps_for.get(language, cps_for.get(base_language(language)))
    resolved = Settings(
        max_chars=chars or max_chars or default_chars,
        max_lines=max_lines,
        min_duration_ms=seconds_to_ms(min_duration_s, "min duration"),
        max_duration_ms=seconds_to_ms(max_duration_s, "max duration"),
        max_cps=cps or max_cps or default_cps,
        min_gap_ms=seconds_to_ms(min_gap_s, "min gap"),
    )
    if resolved.max_chars < 1 or resolved.max_lines < 1 or resolved.max_cps <= 0:
        raise CaptionError("max chars, max lines and max cps must be positive")
    if not 0 < resolved.min_duration_ms <= resolved.max_duration_ms:
        raise CaptionError("durations must satisfy 0 < min <= max")
    return resolved


def parse_overrides(values: list[str], cast: type) -> dict[str, Any]:
    overrides: dict[str, Any] = {}
    for value in values:
        language, separator, amount = value.partition("=")
        if not separator:
            raise CaptionError(f"expected LANG=NUMBER, got {value!r}")
        try:
            overrides[normalize_language(language)] = cast(amount)
        except ValueError as error:
            raise CaptionError(f"expected LANG=NUMBER, got {value!r}") from error
    return overrides


def write_sidecar(path: Path, content: str, overwrite: bool) -> str:
    if path.exists() and not overwrite:
        raise CaptionError(f"{path} exists; pass --overwrite or choose a new --out-dir")
    path.write_text(content, encoding="utf-8")
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def parse_size(text: str) -> tuple[int, int]:
    match = SIZE_PATTERN.match(text)
    if not match:
        raise CaptionError(f"size must look like 1080x1920, got {text!r}")
    width, height = int(match[1]), int(match[2])
    if width > MAX_SIDE or height > MAX_SIDE:
        raise CaptionError(f"size {text} exceeds {MAX_SIDE} px per side")
    return width, height


def parse_ratio(text: Any) -> float:
    match = RATIO_PATTERN.match(text) if isinstance(text, str) else None
    if not match:
        raise CaptionError(f"invalid aspect ratio {text!r}")
    return int(match[1]) / int(match[2])


def placement_safe_rect(
    platforms: Path, placement_id: str, width: int, height: int
) -> tuple[int, int, int, int]:
    try:
        document = json.loads(platforms.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise CaptionError(f"{platforms}: invalid JSON: {error}") from error
    entries = document.get("placements") if isinstance(document, dict) else None
    if not isinstance(entries, list):
        raise CaptionError(f"{platforms}: placements must be a list")
    placement = next(
        (
            entry
            for entry in entries
            if isinstance(entry, dict) and entry.get("id") == placement_id
        ),
        None,
    )
    if placement is None:
        raise CaptionError(f"unknown placement {placement_id!r}")
    expected = parse_ratio(placement.get("aspect_ratio"))
    if abs(width / height - expected) / expected > RATIO_TOLERANCE:
        raise CaptionError(
            f"size {width}x{height} does not match {placement_id} {placement['aspect_ratio']}"
        )
    zone = placement.get("safe_zone") or {}
    values = [zone.get(side) for side in SAFE_SIDES]
    margins = [
        float(value)
        for value in values
        if isinstance(value, (int, float)) and not isinstance(value, bool)
    ]
    if len(margins) != len(SAFE_SIDES):
        raise CaptionError(
            f"safe zone for {placement_id} is unpublished; measure the platform template "
            "and pass --safe-rect X,Y,W,H"
        )
    top, bottom, left, right = (
        math.ceil(round(fraction * side, 6))
        for fraction, side in zip(margins, (height, height, width, width))
    )
    return left, top, width - left - right, height - top - bottom


def resolve_layout(
    size: str | None,
    placement: str | None,
    safe_rect: str | None,
    platforms: Path,
) -> Layout:
    if size is None:
        raise CaptionError("burn-in needs --size WxH")
    width, height = parse_size(size)
    if safe_rect is not None:
        match = RECT_PATTERN.match(safe_rect)
        if not match:
            raise CaptionError(
                f"safe rect must be X,Y,W,H in pixels, got {safe_rect!r}"
            )
        x, y, rect_width, rect_height = (int(value) for value in match.groups())
    elif placement is not None:
        x, y, rect_width, rect_height = placement_safe_rect(
            platforms, placement, width, height
        )
    else:
        raise CaptionError("burn-in needs --placement or --safe-rect")
    if (
        rect_width <= 0
        or rect_height <= 0
        or x + rect_width > width
        or y + rect_height > height
    ):
        raise CaptionError("safe rect must lie inside the frame")
    return Layout(width, height, x, y, rect_width, rect_height)


def resolve_typography(arguments: argparse.Namespace, layout: Layout) -> Typography:
    if not FONT_FAMILY_PATTERN.match(arguments.font_family):
        raise CaptionError(f"invalid font family {arguments.font_family!r}")
    if arguments.font_src is not None and not FONT_SRC_PATTERN.match(
        arguments.font_src
    ):
        raise CaptionError(
            "font source must be a relative woff2, woff, ttf or otf path inside the Studio project"
        )
    for color in (arguments.text_color, arguments.box_color):
        if not COLOR_PATTERN.match(color):
            raise CaptionError(f"color must be #RRGGBB or #RRGGBBAA, got {color!r}")
    size_px = arguments.font_size or round(
        min(layout.width, layout.height) * DEFAULT_FONT_SHARE
    )
    if size_px < 8:
        raise CaptionError("font size must be at least 8 px")
    return Typography(
        arguments.font_family,
        arguments.font_src,
        size_px,
        arguments.text_color,
        arguments.box_color,
        arguments.anchor,
    )


def estimated_width(text: str, size_px: int) -> float:
    clusters = grapheme_clusters(text.replace(RIGHT_TO_LEFT_MARK, ""))
    glyphs = sum(
        size_px * (WIDE_FACTOR if is_ideographic(cluster) else NARROW_FACTOR)
        for cluster in clusters
    )
    return glyphs + size_px * HORIZONTAL_PADDING_EM


def layout_warnings(
    cues: list[Cue], layout: Layout, typography: Typography
) -> list[str]:
    warnings: list[str] = []
    block_limit = layout.safe_height
    for cue in cues:
        widest = max(estimated_width(line, typography.size_px) for line in cue.lines)
        if widest > layout.safe_width:
            warnings.append(
                f"{cue.source_id}: estimated line width {widest:.0f} px exceeds the safe width "
                f"{layout.safe_width} px; shorten the line limit or the font size"
            )
        block = len(cue.lines) * typography.size_px * LINE_HEIGHT
        if block > block_limit:
            warnings.append(
                f"{cue.source_id}: caption block {block:.0f} px exceeds the safe height {block_limit} px"
            )
    return warnings


def seconds_text(milliseconds: int) -> str:
    return f"{milliseconds / 1000:.3f}".rstrip("0").rstrip(".")


def render_composition(
    cues: list[Cue],
    language: str,
    composition_id: str,
    layout: Layout,
    typography: Typography,
) -> str:
    direction = "rtl" if is_right_to_left(language) else "ltr"
    vertical = (
        f"bottom: {layout.height - layout.y - layout.safe_height}px;"
        if typography.anchor == "bottom"
        else f"top: {layout.y}px;"
    )
    font_face = (
        f'      @font-face {{ font-family: "{typography.family}"; src: url("{typography.src}"); }}\n'
        if typography.src
        else ""
    )
    blocks = []
    for index, cue in enumerate(cues, 1):
        body = "<br>".join(html.escape(line, quote=False) for line in cue.lines)
        blocks.append(
            f'        <div id="{composition_id}-c{index:03d}" class="cue" '
            f'data-start="{seconds_text(cue.start_ms)}" '
            f'data-duration="{seconds_text(cue.end_ms - cue.start_ms)}" '
            f'lang="{language}" dir="{direction}"><span>{body}</span></div>'
        )
    return f"""<!doctype html>
<html>
  <head><meta charset="UTF-8" /></head>
  <body>
    <template>
      <style>
{font_face}      #root {{ position: absolute; inset: 0; }}
      .cue {{ position: absolute; left: {layout.x}px; width: {layout.safe_width}px; {vertical} display: flex; justify-content: center; text-align: center; }}
      .cue span {{ font-family: "{typography.family}", sans-serif; font-size: {typography.size_px}px; line-height: {LINE_HEIGHT}; color: {typography.color}; background: {typography.box_color}; padding: 0.12em 0.4em; border-radius: 0.2em; -webkit-box-decoration-break: clone; box-decoration-break: clone; }}
      </style>
      <div id="root" data-composition-id="{composition_id}" data-width="{layout.width}" data-height="{layout.height}">
{chr(10).join(blocks)}
      </div>
      <script>
        window.__timelines = window.__timelines || {{}};
        window.__timelines["{composition_id}"] = gsap.timeline({{ paused: true }});
      </script>
    </template>
  </body>
</html>
"""


def host_snippet(composition_id: str, layout: Layout, duration_ms: int) -> str:
    return (
        f'<div id="{composition_id}" data-composition-id="{composition_id}" '
        f'data-composition-src="compositions/{composition_id}.html" data-start="0" '
        f'data-duration="{seconds_text(duration_ms)}" data-track-kind="graphics" '
        f'data-width="{layout.width}" data-height="{layout.height}"></div>'
    )


def plan_outputs(
    arguments: argparse.Namespace, lines: list[Line], master_ms: int | None
) -> tuple[list[tuple[str, list[Cue]]], list[str]]:
    chars_for = parse_overrides(arguments.max_chars_for, int)
    cps_for = parse_overrides(arguments.max_cps_for, float)
    rtl_marks = {"auto": None, "on": True, "off": False}[arguments.rtl_marks]
    planned: list[tuple[str, list[Cue]]] = []
    warnings: list[str] = []
    for language in arguments.language:
        code = normalize_language(language)
        settings = resolve_settings(
            code,
            max_chars=arguments.max_chars,
            max_lines=arguments.max_lines,
            min_duration_s=arguments.min_duration_s,
            max_duration_s=arguments.max_duration_s,
            max_cps=arguments.max_cps,
            min_gap_s=arguments.min_gap_s,
            chars_for=chars_for,
            cps_for=cps_for,
        )
        cues, language_warnings = build_cues(
            lines,
            code,
            settings,
            overlap=arguments.overlap,
            master_duration_ms=master_ms,
            rtl_marks=rtl_marks,
        )
        warnings.extend(f"[{code}] {warning}" for warning in language_warnings)
        planned.append((code, cues))
    return planned, warnings


def composition_id_for(prefix: str, code: str) -> str:
    identifier = f"{prefix}-{code}"
    if not COMPOSITION_ID_PATTERN.match(identifier):
        raise CaptionError(f"invalid composition id {identifier!r}")
    return identifier


def file_entry(
    path: Path, language: str, kind: str, cues: int, digest: str
) -> dict[str, Any]:
    return {
        "path": str(path),
        "language": language,
        "format": kind,
        "cues": cues,
        "sha256": digest,
    }


def generate(arguments: argparse.Namespace) -> dict[str, Any]:
    if not STEM_PATTERN.match(arguments.master_stem):
        raise CaptionError(f"invalid master stem {arguments.master_stem!r}")
    offset_ms = seconds_to_ms(arguments.offset_s, "offset")
    lines = [
        line for path in arguments.input for line in load_lines(Path(path), offset_ms)
    ]
    master_ms = (
        None
        if arguments.master_duration_s is None
        else seconds_to_ms(arguments.master_duration_s, "master duration")
    )
    burn_in = arguments.composition_dir is not None
    layout = typography = None
    if burn_in:
        layout = resolve_layout(
            arguments.size,
            arguments.placement,
            arguments.safe_rect,
            Path(arguments.platforms),
        )
        typography = resolve_typography(arguments, layout)
    planned, warnings = plan_outputs(arguments, lines, master_ms)
    formats = FORMATS if arguments.format == "both" else (arguments.format,)
    outputs: list[tuple[Path, str, str, str, int]] = []
    hosts: list[str] = []
    out_dir = Path(arguments.out_dir)
    for code, cues in planned:
        for extension in formats:
            content = render_srt(cues) if extension == "srt" else render_vtt(cues)
            target = out_dir / f"{arguments.master_stem}.{code}.{extension}"
            outputs.append((target, content, code, extension, len(cues)))
        if layout is None or typography is None:
            continue
        identifier = composition_id_for(arguments.composition_prefix, code)
        warnings.extend(
            f"[{code}] {warning}"
            for warning in layout_warnings(cues, layout, typography)
        )
        content = render_composition(cues, code, identifier, layout, typography)
        target = Path(arguments.composition_dir) / f"{identifier}.html"
        outputs.append((target, content, code, "hyperframes", len(cues)))
        duration_ms = (
            master_ms if master_ms is not None else max(cue.end_ms for cue in cues)
        )
        hosts.append(host_snippet(identifier, layout, duration_ms))
    for target, _, _, _, _ in outputs:
        if target.exists() and not arguments.overwrite:
            raise CaptionError(
                f"{target} exists; pass --overwrite or choose a new --out-dir"
            )
    files: list[dict[str, Any]] = []
    for target, content, code, kind, count in outputs:
        target.parent.mkdir(parents=True, exist_ok=True)
        digest = write_sidecar(target, content, arguments.overwrite)
        files.append(file_entry(target, code, kind, count, digest))
    result: dict[str, Any] = {"files": files, "warnings": warnings}
    if layout is not None:
        result["safe_rect"] = {
            "x": layout.x,
            "y": layout.y,
            "width": layout.safe_width,
            "height": layout.safe_height,
        }
        result["host_snippets"] = hosts
    return result


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Write per-language SRT/WebVTT captions and optional HyperFrames burn-in layers"
    )
    parser.add_argument(
        "--input", action="append", required=True, help="script timing JSON; repeatable"
    )
    parser.add_argument("--master-stem", required=True)
    parser.add_argument("--language", nargs="+", required=True)
    parser.add_argument("--out-dir", default=".")
    parser.add_argument("--format", choices=["srt", "vtt", "both"], default="srt")
    parser.add_argument("--offset-s", type=float, default=0.0)
    parser.add_argument("--master-duration-s", type=float)
    parser.add_argument("--max-chars", type=int)
    parser.add_argument("--max-lines", type=int, default=2)
    parser.add_argument("--min-duration-s", type=float, default=1.0)
    parser.add_argument("--max-duration-s", type=float, default=7.0)
    parser.add_argument("--max-cps", type=float)
    parser.add_argument("--min-gap-s", type=float, default=0.04)
    parser.add_argument(
        "--max-chars-for", action="append", default=[], metavar="LANG=N"
    )
    parser.add_argument("--max-cps-for", action="append", default=[], metavar="LANG=N")
    parser.add_argument("--overlap", choices=["trim", "error"], default="trim")
    parser.add_argument("--rtl-marks", choices=["auto", "on", "off"], default="auto")
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--composition-dir")
    parser.add_argument("--composition-prefix", default="captions")
    parser.add_argument("--size", metavar="WxH")
    parser.add_argument("--placement")
    parser.add_argument("--safe-rect", metavar="X,Y,W,H")
    parser.add_argument("--platforms", default=str(DEFAULT_PLATFORMS))
    parser.add_argument("--font-family", default="Inter")
    parser.add_argument("--font-src")
    parser.add_argument("--font-size", type=int)
    parser.add_argument("--text-color", default="#FFFFFF")
    parser.add_argument("--box-color", default="#000000B3")
    parser.add_argument("--anchor", choices=["bottom", "top"], default="bottom")
    return parser


def main(argv: list[str] | None = None) -> int:
    try:
        result = generate(build_parser().parse_args(argv))
    except (OSError, CaptionError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
