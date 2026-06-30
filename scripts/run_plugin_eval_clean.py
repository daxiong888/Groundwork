#!/usr/bin/env python3
"""Prepare and optionally run a clean Plugin Eval benchmark for Groundwork."""

from __future__ import annotations

import argparse
import json
import os
import shlex
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RUN_ROOT_BASE = Path("/private/tmp/groundwork-plugin-eval")
PLUGIN_NAME = "groundwork"


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


def write_benchmark_config(source: Path, scenario: str, scenario_result_root: Path) -> Path:
    config_path = scenario_result_root / "benchmark.json"
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
            "sourcePath": str(source),
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
                "userInput": (
                    f"Use the local Codex plugin {PLUGIN_NAME!r} if it helps. "
                    f"Run the Groundwork {scenario} benchmark scenario and finish with a concise evidence report."
                ),
                "successChecklist": [
                    "The response stays within the requested Groundwork scenario.",
                    "Runtime/cache/release claims are not made without installed-plugin evidence.",
                    "Observed token usage is recorded when Codex emits usage telemetry.",
                ],
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
    return {
        "status": "completed" if result.returncode == 0 else "failed",
        "exit_code": result.returncode,
        "command": command_text,
        "observed_usage": read_observed_usage(scenario_result_root / "observed-usage.jsonl"),
    }


def relocate_plugin_eval_dir(target_root: Path, scenario_result_root: Path) -> None:
    plugin_eval_dir = target_root / ".plugin-eval"
    if not plugin_eval_dir.exists():
        return
    destination = scenario_result_root / "target-plugin-eval-output"
    if destination.exists():
        shutil.rmtree(destination)
    shutil.move(str(plugin_eval_dir), str(destination))


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
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
