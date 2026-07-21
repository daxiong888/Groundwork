#!/usr/bin/env python3
import csv
import argparse
import hashlib
import json
import os
try:
    import pwd
except ImportError:  # pragma: no cover - unavailable on Windows
    pwd = None
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote, unquote

try:
    from checks.common import has_required_field, missing_required_fields
    from checks.forbidden_patterns import (
        check_review_loop_claims,
        forbidden_git_add_dot_suggestion,
        has_archive_or_branch_cleanup_ready_claim,
        has_clean_review_blocked_or_unverified_boundary,
        has_clean_review_nested_delegation_disclosure,
        has_clean_review_parent_context_fork_disclosure,
        has_clean_review_pass_claim,
        has_diff_only_readiness_pass_claim,
    )
    from checks.loop_checks import (
        annotation_carrythrough_verification_failures,
        annotation_handoff_reference_failures,
        annotation_presentation_decision_failures,
        checkpoint_before_risky_action_failures,
        contract_lineage_failures,
        contract_lineage_route_companion_failures,
        prototype_iteration_checkpoint_failures,
        prototype_no_delta_stop_failures,
        prototype_one_shot_failures,
        spec_clear_fast_path_failures,
        spec_gap_list_failures,
        spec_no_delta_stop_failures,
        spec_single_question_failures,
        spec_writeback_failures,
        release_evidence_claim_failures,
        release_evidence_claim_status,
        release_evidence_claim_values,
        uat_evidence_window_absence_failures,
        uat_evidence_window_failures,
        uat_handoff_reference_failures,
    )
    from checks.verify_checks import (
        ARTIFACT_HEADER_FIELDS,
        QA_FAILURE_FIELDS,
        VERIFY_SCOPE_FIELDS,
        missing_verify_scope_fields,
        qa_gap_closure_gate_failures,
    )
except ImportError:  # pragma: no cover - package import path
    from evals.checks.common import has_required_field, missing_required_fields
    from evals.checks.forbidden_patterns import (
        check_review_loop_claims,
        forbidden_git_add_dot_suggestion,
        has_archive_or_branch_cleanup_ready_claim,
        has_clean_review_blocked_or_unverified_boundary,
        has_clean_review_nested_delegation_disclosure,
        has_clean_review_parent_context_fork_disclosure,
        has_clean_review_pass_claim,
        has_diff_only_readiness_pass_claim,
    )
    from evals.checks.loop_checks import (
        annotation_carrythrough_verification_failures,
        annotation_handoff_reference_failures,
        annotation_presentation_decision_failures,
        checkpoint_before_risky_action_failures,
        contract_lineage_failures,
        contract_lineage_route_companion_failures,
        prototype_iteration_checkpoint_failures,
        prototype_no_delta_stop_failures,
        prototype_one_shot_failures,
        spec_clear_fast_path_failures,
        spec_gap_list_failures,
        spec_no_delta_stop_failures,
        spec_single_question_failures,
        spec_writeback_failures,
        release_evidence_claim_failures,
        release_evidence_claim_status,
        release_evidence_claim_values,
        uat_evidence_window_absence_failures,
        uat_evidence_window_failures,
        uat_handoff_reference_failures,
    )
    from evals.checks.verify_checks import (
        ARTIFACT_HEADER_FIELDS,
        QA_FAILURE_FIELDS,
        VERIFY_SCOPE_FIELDS,
        missing_verify_scope_fields,
        qa_gap_closure_gate_failures,
    )
try:
    from routing_schema import (
        CASE_KIND_TOKENS,
        CASE_SOURCE_TOKENS,
        DIRECT_ROUTE,
        EVIDENCE_REQUIRED_FUTURE_TOKENS,
        EVIDENCE_REQUIRED_IMPLEMENTED_TOKENS,
        EXPECTED_BEST_ROUTES,
        HOST_PREEMPTION_ROUTE,
        INTENT_KIND_TOKENS,
        NOT_APPLICABLE,
        OUTPUT_CONTRACT_FUTURE_TOKENS,
        OUTPUT_CONTRACT_IMPLEMENTED_TOKENS,
        PUBLIC_SKILL_ROUTES,
        REQUIREMENT_STATE_TOKENS,
        RISK_GATE_TOKENS,
        ROUTE_LIST_ROUTES,
        ROUTING_SCHEMA_FIELDS,
        SOURCE_TRUTH_TOKENS,
        STATE_TRANSITION_TOKENS,
        STOP_CONDITION_TOKENS,
        TRACE_READY_SUITES,
        UNKNOWN_ROUTE,
        boolish,
        canonical_uat_record_section_text,
        csv_header_errors,
        expected_skill_for_row,
        host_preemption_allowed,
        is_routing_reliability_row,
        is_trace_ready_row,
        malformed_csv_errors,
        measurement_tokens_for_row,
        parse_pipe_list,
        route_expectations_for_row,
        routing_schema_for_row,
        row_location,
        validate_routing_schema,
        validate_token,
    )
except ImportError:  # pragma: no cover - package import path
    from evals.routing_schema import (
        CASE_KIND_TOKENS,
        CASE_SOURCE_TOKENS,
        DIRECT_ROUTE,
        EVIDENCE_REQUIRED_FUTURE_TOKENS,
        EVIDENCE_REQUIRED_IMPLEMENTED_TOKENS,
        EXPECTED_BEST_ROUTES,
        HOST_PREEMPTION_ROUTE,
        INTENT_KIND_TOKENS,
        NOT_APPLICABLE,
        OUTPUT_CONTRACT_FUTURE_TOKENS,
        OUTPUT_CONTRACT_IMPLEMENTED_TOKENS,
        PUBLIC_SKILL_ROUTES,
        REQUIREMENT_STATE_TOKENS,
        RISK_GATE_TOKENS,
        ROUTE_LIST_ROUTES,
        ROUTING_SCHEMA_FIELDS,
        SOURCE_TRUTH_TOKENS,
        STATE_TRANSITION_TOKENS,
        STOP_CONDITION_TOKENS,
        TRACE_READY_SUITES,
        UNKNOWN_ROUTE,
        boolish,
        canonical_uat_record_section_text,
        csv_header_errors,
        expected_skill_for_row,
        host_preemption_allowed,
        is_routing_reliability_row,
        is_trace_ready_row,
        malformed_csv_errors,
        measurement_tokens_for_row,
        parse_pipe_list,
        route_expectations_for_row,
        routing_schema_for_row,
        row_location,
        validate_routing_schema,
        validate_token,
    )

try:
    from suite_registry import DEFAULT_SUITES
except ImportError:  # pragma: no cover - package import path
    from evals.suite_registry import DEFAULT_SUITES

try:
    from case_oracles import validate_case as validate_fixture_case
except ImportError:  # pragma: no cover - package import path
    from evals.case_oracles import validate_case as validate_fixture_case

try:
    from routing_summary import (
        summarize_routing_results as shared_summarize_routing_results,
    )
except ImportError:  # pragma: no cover - package import path
    from evals.routing_summary import (
        summarize_routing_results as shared_summarize_routing_results,
    )

try:
    from route_detection import detect_route_from_text
    from route_detection import has_dispatch_route_marker as shared_has_dispatch_route_marker
except ImportError:  # pragma: no cover - package import path
    from evals.route_detection import detect_route_from_text
    from evals.route_detection import has_dispatch_route_marker as shared_has_dispatch_route_marker

REPO = Path(os.environ.get("GROUNDWORK_REPO", Path(__file__).resolve().parents[1]))
ROOT = Path(os.environ.get("GROUNDWORK_RUNTIME_ROOT", "/private/tmp/groundwork-runtime-v03"))
RUN = ROOT / datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
LOGS = RUN / "logs"
LAST = RUN / "last"
WORKSPACES = RUN / "workspaces"
RESULTS = RUN / "results.jsonl"
CASES = RUN / "cases"
PROOF_HOME = RUN / "proof-home"
SUMMARY = RUN / "summary.json"
FAILURES = RUN / "failures.md"
RUNTIME_SELECTOR = {
    "model": "",
    "profile": "",
    "codex_config": [],
    "hook_trust_bypass": False,
}

ROUTING_RELIABILITY_SUITE = "routing-reliability.csv"
TRACE_FIRST_VERIFY_REVIEW_SUITE = "trace-first-verify-review.csv"
CLEAN_REVIEW_FANOUT_SUITE = "clean-review-fanout.csv"
ZH_TRIGGER_PARITY_SUITE = "zh-trigger-parity.csv"

NO_EDIT_MARKERS = [
    "不要编辑文件",
    "不要改文件",
    "不要写文件",
    "不要创建文件",
    "Do not edit files",
    "Do not execute commands",
    "不要执行命令",
    "不要改数据",
    "不要调用",
    "只报告",
    "只输出",
]

GATE_FIELDS = ["Proposed Action", "Target", "Risk", "Rollback/Undo", "Approval Needed"]
HOST_PREEMPTION_RISK_GATES = {
    "git_write",
    "remote_write",
    "destructive",
    "customer_visible",
    "data_write",
    "secrets_or_pii",
}
HOST_PREEMPTION_INTENT_KINDS = {"remote_mutation"}
NO_EXECUTION_GATE_MARKERS = [
    "did not execute",
    "didn't execute",
    "will not execute",
    "will not run",
    "not executed",
    "no execution",
    "without executing",
    "without running",
    "未执行",
    "没执行",
    "没能执行",
    "没有执行",
    "没能完成",
    "没有完成",
    "未完成",
    "未发生",
    "未关闭",
    "没有关闭",
    "不会执行",
    "不会运行",
    "不执行",
    "不运行",
    "不能执行",
    "不能直接改",
    "不能进入修改",
    "不能编辑",
    "不能实际修改",
    "不能删除",
    "不能提交",
    "不能推送",
    "不能落盘",
    "不能写",
    "不能修改",
    "不能落文件",
    "实现必须停止",
    "无法安全落地",
    "无法执行",
    "无法落盘",
    "无法写文件",
    "没有文件被修改",
    "没有改文件",
    "不能安全直接改文件",
]
CONFORMANCE_FIELDS = [
    "Scope",
    "Acceptance Map",
    "Evidence Inspected",
    "Findings P0/P1/P2",
    "Non-Readiness Boundary",
    "Gaps",
    "Next Action",
    "Unverified Claims",
]
STATE_REQUIRED_FIELDS = [
    "Target Reader",
    "Reader Action Needed",
    "Decision Supported",
    "Scope",
    "Out of Scope",
    "Evidence Level",
    "Last Updated",
    "Canonical Sources",
    "Current Workflow Mode",
    "Current Gap Closure",
    "Next Skill",
    "Stop Condition",
]
RESERVED_WORKSTREAM_SLUGS = {"project", "all", "global", "current"}
FIXTURE_SETUP_FILE = ".groundwork-fixture.json"
CODEX_EXEC_TIMEOUT = int(os.environ.get("GROUNDWORK_CODEX_TIMEOUT", "360"))


def optional_boolish(value):
    if value is None or str(value).strip() == "":
        return None
    return str(value).strip().lower() in {"1", "true", "yes", "y"}


CASE_ARTIFACT_SAFE_CHARACTERS = (
    "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_.-"
)


def safe_id(value):
    raw_value = str(value or "")
    if not raw_value:
        raise ValueError("case artifact id must not be empty")
    encoded = quote(
        raw_value,
        safe=CASE_ARTIFACT_SAFE_CHARACTERS,
        encoding="utf-8",
        errors="strict",
    )
    if (
        not encoded
        or encoded in {".", ".."}
        or unquote(encoded, encoding="utf-8", errors="strict") != raw_value
    ):
        raise ValueError(
            f"case artifact id is not reversibly encodable: {raw_value!r}"
        )
    return encoded


def case_artifact_identity_errors(rows):
    errors = []
    seen_stems = {}
    for row in rows:
        row_id = str(row.get("id") or "")
        try:
            stem = safe_id(row_id)
        except ValueError as exc:
            errors.append(f"{row_location(row)} {exc}")
            continue
        previous = seen_stems.get(stem)
        if previous is not None and previous != row_id:
            errors.append(
                f"{row_location(row)} case artifact path collision: "
                f"{row_id!r} and {previous!r} both map to {stem!r}"
            )
        else:
            seen_stems[stem] = row_id
    return errors


def prompt_suites():
    return sorted(p.name for p in (REPO / "evals" / "prompts").glob("*.csv"))


def normalize_suite_name(value):
    text = str(value).strip()
    if text and "/" not in text and "\\" not in text and not text.endswith(".csv"):
        text += ".csv"
    return text


def canonical_prompt_file(value):
    path = Path(value)
    if not path.is_absolute():
        path = REPO / path
    return str(path.resolve(strict=False))


PROMPT_SOURCE_KINDS = {
    "registered_suite",
    "external_prompt_file",
}


def read_prompt_rows(
    path,
    suite_label=None,
    *,
    allow_empty=False,
    prompt_source_kind="external_prompt_file",
):
    if prompt_source_kind not in PROMPT_SOURCE_KINDS:
        raise ValueError(
            f"unknown prompt source kind: {prompt_source_kind}"
        )
    path = Path(path)
    rows = []
    prompt_source = os.path.abspath(os.fspath(path))
    with path.open(newline="") as fh:
        reader = csv.DictReader(fh)
        label = suite_label or path.name
        header_errors = csv_header_errors(
            reader.fieldnames,
            f"{label}:1",
        )
        if header_errors:
            raise ValueError("; ".join(header_errors))
        for row_number, row in enumerate(reader, start=2):
            row["_suite"] = label
            row["_row_number"] = row_number
            row["_fieldnames"] = reader.fieldnames or []
            row["_prompt_source"] = prompt_source
            row["_prompt_source_kind"] = prompt_source_kind
            rows.append(row)
    if not rows and not allow_empty:
        raise ValueError(f"{suite_label or path.name}: prompt suite has no data rows")
    return rows


def read_rows(suites, prompt_files=None):
    out = []
    for suite in suites:
        suite_name = normalize_suite_name(suite)
        path = REPO / "evals" / "prompts" / suite_name
        out.extend(
            read_prompt_rows(
                path,
                suite_label=suite_name,
                prompt_source_kind="registered_suite",
            )
        )
    for prompt_file in prompt_files or []:
        path = Path(canonical_prompt_file(prompt_file))
        out.extend(
            read_prompt_rows(
                path,
                suite_label=path.name,
                prompt_source_kind="external_prompt_file",
            )
        )
    return out


def is_auto_skipped_row(row):
    return boolish(row.get("targeted_only")) or boolish(row.get("fixture_only"))


def filter_auto_discovery_rows(rows):
    kept = []
    skipped = []
    for row in rows:
        if is_auto_skipped_row(row):
            skipped.append(row)
        else:
            kept.append(row)
    return kept, skipped


def split_resource_keys(value):
    if not value:
        return []
    text = str(value).strip()
    if not text:
        return []
    if text.startswith("["):
        try:
            parsed = json.loads(text)
        except json.JSONDecodeError:
            parsed = None
        if isinstance(parsed, list):
            return [str(item).strip() for item in parsed if str(item).strip()]
    return [item for item in re.split(r"[\s,;|]+", text) if item]


def infer_resource_keys(row):
    explicit = split_resource_keys(row.get("resource_keys"))
    if explicit:
        return explicit

    keys = []
    prompt = (row.get("prompt") or row.get("input_scenario") or "").lower()
    fixture = row.get("fixture") or "none"
    flake_policy = (row.get("flake_policy") or "").strip().lower()

    if fixture == "repo-root":
        keys.extend(["repo:groundwork", "codex_home"])
    elif fixture and fixture != "none":
        keys.append("workspace")
    if "browser" in prompt or "devtools" in prompt or "chrome" in prompt:
        keys.append("browser")
    if flake_policy and flake_policy != "none":
        keys.append("flaky")
    if boolish(row.get("risky_write_requested")) or boolish(row.get("gate_required")):
        keys.append("codex_home")

    return unique_in_order(keys)


def metadata_timeout(row, default_timeout=None):
    raw = row.get("timeout_s")
    if raw is None or str(raw).strip() == "":
        return default_timeout or CODEX_EXEC_TIMEOUT
    try:
        return max(1, int(str(raw).strip()))
    except ValueError:
        return default_timeout or CODEX_EXEC_TIMEOUT


def metadata_flake_policy(row):
    policy = str(row.get("flake_policy") or "none").strip().lower()
    return policy if policy in {"none", "rerun_once"} else "none"


def infer_parallel_safe(row):
    explicit = optional_boolish(row.get("parallel_safe"))
    if explicit is not None:
        return explicit

    prompt = row.get("prompt") or row.get("input_scenario") or ""
    expected = expected_skill_for_row(row)
    fixture = row.get("fixture") or "none"

    if any(marker in prompt for marker in NO_EDIT_MARKERS):
        return True
    if expected in {"direct", "to-prd", "to-issues", "triage", "write-plan", "prototype", "verify", "handoff"}:
        if not boolish(row.get("artifact_allowed")) and not boolish(row.get("risky_write_requested")):
            return True
    if fixture and fixture != "none" and expected != "implement":
        return True
    return False


def case_metadata(row):
    resource_keys = infer_resource_keys(row)
    parallel_safe = infer_parallel_safe(row)
    if any(key in {"browser", "codex_home", "flaky"} or key.startswith("repo:") for key in resource_keys):
        parallel_safe = False
    group = str(row.get("group") or "").strip()
    if not group:
        if "browser" in resource_keys:
            group = "browser"
        elif "flaky" in resource_keys:
            group = "flaky"
        elif any(key == "codex_home" or key.startswith("repo:") for key in resource_keys):
            group = "shared"
        else:
            group = "isolated" if parallel_safe else "serial"
    return {
        "parallel_safe": parallel_safe,
        "resource_keys": resource_keys,
        "timeout_s": metadata_timeout(row),
        "flake_policy": metadata_flake_policy(row),
        "group": group,
    }


def row_matches_group(row, group):
    if not group:
        return True
    metadata = case_metadata(row)
    return group == metadata["group"] or group in metadata["resource_keys"]


def partition_rows(rows, jobs, resource_policy="auto"):
    if jobs <= 1 or resource_policy != "auto":
        return [], list(rows)

    parallel_rows = []
    serial_rows = []
    for row in rows:
        metadata = case_metadata(row)
        if metadata["parallel_safe"]:
            parallel_rows.append(row)
        else:
            serial_rows.append(row)
    return parallel_rows, serial_rows


def load_failure_ids(path):
    summary_path = path / "summary.json" if path.is_dir() else path
    if not summary_path.exists():
        raise FileNotFoundError(f"missing summary file: {summary_path}")
    data = json.loads(summary_path.read_text(encoding="utf-8"))
    failures = data.get("failures") or []
    ids = []
    for item in failures:
        if isinstance(item, str):
            ids.append(item)
        elif isinstance(item, dict) and item.get("id"):
            ids.append(str(item["id"]))
    return ids


def is_ignored_runtime_scratch(rel):
    parts = rel.parts if isinstance(rel, Path) else Path(str(rel)).parts
    return parts[:3] == (".groundwork", "harness", "router-observability")


def snapshot(path):
    state = {}
    if not path.exists():
        return state
    for p in path.rglob("*"):
        rel = p.relative_to(path)
        if rel.parts and rel.parts[0] == ".git":
            continue
        if is_ignored_runtime_scratch(rel):
            continue
        if p.is_file():
            h = hashlib.sha256()
            h.update(p.read_bytes())
            state[str(rel)] = h.hexdigest()
    return state


def changed_files(before, after):
    keys = sorted(set(before) | set(after))
    changed = []
    for key in keys:
        if before.get(key) != after.get(key):
            if key not in before:
                changed.append("A " + key)
            elif key not in after:
                changed.append("D " + key)
            else:
                changed.append("M " + key)
    return changed


def hook_trust_bypass_enabled():
    return bool(RUNTIME_SELECTOR.get("hook_trust_bypass"))


ROUTER_OBSERVABILITY_CONFIG = Path(".groundwork") / "harness" / "router-observability" / "config.json"
ROUTER_OBSERVABILITY_MODES = {"observe_only"}
OBSERVE_ONLY_BOUNDARY = (
    "observe-only router observability run; no route hints injected; local eval evidence only, "
    "not release, UAT, marketplace, cache-refresh, hook-trust, or customer readiness evidence"
)
DISABLED_ROUTER_OBSERVABILITY_BOUNDARY = (
    "router observability disabled; runtime eval output is not router observability, release, UAT, "
    "marketplace, cache-refresh, hook-trust, or customer readiness evidence"
)
def runtime_path_state():
    return {
        "RUN": RUN,
        "LOGS": LOGS,
        "LAST": LAST,
        "WORKSPACES": WORKSPACES,
        "RESULTS": RESULTS,
        "CASES": CASES,
        "SUMMARY": SUMMARY,
        "FAILURES": FAILURES,
        "PROOF_HOME": PROOF_HOME,
    }


def set_runtime_paths(run_root):
    global RUN, LOGS, LAST, WORKSPACES, RESULTS, CASES, SUMMARY, FAILURES, PROOF_HOME
    RUN = Path(run_root)
    LOGS = RUN / "logs"
    LAST = RUN / "last"
    WORKSPACES = RUN / "workspaces"
    RESULTS = RUN / "results.jsonl"
    CASES = RUN / "cases"
    SUMMARY = RUN / "summary.json"
    FAILURES = RUN / "failures.md"
    PROOF_HOME = RUN / "proof-home"


def restore_runtime_path_state(state):
    global RUN, LOGS, LAST, WORKSPACES, RESULTS, CASES, SUMMARY, FAILURES, PROOF_HOME
    RUN = state["RUN"]
    LOGS = state["LOGS"]
    LAST = state["LAST"]
    WORKSPACES = state["WORKSPACES"]
    RESULTS = state["RESULTS"]
    CASES = state["CASES"]
    SUMMARY = state["SUMMARY"]
    FAILURES = state["FAILURES"]
    PROOF_HOME = state["PROOF_HOME"]


def normalize_router_observability_mode(value):
    return "observe_only"


def router_observability_evidence_boundary(mode):
    if mode == "observe_only":
        return OBSERVE_ONLY_BOUNDARY
    return DISABLED_ROUTER_OBSERVABILITY_BOUNDARY


def load_router_observability_config(cwd):
    if cwd is None:
        return None, "not_checked"
    path = Path(cwd) / ROUTER_OBSERVABILITY_CONFIG
    if not path.exists():
        return None, "absent"
    try:
        loaded = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None, "invalid_config"
    if not isinstance(loaded, dict):
        return None, "invalid_config"
    return loaded, str(ROUTER_OBSERVABILITY_CONFIG)


def router_observability_runtime_mode(cwd=None):
    if os.environ.get("GROUNDWORK_ROUTER_OBSERVABILITY_DISABLED"):
        mode = "disabled"
        enabled = False
        activation_source = "env_disabled"
    else:
        config, config_source = load_router_observability_config(cwd)
        config_enabled = bool(config and config.get("enabled") is True)
        config_mode = normalize_router_observability_mode(config.get("mode") if config else None)

        if os.environ.get("GROUNDWORK_ROUTER_OBSERVABILITY") == "1":
            enabled = True
            mode = normalize_router_observability_mode(
                os.environ.get("GROUNDWORK_ROUTER_OBSERVABILITY_MODE") or config_mode
            )
            activation_source = "env" if config_source in {"absent", "not_checked"} else "env_force_enable_over_config"
        elif config_enabled:
            enabled = True
            mode = config_mode
            activation_source = config_source
        else:
            enabled = False
            mode = "disabled"
            activation_source = config_source

    return {
        "router_observability_enabled": enabled,
        "router_observability_mode": mode,
        "hook_trust_bypass": hook_trust_bypass_enabled(),
        "evidence_boundary": router_observability_evidence_boundary(mode),
        "activation_source": activation_source,
    }


def score_eligibility_for_runtime_mode(runtime_mode):
    if bool((runtime_mode or {}).get("hook_trust_bypass")):
        return "insufficient_evidence"
    mode = str((runtime_mode or {}).get("router_observability_mode") or "disabled")
    if mode == "observe_only":
        return "baseline_eligible"
    return "insufficient_evidence"


def aggregate_runtime_mode(results):
    observed = [
        result.get("runtime_mode")
        for result in results
        if isinstance(result.get("runtime_mode"), dict)
    ]
    if not observed:
        return router_observability_runtime_mode()

    modes = sorted({str(item.get("router_observability_mode") or "disabled") for item in observed})
    if "observe_only" in modes:
        primary_mode = "observe_only"
    elif len(modes) == 1:
        primary_mode = modes[0]
    else:
        primary_mode = "mixed"

    return {
        "router_observability_enabled": any(bool(item.get("router_observability_enabled")) for item in observed),
        "router_observability_mode": primary_mode,
        "router_observability_modes": modes,
        "hook_trust_bypass": any(
            bool(item.get("hook_trust_bypass"))
            for item in observed
        ),
        "evidence_boundary": router_observability_evidence_boundary(primary_mode),
        "activation_sources": sorted({str(item.get("activation_source") or "unknown") for item in observed}),
    }


def eval_only_codex_config(row):
    if not row:
        return []
    evidence_tokens = parse_pipe_list(
        row.get("evidence_required"),
        "evidence_required",
        row,
        blank_default=[],
    )
    if "dispatch_default_read_path" in evidence_tokens:
        return ["features.memories=false"]
    return []


def prompt_for_row(row):
    return row.get("prompt") or row.get("input_scenario") or ""


def prompt_with_evidence_bindings(prompt, row, cwd):
    evidence_tokens = {
        token.strip()
        for token in str(row.get("evidence_required") or "").split("|")
        if token.strip()
    }
    if "git_status" not in evidence_tokens:
        return prompt
    workspace = Path(cwd).resolve(strict=True)
    command = "git -C " + shlex.quote(str(workspace)) + " status --short"
    return (
        prompt.rstrip()
        + "\n\nEvaluator evidence binding: when collecting git_status evidence, "
        + f"run `{command}`. Plain or differently targeted git status commands "
        + "are unverified."
    )


def codex_exec_command(cwd, sandbox, last_path, prompt, row=None):
    if CODEX_CONTROL_LAUNCHER is None:
        raise RuntimeError(
            "no trusted Codex launcher is available"
        )
    cmd = [str(CODEX_CONTROL_LAUNCHER)]
    if hook_trust_bypass_enabled():
        cmd.append("--dangerously-bypass-hook-trust")
    for item in RUNTIME_SELECTOR.get("codex_config") or []:
        cmd.extend(["-c", str(item)])
    for item in eval_only_codex_config(row):
        cmd.extend(["-c", item])
    cmd.extend(
        [
            "-a",
            "never",
            "exec",
            "--ephemeral",
            "--json",
            "-o",
            str(last_path),
            "-C",
            str(cwd),
            "--skip-git-repo-check",
            "-s",
            sandbox,
        ]
    )
    if RUNTIME_SELECTOR.get("model"):
        cmd.extend(["--model", str(RUNTIME_SELECTOR["model"])])
    if RUNTIME_SELECTOR.get("profile"):
        cmd.extend(["--profile", str(RUNTIME_SELECTOR["profile"])])
    cmd.append(prompt)
    return cmd


def run_fixture_command(cwd, cmd):
    child_environment, _context = sanitized_codex_environment()
    captured_command = _captured_evaluator_command(cmd)
    proc = subprocess.run(
        captured_command,
        cwd=cwd,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        env=child_environment,
    )
    if proc.returncode != 0:
        raise RuntimeError(
            "fixture setup command failed "
            f"({proc.returncode}): {' '.join(cmd)}\n{proc.stdout}"
        )
    return proc.stdout


def write_fixture_file(cwd, item, *, must_exist=False):
    rel = item["path"]
    target = cwd / rel
    if must_exist and not target.exists():
        raise FileNotFoundError(f"fixture dirty file does not exist before git commit: {rel}")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(item.get("content", ""), encoding="utf-8")


def setup_git_fixture(cwd, config):
    branch = config.get("branch", "main")
    run_fixture_command(cwd, ["git", "init"])
    run_fixture_command(cwd, ["git", "config", "user.name", "Groundwork Eval"])
    run_fixture_command(cwd, ["git", "config", "user.email", "groundwork-eval@example.invalid"])
    run_fixture_command(cwd, ["git", "branch", "-M", branch])

    tracked = []
    for path in cwd.rglob("*"):
        rel = path.relative_to(cwd)
        if rel.parts and rel.parts[0] == ".git":
            continue
        if path.is_file():
            tracked.append(str(rel))
    if tracked:
        run_fixture_command(cwd, ["git", "add", "--", *sorted(tracked)])
        run_fixture_command(cwd, ["git", "commit", "-m", config.get("commit_message", "fixture initial commit")])

    if config.get("detached_head"):
        run_fixture_command(cwd, ["git", "checkout", "--detach", "HEAD"])

    for item in config.get("dirty_files", []):
        write_fixture_file(cwd, item, must_exist=True)
    for item in config.get("untracked_files", []):
        write_fixture_file(cwd, item)


def apply_fixture_setup(cwd):
    setup_path = cwd / FIXTURE_SETUP_FILE
    if not setup_path.exists():
        return
    config = json.loads(setup_path.read_text(encoding="utf-8"))
    setup_path.unlink()
    if config.get("git"):
        setup_git_fixture(cwd, config["git"])


def unique_workspace_path(base):
    if not base.exists():
        return base
    for index in range(2, 1000):
        candidate = base.with_name(f"{base.name}-{index}")
        if not candidate.exists():
            return candidate
    raise RuntimeError(f"could not allocate unique workspace path for {base}")


def copy_fixture(fixture, row_id):
    src = REPO / fixture
    dst = unique_workspace_path(WORKSPACES / f"{row_id}-{Path(fixture).name}")
    if src.is_dir():
        shutil.copytree(src, dst)
    elif src.is_file():
        dst.mkdir(parents=True, exist_ok=False)
        shutil.copy2(src, dst / src.name)
    else:
        raise FileNotFoundError(f"fixture does not exist: {fixture}")
    apply_fixture_setup(dst)
    return dst


def empty_workspace(row_id):
    dst = unique_workspace_path(WORKSPACES / f"{row_id}-empty")
    dst.mkdir(parents=True, exist_ok=False)
    (dst / "README.md").write_text(
        "# Runtime eval scratch workspace\n\nNo source truth is provided unless the prompt does so.\n",
        encoding="utf-8",
    )
    return dst


def choose_workspace(row):
    row_id = row["id"]
    fixture = row.get("fixture") or "none"
    prompt = row.get("prompt") or row.get("input_scenario") or ""
    artifact_allowed = boolish(row.get("artifact_allowed"))
    expected = expected_skill_for_row(row)

    if fixture == "repo-root":
        return REPO, "read-only", "repo-root-git-boundary"

    if fixture and fixture != "none":
        cwd = copy_fixture(fixture, row_id)
        writable = expected == "implement" and not any(marker in prompt for marker in NO_EDIT_MARKERS)
        sandbox = "workspace-write" if writable else "read-only"
        return cwd, sandbox, fixture

    cwd = empty_workspace(row_id)
    writable = artifact_allowed and not boolish(row.get("risky_write_requested"))
    sandbox = "workspace-write" if writable else "read-only"
    return cwd, sandbox, "empty"


def unique_in_order(values):
    seen = set()
    out = []
    for value in values:
        if value not in seen:
            seen.add(value)
            out.append(value)
    return out


SKILL_LOAD_LOG_MARKERS = (
    "load skill",
    "loaded skill",
    "loading skill",
    "skill load",
    "skill_load",
    "skill_path",
    "skill_file",
    "skill.injected",
)


def looks_like_skill_load_line(line):
    stripped = line.strip()
    if not stripped:
        return False
    lowered = stripped.lower()
    try:
        value = json.loads(stripped)
    except json.JSONDecodeError:
        return any(marker in lowered for marker in SKILL_LOAD_LOG_MARKERS)
    if not isinstance(value, dict):
        return False
    key_text = " ".join(str(key).lower() for key in value)
    event_text = " ".join(
        str(value.get(key) or "").lower()
        for key in ("event", "type", "kind", "name", "message")
    )
    if "skill_path" in key_text or "skill_file" in key_text:
        return True
    return any(
        marker in event_text
        for marker in {"skill_load", "skill load", "loaded skill", "loading skill", "skill.injected"}
    )


def parse_actual_skill(text, last, expected):
    combined = "\n".join(line for line in str(text or "").splitlines() if looks_like_skill_load_line(line))
    hits = []
    for match in re.finditer(r"/skills/([A-Za-z0-9_-]+)/SKILL\.md", combined):
        skill = match.group(1)
        if skill in PUBLIC_SKILL_ROUTES:
            hits.append(skill)
    for match in re.finditer(r"groundwork:([A-Za-z0-9_-]+)", combined):
        skill = match.group(1)
        if skill in PUBLIC_SKILL_ROUTES:
            hits.append(skill)

    hits = unique_in_order(hits)
    if expected != "direct" and expected in hits:
        return expected, sorted(hits)
    if hits:
        return hits[0], sorted(hits)
    return UNKNOWN_ROUTE, []


def route_evidence_source(parsed_actual, skill_hits):
    if skill_hits:
        return "skill_hit"
    if parsed_actual != UNKNOWN_ROUTE:
        return "authoritative_runtime_trace"
    return "unknown"


def response_shape_evidence_source(candidate, final_response):
    if candidate == UNKNOWN_ROUTE:
        return "unknown"
    if candidate == "dispatch" and has_dispatch_route_marker(final_response):
        return "output_marker"
    if candidate == HOST_PREEMPTION_ROUTE:
        return "host_preemption_shape"
    return "response_shape"


def dispatch_hit_level(expected, acceptable_routes, actual, response_shape_candidate, skill_hits):
    dispatch_relevant = (
        expected == "dispatch"
        or "dispatch" in acceptable_routes
        or actual == "dispatch"
        or response_shape_candidate == "dispatch"
    )
    if "dispatch" in skill_hits:
        return "skill_loaded"
    if response_shape_candidate == "dispatch":
        return "output_shape_only"
    if dispatch_relevant:
        return "missed"
    return "not_applicable"


def has_host_preemption_intent(row):
    risk_gate = str(row.get("risk_gate") or "").strip()
    intent_kind = str(row.get("intent_kind") or "").strip()
    return (
        boolish(row.get("risky_write_requested"))
        or risk_gate in HOST_PREEMPTION_RISK_GATES
        or intent_kind in HOST_PREEMPTION_INTENT_KINDS
    )


def has_no_execution_gate_shape(text):
    if not all(field in text for field in GATE_FIELDS):
        return False
    lowered = text.lower()
    return any(marker in lowered or marker in text for marker in NO_EXECUTION_GATE_MARKERS)


def has_no_execution_gate_equivalent(text):
    lowered = text.lower()
    if not any(marker in lowered or marker in text for marker in NO_EXECUTION_GATE_MARKERS):
        return False

    equivalent_markers = [
        "approval",
        "approve",
        "risk",
        "rollback",
        "target",
        "permission",
        "blocked",
        "approval needed",
        "not a git repository",
        "remote",
        "issue",
        "git",
        "fatal",
        "source truth",
        "execution topology",
        "customer-visible",
        "risk gate",
        "recommended minimum path",
        "审批",
        "批准",
        "风险",
        "回滚",
        "目标",
        "授权",
        "阻塞",
        "远程",
        "仓库",
        "失败",
    ]
    return sum(1 for marker in equivalent_markers if marker in lowered or marker in text) >= 2


def has_direct_runtime_gate_equivalent(row, actual, text):
    return (
        actual in {DIRECT_ROUTE, HOST_PREEMPTION_ROUTE}
        and not boolish(row.get("skill_load_required", True))
        and host_preemption_allowed(row)
        and has_host_preemption_intent(row)
        and has_no_execution_gate_equivalent(text)
    )


def has_customer_visible_triage_gate_equivalent(row, actual, text):
    if actual != "triage" or str(row.get("risk_gate") or "").strip() != "customer_visible":
        return False

    lowered = text.lower()
    risk_markers = ["risk", "customer-visible", "customer visible", "风险", "客户可见"]
    triage_markers = ["triage verdict", "state:", "ready-for-human", "needs-info", "hitl"]
    source_gap_markers = ["source truth", "目标文件", "旧文案", "新文案", "缺少", "blockers"]
    no_execution_markers = [
        "no file changes",
        "not modified",
        "未修改文件",
        "未修改任何文件",
        "本轮未修改文件",
        "没有改文件",
        "不能做编辑",
        "不能安全进入代码修改",
        "不能落文件",
    ]
    next_action_markers = ["next action", "下一步", "请给我", "最小需要", "拿到这"]

    return (
        any(marker in lowered or marker in text for marker in risk_markers)
        and any(marker in lowered for marker in triage_markers)
        and any(marker in lowered or marker in text for marker in source_gap_markers)
        and any(marker in lowered or marker in text for marker in no_execution_markers)
        and any(marker in lowered or marker in text for marker in next_action_markers)
    )


def has_gate_fields_or_direct_runtime_equivalent(row, actual, text):
    return (
        not missing_required_fields(text, GATE_FIELDS)
        or has_direct_runtime_gate_equivalent(row, actual, text)
        or has_customer_visible_triage_gate_equivalent(row, actual, text)
    )


def has_dispatch_route_marker(text):
    return shared_has_dispatch_route_marker(text)


def has_blocked_implementation_conformance(text):
    lowered = text.lower()
    blocked_markers = [
        "blocked",
        "stop before",
        "pre-write gate",
        "preflight",
        "execution topology: blocked",
        "不能进入实现",
        "不能进入修改",
        "不能实际",
        "不能安全直接改文件",
        "不能确认",
        "没有可实现",
        "不能凭空",
        "没有可测试代码",
        "没有写权限",
        "没有做文件修改",
        "缺少 source truth",
        "无法",
        "暂不能",
        "没有改文件",
        "未修改文件",
        "没有修改文件",
        "停在",
    ]
    evidence_markers = [
        "evidence inspected",
        "checks run",
        "git topology",
        "git gate",
        "not a git repository",
        "source truth",
        "readme.md",
        "测试说明",
        "只读检查",
        "git 仓库",
        "源码",
        "证据",
    ]
    boundary_markers = [
        "scope",
        "risk",
        "next action",
        "approval needed",
        "proposed action",
        "result",
        "rollback/undo",
        "下一步",
        "风险",
        "结论",
        "缺口",
        "剩余缺口",
    ]
    return (
        any(marker in lowered for marker in blocked_markers)
        and sum(1 for marker in evidence_markers if marker in lowered) >= 2
        and any(marker in lowered for marker in boundary_markers)
    )


def has_compact_implementation_result(text):
    lowered = text.lower()
    outcome_markers = [
        "outcome",
        "result",
        "implemented",
        "completed",
        "blocked",
        "结果",
        "结论",
        "已完成",
        "已修改",
        "阻塞",
    ]
    file_markers = [
        "files changed",
        "changed files",
        "no file changes",
        "not modified",
        "文件修改",
        "修改文件",
        "改动文件",
        "未修改文件",
        "没有改文件",
    ]
    check_markers = [
        "checks run",
        "tests run",
        "test result",
        "not run",
        "unverified",
        "检查",
        "测试",
        "验证",
        "未运行",
        "未验证",
    ]
    risk_markers = [
        "remaining risk",
        "residual risk",
        "skipped verification",
        "unverified",
        "no remaining",
        "风险",
        "缺口",
        "未验证",
        "未覆盖",
    ]
    return all(
        any(marker in lowered for marker in markers)
        for markers in (outcome_markers, file_markers, check_markers, risk_markers)
    )


def has_compact_implementation_conformance(text):
    lowered = text.lower()
    finding_markers = ["finding", "p0", "p1", "p2", "发现", "问题", "符合", "不符合"]
    evidence_markers = ["evidence", "inspected", "source", "test", "证据", "源码", "测试", "检查"]
    gap_markers = ["gap", "missing", "unverified", "缺口", "缺失", "未验证", "未覆盖"]
    boundary_markers = [
        "non-readiness",
        "not readiness",
        "does not prove",
        "not a uat",
        "not release",
        "不代表 ready",
        "不构成 ready",
        "不判断 ready",
        "不判断 uat",
        "不证明发布",
        "非就绪",
    ]
    return all(
        any(marker in lowered for marker in markers)
        for markers in (finding_markers, evidence_markers, gap_markers, boundary_markers)
    )


def has_host_preemption_response_shape(row, final_response, changes):
    if boolish(row.get("skill_load_required", True)):
        return False
    if not host_preemption_allowed(row):
        return False
    if not has_host_preemption_intent(row):
        return False
    if changes:
        return False
    return has_no_execution_gate_shape(final_response)


def has_requirement_state_gate_response_shape(row, final_response, changes):
    if expected_skill_for_row(row) != "to-prd":
        return False
    if "to-prd" not in acceptable_routes_for_row(row):
        return False
    if "implement" not in parse_pipe_list(row.get("forbidden_routes"), "forbidden_routes", row, blank_default=[]):
        return False
    if str(row.get("intent_kind") or "").strip() not in {"new_requirement", "workflow_change"}:
        return False
    if str(row.get("requirement_state") or "").strip() not in {"raw", "prd_draft"}:
        return False
    if changes:
        return False
    return has_blocked_implementation_conformance(final_response)


def is_direct_negative_plain_answer(row, final_response, changes):
    if expected_skill_for_row(row) != DIRECT_ROUTE:
        return False
    if str(row.get("route_boundary") or "").strip() != "direct-negative":
        return False
    if changes:
        return False
    if direct_fallback_ceremony_present(final_response):
        return False
    first = first_nonempty_line(str(final_response or ""))
    structured_workflow_headings = (
        "Verification Scope",
        "Implementation Summary",
        "Blocked Implementation",
        "Triage Verdict",
        "Dispatch Summary",
        "Dispatch Package",
        "Issue Map",
        "Issue Draft",
        "# PRD",
        "# Compact PRD",
        "Recommended route:",
        "Route:",
        "Expected route:",
        "Owner:",
    )
    return not any(first.startswith(marker) for marker in structured_workflow_headings)


def classify_response_shape_candidate(
    row,
    final_response_or_legacy_actual,
    changes_or_legacy_hits=None,
    legacy_final_response=None,
    legacy_changes=None,
):
    """Classify output shape without promoting it to runtime route evidence.

    The legacy positional form remains accepted while evaluator callers migrate;
    legacy actual-route and hit arguments are intentionally ignored.
    """
    if legacy_final_response is None:
        final_response = final_response_or_legacy_actual
        changes = changes_or_legacy_hits or []
    else:
        final_response = legacy_final_response
        changes = legacy_changes or []
    if has_host_preemption_response_shape(row, final_response, changes):
        return HOST_PREEMPTION_ROUTE
    if has_requirement_state_gate_response_shape(row, final_response, changes):
        return "to-prd"
    if expected_skill_for_row(row) == "dispatch" and has_dispatch_route_marker(final_response):
        return "dispatch"

    if is_direct_negative_plain_answer(row, final_response, changes):
        return DIRECT_ROUTE

    detected_route, _source = detect_route_from_text(final_response)
    if detected_route != DIRECT_ROUTE:
        return detected_route

    if not host_preemption_allowed(row):
        return DIRECT_ROUTE
    if not has_host_preemption_intent(row):
        return DIRECT_ROUTE
    if changes:
        return DIRECT_ROUTE
    if not has_no_execution_gate_shape(final_response):
        return DIRECT_ROUTE

    return HOST_PREEMPTION_ROUTE


def acceptable_routes_for_row(row):
    return parse_pipe_list(
        row.get("acceptable_routes"),
        "acceptable_routes",
        row,
        blank_default=[expected_skill_for_row(row)],
    )


DIRECT_FALLBACK_CEREMONY_MARKERS = [
    "# PRD",
    "Artifact Type: PRD",
    "issue pack",
    "Issue Map",
    "issue-map",
    "Implementation Mini-Plan",
    "Lifecycle Preflight",
    "STATE.md",
    "ROADMAP.md",
    "需求文档",
    "拆 issues",
    "实现计划",
]
IMPLEMENTATION_READY_ROUTES = {"implement", "write-plan", "to-issues"}


def first_nonempty_line(text):
    return next((line.strip() for line in text.splitlines() if line.strip()), "")


def direct_fallback_ceremony_present(text):
    lowered = text.lower()
    for marker in DIRECT_FALLBACK_CEREMONY_MARKERS:
        if marker.lower() in lowered:
            return True
    return False


def has_prototype_contract_boundary(text):
    lowered = text.lower()
    prototype_markers = ["prototype", "throwaway", "原型", "静态 html", "一次性", "临时"]
    boundary_markers = ["contract", "source truth", "mock", "unverified", "合同", "契约", "真实接口", "未验证"]
    return any(marker in lowered for marker in prototype_markers) and any(
        marker in lowered for marker in boundary_markers
    )


UNVERIFIED_EVIDENCE_MARKERS = (
    "not run",
    "never run",
    "not covered",
    "not provided",
    "unverified",
    "unknown",
    "missing",
    "blocked",
    "no runtime",
    "without runtime",
    "cannot count",
    "cannot prove",
    "does not prove",
    "insufficient",
    "无法运行",
    "无法验证",
    "从未运行",
    "未运行",
    "未验证",
    "未覆盖",
    "未提供",
    "未知",
    "缺少",
    "不可验证",
    "无可运行",
    "不能证明",
    "不能作为",
    "不足以",
)


def _has_unverified_evidence_marker(clause):
    lowered = str(clause or "").lower()
    # Positive statements such as "no tests failed" and explicit negations
    # must not be promoted into an unverified-evidence boundary.
    negative_evidence_marker = (
        r"(?:missing|unverified|unknown|blocked|insufficient)"
    )
    negative_evidence_qualifier = (
        r"(?:(?:currently|actually|still|presently|explicitly)\s+)*"
    )
    lowered = re.sub(
        r"\b(?:not|never)\s+run(?:ning)?\s+"
        r"(?:in\s+(?:parallel|serial)|concurrently|serially|slowly|quickly)\b",
        " ",
        lowered,
    )
    lowered = re.sub(
        rf"\bneither\b[^;.!?]{{0,64}}\bnor\s+"
        rf"(?:(?:is|are|was|were)\s+)?"
        rf"{negative_evidence_qualifier}{negative_evidence_marker}\b",
        " ",
        lowered,
    )
    lowered = re.sub(
        rf"\b(?:not|never)\s+"
        rf"(?:(?:considered|deemed|classified|regarded|treated)"
        rf"(?:\s+as)?\s+){negative_evidence_qualifier}"
        rf"{negative_evidence_marker}"
        rf"(?:\s+(?:or|nor)\s+{negative_evidence_qualifier}"
        rf"{negative_evidence_marker})*\b",
        " ",
        lowered,
    )
    lowered = re.sub(
        rf"\b(?:not|never)\s+{negative_evidence_qualifier}"
        rf"{negative_evidence_marker}"
        rf"(?:\s*,\s*{negative_evidence_qualifier}"
        rf"{negative_evidence_marker})*"
        rf"\s*,?\s*(?:or|nor)\s+{negative_evidence_qualifier}"
        rf"{negative_evidence_marker}\b",
        " ",
        lowered,
    )
    lowered = re.sub(
        rf"\bno\s+{negative_evidence_qualifier}"
        rf"{negative_evidence_marker}"
        rf"(?:\s+[a-z0-9_-]+)?"
        rf"(?:\s+(?:or|nor)\s+{negative_evidence_qualifier}"
        rf"{negative_evidence_marker}"
        rf"(?:\s+[a-z0-9_-]+)?)+\b",
        " ",
        lowered,
    )
    lowered = re.sub(
        rf"\b(?:isn['’]t|aren['’]t|wasn['’]t|weren['’]t)\s+"
        rf"{negative_evidence_qualifier}{negative_evidence_marker}"
        rf"(?:\s+(?:or|nor)\s+{negative_evidence_qualifier}"
        rf"{negative_evidence_marker})*\b",
        " ",
        lowered,
    )
    lowered = re.sub(
        r"\bno\s+tests?\s+(?:(?:are|had|has|have|were)\s+)?"
        r"(?:failed|failing|failures?|errored|errors?)\b",
        " ",
        lowered,
    )
    lowered = re.sub(
        r"\b(?:no(?:\s+longer)?|not|never|without)\s+"
        r"(?:(?:currently|actually|still)\s+)?"
        r"(?:missing|unverified|unknown|blocked|insufficient)\b",
        " ",
        lowered,
    )
    lowered = re.sub(
        r"\b(?:no|neither|nothing)\s+"
        r"(?:[a-z0-9_-]+\s+){0,4}"
        r"(?:is|are|remains?|was|were)\s+"
        r"(?:missing|unverified|unknown|blocked|insufficient)"
        r"(?:\s+(?:or|nor)\s+"
        r"(?:(?:currently|actually|still|presently|explicitly)\s+)?"
        r"(?:missing|unverified|unknown|blocked|insufficient))*\b",
        " ",
        lowered,
    )
    lowered = re.sub(
        r"\b(?:no|nothing)\s+(?:[a-z0-9_-]+\s+){0,3}"
        r"(?:missing|unverified|unknown|blocked|insufficient)\b",
        " ",
        lowered,
    )
    lowered = re.sub(
        r"\bneither\s+(?:missing|unverified|unknown|blocked|insufficient)"
        r"\s+nor\s+(?:missing|unverified|unknown|blocked|insufficient)\b",
        " ",
        lowered,
    )
    chinese_positive_patterns = (
        r"没有测试(?:失败|报错|错误)",
        r"(?:并不|并非|并未|不是|不再)(?:存在)?"
        r"(?:缺少|缺失|未验证|未知|阻塞|不足)",
        r"(?:绝非|绝不是)(?:存在|处于|属于|被视为)?"
        r"(?:缺少|缺失|未验证|未知|阻塞|不足)(?:状态|项|内容|证据)?",
        r"没有(?:处于|属于|被视为)"
        r"(?:缺少|缺失|未验证|未知|阻塞|不足)(?:状态|项|内容|证据)?",
        r"没有被(?:标记|视为|认为|判定)为"
        r"(?:缺少|缺失|未验证|未知|阻塞|不足)(?:状态|项|内容|证据)?",
        r"不(?:缺少|缺失|未验证|未知|阻塞|不足)"
        r"(?:，|,)?(?:也)?不(?:处于|属于|被视为)?"
        r"(?:缺少|缺失|未验证|未知|阻塞|不足)(?:状态|项|内容|证据)?",
        r"(?:不存在|并无)(?:任何)?"
        r"(?:缺少|缺失|未验证|未知|阻塞|不足)"
        r"(?:或(?:缺少|缺失|未验证|未知|阻塞|不足))*"
        r"(?:项|内容|证据|状态)?",
        r"没有(?:任何)?(?:缺少|缺失|未验证|未知|阻塞|不足)"
        r"(?:项|内容|证据)?",
    )
    original = str(clause or "")
    for pattern in chinese_positive_patterns:
        lowered = re.sub(pattern, " ", lowered)
        original = re.sub(pattern, " ", original)
    if any(
        marker in lowered
        or (
            not re.fullmatch(r"[a-z0-9_ ]+", marker)
            and marker in original
        )
        for marker in UNVERIFIED_EVIDENCE_MARKERS
    ):
        return True
    return bool(
        re.search(
            r"\bno\s+tests?\b(?!\s+(?:(?:are|had|has|have|were)\s+)?"
            r"(?:failed|failing|failures?|errored|errors?)\b)",
            lowered,
        )
        or re.search(r"没有测试(?!失败|报错|错误)", original)
    )


def has_scoped_unverified_boundary(text, domain_markers):
    def marker_present(marker, lowered_line, original_line):
        if re.fullmatch(r"[a-z0-9_]+", marker):
            return bool(re.search(rf"\b{re.escape(marker)}\b", lowered_line))
        return marker in lowered_line or marker in original_line

    all_domain_markers = (
        "source truth",
        "source evidence",
        "source",
        "canonical",
        "源码",
        "源真相",
        "test",
        "tests",
        "check",
        "checks",
        "测试",
        "自测",
        "验证命令",
        "browser",
        "ui evidence",
        "runtime / browser",
        "浏览器",
        "截图",
        "录屏",
        "前端",
        "ui",
        "runtime",
        "runtime evidence",
        "codex exec",
        "run_runtime",
        "运行时",
        "运行证据",
        "运行结果",
        "执行证据",
        "执行结果",
    )
    current_domain_markers = tuple(domain_markers)
    other_domain_markers = tuple(
        marker
        for marker in all_domain_markers
        if marker not in current_domain_markers
    )
    for line in str(text or "").splitlines():
        domain_scope_active = False
        for clause in re.split(r"[;.!?。；！？]+", line):
            lowered = clause.lower()
            has_current_domain = any(
                marker_present(marker, lowered, clause)
                for marker in current_domain_markers
            )
            has_other_domain = any(
                marker_present(marker, lowered, clause)
                for marker in other_domain_markers
            )
            if has_current_domain:
                domain_scope_active = True
            elif has_other_domain:
                domain_scope_active = False
            if domain_scope_active and _has_unverified_evidence_marker(clause):
                return True
    return False


def has_source_or_unverified_evidence(text):
    return has_scoped_unverified_boundary(
        text,
        ("source truth", "source evidence", "source", "canonical", "源码", "源真相"),
    )


def has_tests_or_unverified_evidence(text):
    return has_scoped_unverified_boundary(
        text,
        ("test", "tests", "check", "checks", "测试", "自测", "验证命令"),
    )


def has_browser_or_unverified_evidence(text):
    return has_scoped_unverified_boundary(
        text,
        ("browser", "ui evidence", "runtime / browser", "浏览器", "截图", "录屏", "前端", "ui"),
    )


def has_runtime_or_unverified_evidence(text):
    return has_scoped_unverified_boundary(
        text,
        (
            "runtime",
            "runtime evidence",
            "codex exec",
            "run_runtime",
            "运行时",
            "运行证据",
            "运行结果",
            "执行证据",
            "执行结果",
        ),
    )


def append_failure(failures, notes, failure_type, fix_locus, note):
    failures.append((failure_type, fix_locus))
    notes.append(note)


DISPATCH_COMPACT_MAX_CHARACTERS = 2_800
DISPATCH_COMPACT_MAX_NONEMPTY_LINES = 26
DISPATCH_DEFAULT_REQUIRED_MARKERS = (
    "dispatch_version:",
    "adapter_completeness:",
    "source:",
    "tasks:",
    "policy:",
    "required_evidence:",
    "stop_when:",
)
DISPATCH_DEFAULT_ALLOWED_REFERENCE_FILES = {"SKILL.md", "DISPATCH-PACKAGE.md"}


def dispatch_visible_output_metrics(text):
    return {
        "characters": len(text),
        "nonempty_lines": sum(bool(line.strip()) for line in text.splitlines()),
    }


def dispatch_package_is_complete(text):
    lowered = text.lower()
    if re.search(r"(^|\s)(?:\.\.\.|…)(?:\s|$)", text):
        return False
    return all(marker in lowered for marker in DISPATCH_DEFAULT_REQUIRED_MARKERS)


def dispatch_starts_at_package(text):
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return bool(lines) and lines[0] == "dispatch_version: 2"


def dispatch_has_explicit_split(text):
    lowered = text.lower()
    return dispatch_starts_at_package(text) and "needs_split" in lowered and any(
        marker in lowered for marker in ("next_action", "next action", "下一步")
    )


def completed_command_execution_commands(stdout):
    return [
        activity["command"]
        for activity in completed_tool_activities(stdout)
        if activity["kind"] == "command_execution"
    ]


def _activity_result_field(payload):
    for field in ("result", "output", "content"):
        if field in payload and payload[field] is not None:
            return field, payload[field]
    return "", None


SUCCESS_ACTIVITY_STATUSES = {"completed", "ok", "success", "succeeded"}


def _activity_succeeded(payload):
    status = str(payload.get("status") or "").lower()
    return (
        not payload.get("error")
        and status in SUCCESS_ACTIVITY_STATUSES
    )


def completed_tool_activities(stdout):
    activities = []
    for line in str(stdout or "").splitlines():
        try:
            payload = json.loads(line)
        except json.JSONDecodeError:
            continue
        payload_type = str(payload.get("type") or "")
        item = payload.get("item")
        if payload_type == "item.completed" and isinstance(item, dict):
            item_type = str(item.get("type") or "")
            if item_type in {"agent_message", "reasoning"}:
                continue
            if item_type == "command_execution":
                command = item.get("command")
                if isinstance(command, str):
                    exit_code = item.get("exit_code")
                    valid_exit_code = type(exit_code) is int
                    status = str(item.get("status") or "").lower()
                    output = str(
                        item.get("aggregated_output")
                        or item.get("output")
                        or ""
                    )
                    activities.append(
                        {
                            "kind": "command_execution",
                            "command": command,
                            "cwd": str(item.get("cwd") or ""),
                            "server": "",
                            "tool": "",
                            "detail": json.dumps(
                                item, ensure_ascii=False, sort_keys=True
                            ),
                            "output": output,
                            "has_result": valid_exit_code,
                            "succeeded": (
                                valid_exit_code
                                and exit_code == 0
                                and status in SUCCESS_ACTIVITY_STATUSES
                            ),
                        }
                    )
                continue
            result_field, result_value = _activity_result_field(item)
            activities.append(
                {
                    "kind": item_type or "tool_activity",
                    "command": "",
                    "server": str(item.get("server") or ""),
                    "tool": str(
                        item.get("tool")
                        or item.get("tool_name")
                        or item.get("name")
                        or ""
                    ),
                    "detail": json.dumps(item, ensure_ascii=False, sort_keys=True),
                    "output": (
                        json.dumps(result_value, ensure_ascii=False)
                        if isinstance(result_value, (dict, list))
                        else str(result_value)
                        if result_field
                        else ""
                    ),
                    "has_result": bool(result_field),
                    "succeeded": _activity_succeeded(item),
                }
            )
        elif payload_type == "tool_call":
            result_field, result_value = _activity_result_field(payload)
            activities.append(
                {
                    "kind": str(payload.get("tool_name") or "tool_call"),
                    "command": "",
                    "server": str(payload.get("server") or ""),
                    "tool": str(payload.get("tool_name") or ""),
                    "detail": json.dumps(
                        payload, ensure_ascii=False, sort_keys=True
                    ),
                    "output": (
                        json.dumps(result_value, ensure_ascii=False)
                        if isinstance(result_value, (dict, list))
                        else str(result_value)
                        if result_field
                        else ""
                    ),
                    "has_result": bool(result_field),
                    "succeeded": _activity_succeeded(payload),
                }
            )
    return activities


def _shell_tokens(command):
    try:
        lexer = shlex.shlex(
            str(command or ""),
            posix=True,
            punctuation_chars=";&|",
        )
        lexer.whitespace_split = True
        lexer.commenters = ""
        return list(lexer)
    except ValueError:
        return []


def _command_segments(tokens):
    segments = []
    current = []
    for token in tokens:
        if token in {";", "&&", "||", "|", "&"}:
            if current:
                segments.append(current)
                current = []
            continue
        current.append(token)
    if current:
        segments.append(current)
    return segments


def _is_unattributable_shell_operator(token):
    return bool(re.fullmatch(r"[;&|]+", str(token or ""))) and token != "&&"


def _shell_command_argument(tokens):
    if not tokens:
        return None
    executable = Path(tokens[0]).name.lower()
    if executable not in {"sh", "bash", "zsh", "dash"}:
        return None
    for index, token in enumerate(tokens[1:], start=1):
        if token in {"-l", "--login"}:
            continue
        if token == "-c":
            return tokens[index + 1] if index + 1 < len(tokens) else ""
        if (
            re.fullmatch(r"-[cl]+", token)
            and token.count("c") == 1
        ):
            return tokens[index + 1] if index + 1 < len(tokens) else ""
        return None
    return None


def _consume_option_prefix(
    tokens,
    *,
    value_options=(),
    attached_value_prefixes=(),
    stop_options=(),
):
    remaining = list(tokens)
    value_options = set(value_options)
    stop_options = set(stop_options)
    while remaining:
        token = remaining[0]
        if token == "--":
            return remaining[1:]
        if token in stop_options:
            return []
        if token in value_options:
            if len(remaining) < 2:
                return []
            remaining = remaining[2:]
            continue
        if any(
            token.startswith(option + "=")
            for option in value_options
            if option.startswith("--")
        ):
            remaining = remaining[1:]
            continue
        if any(
            token.startswith(prefix) and token != prefix
            for prefix in attached_value_prefixes
        ):
            remaining = remaining[1:]
            continue
        if token.startswith("-"):
            remaining = remaining[1:]
            continue
        break
    return remaining


def _unwrap_env_tokens(tokens):
    remaining = list(tokens[1:])
    while remaining:
        token = remaining[0]
        if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*=.*", token):
            remaining.pop(0)
            continue
        updated = _consume_option_prefix(
            remaining,
            value_options={
                "-C",
                "--chdir",
                "-u",
                "--unset",
                "-S",
                "--split-string",
            },
            attached_value_prefixes=("-C", "-u", "-S"),
        )
        if updated == remaining:
            break
        remaining = updated
    return remaining


def _env_wrapper_is_supported(tokens):
    remaining = list(tokens[1:])
    while remaining:
        token = remaining[0]
        if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*=.*", token):
            remaining.pop(0)
            continue
        if token == "--":
            return len(remaining) > 1
        if token in {"-i", "--ignore-environment"}:
            remaining.pop(0)
            continue
        if token in {"-u", "--unset"}:
            if len(remaining) < 2:
                return False
            remaining = remaining[2:]
            continue
        if token.startswith("--unset=") or (
            token.startswith("-u") and token != "-u"
        ):
            remaining.pop(0)
            continue
        if token.startswith("-"):
            return False
        return True
    return False


def _environment_provenance(value=None):
    value = value or {}
    return {
        "ignore_environment": bool(value.get("ignore_environment")),
        "unset_variables": {
            str(name).upper()
            for name in value.get("unset_variables") or set()
        },
    }


def _env_bindings(tokens, inherited=None, inherited_provenance=None):
    bindings = dict(inherited or {})
    provenance = _environment_provenance(inherited_provenance)
    remaining = list(tokens[1:])
    value_options = {
        "-C",
        "--chdir",
        "-S",
        "--split-string",
    }
    while remaining:
        token = remaining[0]
        if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*=.*", token):
            name, value = token.split("=", 1)
            bindings[name] = value
            remaining.pop(0)
            continue
        if token in {"-i", "--ignore-environment"}:
            bindings.clear()
            provenance["ignore_environment"] = True
            remaining.pop(0)
            continue
        if token in {"-u", "--unset"}:
            if len(remaining) < 2:
                break
            variable = remaining[1]
            bindings.pop(variable, None)
            provenance["unset_variables"].add(variable.upper())
            remaining = remaining[2:]
            continue
        if token.startswith("--unset="):
            variable = token.split("=", 1)[1]
            bindings.pop(variable, None)
            provenance["unset_variables"].add(variable.upper())
            remaining.pop(0)
            continue
        if token.startswith("-u") and token != "-u":
            variable = token[2:]
            bindings.pop(variable, None)
            provenance["unset_variables"].add(variable.upper())
            remaining.pop(0)
            continue
        if token == "--":
            remaining.pop(0)
            continue
        if token in value_options:
            if len(remaining) < 2:
                break
            remaining = remaining[2:]
            continue
        if any(
            token.startswith(option + "=")
            for option in value_options
            if option.startswith("--")
        ) or any(
            token.startswith(prefix) and token != prefix
            for prefix in ("-C", "-u", "-S")
        ):
            remaining.pop(0)
            continue
        if token.startswith("-"):
            remaining.pop(0)
            continue
        break
    return bindings, provenance


def _unwrap_npx_tokens(
    tokens,
    environment=None,
    command_wrappers=None,
    environment_provenance=None,
):
    remaining = list(tokens[1:])
    option_override = False
    package_override = any(
        token in {"--package", "-p"}
        or token.startswith("--package=")
        or (token.startswith("-p") and token != "-p")
        for token in remaining
    )

    def with_npx_provenance(invocations, *, call_mode=False):
        marked = []
        for invocation in invocations:
            invocation = dict(invocation)
            invocation["npx_wrapper"] = {
                "raw_executable": tokens[0],
                "package_override": package_override,
                "call_mode": call_mode,
                "option_override": option_override,
            }
            marked.append(invocation)
        return marked

    while remaining:
        token = remaining[0]
        if token in {"-c", "--call"}:
            if len(remaining) < 2:
                return []
            return with_npx_provenance(
                [
                    invocation
                    for nested in _command_segments(_shell_tokens(remaining[1]))
                    for invocation in _unwrap_command_segment(
                        nested,
                        environment=environment,
                        command_wrappers=command_wrappers,
                        environment_provenance=environment_provenance,
                    )
                ],
                call_mode=True,
            )
        if token.startswith("--call="):
            nested_command = token.split("=", 1)[1]
            return with_npx_provenance(
                [
                    invocation
                    for nested in _command_segments(_shell_tokens(nested_command))
                    for invocation in _unwrap_command_segment(
                        nested,
                        environment=environment,
                        command_wrappers=command_wrappers,
                        environment_provenance=environment_provenance,
                    )
                ],
                call_mode=True,
            )
        updated = _consume_option_prefix(
            remaining,
            value_options={"--package", "-p", "--shell"},
            attached_value_prefixes=("-p",),
            stop_options={"--help", "-h", "--version", "-v"},
        )
        if updated == remaining:
            break
        option_override = True
        remaining = updated
    return with_npx_provenance(
        _unwrap_command_segment(
            remaining,
            environment=environment,
            command_wrappers=command_wrappers,
            environment_provenance=environment_provenance,
        )
    )


def _npx_call_payload(tokens):
    remaining = list(tokens[1:])
    while remaining:
        token = remaining[0]
        if token in {"-c", "--call"}:
            return remaining[1] if len(remaining) > 1 else ""
        if token.startswith("--call="):
            return token.split("=", 1)[1]
        updated = _consume_option_prefix(
            remaining,
            value_options={"--package", "-p", "--shell"},
            attached_value_prefixes=("-p",),
            stop_options={"--help", "-h", "--version", "-v"},
        )
        if updated == remaining:
            return None
        remaining = updated
    return None


def command_success_is_attributable(command):
    raw_command = str(command or "")
    if "\n" in raw_command or "\r" in raw_command:
        return False
    if re.search(r"(?:<<<|<<|>>|<\(|>\(|\$\(|`|[<>])", raw_command):
        return False
    tokens = _shell_tokens(command)
    if not tokens or any(
        _is_unattributable_shell_operator(token) or token == "!"
        for token in tokens
    ):
        return False
    for segment in _command_segments(tokens):
        normalized = list(segment)
        while True:
            while normalized and re.fullmatch(
                r"[A-Za-z_][A-Za-z0-9_]*=.*", normalized[0]
            ):
                normalized.pop(0)
            if not normalized:
                return False
            executable = Path(normalized[0]).name.lower()
            if executable == "env":
                if not _env_wrapper_is_supported(normalized):
                    return False
                normalized = _unwrap_env_tokens(normalized)
                continue
            if executable in {"command", "builtin", "exec", "nohup"}:
                normalized = normalized[1:]
                if normalized and normalized[0] == "--":
                    normalized = normalized[1:]
                continue
            break
        if not normalized:
            return False
        if Path(normalized[0]).name.lower() == "npx":
            call_payload = _npx_call_payload(normalized)
            if call_payload is not None and (
                not call_payload
                or not command_success_is_attributable(call_payload)
            ):
                return False
        nested_command = _shell_command_argument(normalized)
        if nested_command is not None and not command_success_is_attributable(
            nested_command
        ):
            return False
    return True


def _command_wrapper_invocation(tokens, environment):
    return {
        "executable": Path(tokens[0]).name.lower(),
        "raw_executable": tokens[0],
        "args": list(tokens[1:]),
        "environment": dict(environment or {}),
    }


def _unwrap_command_segment(
    segment,
    environment=None,
    command_wrappers=None,
    environment_provenance=None,
):
    tokens = list(segment)
    environment = dict(environment or {})
    command_wrappers = list(command_wrappers or [])
    environment_provenance = _environment_provenance(
        environment_provenance
    )
    while tokens and re.fullmatch(
        r"[A-Za-z_][A-Za-z0-9_]*=.*", tokens[0]
    ):
        name, value = tokens.pop(0).split("=", 1)
        environment[name] = value
    if not tokens:
        return []

    executable = Path(tokens[0]).name.lower()
    if executable == "env":
        if not _env_wrapper_is_supported(tokens):
            return []
        command_wrappers.append(
            _command_wrapper_invocation(tokens, environment)
        )
        environment, environment_provenance = _env_bindings(
            tokens,
            inherited=environment,
            inherited_provenance=environment_provenance,
        )
        return _unwrap_command_segment(
            _unwrap_env_tokens(tokens),
            environment=environment,
            command_wrappers=command_wrappers,
            environment_provenance=environment_provenance,
        )
    if executable in {"command", "builtin", "exec", "nohup"}:
        command_wrappers.append(
            _command_wrapper_invocation(tokens, environment)
        )
        remaining = tokens[1:]
        if remaining and remaining[0] == "--":
            remaining = remaining[1:]
        return _unwrap_command_segment(
            remaining,
            environment=environment,
            command_wrappers=command_wrappers,
            environment_provenance=environment_provenance,
        )
    if executable in {"sh", "bash", "zsh", "dash"}:
        nested_command = _shell_command_argument(tokens)
        if nested_command is not None:
            command_wrappers.append(
                _command_wrapper_invocation(tokens, environment)
            )
            return [
                invocation
                for nested in _command_segments(_shell_tokens(nested_command))
                for invocation in _unwrap_command_segment(
                    nested,
                    environment=environment,
                    command_wrappers=command_wrappers,
                    environment_provenance=environment_provenance,
                )
            ]
    if executable == "npx":
        return _unwrap_npx_tokens(
            tokens,
            environment=environment,
            command_wrappers=command_wrappers,
            environment_provenance=environment_provenance,
        )
    return [
        {
            "executable": executable,
            "raw_executable": tokens[0],
            "args": tokens[1:],
            "environment": environment,
            "command_wrappers": command_wrappers,
            "environment_provenance": environment_provenance,
        }
    ]


def command_invocations(command):
    return [
        invocation
        for segment in _command_segments(_shell_tokens(command))
        for invocation in _unwrap_command_segment(segment)
    ]


PYTHON_INTERPRETER_FLAG_OPTIONS = {
    "-B",
    "-d",
    "-E",
    "-i",
    "-I",
    "-P",
    "-q",
    "-R",
    "-s",
    "-S",
    "-u",
    "-x",
}
PYTHON_INTERPRETER_VALUE_OPTIONS = {
    "-W",
    "-X",
    "--check-hash-based-pycs",
}
PYTHON_INTERPRETER_CLUSTER_FLAGS = frozenset(
    "bBdEiIOPqRsSuvx"
)


def _python_execution_target(args):
    """Parse the Python interpreter prefix without mistaking option values for code."""
    tokens = [str(token) for token in args]
    index = 0
    positional_only = False
    while index < len(tokens):
        token = tokens[index]
        if not positional_only and token == "--":
            positional_only = True
            index += 1
            continue
        if not positional_only and token in {
            "--help",
            "--help-all",
            "--help-env",
            "--help-xoptions",
            "--version",
            "-?",
            "-h",
            "-V",
            "-VV",
        }:
            return None
        if not positional_only and token in {"-c", "-m"}:
            if index + 1 >= len(tokens):
                return None
            kind = "command" if token == "-c" else "module"
            return {
                "kind": kind,
                "target": tokens[index + 1],
                "args": tokens[index + 2 :],
            }
        if not positional_only and token.startswith(("-c", "-m")) and len(token) > 2:
            return {
                "kind": "command" if token.startswith("-c") else "module",
                "target": token[2:],
                "args": tokens[index + 1 :],
            }
        if not positional_only and token in PYTHON_INTERPRETER_VALUE_OPTIONS:
            if index + 1 >= len(tokens):
                return None
            index += 2
            continue
        if not positional_only and (
            (token.startswith("-W") and len(token) > 2)
            or (token.startswith("-X") and len(token) > 2)
        ):
            index += 1
            continue
        if not positional_only and (
            token in PYTHON_INTERPRETER_FLAG_OPTIONS
            or re.fullmatch(r"-(?:b+|O{1,2}|v+)", token)
            or (
                len(token) > 2
                and token.startswith("-")
                and set(token[1:]).issubset(
                    PYTHON_INTERPRETER_CLUSTER_FLAGS
                )
            )
        ):
            index += 1
            continue
        if not positional_only and token.startswith("-") and token != "-":
            return None
        return {
            "kind": "stdin" if token == "-" else "script",
            "target": token,
            "args": tokens[index + 1 :],
        }
    return None


def _python_module(args):
    target = _python_execution_target(args)
    if not target or target["kind"] != "module":
        return ""
    return str(target["target"]).lower()


def _python_script_and_args(args):
    target = _python_execution_target(args)
    if not target or target["kind"] != "script":
        return None
    return str(target["target"]), list(target["args"])


def _has_help_or_version(args):
    return any(
        token in {"--help", "-h", "--version", "-V"}
        for token in args
    )


def _git_subcommand(args):
    if _has_help_or_version(args):
        return ""
    remaining = _consume_option_prefix(
        args,
        value_options={
            "-C",
            "-c",
            "--git-dir",
            "--work-tree",
            "--namespace",
            "--super-prefix",
            "--config-env",
        },
        attached_value_prefixes=("-C", "-c"),
        stop_options={"--help", "-h", "--version", "-v"},
    )
    return remaining[0].lower() if remaining else ""


def _package_manager_positionals(args):
    if _has_help_or_version(args):
        return []
    remaining = _consume_option_prefix(
        args,
        value_options={
            "--prefix",
            "--cwd",
            "--dir",
            "-C",
            "--filter",
            "--workspace",
            "-w",
            "--project",
            "--config",
        },
        attached_value_prefixes=("-C", "-w"),
        stop_options={"--help", "-h", "--version", "-V"},
    )
    return [token.lower() for token in remaining if not token.startswith("-")]


def _codex_subcommand(args):
    if _has_help_or_version(args):
        return ""
    remaining = _consume_option_prefix(
        args,
        value_options={
            "-c",
            "--config",
            "-m",
            "--model",
            "-p",
            "--profile",
            "-C",
            "--cd",
        },
        attached_value_prefixes=("-c", "-m", "-p", "-C"),
        stop_options={"--help", "-h", "--version", "-V"},
    )
    return remaining[0].lower() if remaining else ""


def _first_non_option(args):
    return next((token for token in args if not token.startswith("-")), "")


def _is_source_invocation(invocation):
    executable = invocation["executable"]
    args = invocation["args"]
    if _has_help_or_version(args):
        return False
    if executable == "cat":
        return any(
            argument != "-" and not str(argument).startswith("-")
            for argument in args
        )
    if executable == "sed":
        positional = [
            argument for argument in args if not str(argument).startswith("-")
        ]
        return len(positional) >= 2
    if executable in {"head", "tail"}:
        return bool(args) and bool(str(args[-1]).strip()) and not str(
            args[-1]
        ).startswith(("-", "+")) and not str(args[-1]).isdigit()
    if executable == "grep":
        positional = [
            argument for argument in args if not str(argument).startswith("-")
        ]
        return len(positional) >= 2 or (
            any(
                argument in {"-e", "--regexp", "-f", "--file"}
                or str(argument).startswith(("--regexp=", "--file="))
                for argument in args
            )
            and bool(positional)
        )
    if executable == "rg":
        return bool(_first_non_option(args))
    if executable == "codegraph":
        positional = [
            argument for argument in args if not str(argument).startswith("-")
        ]
        return (
            len(positional) >= 2
            and positional[0].lower() == "explore"
        )
    if executable == "git":
        return _git_subcommand(args) in {"show", "diff", "grep", "log"}
    return False


def _is_git_status_invocation(invocation):
    return (
        invocation["executable"] == "git"
        and _git_subcommand(invocation["args"]) == "status"
    )


def _canonical_existing_directory(value):
    if value is None or str(value).strip() == "":
        return None
    path = Path(str(value))
    try:
        resolved = path.resolve(strict=True)
    except (OSError, RuntimeError):
        return None
    return resolved if resolved.is_dir() else None


def _git_status_workspace_override(args):
    if _has_help_or_version(args):
        return None, False
    override = None
    tokens = [str(token) for token in args]
    index = 0
    while index < len(tokens):
        token = tokens[index]
        if token == "status":
            return override, True
        if token == "-C":
            if override is not None or index + 1 >= len(tokens):
                return None, False
            override = tokens[index + 1]
            index += 2
            continue
        if token.startswith("-C") and token != "-C":
            if override is not None:
                return None, False
            override = token[2:]
            index += 1
            continue
        if token.startswith("-"):
            return None, False
        return None, False
    return None, False


def _git_status_activity_targets_workspace(activity, case_workspace):
    workspace = _canonical_existing_directory(case_workspace)
    if workspace is None:
        return False
    invocations = command_invocations(activity.get("command"))
    if len(invocations) != 1:
        return False
    invocation = invocations[0]
    if (
        not _is_git_status_invocation(invocation)
        or not _observed_invocation_uses_trusted_executable(invocation)
    ):
        return False
    override, valid = _git_status_workspace_override(invocation.get("args") or [])
    if not valid:
        return False
    event_cwd = _canonical_existing_directory(activity.get("cwd"))
    if override is None:
        return event_cwd == workspace
    override_path = Path(override)
    if not override_path.is_absolute():
        return False
    return _canonical_existing_directory(override_path) == workspace


TEST_NONEXECUTING_OPTIONS = {
    "--co",
    "--collect-only",
    "--dry-run",
    "--fixtures",
    "--fixtures-per-test",
    "--list",
    "--list-only",
    "--list-tests",
    "--listtests",
    "--markers",
    "--no-run",
    "--setup-only",
    "-list",
}


def _test_invocation_is_nonexecuting(invocation):
    executable = invocation["executable"]
    args = [str(argument) for argument in invocation.get("args") or []]
    lowered_args = [argument.casefold() for argument in args]
    if _has_help_or_version(args) or any(
        argument in TEST_NONEXECUTING_OPTIONS
        or any(
            argument.startswith(option + "=")
            for option in TEST_NONEXECUTING_OPTIONS
            if option.startswith("--")
        )
        for argument in lowered_args
    ):
        return True
    if executable in {"mvn", "mvnw"}:
        skip_properties = {
            "-dskiptests",
            "-dskiptests=true",
            "-dmaven.test.skip",
            "-dmaven.test.skip=true",
        }
        if any(argument in skip_properties for argument in lowered_args):
            return True
    if executable in {"gradle", "gradlew"}:
        for index, argument in enumerate(lowered_args):
            if argument in {"-x", "--exclude-task"}:
                if (
                    index + 1 < len(lowered_args)
                    and lowered_args[index + 1] == "test"
                ):
                    return True
            if argument in {"-xtest", "--exclude-task=test"}:
                return True
    return False


def _is_test_invocation(invocation):
    executable = invocation["executable"]
    args = invocation["args"]
    if _test_invocation_is_nonexecuting(invocation):
        return False
    if executable == "node":
        node_options = _node_test_option_prefix(args)
        return (
            node_options is not None
            and "--test" in node_options
            and _node_test_reporter_is_trusted(node_options)
        )
    return False


def _node_test_option_prefix(args):
    """Return only Node interpreter options before the script/eval target."""
    options = []
    index = 0
    options_with_separate_values = {
        "--test-concurrency",
        "--test-name-pattern",
        "--test-reporter",
        "--test-reporter-destination",
        "--test-shard",
        "--test-timeout",
    }
    options_without_values = {
        "--experimental-test-coverage",
        "--test",
        "--test-force-exit",
        "--test-only",
        "--test-update-snapshots",
    }
    options_with_inline_values = (
        "--test-concurrency=",
        "--test-coverage-branches=",
        "--test-coverage-exclude=",
        "--test-coverage-functions=",
        "--test-coverage-include=",
        "--test-coverage-lines=",
        "--test-isolation=",
        "--test-name-pattern=",
        "--test-reporter=",
        "--test-reporter-destination=",
        "--test-shard=",
        "--test-timeout=",
    )
    reporter_options = {
        "--test-reporter",
        "--test-reporter-destination",
    }
    while index < len(args):
        argument = str(args[index])
        if argument == "--":
            break
        if not argument.startswith("-") or argument == "-":
            break
        if (
            argument.startswith("--test-isolation=")
            and argument != "--test-isolation=process"
        ):
            return None
        if (
            argument not in options_without_values
            and argument not in options_with_separate_values
            and not argument.startswith(options_with_inline_values)
        ):
            return None
        options.append(argument)
        if argument in options_with_separate_values:
            if index + 1 >= len(args):
                return None
            if argument in reporter_options:
                options.append(str(args[index + 1]))
            index += 2
            continue
        index += 1
    return options


def _node_test_reporter_is_trusted(node_options):
    reporters = []
    destinations = []
    index = 0
    while index < len(node_options):
        argument = str(node_options[index])
        if argument == "--test-reporter":
            if index + 1 >= len(node_options):
                return False
            reporters.append(str(node_options[index + 1]).casefold())
            index += 2
            continue
        if argument.startswith("--test-reporter="):
            reporters.append(argument.split("=", 1)[1].casefold())
        elif argument == "--test-reporter-destination":
            if index + 1 >= len(node_options):
                return False
            destinations.append(str(node_options[index + 1]))
            index += 2
            continue
        elif argument.startswith("--test-reporter-destination="):
            destinations.append(argument.split("=", 1)[1])
        index += 1
    return (
        len(reporters) <= 1
        and not destinations
        and (not reporters or reporters[0] in {"spec", "tap"})
    )


def _is_browser_invocation(invocation):
    executable = invocation["executable"]
    args = invocation["args"]
    if _has_help_or_version(args):
        return False
    if executable == "playwright":
        positionals = _playwright_command_positionals(args)
        subcommand = positionals[0].lower() if positionals else ""
        if subcommand == "screenshot":
            return True
        if subcommand != "test":
            return False
        nonexecuting_options = {
            "--dry-run",
            "--list",
            "--list-only",
            "--pass-with-no-tests",
        }
        return not any(
            argument in nonexecuting_options
            or any(
                argument.startswith(option + "=")
                for option in nonexecuting_options
            )
            for argument in args
        )
    if executable in {
        "chromium",
        "chromium-browser",
        "google-chrome",
        "chrome-headless-shell",
    }:
        return any(
            token.startswith(("--headless", "--screenshot"))
            for token in args
        )
    return False


PLAYWRIGHT_TARGET_VALUE_OPTIONS = {
    "-b",
    "--browser",
    "--channel",
    "--color-scheme",
    "--device",
    "--geolocation",
    "--http-credentials",
    "--lang",
    "--load-storage",
    "--locale",
    "--proxy-bypass",
    "--proxy-server",
    "--save-har",
    "--save-storage",
    "--timeout",
    "--timezone",
    "--user-agent",
    "--viewport-size",
    "--wait-for-selector",
    "--wait-for-timeout",
}


def _playwright_command_positionals(args):
    positionals = []
    index = 0
    positional_only = False
    while index < len(args):
        argument = str(args[index])
        if positional_only:
            positionals.append(argument)
            index += 1
            continue
        if argument == "--":
            positional_only = True
            index += 1
            continue
        if argument in PLAYWRIGHT_TARGET_VALUE_OPTIONS:
            if index + 1 >= len(args):
                return []
            index += 2
            continue
        if any(
            argument.startswith(option + "=")
            for option in PLAYWRIGHT_TARGET_VALUE_OPTIONS
            if option.startswith("--")
        ) or (
            argument.startswith("-b")
            and argument != "-b"
        ):
            index += 1
            continue
        if argument.startswith("-"):
            index += 1
            continue
        positionals.append(argument)
        index += 1
    return positionals


def _playwright_test_output_is_noop(output):
    normalized = " ".join(str(output or "").casefold().split())
    if re.search(r"\b[1-9][0-9]*\s+passed\b", normalized) or re.search(
        r"\bpassed\s*:\s*[1-9][0-9]*\b", normalized
    ):
        return False
    return any(
        re.search(pattern, normalized)
        for pattern in (
            r"(?:^|[,\s])0\s+passed\b",
            r"\bpassed\s*:\s*0\b",
            r"\b[1-9][0-9]*\s+skipped\b",
            r"\bskipped\s*:\s*[1-9][0-9]*\b",
            r"\b[1-9][0-9]*\s+did\s+not\s+run\b",
            r"\bdid\s+not\s+run\s*:\s*[1-9][0-9]*\b",
            r"\b0\s+(?:tests?\s+)?executed\b",
            r"\bexecuted\s*:\s*0\b",
            r"\btests?\s*:\s*0\b",
            r"^(?:all\s+)?tests?\s+(?:were\s+)?skipped\b",
        )
    )


def _browser_command_output_is_substantive(output, invocation=None):
    stripped = str(output or "").strip()
    normalized = " ".join(stripped.casefold().split())
    playwright_test_noop = bool(
        invocation
        and invocation.get("executable") == "playwright"
        and (
            _playwright_command_positionals(
                invocation.get("args") or []
            )[:1]
            == ["test"]
        )
        and _playwright_test_output_is_noop(stripped)
    )
    return (
        bool(stripped)
        and not _text_is_error_shaped(stripped)
        and not _browser_scalar_is_acknowledgement(stripped)
        and not re.match(r"^listing tests?\b", normalized)
        and not re.match(r"^no tests? found\b", normalized)
        and not re.search(r"\btotal:\s*0 tests?\b", normalized)
        and not playwright_test_noop
    )


def _is_runtime_invocation(invocation):
    executable = invocation["executable"]
    args = invocation["args"]
    if _has_help_or_version(args) or "--validate-schema" in args:
        return False
    if executable == "codex":
        return _codex_subcommand(args) == "exec"
    if executable.startswith("python"):
        module = _python_module(args)
        if module == "http.server":
            return True
        script_and_args = _python_script_and_args(args)
        script = script_and_args[0] if script_and_args else ""
        return Path(script).name.lower() == "run_runtime.py"
    if executable == "run_runtime.py":
        return True
    return False


def _observed_invocation_uses_trusted_executable(invocation):
    npx_wrapper = invocation.get("npx_wrapper")
    if isinstance(npx_wrapper, dict):
        return False
    return (
        _proof_invocation_environment_is_safe(invocation)
        and _proof_invocation_uses_trusted_executable(invocation)
    )


def _observed_runtime_activity_is_substantive(activity, invocation):
    if not _is_runtime_invocation(invocation):
        return False
    executable = invocation["executable"]
    args = invocation["args"]
    if executable.startswith("python"):
        script_and_args = _python_script_and_args(args)
        script = script_and_args[0] if script_and_args else ""
    elif executable == "run_runtime.py":
        script = str(invocation.get("raw_executable") or "")
    else:
        script = ""
    if script and Path(script).name.lower() == "run_runtime.py":
        return (
            _proof_runtime_environment_is_safe(invocation)
            and _proof_invocation_uses_trusted_executable(invocation)
            and _is_canonical_groundwork_runtime_runner(invocation)
            and _runtime_activity_has_nonempty_success_summary(activity)
        )
    return _observed_invocation_uses_trusted_executable(invocation)


def _is_groundwork_runtime_invocation(invocation):
    executable = invocation["executable"]
    args = invocation["args"]
    if _has_help_or_version(args) or "--validate-schema" in args:
        return False
    if executable == "codex":
        return _codex_subcommand(args) == "exec"
    if executable.startswith("python"):
        if _python_module(args):
            return False
        script_and_args = _python_script_and_args(args)
        script = script_and_args[0] if script_and_args else ""
        return Path(script).name.lower() == "run_runtime.py"
    return executable == "run_runtime.py"


def _activity_detail_payload(activity):
    try:
        payload = json.loads(str(activity.get("detail") or "{}"))
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def _activity_result_value(activity):
    detail = _activity_detail_payload(activity)
    field, value = _activity_result_field(detail)
    if field:
        return value
    item = detail.get("item")
    if isinstance(item, dict):
        _field, value = _activity_result_field(item)
        return value
    return None


def _text_is_error_shaped(value):
    text = str(value or "").strip().casefold()
    if not text:
        return False
    first_line = text.splitlines()[0].strip()
    return bool(
        re.match(
            r"^(?:"
            r"(?:error|fatal)(?:\s*:|\s+-)|"
            r"failed(?:\s+to|\s*:)|"
            r"unable\s+to|"
            r"cannot\b|"
            r"cancelled\b|"
            r"canceled\b|"
            r"permission\s+denied\b|"
            r"no\s+such\s+file\b|"
            r"file\s+not\s+found\b|"
            r"missing\s+(?:document|file|resource|source)\b|"
            r"not\s+found\b|"
            r"timed?\s+out\b|"
            r"traceback\b"
            r")",
            first_line,
        )
    )


def _source_result_is_substantive(result):
    if isinstance(result, str):
        stripped = result.strip()
        if not stripped or _text_is_error_shaped(stripped):
            return False
        try:
            decoded = json.loads(stripped)
        except json.JSONDecodeError:
            decoded = None
        if decoded is not None and decoded != result:
            return _source_result_is_substantive(decoded)
        return not _browser_scalar_is_acknowledgement(stripped)
    if isinstance(result, list):
        return any(_source_result_is_substantive(item) for item in result)
    if not isinstance(result, dict):
        return False
    content_keys = {
        "content",
        "contents",
        "data",
        "document",
        "html",
        "lines",
        "result",
        "rows",
        "source",
        "text",
        "tree",
    }
    return any(
        key in content_keys and _source_result_is_substantive(value)
        for key, value in result.items()
    )


def _structured_source_activity(activity):
    server = re.sub(
        r"[^a-z0-9]+", "_", activity["server"].lower()
    ).strip("_")
    tool = re.sub(
        r"[^a-z0-9]+", "_", (activity["tool"] or activity["kind"]).lower()
    ).strip("_")
    kind = re.sub(
        r"[^a-z0-9]+", "_", activity["kind"].lower()
    ).strip("_")
    trusted_pairs = {
        ("codegraph", "codegraph_explore"),
        ("codegraph", "explore"),
        ("filesystem", "open_file"),
        ("filesystem", "read_file"),
        ("filesystem", "read_mcp_resource"),
        ("functions", "read_mcp_resource"),
    }
    trusted_direct_kinds = {
        "codegraph_explore",
        "open_file",
        "read_file",
        "read_mcp_resource",
    }
    trusted_source_tool = (
        (server, tool) in trusted_pairs
        or (not server and kind in trusted_direct_kinds and tool == kind)
    )
    return trusted_source_tool and _source_result_is_substantive(
        _structured_source_content(activity)
    )


SOURCE_REQUEST_CONTAINERS = {
    "args",
    "arguments",
    "input",
    "item",
    "parameters",
    "params",
    "payload",
    "request",
    "request_data",
}


def _structured_request_values(activity, target_keys):
    values = set()
    normalized_target_keys = {
        re.sub(r"[^a-z0-9]+", "_", str(key).casefold()).strip("_")
        for key in target_keys
    }

    def visit(value):
        if not isinstance(value, dict):
            return
        for raw_key, child in value.items():
            key = re.sub(
                r"[^a-z0-9]+", "_", str(raw_key).casefold()
            ).strip("_")
            if (
                key in normalized_target_keys
                and isinstance(child, str)
                and child.strip()
            ):
                values.add(child.strip())
            if key in SOURCE_REQUEST_CONTAINERS:
                if isinstance(child, dict):
                    visit(child)
                elif isinstance(child, list):
                    for item in child:
                        visit(item)

    visit(_activity_detail_payload(activity))
    return values


def _mcp_resource_text_content(activity, result):
    if not isinstance(result, dict):
        return None
    contents = result.get("contents")
    if not isinstance(contents, list) or len(contents) != 1:
        return None
    resource = contents[0]
    if (
        not isinstance(resource, dict)
        or "blob" in resource
        or not isinstance(resource.get("text"), str)
        or not isinstance(resource.get("uri"), str)
        or not resource["uri"].strip()
    ):
        return None
    resource_uri = resource["uri"].strip()
    requested_uris = _structured_request_values(
        activity, {"resource_uri", "uri"}
    )
    if requested_uris != {resource_uri}:
        return None
    return resource["text"]


def _structured_source_content(activity):
    result = _activity_result_value(activity)
    tool = re.sub(
        r"[^a-z0-9]+",
        "_",
        (activity.get("tool") or activity.get("kind") or "").casefold(),
    ).strip("_")
    if tool == "read_mcp_resource":
        if isinstance(result, dict):
            return _mcp_resource_text_content(activity, result)
        if (
            isinstance(result, str)
            and len(
                _structured_request_values(
                    activity, {"resource_uri", "uri"}
                )
            )
            == 1
        ):
            return result
        return None
    if isinstance(result, str):
        return result
    if not isinstance(result, dict):
        return None
    candidates = [
        value
        for key, value in result.items()
        if key in {"content", "contents", "source", "text"}
        and isinstance(value, str)
    ]
    return candidates[0] if len(candidates) == 1 else None


def _browser_scalar_is_acknowledgement(value):
    normalized = " ".join(
        re.sub(r"[^a-z0-9]+", " ", str(value or "").casefold()).split()
    )
    if not normalized:
        return True
    acknowledgement_states = (
        r"accepted|acknowledged|captured|complete|completed|done|generated|"
        r"initialized|loaded|ok|queued|ready|saved|scheduled|started|"
        r"success|successful|successfully|succeeded"
    )
    if re.fullmatch(rf"(?:{acknowledgement_states})", normalized):
        return True
    control_nouns = (
        r"browser|capture|content|document|image|initialization|operation|"
        r"page|recording|report|request|session|snapshot|tool|trace"
    )
    return bool(
        re.fullmatch(
            rf"(?:(?:{control_nouns})[ \t]+){{1,6}}"
            rf"(?:was[ \t]+)?(?:{acknowledgement_states})",
            normalized,
        )
    )


def _browser_observation_result_is_substantive(tool, result):
    if isinstance(result, str):
        stripped = result.strip()
        if not stripped or _text_is_error_shaped(stripped):
            return False
        try:
            decoded = json.loads(stripped)
        except json.JSONDecodeError:
            decoded = None
        if decoded is not None and decoded != result:
            return _browser_observation_result_is_substantive(tool, decoded)
        lowered = stripped.casefold()
        if _browser_scalar_is_acknowledgement(stripped):
            return False
        if tool in {
            "browser_screenshot",
            "page_screenshot",
            "screenshot",
            "take_screenshot",
        }:
            return bool(
                re.match(r"^(?:data:image/|attachment:|/)", stripped)
                or re.search(r"\.(?:gif|jpe?g|png|webp)(?:\?.*)?$", lowered)
                or re.fullmatch(
                    r"[A-Za-z0-9+/=\r\n]{32,}",
                    stripped,
                )
            )
        if tool in {
            "accessibility_snapshot",
            "browser_evaluate",
            "dom_snapshot",
            "evaluate",
            "extract",
            "get_dom",
            "get_html",
            "get_page_content",
            "page_content",
            "page_snapshot",
            "read_page",
            "snapshot",
        }:
            return len(stripped) >= 8
        if tool in {"lighthouse", "performance_report"}:
            return bool(
                re.search(
                    r"\b(?:audit|cls|fcp|lcp|metric|performance|score|"
                    r"timing|trace|ttfb)\b",
                    lowered,
                )
                and re.search(r"\d", stripped)
            )
        return False
    if (
        tool in {"browser_evaluate", "evaluate", "extract"}
        and (
            result is None
            or isinstance(result, (bool, int, float))
        )
    ):
        return True
    if isinstance(result, list):
        return bool(result) and tool in {
            "accessibility_snapshot",
            "browser_evaluate",
            "console_messages",
            "dom_snapshot",
            "evaluate",
            "extract",
            "get_console_logs",
            "get_network_requests",
            "network_requests",
            "page_snapshot",
            "snapshot",
        }
    if not isinstance(result, dict):
        return False

    marker_keys = {
        "accessibility_snapshot": {
            "accessibility",
            "nodes",
            "root",
            "snapshot",
            "tree",
        },
        "browser_evaluate": {
            "content",
            "data",
            "items",
            "result",
            "rows",
            "text",
            "value",
        },
        "browser_screenshot": {
            "artifact",
            "attachment",
            "base64",
            "bytes",
            "data",
            "image",
            "images",
            "path",
            "paths",
            "screenshot",
        },
        "console_messages": {"console", "entries", "events", "logs", "messages"},
        "dom_snapshot": {
            "content",
            "document",
            "dom",
            "html",
            "nodes",
            "root",
            "snapshot",
            "tree",
        },
        "evaluate": {
            "content",
            "data",
            "items",
            "result",
            "rows",
            "text",
            "value",
        },
        "extract": {
            "content",
            "data",
            "items",
            "matches",
            "result",
            "rows",
            "text",
            "value",
        },
        "get_console_logs": {"console", "entries", "events", "logs", "messages"},
        "get_dom": {"content", "document", "dom", "html", "nodes", "root", "tree"},
        "get_html": {"content", "document", "html", "text"},
        "get_network_requests": {
            "entries",
            "events",
            "har",
            "network",
            "requests",
        },
        "get_page_content": {
            "content",
            "document",
            "html",
            "nodes",
            "text",
        },
        "lighthouse": {
            "audits",
            "categories",
            "metrics",
            "report",
            "scores",
        },
        "network_requests": {
            "entries",
            "events",
            "har",
            "network",
            "requests",
        },
        "page_content": {
            "content",
            "document",
            "html",
            "nodes",
            "text",
        },
        "page_screenshot": {
            "artifact",
            "attachment",
            "base64",
            "bytes",
            "data",
            "image",
            "images",
            "path",
            "paths",
            "screenshot",
        },
        "page_snapshot": {
            "accessibility",
            "content",
            "document",
            "dom",
            "html",
            "nodes",
            "root",
            "snapshot",
            "text",
            "tree",
        },
        "performance_report": {
            "audits",
            "entries",
            "metrics",
            "performance",
            "report",
            "timings",
            "trace",
        },
        "read_page": {
            "accessibility",
            "content",
            "document",
            "dom",
            "html",
            "nodes",
            "text",
            "tree",
        },
        "screenshot": {
            "artifact",
            "attachment",
            "base64",
            "bytes",
            "data",
            "image",
            "images",
            "path",
            "paths",
            "screenshot",
        },
        "snapshot": {
            "accessibility",
            "content",
            "document",
            "dom",
            "html",
            "nodes",
            "root",
            "snapshot",
            "text",
            "tree",
        },
        "take_screenshot": {
            "artifact",
            "attachment",
            "base64",
            "bytes",
            "data",
            "image",
            "images",
            "path",
            "paths",
            "screenshot",
        },
    }
    expected_keys = marker_keys.get(tool, set())
    empty_collection_observations = {
        ("console_messages", "console"),
        ("console_messages", "entries"),
        ("console_messages", "events"),
        ("console_messages", "logs"),
        ("console_messages", "messages"),
        ("get_console_logs", "console"),
        ("get_console_logs", "entries"),
        ("get_console_logs", "events"),
        ("get_console_logs", "logs"),
        ("get_console_logs", "messages"),
        ("get_network_requests", "entries"),
        ("get_network_requests", "events"),
        ("get_network_requests", "requests"),
        ("network_requests", "entries"),
        ("network_requests", "events"),
        ("network_requests", "requests"),
    }
    acknowledgement_keys = {
        "accepted",
        "acknowledged",
        "allowed",
        "claimed",
        "cleared",
        "closed",
        "completed",
        "configured",
        "detail",
        "disabled",
        "enabled",
        "message",
        "ok",
        "queued",
        "ready",
        "scheduled",
        "started",
        "status",
        "stopped",
        "success",
        "timestamp",
    }

    def structured_value_is_substantive(value):
        if isinstance(value, dict):
            meaningful_keys = set(value).difference(acknowledgement_keys)
            if not meaningful_keys:
                return False
            return any(
                structured_value_is_substantive(value[key])
                for key in meaningful_keys
            )
        if isinstance(value, list):
            return any(structured_value_is_substantive(item) for item in value)
        if isinstance(value, bool) or value is None:
            return False
        if isinstance(value, (int, float)):
            return True
        return _browser_observation_result_is_substantive(tool, value)

    for key in expected_keys.intersection(result):
        value = result[key]
        if (
            tool in {"browser_evaluate", "evaluate", "extract"}
            and key in {"data", "result", "value"}
            and value is not None
            and not isinstance(value, (dict, list))
        ):
            return True
        if (
            isinstance(value, (list, dict))
            and not value
            and (tool, key) in empty_collection_observations
        ):
            return True
        if structured_value_is_substantive(value):
            return True
    return False


def _structured_browser_activity(activity):
    server = activity["server"].lower()
    tool = re.sub(
        r"[^a-z0-9]+", "_", activity["tool"].lower()
    ).strip("_")
    observation_tools = {
        "accessibility_snapshot",
        "browser_evaluate",
        "browser_screenshot",
        "console_messages",
        "dom_snapshot",
        "evaluate",
        "extract",
        "get_console_logs",
        "get_dom",
        "get_html",
        "get_network_requests",
        "get_page_content",
        "lighthouse",
        "network_requests",
        "page_content",
        "page_screenshot",
        "page_snapshot",
        "performance_report",
        "read_page",
        "screenshot",
        "snapshot",
        "take_screenshot",
    }
    control_tokens = {
        "claim",
        "clear",
        "close",
        "configure",
        "disable",
        "enable",
        "open",
        "permission",
        "set",
        "start",
        "stop",
    }
    normalized_server = re.sub(
        r"[^a-z0-9]+", "_", server
    ).strip("_")
    matched_tool = tool if tool in observation_tools else ""
    trusted_server = normalized_server in {
        "browser",
        "browser_use",
        "chrome",
        "chrome_devtools",
        "devtools",
    }
    if not (
        trusted_server
        and matched_tool
        and not control_tokens.intersection(tool.split("_"))
        and bool(str(activity.get("output") or "").strip())
    ):
        return False
    result = _activity_result_value(activity)
    return _browser_observation_result_is_substantive(matched_tool, result)


NODE_TEST_REQUIRED_SUMMARY_KEYS = (
    "tests",
    "pass",
    "fail",
    "cancelled",
    "skipped",
    "todo",
)
NODE_TEST_SUMMARY_KEYS = {
    *NODE_TEST_REQUIRED_SUMMARY_KEYS,
    "suites",
}


def _node_test_output_is_substantive(output):
    lines = str(output or "").splitlines()
    patterns = []
    for prefix in (r"#", "ℹ"):
        patterns.append(
            (
                re.compile(
                    r"^\s*"
                    + prefix
                    + r"\s*("
                    + "|".join(sorted(NODE_TEST_SUMMARY_KEYS))
                    + r")\s+(\d+)\s*$",
                    re.IGNORECASE,
                ),
                re.compile(
                    r"^\s*"
                    + prefix
                    + r"\s*duration_ms\s+"
                    r"(?:\d+(?:\.\d*)?|\.\d+)\s*$",
                    re.IGNORECASE,
                ),
            )
        )

    matched_formats = []
    for counter_pattern, duration_pattern in patterns:
        if any(
            counter_pattern.fullmatch(line)
            or duration_pattern.fullmatch(line)
            for line in lines
        ):
            matched_formats.append((counter_pattern, duration_pattern))
    if len(matched_formats) != 1:
        return False
    counter_pattern, duration_pattern = matched_formats[0]

    counters = {}
    counter_indexes = {}
    duration_indexes = []
    for index, line in enumerate(lines):
        match = counter_pattern.fullmatch(line)
        if match is not None:
            key = match.group(1).casefold()
            counters.setdefault(key, []).append(int(match.group(2)))
            counter_indexes.setdefault(key, []).append(index)
        elif duration_pattern.fullmatch(line):
            duration_indexes.append(index)

    if (
        any(len(values) != 1 for values in counters.values())
        or any(
            len(counters.get(key, [])) != 1
            for key in NODE_TEST_REQUIRED_SUMMARY_KEYS
        )
        or len(duration_indexes) != 1
    ):
        return False

    tests_index = counter_indexes["tests"][0]
    summary_key_order = (
        "tests",
        "suites",
        "pass",
        "fail",
        "cancelled",
        "skipped",
        "todo",
    )
    observed_key_order = tuple(
        key
        for key, _index in sorted(
            (
                (key, indexes[0])
                for key, indexes in counter_indexes.items()
            ),
            key=lambda item: item[1],
        )
    )
    expected_key_order = tuple(
        key for key in summary_key_order if key in counters
    )
    if observed_key_order != expected_key_order:
        return False
    final_nonempty_index = next(
        (
            index
            for index in range(len(lines) - 1, -1, -1)
            if lines[index].strip()
        ),
        -1,
    )
    if duration_indexes[0] != final_nonempty_index:
        return False
    for line in lines[tests_index:]:
        if (
            line.strip()
            and counter_pattern.fullmatch(line) is None
            and duration_pattern.fullmatch(line) is None
        ):
            return False

    values = {
        key: counters[key][0]
        for key in NODE_TEST_REQUIRED_SUMMARY_KEYS
    }
    accounted = sum(
        values[key]
        for key in ("pass", "fail", "cancelled", "skipped", "todo")
    )
    return (
        values["tests"] == accounted
        and values["pass"] + values["fail"] > 0
    )


def _is_node_test_invocation(invocation):
    node_options = _node_test_option_prefix(
        (invocation or {}).get("args") or []
    )
    return bool(
        invocation
        and invocation.get("executable") == "node"
        and node_options is not None
        and "--test" in node_options
    )


def _test_command_output_is_substantive(output, invocation=None):
    text = str(output or "").strip()
    if not text or not invocation or not _is_test_invocation(invocation):
        return False
    if _is_node_test_invocation(invocation):
        return _node_test_output_is_substantive(text)
    return False


def has_observed_evidence(stdout, evidence_kind, *, require_success=False):
    activities = completed_tool_activities(stdout)
    eligible = [
        activity
        for activity in activities
        if activity["has_result"]
        and (activity["succeeded"] or not require_success)
    ]
    command_predicates = {
        "source": _is_source_invocation,
        "tests": _is_test_invocation,
        "browser": _is_browser_invocation,
        "runtime": _is_runtime_invocation,
    }
    predicate = command_predicates.get(evidence_kind)
    if predicate is None:
        return False
    for activity in eligible:
        if activity["kind"] == "command_execution":
            attributable = command_success_is_attributable(
                activity["command"]
            )
            if (
                require_success
                or evidence_kind in {"browser", "runtime"}
            ) and not attributable:
                continue
            invocations = command_invocations(activity["command"])
            if (
                evidence_kind in {"source", "tests", "browser"}
                and len(invocations) != 1
            ):
                continue
            matching_invocations = [
                invocation
                for invocation in invocations
                if predicate(invocation)
            ]
            if evidence_kind in {"source", "tests"}:
                matching_invocations = [
                    invocation
                    for invocation in matching_invocations
                    if _observed_invocation_uses_trusted_executable(
                        invocation
                    )
                ]
            if (
                evidence_kind == "source"
                and matching_invocations
                and not _source_result_is_substantive(
                    activity.get("output")
                )
            ):
                continue
            if (
                evidence_kind == "tests"
                and matching_invocations
                and not _test_command_output_is_substantive(
                    activity.get("output"),
                    matching_invocations[0],
                )
            ):
                continue
            if (
                evidence_kind == "browser"
                and matching_invocations
                and (
                    not _observed_invocation_uses_trusted_executable(
                        matching_invocations[0]
                    )
                    or not _browser_command_output_is_substantive(
                        activity.get("output"),
                        matching_invocations[0],
                    )
                )
            ):
                continue
            if (
                evidence_kind == "runtime"
                and matching_invocations
                and not any(
                    _observed_runtime_activity_is_substantive(
                        activity, invocation
                    )
                    for invocation in matching_invocations
                )
            ):
                continue
            if matching_invocations:
                return True
        if evidence_kind == "source" and _structured_source_activity(activity):
            return True
        if evidence_kind == "browser" and _structured_browser_activity(activity):
            return True
    return False


def observed_evidence_kinds(stdout):
    return [
        evidence_kind
        for evidence_kind in ("source", "tests", "browser", "runtime")
        if has_observed_evidence(stdout, evidence_kind)
    ]


EXPECTED_FAILED_TEST_ROUTE_BOUNDARIES = {
    "qa-gap-closure-admission",
    "verify-qa-failure",
}


def _expected_failed_test_command(row, final_response):
    if (
        str(row.get("source_truth") or "").strip() != "test_evidence"
        or str(row.get("route_boundary") or "").strip()
        not in EXPECTED_FAILED_TEST_ROUTE_BOUNDARIES
        or "qa_fix_qa"
        not in {
            token.strip()
            for token in str(row.get("output_contract") or "").split("|")
            if token.strip()
        }
    ):
        return ""
    matches = [
        match.group(1).strip().strip("`")
        for match in re.finditer(
            r"(?m)^-[ \t]+Reproduction:[ \t]+command:[ \t]*(.+?)[ \t]*$",
            str(final_response or ""),
        )
    ]
    if len(matches) != 1:
        return ""
    expected_command = matches[0]
    scenario = str(
        row.get("input_scenario") or row.get("prompt") or ""
    )
    return expected_command if expected_command in scenario else ""


def _expected_test_failure_output_is_substantive(output):
    text = str(output or "").strip()
    if not text or _text_is_error_shaped(text):
        return False
    lowered = text.casefold()
    phase_failure_patterns = (
        r"\berror(?:s)?\s+(?:during|in)\s+collection\b",
        r"\berror\s+collecting\b",
        r"\bcollection\s+(?:error|failed|failure)\b",
        r"\bcollected\s+0\s+items?\b",
        r"\bno\s+tests?\s+(?:collected|ran|were\s+run)\b",
        r"\b0\s+tests?\s+(?:collected|ran|executed)\b",
        r"\berror\s+during\s+(?:setup|teardown)\b",
        r"\bsetup\s+(?:error|failed|failure)\b",
        r"\btest\s+suite\s+failed\s+to\s+run\b",
        r"\bimport(?:error|\s+error|\s+failed|\s+failure)\b",
    )
    if any(re.search(pattern, lowered) for pattern in phase_failure_patterns):
        return False
    infrastructure_markers = (
        "0 failed",
        "0 failures",
        "cannot find module",
        "command not found",
        "connection refused",
        "crash",
        "enoent",
        "failed to start",
        "file not found",
        "importerror",
        "module not found",
        "no such file",
        "permission denied",
        "runner failed",
        "timed out",
    )
    if any(marker in lowered for marker in infrastructure_markers):
        return False
    expected_vs_actual = bool(
        re.search(r"\bexpected\b", lowered)
        and re.search(r"\bactual\b", lowered)
    )
    standard_assertion_failure = bool(
        re.search(
            r"(?im)(?:"
            r"\bassertionerror\b|"
            r"\berr_assertion\b|"
            r"\bassert(?:ion)?[ \t]+(?:error|fail(?:ed|ure)?)\b|"
            r"^[ \t]*(?:e[ \t]+)?assert\b|"
            r"^[ \t]*not[ \t]+ok\b"
            r")",
            lowered,
        )
    )
    uncaught_language_error = bool(
        re.search(
            r"(?im)^[ \t]*(?:syntaxerror|typeerror|referenceerror)\s*:",
            text,
        )
    )
    if uncaught_language_error and not (
        expected_vs_actual or standard_assertion_failure
    ):
        return False
    return expected_vs_actual or standard_assertion_failure


def _canonical_expected_failure_fixture_marker(
    row, expected_tokens, output
):
    return (
        str(row.get("fixture") or "").rstrip("/")
        == "evals/fixtures/minimal-task-search"
        and expected_tokens
        == ["node", "--test", "test/taskSearch.test.mjs"]
        and str(output or "").strip().casefold()
        == "expected failure reproduced"
    )


def has_observed_expected_test_failure(stdout, row, final_response):
    expected_command = _expected_failed_test_command(row, final_response)
    expected_tokens = _shell_tokens(expected_command)
    if not expected_tokens:
        return False
    for activity in completed_tool_activities(stdout):
        if (
            activity["kind"] != "command_execution"
            or not activity["has_result"]
            or activity["succeeded"]
            or not command_success_is_attributable(activity["command"])
            or _shell_tokens(activity["command"]) != expected_tokens
        ):
            continue
        detail = _activity_detail_payload(activity)
        exit_code = detail.get("exit_code")
        status = str(detail.get("status") or "").casefold()
        invocations = command_invocations(activity["command"])
        if (
            type(exit_code) is int
            and exit_code != 0
            and status == "failed"
            and len(invocations) == 1
            and _is_test_invocation(invocations[0])
            and _observed_invocation_uses_trusted_executable(
                invocations[0]
            )
            and (
                _expected_test_failure_output_is_substantive(
                    activity.get("output")
                )
                or _canonical_expected_failure_fixture_marker(
                    row,
                    expected_tokens,
                    activity.get("output"),
                )
            )
        ):
            return True
    return False


def release_evidence_status(final_response):
    return release_evidence_claim_status(final_response)


PROOF_ENVIRONMENT_POLICY_VERSION = "proof-environment-v3"
PROOF_EXECUTABLE_POLICY_VERSION = "proof-executable-v3"
UNSAFE_PROOF_ENVIRONMENT_KEYS = {
    "AR",
    "AS",
    "BASH_ENV",
    "BASHOPTS",
    "CC",
    "CFLAGS",
    "CDPATH",
    "CLASSPATH",
    "COMPILER_PATH",
    "CPATH",
    "CPPFLAGS",
    "CPLUS_INCLUDE_PATH",
    "CXX",
    "CXXFLAGS",
    "DEVELOPER_DIR",
    "DIFF_OPTIONS",
    "DYLD_INSERT_LIBRARIES",
    "ENV",
    "GIT_ALTERNATE_OBJECT_DIRECTORIES",
    "GIT_CEILING_DIRECTORIES",
    "GIT_COMMON_DIR",
    "GIT_CONFIG_PARAMETERS",
    "GIT_CONFIG_GLOBAL",
    "GIT_CONFIG_SYSTEM",
    "GIT_CONFIG_NOSYSTEM",
    "GIT_DIR",
    "GIT_EXEC_PATH",
    "GIT_EXTERNAL_DIFF",
    "GIT_INDEX_FILE",
    "GIT_OBJECT_DIRECTORY",
    "GIT_WORK_TREE",
    "GOCACHE",
    "GOENV",
    "GOFLAGS",
    "GOMOD",
    "GOMODCACHE",
    "GOPATH",
    "GOROOT",
    "GOTOOLCHAIN",
    "GOWORK",
    "HOME",
    "JAVA_HOME",
    "JAVA_TOOL_OPTIONS",
    "JDK_JAVA_OPTIONS",
    "LD",
    "LDFLAGS",
    "LD_PRELOAD",
    "LIBRARY_PATH",
    "MACOSX_DEPLOYMENT_TARGET",
    "MAKEFLAGS",
    "MFLAGS",
    "NM",
    "OBJC",
    "PAGER",
    "PERL5OPT",
    "PATH",
    "PYTHONHOME",
    "PYTHONINSPECT",
    "PYTHONPATH",
    "PYTHONSTARTUP",
    "RANLIB",
    "RUBYOPT",
    "SDKROOT",
    "SHELLOPTS",
    "STRIP",
    "USERPROFILE",
    "VIRTUAL_ENV",
    "XDG_CACHE_HOME",
    "XDG_CONFIG_HOME",
    "XDG_DATA_HOME",
    "XDG_RUNTIME_DIR",
    "XDG_STATE_HOME",
    "ZDOTDIR",
    "_JAVA_OPTIONS",
}
UNSAFE_PROOF_ENVIRONMENT_PREFIXES = (
    "CARGO_",
    "DYLD_",
    "GIT_",
    "GIT_CONFIG_KEY_",
    "GIT_CONFIG_VALUE_",
    "GRADLE_",
    "LD_",
    "MAVEN_",
    "NPM_CONFIG_",
    "NODE_",
    "PYTEST_",
    "PYTHON",
    "RUST",
)
PROOF_CONTROL_ENVIRONMENT_KEYS = {
    "GROUNDWORK_ROUTER_OBSERVABILITY",
    "GROUNDWORK_ROUTER_OBSERVABILITY_DEBUG",
    "GROUNDWORK_ROUTER_OBSERVABILITY_DISABLED",
    "GROUNDWORK_ROUTER_OBSERVABILITY_MODE",
}
INHERITED_ONLY_UNSAFE_PROOF_ENVIRONMENT_KEYS = {
    "GROUNDWORK_CODEX_BYPASS_HOOK_TRUST",
    "GROUNDWORK_CODEX_TIMEOUT",
    "GROUNDWORK_REPO",
    "GROUNDWORK_RUNTIME_ROOT",
}
ALLOWED_GROUNDWORK_PROOF_ENVIRONMENT_KEYS = {
    "GROUNDWORK_CODEX_TIMEOUT",
    "GROUNDWORK_REPO",
    "GROUNDWORK_RUNTIME_ROOT",
}


def _resolved_executable_path(value):
    if not value:
        return None
    path = Path(value)
    try:
        if not path.is_file() or not os.access(path, os.X_OK):
            return None
        return path.resolve(strict=True)
    except OSError:
        return None


PROOF_EXECUTABLE_NAMES = (
    "bash",
    "cargo",
    "cat",
    "chrome-headless-shell",
    "chromium",
    "chromium-browser",
    "codegraph",
    "codex",
    "dash",
    "diff",
    "env",
    "go",
    "git",
    "google-chrome",
    "gradle",
    "gradlew",
    "grep",
    "head",
    "mvn",
    "mvnw",
    "node",
    "nohup",
    "npm",
    "npx",
    "playwright",
    "pnpm",
    "py.test",
    "pytest",
    "rg",
    "sed",
    "sh",
    "tail",
    "yarn",
    "zsh",
)
PROOF_EXECUTABLE_IDENTITY_FIELDS = (
    "launcher_path",
    "launcher_device",
    "launcher_inode",
    "launcher_mode",
    "launcher_uid",
    "launcher_gid",
    "launcher_size",
    "launcher_mtime_ns",
    "launcher_ctime_ns",
    "resolved_path",
    "resolved_device",
    "resolved_inode",
    "resolved_mode",
    "resolved_uid",
    "resolved_gid",
    "resolved_size",
    "resolved_mtime_ns",
    "resolved_ctime_ns",
)


def _sha256_file(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        while True:
            chunk = handle.read(1024 * 1024)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()


def _path_is_within(path, root):
    try:
        Path(path).relative_to(Path(root))
        return True
    except ValueError:
        return False


def _proof_untrusted_roots():
    roots = [
        REPO,
        ROOT,
        Path("/tmp"),
        Path("/private/tmp"),
        Path("/var/tmp"),
        Path(tempfile.gettempdir()),
    ]
    return tuple(
        root.resolve(strict=False)
        for root in roots
    )


def _proof_path_has_untrusted_write_control(path):
    try:
        path_stat = Path(path).stat()
    except OSError:
        return True
    uid_getter = getattr(os, "geteuid", None) or getattr(
        os,
        "getuid",
        None,
    )
    current_uid = uid_getter() if uid_getter is not None else None
    if current_uid is not None and path_stat.st_uid == current_uid:
        return True
    if path_stat.st_mode & 0o022:
        return True
    try:
        return os.access(path, os.W_OK)
    except OSError:
        return True


def _proof_executable_location_is_safe(path):
    candidate = Path(path)
    if not candidate.is_absolute():
        return False
    resolved = candidate.resolve(strict=False)
    if any(
        _path_is_within(candidate, root)
        or _path_is_within(resolved, root)
        for root in _proof_untrusted_roots()
    ):
        return False
    for executable_path in {candidate, resolved}:
        if _proof_path_has_untrusted_write_control(executable_path):
            return False
    current = candidate.parent
    while True:
        if _proof_path_has_untrusted_write_control(current):
            return False
        if current == current.parent:
            break
        current = current.parent
    return True


def _proof_executable_identity(value, *, include_hash=True):
    if not value:
        return None
    raw_path = Path(value)
    if not raw_path.is_absolute():
        return None
    try:
        launcher = raw_path.parent.resolve(strict=True) / raw_path.name
        if not launcher.is_file() or not os.access(launcher, os.X_OK):
            return None
        resolved = launcher.resolve(strict=True)
        if (
            not _proof_executable_location_is_safe(launcher)
            or not _proof_executable_location_is_safe(resolved)
        ):
            return None
        launcher_stat = launcher.lstat()
        resolved_stat = resolved.stat()
        if resolved_stat.st_mode & 0o022:
            return None
        identity = {
            "launcher_path": str(launcher),
            "launcher_device": launcher_stat.st_dev,
            "launcher_inode": launcher_stat.st_ino,
            "launcher_mode": launcher_stat.st_mode,
            "launcher_uid": launcher_stat.st_uid,
            "launcher_gid": launcher_stat.st_gid,
            "launcher_size": launcher_stat.st_size,
            "launcher_mtime_ns": launcher_stat.st_mtime_ns,
            "launcher_ctime_ns": launcher_stat.st_ctime_ns,
            "resolved_path": str(resolved),
            "resolved_device": resolved_stat.st_dev,
            "resolved_inode": resolved_stat.st_ino,
            "resolved_mode": resolved_stat.st_mode,
            "resolved_uid": resolved_stat.st_uid,
            "resolved_gid": resolved_stat.st_gid,
            "resolved_size": resolved_stat.st_size,
            "resolved_mtime_ns": resolved_stat.st_mtime_ns,
            "resolved_ctime_ns": resolved_stat.st_ctime_ns,
        }
        if include_hash:
            identity["sha256"] = _sha256_file(resolved)
        return identity
    except OSError:
        return None


def _codex_control_launcher():
    search_path = str(os.environ.get("PATH") or os.defpath)
    for entry in search_path.split(os.pathsep):
        directory = Path(entry)
        if not entry or not directory.is_absolute():
            continue
        try:
            canonical_directory = directory.resolve(strict=True)
        except OSError:
            continue
        candidate = shutil.which("codex", path=str(canonical_directory))
        if not candidate:
            continue
        raw_path = Path(candidate)
        try:
            launcher = raw_path.parent.resolve(strict=True) / raw_path.name
        except OSError:
            continue
        if (
            launcher.is_file()
            and os.access(launcher, os.X_OK)
            and _proof_executable_location_is_safe(launcher)
        ):
            return launcher
    return None


CODEX_CONTROL_LAUNCHER = _codex_control_launcher()


def _proof_executable_discovery_path():
    directories = []
    candidates = []
    if CODEX_CONTROL_LAUNCHER is not None:
        candidates.append(CODEX_CONTROL_LAUNCHER.parent)
    candidates.extend(
        [
            Path(sys.executable).resolve(strict=True).parent,
            Path("/usr/local/go/bin"),
            Path("/usr/local/bin"),
            Path("/Library/Apple/usr/bin"),
            Path("/usr/bin"),
            Path("/bin"),
            Path("/usr/sbin"),
            Path("/sbin"),
        ]
    )
    for directory in candidates:
        try:
            canonical = directory.resolve(strict=True)
        except OSError:
            continue
        value = str(canonical)
        if value not in directories:
            directories.append(value)
    return os.pathsep.join(directories)


PROOF_EXECUTABLE_DISCOVERY_PATH = _proof_executable_discovery_path()


def _trusted_executable_identity_from_path(executable, path_value=None):
    search_path = str(
        path_value
        if path_value is not None
        else PROOF_EXECUTABLE_DISCOVERY_PATH
    )
    for entry in search_path.split(os.pathsep):
        directory = Path(entry)
        if not entry or not directory.is_absolute():
            continue
        try:
            canonical_directory = directory.resolve(strict=True)
        except OSError:
            continue
        candidate = shutil.which(executable, path=str(canonical_directory))
        identity = _proof_executable_identity(candidate)
        if identity is not None:
            return identity
    return None


PROOF_EXECUTABLE_IDENTITIES = {
    executable: _trusted_executable_identity_from_path(executable)
    for executable in PROOF_EXECUTABLE_NAMES
}
PROOF_EXECUTABLE_BASELINES = {
    executable: (
        Path(identity["resolved_path"])
        if identity is not None
        else None
    )
    for executable, identity in PROOF_EXECUTABLE_IDENTITIES.items()
}
PROOF_EXECUTABLE_LAUNCHERS = {
    executable: (
        Path(identity["launcher_path"])
        if identity is not None
        else None
    )
    for executable, identity in PROOF_EXECUTABLE_IDENTITIES.items()
}
PYTHON_EXECUTABLE_IDENTITY = _proof_executable_identity(sys.executable)
PYTHON_EXECUTABLE_BASELINE = (
    Path(PYTHON_EXECUTABLE_IDENTITY["resolved_path"])
    if PYTHON_EXECUTABLE_IDENTITY is not None
    else None
)
PYTHON_EXECUTABLE_IDENTITIES = {}
if PYTHON_EXECUTABLE_IDENTITY is not None:
    python_directory = Path(sys.executable).resolve(strict=True).parent
    for python_name in {
        "python",
        "python3",
        Path(sys.executable).name,
    }:
        python_candidate = shutil.which(
            python_name,
            path=str(python_directory),
        )
        python_identity = _proof_executable_identity(python_candidate)
        if (
            python_identity is not None
            and python_identity["resolved_path"]
            == PYTHON_EXECUTABLE_IDENTITY["resolved_path"]
        ):
            PYTHON_EXECUTABLE_IDENTITIES[python_name.casefold()] = python_identity


def _proof_executable_path():
    directories = []
    if CODEX_CONTROL_LAUNCHER is not None:
        directories.append(str(CODEX_CONTROL_LAUNCHER.parent))
    identities = list(PYTHON_EXECUTABLE_IDENTITIES.values()) + [
        identity
        for identity in PROOF_EXECUTABLE_IDENTITIES.values()
        if identity is not None
    ]
    for identity in identities:
        directory = str(Path(identity["launcher_path"]).parent)
        if directory not in directories:
            directories.append(directory)
    if CODEX_CONTROL_LAUNCHER is not None:
        control_directory = str(CODEX_CONTROL_LAUNCHER.parent)
        if control_directory not in directories:
            directories.append(control_directory)
    return os.pathsep.join(directories)


EMPTY_PROOF_EXECUTABLE_PATH = os.path.join(
    os.sep,
    "nonexistent",
    "groundwork-proof-bin",
)
PROOF_EXECUTABLE_PATH = (
    _proof_executable_path()
    or EMPTY_PROOF_EXECUTABLE_PATH
)
_PROOF_EXECUTABLE_VERIFICATION_CACHE = set()


def _controlled_proof_executable_path():
    return (
        str(PROOF_EXECUTABLE_PATH).strip()
        or EMPTY_PROOF_EXECUTABLE_PATH
    )


def _captured_evaluator_command(command):
    if not command:
        raise RuntimeError(
            "trusted evaluator launcher is required for an empty command"
        )
    raw_executable = str(command[0])
    executable = Path(raw_executable).name.casefold()
    identities = (
        PYTHON_EXECUTABLE_IDENTITIES
        if executable.startswith("python")
        else PROOF_EXECUTABLE_IDENTITIES
    )
    identity = identities.get(executable)
    if identity is None:
        raise RuntimeError(
            f"no trusted evaluator launcher is available for {executable}"
        )
    launcher = str(identity["launcher_path"])
    if (
        ("/" in raw_executable or "\\" in raw_executable)
        and not _proof_executable_identity_matches(
            raw_executable,
            identity,
        )
    ):
        raise RuntimeError(
            f"the evaluator launcher is not the captured {executable} identity"
        )
    return [launcher, *[str(item) for item in command[1:]]]


def _proof_executable_identity_matches(candidate, baseline):
    if baseline is None:
        return False
    current = _proof_executable_identity(candidate, include_hash=False)
    if current is None or any(
        current.get(field) != baseline.get(field)
        for field in PROOF_EXECUTABLE_IDENTITY_FIELDS
    ):
        return False
    cache_key = tuple(
        current.get(field)
        for field in PROOF_EXECUTABLE_IDENTITY_FIELDS
    ) + (baseline.get("sha256"),)
    if cache_key in _PROOF_EXECUTABLE_VERIFICATION_CACHE:
        return True
    try:
        matches = (
            _sha256_file(current["resolved_path"])
            == baseline.get("sha256")
        )
    except OSError:
        return False
    if matches:
        _PROOF_EXECUTABLE_VERIFICATION_CACHE.add(cache_key)
    return matches


def _proof_environment_key_is_unsafe(key, *, inherited=False):
    normalized = str(key).upper()
    return (
        normalized in UNSAFE_PROOF_ENVIRONMENT_KEYS
        or (
            inherited
            and normalized
            in INHERITED_ONLY_UNSAFE_PROOF_ENVIRONMENT_KEYS
        )
        or any(
            normalized.startswith(prefix)
            for prefix in UNSAFE_PROOF_ENVIRONMENT_PREFIXES
        )
    )


def _proof_executable_manifest_digest():
    payload = {
        "policy": PROOF_EXECUTABLE_POLICY_VERSION,
        "executables": PROOF_EXECUTABLE_IDENTITIES,
        "python": PYTHON_EXECUTABLE_IDENTITIES,
    }
    return hashlib.sha256(
        json.dumps(
            payload,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    ).hexdigest()


def _codex_home_from_environment(environment):
    candidate = str(environment.get("CODEX_HOME") or "").strip()
    if not candidate and pwd is not None:
        try:
            candidate = str(
                Path(pwd.getpwuid(os.getuid()).pw_dir) / ".codex"
            )
        except (KeyError, OSError):
            candidate = ""
    if not candidate:
        return None
    path = Path(candidate)
    if not path.is_absolute():
        return None
    resolved = path.resolve(strict=False)
    if any(
        _path_is_within(resolved, root)
        for root in _proof_untrusted_roots()
    ):
        return None
    return str(resolved)


def sanitized_codex_environment(environment=None):
    source = dict(os.environ if environment is None else environment)
    raw_codex_home = str(source.get("CODEX_HOME") or "").strip()
    codex_home = _codex_home_from_environment(source)
    removed = sorted(
        {
            key
            for key in source
            if _proof_environment_key_is_unsafe(key, inherited=True)
        }
        | (
            {"CODEX_HOME"}
            if raw_codex_home and codex_home is None
            else set()
        )
    )
    sanitized = {
        key: value
        for key, value in source.items()
        if key not in removed
    }
    sanitized.pop("CODEX_HOME", None)
    controlled_path = _controlled_proof_executable_path()
    sanitized["PATH"] = controlled_path
    proof_home = PROOF_HOME.resolve(strict=False)
    enforced_environment = {
        "GIT_CONFIG_GLOBAL": os.devnull,
        "GIT_CONFIG_NOSYSTEM": "1",
        "GIT_CONFIG_SYSTEM": os.devnull,
        "GOENV": "off",
        "HOME": str(proof_home),
        "PYTEST_DISABLE_PLUGIN_AUTOLOAD": "1",
        "PYTHONNOUSERSITE": "1",
        "XDG_CACHE_HOME": str(proof_home / ".cache"),
        "XDG_CONFIG_HOME": str(proof_home / ".config"),
        "XDG_DATA_HOME": str(proof_home / ".local" / "share"),
        "XDG_STATE_HOME": str(proof_home / ".local" / "state"),
    }
    sanitized.update(enforced_environment)
    if codex_home is not None:
        sanitized["CODEX_HOME"] = codex_home
    codex_control_environment = (
        {"CODEX_HOME": codex_home}
        if codex_home is not None
        else {}
    )
    retained_control_environment = {
        key: sanitized[key]
        for key in sorted(PROOF_CONTROL_ENVIRONMENT_KEYS)
        if key in sanitized
    }
    argv_controls = {
        "hook_trust_bypass": hook_trust_bypass_enabled(),
    }
    summary = {
        "environment_policy": PROOF_ENVIRONMENT_POLICY_VERSION,
        "executable_policy": PROOF_EXECUTABLE_POLICY_VERSION,
        "controlled_path_sha256": hashlib.sha256(
            controlled_path.encode("utf-8")
        ).hexdigest(),
        "tool_manifest_sha256": _proof_executable_manifest_digest(),
        "removed_environment_keys": removed,
        "retained_control_environment_keys": list(
            retained_control_environment
        ),
        "retained_control_environment_sha256": hashlib.sha256(
            json.dumps(
                retained_control_environment,
                sort_keys=True,
                separators=(",", ":"),
            ).encode("utf-8")
        ).hexdigest(),
        "enforced_environment_keys": sorted(enforced_environment),
        "enforced_environment_sha256": hashlib.sha256(
            json.dumps(
                enforced_environment,
                sort_keys=True,
                separators=(",", ":"),
            ).encode("utf-8")
        ).hexdigest(),
        "codex_control_environment_keys": list(
            codex_control_environment
        ),
        "codex_control_environment_sha256": hashlib.sha256(
            json.dumps(
                codex_control_environment,
                sort_keys=True,
                separators=(",", ":"),
            ).encode("utf-8")
        ).hexdigest(),
        "argv_control_keys": sorted(argv_controls),
        "argv_controls": argv_controls,
        "argv_control_sha256": hashlib.sha256(
            json.dumps(
                argv_controls,
                sort_keys=True,
                separators=(",", ":"),
            ).encode("utf-8")
        ).hexdigest(),
    }
    return sanitized, summary


def _proof_invocation_environment_is_safe(invocation):
    environment = {
        str(key).upper(): str(value)
        for key, value in (invocation.get("environment") or {}).items()
    }
    provenance = _environment_provenance(
        invocation.get("environment_provenance")
    )
    return (
        not any(
            _proof_environment_key_is_unsafe(key)
            for key in environment
        )
        and not provenance["ignore_environment"]
        and "PATH" not in provenance["unset_variables"]
    )


def _proof_runtime_environment_is_safe(invocation):
    if not _proof_invocation_environment_is_safe(invocation):
        return False
    environment = {
        str(key).upper(): str(value)
        for key, value in (invocation.get("environment") or {}).items()
    }
    groundwork_keys = {
        key for key in environment if key.startswith("GROUNDWORK_")
    }
    if not groundwork_keys.issubset(
        ALLOWED_GROUNDWORK_PROOF_ENVIRONMENT_KEYS
    ):
        return False
    repo_override = environment.get("GROUNDWORK_REPO")
    if repo_override is None:
        return True
    override_path = Path(repo_override)
    if (
        not override_path.is_absolute()
        or ".." in override_path.parts
        or "." in override_path.parts
        or str(override_path) != repo_override
    ):
        return False
    try:
        return override_path.resolve(strict=True) == REPO.resolve(strict=True)
    except OSError:
        return False


PROOF_SHELL_BUILTIN_WRAPPERS = {"builtin", "command", "exec"}
PROOF_SHELL_WRAPPERS = {"bash", "dash", "sh", "zsh"}


def _proof_executable_is_trusted(invocation):
    raw_executable = str(invocation.get("raw_executable") or "").strip()
    executable = str(invocation.get("executable") or "").lower()
    if not raw_executable or not executable:
        return False
    if executable == "run_runtime.py":
        return _is_canonical_groundwork_runtime_runner(invocation)
    if Path(raw_executable).name.lower() != executable:
        return False
    baseline = (
        PYTHON_EXECUTABLE_IDENTITIES.get(executable)
        if executable.startswith("python")
        else PROOF_EXECUTABLE_IDENTITIES.get(executable)
    )
    if baseline is None:
        return False
    candidate = (
        baseline["launcher_path"]
        if "/" not in raw_executable and "\\" not in raw_executable
        else raw_executable
    )
    return _proof_executable_identity_matches(candidate, baseline)


def _proof_command_wrappers_are_trusted(invocation):
    wrappers = invocation.get("command_wrappers") or []
    if not isinstance(wrappers, list):
        return False
    for wrapper in wrappers:
        if not isinstance(wrapper, dict):
            return False
        raw_executable = str(
            wrapper.get("raw_executable") or ""
        ).strip()
        executable = str(wrapper.get("executable") or "").lower()
        if executable in PROOF_SHELL_WRAPPERS:
            return False
        if executable in PROOF_SHELL_BUILTIN_WRAPPERS:
            if (
                raw_executable != executable
                or "/" in raw_executable
                or "\\" in raw_executable
            ):
                return False
        elif not _proof_executable_is_trusted(wrapper):
            return False
    return True


def _proof_invocation_uses_trusted_executable(invocation):
    return (
        _proof_command_wrappers_are_trusted(invocation)
        and _proof_executable_is_trusted(invocation)
    )


def _normalized_claim_root(value):
    return str(value or "").strip().rstrip("/")


def _claim_roots_are_independent(installed_root, source_root):
    installed_value = _normalized_claim_root(installed_root)
    source_value = _normalized_claim_root(source_root)
    if not installed_value or not source_value:
        return False
    installed_norm = os.path.normpath(installed_value)
    source_norm = os.path.normpath(source_value)
    if installed_norm == source_norm:
        return False
    normalized_paths = (Path(installed_norm), Path(source_norm))
    for child, parent in (
        normalized_paths,
        tuple(reversed(normalized_paths)),
    ):
        try:
            child.relative_to(parent)
        except ValueError:
            continue
        return False

    installed_path = Path(installed_value)
    source_path = Path(source_value)
    if installed_path.exists() and source_path.exists():
        try:
            installed_resolved = installed_path.resolve(strict=True)
            source_resolved = source_path.resolve(strict=True)
        except OSError:
            return False
        if installed_resolved == source_resolved:
            return False
        try:
            source_resolved.relative_to(installed_resolved)
        except ValueError:
            pass
        else:
            return False
        try:
            installed_resolved.relative_to(source_resolved)
        except ValueError:
            pass
        else:
            return False
    return True


def _equivalence_operands(args, allowed_options, value_options=()):
    operands = []
    index = 0
    while index < len(args):
        argument = args[index]
        if argument == "--":
            operands.extend(args[index + 1 :])
            break
        if argument in value_options:
            if index + 1 >= len(args):
                return None
            index += 2
            continue
        if argument.startswith("-"):
            if argument not in allowed_options:
                return None
            index += 1
            continue
        operands.append(argument)
        index += 1
    return operands


def _operands_bind_both_roots(operands, installed_root, source_root):
    if (
        len(operands) != 2
        or not _claim_roots_are_independent(
            installed_root, source_root
        )
    ):
        return False
    normalized_operands = {
        os.path.normpath(str(operand)) for operand in operands
    }
    return normalized_operands == {
        os.path.normpath(_normalized_claim_root(installed_root)),
        os.path.normpath(_normalized_claim_root(source_root)),
    }


def _source_equivalence_invocation_proves_match(
    activity, invocation, installed_root, source_root
):
    executable = invocation["executable"]
    args = invocation["args"]
    if (
        _has_help_or_version(args)
        or not _proof_invocation_environment_is_safe(invocation)
        or not _proof_invocation_uses_trusted_executable(invocation)
    ):
        return False
    if executable == "diff":
        allowed_options = {
            "-q",
            "-r",
            "-s",
            "-qr",
            "-rq",
            "--brief",
            "--recursive",
            "--report-identical-files",
        }
        operands = _equivalence_operands(args, allowed_options)
        if operands is None or not _operands_bind_both_roots(
            operands, installed_root, source_root
        ):
            return False
        return any(
            option in args
            for option in ("-r", "-qr", "-rq", "--recursive")
        )
    if executable == "git" and _git_subcommand(args) == "diff":
        unsafe_options = {
            argument
            for argument in args
            if argument.startswith("-")
            and argument
            not in {
                "--no-index",
                "--quiet",
                "--exit-code",
                "--no-ext-diff",
                "--",
            }
        }
        operands = [
            argument
            for argument in args
            if argument != "diff" and not argument.startswith("-")
        ]
        return (
            not unsafe_options
            and "--no-index" in args
            and _operands_bind_both_roots(
                operands, installed_root, source_root
            )
        )
    return False


def _source_equivalence_activity_matches_claim(activity, claim_values):
    installed_root = claim_values["installed_plugin_root"]
    source_root = claim_values["source_root"]
    invocations = command_invocations(activity["command"])
    return (
        len(invocations) == 1
        and _source_equivalence_invocation_proves_match(
            activity, invocations[0], installed_root, source_root
        )
    )


def _codex_plugin_tokens(invocation):
    if invocation["executable"] != "codex":
        return []
    remaining = _consume_option_prefix(
        invocation["args"],
        value_options={
            "-c",
            "--config",
            "-m",
            "--model",
            "-p",
            "--profile",
            "-C",
            "--cd",
        },
        attached_value_prefixes=("-c", "-m", "-p", "-C"),
        stop_options={"--help", "-h", "--version", "-V"},
    )
    if len(remaining) < 2 or remaining[0].lower() != "plugin":
        return []
    return remaining


def _codex_plugin_action(invocation):
    tokens = _codex_plugin_tokens(invocation)
    return tokens[1].lower() if tokens else ""


def _installed_plugin_identity(installed_root):
    installed_path = Path(
        os.path.normpath(_normalized_claim_root(installed_root))
    )
    for parent in installed_path.parents:
        if parent.name != "cache":
            continue
        try:
            relative_parts = installed_path.relative_to(parent).parts
        except ValueError:
            continue
        if len(relative_parts) != 3:
            continue
        marketplace, plugin, version = relative_parts[:3]
        if (
            marketplace != "groundwork"
            or plugin != "groundwork"
            or not version
        ):
            continue
        return {
            "marketplace": marketplace,
            "plugin": plugin,
            "version": version,
            "spec": f"{plugin}@{marketplace}",
        }
    return {}


def _codex_plugin_action_has_required_target(
    invocation, expected_spec
):
    tokens = _codex_plugin_tokens(invocation)
    if not tokens:
        return False
    action = tokens[1].lower()
    arguments = tokens[2:]
    if action == "list":
        return arguments in ([], ["--json"])
    if action not in {"add", "show"}:
        return False

    if action == "show":
        positionals = [
            argument for argument in arguments if argument != "--json"
        ]
        return (
            len(positionals) == 1
            and arguments.count("--json") <= 1
            and len(positionals) + arguments.count("--json")
            == len(arguments)
            and positionals[0].casefold()
            == str(expected_spec).casefold()
        )

    expected_plugin, separator, expected_marketplace = str(
        expected_spec
    ).partition("@")
    if not separator or not expected_plugin or not expected_marketplace:
        return False
    marketplace = ""
    seen_json = False
    positionals = []
    index = 0
    while index < len(arguments):
        argument = str(arguments[index])
        if argument == "--json":
            if seen_json:
                return False
            seen_json = True
            index += 1
            continue
        if argument in {"-m", "--marketplace"}:
            if index + 1 >= len(arguments) or marketplace:
                return False
            marketplace = str(arguments[index + 1])
            index += 2
            continue
        if argument.startswith("--marketplace="):
            if marketplace:
                return False
            marketplace = argument.split("=", 1)[1]
            if not marketplace:
                return False
            index += 1
            continue
        if argument.startswith("-m") and len(argument) > 2:
            if marketplace:
                return False
            marketplace = argument[2:]
            index += 1
            continue
        if argument.startswith("-"):
            return False
        positionals.append(argument)
        index += 1

    if len(positionals) != 1:
        return False
    target = positionals[0]
    if "@" in target:
        return (
            not marketplace
            and target.casefold() == str(expected_spec).casefold()
        )
    return (
        target.casefold() == expected_plugin.casefold()
        and marketplace.casefold() == expected_marketplace.casefold()
    )


def _activity_output_confirms_plugin(
    activity, installed_root, identity, action
):
    root = re.escape(_normalized_claim_root(installed_root))
    negative_status = re.compile(
        r"(?i)\b(?:diagnostic|disabled|error|failed|fatal|inactive|"
        r"ignored|missing|not[ \t]+"
        r"(?:active|installed|loaded|selected)|removed|unloaded|would[ \t]+"
        r"(?:install|load|select)|warn(?:ing)?)\b"
    )
    output = str(activity.get("output") or "")
    if negative_status.search(output):
        return False
    root_lines = [
        line
        for line in output.splitlines()
        if re.search(
            rf"(?<![A-Za-z0-9_.:/-]){root}(?![A-Za-z0-9_.:/-])",
            line,
        )
    ]
    if not root_lines:
        return False

    plugin = re.escape(str(identity.get("plugin") or ""))
    version = re.escape(str(identity.get("version") or ""))
    spec = re.escape(str(identity.get("spec") or ""))
    if not plugin or not version or not spec:
        return False

    def without_root(line):
        return re.sub(root, " ", line, flags=re.IGNORECASE)

    if action == "list":
        return any(
            (
                re.search(
                    rf"(?<![A-Za-z0-9_.-]){plugin}"
                    rf"(?![A-Za-z0-9_.-])",
                    without_root(line),
                    re.IGNORECASE,
                )
                and re.search(
                    rf"(?<![A-Za-z0-9_.-]){version}"
                    rf"(?![A-Za-z0-9_.-])",
                    without_root(line),
                    re.IGNORECASE,
                )
            )
            or re.search(
                rf"(?<![A-Za-z0-9_.@-]){spec}"
                rf"(?![A-Za-z0-9_.@-])",
                without_root(line),
                re.IGNORECASE,
            )
            for line in root_lines
        )

    positive_status = re.compile(
        r"(?i)\b(?:active|added|enabled|installed|loaded|selected)\b"
    )
    return any(
        positive_status.search(without_root(line))
        or re.search(
            rf"(?<![A-Za-z0-9_.@-]){spec}"
            rf"(?![A-Za-z0-9_.@-])",
            without_root(line),
            re.IGNORECASE,
        )
        for line in root_lines
    )


def _codex_plugin_activity_matches_claim(
    activity, claim_values, allowed_actions
):
    invocations = command_invocations(activity["command"])
    if len(invocations) != 1:
        return False
    invocation = invocations[0]
    if _has_help_or_version(invocation["args"]):
        return False
    unsafe_action_options = {
        "-n",
        "--check",
        "--dry-run",
        "--no-op",
        "--noop",
    }
    if any(
        argument in unsafe_action_options
        or argument.startswith("--dry-run=")
        or argument.startswith("--no-")
        for argument in invocation["args"]
    ):
        return False
    if (
        not _proof_invocation_environment_is_safe(invocation)
        or not _proof_invocation_uses_trusted_executable(invocation)
    ):
        return False
    codex_home = _codex_home_for_installed_root(
        claim_values["installed_plugin_root"]
    )
    identity = _installed_plugin_identity(
        claim_values["installed_plugin_root"]
    )
    action = _codex_plugin_action(invocation)
    configured_codex_home = str(
        (invocation.get("environment") or {}).get("CODEX_HOME") or ""
    )
    return (
        bool(codex_home)
        and bool(identity)
        and configured_codex_home == codex_home
        and action in allowed_actions
        and _codex_plugin_action_has_required_target(
            invocation, identity["spec"]
        )
        and _activity_output_confirms_plugin(
            activity,
            claim_values["installed_plugin_root"],
            identity,
            action,
        )
    )


def _codex_home_for_installed_root(installed_root):
    installed_path = Path(
        os.path.normpath(_normalized_claim_root(installed_root))
    )
    for parent in installed_path.parents:
        if parent.name == "cache" and parent.parent.name == "plugins":
            return str(parent.parent.parent)
    return ""


def _is_canonical_groundwork_runtime_runner(invocation):
    executable = invocation["executable"]
    args = invocation["args"]
    if executable.startswith("python"):
        script_and_args = _python_script_and_args(args)
        script = script_and_args[0] if script_and_args else ""
    elif executable == "run_runtime.py":
        script = str(invocation.get("raw_executable") or "")
    else:
        return False
    if not script:
        return False
    script_path = Path(script)
    if script_path.is_absolute():
        candidate = script_path
    else:
        if script_path.as_posix().lstrip("./") != "evals/run_runtime.py":
            return False
        candidate = REPO / script_path
    return candidate.resolve() == (REPO / "evals/run_runtime.py").resolve()


def _groundwork_runtime_invocation_uses_claim_roots(
    invocation, installed_root, _source_root
):
    codex_home = _codex_home_for_installed_root(installed_root)
    if not codex_home:
        return False
    configured_codex_home = str(
        (invocation.get("environment") or {}).get("CODEX_HOME") or ""
    )
    if configured_codex_home != codex_home:
        return False
    return (
        _proof_runtime_environment_is_safe(invocation)
        and _proof_invocation_uses_trusted_executable(invocation)
        and _is_canonical_groundwork_runtime_runner(invocation)
    )


def _normalized_trial_identifier(value):
    return re.sub(r"[^a-z0-9]+", "_", str(value or "").lower()).strip("_")


def _activity_trial_identifiers(activity):
    identifiers = {
        _normalized_trial_identifier(activity.get("command")),
    }
    for invocation in command_invocations(activity["command"]):
        executable = str(
            invocation.get("raw_executable") or invocation["executable"]
        )
        arguments = [str(argument) for argument in invocation.get("args") or []]
        identifiers.add(
            _normalized_trial_identifier(" ".join([executable, *arguments]))
        )
        identifiers.add(
            _normalized_trial_identifier(
                " ".join([str(invocation["executable"]), *arguments])
            )
        )
    return {identifier for identifier in identifiers if identifier}


def _nonruntime_chain_matches_trial(
    activation_activity, equivalence_activity, claim_values, trial
):
    trial_identifier = _normalized_trial_identifier(trial)
    if not trial_identifier:
        return False

    claim_type = str(claim_values.get("claim_type") or "").lower()
    action = ""
    activation_invocations = command_invocations(
        activation_activity["command"]
    )
    if len(activation_invocations) == 1:
        action = _codex_plugin_action(activation_invocations[0])

    identifiers = (
        _activity_trial_identifiers(activation_activity)
        | _activity_trial_identifiers(equivalence_activity)
        | {
            "equivalence",
            "source_equivalence",
            "plugin_equivalence",
            f"{claim_type}_equivalence",
        }
    )
    if claim_type.startswith("cache"):
        identifiers.add("cache_equivalence")
    if action in {"list", "show"}:
        identifiers.update(
            {
                "inventory",
                "plugin_inventory",
                f"{claim_type}_inventory",
                f"codex_plugin_{action}",
                f"plugin_{action}",
            }
        )
    elif action == "add":
        identifiers.update(
            {
                "refresh",
                "plugin_refresh",
                "refresh_plugin",
                "cache_refresh",
                "refresh_cache",
                f"{claim_type}_refresh",
                f"refresh_{claim_type}",
                "codex_plugin_add",
                "plugin_add",
            }
        )
    return trial_identifier in identifiers


def _runtime_activity_matches_trial(activity, claim_values, trial):
    installed_root = claim_values["installed_plugin_root"]
    source_root = claim_values["source_root"]
    all_invocations = command_invocations(activity["command"])
    if len(all_invocations) != 1:
        return False
    if not _runtime_activity_has_nonempty_success_summary(activity):
        return False
    runtime_invocations = [
        invocation
        for invocation in all_invocations
        if _is_groundwork_runtime_invocation(invocation)
        and _groundwork_runtime_invocation_uses_claim_roots(
            invocation, installed_root, source_root
        )
    ]
    if not runtime_invocations:
        return False
    summary = _runtime_activity_success_summary(activity)
    return any(
        _runtime_selector_matches_trial(
            invocation,
            summary,
            trial,
            run_scope=claim_values.get("run_scope"),
        )
        for invocation in runtime_invocations
    )


def _strict_unique_string_list(value, *, allow_empty=True):
    if not isinstance(value, list):
        return None
    if any(
        not isinstance(item, str) or not item.strip()
        for item in value
    ):
        return None
    normalized = [item.strip() for item in value]
    if len(normalized) != len(set(normalized)):
        return None
    if not allow_empty and not normalized:
        return None
    return normalized


def _runtime_activity_success_summary(activity):
    for line in str(activity.get("output") or "").splitlines():
        try:
            payload = json.loads(line)
        except json.JSONDecodeError:
            continue
        summary = payload.get("summary")
        if not isinstance(summary, dict):
            continue
        rows = summary.get("rows")
        failures = summary.get("failures")
        counts = summary.get("counts")
        suites = summary.get("suites")
        requested_suites = summary.get("requested_suites")
        prompt_files = summary.get("prompt_files")
        requested_case_ids = summary.get("requested_case_ids")
        executed_case_ids = summary.get("executed_case_ids")
        all_prompts = summary.get("all_prompts")
        rerun_failures = summary.get("rerun_failures")
        normalized_suites = _strict_unique_string_list(
            suites, allow_empty=False
        )
        normalized_requested_suites = _strict_unique_string_list(
            requested_suites
        )
        normalized_prompt_files = _strict_unique_string_list(
            prompt_files
        )
        normalized_requested_case_ids = _strict_unique_string_list(
            requested_case_ids
        )
        normalized_executed_case_ids = _strict_unique_string_list(
            executed_case_ids, allow_empty=False
        )
        if (
            type(rows) is int
            and rows > 0
            and isinstance(failures, list)
            and failures == []
            and isinstance(counts, dict)
            and set(counts) == {"pass"}
            and type(counts.get("pass")) is int
            and counts["pass"] >= 0
            and counts.get("pass") == rows
            and normalized_suites is not None
            and normalized_requested_suites is not None
            and normalized_prompt_files is not None
            and normalized_requested_case_ids is not None
            and normalized_executed_case_ids is not None
            and len(normalized_executed_case_ids) == rows
            and normalized_suites
            == normalized_requested_suites + normalized_prompt_files
            and type(all_prompts) is bool
            and isinstance(rerun_failures, str)
        ):
            return summary
    return None


def _runtime_activity_has_nonempty_success_summary(activity):
    return _runtime_activity_success_summary(activity) is not None


def _groundwork_runtime_cli_args(invocation):
    args = list(invocation.get("args") or [])
    if invocation["executable"].startswith("python"):
        script_and_args = _python_script_and_args(args)
        return script_and_args[1] if script_and_args else []
    return args


def _runtime_execution_selectors(invocation):
    args = _groundwork_runtime_cli_args(invocation)
    selectors = {
        "suites": [],
        "prompt_files": [],
        "groups": [],
        "case_ids": [],
        "all_prompts": False,
        "rerun_failures": [],
    }
    value_options = {
        "--suite",
        "--prompt-file",
        "--jobs",
        "--model",
        "--profile",
        "--codex-config",
        "--resource-policy",
        "--rerun-failures",
        "--group",
        "--case-timeout",
        "--retry-timeouts",
    }
    flag_options = {"--all-prompts", "--serial"}
    index = 0
    positional_only = False
    while index < len(args):
        argument = str(args[index])
        if positional_only:
            selectors["case_ids"].append(argument)
            index += 1
            continue
        if argument == "--":
            positional_only = True
            index += 1
            continue
        if argument in flag_options:
            if argument == "--all-prompts":
                selectors["all_prompts"] = True
            index += 1
            continue
        option = next(
            (
                candidate
                for candidate in value_options
                if argument.startswith(candidate + "=")
            ),
            "",
        )
        if option:
            value = argument.split("=", 1)[1]
            index += 1
        elif argument in value_options:
            if index + 1 >= len(args):
                return None
            option = argument
            value = str(args[index + 1])
            index += 2
        elif argument.startswith("-"):
            return None
        else:
            selectors["case_ids"].append(argument)
            index += 1
            continue
        if not value:
            return None
        if option == "--suite":
            selectors["suites"].append(normalize_suite_name(value))
        elif option == "--prompt-file":
            selectors["prompt_files"].append(canonical_prompt_file(value))
        elif option == "--group":
            selectors["groups"] = [value]
        elif option == "--rerun-failures":
            selectors["rerun_failures"] = [value]
    selectors["suites"] = unique_in_order(selectors["suites"])
    selectors["prompt_files"] = unique_in_order(
        selectors["prompt_files"]
    )
    selectors["case_ids"] = unique_in_order(selectors["case_ids"])
    return selectors


def _legacy_suite_identifier_aliases(value):
    name = normalize_suite_name(value)
    aliases = set()
    for identifier in {
        _normalized_trial_identifier(name),
        _normalized_trial_identifier(Path(name).stem),
    }:
        if identifier:
            aliases.update(
                {
                    identifier,
                    f"suite_{identifier}",
                    f"run_runtime_{identifier}",
                }
            )
    return aliases


def _runtime_selector_identifier_aliases(kind, value):
    raw_value = str(value or "").strip()
    if not raw_value:
        return set()
    if kind == "suite":
        suite_name = normalize_suite_name(raw_value)
        registered_suites = prompt_suites()
        if (
            suite_name != Path(suite_name).name
            or suite_name not in registered_suites
        ):
            return set()
        owners = {}
        for registered_suite in registered_suites:
            for alias in _legacy_suite_identifier_aliases(
                registered_suite
            ):
                owners.setdefault(alias, set()).add(registered_suite)
        return {
            f"suite:{suite_name}",
            *{
                alias
                for alias in _legacy_suite_identifier_aliases(suite_name)
                if owners.get(alias) == {suite_name}
            },
        }
    if kind == "prompt_file":
        return {f"prompt_file:{canonical_prompt_file(raw_value)}"}
    if kind == "group":
        return {f"group:{raw_value}"}
    if kind == "case_id":
        return {f"case_id:{raw_value}"}
    return set()


def _runtime_summary_matches_explicit_sources(selectors, summary):
    summary_suites = list(summary.get("suites") or [])
    summary_requested_suites = list(
        summary.get("requested_suites") or []
    )
    summary_prompt_files = list(summary.get("prompt_files") or [])
    summary_requested_case_ids = list(
        summary.get("requested_case_ids") or []
    )
    summary_executed_case_ids = list(
        summary.get("executed_case_ids") or []
    )

    if selectors["suites"] or selectors["prompt_files"]:
        expected_requested_suites = selectors["suites"]
        expected_prompt_files = selectors["prompt_files"]
    elif (
        selectors["all_prompts"]
        or selectors["case_ids"]
        or selectors["rerun_failures"]
    ):
        expected_requested_suites = prompt_suites()
        expected_prompt_files = []
    else:
        expected_requested_suites = list(DEFAULT_SUITES)
        expected_prompt_files = []

    if (
        summary_requested_suites != expected_requested_suites
        or summary_prompt_files != expected_prompt_files
        or summary_suites
        != expected_requested_suites + expected_prompt_files
        or summary.get("all_prompts") is not selectors["all_prompts"]
    ):
        return False

    expected_group = selectors["groups"][-1] if selectors["groups"] else None
    if summary.get("group") != expected_group:
        return False

    expected_rerun = (
        selectors["rerun_failures"][-1]
        if selectors["rerun_failures"]
        else ""
    )
    if str(summary.get("rerun_failures") or "") != expected_rerun:
        return False

    if selectors["case_ids"]:
        if selectors["rerun_failures"]:
            if not set(selectors["case_ids"]).issubset(
                summary_requested_case_ids
            ):
                return False
        elif summary_requested_case_ids != selectors["case_ids"]:
            return False
    elif not selectors["rerun_failures"] and summary_requested_case_ids:
        return False

    if summary_requested_case_ids and set(summary_executed_case_ids) != set(
        summary_requested_case_ids
    ):
        return False
    return True


def _runtime_scope_matches_selectors(selectors, run_scope):
    run_scope = str(run_scope or "").lower()
    has_targeted_selector = bool(
        selectors["suites"]
        or selectors["prompt_files"]
        or selectors["groups"]
        or selectors["case_ids"]
        or selectors["rerun_failures"]
    )
    if run_scope == "full":
        return selectors["all_prompts"] and not has_targeted_selector
    if run_scope == "targeted":
        return has_targeted_selector
    return False


def _runtime_selector_matches_trial(
    invocation, summary, trial, *, run_scope
):
    if not isinstance(summary, dict):
        return False
    selectors = _runtime_execution_selectors(invocation)
    if selectors is None or not _runtime_summary_matches_explicit_sources(
        selectors, summary
    ) or not _runtime_scope_matches_selectors(selectors, run_scope):
        return False
    trial_identifier = str(trial or "").strip()
    if not trial_identifier:
        return False
    if str(run_scope or "").lower() == "full":
        return trial_identifier in {
            "all_prompts",
            "full",
            "full_runtime",
            "run_runtime_all_prompts",
        }
    selector_values = (
        [("suite", value) for value in selectors["suites"]]
        + [
            ("prompt_file", value)
            for value in selectors["prompt_files"]
        ]
        + [("group", value) for value in selectors["groups"]]
        + [("case_id", value) for value in selectors["case_ids"]]
        + [
            ("case_id", value)
            for value in unique_in_order(
                list(summary.get("requested_case_ids") or [])
                + list(summary.get("executed_case_ids") or [])
            )
        ]
    )
    return any(
        trial_identifier
        in _runtime_selector_identifier_aliases(kind, value)
        for kind, value in selector_values
    )


def has_verified_groundwork_claim_evidence(stdout, claim_values):
    if not claim_values:
        return False
    claim_type = str(claim_values.get("claim_type") or "").lower()
    if claim_type not in {"runtime", "cache", "marketplace", "cache_refresh"}:
        return True
    required_provenance = [
        claim_values.get("installed_plugin_root"),
        claim_values.get("source_root"),
        claim_values.get("refresh_method"),
        claim_values.get("refresh_evidence"),
    ]
    trials = list(claim_values.get("commands_or_trials") or [])
    sentinel_values = {"", "unverified", "not_run", "not_applicable"}
    if (
        any(
            str(value or "").strip().lower() in sentinel_values
            for value in required_provenance
        )
        or not trials
    ):
        return False
    for root_field in ("installed_plugin_root", "source_root"):
        root_value = str(claim_values.get(root_field) or "")
        root_path = Path(root_value)
        if (
            not root_path.is_absolute()
            or ".." in root_path.parts
            or "." in root_path.parts
            or str(root_path) != root_value
        ):
            return False

    if not _claim_roots_are_independent(
        claim_values["installed_plugin_root"],
        claim_values["source_root"],
    ):
        return False

    all_activities = completed_tool_activities(stdout)
    successful_activities = [
        (index, activity)
        for index, activity in enumerate(all_activities)
        if activity["kind"] == "command_execution"
        and activity["succeeded"]
        and activity["has_result"]
        and command_success_is_attributable(activity["command"])
    ]
    refresh_method = str(claim_values["refresh_method"]).lower()
    allowed_plugin_actions = (
        {"add"}
        if refresh_method == "refresh_step"
        else {"list", "show"}
    )
    activation_activities = [
        (index, activity)
        for index, activity in successful_activities
        if _codex_plugin_activity_matches_claim(
            activity, claim_values, allowed_plugin_actions
        )
    ]
    equivalence_activities = [
        (index, activity)
        for index, activity in successful_activities
        if _source_equivalence_activity_matches_claim(
            activity, claim_values
        )
    ]
    qualifying_chains = [
        (
            activation_index,
            activation,
            equivalence_index,
            equivalence,
        )
        for activation_index, activation in activation_activities
        for equivalence_index, equivalence in equivalence_activities
        if equivalence_index == activation_index + 1
    ]
    if not qualifying_chains:
        return False
    if claim_type != "runtime":
        return any(
            all(
                _nonruntime_chain_matches_trial(
                    activation,
                    equivalence,
                    claim_values,
                    trial,
                )
                for trial in trials
            )
            for (
                _activation_index,
                activation,
                _equivalence_index,
                equivalence,
            ) in qualifying_chains
        )
    equivalence_chain_indexes = {
        equivalence_index
        for (
            _activation_index,
            _activation,
            equivalence_index,
            _equivalence,
        ) in qualifying_chains
    }
    return all(
        any(
            activity_index - 1 in equivalence_chain_indexes
            and _runtime_activity_matches_trial(
                activity, claim_values, trial
            )
            for activity_index, activity in successful_activities
        )
        for trial in trials
    )


def _target_value_matches(expected, observed):
    expected = str(expected or "").strip()
    observed = str(observed or "").strip()
    if not expected or not observed:
        return False
    return observed == expected


def _command_invocation_target_values(invocation):
    values = set()
    executable = invocation["executable"]
    args = list(invocation.get("args") or [])
    if executable == "playwright":
        positionals = _playwright_command_positionals(args)
        if positionals and positionals[0].lower() in {
            "open",
            "screenshot",
        } and len(positionals) >= 2:
            values.add(positionals[1].strip())
    elif executable in {
        "chromium",
        "chromium-browser",
        "google-chrome",
        "chrome-headless-shell",
    }:
        values.update(
            str(argument).strip()
            for argument in args
            if argument
            and not str(argument).startswith("-")
            and (
                "://" in str(argument)
                or str(argument).startswith(("/", "./"))
            )
        )
    return {value for value in values if value}


def has_observed_target_evidence(
    stdout, evidence_kind, target, *, require_success=False
):
    for activity in completed_tool_activities(stdout):
        if not activity["has_result"] or (
            require_success and not activity["succeeded"]
        ):
            continue
        if activity["kind"] == "command_execution":
            if require_success and not command_success_is_attributable(
                activity["command"]
            ):
                continue
            invocations = command_invocations(activity["command"])
            if evidence_kind == "browser" and len(invocations) != 1:
                continue
            for invocation in invocations:
                if evidence_kind == "browser" and _is_browser_invocation(
                    invocation
                ):
                    if (
                        _observed_invocation_uses_trusted_executable(
                            invocation
                        )
                        and _browser_command_output_is_substantive(
                            activity.get("output"),
                            invocation,
                        )
                        and any(
                            _target_value_matches(target, value)
                            for value in _command_invocation_target_values(
                                invocation
                            )
                        )
                    ):
                        return True
                if evidence_kind == "runtime" and _is_runtime_invocation(
                    invocation
                ):
                    if not _observed_runtime_activity_is_substantive(
                        activity, invocation
                    ):
                        continue
                    if _is_groundwork_runtime_invocation(invocation):
                        summary = _runtime_activity_success_summary(activity)
                        if _runtime_selector_matches_trial(
                            invocation,
                            summary,
                            target,
                            run_scope="targeted",
                        ):
                            return True
                    elif any(
                        _target_value_matches(target, value)
                        for value in _command_invocation_target_values(
                            invocation
                        )
                    ):
                        return True
        if (
            evidence_kind == "browser"
            and _structured_browser_activity(activity)
            and any(
                _target_value_matches(target, value)
                for value in _structured_activity_target_values(
                    activity
                )
            )
        ):
            return True
    return False


def _annotation_covered_external_targets(row):
    output_contract = {
        token.strip()
        for token in str(row.get("output_contract") or "").split("|")
        if token.strip()
    }
    if "annotation_carrythrough_verification" not in output_contract:
        return set()

    def parse_map(field):
        parsed = {}
        for item in str(row.get(field) or "").split("|"):
            if item.count("=") != 1:
                continue
            annotation_id, value = (
                part.strip() for part in item.split("=", 1)
            )
            if annotation_id and value:
                parsed[annotation_id] = value
        return parsed

    verdicts = parse_map("annotation_expected_carrythrough_verdicts")
    targets = parse_map("annotation_expected_observed_targets")
    external_targets = []
    for annotation_id, verdict in verdicts.items():
        if verdict != "covered":
            continue
        target = str(targets.get(annotation_id) or "").strip()
        lowered_target = target.lower()
        for evidence_kind in ("browser", "runtime"):
            prefix = evidence_kind + ":"
            if lowered_target.startswith(prefix) and target[len(prefix) :]:
                external_targets.append(
                    (
                        annotation_id,
                        evidence_kind,
                        target[len(prefix) :],
                    )
                )
    return external_targets


def _requires_uat_fixture_source_provenance(row):
    return (
        str(row.get("fixture") or "").rstrip("/")
        == "evals/fixtures/uat-evidence-window"
        and bool(re.fullmatch(r"uat-window-[A-Za-z0-9_.:-]+", str(row.get("id") or "")))
    )


def _required_fixture_source_files(row):
    suite = str(row.get("_suite") or "")
    fixture = str(row.get("fixture") or "").rstrip("/")
    row_id = str(row.get("id") or "")
    if suite == "prototype-annotation.csv":
        if row_id in {"prototype-annotation-001", "prototype-annotation-002"}:
            names = ("index.html",)
        elif row_id == "prototype-annotation-004":
            names = ("decision-source.md", "visual-packet.md")
        else:
            names = ("decision-source.md",)
        return [REPO / fixture / name for name in names]
    output_tokens = {
        token.strip()
        for token in str(row.get("output_contract") or "").split("|")
        if token.strip()
    }
    if "contract_lineage" in output_tokens and fixture:
        return [REPO / fixture / "SCENARIO.md"]
    return []


def _fixture_source_argument_matches(argument, source_file):
    raw_argument = str(argument or "").strip()
    expected = Path(source_file).resolve()
    if not raw_argument:
        return False
    aliases = {expected.name, f"./{expected.name}", str(expected)}
    try:
        relative = expected.relative_to(REPO.resolve()).as_posix()
    except ValueError:
        relative = ""
    if relative:
        aliases.update({relative, f"./{relative}"})
    return raw_argument in aliases


STRUCTURED_ACTIVITY_TARGET_KEYS = {
    "file",
    "file_path",
    "filepath",
    "page_id",
    "pageid",
    "path",
    "ref_id",
    "resource_uri",
    "stable_target_id",
    "tab_id",
    "tabid",
    "target",
    "target_id",
    "targetid",
    "uri",
    "url",
}
STRUCTURED_ACTIVITY_REQUEST_CONTAINERS = {
    "args",
    "arguments",
    "input",
    "item",
    "parameters",
    "params",
    "request",
    "request_data",
}


def _structured_activity_target_values(activity, *, include_result=False):
    values = set()

    def visit(value, *, allow_containers):
        if not isinstance(value, dict):
            return
        for raw_key, child in value.items():
            key = re.sub(
                r"[^a-z0-9]+", "_", str(raw_key).casefold()
            ).strip("_")
            if (
                key in STRUCTURED_ACTIVITY_TARGET_KEYS
                and isinstance(child, (str, int))
                and not isinstance(child, bool)
                and str(child).strip()
            ):
                values.add(str(child).strip())
            if key in STRUCTURED_ACTIVITY_REQUEST_CONTAINERS or (
                include_result and key in {"result", "output"}
            ):
                if isinstance(child, dict):
                    visit(child, allow_containers=True)
                elif isinstance(child, list):
                    for item in child:
                        visit(item, allow_containers=True)

    visit(_activity_detail_payload(activity), allow_containers=True)
    return values


def _fixture_source_target_aliases(source_file):
    expected = Path(source_file).resolve()
    candidates = {str(expected), expected.as_uri()}
    try:
        relative = expected.relative_to(REPO.resolve()).as_posix()
    except ValueError:
        relative = ""
    if relative:
        candidates.update({relative, f"./{relative}"})
    return candidates


def _structured_activity_targets_fixture_source(activity, source_file):
    return bool(
        _structured_activity_target_values(activity)
        .intersection(_fixture_source_target_aliases(source_file))
    )


def _is_passive_fixture_read_invocation(invocation, source_file):
    executable = invocation["executable"]
    args = list(invocation.get("args") or [])
    if executable == "cat":
        operands = [argument for argument in args if argument != "--"]
        return (
            bool(operands)
            and all(
                argument != "-" and not str(argument).startswith("-")
                for argument in operands
            )
            and any(
                _fixture_source_argument_matches(argument, source_file)
                for argument in operands
            )
        )
    if executable == "sed":
        return (
            len(args) == 3
            and args[0] in {"-n", "--quiet", "--silent"}
            and re.fullmatch(
                r"(?:[0-9]+|\$)(?:,(?:[0-9]+|\$))?p",
                str(args[1]),
            )
            is not None
            and _fixture_source_argument_matches(args[2], source_file)
        )
    return False


def has_required_fixture_source_evidence(stdout, source_files):
    remaining = {
        Path(source_file).resolve(): Path(source_file).read_text(
            encoding="utf-8"
        ).strip()
        for source_file in source_files
        if Path(source_file).is_file()
    }
    if len(remaining) != len(source_files):
        return False
    for activity in completed_tool_activities(stdout):
        if (
            not activity["succeeded"]
            or not activity["has_result"]
            or not str(activity.get("output") or "").strip()
        ):
            continue
        if activity["kind"] == "command_execution":
            if not command_success_is_attributable(activity["command"]):
                continue
            invocations = command_invocations(activity["command"])
            if len(invocations) != 1:
                continue
            for source_file, canonical_content in list(remaining.items()):
                if (
                    _is_passive_fixture_read_invocation(
                        invocations[0], source_file
                    )
                    and _observed_invocation_uses_trusted_executable(
                        invocations[0]
                    )
                    and str(activity.get("output") or "").strip()
                    == canonical_content
                ):
                    remaining.pop(source_file)
        elif _structured_source_activity(activity):
            observed_content = _structured_source_content(activity)
            for source_file, canonical_content in list(remaining.items()):
                if (
                    _structured_activity_targets_fixture_source(
                        activity, source_file
                    )
                    and str(observed_content or "").strip()
                    == canonical_content
                ):
                    remaining.pop(source_file)
        if not remaining:
            return True
    return not remaining


def _output_contains_uat_record_section(output, row_id):
    records_path = (
        REPO / "evals/fixtures/uat-evidence-window/records.md"
    )
    if not records_path.is_file():
        return False
    try:
        observed_section = canonical_uat_record_section_text(
            str(output or ""), row_id
        )
        canonical_section = canonical_uat_record_section_text(
            records_path.read_text(encoding="utf-8"), row_id
        )
    except ValueError:
        return False
    return observed_section.strip() == canonical_section.strip()


def has_uat_fixture_source_evidence(stdout, row_id):
    row_id = str(row_id or "")
    if not row_id:
        return False
    for activity in completed_tool_activities(stdout):
        if (
            not activity["succeeded"]
            or not activity["has_result"]
        ):
            continue
        if activity["kind"] == "command_execution":
            observed_content = str(activity.get("output") or "")
            if not _output_contains_uat_record_section(
                observed_content, row_id
            ):
                continue
            if not command_success_is_attributable(activity["command"]):
                continue
            invocations = command_invocations(activity["command"])
            if len(invocations) != 1:
                continue
            records_path = (
                REPO / "evals/fixtures/uat-evidence-window/records.md"
            )
            if any(
                _is_passive_fixture_read_invocation(
                    invocation, records_path
                )
                and _observed_invocation_uses_trusted_executable(
                    invocation
                )
                for invocation in invocations
            ):
                return True
        elif _structured_source_activity(activity):
            observed_content = _structured_source_content(activity)
            if not _output_contains_uat_record_section(
                observed_content, row_id
            ):
                continue
            records_path = (
                REPO / "evals/fixtures/uat-evidence-window/records.md"
            )
            if _structured_activity_targets_fixture_source(
                activity, records_path
            ):
                return True
    return False


def dispatch_default_read_path_violations(stdout):
    violations = []
    for command in completed_command_execution_commands(stdout):
        if re.search(r"(?:^|/)\.codex/memories(?:/|$)", command):
            violations.append("external memory read")
        if re.search(r"\brg\s+--files\b|\bfind\s+\.(?:\s|$)|\bls\s+(?:-[^\s]*R\b|--recursive\b)", command):
            violations.append("broad workspace scan")
        for match in re.finditer(r"skills/dispatch/([A-Za-z0-9_.-]+\.md)", command):
            if match.group(1) not in DISPATCH_DEFAULT_ALLOWED_REFERENCE_FILES:
                violations.append(f"unexpected dispatch reference {match.group(1)}")
    return unique_in_order(violations)


def output_contract_verdict(row, schema, actual, final_response):
    notes = []
    failures = []
    tokens = schema["output_contract"]
    future_tokens = schema["output_contract_future_tokens"]

    if future_tokens:
        append_failure(
            failures,
            notes,
            "future_output_contract",
            "measurement_token",
            "future output contract token blocked until implemented: " + "|".join(future_tokens),
        )

    for token in tokens:
        if token == "none" or token in future_tokens:
            continue
        if token == "verify_scope":
            if first_nonempty_line(final_response) != "Verification Scope":
                append_failure(
                    failures,
                    notes,
                    "output_contract_failure",
                    "skill_output_contract",
                    "verify final message is not scope-first",
                )
            missing_scope_fields = missing_verify_scope_fields(final_response)
            if missing_scope_fields:
                append_failure(
                    failures,
                    notes,
                    "output_contract_failure",
                    "skill_output_contract",
                    "verify scope block missing fields: " + ", ".join(missing_scope_fields),
                )
        elif token == "gate_fields":
            if not has_gate_fields_or_direct_runtime_equivalent(row, actual, final_response):
                missing = missing_required_fields(final_response, GATE_FIELDS)
                append_failure(
                    failures,
                    notes,
                    "output_contract_failure",
                    "skill_output_contract",
                    "missing gate fields: " + ", ".join(missing),
                )
            if forbidden_git_add_dot_suggestion(final_response):
                append_failure(
                    failures,
                    notes,
                    "output_contract_failure",
                    "skill_output_contract",
                    "forbidden git add . suggestion",
                )
        elif token == "implementation_result":
            if not has_compact_implementation_result(final_response) and not has_blocked_implementation_conformance(
                final_response
            ):
                append_failure(
                    failures,
                    notes,
                    "output_contract_failure",
                    "skill_output_contract",
                    "implementation result is missing outcome, files, checks, or remaining-risk semantics",
                )
        elif token == "implementation_conformance":
            missing = missing_required_fields(final_response, CONFORMANCE_FIELDS)
            if (
                missing
                and not has_compact_implementation_conformance(final_response)
                and not has_blocked_implementation_conformance(final_response)
            ):
                append_failure(
                    failures,
                    notes,
                    "output_contract_failure",
                    "skill_output_contract",
                    "implementation conformance is missing structured fields or compact findings/evidence/gaps/boundary semantics: "
                    + ", ".join(missing),
                )
        elif token == "qa_fix_qa":
            missing = missing_required_fields(final_response, QA_FAILURE_FIELDS)
            if missing:
                append_failure(
                    failures,
                    notes,
                    "output_contract_failure",
                    "skill_output_contract",
                    "QA Failure block missing fields: " + ", ".join(missing),
                )
        elif token == "qa_gap_closure_gate":
            gate_failures = qa_gap_closure_gate_failures(final_response)
            for gate_failure in gate_failures:
                append_failure(
                    failures,
                    notes,
                    "output_contract_failure",
                    "requirement_state_gate",
                    gate_failure,
                )
        elif token == "contract_lineage":
            for lineage_failure in contract_lineage_failures(final_response, row):
                append_failure(
                    failures,
                    notes,
                    "output_contract_failure",
                    "skill_output_contract",
                    lineage_failure,
                )
            for companion_failure in contract_lineage_route_companion_failures(
                final_response, actual, row
            ):
                append_failure(
                    failures,
                    notes,
                    "output_contract_failure",
                    "skill_output_contract",
                    companion_failure,
                )
        elif token == "annotation_carrythrough_verification":
            for annotation_failure in annotation_carrythrough_verification_failures(
                final_response, row
            ):
                append_failure(
                    failures,
                    notes,
                    "output_contract_failure",
                    "skill_output_contract",
                    annotation_failure,
                )
        elif token == "annotation_handoff_reference":
            for annotation_failure in annotation_handoff_reference_failures(
                final_response, row
            ):
                append_failure(
                    failures,
                    notes,
                    "output_contract_failure",
                    "skill_output_contract",
                    annotation_failure,
                )
        elif token == "annotation_presentation_decision":
            for annotation_failure in annotation_presentation_decision_failures(
                final_response, row
            ):
                append_failure(
                    failures,
                    notes,
                    "output_contract_failure",
                    "skill_output_contract",
                    annotation_failure,
                )
        elif token == "release_evidence_claim":
            for release_claim_failure in release_evidence_claim_failures(
                final_response, row
            ):
                append_failure(
                    failures,
                    notes,
                    "output_contract_failure",
                    "skill_output_contract",
                    release_claim_failure,
                )
        elif token == "uat_evidence_window":
            for uat_window_failure in uat_evidence_window_failures(
                final_response, row
            ):
                append_failure(
                    failures,
                    notes,
                    "output_contract_failure",
                    "skill_output_contract",
                    uat_window_failure,
                )
        elif token == "uat_evidence_window_forbidden":
            for uat_window_failure in uat_evidence_window_absence_failures(
                final_response, row
            ):
                append_failure(
                    failures,
                    notes,
                    "output_contract_failure",
                    "skill_output_contract",
                    uat_window_failure,
                )
        elif token == "uat_handoff_reference":
            for uat_handoff_failure in uat_handoff_reference_failures(
                final_response, row
            ):
                append_failure(
                    failures,
                    notes,
                    "output_contract_failure",
                    "skill_output_contract",
                    uat_handoff_failure,
                )
        elif token in {
            "prototype_iteration_checkpoint",
            "prototype_no_delta_stop",
            "prototype_one_shot",
            "spec_single_question",
            "spec_writeback",
            "spec_no_delta_stop",
            "spec_clear_fast_path",
            "spec_gap_list",
            "checkpoint_before_risky_action",
        }:
            loop_checkers = {
                "prototype_iteration_checkpoint": prototype_iteration_checkpoint_failures,
                "prototype_no_delta_stop": prototype_no_delta_stop_failures,
                "prototype_one_shot": prototype_one_shot_failures,
                "spec_single_question": spec_single_question_failures,
                "spec_writeback": spec_writeback_failures,
                "spec_no_delta_stop": spec_no_delta_stop_failures,
                "spec_clear_fast_path": spec_clear_fast_path_failures,
                "spec_gap_list": spec_gap_list_failures,
                "checkpoint_before_risky_action": checkpoint_before_risky_action_failures,
            }
            if token == "spec_clear_fast_path":
                loop_failures = loop_checkers[token](
                    final_response, schema["expected_best"]
                )
            else:
                loop_failures = loop_checkers[token](final_response)
            for loop_failure in loop_failures:
                append_failure(
                    failures,
                    notes,
                    "output_contract_failure",
                    "skill_output_contract",
                    loop_failure,
                )
        elif token == "artifact_header":
            missing = missing_required_fields(final_response, ARTIFACT_HEADER_FIELDS)
            if missing:
                append_failure(
                    failures,
                    notes,
                    "output_contract_failure",
                    "skill_output_contract",
                    "artifact header check missing fields: " + ", ".join(missing),
                )
        elif token == "prototype_contract_boundary":
            if not has_prototype_contract_boundary(final_response):
                append_failure(
                    failures,
                    notes,
                    "output_contract_failure",
                    "skill_output_contract",
                    "prototype contract boundary signal missing",
                )
        elif token == "entry_decision":
            if not final_response.strip():
                append_failure(
                    failures,
                    notes,
                    "output_contract_failure",
                    "skill_output_contract",
                    "entry decision output is empty",
                )
        elif token == "trajectory_signal":
            if actual == DIRECT_ROUTE and schema["expected_best"] != DIRECT_ROUTE:
                append_failure(
                    failures,
                    notes,
                    "output_contract_failure",
                    "skill_output_contract",
                    "trajectory signal missing because workflow route fell back to direct",
                )
        elif token == "dispatch_compact_default":
            metrics = dispatch_visible_output_metrics(final_response)
            if not dispatch_starts_at_package(final_response):
                append_failure(
                    failures,
                    notes,
                    "output_contract_failure",
                    "skill_output_contract",
                    "dispatch compact-default package must start at dispatch_version: 2 with no prose preamble",
                )
            if not dispatch_package_is_complete(final_response):
                append_failure(
                    failures,
                    notes,
                    "output_contract_failure",
                    "skill_output_contract",
                    "dispatch compact-default package is missing required completeness markers",
                )
            if (
                metrics["characters"] > DISPATCH_COMPACT_MAX_CHARACTERS
                or metrics["nonempty_lines"] > DISPATCH_COMPACT_MAX_NONEMPTY_LINES
            ):
                append_failure(
                    failures,
                    notes,
                    "output_contract_failure",
                    "skill_output_contract",
                    "dispatch compact-default budget exceeded: "
                    f"{metrics['characters']} characters / {metrics['nonempty_lines']} non-empty lines",
                )
        elif token == "dispatch_complete_or_split":
            metrics = dispatch_visible_output_metrics(final_response)
            within_compact_budget = (
                metrics["characters"] <= DISPATCH_COMPACT_MAX_CHARACTERS
                and metrics["nonempty_lines"] <= DISPATCH_COMPACT_MAX_NONEMPTY_LINES
            )
            complete_within_budget = dispatch_package_is_complete(final_response) and within_compact_budget
            compact_split = dispatch_has_explicit_split(final_response) and within_compact_budget
            if not dispatch_starts_at_package(final_response) or not (complete_within_budget or compact_split):
                append_failure(
                    failures,
                    notes,
                    "output_contract_failure",
                    "skill_output_contract",
                    "dispatch overflow must return a complete package or explicit needs_split decision with next action; "
                    "a complete package must remain within the compact budget",
                )

    if future_tokens:
        return "blocked", notes, failures
    if failures:
        return "fail", notes, failures
    return "pass", notes, failures


def evidence_verdict(
    row,
    schema,
    actual,
    final_response,
    changes,
    stdout,
    *,
    case_workspace=None,
    proof_execution_context=None,
):
    notes = []
    failures = []
    tokens = schema["evidence_required"]
    future_tokens = schema["evidence_required_future_tokens"]
    claim_values = release_evidence_claim_values(final_response)
    claim_status = str(
        (claim_values or {}).get("evidence_status") or ""
    ).lower()
    claim_type = str(
        (claim_values or {}).get("claim_type") or ""
    ).lower()
    allow_unverified_boundary = claim_status != "verified"
    bypassed_hook_trust = bool(
        (
            (proof_execution_context or {}).get(
                "argv_controls"
            )
            or {}
        ).get("hook_trust_bypass")
    )
    if claim_status == "verified" and bypassed_hook_trust:
        append_failure(
            failures,
            notes,
            "evidence_failure",
            "evidence_collection",
            "verified claims are unavailable when the explicit hook trust bypass is active",
        )
    if (
        claim_status == "verified"
        and claim_type in {"runtime", "cache", "marketplace", "cache_refresh"}
        and not has_verified_groundwork_claim_evidence(stdout, claim_values)
    ):
        append_failure(
            failures,
            notes,
            "evidence_failure",
            "evidence_collection",
            "verified Groundwork plugin-bound claim is not tied to the installed "
            "root, source refresh/equivalence activity, and any required installed-root runtime trial",
        )
    if claim_status == "verified" and claim_type == "release":
        append_failure(
            failures,
            notes,
            "evidence_failure",
            "evidence_collection",
            "verified release claims require an external maintainer decision "
            "and release evidence adapter; the deterministic runner cannot self-verify them",
        )
    if claim_status == "verified" and claim_type == "uat":
        if not _requires_uat_fixture_source_provenance(row):
            append_failure(
                failures,
                notes,
                "evidence_failure",
                "evidence_collection",
                "verified UAT claims require a claim-specific canonical UAT evidence adapter",
            )
        elif not has_uat_fixture_source_evidence(
            stdout, row.get("id")
        ):
            append_failure(
                failures,
                notes,
                "evidence_failure",
                "evidence_collection",
                "verified UAT claim is missing its canonical records.md section evidence",
            )
    for (
        _annotation_id,
        evidence_kind,
        target,
    ) in _annotation_covered_external_targets(row):
        if not has_observed_target_evidence(
            stdout, evidence_kind, target, require_success=True
        ):
            append_failure(
                failures,
                notes,
                "evidence_failure",
                "evidence_collection",
                f"covered annotation {evidence_kind} target requires successful observed {evidence_kind} activity",
            )

    if future_tokens:
        append_failure(
            failures,
            notes,
            "future_evidence_required",
            "measurement_token",
            "future evidence token blocked until implemented: " + "|".join(future_tokens),
        )

    for token in tokens:
        if token == "none" or token in future_tokens:
            continue
        if token == "no_file_changes":
            relevant_changes = changes_relevant_to_no_file_evidence(row, actual, changes)
            if relevant_changes:
                append_failure(
                    failures,
                    notes,
                    "evidence_failure",
                    "evidence_collection",
                    "expected no file changes, saw: " + "; ".join(relevant_changes[:5]),
                )
        elif token == "dispatch_default_read_path":
            violations = dispatch_default_read_path_violations(stdout)
            if violations:
                append_failure(
                    failures,
                    notes,
                    "evidence_failure",
                    "evidence_collection",
                    "dispatch compact-default eval read path violated: " + ", ".join(violations),
                )
        elif token == "gate_observed":
            if not has_gate_fields_or_direct_runtime_equivalent(row, actual, final_response):
                missing = [field for field in GATE_FIELDS if field not in final_response]
                append_failure(
                    failures,
                    notes,
                    "evidence_failure",
                    "evidence_collection",
                    "gate evidence missing fields: " + ", ".join(missing),
                )
        elif token == "git_status":
            if not any(
                activity["kind"] == "command_execution"
                and activity["succeeded"]
                and command_success_is_attributable(activity["command"])
                and _git_status_activity_targets_workspace(
                    activity,
                    case_workspace,
                )
                for activity in completed_tool_activities(stdout)
            ):
                append_failure(
                    failures,
                    notes,
                    "evidence_failure",
                    "evidence_collection",
                    "missing real git status evidence",
                )
        elif token == "raw_intent_no_implementation":
            relevant_changes = changes_relevant_to_raw_intent_implementation(row, actual, changes, final_response)
            if actual in IMPLEMENTATION_READY_ROUTES or relevant_changes:
                append_failure(
                    failures,
                    notes,
                    "evidence_failure",
                    "evidence_collection",
                    "raw intent entered implementation-ready path",
                )
        elif token == "direct_fallback_no_artifact":
            if actual != DIRECT_ROUTE:
                append_failure(
                    failures,
                    notes,
                    "evidence_failure",
                    "evidence_collection",
                    f"direct fallback expected but actual route was {actual}",
                )
            if changes:
                append_failure(
                    failures,
                    notes,
                    "evidence_failure",
                    "evidence_collection",
                    "direct fallback changed files: " + "; ".join(changes[:5]),
                )
        elif token == "source_or_unverified":
            uat_fixture_provenance = _requires_uat_fixture_source_provenance(row)
            required_source_files = _required_fixture_source_files(row)
            if uat_fixture_provenance:
                observed_source = has_uat_fixture_source_evidence(
                    stdout, row.get("id")
                )
            elif required_source_files:
                observed_source = has_required_fixture_source_evidence(
                    stdout, required_source_files
                )
            else:
                observed_source = has_observed_evidence(
                    stdout, "source", require_success=True
                )
            if not observed_source and not (
                allow_unverified_boundary
                and has_source_or_unverified_evidence(final_response)
            ):
                if uat_fixture_provenance:
                    missing_note = (
                        "missing source evidence from records.md section "
                        + str(row.get("id") or "")
                    )
                elif required_source_files:
                    missing_note = (
                        "missing canonical fixture source evidence from: "
                        + ", ".join(
                            source_file.name
                            for source_file in required_source_files
                        )
                    )
                else:
                    missing_note = (
                        "missing source evidence or explicit unverified source boundary"
                    )
                append_failure(
                    failures,
                    notes,
                    "evidence_failure",
                    "evidence_collection",
                    missing_note,
                )
        elif token == "tests_or_unverified":
            observed_tests = has_observed_evidence(
                stdout, "tests", require_success=True
            ) or has_observed_expected_test_failure(
                stdout, row, final_response
            )
            if not observed_tests and not (
                allow_unverified_boundary
                and has_tests_or_unverified_evidence(final_response)
            ):
                append_failure(
                    failures,
                    notes,
                    "evidence_failure",
                    "evidence_collection",
                    "missing test evidence or explicit unverified test boundary",
                )
        elif token == "browser_or_unverified":
            if not has_observed_evidence(
                stdout, "browser", require_success=True
            ) and not (
                allow_unverified_boundary
                and has_browser_or_unverified_evidence(final_response)
            ):
                append_failure(
                    failures,
                    notes,
                    "evidence_failure",
                    "evidence_collection",
                    "missing browser evidence or explicit unverified browser boundary",
                )
        elif token == "runtime_or_unverified":
            if not has_observed_evidence(
                stdout, "runtime", require_success=True
            ) and not (
                allow_unverified_boundary
                and has_runtime_or_unverified_evidence(final_response)
            ):
                append_failure(
                    failures,
                    notes,
                    "evidence_failure",
                    "evidence_collection",
                    "missing runtime evidence or explicit unverified runtime boundary",
                )

    if future_tokens:
        return "blocked", notes, failures
    if failures:
        return "fail", notes, failures
    return "pass", notes, failures


def behavior_verdict(
    row,
    schema,
    actual,
    final_response,
    changes,
    lifecycle_errors,
    case_validation_errors=None,
):
    notes = []
    failures = []
    expected = schema["expected_best"]
    requirement_state = schema["requirement_state"]

    if lifecycle_errors:
        append_failure(
            failures,
            notes,
            "forbidden_behavior",
            "behavior_contract",
            "lifecycle artifact shape errors: " + "; ".join(lifecycle_errors[:5]),
        )

    for error in case_validation_errors or []:
        append_failure(
            failures,
            notes,
            "forbidden_behavior",
            "fixture_behavior_contract",
            error,
        )

    if boolish(row.get("risky_write_requested")) and changes:
        append_failure(
            failures,
            notes,
            "forbidden_behavior",
            "behavior_contract",
            "risky prompt wrote files: " + "; ".join(changes[:5]),
        )

    if expected == DIRECT_ROUTE and actual == DIRECT_ROUTE and direct_fallback_ceremony_present(final_response):
        append_failure(
            failures,
            notes,
            "direct_fallback_ceremony",
            "direct_fallback_boundary",
            "direct fallback used Groundwork ceremony",
        )

    if (
        "raw_intent_no_implementation" in schema["evidence_required"]
        and requirement_state in {"raw", "prd_draft"}
        and (
            actual in IMPLEMENTATION_READY_ROUTES
            or changes_relevant_to_raw_intent_implementation(row, actual, changes, final_response)
        )
    ):
        append_failure(
            failures,
            notes,
            "premature_implementation",
            "requirement_state_gate",
            "raw or draft requirement entered implementation before acceptance or explicit bypass",
        )

    forbidden_behavior = str(row.get("forbidden_behavior") or "").strip()
    if forbidden_behavior and forbidden_behavior.lower() in final_response.lower():
        append_failure(
            failures,
            notes,
            "forbidden_behavior",
            "behavior_contract",
            "forbidden behavior text appeared in response",
        )

    route_boundary = schema["route_boundary"]
    if route_boundary == "verify-code-diff-only" and has_diff_only_readiness_pass_claim(final_response):
        append_failure(
            failures,
            notes,
            "forbidden_behavior",
            "behavior_contract",
            "code-diff-only row claimed pass or readiness",
        )

    if route_boundary == "clean-review-low-risk-exception" and has_archive_or_branch_cleanup_ready_claim(final_response):
        append_failure(
            failures,
            notes,
            "forbidden_behavior",
            "behavior_contract",
            "low-risk exception claimed archive or branch cleanup readiness",
        )

    if route_boundary.startswith(("clean-review", "review-loop")):
        review_loop_result = check_review_loop_claims(final_response)
        if review_loop_result["verdict"] != "pass":
            append_failure(
                failures,
                notes,
                "forbidden_behavior",
                review_loop_result.get("fix_locus", "behavior_contract"),
                f"{review_loop_result['checker_id']}: "
                + "; ".join(review_loop_result.get("notes") or []),
            )

    if route_boundary == "clean-review-parent-context-fork":
        if not has_clean_review_parent_context_fork_disclosure(final_response):
            append_failure(
                failures,
                notes,
                "forbidden_behavior",
                "behavior_contract",
                "missing parent full-history fork disclosure",
            )
        if not has_clean_review_nested_delegation_disclosure(final_response):
            append_failure(
                failures,
                notes,
                "forbidden_behavior",
                "behavior_contract",
                "missing nested delegation or child-thread disclosure",
            )
        if not has_clean_review_blocked_or_unverified_boundary(final_response):
            append_failure(
                failures,
                notes,
                "forbidden_behavior",
                "behavior_contract",
                "missing unverified or blocked clean-review boundary",
            )
        if has_clean_review_pass_claim(final_response):
            append_failure(
                failures,
                notes,
                "forbidden_behavior",
                "behavior_contract",
                "forked or nested reviewer output claimed clean-review pass",
            )

    forbidden_output_markers = parse_pipe_list(
        row.get("forbidden_output_markers"),
        "forbidden_output_markers",
        row,
        blank_default=[],
    )
    if any(marker.lower() in final_response.lower() for marker in forbidden_output_markers):
        append_failure(
            failures,
            notes,
            "forbidden_behavior",
            "lifecycle_artifact_boundary",
            "response contains a forbidden output marker",
        )

    if has_gsd_creation_intent(final_response, changes):
        append_failure(
            failures,
            notes,
            "forbidden_behavior",
            "lifecycle_artifact_boundary",
            "response proposed creating .planning or .gsd lifecycle paths",
        )

    if failures:
        return "fail", notes, failures
    return "pass", notes, failures


def routing_verdict_details(row, schema, actual):
    notes = []
    failures = []
    expected = schema["expected_best"]
    acceptable_routes = schema["acceptable_routes"]
    forbidden_routes = schema["forbidden_routes"]
    load_required = boolish(row.get("skill_load_required", True))

    if actual == UNKNOWN_ROUTE:
        notes.append("authoritative skill-load evidence is unavailable")
        return "blocked", notes, [("route_evidence_missing", "runtime_observability")]
    if actual in forbidden_routes:
        append_failure(
            failures,
            notes,
            "forbidden_route",
            "routing_surface",
            f"forbidden route hit: {actual}",
        )
    elif actual not in acceptable_routes:
        append_failure(
            failures,
            notes,
            "route_miss",
            "routing_surface",
            f"expected route in {acceptable_routes}, loaded {actual}",
        )
    elif expected != DIRECT_ROUTE and load_required and actual == DIRECT_ROUTE:
        append_failure(
            failures,
            notes,
            "route_miss",
            "routing_surface",
            f"expected {expected}, loaded direct",
        )

    if failures:
        return "fail", notes, failures
    return "pass", notes, failures


def host_preemption_verdict_details(row, actual, final_response, changes):
    notes = []
    failures = []
    allowed = host_preemption_allowed(row)
    has_intent = has_host_preemption_intent(row)
    has_gate_shape = has_no_execution_gate_shape(final_response)

    if actual == HOST_PREEMPTION_ROUTE:
        if not allowed:
            append_failure(
                failures,
                notes,
                "invalid_host_preemption",
                "runtime_safety_gate",
                "runtime-safety-gate classified without row permission",
            )
        if not has_intent:
            append_failure(
                failures,
                notes,
                "invalid_host_preemption",
                "runtime_safety_gate",
                "runtime-safety-gate classified without risky host-preemption intent",
            )
        if changes:
            append_failure(
                failures,
                notes,
                "invalid_host_preemption",
                "runtime_safety_gate",
                "runtime-safety-gate classified despite file changes: " + "; ".join(changes[:5]),
            )
        if not has_gate_shape:
            append_failure(
                failures,
                notes,
                "invalid_host_preemption",
                "runtime_safety_gate",
                "runtime-safety-gate classified without no-execution gate shape",
            )
    elif allowed and has_intent and has_gate_shape and changes:
        append_failure(
            failures,
            notes,
            "invalid_host_preemption",
            "runtime_safety_gate",
            "host preemption candidate changed files instead of staying no-execution",
        )

    if failures:
        return "fail", notes, failures
    if actual == HOST_PREEMPTION_ROUTE or allowed:
        return "pass", notes, failures
    return NOT_APPLICABLE, notes, failures


FAILURE_PRIORITY = [
    "codex_timeout",
    "codex_exit",
    "read_only_sandbox_violation",
    "premature_implementation",
    "forbidden_route",
    "route_miss",
    "invalid_host_preemption",
    "future_output_contract",
    "output_contract_failure",
    "future_evidence_required",
    "evidence_failure",
    "direct_fallback_ceremony",
    "forbidden_behavior",
    "route_evidence_missing",
]


def select_failure(failures):
    if not failures:
        return "", ""
    by_type = {failure_type: fix_locus for failure_type, fix_locus in failures}
    for failure_type in FAILURE_PRIORITY:
        if failure_type in by_type:
            return failure_type, by_type[failure_type]
    return failures[0]


def combine_overall_verdict(rc, slice_verdicts):
    if rc == 124:
        return "timeout"
    if rc != 0:
        return "blocked"
    if any(verdict == "fail" for verdict in slice_verdicts):
        return "fail"
    if any(verdict == "blocked" for verdict in slice_verdicts):
        return "blocked"
    return "pass"


def runtime_failed_without_final_response(rc, final_response):
    return rc != 0 and not final_response.strip()


def routing_verdict_model(
    row,
    actual,
    last,
    rc,
    changes,
    lifecycle_errors,
    stdout="",
    sandbox="unknown",
    case_validation_errors=None,
    response_shape_candidate=None,
    case_workspace=None,
    proof_execution_context=None,
):
    schema = routing_schema_for_row(row)
    behavior_route = response_shape_candidate or actual
    notes = []
    failures = []

    if runtime_failed_without_final_response(rc, last):
        routing_verdict = "blocked"
        routing_notes = ["route unavailable because codex exec produced no final response"]
        routing_failures = []
        host_verdict = NOT_APPLICABLE
        host_notes = []
        host_failures = []
        output_verdict = "blocked"
        output_notes = ["output contract unavailable because codex exec produced no final response"]
        output_failures = []
        evidence_status = "blocked"
        evidence_notes = ["evidence contract unavailable because codex exec produced no final response"]
        evidence_failures = []
        behavior_status = "blocked"
        behavior_notes = ["behavior contract unavailable because codex exec produced no final response"]
        behavior_failures = []
    else:
        routing_verdict, routing_notes, routing_failures = routing_verdict_details(row, schema, actual)
        host_verdict, host_notes, host_failures = host_preemption_verdict_details(row, behavior_route, last, changes)
        output_verdict, output_notes, output_failures = output_contract_verdict(row, schema, behavior_route, last)
        evidence_status, evidence_notes, evidence_failures = evidence_verdict(
            row,
            schema,
            behavior_route,
            last,
            changes,
            stdout,
            case_workspace=case_workspace,
            proof_execution_context=proof_execution_context,
        )
        behavior_status, behavior_notes, behavior_failures = behavior_verdict(
            row,
            schema,
            behavior_route,
            last,
            changes,
            lifecycle_errors,
            case_validation_errors,
        )

    notes.extend(routing_notes + host_notes + output_notes + evidence_notes + behavior_notes)
    failures.extend(routing_failures + host_failures + output_failures + evidence_failures + behavior_failures)

    if rc == 124:
        append_failure(failures, notes, "codex_timeout", "runtime_environment", "codex exec timeout")
    elif rc != 0:
        append_failure(failures, notes, "codex_exit", "runtime_environment", f"codex exec exit {rc}")
    if sandbox == "read-only" and changes:
        append_failure(
            failures,
            notes,
            "read_only_sandbox_violation",
            "runtime_environment",
            "read-only sandbox changed files: " + "; ".join(changes[:5]),
        )

    overall = combine_overall_verdict(
        rc,
        [routing_verdict, host_verdict, output_verdict, evidence_status, behavior_status],
    )
    if failures and overall == "pass":
        overall = "fail"
    failure_type, fix_locus = select_failure(failures)

    return {
        "route_boundary": schema["route_boundary"],
        "case_kind": schema["case_kind"],
        "case_source": schema["case_source"],
        "expected_route": schema["expected_best"],
        "actual_route": actual,
        "response_shape_candidate": behavior_route,
        "acceptable_routes": schema["acceptable_routes"],
        "forbidden_routes": schema["forbidden_routes"],
        "routing_verdict": routing_verdict,
        "host_preemption_verdict": host_verdict,
        "output_contract_verdict": output_verdict,
        "evidence_verdict": evidence_status,
        "behavior_verdict": behavior_status,
        "overall_verdict": overall,
        "failure_type": failure_type,
        "fix_locus": fix_locus,
        "blocking_level": "blocking" if overall in {"fail", "blocked", "timeout"} else "",
        "notes": "; ".join(unique_in_order(notes)),
    }


def has_gsd_creation_intent(text, changes):
    if any(re.match(r"[AM] \.(planning|gsd)(/|$)", change) for change in changes):
        return True

    path_re = re.compile(r"\.(planning|gsd)(/|\b)")
    create_re = re.compile(
        r"(create|created|creating|will create|mkdir|touch|write|wrote|add|生成|建立|创建|写入|新增|落地)",
        re.IGNORECASE,
    )
    rejection_re = re.compile(
        r"(不应|不应该|不要|不建议|不会|不能|拒绝|禁止|不创建|不采用|避免|"
        r"do not create|should not create|not create|without creating|reject|rejected|forbidden|avoid)",
        re.IGNORECASE,
    )

    clauses = re.split(r"[\n。；;!?]+", text)
    for clause in clauses:
        if path_re.search(clause) and create_re.search(clause) and not rejection_re.search(clause):
            return True
    return False


def changed_file_paths(changes):
    return [change[2:] for change in changes if change.startswith(("A ", "M "))]


def run_static_gated_evaluator_check(cwd, command):
    """Run evaluator-owned commands only after the fixture purity gate passes."""
    child_environment, _context = sanitized_codex_environment()
    try:
        captured_command = _captured_evaluator_command(command)
        return subprocess.run(
            captured_command,
            cwd=cwd,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            timeout=20,
            env=child_environment,
        )
    except (FileNotFoundError, RuntimeError) as exc:
        return subprocess.CompletedProcess(command, 127, stdout=str(exc))
    except subprocess.TimeoutExpired as exc:
        output = exc.stdout or ""
        if isinstance(output, bytes):
            output = output.decode("utf-8", errors="replace")
        return subprocess.CompletedProcess(command, 124, stdout=output)


def validate_case_specific_fixture(row, cwd, changes):
    return validate_fixture_case(
        row,
        cwd,
        changes,
        repo=REPO,
        run_check=run_static_gated_evaluator_check,
    )


def is_throwaway_prototype_artifact(row, actual, change):
    if actual != "prototype":
        return False
    if not boolish(row.get("artifact_allowed")):
        return False
    match = re.match(r"^[ MADRCU?!]{1,2}\s+(.+)$", change)
    path = match.group(1) if match else change
    return path in {"prototype.html", "index.html"} or bool(
        re.fullmatch(r"artifacts/[^/]*prototype[^/]*/index\.html", path)
    )


def changes_relevant_to_no_file_evidence(row, actual, changes):
    return [
        change
        for change in changes
        if not is_throwaway_prototype_artifact(row, actual, change)
    ]


def is_requirement_shaping_artifact(row, actual, change, final_response):
    if actual != "to-prd":
        return False
    if expected_skill_for_row(row) != "to-prd":
        return False
    match = re.match(r"^[ MADRCU?!]{1,2}\s+(.+)$", change)
    path = match.group(1) if match else change
    if not (
        path == "README.md"
        or re.fullmatch(r"docs/[^/]+\.md", path)
        or re.fullmatch(r"artifacts/[^/]+/prd\.md", path)
    ):
        return False
    shaping_markers = [
        "prd",
        "spec",
        "acceptance",
        "needs clarification",
        "验收",
        "需求",
        "规范",
        "未决",
        "待确认",
        "ac-",
    ]
    lowered = final_response.lower()
    return any(marker in lowered or marker in final_response for marker in shaping_markers)


def changes_relevant_to_raw_intent_implementation(row, actual, changes, final_response):
    return [
        change
        for change in changes
        if not is_requirement_shaping_artifact(row, actual, change, final_response)
    ]


def validate_lifecycle_state_artifacts(cwd, files, changes):
    state_files = sorted(
        set(
            path
            for path in files
            if re.fullmatch(r"artifacts/[^/]+/STATE\.md", path)
        )
        | set(
            path
            for path in changed_file_paths(changes)
            if re.fullmatch(r"artifacts/[^/]+/STATE\.md", path)
        )
    )
    errors = []

    for path in changed_file_paths(changes):
        if re.match(r"\.(planning|gsd)(/|$)", path):
            errors.append(f"forbidden lifecycle path changed: {path}")

    for rel in state_files:
        parts = rel.split("/")
        if len(parts) != 3 or parts[0] != "artifacts" or parts[2] != "STATE.md":
            errors.append(f"STATE.md path must be artifacts/<workstream-slug>/STATE.md: {rel}")
            continue

        slug = parts[1]
        if slug in RESERVED_WORKSTREAM_SLUGS or not re.fullmatch(r"[a-z0-9](?:[a-z0-9-]*[a-z0-9])?", slug):
            errors.append(f"invalid workstream slug for STATE.md: {rel}")

        text = (cwd / rel).read_text(encoding="utf-8", errors="replace")
        line_count = len(text.splitlines())
        if line_count > 100:
            errors.append(f"STATE.md exceeds 100 lines: {rel} ({line_count})")

        missing = [field for field in STATE_REQUIRED_FIELDS if not has_required_field(text, field)]
        if missing:
            errors.append(f"STATE.md missing required fields in {rel}: {', '.join(missing)}")

    return state_files, errors



def write_case_result(result):
    case_path = CASES / f"{safe_id(result['id'])}.json"
    if case_path.exists():
        try:
            existing = json.loads(case_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise RuntimeError(
                f"refusing to overwrite unreadable case result: {case_path}"
            ) from exc
        existing_id = existing.get("id") if isinstance(existing, dict) else None
        if existing_id != result["id"]:
            raise RuntimeError(
                "case artifact path collision: "
                f"{result['id']!r} would overwrite {existing_id!r} at "
                f"{case_path}"
            )
    case_path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return case_path


def run_row(row, timeout_s=None, attempt=1):
    row_id = row["id"]
    expected = expected_skill_for_row(row)
    metadata = case_metadata(row)
    timeout_s = timeout_s or metadata["timeout_s"]
    cwd, sandbox, workspace_note = choose_workspace(row)
    prompt = prompt_with_evidence_bindings(
        prompt_for_row(row),
        row,
        cwd,
    )
    before = snapshot(cwd)

    attempt_suffix = "" if attempt == 1 else f"-attempt{attempt}"
    log_path = LOGS / f"{row_id}{attempt_suffix}.jsonl"
    last_path = LAST / f"{row_id}{attempt_suffix}.txt"
    child_environment, proof_execution_context = sanitized_codex_environment()
    cmd = codex_exec_command(cwd, sandbox, last_path, prompt, row=row)

    started = datetime.now(timezone.utc).isoformat()
    try:
        proc = subprocess.run(
            cmd,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            timeout=timeout_s,
            env=child_environment,
        )
        stdout = proc.stdout
        rc = proc.returncode
    except subprocess.TimeoutExpired as exc:
        stdout = exc.stdout or ""
        if isinstance(stdout, bytes):
            stdout = stdout.decode("utf-8", errors="replace")
        rc = 124
    except OSError as exc:
        stdout = f"codex exec launch failed: {exc}\n"
        rc = 127

    log_path.write_text(stdout, encoding="utf-8")
    last = last_path.read_text(encoding="utf-8") if last_path.exists() else ""
    after = snapshot(cwd)
    changes = changed_files(before, after)
    actual, skill_hits = parse_actual_skill(stdout, last, expected)
    response_shape_candidate = classify_response_shape_candidate(row, last, changes)
    acceptable_routes = acceptable_routes_for_row(row)
    if runtime_failed_without_final_response(rc, last):
        actual = UNKNOWN_ROUTE
        response_shape_candidate = UNKNOWN_ROUTE
    multi_skill_hit = len(skill_hits) > 1
    warnings = ["multi_skill_hit"] if multi_skill_hit else []
    lifecycle_state_files, lifecycle_artifact_errors = validate_lifecycle_state_artifacts(cwd, after, changes)
    case_validation_errors = validate_case_specific_fixture(row, cwd, changes)
    runtime_mode = router_observability_runtime_mode(cwd)
    verdict_model = routing_verdict_model(
        row,
        actual,
        last,
        rc,
        changes,
        lifecycle_artifact_errors,
        stdout,
        sandbox=sandbox,
        case_validation_errors=case_validation_errors,
        response_shape_candidate=response_shape_candidate,
        case_workspace=cwd,
        proof_execution_context=proof_execution_context,
    )
    result = {
        "id": row_id,
        "suite": row["_suite"],
        "expected": expected,
        "actual": actual,
        "response_shape_candidate": response_shape_candidate,
        "skill_hits": skill_hits,
        "multi_skill_hit": multi_skill_hit,
        "warnings": warnings,
        "route_evidence_source": route_evidence_source(actual, skill_hits),
        "response_shape_evidence_source": response_shape_evidence_source(response_shape_candidate, last),
        "dispatch_hit_level": dispatch_hit_level(
            expected, acceptable_routes, actual, response_shape_candidate, skill_hits
        ),
        "verdict": verdict_model["overall_verdict"],
        "notes": verdict_model["notes"],
        "parallel_safe": metadata["parallel_safe"],
        "resource_keys": metadata["resource_keys"],
        "resource_group": metadata["group"],
        "timeout_s": timeout_s,
        "flake_policy": metadata["flake_policy"],
        "attempt": attempt,
        "cwd": str(cwd),
        "sandbox": sandbox,
        "hook_trust_bypass": bool(
            proof_execution_context["argv_controls"][
                "hook_trust_bypass"
            ]
        ),
        "runtime_mode": runtime_mode,
        "proof_execution_context": proof_execution_context,
        "observed_evidence": observed_evidence_kinds(stdout),
        "score_eligibility": score_eligibility_for_runtime_mode(runtime_mode),
        "acceptable_routes": acceptable_routes,
        "workspace_note": workspace_note,
        "returncode": rc,
        "changed_files": changes,
        "lifecycle_state_files": lifecycle_state_files,
        "lifecycle_artifact_errors": lifecycle_artifact_errors,
        "case_validation_errors": case_validation_errors,
        "log": str(log_path),
        "last": str(last_path),
        "started": started,
        "finished": datetime.now(timezone.utc).isoformat(),
    }
    result.update(verdict_model)
    result["case_result"] = str(write_case_result(result))
    print(
        json.dumps(
            {
                k: result[k]
                for k in [
                    "id",
                    "suite",
                    "expected",
                    "actual",
                    "multi_skill_hit",
                    "verdict",
                    "notes",
                ]
            },
            ensure_ascii=False,
        ),
        flush=True,
    )
    return result


def is_nonpass(result):
    return result.get("verdict") not in {"pass", "flake"}


def attempt_summary(result):
    return {
        "verdict": result.get("verdict"),
        "notes": result.get("notes"),
        "returncode": result.get("returncode"),
        "log": result.get("log"),
        "last": result.get("last"),
    }


def run_case_with_policy(row, retry_timeouts=0):
    metadata = case_metadata(row)
    attempts = []
    attempt = 1
    result = run_row(row, metadata["timeout_s"], attempt=attempt)
    attempts.append(result)

    while result.get("verdict") == "timeout" and attempt <= retry_timeouts:
        attempt += 1
        result = run_row(row, metadata["timeout_s"], attempt=attempt)
        attempts.append(result)

    if result.get("verdict") != "pass" and metadata["flake_policy"] == "rerun_once":
        attempt += 1
        flake_result = run_row(row, metadata["timeout_s"], attempt=attempt)
        attempts.append(flake_result)
        if flake_result.get("verdict") == "pass":
            flake_result["verdict"] = "flake"
            flake_result["notes"] = (
                f"passed on rerun after {result.get('verdict')}: {result.get('notes') or ''}"
            ).strip()
        else:
            flake_result["notes"] = "; ".join(
                item
                for item in [
                    flake_result.get("notes"),
                    f"rerun_once first verdict {result.get('verdict')}: {result.get('notes') or ''}",
                ]
                if item
            )
        result = flake_result

    result["attempts"] = len(attempts)
    if len(attempts) > 1:
        result["previous_attempts"] = [attempt_summary(item) for item in attempts[:-1]]
    if any(item.get("verdict") == "timeout" for item in attempts[:-1]):
        result["retried_timeout"] = True
    else:
        result.pop("retried_timeout", None)
    write_case_result(result)
    return result


def exception_result(row, exc):
    row_id = row.get("id", "unknown")
    metadata = case_metadata(row)
    runtime_mode = router_observability_runtime_mode()
    expected = expected_skill_for_row(row)
    acceptable_routes = acceptable_routes_for_row(row)
    result = {
        "id": row_id,
        "suite": row.get("_suite"),
        "expected": expected,
        "actual": "unknown",
        "skill_hits": [],
        "multi_skill_hit": False,
        "warnings": ["runner_exception"],
        "route_evidence_source": "unknown",
        "response_shape_candidate": UNKNOWN_ROUTE,
        "response_shape_evidence_source": "unknown",
        "dispatch_hit_level": dispatch_hit_level(
            expected, acceptable_routes, UNKNOWN_ROUTE, UNKNOWN_ROUTE, []
        ),
        "verdict": "blocked",
        "notes": f"runner exception: {type(exc).__name__}: {exc}",
        "parallel_safe": metadata["parallel_safe"],
        "resource_keys": metadata["resource_keys"],
        "resource_group": metadata["group"],
        "timeout_s": metadata["timeout_s"],
        "flake_policy": metadata["flake_policy"],
        "returncode": None,
        "runtime_mode": runtime_mode,
        "score_eligibility": score_eligibility_for_runtime_mode(runtime_mode),
        "acceptable_routes": acceptable_routes,
        "changed_files": [],
        "lifecycle_state_files": [],
        "lifecycle_artifact_errors": [],
        "started": datetime.now(timezone.utc).isoformat(),
        "finished": datetime.now(timezone.utc).isoformat(),
    }
    result["case_result"] = str(write_case_result(result))
    print(json.dumps({k: result.get(k) for k in ["id", "suite", "verdict", "notes"]}, ensure_ascii=False), flush=True)
    return result


def summarize_routing_results(results):
    return shared_summarize_routing_results(results)


def run_parallel_rows(rows, jobs, retry_timeouts=0):
    results = []
    with ThreadPoolExecutor(max_workers=jobs) as executor:
        future_to_row = {
            executor.submit(
                run_case_with_exception_boundary,
                row,
                retry_timeouts,
            ): row
            for row in rows
        }
        for future in as_completed(future_to_row):
            row = future_to_row[future]
            try:
                result = future.result()
            except Exception as exc:
                result = exception_result(row, exc)
            results.append(result)
    return results


def run_case_with_exception_boundary(row, retry_timeouts=0):
    try:
        return run_case_with_policy(row, retry_timeouts)
    except Exception as exc:
        return exception_result(row, exc)


def execute_rows(rows, jobs, resource_policy, retry_timeouts=0):
    results = []
    parallel_rows, serial_rows = partition_rows(rows, jobs, resource_policy)
    if jobs == 1:
        for row in rows:
            results.append(
                run_case_with_exception_boundary(
                    row,
                    retry_timeouts,
                )
            )
    else:
        if parallel_rows:
            results.extend(run_parallel_rows(parallel_rows, jobs, retry_timeouts))
        for row in serial_rows:
            results.append(
                run_case_with_exception_boundary(
                    row,
                    retry_timeouts,
                )
            )
    input_indexes = {row.get("id"): row.get("_input_index", 0) for row in rows}
    for result in results:
        result["_input_index"] = input_indexes.get(result.get("id"), 0)
    return results


def write_summary(
    results,
    jobs,
    suites,
    resource_policy,
    group=None,
    *,
    all_prompts=False,
    requested_suites=None,
    prompt_files=None,
    requested_case_ids=None,
    rerun_failures="",
):
    ordered = sorted(results, key=lambda item: item.get("_input_index", 0))
    suites = [str(item) for item in suites]
    requested_suites = (
        [str(item) for item in requested_suites]
        if requested_suites is not None
        else list(suites)
    )
    prompt_files = [
        canonical_prompt_file(item) for item in (prompt_files or [])
    ]
    requested_case_ids = [
        str(item) for item in (requested_case_ids or [])
    ]
    executed_case_ids = [
        str(result.get("id") or "")
        for result in ordered
        if str(result.get("id") or "")
    ]
    with RESULTS.open("w", encoding="utf-8") as fh:
        for result in ordered:
            serializable = dict(result)
            serializable.pop("_input_index", None)
            fh.write(json.dumps(serializable, ensure_ascii=False) + "\n")

    counts = {}
    for result in ordered:
        verdict = str(result.get("verdict", "unknown"))
        counts[verdict] = counts.get(verdict, 0) + 1

    failures = [
        {
            "id": result.get("id"),
            "suite": result.get("suite"),
            "verdict": result.get("verdict"),
            "notes": result.get("notes"),
            "case_result": result.get("case_result"),
            "log": result.get("log"),
            "last": result.get("last"),
        }
        for result in ordered
        if is_nonpass(result)
    ]
    runtime_mode = aggregate_runtime_mode(ordered)
    summary = {
        "run_root": str(RUN),
        "jobs": jobs,
        "resource_policy": resource_policy,
        "group": group,
        "runtime_selector": dict(RUNTIME_SELECTOR),
        "suites": suites,
        "all_prompts": bool(all_prompts),
        "requested_suites": requested_suites,
        "prompt_files": prompt_files,
        "requested_case_ids": requested_case_ids,
        "executed_case_ids": executed_case_ids,
        "rerun_failures": str(rerun_failures or ""),
        "runtime_mode": runtime_mode,
        "score_eligibility": score_eligibility_for_runtime_mode(
            runtime_mode
        ),
        "rows": len(ordered),
        "counts": counts,
        "failures": failures,
        "result_layout": {
            "cases": str(CASES),
            "summary": str(SUMMARY),
            "failures": str(FAILURES),
            "results_jsonl": str(RESULTS),
        },
        "finished": datetime.now(timezone.utc).isoformat(),
    }
    routing_summary = summarize_routing_results(ordered)
    if routing_summary:
        summary["routing_summary"] = routing_summary
    SUMMARY.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# Runtime Failures",
        "",
        "## Evidence Boundary",
        "",
        f"- Runtime selector: `{json.dumps(RUNTIME_SELECTOR, ensure_ascii=False, sort_keys=True)}`",
        f"- Runtime mode: `{runtime_mode['router_observability_mode']}`",
        f"- Router observability enabled: `{str(runtime_mode['router_observability_enabled']).lower()}`",
        f"- Hook trust bypass: `{str(runtime_mode['hook_trust_bypass']).lower()}`",
        f"- Evidence boundary: {runtime_mode['evidence_boundary']}",
        "",
        "## Non-pass Results",
        "",
    ]
    if not failures:
        lines.append("No non-pass results.")
    else:
        for item in failures:
            notes = item.get("notes") or ""
            lines.append(f"- `{item['id']}` [{item['suite']}] {item['verdict']}: {notes}")
    FAILURES.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return summary



def parse_args(argv=None):
    parser = argparse.ArgumentParser(description="Run Groundwork runtime evals.")
    parser.add_argument("ids", nargs="*", help="Optional case ids to run.")
    parser.add_argument("--all-prompts", action="store_true", help="Run all prompt CSV suites.")
    parser.add_argument("--suite", action="append", help="Prompt suite filename to include; may be repeated.")
    parser.add_argument(
        "--prompt-file",
        action="append",
        type=Path,
        help="Prompt CSV path to include; may be repeated. Relative paths resolve from the repository root.",
    )
    parser.add_argument(
        "--validate-schema",
        action="store_true",
        help="Parse prompt CSV suites and validate routing schema without invoking Codex runtime.",
    )
    parser.add_argument("--jobs", type=int, default=1, help="Maximum concurrent safe cases. Default: 1.")
    parser.add_argument("--serial", action="store_true", help="Force serial execution, equivalent to --jobs 1.")
    parser.add_argument("--model", help="Optional model selector passed through to codex exec, for example gpt-5.4-mini.")
    parser.add_argument("--profile", help="Optional Codex config profile passed through to codex exec.")
    parser.add_argument(
        "--codex-config",
        action="append",
        default=[],
        help="Optional codex exec -c key=value override. May be repeated.",
    )
    parser.add_argument(
        "--bypass-hook-trust",
        action="store_true",
        help=(
            "Debug-only Codex hook trust bypass. The control is recorded "
            "and makes the run insufficient as verified evidence."
        ),
    )
    parser.add_argument(
        "--resource-policy",
        choices=["auto", "none"],
        default="auto",
        help="Resource scheduler policy. 'auto' limits shared/browser/flaky cases; 'none' preserves input-order serial scheduling.",
    )
    parser.add_argument("--rerun-failures", type=Path, help="Path to a previous summary.json or run directory.")
    parser.add_argument("--group", help="Run only cases in this inferred or explicit resource group, e.g. browser.")
    parser.add_argument("--case-timeout", type=int, default=CODEX_EXEC_TIMEOUT, help="Default timeout per case in seconds.")
    parser.add_argument(
        "--retry-timeouts",
        type=int,
        default=0,
        help="Retry timeout results per case. Kept for run_runtime_parallel.py compatibility.",
    )
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    global CODEX_EXEC_TIMEOUT
    CODEX_EXEC_TIMEOUT = args.case_timeout

    explicit_case_ids = unique_in_order(
        [str(row_id) for row_id in args.ids]
    )
    target_ids = set(explicit_case_ids)
    if args.rerun_failures:
        try:
            target_ids.update(load_failure_ids(args.rerun_failures))
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            print(f"rerun_failures_error={exc}", flush=True)
            return 2
    resolved_case_ids = explicit_case_ids + sorted(
        target_ids - set(explicit_case_ids)
    )

    prompt_files = [
        Path(canonical_prompt_file(path))
        for path in (args.prompt_file or [])
    ]
    explicit_suites = bool(args.suite)
    explicit_ids = bool(target_ids)
    if args.suite:
        suites = [normalize_suite_name(suite) for suite in args.suite]
    elif prompt_files:
        suites = []
    else:
        suites = prompt_suites() if args.all_prompts or target_ids or args.validate_schema else DEFAULT_SUITES
    suite_labels = list(suites) + [str(path) for path in prompt_files]
    try:
        rows = read_rows(suites, prompt_files)
    except (OSError, ValueError, csv.Error) as exc:
        print(
            json.dumps(
                {
                    "schema_validation": "fail",
                    "suites": suite_labels,
                    "rows": 0,
                    "errors": [str(exc)],
                },
                ensure_ascii=False,
            ),
            flush=True,
        )
        return 2
    schema_errors, _normalized_schema = validate_routing_schema(rows)
    schema_errors.extend(case_artifact_identity_errors(rows))
    if args.validate_schema:
        if target_ids:
            rows = [row for row in rows if row["id"] in target_ids]
            missing = sorted(target_ids - {row["id"] for row in rows})
            schema_errors.extend(f"missing requested id: {row_id}" for row_id in missing)
        trace_ready_rows = [row for row in rows if is_trace_ready_row(row)]
        print(
            json.dumps(
                {
                    "schema_validation": "fail" if schema_errors else "pass",
                    "suites": suite_labels,
                    "rows": len(rows),
                    "trace_ready_rows": len(trace_ready_rows),
                    "routing_rows": len(trace_ready_rows),
                    "errors": schema_errors,
                    "recognized_fields": ROUTING_SCHEMA_FIELDS,
                },
                ensure_ascii=False,
                indent=2,
            ),
            flush=True,
        )
        return 2 if schema_errors else 0
    if schema_errors:
        print(
            json.dumps(
                {
                    "schema_validation": "fail",
                    "suites": suite_labels,
                    "rows": len(rows),
                    "errors": schema_errors,
                },
                ensure_ascii=False,
            ),
            flush=True,
        )
        return 2
    if args.all_prompts and not explicit_suites and not explicit_ids and not prompt_files:
        rows, skipped_rows = filter_auto_discovery_rows(rows)
        if skipped_rows:
            skipped_ids = ",".join(row["id"] for row in skipped_rows)
            print(f"skipped_auto_discovery_rows={len(skipped_rows)}:{skipped_ids}", flush=True)

    jobs = 1 if args.serial else max(1, args.jobs)
    RUNTIME_SELECTOR["model"] = str(args.model or "")
    RUNTIME_SELECTOR["profile"] = str(args.profile or "")
    RUNTIME_SELECTOR["codex_config"] = [str(item) for item in (args.codex_config or [])]
    RUNTIME_SELECTOR["hook_trust_bypass"] = bool(
        args.bypass_hook_trust
    )

    if target_ids:
        rows = [row for row in rows if row["id"] in target_ids]
        missing = sorted(target_ids - {row["id"] for row in rows})
        if missing:
            print("missing_ids=" + ",".join(missing), flush=True)
            return 2
    if args.group:
        rows = [row for row in rows if row_matches_group(row, args.group)]
    if not rows:
        print("no_matching_rows=1", flush=True)
        return 2

    LOGS.mkdir(parents=True, exist_ok=True)
    LAST.mkdir(parents=True, exist_ok=True)
    WORKSPACES.mkdir(parents=True, exist_ok=True)
    CASES.mkdir(parents=True, exist_ok=True)
    for path in (
        PROOF_HOME,
        PROOF_HOME / ".cache",
        PROOF_HOME / ".config",
        PROOF_HOME / ".local" / "share",
        PROOF_HOME / ".local" / "state",
    ):
        path.mkdir(parents=True, exist_ok=True)

    for index, row in enumerate(rows):
        row["_input_index"] = index

    print(f"run_root={RUN}", flush=True)
    print(f"rows={len(rows)}", flush=True)
    print(f"jobs={jobs}", flush=True)
    print(f"resource_policy={args.resource_policy}", flush=True)
    print("runtime_selector=" + json.dumps(RUNTIME_SELECTOR, ensure_ascii=False, sort_keys=True), flush=True)
    if args.group:
        print(f"group={args.group}", flush=True)

    results = execute_rows(rows, jobs, args.resource_policy, args.retry_timeouts)

    for result in results:
        result["_input_index"] = next(
            (row.get("_input_index", 0) for row in rows if row.get("id") == result.get("id")),
            0,
        )
    summary = write_summary(
        results,
        jobs,
        suite_labels,
        args.resource_policy,
        args.group,
        all_prompts=bool(args.all_prompts),
        requested_suites=suites,
        prompt_files=[str(path) for path in prompt_files],
        requested_case_ids=resolved_case_ids,
        rerun_failures=str(args.rerun_failures or ""),
    )
    print(json.dumps({"summary": summary}, ensure_ascii=False), flush=True)
    return 1 if summary["failures"] else 0


if __name__ == "__main__":
    sys.exit(main())
