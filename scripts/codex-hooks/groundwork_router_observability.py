"""Codex hook helpers for Groundwork router observability v0."""

import hashlib
import importlib.util
import json
import os
import re
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path


def _load_route_detection_module():
    try:
        import groundwork_route_detection

        return groundwork_route_detection
    except ImportError:
        module_path = Path(__file__).with_name("groundwork_route_detection.py")
        spec = importlib.util.spec_from_file_location("groundwork_route_detection", module_path)
        if spec is None or spec.loader is None:
            raise
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module


_route_detection = _load_route_detection_module()
CLASSIFIER_SOURCE_PATH = _route_detection.CLASSIFIER_SOURCE_PATH
PUBLIC_SKILL_ROUTES = _route_detection.PUBLIC_SKILL_ROUTES
DIRECT_ROUTE = _route_detection.DIRECT_ROUTE
UNKNOWN_ROUTE = _route_detection.UNKNOWN_ROUTE
HOST_PREEMPTION_ROUTE = _route_detection.HOST_PREEMPTION_ROUTE
WORKFLOW_ROUTES = _route_detection.WORKFLOW_ROUTES
normalize_route = _route_detection.normalize_route
as_list = _route_detection.as_list
detect_route_from_text = _route_detection.detect_route_from_text
has_dispatch_route_marker = _route_detection.has_dispatch_route_marker
entry_decision_from_prompt = _route_detection.entry_decision_from_prompt
classify_command = _route_detection.classify_command
risk_markers = _route_detection.risk_markers
evidence_markers = _route_detection.evidence_markers


SECRET_PATTERNS = (
    (re.compile(r"(Authorization:\s*Bearer\s+)[^\s,;]+", re.I), r"\1[REDACTED]"),
    (re.compile(r"(token=)[^\s,;]+", re.I), r"\1[REDACTED]"),
    (re.compile(r"(api[_-]?key=)[^\s,;]+", re.I), r"\1[REDACTED]"),
    (re.compile(r"((?:password|passwd|client[_-]?secret|aws_secret_access_key)\s*[:=]\s*)[^\s,;]+", re.I), r"\1[REDACTED]"),
    (re.compile(r"(cookie:\s*)[^\n]+", re.I), r"\1[REDACTED]"),
    (re.compile(r"\b(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9_]{20,}\b"), "[REDACTED_GITHUB_TOKEN]"),
    (re.compile(r"\bgithub_pat_[A-Za-z0-9_]{20,}\b"), "[REDACTED_GITHUB_PAT]"),
    (re.compile(r"\bAKIA[0-9A-Z]{16}\b"), "[REDACTED_AWS_ACCESS_KEY_ID]"),
    (re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}\b"), "[REDACTED_SLACK_TOKEN]"),
    (re.compile(r"\bsk-(?:[A-Za-z0-9]+-)?[A-Za-z0-9_-]{20,}\b"), "[REDACTED_OPENAI_KEY]"),
    (
        re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----.*?-----END [A-Z ]*PRIVATE KEY-----", re.S),
        "[REDACTED_PRIVATE_KEY]",
    ),
)

DEFAULT_CONFIG = {
    "enabled": False,
    "mode": "observe_only",
    "raw_capture": False,
    "snippet_capture": False,
}
ROUTER_OBSERVABILITY_MODES = {"observe_only", "thin_prompt_trial", "guided_hint_trial"}
THIN_PROMPT_CONTEXT = (
    "Groundwork context: Preserve evidence boundaries. Do not upgrade local, source, runtime, "
    "test, screenshot, cache, or self-check evidence into readiness, release, UAT, customer "
    "acceptance, or clean-review claims unless the user asks for that scope and evidence is "
    "present. Keep the user's requested task primary and preserve the requested answer shape. If "
    "information is missing, say what is unknown without inventing source truth or escalating the "
    "claim. Do not create artifacts or change files unless the user explicitly requested that action "
    "and the available evidence supports it."
)

NOT_APPLICABLE = "not_applicable"
VERIFY_SCOPE_FIELDS = [
    "In Scope",
    "Out of Scope",
    "Covered",
    "Not Covered",
    "Evidence Sources",
    "User-visible Claim Being Verified",
]

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
        final_hash = final_hash or hashlib.sha256(final_text.encode("utf-8")).hexdigest()
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
    if decision.get("decision_mode") == "thin_prompt_trial" or score.get("prompt_enhancement_emitted"):
        score["score_eligibility"] = "thin_prompt_excluded"
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
    route_evidence_source = actual_source
    if actual == UNKNOWN_ROUTE:
        route_evidence_source = "unknown"
    elif actual == "dispatch" and has_dispatch_route_marker(final_message):
        route_evidence_source = "output_marker"
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
    if actual == "dispatch":
        dispatch_hit_level = "output_shape_only"
    elif expected == "dispatch" or "dispatch" in acceptable:
        dispatch_hit_level = "missed"
    else:
        dispatch_hit_level = "not_applicable"

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
        "route_evidence_source": route_evidence_source,
        "skill_hit_source": "unknown",
        "dispatch_hit_level": dispatch_hit_level,
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
        "skill_hits": [],
        "dispatch_decisions": dispatches,
        "router_hint_emitted": bool(decision.get("router_hint_emitted")),
        "prompt_enhancement_emitted": bool(decision.get("prompt_enhancement_emitted")),
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
        "## Route Evidence Source",
        f"- `{score.get('route_evidence_source', 'unknown')}`",
        "",
        "## Dispatch Hit Level",
        f"- `{score.get('dispatch_hit_level', 'unknown')}`",
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


def utc_now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_stdin_event():
    raw = sys.stdin.read()
    if not raw.strip():
        return {}
    return json.loads(raw)


def redact_text(text, *, compact=False, limit=None):
    value = str(text or "")
    for pattern, replacement in SECRET_PATTERNS:
        value = pattern.sub(replacement, value)
    if compact:
        value = " ".join(value.split())
    if limit is not None:
        value = value[:limit]
    return value


def redacted_snippet(text, limit=120):
    return redact_text(text, compact=True, limit=limit)


def stable_hash(text):
    return hashlib.sha256(str(text or "").encode("utf-8")).hexdigest()


def cwd_from_event(event):
    value = event.get("cwd") or event.get("working_dir") or event.get("workspace_dir") or os.getcwd()
    return Path(value).resolve()


def config_path(cwd):
    return cwd / ".groundwork" / "harness" / "router-observability" / "config.json"


def load_config(cwd):
    if os.environ.get("GROUNDWORK_ROUTER_OBSERVABILITY_DISABLED"):
        return None, "env_disabled"
    config = dict(DEFAULT_CONFIG)
    path = config_path(cwd)
    config_source = "absent"
    if path.exists():
        try:
            loaded = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            if os.environ.get("GROUNDWORK_ROUTER_OBSERVABILITY") != "1":
                return None, "invalid_config"
            config_source = "invalid_config_env_force_enable"
        else:
            if isinstance(loaded, dict):
                config.update(loaded)
                config_source = str(path.relative_to(cwd))
    if os.environ.get("GROUNDWORK_ROUTER_OBSERVABILITY") == "1":
        config["enabled"] = True
        config["mode"] = os.environ.get("GROUNDWORK_ROUTER_OBSERVABILITY_MODE", config.get("mode") or "observe_only")
        if config_source == "absent":
            return config, "env"
        if config_source == "invalid_config_env_force_enable":
            return config, config_source
        return config, "env_force_enable_over_config"
    if config_source != "absent":
        return config, config_source
    return None, "absent"


def normalize_mode(value):
    mode = str(value or "observe_only").strip()
    if mode in ROUTER_OBSERVABILITY_MODES:
        return mode
    return "observe_only"


def ids_from_event_with_sources(event):
    session_source = "session_id"
    session_id = event.get("session_id")
    if not session_id:
        session_source = "conversation_id"
        session_id = event.get("conversation_id")
    if not session_id:
        session_source = "thread_id"
        session_id = event.get("thread_id")
    if not session_id:
        session_source = "fallback"
        session_id = "session-unknown"

    turn_source = "turn_id"
    turn_id = event.get("turn_id")
    if not turn_id:
        turn_source = "event_id"
        turn_id = event.get("event_id")
    if not turn_id:
        turn_source = "request_id"
        turn_id = event.get("request_id")
    if not turn_id and event.get("tool_use_id"):
        turn_source = "tool_use_id_fallback"
        turn_id = stable_hash(f"{session_id}:tool:{event.get('tool_use_id')}")[:12]
    if not turn_id and event.get("transcript_path"):
        turn_source = "transcript_path_fallback"
        turn_id = stable_hash(f"{session_id}:transcript:{event.get('transcript_path')}")[:12]
    if not turn_id:
        turn_source = "event_hash_fallback"
        turn_id = stable_hash(json.dumps(event, sort_keys=True))[:12]
    return str(session_id), str(turn_id), session_source, turn_source


def is_enabled(config):
    return bool(config and config.get("enabled"))


def ids_from_event(event):
    session_id, turn_id, _, _ = ids_from_event_with_sources(event)
    return session_id, turn_id


def turn_dir(cwd, event):
    session_id, turn_id = ids_from_event(event)
    return cwd / ".groundwork" / "harness" / "router-observability" / session_id / turn_id


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def append_jsonl(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(value, ensure_ascii=False, sort_keys=True) + "\n")


def read_json(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None


def read_jsonl_with_diagnostics(path):
    rows = []
    malformed = 0
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except FileNotFoundError:
        return rows, malformed
    for line in lines:
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError:
            malformed += 1
            continue
        if isinstance(value, dict):
            rows.append(value)
    return rows, malformed


def read_jsonl(path):
    rows, _malformed = read_jsonl_with_diagnostics(path)
    return rows


def event_metadata():
    return {
        "observed_at_ns": time.time_ns(),
        "pid": os.getpid(),
        "event_uuid": str(uuid.uuid4()),
    }


def raw_capture_allows_unredacted():
    return os.environ.get("GROUNDWORK_ROUTER_OBSERVABILITY_ALLOW_UNREDACTED_RAW_CAPTURE") == "1"


def raw_capture_payload(key, value):
    if raw_capture_allows_unredacted():
        return {
            key: value,
            "redaction": {"status": "unredacted_explicitly_allowed", "notes": []},
        }
    return {
        key: redact_text(value),
        "redaction": {
            "status": "redacted",
            "notes": ["set GROUNDWORK_ROUTER_OBSERVABILITY_ALLOW_UNREDACTED_RAW_CAPTURE=1 to store unredacted raw text"],
        },
    }


def ordered_events_for_stop(out_dir):
    tool_events, malformed_tool_events = read_jsonl_with_diagnostics(out_dir / "tool-events.jsonl")
    permission_events, malformed_permission_events = read_jsonl_with_diagnostics(out_dir / "permission-events.jsonl")
    events = tool_events + permission_events
    events.sort(
        key=lambda event: (
            int(event.get("observed_at_ns") or 0),
            str(event.get("event_uuid") or ""),
        )
    )
    for index, event in enumerate(events, start=1):
        event["event_index"] = index
    diagnostics = {
        "schema_version": "router_observability.coverage.v0",
        "tool_events": len(tool_events),
        "permission_events": len(permission_events),
        "malformed_tool_events": malformed_tool_events,
        "malformed_permission_events": malformed_permission_events,
        "event_ordering": "observed_at_ns,event_uuid",
    }
    return events, diagnostics


def prompt_from_event(event):
    return (
        event.get("prompt")
        or event.get("user_prompt")
        or event.get("input")
        or event.get("message")
        or ""
    )


def final_message_from_event(event):
    return (
        event.get("last_assistant_message")
        or event.get("final_response")
        or event.get("assistant_response")
        or event.get("final_message")
        or event.get("message")
        or ""
    )


def tool_name_from_event(event):
    return str(event.get("tool_name") or event.get("tool") or event.get("name") or "unknown")


def command_from_event(event):
    tool_input = event.get("tool_input") or event.get("input") or {}
    if isinstance(tool_input, dict):
        return (
            tool_input.get("command")
            or tool_input.get("cmd")
            or tool_input.get("patch")
            or tool_input.get("arguments")
            or ""
        )
    return str(tool_input or event.get("command") or "")


def compact_jsonish(value):
    try:
        return json.dumps(value, ensure_ascii=False, sort_keys=True)
    except TypeError:
        return str(value or "")


def tool_response_summary(event):
    marker = object()
    response = event.get("tool_response", marker)
    if response is marker:
        response = event.get("response", marker)
    if response is marker:
        return {
            "tool_response_present": False,
            "tool_response_status": "",
            "tool_response_length": 0,
            "tool_response_sha256": "",
        }
    text = compact_jsonish(response)
    status = ""
    if isinstance(response, dict):
        for key in ("status", "outcome", "exit_code", "returncode", "rc"):
            if key in response and response.get(key) is not None:
                status = str(response.get(key))
                break
    return {
        "tool_response_present": True,
        "tool_response_status": status,
        "tool_response_length": len(text),
        "tool_response_sha256": stable_hash(text),
    }


def guided_route_hint(decision):
    route = str((decision or {}).get("expected_best") or "unknown")
    if route == "verify":
        return (
            "Groundwork route hint: use verify-lite. Final answer must start with the exact line "
            "`Verification Scope`, followed by all six fields: In Scope, Out of Scope, Covered, "
            "Not Covered, Evidence Sources, User-visible Claim Being Verified. Do not answer as direct."
        )
    return ""


def additional_context_for_mode(mode, decision):
    if mode == "thin_prompt_trial":
        route = str((decision or {}).get("expected_best") or "unknown")
        if route == DIRECT_ROUTE:
            return ""
        return THIN_PROMPT_CONTEXT
    if mode == "guided_hint_trial":
        return guided_route_hint(decision)
    return ""


def handle_user_prompt_submit(event):
    cwd = cwd_from_event(event)
    config, source = load_config(cwd)
    if not is_enabled(config):
        return None
    session_id, turn_id, session_id_source, turn_id_source = ids_from_event_with_sources(event)
    mode = normalize_mode(config.get("mode"))
    raw_capture = bool(config.get("raw_capture"))
    snippet_capture = bool(config.get("snippet_capture"))
    prompt = prompt_from_event(event)
    decision = entry_decision_from_prompt(prompt)
    additional_context = additional_context_for_mode(mode, decision)
    router_hint_emitted = mode == "guided_hint_trial" and bool(additional_context)
    prompt_enhancement_emitted = mode == "thin_prompt_trial" and bool(additional_context)
    out_dir = turn_dir(cwd, event)
    prompt_metadata = {
        "schema_version": "router_observability.prompt_metadata.v0",
        "session_id": session_id,
        "turn_id": turn_id,
        "session_id_source": session_id_source,
        "turn_id_source": turn_id_source,
        "created_at": utc_now(),
        "prompt_sha256": stable_hash(prompt),
        "prompt_length": len(str(prompt or "")),
        "prompt_snippet": redacted_snippet(prompt) if snippet_capture else "",
        "snippet_capture": "enabled" if snippet_capture else "disabled",
        "raw_prompt_storage": "enabled" if raw_capture else "disabled",
    }
    router_decision = {
        "schema_version": "router_observability.v0",
        "session_id": session_id,
        "turn_id": turn_id,
        "session_id_source": session_id_source,
        "turn_id_source": turn_id_source,
        "created_at": utc_now(),
        "cwd": str(cwd),
        "deployment_target": "personal_maintainer_cross_project_trial",
        "hook_packaging": "plugin_bundled",
        "project_opt_in": True,
        "activation_source": source,
        "decision_mode": mode,
        "router_hint_emitted": router_hint_emitted,
        "prompt_enhancement_emitted": prompt_enhancement_emitted,
        "raw_prompt_storage": "enabled" if raw_capture else "disabled",
        "snippet_capture": "enabled" if snippet_capture else "disabled",
        "entry_decision": decision,
        "decision_evidence": [{"kind": "prompt_hash", "value": prompt_metadata["prompt_sha256"]}],
        "decision_source": "heuristic",
        "confidence": "medium" if decision["expected_best"] != "unknown" else "low",
        "limitations": [
            "heuristic live candidate; fixture-backed replay required for route truth",
            "prompt and final snippets are disabled by default unless snippet_capture is explicitly enabled",
        ],
    }
    write_json(out_dir / "prompt-metadata.json", prompt_metadata)
    write_json(out_dir / "router-decision.json", router_decision)
    dispatch_decision = dispatch_decision_from_entry(
        {
            **router_decision,
            "prompt_snippet": prompt_metadata["prompt_snippet"],
            "prompt_text_for_detection": prompt,
        }
    )
    if dispatch_decision:
        write_json(out_dir / "dispatch-decision.json", dispatch_decision)
    if raw_capture:
        write_json(out_dir / "prompt.raw.json", raw_capture_payload("prompt", prompt))
    if additional_context:
        return {"hookSpecificOutput": {"hookEventName": "UserPromptSubmit", "additionalContext": additional_context}}
    return None


def handle_tool_event(event, hook_event_name):
    cwd = cwd_from_event(event)
    config, _ = load_config(cwd)
    if not is_enabled(config):
        return None
    out_dir = turn_dir(cwd, event)
    tool_name = tool_name_from_event(event)
    command = command_from_event(event)
    session_id, turn_id, session_id_source, turn_id_source = ids_from_event_with_sources(event)
    tool_input = event.get("tool_input") or event.get("input") or {}
    event_row = {
        "schema_version": "router_observability.tool_event.v0",
        "session_id": session_id,
        "turn_id": turn_id,
        "session_id_source": session_id_source,
        "turn_id_source": turn_id_source,
        "hook_event_name": hook_event_name,
        "tool_name": tool_name,
        "tool_use_id": str(event.get("tool_use_id") or ""),
        "tool_input_sha256": stable_hash(compact_jsonish(tool_input)) if tool_input else "",
        "command_class": classify_command(command, tool_name),
        "coverage_status": "observed_supported" if tool_name in {"Bash", "apply_patch"} or tool_name.startswith("mcp__") else "unsupported",
        "coverage_limitations": ["hooks do not prove complete shell, WebSearch, non-shell, or non-MCP coverage"],
        "risk_markers": risk_markers(command, tool_name),
        "evidence_markers": evidence_markers(command),
        "status": str(event.get("status") or "unknown"),
        **tool_response_summary(event),
        "redaction": {"status": "not_reviewed", "notes": []},
        **event_metadata(),
    }
    append_jsonl(out_dir / "tool-events.jsonl", event_row)
    return None


def handle_permission_event(event):
    cwd = cwd_from_event(event)
    config, _ = load_config(cwd)
    if not is_enabled(config):
        return None
    out_dir = turn_dir(cwd, event)
    session_id, turn_id, session_id_source, turn_id_source = ids_from_event_with_sources(event)
    row = {
        "schema_version": "router_observability.permission_event.v0",
        "session_id": session_id,
        "turn_id": turn_id,
        "session_id_source": session_id_source,
        "turn_id_source": turn_id_source,
        "hook_event_name": "PermissionRequest",
        "permission": str(event.get("permission") or event.get("action") or "unknown"),
        "command_class": classify_command(command_from_event(event), tool_name_from_event(event)),
        "coverage_status": "observed_supported",
        "coverage_limitations": ["permission hooks do not prove complete tool or shell coverage"],
        "risk_markers": risk_markers(command_from_event(event), tool_name_from_event(event)),
        "evidence_markers": evidence_markers(command_from_event(event)),
        "status": str(event.get("status") or "unknown"),
        "redaction": {"status": "not_reviewed", "notes": []},
        **event_metadata(),
    }
    append_jsonl(out_dir / "permission-events.jsonl", row)
    return None


def handle_stop(event):
    cwd = cwd_from_event(event)
    config, _ = load_config(cwd)
    if not is_enabled(config):
        return None
    out_dir = turn_dir(cwd, event)
    decision = read_json(out_dir / "router-decision.json")
    if not isinstance(decision, dict):
        return None
    final_message = final_message_from_event(event)
    snippet_capture = bool(config.get("snippet_capture"))
    final_metadata = {
        "schema_version": "router_observability.final_metadata.v0",
        "session_id": decision.get("session_id", "unknown"),
        "turn_id": decision.get("turn_id", "unknown"),
        "created_at": utc_now(),
        "final_sha256": stable_hash(final_message),
        "final_length": len(str(final_message or "")),
        "final_snippet": redacted_snippet(final_message) if snippet_capture else "",
        "snippet_capture": "enabled" if snippet_capture else "disabled",
        "raw_final_storage": "enabled" if config.get("raw_capture") else "disabled",
    }
    write_json(out_dir / "final-metadata.json", final_metadata)
    if config.get("raw_capture"):
        final_raw = raw_capture_payload("final", final_message)
        (out_dir / "final.raw.txt").write_text(str(final_raw["final"] or ""), encoding="utf-8")
        write_json(
            out_dir / "final.raw.meta.json",
            {
                "schema_version": "router_observability.final_raw_metadata.v0",
                "session_id": final_metadata["session_id"],
                "turn_id": final_metadata["turn_id"],
                "created_at": utc_now(),
                "final_sha256": final_metadata["final_sha256"],
                "final_length": final_metadata["final_length"],
                "redaction": final_raw["redaction"],
            },
        )
    events, coverage = ordered_events_for_stop(out_dir)
    write_json(out_dir / "coverage.json", coverage)
    dispatch_decision = read_json(out_dir / "dispatch-decision.json")
    score = score_turn({**decision, "final_sha256": final_metadata["final_sha256"]}, final_message, events, dispatch_decision)
    write_json(out_dir / "router-score.json", score)
    (out_dir / "router-card.md").write_text(
        render_router_card(score, decision, dispatch_decision),
        encoding="utf-8",
    )
    return None


def run_handler(handler, event_name=None):
    try:
        event = load_stdin_event()
        output = handler(event) if event_name is None else handler(event, event_name)
    except Exception as exc:  # Hooks must not break normal Codex use.
        output = None
        if os.environ.get("GROUNDWORK_ROUTER_OBSERVABILITY_DEBUG"):
            print(f"Groundwork router observability hook failed: {exc}", file=sys.stderr)
    if output is not None:
        print(json.dumps(output, ensure_ascii=False, sort_keys=True))
    return 0
