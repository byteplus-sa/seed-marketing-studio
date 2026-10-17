from __future__ import annotations

import argparse
import hashlib
import json
import re
from dataclasses import asdict, dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

SCHEMA_PATH = (
    Path(__file__).resolve().parents[3] / "contracts/schemas/product-facts.schema.json"
)
PERISHABLE_KINDS = {"price", "availability", "offer"}
SUBSTANTIATED_KINDS = {"performance", "comparison"}
QUALIFIERS = (
    ("up to", re.compile(r"\bup to\b", re.IGNORECASE)),
    ("as low as", re.compile(r"\bas low as\b", re.IGNORECASE)),
    ("from", re.compile(r"\bfrom\s+[^\w\s]?\d", re.IGNORECASE)),
    ("starting at", re.compile(r"\bstarting at\b", re.IGNORECASE)),
    ("may", re.compile(r"\bmay\b", re.IGNORECASE)),
    ("approximately", re.compile(r"\bapproximately\b", re.IGNORECASE)),
)


@dataclass(frozen=True)
class Finding:
    rule_id: str
    path: str
    message: str
    severity: str = "error"


class FactsError(Exception):
    pass


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def parse_time(value: Any) -> datetime | None:
    if not isinstance(value, str):
        return None
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError:
        return None
    return parsed if parsed.tzinfo else None


def schema_findings(document: Any) -> list[Finding]:
    schema = json.loads(SCHEMA_PATH.read_text())
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    return [
        Finding("facts.schema", ".".join(map(str, error.absolute_path)), error.message)
        for error in validator.iter_errors(document)
    ]


def entries(document: dict[str, Any], key: str) -> list[tuple[int, dict[str, Any]]]:
    value = document.get(key)
    if not isinstance(value, list):
        return []
    return [(index, entry) for index, entry in enumerate(value) if isinstance(entry, dict)]


def dropped_qualifiers(fact: dict[str, Any]) -> list[str]:
    claim = fact.get("claim")
    quote = fact.get("quote")
    if not isinstance(claim, str) or not isinstance(quote, str):
        return []
    return [
        label
        for label, pattern in QUALIFIERS
        if pattern.search(quote) and not pattern.search(claim)
    ]


def qualifier_message(label: str) -> str:
    return f"The quote says {label!r} but the claim drops it; keep the qualifier in the claim"


def qualifier_findings(fact: dict[str, Any], path: str) -> list[Finding]:
    return [
        Finding(
            "facts.claim_qualifier",
            f"{path}.claim",
            f"{qualifier_message(label)}; supported withholds the claim until then",
            "warning",
        )
        for label in dropped_qualifiers(fact)
    ]


def retrieval_findings(value: Any, path: str, now: datetime) -> list[Finding]:
    retrieved = parse_time(value)
    if retrieved is None:
        return [Finding("facts.retrieved_at", path, "Use an ISO-8601 time with a UTC offset")]
    if retrieved > now + timedelta(minutes=5):
        return [Finding("facts.retrieved_at", path, "Retrieval time is in the future")]
    return []


def fact_findings(fact: dict[str, Any], path: str, now: datetime) -> list[Finding]:
    findings = qualifier_findings(fact, path)
    kind = fact.get("kind")
    status = fact.get("status")
    if not fact.get("source_url") and not fact.get("source_ref"):
        findings.append(
            Finding("facts.source", path, "A fact needs a source_url or a source_ref")
        )
    if kind in PERISHABLE_KINDS and status != "perishable":
        findings.append(
            Finding(
                "facts.perishable",
                f"{path}.status",
                f"A {kind} fact is time-sensitive and must be marked perishable",
            )
        )
    if kind in SUBSTANTIATED_KINDS and status == "supported" and not fact.get("substantiation"):
        findings.append(
            Finding(
                "facts.substantiation",
                f"{path}.status",
                f"A supported {kind} claim needs a substantiation reference beyond marketing copy",
            )
        )
    findings.extend(retrieval_findings(fact.get("retrieved_at"), f"{path}.retrieved_at", now))
    return findings


def image_findings(image: dict[str, Any], path: str, card_dir: Path) -> list[Finding]:
    name = image.get("file")
    if not isinstance(name, str) or "/" in name or "\\" in name or name.startswith("."):
        return [Finding("facts.image_contained", path, "Image file must be a plain name beside facts.json")]
    target = card_dir / name
    if target.is_symlink() or not target.is_file():
        return [Finding("facts.image_exists", path, f"{name} does not exist beside facts.json")]
    actual = sha256_file(target)
    if actual != image.get("sha256"):
        return [
            Finding(
                "facts.image_hash",
                path,
                f"{name} SHA-256 is {actual}, facts record {image.get('sha256')}",
            )
        ]
    return []


def validate_facts(document: Any, card_dir: Path, now: datetime) -> list[Finding]:
    findings = schema_findings(document)
    if not isinstance(document, dict):
        return findings
    if card_dir.name != document.get("product_id"):
        findings.append(
            Finding(
                "facts.product_directory",
                "product_id",
                f"product_id {document.get('product_id')!r} must equal its directory name {card_dir.name!r}",
            )
        )
    facts = entries(document, "facts")
    identifiers = [fact.get("fact_id") for _, fact in facts]
    for identifier in sorted({value for value in identifiers if isinstance(value, str) and identifiers.count(value) > 1}):
        findings.append(Finding("facts.unique", "facts", f"Duplicate fact_id {identifier}"))
    for index, fact in facts:
        findings.extend(fact_findings(fact, f"facts.{index}", now))
    images = entries(document, "images")
    files = [image.get("file") for _, image in images]
    for name in sorted({value for value in files if isinstance(value, str) and files.count(value) > 1}):
        findings.append(Finding("facts.unique", "images", f"Duplicate image file {name}"))
    for index, image in images:
        findings.extend(image_findings(image, f"images.{index}", card_dir))
        findings.extend(retrieval_findings(image.get("retrieved_at"), f"images.{index}.retrieved_at", now))
    return findings


def read_facts(path: Path) -> Any:
    if path.is_symlink() or not path.is_file():
        raise FactsError(f"{path} is not a regular file")
    try:
        return json.loads(path.read_text())
    except ValueError as error:
        raise FactsError(f"{path} is not valid JSON: {error}") from error


def usable_status(fact: dict[str, Any], now: datetime, max_age_hours: float | None) -> bool:
    status = fact.get("status")
    if status == "supported":
        return True
    if status != "perishable" or max_age_hours is None:
        return False
    retrieved = parse_time(fact.get("retrieved_at"))
    return retrieved is not None and now - retrieved <= timedelta(hours=max_age_hours)


def claim_view(fact: dict[str, Any]) -> dict[str, Any]:
    return {
        str(key): fact[key]
        for key in (
            "fact_id",
            "kind",
            "claim",
            "quote",
            "conditions",
            "source_url",
            "source_ref",
            "retrieved_at",
            "status",
        )
        if key in fact
    }


def usable_claims(
    document: dict[str, Any], now: datetime, max_age_hours: float | None
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    usable: list[dict[str, Any]] = []
    blocked: list[dict[str, Any]] = []
    for _, fact in entries(document, "facts"):
        if not usable_status(fact, now, max_age_hours):
            continue
        dropped = dropped_qualifiers(fact)
        if dropped:
            blocked.append(
                {
                    "fact_id": fact.get("fact_id"),
                    "rule_id": "facts.claim_qualifier",
                    "reason": "; ".join(qualifier_message(label) for label in dropped),
                }
            )
            continue
        usable.append(claim_view(fact))
    return usable, blocked


def emit(document: dict[str, Any]) -> None:
    print(json.dumps(document, indent=2, ensure_ascii=False))


def blocking(findings: list[Finding]) -> list[Finding]:
    return [finding for finding in findings if finding.severity == "error"]


def checked(path: Path, now: datetime) -> tuple[Any, list[Finding]]:
    document = read_facts(path)
    return document, validate_facts(document, path.resolve().parent, now)


def command_validate(args: argparse.Namespace, now: datetime) -> int:
    _, findings = checked(args.facts, now)
    errors = blocking(findings)
    emit({"ok": not errors, "findings": [asdict(finding) for finding in findings]})
    return int(bool(errors))


def command_supported(args: argparse.Namespace, now: datetime) -> int:
    if args.max_age_hours is not None and args.max_age_hours <= 0:
        raise FactsError("--max-age-hours must be greater than zero")
    document, findings = checked(args.facts, now)
    errors = blocking(findings)
    if errors:
        emit({"ok": False, "findings": [asdict(finding) for finding in errors]})
        return 1
    claims, blocked = usable_claims(document, now, args.max_age_hours)
    emit(
        {
            "ok": True,
            "product_id": document["product_id"],
            "claims": claims,
            "blocked": blocked,
        }
    )
    return 0


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description="Validate product facts and list claims usable in copy")
    commands = root.add_subparsers(dest="command", required=True)
    validate = commands.add_parser("validate", help="Validate schema, sources, statuses and image hashes")
    validate.add_argument("facts", type=Path)
    validate.set_defaults(handler=command_validate)
    supported = commands.add_parser("supported", help="Print only claims usable in scripts, supers and captions")
    supported.add_argument("facts", type=Path)
    supported.add_argument(
        "--max-age-hours",
        type=float,
        help="Also include perishable facts (price, availability, offer) retrieved within this many hours",
    )
    supported.set_defaults(handler=command_supported)
    return root


def main(argv: list[str] | None = None, now: datetime | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        return int(args.handler(args, now or datetime.now(UTC)))
    except (FactsError, OSError) as error:
        emit({"ok": False, "error": str(error)})
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
