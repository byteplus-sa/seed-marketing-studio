from __future__ import annotations

import argparse
import hashlib
import html
import json
import math
import os
import re
import shlex
import sys
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any
from urllib.parse import quote

SKILL_ROOT = Path(__file__).resolve().parents[1]
TEMPLATES = SKILL_ROOT / "assets" / "templates"
REPOSITORY_ROOT = Path(__file__).resolve().parents[4]
RENDERER = REPOSITORY_ROOT / ".agents/skills/html-graphic-render/scripts/render_html.py"
LAYOUTS = (
    "hero-product",
    "problem-solution",
    "comparison",
    "social-proof",
    "offer",
)
RATIOS = {
    "1:1": ("1x1", 1080, 1080),
    "4:5": ("4x5", 1080, 1350),
    "9:16": ("9x16", 1080, 1920),
    "16:9": ("16x9", 1920, 1080),
}
ANGLE_TYPES = (
    "demonstration",
    "objection-handling",
    "discovery",
    "experience",
    "quantified-comparison",
)
REQUIRED_PALETTE_ROLES = ("primary", "background", "text")
REQUIRED_TYPOGRAPHY_ROLES = ("headline", "body")
FONT_FORMATS = {".woff2": "woff2", ".woff": "woff", ".ttf": "truetype", ".otf": "opentype"}
IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp", ".svg"}
KEBAB = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")
HEX_COLOR = re.compile(r"#[0-9A-Fa-f]{6}")
LANGUAGE_TAG = re.compile(r"[A-Za-z]{2,3}(?:-[A-Za-z0-9]{2,8})*")
PLACEHOLDER = re.compile(r"\{\{([a-z_]+)\}\}")
CONTROL_CHARACTERS = re.compile(r"[\x00-\x1f\x7f]")
MAX_COPY_LENGTH = 240
MAX_CLAIMS = 3
MAX_COMPARISON_ROWS = 4
CONTACT_ROWS_PER_PAGE = 12
CONTACT_TILE = 360
CONTACT_GAP = 24
DEFAULT_PERISHABLE_MAX_AGE_HOURS = 24
TRADEMARK_MARKS = ("®", "™", "℠")
REQUIRED_LINE_CONDITIONS: dict[str, tuple[str, ...]] = {
    "always": LAYOUTS,
    "offer shown": ("offer",),
    "price shown": ("offer",),
    "discount shown": ("offer",),
    "promotion shown": ("offer",),
    "comparison shown": ("comparison",),
    "review shown": ("social-proof",),
    "rating shown": ("social-proof",),
    "testimonial shown": ("social-proof",),
}
WHITESPACE = re.compile(r"\s+")
CLOCK_SKEW = timedelta(minutes=5)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def fill_template(
    template: str, values: Mapping[str, str], raw: Mapping[str, str] | None = None
) -> str:
    trusted = raw or {}

    def replace(match: re.Match[str]) -> str:
        key = match.group(1)
        if key in trusted:
            return trusted[key]
        if key in values:
            return html.escape(values[key], quote=True)
        raise ValueError(f"Template placeholder {{{{{key}}}}} has no value")

    return PLACEHOLDER.sub(replace, template)


def require_text(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} must be a non-empty string")
    if CONTROL_CHARACTERS.search(value):
        raise ValueError(f"{label} must be one line without control characters")
    if len(value) > MAX_COPY_LENGTH:
        raise ValueError(f"{label} exceeds {MAX_COPY_LENGTH} characters")
    return value


def require_id(value: Any, label: str) -> str:
    if not isinstance(value, str) or not KEBAB.fullmatch(value):
        raise ValueError(f"{label} must be lowercase kebab-case: {value!r}")
    return value


def load_json(path: Path, label: str) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as error:
        raise ValueError(f"{label} not found: {path}") from error
    except json.JSONDecodeError as error:
        raise ValueError(f"{label} is not valid JSON: {error}") from error


def contained_file(
    root: Path, base: Path, value: Any, label: str, suffixes: set[str] | None = None
) -> Path:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} path is missing")
    candidate = (base / value).resolve()
    if not candidate.is_relative_to(root):
        raise ValueError(f"{label} escapes the asset root: {value}")
    if not candidate.is_file():
        raise ValueError(f"{label} not found: {value}")
    if suffixes is not None and candidate.suffix.lower() not in suffixes:
        raise ValueError(f"{label} has an unsupported file type: {value}")
    return candidate


def canonical_sha256(document: dict[str, Any]) -> str:
    payload = json.dumps(document, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def verify_recorded_hash(path: Path, expected: Any, label: str) -> str:
    if not isinstance(expected, str) or not expected:
        raise ValueError(f"{label} has no recorded SHA-256 in the brand kit")
    actual = sha256(path)
    if expected != actual:
        raise ValueError(f"{label} SHA-256 differs from the brand kit record")
    return actual


def require_license(entry: dict[str, Any], label: str) -> None:
    value = entry.get("license")
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} has no recorded license in the brand kit")


def font_alias(role: str) -> str:
    return f"brand-{role}"


def entries_by_role(entries: Any, label: str) -> dict[str, dict[str, Any]]:
    if not isinstance(entries, list):
        raise TypeError(f"Brand kit {label} must be a list")
    result: dict[str, dict[str, Any]] = {}
    for entry in entries:
        if isinstance(entry, dict) and isinstance(entry.get("role"), str):
            result.setdefault(entry["role"], entry)
    return result


def condition_key(when: str) -> str:
    return WHITESPACE.sub(" ", when).strip().rstrip(".").lower()


def required_lines(value: Any) -> list[dict[str, str]]:
    if not isinstance(value, list):
        raise TypeError("Brand kit copy_rules.required_lines must be a list")
    lines: list[dict[str, str]] = []
    for index, entry in enumerate(value, 1):
        if not isinstance(entry, dict):
            raise TypeError(f"Brand kit required line {index} must be an object")
        text = require_text(entry.get("text"), f"Brand kit required line {index} text")
        when = require_text(entry.get("when"), f"Brand kit required line {index} when")
        lines.append({"text": text, "when": when})
    return lines


def trademark_marks(value: Any) -> dict[str, str]:
    if not isinstance(value, dict):
        raise TypeError("Brand kit copy_rules.trademark_marks must be an object")
    marks: dict[str, str] = {}
    for name, mark in value.items():
        require_text(name, "Brand kit trademark name")
        if mark not in TRADEMARK_MARKS:
            raise ValueError(
                f"Brand kit trademark mark for {name!r} must be one of "
                f"{', '.join(TRADEMARK_MARKS)}: {mark!r}"
            )
        marks[name] = mark
    return marks


def load_brand(root: Path, spec: dict[str, Any]) -> dict[str, Any]:
    path = contained_file(root, root, spec.get("brand_kit"), "Brand kit", {".json"})
    kit = load_json(path, "Brand kit")
    if not isinstance(kit, dict):
        raise TypeError("Brand kit must be a JSON object")
    kit_hash = canonical_sha256(kit)
    pinned = spec.get("brand_kit_sha256")
    if not isinstance(pinned, str) or not pinned:
        raise ValueError(
            "Spec brand_kit_sha256 is required; record the campaign pin from brand_kit.py pin"
        )
    if pinned != kit_hash:
        raise ValueError("Brand kit SHA-256 differs from the campaign pin")
    if kit.get("status") != "approved":
        raise ValueError("Brand kit status must be approved before a static batch")
    missing: list[str] = []
    palette = entries_by_role(kit.get("palette", []), "palette")
    colors: dict[str, str] = {}
    for role in (*REQUIRED_PALETTE_ROLES, "accent"):
        value = palette.get(role, {}).get("hex")
        if isinstance(value, str) and HEX_COLOR.fullmatch(value):
            colors[role] = value.upper()
        elif role in REQUIRED_PALETTE_ROLES:
            missing.append(f"palette.{role}")
    typography = entries_by_role(kit.get("typography", []), "typography")
    fonts: dict[str, dict[str, Any]] = {}
    for role in (*REQUIRED_TYPOGRAPHY_ROLES, "cta"):
        entry = typography.get(role)
        if entry is None or not entry.get("family") or not entry.get("file"):
            if role in REQUIRED_TYPOGRAPHY_ROLES:
                missing.append(f"typography.{role}")
            continue
        family = require_text(entry["family"], f"Font family for {role}")
        font_path = contained_file(
            root, path.parent, entry["file"], f"Font for {role}", set(FONT_FORMATS)
        )
        require_license(entry, f"Font {role}")
        weight = entry.get("weight")
        fonts[role] = {
            "family": family,
            "alias": font_alias(role),
            "weight": weight if isinstance(weight, int) and not isinstance(weight, bool) else None,
            "path": str(font_path),
            "sha256": verify_recorded_hash(font_path, entry.get("sha256"), f"Font {role}"),
        }
    logo_entry = entries_by_role(kit.get("logos", []), "logos").get("primary") or {}
    if not logo_entry.get("file"):
        missing.append("logos.primary")
    if missing:
        raise ValueError("Brand kit is missing required tokens: " + ", ".join(missing))
    logo_path = contained_file(
        root, path.parent, logo_entry["file"], "Primary logo", IMAGE_SUFFIXES
    )
    name = require_text(kit.get("name"), "Brand name")
    copy_rules = kit.get("copy_rules") or {}
    cta_style = kit.get("cta_style") or {}
    return {
        "path": path,
        "sha256": kit_hash,
        "brand_id": kit.get("brand_id"),
        "name": name,
        "colors": colors,
        "fonts": fonts,
        "logo": {
            "path": str(logo_path),
            "sha256": verify_recorded_hash(logo_path, logo_entry.get("sha256"), "Logo"),
        },
        "banned_words": [
            word for word in copy_rules.get("banned_words", []) if isinstance(word, str)
        ],
        "cta_verbs": [
            verb for verb in cta_style.get("verbs", []) if isinstance(verb, str)
        ],
        "required_lines": required_lines(copy_rules.get("required_lines", [])),
        "trademark_marks": trademark_marks(copy_rules.get("trademark_marks", {})),
    }


def load_facts(root: Path, spec: dict[str, Any]) -> dict[str, Any]:
    path = contained_file(root, root, spec.get("facts"), "Product facts", {".json"})
    document = load_json(path, "Product facts")
    entries = document.get("facts") if isinstance(document, dict) else document
    if not isinstance(entries, list):
        raise TypeError("Product facts must be a list or an object with a facts list")
    facts = [entry for entry in entries if isinstance(entry, dict)]
    return {"path": path, "sha256": sha256(path), "facts": facts}


def parse_time(value: Any) -> datetime | None:
    if not isinstance(value, str):
        return None
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError:
        return None
    return parsed if parsed.tzinfo else None


@dataclass(frozen=True)
class Freshness:
    now: datetime
    max_age_hours: float


def check_fresh(fact: dict[str, Any], reference: str, freshness: Freshness) -> None:
    retrieved = parse_time(fact.get("retrieved_at"))
    if retrieved is None:
        raise ValueError(
            f"Perishable claim {reference!r} needs a retrieved_at time with a UTC offset"
        )
    if retrieved > freshness.now + CLOCK_SKEW:
        raise ValueError(f"Perishable claim {reference!r} has a retrieved_at in the future")
    if freshness.now - retrieved > timedelta(hours=freshness.max_age_hours):
        raise ValueError(
            f"Perishable claim {reference!r} is stale: retrieved {fact.get('retrieved_at')}, "
            f"older than {freshness.max_age_hours:g} hours; re-verify it and update facts.json"
        )


QUALIFIERS = (
    ("up to", re.compile(r"\bup to\b", re.IGNORECASE)),
    ("as low as", re.compile(r"\bas low as\b", re.IGNORECASE)),
    ("from", re.compile(r"\bfrom\s+[^\w\s]?\d", re.IGNORECASE)),
    ("starting at", re.compile(r"\bstarting at\b", re.IGNORECASE)),
    ("may", re.compile(r"\bmay\b", re.IGNORECASE)),
    ("approximately", re.compile(r"\bapproximately\b", re.IGNORECASE)),
)


def check_qualifiers(fact: dict[str, Any], reference: str) -> None:
    claim = fact.get("claim")
    quote = fact.get("quote")
    if not isinstance(claim, str) or not isinstance(quote, str):
        return
    for label, pattern in QUALIFIERS:
        if pattern.search(quote) and not pattern.search(claim):
            raise ValueError(
                f"Claim {reference!r} drops {label!r} from its quote; "
                "keep the qualifier in the claim (facts.claim_qualifier)"
            )


def resolve_claim(
    reference: Any,
    facts: list[dict[str, Any]],
    freshness: Freshness | None = None,
) -> dict[str, Any]:
    if not isinstance(reference, str) or not reference.strip():
        raise ValueError("Claim references must be non-empty strings")
    for fact in facts:
        if reference in (fact.get("fact_id"), fact.get("claim")):
            status = fact.get("status")
            if status == "perishable" and freshness is not None:
                check_fresh(fact, reference, freshness)
            elif status != "supported":
                exception = ", plus fresh perishable offers" if freshness else ""
                raise ValueError(
                    f"Claim {reference!r} has status {status!r}; "
                    f"only supported claims may appear in an ad{exception}"
                )
            check_qualifiers(fact, reference)
            return {
                "ref": reference,
                "claim": require_text(fact.get("claim"), f"Claim {reference!r}"),
                "status": status,
                "source_url": fact.get("source_url"),
                "retrieved_at": fact.get("retrieved_at"),
            }
    raise ValueError(f"Claim {reference!r} is not in the product facts")


def resolve_claims(angle: dict[str, Any], facts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    references = angle.get("claims")
    if not isinstance(references, list) or not 1 <= len(references) <= MAX_CLAIMS:
        raise ValueError(
            f"Angle {angle['id']!r} needs 1-{MAX_CLAIMS} claim references for this layout"
        )
    return [resolve_claim(reference, facts) for reference in references]


def numbered_keys(copy: Mapping[str, str], prefix: str, suffix: str = "") -> list[str]:
    pattern = re.compile(rf"{prefix}_(\d+){suffix}")
    numbered = [
        (int(match.group(1)), key) for key in copy if (match := pattern.fullmatch(key))
    ]
    return [key for _, key in sorted(numbered)]


def copy_node(tag: str, css_class: str | None, key: str, copy: Mapping[str, str]) -> str:
    attribute = f' class="{css_class}"' if css_class else ""
    return (
        f'<{tag}{attribute} data-copy-key="{key}">'
        f"{html.escape(copy[key], quote=True)}</{tag}>"
    )


def copy_markup(copy: Mapping[str, str]) -> dict[str, str]:
    rows = []
    for key in numbered_keys(copy, "row", "_attribute"):
        index = key.split("_")[1]
        rows.append(
            "<tr>"
            + copy_node("th", None, f"row_{index}_attribute", copy)
            + copy_node("td", "ours", f"row_{index}_ours", copy)
            + copy_node("td", None, f"row_{index}_alternative", copy)
            + "</tr>"
        )
    return {
        "claims": "".join(
            copy_node("li", "claim", key, copy) for key in numbered_keys(copy, "claim")
        ),
        "rows": "".join(rows),
        "terms": copy_node("p", "terms", "terms", copy) if "terms" in copy else "",
        "legal": "".join(
            copy_node("p", "legal", key, copy) for key in numbered_keys(copy, "legal")
        ),
    }


def layout_content(
    layout: str, angle: dict[str, Any], facts: list[dict[str, Any]], freshness: Freshness
) -> tuple[dict[str, str], list[dict[str, Any]]]:
    label = f"Angle {angle['id']!r}"
    copy = {
        "headline": require_text(angle.get("headline"), f"{label} headline"),
        "cta": require_text(angle.get("cta"), f"{label} cta"),
    }
    claims: list[dict[str, Any]] = []
    if layout in ("hero-product", "problem-solution"):
        claims = resolve_claims(angle, facts)
        copy.update({f"claim_{i}": c["claim"] for i, c in enumerate(claims, 1)})
        if layout == "problem-solution":
            copy["problem"] = require_text(angle.get("problem"), f"{label} problem")
    elif layout == "comparison":
        comparison = angle.get("comparison")
        if not isinstance(comparison, dict):
            raise ValueError(f"{label} needs a comparison block for this layout")
        rows = comparison.get("rows")
        if not isinstance(rows, list) or not 1 <= len(rows) <= MAX_COMPARISON_ROWS:
            raise ValueError(f"{label} comparison needs 1-{MAX_COMPARISON_ROWS} rows")
        copy["ours_label"] = require_text(comparison.get("ours_label"), f"{label} ours_label")
        copy["alternative_label"] = require_text(
            comparison.get("alternative_label"), f"{label} alternative_label"
        )
        for index, row in enumerate(rows, 1):
            if not isinstance(row, dict):
                raise TypeError(f"{label} comparison row {index} must be an object")
            attribute = require_text(row.get("attribute"), f"{label} row {index} attribute")
            ours = resolve_claim(row.get("ours"), facts)
            alternative = resolve_claim(row.get("alternative"), facts)
            claims.extend([ours, alternative])
            copy[f"row_{index}_attribute"] = attribute
            copy[f"row_{index}_ours"] = ours["claim"]
            copy[f"row_{index}_alternative"] = alternative["claim"]
    elif layout == "social-proof":
        proof = resolve_claim(angle.get("proof"), facts)
        claims.append(proof)
        copy["proof"] = proof["claim"]
    elif layout == "offer":
        offer = resolve_claim(angle.get("offer"), facts, freshness)
        claims.append(offer)
        copy["offer"] = offer["claim"]
        terms = angle.get("terms")
        if terms is not None:
            copy["terms"] = require_text(terms, f"{label} terms")
    return copy, claims


def mark_order(copy: Mapping[str, str]) -> list[str]:
    trailing = ("cta", "terms")
    middle = [key for key in copy if key != "headline" and key not in trailing]
    return [key for key in ("headline", *middle, *trailing) if key in copy]


def apply_trademarks(
    copy: dict[str, str], marks: Mapping[str, str]
) -> list[dict[str, str]]:
    applied: list[dict[str, str]] = []
    for name in sorted(marks, key=lambda item: (-len(item), item)):
        mark = marks[name]
        pattern = re.compile(rf"(?<!\w){re.escape(name)}(?!\w)")
        for key in mark_order(copy):
            match = pattern.search(copy[key])
            if match is None:
                continue
            text = copy[key]
            if not text[match.end() :].startswith(TRADEMARK_MARKS):
                copy[key] = text[: match.end()] + mark + text[match.end() :]
                applied.append({"key": key, "name": name, "mark": mark})
            break
    return applied


def unmapped_conditions(lines: list[dict[str, str]]) -> list[str]:
    return [
        f"Required line {line['text']!r} has condition {line['when']!r} that the planner "
        "cannot map to a layout; decide whether it applies and add it in post or as "
        "offer terms"
        for line in lines
        if condition_key(line["when"]) not in REQUIRED_LINE_CONDITIONS
    ]


def add_required_lines(
    copy: dict[str, str], lines: list[dict[str, str]], layout: str
) -> list[dict[str, str]]:
    placed: list[dict[str, str]] = []
    for line in lines:
        if layout not in REQUIRED_LINE_CONDITIONS.get(condition_key(line["when"]), ()):
            continue
        if copy.get("terms") == line["text"]:
            placed.append({"key": "terms", **line})
            continue
        if any(entry["text"] == line["text"] for entry in placed):
            continue
        key = f"legal_{len(numbered_keys(copy, 'legal')) + 1}"
        copy[key] = line["text"]
        placed.append({"key": key, **line})
    return placed


def check_banned_words(copy: Mapping[str, str], banned: list[str], name: str) -> None:
    for word in banned:
        pattern = re.compile(rf"(?<!\w){re.escape(word)}(?:e?s)?(?!\w)", re.IGNORECASE)
        for key, text in copy.items():
            if pattern.search(text):
                raise ValueError(f"{name}: {key} uses the banned word {word!r}")


def relative_url(target: Path, directory: Path) -> str:
    relative = Path(os.path.relpath(target, directory)).as_posix()
    if "\\" in relative or CONTROL_CHARACTERS.search(relative):
        raise ValueError(f"Unsupported character in asset path: {relative}")
    return quote(relative, safe="/")


def display_path(path: Path) -> str:
    if path.is_relative_to(REPOSITORY_ROOT):
        return path.relative_to(REPOSITORY_ROOT).as_posix()
    return str(path)


def stylesheet(brand: dict[str, Any], output_dir: Path) -> str:
    fonts = brand["fonts"]
    faces = []
    for role in sorted(fonts):
        entry = fonts[role]
        font = Path(entry["path"])
        weight = "" if entry["weight"] is None else f"  font-weight: {entry['weight']};\n"
        faces.append(
            "@font-face {\n"
            f"  font-family: '{entry['alias']}';\n"
            f"{weight}"
            f"  src: url('{relative_url(font, output_dir)}') "
            f"format('{FONT_FORMATS[font.suffix.lower()]}');\n"
            "  font-display: block;\n"
            "}"
        )
    colors = brand["colors"]
    template = (TEMPLATES / "static-ad.css").read_text(encoding="utf-8")
    return fill_template(
        template,
        {},
        {
            "font_faces": "\n".join(faces),
            "color_primary": colors["primary"],
            "color_accent": colors.get("accent", colors["primary"]),
            "color_background": colors["background"],
            "color_text": colors["text"],
            "font_headline": fonts["headline"]["alias"],
            "font_body": fonts["body"]["alias"],
            "font_cta": fonts.get("cta", fonts["body"])["alias"],
        },
    )


def render_command(
    html_path: Path,
    png_path: Path,
    root: Path,
    width: int,
    height: int,
    copy: Mapping[str, str],
    font_family: str | None,
) -> list[str]:
    command = [
        "uv",
        "run",
        "python",
        display_path(RENDERER),
        display_path(html_path),
        display_path(png_path),
        "--asset-root",
        display_path(root),
        "--width",
        str(width),
        "--height",
        str(height),
    ]
    if font_family:
        command.extend(["--require-local-font", font_family])
    for key, text in copy.items():
        command.extend(["--copy", f"{key}={text}"])
    return command


def angle_layouts(angle: dict[str, Any], default: list[str]) -> list[str]:
    layouts = angle.get("layouts", default)
    return unique_list(layouts, LAYOUTS, f"Angle {angle['id']!r} layouts")


def unique_list(values: Any, allowed: tuple[str, ...], label: str) -> list[str]:
    if not isinstance(values, list) or not values:
        raise ValueError(f"{label} must be a non-empty list")
    unknown = [value for value in values if value not in allowed]
    if unknown:
        raise ValueError(f"{label} has unsupported values: {unknown}")
    if len(set(values)) != len(values):
        raise ValueError(f"{label} has duplicates")
    return list(values)


def validate_angles(spec: dict[str, Any]) -> list[dict[str, Any]]:
    angles = spec.get("angles")
    if not isinstance(angles, list) or not angles:
        raise ValueError("Spec needs a non-empty angles list")
    seen: set[str] = set()
    for angle in angles:
        if not isinstance(angle, dict):
            raise TypeError("Each angle must be an object")
        angle_id = require_id(angle.get("id"), "Angle id")
        if angle_id in seen:
            raise ValueError(f"Duplicate angle id {angle_id!r}")
        seen.add(angle_id)
        if angle.get("type") not in ANGLE_TYPES:
            raise ValueError(
                f"Angle {angle_id!r} type must be one of: {', '.join(ANGLE_TYPES)}"
            )
    return angles


def build_jobs(
    spec: dict[str, Any],
    root: Path,
    output_dir: Path,
    brand: dict[str, Any],
    facts: dict[str, Any],
    product: dict[str, Any],
    plate: dict[str, Any] | None,
    freshness: Freshness,
) -> tuple[list[dict[str, Any]], list[str]]:
    campaign = spec["campaign"]
    version = spec["version"]
    layouts = unique_list(spec.get("layouts"), LAYOUTS, "Spec layouts")
    ratios = unique_list(spec.get("ratios"), tuple(RATIOS), "Spec ratios")
    css_name = f"static_{campaign}_v{version:02d}.css"
    jobs: list[dict[str, Any]] = []
    warnings = unmapped_conditions(brand["required_lines"])
    for angle in validate_angles(spec):
        for layout in angle_layouts(angle, layouts):
            copy, claims = layout_content(layout, angle, facts["facts"], freshness)
            label = f"Angle {angle['id']!r} {layout}"
            check_banned_words(copy, brand["banned_words"], label)
            if brand["cta_verbs"] and copy["cta"] not in brand["cta_verbs"]:
                warnings.append(f"{label}: CTA {copy['cta']!r} is not a brand kit CTA verb")
            marks = apply_trademarks(copy, brand["trademark_marks"])
            placed = add_required_lines(copy, brand["required_lines"], layout)
            if layout == "offer":
                warnings.append(
                    f"{label}: offer facts are perishable; re-check price and "
                    "availability before delivery"
                )
            template = (TEMPLATES / f"{layout}.html").read_text(encoding="utf-8")
            if numbered_keys(copy, "legal") and "{{legal}}" not in template:
                raise ValueError(
                    f"{label}: the template has no {{{{legal}}}} slot for required "
                    "brand lines; add the slot or render the lines another way"
                )
            raw = copy_markup(copy)
            for ratio in ratios:
                token, width, height = RATIOS[ratio]
                name = f"{campaign}_{angle['id']}_{layout}_{token}_v{version:02d}"
                html_path = output_dir / f"{name}.html"
                png_path = output_dir / f"{name}.png"
                plate_markup = ""
                if plate is not None:
                    plate_markup = (
                        '<img class="plate" src="'
                        + html.escape(relative_url(Path(plate["path"]), output_dir))
                        + '" alt="">'
                    )
                document = fill_template(
                    template,
                    {
                        **copy,
                        "lang": spec["language"],
                        "stylesheet": css_name,
                        "ratio_class": f"ratio-{token}",
                        "logo_src": relative_url(Path(brand["logo"]["path"]), output_dir),
                        "brand_name": brand["name"],
                        "product_src": relative_url(Path(product["path"]), output_dir),
                        "product_name": product["name"],
                    },
                    {**raw, "plate": plate_markup},
                )
                jobs.append(
                    {
                        "name": name,
                        "angle": angle["id"],
                        "angle_type": angle["type"],
                        "layout": layout,
                        "ratio": ratio,
                        "width": width,
                        "height": height,
                        "html": html_path.relative_to(root).as_posix(),
                        "png": png_path.relative_to(root).as_posix(),
                        "render_record": png_path.with_name(f"render_{name}.json")
                        .relative_to(root)
                        .as_posix(),
                        "copy": copy,
                        "claims": claims,
                        "trademark_marks_applied": marks,
                        "required_lines": placed,
                        "document": document,
                        "command": render_command(
                            html_path,
                            png_path,
                            root,
                            width,
                            height,
                            copy,
                            brand["fonts"]["headline"]["alias"],
                        ),
                    }
                )
    return jobs, warnings


def contact_pages(
    spec: dict[str, Any], root: Path, output_dir: Path, jobs: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    columns = len(spec["ratios"])
    rows = [jobs[index : index + columns] for index in range(0, len(jobs), columns)]
    template = (TEMPLATES / "contact-sheet.html").read_text(encoding="utf-8")
    page_count = math.ceil(len(rows) / CONTACT_ROWS_PER_PAGE)
    pages: list[dict[str, Any]] = []
    for page_index in range(page_count):
        page_rows = rows[
            page_index * CONTACT_ROWS_PER_PAGE : (page_index + 1) * CONTACT_ROWS_PER_PAGE
        ]
        tiles = "".join(
            '<figure class="tile">'
            f'<img src="{html.escape(quote(Path(job["png"]).name))}" alt="">'
            f"<figcaption>{html.escape(job['name'])}</figcaption>"
            "</figure>"
            for row in page_rows
            for job in row
        )
        width = columns * CONTACT_TILE + (columns + 1) * CONTACT_GAP
        height = 2 * CONTACT_GAP + 56 + len(page_rows) * (CONTACT_TILE + 40 + CONTACT_GAP)
        stem = f"contact_{spec['campaign']}_p{page_index + 1:02d}_v{spec['version']:02d}"
        html_path = output_dir / f"{stem}.html"
        png_path = output_dir / f"{stem}.png"
        document = fill_template(
            template,
            {
                "lang": spec["language"],
                "title": f"{spec['campaign']} v{spec['version']:02d} "
                f"page {page_index + 1} of {page_count}",
            },
            {
                "width": str(width),
                "height": str(height),
                "columns": str(columns),
                "tiles": tiles,
            },
        )
        pages.append(
            {
                "name": stem,
                "html": html_path.relative_to(root).as_posix(),
                "png": png_path.relative_to(root).as_posix(),
                "width": width,
                "height": height,
                "jobs": [job["name"] for row in page_rows for job in row],
                "document": document,
                "command": render_command(
                    html_path, png_path, root, width, height, {}, None
                ),
            }
        )
    return pages


def validate_spec(spec: Any) -> dict[str, Any]:
    if not isinstance(spec, dict):
        raise TypeError("Spec must be a JSON object")
    require_id(spec.get("campaign"), "Campaign")
    language = spec.get("language")
    if not isinstance(language, str) or not LANGUAGE_TAG.fullmatch(language):
        raise ValueError("Spec language must be a BCP 47 tag such as 'en' or 'es-MX'")
    version = spec.setdefault("version", 1)
    if not isinstance(version, int) or isinstance(version, bool) or not 1 <= version <= 99:
        raise ValueError("Spec version must be an integer from 1 to 99")
    output = spec.get("output_dir")
    if not isinstance(output, str) or not output.strip():
        raise ValueError("Spec output_dir is required")
    window = spec.setdefault("perishable_max_age_hours", DEFAULT_PERISHABLE_MAX_AGE_HOURS)
    if not isinstance(window, (int, float)) or isinstance(window, bool) or not window > 0:
        raise ValueError("Spec perishable_max_age_hours must be a number greater than zero")
    return spec


def plan(
    spec_path: Path,
    asset_root: Path | None,
    overwrite: bool,
    now: datetime | None = None,
) -> dict[str, Any]:
    freshness_clock = now or datetime.now(UTC)
    spec_path = spec_path.expanduser().resolve()
    spec = validate_spec(load_json(spec_path, "Spec"))
    root = (asset_root or spec_path.parent).expanduser().resolve()
    if not root.is_dir():
        raise ValueError(f"Asset root is not a directory: {root}")
    output_dir = (root / spec["output_dir"]).resolve()
    if not output_dir.is_relative_to(root):
        raise ValueError("Spec output_dir escapes the asset root")
    brand = load_brand(root, spec)
    facts = load_facts(root, spec)
    product_spec = spec.get("product")
    if not isinstance(product_spec, dict):
        raise TypeError("Spec product must be an object with name and image")
    product_path = contained_file(
        root, root, product_spec.get("image"), "Product image", IMAGE_SUFFIXES
    )
    product = {
        "name": require_text(product_spec.get("name"), "Product name"),
        "path": str(product_path),
        "sha256": sha256(product_path),
    }
    plate = None
    if spec.get("background_plate") is not None:
        plate_path = contained_file(
            root, root, spec["background_plate"], "Background plate", IMAGE_SUFFIXES
        )
        plate = {"path": str(plate_path), "sha256": sha256(plate_path)}
    freshness = Freshness(freshness_clock, float(spec["perishable_max_age_hours"]))
    jobs, warnings = build_jobs(
        spec, root, output_dir, brand, facts, product, plate, freshness
    )
    pages = contact_pages(spec, root, output_dir, jobs)
    css_name = f"static_{spec['campaign']}_v{spec['version']:02d}.css"
    css = stylesheet(brand, output_dir)
    manifest_path = output_dir / f"batch_{spec['campaign']}_v{spec['version']:02d}.json"
    writes = {output_dir / css_name: css}
    for item in [*jobs, *pages]:
        writes[root / item["html"]] = item.pop("document")
    existing = [path for path in [*writes, manifest_path] if path.exists()]
    if existing and not overwrite:
        raise ValueError(
            "Refusing to overwrite existing files; raise the spec version or pass "
            "--overwrite: " + ", ".join(sorted(display_path(p) for p in existing))
        )

    def record(path: Path) -> dict[str, str]:
        return {"path": display_path(path), "sha256": sha256(path)}

    manifest = {
        "schema_version": 1,
        "campaign": spec["campaign"],
        "version": spec["version"],
        "language": spec["language"],
        "perishable_max_age_hours": spec["perishable_max_age_hours"],
        "checked_at": freshness_clock.isoformat(),
        "generation": "deterministic_html",
        "renderer": "html-graphic-render",
        "status": "review",
        "asset_root": display_path(root),
        "inputs": {
            "brand_kit": {
                "path": display_path(brand["path"]),
                "sha256": brand["sha256"],
                "brand_id": brand["brand_id"],
            },
            "facts": {"path": display_path(facts["path"]), "sha256": facts["sha256"]},
            "product_image": {"path": display_path(product_path), "sha256": product["sha256"]},
            "background_plate": None
            if plate is None
            else {"path": display_path(Path(plate["path"])), "sha256": plate["sha256"]},
            "logo": {"path": display_path(Path(brand["logo"]["path"])), "sha256": brand["logo"]["sha256"]},
            "fonts": {
                role: {
                    "family": font["family"],
                    "alias": font["alias"],
                    "weight": font["weight"],
                    "path": display_path(Path(font["path"])),
                    "sha256": font["sha256"],
                }
                for role, font in sorted(brand["fonts"].items())
            },
            "templates": {
                path.name: sha256(path) for path in sorted(TEMPLATES.iterdir()) if path.is_file()
            },
        },
        "stylesheet": (output_dir / css_name).relative_to(root).as_posix(),
        "jobs": jobs,
        "contact_sheets": pages,
        "warnings": warnings,
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    for path, content in writes.items():
        path.write_text(content, encoding="utf-8")
    manifest["inputs"]["stylesheet_sha256"] = sha256(output_dir / css_name)
    manifest_path.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    manifest["manifest"] = display_path(manifest_path)
    manifest["shell_commands"] = [
        shlex.join(item["command"]) for item in [*jobs, *pages]
    ]
    return manifest


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Expand a static-ad spec into angle x layout x ratio HTML entrypoints "
            "for html-graphic-render"
        )
    )
    commands = parser.add_subparsers(dest="command", required=True)
    plan_parser = commands.add_parser("plan", help="write HTML entrypoints and a batch manifest")
    plan_parser.add_argument("spec", type=Path)
    plan_parser.add_argument("--asset-root", type=Path)
    plan_parser.add_argument("--overwrite", action="store_true")
    return parser


def main() -> int:
    arguments = build_parser().parse_args()
    try:
        result = plan(arguments.spec, arguments.asset_root, arguments.overwrite)
    except (OSError, TypeError, ValueError) as error:
        print(str(error), file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
