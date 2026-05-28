# Runtime Eval Bounded Parallelism Design

Target Reader: Groundwork maintainers improving `evals/run_runtime.py` and evaluating v0.3 regression speed.
Reader Action Needed: Decide whether to adopt a bounded parallel scheduler, per-case result files, and serial fallback.
Decision Supported: How to speed up runtime evals without introducing shared result writes, browser contention, or Codex state races.
Scope: Runner CLI, result layout, resource policy, rerun behavior, and compatibility with existing prompt CSV suites.
Out of Scope: Changing skill semantics, adding tracker integrations, or forcing browser/shared-state cases to run in parallel.
Evidence Level: Based on observed serial runner behavior and v0.3 lifecycle-state regression needs.
Related Issues: #32, #33.

## Problem

The current runtime runner executes rows serially. This is reliable but slow when many prompt cases are independent.

Naive shell parallelism is risky because cases may share:

- result files;
- Codex home or state DB;
- browser resources;
- repo fixtures;
- network or environment dependencies;
- stdout/stderr aggregation.

## Target CLI

```bash
python evals/run_runtime_parallel.py --jobs 4
python evals/run_runtime_parallel.py --serial
python evals/run_runtime_parallel.py --all-prompts --jobs 3
python evals/run_runtime_parallel.py --rerun-failures /path/to/results
python evals/run_runtime_parallel.py --all-prompts --serial --case-timeout 720 --retry-timeouts 1
```

Future integration may fold this behavior into `evals/run_runtime.py` as:

```bash
python evals/run_runtime.py --jobs 4 --resource-policy auto
python evals/run_runtime.py --serial
```

## Result Layout

```text
.groundwork or runtime root /
  <run-id>/
    cases/
      <case-id>.json
    child-stdout/
      <case-id>.txt
    summary.json
    failures.md
```

Per-case results avoid shared JSONL writes from concurrent workers.

## Resource Policy

Default behavior should be conservative:

- `--serial` or `--jobs 1` is fully reproducible;
- prompt-only / isolated workspace cases may run in bounded parallel;
- browser, shared Codex state, or flaky groups should be limited or serial;
- cases may declare `parallel_safe`, `resource_keys`, `timeout_s`, and `flake_policy` in future CSV metadata.

Current wrapper limitation: `evals/run_runtime_parallel.py` does not yet enforce `parallel_safe`, `resource_keys`, or resource-specific serial groups. Use it for targeted smoke runs, not full mixed-resource scheduler runs.

The wrapper passes its per-case timeout to `run_runtime.py` as the child `codex exec` timeout, leaving 30 seconds for wrapper cleanup.

## Acceptance

- independent cases can run with `--jobs N`;
- each case writes its own result file;
- aggregate summary distinguishes pass / fail / blocked / timeout / flake when available;
- failures can be rerun without scanning unrelated cases;
- timeout retries are explicit and do not retry semantic failures;
- per-case wrapper timeout also controls the child `codex exec` timeout;
- serial mode remains available for reproduction;
- browser/shared-state cases can be limited by metadata in future work.
