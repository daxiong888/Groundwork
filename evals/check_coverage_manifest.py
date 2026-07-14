#!/usr/bin/env python3
"""Validate the stdlib-readable eval coverage manifest."""

from __future__ import annotations

import csv
import sys
import tomllib
from pathlib import Path

EVALS_DIR = Path(__file__).resolve().parent
if str(EVALS_DIR) not in sys.path:
    sys.path.insert(0, str(EVALS_DIR))

try:
    from routing_schema import PUBLIC_SKILL_ROUTES, expected_skill_for_row, route_expectations_for_row
    from suite_registry import DEFAULT_SUITES
except ImportError:  # pragma: no cover - package import path
    from evals.routing_schema import PUBLIC_SKILL_ROUTES, expected_skill_for_row, route_expectations_for_row
    from evals.suite_registry import DEFAULT_SUITES


REPO = Path(__file__).resolve().parents[1]
PROMPTS = REPO / "evals" / "prompts"
DEFAULT_MANIFEST = REPO / "evals" / "coverage-manifest.toml"
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
expected_route = expected_skill_for_row
STRUCTURED_ROUTE_FIELDS = ("expected_best", "acceptable_routes", "forbidden_routes")


class ManifestError(ValueError):
    pass


def parse_manifest(path: Path) -> dict[str, dict[str, list[str]]]:
    try:
        payload = tomllib.loads(path.read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError) as exc:
        raise ManifestError(f"{path}: unable to parse TOML: {exc}") from exc

    data = payload.get("public_skills")
    if not isinstance(data, dict) or not data:
        raise ManifestError(f"{path}: no public_skills entries found")
    for skill, contract in data.items():
        if not isinstance(contract, dict):
            raise ManifestError(f"{path}: {skill} must be a table")
        for key, values in contract.items():
            if not isinstance(values, list) or any(not isinstance(item, str) for item in values):
                raise ManifestError(f"{path}: {skill}.{key} must be a string array")
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
    try:
        route, acceptable, forbidden = route_expectations_for_row(row)
    except ValueError as exc:
        errors.append(f"{skill}: route_negative {reference} has invalid route expectations: {exc}")
        return
    should_trigger = (row.get("should_trigger") or "").strip().lower()
    if should_trigger == "false":
        owner = (row.get("skill") or "").strip()
        if owner != skill:
            errors.append(
                f"{skill}: route_negative {reference} is owned by {owner!r}, not {skill!r}"
            )
        has_structured_expectations = any(
            str(row.get(field) or "").strip() for field in STRUCTURED_ROUTE_FIELDS
        )
        if not has_structured_expectations:
            return
    if route == skill:
        if should_trigger == "false":
            errors.append(
                f"{skill}: route_negative {reference} still expects {skill!r}; "
                "structured negatives must route elsewhere"
            )
        else:
            errors.append(
                f"{skill}: route_negative {reference} still expects {skill!r}; "
                "use should_trigger=false or a row routed elsewhere"
            )
    if skill in acceptable:
        errors.append(f"{skill}: route_negative {reference} allows {skill!r}")
    if skill not in forbidden:
        errors.append(
            f"{skill}: route_negative {reference} does not explicitly forbid {skill!r}"
        )


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
    public_routes = set(PUBLIC_SKILL_ROUTES)
    skill_dirs = public_skill_dirs()
    expected_skills = public_routes | skill_dirs
    default_suites = set(DEFAULT_SUITES)
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
