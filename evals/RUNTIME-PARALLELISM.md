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
python evals/run_runtime.py --jobs 4 --resource-policy auto
python evals/run_runtime.py --serial
python evals/run_runtime.py --all-prompts --jobs 3
python evals/run_runtime.py --rerun-failures /path/to/results
python evals/run_runtime.py --jobs 2 --group browser
```

`evals/run_runtime_parallel.py` remains as a compatibility entrypoint and
delegates to `evals/run_runtime.py`.

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

When metadata is absent, the runner infers conservative defaults from the
existing CSV fields. Prompt-only, read-only, isolated workspace cases may run in
the bounded pool. Browser, shared Codex state, repo-root, and flaky cases are
kept out of that pool and run serially after the parallel-safe cases.

`--group <name>` filters the selected rows to an explicit `group` metadata
value, an inferred group such as `browser`, `shared`, `flaky`, `isolated`, or
`serial`, or a declared resource key. For example, `--group browser` runs only
browser-resource cases with the selected suite/id filters.

## Acceptance

- independent cases can run with `--jobs N`;
- each case writes its own result file;
- aggregate summary distinguishes pass / fail / blocked / timeout / flake when available;
- failures can be rerun without scanning unrelated cases;
- timeout retries are explicit and do not retry semantic failures;
- per-case wrapper timeout also controls the child `codex exec` timeout;
- serial mode remains available for reproduction;
- browser/shared-state cases can be limited by metadata in future work.
