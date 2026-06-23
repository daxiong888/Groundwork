#!/usr/bin/env python3
"""Generate proposal-only patch suggestion artifacts from eval failures."""

import argparse
import json
import re
from pathlib import Path


UNCLASSIFIED_FAILURE_TYPES = {"", "none", "unknown", "unclassified"}
PASS_VERDICTS = {"pass", "not_applicable"}
SECRET_PATTERNS = (
    re.compile(r"(Authorization:\s*Bearer\s+)[^\s,;]+", re.IGNORECASE),
    re.compile(r"(token=)[^\s,;]+", re.IGNORECASE),
    re.compile(r"(api[_-]?key=)[^\s,;]+", re.IGNORECASE),
    re.compile(r"(cookie:\s*)[^\n]+", re.IGNORECASE),
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----.*?-----END [A-Z ]*PRIVATE KEY-----", re.DOTALL),
)


def load_json(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None


def load_jsonl(path):
    rows = []
    warnings = []
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except FileNotFoundError:
        return rows, [f"missing {path.name}"]

    for line_number, line in enumerate(lines, start=1):
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError as exc:
            warnings.append(f"{path.name}:{line_number}: invalid JSON: {exc.msg}")
            continue
        if isinstance(value, dict):
            rows.append(value)
        else:
            warnings.append(f"{path.name}:{line_number}: non-object JSONL row ignored")
    return rows, warnings


def load_score_artifacts(score_dir):
    scores = []
    if not score_dir.exists() or not score_dir.is_dir():
        return scores
    for path in sorted(score_dir.glob("*.json")):
        score = load_json(path)
        if isinstance(score, dict):
            scores.append((path, score))
    return scores


def verdict_for(record):
    return str(record.get("overall_verdict") or record.get("verdict") or "unknown").strip()


def normalize_failure_type(value):
    return str(value or "").strip() or "unknown"


def normalize_fix_locus(value):
    return str(value or "").strip() or "unknown"


def failed_checker_results(record):
    checker_results = record.get("checker_results")
    if not isinstance(checker_results, list):
        return []
    return [
        checker
        for checker in checker_results
        if isinstance(checker, dict) and checker.get("verdict") == "fail"
    ]


def unique_sorted(values):
    return sorted({str(value).strip() for value in values if str(value).strip()})


def redact_sensitive_text(text):
    redacted = str(text)
    for pattern in SECRET_PATTERNS:
        if pattern.groups:
            redacted = pattern.sub(r"\1[REDACTED]", redacted)
        else:
            redacted = pattern.sub("[REDACTED_PRIVATE_KEY]", redacted)
    return redacted


def append_notes(notes, value):
    if value is None:
        return
    if isinstance(value, list):
        for item in value:
            item = redact_sensitive_text(item).strip()
            if item:
                notes.append(item)
        return
    text = redact_sensitive_text(value).strip()
    if text:
        notes.append(text)


def proposal_summary(failure_type, fix_locus, checker_ids):
    if checker_ids:
        checker_text = ", ".join(checker_ids)
        return f"Review {fix_locus} for failed deterministic checker(s): {checker_text}."
    if failure_type == "forbidden_behavior":
        return "Tighten trace-ready behavior so forbidden behavior cannot pass readiness."
    if failure_type == "forbidden_route":
        return "Tighten routing guardrails so forbidden routes cannot be selected."
    if failure_type == "route_miss":
        return "Review routing classification so expected routes are selected when evidence supports them."
    if failure_type == "schema_validation_error":
        return "Review schema contract handling for invalid score or eval artifacts."
    return f"Review {fix_locus} for classified eval failure `{failure_type}`."


def case_records_from_run(run_dir):
    run_dir = Path(run_dir)
    records = {}
    warnings = []

    results, result_warnings = load_jsonl(run_dir / "results.jsonl")
    warnings.extend(result_warnings)
    for result in results:
        case_id = str(result.get("id") or result.get("case_id") or "").strip()
        if case_id:
            records.setdefault(case_id, {"case_id": case_id, "sources": []})
            records[case_id]["sources"].append(("results.jsonl", result))

    for path, score in load_score_artifacts(run_dir / "score"):
        case_id = str(score.get("case_id") or score.get("id") or "").strip()
        if case_id:
            records.setdefault(case_id, {"case_id": case_id, "sources": []})
            records[case_id]["sources"].append((str(path.relative_to(run_dir)), score))

    summary = load_json(run_dir / "summary.json")
    if isinstance(summary, dict):
        for failure in summary.get("failures") or []:
            if not isinstance(failure, dict):
                continue
            case_id = str(failure.get("id") or failure.get("case_id") or "").strip()
            if case_id:
                records.setdefault(case_id, {"case_id": case_id, "sources": []})
                records[case_id]["sources"].append(("summary.json", failure))

    return records, warnings


def suggestion_from_case(case_id, sources, index):
    nonpass_sources = [
        (source_name, record)
        for source_name, record in sources
        if verdict_for(record) not in PASS_VERDICTS
    ]
    if not nonpass_sources:
        return None

    failed_checkers = []
    failure_types = []
    fix_loci = []
    source_artifacts = []
    notes = ["Generated from classified eval failure; proposal only."]
    severities = []

    for source_name, record in nonpass_sources:
        source_artifacts.append(source_name)
        failure_types.append(normalize_failure_type(record.get("failure_type")))
        fix_loci.append(normalize_fix_locus(record.get("fix_locus")))
        append_notes(notes, record.get("notes"))
        for checker in failed_checker_results(record):
            checker_id = str(checker.get("checker_id") or "").strip()
            if checker_id:
                failed_checkers.append(checker_id)
            severity = str(checker.get("severity") or "").strip()
            if severity and severity != "none":
                severities.append(severity)
            append_notes(notes, checker.get("notes"))

    checker_ids = unique_sorted(failed_checkers)
    classified_failures = [
        failure_type
        for failure_type in failure_types
        if failure_type not in UNCLASSIFIED_FAILURE_TYPES
    ]
    if not classified_failures and not checker_ids:
        return None

    failure_type = classified_failures[0] if classified_failures else "unknown"
    fix_locus = next(
        (fix_locus for fix_locus in fix_loci if fix_locus != "unknown"),
        "unknown",
    )

    suggestion = {
        "suggestion_id": f"ps-{index:03d}",
        "triggering_cases": [case_id],
        "failure_type": failure_type,
        "fix_locus": fix_locus,
        "proposed_patch_summary": proposal_summary(failure_type, fix_locus, checker_ids),
        "affected_files": [],
        "rollback": "Discard this suggestion artifact; no repository files were modified.",
        "human_decision": "none",
        "auto_apply": False,
        "notes": unique_sorted(notes),
        "source_artifacts": unique_sorted(source_artifacts),
    }
    if checker_ids:
        suggestion["checker_ids"] = checker_ids
    if severities:
        suggestion["severity"] = unique_sorted(severities)[0]
    return suggestion


def generate_patch_suggestions(run_dir):
    records, warnings = case_records_from_run(run_dir)
    suggestions = []
    for case_id in sorted(records):
        suggestion = suggestion_from_case(case_id, records[case_id]["sources"], len(suggestions) + 1)
        if suggestion:
            suggestions.append(suggestion)
    artifact = {"suggestions": suggestions}
    if warnings:
        artifact["warnings"] = warnings
    return artifact


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Generate proposal-only patch suggestions from local Groundwork eval artifacts."
    )
    parser.add_argument("--run-dir", type=Path, required=True, help="Directory containing summary/results/score artifacts.")
    parser.add_argument("--output", type=Path, help="Optional explicit output file. Defaults to stdout.")
    args = parser.parse_args(argv)

    artifact = generate_patch_suggestions(args.run_dir)
    output = json.dumps(artifact, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(output, encoding="utf-8")
    else:
        print(output, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
