#!/usr/bin/env python3
"""Assemble a human-readable eval report from local eval artifacts."""

import argparse
import json
from collections import Counter
from pathlib import Path


EVIDENCE_BOUNDARY = (
    "This report is assembled from local/redacted eval artifacts. It is not "
    "runtime, cache-refresh, release, UAT, or customer-readiness evidence unless "
    "separate runtime evidence is named."
)


def load_json(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None
    except json.JSONDecodeError as exc:
        return {"__parse_error__": f"{path}: {exc}"}


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
    artifacts = []
    warnings = []
    if not score_dir.exists():
        return artifacts, ["score artifacts missing: score/ directory not found"]
    if not score_dir.is_dir():
        return artifacts, ["score artifacts missing: score path is not a directory"]

    for path in sorted(score_dir.glob("*.json")):
        score = load_json(path)
        if isinstance(score, dict) and "__parse_error__" in score:
            warnings.append(score["__parse_error__"])
            continue
        if not isinstance(score, dict):
            warnings.append(f"{path}: score artifact is not a JSON object")
            continue
        artifacts.append((path, score))
    return artifacts, warnings


def verdict_for_result(result):
    return str(result.get("overall_verdict") or result.get("verdict") or "unknown")


def is_nonpass_result(result):
    return verdict_for_result(result) not in {"pass", "not_applicable"}


def sorted_counts(counter):
    return {key: counter[key] for key in sorted(counter)}


def append_json_block(lines, value):
    lines.append("```json")
    lines.append(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True))
    lines.append("```")


def rate_line(label, value):
    if not isinstance(value, dict):
        return f"- {label}: not provided"
    count = value.get("count", "unknown")
    total = value.get("total", "unknown")
    rate = value.get("rate")
    if isinstance(rate, (int, float)):
        return f"- {label}: {count}/{total} ({rate:.2%})"
    return f"- {label}: {count}/{total}"


def runtime_evidence_status(summary, diagnostics):
    if isinstance(summary, dict):
        value = summary.get("runtime_evidence")
        if value in {"present", "absent", "not_applicable"}:
            return value
        if summary.get("run_root") or summary.get("result_layout"):
            return "absent"
    if diagnostics:
        return "not_applicable"
    return "absent"


def top_regressions(results, summary):
    result_by_id = {
        str(result.get("id")): result
        for result in results
        if result.get("id") is not None
    }
    failures = []
    if isinstance(summary, dict):
        failures = summary.get("failures") or []
    if not failures:
        failures = [result for result in results if is_nonpass_result(result)]

    ranked = []
    for item in failures:
        matching_result = result_by_id.get(str(item.get("id")))
        failure_type = str(
            item.get("failure_type")
            or (matching_result or {}).get("failure_type")
            or item.get("case_result")
            or "unknown"
        )
        ranked.append(
            {
                "id": item.get("id") or "unknown",
                "suite": item.get("suite") or "unknown",
                "verdict": verdict_for_result(item),
                "failure_type": failure_type,
                "notes": item.get("notes") or "",
            }
        )
    return ranked[:5]


def deterministic_failures(results, scores):
    failures = []
    seen = set()

    def append_failure(case_id, checker):
        if not isinstance(checker, dict) or checker.get("verdict") != "fail":
            return
        checker_id = checker.get("checker_id") or "unknown"
        severity = checker.get("severity") or "unknown"
        key = (case_id, checker_id, severity)
        if key in seen:
            return
        seen.add(key)
        failures.append(
            {
                "case_id": case_id,
                "checker_id": checker_id,
                "severity": severity,
            }
        )

    for result in results:
        checker_results = result.get("checker_results")
        if not isinstance(checker_results, list):
            continue
        for checker in checker_results:
            append_failure(result.get("id") or "unknown", checker)
    for _, score in scores:
        for checker in score.get("checker_results") or []:
            append_failure(score.get("case_id") or "unknown", checker)
    return failures


def render_report(run_dir):
    run_dir = Path(run_dir)
    summary = load_json(run_dir / "summary.json")
    results, result_warnings = load_jsonl(run_dir / "results.jsonl")
    scores, score_warnings = load_score_artifacts(run_dir / "score")
    diagnostics = load_json(run_dir / "diagnostics.json")
    patch_suggestions = load_json(run_dir / "patch-suggestions.json")
    warnings = result_warnings + score_warnings

    if isinstance(summary, dict) and "__parse_error__" in summary:
        warnings.append(summary["__parse_error__"])
        summary = None
    if isinstance(diagnostics, dict) and "__parse_error__" in diagnostics:
        warnings.append(diagnostics["__parse_error__"])
        diagnostics = None
    if isinstance(patch_suggestions, dict) and "__parse_error__" in patch_suggestions:
        warnings.append(patch_suggestions["__parse_error__"])
        patch_suggestions = None

    counts = Counter(verdict_for_result(result) for result in results)
    summary_counts = summary.get("counts") if isinstance(summary, dict) else None
    suites = summary.get("suites") if isinstance(summary, dict) else None
    if not suites:
        suites = sorted({str(result.get("suite") or "unknown") for result in results})

    nonpass = [result for result in results if is_nonpass_result(result)]
    deterministic = deterministic_failures(results, scores)

    lines = [
        "# Groundwork Eval Report",
        "",
        "Target Reader: Eval maintainer or implementation reviewer.",
        "Reader Action Needed: Review local eval artifact interpretation and investigate non-pass cases.",
        f"Evidence Boundary: {EVIDENCE_BOUNDARY}",
        "",
        "## Run Metadata",
        f"- Run directory: `{run_dir}`",
        f"- Runtime evidence status: {runtime_evidence_status(summary or {}, diagnostics)}",
    ]
    if isinstance(summary, dict):
        lines.extend(
            [
                f"- Finished: {summary.get('finished', 'unknown')}",
                f"- Jobs: {summary.get('jobs', 'unknown')}",
                f"- Resource policy: {summary.get('resource_policy', 'unknown')}",
                f"- Group: {summary.get('group') or 'not_applicable'}",
            ]
        )
    else:
        lines.append("- Summary file: missing or invalid")

    lines.extend(["", "## Summary Counts"])
    if summary_counts:
        for verdict, count in sorted(summary_counts.items()):
            lines.append(f"- {verdict}: {count}")
    elif counts:
        for verdict, count in sorted_counts(counts).items():
            lines.append(f"- {verdict}: {count}")
    else:
        lines.append("- No result rows available.")

    routing = summary.get("routing_summary") if isinstance(summary, dict) else None
    lines.extend(["", "## Suites"])
    if suites:
        for suite in suites:
            lines.append(f"- `{suite}`")
    else:
        lines.append("- No suites provided.")

    lines.extend(["", "## Route Metrics"])
    if routing:
        lines.append(rate_line("Best route hit at 1", routing.get("best_route_hit_at_1")))
        lines.append(rate_line("Acceptable route coverage", routing.get("acceptable_route_coverage")))
        lines.append(rate_line("Forbidden route hits", routing.get("forbidden_route_hits")))
        lines.append(rate_line("Invalid host preemption", routing.get("invalid_host_preemption")))
        if routing.get("failure_type_counts"):
            lines.append("- Failure type counts:")
            for failure_type, count in routing["failure_type_counts"].items():
                lines.append(f"  - {failure_type}: {count}")
    else:
        lines.append("- Route metrics not provided.")

    lines.extend(["", "## Non-pass Cases"])
    if nonpass:
        for result in nonpass:
            notes = str(result.get("notes") or "").strip()
            suffix = f" - {notes}" if notes else ""
            lines.append(
                f"- `{result.get('id', 'unknown')}` [{result.get('suite', 'unknown')}] "
                f"{verdict_for_result(result)} / {result.get('failure_type') or 'unknown'}{suffix}"
            )
    else:
        lines.append("- No non-pass cases.")

    lines.extend(["", "## Score Artifacts"])
    if scores:
        lines.append(f"- Score artifact count: {len(scores)}")
        lines.append("- Score validation: not run by report generator; validate score JSON separately.")
        for path, score in scores:
            lines.append(
                f"- `{path.relative_to(run_dir)}`: case `{score.get('case_id', 'unknown')}`, "
                f"overall `{score.get('overall_verdict', 'unknown')}`, "
                f"failure_type `{score.get('failure_type', 'none')}`"
            )
    else:
        lines.append("- Score artifacts missing or empty.")
        lines.append("- Score validation: not_applicable.")

    lines.extend(["", "## Deterministic Failures"])
    if deterministic:
        for item in deterministic:
            lines.append(
                f"- `{item['checker_id']}` failed for `{item['case_id']}` "
                f"(severity `{item['severity']}`)"
            )
    else:
        lines.append("- No deterministic checker failures found in provided artifacts.")

    lines.extend(["", "## Trace Diagnostics"])
    if diagnostics:
        lines.append(
            f"- Events: {diagnostics.get('trace_event_count', 'unknown')}; "
            f"command-related events: {diagnostics.get('command_count', 'unknown')}; "
            f"duplicates: {diagnostics.get('duplicate_command_count', 'unknown')}; "
            f"failed commands: {diagnostics.get('failed_command_count', 'unknown')}"
        )
        lines.append(f"- Trace command thrashing: {diagnostics.get('trace_command_thrashing', 'unknown')}")
        lines.append(f"- Blocked reason: {diagnostics.get('blocked_reason', 'unknown')}")
        evidence_latency = diagnostics.get("evidence_latency") or {}
        lines.append(
            f"- Evidence latency: {evidence_latency.get('status', 'unknown')} "
            f"(first event index: {evidence_latency.get('first_evidence_event_index')}, "
            f"seconds: {evidence_latency.get('first_evidence_seconds')})"
        )
    else:
        lines.append("- Trace diagnostics not provided.")

    lines.extend(["", "## Top Regressions"])
    regressions = top_regressions(results, summary or {})
    if regressions:
        for item in regressions:
            lines.append(
                f"- `{item['id']}` [{item['suite']}] {item['verdict']} / "
                f"{item['failure_type']}: {item['notes'] or 'no notes'}"
            )
    else:
        lines.append("- No top regressions detected.")

    lines.extend(["", "## Patch Suggestions"])
    suggestions = []
    if isinstance(patch_suggestions, dict):
        raw_suggestions = patch_suggestions.get("suggestions")
        if isinstance(raw_suggestions, list):
            suggestions = [item for item in raw_suggestions if isinstance(item, dict)]
    if suggestions:
        lines.append(f"- Patch suggestion count: {len(suggestions)}")
        for suggestion in suggestions:
            lines.append(
                f"- `{suggestion.get('suggestion_id', 'unknown')}`: "
                f"{suggestion.get('failure_type', 'unknown')} / "
                f"{suggestion.get('fix_locus', 'unknown')}; "
                f"auto_apply `{suggestion.get('auto_apply')}`"
            )
    else:
        lines.append("No patch suggestions provided. Patch suggestion generation is deferred.")

    lines.extend(
        [
            "",
            "## Limitations",
            f"- {EVIDENCE_BOUNDARY}",
            "- Trace command diagnostics are event-level heuristics, not strict unique command invocation counts.",
            "- Evidence latency markers are heuristic and can overmatch generic future-looking text such as planned tests.",
            "- Missing optional artifacts are reported as gaps; this command does not promote or redact artifacts.",
            "- Patch suggestions are proposal-only artifacts and are not accepted patches.",
        ]
    )
    if warnings:
        lines.append("- Parse or input warnings:")
        for warning in warnings:
            lines.append(f"  - {warning}")

    return "\n".join(lines) + "\n"


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Assemble a markdown eval report from local Groundwork eval artifacts."
    )
    parser.add_argument("--run-dir", type=Path, required=True, help="Directory containing summary/results/score artifacts.")
    parser.add_argument("--output", type=Path, help="Optional explicit output file. Defaults to stdout.")
    args = parser.parse_args(argv)

    report = render_report(args.run_dir)
    if args.output:
        args.output.write_text(report, encoding="utf-8")
    else:
        print(report, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
