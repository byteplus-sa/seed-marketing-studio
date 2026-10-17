from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
from fractions import Fraction
from pathlib import Path, PurePosixPath
from typing import Any

from jsonschema import Draft202012Validator

SCHEMA_PATH = Path(__file__).resolve().parents[1] / "references/checks.schema.json"
CHECK_RULES = {
    "product_reveal": None,
    "logo_legible": None,
    "opening_change": None,
    "cta_safe_zone": "ad.safe_zone",
    "sound_off_readable": "ad.safe_zone",
    "claims_supported": "ad.claims_supported",
    "brand_copy": "brand.copy_rules",
    "speech_intelligible": None,
    "loudness_target": None,
    "disclosure_recorded": "ad.disclosure_recorded",
}
FRAME_EVIDENCE = {
    "product_reveal",
    "logo_legible",
    "opening_change",
    "cta_safe_zone",
    "sound_off_readable",
}
MAY_NOT_APPLY = {
    "logo_legible",
    "cta_safe_zone",
    "sound_off_readable",
    "claims_supported",
    "brand_copy",
    "speech_intelligible",
}
DISCLOSURE_DECISIONS = {"disclose", "not_required", "declined"}
DEFAULT_REVEAL_S = 2.0
DEFAULT_OPENING_S = 2.0
DEFAULT_LOUDNESS = {"integrated_lufs": -16.0, "true_peak_dbtp": -1.5, "tolerance_lu": 1.0}
FRAME_PATTERN = "frame_%05d.png"
MAX_INTERVAL_S = 10.0


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def frame_rate(every: float) -> str:
    if not 0 < every <= MAX_INTERVAL_S:
        raise ValueError(f"--every must be greater than 0 and at most {MAX_INTERVAL_S}")
    rate = 1 / Fraction(str(every)).limit_denominator(1000)
    return f"{rate.numerator}/{rate.denominator}"


def frame_command(
    video: Path, out: Path, every: float, until: float | None = None
) -> list[str]:
    command = ["ffmpeg", "-v", "error", "-nostdin", "-y", "-i", str(video)]
    if until is not None:
        if until <= 0:
            raise ValueError("--until must be greater than 0")
        command += ["-t", f"{until:g}"]
    command += [
        "-vf",
        f"fps={frame_rate(every)}",
        "-start_number",
        "0",
        str(out / FRAME_PATTERN),
    ]
    return command


def sample_frames(
    video: Path, out: Path, every: float, until: float | None
) -> dict[str, Any]:
    if not video.is_file():
        raise ValueError(f"video not found: {video}")
    if shutil.which("ffmpeg") is None:
        raise RuntimeError("ffmpeg is required to sample frames")
    command = frame_command(video, out, every, until)
    out.mkdir(parents=True, exist_ok=True)
    if any(out.glob("frame_*.png")):
        raise ValueError(f"{out} already holds sampled frames; use an empty folder")
    subprocess.run(command, check=True, capture_output=True, text=True)
    files = sorted(out.glob("frame_*.png"))
    if not files:
        raise RuntimeError("ffmpeg produced no frames")
    return {
        "video": str(video),
        "video_sha256": sha256(video),
        "every_s": every,
        "frames": [
            {"path": f"{out.name}/{path.name}", "time_s": round(index * every, 3)}
            for index, path in enumerate(files)
        ],
    }


def confined(base: Path, relative: str, label: str) -> Path:
    pure = PurePosixPath(relative)
    if pure.is_absolute() or Path(relative).is_absolute() or ".." in pure.parts:
        raise ValueError(f"{label} must stay inside the check folder: {relative}")
    root = base.resolve()
    resolved = (root / relative).resolve()
    if not resolved.is_relative_to(root):
        raise ValueError(f"{label} escapes the check folder: {relative}")
    return resolved


def schema_errors(document: Any) -> list[str]:
    validator = Draft202012Validator(json.loads(SCHEMA_PATH.read_text()))
    return [
        f"{'/'.join(str(part) for part in error.absolute_path) or '<root>'}: {error.message}"
        for error in sorted(validator.iter_errors(document), key=lambda item: list(item.absolute_path))
    ]


def coverage_errors(checks: list[dict[str, Any]]) -> list[str]:
    seen = [check["id"] for check in checks]
    errors = [f"{name}: missing check" for name in CHECK_RULES if name not in seen]
    errors += [f"{name}: listed more than once" for name in sorted(set(seen)) if seen.count(name) > 1]
    return errors


def evidence_errors(check: dict[str, Any], duration: float, base: Path) -> list[str]:
    name, status = check["id"], check["status"]
    timestamps = check.get("timestamps", [])
    errors = [f"{name}: timestamp {value} is after the {duration} s cut" for value in timestamps if value > duration]
    if status in ("pass", "fail") and name in FRAME_EVIDENCE:
        if not timestamps:
            errors.append(f"{name}: {status} needs timestamps")
        if not check.get("frames"):
            errors.append(f"{name}: {status} needs frame paths")
    for frame in check.get("frames", []):
        try:
            if not confined(base, frame, f"{name} frame").is_file():
                errors.append(f"{name}: frame not found: {frame}")
        except ValueError as error:
            errors.append(str(error))
    return errors


def timing_errors(check: dict[str, Any], limit: float) -> list[str]:
    if check["status"] != "pass" or not check.get("timestamps"):
        return []
    first = min(check["timestamps"])
    if first <= limit:
        return []
    return [f"{check['id']}: pass needs evidence at or before {limit} s, first is {first} s"]


def loudness_errors(check: dict[str, Any], target: dict[str, float]) -> list[str]:
    if check["status"] not in ("pass", "fail"):
        return []
    measured = check.get("measured")
    if measured is None:
        return [f"loudness_target: {check['status']} needs measured values"]
    within = (
        abs(measured["integrated_lufs"] - target["integrated_lufs"]) <= target["tolerance_lu"]
        and measured["true_peak_dbtp"] <= target["true_peak_dbtp"]
    )
    expected = "pass" if within else "fail"
    if check["status"] == expected:
        return []
    return [f"loudness_target: measured values say {expected}, recorded {check['status']}"]


def disclosure_errors(
    check: dict[str, Any], document: dict[str, Any], base: Path
) -> list[str]:
    status = check["status"]
    if not document["paid"]:
        if status != "not_applicable":
            return ["disclosure_recorded: unpaid deliverables stay label-free and record not_applicable"]
        return []
    if status == "not_applicable":
        return ["disclosure_recorded: a paid deliverable needs a recorded disclosure decision"]
    if status != "pass":
        return []
    reference = check.get("disclosure_record")
    if not reference:
        return ["disclosure_recorded: pass needs disclosure_record"]
    try:
        path = confined(base, reference, "disclosure_record")
        record = json.loads(path.read_text())
    except (OSError, ValueError) as error:
        return [f"disclosure_recorded: unreadable record: {error}"]
    errors = []
    if not isinstance(record, dict):
        return ["disclosure_recorded: record must be a JSON object"]
    if record.get("deliverable_id") != document["deliverable_id"]:
        errors.append("disclosure_recorded: record is for another deliverable")
    if record.get("decided_by") != "user" or not str(record.get("user_quote", "")).strip():
        errors.append("disclosure_recorded: decision must be the user's, with their words quoted")
    if record.get("decision") not in DISCLOSURE_DECISIONS:
        errors.append("disclosure_recorded: decision must be disclose, not_required or declined")
    return errors


def check_errors(check: dict[str, Any], document: dict[str, Any], base: Path) -> list[str]:
    name, status = check["id"], check["status"]
    errors = evidence_errors(check, document["duration_s"], base)
    if status == "not_applicable" and name not in MAY_NOT_APPLY | {"disclosure_recorded"}:
        errors.append(f"{name}: not_applicable is not allowed for this check")
    if name == "product_reveal":
        errors += timing_errors(check, document.get("reveal_time_s", DEFAULT_REVEAL_S))
    if name == "opening_change":
        errors += timing_errors(check, document.get("opening_window_s", DEFAULT_OPENING_S))
    if name == "loudness_target":
        errors += loudness_errors(check, document.get("loudness_target", DEFAULT_LOUDNESS))
    if name == "disclosure_recorded":
        errors += disclosure_errors(check, document, base)
    return errors


def validate(document: Any, base: Path) -> list[str]:
    errors = schema_errors(document)
    if errors:
        return errors
    errors = coverage_errors(document["checks"])
    for check in document["checks"]:
        errors += check_errors(check, document, base)
    return errors


def verdict(checks: list[dict[str, Any]]) -> str:
    statuses = {check["status"] for check in checks}
    if "fail" in statuses:
        return "fail"
    if "needs_human" in statuses:
        return "needs_human"
    return "pass"


def summarize(document: dict[str, Any]) -> dict[str, Any]:
    checks = document["checks"]
    order = list(CHECK_RULES)
    ordered = sorted(checks, key=lambda check: order.index(check["id"]))
    return {
        "schema_version": 1,
        "deliverable_id": document["deliverable_id"],
        "video_sha256": document["video_sha256"],
        "paid": document["paid"],
        "placement": document["placement"],
        "verdict": verdict(checks),
        "counts": {
            status: sum(1 for check in checks if check["status"] == status)
            for status in ("pass", "fail", "needs_human", "not_applicable")
        },
        "checks": [
            {
                "id": check["id"],
                "rule_id": CHECK_RULES[check["id"]],
                "status": check["status"],
                "evidence": check["evidence"],
                "timestamps": check.get("timestamps", []),
                "frames": check.get("frames", []),
            }
            for check in ordered
        ],
    }


def report(path: Path) -> tuple[int, dict[str, Any]]:
    try:
        document = json.loads(path.read_text())
    except (OSError, ValueError) as error:
        return 2, {"valid": False, "errors": [f"cannot read {path}: {error}"]}
    errors = validate(document, path.parent)
    if errors:
        return 2, {"valid": False, "errors": errors}
    summary = {"valid": True, **summarize(document)}
    return (0 if summary["verdict"] == "pass" else 1), summary


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Pre-spend ad creative checklist: frame sampling and report validation"
    )
    commands = parser.add_subparsers(dest="command", required=True)
    frames = commands.add_parser("frames", help="Sample frames from a cut with ffmpeg")
    frames.add_argument("video", type=Path)
    frames.add_argument("--out", type=Path, required=True)
    frames.add_argument("--every", type=float, default=0.5)
    frames.add_argument("--until", type=float)
    summary = commands.add_parser("report", help="Validate and summarize a filled checklist")
    summary.add_argument("checks", type=Path)
    summary.add_argument("--out", type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    arguments = build_parser().parse_args(argv)
    if arguments.command == "report":
        code, result = report(arguments.checks)
        text = json.dumps(result, indent=2)
        if arguments.out is not None and result.get("valid"):
            arguments.out.write_text(text + "\n")
        print(text)
        return code
    try:
        result = sample_frames(arguments.video, arguments.out, arguments.every, arguments.until)
    except (OSError, RuntimeError, ValueError, subprocess.SubprocessError) as error:
        print(json.dumps({"error": str(error)}), file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
