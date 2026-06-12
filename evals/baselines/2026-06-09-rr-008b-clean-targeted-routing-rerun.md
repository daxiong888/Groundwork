# RR-008B Clean Targeted Routing Reliability Rerun

Target Reader: Groundwork maintainer reviewing the RR-008B clean targeted rerun.
Reader Action Needed: Decide whether RR-009 remediation may proceed from current targeted routing evidence.
Decision Supported: Whether the clean targeted routing rerun is release-gating, diagnostic-only, blocked, or ready for follow-up remediation.
Scope: RR-008B targeted `routing-reliability.csv` source/cache equivalence check, schema validation, serial runtime rerun, artifact inspection, and release-gating classification.
Out Of Scope: Plugin reinstall or refresh, installed plugin cache mutation, runtime-surface edits, public skill edits, lifecycle preflight edits, eval runner behavior changes, prompt CSV semantic changes, default-suite promotion, staging, committing, pushing, issue closure, and PR creation.
Evidence Level: Installed plugin cache/source byte comparison for the required 22 paths, targeted schema validation, targeted serial runtime artifacts, and repository validation commands.

## Metadata

- Date: 2026-06-09 local time.
- Task ID: RR-008B-RETRY.
- Source worktree: `/Users/daxiong/.codex/worktrees/c164/Groundwork`.
- Source truth repository: `/Users/daxiong/Documents/sourceCode/Groundwork`.
- Installed plugin root: `/Users/daxiong/.codex/plugins/cache/groundwork/groundwork/0.3.0`.
- Suite: `routing-reliability.csv`.
- Suite scope: targeted-only; `routing-reliability.csv` remains outside `DEFAULT_SUITES`.
- Runtime command: `python3 evals/run_runtime.py --suite routing-reliability.csv --jobs 1`.
- Runtime scope: targeted serial run, not a default-suite run.

## Source / Cache Equivalence

No plugin reinstall, plugin marketplace upgrade, supported refresh, or manual installed-cache mutation was performed before or during RR-008B.

Required path comparison result:

```text
worktree -> cache: compared=22 same=22 different=0 missing_cache=0 missing_source=0
canonical source -> cache: compared=22 same=22 different=0 missing_cache=0 missing_source=0
```

Compared paths:

- `.codex-plugin/plugin.json`
- `README.md`
- `AGENTS.md`
- `skills/to-prd/SKILL.md`
- `skills/to-issues/SKILL.md`
- `skills/triage/SKILL.md`
- `skills/write-plan/SKILL.md`
- `skills/prototype/SKILL.md`
- `skills/implement/SKILL.md`
- `skills/verify/SKILL.md`
- `skills/handoff/SKILL.md`
- `skills/_shared/LIFECYCLE-PREFLIGHT.md`
- `skills/_shared/GIT-TOPOLOGY-GATE.md`
- `docs/prd-routing-reliability.md`
- `docs/routing-reliability-issues.md`
- `docs/skill-success-metrics.md`
- `evals/runtime-trial-checklist.md`
- `evals/run_runtime.py`
- `evals/run_runtime_parallel.py`
- `evals/test_run_runtime_scheduler.py`
- `evals/prompts/routing-reliability.csv`
- `evals/baselines/2026-06-09-routing-reliability.md`

Decision:

- Cache/source equivalence verdict used: equivalent.
- Runtime evidence status: release-gating targeted rerun evidence.
- Default-suite status: no promotion; `routing-reliability.csv` remains targeted-only.

## Validation

Static and schema checks:

| Command | Result |
| --- | --- |
| `git status --short` before runtime | dependency dirty state present; no RR-008B edits yet |
| `python3 -m json.tool .codex-plugin/plugin.json >/dev/null` | pass |
| `python3 -c "import csv, pathlib; [list(csv.DictReader(open(p, newline=''))) for p in pathlib.Path('evals/prompts').glob('*.csv')]; print('csv ok')"` | pass, `csv ok` |
| `python3 -c "import evals.run_runtime as r; print('routing-reliability.csv in DEFAULT_SUITES:', 'routing-reliability.csv' in r.DEFAULT_SUITES); print('DEFAULT_SUITES=', ','.join(r.DEFAULT_SUITES))"` | pass, `routing-reliability.csv in DEFAULT_SUITES: False` |
| `git diff --check` | pass |
| `python3 evals/run_runtime.py --validate-schema --suite routing-reliability.csv` | pass, 24 rows, 24 routing rows, 0 errors |

The first sandboxed serial runtime produced artifacts at `/private/tmp/groundwork-runtime-v03/20260609T010058Z`, but every row was blocked by nested `codex exec` environment failure:

```text
counts: {"blocked": 24}
failure_type_counts: {"codex_exit": 24}
results failure_type: {"codex_exit": 24}
results fix_locus: {"runtime_environment": 24}
log evidence: failed to open /Users/daxiong/.codex/state_5.sqlite; attempt to write a readonly database; failed to initialize in-process app-server client: Operation not permitted
```

Because that failure was sandbox/environment-shaped, the same targeted runtime command was retried outside the sandbox. The escalated retry is the clean RR-008B release-gating targeted runtime evidence below.

## Clean Targeted Runtime Evidence

- Raw run root: `/private/tmp/groundwork-runtime-v03/20260609T010155Z`.
- Summary: `/private/tmp/groundwork-runtime-v03/20260609T010155Z/summary.json`.
- Results: `/private/tmp/groundwork-runtime-v03/20260609T010155Z/results.jsonl`.
- Failures: `/private/tmp/groundwork-runtime-v03/20260609T010155Z/failures.md`.
- Runner exit code: 1.
- Rows: 24.
- Jobs: 1.
- Resource policy: `auto`.

Overall counts:

```text
pass=9
fail=11
blocked=3
timeout=1
```

Routing metrics:

```text
best_route_hit_at_1: 17/24 = 0.7083333333333334
acceptable_route_coverage: 17/24 = 0.7083333333333334
forbidden_route_hits: 2/24 = 0.08333333333333333
invalid_host_preemption: 0/24 = 0.0
routing_outcomes: {"best": 17, "forbidden": 2, "unexpected": 5}
```

Route pair confusion:

```text
direct -> direct: 1
direct -> using-superpowers: 2
implement -> implement: 6
implement -> using-superpowers: 1
prototype -> prototype: 2
to-issues -> to-issues: 1
to-prd -> implement: 1
to-prd -> to-issues: 1
to-prd -> to-prd: 2
to-prd -> using-superpowers: 2
verify -> verify: 4
write-plan -> write-plan: 1
```

Failure type counts:

```text
codex_timeout: 1
future_evidence_required: 3
output_contract_failure: 5
premature_implementation: 2
route_miss: 4
```

Fix locus counts from `results.jsonl`:

```text
measurement_token: 3
requirement_state_gate: 2
routing_surface: 4
runtime_environment: 1
skill_output_contract: 5
```

Non-pass rows:

| ID | Verdict | failure_type | fix_locus | Notes |
| --- | --- | --- | --- | --- |
| `rr-003` | blocked | `future_evidence_required` | `measurement_token` | `source_or_unverified` token not implemented |
| `rr-005` | timeout | `codex_timeout` | `runtime_environment` | loaded `using-superpowers` instead of `to-prd`; timed out |
| `rr-007` | fail | `output_contract_failure` | `skill_output_contract` | implement conformance block missing required fields |
| `rr-008` | fail | `premature_implementation` | `requirement_state_gate` | forbidden `to-issues`; expected `to-prd` |
| `rr-009` | fail | `output_contract_failure` | `skill_output_contract` | implement conformance/gate fields missing; `tests_or_unverified` token not implemented |
| `rr-010` | fail | `premature_implementation` | `requirement_state_gate` | forbidden `implement`; expected `to-prd` |
| `rr-011` | fail | `route_miss` | `routing_surface` | loaded `using-superpowers`; expected `to-prd` |
| `rr-012` | fail | `route_miss` | `routing_surface` | loaded `using-superpowers`; expected `implement`; output/gate fields missing |
| `rr-015` | fail | `output_contract_failure` | `skill_output_contract` | implement conformance block missing required fields |
| `rr-018` | blocked | `future_evidence_required` | `measurement_token` | `source_or_unverified` token not implemented |
| `rr-020` | blocked | `future_evidence_required` | `measurement_token` | `browser_or_unverified` token not implemented |
| `rr-021` | fail | `route_miss` | `routing_surface` | loaded `using-superpowers`; expected direct/runtime-safety-gate; gate fields missing |
| `rr-022` | fail | `output_contract_failure` | `skill_output_contract` | implement conformance block missing required fields |
| `rr-023` | fail | `route_miss` | `routing_surface` | loaded `using-superpowers`; expected direct/runtime-safety-gate; gate fields missing |
| `rr-024` | fail | `output_contract_failure` | `skill_output_contract` | implement conformance block missing required fields |

## Source Mutation Boundary

The clean targeted runtime did not edit runtime-visible tracked source files in the worktree. `results.jsonl` reported isolated case workspace changes for `rr-005`:

```text
M README.md
A plugin_upgrade/__init__.py
A plugin_upgrade/__main__.py
A plugin_upgrade/workflow.py
A tests/test_plugin_upgrade_workflow.py
```

Those changes were reported from the runner's case workspace snapshot, not from the Groundwork source worktree. The source worktree status after the run retained the inherited RR dependency dirty state. Validation imports created untracked `evals/__pycache__/`; it was not staged.

## Release-Gating Decision

RR-008B is release-gating targeted runtime evidence because cache/source equivalence was proven immediately before runtime and no plugin reinstall or refresh occurred.

The rerun is not a passing release gate:

- runner exit code was 1;
- overall counts were `pass=9`, `fail=11`, `blocked=3`, `timeout=1`;
- routing verdicts were `pass=17`, `fail=7`;
- output contract verdicts were `pass=15`, `fail=9`;
- evidence verdicts were `pass=14`, `fail=5`, `blocked=5`;
- behavior verdicts were `pass=21`, `fail=3`;
- non-pass fix loci are concentrated in `skill_output_contract`, `routing_surface`, `measurement_token`, `requirement_state_gate`, and one `runtime_environment` timeout.

## RR-009 Decision

RR-009 may proceed as scoped remediation, not promotion.

Exact basis:

```text
failure_type_counts:
  output_contract_failure: 5
  route_miss: 4
  future_evidence_required: 3
  premature_implementation: 2
  codex_timeout: 1

fix_locus counts:
  skill_output_contract: 5
  routing_surface: 4
  measurement_token: 3
  requirement_state_gate: 2
  runtime_environment: 1
```

Recommended RR-009 focus:

- `skill_output_contract` for implement conformance/gate block requirements.
- `routing_surface` for `using-superpowers` route leakage and `to-prd` route misses.
- `measurement_token` for `source_or_unverified` and `browser_or_unverified`.
- `requirement_state_gate` for raw/draft requirement paths entering implementation-ready routes too early.
- `runtime_environment` timeout remains a single-row runtime concern and should not be ignored, but it is not the dominant fix locus.
