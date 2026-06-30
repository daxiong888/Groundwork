"""Shared routing and router-observability schema vocabulary."""

PUBLIC_SKILL_ROUTES = {
    "dispatch",
    "to-prd",
    "to-issues",
    "triage",
    "write-plan",
    "prototype",
    "implement",
    "verify",
    "handoff",
    "wiki",
}

DIRECT_ROUTE = "direct"
UNKNOWN_ROUTE = "unknown"
HOST_PREEMPTION_ROUTE = "runtime-safety-gate"

EXPECTED_BEST_ROUTES = PUBLIC_SKILL_ROUTES | {DIRECT_ROUTE}
ROUTE_LIST_ROUTES = EXPECTED_BEST_ROUTES | {HOST_PREEMPTION_ROUTE}
WORKFLOW_ROUTES = ROUTE_LIST_ROUTES | {UNKNOWN_ROUTE}

DIMENSION_VERDICTS = {"pass", "fail", "blocked", "not_applicable"}
OVERALL_VERDICTS = {"pass", "partial", "fail", "blocked", "flake"}

EXECUTION_PROFILE_VERDICTS = {
    "mismatch",
    "pass",
    "insufficient_evidence",
    "not_applicable",
}
MODEL_PROFILES = {
    "fast_scan",
    "balanced_work",
    "strong_reasoning",
    "exhaustive_review",
    "spark_iteration",
    "unknown",
}
REASONING_EFFORTS = {"low", "medium", "high", "xhigh", "unknown"}
COST_LATENCY_BIASES = {"fast", "balanced", "quality", "unknown"}
SELECTOR_ENFORCEMENT = {"tool_enforced", "prompt_preference", "unavailable", "unknown"}
EVIDENCE_LAYERS = {
    "prompt_preference",
    "runtime_tool_evidence",
    "user_observed_model_menu_seed",
    "official_docs",
    "community_evidence",
    "local_characterization_eval",
}

SCORE_ELIGIBILITY = {
    "baseline_eligible",
    "display_only",
    "guided_hint_excluded",
    "insufficient_evidence",
}

TRACE_READY_SUITES = {
    "routing-reliability.csv",
    "trace-first-verify-review.csv",
    "clean-review-fanout.csv",
    "zh-trigger-parity.csv",
}

ROUTING_SCHEMA_FIELDS = [
    "intent_kind",
    "requirement_state",
    "source_truth",
    "risk_gate",
    "expected_state_transition",
    "expected_stop_condition",
    "expected_best",
    "acceptable_routes",
    "forbidden_routes",
    "route_boundary",
    "case_kind",
    "case_source",
    "output_contract",
    "evidence_required",
]

ROUTER_OBSERVABILITY_BACKFILL_FIELDS = [
    "id",
    "route_boundary",
    "case_kind",
    "case_source",
    "intent_kind",
    "requirement_state",
    "source_truth",
    "risk_gate",
    "expected_state_transition",
    "expected_stop_condition",
    "expected_best",
    "acceptable_routes",
    "forbidden_routes",
    "input_scenario",
    "expected_behavior",
    "forbidden_behavior",
    "output_contract",
    "evidence_required",
]

# Backward-compatible alias for older scripts. New code should use the
# backfill-specific name so this is not confused with runtime schema fields.
ROUTER_OBSERVABILITY_ROW_FIELDS = ROUTER_OBSERVABILITY_BACKFILL_FIELDS


def as_list(value):
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    text = str(value).strip()
    if not text:
        return []
    if "|" in text:
        return [part.strip() for part in text.split("|") if part.strip()]
    if "," in text:
        return [part.strip() for part in text.split(",") if part.strip()]
    return [text]


def sorted_counts(counts):
    return {key: counts[key] for key in sorted(counts)}


def increment(counts, key):
    counts[key] = counts.get(key, 0) + 1


def rate_summary(count, total):
    return {"count": count, "total": total, "rate": (count / total if total else 0)}


def normalize_route(value):
    route = str(value or "").strip()
    return route if route in WORKFLOW_ROUTES else UNKNOWN_ROUTE


def normalize_dimension_verdict(value, default="not_applicable"):
    verdict = str(value or "").strip()
    return verdict if verdict in DIMENSION_VERDICTS else default


def normalize_overall_verdict(value):
    verdict = str(value or "").strip()
    if verdict == "timeout":
        return "blocked"
    return verdict if verdict in OVERALL_VERDICTS else "blocked"
