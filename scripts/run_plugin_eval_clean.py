#!/usr/bin/env python3
"""Prepare and optionally run a clean Plugin Eval benchmark for Groundwork."""

from __future__ import annotations

import argparse
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RUN_ROOT_BASE = Path("/private/tmp/groundwork-plugin-eval")
PLUGIN_NAME = "groundwork"
NESTED_BENCHMARK_SCRIPT_PATTERN = re.compile(
    r"(^|[\s'\";&|])(?:\./)?(?:scripts|evals)/[^'\"\s;&|]*benchmark[^'\"\s;&|]*"
)
BROAD_SCAN_PATTERNS = (
    "rg --files",
    "find .",
    "ls -R",
)
FORBIDDEN_SOURCE_SCAN_ROOTS = (
    "docs",
    "evals",
    "artifacts",
    "scripts",
    "research",
)
SCRIPT_EXECUTORS = {
    "python",
    "python3",
    "node",
    "sh",
    "bash",
    "zsh",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Create clean Groundwork Plugin Eval targets, build a local marketplace, "
            "record package metadata, and print or execute benchmark commands."
        )
    )
    parser.add_argument(
        "--scenario",
        action="append",
        required=True,
        help="Scenario id to prepare. Repeat for multiple scenarios.",
    )
    parser.add_argument(
        "--source",
        type=Path,
        default=Path("."),
        help="Groundwork source checkout. Default: current directory.",
    )
    parser.add_argument(
        "--run-root",
        type=Path,
        default=None,
        help="Run root. Default: /private/tmp/groundwork-plugin-eval/<timestamp>.",
    )
    parser.add_argument(
        "--target-basename",
        default=PLUGIN_NAME,
        help="Target directory basename. Must be groundwork.",
    )
    parser.add_argument(
        "--plugin-eval-command",
        default=os.environ.get("PLUGIN_EVAL_COMMAND"),
        help=(
            "Plugin Eval command. Defaults to PATH plugin-eval, or the installed "
            "plugin-eval cache script when visible."
        ),
    )
    parser.add_argument(
        "--model",
        default=None,
        help="Optional model passed through to plugin-eval benchmark.",
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Run plugin-eval benchmark. Without this, benchmark execution is skipped; static analyze still runs when available.",
    )
    parser.add_argument(
        "--print-commands",
        action="store_true",
        help="Print copyable benchmark commands and skip benchmark execution; static analyze still runs when available.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Remove an existing run root before preparing targets.",
    )
    return parser.parse_args()


def timestamp_run_root() -> Path:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return DEFAULT_RUN_ROOT_BASE / stamp


def clean_id(value: str) -> str:
    cleaned = "".join(ch if ch.isalnum() or ch in {"-", "_"} else "-" for ch in value.strip())
    cleaned = cleaned.strip("-_")
    if not cleaned:
        raise SystemExit("Scenario must contain at least one alphanumeric character.")
    return cleaned


def run_command(
    args: list[str],
    *,
    cwd: Path,
    stdout_path: Path | None = None,
    stderr_path: Path | None = None,
    check: bool = True,
) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        args,
        cwd=cwd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if stdout_path:
        stdout_path.parent.mkdir(parents=True, exist_ok=True)
        stdout_path.write_text(result.stdout, encoding="utf-8")
    if stderr_path:
        stderr_path.parent.mkdir(parents=True, exist_ok=True)
        stderr_path.write_text(result.stderr, encoding="utf-8")
    if check and result.returncode != 0:
        raise SystemExit(
            f"Command failed with exit code {result.returncode}: {' '.join(args)}\n"
            f"stdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )
    return result


def shell_join(args: list[str]) -> str:
    return " ".join(shlex.quote(str(arg)) for arg in args)


def resolve_source(source: Path) -> Path:
    resolved = source.expanduser().resolve()
    if not (resolved / "scripts" / "build_local_marketplace.py").is_file():
        raise SystemExit(f"Not a Groundwork source checkout: {resolved}")
    if not (resolved / ".codex-plugin" / "plugin.json").is_file():
        raise SystemExit(f"Missing plugin manifest under source: {resolved}")
    return resolved


def ensure_run_root(run_root: Path, source: Path, force: bool) -> Path:
    resolved = run_root.expanduser().resolve()
    if resolved == source or source in resolved.parents:
        raise SystemExit("Refusing to place benchmark run output inside the source checkout.")
    if resolved in source.parents:
        raise SystemExit("Refusing to use a parent of the source checkout as benchmark run output.")
    if force and (resolved == DEFAULT_RUN_ROOT_BASE or DEFAULT_RUN_ROOT_BASE not in resolved.parents):
        raise SystemExit(
            f"Refusing --force outside {DEFAULT_RUN_ROOT_BASE}/<run-id>: {resolved}"
        )
    if force and resolved.exists():
        shutil.rmtree(resolved)
    resolved.mkdir(parents=True, exist_ok=True)
    return resolved


def ensure_target_basename(target_basename: str) -> None:
    if target_basename != PLUGIN_NAME:
        raise SystemExit(
            f"Refusing target basename {target_basename!r}; clean Plugin Eval target must be {PLUGIN_NAME!r}."
        )


def git_value(source: Path, *args: str) -> str | None:
    result = subprocess.run(
        ["git", "-C", str(source), *args],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if result.returncode != 0:
        return None
    return result.stdout.strip()


def parse_packaged_entries(builder_stdout: str) -> list[str]:
    entries: list[str] = []
    in_entries = False
    for line in builder_stdout.splitlines():
        if line == "Packaged runtime entries:":
            in_entries = True
            continue
        if line == "Forbidden package roots:":
            break
        if in_entries and line.startswith("- "):
            entries.append(line[2:])
    return entries


def build_marketplace(source: Path, run_root: Path) -> dict:
    marketplace_root = run_root / "marketplace"
    result = run_command(
        [
            sys.executable,
            str(source / "scripts" / "build_local_marketplace.py"),
            "--output",
            str(marketplace_root),
        ],
        cwd=source,
        stdout_path=run_root / "results" / "build-local-marketplace.stdout.log",
        stderr_path=run_root / "results" / "build-local-marketplace.stderr.log",
    )
    package_root = marketplace_root / "plugins" / PLUGIN_NAME
    if not package_root.is_dir():
        raise SystemExit(f"Builder did not create expected plugin package root: {package_root}")
    return {
        "marketplace_root": str(marketplace_root),
        "package_root": str(package_root),
        "packaged_entries": parse_packaged_entries(result.stdout),
        "builder_stdout_path": str(run_root / "results" / "build-local-marketplace.stdout.log"),
        "builder_stderr_path": str(run_root / "results" / "build-local-marketplace.stderr.log"),
    }


def copy_clean_target(package_root: Path, target_root: Path) -> None:
    if target_root.exists():
        shutil.rmtree(target_root)
    target_root.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(package_root, target_root, ignore=shutil.ignore_patterns(".DS_Store", "__pycache__"))
    assert_no_plugin_eval(target_root)


def assert_no_plugin_eval(target_root: Path) -> None:
    plugin_eval_path = target_root / ".plugin-eval"
    if plugin_eval_path.exists():
        raise SystemExit(f"Refusing polluted target; .plugin-eval exists inside {target_root}")


def find_plugin_eval_command(explicit: str | None) -> list[str] | None:
    if explicit:
        return shlex.split(explicit)
    from_path = shutil.which("plugin-eval")
    if from_path:
        return [from_path]

    cache_root = Path.home() / ".codex" / "plugins" / "cache" / "openai-curated-remote" / "plugin-eval"
    candidates = sorted(cache_root.glob("*/scripts/plugin-eval.js"), reverse=True)
    for script in candidates:
        if script.is_file() and shutil.which("node"):
            return ["node", str(script)]
    return None


def run_plugin_eval_analyze(command: list[str] | None, target_root: Path, scenario_result_root: Path) -> dict:
    analyze_path = scenario_result_root / "plugin-eval-analyze.json"
    if not command:
        return {
            "status": "not_run",
            "reason": "plugin-eval command not found",
            "path": None,
            "static_budgets": None,
        }

    result = run_command(
        [*command, "analyze", str(target_root), "--format", "json", "--output", str(analyze_path)],
        cwd=target_root,
        stdout_path=scenario_result_root / "plugin-eval-analyze.stdout.log",
        stderr_path=scenario_result_root / "plugin-eval-analyze.stderr.log",
        check=False,
    )
    relocate_plugin_eval_dir(target_root, scenario_result_root)
    assert_no_plugin_eval(target_root)
    if result.returncode != 0:
        return {
            "status": "failed",
            "exit_code": result.returncode,
            "path": str(analyze_path),
            "static_budgets": None,
        }

    budgets = None
    if analyze_path.exists():
        data = json.loads(analyze_path.read_text(encoding="utf-8"))
        raw_budgets = data.get("budgets") or {}
        budgets = {
            "trigger_cost_tokens": budget_value(raw_budgets.get("trigger_cost_tokens")),
            "invoke_cost_tokens": budget_value(raw_budgets.get("invoke_cost_tokens")),
            "deferred_cost_tokens": budget_value(raw_budgets.get("deferred_cost_tokens")),
        }
    return {
        "status": "completed",
        "path": str(analyze_path),
        "static_budgets": budgets,
    }


def budget_value(bucket: object) -> int | None:
    if isinstance(bucket, dict) and isinstance(bucket.get("value"), int):
        return bucket["value"]
    return None


def scenario_workspace_files(scenario: str) -> dict[str, str]:
    common_boundary = (
        "Do not run plugin-eval, scripts/run_plugin_eval_clean.py, eval scripts, "
        "benchmark commands, or repository-wide discovery. Use only the files in "
        "this workspace plus the local Groundwork plugin if it is useful.\n"
    )
    if scenario == "to-prd":
        return {
            "TASK.md": (
                "# Rough Requirement\n\n"
                "A maintainer wants a draft-only PRD workflow for proposed plugin "
                "changes. The PRD should capture the visible user value, acceptance "
                "criteria, evidence needed before implementation, and open decisions. "
                "No file edits are requested; produce the PRD/spec in the final answer.\n\n"
                "If local Groundwork guidance is useful, read only "
                "`plugins/groundwork/skills/to-prd/SKILL.md`. Do not inspect "
                "Groundwork plugin README, `.codex-plugin/plugin.json`, plugin manifests, "
                "package internals, `PRD-TEMPLATE.md`, `GRILL-BEFORE-WRITE.md`, or shared "
                "lifecycle/evidence references unless this task explicitly asks for a "
                "durable artifact, source-backed product truth, wiki-backed context, or "
                "lifecycle gate evaluation.\n\n"
                f"{common_boundary}"
            )
        }
    if scenario == "verify":
        return {
            "CLAIM.md": (
                "# Claim To Verify\n\n"
                "Claim: A local package-boundary change is ready to be treated as "
                "runtime evidence because the package build and static checks passed.\n\n"
                "If local Groundwork guidance is useful, read only "
                "`plugins/groundwork/skills/verify/SKILL.md`, "
                "`plugins/groundwork/skills/verify/VERIFY-SCOPE.md`, and "
                "`plugins/groundwork/skills/verify/SCOPE-EVIDENCE-TEMPLATE.md`. "
                "Do not inspect Groundwork plugin README, `.codex-plugin/plugin.json`, "
                "plugin manifests, package internals, other skill `SKILL.md` files, "
                "or repository-wide docs/source unless this task explicitly asks for "
                "Groundwork maintenance, plugin/package/install/cache/release verification, "
                "or a named in-scope artifact cites that path.\n\n"
                f"{common_boundary}"
            ),
            "EVIDENCE.md": (
                "# Available Evidence\n\n"
                "- Static package-boundary check passed.\n"
                "- Skill entry budget check passed.\n"
                "- No installed-cache equivalence check has been provided.\n"
                "- No live runtime or UAT run has been provided.\n"
            ),
        }
    if scenario == "dispatch":
        return {
            "ACCEPTED-TASK.md": (
                "# Accepted Task\n\n"
                "Prepare a Dispatch Package v2 for a small documentation-only change: "
                "update an existing maintainer guide so benchmark reports separate "
                "static estimates, observed runtime usage, and installed-cache evidence. "
                "The package should stay package-only and include source truth, readiness, "
                "a compact task matrix, safety policy, required evidence, stop conditions, "
                "and expected output type. Do not produce an adapter-ready package, full "
                "schema, runtime adapter analysis, model/profile selection, or result "
                "package details unless explicitly requested. Do not execute the work; "
                "produce the compact package skeleton in the final answer.\n\n"
                "If local Groundwork guidance is useful, read only "
                "`plugins/groundwork/skills/dispatch/SKILL.md` and "
                "`plugins/groundwork/skills/dispatch/DISPATCH-PACKAGE.md`. Do not inspect "
                "Groundwork plugin README, `.codex-plugin/plugin.json`, plugin manifests, "
                "package internals, `DISPATCH-PACKAGE-DETAILS.md`, `RESULT-PACKAGE.md`, "
                "`RUNTIME-ADAPTERS.md`, `ROUTING-PROFILES.md`, or `EXAMPLES.md` unless "
                "this task explicitly asks for adapter-ready output, full schema, runtime "
                "adapter behavior, model/profile selection, examples, or returned evidence "
                "details.\n\n"
                f"{common_boundary}"
            )
        }
    return {
        "TASK.md": (
            f"# {scenario} Scenario Task\n\n"
            "Use the local Groundwork plugin only if it helps. Produce a concise "
            "final answer for this task without editing files.\n\n"
            f"{common_boundary}"
        )
    }


def write_benchmark_workspace_source(scenario: str, scenario_result_root: Path) -> Path:
    workspace_source = scenario_result_root / "workspace-source"
    if workspace_source.exists():
        shutil.rmtree(workspace_source)
    workspace_source.mkdir(parents=True, exist_ok=True)
    for relative_path, contents in scenario_workspace_files(scenario).items():
        path = workspace_source / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(contents, encoding="utf-8")
    return workspace_source


def scenario_user_input(scenario: str) -> str:
    if scenario == "to-prd":
        task = (
            "Read TASK.md in the current workspace and produce a compact PRD/spec "
            "with acceptance criteria, known facts, assumptions, open questions, "
            "and implementation-prep evidence needs in the final answer only. If "
            "Groundwork guidance is useful, read only "
            "plugins/groundwork/skills/to-prd/SKILL.md and do not inspect plugin "
            "README, .codex-plugin/plugin.json, package internals, PRD-TEMPLATE.md, "
            "GRILL-BEFORE-WRITE.md, or shared lifecycle/evidence references unless "
            "this task explicitly asks for durable, source-backed, wiki-backed, or "
            "lifecycle-gate output."
        )
    elif scenario == "verify":
        task = (
            "Read CLAIM.md and EVIDENCE.md in the current workspace and produce a "
            "scope-first verification report that separates covered, not covered, "
            "and missing evidence. If Groundwork guidance is useful, read only "
            "plugins/groundwork/skills/verify/SKILL.md, "
            "plugins/groundwork/skills/verify/VERIFY-SCOPE.md, and "
            "plugins/groundwork/skills/verify/SCOPE-EVIDENCE-TEMPLATE.md. Do not "
            "inspect plugin README, .codex-plugin/plugin.json, plugin manifests, "
            "package internals, or other skill SKILL.md files unless this task "
            "explicitly asks for Groundwork maintenance, plugin/package/install/cache/"
            "release verification, or a named in-scope artifact cites that path."
        )
    elif scenario == "dispatch":
        task = (
            "Read ACCEPTED-TASK.md in the current workspace and produce a Dispatch "
            "Package v2 compact package skeleton in the final answer only. If Groundwork "
            "guidance is useful, read only plugins/groundwork/skills/dispatch/SKILL.md "
            "and plugins/groundwork/skills/dispatch/DISPATCH-PACKAGE.md. Do not inspect "
            "plugin README, .codex-plugin/plugin.json, package internals, "
            "DISPATCH-PACKAGE-DETAILS.md, RESULT-PACKAGE.md, RUNTIME-ADAPTERS.md, "
            "ROUTING-PROFILES.md, or EXAMPLES.md unless this task explicitly asks for "
            "adapter-ready output, full schema, runtime adapter behavior, model/profile "
            "selection, examples, or returned evidence details."
        )
    else:
        task = (
            "Read TASK.md in the current workspace and produce a concise final "
            "answer for the requested Groundwork scenario."
        )
    return (
        f"Use the local Codex plugin {PLUGIN_NAME!r} if it helps. {task} "
        "Do not edit files. Do not run plugin-eval. Do not run "
        "scripts/run_plugin_eval_clean.py. Do not run eval scripts, benchmark "
        "commands, or broad repository scans."
    )


def scenario_success_checklist(scenario: str) -> list[str]:
    checklist = [
        "The response stays within the requested Groundwork scenario.",
        "No nested Plugin Eval, run_plugin_eval_clean.py, eval script, or benchmark command is run.",
        "The agent uses only the minimal scenario workspace plus the local plugin when useful.",
        "Runtime/cache/release claims are not made without installed-plugin evidence.",
        "Observed token usage is recorded when Codex emits usage telemetry.",
    ]
    if scenario == "dispatch":
        checklist.append("The final answer is a package-only dispatch result and does not execute the task.")
    return checklist


def write_benchmark_config(source: Path, scenario: str, scenario_result_root: Path) -> Path:
    config_path = scenario_result_root / "benchmark.json"
    workspace_source = write_benchmark_workspace_source(scenario, scenario_result_root)
    config = {
        "kind": "plugin-eval-benchmark",
        "schemaVersion": 2,
        "version": 2,
        "targetKind": "plugin",
        "targetName": PLUGIN_NAME,
        "runner": {
            "type": "codex-cli",
            "model": "gpt-5.4",
            "sandbox": "workspace-write",
            "approvalPolicy": "never",
            "extraArgs": [],
        },
        "workspace": {
            "sourcePath": str(workspace_source),
            "setupMode": "copy",
            "preserve": "on-failure",
        },
        "targetProvisioning": {
            "mode": "workspace-plugin-marketplace",
        },
        "verifiers": {
            "commands": [],
        },
        "scenarios": [
            {
                "id": scenario,
                "title": scenario,
                "purpose": f"Measure Groundwork runtime behavior for the {scenario} scenario.",
                "userInput": scenario_user_input(scenario),
                "successChecklist": scenario_success_checklist(scenario),
            }
        ],
    }
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")
    return config_path


def benchmark_command(
    command: list[str] | None,
    target_root: Path,
    config_path: Path,
    scenario_result_root: Path,
    model: str | None,
) -> list[str] | None:
    base_command = command or ["plugin-eval"]
    args = [
        *base_command,
        "benchmark",
        str(target_root),
        "--config",
        str(config_path),
        "--usage-out",
        str(scenario_result_root / "observed-usage.jsonl"),
        "--result-out",
        str(scenario_result_root / "benchmark-result.json"),
        "--format",
        "json",
        "--output",
        str(scenario_result_root / "benchmark-output.json"),
    ]
    if model:
        args.extend(["--model", model])
    return args


def run_plugin_eval_benchmark(
    command_args: list[str] | None,
    command_available: bool,
    target_root: Path,
    scenario_result_root: Path,
    execute: bool,
    print_commands: bool,
) -> dict:
    command_text = shell_join(command_args) if command_args else None
    print(command_text)

    if print_commands or not execute:
        return {
            "status": "not_run",
            "reason": "print_commands" if print_commands else "execute flag not set",
            "command": command_text,
            "observed_usage": None,
        }
    if not command_available:
        return {
            "status": "not_run",
            "reason": "plugin-eval command not found",
            "command": command_text,
            "observed_usage": None,
        }

    result = run_command(
        command_args,
        cwd=target_root,
        stdout_path=scenario_result_root / "plugin-eval-benchmark.stdout.log",
        stderr_path=scenario_result_root / "plugin-eval-benchmark.stderr.log",
        check=False,
    )
    relocate_plugin_eval_dir(target_root, scenario_result_root)
    assert_no_plugin_eval(target_root)
    runtime_trace = read_runtime_trace_summary(scenario_result_root)
    status = benchmark_status(result.returncode, runtime_trace)
    return {
        "status": status,
        "exit_code": result.returncode,
        "command": command_text,
        "observed_usage": read_observed_usage(scenario_result_root / "observed-usage.jsonl"),
        "runtime_trace": runtime_trace,
    }


def relocate_plugin_eval_dir(target_root: Path, scenario_result_root: Path) -> None:
    plugin_eval_dir = target_root / ".plugin-eval"
    if not plugin_eval_dir.exists():
        return
    destination = scenario_result_root / "target-plugin-eval-output"
    if destination.exists():
        shutil.rmtree(destination)
    shutil.move(str(plugin_eval_dir), str(destination))


def benchmark_status(exit_code: int, runtime_trace: dict) -> str:
    if exit_code != 0:
        return "failed"
    if runtime_trace.get("status") != "present":
        return "failed"
    if runtime_trace.get("nested_command_count", 0) > 0:
        return "failed"
    if runtime_trace.get("forbidden_source_scan_count", 0) > 0:
        return "failed"
    return "completed"


def read_runtime_trace_summary(scenario_result_root: Path) -> dict:
    log_paths = sorted((scenario_result_root / "target-plugin-eval-output").rglob("codex.stdout.jsonl"))
    if not log_paths:
        return {
            "status": "not_found",
            "log_paths": [],
            "model_turn_count": 0,
            "command_execution_count": 0,
            "nested_command_count": 0,
            "nested_commands": [],
            "forbidden_source_scan_count": 0,
            "forbidden_source_scan_commands": [],
            "broad_scan_count": 0,
            "broad_scan_commands": [],
            "package_files_read": [],
            "invalid_json_line_count": 0,
        }

    model_turn_count = 0
    command_execution_count = 0
    nested_commands: list[str] = []
    forbidden_source_scan_commands: list[str] = []
    broad_scan_commands: list[str] = []
    package_files_read: set[str] = set()
    invalid_json_line_count = 0

    for log_path in log_paths:
        for line in log_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            try:
                payload = json.loads(line)
            except json.JSONDecodeError:
                invalid_json_line_count += 1
                continue

            if payload.get("type") == "turn.started":
                model_turn_count += 1

            item = payload.get("item")
            if not isinstance(item, dict):
                continue
            if payload.get("type") != "item.completed" or item.get("type") != "command_execution":
                continue

            command = item.get("command")
            if not isinstance(command, str):
                continue
            command_execution_count += 1
            if is_nested_benchmark_command(command):
                nested_commands.append(command)
            if is_forbidden_source_scan_command(command):
                forbidden_source_scan_commands.append(command)
            if is_broad_scan_command(command):
                broad_scan_commands.append(command)
            package_files_read.update(extract_package_file_reads(command))

    return {
        "status": "present",
        "log_paths": [str(path) for path in log_paths],
        "model_turn_count": model_turn_count,
        "command_execution_count": command_execution_count,
        "nested_command_count": len(nested_commands),
        "nested_commands": nested_commands,
        "forbidden_source_scan_count": len(forbidden_source_scan_commands),
        "forbidden_source_scan_commands": forbidden_source_scan_commands,
        "broad_scan_count": len(broad_scan_commands),
        "broad_scan_commands": broad_scan_commands,
        "package_files_read": sorted(package_files_read),
        "invalid_json_line_count": invalid_json_line_count,
    }


def is_nested_benchmark_command(command: str) -> bool:
    for segment in command_segments(command_words(command)):
        if not segment:
            continue
        tool = Path(segment[0]).name
        if tool == "plugin-eval":
            return True
        if tool == "node" and any(is_plugin_eval_script_path(arg) for arg in segment[1:]):
            return True
        if tool in {"which", "command"} and "plugin-eval" in segment[1:]:
            return True
        if is_run_plugin_eval_wrapper_path(segment[0]):
            return True
        if tool in SCRIPT_EXECUTORS and any(is_run_plugin_eval_wrapper_path(arg) for arg in segment[1:]):
            return True
        if any(is_benchmark_script_path(arg) for arg in segment):
            return True
    return False


def is_broad_scan_command(command: str) -> bool:
    return any(pattern in command for pattern in BROAD_SCAN_PATTERNS)


def is_forbidden_source_scan_command(command: str) -> bool:
    for segment in command_segments(command_words(command)):
        if not segment:
            continue
        tool = Path(segment[0]).name
        args = segment[1:]
        if tool == "rg" and any(is_forbidden_source_path(path) for path in ripgrep_path_operands(args)):
            return True
        if tool == "grep" and any(is_forbidden_source_path(path) for path in grep_path_operands(args)):
            return True
        if tool == "find" and any(is_forbidden_source_path(path) for path in find_path_operands(args)):
            return True
        if tool == "ls" and any(is_forbidden_source_path(path) for path in ls_path_operands(args)):
            return True
    return False


def command_words(command: str) -> list[str]:
    try:
        words = shlex.split(command)
    except ValueError:
        return command.split()
    if len(words) >= 3 and Path(words[0]).name in {"sh", "bash", "zsh"} and words[1] == "-lc":
        try:
            return shlex.split(words[2])
        except ValueError:
            return words[2].split()
    return words


def command_segments(words: list[str]) -> list[list[str]]:
    segments: list[list[str]] = []
    current: list[str] = []
    separators = {"&&", "||", "|", ";"}
    for word in words:
        if word in separators:
            if current:
                segments.append(current)
                current = []
            continue
        current.append(word)
    if current:
        segments.append(current)
    return segments


def non_option_args(args: list[str], value_options: set[str]) -> list[str]:
    values: list[str] = []
    skip_next = False
    for arg in args:
        if skip_next:
            skip_next = False
            continue
        if arg == "--":
            values.extend(args[args.index(arg) + 1 :])
            break
        if arg in value_options:
            skip_next = True
            continue
        if arg.startswith("--") and "=" in arg:
            continue
        if arg.startswith("-"):
            continue
        values.append(arg)
    return values


def ripgrep_path_operands(args: list[str]) -> list[str]:
    value_options = {"-e", "--regexp", "-g", "--glob", "-t", "--type", "-T", "--type-not", "-f", "--file"}
    values = non_option_args(args, value_options)
    if "--files" in args or "--files-with-matches" in args:
        return values
    uses_pattern_option = any(arg in {"-e", "--regexp"} or arg.startswith("--regexp=") for arg in args)
    return values if uses_pattern_option else values[1:]


def grep_path_operands(args: list[str]) -> list[str]:
    value_options = {"-e", "--regexp", "-f", "--file"}
    values = non_option_args(args, value_options)
    uses_pattern_option = any(arg in {"-e", "--regexp"} or arg.startswith("--regexp=") for arg in args)
    return values if uses_pattern_option else values[1:]


def find_path_operands(args: list[str]) -> list[str]:
    paths: list[str] = []
    for arg in args:
        if arg.startswith("-") or arg in {"(", ")", "!", ","}:
            break
        paths.append(arg)
    return paths


def ls_path_operands(args: list[str]) -> list[str]:
    return [arg for arg in args if not arg.startswith("-")]


def is_forbidden_source_path(path: str) -> bool:
    cleaned = path.strip().rstrip("/")
    while cleaned.startswith("./"):
        cleaned = cleaned[2:]
    if any(cleaned == root or cleaned.startswith(f"{root}/") for root in FORBIDDEN_SOURCE_SCAN_ROOTS):
        return True
    try:
        relative = Path(cleaned).expanduser().resolve().relative_to(REPO_ROOT)
    except (OSError, ValueError):
        return False
    return bool(relative.parts and relative.parts[0] in FORBIDDEN_SOURCE_SCAN_ROOTS)


def is_plugin_eval_script_path(path: str) -> bool:
    cleaned = path.strip()
    return Path(cleaned).name == "plugin-eval.js" or "/plugin-eval/" in cleaned


def is_run_plugin_eval_wrapper_path(path: str) -> bool:
    cleaned = path.strip()
    return cleaned.endswith("scripts/run_plugin_eval_clean.py")


def is_benchmark_script_path(path: str) -> bool:
    cleaned = path.strip()
    name = Path(cleaned).name.lower()
    if "benchmark" not in name:
        return False
    parts = Path(cleaned).parts
    if "scripts" in parts or "evals" in parts:
        return True
    try:
        relative = Path(cleaned).expanduser().resolve().relative_to(REPO_ROOT)
    except (OSError, ValueError):
        return False
    return bool(relative.parts and relative.parts[0] in {"scripts", "evals"})


def extract_package_file_reads(command: str) -> set[str]:
    read_commands = ("sed ", "cat ", "nl ", "awk ", "python ")
    if not any(read_command in command for read_command in read_commands):
        return set()
    return {
        match.group(0).rstrip(".,:")
        for match in re.finditer(r"plugins/groundwork/[A-Za-z0-9_./-]+", command)
    }


def read_observed_usage(usage_path: Path) -> dict | None:
    if not usage_path.exists():
        return None
    input_tokens = 0
    output_tokens = 0
    total_tokens = 0
    samples = 0
    skipped_lines = 0
    invalid_lines = 0
    for line in usage_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            skipped_lines += 1
            continue
        try:
            payload = json.loads(line)
        except json.JSONDecodeError:
            invalid_lines += 1
            continue
        usage = extract_usage_payload(payload)
        if not isinstance(usage, dict):
            invalid_lines += 1
            continue
        token_values = {
            "input_tokens": parse_token_count(usage.get("input_tokens")),
            "output_tokens": parse_token_count(usage.get("output_tokens")),
            "total_tokens": parse_token_count(usage.get("total_tokens")),
        }
        if all(value is None for value in token_values.values()):
            invalid_lines += 1
            continue
        if token_values["total_tokens"] is None:
            token_values["total_tokens"] = (
                (token_values["input_tokens"] or 0)
                + (token_values["output_tokens"] or 0)
            )
        input_tokens += token_values["input_tokens"] or 0
        output_tokens += token_values["output_tokens"] or 0
        total_tokens += token_values["total_tokens"] or 0
        samples += 1
    if samples == 0:
        return {
            "status": "unavailable",
            "sample_count": 0,
            "skipped_line_count": skipped_lines,
            "invalid_line_count": invalid_lines,
            "path": str(usage_path),
        }
    return {
        "status": "present",
        "sample_count": samples,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": total_tokens,
        "skipped_line_count": skipped_lines,
        "invalid_line_count": invalid_lines,
        "path": str(usage_path),
    }


def extract_usage_payload(payload: object) -> object | None:
    if not isinstance(payload, dict):
        return None
    direct_usage = payload.get("usage")
    if direct_usage is not None:
        return direct_usage
    response = payload.get("response")
    if isinstance(response, dict):
        return response.get("usage")
    return None


def parse_token_count(value: object) -> int | None:
    if isinstance(value, bool) or value is None:
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, str) and value.isdigit():
        return int(value)
    return None


def find_installed_cache_root() -> str | None:
    root = Path.home() / ".codex" / "plugins" / "cache" / "groundwork" / PLUGIN_NAME
    if not root.is_dir():
        return None
    versions = [path for path in root.iterdir() if path.is_dir()]
    if not versions:
        return None
    newest = max(versions, key=lambda path: path.stat().st_mtime)
    return str(newest)


def write_run_manifest(run_root: Path, manifest: dict) -> Path:
    path = run_root / "results" / "run-manifest.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return path


def main() -> int:
    args = parse_args()
    ensure_target_basename(args.target_basename)
    source = resolve_source(args.source)
    run_root = ensure_run_root(args.run_root or timestamp_run_root(), source, args.force)
    result_root = run_root / "results"
    if result_root.exists():
        shutil.rmtree(result_root)
    result_root.mkdir(parents=True, exist_ok=True)

    command = find_plugin_eval_command(args.plugin_eval_command)
    marketplace = build_marketplace(source, run_root)
    package_root = Path(marketplace["package_root"])
    scenarios = [clean_id(scenario) for scenario in args.scenario]

    scenario_results = []
    for scenario in scenarios:
        scenario_root = run_root / scenario
        target_root = scenario_root / args.target_basename
        scenario_result_root = result_root / scenario
        scenario_result_root.mkdir(parents=True, exist_ok=True)
        copy_clean_target(package_root, target_root)
        analyze_result = run_plugin_eval_analyze(command, target_root, scenario_result_root)
        config_path = write_benchmark_config(source, scenario, scenario_result_root)
        command_args = benchmark_command(command, target_root, config_path, scenario_result_root, args.model)
        benchmark_result = run_plugin_eval_benchmark(
            command_args=command_args,
            command_available=command is not None,
            target_root=target_root,
            scenario_result_root=scenario_result_root,
            execute=args.execute,
            print_commands=args.print_commands,
        )
        assert_no_plugin_eval(target_root)
        scenario_results.append(
            {
                "scenario": scenario,
                "target_root": str(target_root),
                "target_basename": target_root.name,
                "result_root": str(scenario_result_root),
                "benchmark_config": str(config_path),
                "plugin_eval_command": benchmark_result["command"],
                "analyze": analyze_result,
                "benchmark": benchmark_result,
            }
        )

    manifest = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "source_root": str(source),
        "source_repo_sha": git_value(source, "rev-parse", "HEAD"),
        "source_dirty_status": git_value(source, "status", "--short"),
        "run_root": str(run_root),
        "result_root": str(result_root),
        "marketplace": marketplace,
        "installed_cache_root": find_installed_cache_root(),
        "plugin_eval_command_detected": command,
        "execute": args.execute,
        "print_commands": args.print_commands,
        "scenarios": scenario_results,
    }
    manifest_path = write_run_manifest(run_root, manifest)
    print(f"Run manifest: {manifest_path}")
    print(f"Marketplace root: {marketplace['marketplace_root']}")
    print(f"Package root: {marketplace['package_root']}")
    print(f"Result root: {result_root}")
    if any(result["benchmark"]["status"] == "failed" for result in scenario_results):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
