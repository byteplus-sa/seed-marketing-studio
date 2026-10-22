from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import re
import sys
from collections import Counter
from dataclasses import asdict
from pathlib import Path
from typing import Any

from ruamel.yaml.error import YAMLError
from validate_request import (
    Finding,
    is_seedance_25,
    project_review_mode,
    schema_findings,
)

AXES = (
    "hook",
    "talent",
    "product",
    "outfit",
    "location",
    "language",
    "market",
    "ratio",
)
SWAP_AXES = ("talent", "product", "outfit", "location")
RECAST_TRIGGER = {"talent", "location"}
RECAST_COST_KEY = "motion-recast"
DELIVERY_ONLY_AXES = {"market", "ratio"}
DELIVERY_ROUTES = {"market-adapt", "ratio-reframe"}
DEFAULT_UNIT_COSTS = {"ratio": 0.0}
LOCALIZE_SKILL = "ad-localize"
COST_KEYS = (*AXES, RECAST_COST_KEY)
AD_GROUP_CREATIVES = 5
HOOK_MIN_DURATION_S = 4
DRAFT_RESOLUTION = "480p"
PLACEHOLDER = re.compile(r"\{([a-z]+)\}")
TAKE = re.compile(r"^t\d{2}$")
RESOLUTION = re.compile(r"^\d{3,4}p$")
STEP_SKILLS = {
    "object-swap": ["source-subject-map", "seedance-object-swap"],
    "motion-recast": ["seedance-motion-recast"],
    "hook-opening": ["ugc-ad-modes", "seedance-prompt-25"],
    "language-dub": ["audio-dubbing", "seedance-prompt-25-dialogue", "ad-captions"],
    "market-adapt": [LOCALIZE_SKILL],
    "ratio-reframe": ["ad-delivery-formats"],
}
STEP_OUTPUT_SUFFIX = {"language-dub": ".wav"}
STEP_NOTES = {
    "hook-opening": (
        f"Generate at the {HOOK_MIN_DURATION_S} s minimum supported duration, then "
        "trim it in Studio to the hero's recorded opening span before the hero body"
    ),
    "language-dub": (
        "Mux the dubbed audio onto the hero picture in post and place the muxed "
        "take in the variant shot"
    ),
    "ratio-reframe": (
        "Reframe per placement with ad-delivery-formats; no provider operation "
        "or registry entry"
    ),
}
LOCALIZE_REMINDER = (
    "No command here: ad-localize plans, reviews and registers its own "
    "operations for the per-element levels recorded in the market inventory"
)
MARKET_ESTIMATE_NOTE = (
    "Market rows use the supplied market unit cost as an estimate; the real cost "
    "depends on the per-element adaptation levels chosen in ad-localize, which "
    "estimates and registers its own operations"
)
RATIO_COST_NOTE = (
    "Ratio rows default to 0 USD because a Studio reframe is not a provider "
    "operation; set a ratio unit cost only to budget native per-ratio regeneration"
)
REGISTER_PROCEDURE = [
    "Write the variant shot manifest at studio.manifest with studio.frontmatter",
    "Write and freeze the row prompt at the --prompt path",
    "Run hash_command; bind required compliance evidence (and strict prompt-review) to request_sha256",
    "Resolve failing or incomplete required evidence, then run register_command",
    "Submit only a registered operation, in 'after' order, under the project approval mode",
    (
        "A row with base_variant starts from that variant's selected take; an "
        "operation with 'after' uses the selected take of the named variant as "
        "its source, and a step owned by another row is never registered again"
    ),
    (
        "Inspect and select the 480p draft with a hash-bound decision in both "
        "review modes; promote Seedance 2.5 with the selected draft_task_id and "
        "output settings, use --stage final for other models; a retake uses a new --take"
    ),
]
PROVIDER_ROUTES = {"object-swap", "motion-recast", "hook-opening", "language-dub"}
AUDIO_ROUTES = {"language-dub"}
SOURCE_PRESERVING_ROUTES = {"object-swap", "motion-recast"}
COMPLIANCE_RULES = (
    "ad.claims_supported",
    "ad.no_fabricated_testimonial",
    "brand.copy_rules",
    "library.pin_current",
)
COMMON_RULES = (
    *COMPLIANCE_RULES,
    "ad.variant_one_axis",
    "ad.variant_budget_gate",
)
VIDEO_RULES = ("video.text_free",)
SHOT_RULES = ("shot.plan_bound", "shot.variety", "shot.axis_carry")
STATIC_BY_DESIGN = (
    "ugc",
    "ugc-how-to",
    "ugc-unboxing",
    "product-review",
    "ugc-virtual-try-on",
    "ugc-preset",
    "talking-head",
    "avatar",
    "news",
    "frame-break",
    "user-lock",
)


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
    if matrix["strategy"] == "full_factorial" and not matrix.get("notes", "").strip():
        findings.append(
            Finding(
                "matrix.factorial_request",
                "full_factorial needs notes recording the user's explicit request "
                "for every combination (ad.variant_one_axis)",
                "notes",
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


def variant_count(matrix: dict[str, Any]) -> int:
    counts = [len(levels(matrix, axis)) for axis in active_axes(matrix)]
    if matrix["strategy"] == "full_factorial":
        return math.prod(counts) - 1
    return sum(count - 1 for count in counts)


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


def step_cost_key(route: str, axes: list[str]) -> str:
    return RECAST_COST_KEY if route == "motion-recast" else axes[0]


def plan_steps(values: dict[str, str], changed: list[str]) -> list[dict[str, Any]]:
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
    if "market" in changed:
        routed.append(("market-adapt", ["market"]))
    if "ratio" in changed:
        routed.append(("ratio-reframe", ["ratio"]))
    steps: list[dict[str, Any]] = []
    lineage: list[str] = []
    for route, axes in routed:
        lineage.append(
            f"{route}:" + "+".join(f"{axis}={values[axis]}" for axis in axes)
        )
        step: dict[str, Any] = {
            "route": route,
            "axes": axes,
            "skills": STEP_SKILLS[route],
            "provider_operation": route in PROVIDER_ROUTES,
            "cost_key": step_cost_key(route, axes),
            "operation_key": ">".join(lineage),
        }
        if route == "hook-opening":
            step["generate_duration_s"] = HOOK_MIN_DURATION_S
        if route in STEP_NOTES:
            step["studio_note"] = STEP_NOTES[route]
        steps.append(step)
    return steps


def studio_target(name: str) -> dict[str, Any]:
    shot_id = f"variant-{slug(name)}"
    directory = f"scenes/{shot_id}"
    frontmatter = {"shot_id": shot_id, "title": name, "variant": name}
    return {
        "shot_id": shot_id,
        "directory": directory,
        "manifest": f"{directory}/shot.md",
        "frontmatter": frontmatter,
    }


def market_folder(campaign: str, market_id: str) -> str:
    return f"projects/{slug(campaign)}/markets/{market_id}"


def project_path(campaign: str, values: dict[str, str], changed: list[str]) -> str:
    parts = [campaign]
    if DELIVERY_ONLY_AXES & set(changed):
        parts.extend(values[axis] for axis in changed if axis not in DELIVERY_ONLY_AXES)
    return "projects/" + "-".join(slug(part) for part in parts)


def localize_target(
    campaign: str, values: dict[str, str], changed: list[str]
) -> dict[str, Any] | None:
    if "market" not in changed:
        return None
    market_id = values["market"]
    folder = market_folder(campaign, market_id)
    generated = [axis for axis in changed if axis not in DELIVERY_ONLY_AXES]
    variant_key = "-".join(slug(values[axis]) for axis in generated) or None
    work = f"{folder}/{variant_key}" if variant_key else folder
    return {
        "skill": LOCALIZE_SKILL,
        "market_id": market_id,
        "variant_key": variant_key,
        "card": f"{folder}/market.json",
        "inventory": f"{work}/inventory.md",
        "project": f"{project_path(campaign, values, changed)}-{market_id}",
    }


def delivery_target(
    campaign: str,
    values: dict[str, str],
    changed: list[str],
    localize: dict[str, Any] | None,
) -> dict[str, Any] | None:
    if "ratio" not in changed:
        return None
    base = localize["project"] if localize else project_path(campaign, values, changed)
    return {
        "skill": "ad-delivery-formats",
        "aspect": values["ratio"],
        "project": f"{base}-{slug(values['ratio'])}",
    }


def owned_projects(row: dict[str, Any]) -> list[tuple[str, str]]:
    if not DELIVERY_ONLY_AXES & set(row["changed_axes"]):
        return []
    values = row["values"]
    source = json.dumps(
        {axis: value for axis, value in values.items() if axis != "ratio"}
    )
    owned = (
        [(row["delivery"]["project"], json.dumps(values))] if row["delivery"] else []
    )
    if row["localize"]:
        owned.append((row["localize"]["project"], source))
    return owned


def project_collisions(rows: list[dict[str, Any]]) -> list[str]:
    owners: dict[str, set[str]] = {}
    for row in rows:
        for path, source in owned_projects(row):
            owners.setdefault(path, set()).add(source)
    return sorted(path for path, sources in owners.items() if len(sources) > 1)


def owned_steps(row: dict[str, Any]) -> list[dict[str, Any]]:
    return [step for step in row["steps"] if step["owner"] == row["name"]]


def owns_route(row: dict[str, Any], route: str) -> bool:
    return any(step["route"] == route for step in owned_steps(row))


def base_variant(name: str, steps: list[dict[str, Any]], hero: str) -> str:
    reused = [step["owner"] for step in steps if step["owner"] != name]
    return reused[-1] if reused else hero


def annotate_market_step(
    name: str, steps: list[dict[str, Any]], localize: dict[str, Any] | None
) -> list[dict[str, Any]]:
    if localize is None:
        return steps
    for step in steps:
        if step["route"] == "market-adapt" and step["owner"] == name:
            step["note"] = (
                f"Run {LOCALIZE_SKILL} with the market card {localize['card']} "
                "(market facts and level_default) and the per-element levels in "
                f"{localize['inventory']}; it plans, reviews and registers its own "
                f"paid operations and delivers into {localize['project']}"
            )
    return steps


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
    hero_name = variant_name(matrix, hero)
    owners: dict[str, str] = {}
    rows: list[dict[str, Any]] = []
    for index, values in enumerate(combinations(matrix)):
        changed = [axis for axis in values if values[axis] != hero[axis]]
        name = variant_name(matrix, values)
        steps = plan_steps(values, changed)
        for step in steps:
            step["owner"] = owners.setdefault(step["operation_key"], name)
        generated = any(
            step["owner"] == name and step["route"] not in DELIVERY_ROUTES
            for step in steps
        )
        localize = localize_target(matrix["campaign"], values, changed)
        rows.append(
            {
                "index": index,
                "name": name,
                "role": "variant" if changed else "hero",
                "values": values,
                "changed_axes": changed,
                "base_variant": base_variant(name, steps, hero_name)
                if changed
                else None,
                "steps": annotate_market_step(name, steps, localize),
                "studio": studio_target(name) if generated else None,
                "localize": localize,
                "delivery": delivery_target(
                    matrix["campaign"], values, changed, localize
                ),
            }
        )
    return rows


def gate_findings(matrix: dict[str, Any], rows: list[dict[str, Any]]) -> list[Finding]:
    findings: list[Finding] = []
    names = [row["name"] for row in rows]
    duplicates = sorted(name for name, count in Counter(names).items() if count > 1)
    if duplicates:
        findings.append(
            Finding(
                "matrix.unique_names",
                f"Variant names collide: {', '.join(duplicates)}",
                "naming",
            )
        )
    shot_ids = [row["studio"]["shot_id"] for row in rows if row["studio"]]
    shared = sorted(shot for shot, count in Counter(shot_ids).items() if count > 1)
    if shared and not duplicates:
        findings.append(
            Finding(
                "matrix.unique_shot_ids",
                f"Variant names map to the same Studio shot folder: {', '.join(shared)}",
                "naming",
            )
        )
    clashing = project_collisions(rows)
    if clashing:
        findings.append(
            Finding(
                "matrix.unique_projects",
                "Variant rows would build or render into the same localized or "
                f"delivery project: {', '.join(clashing)}",
                "axes",
            )
        )
    redundant = [
        row["name"]
        for row in rows
        if {"market", "language"} <= set(row["changed_axes"])
    ]
    if redundant:
        findings.append(
            Finding(
                "matrix.market_language",
                "Rows change market and language together: "
                f"{', '.join(redundant)}. Language belongs inside the market "
                f"adaptation; let {LOCALIZE_SKILL} set the market card's language, "
                "or test language and market one axis at a time",
                "axes",
            )
        )
    count = sum(row["role"] == "variant" for row in rows)
    if count == 0:
        findings.append(
            Finding("matrix.empty", "No axis value differs from the hero", "axes")
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
        if not separator or axis not in COST_KEYS:
            raise ValueError(
                "Expected --unit-cost <axis|motion-recast>=<usd> with a known "
                f"axis: {item}"
            )
        amount = float(value)
        if not math.isfinite(amount) or amount < 0:
            raise ValueError(f"Unit cost must be a finite non-negative number: {item}")
        costs[axis] = amount
    return costs


def unique_operations(
    rows: list[dict[str, Any]], units: dict[str, float]
) -> list[dict[str, Any]]:
    operations: dict[str, dict[str, Any]] = {}
    for row in rows:
        for step in row["steps"]:
            operation = operations.setdefault(
                step["operation_key"],
                {
                    "operation_key": step["operation_key"],
                    "owner": step["owner"],
                    "route": step["route"],
                    "axes": step["axes"],
                    "cost_key": step["cost_key"],
                    "unit_cost_usd": units[step["cost_key"]],
                    "used_by": [],
                },
            )
            operation["used_by"].append(row["name"])
    return list(operations.values())


def apply_costs(
    matrix: dict[str, Any], rows: list[dict[str, Any]], overrides: dict[str, float]
) -> tuple[dict[str, Any], list[Finding]]:
    units = {**DEFAULT_UNIT_COSTS, **matrix.get("unit_cost_usd", {}), **overrides}
    findings: list[Finding] = []
    missing = sorted(
        {
            step["cost_key"]
            for row in rows
            for step in row["steps"]
            if step["cost_key"] not in units
        },
        key=COST_KEYS.index,
    )
    if missing:
        findings.append(
            Finding(
                "cost.unit_missing",
                f"No unit cost for: {', '.join(missing)}",
                "unit_cost_usd",
            )
        )
        return {}, findings
    operations = unique_operations(rows, units)
    for row in rows:
        row["estimated_cost_usd"] = round(
            sum(units[step["cost_key"]] for step in owned_steps(row)), 2
        )
    total = round(sum(operation["unit_cost_usd"] for operation in operations), 2)
    if total > matrix["budget_usd"]:
        findings.append(
            Finding(
                "matrix.budget",
                f"Estimated total {total:.2f} USD exceeds budget_usd {matrix['budget_usd']}",
                "budget_usd",
            )
        )
    routes = {operation["route"] for operation in operations}
    summary: dict[str, Any] = {
        "unit_cost_usd": {key: units[key] for key in COST_KEYS if key in units},
        "total_estimated_usd": total,
        "budget_usd": matrix["budget_usd"],
        "currency": "USD",
        "estimate_note": (
            "Estimate from supplied unit costs, one unit per unique operation (a "
            "combined talent and location Motion Transfer costs one motion-recast "
            "unit) covering its draft and final. A row that reuses another row's "
            "operation adds nothing for it: each row's estimated_cost_usd counts "
            "only the operations it owns, and operations_estimate lists every "
            "unique operation with the rows that use it. Confirmed cost is recorded "
            "per operation after completion"
        ),
        "operations_estimate": operations,
    }
    if "market-adapt" in routes:
        summary["market_estimate_note"] = MARKET_ESTIMATE_NOTE
    if "ratio-reframe" in routes:
        summary["ratio_cost_note"] = RATIO_COST_NOTE
    return summary, findings


def shot_rule_exemption(route: str, static_by_design: str | None) -> str | None:
    if route in AUDIO_ROUTES:
        return "no video shot: audio re-voice of the hero soundtrack"
    if route in SOURCE_PRESERVING_ROUTES:
        return "source-preserving edit: keeps the hero's camera, cuts and timing"
    if static_by_design:
        return f"static-by-design format: {static_by_design}"
    return None


def step_params(route: str, options: argparse.Namespace) -> list[str]:
    if route in AUDIO_ROUTES:
        return []
    resolution = (
        DRAFT_RESOLUTION if options.stage == "draft" else options.final_resolution
    )
    params = [f"resolution={resolution}"]
    if options.stage == "draft" and is_seedance_25(options.video_model):
        params.append("draft=true")
    if route == "hook-opening":
        params.append(f"duration={HOOK_MIN_DURATION_S}")
    return params


def step_rules(route: str, exemption: str | None, review_mode: str) -> list[str]:
    if review_mode == "default":
        return list(COMPLIANCE_RULES)
    rules = list(COMMON_RULES)
    if route not in AUDIO_ROUTES:
        rules.extend(VIDEO_RULES)
    if exemption is None:
        rules.extend(SHOT_RULES)
    return rules


def flag_pairs(flag: str, values: list[str]) -> list[str]:
    return [item for value in values for item in (flag, value)]


def staged(step: dict[str, Any], stage: str) -> bool:
    return step["provider_operation"] and (
        stage != "final" or step["route"] not in AUDIO_ROUTES
    )


def staged_steps(row: dict[str, Any], stage: str) -> list[dict[str, Any]]:
    return [step for step in owned_steps(row) if staged(step, stage)]


def operation_commands(
    project: str, row: dict[str, Any], options: argparse.Namespace
) -> list[dict[str, Any]]:
    if row["studio"] is None:
        return []
    folder = row["studio"]["directory"]
    operations: list[dict[str, Any]] = []
    previous: str | None = None
    for step in row["steps"]:
        if not staged(step, options.stage):
            continue
        if step["owner"] != row["name"]:
            previous = step["owner"]
            continue
        route = step["route"]
        audio = route in AUDIO_ROUTES
        asset = f"{row['name']}_{options.take}_{'audio' if audio else options.stage}"
        params = step_params(route, options)
        exemption = shot_rule_exemption(route, options.static_by_design)
        rules = step_rules(route, exemption, options.review_mode)
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
            *flag_pairs("--param", params),
            "--expected-output",
            f"{folder}/{asset}{STEP_OUTPUT_SUFFIX.get(route, '.mp4')}",
            *flag_pairs("--required-rule", rules),
        ]
        operations.append(
            {
                "asset": asset,
                "route": route,
                "stage": options.stage,
                "take": options.take,
                "skills": step["skills"],
                "after": previous,
                "params": params,
                "required_rules": rules,
                "shot_rule_exemption": exemption,
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
        previous = row["name"]
    return operations


def project_file(project: Path, relative: str | None) -> Path | None:
    if not relative or Path(relative).is_absolute():
        return None
    root = project.resolve()
    path = (root / relative).resolve()
    if not path.is_relative_to(root) or not path.is_file():
        return None
    return path


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def hero_findings(hero: dict[str, Any], project: Path) -> list[Finding]:
    findings: list[Finding] = []
    if project_file(project, hero.get("decision_ref")) is None:
        findings.append(
            Finding(
                "matrix.hero_decision",
                "hero.decision_ref must name the approval decision record as a "
                "regular file inside --project",
                "hero.decision_ref",
            )
        )
    take = project_file(project, hero.get("take_file"))
    if take is None:
        findings.append(
            Finding(
                "matrix.hero_take",
                "hero.take_file must name the approved hero take as a regular file "
                "inside --project",
                "hero.take_file",
            )
        )
    elif hero["sha256"] and file_sha256(take) != hero["sha256"]:
        findings.append(
            Finding(
                "matrix.hero_hash_mismatch",
                "The hero take no longer matches hero.sha256; re-approve the hero "
                "before planning variants",
                "hero.sha256",
            )
        )
    return findings


def register_findings(matrix: dict[str, Any], project: Path) -> list[Finding]:
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
    findings.extend(hero_findings(matrix["hero"], project))
    return findings


def unresolved(value: str | None) -> bool:
    return not value or not value.strip() or "<" in value or ">" in value


def option_findings(
    rows: list[dict[str, Any]], options: argparse.Namespace
) -> list[Finding]:
    findings: list[Finding] = []
    routes = {
        step["route"]
        for row in rows
        if row["role"] == "variant"
        for step in staged_steps(row, options.stage)
    }
    if (
        routes - AUDIO_ROUTES
        and options.stage != "draft"
        and is_seedance_25(options.video_model or "")
    ):
        findings.append(
            Finding(
                "seedance.draft_promotion",
                "Seedance 2.5 starts with --stage draft in both review modes. "
                "For finals, prepare each selected native draft_task_id with only "
                "supported output settings; this matrix has no per-row draft task "
                "selection and cannot emit native promotions. A delivery target "
                "alone does not authorize a fresh non-draft request.",
                "--stage",
            )
        )
    if (
        routes - AUDIO_ROUTES
        and options.stage != "draft"
        and (
            not options.final_resolution
            or not RESOLUTION.fullmatch(options.final_resolution)
            or (
                options.stage == "final"
                and options.final_resolution == DRAFT_RESOLUTION
            )
        )
    ):
        findings.append(
            Finding(
                "register.final_resolution",
                "Production/final video needs --final-resolution at the delivery "
                "target; --stage final at 480p reuses the selected draft instead",
                "--final-resolution",
            )
        )
    needed: list[str] = []
    if routes - AUDIO_ROUTES:
        needed += ["video_model", "video_operation"]
    if routes & AUDIO_ROUTES:
        needed += ["audio_model", "audio_operation"]
    if routes:
        needed.append("capabilities")
    missing = [name for name in needed if unresolved(getattr(options, name))]
    if missing:
        flags = ", ".join(f"--{name.replace('_', '-')}" for name in missing)
        findings.append(
            Finding(
                "register.placeholder",
                f"Pass resolved values for {flags} before register commands are printed",
                "register",
            )
        )
    return findings


def run(args: argparse.Namespace) -> tuple[dict[str, Any], list[Finding]]:
    matrix, findings = load_matrix(args.matrix)
    if findings:
        return {}, findings
    count = variant_count(matrix)
    result: dict[str, Any] = {
        "campaign": matrix["campaign"],
        "concept": matrix["concept"],
        "strategy": matrix["strategy"],
        "variant_count": count,
        "max_variants": matrix["max_variants"],
    }
    if count > matrix["max_variants"]:
        return {**result, "rows": []}, [
            Finding(
                "matrix.max_variants",
                f"{count} variants exceed max_variants {matrix['max_variants']}",
                "max_variants",
            )
        ]
    rows = expand(matrix)
    findings = gate_findings(matrix, rows)
    if args.command != "plan":
        summary, cost_findings = apply_costs(
            matrix, rows, parse_unit_costs(args.unit_cost)
        )
        result.update(summary)
        findings.extend(cost_findings)
    result["rows"] = rows
    if args.command == "register":
        args.review_mode = project_review_mode(args.project)
        args.stage = args.stage or "draft"
        result["review_mode"] = args.review_mode
        if not TAKE.fullmatch(args.take):
            raise ValueError(f"--take must look like t01: {args.take}")
        findings.extend(register_findings(matrix, args.project))
        findings.extend(option_findings(rows, args))
        if not blocking(findings):
            result["dry_run"] = True
            result["stage"] = args.stage
            result["take"] = args.take
            result["procedure"] = REGISTER_PROCEDURE
            result["operations"] = {
                row["name"]: operation_commands(str(args.project), row, args)
                for row in rows
                if row["role"] == "variant"
            }
            localize = [
                {
                    "variant": row["name"],
                    **row["localize"],
                    "reminder": LOCALIZE_REMINDER,
                }
                for row in rows
                if row["localize"] and owns_route(row, "market-adapt")
            ]
            if localize:
                result["localize"] = localize
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
    register.add_argument("--video-model")
    register.add_argument("--video-operation")
    register.add_argument("--audio-model")
    register.add_argument("--audio-operation")
    register.add_argument("--capabilities")
    register.add_argument("--stage", choices=("production", "draft", "final"))
    register.add_argument("--final-resolution")
    register.add_argument("--take", default="t01")
    register.add_argument("--static-by-design", choices=STATIC_BY_DESIGN)
    return cli


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        result, findings = run(args)
    except (OSError, ValueError, TypeError, UnicodeError, YAMLError) as error:
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
