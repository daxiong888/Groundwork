#!/usr/bin/env python3
"""Bounded-parallel wrapper for Groundwork runtime evals.

This additive wrapper runs the existing `evals/run_runtime.py` one case at a time in
parallel child processes. Each child gets its own runtime root, so the current
runner's shared `results.jsonl` file is not written by multiple workers.

It does not enforce future `parallel_safe` or `resource_keys` metadata yet. Use
it for targeted smoke runs, not full mixed-resource scheduler runs.

It is intentionally conservative and can later be folded into `run_runtime.py`.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO = Path(os.environ.get("GROUNDWORK_REPO", Path(__file__).resolve().parents[1]))
ROOT = Path(os.environ.get("GROUNDWORK_RUNTIME_ROOT", "/private/tmp/groundwork-runtime-v03-parallel"))
RUN = ROOT / datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
CASES = RUN / "cases"
CHILD_STDOUT = RUN / "child-stdout"
SUMMARY = RUN / "summary.json"
FAILURES = RUN / "failures.md"

DEFAULT_SUITES = [
    "smoke.csv",
    "safety.csv",
    "reliability.csv",
    "guardrails-regression.csv",
    "lifecycle-state.csv",
    "lifecycle-preflight-regressions.csv",
]


def safe_id(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "-", value).strip("-") or "case"


def boolish(value: object) -> bool:
    return str(value).strip().lower() == "true"


def expected_skill_for_row(row: dict[str, str]) -> str:
    if row.get("expected_skill"):
        return row["expected_skill"]

    expected = row.get("skill") or "direct"
    behavior = row.get("expected_behavior") or ""
    if not boolish(row.get("should_trigger", "true")):
        route_match = re.search(r"Should route to ([A-Za-z0-9_-]+)", behavior)
        if route_match:
            return route_match.group(1)
        return "direct"

    return expected


def prompt_suites() -> list[str]:
    return sorted(p.name for p in (REPO / "evals" / "prompts").glob("*.csv"))


def read_rows(suites: list[str]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for suite in suites:
        path = REPO / "evals" / "prompts" / suite
        if not path.exists():
            continue
        with path.open(newline="", encoding="utf-8") as fh:
            for row in csv.DictReader(fh):
                row["_suite"] = suite
                rows.append(row)
    return rows


def load_failure_ids(path: Path) -> list[str]:
    """Load failed case ids from a previous summary directory or summary file."""
    summary_path = path / "summary.json" if path.is_dir() else path
    if not summary_path.exists():
        raise FileNotFoundError(f"missing summary file: {summary_path}")
    data = json.loads(summary_path.read_text(encoding="utf-8"))
    failures = data.get("failures") or []
    if isinstance(failures, list):
        ids: list[str] = []
        for item in failures:
            if isinstance(item, str):
                ids.append(item)
            elif isinstance(item, dict) and item.get("id"):
                ids.append(str(item["id"]))
        return ids
    raise ValueError(f"summary does not contain a supported failures list: {summary_path}")


def parse_child_result(stdout: str, row: dict[str, str], returncode: int) -> dict[str, Any]:
    parsed: dict[str, Any] | None = None
    for line in stdout.splitlines():
        line = line.strip()
        if not line.startswith("{"):
            continue
        try:
            candidate = json.loads(line)
        except json.JSONDecodeError:
            continue
        if candidate.get("id") == row["id"]:
            parsed = candidate
    if parsed is None:
        parsed = {
            "id": row["id"],
            "suite": row.get("_suite"),
            "expected": expected_skill_for_row(row),
            "actual": "unknown",
            "verdict": "blocked" if returncode else "unknown",
            "notes": "child run produced no parseable per-case summary",
        }
    parsed["child_returncode"] = returncode
    return parsed


def run_case(row: dict[str, str], timeout_s: int) -> dict[str, Any]:
    case_id = safe_id(row["id"])
    case_root = RUN / "child-runs" / case_id
    case_root.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    env["GROUNDWORK_RUNTIME_ROOT"] = str(case_root)
    env["GROUNDWORK_CODEX_TIMEOUT"] = str(max(60, timeout_s - 30))

    cmd = [sys.executable, str(REPO / "evals" / "run_runtime.py"), row["id"]]
    try:
        proc = subprocess.run(
            cmd,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            timeout=timeout_s,
            env=env,
            cwd=str(REPO),
        )
        stdout = proc.stdout
        returncode = proc.returncode
    except subprocess.TimeoutExpired as exc:
        stdout = exc.stdout or ""
        if isinstance(stdout, bytes):
            stdout = stdout.decode("utf-8", errors="replace")
        stdout += f"\nwrapper_timeout={timeout_s}\n"
        returncode = 124

    stdout_path = CHILD_STDOUT / f"{case_id}.txt"
    stdout_path.write_text(stdout, encoding="utf-8")
    result = parse_child_result(stdout, row, returncode)
    result["wrapper_child_root"] = str(case_root)
    result["wrapper_stdout"] = str(stdout_path)
    result["wrapper_finished"] = datetime.now(timezone.utc).isoformat()

    case_path = CASES / f"{case_id}.json"
    case_path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return result


def is_timeout_result(result: dict[str, Any]) -> bool:
    notes = str(result.get("notes") or "")
    return result.get("child_returncode") == 124 or "codex exec exit 124" in notes


def run_case_with_retries(row: dict[str, str], timeout_s: int, retry_timeouts: int) -> dict[str, Any]:
    attempts = 0
    result: dict[str, Any] | None = None
    while attempts <= retry_timeouts:
        attempts += 1
        result = run_case(row, timeout_s)
        if not is_timeout_result(result):
            break
    assert result is not None
    result["wrapper_attempts"] = attempts
    if attempts > 1:
        result["wrapper_retried_timeout"] = True
    return result


def wrapper_exception_result(row: dict[str, str], exc: BaseException) -> dict[str, Any]:
    case_id = safe_id(row.get("id", "unknown"))
    stdout_path = CHILD_STDOUT / f"{case_id}.txt"
    stdout_path.write_text(
        f"wrapper_exception={type(exc).__name__}: {exc}\n",
        encoding="utf-8",
    )
    result: dict[str, Any] = {
        "id": row.get("id"),
        "suite": row.get("_suite"),
        "expected": expected_skill_for_row(row),
        "actual": "unknown",
        "verdict": "blocked",
        "notes": f"wrapper exception: {type(exc).__name__}: {exc}",
        "wrapper_stdout": str(stdout_path),
        "wrapper_finished": datetime.now(timezone.utc).isoformat(),
    }
    case_path = CASES / f"{case_id}.json"
    case_path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return result


def summarize(results: list[dict[str, Any]], jobs: int, suites: list[str]) -> dict[str, Any]:
    counts: dict[str, int] = {}
    for result in results:
        verdict = str(result.get("verdict", "unknown"))
        counts[verdict] = counts.get(verdict, 0) + 1

    failures = [
        {
            "id": result.get("id"),
            "suite": result.get("suite"),
            "verdict": result.get("verdict"),
            "notes": result.get("notes"),
            "stdout": result.get("wrapper_stdout"),
        }
        for result in results
        if result.get("verdict") != "pass"
    ]

    summary = {
        "run_root": str(RUN),
        "jobs": jobs,
        "suites": suites,
        "rows": len(results),
        "counts": counts,
        "failures": failures,
        "finished": datetime.now(timezone.utc).isoformat(),
    }
    SUMMARY.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    lines = ["# Runtime Failures", ""]
    if not failures:
        lines.append("No non-pass results.")
    else:
        for item in failures:
            lines.append(f"- `{item['id']}` [{item['suite']}] {item['verdict']}: {item.get('notes') or ''}")
    FAILURES.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return summary


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Groundwork runtime evals with bounded parallelism.")
    parser.add_argument("ids", nargs="*", help="Optional case ids to run.")
    parser.add_argument("--all-prompts", action="store_true", help="Run all prompt CSV suites.")
    parser.add_argument("--suite", action="append", help="Prompt suite filename to include; may be repeated.")
    parser.add_argument("--jobs", type=int, default=1, help="Maximum concurrent child runs. Default: 1.")
    parser.add_argument("--serial", action="store_true", help="Force serial execution, equivalent to --jobs 1.")
    parser.add_argument("--rerun-failures", type=Path, help="Path to a previous summary.json or run directory.")
    parser.add_argument("--case-timeout", type=int, default=420, help="Wrapper timeout per case in seconds.")
    parser.add_argument("--retry-timeouts", type=int, default=0, help="Retry codex exec timeout results per case. Default: 0.")
    args = parser.parse_args(argv)

    jobs = 1 if args.serial else max(1, args.jobs)
    suites = args.suite or (prompt_suites() if args.all_prompts or args.ids or args.rerun_failures else DEFAULT_SUITES)
    rows = read_rows(suites)

    target_ids = set(args.ids)
    if args.rerun_failures:
        target_ids.update(load_failure_ids(args.rerun_failures))

    if target_ids:
        rows = [row for row in rows if row.get("id") in target_ids]
        missing = sorted(target_ids - {row.get("id") for row in rows})
        if missing:
            print("missing_ids=" + ",".join(missing), flush=True)
            return 2

    CASES.mkdir(parents=True, exist_ok=True)
    CHILD_STDOUT.mkdir(parents=True, exist_ok=True)
    print(f"run_root={RUN}", flush=True)
    print(f"rows={len(rows)}", flush=True)
    print(f"jobs={jobs}", flush=True)

    results: list[dict[str, Any]] = []
    if jobs == 1:
        for row in rows:
            result = run_case_with_retries(row, args.case_timeout, args.retry_timeouts)
            results.append(result)
            print(json.dumps({k: result.get(k) for k in ["id", "suite", "verdict", "notes"]}, ensure_ascii=False), flush=True)
    else:
        with ThreadPoolExecutor(max_workers=jobs) as executor:
            future_to_row = {
                executor.submit(run_case_with_retries, row, args.case_timeout, args.retry_timeouts): row
                for row in rows
            }
            for future in as_completed(future_to_row):
                row = future_to_row[future]
                try:
                    result = future.result()
                except Exception as exc:  # Keep one wrapper failure from aborting the full run.
                    result = wrapper_exception_result(row, exc)
                results.append(result)
                print(json.dumps({k: result.get(k) for k in ["id", "suite", "verdict", "notes"]}, ensure_ascii=False), flush=True)

    results.sort(key=lambda item: str(item.get("id", "")))
    summary = summarize(results, jobs, suites)
    print(json.dumps({"summary": summary}, ensure_ascii=False), flush=True)
    return 1 if summary["failures"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
