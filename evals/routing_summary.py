"""Shared routing summary metrics for runner and observability reports."""

try:
    from routing_schema import TRACE_READY_SUITES, as_list, increment, rate_summary, sorted_counts
except ImportError:  # pragma: no cover - package import path
    from evals.routing_schema import TRACE_READY_SUITES, as_list, increment, rate_summary, sorted_counts


NOT_APPLICABLE = "not_applicable"
PASS_VERDICTS = {"pass", "flake"}

def routing_outcome(expected, actual, acceptable_routes, forbidden_routes):
    if not actual or actual == "unknown":
        return "missing"
    if actual == expected:
        return "best"
    if actual in forbidden_routes:
        return "forbidden"
    if actual in acceptable_routes:
        return "acceptable"
    return "unexpected"


def routing_result_present(result):
    boundary = str(result.get("route_boundary") or "").strip()
    return result.get("suite") in TRACE_READY_SUITES or (boundary and boundary != NOT_APPLICABLE)


def verdict_status(result):
    verdict = str(result.get("overall_verdict") or result.get("verdict") or "unknown")
    if verdict in PASS_VERDICTS:
        return "pass"
    if verdict == "blocked":
        return "blocking"
    return "fail"


def is_nonpass(result):
    return str(result.get("overall_verdict") or result.get("verdict") or "unknown") not in PASS_VERDICTS


def summarize_routing_results(results):
    routing_results = [result for result in results if routing_result_present(result)]
    if not routing_results:
        return None

    baseline_results = [
        result
        for result in routing_results
        if str(result.get("score_eligibility") or "baseline_eligible") == "baseline_eligible"
    ]
    total = len(baseline_results)
    best_hits = 0
    acceptable_hits = 0
    forbidden_hits = 0
    invalid_host_preemptions = 0
    outcome_counts = {}
    route_pair_counts = {}
    expected_route_counts = {}
    actual_route_counts = {}
    boundary_counts = {}
    verdict_dimension_counts = {
        "routing_verdict": {},
        "host_preemption_verdict": {},
        "output_contract_verdict": {},
        "evidence_verdict": {},
        "behavior_verdict": {},
        "overall_verdict": {},
        "execution_profile_verdict": {},
    }
    selector_enforcement_counts = {}
    selector_mismatch_reason_counts = {}
    failure_type_counts = {}
    unclassified_nonpass_ids = []

    for result in baseline_results:
        expected = str(result.get("expected_route") or result.get("expected") or "").strip() or "unknown"
        actual = str(result.get("actual_route") or result.get("actual") or "").strip() or "unknown"
        acceptable_routes = as_list(result.get("acceptable_routes"))
        if not acceptable_routes and expected != "unknown":
            acceptable_routes = [expected]
        forbidden_routes = as_list(result.get("forbidden_routes"))
        boundary = str(result.get("route_boundary") or NOT_APPLICABLE).strip() or NOT_APPLICABLE
        overall = str(result.get("overall_verdict") or result.get("verdict") or "unknown")
        failure_type = str(result.get("failure_type") or "").strip()

        if actual == expected:
            best_hits += 1
        if actual in acceptable_routes:
            acceptable_hits += 1
        if actual in forbidden_routes or failure_type == "forbidden_route":
            forbidden_hits += 1
        if result.get("host_preemption_verdict") == "fail" or failure_type == "invalid_host_preemption":
            invalid_host_preemptions += 1

        increment(outcome_counts, routing_outcome(expected, actual, acceptable_routes, forbidden_routes))
        increment(route_pair_counts, f"{expected} -> {actual}")
        increment(expected_route_counts, expected)
        increment(actual_route_counts, actual)
        if failure_type:
            increment(failure_type_counts, failure_type)

        if boundary not in boundary_counts:
            boundary_counts[boundary] = {"count": 0, "pass": 0, "fail": 0, "blocking": 0}
        status = verdict_status(result)
        boundary_counts[boundary]["count"] += 1
        boundary_counts[boundary][status] += 1
        if status != "blocking" and str(result.get("blocking_level") or "").strip():
            boundary_counts[boundary]["blocking"] += 1

        for dimension in verdict_dimension_counts:
            if dimension == "overall_verdict":
                value = str(result.get(dimension) or overall)
            else:
                value = str(result.get(dimension) or NOT_APPLICABLE)
            increment(verdict_dimension_counts[dimension], value)

        selector_enforcement = str(result.get("selector_enforcement") or "").strip()
        if selector_enforcement:
            increment(selector_enforcement_counts, selector_enforcement)
        selector_mismatch_reason = str(result.get("selector_mismatch_reason") or "").strip()
        if selector_mismatch_reason:
            increment(selector_mismatch_reason_counts, selector_mismatch_reason)

        if is_nonpass(result) and not failure_type:
            unclassified_nonpass_ids.append(str(result.get("id") or result.get("case_id") or "unknown"))

    return {
        "rows": len(routing_results),
        "baseline_eligible_rows": total,
        "best_route_hit_at_1": rate_summary(best_hits, total),
        "acceptable_route_coverage": rate_summary(acceptable_hits, total),
        "forbidden_route_hits": rate_summary(forbidden_hits, total),
        "invalid_host_preemption": rate_summary(invalid_host_preemptions, total),
        "routing_outcomes": sorted_counts(outcome_counts),
        "route_boundaries": {key: boundary_counts[key] for key in sorted(boundary_counts)},
        "per_route_counts": {
            "expected": sorted_counts(expected_route_counts),
            "actual": sorted_counts(actual_route_counts),
        },
        "route_pair_confusion": sorted_counts(route_pair_counts),
        "verdict_dimension_counts": {
            dimension: sorted_counts(counts)
            for dimension, counts in verdict_dimension_counts.items()
        },
        "execution_profile_verdict_counts": sorted_counts(
            verdict_dimension_counts["execution_profile_verdict"]
        ),
        "selector_enforcement_counts": sorted_counts(selector_enforcement_counts),
        "selector_mismatch_reason_counts": sorted_counts(selector_mismatch_reason_counts),
        "route_vs_execution_separability": {
            "routing": "routing_verdict",
            "execution": [
                "host_preemption_verdict",
                "execution_profile_verdict",
                "output_contract_verdict",
                "evidence_verdict",
                "behavior_verdict",
                "overall_verdict",
            ],
        },
        "failure_type_counts": sorted_counts(failure_type_counts),
        "unclassified_nonpass": {
            "count": len(unclassified_nonpass_ids),
            "ids": sorted(unclassified_nonpass_ids),
        },
    }
