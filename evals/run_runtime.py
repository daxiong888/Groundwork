#!/usr/bin/env python3
import csv
import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

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
    from checks.verify_checks import (
        ARTIFACT_HEADER_FIELDS,
        QA_FAILURE_FIELDS,
        VERIFY_SCOPE_FIELDS,
        missing_verify_scope_fields,
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
    from evals.checks.verify_checks import (
        ARTIFACT_HEADER_FIELDS,
        QA_FAILURE_FIELDS,
        VERIFY_SCOPE_FIELDS,
        missing_verify_scope_fields,
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
SUMMARY = RUN / "summary.json"
FAILURES = RUN / "failures.md"
RUNTIME_SELECTOR = {"model": "", "profile": "", "codex_config": []}

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


def safe_id(value):
    return re.sub(r"[^A-Za-z0-9_.-]+", "-", str(value)).strip("-") or "case"


def prompt_suites():
    return sorted(p.name for p in (REPO / "evals" / "prompts").glob("*.csv"))


def normalize_suite_name(value):
    text = str(value).strip()
    if text and "/" not in text and "\\" not in text and not text.endswith(".csv"):
        text += ".csv"
    return text


def read_prompt_rows(path, suite_label=None):
    rows = []
    with path.open(newline="") as fh:
        reader = csv.DictReader(fh)
        for row_number, row in enumerate(reader, start=2):
            row["_suite"] = suite_label or path.name
            row["_row_number"] = row_number
            row["_fieldnames"] = reader.fieldnames or []
            rows.append(row)
    return rows


def read_rows(suites, prompt_files=None):
    out = []
    for suite in suites:
        suite_name = normalize_suite_name(suite)
        path = REPO / "evals" / "prompts" / suite_name
        out.extend(read_prompt_rows(path, suite_label=suite_name))
    for prompt_file in prompt_files or []:
        path = Path(prompt_file)
        if not path.is_absolute():
            path = REPO / path
        out.extend(read_prompt_rows(path, suite_label=path.name))
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
    return os.environ.get("GROUNDWORK_CODEX_BYPASS_HOOK_TRUST") == "1"


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
    }


def set_runtime_paths(run_root):
    global RUN, LOGS, LAST, WORKSPACES, RESULTS, CASES, SUMMARY, FAILURES
    RUN = Path(run_root)
    LOGS = RUN / "logs"
    LAST = RUN / "last"
    WORKSPACES = RUN / "workspaces"
    RESULTS = RUN / "results.jsonl"
    CASES = RUN / "cases"
    SUMMARY = RUN / "summary.json"
    FAILURES = RUN / "failures.md"


def restore_runtime_path_state(state):
    global RUN, LOGS, LAST, WORKSPACES, RESULTS, CASES, SUMMARY, FAILURES
    RUN = state["RUN"]
    LOGS = state["LOGS"]
    LAST = state["LAST"]
    WORKSPACES = state["WORKSPACES"]
    RESULTS = state["RESULTS"]
    CASES = state["CASES"]
    SUMMARY = state["SUMMARY"]
    FAILURES = state["FAILURES"]


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
        "hook_trust_bypass": hook_trust_bypass_enabled(),
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


def codex_exec_command(cwd, sandbox, last_path, prompt, row=None):
    cmd = ["codex"]
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
    proc = subprocess.run(
        cmd,
        cwd=cwd,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"fixture setup command failed ({proc.returncode}): {' '.join(cmd)}\n{proc.stdout}")
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


def has_source_or_unverified_evidence(text):
    lowered = text.lower()
    source_markers = ["source truth", "source evidence", "source", "canonical", "源码", "源真相", "证据"]
    unverified_markers = [
        "unverified",
        "unknown",
        "not provided",
        "not covered",
        "missing",
        "blocked",
        "无法验证",
        "未验证",
        "未知",
        "缺少",
        "没有",
        "不可验证",
        "未提供",
    ]
    return any(marker in lowered for marker in source_markers) and any(
        marker in lowered for marker in unverified_markers
    )


def has_tests_or_unverified_evidence(text):
    lowered = text.lower()
    test_markers = ["test", "tests", "check", "checks", "测试", "自测", "验证", "验证命令", "focused"]
    unverified_markers = [
        "not run",
        "not covered",
        "unverified",
        "missing",
        "blocked",
        "no test",
        "no tests",
        "无法运行",
        "未运行",
        "未覆盖",
        "无可运行",
        "没有测试",
        "只读",
        "不能落文件",
        "无法安全落地",
        "缺少",
    ]
    return any(marker in lowered for marker in test_markers) and any(
        marker in lowered for marker in unverified_markers
    )


def has_browser_or_unverified_evidence(text):
    lowered = text.lower()
    browser_markers = ["browser", "ui evidence", "runtime / browser", "浏览器", "截图", "录屏", "前端", "ui"]
    unverified_markers = [
        "unverified",
        "not covered",
        "not provided",
        "missing",
        "blocked",
        "无法验证",
        "未验证",
        "未覆盖",
        "未提供",
        "缺少",
    ]
    return any(marker in lowered for marker in browser_markers) and any(
        marker in lowered for marker in unverified_markers
    )


def has_runtime_or_unverified_evidence(text):
    runtime_markers = [
        "runtime",
        "runtime evidence",
        "codex exec",
        "run_runtime",
        "exit code",
        "command output",
        "运行时",
        "运行证据",
        "运行结果",
        "执行证据",
        "执行结果",
        "命令输出",
        "日志",
    ]
    runtime_observed_markers = [
        "exit code",
        "command output",
        "run_root",
        "log:",
        "logs/",
        "passed",
        "pass",
        "ok",
        "执行通过",
        "运行通过",
        "命令输出",
    ]
    unverified_markers = [
        "not run",
        "not covered",
        "not provided",
        "unverified",
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
        "未运行",
        "未验证",
        "未覆盖",
        "未提供",
        "缺少",
        "不能证明",
        "不能作为",
        "不足以",
    ]
    for line in str(text or "").splitlines():
        lowered = line.lower()
        if not any(marker in lowered for marker in runtime_markers):
            continue
        if any(marker in lowered for marker in unverified_markers):
            return True
        if any(marker in lowered for marker in runtime_observed_markers):
            return True
    return False


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
    commands = []
    for line in stdout.splitlines():
        try:
            payload = json.loads(line)
        except json.JSONDecodeError:
            continue
        item = payload.get("item")
        if (
            payload.get("type") == "item.completed"
            and isinstance(item, dict)
            and item.get("type") == "command_execution"
            and isinstance(item.get("command"), str)
        ):
            commands.append(item["command"])
    return commands


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


def evidence_verdict(row, schema, actual, final_response, changes, stdout):
    notes = []
    failures = []
    tokens = schema["evidence_required"]
    future_tokens = schema["evidence_required_future_tokens"]
    combined = stdout + "\n" + final_response

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
            if "git status" not in combined:
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
            if not has_source_or_unverified_evidence(combined):
                append_failure(
                    failures,
                    notes,
                    "evidence_failure",
                    "evidence_collection",
                    "missing source evidence or explicit unverified source boundary",
                )
        elif token == "tests_or_unverified":
            if not has_tests_or_unverified_evidence(combined):
                append_failure(
                    failures,
                    notes,
                    "evidence_failure",
                    "evidence_collection",
                    "missing test evidence or explicit unverified test boundary",
                )
        elif token == "browser_or_unverified":
            if not has_browser_or_unverified_evidence(combined):
                append_failure(
                    failures,
                    notes,
                    "evidence_failure",
                    "evidence_collection",
                    "missing browser evidence or explicit unverified browser boundary",
                )
        elif token == "runtime_or_unverified":
            if not has_runtime_or_unverified_evidence(combined):
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
            row, schema, behavior_route, last, changes, stdout
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
    try:
        return subprocess.run(
            command,
            cwd=cwd,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            timeout=20,
        )
    except FileNotFoundError as exc:
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
    case_path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return case_path


def run_row(row, timeout_s=None, attempt=1):
    row_id = row["id"]
    prompt = row.get("prompt") or row.get("input_scenario") or ""
    expected = expected_skill_for_row(row)
    metadata = case_metadata(row)
    timeout_s = timeout_s or metadata["timeout_s"]
    cwd, sandbox, workspace_note = choose_workspace(row)
    before = snapshot(cwd)

    attempt_suffix = "" if attempt == 1 else f"-attempt{attempt}"
    log_path = LOGS / f"{row_id}{attempt_suffix}.jsonl"
    last_path = LAST / f"{row_id}{attempt_suffix}.txt"
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
        )
        stdout = proc.stdout
        rc = proc.returncode
    except subprocess.TimeoutExpired as exc:
        stdout = exc.stdout or ""
        if isinstance(stdout, bytes):
            stdout = stdout.decode("utf-8", errors="replace")
        rc = 124

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
        "hook_trust_bypass": hook_trust_bypass_enabled(),
        "runtime_mode": runtime_mode,
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
        future_to_row = {executor.submit(run_case_with_policy, row, retry_timeouts): row for row in rows}
        for future in as_completed(future_to_row):
            row = future_to_row[future]
            try:
                result = future.result()
            except Exception as exc:
                result = exception_result(row, exc)
            results.append(result)
    return results


def execute_rows(rows, jobs, resource_policy, retry_timeouts=0):
    results = []
    parallel_rows, serial_rows = partition_rows(rows, jobs, resource_policy)
    if jobs == 1:
        for row in rows:
            results.append(run_case_with_policy(row, retry_timeouts))
    else:
        if parallel_rows:
            results.extend(run_parallel_rows(parallel_rows, jobs, retry_timeouts))
        for row in serial_rows:
            results.append(run_case_with_policy(row, retry_timeouts))
    input_indexes = {row.get("id"): row.get("_input_index", 0) for row in rows}
    for result in results:
        result["_input_index"] = input_indexes.get(result.get("id"), 0)
    return results


def write_summary(results, jobs, suites, resource_policy, group=None):
    ordered = sorted(results, key=lambda item: item.get("_input_index", 0))
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
        "runtime_mode": runtime_mode,
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

    target_ids = set(args.ids)
    if args.rerun_failures:
        try:
            target_ids.update(load_failure_ids(args.rerun_failures))
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            print(f"rerun_failures_error={exc}", flush=True)
            return 2

    prompt_files = args.prompt_file or []
    explicit_suites = bool(args.suite)
    explicit_ids = bool(target_ids)
    if args.suite:
        suites = [normalize_suite_name(suite) for suite in args.suite]
    elif prompt_files:
        suites = []
    else:
        suites = prompt_suites() if args.all_prompts or target_ids or args.validate_schema else DEFAULT_SUITES
    suite_labels = list(suites) + [str(path) for path in prompt_files]
    rows = read_rows(suites, prompt_files)
    if (args.all_prompts or args.validate_schema) and not explicit_suites and not explicit_ids and not prompt_files:
        rows, skipped_rows = filter_auto_discovery_rows(rows)
        if skipped_rows:
            skipped_ids = ",".join(row["id"] for row in skipped_rows)
            print(f"skipped_auto_discovery_rows={len(skipped_rows)}:{skipped_ids}", flush=True)
    schema_errors, _normalized_schema = validate_routing_schema(rows)
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

    LOGS.mkdir(parents=True, exist_ok=True)
    LAST.mkdir(parents=True, exist_ok=True)
    WORKSPACES.mkdir(parents=True, exist_ok=True)
    CASES.mkdir(parents=True, exist_ok=True)

    jobs = 1 if args.serial else max(1, args.jobs)
    RUNTIME_SELECTOR["model"] = str(args.model or "")
    RUNTIME_SELECTOR["profile"] = str(args.profile or "")
    RUNTIME_SELECTOR["codex_config"] = [str(item) for item in (args.codex_config or [])]

    if target_ids:
        rows = [row for row in rows if row["id"] in target_ids]
        missing = sorted(target_ids - {row["id"] for row in rows})
        if missing:
            print("missing_ids=" + ",".join(missing), flush=True)
            return 2
    if args.group:
        rows = [row for row in rows if row_matches_group(row, args.group)]

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
    summary = write_summary(results, jobs, suite_labels, args.resource_policy, args.group)
    print(json.dumps({"summary": summary}, ensure_ascii=False), flush=True)
    return 1 if summary["failures"] else 0


if __name__ == "__main__":
    sys.exit(main())
