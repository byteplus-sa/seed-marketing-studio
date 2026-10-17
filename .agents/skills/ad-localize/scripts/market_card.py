from __future__ import annotations

import argparse
import hashlib
import json
import re
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path, PurePosixPath
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker, ValidationError

AGENTS_ROOT = Path(__file__).resolve().parents[3]
SCHEMA_PATH = AGENTS_ROOT / "contracts/schemas/market-card.schema.json"
REVIEW_SCHEMA_PATH = AGENTS_ROOT / "contracts/schemas/native-review.schema.json"
PLATFORMS_PATH = AGENTS_ROOT / "contracts/ad-platforms.json"
ID_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
BCP47_PATH = re.compile(r"^(languages\.\d+\.code|subtitle_languages\.\d+)$")
MARKET_ID_MAX = 48
VARIANT_KEY_MAX = 96
RESERVED_VARIANT_KEYS = frozenset({"decisions"})
VARIANT_REVIEW_REF = "decisions/native_review.json"
CARD_NAME = "market.json"
MARKETS_DIR = "markets"
PROJECTS_DIR = "projects"
INVENTORY_NAME = "inventory.md"
TRANSLATION_NAME = "translation.md"
REVIEWED_FILES = (TRANSLATION_NAME, INVENTORY_NAME)
LEVELS = ("L1", "L2", "L3", "L4", "L5")
REVIEWED_LEVELS = ("L3", "L4", "L5")
STAGES = ("draft", "final", "delivery")
NOT_LISTED = ("approval", "reviewer", "missing")
RTL_LANGUAGES = frozenset({"ar", "he", "fa", "ur", "ps", "sd", "ug", "yi", "dv", "ckb"})
RTL_SCRIPTS = frozenset({"Arab", "Hebr", "Thaa", "Syrc", "Nkoo"})
DEPRECATED_LANGUAGES = {"iw": "he", "ji": "yi"}
REVIEW_FIELDS = (
    "languages",
    "casting_notes",
    "settings_notes",
    "props_wardrobe_notes",
    "gestures_and_taboos",
    "legal_lines",
    "currency",
)
APPROVAL_EXEMPT = {
    "": ("status", "approval"),
    "reviewer": ("status", "name", "decision_ref", "evidence"),
    "ai_disclosure": ("decision_refs",),
}
CULTURAL_FIELDS = (
    "languages",
    "settings_notes",
    "props_wardrobe_notes",
    "gestures_and_taboos",
    "currency.code",
    "currency.format",
    "number_and_date_formats.number",
    "number_and_date_formats.date",
    "units",
    "legal_lines",
)
LEVEL_FIELDS: dict[str, tuple[str, ...]] = {
    "L1": ("languages", "subtitle_languages"),
    "L2": ("languages",),
    "L3": ("languages", "casting_notes"),
    "L4": CULTURAL_FIELDS,
    "L5": (*CULTURAL_FIELDS, "casting_notes"),
}
DELIVERY_FIELDS = ("placements", "ai_disclosure.jurisdictions")


@dataclass(frozen=True)
class Finding:
    rule_id: str
    path: str
    message: str
    severity: str = "error"


class MarketCardError(Exception):
    pass


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_schema(path: Path = SCHEMA_PATH) -> dict[str, Any]:
    schema = json.loads(path.read_text())
    Draft202012Validator.check_schema(schema)
    return dict(schema)


def canonical_sha256(value: Any) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def card_sha256(card: dict[str, Any]) -> str:
    content = {key: value for key, value in card.items() if key not in APPROVAL_EXEMPT[""]}
    for section, keys in APPROVAL_EXEMPT.items():
        if section and isinstance(content.get(section), dict):
            content[section] = {key: value for key, value in content[section].items() if key not in keys}
    return canonical_sha256(content)


def review_fields_sha256(card: dict[str, Any]) -> str:
    return canonical_sha256({field: card.get(field) for field in REVIEW_FIELDS})


def known_placements(path: Path = PLATFORMS_PATH) -> set[str]:
    document = json.loads(path.read_text())
    return {placement["id"] for placement in document["placements"]}


def schema_findings(card: Any) -> list[Finding]:
    validator = Draft202012Validator(load_schema(), format_checker=FormatChecker())
    findings = []
    for error in validator.iter_errors(card):
        path = ".".join(map(str, error.absolute_path))
        rule = "market.bcp47" if BCP47_PATH.fullmatch(path) else "market.schema"
        findings.append(Finding(rule, path, error.message))
    return findings


def null_paths(value: Any, prefix: str = "") -> list[str]:
    if value is None:
        return [prefix]
    if isinstance(value, dict):
        return [
            path
            for key, child in value.items()
            if not (prefix == "" and key in NOT_LISTED)
            for path in null_paths(child, f"{prefix}.{key}" if prefix else key)
        ]
    if isinstance(value, list):
        return [
            path
            for index, child in enumerate(value)
            for path in null_paths(child, f"{prefix}.{index}")
        ]
    return []


def missing_findings(card: dict[str, Any]) -> list[Finding]:
    raw = card.get("missing")
    listed = {path for path in raw if isinstance(path, str)} if isinstance(raw, list) else set()
    unknown = set(null_paths(card))
    findings = [
        Finding(
            "market.missing_listed",
            path,
            "Unknown value must be listed in missing rather than left silent or invented",
        )
        for path in sorted(unknown - listed)
    ]
    findings.extend(
        Finding(
            "market.missing_listed",
            path,
            "Listed as missing but a value is present; remove it from missing",
            "warning",
        )
        for path in sorted(listed - unknown)
    )
    return findings


def parse_timestamp(value: str) -> datetime | None:
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError:
        return None
    return parsed if parsed.tzinfo is not None else None


def timestamp_message(value: Any) -> str | None:
    if not isinstance(value, str) or parse_timestamp(value) is not None:
        return None
    return f"{value!r} is not an ISO-8601 date-time with a UTC offset, such as 2026-10-17T09:00:00Z"


def timestamp_findings(card: dict[str, Any]) -> list[Finding]:
    approval = card.get("approval")
    message = timestamp_message(approval.get("decided_at")) if isinstance(approval, dict) else None
    return [] if message is None else [Finding("market.timestamp", "approval.decided_at", message)]


def directory_findings(card: dict[str, Any], card_dir: Path) -> list[Finding]:
    findings = []
    if card_dir.parent.name != MARKETS_DIR:
        findings.append(
            Finding(
                "market.campaign_matches_directory",
                "campaign",
                f"A market card lives at <campaign>/{MARKETS_DIR}/<market-id>/{CARD_NAME}, not in {card_dir.parent.name!r}",
            )
        )
    if card.get("market_id") != card_dir.name:
        findings.append(
            Finding(
                "market.id_matches_directory",
                "market_id",
                f"market_id {card.get('market_id')!r} must equal its directory name {card_dir.name!r}",
            )
        )
    campaign_dir = card_dir.parent.parent
    if card_dir.parent.name == MARKETS_DIR and card.get("campaign") != campaign_dir.name:
        findings.append(
            Finding(
                "market.campaign_matches_directory",
                "campaign",
                f"campaign {card.get('campaign')!r} must equal the campaign directory {campaign_dir.name!r}",
            )
        )
    return findings


def script_subtag(code: str) -> str | None:
    for subtag in code.split("-")[1:]:
        if len(subtag) == 1:
            return None
        if len(subtag) == 4 and subtag.isalpha():
            return subtag.title()
    return None


def expected_direction(code: str) -> tuple[str | None, bool]:
    script = script_subtag(code)
    right_to_left_language = code.split("-")[0].lower() in RTL_LANGUAGES
    if script in RTL_SCRIPTS or (script is None and right_to_left_language):
        return "rtl", True
    if script is not None and right_to_left_language:
        return "ltr", True
    return None, False


def deprecated_tag_findings(card: dict[str, Any]) -> list[Finding]:
    tagged: list[tuple[str, Any]] = []
    if isinstance(card.get("languages"), list):
        tagged.extend(
            (f"languages.{index}.code", language.get("code"))
            for index, language in enumerate(card["languages"])
            if isinstance(language, dict)
        )
    if isinstance(card.get("subtitle_languages"), list):
        tagged.extend((f"subtitle_languages.{index}", code) for index, code in enumerate(card["subtitle_languages"]))
    findings = []
    for path, code in tagged:
        if not isinstance(code, str):
            continue
        replacement = DEPRECATED_LANGUAGES.get(code.split("-")[0].lower())
        if replacement is not None:
            findings.append(
                Finding("market.bcp47", path, f"{code} uses a deprecated language subtag; use {replacement!r}")
            )
    return findings


def direction_findings(card: dict[str, Any]) -> list[Finding]:
    languages = card.get("languages")
    if not isinstance(languages, list):
        return []
    findings = []
    for index, language in enumerate(languages):
        if not isinstance(language, dict) or not isinstance(language.get("code"), str):
            continue
        code, direction = language["code"], language.get("direction")
        expected, certain = expected_direction(code)
        path = f"languages.{index}.direction"
        if certain and direction != expected:
            findings.append(
                Finding("market.direction", path, f"{code} is written {expected}; direction is {direction}")
            )
        elif not certain and direction == "rtl":
            findings.append(
                Finding(
                    "market.direction",
                    path,
                    f"{code} is marked rtl; confirm the script, or add a script subtag such as -Arab",
                    "warning",
                )
            )
    return findings


def placement_findings(card: dict[str, Any], placements: set[str]) -> list[Finding]:
    requested = card.get("placements")
    if not isinstance(requested, list):
        return []
    return [
        Finding(
            "market.placement_known",
            f"placements.{index}",
            f"Unknown placement {value!r}; use an id from ad-platforms.json: {', '.join(sorted(placements))}",
        )
        for index, value in enumerate(requested)
        if value not in placements
    ]


def reviewer_findings(card: dict[str, Any]) -> list[Finding]:
    reviewer = card.get("reviewer")
    if not isinstance(reviewer, dict):
        return []
    status = reviewer.get("status")
    findings = []
    if status in ("pending", "signed_off") and reviewer.get("role") is None:
        findings.append(Finding("market.reviewer_record", "reviewer.role", f"A {status} review needs a reviewer role"))
    if status == "signed_off":
        findings.extend(
            Finding(
                "market.reviewer_record",
                f"reviewer.{field}",
                f"A signed_off review needs {field}; the agent never signs off on its own",
            )
            for field in ("decision_ref", "evidence")
            if not reviewer.get(field)
        )
    level = card.get("level_default")
    if level in REVIEWED_LEVELS and status == "none":
        findings.append(
            Finding(
                "localize.native_review",
                "reviewer.status",
                f"{level} needs a native-speaker or local reviewer sign-off before final generation and delivery; name the reviewer",
                "error" if card.get("status") == "approved" else "warning",
            )
        )
    return findings


def repository_root(card_dir: Path) -> Path | None:
    parents = card_dir.parents
    if len(parents) < 4 or parents[0].name != MARKETS_DIR or parents[2].name != PROJECTS_DIR:
        return None
    return parents[3]


def price_fact_findings(card: dict[str, Any], card_dir: Path, facts_ref: str, price_source: str) -> list[Finding]:
    root = repository_root(card_dir)
    if root is None:
        return []
    try:
        path = contained_file(root, facts_ref)
        if not path.is_file():
            return []
        facts = read_json(path)
    except MarketCardError as error:
        return [Finding("market.price_fact", "facts_ref", str(error))]
    entries = facts.get("facts") if isinstance(facts, dict) else None
    fact = next(
        (entry for entry in entries or [] if isinstance(entry, dict) and entry.get("fact_id") == price_source),
        None,
    )
    if fact is None:
        return [Finding("market.price_fact", "price_source", f"{price_source} is not a fact in {facts_ref}")]
    if fact.get("status") != "perishable":
        return [
            Finding(
                "market.price_fact",
                "price_source",
                f"{price_source} has status {fact.get('status')!r}; a price must be a perishable fact",
            )
        ]
    return []


def facts_in_localized_project(card: dict[str, Any], facts_ref: str) -> bool:
    parts = facts_ref.split("/")
    if len(parts) < 3 or parts[0] != PROJECTS_DIR or parts[2] != "elements":
        return False
    project, campaign, market_id = parts[1], card.get("campaign"), card.get("market_id")
    if project == f"{campaign}-{market_id}":
        return True
    prefix, suffix = f"{campaign}-", f"-{market_id}"
    return (
        project.startswith(prefix)
        and project.endswith(suffix)
        and len(project) > len(prefix) + len(suffix)
        and bool(ID_PATTERN.fullmatch(project[len(prefix) : -len(suffix)]))
    )


def price_findings(card: dict[str, Any], card_dir: Path) -> list[Finding]:
    findings = []
    facts_ref = card.get("facts_ref")
    if isinstance(facts_ref, str) and not facts_in_localized_project(card, facts_ref):
        findings.append(
            Finding(
                "market.price_fact",
                "facts_ref",
                f"facts_ref must be the target market's own facts under {output_project(card)}/elements/ "
                f"or a variant's {output_project(card, '<variant-key>')}/elements/, not the source campaign's",
            )
        )
    price_source = card.get("price_source")
    if price_source is None:
        return findings
    if facts_ref is None:
        findings.append(
            Finding("market.price_fact", "facts_ref", "price_source needs the market facts file it belongs to")
        )
    currency = card.get("currency")
    if not isinstance(currency, dict) or currency.get("code") is None:
        findings.append(Finding("market.price_fact", "currency.code", "A price needs the market currency code"))
    if not findings and isinstance(facts_ref, str) and isinstance(price_source, str):
        findings.extend(price_fact_findings(card, card_dir, facts_ref, price_source))
    return findings


def approval_findings(card: dict[str, Any], card_dir: Path) -> list[Finding]:
    approval = card.get("approval")
    if not isinstance(approval, dict) or not isinstance(approval.get("decision_ref"), str):
        return []
    try:
        target = contained_file(card_dir, approval["decision_ref"])
    except MarketCardError as error:
        return [Finding("market.approval_record", "approval.decision_ref", str(error))]
    if target.is_symlink() or not target.is_file():
        return [
            Finding(
                "market.approval_record",
                "approval.decision_ref",
                f"The approval decision record {approval['decision_ref']} does not exist",
            )
        ]
    return []


def validate_card(card: Any, card_dir: Path, placements: set[str] | None = None) -> list[Finding]:
    findings = schema_findings(card)
    if not isinstance(card, dict):
        return findings
    findings.extend(missing_findings(card))
    findings.extend(directory_findings(card, card_dir))
    findings.extend(direction_findings(card))
    findings.extend(deprecated_tag_findings(card))
    findings.extend(placement_findings(card, known_placements() if placements is None else placements))
    findings.extend(reviewer_findings(card))
    findings.extend(price_findings(card, card_dir))
    findings.extend(approval_findings(card, card_dir))
    findings.extend(timestamp_findings(card))
    return findings


def blocking(findings: list[Finding]) -> list[Finding]:
    return [finding for finding in findings if finding.severity == "error"]


def read_json(path: Path) -> Any:
    if path.is_symlink() or not path.is_file():
        raise MarketCardError(f"{path} is not a regular file")
    try:
        return json.loads(path.read_text())
    except ValueError as error:
        raise MarketCardError(f"{path} is not valid JSON: {error}") from error
    except RecursionError as error:
        raise MarketCardError(f"{path} is too deeply nested to read") from error


def read_regular_text(path: Path) -> str:
    if path.is_symlink() or not path.is_file():
        raise MarketCardError(f"{path.name} is missing or not a regular file")
    return path.read_text()


def contained_file(base: Path, relative: str) -> Path:
    pure = PurePosixPath(relative)
    if pure.is_absolute() or ".." in pure.parts:
        raise MarketCardError(f"{relative} must stay inside {base}")
    root = base.resolve()
    resolved = (root / relative).resolve()
    if not resolved.is_relative_to(root):
        raise MarketCardError(f"{relative} escapes {base}")
    return resolved


def value_at(card: dict[str, Any], dotted: str) -> Any:
    value: Any = card
    for key in dotted.split("."):
        if not isinstance(value, dict):
            return None
        value = value.get(key)
    return value


def field_blockers(card: dict[str, Any], fields: tuple[str, ...], rule: str, reason: str) -> list[Finding]:
    return [
        Finding(rule, field, f"{field} is unknown; ask the user for it ({reason})")
        for field in fields
        if value_at(card, field) is None
    ]


def reviewed_file_blockers(card_dir: Path, reviewed: list[dict[str, Any]]) -> list[str]:
    paths = {entry["path"] for entry in reviewed}
    messages = [
        f"The sign-off record must cover {name} with its SHA-256"
        for name in REVIEWED_FILES
        if name not in paths
    ]
    for entry in reviewed:
        try:
            target = contained_file(card_dir, entry["path"])
        except MarketCardError as error:
            messages.append(str(error))
            continue
        if not target.is_file():
            messages.append(f"Reviewed file {entry['path']} does not exist")
        elif sha256_file(target) != entry["sha256"]:
            messages.append(f"{entry['path']} changed after sign-off; the review is stale")
    return messages


def record_blockers(card: dict[str, Any], review_dir: Path, record: dict[str, Any], variant: str | None) -> list[str]:
    messages = []
    if record.get("variant") != variant:
        expected = f"variant {variant!r}" if variant else "no variant"
        messages.append(f"The sign-off record names variant {record.get('variant')!r}; this gate needs {expected}")
    if record["market_id"] != card["market_id"]:
        messages.append(f"The sign-off record's market_id {record['market_id']!r} is not this card's")
    if record["reviewer_role"] != card["reviewer"]["role"]:
        messages.append(
            f"The sign-off record's reviewer_role {record['reviewer_role']!r} differs from the card's reviewer role"
        )
    if not record["evidence"].strip():
        messages.append("The sign-off record must quote the reviewer's or user's words in evidence")
    if record["card_fields_sha256"] != review_fields_sha256(card):
        messages.append(
            "Card fields the reviewer checked (" + ", ".join(REVIEW_FIELDS) + ") changed after sign-off; the review is stale"
        )
    messages.extend(reviewed_file_blockers(review_dir, record["reviewed"]))
    return messages


def schema_message(error: ValidationError) -> str:
    path = ".".join(map(str, error.absolute_path)) or "root"
    if path == "reviewed" and error.validator in ("contains", "minItems"):
        return "The sign-off record must cover " + " and ".join(REVIEWED_FILES) + " with their SHA-256"
    return f"Sign-off record {path}: {error.message}"


def review_record_blockers(
    card: dict[str, Any], review_dir: Path, decision_ref: str, variant: str | None
) -> list[Finding]:
    def blockers(messages: list[str]) -> list[Finding]:
        return [Finding("localize.native_review", "reviewer.decision_ref", message) for message in messages]

    try:
        record = read_json(contained_file(review_dir, decision_ref))
    except MarketCardError as error:
        return blockers([str(error)])
    validator = Draft202012Validator(load_schema(REVIEW_SCHEMA_PATH), format_checker=FormatChecker())
    errors = [schema_message(error) for error in validator.iter_errors(record)]
    if isinstance(record, dict) and record.get("decided_by") == "agent":
        errors.append("decided_by is agent; the agent never signs off, only the user or the reviewer")
    decided = timestamp_message(record.get("decided_at")) if isinstance(record, dict) else None
    if decided is not None:
        errors.append(f"Sign-off record decided_at: {decided}")
    if errors:
        return blockers(errors)
    return blockers(record_blockers(card, review_dir, record, variant))


def native_review_blockers(card: dict[str, Any], card_dir: Path, variant: str | None) -> list[Finding]:
    reviewer = card["reviewer"]
    if variant is not None:
        if reviewer["role"] is None:
            return [Finding("localize.native_review", "reviewer.role", "Name the reviewer role on the card first")]
        return review_record_blockers(card, card_dir / variant, VARIANT_REVIEW_REF, variant)
    if reviewer["status"] != "signed_off" or not reviewer.get("decision_ref"):
        return [
            Finding(
                "localize.native_review",
                "reviewer.status",
                "Final generation and delivery at this level need a recorded native-speaker or local reviewer sign-off",
            )
        ]
    return review_record_blockers(card, card_dir, reviewer["decision_ref"], None)


def approval_blockers(card: dict[str, Any]) -> list[Finding]:
    if card["status"] != "approved":
        return [Finding("market.card_approved", "status", "The market card must be approved first")]
    if card["approval"]["card_sha256"] != card_sha256(card):
        return [
            Finding(
                "market.card_approved",
                "approval.card_sha256",
                "The card changed after approval, so it is back to draft; re-approve it",
            )
        ]
    return []


def inventory_levels(text: str) -> dict[str, str]:
    levels: dict[str, str] = {}
    columns: list[str] | None = None
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped.startswith("|"):
            columns = None
            continue
        cells = [cell.strip().strip("`").strip() for cell in stripped.strip("|").split("|")]
        if columns is None:
            columns = [cell.lower() for cell in cells]
            continue
        if "id" not in columns or "level" not in columns or set("".join(cells)) <= set("-: "):
            continue
        row = dict(zip(columns, cells, strict=False))
        element, level = row.get("id", ""), row.get("level", "").upper()
        if not element:
            continue
        if level not in LEVELS:
            raise MarketCardError(f"{INVENTORY_NAME} gives {element} the level {row.get('level')!r}; use L1 to L5")
        if element in levels:
            raise MarketCardError(f"{INVENTORY_NAME} lists {element} more than once")
        levels[element] = level
    return levels


def stricter(first: str, second: str | None) -> str:
    return first if second is None or LEVELS.index(first) >= LEVELS.index(second) else second


def variant_dir(card_dir: Path, variant: str) -> Path:
    if not ID_PATTERN.fullmatch(variant) or len(variant) > VARIANT_KEY_MAX or variant in RESERVED_VARIANT_KEYS:
        raise MarketCardError(
            f"Invalid variant key {variant!r}; use the kebab-case variant key of at most {VARIANT_KEY_MAX} characters"
        )
    path = card_dir / variant
    if path.is_symlink():
        raise MarketCardError(f"{path} is a symlink; variant folders must live inside the market folder")
    return path


def review_dir_blockers(review_dir: Path, variant: str | None) -> list[Finding]:
    if variant is None or review_dir.is_dir():
        return []
    return [
        Finding(
            "market.variant_dir",
            variant,
            f"{variant} has no folder beside the card; create it with its {INVENTORY_NAME} and {TRANSLATION_NAME}",
        )
    ]


def effective_level(review_dir: Path, card: dict[str, Any], requested: str, element: str | None) -> tuple[str, list[Finding]]:
    default = stricter(requested, card["level_default"])
    inventory = review_dir / INVENTORY_NAME
    if element is None and not inventory.exists() and not inventory.is_symlink():
        return default, []
    try:
        levels = inventory_levels(read_regular_text(inventory))
    except MarketCardError as error:
        return default, [Finding("market.level_override", INVENTORY_NAME, str(error))]
    if element is None:
        highest = max(levels.values(), key=LEVELS.index, default=None)
        return stricter(default, highest), []
    if element not in levels:
        return default, [
            Finding(
                "market.level_override",
                INVENTORY_NAME,
                f"{element} has no row in {INVENTORY_NAME}; record its level there before gating it below the card default",
            )
        ]
    return stricter(requested, levels[element]), []


def gate_blockers(
    card: dict[str, Any], card_dir: Path, level: str, stage: str, variant: str | None = None
) -> list[Finding]:
    blockers = field_blockers(card, LEVEL_FIELDS[level], "market.level_fields", f"needed for {level}")
    if stage == "draft":
        return blockers
    blockers.extend(approval_blockers(card))
    if level in REVIEWED_LEVELS:
        blockers.extend(native_review_blockers(card, card_dir, variant))
    if stage == "delivery":
        blockers.extend(field_blockers(card, DELIVERY_FIELDS, "market.delivery_fields", "needed for delivery"))
    return blockers


def scaffold(campaign: str, market_id: str, label: str | None) -> dict[str, Any]:
    card: dict[str, Any] = {
        "schema_version": 1,
        "market_id": market_id,
        "campaign": campaign,
        "label": label,
        "languages": None,
        "subtitle_languages": None,
        "casting_notes": None,
        "settings_notes": None,
        "props_wardrobe_notes": None,
        "gestures_and_taboos": None,
        "currency": {"code": None, "symbol": None, "format": None},
        "number_and_date_formats": {"number": None, "date": None},
        "units": None,
        "facts_ref": None,
        "price_source": None,
        "legal_lines": None,
        "ai_disclosure": {"jurisdictions": None, "decision_refs": []},
        "placements": None,
        "reviewer": {"role": None, "name": None, "status": "none", "decision_ref": None, "evidence": None},
        "level_default": None,
        "missing": [],
        "status": "draft",
        "approval": None,
    }
    card["missing"] = sorted(null_paths(card))
    return card


def init_card(campaign_dir: Path, market_id: str, label: str | None) -> Path:
    if campaign_dir.is_symlink() or not campaign_dir.is_dir():
        raise MarketCardError(f"{campaign_dir} is not a campaign project directory")
    campaign = campaign_dir.resolve().name
    if not ID_PATTERN.fullmatch(campaign):
        raise MarketCardError(f"Campaign directory {campaign!r} is not lowercase kebab-case")
    if not ID_PATTERN.fullmatch(market_id) or len(market_id) > MARKET_ID_MAX:
        raise MarketCardError(
            f"Invalid market id {market_id!r}; use lowercase kebab-case of at most {MARKET_ID_MAX} characters"
        )
    markets_dir = campaign_dir / MARKETS_DIR
    card_dir = markets_dir / market_id
    for candidate in (markets_dir, card_dir):
        if candidate.is_symlink():
            raise MarketCardError(f"{candidate} is a symlink; market cards must live inside the campaign")
    if markets_dir.exists() and not markets_dir.is_dir():
        raise MarketCardError(f"{markets_dir} is not a directory")
    if not card_dir.resolve().is_relative_to(campaign_dir.resolve()):
        raise MarketCardError(f"{card_dir} escapes the campaign directory")
    if card_dir.exists():
        raise MarketCardError(f"{card_dir} already exists; edit the existing card instead")
    (card_dir / "decisions").mkdir(parents=True)
    card_path = card_dir / CARD_NAME
    card_path.write_text(json.dumps(scaffold(campaign, market_id, label), indent=2, ensure_ascii=False) + "\n")
    return card_path


def output_project(card: dict[str, Any], variant: str | None = None) -> str:
    middle = f"-{variant}" if variant else ""
    return f"{PROJECTS_DIR}/{card.get('campaign')}{middle}-{card.get('market_id')}"


def summary(card: dict[str, Any], card_dir: Path) -> dict[str, Any]:
    languages = card["languages"] or []
    return {
        "market_id": card["market_id"],
        "label": card["label"],
        "campaign": card["campaign"],
        "status": card["status"],
        "output_project": output_project(card),
        "languages": languages,
        "caption_codes": [code.lower() for code in card["subtitle_languages"] or []],
        "rtl": any(language["direction"] == "rtl" for language in languages),
        "currency": card["currency"],
        "placements": card["placements"],
        "level_default": card["level_default"],
        "reviewer_status": card["reviewer"]["status"],
        "final_gate": {
            level: [asdict(finding) for finding in gate_blockers(card, card_dir, level, "final")]
            for level in LEVELS
        },
        "missing": card["missing"],
    }


def emit(document: dict[str, Any]) -> None:
    print(json.dumps(document, indent=2, ensure_ascii=False))


def validated(path: Path) -> tuple[dict[str, Any] | None, list[Finding]]:
    card = read_json(path)
    findings = validate_card(card, path.resolve().parent)
    return (card if isinstance(card, dict) and not blocking(findings) else None), findings


def command_init(args: argparse.Namespace) -> int:
    path = init_card(args.campaign_dir, args.market_id, args.label)
    emit({"ok": True, "card": str(path)})
    return 0


def command_validate(args: argparse.Namespace) -> int:
    _, findings = validated(args.card)
    errors = blocking(findings)
    emit({"ok": not errors, "findings": [asdict(finding) for finding in findings]})
    return int(bool(errors))


def command_show(args: argparse.Namespace) -> int:
    card, findings = validated(args.card)
    if card is None:
        emit({"ok": False, "findings": [asdict(finding) for finding in blocking(findings)]})
        return 1
    emit({"ok": True, **summary(card, args.card.resolve().parent)})
    return 0


def command_fingerprint(args: argparse.Namespace) -> int:
    card = read_json(args.card)
    if not isinstance(card, dict):
        raise MarketCardError(f"{args.card} is not a market card object")
    card_dir = args.card.resolve().parent
    review_dir = card_dir if args.variant is None else variant_dir(card_dir, args.variant)
    files = {}
    for name in REVIEWED_FILES:
        path = review_dir / name
        files[name] = sha256_file(path) if path.is_file() and not path.is_symlink() else None
    emit(
        {
            "ok": True,
            "card_sha256": card_sha256(card),
            "review_fields_sha256": review_fields_sha256(card),
            "files": files,
        }
    )
    return 0


def command_gate(args: argparse.Namespace) -> int:
    card, findings = validated(args.card)
    if card is None:
        emit({"ok": False, "findings": [asdict(finding) for finding in blocking(findings)]})
        return 1
    card_dir = args.card.resolve().parent
    review_dir = card_dir if args.variant is None else variant_dir(card_dir, args.variant)
    blockers = review_dir_blockers(review_dir, args.variant)
    level, level_blockers = effective_level(review_dir, card, args.level, args.element)
    if not blockers:
        blockers.extend(level_blockers)
        blockers.extend(gate_blockers(card, card_dir, level, args.stage, args.variant))
    emit(
        {
            "ok": not blockers,
            "requested_level": args.level,
            "level": level,
            "element": args.element,
            "variant": args.variant,
            "stage": args.stage,
            "output_project": output_project(card, args.variant),
            "blockers": [asdict(finding) for finding in blockers],
        }
    )
    return int(bool(blockers))


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description="Create, validate, show and gate market cards")
    commands = root.add_subparsers(dest="command", required=True)
    init = commands.add_parser("init", help="Scaffold markets/<market-id>/market.json in a campaign")
    init.add_argument("campaign_dir", type=Path)
    init.add_argument("market_id")
    init.add_argument("--label")
    init.set_defaults(handler=command_init)
    validate = commands.add_parser("validate", help="Validate schema, language tags, placements and review records")
    validate.add_argument("card", type=Path)
    validate.set_defaults(handler=command_validate)
    show = commands.add_parser("show", help="Print the consumer view of a valid card")
    show.add_argument("card", type=Path)
    show.set_defaults(handler=command_show)
    gate = commands.add_parser("gate", help="Check whether a level may proceed to a stage")
    gate.add_argument("card", type=Path)
    gate.add_argument("--level", choices=LEVELS, required=True)
    gate.add_argument("--stage", choices=STAGES, default="final")
    gate.add_argument("--element", help="Inventory id whose level in inventory.md may override the card default")
    gate.add_argument("--variant", help="Matrix variant key whose inventory, translation and sign-off to check")
    gate.set_defaults(handler=command_gate)
    fingerprint = commands.add_parser(
        "fingerprint", help="Print the hashes an approval or a reviewer sign-off record binds"
    )
    fingerprint.add_argument("card", type=Path)
    fingerprint.add_argument("--variant", help="Matrix variant key whose reviewed files to hash")
    fingerprint.set_defaults(handler=command_fingerprint)
    return root


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        return int(args.handler(args))
    except (MarketCardError, OSError) as error:
        emit({"ok": False, "error": str(error)})
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
