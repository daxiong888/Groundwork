# Routing Reliability Default-Suite Promotion Baseline

Target Reader: Groundwork maintainer reviewing the v0.3.1 routing reliability default-suite decision.
Reader Action Needed: Treat `routing-reliability.csv` as part of default internal regression coverage starting in v0.3.1, while keeping future public-surface or release-gate broadening behind targeted evidence.
Decision Supported: Whether `routing-reliability.csv` should move from targeted-only evidence into `DEFAULT_SUITES` for personal and team-internal Groundwork use.
Scope: Plugin manifest version bump, serial runner default-suite membership, parallel wrapper compatibility by delegation, routing reliability promotion documentation, schema validation, runner unit tests, CSV parsing, source/package/cache refresh, and source/cache equivalence.
Out of Scope: Public SLA, new public skills, learned routing, retrieval/rerank pilots, MCP/A2A pilots, production observability dashboards, remote tracker writes, task CRUD, full targeted runtime rerun, full default runtime rerun, push, PR creation, and manual installed-cache mutation.
Evidence Level: Promotion decision based on prior targeted remediation evidence, focused RR closeout evidence, local dry-path validation, runner unit tests, and supported plugin reinstall/source-cache equivalence checks for the v0.3.1 package.

## Decision

Verdict: `promote_to_default`.

`routing-reliability.csv` enters `DEFAULT_SUITES` in v0.3.1 for internal default regression coverage. This does not change Groundwork's public skill surface and does not create a public release SLA.

The promotion is intentionally narrow:

- `evals/run_runtime.py` owns `DEFAULT_SUITES` and now includes `routing-reliability.csv`.
- `evals/run_runtime_parallel.py` remains a compatibility wrapper around the serial runner and does not maintain an independent default-suite list.
- Future broader promotion, public release-gating, or route-surface expansion still requires targeted evidence and a new recorded decision.

## Evidence Context

Recent evidence before this promotion:

- `RR-008B-RETRY` established targeted routing rerun evidence but did not support promotion at that time.
- `RR-009` and later focused remediations reduced the runtime surface based on observed evidence.
- `RR-012` closed the remaining focused `rr-005` and `rr-019` failures with targeted row evidence, while explicitly not claiming full targeted release-gate evidence.
- The maintainer decision on 2026-06-15 scoped this promotion to personal and team-internal use, so a new full runtime rerun is not required for this small default-suite membership change.

## Changed Files

- `.codex-plugin/plugin.json`: version bumped from `0.3.0` to `0.3.1`.
- `evals/run_runtime.py`: `routing-reliability.csv` added to `DEFAULT_SUITES`.
- `docs/prd-routing-reliability.md`: post-acceptance status records the v0.3.1 internal promotion boundary.
- `evals/runtime-trial-checklist.md`: routing reliability guidance now reflects default coverage starting in v0.3.1.
- `CHANGELOG.md`: v0.3.1 release note added.
- `evals/baselines/2026-06-15-routing-reliability-default-promotion.md`: this promotion record.

## Validation

Local validation before supported plugin reinstall:

| Check | Result |
| --- | --- |
| `python3 -m json.tool .codex-plugin/plugin.json` | pass, manifest version `0.3.1` |
| `python3 -B evals/run_runtime.py --validate-schema --suite routing-reliability.csv` | pass, 24 rows, 24 routing rows, 0 errors |
| `python3 -B -c "import evals.run_runtime as r; print('routing-reliability.csv' in r.DEFAULT_SUITES); print(','.join(r.DEFAULT_SUITES))"` | pass, `True`; default suites include `routing-reliability.csv` |
| `python3 -B evals/test_run_runtime_scheduler.py` | pass, 64 tests |
| `git diff --check` | pass |
| `python3 -c "import csv, pathlib; [list(csv.DictReader(open(p, newline=''))) for p in pathlib.Path('evals/prompts').glob('*.csv')]; print('csv ok')"` | pass |

Supported plugin reinstall and equivalence evidence:

| Check | Result |
| --- | --- |
| `codex plugin add groundwork@groundwork` | pass; installed plugin root `/Users/daxiong/.codex/plugins/cache/groundwork/groundwork/0.3.1` |
| `codex plugin list` | pass; `groundwork@groundwork` installed and enabled at version `0.3.1` |
| source/marketplace/cache package comparison | pass; source `125`, marketplace `125`, cache `125`, missing `0`, different `0` |

Compared package paths:

- `.codex-plugin`
- `skills`
- `docs`
- `evals`
- `CHANGELOG.md`

Runtime validation scope:

- Full targeted runtime rerun: not run for this final promotion step.
- Full default runtime rerun: not run for this final promotion step.
- Reason: the change is limited to default-suite membership, version metadata, and canonical documentation after prior focused route-remediation evidence; current use is personal and team-internal rather than public release-gate promotion.

## Promotion Boundary

This baseline supersedes earlier targeted-only promotion decisions only for the v0.3.1 internal default-suite membership. Earlier baseline notes remain accurate historical evidence for their run time.

Future changes still need a new baseline when they:

- add or remove default-suite members;
- broaden public skill routing surface;
- change measurement-token semantics across row groups;
- claim public release-gate or SLA status;
- introduce learned routing, retrieval/rerank, MCP/A2A, or observability backend behavior.
