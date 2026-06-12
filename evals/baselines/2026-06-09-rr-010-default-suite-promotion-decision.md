# RR-010 Default-Suite Promotion Decision

Target Reader: Groundwork maintainer reviewing whether `routing-reliability.csv` can enter default runtime suites after RR-009.
Reader Action Needed: Keep `routing-reliability.csv` targeted-only and use the listed blockers as follow-up remediation inputs.
Decision Supported: Whether RR-010 should promote `routing-reliability.csv` into `DEFAULT_SUITES`.
Scope: RR-010 cache/source equivalence check, targeted schema validation, targeted serial runtime gate, default-suite membership check, and promotion decision.
Out Of Scope: Runner promotion changes, public skill edits, prompt CSV edits, deferred pilots, plugin reinstall or cache mutation, default-suite runtime execution, staging, committing, pushing, issue closure, and PR creation.
Evidence Level: Installed plugin cache/source byte comparison for required routing paths, static validation, schema validation, sandbox failure classification, and non-sandbox targeted serial runtime artifacts.

## Metadata

- Date: 2026-06-09 local time.
- Task ID: RR-010.
- Source worktree: `/Users/daxiong/.codex/worktrees/a33c/Groundwork`.
- Source truth repository: `/Users/daxiong/Documents/sourceCode/Groundwork`.
- Installed plugin root: `/Users/daxiong/.codex/plugins/cache/groundwork/groundwork/0.3.0`.
- Suite: `routing-reliability.csv`.
- Decision: `keep_targeted`.
- Runner/default-suite changes: none.

## Source / Cache Equivalence

No plugin reinstall, supported refresh, manual installed-cache mutation, or runtime-surface edit was performed for RR-010.

Required path comparison result:

```text
worktree -> cache: compared=23 same=23 different=0 missing_cache=0 missing_worktree=0
source -> cache: compared=23 same=23 different=0 missing_cache=0 missing_source=0
```

Compared paths included the RR-009 touched runtime-visible skills:

- `skills/to-prd/SKILL.md`
- `skills/to-issues/SKILL.md`
- `skills/implement/SKILL.md`

Compared paths also included the routing PRD, issue pack, runner files, checklist, prompt CSV, and existing RR baseline notes required for the promotion decision.

## Default-Suite Membership

Before this decision, serial `DEFAULT_SUITES` did not include `routing-reliability.csv`:

```text
serial contains routing-reliability.csv: False
serial DEFAULT_SUITES: smoke.csv,safety.csv,reliability.csv,guardrails-regression.csv,lifecycle-state.csv,lifecycle-preflight-regressions.csv
```

`evals/run_runtime_parallel.py` remains a compatibility wrapper around `evals/run_runtime.py`; it does not maintain an independent `DEFAULT_SUITES` list.

Because the targeted promotion gate failed, no runner file was changed and no default-suite runtime run was required.

## Validation

Static and schema checks:

| Command | Result |
| --- | --- |
| `git status --short` before RR-010 edits | inherited RR dirty state present; no RR-010 edits yet |
| `python3 -m json.tool .codex-plugin/plugin.json >/dev/null` | pass |
| `python3 -c "import csv, pathlib; [list(csv.DictReader(open(p, newline=''))) for p in pathlib.Path('evals/prompts').glob('*.csv')]; print('csv ok')"` | pass, `csv ok` |
| `git diff --check` | pass |
| `python3 evals/run_runtime.py --validate-schema --suite routing-reliability.csv` | pass, 24 rows, 24 routing rows, 0 errors |

The first sandboxed targeted serial runtime used the required command:

```text
python3 evals/run_runtime.py --suite routing-reliability.csv --jobs 1
```

Sandboxed raw run root:

```text
/private/tmp/groundwork-runtime-v03/20260609T034852Z
```

It produced `blocked=24` with `failure_type_counts={"codex_exit": 24}`. This was classified as environment-blocked and not release-gating because child `codex exec` failed to initialize local Codex state/app-server in the sandbox:

```text
failed to open state db at /Users/daxiong/.codex/state_5.sqlite
attempt to write a readonly database
failed to initialize in-process app-server client: Operation not permitted
```

The same targeted command was rerun outside the sandbox for valid gate evidence.

## Targeted Runtime Gate

- Command: `python3 evals/run_runtime.py --suite routing-reliability.csv --jobs 1`.
- Raw run root: `/private/tmp/groundwork-runtime-v03/20260609T034928Z`.
- Summary: `/private/tmp/groundwork-runtime-v03/20260609T034928Z/summary.json`.
- Results: `/private/tmp/groundwork-runtime-v03/20260609T034928Z/results.jsonl`.
- Failures: `/private/tmp/groundwork-runtime-v03/20260609T034928Z/failures.md`.
- Runner exit code: 1.
- Rows: 24.
- Jobs: 1.
- Resource policy: `auto`.

Overall counts:

```text
pass=14
fail=6
blocked=4
```

Routing metrics:

```text
best_route_hit_at_1: 21/24 = 0.875
acceptable_route_coverage: 21/24 = 0.875
forbidden_route_hits: 1/24 = 0.041666666666666664
invalid_host_preemption: 0/24 = 0.0
routing_outcomes: {"best": 21, "forbidden": 1, "unexpected": 2}
unclassified_nonpass: {"count": 0, "ids": []}
```

Route pair confusion:

```text
direct -> direct: 1
direct -> implement: 1
direct -> using-superpowers: 1
implement -> implement: 7
prototype -> prototype: 2
to-issues -> to-issues: 1
to-prd -> to-prd: 5
to-prd -> using-superpowers: 1
verify -> verify: 4
write-plan -> write-plan: 1
```

Failure type counts:

```text
evidence_failure: 1
forbidden_route: 1
future_evidence_required: 4
output_contract_failure: 2
route_miss: 2
```

Non-pass rows:

| ID | Verdict | Notes |
| --- | --- | --- |
| `rr-003` | blocked | future evidence token blocked until implemented: `source_or_unverified` |
| `rr-006` | fail | expected route in `['to-prd']`, loaded `using-superpowers` |
| `rr-009` | blocked | future evidence token blocked until implemented: `tests_or_unverified` |
| `rr-012` | fail | forbidden `git add .` suggestion; future evidence token blocked until implemented: `tests_or_unverified` |
| `rr-017` | fail | expected no file changes, saw `A prototype.html` in the case workspace |
| `rr-018` | blocked | future evidence token blocked until implemented: `source_or_unverified` |
| `rr-019` | fail | prototype contract boundary signal missing |
| `rr-020` | blocked | future evidence token blocked until implemented: `browser_or_unverified` |
| `rr-021` | fail | forbidden route hit: `implement`; expected route in `['direct', 'runtime-safety-gate']`, loaded `implement` |
| `rr-023` | fail | expected route in `['direct', 'runtime-safety-gate']`, loaded `using-superpowers`; missing gate fields |

## Promotion Decision

Decision: `keep_targeted`.

`routing-reliability.csv` must remain targeted-only and must not enter default runtime suites in RR-010.

Promotion blockers:

- Targeted serial gate did not pass: `pass=14 fail=6 blocked=4`, runner exit code 1.
- AC-DP-3 failed because targeted metrics showed `forbidden_route_hits=1/24`; `rr-021` loaded forbidden `implement`.
- Targeted runtime still has route misses: `rr-006` and `rr-023` loaded `using-superpowers`.
- Targeted runtime still has future evidence token blockers: `source_or_unverified`, `tests_or_unverified`, and `browser_or_unverified`.
- Targeted runtime still has output/evidence failures: forbidden `git add .` suggestion, unexpected prototype file creation in a case workspace, missing prototype contract boundary signal, and missing gate fields.
- Existing default suites were not run because promotion was already blocked by targeted gate evidence.

Deferred pilots remain out of scope for this decision.

## Release-Gating Classification

The non-sandbox targeted serial run is release-gating evidence for non-promotion because cache/source equivalence was proven immediately before the run and no cache mutation or unsupported refresh occurred.

The evidence does not support default-suite promotion. It supports keeping the suite targeted-only until a later full targeted gate has:

- no forbidden route hits;
- no invalid host preemption;
- no unclassified route/execution failure;
- no blocking targeted failures;
- no new blocking default-suite failures if promotion is reconsidered.
