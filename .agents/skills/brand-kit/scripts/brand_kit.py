from __future__ import annotations

import argparse
import hashlib
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path, PurePosixPath
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

SCHEMA_PATH = (
    Path(__file__).resolve().parents[3] / "contracts/schemas/brand-kit.schema.json"
)
BRAND_ID_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
LISTABLE_EMPTY = ("logos", "palette", "typography")
KIT_NAME = "brand.json"


@dataclass(frozen=True)
class Finding:
    rule_id: str
    path: str
    message: str
    severity: str = "error"


class BrandKitError(Exception):
    pass


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_sha256(kit: dict[str, Any]) -> str:
    payload = json.dumps(kit, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def load_schema() -> dict[str, Any]:
    schema = json.loads(SCHEMA_PATH.read_text())
    Draft202012Validator.check_schema(schema)
    return dict(schema)


def schema_rule(path: str) -> str:
    if path.startswith("palette.") and path.endswith(".hex"):
        return "brand.hex"
    return "brand.schema"


def schema_findings(kit: Any) -> list[Finding]:
    validator = Draft202012Validator(load_schema(), format_checker=FormatChecker())
    findings = []
    for error in validator.iter_errors(kit):
        path = ".".join(map(str, error.absolute_path))
        findings.append(Finding(schema_rule(path), path, error.message))
    return findings


def entries(kit: dict[str, Any], key: str) -> list[dict[str, Any]]:
    value = kit.get(key)
    if not isinstance(value, list):
        return []
    return [entry for entry in value if isinstance(entry, dict)]


def null_paths(value: Any, prefix: str = "") -> list[str]:
    if value is None:
        return [prefix]
    if isinstance(value, dict):
        return [
            path
            for key, child in value.items()
            if key != "approval"
            for path in null_paths(child, f"{prefix}.{key}" if prefix else key)
        ]
    if isinstance(value, list):
        return [
            path
            for index, child in enumerate(value)
            for path in null_paths(child, f"{prefix}.{index}")
        ]
    return []


def unknown_paths(kit: dict[str, Any]) -> list[str]:
    paths = null_paths(kit)
    paths.extend(key for key in LISTABLE_EMPTY if kit.get(key) == [])
    return paths


def missing_findings(kit: dict[str, Any]) -> list[Finding]:
    raw = kit.get("missing")
    listed = {path for path in raw if isinstance(path, str)} if isinstance(raw, list) else set()
    unknown = set(unknown_paths(kit))
    findings = [
        Finding(
            "brand.missing_listed",
            path,
            "Unknown value must be listed in missing rather than left silent or invented",
        )
        for path in sorted(unknown - listed)
    ]
    findings.extend(
        Finding(
            "brand.missing_listed",
            path,
            "Listed as missing but a value is present; remove it from missing",
            "warning",
        )
        for path in sorted(listed - unknown)
    )
    return findings


def contained_file(kit_dir: Path, relative: str) -> Path:
    pure = PurePosixPath(relative)
    if pure.is_absolute() or ".." in pure.parts:
        raise BrandKitError(f"{relative} must stay inside the brand kit directory")
    root = kit_dir.resolve()
    resolved = (root / relative).resolve()
    if not resolved.is_relative_to(root):
        raise BrandKitError(f"{relative} escapes the brand kit directory")
    return resolved


def file_findings(kit_dir: Path, path: str, relative: Any, expected: Any) -> list[Finding]:
    if not isinstance(relative, str):
        return []
    try:
        resolved = contained_file(kit_dir, relative)
    except BrandKitError as error:
        return [Finding("brand.file_contained", path, str(error))]
    if not resolved.is_file():
        return [Finding("brand.file_exists", path, f"{relative} does not exist")]
    if not isinstance(expected, str):
        return [Finding("brand.file_hash", path, f"{relative} has no recorded SHA-256")]
    actual = sha256_file(resolved)
    if actual != expected:
        return [
            Finding(
                "brand.file_hash",
                path,
                f"{relative} SHA-256 is {actual}, kit records {expected}",
            )
        ]
    return []


def asset_findings(kit: dict[str, Any], kit_dir: Path) -> list[Finding]:
    findings: list[Finding] = []
    for index, logo in enumerate(entries(kit, "logos")):
        findings.extend(
            file_findings(kit_dir, f"logos.{index}", logo.get("file"), logo.get("sha256"))
        )
    for index, font in enumerate(entries(kit, "typography")):
        path = f"typography.{index}"
        if font.get("file") is None and font.get("sha256") is not None:
            findings.append(Finding("brand.file_hash", path, "SHA-256 recorded without a font file"))
        findings.extend(file_findings(kit_dir, path, font.get("file"), font.get("sha256")))
        findings.extend(font_license_findings(font, path, kit.get("status")))
    return findings


def font_license_findings(font: dict[str, Any], path: str, status: Any) -> list[Finding]:
    if isinstance(font.get("license"), str) and font["license"].strip():
        return []
    if font.get("file") is not None:
        return [
            Finding(
                "brand.font_license",
                f"{path}.license",
                "A stored font file needs a recorded license before any render uses it",
            )
        ]
    severity = "error" if status == "approved" else "warning"
    return [
        Finding(
            "brand.font_license",
            f"{path}.license",
            f"{font.get('family')} has no recorded license; renders cannot use it yet",
            severity,
        )
    ]


def consistency_findings(kit: dict[str, Any], kit_dir: Path) -> list[Finding]:
    findings: list[Finding] = []
    if kit.get("brand_id") != kit_dir.name:
        findings.append(
            Finding(
                "brand.id_matches_directory",
                "brand_id",
                f"brand_id {kit.get('brand_id')!r} must equal its directory name {kit_dir.name!r}",
            )
        )
    names = [entry.get("name") for entry in entries(kit, "palette")]
    duplicates = sorted({name for name in names if isinstance(name, str) and names.count(name) > 1})
    findings.extend(
        Finding("brand.palette_unique", "palette", f"Duplicate palette name {name}")
        for name in duplicates
    )
    roles = [entry.get("role") for entry in entries(kit, "logos")]
    if roles.count("primary") > 1:
        findings.append(Finding("brand.logo_primary", "logos", "Only one primary logo is allowed"))
    return findings


def validate_kit(kit: Any, kit_dir: Path) -> list[Finding]:
    findings = schema_findings(kit)
    if not isinstance(kit, dict):
        return findings
    findings.extend(missing_findings(kit))
    findings.extend(asset_findings(kit, kit_dir))
    findings.extend(consistency_findings(kit, kit_dir))
    return findings


def read_kit(path: Path) -> Any:
    if path.is_symlink() or not path.is_file():
        raise BrandKitError(f"{path} is not a regular file")
    try:
        return json.loads(path.read_text())
    except ValueError as error:
        raise BrandKitError(f"{path} is not valid JSON: {error}") from error


def blocking(findings: list[Finding]) -> list[Finding]:
    return [finding for finding in findings if finding.severity == "error"]


def scaffold(brand_id: str, name: str | None) -> dict[str, Any]:
    kit: dict[str, Any] = {
        "schema_version": 1,
        "brand_id": brand_id,
        "name": name,
        "source": {"method": "manual", "urls": [], "retrieved_at": None, "authorized_by": None},
        "logos": [],
        "palette": [],
        "typography": [],
        "voice": {"tone": [], "reading_level": None, "do": [], "dont": []},
        "copy_rules": {"banned_words": [], "required_lines": [], "trademark_marks": {}},
        "cta_style": {"shape": None, "case": None, "verbs": []},
        "imagery": {"style_sentence": None, "avoid": []},
        "disclosure": {"ai_label_text": None, "placement": None},
        "missing": [],
        "status": "draft",
        "approval": None,
    }
    kit["missing"] = sorted(unknown_paths(kit))
    return kit


def init_kit(library_root: Path, brand_id: str, name: str | None) -> Path:
    if not BRAND_ID_PATTERN.fullmatch(brand_id) or len(brand_id) > 64:
        raise BrandKitError(f"Invalid brand id {brand_id!r}; use lowercase kebab-case")
    kit_dir = library_root / brand_id
    if kit_dir.exists():
        raise BrandKitError(f"{kit_dir} already exists; edit the existing kit instead")
    (kit_dir / "assets").mkdir(parents=True)
    kit_path = kit_dir / KIT_NAME
    kit_path.write_text(json.dumps(scaffold(brand_id, name), indent=2, ensure_ascii=False) + "\n")
    return kit_path


def summary(kit: dict[str, Any]) -> dict[str, Any]:
    return {
        "brand_id": kit["brand_id"],
        "name": kit["name"],
        "status": kit["status"],
        "pin_sha256": canonical_sha256(kit),
        "palette": {entry["name"]: entry["hex"] for entry in kit["palette"]},
        "fonts": [
            {"role": font["role"], "family": font["family"], "file": font["file"]}
            for font in kit["typography"]
        ],
        "logos": [{"role": logo["role"], "file": logo["file"]} for logo in kit["logos"]],
        "banned_words": kit["copy_rules"]["banned_words"],
        "required_lines": kit["copy_rules"]["required_lines"],
        "trademark_marks": kit["copy_rules"]["trademark_marks"],
        "cta_style": kit["cta_style"],
        "style_sentence": kit["imagery"]["style_sentence"],
        "imagery_avoid": kit["imagery"]["avoid"],
        "disclosure": kit["disclosure"],
        "missing": kit["missing"],
    }


def emit(document: dict[str, Any]) -> None:
    print(json.dumps(document, indent=2, ensure_ascii=False))


def validated(path: Path) -> tuple[dict[str, Any] | None, list[Finding]]:
    kit = read_kit(path)
    findings = validate_kit(kit, path.resolve().parent)
    return (kit if isinstance(kit, dict) and not blocking(findings) else None), findings


def command_validate(args: argparse.Namespace) -> int:
    _, findings = validated(args.kit)
    errors = blocking(findings)
    emit({"ok": not errors, "findings": [asdict(finding) for finding in findings]})
    return int(bool(errors))


def command_pin(args: argparse.Namespace) -> int:
    kit, findings = validated(args.kit)
    if kit is None:
        emit({"ok": False, "findings": [asdict(finding) for finding in blocking(findings)]})
        return 1
    if kit["status"] != "approved" and not args.allow_draft:
        emit({"ok": False, "error": "Only an approved kit can be pinned; pass --allow-draft for prompt-only drafts"})
        return 1
    digest = canonical_sha256(kit)
    matches = args.expect is None or args.expect == digest
    emit({"ok": matches, "brand_id": kit["brand_id"], "status": kit["status"], "sha256": digest, "expected": args.expect})
    return int(not matches)


def command_show(args: argparse.Namespace) -> int:
    kit, findings = validated(args.kit)
    if kit is None:
        emit({"ok": False, "findings": [asdict(finding) for finding in blocking(findings)]})
        return 1
    emit({"ok": True, **summary(kit)})
    return 0


def command_init(args: argparse.Namespace) -> int:
    path = init_kit(args.library_root, args.brand_id, args.name)
    emit({"ok": True, "kit": str(path)})
    return 0


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description="Create, validate, pin and show brand kits")
    commands = root.add_subparsers(dest="command", required=True)
    init = commands.add_parser("init", help="Scaffold a draft brand.json and assets/")
    init.add_argument("library_root", type=Path)
    init.add_argument("brand_id")
    init.add_argument("--name")
    init.set_defaults(handler=command_init)
    validate = commands.add_parser("validate", help="Validate schema, files, hashes and licenses")
    validate.add_argument("kit", type=Path)
    validate.set_defaults(handler=command_validate)
    pin = commands.add_parser("pin", help="Print the canonical SHA-256 a campaign pins")
    pin.add_argument("kit", type=Path)
    pin.add_argument("--expect", help="Exit 1 unless the current pin equals this SHA-256")
    pin.add_argument("--allow-draft", action="store_true")
    pin.set_defaults(handler=command_pin)
    show = commands.add_parser("show", help="Print the consumer view of a valid kit")
    show.add_argument("kit", type=Path)
    show.set_defaults(handler=command_show)
    return root


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        return int(args.handler(args))
    except (BrandKitError, OSError) as error:
        emit({"ok": False, "error": str(error)})
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
