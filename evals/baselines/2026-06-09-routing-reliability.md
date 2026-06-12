# Groundwork Routing Reliability Targeted Baseline

Target Reader: Groundwork maintainer reviewing RR-008 routing reliability evidence.
Reader Action Needed: Review the targeted routing run, cache/source status, and release-gate decision before deciding whether RR-009 or RR-010 may proceed.
Decision Supported: Whether the targeted routing runtime evidence can be treated as release-gating, diagnostic, blocked, or ready for follow-up remediation.
Scope: RR-008 targeted `routing-reliability.csv` schema validation, serial runtime run, cache/source comparison, runner mutation check, and targeted routing metrics.
Out Of Scope: Runtime-surface edits, public skill frontmatter edits, `.codex-plugin/plugin.json` edits, lifecycle preflight edits, default-suite promotion, staging, committing, pushing, issue closure, and installed plugin cache mutation.
Evidence Level: Source checkout evidence, installed plugin cache hash comparison, targeted runner output, raw runtime artifacts, and repository validation commands from the Codex-managed worktree.

## Metadata

- Date: 2026-06-09 local time.
- Task ID: RR-008.
- Source package root: `/Users/daxiong/.codex/worktrees/7fc9/Groundwork`.
- Source truth repository: `/Users/daxiong/Documents/sourceCode/Groundwork`.
- Current worktree state: detached HEAD.
- Branch check:
  - `git branch --show-current`: empty output.
  - `git symbolic-ref --short HEAD || true`: `fatal: ref HEAD is not a symbolic ref`.
- Base commit / HEAD: `b37bdf58380f4b4f0d4f35086ab15309dd368b06`.
- Installed plugin root: `/Users/daxiong/.codex/plugins/cache/groundwork/groundwork/0.3.0`.
- Installed manifest path: `/Users/daxiong/.codex/plugins/cache/groundwork/groundwork/0.3.0/.codex-plugin/plugin.json`.
- Suite: `routing-reliability.csv`.
- Suite scope: targeted-only; `routing-reliability.csv` is not in `DEFAULT_SUITES`.
- Intended RR-008 edit allowlist: `evals/baselines/2026-06-09-routing-reliability.md`.

## Dependency And Scope Check

RR-007 documentation/checklist expectations are present in `evals/runtime-trial-checklist.md`:

- targeted routing trial runs before default-suite promotion;
- runtime truth alignment requires branch/worktree state, `git status --short`, intended file allowlist, installed plugin root, source package root, compared path list, source/cache diff or supported refresh result, raw runtime result path, targeted/full scope, and runner mutation check;
- runtime evidence is diagnostic/non-release-gating when installed cache equivalence is not proven and no supported refresh is performed.

Pre-existing dependency dirty state before RR-008 baseline write:

```text
 M docs/prd-routing-reliability.md
 M docs/skill-success-metrics.md
 M evals/run_runtime.py
 M evals/runtime-trial-checklist.md
 M evals/test_run_runtime_scheduler.py
?? docs/routing-reliability-issues.md
?? evals/prompts/routing-reliability.csv
```

These files are treated as RR-001 through RR-007 dependency state. RR-008 did not edit them.

## Source / Cache Comparison

No supported cache refresh was performed. The installed cache was not manually mutated.

Comparison command used a SHA-256 check between:

- source: `/Users/daxiong/.codex/worktrees/7fc9/Groundwork`
- cache: `/Users/daxiong/.codex/plugins/cache/groundwork/groundwork/0.3.0`

Compared path list and outcome:

| Path | Result |
| --- | --- |
| `.codex-plugin/plugin.json` | same |
| `README.md` | same |
| `AGENTS.md` | same |
| `skills/handoff/SKILL.md` | same |
| `skills/implement/SKILL.md` | same |
| `skills/prototype/SKILL.md` | same |
| `skills/to-issues/SKILL.md` | same |
| `skills/to-prd/SKILL.md` | same |
| `skills/triage/SKILL.md` | same |
| `skills/verify/SKILL.md` | same |
| `skills/write-plan/SKILL.md` | same |
| `skills/_shared/LIFECYCLE-PREFLIGHT.md` | same |
| `skills/_shared/GIT-TOPOLOGY-GATE.md` | same |
| `docs/prd-routing-reliability.md` | different |
| `docs/routing-reliability-issues.md` | missing in cache |
| `docs/skill-success-metrics.md` | different |
| `evals/runtime-trial-checklist.md` | different |
| `evals/run_runtime.py` | different |
| `evals/run_runtime_parallel.py` | same |
| `evals/test_run_runtime_scheduler.py` | different |
| `evals/prompts/routing-reliability.csv` | missing in cache |

Decision:

- Cache/source equivalence: not proven.
- Supported refresh result: not performed.
- Runtime evidence release-gating status: diagnostic / non-release-gating.
- Reason: the targeted suite and several routing reliability docs/runner files differ from or are absent in the installed plugin cache.

## Targeted Schema Validation

Command:

```bash
python3 evals/run_runtime.py --validate-schema --suite routing-reliability.csv
```

Result:

```text
schema_validation: pass
suites: routing-reliability.csv
rows: 24
routing_rows: 24
errors: []
recognized_fields:
- intent_kind
- requirement_state
- source_truth
- risk_gate
- expected_state_transition
- expected_stop_condition
- expected_best
- acceptable_routes
- forbidden_routes
- route_boundary
- case_kind
- case_source
- output_contract
- evidence_required
```

## Targeted Runtime Run

Command:

```bash
python3 evals/run_runtime.py --suite routing-reliability.csv --jobs 1
```

Process result:

- Exit code: 1.
- Reason: targeted rows completed as `blocked`; the runner produced artifacts, but each `codex exec` row exited 1.
- Row-level environment blocker evidence from `logs/rr-001.jsonl`: Codex could not initialize runtime state under `/Users/daxiong/.codex` because the state DB was read-only in this worktree context, then failed to initialize the in-process app-server client with `Operation not permitted`.
- Run root: `/private/tmp/groundwork-runtime-v03/20260608T162944Z`.
- Raw summary: `/private/tmp/groundwork-runtime-v03/20260608T162944Z/summary.json`.
- Raw results: `/private/tmp/groundwork-runtime-v03/20260608T162944Z/results.jsonl`.
- Raw failures: `/private/tmp/groundwork-runtime-v03/20260608T162944Z/failures.md`.
- Raw cases: `/private/tmp/groundwork-runtime-v03/20260608T162944Z/cases`.
- Raw logs: `/private/tmp/groundwork-runtime-v03/20260608T162944Z/logs`.
- Suite scope: targeted-only.
- Jobs: 1.

Verdict counts:

| Verdict | Count |
| --- | ---: |
| pass | 0 |
| partial | 0 |
| fail | 0 |
| blocked | 24 |

Runner execution mutation check:

- `git status --short` before targeted runtime run matched `git status --short` after targeted runtime run.
- Runner execution did not mutate source repository files.
- The only RR-008 source mutation is this baseline file, written after the runtime run.

## Targeted Routing Metric Summary

From `/private/tmp/groundwork-runtime-v03/20260608T162944Z/summary.json` `routing_summary`:

| Metric | Count / Total | Rate |
| --- | ---: | ---: |
| Best-route Hit@1 | 3 / 24 | 0.125 |
| Acceptable route coverage | 3 / 24 | 0.125 |
| Forbidden route hits | 10 / 24 | 0.4166666666666667 |
| Invalid host preemption | 0 / 24 | 0.0 |
| Unclassified non-pass | 0 / 24 | 0.0 |

Routing outcomes:

| Outcome | Count |
| --- | ---: |
| best | 3 |
| forbidden | 10 |
| unexpected | 11 |

Per-route counts:

| Route | Expected | Actual |
| --- | ---: | ---: |
| direct | 3 | 24 |
| implement | 7 | 0 |
| prototype | 2 | 0 |
| to-issues | 1 | 0 |
| to-prd | 6 | 0 |
| verify | 4 | 0 |
| write-plan | 1 | 0 |

Route-pair confusion:

| Pair | Count |
| --- | ---: |
| direct -> direct | 3 |
| implement -> direct | 7 |
| prototype -> direct | 2 |
| to-issues -> direct | 1 |
| to-prd -> direct | 6 |
| verify -> direct | 4 |
| write-plan -> direct | 1 |

Verdict dimension counts:

| Dimension | Counts |
| --- | --- |
| `routing_verdict` | `pass=3`, `fail=21` |
| `host_preemption_verdict` | `pass=4`, `not_applicable=20` |
| `output_contract_verdict` | `fail=24` |
| `evidence_verdict` | `pass=13`, `fail=6`, `blocked=5` |
| `behavior_verdict` | `pass=24` |
| `overall_verdict` | `blocked=24` |

Route boundary counts:

| Boundary | Count | Pass | Fail | Blocking |
| --- | ---: | ---: | ---: | ---: |
| entry-contract | 4 | 0 | 0 | 4 |
| explicit-bypass-vs-raw-intent | 4 | 0 | 0 | 4 |
| implement-vs-verify | 4 | 0 | 0 | 4 |
| prototype-vs-verify | 4 | 0 | 0 | 4 |
| requirement-state-vs-implementation | 4 | 0 | 0 | 4 |
| runtime-safety-gate-vs-skill-gate | 4 | 0 | 0 | 4 |

Failure type counts:

| Failure type | Count |
| --- | ---: |
| codex_exit | 24 |

## Release-Gate Decision

Runtime evidence status: diagnostic / non-release-gating.

Rationale:

- Source/cache equivalence was not proven.
- No supported cache refresh was performed.
- `routing-reliability.csv` is absent from the installed cache.
- The targeted runtime run completed with all rows `blocked` and `codex exec exit 1` in failure type counts.
- The run still provides useful diagnostic metrics for RR-009 investigation, but it must not be used as release-gating proof or default-promotion evidence.

Default-suite promotion decision:

- `targeted_only`.
- `routing-reliability.csv` remains outside `DEFAULT_SUITES`.
- RR-010 promotion remains blocked pending stable targeted baseline evidence with cache/source equivalence or supported refresh.

## Validation Summary

Commands and observed results:

| Command | Result |
| --- | --- |
| `git status --short` before runtime | pre-existing dependency dirt only |
| source/cache SHA-256 comparison | not equivalent |
| `python3 evals/run_runtime.py --validate-schema --suite routing-reliability.csv` | pass, 24 rows |
| `python3 evals/run_runtime.py --suite routing-reliability.csv --jobs 1` | exit 1, produced run artifacts, 24 blocked |
| `git status --short` after runtime | unchanged from before runtime |
| `git diff --check` after baseline write | pass |
| `python3 -m json.tool .codex-plugin/plugin.json >/dev/null` | pass |
| `python3 -c "import csv, pathlib; [list(csv.DictReader(open(p, newline=''))) for p in pathlib.Path('evals/prompts').glob('*.csv')]; print('csv ok')"` | pass, `csv ok` |
| `git diff --name-only` after baseline write | only pre-existing tracked dependency diffs; untracked RR-008 baseline is listed separately by `git status --short` |
| `git ls-files --others --exclude-standard` | `docs/routing-reliability-issues.md`, `evals/baselines/2026-06-09-routing-reliability.md`, `evals/prompts/routing-reliability.csv` |
| `DEFAULT_SUITES` check in `evals/run_runtime.py` | `routing-reliability.csv in DEFAULT_SUITES: False` |

Final RR-008 git status:

```text
 M docs/prd-routing-reliability.md
 M docs/skill-success-metrics.md
 M evals/run_runtime.py
 M evals/runtime-trial-checklist.md
 M evals/test_run_runtime_scheduler.py
?? docs/routing-reliability-issues.md
?? evals/baselines/2026-06-09-routing-reliability.md
?? evals/prompts/routing-reliability.csv
```

Forbidden/non-goal diff check:

- RR-008 touched only `evals/baselines/2026-06-09-routing-reliability.md`.
- No RR-008 edit was made to `.codex-plugin/plugin.json`, public skill frontmatter, `skills/_shared/LIFECYCLE-PREFLIGHT.md`, `docs/prd-routing-reliability.md`, `docs/routing-reliability-issues.md`, `docs/skill-success-metrics.md`, `evals/runtime-trial-checklist.md`, `evals/run_runtime.py`, `evals/run_runtime_parallel.py`, `evals/test_run_runtime_scheduler.py`, or `evals/prompts/routing-reliability.csv`.

## Follow-Up

- RR-009 should not make runtime-surface edits from this baseline alone as release-gating evidence, because cache/source equivalence was not proven.
- RR-009 may use the raw run diagnostically to investigate why all rows returned `codex exec exit 1`, all actual routes were `direct`, and all output contracts failed.
- A release-gating targeted rerun requires either supported cache refresh through the install/marketplace path or a new source/cache equivalence proof.
