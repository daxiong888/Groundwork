#!/usr/bin/env python3
"""Draft routing-reliability CSV rows from reviewed router score artifacts."""

import argparse
import csv
import io
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

try:
    from evals.routing_schema import ROUTER_OBSERVABILITY_BACKFILL_FIELDS, as_list
except ImportError:  # pragma: no cover - script execution from evals/
    from routing_schema import ROUTER_OBSERVABILITY_BACKFILL_FIELDS, as_list


def load_score(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def row_from_score(score):
    expected = str(score.get("expected_route") or "unknown")
    actual = str(score.get("actual_route") or "unknown")
    failure_type = str(score.get("failure_type") or "unknown")
    route_boundary = str(score.get("route_boundary") or "live-observation")
    case_id = str(score.get("turn_id") or score.get("case_id") or "router-observability-live").strip()
    acceptable = as_list(score.get("acceptable_routes")) or ([expected] if expected != "unknown" else [])
    forbidden = as_list(score.get("forbidden_routes"))
    missing = []
    checker_ids = [
        str(checker.get("checker_id") or "")
        for checker in score.get("checker_results") or []
        if isinstance(checker, dict)
    ]
    output_contract = "entry_decision"
    if failure_type == "output_contract_failure" and (
        expected == "verify"
        or any("verify_scope" in checker_id for checker_id in checker_ids)
    ):
        output_contract = "verify_scope_full"

    row = {
        "id": f"ro-backfill-{case_id}",
        "route_boundary": route_boundary,
        "case_kind": "positive" if failure_type in {"none", ""} else "hard_negative",
        "case_source": "real_drift",
        "intent_kind": "implement" if expected == "implement" else "direct",
        "requirement_state": "implementation_ready" if expected == "implement" else "unknown",
        "source_truth": "mixed",
        "risk_gate": "none",
        "expected_state_transition": "implement" if expected == "implement" else "none",
        "expected_stop_condition": "continue",
        "expected_best": expected,
        "acceptable_routes": "|".join(acceptable),
        "forbidden_routes": "|".join(forbidden),
        "input_scenario": "Reviewed and redacted live router observability failure; raw prompt is not copied.",
        "expected_behavior": f"Route to `{expected}` with explicit evidence boundaries.",
        "forbidden_behavior": f"Route to `{actual}` without sufficient source-strength evidence.",
        "output_contract": output_contract,
        "evidence_required": "source_or_unverified",
    }
    if expected == "unknown":
        missing.append("expected_best")
    if actual == "unknown" and failure_type != "route_miss":
        missing.append("actual_route")
    return row, missing


def csv_text(row):
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=ROUTER_OBSERVABILITY_BACKFILL_FIELDS, extrasaction="ignore")
    writer.writeheader()
    writer.writerow(row)
    return buffer.getvalue()


def markdown_text(row, missing):
    lines = [
        "# Router Observability Backfill Draft",
        "",
        "Target Reader: Groundwork eval maintainer.",
        "Reader Action Needed: Review, redact, and decide whether to add this row to `evals/prompts/routing-reliability.csv`.",
        "Evidence Boundary: Draft row only; not runtime, release, UAT, cache, or customer readiness evidence.",
        "",
        "## Missing Fields",
    ]
    if missing:
        lines.extend(f"- `{field}`" for field in missing)
    else:
        lines.append("- none")
    lines.extend(["", "## CSV Draft", "", "```csv", csv_text(row).rstrip(), "```", ""])
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Draft a routing-reliability CSV row from router-score.json.")
    parser.add_argument("--score", type=Path, required=True, help="Path to router-score.json.")
    parser.add_argument("--format", choices=["csv", "markdown"], default="csv")
    args = parser.parse_args(argv)

    row, missing = row_from_score(load_score(args.score))
    if args.format == "markdown":
        print(markdown_text(row, missing), end="")
    else:
        print(csv_text(row), end="")
    return 0 if not missing else 2


if __name__ == "__main__":
    raise SystemExit(main())
