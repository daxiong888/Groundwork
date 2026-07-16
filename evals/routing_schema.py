"""Shared routing and router-observability schema vocabulary."""

import json
import re
from pathlib import Path


ROUTE_REGISTRY_PATH = (
    Path(__file__).resolve().parents[1]
    / "scripts"
    / "codex-hooks"
    / "groundwork_route_registry.json"
)
ROUTE_REGISTRY = json.loads(ROUTE_REGISTRY_PATH.read_text(encoding="utf-8"))
PUBLIC_SKILL_ROUTES = set(ROUTE_REGISTRY["public_routes"])

DIRECT_ROUTE = "direct"
UNKNOWN_ROUTE = "unknown"
HOST_PREEMPTION_ROUTE = "runtime-safety-gate"
NOT_APPLICABLE = "not_applicable"

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
SELECTOR_POLICIES = {
    "tool_if_available_else_prompt_preference",
    "prompt_preference_only",
    "unavailable",
    "unknown",
}
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
    "insufficient_evidence",
}

TRACE_READY_SUITES = {
    "routing-reliability.csv",
    "routing-blind.csv",
    "trace-first-verify-review.csv",
    "uat-evidence-window.csv",
    "clean-review-fanout.csv",
    "zh-trigger-parity.csv",
}

INTENT_KIND_TOKENS = {
    "direct",
    "new_requirement",
    "clarify",
    "issue_split",
    "plan",
    "prototype",
    "implement",
    "verify",
    "handoff",
    "delivery",
    "remote_mutation",
}
REQUIREMENT_STATE_TOKENS = {
    "raw",
    "grilled",
    "prd_draft",
    "prd_accepted",
    "issue_ready",
    "implementation_ready",
    "verified",
    "blocked",
}
SOURCE_TRUTH_TOKENS = {
    "conversation",
    "accepted_prd",
    "local_artifact",
    "external_issue",
    "pull_request",
    "source_code",
    "test_evidence",
    "runtime_evidence",
    "state_md",
    "mixed",
    "unknown",
}
RISK_GATE_TOKENS = {
    "none",
    "git_write",
    "remote_write",
    "destructive",
    "customer_visible",
    "data_write",
    "secrets_or_pii",
    "blocked",
}
STATE_TRANSITION_TOKENS = {
    "none",
    "clarify",
    "draft",
    "accept",
    "split",
    "plan",
    "implement",
    "verify",
    "handoff",
    "block",
    "close",
}
STOP_CONDITION_TOKENS = {
    "continue",
    "ask_clarification",
    "require_prd_acceptance",
    "require_artifact_promotion",
    "require_gate",
    "direct_answer",
    "blocked",
}
CASE_KIND_TOKENS = {"positive", "hard_negative", "host_preemption"}
CASE_SOURCE_TOKENS = {
    "real_drift",
    "synthetic_hard_negative",
    "regression_protection",
    "unverified_hypothesis",
}
OUTPUT_CONTRACT_IMPLEMENTED_TOKENS = {
    "none",
    "verify_scope",
    "gate_fields",
    "prototype_contract_boundary",
    "implementation_result",
    "implementation_conformance",
    "entry_decision",
    "trajectory_signal",
    "qa_fix_qa",
    "qa_gap_closure_gate",
    "contract_lineage",
    "release_evidence_claim",
    "uat_evidence_window",
    "uat_evidence_window_forbidden",
    "uat_handoff_reference",
    "prototype_iteration_checkpoint",
    "prototype_no_delta_stop",
    "prototype_one_shot",
    "spec_single_question",
    "spec_writeback",
    "spec_no_delta_stop",
    "spec_clear_fast_path",
    "spec_gap_list",
    "checkpoint_before_risky_action",
    "artifact_header",
    "dispatch_compact_default",
    "dispatch_complete_or_split",
}
OUTPUT_CONTRACT_FUTURE_TOKENS = {
    "handoff_compact_reference",
    "route_failure_feedback",
}
CONTRACT_LINEAGE_EXPECTATION_FIELDS = (
    "lineage_expected_canonical_owner",
    "lineage_expected_divergence",
    "lineage_expected_fix_owner",
    "lineage_expected_hops",
    "lineage_expected_unverified_hops",
)
CONTRACT_LINEAGE_SCOPE_EXPECTATION_FIELDS = (
    "lineage_expected_scope_claim",
    "lineage_expected_scope_covered",
    "lineage_expected_scope_missing",
    "lineage_expected_scope_verdict",
)
UAT_EVIDENCE_WINDOW_EXPECTATION_FIELDS = (
    "uat_expected_claim_scope",
    "uat_expected_fingerprint",
    "uat_expected_preconditions",
    "uat_expected_window_stability",
    "uat_expected_coverage_basis",
    "uat_expected_result_missing",
    "uat_expected_rerun_supersedes",
)
UAT_EVIDENCE_WINDOW_SCOPE_EXPECTATION_FIELDS = (
    "uat_expected_scope_claim",
    "uat_expected_scope_covered",
    "uat_expected_scope_missing",
    "uat_expected_scope_verdict",
)
RELEASE_EVIDENCE_CLAIM_EXPECTATION_FIELDS = (
    "release_expected_claim_type",
    "release_expected_claim",
    "release_expected_evidence_status",
    "release_expected_installed_plugin_root",
    "release_expected_source_root",
    "release_expected_refresh_method",
    "release_expected_refresh_evidence",
    "release_expected_run_scope",
    "release_expected_commands_or_trials",
    "release_expected_limitations",
)
UAT_HANDOFF_REFERENCE_EXPECTATION_FIELDS = (
    "uat_handoff_expected_canonical_reference",
    "uat_handoff_expected_claim_scope",
    "uat_handoff_expected_fingerprint",
    "uat_handoff_expected_window_stability",
    "uat_handoff_expected_gap",
    "uat_handoff_expected_rerun_supersedes",
    "uat_handoff_expected_next_owner_action",
    "uat_handoff_expected_execution_boundary",
)
EVIDENCE_REQUIRED_IMPLEMENTED_TOKENS = {
    "none",
    "no_file_changes",
    "gate_observed",
    "git_status",
    "raw_intent_no_implementation",
    "direct_fallback_no_artifact",
    "source_or_unverified",
    "tests_or_unverified",
    "browser_or_unverified",
    "runtime_or_unverified",
    "dispatch_default_read_path",
}
EVIDENCE_REQUIRED_FUTURE_TOKENS = {
    "cache_equivalence",
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


def boolish(value):
    return str(value).strip().lower() == "true"


def expected_skill_for_row(row):
    expected_best = str(row.get("expected_best") or "").strip()
    if expected_best:
        return expected_best

    if row.get("expected_skill"):
        return str(row["expected_skill"]).strip()

    behavior = row.get("expected_behavior") or ""
    if not boolish(row.get("should_trigger", True)):
        route_match = re.search(r"Should route to ([A-Za-z0-9_-]+)", behavior)
        if route_match:
            return route_match.group(1)
        return DIRECT_ROUTE

    expected = str(row.get("skill") or "").strip()
    return expected or DIRECT_ROUTE


def row_location(row):
    return f"{row.get('_suite', 'unknown')}:{row.get('_row_number', '?')}:{row.get('id') or '<missing id>'}"


def is_trace_ready_row(row):
    return row.get("_suite") in TRACE_READY_SUITES


def is_routing_reliability_row(row):
    return is_trace_ready_row(row)


def host_preemption_allowed(row):
    return (
        boolish(row.get("host_preemption_allowed"))
        or boolish(row.get("host_preemption_classification_allowed"))
        or str(row.get("case_kind") or "").strip() == "host_preemption"
    )


def parse_pipe_list(value, field, row, *, blank_default=None):
    text = str(value or "").strip()
    if not text:
        return list(blank_default or [])
    if "," in text or ";" in text:
        raise ValueError(f"{row_location(row)} {field} must use '|' separators, not commas or semicolons")
    parts = [part.strip() for part in text.split("|")]
    if any(not part for part in parts):
        raise ValueError(f"{row_location(row)} {field} contains an empty list item")
    if any(re.search(r"\s", part) for part in parts):
        raise ValueError(f"{row_location(row)} {field} contains whitespace inside a token")
    return parts


def validate_token(value, allowed, field, row, *, required=False, legacy_not_applicable=True):
    text = str(value or "").strip()
    if not text:
        if required:
            raise ValueError(f"{row_location(row)} missing required {field}")
        return NOT_APPLICABLE if legacy_not_applicable else ""
    if text not in allowed:
        if legacy_not_applicable:
            return NOT_APPLICABLE
        raise ValueError(f"{row_location(row)} unknown {field}: {text}")
    return text


def measurement_tokens_for_row(row, field, implemented, future):
    text = str(row.get(field) or "").strip()
    if not text:
        if field == "output_contract" and boolish(row.get("verify_scope_required")):
            return ["verify_scope"], []
        return ["none"], []

    tokens = parse_pipe_list(text, field, row)
    allowed = implemented | future
    unknown = [token for token in tokens if token not in allowed]
    if unknown:
        raise ValueError(f"{row_location(row)} unknown {field}: {', '.join(unknown)}")
    future_tokens = [token for token in tokens if token in future]
    return tokens, future_tokens


def require_contract_lineage_expectations(row, output_contract):
    if "contract_lineage" not in output_contract:
        return
    required = list(CONTRACT_LINEAGE_EXPECTATION_FIELDS)
    if "verify_scope" in output_contract:
        required.extend(CONTRACT_LINEAGE_SCOPE_EXPECTATION_FIELDS)
    missing = [field for field in required if not str(row.get(field) or "").strip()]
    if missing:
        raise ValueError(
            f"{row_location(row)} contract_lineage missing required oracle fields: "
            + ", ".join(missing)
        )


def require_uat_evidence_window_expectations(row, output_contract):
    if "uat_evidence_window" not in output_contract:
        return
    if "verify_scope" not in output_contract:
        raise ValueError(
            f"{row_location(row)} uat_evidence_window requires verify_scope"
        )
    if "release_evidence_claim" not in output_contract:
        raise ValueError(
            f"{row_location(row)} uat_evidence_window requires release_evidence_claim"
        )
    required = list(UAT_EVIDENCE_WINDOW_EXPECTATION_FIELDS)
    required.extend(UAT_EVIDENCE_WINDOW_SCOPE_EXPECTATION_FIELDS)
    missing = [field for field in required if not str(row.get(field) or "").strip()]
    if missing:
        raise ValueError(
            f"{row_location(row)} uat_evidence_window missing required oracle fields: "
            + ", ".join(missing)
        )


def require_release_evidence_claim_expectations(row, output_contract):
    if "release_evidence_claim" not in output_contract:
        return
    missing = [
        field
        for field in RELEASE_EVIDENCE_CLAIM_EXPECTATION_FIELDS
        if not str(row.get(field) or "").strip()
    ]
    if missing:
        raise ValueError(
            f"{row_location(row)} release_evidence_claim missing required oracle fields: "
            + ", ".join(missing)
        )


def require_uat_evidence_window_forbidden_contract(row, output_contract):
    if "uat_evidence_window_forbidden" not in output_contract:
        return
    required = {"verify_scope", "release_evidence_claim"}
    missing = sorted(required - set(output_contract))
    if missing:
        raise ValueError(
            f"{row_location(row)} uat_evidence_window_forbidden requires "
            + ", ".join(missing)
        )
    if "uat_evidence_window" in output_contract:
        raise ValueError(
            f"{row_location(row)} uat_evidence_window_forbidden conflicts with uat_evidence_window"
        )


def require_uat_handoff_reference_expectations(row, output_contract):
    if "uat_handoff_reference" not in output_contract:
        return
    if "release_evidence_claim" not in output_contract:
        raise ValueError(
            f"{row_location(row)} uat_handoff_reference requires release_evidence_claim"
        )
    missing = [
        field
        for field in UAT_HANDOFF_REFERENCE_EXPECTATION_FIELDS
        if not str(row.get(field) or "").strip()
    ]
    if missing:
        raise ValueError(
            f"{row_location(row)} uat_handoff_reference missing required oracle fields: "
            + ", ".join(missing)
        )


def route_expectations_for_row(row):
    expected_best = expected_skill_for_row(row)
    acceptable_routes = parse_pipe_list(
        row.get("acceptable_routes"),
        "acceptable_routes",
        row,
        blank_default=[expected_best],
    )
    forbidden_routes = parse_pipe_list(
        row.get("forbidden_routes"),
        "forbidden_routes",
        row,
        blank_default=[],
    )
    route_lists = acceptable_routes + forbidden_routes

    if not expected_best:
        raise ValueError(f"{row_location(row)} missing required expected_best")
    if expected_best == "blocked":
        raise ValueError(f"{row_location(row)} blocked is not a route")
    if expected_best == HOST_PREEMPTION_ROUTE:
        raise ValueError(f"{row_location(row)} runtime-safety-gate is not allowed as expected_best")
    if expected_best not in EXPECTED_BEST_ROUTES:
        raise ValueError(f"{row_location(row)} unknown expected_best route: {expected_best}")

    if "blocked" in route_lists:
        raise ValueError(f"{row_location(row)} blocked is not allowed in route lists")

    unknown_routes = [route for route in route_lists if route not in ROUTE_LIST_ROUTES]
    if unknown_routes:
        raise ValueError(f"{row_location(row)} unknown route: {', '.join(sorted(set(unknown_routes)))}")

    if HOST_PREEMPTION_ROUTE in route_lists and not host_preemption_allowed(row):
        raise ValueError(
            f"{row_location(row)} runtime-safety-gate route list requires "
            "host_preemption_allowed=true or case_kind=host_preemption"
        )

    overlap = sorted(set(acceptable_routes) & set(forbidden_routes))
    if overlap:
        raise ValueError(f"{row_location(row)} acceptable_routes overlaps forbidden_routes: {', '.join(overlap)}")

    return expected_best, acceptable_routes, forbidden_routes


def routing_schema_for_row(row):
    routing_row = is_trace_ready_row(row)
    expected_best, acceptable_routes, forbidden_routes = route_expectations_for_row(row)
    legacy_not_applicable = not routing_row
    intent_kind = validate_token(
        row.get("intent_kind"),
        INTENT_KIND_TOKENS,
        "intent_kind",
        row,
        required=routing_row,
        legacy_not_applicable=legacy_not_applicable,
    )
    requirement_state = validate_token(
        row.get("requirement_state"),
        REQUIREMENT_STATE_TOKENS,
        "requirement_state",
        row,
        required=routing_row,
        legacy_not_applicable=legacy_not_applicable,
    )
    source_truth = validate_token(
        row.get("source_truth"),
        SOURCE_TRUTH_TOKENS,
        "source_truth",
        row,
        required=routing_row,
        legacy_not_applicable=legacy_not_applicable,
    )
    risk_gate = validate_token(
        row.get("risk_gate"),
        RISK_GATE_TOKENS,
        "risk_gate",
        row,
        required=routing_row,
        legacy_not_applicable=legacy_not_applicable,
    )
    expected_state_transition = validate_token(
        row.get("expected_state_transition"),
        STATE_TRANSITION_TOKENS,
        "expected_state_transition",
        row,
        required=routing_row,
        legacy_not_applicable=legacy_not_applicable,
    )
    expected_stop_condition = validate_token(
        row.get("expected_stop_condition"),
        STOP_CONDITION_TOKENS,
        "expected_stop_condition",
        row,
        required=routing_row,
        legacy_not_applicable=legacy_not_applicable,
    )
    route_boundary = str(row.get("route_boundary") or "").strip() or (
        NOT_APPLICABLE if legacy_not_applicable else ""
    )
    case_kind = validate_token(
        row.get("case_kind"),
        CASE_KIND_TOKENS,
        "case_kind",
        row,
        required=routing_row,
        legacy_not_applicable=legacy_not_applicable,
    )
    case_source = validate_token(
        row.get("case_source"),
        CASE_SOURCE_TOKENS,
        "case_source",
        row,
        required=routing_row,
        legacy_not_applicable=legacy_not_applicable,
    )
    output_contract, future_output_contract = measurement_tokens_for_row(
        row,
        "output_contract",
        OUTPUT_CONTRACT_IMPLEMENTED_TOKENS,
        OUTPUT_CONTRACT_FUTURE_TOKENS,
    )
    require_contract_lineage_expectations(row, output_contract)
    require_release_evidence_claim_expectations(row, output_contract)
    require_uat_evidence_window_expectations(row, output_contract)
    require_uat_evidence_window_forbidden_contract(row, output_contract)
    require_uat_handoff_reference_expectations(row, output_contract)
    evidence_required, future_evidence_required = measurement_tokens_for_row(
        row,
        "evidence_required",
        EVIDENCE_REQUIRED_IMPLEMENTED_TOKENS,
        EVIDENCE_REQUIRED_FUTURE_TOKENS,
    )

    if routing_row and not route_boundary:
        raise ValueError(f"{row_location(row)} missing required route_boundary")

    return {
        "input_scenario": row.get("input_scenario") or row.get("prompt") or "",
        "expected_best": expected_best,
        "acceptable_routes": acceptable_routes,
        "forbidden_routes": forbidden_routes,
        "host_preemption_allowed": host_preemption_allowed(row),
        "intent_kind": intent_kind,
        "requirement_state": requirement_state,
        "source_truth": source_truth,
        "risk_gate": risk_gate,
        "expected_state_transition": expected_state_transition,
        "expected_stop_condition": expected_stop_condition,
        "route_boundary": route_boundary,
        "case_kind": case_kind,
        "case_source": case_source,
        "output_contract": output_contract,
        "output_contract_future_tokens": future_output_contract,
        "evidence_required": evidence_required,
        "evidence_required_future_tokens": future_evidence_required,
        "behavior_assertion": row.get("acceptance_standard") or row.get("expected_behavior") or "",
    }


def malformed_csv_errors(row):
    errors = []
    if None in row:
        errors.append(f"{row_location(row)} malformed CSV row has extra cells: {row.get(None)}")
    fieldnames = row.get("_fieldnames") or []
    if any(name is None or str(name).strip() == "" for name in fieldnames):
        errors.append(f"{row_location(row)} malformed CSV header has blank columns")
    if not str(row.get("id") or "").strip():
        errors.append(f"{row_location(row)} missing required id")
    return errors


def validate_routing_schema(rows):
    errors = []
    seen_ids = {}
    normalized = []

    for row in rows:
        errors.extend(malformed_csv_errors(row))
        row_id = str(row.get("id") or "").strip()
        if row_id:
            if row_id in seen_ids:
                errors.append(f"{row_location(row)} duplicate row id also seen at {seen_ids[row_id]}")
            else:
                seen_ids[row_id] = row_location(row)
        try:
            normalized.append(routing_schema_for_row(row))
        except ValueError as exc:
            errors.append(str(exc))

    return errors, normalized


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
