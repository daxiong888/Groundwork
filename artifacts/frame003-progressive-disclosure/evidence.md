# Integrated Skill Contract Evidence

Target Reader: Groundwork maintainers reviewing the integrated replacement PR for draft PRs #74 through #79.
Reader Action Needed: Use this evidence map to see what the integrated source diff covers, which local checks were run, and which stronger runtime/release claims are not being made.
Decision Supported: Whether the integrated source changes are coherent enough for PR review and fresh clean review.
Artifact Type: evidence map
Source of Truth: Current branch `codex/frame-007-integrated-skill-contracts`, local source diff, eval prompt CSV files, and local validation command output from this integration pass.
Scope: Workflow state machine, evidence-boundary references, non-executor boundary references, progressive disclosure split for `dispatch` and `verify`, zh-CN trigger parity governance, coverage manifest validation, and CI source gates.
Out of Scope: Installed plugin cache refresh, Codex runtime execution, full-suite runtime behavior, release readiness, UAT readiness, customer readiness, marketplace publication, and merge approval.
Evidence Level: Source-validation and implementer self-check evidence only.
Safe to Share / Redaction Notes: Safe to share as-is; contains no secrets, credentials, PII, raw runtime logs, or private payloads.

## Requirement Map

| Requirement | Source Evidence | Local Check Evidence | Not Claimed |
|---|---|---|---|
| `issue_ready -> dispatch` is canonical when ready-for-agent evidence exists | `skills/_shared/WORKFLOW-STATE-MACHINE.md` lists `dispatch` accepted pre-states as `issue_ready`, `implementation_ready`, `verified` and adds an `issue_ready -> dispatch` gate. | `PYTHONPATH=evals python3 evals/run_runtime.py --validate-schema --suite zh-trigger-parity.csv` passed with 23 rows. | Runtime dispatch execution. |
| `blocked` is not a route-list token | `skills/_shared/WORKFLOW-STATE-MACHINE.md` separates route tokens from outcome/produced/stop-condition token `blocked`; routing PRD already keeps `blocked` out of route-list fields. | `PYTHONPATH=evals python3 evals/run_runtime.py --validate-schema --all-prompts` passed with 371 rows and no schema errors. | Runtime behavior for blocked prompts. |
| Evidence boundary references survive skill consolidation | `skills/_shared/EVIDENCE-BOUNDARY.md` is cited from affected public skills; `skills/verify/*BRANCH.md` files inherit relevant `EB-*` references after the split. | `python3 -m unittest evals.test_progressive_disclosure` passed. | Clean review or independent verification. |
| Non-executor boundary survives skill consolidation | `skills/_shared/NON-EXECUTOR-BOUNDARY.md` is cited from `dispatch`, `handoff`, `verify`, `wiki`, and relevant verify branch files. | `git diff --check` passed. | Actual thread, subagent, worktree, runtime, cache, release, UAT, or customer actions. |
| Coverage manifest is a quality gate | `evals/test_coverage_manifest.py` calls `validate_manifest()`; `.github/workflows/evals.yml` runs the test and compiles `evals/check_coverage_manifest.py`. | `python3 -m unittest evals.test_coverage_manifest` and `PYTHONPATH=evals python3 evals/check_coverage_manifest.py` passed. | Runtime coverage sufficiency. |
| zh-CN trigger parity governance is auditable without overclaiming full coverage | `skills/_shared/LOCALE-GUARD.md` requires auditable zh-CN parity coverage and says full per-skill parity must not be claimed without a manifest or checker. | `PYTHONPATH=evals python3 evals/run_runtime.py --validate-schema --suite zh-trigger-parity.csv` passed. | Full per-public-skill zh-CN parity coverage. |
| Existing eval source gates stay parseable | New and existing prompt CSV files parse under `csv.DictReader`; plugin metadata remains valid JSON. | `python3 -c "import csv, pathlib; [list(csv.DictReader(open(p, newline=''))) for p in pathlib.Path('evals/prompts').glob('*.csv')]; print('csv ok')"` and `python3 -m json.tool .codex-plugin/plugin.json >/dev/null` passed. | Installed plugin or marketplace validation. |

## Checks Run

```text
python3 -m py_compile evals/run_runtime.py evals/check_coverage_manifest.py evals/schema_validation.py evals/scoring.py evals/report.py evals/patch_suggestions.py
python3 -m unittest evals.test_schema_validation evals.test_scoring evals.test_checks evals.test_trace_diagnostics evals.test_report evals.test_patch_suggestions evals.test_coverage_manifest
PYTHONPATH=evals python3 -m unittest evals.test_run_runtime_scheduler
python3 -m unittest evals.test_progressive_disclosure
PYTHONPATH=evals python3 evals/check_coverage_manifest.py
PYTHONPATH=evals python3 evals/run_runtime.py --validate-schema --suite zh-trigger-parity.csv
PYTHONPATH=evals python3 evals/run_runtime.py --validate-schema --suite routing-reliability.csv
PYTHONPATH=evals python3 evals/run_runtime.py --validate-schema --all-prompts
python3 -c "import csv, pathlib; [list(csv.DictReader(open(p, newline=''))) for p in pathlib.Path('evals/prompts').glob('*.csv')]; print('csv ok')"
python3 -m json.tool .codex-plugin/plugin.json >/dev/null
git diff --check
```

## Evidence Boundaries

- Runtime Evidence: not refreshed and not claimed for this integrated branch.
- Installed Plugin Cache Evidence: not refreshed and not claimed.
- Clean Review Evidence: pending for this new integrated diff.
- Independent Verification Evidence: pending.
- Release / UAT / Customer Readiness: not claimed.
