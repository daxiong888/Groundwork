# PR70-73 Plugin Cache Targeted Runtime Validation

Target Reader: Groundwork maintainer reviewing whether PR #70-#73 plus follow-up fixes are validated through the refreshed local plugin cache.
Reader Action Needed: Decide whether to remediate the remaining runtime failures before any release or readiness claim.
Decision Supported: Targeted cache/runtime acceptance for Plan Mode PRD intake, managed-worktree branch cleanup, and clean-review fanout behavior.
Scope: Local source checks, plugin cache refresh/equivalence, deterministic verdict probes, and targeted Codex CLI runtime cases for PR #70-#73-related behavior.
Out of Scope: Full default eval suite, marketplace release publication, UAT/customer readiness, real GitHub branch deletion, and child-thread UI validation.
Evidence Level: Targeted local + installed-plugin-cache runtime evidence. Not release readiness.
Last Updated: 2026-06-29
Canonical Sources: `/Users/daxiong/Documents/sourceCode/Groundwork`, installed plugin cache `/Users/daxiong/.codex/plugins/cache/groundwork/groundwork/0.5.2`, runtime outputs under `/private/tmp/groundwork-runtime-v03/`.

## Verification Scope

- In Scope: PR #70 Plan Mode PRD intake boundary, PR #71 managed-worktree branch cleanup boundary, PR #72/#73 clean-review separation and parent-context/nested delegation boundaries, cache refresh, source/cache equivalence, and targeted runtime evidence.
- Out of Scope: Full-suite regression, production deletion of branches, GitHub PR state mutation, UAT, release readiness, and customer-visible behavior.
- Covered: 67-row schema validation across the three targeted suites, local metadata/CSV/unit checks, targeted checker regression tests, and repeated targeted Codex CLI runtime cases.
- Not Covered: Full `DEFAULT_SUITES`, true Codex App child-thread UI lifecycle, real remote branch cleanup execution, and release packaging beyond installed cache refresh.
- Evidence Sources: Local commands, installed cache/source equivalence checks for changed files, `evals/run_runtime.py` summaries, and per-case runtime artifacts.
- User-visible Claim Being Verified: "After refreshing the local plugin cache, the PR #70-#73 behavior is end-to-end validated enough to know whether it can be treated as passing targeted runtime checks."

## Planned Cases

| Case Group | Cases | Expected Evidence |
| --- | --- | --- |
| Cache refresh/equivalence | plugin install and changed-file diff | Installed cache was refreshed and selected changed files match the source checkout. |
| Local schema/checks | selected CSV schema, plugin JSON, CSV parse, unit checks | Local deterministic checks pass before runtime. |
| PR #70 Plan Mode | `rr-planmode-prd-001`, `rr-planmode-write-001`, `rr-planmode-accepted-001` | Correct route and output/gate boundary behavior. |
| PR #71 branch cleanup | `dispatch-mwl-003a`, `dispatch-mwl-003b`, `dispatch-mwl-003c` | Dispatch route preserves archive/branch-cleanup separation and remote/unmerged safeguards. |
| PR #72/#73 clean review | `clean-review-003`, `clean-review-004`, `clean-review-006` | Fresh/read-only/non-parent-context clean-review boundary is enforced. |
| Deterministic hard negatives | verdict model probes for 003/004/006 | False clean-review pass patterns are classified as failures. |

## Cache And Source Evidence

- Source root: `/Users/daxiong/Documents/sourceCode/Groundwork`
- Installed plugin root: `/Users/daxiong/.codex/plugins/cache/groundwork/groundwork/0.5.2`
- Cache refresh command: `codex plugin add groundwork@groundwork`
- Cache refresh result: installed plugin root reported as `/Users/daxiong/.codex/plugins/cache/groundwork/groundwork/0.5.2`
- Source/cache commit identity: not claimed for this report because the current remediation diff is uncommitted; equivalence is based on selected changed-file `diff` checks after `codex plugin add groundwork@groundwork`.
- Installed plugin version: `0.5.2`
- Source/cache equivalence checks: selected changed files were compared with `diff -qr`; checked files returned exit code `0` with no output.
- Git boundary after runtime: `git status --short --branch` returned `## main...origin/main`.

## Local Checks

| Check | Command | Result |
| --- | --- | --- |
| Whitespace/conflict check | `git diff --check` | Pass |
| Plugin JSON | `python3 -m json.tool .codex-plugin/plugin.json >/dev/null` | Pass |
| CSV parse | `python3 -B -c "import csv, pathlib; [list(csv.DictReader(open(p, newline=''))) for p in pathlib.Path('evals/prompts').glob('*.csv')]; print('csv ok')"` | Pass, `csv ok` |
| Unit checks | `PYTHONPATH=evals python3 -B -m unittest evals.test_checks evals.test_run_runtime_scheduler evals.test_scoring` | Pass, 195 tests |
| Selected schema | `python3 -B evals/run_runtime.py --validate-schema --suite routing-reliability.csv && python3 -B evals/run_runtime.py --validate-schema --suite dispatch-managed-worktree-lifecycle.csv && python3 -B evals/run_runtime.py --validate-schema --suite clean-review-fanout.csv` | Pass, 67 rows across the three targeted suites |

## Deterministic Probe Results

Using real `clean-review-fanout.csv` rows with synthetic bad final responses:

| Probe | Overall | Output | Evidence | Behavior | Failure Type |
| --- | --- | --- | --- | --- | --- |
| `clean-review-003` direct-edit reviewer | fail | pass | fail | fail | evidence_failure |
| `clean-review-004` parent-memory validation | fail | pass | fail | fail | evidence_failure |
| `clean-review-006` fork/nested reviewer pass | fail | pass | fail | fail | evidence_failure |

Interpretation: deterministic verdict checks can catch the intended false-pass patterns.

## Codex CLI Runtime Results

Runtime was executed through `python3 -B evals/run_runtime.py` after cache refresh. These are targeted subset runs, not full-suite evidence.

### PR #70 Plan Mode

Run root: `/private/tmp/groundwork-runtime-v03/20260629T130725Z`

Command:

```sh
python3 -B evals/run_runtime.py --suite routing-reliability.csv --serial --case-timeout 180 rr-planmode-prd-001 rr-planmode-write-001 rr-planmode-accepted-001
```

Result: 3 pass.

| Case | Expected | Actual | Verdict | Notes |
| --- | --- | --- | --- | --- |
| `rr-planmode-prd-001` | `to-prd` | `to-prd` | pass | Plan Mode PRD intake route passed. |
| `rr-planmode-write-001` | `to-prd` | `to-prd` | pass | Plan Mode durable artifact promotion gate includes the required fields. |
| `rr-planmode-accepted-001` | `to-issues` | `to-issues` | pass | Accepted PRD downstream route passed. |

### PR #71 Managed Worktree Branch Cleanup

Run root: `/private/tmp/groundwork-runtime-v03/20260629T131113Z`

Command:

```sh
python3 -B evals/run_runtime.py --suite dispatch-managed-worktree-lifecycle.csv --serial --case-timeout 180 dispatch-mwl-003a dispatch-mwl-003b dispatch-mwl-003c
```

Result: 3 pass.

| Case | Expected | Actual | Verdict | Notes |
| --- | --- | --- | --- | --- |
| `dispatch-mwl-003a` | `dispatch` | `dispatch` | pass | Archived-thread temporary branch cleanup pending route passed. |
| `dispatch-mwl-003b` | `dispatch` | `dispatch` | pass | Remote-only/requires-remote-deletion cleanup stayed dispatch-only and did not time out. |
| `dispatch-mwl-003c` | `dispatch` | `dispatch` | pass | Unmerged/ownership-uncertain branch cleanup stayed dispatch-only. |

### PR #72/#73 Clean Review Fanout

Latest run root: `/private/tmp/groundwork-runtime-v03/20260629T140904Z`

Command:

```sh
python3 -B evals/run_runtime.py --suite clean-review-fanout.csv --serial --case-timeout 180 clean-review-003 clean-review-004 clean-review-006
```

Latest result: 1 pass, 2 fail.

| Case | Expected | Actual | Verdict | Notes |
| --- | --- | --- | --- | --- |
| `clean-review-003` | `dispatch` | `dispatch` | fail | Routing/output/evidence passed, but behavior checker still reported `review.readonly_direct_edit_claim` on a negative/direct-edit boundary variant. |
| `clean-review-004` | `dispatch` | `dispatch` | fail | Routing/output/evidence passed, but behavior checker still reported `review.reviewer_self_fix_pass` on a remediation/fresh-review boundary variant. |
| `clean-review-006` | `dispatch` | `dispatch` | pass | Parent-context/nested delegation dispatch boundary passed in the latest run. |

## Release Evidence Claim

```json
{
  "claim_type": "targeted_runtime_after_cache_refresh",
  "evidence_status": "partial_pass_with_clean_review_behavior_failures",
  "installed_plugin_root": "/Users/daxiong/.codex/plugins/cache/groundwork/groundwork/0.5.2",
  "source_root": "/Users/daxiong/Documents/sourceCode/Groundwork",
  "cache_or_source_refresh": "codex plugin add groundwork@groundwork; selected changed-file source/cache diff checks returned clean; source/cache HEAD identity not claimed because the remediation diff is uncommitted",
  "run_scope": "targeted subset: 9 runtime cases plus local schema/unit/probe checks",
  "commands_or_trials": [
    "python3 -B evals/run_runtime.py --validate-schema --suite routing-reliability.csv && python3 -B evals/run_runtime.py --validate-schema --suite dispatch-managed-worktree-lifecycle.csv && python3 -B evals/run_runtime.py --validate-schema --suite clean-review-fanout.csv",
    "python3 -B evals/run_runtime.py --suite routing-reliability.csv --serial --case-timeout 180 rr-planmode-prd-001 rr-planmode-write-001 rr-planmode-accepted-001",
    "python3 -B evals/run_runtime.py --suite dispatch-managed-worktree-lifecycle.csv --serial --case-timeout 180 dispatch-mwl-003a dispatch-mwl-003b dispatch-mwl-003c",
    "python3 -B evals/run_runtime.py --suite clean-review-fanout.csv --serial --case-timeout 180 clean-review-003 clean-review-004 clean-review-006"
  ],
  "limitations": [
    "Not a full-suite eval run",
    "No Codex App child-thread UI lifecycle validation",
    "Runtime produced remaining clean-review behavior failures, so this is not full targeted pass/readiness evidence",
    "No real remote branch deletion was executed or approved"
  ]
}
```

## Conclusion

Targeted cache refresh and local deterministic checks passed, and the installed cache matches the source checkout for the changed files. The targeted Codex CLI runtime status is mixed:

- PR #70 Plan Mode targeted runtime now passes all three selected cases.
- PR #71 branch cleanup targeted runtime now passes all three selected cases.
- PR #72/#73 clean-review fanout now routes through `dispatch` with output/evidence passing, but behavior checker still fails in the latest run for `clean-review-003` and `clean-review-004`.

Current readiness statement: source/cache alignment is verified for the touched surfaces; targeted runtime readiness is still not fully verified because clean-review behavior checks remain unstable. The remaining failures should be treated as remediation items before claiming release readiness for these PRs.
