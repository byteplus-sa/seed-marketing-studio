from __future__ import annotations

import argparse
import itertools
import json
import math
import re
import sys
from dataclasses import asdict
from pathlib import Path
from typing import Any

from validate_request import Finding, schema_findings

AXES = ("hook", "talent", "product", "outfit", "location", "language", "ratio")
SWAP_AXES = ("talent", "product", "outfit", "location")
RECAST_TRIGGER = {"talent", "location"}
AD_GROUP_CREATIVES = 5
PLACEHOLDER = re.compile(r"\{([a-z]+)\}")
STEP_SKILLS = {
    "object-swap": ["seedance-object-swap"],
    "motion-recast": ["seedance-motion-recast"],
    "hook-opening": ["ugc-ad-modes", "seedance-prompt-25"],
    "language-dub": ["audio-dubbing", "seedance-prompt-25-dialogue", "ad-captions"],
    "ratio-reframe": ["ad-delivery-formats"],
}
STEP_OUTPUT_SUFFIX = {"language-dub": ".wav"}
REGISTER_PROCEDURE = [
    "Write and freeze the row prompt at the --prompt path",
    "Run hash_command and bind prompt-review to the printed request_sha256",
    "Resolve CRITICAL and MAJOR findings, then run register_command",
    "Submit only a registered operation, in 'after' order, under the project approval mode",
]
PROVIDER_ROUTES = {"object-swap", "motion-recast", "hook-opening", "language-dub"}


def slug(value: str) -> str:
    text = value.lower().replace(":", "x")
    return re.sub(r"[^a-z0-9]+", "-", text).strip("-")


def active_axes(matrix: dict[str, Any]) -> list[str]:
    return [axis for axis in AXES if axis in matrix["axes"]]


def named_axes(matrix: dict[str, Any]) -> list[str]:
    fixed = matrix["hero"]["values"]
    return [axis for axis in AXES if axis in fixed or axis in matrix["axes"]]


def default_naming(axes: list[str]) -> str:
    return "_".join(
        ["{campaign}", "{concept}", *(f"{{{axis}}}" for axis in axes), "v{nn}"]
    )


def semantic_findings(matrix: dict[str, Any]) -> list[Finding]:
    findings: list[Finding] = []
    axes = active_axes(matrix)
    hero_values = matrix["hero"]["values"]
    for axis in axes:
        if axis not in hero_values:
            findings.append(
                Finding(
                    "matrix.hero_values",
                    f"hero.values has no value for axis {axis}",
                    "hero.values",
                )
            )
    named = named_axes(matrix)
    allowed = {"campaign", "concept", "nn", *named}
    naming = matrix.get("naming", default_naming(named))
    unknown = sorted(set(PLACEHOLDER.findall(naming)) - allowed)
    if unknown:
        findings.append(
            Finding(
                "matrix.naming",
                f"Unknown naming placeholders: {', '.join(unknown)}",
                "naming",
            )
        )
    return findings


def load_matrix(path: Path) -> tuple[dict[str, Any], list[Finding]]:
    document = json.loads(path.read_text(encoding="utf-8"))
    findings = schema_findings(document, "variant-matrix.schema.json")
    if findings:
        return document, findings
    return document, semantic_findings(document)


def levels(matrix: dict[str, Any], axis: str) -> list[str]:
    hero = matrix["hero"]["values"][axis]
    return [hero, *(value for value in matrix["axes"][axis] if value != hero)]


def combinations(matrix: dict[str, Any]) -> list[dict[str, str]]:
    axes = active_axes(matrix)
    hero = {axis: matrix["hero"]["values"][axis] for axis in named_axes(matrix)}
    if matrix["strategy"] == "full_factorial":
        grid = itertools.product(*(levels(matrix, axis) for axis in axes))
        return [{**hero, **dict(zip(axes, values, strict=True))} for values in grid]
    rows = [hero]
    for axis in axes:
        rows.extend({**hero, axis: value} for value in levels(matrix, axis)[1:])
    return rows


def plan_steps(changed: list[str]) -> list[dict[str, Any]]:
    swaps = [axis for axis in SWAP_AXES if axis in changed]
    routed: list[tuple[str, list[str]]] = []
    if RECAST_TRIGGER <= set(swaps):
        routed.append(("motion-recast", swaps))
    else:
        routed.extend(("object-swap", [axis]) for axis in swaps)
    if "hook" in changed:
        routed.append(("hook-opening", ["hook"]))
    if "language" in changed:
        routed.append(("language-dub", ["language"]))
    if "ratio" in changed:
        routed.append(("ratio-reframe", ["ratio"]))
    return [
        {
            "route": route,
            "axes": axes,
            "skills": STEP_SKILLS[route],
            "provider_operation": route in PROVIDER_ROUTES,
        }
        for route, axes in routed
    ]


def variant_name(matrix: dict[str, Any], values: dict[str, str]) -> str:
    fields = {
        "campaign": matrix["campaign"],
        "concept": matrix["concept"],
        "nn": f"{matrix.get('version', 1):02d}",
        **{axis: slug(value) for axis, value in values.items()},
    }
    naming = matrix.get("naming", default_naming(named_axes(matrix)))
    return PLACEHOLDER.sub(lambda match: fields[match.group(1)], naming)


def expand(matrix: dict[str, Any]) -> list[dict[str, Any]]:
    hero = {axis: matrix["hero"]["values"][axis] for axis in named_axes(matrix)}
    rows: list[dict[str, Any]] = []
    for index, values in enumerate(combinations(matrix)):
        changed = [axis for axis in values if values[axis] != hero[axis]]
        rows.append(
            {
                "index": index,
                "name": variant_name(matrix, values),
                "role": "variant" if changed else "hero",
                "values": values,
                "changed_axes": changed,
                "steps": plan_steps(changed),
            }
        )
    return rows


def gate_findings(matrix: dict[str, Any], rows: list[dict[str, Any]]) -> list[Finding]:
    findings: list[Finding] = []
    names = [row["name"] for row in rows]
    duplicates = sorted({name for name in names if names.count(name) > 1})
    if duplicates:
        findings.append(
            Finding(
                "matrix.unique_names",
                f"Variant names collide: {', '.join(duplicates)}",
                "naming",
            )
        )
    count = sum(row["role"] == "variant" for row in rows)
    if count == 0:
        findings.append(
            Finding("matrix.empty", "No axis value differs from the hero", "axes")
        )
    if count > matrix["max_variants"]:
        findings.append(
            Finding(
                "matrix.max_variants",
                f"{count} variants exceed max_variants {matrix['max_variants']}",
                "max_variants",
            )
        )
    if count > AD_GROUP_CREATIVES:
        findings.append(
            Finding(
                "matrix.ad_group_size",
                f"{count} variants; plan them across ad groups of 3-5 creatives",
                "axes",
                "warning",
            )
        )
    return findings


def parse_unit_costs(items: list[str]) -> dict[str, float]:
    costs: dict[str, float] = {}
    for item in items:
        axis, separator, value = item.partition("=")
        if not separator or axis not in AXES:
            raise ValueError(
                f"Expected --unit-cost <axis>=<usd> with a known axis: {item}"
            )
        amount = float(value)
        if not math.isfinite(amount) or amount < 0:
            raise ValueError(f"Unit cost must be a finite non-negative number: {item}")
        costs[axis] = amount
    return costs


def apply_costs(
    matrix: dict[str, Any], rows: list[dict[str, Any]], overrides: dict[str, float]
) -> tuple[dict[str, Any], list[Finding]]:
    units = {**matrix.get("unit_cost_usd", {}), **overrides}
    findings: list[Finding] = []
    missing = sorted(
        {axis for row in rows for axis in row["changed_axes"] if axis not in units},
        key=AXES.index,
    )
    if missing:
        findings.append(
            Finding(
                "cost.unit_missing",
                f"No unit cost for axes: {', '.join(missing)}",
                "unit_cost_usd",
            )
        )
        return {}, findings
    total = 0.0
    for row in rows:
        row["estimated_cost_usd"] = round(
            sum(units[axis] for axis in row["changed_axes"]), 2
        )
        total += row["estimated_cost_usd"]
    total = round(total, 2)
    if total > matrix["budget_usd"]:
        findings.append(
            Finding(
                "matrix.budget",
                f"Estimated total {total:.2f} USD exceeds budget_usd {matrix['budget_usd']}",
                "budget_usd",
            )
        )
    summary = {
        "unit_cost_usd": {axis: units[axis] for axis in AXES if axis in units},
        "total_estimated_usd": total,
        "budget_usd": matrix["budget_usd"],
        "currency": "USD",
        "estimate_note": "Estimate from supplied unit costs; confirmed cost is recorded per operation after completion",
    }
    return summary, findings


def operation_commands(
    project: str, row: dict[str, Any], options: argparse.Namespace
) -> list[dict[str, Any]]:
    paid = [step for step in row["steps"] if step["provider_operation"]]
    operations: list[dict[str, Any]] = []
    previous: str | None = None
    for step in paid:
        route = step["route"]
        asset = (
            row["name"] if len(paid) == 1 else f"{row['name']}_{'-'.join(step['axes'])}"
        )
        folder = f"variants/{row['name']}"
        audio = route == "language-dub"
        base = [
            "uv",
            "run",
            "python",
            ".agents/scripts/prepare_request.py",
            "--project",
            project,
            "--asset",
            asset,
            "--prompt",
            f"{folder}/prompt_{asset}.md",
            "--model",
            options.audio_model if audio else options.video_model,
            "--operation",
            options.audio_operation if audio else options.video_operation,
            "--expected-output",
            f"{folder}/{asset}{STEP_OUTPUT_SUFFIX.get(route, '.mp4')}",
        ]
        operations.append(
            {
                "asset": asset,
                "route": route,
                "skills": step["skills"],
                "after": previous,
                "hash_command": base,
                "register_command": [
                    *base,
                    "--review",
                    f"{folder}/review_{asset}.json",
                    "--capabilities",
                    options.capabilities,
                    "--write",
                    "--register",
                ],
                "references_note": "Add --ref path:role:manifest for every approved reference the reviewed prompt binds",
            }
        )
        previous = asset
    return operations


def register_findings(matrix: dict[str, Any]) -> list[Finding]:
    findings: list[Finding] = []
    if matrix["status"] != "approved":
        findings.append(
            Finding(
                "matrix.status",
                "Only an approved matrix may be prepared for registration",
                "status",
            )
        )
    if not matrix["hero"]["sha256"]:
        findings.append(
            Finding(
                "matrix.hero_hash",
                "hero.sha256 must bind the approved hero take",
                "hero.sha256",
            )
        )
    return findings


def run(args: argparse.Namespace) -> tuple[dict[str, Any], list[Finding]]:
    matrix, findings = load_matrix(args.matrix)
    if findings:
        return {}, findings
    rows = expand(matrix)
    findings = gate_findings(matrix, rows)
    result: dict[str, Any] = {
        "campaign": matrix["campaign"],
        "concept": matrix["concept"],
        "strategy": matrix["strategy"],
        "variant_count": sum(row["role"] == "variant" for row in rows),
        "max_variants": matrix["max_variants"],
    }
    if args.command != "plan":
        summary, cost_findings = apply_costs(
            matrix, rows, parse_unit_costs(args.unit_cost)
        )
        result.update(summary)
        findings.extend(cost_findings)
    result["rows"] = rows
    if args.command == "register":
        findings.extend(register_findings(matrix))
        if not blocking(findings):
            result["dry_run"] = True
            result["procedure"] = REGISTER_PROCEDURE
            result["operations"] = {
                row["name"]: operation_commands(str(args.project), row, args)
                for row in rows
                if row["role"] == "variant"
            }
    return result, findings


def blocking(findings: list[Finding]) -> bool:
    return any(finding.severity == "error" for finding in findings)


def parser() -> argparse.ArgumentParser:
    cli = argparse.ArgumentParser(
        description="Expand, cost and plan registration of an ad variant matrix; never calls a provider"
    )
    commands = cli.add_subparsers(dest="command", required=True)
    plan = commands.add_parser("plan")
    plan.add_argument("matrix", type=Path)
    cost = commands.add_parser("cost")
    cost.add_argument("matrix", type=Path)
    cost.add_argument("--unit-cost", action="append", default=[])
    register = commands.add_parser("register")
    register.add_argument("matrix", type=Path)
    register.add_argument("--project", type=Path, required=True)
    register.add_argument("--unit-cost", action="append", default=[])
    register.add_argument("--video-model", default="<video-model-id>")
    register.add_argument("--video-operation", default="<video-operation>")
    register.add_argument("--audio-model", default="<audio-model-id>")
    register.add_argument("--audio-operation", default="<audio-operation>")
    register.add_argument("--capabilities", default="<capability-evidence.json>")
    return cli


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        result, findings = run(args)
    except (OSError, ValueError, TypeError, UnicodeError) as error:
        result, findings = {}, [Finding("input.readable", str(error))]
    print(
        json.dumps(
            {
                "ok": not blocking(findings),
                **result,
                "findings": [asdict(f) for f in findings],
            },
            indent=2,
            ensure_ascii=False,
        )
    )
    return int(blocking(findings))


if __name__ == "__main__":
    sys.exit(main())
