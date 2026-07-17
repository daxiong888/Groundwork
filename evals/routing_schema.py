"""Shared routing and router-observability schema vocabulary."""

import html
import json
import re
import unicodedata
from decimal import Decimal, InvalidOperation
from html.parser import HTMLParser
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
LEGACY_FIXTURE_ONLY_INTERNAL_ROUTE_ALLOWLIST = frozenset(
    {("goal-contract.csv", "goal-contract")}
)

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
    "contract-lineage.csv",
    "routing-reliability.csv",
    "routing-blind.csv",
    "trace-first-verify-review.csv",
    "uat-evidence-window.csv",
    "prototype-annotation.csv",
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
    "annotation_presentation_decision",
    "annotation_handoff_reference",
    "annotation_carrythrough_verification",
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
ANNOTATION_PRESENTATION_EXPECTATION_FIELDS = (
    "annotation_expected_purposes",
    "annotation_expected_decisions",
    "annotation_expected_audience_sources",
    "annotation_expected_companions",
)
ANNOTATION_CARRYTHROUGH_EXPECTATION_FIELDS = (
    "annotation_expected_scope_claim",
    "annotation_expected_scope_covered",
    "annotation_expected_scope_missing",
    "annotation_expected_scope_verdict",
    "annotation_expected_carrythrough_verdicts",
    "annotation_expected_observed_targets",
)
ANNOTATION_REFERENCE_EXPECTATION_FIELD = "annotation_expected_reference"
ANNOTATION_CARRYTHROUGH_VERDICTS = {"covered", "gap", "unverified"}
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
UAT_EVIDENCE_WINDOW_RECORD_FIELDS = (
    "Claim / Delivery Scope",
    "Relevant SUT Fingerprint",
    "Preconditions",
    "Window Stability",
    "Coverage Basis",
    "Result / Missing",
    "Rerun Of / Supersedes",
)
UAT_MUTUALLY_EXCLUSIVE_STRICT_SECTION_KEYS = frozenset(
    {
        "contract-lineage",
        "annotation-presentation-decision",
        "annotation-decision-carry-through",
        "annotation-carry-through-check",
        "uat-evidence-window-continuation",
    }
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
RELEASE_EVIDENCE_CLAIM_TYPES = {
    "runtime",
    "cache",
    "release",
    "uat",
    "marketplace",
    "cache_refresh",
    "not_applicable",
}
RELEASE_EVIDENCE_STATUSES = {"verified", "unverified", "not_applicable"}
RELEASE_REFRESH_METHODS = {
    "refresh_step",
    "source_equivalence",
    "not_run",
    "not_applicable",
}
RELEASE_RUN_SCOPES = {"targeted", "full", "not_run", "not_applicable"}
RELEASE_PLUGIN_BOUND_CLAIM_TYPES = {
    "runtime",
    "cache",
    "marketplace",
    "cache_refresh",
}
UAT_PRECONDITION_TOKENS = {
    "satisfied",
    "unsatisfied",
    "unverified",
    "not_applicable",
}
UAT_WINDOW_STABILITY_TOKENS = {
    "stable",
    "changed",
    "unverified",
    "stability_unverified",
    "restart_required",
}
UAT_WINDOW_STABILITY_PRODUCTIONS = {
    ("stable",),
    ("changed", "restart_required"),
    ("unverified",),
}
UAT_SCOPE_VERDICTS = {"pass", "partial", "fail", "blocked"}
UAT_RESULT_TOKENS = {"pass", "partial", "fail", "blocked", "observed_only"}
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
ANNOTATION_OUTPUT_CONTRACT_TOKENS = frozenset(
    {
        "annotation_presentation_decision",
        "annotation_handoff_reference",
        "annotation_carrythrough_verification",
    }
)
OUTPUT_CONTRACT_ORACLE_BINDINGS = (
    (
        "contract_lineage core",
        CONTRACT_LINEAGE_EXPECTATION_FIELDS,
        frozenset({"contract_lineage"}),
        frozenset(),
    ),
    (
        "contract_lineage scope",
        CONTRACT_LINEAGE_SCOPE_EXPECTATION_FIELDS,
        frozenset({"contract_lineage", "verify_scope"}),
        frozenset(),
    ),
    (
        "annotation base",
        ANNOTATION_PRESENTATION_EXPECTATION_FIELDS,
        frozenset(),
        ANNOTATION_OUTPUT_CONTRACT_TOKENS,
    ),
    (
        "annotation carrythrough",
        ANNOTATION_CARRYTHROUGH_EXPECTATION_FIELDS,
        frozenset({"annotation_carrythrough_verification"}),
        frozenset(),
    ),
    (
        "annotation reference",
        (ANNOTATION_REFERENCE_EXPECTATION_FIELD,),
        frozenset({"annotation_handoff_reference"}),
        frozenset(),
    ),
    (
        "UAT evidence window",
        UAT_EVIDENCE_WINDOW_EXPECTATION_FIELDS,
        frozenset({"uat_evidence_window"}),
        frozenset(),
    ),
    (
        "release evidence claim",
        RELEASE_EVIDENCE_CLAIM_EXPECTATION_FIELDS,
        frozenset({"release_evidence_claim"}),
        frozenset(),
    ),
    (
        "UAT verification scope",
        UAT_EVIDENCE_WINDOW_SCOPE_EXPECTATION_FIELDS,
        frozenset({"verify_scope"}),
        frozenset(
            {
                "uat_evidence_window",
                "uat_evidence_window_forbidden",
            }
        ),
    ),
    (
        "UAT handoff",
        UAT_HANDOFF_REFERENCE_EXPECTATION_FIELDS,
        frozenset({"uat_handoff_reference"}),
        frozenset(),
    ),
)
CONTRACT_LINEAGE_CANONICAL_FIXTURES = frozenset(
    {
        "evals/fixtures/contract-lineage-producer",
        "evals/fixtures/contract-lineage-renderer",
        "evals/fixtures/contract-lineage-branched",
    }
)
CONTRACT_LINEAGE_CANONICAL_FACT_FIELDS = (
    ("Canonical Owner / Source", "lineage_expected_canonical_owner"),
    ("Hops", "lineage_expected_hops"),
    ("First Confirmed Divergence", "lineage_expected_divergence"),
    ("Fix Owner / Boundary", "lineage_expected_fix_owner"),
    ("Unverified / Branched Hops", "lineage_expected_unverified_hops"),
)
PROTOTYPE_ANNOTATION_DOWNSTREAM_ROW_IDS = frozenset(
    {
        "prototype-annotation-003",
        "prototype-annotation-004",
        "prototype-annotation-005",
    }
)
STRICT_OUTPUT_CONTRACT_FAMILY_TOKENS = frozenset(
    {
        "contract_lineage",
        "annotation_presentation_decision",
        "annotation_handoff_reference",
        "annotation_carrythrough_verification",
        "uat_evidence_window",
        "uat_evidence_window_forbidden",
        "uat_handoff_reference",
    }
)
STRICT_OUTPUT_CONTRACT_COMPATIBILITY = {
    token: frozenset() for token in STRICT_OUTPUT_CONTRACT_FAMILY_TOKENS
}
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

RESERVED_CSV_HEADERS = frozenset(
    set(ROUTING_SCHEMA_FIELDS)
    | set(CONTRACT_LINEAGE_EXPECTATION_FIELDS)
    | set(CONTRACT_LINEAGE_SCOPE_EXPECTATION_FIELDS)
    | set(ANNOTATION_PRESENTATION_EXPECTATION_FIELDS)
    | set(ANNOTATION_CARRYTHROUGH_EXPECTATION_FIELDS)
    | {ANNOTATION_REFERENCE_EXPECTATION_FIELD}
    | set(UAT_EVIDENCE_WINDOW_EXPECTATION_FIELDS)
    | set(UAT_EVIDENCE_WINDOW_SCOPE_EXPECTATION_FIELDS)
    | set(RELEASE_EVIDENCE_CLAIM_EXPECTATION_FIELDS)
    | set(UAT_HANDOFF_REFERENCE_EXPECTATION_FIELDS)
    | {
        "id",
        "expected_skill",
        "fixture",
        "input_scenario",
        "prompt",
        "expected_behavior",
        "acceptance_standard",
        "forbidden_behavior",
        "artifact_allowed",
        "risky_write_requested",
        "host_preemption_allowed",
        "host_preemption_classification_allowed",
        "skill_load_required",
        "gate_required",
        "forbidden_output_markers",
        "verify_scope_required",
    }
)


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


def _canonical_row_id(row):
    raw_value = str(row.get("id") or "")
    if not raw_value.strip():
        raise ValueError(f"{row_location(row)} missing required id")
    normalized = unicodedata.normalize("NFKC", raw_value)
    if (
        raw_value != raw_value.strip()
        or raw_value != normalized
        or any(
            unicodedata.category(character) in {"Cc", "Cs"}
            or _is_default_ignorable_code_point(character)
            for character in normalized
        )
        or re.fullmatch(
            r"[A-Za-z0-9][A-Za-z0-9_.:-]*",
            normalized,
        )
        is None
    ):
        raise ValueError(
            f"{row_location(row)} id must use one canonical ASCII stable identifier "
            "without NFKC changes or default-ignorable Unicode"
        )
    return normalized, normalized.casefold()


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
    duplicates = sorted(
        token for token in set(parts) if parts.count(token) > 1
    )
    if duplicates:
        raise ValueError(
            f"{row_location(row)} {field} contains duplicate token(s): "
            + ", ".join(duplicates)
        )
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
    if "none" in tokens and len(tokens) != 1:
        raise ValueError(
            f"{row_location(row)} {field} token none must be used alone"
        )
    allowed = implemented | future
    unknown = [token for token in tokens if token not in allowed]
    if unknown:
        raise ValueError(f"{row_location(row)} unknown {field}: {', '.join(unknown)}")
    future_tokens = [token for token in tokens if token in future]
    return tokens, future_tokens


def _oracle_token(row, field):
    return str(row.get(field) or "").strip()


def _oracle_pipe_tokens(row, field):
    raw_value = _oracle_token(row, field)
    if not raw_value or raw_value.lower() in {"none", "[]"}:
        return []
    return parse_pipe_list(raw_value, field, row)


def _oracle_field_is_active(row, field):
    return _oracle_token(row, field).lower() not in {"", "none", "[]"}


def require_output_contract_oracle_alignment(row, output_contract):
    output_tokens = set(output_contract)
    for label, fields, required_all, required_any in (
        OUTPUT_CONTRACT_ORACLE_BINDINGS
    ):
        active_fields = [
            field for field in fields if _oracle_field_is_active(row, field)
        ]
        if not active_fields:
            continue
        missing_all = sorted(required_all - output_tokens)
        missing_any = bool(required_any and output_tokens.isdisjoint(required_any))
        if not missing_all and not missing_any:
            continue
        expected = []
        if required_all:
            expected.extend(sorted(required_all))
        if required_any:
            expected.append(
                "one of " + ", ".join(sorted(required_any))
            )
        raise ValueError(
            f"{row_location(row)} {label} has stale oracle fields without "
            f"required output_contract token(s) {' + '.join(expected)}: "
            + ", ".join(active_fields)
        )


def require_output_contract_compatibility(row, output_contract):
    strict_tokens = sorted(
        set(output_contract) & STRICT_OUTPUT_CONTRACT_FAMILY_TOKENS
    )
    incompatible_pairs = []
    for index, left in enumerate(strict_tokens):
        for right in strict_tokens[index + 1:]:
            if (
                right not in STRICT_OUTPUT_CONTRACT_COMPATIBILITY[left]
                or left not in STRICT_OUTPUT_CONTRACT_COMPATIBILITY[right]
            ):
                incompatible_pairs.append(f"{left}+{right}")
    if incompatible_pairs:
        raise ValueError(
            f"{row_location(row)} output_contract combines incompatible strict "
            "families: "
            + ", ".join(incompatible_pairs)
        )


def _require_oracle_enum(row, field, allowed):
    value = _oracle_token(row, field)
    if value not in allowed:
        raise ValueError(
            f"{row_location(row)} {field} must be one of: {', '.join(sorted(allowed))}"
        )
    return value


def _require_concrete_oracle_value(row, field):
    value = _oracle_token(row, field)
    if value.lower() in {"", "unverified", "not_run", "not_applicable"}:
        raise ValueError(f"{row_location(row)} {field} must name a concrete value")
    return value


def _require_canonical_absolute_oracle_path(row, field):
    value = _require_concrete_oracle_value(row, field)
    path = Path(value)
    if (
        not path.is_absolute()
        or ".." in path.parts
        or "." in path.parts
        or str(path) != value
    ):
        raise ValueError(
            f"{row_location(row)} {field} must be a canonical absolute path"
        )
    return value


def _paths_have_ancestor_relationship(left, right):
    for child, parent in ((left, right), (right, left)):
        try:
            child.relative_to(parent)
        except ValueError:
            continue
        return True
    return False


def _require_attributed_uat_fingerprint(row, field):
    value = _oracle_token(row, field)
    if value.lower() in {
        "",
        "none",
        "unknown",
        "unverified",
        "not_run",
        "not_applicable",
    }:
        raise ValueError(
            f"{row_location(row)} {field} must name an attributed fingerprint"
        )
    return value


def _require_material_uat_value(row, field, *, pipe_list=False):
    sentinel_values = {
        "",
        "none",
        "unknown",
        "unverified",
        "not_run",
        "not_applicable",
    }
    if pipe_list:
        raw_value = _oracle_token(row, field)
        values = [
            value.strip()
            for value in raw_value.split("|")
            if value.strip()
        ]
        if not values or any(
            value.strip().lower() in sentinel_values
            for value in values
        ):
            raise ValueError(
                f"{row_location(row)} {field} must name concrete UAT evidence"
            )
        return values
    value = _oracle_token(row, field)
    if value.lower() in sentinel_values:
        raise ValueError(
            f"{row_location(row)} {field} must name concrete UAT evidence"
        )
    return value


def _blank_non_newline_characters(value):
    return "".join(
        character if character in "\r\n" else " "
        for character in str(value or "")
    )


def _normalized_html_attribute_name(value):
    return unicodedata.normalize(
        "NFKC",
        str(value or ""),
    ).casefold()


def _inline_style_hides_content(value):
    style = re.sub(
        r"\s+",
        "",
        re.sub(
            r"(?s)/\*.*?\*/",
            "",
            str(value or "").casefold(),
        ),
    )
    for declaration in style.split(";"):
        property_name, separator, property_value = declaration.partition(":")
        if not separator:
            continue
        property_value = re.sub(
            r"!important$",
            "",
            property_value,
        )
        if (
            property_name == "display"
            and property_value == "none"
        ) or (
            property_name == "visibility"
            and property_value in {"hidden", "collapse"}
        ) or (
            property_name == "content-visibility"
            and property_value == "hidden"
        ):
            return True
        if property_name != "opacity" or re.fullmatch(
            r"[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:e[+-]?\d+)?",
            property_value,
        ) is None:
            continue
        try:
            if Decimal(property_value).is_zero():
                return True
        except InvalidOperation:
            continue
    return False


def _canonical_html_comment_error(value):
    raw_text = str(value or "")
    comment_matches = list(
        re.finditer(r"(?s)<!--(.*?)-->", raw_text)
    )
    if any(match.group(1).strip() for match in comment_matches):
        return "canonical Markdown contains a non-empty HTML comment"
    without_comments = re.sub(
        r"(?s)<!--.*?-->",
        "",
        raw_text,
    )
    if "<!--" in without_comments or "-->" in without_comments:
        return "canonical Markdown contains a malformed HTML comment"
    return ""


def _markdown_visible_structure(value):
    text = str(value or "")
    without_comments = re.sub(
        r"(?s)<!--.*?(?:-->|\Z)",
        lambda match: _blank_non_newline_characters(match.group(0)),
        text,
    )
    visible_lines = []
    fence_character = None
    fence_length = 0
    for line in without_comments.splitlines(keepends=True):
        line_without_ending = line.rstrip("\r\n")
        if fence_character is not None:
            closing = re.fullmatch(
                rf" {{0,3}}{re.escape(fence_character)}"
                rf"{{{fence_length},}}[ \t]*",
                line_without_ending,
            )
            visible_lines.append(_blank_non_newline_characters(line))
            if closing is not None:
                fence_character = None
                fence_length = 0
            continue
        opener = re.fullmatch(
            r" {0,3}(?P<fence>`{3,}|~{3,})[^\r\n]*",
            line_without_ending,
        )
        if opener is not None:
            marker = opener.group("fence")
            fence_character = marker[0]
            fence_length = len(marker)
            visible_lines.append(_blank_non_newline_characters(line))
            continue
        if re.match(r"(?: {4}|\t)", line_without_ending):
            visible_lines.append(_blank_non_newline_characters(line))
            continue
        visible_lines.append(line)
    return "".join(visible_lines)


CANONICAL_NON_RENDERED_HTML_ANCESTORS = frozenset(
    {
        "datalist",
        "defs",
        "noscript",
        "script",
        "style",
        "symbol",
        "template",
    }
)


class _CanonicalVisibilityHTMLParser(HTMLParser):
    _ALWAYS_NON_RENDERED_CONTAINERS = (
        CANONICAL_NON_RENDERED_HTML_ANCESTORS
    )
    _OPEN_ATTRIBUTE_CONTAINERS = {"details", "dialog"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.non_rendered_tags = set()
        self.hidden_attribute_tags = set()
        self.hidden_style_tags = set()
        self.duplicate_attribute_tags = set()

    def _inspect(self, tag, attrs):
        normalized_tag = str(tag or "").casefold()
        normalized_attrs = {}
        for raw_name, value in attrs:
            name = _normalized_html_attribute_name(raw_name)
            if name in normalized_attrs:
                self.duplicate_attribute_tags.add(
                    f"{normalized_tag}[{name}]"
                )
                continue
            normalized_attrs[name] = value
        if normalized_tag in self._ALWAYS_NON_RENDERED_CONTAINERS:
            self.non_rendered_tags.add(normalized_tag)
        if (
            normalized_tag in self._OPEN_ATTRIBUTE_CONTAINERS
            and "open" not in normalized_attrs
        ):
            self.non_rendered_tags.add(normalized_tag)
        for attribute in ("hidden", "inert", "popover"):
            if attribute in normalized_attrs:
                self.hidden_attribute_tags.add(
                    f"{normalized_tag}[{attribute}]"
                )
        if (
            str(normalized_attrs.get("aria-hidden") or "")
            .strip()
            .casefold()
            == "true"
        ):
            self.hidden_attribute_tags.add(
                f"{normalized_tag}[aria-hidden=true]"
            )
        if _inline_style_hides_content(normalized_attrs.get("style")):
            self.hidden_style_tags.add(normalized_tag)
        if (
            normalized_tag == "input"
            and str(normalized_attrs.get("type") or "").casefold() == "hidden"
        ):
            self.non_rendered_tags.add("input[type=hidden]")

    def handle_starttag(self, tag, attrs):
        self._inspect(tag, attrs)

    def handle_startendtag(self, tag, attrs):
        self._inspect(tag, attrs)


def _validate_canonical_html_visibility(value):
    comment_error = _canonical_html_comment_error(value)
    if comment_error:
        raise ValueError(comment_error)
    parser = _CanonicalVisibilityHTMLParser()
    parser.feed(str(value or ""))
    parser.close()
    if parser.duplicate_attribute_tags:
        raise ValueError(
            "canonical Markdown contains duplicate normalized HTML "
            "attribute(s) on: "
            + ", ".join(sorted(parser.duplicate_attribute_tags))
        )
    if parser.non_rendered_tags:
        raise ValueError(
            "canonical Markdown contains non-rendered HTML container(s): "
            + ", ".join(sorted(parser.non_rendered_tags))
        )
    if parser.hidden_attribute_tags:
        raise ValueError(
            "canonical Markdown contains hidden HTML attribute(s) on: "
            + ", ".join(sorted(parser.hidden_attribute_tags))
        )
    if parser.hidden_style_tags:
        raise ValueError(
            "canonical Markdown contains CSS-hidden HTML element(s): "
            + ", ".join(sorted(parser.hidden_style_tags))
        )


def _canonical_visible_markdown_structure(
    value,
    *,
    allow_release_claim_fences=False,
):
    raw_text = str(value or "")
    comment_matches = list(
        re.finditer(r"(?s)<!--(.*?)-->", raw_text)
    )
    if any(match.group(1).strip() for match in comment_matches):
        raise ValueError(
            "canonical Markdown contains a non-empty HTML comment"
        )
    without_comments = re.sub(
        r"(?s)<!--.*?-->",
        lambda match: _blank_non_newline_characters(match.group(0)),
        raw_text,
    )
    if "<!--" in without_comments or "-->" in without_comments:
        raise ValueError(
            "canonical Markdown contains a malformed HTML comment"
        )
    _validate_canonical_html_visibility(without_comments)

    visible_lines = []
    release_fence_lines = []
    in_release_fence = False
    current_uat_section = ""
    release_fence_sections = set()
    seen_uat_sections = set()
    for line in without_comments.splitlines(keepends=True):
        line_without_ending = line.rstrip("\r\n")
        if in_release_fence:
            if line_without_ending == "```":
                release_block = (
                    "```yaml\n"
                    + "".join(release_fence_lines).rstrip("\r\n")
                    + "\n```"
                )
                if _canonical_record_release_values(
                    release_block
                ) is None:
                    raise ValueError(
                        "canonical Markdown contains a malformed "
                        "release_evidence_claim fence"
                    )
                in_release_fence = False
                release_fence_lines = []
            else:
                release_fence_lines.append(line)
            visible_lines.append(
                _blank_non_newline_characters(line)
            )
            continue

        opener = re.fullmatch(
            r" {0,3}(?P<fence>`{3,}|~{3,})(?P<info>[^\r\n]*)",
            line_without_ending,
        )
        if opener is not None:
            if (
                allow_release_claim_fences
                and opener.group("fence") == "```"
                and opener.group("info").strip().casefold() == "yaml"
            ):
                if not current_uat_section:
                    raise ValueError(
                        "canonical UAT release_evidence_claim fence must "
                        "belong to one uat-window section"
                    )
                if current_uat_section in release_fence_sections:
                    raise ValueError(
                        "canonical UAT section contains multiple "
                        "release_evidence_claim fences"
                    )
                release_fence_sections.add(current_uat_section)
                in_release_fence = True
                visible_lines.append(
                    _blank_non_newline_characters(line)
                )
                continue
            raise ValueError(
                "canonical Markdown contains a fenced hidden payload"
            )
        if line_without_ending.strip() and re.match(
            r"(?: {4}|\t)", line_without_ending
        ):
            raise ValueError(
                "canonical Markdown contains an indented hidden payload"
            )
        uat_heading = re.fullmatch(
            r"##[ \t]+(uat-window-[A-Za-z0-9_.:-]+)[ \t]*",
            line_without_ending,
        )
        if uat_heading is not None:
            current_uat_section = uat_heading.group(1)
            if current_uat_section in seen_uat_sections:
                raise ValueError(
                    "canonical UAT record section must appear exactly once"
                )
            seen_uat_sections.add(current_uat_section)
        elif re.match(
            r"#{1,2}[ \t]+\S",
            line_without_ending,
        ):
            current_uat_section = ""
        visible_lines.append(line)
    if in_release_fence:
        raise ValueError(
            "canonical Markdown contains an unclosed "
            "release_evidence_claim fence"
        )

    visible_structure = "".join(visible_lines)
    _validate_canonical_html_visibility(visible_structure)
    return visible_structure


def _canonical_record_visible_parts(row, section):
    raw_section = str(section or "")
    comment_matches = list(re.finditer(r"(?s)<!--(.*?)-->", raw_section))
    if any(match.group(1).strip() for match in comment_matches):
        raise ValueError(
            f"{row_location(row)} canonical UAT record contains a non-empty HTML comment"
        )
    without_comments = re.sub(
        r"(?s)<!--.*?-->",
        lambda match: _blank_non_newline_characters(match.group(0)),
        raw_section,
    )
    if "<!--" in without_comments or "-->" in without_comments:
        raise ValueError(
            f"{row_location(row)} canonical UAT record contains a malformed HTML comment"
        )

    visible_lines = []
    release_blocks = []
    active_fence = None
    active_fence_length = 0
    active_fence_info = ""
    active_fence_lines = []
    for line in without_comments.splitlines(keepends=True):
        line_without_ending = line.rstrip("\r\n")
        if active_fence is not None:
            closing = re.fullmatch(
                rf" {{0,3}}{re.escape(active_fence)}"
                rf"{{{active_fence_length},}}[ \t]*",
                line_without_ending,
            )
            visible_lines.append(_blank_non_newline_characters(line))
            if closing is not None:
                block = "".join(active_fence_lines)
                if (
                    active_fence_info != "yaml"
                    or not re.match(
                        r"release_evidence_claim:[ \t]*(?:\r?\n|\Z)",
                        block,
                    )
                ):
                    raise ValueError(
                        f"{row_location(row)} canonical UAT record contains a fenced hidden payload"
                    )
                release_blocks.append(
                    f"```yaml\n{block.rstrip()}\n```"
                )
                active_fence = None
                active_fence_length = 0
                active_fence_info = ""
                active_fence_lines = []
            else:
                active_fence_lines.append(line)
            continue

        opener = re.fullmatch(
            r" {0,3}(?P<fence>`{3,}|~{3,})(?P<info>[^\r\n]*)",
            line_without_ending,
        )
        if opener is not None:
            marker = opener.group("fence")
            active_fence = marker[0]
            active_fence_length = len(marker)
            active_fence_info = opener.group("info").strip().lower()
            visible_lines.append(_blank_non_newline_characters(line))
            continue
        if line_without_ending.strip() and re.match(
            r"(?: {4}|\t)", line_without_ending
        ):
            raise ValueError(
                f"{row_location(row)} canonical UAT record contains an indented hidden payload"
            )
        visible_lines.append(line)

    if active_fence is not None:
        raise ValueError(
            f"{row_location(row)} canonical UAT record contains an unclosed fenced payload"
        )
    if len(release_blocks) > 1:
        raise ValueError(
            f"{row_location(row)} canonical UAT record contains multiple fenced payloads"
        )
    release_block = release_blocks[0] if release_blocks else ""
    return "".join(visible_lines), release_block


def _canonical_uat_records_text():
    records_path = (
        Path(__file__).resolve().parent
        / "fixtures"
        / "uat-evidence-window"
        / "records.md"
    )
    if not records_path.is_file():
        return None
    return records_path.read_text(encoding="utf-8")


def canonical_uat_record_section_text(records_text, row_id):
    normalized_row_id = str(row_id or "").strip()
    if not re.fullmatch(
        r"uat-window-[A-Za-z0-9_.:-]+", normalized_row_id
    ):
        raise ValueError("canonical UAT record row ID is invalid")
    visible_structure = _canonical_visible_markdown_structure(
        records_text,
        allow_release_claim_fences=True,
    )
    if re.search(r"(?is)<[A-Za-z][^>]*>", visible_structure):
        raise ValueError(
            "canonical UAT records must not contain raw HTML"
        )
    matches = list(
        re.finditer(
            rf"(?ms)^##[ \t]+{re.escape(normalized_row_id)}[ \t]*\r?\n"
            r".*?(?=^#{1,2}[ \t]+\S|\Z)",
            visible_structure,
        )
    )
    if not matches:
        raise ValueError("canonical UAT record section is missing")
    if len(matches) != 1:
        raise ValueError(
            "canonical UAT record section must appear exactly once"
        )
    match = matches[0]
    return str(records_text or "")[match.start():match.end()]


def _canonical_uat_record_section(row):
    if (
        str(row.get("fixture") or "").rstrip("/")
        != "evals/fixtures/uat-evidence-window"
    ):
        return "", ""
    row_id = _oracle_token(row, "id")
    if not re.fullmatch(r"uat-window-[A-Za-z0-9_.:-]+", row_id):
        return "", ""
    records_text = _canonical_uat_records_text()
    if records_text is None:
        raise ValueError(
            f"{row_location(row)} canonical UAT records.md is missing"
        )
    try:
        raw_section = canonical_uat_record_section_text(
            records_text, row_id
        )
    except ValueError as exc:
        raise ValueError(f"{row_location(row)} {exc}") from exc
    return _canonical_record_visible_parts(row, raw_section)


def _canonical_record_bullet_value(section, field):
    values = [
        match.group(1).strip()
        for match in re.finditer(
            rf"(?m)^[ \t]*-[ \t]+{re.escape(field)}"
            r":[ \t]*([^\r\n]*)[ \t]*$",
            section,
        )
    ]
    return values[0] if len(values) == 1 else None


def _canonical_uat_visible_text(value):
    value = html.unescape(str(value or ""))
    value = unicodedata.normalize("NFKC", value)
    value = "".join(
        character
        for character in value
        if not _is_default_ignorable_code_point(character)
    )
    return re.sub(r"[\u2010-\u2015\u2212]+", "-", value)


def _canonical_uat_visible_line_key(line):
    return _markdown_heading_anchor(
        _canonical_uat_visible_text(line)
    )


def _canonical_uat_visible_field_key(line):
    value = _canonical_uat_visible_text(line).strip()
    while True:
        previous = value
        value = re.sub(r"^(?:>[ \t]*)+", "", value).lstrip()
        value = re.sub(
            r"^(?:[-*+]|\d+[.)])[ \t]+",
            "",
            value,
        ).lstrip()
        value = re.sub(r"^#{1,6}[ \t]*", "", value).lstrip()
        if value == previous:
            break
    value = re.sub(
        r"\[([^\]]+)\]\([^)]+\)",
        r"\1",
        value,
    )
    value = re.sub(
        r"\[([^\]]+)\]\[[^\]]*\]",
        r"\1",
        value,
    )
    match = re.match(r"(?s)^(.*?)[ \t]*[:：]", value)
    if match is None:
        return ""
    return _markdown_heading_anchor(match.group(1))


def _canonical_uat_confusable_key(key):
    return str(key or "").translate(
        _CSV_HEADER_CONFUSABLE_TRANSLATION
    )


def _canonical_uat_forbidden_section_errors(section):
    errors = []
    lines = str(section or "").splitlines()
    line_keys = [_canonical_uat_visible_line_key(line) for line in lines]
    field_keys = [
        _canonical_uat_visible_field_key(line) for line in lines
    ]
    record_field_keys = {
        _markdown_heading_anchor(field)
        for field in UAT_EVIDENCE_WINDOW_RECORD_FIELDS
    }
    reserved_keys = (
        {"uat-evidence-window"}
        | set(UAT_MUTUALLY_EXCLUSIVE_STRICT_SECTION_KEYS)
        | record_field_keys
    )
    confusable_aliases = sorted(
        {
            key
            for key in line_keys + field_keys
            if key
            and (
                skeleton := _canonical_uat_confusable_key(key)
            )
            != key
            and any(
                skeleton == reserved
                or skeleton.startswith(reserved + "-")
                for reserved in reserved_keys
            )
        }
    )
    if confusable_aliases:
        errors.append(
            "contains cross-script confusable machine-significant "
            "label(s): "
            + ", ".join(confusable_aliases)
        )
    window_heading_keys = sorted(
        {
            key
            for key in line_keys
            if key == "uat-evidence-window"
            or key.startswith("uat-evidence-window-")
        }
    )
    if window_heading_keys:
        errors.append(
            "contains forbidden UAT Evidence Window heading variant(s): "
            + ", ".join(window_heading_keys)
        )

    mutually_exclusive = sorted(
        {
            strict_key
            for key in line_keys
            for strict_key in UAT_MUTUALLY_EXCLUSIVE_STRICT_SECTION_KEYS
            if key == strict_key
            or key.startswith(strict_key + "-")
        }
    )
    if mutually_exclusive:
        errors.append(
            "contains mutually exclusive strict section(s): "
            + ", ".join(mutually_exclusive)
        )

    record_field_by_key = {
        _markdown_heading_anchor(field): field
        for field in UAT_EVIDENCE_WINDOW_RECORD_FIELDS
    }
    orphan_fields = sorted(
        {
            record_field
            for visible_key in line_keys + field_keys
            if visible_key
            for record_key, record_field in record_field_by_key.items()
            if visible_key == record_key
            or visible_key.startswith(record_key + "-")
        }
    )
    if orphan_fields:
        errors.append(
            "contains forbidden UAT Evidence Window field(s): "
            + ", ".join(orphan_fields)
        )
    return errors


def _canonical_record_release_values(release_block):
    match = re.fullmatch(
        r"(?ms)```yaml[ \t]*\r?\n"
        r"release_evidence_claim:[ \t]*\r?\n"
        r"[ ]{2}claim_type:[ \t]*(?P<claim_type>[^\r\n]+)\r?\n"
        r"[ ]{2}claim:[ \t]*(?P<claim>[^\r\n]+)\r?\n"
        r"[ ]{2}evidence_status:[ \t]*(?P<evidence_status>[^\r\n]+)\r?\n"
        r"[ ]{2}installed_plugin_root:[ \t]*(?P<installed_plugin_root>[^\r\n]+)\r?\n"
        r"[ ]{2}source_root:[ \t]*(?P<source_root>[^\r\n]+)\r?\n"
        r"[ ]{2}cache_or_source_refresh:[ \t]*\r?\n"
        r"[ ]{4}method:[ \t]*(?P<refresh_method>[^\r\n]+)\r?\n"
        r"[ ]{4}evidence:[ \t]*(?P<refresh_evidence>[^\r\n]+)\r?\n"
        r"[ ]{2}run_scope:[ \t]*(?P<run_scope>[^\r\n]+)\r?\n"
        r"[ ]{2}commands_or_trials:[ \t]*(?P<commands_or_trials>[^\r\n]+)\r?\n"
        r"[ ]{2}limitations:[ \t]*(?P<limitations>[^\r\n]+)\r?\n"
        r"```",
        str(release_block or "").strip(),
    )
    if match is None:
        return None

    def inline_list(value):
        if value is None:
            return None
        value = value.strip()
        if not (value.startswith("[") and value.endswith("]")):
            return None
        inner = value[1:-1].strip()
        return (
            []
            if not inner
            else [item.strip() for item in inner.split(",")]
        )

    return {
        "claim_type": match.group("claim_type").strip(),
        "claim": match.group("claim").strip(),
        "evidence_status": match.group("evidence_status").strip(),
        "installed_plugin_root": match.group("installed_plugin_root").strip(),
        "source_root": match.group("source_root").strip(),
        "refresh_method": match.group("refresh_method").strip(),
        "refresh_evidence": match.group("refresh_evidence").strip(),
        "run_scope": match.group("run_scope").strip(),
        "commands_or_trials": inline_list(
            match.group("commands_or_trials")
        ),
        "limitations": inline_list(match.group("limitations")),
    }


def require_canonical_uat_record_alignment(row, output_contract):
    if not {
        "uat_evidence_window",
        "uat_evidence_window_forbidden",
        "uat_handoff_reference",
    }.intersection(output_contract):
        return
    visible_section, release_block = _canonical_uat_record_section(row)
    if not visible_section:
        return

    if "uat_evidence_window_forbidden" in output_contract:
        forbidden_errors = _canonical_uat_forbidden_section_errors(
            visible_section
        )
        if forbidden_errors:
            raise ValueError(
                f"{row_location(row)} canonical UAT record violates "
                "uat_evidence_window_forbidden: "
                + "; ".join(forbidden_errors)
            )

    field_mappings = {}
    if "verify_scope" in output_contract:
        field_mappings.update(
            {
                "Claim": "uat_expected_scope_claim",
                "Covered": "uat_expected_scope_covered",
                "Missing": "uat_expected_scope_missing",
                "Verdict": "uat_expected_scope_verdict",
            }
        )
    if "uat_evidence_window" in output_contract:
        field_mappings.update(
            {
                "Claim / Delivery Scope": "uat_expected_claim_scope",
                "Relevant SUT Fingerprint": "uat_expected_fingerprint",
                "Preconditions": "uat_expected_preconditions",
                "Window Stability": "uat_expected_window_stability",
                "Coverage Basis": "uat_expected_coverage_basis",
                "Result / Missing": "uat_expected_result_missing",
                "Rerun Of / Supersedes": "uat_expected_rerun_supersedes",
            }
        )
    if "uat_handoff_reference" in output_contract:
        field_mappings.update(
            {
                "Canonical Reference": "uat_handoff_expected_canonical_reference",
                "Claim / Delivery Scope": "uat_handoff_expected_claim_scope",
                "Relevant SUT Fingerprint": "uat_handoff_expected_fingerprint",
                "Window Stability": "uat_handoff_expected_window_stability",
                "Missing / Closeout Gap": "uat_handoff_expected_gap",
                "Rerun Of / Supersedes": "uat_handoff_expected_rerun_supersedes",
                "Next Owner Action": "uat_handoff_expected_next_owner_action",
                "Execution Boundary": "uat_handoff_expected_execution_boundary",
            }
        )
    mismatches = []
    for record_field, row_field in field_mappings.items():
        record_value = _canonical_record_bullet_value(
            visible_section, record_field
        )
        expected_value = _oracle_token(row, row_field)
        if record_value != expected_value:
            mismatches.append(
                f"{record_field}={record_value!r} != {row_field}={expected_value!r}"
            )

    release_values = _canonical_record_release_values(release_block)
    if release_values is None:
        mismatches.append("release_evidence_claim is missing or malformed")
    else:
        release_mapping = {
            "claim_type": "release_expected_claim_type",
            "claim": "release_expected_claim",
            "evidence_status": "release_expected_evidence_status",
            "installed_plugin_root": "release_expected_installed_plugin_root",
            "source_root": "release_expected_source_root",
            "refresh_method": "release_expected_refresh_method",
            "refresh_evidence": "release_expected_refresh_evidence",
            "run_scope": "release_expected_run_scope",
        }
        for record_field, row_field in release_mapping.items():
            expected_value = _oracle_token(row, row_field)
            if release_values.get(record_field) != expected_value:
                mismatches.append(
                    f"{record_field}={release_values.get(record_field)!r} "
                    f"!= {row_field}={expected_value!r}"
                )
        for record_field, row_field in (
            (
                "commands_or_trials",
                "release_expected_commands_or_trials",
            ),
            ("limitations", "release_expected_limitations"),
        ):
            expected_values = _oracle_pipe_tokens(row, row_field)
            if release_values.get(record_field) != expected_values:
                mismatches.append(
                    f"{record_field}={release_values.get(record_field)!r} "
                    f"!= {row_field}={expected_values!r}"
                )
    if mismatches:
        raise ValueError(
            f"{row_location(row)} canonical UAT record does not match row oracle: "
            + "; ".join(mismatches)
        )


def _parse_uat_window_stability(
    row, field="uat_expected_window_stability"
):
    tokens = _oracle_pipe_tokens(row, field)
    production = tuple(tokens)
    observed_production = (
        len(tokens) == 2
        and re.fullmatch(r"observed_at:[A-Za-z0-9_.:-]+", tokens[0]) is not None
        and tokens[1] == "stability_unverified"
    )
    if production not in UAT_WINDOW_STABILITY_PRODUCTIONS and not observed_production:
        raise ValueError(
            f"{row_location(row)} {field} must use exactly one production: "
            "stable, changed|restart_required, unverified, or "
            "observed_at:<id>|stability_unverified"
        )
    return tokens


def _parse_annotation_expectation_map(row, field):
    raw_value = _oracle_token(row, field)
    if raw_value.lower() == "none":
        return {}
    parsed = {}
    items = [item.strip() for item in raw_value.split("|")]
    if any(not item for item in items):
        raise ValueError(
            f"{row_location(row)} {field} contains an empty list item"
        )
    for item in items:
        if item.count("=") != 1:
            raise ValueError(
                f"{row_location(row)} {field} items must use annotation_id=value"
            )
        annotation_id, value = item.split("=", 1)
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.:-]*", annotation_id):
            raise ValueError(
                f"{row_location(row)} {field} has invalid annotation ID: {annotation_id}"
            )
        if not value or annotation_id in parsed:
            raise ValueError(
                f"{row_location(row)} {field} has an empty or duplicate annotation ID"
            )
        parsed[annotation_id] = value
    return parsed


def _canonical_relative_path(value):
    raw_value = str(value or "")
    path = Path(raw_value)
    return (
        raw_value
        and "\\" not in raw_value
        and not path.is_absolute()
        and ".." not in path.parts
        and "." not in path.parts
        and str(path) == raw_value
    )


def _markdown_heading_anchor(value):
    text = html.unescape(str(value or ""))
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"[`*_~]", "", text)
    text = unicodedata.normalize("NFKC", text).strip().lower()
    text = re.sub(r"[^\w\- ]", "", text, flags=re.UNICODE)
    text = re.sub(r"[ \t]+", "-", text)
    return re.sub(r"-{2,}", "-", text).strip("-")


def _annotation_anchor_region(path, anchor):
    text = path.read_text(encoding="utf-8")
    explicit_anchors = list(
        re.finditer(
            r"""(?is)<[A-Za-z][^>]*\bid\s*=\s*(['"])(?P<id>[^'"]+)\1[^>]*>""",
            text,
        )
    )
    explicit_matches = [
        (index, match)
        for index, match in enumerate(explicit_anchors)
        if html.unescape(match.group("id")) == anchor
    ]
    if len(explicit_matches) == 1:
        index, match = explicit_matches[0]
        if index + 1 < len(explicit_anchors):
            next_anchor_start = explicit_anchors[index + 1].start()
            end = text.rfind("\n", 0, next_anchor_start) + 1
        else:
            end = len(text)
        return text[match.start():end]
    if len(explicit_matches) > 1:
        return None

    if path.suffix.lower() not in {".md", ".markdown"}:
        return None
    headings = []
    for match in re.finditer(
        r"(?m)^(?P<marks>#{1,6})[ \t]+(?P<title>[^\r\n]+?)[ \t]*#*[ \t]*$",
        text,
    ):
        headings.append(
            (
                match,
                len(match.group("marks")),
                _markdown_heading_anchor(match.group("title")),
            )
        )
    heading_matches = [
        (index, match, level)
        for index, (match, level, generated_anchor) in enumerate(headings)
        if generated_anchor == anchor
    ]
    if len(heading_matches) != 1:
        return None
    index, match, level = heading_matches[0]
    end = len(text)
    for following_match, following_level, _anchor in headings[index + 1:]:
        if following_level <= level:
            end = following_match.start()
            break
    return text[match.start():end]


class _AnnotationReferenceHTMLParser(HTMLParser):
    _IGNORED_CONTEXTS = {"script", "style", "template"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.annotation_ids = []
        self.visible_text = []
        self._ignored_context_stack = []

    def _collect_annotation_ids(self, attrs):
        for name, value in attrs:
            if (
                name == "data-annotation-id"
                and value is not None
                and re.fullmatch(
                    r"[A-Za-z0-9][A-Za-z0-9_.:-]*",
                    value,
                )
            ):
                self.annotation_ids.append(value)

    def handle_starttag(self, tag, attrs):
        tag = tag.lower()
        if tag in self._IGNORED_CONTEXTS:
            self._ignored_context_stack.append(tag)
            return
        if not self._ignored_context_stack:
            self._collect_annotation_ids(attrs)

    def handle_startendtag(self, tag, attrs):
        tag = tag.lower()
        if (
            not self._ignored_context_stack
            and tag not in self._IGNORED_CONTEXTS
        ):
            self._collect_annotation_ids(attrs)

    def handle_endtag(self, tag):
        tag = tag.lower()
        if (
            self._ignored_context_stack
            and tag == self._ignored_context_stack[-1]
        ):
            self._ignored_context_stack.pop()

    def handle_data(self, data):
        if not self._ignored_context_stack:
            self.visible_text.append(data)


def _annotation_ids_in_reference_region(region):
    visible_region = _markdown_visible_structure(region)
    parser = _AnnotationReferenceHTMLParser()
    parser.feed(visible_region)
    parser.close()
    markdown_ids = re.findall(
        r"(?m)^[ \t]*-[ \t]+Annotation ID:[ \t]*"
        r"([A-Za-z0-9][A-Za-z0-9_.:-]*)[ \t]*$",
        "".join(parser.visible_text),
    )
    return markdown_ids + parser.annotation_ids


def _resolve_annotation_file_reference(row, field, value):
    raw_value = str(value or "").strip()
    if raw_value.count("#") != 1:
        raise ValueError(
            f"{row_location(row)} {field} must use relative-file#anchor"
        )
    relative_path, anchor = raw_value.rsplit("#", 1)
    if not _canonical_relative_path(relative_path):
        raise ValueError(
            f"{row_location(row)} {field} must use a canonical repo- or fixture-relative file"
        )
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.:-]*", anchor):
        raise ValueError(
            f"{row_location(row)} {field} must name a stable Markdown/HTML anchor"
        )

    repository_root = Path(__file__).resolve().parents[1]
    fixture_value = str(row.get("fixture") or "").strip().rstrip("/")
    candidate_paths = [repository_root / relative_path]
    if _canonical_relative_path(fixture_value):
        candidate_paths.append(repository_root / fixture_value / relative_path)
    resolved_candidates = []
    for candidate in candidate_paths:
        try:
            resolved = candidate.resolve()
            resolved.relative_to(repository_root.resolve())
        except (OSError, ValueError):
            continue
        if (
            resolved.is_file()
            and resolved.suffix.lower() in {".md", ".markdown", ".html", ".htm"}
            and resolved not in resolved_candidates
        ):
            resolved_candidates.append(resolved)
    if len(resolved_candidates) != 1:
        raise ValueError(
            f"{row_location(row)} {field} must resolve to exactly one existing Markdown/HTML file"
        )
    region = _annotation_anchor_region(resolved_candidates[0], anchor)
    if region is None:
        raise ValueError(
            f"{row_location(row)} {field} anchor is missing or ambiguous"
        )
    return region


def _require_annotation_reference_alignment(
    row,
    field,
    value,
    expected_maps,
):
    region = _resolve_annotation_file_reference(row, field, value)
    actual_annotation_ids = _annotation_ids_in_reference_region(region)
    expected_annotation_ids = expected_maps[1]
    if (
        len(actual_annotation_ids) != len(set(actual_annotation_ids))
        or set(actual_annotation_ids) != set(expected_annotation_ids)
    ):
        raise ValueError(
            f"{row_location(row)} {field} target Annotation IDs must match "
            f"{', '.join(sorted(expected_annotation_ids))}"
        )
    try:
        actual_maps = _canonical_annotation_decision_source_maps(region)
    except ValueError as exc:
        raise ValueError(
            f"{row_location(row)} {field} target decision map is invalid: {exc}"
        ) from exc
    if actual_maps != expected_maps:
        raise ValueError(
            f"{row_location(row)} {field} target decision fields must match "
            "the canonical annotation oracle"
        )


def _require_annotation_observed_target(
    row,
    annotation_id,
    target,
    evidence_required,
    expected_maps,
):
    field = f"annotation_expected_observed_targets[{annotation_id}]"
    lowered = str(target or "").strip().lower()
    for target_kind, evidence_token in (
        ("browser", "browser_or_unverified"),
        ("runtime", "runtime_or_unverified"),
    ):
        prefix = target_kind + ":"
        if lowered.startswith(prefix):
            if not lowered[len(prefix):].strip():
                raise ValueError(
                    f"{row_location(row)} {field} must name a concrete {target_kind} target"
                )
            if evidence_token not in evidence_required:
                raise ValueError(
                    f"{row_location(row)} {field} requires {evidence_token} evidence"
                )
            return

    region = _resolve_annotation_file_reference(row, field, target)
    actual_annotation_ids = _annotation_ids_in_reference_region(region)
    if actual_annotation_ids != [annotation_id]:
        raise ValueError(
            f"{row_location(row)} {field} target content must align with Annotation ID "
            f"{annotation_id}"
        )
    try:
        actual_maps = _canonical_annotation_decision_source_maps(region)
    except ValueError as exc:
        raise ValueError(
            f"{row_location(row)} {field} target decision map is invalid: {exc}"
        ) from exc
    expected_purposes, expected_decisions, expected_sources, expected_companions = (
        expected_maps
    )
    expected_target_maps = (
        {annotation_id: expected_purposes[annotation_id]},
        {annotation_id: expected_decisions[annotation_id]},
        (
            {annotation_id: expected_sources[annotation_id]}
            if annotation_id in expected_sources
            else {}
        ),
        (
            {annotation_id: expected_companions[annotation_id]}
            if annotation_id in expected_companions
            else {}
        ),
    )
    if actual_maps != expected_target_maps:
        raise ValueError(
            f"{row_location(row)} {field} target decision fields must match "
            f"the canonical oracle for {annotation_id}"
        )


def _annotation_scope_id_set(row, field):
    values = _oracle_pipe_tokens(row, field)
    duplicate_ids = sorted(
        annotation_id
        for annotation_id in set(values)
        if values.count(annotation_id) > 1
    )
    if duplicate_ids:
        raise ValueError(
            f"{row_location(row)} {field} has duplicate annotation IDs: "
            + ", ".join(duplicate_ids)
        )
    return set(values)


class _PrototypeAnnotationIndexHTMLParser(HTMLParser):
    _NON_RENDERED_ANCESTOR_TAGS = (
        CANONICAL_NON_RENDERED_HTML_ANCESTORS | {"head", "title"}
    )
    _NON_RENDERED_ELEMENT_TAGS = {
        "base",
        "link",
        "meta",
    }

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.purposes = {}
        self.product_content_ids = set()
        self.errors = []
        self._body_depth = 0
        self._non_rendered_ancestor_stack = []

    def _inspect(self, tag, attrs):
        normalized_attrs = {}
        for raw_name, value in attrs:
            name = str(raw_name or "").casefold()
            if name in normalized_attrs:
                self.errors.append(
                    f"duplicate HTML attribute: {name}"
                )
                continue
            normalized_attrs[name] = value

        annotation_id = normalized_attrs.get(
            "data-annotation-id"
        )
        purpose = normalized_attrs.get(
            "data-annotation-purpose"
        )
        if annotation_id is not None or purpose is not None:
            annotation_id = str(annotation_id or "").strip()
            purpose = str(purpose or "").strip()
            if (
                self._body_depth <= 0
                or self._non_rendered_ancestor_stack
                or tag in self._NON_RENDERED_ELEMENT_TAGS
            ):
                self.errors.append(
                    "prototype annotation IDs and purposes must be attached "
                    "to a renderable element inside body"
                )
            elif not re.fullmatch(
                r"[A-Za-z0-9][A-Za-z0-9_.:-]*",
                annotation_id,
            ):
                self.errors.append(
                    "prototype annotation index has an invalid "
                    "data-annotation-id"
                )
            elif not purpose:
                self.errors.append(
                    f"prototype annotation {annotation_id} is missing "
                    "data-annotation-purpose"
                )
            elif annotation_id in self.purposes:
                self.errors.append(
                    f"prototype annotation ID is duplicated: "
                    f"{annotation_id}"
                )
            else:
                self.purposes[annotation_id] = purpose

        product_content_id = normalized_attrs.get(
            "data-product-content-id"
        )
        if product_content_id is not None:
            product_content_id = str(
                product_content_id or ""
            ).strip()
            if product_content_id:
                self.product_content_ids.add(product_content_id)

    def handle_starttag(self, tag, attrs):
        tag = str(tag or "").casefold()
        if tag == "body":
            self._body_depth += 1
        if tag in self._NON_RENDERED_ANCESTOR_TAGS:
            self._non_rendered_ancestor_stack.append(tag)
        self._inspect(tag, attrs)

    def handle_startendtag(self, tag, attrs):
        tag = str(tag or "").casefold()
        self._inspect(tag, attrs)

    def handle_endtag(self, tag):
        tag = str(tag or "").casefold()
        if (
            self._non_rendered_ancestor_stack
            and tag == self._non_rendered_ancestor_stack[-1]
        ):
            self._non_rendered_ancestor_stack.pop()
        if tag == "body" and self._body_depth > 0:
            self._body_depth -= 1


def _canonical_annotation_index_text():
    index_path = (
        Path(__file__).resolve().parent
        / "fixtures"
        / "prototype-annotation"
        / "index.html"
    )
    if not index_path.is_file():
        return None
    return index_path.read_text(encoding="utf-8")


def _canonical_annotation_index_purposes(source_text):
    _validate_canonical_html_visibility(source_text)
    parser = _PrototypeAnnotationIndexHTMLParser()
    parser.feed(str(source_text or ""))
    parser.close()
    if parser.errors:
        raise ValueError("; ".join(parser.errors))
    if not parser.purposes:
        raise ValueError(
            "prototype annotation index contains no annotations"
        )
    overlap = set(parser.purposes) & parser.product_content_ids
    if overlap:
        raise ValueError(
            "prototype annotation IDs overlap product-owned content IDs: "
            + ", ".join(sorted(overlap))
        )
    return parser.purposes


def _require_canonical_annotation_index_alignment(row, purposes):
    if (
        str(row.get("fixture") or "").rstrip("/")
        != "evals/fixtures/prototype-annotation"
    ):
        return
    source_text = _canonical_annotation_index_text()
    if source_text is None:
        raise ValueError(
            f"{row_location(row)} canonical prototype index.html is missing"
        )
    try:
        canonical_purposes = (
            _canonical_annotation_index_purposes(source_text)
        )
    except ValueError as exc:
        raise ValueError(f"{row_location(row)} {exc}") from exc
    if canonical_purposes != purposes:
        raise ValueError(
            f"{row_location(row)} canonical prototype index purpose map "
            "does not match row oracle"
        )


def _canonical_annotation_decision_source_text():
    decision_source_path = (
        Path(__file__).resolve().parent
        / "fixtures"
        / "prototype-annotation"
        / "decision-source.md"
    )
    if not decision_source_path.is_file():
        return None
    return decision_source_path.read_text(encoding="utf-8")


def _canonical_annotation_decision_source_maps(source_text):
    visible_structure = _canonical_visible_markdown_structure(source_text)
    sections = [
        match.group(0)
        for match in re.finditer(
            r"(?ms)^#{2,6}[ \t]+Annotation Presentation Decision[ \t]*\r?\n"
            r".*?(?=^#{1,6}[ \t]+\S|\Z)",
            visible_structure,
        )
    ]
    if not sections:
        raise ValueError(
            "canonical annotation decision source has no decision sections"
        )

    required_fields = {
        "Annotation ID",
        "Annotation Purpose",
        "Presentation Disposition",
    }
    allowed_fields = required_fields | {
        "Audience-facing Source",
        "Companion Reference",
    }
    purposes = {}
    decisions = {}
    sources = {}
    companions = {}
    for section in sections:
        fields = {}
        for line in section.splitlines()[1:]:
            if not line.strip():
                continue
            match = re.fullmatch(
                r"[ \t]*-[ \t]+(?P<field>[^:\r\n]+)"
                r":[ \t]*(?P<value>[^\r\n]*?)[ \t]*",
                line,
            )
            if match is None:
                raise ValueError(
                    "canonical annotation decision section contains "
                    "non-machine-parsable content"
                )
            field = match.group("field").strip()
            value = match.group("value").strip()
            if (
                field not in allowed_fields
                or field in fields
                or not value
            ):
                raise ValueError(
                    "canonical annotation decision section has an unknown, "
                    "duplicate, or empty field"
                )
            fields[field] = value
        missing_fields = sorted(required_fields - set(fields))
        if missing_fields:
            raise ValueError(
                "canonical annotation decision section is missing: "
                + ", ".join(missing_fields)
            )
        annotation_id = fields["Annotation ID"]
        if (
            not re.fullmatch(
                r"[A-Za-z0-9][A-Za-z0-9_.:-]*", annotation_id
            )
            or annotation_id in decisions
        ):
            raise ValueError(
                "canonical annotation decision source has an invalid or "
                "duplicate Annotation ID"
            )
        disposition = fields["Presentation Disposition"]
        source = fields.get("Audience-facing Source")
        companion = fields.get("Companion Reference")
        if disposition == "retain_as_audience_content_candidate":
            valid_conditionals = bool(source) and companion is None
        elif disposition == "separate_review_companion":
            valid_conditionals = bool(companion) and source is None
        elif disposition == "remove_before_final":
            valid_conditionals = source is None and companion is None
        else:
            valid_conditionals = False
        if not valid_conditionals:
            raise ValueError(
                "canonical annotation decision source has inconsistent "
                f"conditional fields for {annotation_id}"
            )
        purposes[annotation_id] = fields["Annotation Purpose"]
        decisions[annotation_id] = disposition
        if source is not None:
            sources[annotation_id] = source
        if companion is not None:
            companions[annotation_id] = companion
    return purposes, decisions, sources, companions


def _require_canonical_annotation_decision_source_alignment(
    row,
    purposes,
    decisions,
    sources,
    companions,
):
    if (
        str(row.get("fixture") or "").rstrip("/")
        != "evals/fixtures/prototype-annotation"
        or _oracle_token(row, "id")
        not in PROTOTYPE_ANNOTATION_DOWNSTREAM_ROW_IDS
    ):
        return
    source_text = _canonical_annotation_decision_source_text()
    if source_text is None:
        raise ValueError(
            f"{row_location(row)} canonical annotation decision-source.md is missing"
        )
    try:
        canonical_maps = _canonical_annotation_decision_source_maps(
            source_text
        )
    except ValueError as exc:
        raise ValueError(f"{row_location(row)} {exc}") from exc
    expected_maps = (purposes, decisions, sources, companions)
    labels = (
        "purpose",
        "disposition",
        "audience source",
        "companion",
    )
    mismatches = [
        label
        for label, canonical_map, expected_map in zip(
            labels, canonical_maps, expected_maps
        )
        if canonical_map != expected_map
    ]
    if mismatches:
        raise ValueError(
            f"{row_location(row)} canonical annotation decision source does "
            "not match row oracle map(s): "
            + ", ".join(mismatches)
        )


def require_annotation_presentation_expectations(row, output_contract):
    if not {
        "annotation_presentation_decision",
        "annotation_handoff_reference",
        "annotation_carrythrough_verification",
    }.intersection(output_contract):
        return
    missing = [
        field
        for field in ANNOTATION_PRESENTATION_EXPECTATION_FIELDS
        if not _oracle_token(row, field)
    ]
    if missing:
        raise ValueError(
            f"{row_location(row)} annotation_presentation_decision missing required oracle fields: "
            + ", ".join(missing)
        )

    purposes = _parse_annotation_expectation_map(
        row, "annotation_expected_purposes"
    )
    decisions = _parse_annotation_expectation_map(
        row, "annotation_expected_decisions"
    )
    sources = _parse_annotation_expectation_map(
        row, "annotation_expected_audience_sources"
    )
    companions = _parse_annotation_expectation_map(
        row, "annotation_expected_companions"
    )
    if not decisions or not purposes:
        raise ValueError(
            f"{row_location(row)} annotation purposes and decisions must not be none"
        )
    if set(purposes) != set(decisions):
        raise ValueError(
            f"{row_location(row)} annotation purpose IDs must match decision IDs"
        )
    _require_canonical_annotation_index_alignment(row, purposes)
    allowed_dispositions = {
        "remove_before_final",
        "separate_review_companion",
        "retain_as_audience_content_candidate",
    }
    invalid = {
        annotation_id: disposition
        for annotation_id, disposition in decisions.items()
        if disposition not in allowed_dispositions
    }
    if invalid:
        raise ValueError(
            f"{row_location(row)} annotation_expected_decisions has invalid dispositions: {invalid}"
        )
    unknown_conditional_ids = (set(sources) | set(companions)) - set(decisions)
    if unknown_conditional_ids:
        raise ValueError(
            f"{row_location(row)} annotation conditional fields reference unknown IDs: "
            + ", ".join(sorted(unknown_conditional_ids))
        )
    for annotation_id, disposition in decisions.items():
        has_source = annotation_id in sources
        has_companion = annotation_id in companions
        if disposition == "retain_as_audience_content_candidate":
            valid = has_source and not has_companion
        elif disposition == "separate_review_companion":
            valid = has_companion and not has_source
        else:
            valid = not has_source and not has_companion
        if not valid:
            raise ValueError(
                f"{row_location(row)} annotation conditional fields do not match "
                f"{annotation_id}={disposition}"
            )

    _require_canonical_annotation_decision_source_alignment(
        row,
        purposes,
        decisions,
        sources,
        companions,
    )

    expected_reference = _oracle_token(
        row, ANNOTATION_REFERENCE_EXPECTATION_FIELD
    )
    if "annotation_handoff_reference" in output_contract:
        if expected_reference.lower() in {
            "",
            "none",
            "unknown",
            "unverified",
            "not_applicable",
        }:
            raise ValueError(
                f"{row_location(row)} annotation_handoff_reference requires "
                f"{ANNOTATION_REFERENCE_EXPECTATION_FIELD}"
            )
        _require_annotation_reference_alignment(
            row,
            ANNOTATION_REFERENCE_EXPECTATION_FIELD,
            expected_reference,
            (purposes, decisions, sources, companions),
        )
    elif expected_reference.lower() not in {"", "none"}:
        raise ValueError(
            f"{row_location(row)} {ANNOTATION_REFERENCE_EXPECTATION_FIELD} "
            "is only valid for annotation_handoff_reference"
        )

    if "annotation_carrythrough_verification" not in output_contract:
        return

    carrythrough_missing = [
        field
        for field in ANNOTATION_CARRYTHROUGH_EXPECTATION_FIELDS
        if not _oracle_token(row, field)
    ]
    if carrythrough_missing:
        raise ValueError(
            f"{row_location(row)} annotation_carrythrough_verification missing required oracle fields: "
            + ", ".join(carrythrough_missing)
        )

    carrythrough_verdicts = _parse_annotation_expectation_map(
        row, "annotation_expected_carrythrough_verdicts"
    )
    observed_targets = _parse_annotation_expectation_map(
        row, "annotation_expected_observed_targets"
    )
    scope_claim = _oracle_token(row, "annotation_expected_scope_claim")
    if scope_claim.lower() in {"none", "unknown", "unverified", "not_applicable"}:
        raise ValueError(
            f"{row_location(row)} annotation_expected_scope_claim must name the checked claim"
        )
    decision_ids = set(decisions)
    if set(carrythrough_verdicts) != decision_ids:
        raise ValueError(
            f"{row_location(row)} annotation carry-through verdict IDs must match decision IDs"
        )
    if set(observed_targets) != decision_ids:
        raise ValueError(
            f"{row_location(row)} annotation observed target IDs must match decision IDs"
        )
    invalid_verdicts = {
        annotation_id: verdict
        for annotation_id, verdict in carrythrough_verdicts.items()
        if verdict not in ANNOTATION_CARRYTHROUGH_VERDICTS
    }
    if invalid_verdicts:
        raise ValueError(
            f"{row_location(row)} annotation carry-through verdicts are invalid: "
            + repr(invalid_verdicts)
        )
    missing_covered_targets = sorted(
        annotation_id
        for annotation_id, verdict in carrythrough_verdicts.items()
        if verdict == "covered"
        and observed_targets[annotation_id].strip().lower()
        in {"none", "missing", "unknown", "unverified", "not_applicable"}
    )
    if missing_covered_targets:
        raise ValueError(
            f"{row_location(row)} covered annotation IDs require concrete observed targets: "
            + ", ".join(missing_covered_targets)
        )
    evidence_required = set(
        _oracle_pipe_tokens(row, "evidence_required")
    )
    for annotation_id, verdict in carrythrough_verdicts.items():
        if verdict == "covered":
            _require_annotation_observed_target(
                row,
                annotation_id,
                observed_targets[annotation_id],
                evidence_required,
                (purposes, decisions, sources, companions),
            )

    covered_ids = {
        annotation_id
        for annotation_id, verdict in carrythrough_verdicts.items()
        if verdict == "covered"
    }
    missing_ids = decision_ids - covered_ids
    scope_covered_ids = _annotation_scope_id_set(
        row, "annotation_expected_scope_covered"
    )
    scope_missing_ids = _annotation_scope_id_set(
        row, "annotation_expected_scope_missing"
    )
    if scope_covered_ids != covered_ids:
        raise ValueError(
            f"{row_location(row)} annotation scope covered IDs must match covered per-ID verdicts"
        )
    if scope_missing_ids != missing_ids:
        raise ValueError(
            f"{row_location(row)} annotation scope missing IDs must match gap/unverified per-ID verdicts"
        )

    if any(verdict == "gap" for verdict in carrythrough_verdicts.values()):
        expected_scope_verdict = "fail"
    elif any(
        verdict == "unverified" for verdict in carrythrough_verdicts.values()
    ):
        expected_scope_verdict = "partial"
    else:
        expected_scope_verdict = "pass"
    actual_scope_verdict = _oracle_token(
        row, "annotation_expected_scope_verdict"
    )
    if actual_scope_verdict != expected_scope_verdict:
        raise ValueError(
            f"{row_location(row)} annotation scope verdict must be "
            f"{expected_scope_verdict}, not {actual_scope_verdict}"
        )


def _parse_lineage_graph_value(
    row,
    raw_value,
    field="lineage_expected_hops",
):
    normalized = raw_value.replace("→", ">").replace("->", ">")
    if not normalized:
        raise ValueError(
            f"{row_location(row)} {field} must not be empty"
        )
    if re.search(r"[\r\n]", normalized):
        raise ValueError(
            f"{row_location(row)} {field} has invalid hop whitespace"
        )
    stages = []
    for stage in re.split(r"[ \t]*>[ \t]*", normalized):
        if not stage.strip():
            raise ValueError(
                f"{row_location(row)} {field} has an empty stage"
            )
        stage_hops = []
        for branch in re.split(r"[ \t]*\|[ \t]*", stage.strip()):
            if not branch.strip():
                raise ValueError(
                    f"{row_location(row)} {field} has an empty branch"
                )
            match = re.fullmatch(
                r"[ \t]*([A-Za-z0-9][A-Za-z0-9_.:/-]*)[ \t]*"
                r"\((verified|unverified|not_applicable)\)",
                branch.strip(),
                flags=re.IGNORECASE,
            )
            if match is None:
                raise ValueError(
                    f"{row_location(row)} {field} has invalid hop: {branch}"
                )
            stage_hops.append((match.group(1), match.group(2).lower()))
        stages.append(stage_hops)
    return stages


def _parse_lineage_graph(row):
    return _parse_lineage_graph_value(
        row,
        _oracle_token(row, "lineage_expected_hops"),
    )


def _canonical_lineage_scenario_text(fixture):
    repository_root = Path(__file__).resolve().parents[1]
    scenario_path = (repository_root / fixture / "SCENARIO.md").resolve()
    try:
        scenario_path.relative_to(repository_root.resolve())
    except ValueError:
        return None
    if not scenario_path.is_file():
        return None
    return scenario_path.read_text(encoding="utf-8")


def _canonical_lineage_fact_map(source_text):
    visible_structure = _canonical_visible_markdown_structure(source_text)
    heading_matches = list(
        re.finditer(
            r"(?m)^##[ \t]+Canonical Lineage Facts[ \t]*$",
            visible_structure,
        )
    )
    if len(heading_matches) != 1:
        raise ValueError(
            "canonical Contract Lineage facts heading must appear exactly once"
        )
    lines = visible_structure[heading_matches[0].end():].splitlines()
    fact_lines = []
    started = False
    for line in lines:
        if not line.strip():
            if started:
                break
            continue
        if not re.match(r"[ \t]*-[ \t]+", line):
            raise ValueError(
                "canonical Contract Lineage facts block is not machine-parsable"
            )
        started = True
        fact_lines.append(line)

    allowed_fields = {
        label for label, _row_field in CONTRACT_LINEAGE_CANONICAL_FACT_FIELDS
    }
    facts = {}
    for line in fact_lines:
        match = re.fullmatch(
            r"[ \t]*-[ \t]+(?P<field>[^:\r\n]+)"
            r":[ \t]*(?P<value>[^\r\n]*?)[ \t]*",
            line,
        )
        if match is None:
            raise ValueError(
                "canonical Contract Lineage facts block is not machine-parsable"
            )
        field = match.group("field").strip()
        value = match.group("value").strip()
        if field not in allowed_fields or field in facts or not value:
            raise ValueError(
                "canonical Contract Lineage facts block has an unknown, "
                "duplicate, or empty field"
            )
        facts[field] = value
    missing = sorted(allowed_fields - set(facts))
    if missing:
        raise ValueError(
            "canonical Contract Lineage facts block is missing: "
            + ", ".join(missing)
        )
    return facts


def _normalized_lineage_unverified_tokens(row, value, field):
    raw_value = str(value or "").strip()
    if raw_value.lower() == "none":
        return ()
    tokens = [token.strip() for token in raw_value.split("|")]
    if any(not token for token in tokens) or len(tokens) != len(set(tokens)):
        raise ValueError(
            f"{row_location(row)} {field} has empty or duplicate IDs"
        )
    return tuple(tokens)


def _require_canonical_contract_lineage_alignment(row, stages):
    fixture = str(row.get("fixture") or "").rstrip("/")
    if fixture not in CONTRACT_LINEAGE_CANONICAL_FIXTURES:
        return
    source_text = _canonical_lineage_scenario_text(fixture)
    if source_text is None:
        raise ValueError(
            f"{row_location(row)} canonical Contract Lineage SCENARIO.md is missing"
        )
    try:
        facts = _canonical_lineage_fact_map(source_text)
        canonical_stages = _parse_lineage_graph_value(
            row,
            facts["Hops"],
            "canonical Contract Lineage Hops",
        )
        canonical_unverified = _normalized_lineage_unverified_tokens(
            row,
            facts["Unverified / Branched Hops"],
            "canonical Contract Lineage Unverified / Branched Hops",
        )
    except ValueError as exc:
        raise ValueError(f"{row_location(row)} {exc}") from exc

    facts_by_row_field = {
        row_field: facts[label]
        for label, row_field in CONTRACT_LINEAGE_CANONICAL_FACT_FIELDS
    }
    mismatches = []
    for row_field in (
        "lineage_expected_canonical_owner",
        "lineage_expected_divergence",
        "lineage_expected_fix_owner",
    ):
        if facts_by_row_field[row_field] != _oracle_token(row, row_field):
            mismatches.append(row_field)
    if canonical_stages != stages:
        mismatches.append("lineage_expected_hops")
    expected_unverified = _normalized_lineage_unverified_tokens(
        row,
        _oracle_token(row, "lineage_expected_unverified_hops"),
        "lineage_expected_unverified_hops",
    )
    if canonical_unverified != expected_unverified:
        mismatches.append("lineage_expected_unverified_hops")
    if mismatches:
        raise ValueError(
            f"{row_location(row)} canonical Contract Lineage facts do not "
            "match row oracle: "
            + ", ".join(mismatches)
        )


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
    if "verify_scope" in output_contract:
        covered = _oracle_pipe_tokens(
            row, "lineage_expected_scope_covered"
        )
        missing_scope = _oracle_pipe_tokens(
            row, "lineage_expected_scope_missing"
        )
        if len(covered) != len(set(covered)) or len(missing_scope) != len(
            set(missing_scope)
        ):
            raise ValueError(
                f"{row_location(row)} Contract Lineage scope IDs must not repeat"
            )
        overlap = set(covered) & set(missing_scope)
        if overlap:
            raise ValueError(
                f"{row_location(row)} Contract Lineage scope covered/missing overlap: "
                + ", ".join(sorted(overlap))
            )
        scope_verdict = _oracle_token(
            row, "lineage_expected_scope_verdict"
        )
        if scope_verdict not in {
            "pass",
            "partial",
            "fail",
            "blocked",
            "unverified",
        }:
            raise ValueError(
                f"{row_location(row)} lineage_expected_scope_verdict must be one of: "
                "blocked, fail, partial, pass, unverified"
            )
        if missing_scope and scope_verdict == "pass":
            raise ValueError(
                f"{row_location(row)} Contract Lineage scope with missing evidence cannot pass"
            )
        if not missing_scope and scope_verdict != "pass":
            raise ValueError(
                f"{row_location(row)} complete Contract Lineage scope must pass"
            )
    stages = _parse_lineage_graph(row)
    hops = [hop for stage in stages for hop in stage]
    hop_id_list = [hop_id for hop_id, _state in hops]
    duplicate_hop_ids = sorted(
        hop_id for hop_id in set(hop_id_list) if hop_id_list.count(hop_id) > 1
    )
    if duplicate_hop_ids:
        raise ValueError(
            f"{row_location(row)} lineage_expected_hops has duplicate hop IDs: "
            + ", ".join(duplicate_hop_ids)
        )
    hop_ids = {hop_id for hop_id, _state in hops}
    hop_states = {hop_id: state for hop_id, state in hops}
    unverified_hop_ids = {
        hop_id for hop_id, state in hops if state == "unverified"
    }
    expected_unverified = _oracle_token(
        row, "lineage_expected_unverified_hops"
    )
    if expected_unverified.lower() == "none":
        expected_unverified_ids = set()
    else:
        expected_unverified_list = _oracle_pipe_tokens(
            row, "lineage_expected_unverified_hops"
        )
        duplicate_unverified_ids = sorted(
            hop_id
            for hop_id in set(expected_unverified_list)
            if expected_unverified_list.count(hop_id) > 1
        )
        if duplicate_unverified_ids:
            raise ValueError(
                f"{row_location(row)} lineage_expected_unverified_hops has duplicate IDs: "
                + ", ".join(duplicate_unverified_ids)
            )
        expected_unverified_ids = set(expected_unverified_list)
    missing_unverified_ids = unverified_hop_ids - expected_unverified_ids
    incorrectly_unverified_ids = (
        expected_unverified_ids & hop_ids
    ) - unverified_hop_ids
    if missing_unverified_ids:
        raise ValueError(
            f"{row_location(row)} unverified lineage hops are missing from "
            "lineage_expected_unverified_hops: "
            + ", ".join(sorted(missing_unverified_ids))
        )
    if incorrectly_unverified_ids:
        raise ValueError(
            f"{row_location(row)} verified lineage hops cannot be listed as unverified: "
            + ", ".join(sorted(incorrectly_unverified_ids))
        )

    canonical_owner = _oracle_token(row, "lineage_expected_canonical_owner")
    divergence = _oracle_token(row, "lineage_expected_divergence")
    fix_owner = _oracle_token(row, "lineage_expected_fix_owner")
    identifier_or_unverified = re.compile(
        r"(?:unverified|[A-Za-z0-9][A-Za-z0-9_.:/-]*)$"
    )
    for field, value in (
        ("lineage_expected_canonical_owner", canonical_owner),
        ("lineage_expected_divergence", divergence),
        ("lineage_expected_fix_owner", fix_owner),
    ):
        if not identifier_or_unverified.fullmatch(value):
            raise ValueError(
                f"{row_location(row)} {field} has an invalid identifier: {value}"
            )
    if canonical_owner != "unverified" and canonical_owner not in hop_ids:
        raise ValueError(
            f"{row_location(row)} lineage_expected_canonical_owner must be a hop or unverified"
        )
    if divergence != "unverified" and divergence not in hop_ids:
        raise ValueError(
            f"{row_location(row)} lineage_expected_divergence must be a hop or unverified"
        )
    if (
        canonical_owner != "unverified"
        and hop_states.get(canonical_owner) != "verified"
    ):
        raise ValueError(
            f"{row_location(row)} concrete lineage canonical owner must be verified"
        )
    if divergence != "unverified" and hop_states.get(divergence) != "verified":
        raise ValueError(
            f"{row_location(row)} First Confirmed Divergence must be a verified hop"
        )
    if fix_owner != "unverified" and divergence == "unverified":
        raise ValueError(
            f"{row_location(row)} lineage fix owner cannot be confirmed while divergence is unverified"
        )
    if canonical_owner == "unverified" and divergence != "unverified":
        raise ValueError(
            f"{row_location(row)} lineage divergence cannot be confirmed while canonical owner is unverified"
        )
    if divergence != "unverified":
        divergence_stage = next(
            index
            for index, stage in enumerate(stages)
            if any(hop_id == divergence for hop_id, _state in stage)
        )
        if any(
            state == "unverified"
            for stage in stages[:divergence_stage]
            for _hop_id, state in stage
        ):
            raise ValueError(
                f"{row_location(row)} lineage divergence cannot be confirmed after an earlier unverified hop"
            )
    if "verify_scope" in output_contract:
        _require_oracle_enum(
            row,
            "lineage_expected_scope_verdict",
            UAT_SCOPE_VERDICTS,
        )
    _require_canonical_contract_lineage_alignment(row, stages)


def require_release_evidence_claim_matrix(row):
    claim_type = _require_oracle_enum(
        row, "release_expected_claim_type", RELEASE_EVIDENCE_CLAIM_TYPES
    )
    evidence_status = _require_oracle_enum(
        row, "release_expected_evidence_status", RELEASE_EVIDENCE_STATUSES
    )
    refresh_method = _require_oracle_enum(
        row, "release_expected_refresh_method", RELEASE_REFRESH_METHODS
    )
    run_scope = _require_oracle_enum(
        row, "release_expected_run_scope", RELEASE_RUN_SCOPES
    )
    commands = _oracle_pipe_tokens(row, "release_expected_commands_or_trials")
    limitations = _oracle_pipe_tokens(row, "release_expected_limitations")

    if claim_type == "not_applicable" and evidence_status != "not_applicable":
        raise ValueError(
            f"{row_location(row)} not_applicable claim type requires not_applicable evidence status"
        )
    if evidence_status == "not_applicable" and claim_type != "not_applicable":
        raise ValueError(
            f"{row_location(row)} not_applicable evidence status requires not_applicable claim type"
        )
    if evidence_status == "verified":
        if not commands:
            raise ValueError(
                f"{row_location(row)} verified release claim requires commands_or_trials"
            )
        _require_concrete_oracle_value(row, "release_expected_source_root")
        if run_scope not in {"targeted", "full"}:
            raise ValueError(
                f"{row_location(row)} verified release claim requires targeted or full run scope"
            )
        if claim_type in RELEASE_PLUGIN_BOUND_CLAIM_TYPES:
            installed_plugin_root = _require_canonical_absolute_oracle_path(
                row, "release_expected_installed_plugin_root"
            )
            source_root = _require_canonical_absolute_oracle_path(
                row, "release_expected_source_root"
            )
            try:
                installed_resolved = Path(installed_plugin_root).resolve(
                    strict=False
                )
                source_resolved = Path(source_root).resolve(strict=False)
            except (OSError, RuntimeError) as exc:
                raise ValueError(
                    f"{row_location(row)} verified {claim_type} claim roots "
                    "must be safely resolvable"
                ) from exc
            if (
                installed_plugin_root == source_root
                or installed_resolved == source_resolved
            ):
                raise ValueError(
                    f"{row_location(row)} verified {claim_type} claim requires "
                    "distinct installed_plugin_root and source_root subjects"
                )
            if _paths_have_ancestor_relationship(
                Path(installed_plugin_root),
                Path(source_root),
            ) or _paths_have_ancestor_relationship(
                installed_resolved,
                source_resolved,
            ):
                raise ValueError(
                    f"{row_location(row)} verified {claim_type} claim installed_plugin_root "
                    "and source_root must not have an ancestor/descendant relationship"
                )
            if claim_type == "cache_refresh":
                allowed_refresh = {"refresh_step"}
            else:
                allowed_refresh = {"refresh_step", "source_equivalence"}
            if refresh_method not in allowed_refresh:
                raise ValueError(
                    f"{row_location(row)} verified {claim_type} claim has invalid refresh method"
                )
            _require_concrete_oracle_value(
                row, "release_expected_refresh_evidence"
            )
    elif evidence_status == "unverified":
        if not limitations:
            raise ValueError(
                f"{row_location(row)} unverified release claim requires limitations"
            )
    else:
        expected_not_applicable_fields = (
            "release_expected_installed_plugin_root",
            "release_expected_source_root",
            "release_expected_refresh_evidence",
        )
        for field in expected_not_applicable_fields:
            if _oracle_token(row, field) != "not_applicable":
                raise ValueError(
                    f"{row_location(row)} not_applicable release claim requires {field}=not_applicable"
                )
        if refresh_method != "not_applicable" or run_scope != "not_applicable":
            raise ValueError(
                f"{row_location(row)} not_applicable release claim requires not_applicable refresh and run scope"
            )
        if commands:
            raise ValueError(
                f"{row_location(row)} not_applicable release claim must not name commands_or_trials"
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
    if _oracle_token(row, "release_expected_claim_type") != "uat":
        raise ValueError(
            f"{row_location(row)} uat_evidence_window requires release claim type uat"
        )
    if _oracle_token(row, "release_expected_claim") != _oracle_token(
        row, "uat_expected_scope_claim"
    ):
        raise ValueError(
            f"{row_location(row)} UAT release claim must match Verification Scope claim"
        )

    scope_verdict = _require_oracle_enum(
        row, "uat_expected_scope_verdict", UAT_SCOPE_VERDICTS
    )
    result_tokens = _oracle_pipe_tokens(row, "uat_expected_result_missing")
    if len(result_tokens) != 2 or result_tokens[0] not in UAT_RESULT_TOKENS:
        raise ValueError(
            f"{row_location(row)} uat_expected_result_missing must use result|missing_reason"
        )
    result = result_tokens[0]
    expected_scope_verdict = {
        "pass": "pass",
        "partial": "partial",
        "observed_only": "partial",
        "fail": "fail",
        "blocked": "blocked",
    }[result]
    if scope_verdict != expected_scope_verdict:
        raise ValueError(
            f"{row_location(row)} UAT result {result} requires scope verdict "
            f"{expected_scope_verdict}"
        )
    scope_missing = _oracle_token(row, "uat_expected_scope_missing")
    fingerprint = _oracle_token(row, "uat_expected_fingerprint")
    preconditions = _require_oracle_enum(
        row, "uat_expected_preconditions", UAT_PRECONDITION_TOKENS
    )
    stability_list = _parse_uat_window_stability(row)
    stability_tokens = set(stability_list)
    evidence_status = _oracle_token(row, "release_expected_evidence_status")
    unstable = bool(
        stability_tokens
        & {"changed", "restart_required", "unverified", "stability_unverified"}
    )
    unattributed = fingerprint.lower() in {
        "",
        "none",
        "unknown",
        "unverified",
        "not_run",
        "not_applicable",
    }
    if result == "pass" or evidence_status == "verified":
        _require_attributed_uat_fingerprint(
            row, "uat_expected_fingerprint"
        )
        _require_material_uat_value(
            row, "uat_expected_scope_claim"
        )
        _require_material_uat_value(
            row, "release_expected_claim"
        )
        _require_material_uat_value(
            row, "uat_expected_claim_scope", pipe_list=True
        )
        _require_material_uat_value(
            row, "uat_expected_scope_covered", pipe_list=True
        )
        _require_material_uat_value(
            row, "uat_expected_coverage_basis", pipe_list=True
        )

    if result == "pass":
        if (
            scope_verdict != "pass"
            or scope_missing != "none"
            or preconditions != "satisfied"
            or stability_tokens != {"stable"}
            or result_tokens[1] != "none"
            or evidence_status != "verified"
            or unattributed
        ):
            raise ValueError(
                f"{row_location(row)} UAT pass oracle requires stable, satisfied, fully covered, verified evidence"
            )
    else:
        if result_tokens[1] == "none" or scope_missing == "none":
            raise ValueError(
                f"{row_location(row)} non-pass UAT result must name missing evidence in both result and scope"
            )
    if unstable or unattributed:
        if result == "pass" or scope_verdict == "pass" or evidence_status == "verified":
            raise ValueError(
                f"{row_location(row)} unstable or unattributed UAT evidence cannot be pass or verified"
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
    require_release_evidence_claim_matrix(row)


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
    missing_scope = [
        field
        for field in UAT_EVIDENCE_WINDOW_SCOPE_EXPECTATION_FIELDS
        if not _oracle_token(row, field)
    ]
    if missing_scope:
        raise ValueError(
            f"{row_location(row)} bounded UAT observation requires scope oracle fields: "
            + ", ".join(missing_scope)
        )
    stale_fields = [
        field
        for field in UAT_EVIDENCE_WINDOW_EXPECTATION_FIELDS
        if _oracle_token(row, field)
    ]
    if stale_fields:
        raise ValueError(
            f"{row_location(row)} uat_evidence_window_forbidden has stale UAT oracle fields: "
            + ", ".join(stale_fields)
        )
    if _oracle_token(row, "release_expected_claim_type") != "uat":
        raise ValueError(
            f"{row_location(row)} bounded UAT observation requires release claim type uat"
        )
    if _oracle_token(row, "release_expected_claim") != _oracle_token(
        row, "uat_expected_scope_claim"
    ):
        raise ValueError(
            f"{row_location(row)} bounded UAT release claim must match Verification Scope claim"
        )
    _require_oracle_enum(
        row, "uat_expected_scope_verdict", UAT_SCOPE_VERDICTS
    )
    if _oracle_token(row, "release_expected_evidence_status") == "verified":
        _require_material_uat_value(
            row, "uat_expected_scope_claim"
        )
        _require_material_uat_value(
            row, "release_expected_claim"
        )
        _require_material_uat_value(
            row, "uat_expected_scope_covered", pipe_list=True
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
    if _oracle_token(row, "release_expected_claim_type") != "uat":
        raise ValueError(
            f"{row_location(row)} UAT handoff requires release claim type uat"
        )
    if _oracle_token(row, "release_expected_claim") != _oracle_token(
        row, "uat_handoff_expected_claim_scope"
    ):
        raise ValueError(
            f"{row_location(row)} UAT handoff release claim must match continuation scope"
        )
    stability_tokens = _parse_uat_window_stability(
        row, "uat_handoff_expected_window_stability"
    )
    if _oracle_token(row, "release_expected_evidence_status") == "verified":
        if stability_tokens != ["stable"]:
            raise ValueError(
                f"{row_location(row)} verified UAT handoff requires a stable window"
            )
        _require_attributed_uat_fingerprint(
            row, "uat_handoff_expected_fingerprint"
        )
        _require_material_uat_value(
            row, "release_expected_claim"
        )
        _require_material_uat_value(
            row, "uat_handoff_expected_claim_scope", pipe_list=True
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
    suite_name = str(row.get("_suite") or "")

    def canonical_repo_prompt_source():
        raw_source = str(row.get("_prompt_source") or "")
        source_kind = str(row.get("_prompt_source_kind") or "")
        if (
            source_kind != "registered_suite"
            or not raw_source
        ):
            return False
        source_path = Path(raw_source)
        prompts_root = Path(__file__).resolve().parent / "prompts"
        canonical_source = prompts_root / suite_name
        if (
            not source_path.is_absolute()
            or raw_source != str(source_path)
            or source_path != canonical_source
            or prompts_root.is_symlink()
            or canonical_source.is_symlink()
            or not canonical_source.is_file()
        ):
            return False
        try:
            resolved_prompts_root = prompts_root.resolve(strict=True)
            resolved_source = source_path.resolve(strict=True)
            resolved_canonical_source = canonical_source.resolve(
                strict=True
            )
            resolved_source.relative_to(resolved_prompts_root)
        except (OSError, RuntimeError, ValueError):
            return False
        return (
            resolved_prompts_root == prompts_root
            and resolved_source == resolved_canonical_source
            and resolved_source.parent == resolved_prompts_root
        )

    def legacy_fixture_route_allowed(route):
        return (
            boolish(row.get("fixture_only"))
            and not is_trace_ready_row(row)
            and canonical_repo_prompt_source()
            and (suite_name, route)
            in LEGACY_FIXTURE_ONLY_INTERNAL_ROUTE_ALLOWLIST
        )

    if not expected_best:
        raise ValueError(f"{row_location(row)} missing required expected_best")
    if expected_best == "blocked":
        raise ValueError(f"{row_location(row)} blocked is not a route")
    if expected_best == HOST_PREEMPTION_ROUTE:
        raise ValueError(f"{row_location(row)} runtime-safety-gate is not allowed as expected_best")
    if (
        expected_best not in EXPECTED_BEST_ROUTES
        and not legacy_fixture_route_allowed(expected_best)
    ):
        raise ValueError(f"{row_location(row)} unknown expected_best route: {expected_best}")

    if "blocked" in route_lists:
        raise ValueError(f"{row_location(row)} blocked is not allowed in route lists")

    unknown_routes = [
        route
        for route in route_lists
        if route not in ROUTE_LIST_ROUTES
        and not legacy_fixture_route_allowed(route)
    ]
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
    _canonical_row_id(row)
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
    require_output_contract_compatibility(row, output_contract)
    require_output_contract_oracle_alignment(row, output_contract)
    require_contract_lineage_expectations(row, output_contract)
    require_annotation_presentation_expectations(row, output_contract)
    require_release_evidence_claim_expectations(row, output_contract)
    require_uat_evidence_window_expectations(row, output_contract)
    require_uat_evidence_window_forbidden_contract(row, output_contract)
    require_uat_handoff_reference_expectations(row, output_contract)
    require_canonical_uat_record_alignment(row, output_contract)
    if "contract_lineage" in output_contract and "uat_evidence_window" in output_contract:
        mismatched_scope_fields = []
        for lineage_field, uat_field in zip(
            CONTRACT_LINEAGE_SCOPE_EXPECTATION_FIELDS,
            UAT_EVIDENCE_WINDOW_SCOPE_EXPECTATION_FIELDS,
        ):
            if _oracle_token(row, lineage_field) != _oracle_token(row, uat_field):
                mismatched_scope_fields.append(f"{lineage_field}!={uat_field}")
        if mismatched_scope_fields:
            raise ValueError(
                f"{row_location(row)} UAT and Contract Lineage must share one identical Verification Scope: "
                + ", ".join(mismatched_scope_fields)
            )
    evidence_required, future_evidence_required = measurement_tokens_for_row(
        row,
        "evidence_required",
        EVIDENCE_REQUIRED_IMPLEMENTED_TOKENS,
        EVIDENCE_REQUIRED_FUTURE_TOKENS,
    )
    if (
        _oracle_token(row, "release_expected_claim_type") == "uat"
        and _oracle_token(row, "release_expected_evidence_status")
        == "verified"
        and {
            "uat_evidence_window",
            "uat_evidence_window_forbidden",
            "uat_handoff_reference",
        }.intersection(output_contract)
        and "source_or_unverified" not in evidence_required
    ):
        raise ValueError(
            f"{row_location(row)} verified UAT adapter requires source_or_unverified evidence"
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


_CSV_HEADER_CONFUSABLE_TRANSLATION = str.maketrans(
    {
        "А": "a",
        "а": "a",
        "Α": "a",
        "α": "a",
        "В": "b",
        "Β": "b",
        "Е": "e",
        "е": "e",
        "Ε": "e",
        "ε": "e",
        "Н": "h",
        "І": "i",
        "і": "i",
        "Ι": "i",
        "ι": "i",
        "ј": "j",
        "Ј": "j",
        "κ": "k",
        "Κ": "k",
        "К": "k",
        "к": "k",
        "М": "m",
        "м": "m",
        "Μ": "m",
        "Ν": "n",
        "Ο": "o",
        "ο": "o",
        "О": "o",
        "о": "o",
        "Ρ": "p",
        "ρ": "p",
        "Р": "p",
        "р": "p",
        "Ѕ": "s",
        "ѕ": "s",
        "С": "c",
        "с": "c",
        "Т": "t",
        "Τ": "t",
        "τ": "t",
        "Υ": "y",
        "υ": "y",
        "У": "y",
        "у": "y",
        "Χ": "x",
        "χ": "x",
        "Х": "x",
        "х": "x",
    }
)


def _is_default_ignorable_code_point(character):
    codepoint = ord(character)
    if unicodedata.category(character) == "Cf":
        return True
    return (
        codepoint == 0x034F
        or 0x115F <= codepoint <= 0x1160
        or 0x17B4 <= codepoint <= 0x17B5
        or 0x180B <= codepoint <= 0x180F
        or codepoint == 0x2065
        or 0xFE00 <= codepoint <= 0xFE0F
        or codepoint == 0x3164
        or codepoint == 0xFFA0
        or 0xFFF0 <= codepoint <= 0xFFF8
        or 0x1BCA0 <= codepoint <= 0x1BCA3
        or 0x1D173 <= codepoint <= 0x1D17A
        or 0xE0000 <= codepoint <= 0xE0FFF
    )


def _csv_header_has_forbidden_unicode(name):
    normalized = unicodedata.normalize("NFKC", str(name or ""))
    return any(
        unicodedata.category(character) in {"Cc", "Cs"}
        or _is_default_ignorable_code_point(character)
        for character in normalized
    )


def _csv_header_is_canonical_ascii_identifier(name):
    raw_name = str(name or "")
    normalized = unicodedata.normalize("NFKC", raw_name)
    return (
        raw_name == normalized
        and re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", normalized)
        is not None
    )


def _normalized_csv_header(name):
    if name is None:
        return ""
    normalized = unicodedata.normalize(
        "NFKC",
        str(name),
    ).strip().lstrip("\ufeff").strip()
    normalized = "".join(
        character
        for character in normalized
        if unicodedata.category(character) not in {"Cc", "Cs"}
        and not _is_default_ignorable_code_point(character)
    )
    return normalized.casefold()


def _csv_header_reserved_confusable(name):
    normalized = _normalized_csv_header(name)
    skeleton = normalized.translate(
        _CSV_HEADER_CONFUSABLE_TRANSLATION
    )
    return (
        normalized != skeleton
        and skeleton in RESERVED_CSV_HEADERS
    )


def _csv_header_reserved_noncanonical_spelling(name):
    raw_name = str(name or "")
    normalized = unicodedata.normalize("NFKC", raw_name)
    return (
        normalized.casefold() in RESERVED_CSV_HEADERS
        and raw_name != normalized.casefold()
    )


def csv_header_errors(fieldnames, location):
    location = str(location or "unknown")
    if fieldnames is None:
        return [f"{location} malformed CSV header is missing"]
    fieldnames = list(fieldnames)
    if not fieldnames:
        return [f"{location} malformed CSV header is missing"]

    errors = []
    if any(not _normalized_csv_header(name) for name in fieldnames):
        errors.append(f"{location} malformed CSV header has blank columns")
    forbidden_unicode_headers = [
        str(name)
        for name in fieldnames
        if name is not None
        and _csv_header_has_forbidden_unicode(name)
    ]
    if forbidden_unicode_headers:
        errors.append(
            f"{location} malformed CSV header contains control "
            "or default-ignorable Unicode: "
            + ", ".join(repr(name) for name in forbidden_unicode_headers)
        )
    invalid_identifier_headers = [
        str(name)
        for name in fieldnames
        if name is not None
        and not _csv_header_is_canonical_ascii_identifier(name)
    ]
    if invalid_identifier_headers:
        errors.append(
            f"{location} malformed CSV header must use canonical "
            "ASCII identifiers after NFKC: "
            + ", ".join(repr(name) for name in invalid_identifier_headers)
        )
    reserved_confusables = [
        str(name)
        for name in fieldnames
        if name is not None
        and _csv_header_reserved_confusable(name)
    ]
    if reserved_confusables:
        errors.append(
            f"{location} malformed CSV header visually aliases "
            "a reserved field: "
            + ", ".join(repr(name) for name in reserved_confusables)
        )
    reserved_noncanonical_spellings = [
        str(name)
        for name in fieldnames
        if name is not None
        and _csv_header_reserved_noncanonical_spelling(name)
    ]
    if reserved_noncanonical_spellings:
        errors.append(
            f"{location} malformed CSV header must use canonical "
            "reserved-field spelling: "
            + ", ".join(
                repr(name) for name in reserved_noncanonical_spellings
            )
        )
    normalized_headers = {}
    for name in fieldnames:
        if name is None:
            continue
        normalized = _normalized_csv_header(name)
        normalized_headers.setdefault(normalized, []).append(str(name))
    duplicate_headers = [
        names
        for normalized, names in normalized_headers.items()
        if normalized and len(names) > 1
    ]
    if duplicate_headers:
        errors.append(
            f"{location} malformed CSV header has duplicate columns "
            "after BOM/strip/casefold normalization: "
            + "; ".join(
                ", ".join(repr(name) for name in names)
                for names in duplicate_headers
            )
        )
    return errors


def malformed_csv_errors(row):
    errors = []
    if None in row:
        errors.append(f"{row_location(row)} malformed CSV row has extra cells: {row.get(None)}")
    fieldnames = row.get("_fieldnames")
    if fieldnames:
        errors.extend(csv_header_errors(fieldnames, row_location(row)))
        if is_trace_ready_row(row):
            missing_headers = sorted(
                set(ROUTING_SCHEMA_FIELDS) - set(fieldnames)
            )
            if missing_headers:
                errors.append(
                    f"{row_location(row)} trace-ready CSV header is missing "
                    "required columns: "
                    + ", ".join(missing_headers)
                )
    try:
        _canonical_row_id(row)
    except ValueError as exc:
        errors.append(str(exc))
    return errors


def validate_routing_schema(rows):
    errors = []
    seen_ids = {}
    normalized = []

    for row in rows:
        row_errors = malformed_csv_errors(row)
        errors.extend(row_errors)
        try:
            row_id, row_identity = _canonical_row_id(row)
        except ValueError:
            continue
        if row_identity in seen_ids:
            errors.append(
                f"{row_location(row)} duplicate row id canonical identity "
                f"{row_id!r} also seen at {seen_ids[row_identity]}"
            )
        else:
            seen_ids[row_identity] = row_location(row)
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
