#!/usr/bin/env python3
"""Check clean targeted Plugin Eval runtime results against regression thresholds."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


REQUIRED_SCENARIOS = ("to-prd", "verify", "dispatch")
INPUT_THRESHOLDS = {
    "to-prd": 35_000,
    "verify": 55_000,
    "dispatch": 50_000,
}
TOTAL_INPUT_THRESHOLD = 140_000
EXPECTED_PACKAGE_READS = {
    "to-prd": {
        "plugins/groundwork/skills/to-prd/SKILL.md",
    },
    "verify": {
        "plugins/groundwork/skills/verify/SKILL.md",
        "plugins/groundwork/skills/verify/VERIFY-SCOPE.md",
        "plugins/groundwork/skills/verify/SCOPE-EVIDENCE-TEMPLATE.md",
    },
    "dispatch": {
        "plugins/groundwork/skills/dispatch/SKILL.md",
        "plugins/groundwork/skills/dispatch/DISPATCH-PACKAGE.md",
    },
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate clean targeted Plugin Eval run manifests against read-path regression thresholds."
    )
    parser.add_argument(
        "paths",
        nargs="+",
        type=Path,
        help="Path to run-manifest.json or a run root containing results/run-manifest.json. Pass one multi-scenario manifest or multiple single-scenario manifests.",
    )
    parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="Output format. Default: text.",
    )
    return parser.parse_args()


def resolve_manifest_path(path: Path) -> Path:
    if path.is_dir():
        candidate = path / "results" / "run-manifest.json"
        if candidate.is_file():
            return candidate
        candidate = path / "run-manifest.json"
        if candidate.is_file():
            return candidate
    return path


def load_manifest(path: Path) -> dict:
    manifest_path = resolve_manifest_path(path)
    if not manifest_path.is_file():
        raise ValueError(f"manifest not found: {path}")
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid manifest JSON: {manifest_path}: {exc}") from exc
    if not isinstance(manifest, dict):
        raise ValueError(f"manifest root is not an object: {manifest_path}")
    manifest["_manifest_path"] = str(manifest_path)
    return manifest


def collect_scenarios(manifests: list[dict]) -> dict[str, dict]:
    scenarios: dict[str, dict] = {}
    for manifest in manifests:
        manifest_scenarios = manifest.get("scenarios")
        if not isinstance(manifest_scenarios, list):
            continue
        for scenario in manifest_scenarios:
            if not isinstance(scenario, dict):
                continue
            name = scenario.get("scenario")
            if not isinstance(name, str):
                continue
            record = dict(scenario)
            record["_manifest_path"] = manifest.get("_manifest_path")
            if name in scenarios:
                raise ValueError(f"duplicate scenario in manifests: {name}")
            scenarios[name] = record
    return scenarios


def int_value(value: object) -> int | None:
    if isinstance(value, bool) or value is None:
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, str) and value.isdigit():
        return int(value)
    return None


def unexpected_package_reads(package_files: list[str], expected: set[str]) -> list[str]:
    unexpected: list[str] = []
    for path in package_files:
        if path not in expected:
            unexpected.append(path)
    return unexpected


def validate_scenarios(scenarios: dict[str, dict]) -> dict:
    failures: list[str] = []
    metrics: dict[str, dict] = {}

    missing = [scenario for scenario in REQUIRED_SCENARIOS if scenario not in scenarios]
    if missing:
        failures.append(f"missing scenarios: {', '.join(missing)}")

    total_input = 0
    for name in REQUIRED_SCENARIOS:
        scenario = scenarios.get(name)
        if not scenario:
            continue
        benchmark = scenario.get("benchmark") if isinstance(scenario.get("benchmark"), dict) else {}
        usage = benchmark.get("observed_usage") if isinstance(benchmark.get("observed_usage"), dict) else {}
        trace = benchmark.get("runtime_trace") if isinstance(benchmark.get("runtime_trace"), dict) else {}
        input_tokens = int_value(usage.get("input_tokens"))
        output_tokens = int_value(usage.get("output_tokens"))
        total_tokens = int_value(usage.get("total_tokens"))
        model_turns = int_value(trace.get("model_turn_count"))
        command_count = int_value(trace.get("command_execution_count"))
        nested_count = int_value(trace.get("nested_command_count")) or 0
        forbidden_scan_count = int_value(trace.get("forbidden_source_scan_count")) or 0
        broad_scan_count = int_value(trace.get("broad_scan_count")) or 0
        package_files = trace.get("package_files_read") if isinstance(trace.get("package_files_read"), list) else []

        metrics[name] = {
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": total_tokens,
            "model_turn_count": model_turns,
            "command_execution_count": command_count,
            "nested_command_count": nested_count,
            "forbidden_source_scan_count": forbidden_scan_count,
            "broad_scan_count": broad_scan_count,
            "package_files_read": package_files,
            "status": benchmark.get("status"),
            "valid_for_usage_regression": benchmark.get("valid_for_usage_regression"),
            "manifest_path": scenario.get("_manifest_path"),
        }

        if benchmark.get("status") != "completed":
            failures.append(f"{name}: benchmark status is {benchmark.get('status')}, expected completed")
        if benchmark.get("valid_for_usage_regression") is not True:
            failures.append(f"{name}: valid_for_usage_regression is not true")
        if input_tokens is None or input_tokens <= 0:
            failures.append(f"{name}: missing positive input_tokens")
        elif input_tokens > INPUT_THRESHOLDS[name]:
            failures.append(f"{name}: input_tokens {input_tokens} exceeds threshold {INPUT_THRESHOLDS[name]}")
        if model_turns != 1:
            failures.append(f"{name}: model_turn_count {model_turns} != 1")
        if nested_count != 0:
            failures.append(f"{name}: nested_command_count {nested_count} != 0")
        if forbidden_scan_count != 0:
            failures.append(f"{name}: forbidden_source_scan_count {forbidden_scan_count} != 0")

        extra_reads = unexpected_package_reads(package_files, EXPECTED_PACKAGE_READS.get(name, set()))
        if extra_reads:
            failures.append(f"{name}: unexpected package reads: {', '.join(extra_reads)}")

        total_input += input_tokens or 0

    if total_input > TOTAL_INPUT_THRESHOLD:
        failures.append(f"total input_tokens {total_input} exceeds threshold {TOTAL_INPUT_THRESHOLD}")

    return {
        "status": "pass" if not failures else "fail",
        "thresholds": {
            "input_tokens": INPUT_THRESHOLDS,
            "total_input_tokens": TOTAL_INPUT_THRESHOLD,
            "model_turn_count_per_scenario": 1,
            "nested_command_count": 0,
            "forbidden_source_scan_count": 0,
            "expected_package_reads": EXPECTED_PACKAGE_READS,
        },
        "total_input_tokens": total_input,
        "metrics": metrics,
        "failures": failures,
    }


def render_text(result: dict) -> str:
    lines = [
        f"clean targeted plugin eval regression: {result['status']}",
        f"total input tokens: {result['total_input_tokens']} / {TOTAL_INPUT_THRESHOLD}",
    ]
    for name in REQUIRED_SCENARIOS:
        metrics = result["metrics"].get(name)
        if not metrics:
            continue
        lines.append(
            f"{name}: input={metrics['input_tokens']} output={metrics['output_tokens']} "
            f"total={metrics['total_tokens']} turns={metrics['model_turn_count']} "
            f"commands={metrics['command_execution_count']} nested={metrics['nested_command_count']} "
            f"forbidden_scans={metrics['forbidden_source_scan_count']} broad_scans={metrics['broad_scan_count']}"
        )
    if result["failures"]:
        lines.append("failures:")
        lines.extend(f"- {failure}" for failure in result["failures"])
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    try:
        manifests = [load_manifest(path) for path in args.paths]
        result = validate_scenarios(collect_scenarios(manifests))
    except ValueError as exc:
        result = {
            "status": "fail",
            "thresholds": {
                "input_tokens": INPUT_THRESHOLDS,
                "total_input_tokens": TOTAL_INPUT_THRESHOLD,
            },
            "total_input_tokens": 0,
            "metrics": {},
            "failures": [str(exc)],
        }

    if args.format == "json":
        print(json.dumps(result, indent=2) + "\n", end="")
    else:
        print(render_text(result))
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
