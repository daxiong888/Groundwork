#!/usr/bin/env python3
"""Validate eval coverage-manifest.yaml without requiring PyYAML."""

from __future__ import annotations

import csv
import sys
from pathlib import Path

import run_runtime


REPO = Path(__file__).resolve().parents[1]
PROMPTS = REPO / "evals" / "prompts"
DEFAULT_MANIFEST = REPO / "evals" / "coverage-manifest.yaml"
REQUIRED_LISTS = (
    "positives",
    "route_negatives",
    "hard_negatives",
    "default_suite_coverage",
    "targeted_only_coverage",
    "gaps",
)
MINIMUM_COUNTS = {
    "positives": 3,
    "route_negatives": 3,
    "hard_negatives": 3,
}
ALLOWED_HARD_MARKERS = {
    "canonical_conflict",
    "conformance_boundary",
    "executable_next_action",
    "forbidden_state_store",
    "git_topology_gate",
    "lifecycle_boundary",
    "missing_acceptance",
    "missing_evidence",
    "missing_source",
    "prototype_contract_boundary",
    "redaction_boundary",
    "runtime_evidence_boundary",
    "stale_source_truth",
    "test_gap",
    "wiki_citation_boundary",
    "wiki_source_truth_boundary",
}


class ManifestError(ValueError):
    pass


def parse_manifest(path: Path) -> dict[str, dict[str, list[str]]]:
    """Parse the small YAML subset used by coverage-manifest.yaml."""
    data: dict[str, dict[str, list[str]]] = {}
    in_public_skills = False
    current_skill: str | None = None
    current_key: str | None = None

    for line_number, raw_line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        stripped = raw_line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        indent = len(raw_line) - len(raw_line.lstrip(" "))
        if indent == 0:
            if stripped != "public_skills:":
                raise ManifestError(f"{path}:{line_number}: unsupported top-level key: {stripped}")
            in_public_skills = True
            current_skill = None
            current_key = None
            continue

        if not in_public_skills:
            raise ManifestError(f"{path}:{line_number}: content before public_skills")

        if indent == 2 and stripped.endswith(":"):
            current_skill = stripped[:-1]
            current_key = None
            if not current_skill:
                raise ManifestError(f"{path}:{line_number}: blank skill key")
            if current_skill in data:
                raise ManifestError(f"{path}:{line_number}: duplicate skill key: {current_skill}")
            data[current_skill] = {}
            continue

        if indent == 4 and ":" in stripped:
            if current_skill is None:
                raise ManifestError(f"{path}:{line_number}: list key without skill")
            key, value = stripped.split(":", 1)
            key = key.strip()
            value = value.strip()
            if key in data[current_skill]:
                raise ManifestError(f"{path}:{line_number}: duplicate key for {current_skill}: {key}")
            if value == "":
                data[current_skill][key] = []
                current_key = key
                continue
            if value == "[]":
                data[current_skill][key] = []
                current_key = key
                continue
            raise ManifestError(f"{path}:{line_number}: only block lists or [] are supported for {key}")

        if indent == 6 and stripped.startswith("- "):
            if current_skill is None or current_key is None:
                raise ManifestError(f"{path}:{line_number}: list item without active key")
            item = stripped[2:].strip()
            if not item:
                raise ManifestError(f"{path}:{line_number}: blank list item")
            data[current_skill][current_key].append(item)
            continue

        raise ManifestError(f"{path}:{line_number}: unsupported YAML shape")

    if not data:
        raise ManifestError(f"{path}: no public_skills entries found")
    return data


def public_skill_dirs() -> set[str]:
    return {
        item.parent.name
        for item in (REPO / "skills").glob("*/SKILL.md")
        if item.parent.name != "_shared"
    }


def load_rows() -> dict[tuple[str, str], dict[str, str]]:
    rows: dict[tuple[str, str], dict[str, str]] = {}
    for suite in sorted(PROMPTS.glob("*.csv")):
        with suite.open(newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            for row_number, row in enumerate(reader, start=2):
                row_id = (row.get("id") or "").strip()
                if not row_id:
                    continue
                key = (f"evals/prompts/{suite.name}", row_id)
                if key in rows:
                    raise ManifestError(f"{suite}:{row_number}: duplicate row id in suite: {row_id}")
                row["_suite"] = suite.name
                row["_row_number"] = str(row_number)
                rows[key] = row
    return rows


def split_reference(reference: str) -> tuple[str, str, str | None]:
    if "::" not in reference:
        raise ManifestError(f"invalid reference, expected path::id: {reference}")
    reference_body, marker = (reference.split("#", 1) + [None])[:2] if "#" in reference else (reference, None)
    path, row_id = reference_body.split("::", 1)
    if not path.startswith("evals/prompts/") or not path.endswith(".csv"):
        raise ManifestError(f"reference must point to evals/prompts/*.csv: {reference}")
    if not row_id:
        raise ManifestError(f"reference missing row id: {reference}")
    return path, row_id, marker


def expected_route(row: dict[str, str]) -> str:
    for field in ("expected_best", "expected_skill", "skill"):
        value = (row.get(field) or "").strip()
        if value:
            return value
    return ""


def parse_routes(value: str | None, default: list[str]) -> list[str]:
    if not value:
        return default
    return [item.strip() for item in value.split("|") if item.strip()]


def validate_positive(skill: str, reference: str, row: dict[str, str], errors: list[str]) -> None:
    route = expected_route(row)
    should_trigger = (row.get("should_trigger") or "").strip().lower()
    case_kind = (row.get("case_kind") or "").strip()
    if route != skill:
        errors.append(f"{skill}: positive {reference} expects {route!r}, not {skill!r}")
    if should_trigger == "false":
        errors.append(f"{skill}: positive {reference} has should_trigger=false")
    if case_kind == "hard_negative":
        errors.append(f"{skill}: positive {reference} is marked hard_negative")


def validate_route_negative(skill: str, reference: str, row: dict[str, str], errors: list[str]) -> None:
    route = expected_route(row)
    should_trigger = (row.get("should_trigger") or "").strip().lower()
    acceptable = parse_routes(row.get("acceptable_routes"), [route] if route else [])
    if should_trigger == "false":
        return
    if route == skill:
        errors.append(
            f"{skill}: route_negative {reference} still expects {skill!r}; "
            "use should_trigger=false or a row routed elsewhere"
        )
    if skill in acceptable:
        errors.append(f"{skill}: route_negative {reference} allows {skill!r}")


def validate_hard_negative(
    skill: str,
    reference: str,
    row: dict[str, str],
    marker: str | None,
    errors: list[str],
) -> None:
    route = expected_route(row)
    case_kind = (row.get("case_kind") or "").strip()

    if case_kind == "hard_negative":
        return

    if marker and marker.startswith("hard:") and marker[5:] in ALLOWED_HARD_MARKERS:
        return

    errors.append(
        f"{skill}: hard_negative {reference} lacks case_kind=hard_negative or allowed #hard marker "
        f"(expected route {route!r})"
    )


def validate_manifest(path: Path) -> list[str]:
    errors: list[str] = []
    manifest = parse_manifest(path)
    rows = load_rows()
    public_routes = set(run_runtime.PUBLIC_SKILL_ROUTES)
    skill_dirs = public_skill_dirs()
    expected_skills = public_routes | skill_dirs
    default_suites = set(run_runtime.DEFAULT_SUITES)
    actual_suites = {item.name for item in PROMPTS.glob("*.csv")}

    missing = sorted(expected_skills - set(manifest))
    extra = sorted(set(manifest) - expected_skills)
    if missing:
        errors.append("manifest missing public skills: " + ", ".join(missing))
    if extra:
        errors.append("manifest contains unknown public skills: " + ", ".join(extra))
    route_dir_drift = sorted(public_routes ^ skill_dirs)
    if route_dir_drift:
        errors.append("PUBLIC_SKILL_ROUTES and skills/*/SKILL.md disagree: " + ", ".join(route_dir_drift))

    for skill, config in sorted(manifest.items()):
        for key in REQUIRED_LISTS:
            if key not in config:
                errors.append(f"{skill}: missing required list {key}")
                config[key] = []
            elif not isinstance(config[key], list):
                errors.append(f"{skill}: {key} must be a list")

        for key, minimum in MINIMUM_COUNTS.items():
            if len(config[key]) < minimum:
                errors.append(f"{skill}: {key} has {len(config[key])}, expected at least {minimum}")

        if config["gaps"]:
            errors.append(f"{skill}: gaps must be empty before coverage gate passes")

        declared_default = set(config["default_suite_coverage"])
        declared_targeted = set(config["targeted_only_coverage"])
        overlap = sorted(declared_default & declared_targeted)
        if overlap:
            errors.append(f"{skill}: suites listed as both default and targeted-only: {', '.join(overlap)}")

        for suite in sorted(declared_default):
            if suite not in actual_suites:
                errors.append(f"{skill}: default suite does not exist: {suite}")
            if suite not in default_suites:
                errors.append(f"{skill}: default_suite_coverage includes non-default suite: {suite}")

        for suite in sorted(declared_targeted):
            if suite not in actual_suites:
                errors.append(f"{skill}: targeted-only suite does not exist: {suite}")
            if suite in default_suites:
                errors.append(f"{skill}: targeted_only_coverage includes default suite: {suite}")

        seen_refs: set[str] = set()
        seen_row_refs: set[tuple[str, str]] = set()
        referenced_suites: set[str] = set()
        for category in ("positives", "route_negatives", "hard_negatives"):
            for reference in config[category]:
                if reference in seen_refs:
                    errors.append(f"{skill}: duplicate reference across coverage lists: {reference}")
                    continue
                seen_refs.add(reference)
                try:
                    ref_path, row_id, marker = split_reference(reference)
                except ManifestError as exc:
                    errors.append(f"{skill}: {exc}")
                    continue
                if category != "hard_negatives" and marker:
                    errors.append(f"{skill}: {category} reference must not include marker: {reference}")
                if category == "hard_negatives" and marker and not marker.startswith("hard:"):
                    errors.append(f"{skill}: hard_negative marker must start with hard: {reference}")
                row_ref = (ref_path, row_id)
                if row_ref in seen_row_refs:
                    errors.append(f"{skill}: duplicate CSV row across coverage lists: {ref_path}::{row_id}")
                seen_row_refs.add(row_ref)
                row = rows.get((ref_path, row_id))
                if row is None:
                    errors.append(f"{skill}: referenced CSV row does not exist: {reference}")
                    continue

                suite = Path(ref_path).name
                referenced_suites.add(suite)
                if suite in default_suites and suite not in declared_default:
                    errors.append(f"{skill}: {reference} is default suite coverage but {suite} is not listed")
                if suite not in default_suites and suite not in declared_targeted:
                    errors.append(f"{skill}: {reference} is targeted-only coverage but {suite} is not listed")

                if category == "positives":
                    validate_positive(skill, reference, row, errors)
                elif category == "route_negatives":
                    validate_route_negative(skill, reference, row, errors)
                elif category == "hard_negatives":
                    validate_hard_negative(skill, reference, row, marker, errors)

        unused_suites = sorted((declared_default | declared_targeted) - referenced_suites)
        if unused_suites:
            errors.append(f"{skill}: suite coverage declared without referenced rows: {', '.join(unused_suites)}")

    return errors


def main(argv: list[str]) -> int:
    path = Path(argv[1]) if len(argv) > 1 else DEFAULT_MANIFEST
    errors = validate_manifest(path)
    if errors:
        print("coverage manifest validation: fail")
        for error in errors:
            print(f"- {error}")
        return 1
    print("coverage manifest validation: pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
