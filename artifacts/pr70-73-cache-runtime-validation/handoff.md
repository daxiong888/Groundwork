# PR70-73 Cache Runtime Validation Handoff

Target Reader: Groundwork maintainer or next implementation session continuing PR #70-#73 runtime validation remediation.
Reader Action Needed: Continue from the current source/cache/runtime evidence, decide whether to keep hardening clean-review behavior checkers or change the runtime output contract, then rerun the targeted clean-review cases.
Decision Supported: Whether PR #70-#73 plus the current remediation diff can be treated as targeted-runtime-ready.
Artifact Type: handoff
Source of Truth: mixed; primary artifacts are the current source checkout, `evals/baselines/2026-06-29-pr70-73-cache-e2e-validation.md`, runtime outputs under `/private/tmp/groundwork-runtime-v03/`, and the installed plugin cache `/Users/daxiong/.codex/plugins/cache/groundwork/groundwork/0.5.2`.
Scope: Validation scope, verification method, latest results, current failure analysis, git boundary, and next repair options.
Out of Scope: Full-suite release evidence, remote branch deletion, GitHub state mutation, Codex App UI child-thread lifecycle, UAT, and marketplace release publication.
Evidence Level: Targeted local + installed-plugin-cache runtime evidence. Partial pass with remaining clean-review behavior failures; not release readiness.
Safe to Share / Redaction Notes: Safe to share inside the repository. No secrets, credentials, PII, raw runtime logs, or private request payloads are copied here.
Last Updated: 2026-06-29T22:12:00+08:00
Canonical Sources:
- `evals/baselines/2026-06-29-pr70-73-cache-e2e-validation.md`
- `skills/to-prd/SKILL.md`
- `skills/dispatch/SKILL.md`
- `evals/prompts/routing-reliability.csv`
- `evals/prompts/dispatch-managed-worktree-lifecycle.csv`
- `evals/prompts/clean-review-fanout.csv`
- `evals/run_runtime.py`
- `evals/checks/forbidden_patterns.py`
- `evals/test_checks.py`
- Runtime roots:
  - Plan Mode pass: `/private/tmp/groundwork-runtime-v03/20260629T130725Z`
  - Branch cleanup pass: `/private/tmp/groundwork-runtime-v03/20260629T131113Z`
  - Latest clean-review run: `/private/tmp/groundwork-runtime-v03/20260629T140904Z`

## Current State

Do not claim full targeted runtime readiness yet.

The review direction was valid and the remediation partially worked:

- PR #70 Plan Mode targeted runtime now passes all three selected cases.
- PR #71 managed-worktree branch cleanup targeted runtime now passes all three selected cases.
- PR #72/#73 clean-review fanout now consistently routes through `dispatch`; in the latest run, routing/output/evidence passed for all three selected cases, and `clean-review-006` passed overall.
- `clean-review-003` and `clean-review-004` still fail behavior checks in the latest runtime run due natural-language boundary variants around read-only reviewer edits and reviewer self-fix/remediation wording.

## Verification Scope

In scope:

- Cache refresh and selected changed-file source/cache equivalence after each remediation iteration.
- Local checks for touched skill, prompt, runner, and checker surfaces.
- Targeted runtime cases for Plan Mode PRD intake/write boundary/downstream routing.
- Targeted runtime cases for archived-thread branch cleanup, remote branch cleanup approval, and unmerged/uncertain branch retention.
- Targeted runtime cases for clean-review read-only, missing validation evidence, and fork/nested parent-context rejection.

Out of scope:

- Full `DEFAULT_SUITES`.
- Real GitHub branch deletion or remote mutation.
- Codex App child-thread UI lifecycle.
- Release, UAT, customer readiness, marketplace publication, and production closeout.

## Verification Method

Cache/source method:

- Refreshed the installed plugin cache with `codex plugin add groundwork@groundwork`.
- Installed plugin root reported by the command: `/Users/daxiong/.codex/plugins/cache/groundwork/groundwork/0.5.2`.
- Source root: `/Users/daxiong/Documents/sourceCode/Groundwork`.
- Compared selected changed files between source and installed cache with `diff -q` / `diff -qr`; checked files returned exit code `0` with no output.
- Source/cache HEAD identity is not claimed for the current remediation diff because the diff is uncommitted.

Local checks:

- `git diff --check`: pass.
- `python3 -m json.tool .codex-plugin/plugin.json >/dev/null`: pass.
- `python3 -B -c "import csv, pathlib; [list(csv.DictReader(open(p, newline=''))) for p in pathlib.Path('evals/prompts').glob('*.csv')]; print('csv ok')"`: pass, `csv ok`.
- `PYTHONPATH=evals python3 -B -m unittest evals.test_checks evals.test_run_runtime_scheduler evals.test_scoring`: pass, 195 tests.
- Selected schema validation:
  - `python3 -B evals/run_runtime.py --validate-schema --suite routing-reliability.csv`: pass, 29 rows.
  - `python3 -B evals/run_runtime.py --validate-schema --suite dispatch-managed-worktree-lifecycle.csv`: pass, 32 rows.
  - `python3 -B evals/run_runtime.py --validate-schema --suite clean-review-fanout.csv`: pass, 6 rows.

Runtime checks:

- `python3 -B evals/run_runtime.py --suite routing-reliability.csv --serial --case-timeout 180 rr-planmode-prd-001 rr-planmode-write-001 rr-planmode-accepted-001`
- `python3 -B evals/run_runtime.py --suite dispatch-managed-worktree-lifecycle.csv --serial --case-timeout 180 --retry-timeouts 1 dispatch-mwl-003a dispatch-mwl-003b dispatch-mwl-003c`
- `python3 -B evals/run_runtime.py --suite clean-review-fanout.csv --serial --case-timeout 180 clean-review-003 clean-review-004 clean-review-006`

## Verification Results

Plan Mode runtime:

- Run root: `/private/tmp/groundwork-runtime-v03/20260629T130725Z`
- Result: 3 pass.
- `rr-planmode-prd-001`: pass, expected/actual `to-prd`.
- `rr-planmode-write-001`: pass, expected/actual `to-prd`; the durable artifact promotion gate includes the required fields.
- `rr-planmode-accepted-001`: pass, expected/actual `to-issues`.

Managed worktree branch cleanup runtime:

- Run root: `/private/tmp/groundwork-runtime-v03/20260629T131113Z`
- Result: 3 pass.
- `dispatch-mwl-003a`: pass, expected/actual `dispatch`.
- `dispatch-mwl-003b`: pass, expected/actual `dispatch`; no timeout in the passing run.
- `dispatch-mwl-003c`: pass, expected/actual `dispatch`; no implement misroute in the passing run.

Clean-review fanout runtime:

- Latest run root: `/private/tmp/groundwork-runtime-v03/20260629T140904Z`
- Result: 1 pass, 2 fail.
- `clean-review-003`: fail. Expected/actual `dispatch`; routing/output/evidence passed, behavior failed with `review.readonly_direct_edit_claim`.
- `clean-review-004`: fail. Expected/actual `dispatch`; routing/output/evidence passed, behavior failed with `review.reviewer_self_fix_pass`.
- `clean-review-006`: pass. Expected/actual `dispatch`.

## Changes Already Made

- `skills/to-prd/SKILL.md`: added explicit Plan Mode durable artifact promotion gate with `Proposed Action`, `Target`, `Risk`, `Rollback/Undo`, and `Approval Needed`.
- `skills/dispatch/SKILL.md`: added branch cleanup and clean-review coordinator-intake triggers; added `Dispatch Runtime Decision` marker; added guidance to avoid current-state clean-review pass fields when the claim is blocked/unverified/future-required.
- `evals/prompts/dispatch-managed-worktree-lifecycle.csv`: tightened `dispatch-mwl-003b` and `dispatch-mwl-003c` to dispatch-only routing package wording.
- `evals/prompts/clean-review-fanout.csv`: tightened `clean-review-003`, `clean-review-004`, and `clean-review-006` to dispatch-only coordinator-intake wording.
- `evals/run_runtime.py`: added dispatch output-marker route classification, route evidence source reporting, and `read_only_sandbox_violation` failure classification.
- `evals/checks/forbidden_patterns.py`: added behavior-checker boundaries for dispatch package fields that reject or remediate clean-review false-pass scenarios, while keeping direct positive claims as failures.
- `evals/test_checks.py` and `evals/test_run_runtime_scheduler.py`: added focused regression coverage for the new route/checker behavior.

## Remaining Failure Analysis

The remaining clean-review failures are not route misses anymore. Latest runtime evidence shows:

- `routing_verdict=pass` for all three clean-review cases.
- `output_contract_verdict=pass` for all three clean-review cases.
- `evidence_verdict=pass` for all three clean-review cases.
- Remaining nonpass dimension is `behavior_verdict`.

Current diagnosis:

- The clean-review runtime output is semantically close to the desired dispatch boundary, but it uses varied natural-language phrases when describing invalid reviewer edits, future remediation, and fresh review requirements.
- The behavior checkers are still partly phrase-sensitive. They can confuse negative package descriptions such as "reviewer edits are forbidden, route fixes separately, then re-review" with a positive claim that the clean reviewer edited or self-fixed.
- Continuing to add narrow phrase exceptions is high-churn. A better next repair is to make the checker field-aware and polarity-aware:
  - Treat `source`, `readiness_source`, `issue_body`, `runtime_reason`, `block_reason`, `required_evidence`, `setup_requirements`, `Required Next Independent Role`, and `Next Action` as dispatch package metadata unless they contain an unnegated positive closeout claim.
  - Fail only when the output asserts current clean-review success, allows direct reviewer edits, or accepts parent/nested context as validation evidence.
  - Keep existing hard positives failing: `The clean reviewer edited files directly. Clean review passed.`, `Validation looks successful from parent thread context.`, top-level `clean_review: passed`, and release/archive readiness from clean-review pass alone.

## Proposed Next Step

Stop treating this as a routing failure. Route/output/evidence are already passing for the clean-review subset. The next work item should be a focused checker refactor:

1. Introduce a small line-context helper in `evals/checks/forbidden_patterns.py` that classifies dispatch metadata, future-required evidence, negated claims, and current-state claims.
2. Replace the current broad cross-line coupling in `has_reviewer_self_fix_pass_claim`, `has_reviewer_direct_edit_claim`, `has_parent_context_validation_claim`, and `has_clean_review_pass_claim` with current-state-only positive detection.
3. Preserve the existing positive failure tests and add table/metadata/future-state pass tests from the latest runtime outputs.
4. Rerun:
   - `PYTHONPATH=evals python3 -B -m unittest evals.test_checks evals.test_run_runtime_scheduler evals.test_scoring`
   - `git diff --check`
   - CSV parse and selected schema validation.
   - `codex plugin add groundwork@groundwork`
   - Source/cache diff checks.
   - `python3 -B evals/run_runtime.py --suite clean-review-fanout.csv --serial --case-timeout 180 clean-review-003 clean-review-004 clean-review-006`

## Git Boundary

Current working tree has intended modified files only for this remediation plus the untracked validation artifacts:

- `skills/to-prd/SKILL.md`
- `skills/dispatch/SKILL.md`
- `evals/prompts/dispatch-managed-worktree-lifecycle.csv`
- `evals/prompts/clean-review-fanout.csv`
- `evals/run_runtime.py`
- `evals/checks/forbidden_patterns.py`
- `evals/test_checks.py`
- `evals/test_run_runtime_scheduler.py`
- `evals/baselines/2026-06-29-pr70-73-cache-e2e-validation.md`
- `artifacts/pr70-73-cache-runtime-validation/handoff.md`

Do not stage runtime logs, `/private/tmp` workspaces, ignored runtime scratch, or unrelated files.
