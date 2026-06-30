"""Router observability verdict and card helpers."""

from datetime import datetime, timezone

try:
    from route_detection import detect_route_from_text
    from routing_schema import as_list, normalize_route
except ImportError:  # pragma: no cover - package import path
    from evals.route_detection import detect_route_from_text
    from evals.routing_schema import as_list, normalize_route


NOT_APPLICABLE = "not_applicable"
VERIFY_SCOPE_FIELDS = [
    "In Scope",
    "Out of Scope",
    "Covered",
    "Not Covered",
    "Evidence Sources",
    "User-visible Claim Being Verified",
]


def utc_now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def normalize_execution_profile(source_value="", *, task_shape="", selector_enforcement="prompt_preference"):
    text = f"{source_value} {task_shape}".lower()
    profile_options = {"model_profiles": [], "reasoning_efforts": [], "cost_latency_biases": []}

    if "reviewer" in text or "clean review" in text:
        profile_options["model_profiles"].append("exhaustive_review")
        model_profile = "exhaustive_review"
    elif "strongest" in text or "schema" in text or "security" in text or "migration" in text:
        profile_options["model_profiles"].append("strong_reasoning")
        model_profile = "strong_reasoning"
    elif "fast" in text or "tiny" in text:
        profile_options["model_profiles"].append("fast_scan")
        model_profile = "fast_scan"
    elif text.strip():
        profile_options["model_profiles"].append("balanced_work")
        model_profile = "balanced_work"
    else:
        model_profile = "unknown"

    if "xhigh" in text:
        profile_options["reasoning_efforts"].append("xhigh")
        reasoning_effort = "xhigh"
    elif "medium/high" in text or "high" in text or model_profile in {"strong_reasoning", "exhaustive_review"}:
        profile_options["reasoning_efforts"].extend(["medium", "high"] if "medium/high" in text else ["high"])
        reasoning_effort = "high"
    elif "low" in text:
        profile_options["reasoning_efforts"].append("low")
        reasoning_effort = "low"
    elif text.strip():
        profile_options["reasoning_efforts"].append("medium")
        reasoning_effort = "medium"
    else:
        reasoning_effort = "unknown"

    if "balanced/quality" in text:
        profile_options["cost_latency_biases"].extend(["balanced", "quality"])
        cost_latency_bias = "quality" if model_profile in {"strong_reasoning", "exhaustive_review"} else "balanced"
    elif "quality" in text or model_profile in {"strong_reasoning", "exhaustive_review"}:
        profile_options["cost_latency_biases"].append("quality")
        cost_latency_bias = "quality"
    elif "fast" in text:
        profile_options["cost_latency_biases"].append("fast")
        cost_latency_bias = "fast"
    elif text.strip():
        profile_options["cost_latency_biases"].append("balanced")
        cost_latency_bias = "balanced"
    else:
        cost_latency_bias = "unknown"

    return {
        "model_profile": model_profile,
        "reasoning_effort": reasoning_effort,
        "cost_latency_bias": cost_latency_bias,
        "profile_source": "dispatch_routing_profile" if source_value else "unknown",
        "profile_source_value": source_value,
        "profile_options": {key: sorted(set(value)) for key, value in profile_options.items()},
        "normalization_reason": (
            "normalized from dispatch routing profile source value"
            if source_value
            else "no execution profile source was provided"
        ),
        "concrete_model": "",
        "capability_status": "known" if source_value else "unknown",
        "selector_enforcement": selector_enforcement,
        "selector_enforcement_policy": "tool_if_available_else_prompt_preference",
        "evidence_layer": "prompt_preference",
    }


def dispatch_decision_from_entry(decision):
    entry = decision.get("entry_decision") or {}
    expected = str(entry.get("expected_best") or "")
    prompt_source = str(decision.get("prompt_text_for_detection") or decision.get("prompt_snippet") or "")
    if expected != "dispatch" and "dispatch" not in prompt_source.lower():
        return None
    task_shape = "clean review" if "clean review" in prompt_source.lower() else "dispatch"
    profile_source_value = (
        "Read-only multi-perspective clean review -> reviewer profile / medium/high / balanced/quality"
        if task_shape == "clean review"
        else "Dispatch selected or mentioned -> balanced runtime routing / medium / balanced"
    )
    profile = normalize_execution_profile(profile_source_value, task_shape=task_shape)
    return {
        "schema_version": "router_observability.dispatch_decision.v0",
        "session_id": decision.get("session_id", "unknown"),
        "turn_id": decision.get("turn_id", "unknown"),
        "dispatch_version": 2,
        "task_id": decision.get("turn_id", "unknown"),
        "task_shape": task_shape.replace(" ", "_"),
        "task_type": "hybrid",
        "runtime_id": "main_thread_readonly",
        "route_decision": "local_with_artifact",
        "decision_source": "heuristic_dispatch_candidate",
        "actual_dispatch_output_observed": False,
        "score_eligibility": "insufficient_evidence",
        "evidence_boundary": "heuristic dispatch candidate only; not actual dispatch skill output or runtime adapter evidence",
        "execution_profile": profile,
        "expected_result_package": "review_package",
        "execution_claim": "not_executed_by_dispatch",
        "selector_evidence": {
            "runtime_reported": False,
            "source": "dispatch_package",
            "notes": [],
        },
    }


def dispatch_requires_strong_profile(dispatch_decision):
    if not dispatch_decision:
        return False
    if dispatch_decision.get("clean_review_required") is True:
        return True
    task_shape = str(dispatch_decision.get("task_shape") or "").strip().lower().replace("-", "_").replace(" ", "_")
    if task_shape in {"clean_review", "read_only_clean_review"}:
        return True
    review_type = str(dispatch_decision.get("review_type") or "").strip().lower().replace("-", "_").replace(" ", "_")
    if review_type in {"clean_review", "independent_clean_review"}:
        return True
    route_decision = str(dispatch_decision.get("route_decision") or "").strip().lower()
    return route_decision in {"clean_review", "worktree_clean_review", "readonly_clean_review"}


def execution_profile_verdict(dispatch_decision):
    if not dispatch_decision:
        return "not_applicable", "none"
    profile = dispatch_decision.get("execution_profile") or {}
    if not isinstance(profile, dict):
        return "insufficient_evidence", "selector_unverified"
    required = ["model_profile", "reasoning_effort", "cost_latency_bias", "selector_enforcement", "evidence_layer"]
    if any(not str(profile.get(field) or "").strip() for field in required):
        return "insufficient_evidence", "selector_unverified"
    if profile.get("selector_enforcement") == "tool_enforced":
        selector_evidence = dispatch_decision.get("selector_evidence") or {}
        if not selector_evidence.get("runtime_reported"):
            return "insufficient_evidence", "selector_unverified"
        if profile.get("evidence_layer") != "runtime_tool_evidence":
            return "insufficient_evidence", "selector_unverified"
        if selector_evidence.get("source") not in {"runtime_adapter", "tool_report"}:
            return "insufficient_evidence", "selector_unverified"
    if profile.get("model_profile") in {"fast_scan", "spark_iteration"} and dispatch_requires_strong_profile(dispatch_decision):
        return "mismatch", "profile_too_weak_for_risk"
    return "pass", "none"


def checker_results_for_score(expected, actual, final_message, decision):
    final_text = str(final_message or "")
    route_match = actual == expected and actual != "unknown"
    final_hash = decision.get("final_sha256") or ""
    if final_text:
        final_hash = final_hash or __import__("hashlib").sha256(final_text.encode("utf-8")).hexdigest()
    return [
        {
            "checker_id": "router_observability.actual_route_marker",
            "verdict": "pass" if actual != "unknown" else "fail",
            "severity": "p2" if actual == "unknown" else "none",
            "notes": [f"actual_route={actual}", f"final_sha256={final_hash}"] if final_hash else [f"actual_route={actual}"],
        },
        {
            "checker_id": "router_observability.expected_actual_match",
            "verdict": "pass" if route_match else "fail",
            "severity": "p2" if not route_match else "none",
            "notes": [f"expected_route={expected}", f"actual_route={actual}"],
        },
    ]


def output_contract_check(expected, final_message):
    text = str(final_message or "")
    if not text:
        return "blocked", {
            "checker_id": "router_observability.output_contract",
            "verdict": "fail",
            "severity": "p2",
            "fix_locus": "skill_output_contract",
            "notes": ["final_message_missing"],
        }, "output_contract_failure", "skill_output_contract"
    if expected == "verify":
        missing = [field for field in VERIFY_SCOPE_FIELDS if field not in text]
        first_line = text.splitlines()[0].strip() if text.splitlines() else ""
        if first_line != "Verification Scope" or missing:
            return "fail", {
                "checker_id": "router_observability.verify_scope_full",
                "verdict": "fail",
                "severity": "p1",
                "fix_locus": "skill_output_contract",
                "notes": [f"first_line={first_line or 'missing'}"] + [f"missing={field}" for field in missing],
            }, "output_contract_failure", "skill_output_contract"
    return "pass", {
        "checker_id": "router_observability.output_contract",
        "verdict": "pass",
        "severity": "none",
        "notes": [f"expected_route={expected}"],
    }, "none", "unknown"


def tool_coverage_status(events):
    if not events:
        return "unknown"
    statuses = {str(event.get("coverage_status") or "unknown") for event in events}
    if statuses == {"observed_supported"}:
        return "supported_events_observed"
    if "observed_supported" in statuses:
        return "partial"
    if "unsupported" in statuses:
        return "unsupported"
    return "unknown"


def apply_live_score_authority_gate(score, decision):
    blockers = []
    if decision.get("decision_mode") == "guided_hint_trial" or score.get("router_hint_emitted"):
        score["score_eligibility"] = "guided_hint_excluded"
        return score
    if decision.get("decision_mode") != "observe_only":
        blockers.append("decision_mode")
    if score.get("expected_route_source") not in {"fixture", "deterministic_entry_classifier"}:
        blockers.append("expected_route_source")
    if score.get("expected_route_source") == "deterministic_entry_classifier":
        evidence = decision.get("classifier_evidence") or {}
        if not evidence.get("accepted_fixture_evidence"):
            blockers.append("classifier_evidence")
    if score.get("actual_route_source") == "unknown":
        blockers.append("actual_route_source")
    if score.get("tool_coverage_status") != "supported_events_observed":
        blockers.append("tool_coverage_status")
    if score.get("execution_profile_verdict") not in {"not_applicable", "pass"}:
        blockers.append("execution_profile_verdict")
    if score.get("execution_profile_verdict") not in {"not_applicable", "pass"} and score.get("execution_profile_source") == "unknown":
        blockers.append("execution_profile_source")
    if not score.get("checker_results"):
        blockers.append("checker_results")

    if blockers:
        if score.get("expected_route_source") == "heuristic":
            score["score_eligibility"] = "display_only"
            score["notes"] = (
                "display-only live heuristic; candidate verdict is not baseline scoring evidence; "
                "baseline scoring blocked by: " + ", ".join(blockers)
            )
            return score
        score["score_eligibility"] = "insufficient_evidence"
        score["routing_verdict"] = "blocked"
        score["overall_verdict"] = "blocked"
        score["failure_type"] = "route_miss" if score.get("actual_route") == "unknown" else score.get("failure_type", "unclassified")
        score["notes"] = "baseline scoring blocked by: " + ", ".join(blockers)
    else:
        score["score_eligibility"] = "baseline_eligible"
    return score


def score_turn(decision, final_message="", events=None, dispatch_decision=None, changed_files=None):
    events = events or []
    changed_files = changed_files or []
    entry = decision.get("entry_decision") or {}
    expected = normalize_route(entry.get("expected_best"))
    acceptable = as_list(entry.get("acceptable_routes")) or ([expected] if expected != "unknown" else [])
    forbidden = as_list(entry.get("forbidden_routes"))
    actual, actual_source = detect_route_from_text(final_message)
    actual = normalize_route(actual)
    dispatches = [dispatch_decision] if dispatch_decision else []
    profile_verdict, selector_mismatch_reason = execution_profile_verdict(dispatch_decision)

    if actual == expected or actual in acceptable:
        routing_verdict = "pass"
        overall = "pass"
        failure_type = "none"
        fix_locus = "unknown"
    elif actual in forbidden:
        routing_verdict = "fail"
        overall = "fail"
        failure_type = "forbidden_route"
        fix_locus = "routing_surface"
    elif actual == "unknown":
        routing_verdict = "blocked"
        overall = "blocked"
        failure_type = "route_miss"
        fix_locus = "routing_surface"
    else:
        routing_verdict = "fail"
        overall = "fail"
        failure_type = "route_miss"
        fix_locus = "routing_surface"

    selector_enforcement = "unknown"
    if dispatch_decision:
        selector_enforcement = (
            (dispatch_decision.get("execution_profile") or {}).get("selector_enforcement")
            or "unknown"
        )

    output_contract_verdict, output_checker, output_failure_type, output_fix_locus = output_contract_check(expected, final_message)
    checker_results = checker_results_for_score(expected, actual, final_message, decision)
    checker_results.append(output_checker)
    if output_contract_verdict != "pass":
        overall = "blocked" if output_contract_verdict == "blocked" else "fail"
        failure_type = output_failure_type
        fix_locus = output_fix_locus
    score = {
        "schema_version": "router_observability.score.v0",
        "session_id": decision.get("session_id", "unknown"),
        "turn_id": decision.get("turn_id", "unknown"),
        "created_at": utc_now(),
        "expected_route": expected,
        "actual_route": actual,
        "route_boundary": entry.get("route_boundary", "entry-contract"),
        "expected_route_source": decision.get("decision_source", "unknown"),
        "actual_route_source": actual_source,
        "skill_hit_source": actual_source,
        "tool_coverage_status": tool_coverage_status(events),
        "score_eligibility": "insufficient_evidence",
        "acceptable_routes": acceptable,
        "forbidden_routes": forbidden,
        "routing_verdict": routing_verdict,
        "candidate_routing_verdict": routing_verdict,
        "host_preemption_verdict": NOT_APPLICABLE,
        "execution_profile_verdict": profile_verdict,
        "execution_profile_source": "dispatch_decision" if dispatch_decision else "unknown",
        "selector_enforcement": selector_enforcement,
        "selector_mismatch_reason": selector_mismatch_reason,
        "output_contract_verdict": output_contract_verdict,
        "evidence_verdict": "pass" if events or final_message else "blocked",
        "behavior_verdict": "pass" if overall == "pass" else "fail",
        "overall_verdict": overall,
        "candidate_overall_verdict": overall,
        "failure_type": failure_type,
        "fix_locus": fix_locus,
        "changed_files": changed_files,
        "skill_hits": [] if actual == "unknown" else [actual],
        "dispatch_decisions": dispatches,
        "router_hint_emitted": bool(decision.get("router_hint_emitted")),
        "checker_results": checker_results,
        "notes": "",
        "evidence_boundary": "local hook score only; not release, runtime, cache, UAT, or customer readiness evidence",
    }
    return apply_live_score_authority_gate(score, decision)


def render_router_card(score, decision=None, dispatch_decision=None):
    decision = decision or {}
    lines = [
        "# Groundwork Router Decision",
        "",
        "## Input Summary",
        f"- Session: `{score.get('session_id', 'unknown')}`",
        f"- Turn: `{score.get('turn_id', 'unknown')}`",
        "",
        "## Expected Route",
        f"- `{score.get('expected_route', 'unknown')}`",
        "",
        "## Expected Route Source",
        f"- `{score.get('expected_route_source', 'unknown')}`",
        "",
        "## Actual Route",
        f"- `{score.get('actual_route', 'unknown')}`",
        "",
        "## Actual Route Source",
        f"- `{score.get('actual_route_source', 'unknown')}`",
        "",
        "## Tool Coverage",
        f"- `{score.get('tool_coverage_status', 'unknown')}`",
    ]
    if dispatch_decision:
        profile = dispatch_decision.get("execution_profile") or {}
        lines.extend(
            [
                "",
                "## Dispatch Candidate",
                f"- Runtime: `{dispatch_decision.get('runtime_id', 'unknown')}`",
                f"- Route decision: `{dispatch_decision.get('route_decision', 'unknown')}`",
                f"- Decision source: `{dispatch_decision.get('decision_source', 'unknown')}`",
                f"- Actual dispatch output observed: `{dispatch_decision.get('actual_dispatch_output_observed', 'unknown')}`",
                f"- Execution claim: `{dispatch_decision.get('execution_claim', 'unknown')}`",
                "",
                "## Execution Profile Decision",
                f"- Model profile: `{profile.get('model_profile', 'unknown')}`",
                f"- Reasoning effort: `{profile.get('reasoning_effort', 'unknown')}`",
                f"- Cost/latency bias: `{profile.get('cost_latency_bias', 'unknown')}`",
                "",
                "## Selector Enforcement Evidence",
                f"- Selector enforcement: `{profile.get('selector_enforcement', 'unknown')}`",
                f"- Evidence layer: `{profile.get('evidence_layer', 'unknown')}`",
            ]
        )
    lines.extend(
        [
            "",
            "## Verdicts",
            f"- routing_verdict: `{score.get('routing_verdict', 'unknown')}`",
            f"- execution_profile_verdict: `{score.get('execution_profile_verdict', 'unknown')}`",
            f"- output_contract_verdict: `{score.get('output_contract_verdict', 'unknown')}`",
            f"- evidence_verdict: `{score.get('evidence_verdict', 'unknown')}`",
            f"- behavior_verdict: `{score.get('behavior_verdict', 'unknown')}`",
            f"- overall_verdict: `{score.get('overall_verdict', 'unknown')}`",
            "",
            "## Failure Classification",
            f"- failure_type: `{score.get('failure_type', 'unknown')}`",
            f"- fix_locus: `{score.get('fix_locus', 'unknown')}`",
            "",
            "## Evidence Used",
            f"- changed_files: `{len(score.get('changed_files') or [])}`",
            f"- skill_hits: `{', '.join(score.get('skill_hits') or []) or 'none'}`",
            "",
            "## Limitations",
            f"- {score.get('evidence_boundary')}",
            (
                "- Live heuristic display-only: candidate verdicts are shown for review, "
                "but they do not count as baseline pass/fail evidence."
                if score.get("score_eligibility") == "display_only"
                else ""
            ),
            "",
            "## Score Eligibility",
            f"- `{score.get('score_eligibility', 'unknown')}`",
            "",
            "## Next Suggested Action",
            "- Review this card and backfill a redacted eval row only when the failure is reproducible and useful.",
            "",
        ]
    )
    return "\n".join(lines)
