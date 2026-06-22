#!/usr/bin/env python3
"""Score dict adapters for Groundwork eval result records."""


WORKFLOW_ROUTES = {
    "dispatch",
    "to-prd",
    "to-issues",
    "triage",
    "write-plan",
    "prototype",
    "implement",
    "verify",
    "handoff",
    "direct",
    "runtime-safety-gate",
    "unknown",
}

DIMENSION_VERDICTS = {"pass", "fail", "blocked", "not_applicable"}
OVERALL_VERDICTS = {"pass", "partial", "fail", "blocked"}
FAILURE_TYPES = {
    "forbidden_route",
    "route_miss",
    "invalid_host_preemption",
    "future_output_contract",
    "output_contract_failure",
    "future_evidence_required",
    "evidence_failure",
    "behavior_failure",
    "forbidden_behavior",
    "direct_fallback_ceremony",
    "premature_implementation",
    "legacy_runtime_check",
    "codex_timeout",
    "codex_exit",
    "schema_validation_error",
    "unclassified",
    "none",
    "unknown",
}
FIX_LOCI = {
    "routing_surface",
    "runtime_safety_gate",
    "skill_output_contract",
    "evidence_collection",
    "requirement_state_gate",
    "direct_fallback_boundary",
    "runtime_environment",
    "runtime_verdict",
    "behavior_contract",
    "behavior_guardrail",
    "measurement_token",
    "artifact_policy",
    "git_boundary",
    "schema_contract",
    "fixture_contract",
    "unknown",
}


def first_nonempty(*values, default="unknown"):
    for value in values:
        if value is None:
            continue
        text = str(value).strip()
        if text:
            return text
    return default


def normalize_workflow_route(value):
    route = first_nonempty(value)
    return route if route in WORKFLOW_ROUTES else "unknown"


def normalize_dimension_verdict(value, *, default="not_applicable"):
    verdict = first_nonempty(value, default=default)
    return verdict if verdict in DIMENSION_VERDICTS else default


def normalize_overall_verdict(value):
    verdict = first_nonempty(value, default="blocked")
    if verdict == "timeout":
        return "blocked"
    return verdict if verdict in OVERALL_VERDICTS else "blocked"


def normalize_failure_type(value):
    failure_type = first_nonempty(value, default="none")
    return failure_type if failure_type in FAILURE_TYPES else "unknown"


def normalize_fix_locus(value):
    fix_locus = first_nonempty(value, default="")
    if not fix_locus:
        return ""
    return fix_locus if fix_locus in FIX_LOCI else "unknown"


def normalize_notes(value):
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    text = str(value).strip()
    if not text:
        return []
    return [part.strip() for part in text.split(";") if part.strip()]


def infer_score_subject(result, expected_skill, suite):
    explicit = str(result.get("score_subject") or "").strip()
    if explicit in {"verify", "review", "routing", "closeout", "generic"}:
        return explicit

    route_boundary = str(result.get("route_boundary") or "").lower()
    suite_text = suite.lower()
    if "closeout" in route_boundary:
        return "closeout"
    if "review" in route_boundary:
        return "review"
    if "routing" in route_boundary:
        return "routing"
    if "verify" in route_boundary:
        return "verify"

    if expected_skill == "verify":
        return "verify"
    if expected_skill == "dispatch" and "review" in suite_text:
        return "review"
    if "routing" in suite_text:
        return "routing"
    if "closeout" in suite_text:
        return "closeout"
    if "review" in suite_text and "verify" not in suite_text:
        return "review"
    if "verify" in suite_text:
        return "verify"
    return "generic"


def normalize_checker_results(value):
    if isinstance(value, list):
        return value
    return []


def score_from_result(result: dict, *, score_version: str = "v0.4.2") -> dict:
    """Return a schema-shaped score dict for a runner result record."""
    case_id = first_nonempty(result.get("id"))
    suite = first_nonempty(result.get("suite"))
    expected_skill = normalize_workflow_route(result.get("expected_route") or result.get("expected"))
    triggered_skill = normalize_workflow_route(result.get("actual_route") or result.get("actual"))
    overall_verdict = normalize_overall_verdict(result.get("overall_verdict") or result.get("verdict"))

    score = {
        "metadata": {
            "schema_version": "2020-12",
            "schema_name": "groundwork-eval-score",
            "score_version": score_version,
            "suite": suite,
            "case_id": case_id,
        },
        "case_id": case_id,
        "suite": suite,
        "expected_skill": expected_skill,
        "triggered_skill": triggered_skill,
        "output_contract_verdict": normalize_dimension_verdict(result.get("output_contract_verdict")),
        "evidence_verdict": normalize_dimension_verdict(result.get("evidence_verdict")),
        "behavior_verdict": normalize_dimension_verdict(result.get("behavior_verdict")),
        "routing_verdict": normalize_dimension_verdict(result.get("routing_verdict")),
        "host_preemption_verdict": normalize_dimension_verdict(result.get("host_preemption_verdict")),
        "overall_verdict": overall_verdict,
        "failure_type": normalize_failure_type(result.get("failure_type")),
        "checker_results": normalize_checker_results(result.get("checker_results")),
        "score_subject": infer_score_subject(result, expected_skill, suite),
    }

    fix_locus = normalize_fix_locus(result.get("fix_locus"))
    if fix_locus:
        score["fix_locus"] = fix_locus

    notes = normalize_notes(result.get("notes"))
    if notes:
        score["notes"] = notes

    return score
