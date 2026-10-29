from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import math
import re
import sys
from collections.abc import Iterable
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any

FIELDS = (
    "ad_name",
    "impressions",
    "views_3s",
    "clicks",
    "spend",
    "conversions",
    "date",
    "reach",
    "frequency",
)
NUMERIC = (
    "impressions",
    "views_3s",
    "clicks",
    "spend",
    "conversions",
    "reach",
    "frequency",
)
SUMMED = ("impressions", "views_3s", "clicks", "spend", "conversions", "reach")
AXES = ("hook", "talent", "product", "outfit", "location", "language", "market", "ratio")
KPIS = {
    "hook_rate": ("views_3s", "impressions", "higher"),
    "ctr": ("clicks", "impressions", "higher"),
    "cvr": ("conversions", "clicks", "higher"),
    "cpa": ("spend", "conversions", "lower"),
}
EMPTY_VALUES = {"", "-", "--", "—", "n/a", "na", "none", "null"}
SPACES = re.compile(r"[\s  ']")
CURRENCY_SYMBOLS = re.compile(r"[$€£¥₹₩₱₫฿₺₽₦₴₪₡¢]")
ABBREVIATED = re.compile(r"^-?[\d.,]+[KkMmBb]$")
NUMBER = re.compile(r"^-?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?$")
GROUPED = {
    ".": re.compile(r"^-?\d{1,3}(?:,\d{3})+(?:\.\d+)?(?:[eE][+-]?\d+)?$"),
    ",": re.compile(r"^-?\d{1,3}(?:\.\d{3})+(?:,\d+)?(?:[eE][+-]?\d+)?$"),
}
DEFAULT_MIN_IMPRESSIONS = 1000.0
DEFAULT_WINDOW_DAYS = 7
GROUP_AXES = ("market", "ratio")
ALL_GROUP = "all"
UNMATCHED_GROUP = "unmatched"
BENCHMARK_NOTE = (
    "Ranked within this account export only. No external or platform benchmark "
    "is implied; vendor benchmarks are not official."
)
MAX_BYTES = 50 * 1024 * 1024


class InputError(ValueError):
    pass


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def strip_currency(value: str, currency: str) -> str:
    value = CURRENCY_SYMBOLS.sub("", value)
    if currency and value.startswith(currency):
        value = value[len(currency) :]
    if currency and value.endswith(currency):
        value = value[: -len(currency)]
    return value


def normalize_separators(value: str, decimal: str) -> str:
    thousands = "," if decimal == "." else "."
    if thousands in value:
        if not GROUPED[decimal].fullmatch(value):
            raise ValueError(f"misplaced thousands separator in {value!r}")
        value = value.replace(thousands, "")
    return value.replace(",", ".") if decimal == "," else value


def parse_number(text: str, decimal: str, currency: str = "") -> float | None:
    value = text.strip()
    if value.lower() in EMPTY_VALUES:
        return None
    negative = value.startswith("(") and value.endswith(")")
    value = strip_currency(SPACES.sub("", value.strip("()")), currency)
    if value.endswith("%"):
        raise ValueError(
            f"percentage {text!r} where a count or amount is expected; map the raw column"
        )
    if ABBREVIATED.fullmatch(value):
        raise ValueError(
            f"abbreviated value {text!r}; export full numbers instead of K/M/B"
        )
    if re.search(r"[A-DF-Za-df-z]", value):
        raise ValueError(
            f"unexpected letters or currency in {text!r} (expected currency: "
            f"{currency or 'none set'})"
        )
    value = normalize_separators(value, decimal)
    if not NUMBER.fullmatch(value):
        raise ValueError(f"not a number: {text!r}")
    number = float(value)
    if not math.isfinite(number):
        raise ValueError(f"not a finite number: {text!r}")
    return -number if negative else number


def parse_date(text: str, date_format: str) -> date | None:
    value = text.strip()
    if not value:
        return None
    try:
        return datetime.strptime(value, date_format).replace(tzinfo=UTC).date()
    except ValueError:
        return date.fromisoformat(value[:10])


def load_mapping(path: Path) -> dict[str, Any]:
    document = read_json(path)
    columns = document.get("columns") if isinstance(document, dict) else None
    if not isinstance(columns, dict) or not all(
        isinstance(value, str) and value for value in columns.values()
    ):
        raise InputError("Mapping needs a 'columns' object of field -> CSV header")
    unknown = sorted(set(columns) - set(FIELDS))
    if unknown:
        raise InputError(f"Unknown mapping fields: {', '.join(unknown)}")
    if "ad_name" not in columns:
        raise InputError("Mapping must name the ad_name column")
    decimal = document.get("decimal", ".")
    if decimal not in (".", ","):
        raise InputError("decimal must be '.' or ','")
    delimiter = document.get("delimiter")
    if delimiter is not None and (
        not isinstance(delimiter, str) or len(delimiter) != 1
    ):
        raise InputError("delimiter must be one character")
    return {
        "columns": columns,
        "decimal": decimal,
        "delimiter": delimiter,
        "date_format": str(document.get("date_format", "%Y-%m-%d")),
        "currency": str(document.get("currency", "")),
    }


def load_variants(path: Path | None) -> dict[str, dict[str, str]]:
    if path is None:
        return {}
    document = read_json(path)
    rows = document.get("rows") if isinstance(document, dict) else document
    if not isinstance(rows, list):
        raise InputError("Variants file must be a plan with 'rows' or a list of names")
    variants: dict[str, dict[str, str]] = {}
    for row in rows:
        if isinstance(row, str):
            variants[row] = {}
        elif isinstance(row, dict) and isinstance(row.get("name"), str):
            values = row.get("values", {})
            variants[row["name"]] = dict(values) if isinstance(values, dict) else {}
        else:
            raise InputError("Each variant must be a name or a row with a name")
    return variants


def read_rows(
    path: Path, delimiter: str | None
) -> tuple[list[str], list[dict[str, str]]]:
    if path.stat().st_size > MAX_BYTES:
        raise InputError("CSV export is larger than 50 MB")
    text = path.read_text(encoding="utf-8-sig")
    if delimiter is None:
        try:
            delimiter = csv.Sniffer().sniff(text[:4096], delimiters=",;\t").delimiter
        except csv.Error:
            delimiter = ","
    reader = csv.DictReader(io.StringIO(text), delimiter=delimiter)
    headers = [header.strip() for header in reader.fieldnames or []]
    if not headers:
        raise InputError("CSV export has no header row")
    reader.fieldnames = headers
    return headers, [dict(row) for row in reader]


def match_variant(ad_name: str, names: Iterable[str]) -> tuple[str | None, list[str]]:
    candidates = sorted(names)
    if ad_name in candidates:
        return ad_name, [ad_name]
    matched = [
        name
        for name in candidates
        if re.search(rf"(?<![A-Za-z0-9]){re.escape(name)}(?![A-Za-z0-9])", ad_name)
    ]
    found = [
        name
        for name in matched
        if not any(name != other and name in other for other in matched)
    ]
    return (found[0] if len(found) == 1 else None), found


def ingest(args: argparse.Namespace) -> dict[str, Any]:
    mapping = load_mapping(args.map)
    variants = load_variants(args.variants)
    headers, rows = read_rows(args.csv, mapping["delimiter"])
    columns = mapping["columns"]
    if columns["ad_name"] not in headers:
        raise InputError(f"Ad name column not found: {columns['ad_name']}")
    present = {field: column for field, column in columns.items() if column in headers}
    records: list[dict[str, Any]] = []
    issues: list[dict[str, Any]] = []
    skipped: list[dict[str, Any]] = []
    unmatched: set[str] = set()
    ambiguous: dict[str, list[str]] = {}
    for line, row in enumerate(rows, start=2):
        ad_name = (row.get(present["ad_name"]) or "").strip()
        if not ad_name:
            skipped.append({"line": line, "reason": "empty ad name"})
            continue
        record: dict[str, Any] = {"line": line, "ad_name": ad_name}
        for field in NUMERIC:
            record[field] = None
            if field not in present:
                continue
            raw = row.get(present[field]) or ""
            try:
                record[field] = parse_number(
                    raw, mapping["decimal"], mapping["currency"]
                )
            except ValueError as error:
                issues.append({"line": line, "field": field, "problem": str(error)})
        record["date"] = None
        if "date" in present:
            raw = row.get(present["date"]) or ""
            try:
                parsed = parse_date(raw, mapping["date_format"])
                record["date"] = parsed.isoformat() if parsed else None
            except ValueError:
                issues.append(
                    {
                        "line": line,
                        "field": "date",
                        "problem": f"unreadable date: {raw!r}",
                    }
                )
        variant, found = match_variant(ad_name, variants) if variants else (None, [])
        record["variant"] = variant
        if variant is None and len(found) > 1:
            ambiguous[ad_name] = found
        elif variant is None:
            unmatched.add(ad_name)
        records.append(record)
    matched = {record["variant"] for record in records if record["variant"]}
    return {
        "schema_version": 1,
        "source": {
            "file": args.csv.name,
            "sha256": hashlib.sha256(args.csv.read_bytes()).hexdigest(),
            "data_rows": len(rows),
        },
        "currency": mapping["currency"],
        "columns": present,
        "missing_columns": sorted(set(columns) - set(present)),
        "unmapped_fields": [field for field in FIELDS if field not in columns],
        "variants": variants,
        "records": records,
        "unmatched_ads": sorted(unmatched),
        "ambiguous_ads": ambiguous,
        "variants_without_data": sorted(set(variants) - matched),
        "skipped_rows": skipped,
        "issues": issues,
    }


def entity_key(record: dict[str, Any]) -> tuple[str, bool]:
    variant = record.get("variant")
    return (variant, True) if variant else (record["ad_name"], False)


def total(records: list[dict[str, Any]], field: str) -> float | None:
    values = [record[field] for record in records if record.get(field) is not None]
    return sum(values) if values else None


def ratio(numerator: float | None, denominator: float | None) -> float | None:
    if numerator is None or not denominator:
        return None
    return numerator / denominator


def kpi_values(totals: dict[str, float | None]) -> dict[str, float | None]:
    return {
        name: ratio(totals[numerator], totals[denominator])
        for name, (numerator, denominator, _) in KPIS.items()
    }


def aggregate(records: list[dict[str, Any]]) -> dict[str, float | None]:
    totals = {field: total(records, field) for field in SUMMED}
    totals["frequency"] = frequency(records, totals)
    return {**totals, **kpi_values(totals)}


def frequency(
    records: list[dict[str, Any]], totals: dict[str, float | None]
) -> float | None:
    if records and all(record.get("reach") for record in records):
        return ratio(totals["impressions"], totals["reach"])
    if not records or any(
        record.get("frequency") is None or record.get("impressions") is None
        for record in records
    ):
        return None
    weight = sum(record["impressions"] for record in records)
    if not weight:
        return None
    return (
        sum(record["frequency"] * record["impressions"] for record in records) / weight
    )


def group(
    records: list[dict[str, Any]],
) -> dict[tuple[str, bool], list[dict[str, Any]]]:
    groups: dict[tuple[str, bool], list[dict[str, Any]]] = {}
    for record in records:
        groups.setdefault(entity_key(record), []).append(record)
    return groups


def ineligible_reason(
    metrics: dict[str, Any], kpi: str, min_impressions: float
) -> str | None:
    numerator, denominator, _ = KPIS[kpi]
    if metrics[numerator] is None or metrics[denominator] is None:
        return f"missing {numerator if metrics[numerator] is None else denominator}"
    if not metrics[denominator]:
        return f"zero {denominator}"
    if metrics["impressions"] is None and min_impressions > 0:
        return "missing impressions for the impression floor; set --min-impressions 0 to rank without it"
    if (metrics["impressions"] or 0) < min_impressions:
        return f"fewer than {min_impressions:g} impressions"
    return None


def comparable_group(
    key: str, matched: bool, variants: dict[str, Any], across_groups: bool
) -> str:
    if across_groups:
        return ALL_GROUP
    if not matched:
        return UNMATCHED_GROUP
    values = variants.get(key) or {}
    return ",".join(f"{axis}={values.get(axis) or '-'}" for axis in GROUP_AXES)


def rank(
    metrics_document: dict[str, Any],
    kpi: str,
    min_impressions: float,
    across_groups: bool = False,
) -> dict[str, Any]:
    variants = metrics_document.get("variants") or {}
    entities: list[dict[str, Any]] = []
    for (key, matched), records in group(metrics_document["records"]).items():
        metrics = aggregate(records)
        entities.append(
            {
                "key": key,
                "matched": matched,
                "group": comparable_group(key, matched, variants, across_groups),
                "rows": len(records),
                **metrics,
                "reason": ineligible_reason(metrics, kpi, min_impressions),
            }
        )
    direction = KPIS[kpi][2]
    eligible = [entity for entity in entities if entity["reason"] is None]
    eligible.sort(
        key=lambda entity: (
            entity["group"],
            -entity[kpi] if direction == "higher" else entity[kpi],
            entity["key"],
        )
    )
    groups: dict[str, list[dict[str, Any]]] = {}
    for entity in eligible:
        members = groups.setdefault(entity["group"], [])
        members.append(entity)
        entity["rank"] = len(members)
        entity["low_volume"] = (entity["impressions"] or 0) < DEFAULT_MIN_IMPRESSIONS
        del entity["reason"]
    return {
        "kpi": kpi,
        "direction": direction,
        "min_impressions": min_impressions,
        "low_volume_below": DEFAULT_MIN_IMPRESSIONS,
        "currency": metrics_document.get("currency", ""),
        "note": BENCHMARK_NOTE,
        "group_by": [] if across_groups else list(GROUP_AXES),
        "groups": [
            {"group": name, "ranked": len(members), "leader": members[0]["key"]}
            for name, members in groups.items()
        ],
        "ranked": eligible,
        "not_ranked": sorted(
            (entity for entity in entities if entity.get("reason")),
            key=lambda entity: entity["key"],
        ),
        "unmatched_ads": metrics_document.get("unmatched_ads", []),
        "variants_without_data": metrics_document.get("variants_without_data", []),
    }


def windows(
    records: list[dict[str, Any]], start: date, days: int
) -> list[dict[str, Any]]:
    buckets: dict[int, list[dict[str, Any]]] = {}
    for record in records:
        offset = (date.fromisoformat(record["date"]) - start).days // days
        buckets.setdefault(offset, []).append(record)
    result = []
    for offset in sorted(buckets):
        metrics = aggregate(buckets[offset])
        result.append(
            {
                "window": offset,
                "from": date.fromordinal(start.toordinal() + offset * days).isoformat(),
                "impressions": metrics["impressions"],
                "frequency": metrics["frequency"],
                "ctr": metrics["ctr"],
                "hook_rate": metrics["hook_rate"],
            }
        )
    return result


def fatigue_status(series: list[dict[str, Any]]) -> tuple[str, str]:
    usable = [window for window in series if window["impressions"]]
    if len(usable) < 2:
        return "insufficient_data", "fewer than two dated windows with impressions"
    previous, latest = usable[-2], usable[-1]
    if previous["frequency"] is None or latest["frequency"] is None:
        return "insufficient_data", "no reach or frequency column for both windows"
    falling = [
        name
        for name in ("ctr", "hook_rate")
        if previous[name] is not None
        and latest[name] is not None
        and latest[name] < previous[name]
    ]
    if latest["frequency"] > previous["frequency"] and falling:
        return "fatigued", f"frequency rose while {' and '.join(falling)} fell"
    if previous["ctr"] is None and previous["hook_rate"] is None:
        return "insufficient_data", "no clicks or 3-second views to compare"
    return "stable", "no rising frequency with a falling rate in the latest window"


def fatigue(metrics_document: dict[str, Any], days: int) -> dict[str, Any]:
    dated = [record for record in metrics_document["records"] if record.get("date")]
    entities = []
    if dated:
        start = min(date.fromisoformat(record["date"]) for record in dated)
        for (key, matched), records in sorted(group(dated).items()):
            series = windows(records, start, days)
            status, reason = fatigue_status(series)
            entities.append(
                {
                    "key": key,
                    "matched": matched,
                    "status": status,
                    "reason": reason,
                    "windows": series,
                }
            )
    undated = sorted(
        {entity_key(record)[0] for record in metrics_document["records"]}
        - {e["key"] for e in entities}
    )
    return {
        "window_days": days,
        "rule": "Latest window vs previous: frequency up while CTR or hook rate down",
        "entities": entities,
        "undated": undated,
        "note": "Frequency from summed row reach is an approximation; an exported frequency column per window is more exact.",
    }


def parse_axis(text: str) -> tuple[str, list[str]]:
    axis, separator, raw = text.partition("=")
    values = [value.strip() for value in raw.split(",") if value.strip()]
    if not separator or axis not in AXES or not values:
        raise InputError(
            f"Expected --axis <axis>=<value>[,<value>...] with a known axis: {text}"
        )
    if len(set(values)) != len(values):
        raise InputError("Axis values must be unique")
    return axis, values


def matched_winners(ranking: dict[str, Any], chosen: str | None) -> list[dict[str, Any]]:
    winners = [entity for entity in ranking["ranked"] if entity["matched"]]
    if not winners:
        raise InputError("No matched variant has enough data to choose a winner")
    names = sorted({entity["group"] for entity in winners})
    if chosen is not None:
        if chosen not in names:
            raise InputError(
                f"Group {chosen} has no ranked matched variant; choose one of: "
                + "; ".join(names)
            )
        return [entity for entity in winners if entity["group"] == chosen]
    if len(names) > 1:
        raise InputError(
            "Matched variants run in different markets or ratios and are ranked "
            "separately; pass --group with one of: "
            + "; ".join(names)
            + " (or --across-groups to compare them anyway)"
        )
    return winners


def winner_fatigue(
    metrics_document: dict[str, Any], winner: str, days: int
) -> dict[str, str]:
    report = fatigue(metrics_document, days)
    for entity in report["entities"]:
        if entity["key"] == winner:
            return {"status": entity["status"], "reason": entity["reason"]}
    return {"status": "insufficient_data", "reason": "no dated rows for the winner"}


def next_matrix_warnings(
    leader: dict[str, Any], fatigue_state: dict[str, str], across_groups: bool
) -> list[str]:
    winner = leader["key"]
    warnings: list[str] = [
        (
            "Fill hero.decision_ref, hero.take_file, hero.take and hero.sha256 from "
            "the approved winner before variant_matrix.py register"
        )
    ]
    if leader["low_volume"]:
        warnings.append(
            f"{winner} won on low volume ({leader['impressions'] or 0:g} "
            f"impressions, below {DEFAULT_MIN_IMPRESSIONS:g}); let the test run "
            "longer before treating it as the winner"
        )
    if fatigue_state["status"] == "fatigued":
        warnings.append(
            f"{winner} is fatigued ({fatigue_state['reason']}); its totals may "
            "overstate current performance, so confirm the latest window or refresh "
            "the creative before building the next round on it"
        )
    if across_groups:
        warnings.append(
            "Ranked across markets and ratios; audiences and placements differ, so "
            "the winner may not carry over to the other groups"
        )
    return warnings


def next_matrix(args: argparse.Namespace) -> dict[str, Any]:
    if args.window_days < 1:
        raise InputError("--window-days must be at least 1")
    if args.group is not None and args.across_groups:
        raise InputError("Pass either --group or --across-groups, not both")
    metrics_document = read_json(args.metrics)
    matrix = read_json(args.matrix)
    if not isinstance(matrix, dict) or not isinstance(matrix.get("hero"), dict):
        raise InputError("Matrix file is not a variant matrix")
    ranking = rank(metrics_document, args.kpi, args.min_impressions, args.across_groups)
    winners = matched_winners(ranking, args.group)
    winner = winners[0]["key"]
    values = dict(metrics_document.get("variants", {}).get(winner) or {})
    if not values:
        raise InputError(
            "Winner has no axis values; ingest with --variants <plan.json>"
        )
    axis, levels = parse_axis(args.axis)
    naming = matrix.get("naming")
    if isinstance(naming, str) and f"{{{axis}}}" not in naming:
        raise InputError(
            f"The matrix naming has no {{{axis}}} placeholder; add it so the new "
            "variants get distinct names"
        )
    if axis not in values:
        if not args.hero_value:
            raise InputError(f"{axis} is new to this campaign; pass --hero-value")
        values[axis] = args.hero_value
    tested = sorted(set(matrix.get("axes", {})))
    draft = {
        "schema_version": 1,
        "status": "draft",
        "campaign": matrix["campaign"],
        "concept": matrix["concept"],
        "hero": {
            "variant": winner,
            "shot_id": None,
            "take": None,
            "take_file": None,
            "sha256": None,
            "decision_ref": None,
            "values": values,
        },
        "axes": {axis: levels},
        "strategy": "one_axis_at_a_time",
        "max_variants": matrix["max_variants"],
        "version": min(int(matrix.get("version", 1)) + 1, 99),
        "notes": (
            f"Draft from the performance loop: {winner} ranked first by {args.kpi} within "
            f"this account, comparison group {winners[0]['group']}. Kept axes: {', '.join(tested) or 'none'}. Testing: {axis}. "
            "Bind hero to the approved winning take before planning."
        ),
    }
    for key in ("naming", "unit_cost_usd"):
        if key in matrix:
            draft[key] = matrix[key]
    target = args.out
    if target.is_symlink() or target.exists():
        raise InputError(f"Refusing to overwrite: {target}")
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("x", encoding="utf-8") as handle:
        handle.write(json.dumps(draft, indent=2, ensure_ascii=False) + "\n")
    fatigue_state = winner_fatigue(metrics_document, winner, args.window_days)
    return {
        "winner": winner,
        "group": winners[0]["group"],
        "kpi": args.kpi,
        "kpi_value": winners[0][args.kpi],
        "min_impressions": args.min_impressions,
        "winner_fatigue": fatigue_state,
        "warnings": next_matrix_warnings(winners[0], fatigue_state, args.across_groups),
        "draft": str(target),
        "matrix": draft,
    }


def write_or_print(document: dict[str, Any], out: Path | None) -> dict[str, Any]:
    if out is None:
        return document
    if out.is_symlink():
        raise InputError(f"Refusing to write through a symlink: {out}")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        json.dumps(document, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    listed = ("unmatched_ads", "ambiguous_ads", "variants_without_data", "skipped_rows")
    return {
        "written": str(out),
        "records": len(document["records"]),
        "missing_columns": document["missing_columns"],
        "issues": len(document["issues"]),
        **{key: document[key] for key in listed},
        "counts": {
            "records": len(document["records"]),
            **{key: len(document[key]) for key in listed},
            "issues": len(document["issues"]),
        },
    }


def parser() -> argparse.ArgumentParser:
    cli = argparse.ArgumentParser(
        description="Rank exported ad results by variant; no platform API calls"
    )
    commands = cli.add_subparsers(dest="command", required=True)
    ingest_cli = commands.add_parser("ingest")
    ingest_cli.add_argument("csv", type=Path)
    ingest_cli.add_argument("--map", type=Path, required=True)
    ingest_cli.add_argument("--variants", type=Path)
    ingest_cli.add_argument("--out", type=Path)
    rank_cli = commands.add_parser("rank")
    rank_cli.add_argument("metrics", type=Path)
    rank_cli.add_argument("--kpi", choices=sorted(KPIS), required=True)
    rank_cli.add_argument(
        "--min-impressions", type=float, default=DEFAULT_MIN_IMPRESSIONS
    )
    rank_cli.add_argument("--across-groups", action="store_true")
    fatigue_cli = commands.add_parser("fatigue")
    fatigue_cli.add_argument("metrics", type=Path)
    fatigue_cli.add_argument("--window-days", type=int, default=DEFAULT_WINDOW_DAYS)
    next_cli = commands.add_parser("next-matrix")
    next_cli.add_argument("metrics", type=Path)
    next_cli.add_argument("--matrix", type=Path, required=True)
    next_cli.add_argument("--kpi", choices=sorted(KPIS), required=True)
    next_cli.add_argument("--axis", required=True)
    next_cli.add_argument("--hero-value")
    next_cli.add_argument(
        "--min-impressions", type=float, default=DEFAULT_MIN_IMPRESSIONS
    )
    next_cli.add_argument("--out", type=Path, required=True)
    next_cli.add_argument("--group")
    next_cli.add_argument("--across-groups", action="store_true")
    next_cli.add_argument("--window-days", type=int, default=DEFAULT_WINDOW_DAYS)
    return cli


def run(args: argparse.Namespace) -> dict[str, Any]:
    if args.command == "ingest":
        return write_or_print(ingest(args), args.out)
    if args.command == "next-matrix":
        return next_matrix(args)
    metrics_document = read_json(args.metrics)
    if not isinstance(metrics_document, dict) or not isinstance(
        metrics_document.get("records"), list
    ):
        raise InputError("Metrics file must come from the ingest command")
    if args.command == "rank":
        return rank(
            metrics_document, args.kpi, args.min_impressions, args.across_groups
        )
    if args.window_days < 1:
        raise InputError("--window-days must be at least 1")
    return fatigue(metrics_document, args.window_days)


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        result = run(args)
    except (OSError, ValueError, TypeError, KeyError, UnicodeError, csv.Error) as error:
        print(json.dumps({"ok": False, "error": str(error)}, indent=2))
        return 1
    print(json.dumps({"ok": True, **result}, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
