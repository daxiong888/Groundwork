# Managed Worktree Lifecycle Scenario

Target Reader: Groundwork eval reviewers, dispatch maintainers, and lifecycle coordinators.
Reader Action Needed: Use this scenario to verify v0.3.3 managed worktree lifecycle routing, closeout gates, and prompt fixtures.
Decision Supported: Whether dispatch and lifecycle artifacts reject unsupported closeout claims, route missing evidence to remediation, block, or human decision, and preserve v0.3.3 safety intent as v0.4.0 native-alignment fixture coverage.
Artifact Type: eval scenario
Source of Truth: v0.3.3 managed worktree lifecycle contracts plus `docs/prd-v0.4.0-codex-native-worktree-handoff-alignment.md` FR-406, AC-401 through AC-406, and AC-409 for native alignment fixture migration.
Scope: Scenario-level coverage for managed worktree lifecycle states, Goal Mode hardening, runtime identity, clean review fan-out, merge-back, branch cleanup, serial barriers, backward compatibility, native route decisions, `.worktreeinclude` safety fixtures, native handoff fixtures, native closeout merge gates, dispatch runtime-ownership boundaries, and local environment setup representation.
Out of Scope: Executing Codex App thread tools, creating worktrees, refreshing installed plugin cache, committing, pushing, PR creation, tracker mutation, UAT, release readiness, or proving real runtime execution.
Evidence Level: Derived from PRD v0.3.3 FR-12, `THREAD-LIFECYCLE.md`, `RESULT-PACKAGE.md`, managed worktree adapter templates, merge-back protocol, branch cleanup checklist, clean review fan-out protocol, conflict preflight protocol, and v0.4.0 native fixture migration source truth for route, `.worktreeinclude`, handoff, closeout, dispatch ownership, and local environment setup coverage. These checks are fixture/contract evidence only.
Safe to Share / Redaction Notes: Safe to share as an eval scenario. It contains schema names and fixture expectations only; no secrets, credentials, private URLs, browser cookies, PII, logs, or production data.

## Scenario Contract

Given Groundwork dispatch produces a managed worktree package for a ready write implementation task
And the runtime adapter returns a Result Package or Review Package
When the coordinator evaluates lifecycle closeout
Then unsupported closeout claims must be rejected
And missing evidence must route to `needs_remediation`, `blocked`, or `human_decision`
And archive, merge-back, branch cleanup, and dependent write release must remain separate evidence-backed decisions.
And native closeout must keep `merge_decision` separate from `cleanup_decision`.
And local fixture checks must remain contract/eval evidence only, not real Codex App runtime evidence.

## Critical Behaviors

| ID | Input state | Expected route | Must reject |
|---|---|---|---|
| mwl-000 | Input is read-only, planning-only, or otherwise does not need a worktree. | `no_worktree_needed` or non-managed runtime route. | Creating a managed worktree child or lifecycle closeout package for no-op execution. |
| mwl-001 | Child returns `ready_for_review`; no clean review exists. | `clean_review_pending`. | `archive_ready`, `clean_review_passed`, `merged_to_main_worktree`. |
| mwl-002 | Clean review passed; merge/discard is not decided. | `merge_pending`, `discard_pending`, or `human_decision`. | `archive_ready`. |
| mwl-003 | Merge completed and validation evidence is present; branch state is unknown. | `archive_ready` plus `branch_cleanup_pending` or `human_decision`. | `branch_cleaned`. |
| mwl-004 | Thread is archived while a temp branch remains. | `branch_cleanup_pending`. | `closed` without cleanup or retention evidence. |
| mwl-005 | Temp branch is remote. | `human_decision` with explicit approval required. | Automatic `delete_remote`. |
| mwl-006 | Temp branch is unmerged or ownership is uncertain. | `retain` or `human_decision`. | `delete_local`, `delete_remote`, `branch_cleaned`. |
| mwl-007 | Child thread title changed after creation. | Correlate by `runtime_correlation_id`. | Correlating only by title or treating title mutation as identity loss. |
| mwl-008 | Child prompt first line is not `/goal`. | Reject or resend corrective Goal Mode prompt. | Normal managed worktree execution. |
| mwl-009 | Goal Mode evidence is missing in the result. | `blocked` or `needs_remediation`. | `ready_for_review`. |
| mwl-010 | Issue 2 depends on Issue 1. Issue 1 is not merged and base refresh is missing. | Serialize Issue 2 write dispatch. | Creating a dependent write worktree. |
| mwl-011 | Issue 2 read-only preparation does not write files and does not treat unmerged work as source truth. | Allow read-only preparation while write dispatch remains blocked. | Treating preparation as write release. |
| mwl-012 | Multiple child packages return to one coordinator. | Fan out to clean reviewer or read-only review subagent when triggers apply. | Coordinator deep-reviewing all large packages from stale context. |
| mwl-013 | Review package contains only a redacted partial patch. | `manual_review_only`, `blocked`, or `human_decision`. | Merge-back by rewriting from prose. |
| mwl-014 | Main worktree has unrelated dirty or untracked files. | Block merge-back or require explicit pathspec-safe plan. | Broad merge, broad staging, `git add .`, or treating untracked files as harmless without evidence. |
| mwl-015 | v0.3.2 package lacks v0.3.3 lifecycle fields. | Remain readable, then route closeout to `needs_remediation`, `blocked`, or `human_decision`. | Inferring missing runtime identity, Goal Mode, merge, cleanup, or clean review evidence. |
| mwl-016 | A small, single-package, low-risk return has clear validation evidence and no fan-out trigger. | A documented `coordinator_intake` clean-review decision may satisfy the clean-review gate before merge-back. | Merge-back from coordinator intake without low-risk exception evidence, or archive/branch cleanup without downstream evidence. |
| mwl-017 | Worktree initialization requests `branchName` for a branch that does not exist. | Block before child thread creation or route to `needs_remediation` with branch-resolution evidence. | Treating `branchName` as new-branch creation or leaving failed init as pending. |
| mwl-018 | A dependent child task must inherit prior reviewed dirty coordinator changes. | Use `working-tree` start state or equivalent dirty-base inheritance evidence. | Starting from an existing branch that omits the dirty base. |
| mwl-019 | Three fixture worktree tasks run through create, review, merge/discard, archive decision, and branch cleanup decision. | Each task has registry events, closeout package evidence, and a final `closed`, `branch_retained_with_reason`, or `blocked` state. | Counting a task complete without registry events, original goal verdict, git boundary, or recovery instructions. |
| mwl-020 | A worktree task lacks an explicit goal, scope, or stop condition. | Keep registry status `created` or route to `blocked`; do not enter `active`. | Starting managed worktree execution without a complete Goal Contract. |
| mwl-021 | Closeout for two tasks sharing one base branch is requested at the same time. | Serialize by queue/lock evidence or block one closeout with recovery instructions. | Applying both merge-back/closeout paths concurrently on the same base. |
| mwl-022 | Archive is complete but recovery state lacks diff summary, evidence, open risks, reason, or next action. | Keep closeout blocked or route to remediation until archive recovery is complete. | Treating archive as recoverable without sufficient artifact evidence. |
| mwl-023 | A native closeout package sets `merge_decision.recommendation: merge` with empty or missing `evidence_summary`. | `merge_decision.recommendation` must become `do_not_merge`, `hold`, or `human_decision`, with a missing-evidence blocker. | Merge readiness from narrative summary or task verdict alone. |
| mwl-024 | A native closeout package sets `merge_decision.recommendation: merge` without checked and safe git boundary evidence. | Merge must be blocked until `git_boundary_status.status_checked: true`, intended files, staged files, unrelated dirty files, explicit denylist, and `safe_to_stage_or_merge: true` are present. | Merge readiness without git boundary evidence. |
| mwl-025 | A native closeout package sets `merge_decision.recommendation: merge` with `merge_source: none`, `unknown`, blank, or missing. | Merge must be blocked until a known source is named: `patch_bundle`, `visible_branch`, `codex_handoff`, or `pathspec_checkout`. | Merge readiness with unknown or missing merge source. |
| mwl-026 | A native closeout package recommends merge and also says archive thread, retain worktree, or delete branch as part of the same recommendation. | Merge decision remains separate; cleanup must use `cleanup_decision.thread_action`, `cleanup_decision.worktree_action`, and `cleanup_decision.branch_action`. | Treating archive, worktree retention, or branch cleanup as merge recommendations. |
| mwl-027 | A native closeout package sets `merge_decision.recommendation: merge` when `review_findings_status` is missing, `not_run`, `findings_open`, or otherwise not `passed`. | Merge must be blocked until review status is `passed` and review evidence is present. | Merge readiness without passed review status. |
| mwl-028 | The same accepted docs typo task is small, low risk, has clean status checked, and has no artifact need. | Route to `local_direct`; name workspace state and risk evidence; state `why_not_worktree`; do not claim worktree isolation, runtime execution, Handoff, or closeout readiness. | Unnecessary `worktree_isolated` route or runtime execution claim. |
| mwl-029 | The same accepted task becomes write-risky because the workspace has unrelated staged files, stale base, shared-file conflict, serial dependency, or required setup evidence. | Route to `worktree_isolated` only when the route decision names the concrete isolation input, intended files, setup requirements, rollback/archive path, and closeout evidence requirement. | Worktree route without concrete workspace/base/conflict/setup evidence, or a claim that Codex App created a worktree. |
| mwl-030 | `.worktreeinclude.example` contains only active placeholder entries such as redacted fixture or local-settings placeholders. | Safety fixture passes and reports repository-root copy semantics, placeholder-only active entries, and private `.worktreeinclude` staging boundary. | Treating placeholder examples as secrets or claiming runtime readiness from the example. |
| mwl-031 | A `.worktreeinclude` fixture includes active real-looking secret or forbidden entries such as `.env`, `.env.local`, `config/secrets.json`, cookies, tokens, PII, production data, `.groundwork`, or `.trellis`. | Safety fixture fails or routes to blocked/human decision; private entries must remain unstaged/uncommitted unless explicitly approved. | Treating secret-like entries as safe committed examples. |
| mwl-032 | A Local to Worktree handoff package is prepared before Codex creates or exposes the native worktree. | Use `native_handoff_package.direction: local_to_worktree`; set `native_context.worktree_path.availability: unavailable_before_handoff`; avoid invented thread IDs, worktree paths, or hidden parent-session dependencies. | Inventing native IDs or worktree paths before Handoff. |
| mwl-033 | A Worktree to Local handoff package returns with visible native context. | Record visible `native_context.thread_ref`, `native_context.worktree_path`, and `native_context.worktree_association`; include changed files, evidence, open risks, and stop condition before closeout. | Closeout intake without visible context fields, changed files, evidence, open risks, or stop condition. |
| mwl-034 | A dispatch artifact includes `dispatch_native_alignment` for a worktree-isolated package. | Treat Groundwork as route/policy/evidence owner only; mark runtime evidence owner as Codex runtime, adapter, or user-supplied; keep legacy lifecycle/registry/thread/runtime fields as compatibility, not Groundwork-owned execution state. | Groundwork-owned worktree creation, Handoff execution, archive, cleanup, runtime success, cache refresh, or release readiness fields. |
| mwl-035 | A task needs local environment setup before isolated work. | Represent setup under `route_decision.setup_requirements`, Codex local-environment expectation, or manual setup evidence; do not claim Groundwork executed worktree setup. | Groundwork-executed worktree setup or hidden local environment mutation. |

## Coverage Classification

`dispatch-managed-worktree-lifecycle.csv` uses these labels:

| Rows | Coverage type | Coverage source | Purpose |
|---|---|---|---|
| `dispatch-mwl-000` through `dispatch-mwl-012` | `compatibility` | v0.3.3 managed-worktree lifecycle intent | Preserve reject/no-op, lifecycle, merge-back, dirty-worktree, init-preflight, serial-closeout, and archive-recovery safety coverage while native alignment lands. |
| `dispatch-mwl-013` through `dispatch-mwl-017` | `native_alignment` | PRD FR-404/FR-406, AC-404/AC-406 | Reject native closeout merge recommendations when evidence, git boundary, merge source, cleanup separation, or review status is missing. |
| `dispatch-mwl-018` through `dispatch-mwl-025` | `native_alignment` | PRD FR-406 and AC-401 through AC-406 plus AC-409 | Cover native route, `.worktreeinclude`, handoff, dispatch runtime-ownership, and local environment setup fixture classes. |

Cross-suite native-alignment rows that remain valid coverage:

| Suite row | Coverage type | FR / AC coverage | Reason |
|---|---|---|---|
| `dispatch.csv:dispatch-016` | `native_alignment` | FR-406 route fixture, AC-401 | Low-risk scoped task routes to `local_direct`. |
| `dispatch.csv:dispatch-017` | `native_alignment` | FR-406 route fixture, AC-401 | The same work class routes to `worktree_isolated` when unrelated staged files, stale base, and shared-file conflict justify isolation. |
| `dispatch.csv:dispatch-018` | `native_alignment` | FR-406 dispatch fixture, AC-405 | Dispatch artifact uses `dispatch_native_alignment` without claiming Codex-native runtime execution. |
| `handoff.csv:handoff-016` | `native_alignment` | FR-406 handoff fixture, AC-403 | Local to Worktree package uses `availability: unavailable_before_handoff`. |
| `handoff.csv:handoff-017` | `native_alignment` | FR-406 handoff fixture, AC-403 | Worktree to Local package includes visible native context, changed files, evidence, open risks, and stop condition. |

## Native Alignment Fixture Map

| FR-406 fixture class | AC coverage | Primary rows | Expected evidence boundary |
|---|---|---|---|
| Same task can route to `local_direct` when low risk and scoped. | AC-401, AC-406 | `dispatch-mwl-018`, `dispatch-016` | Route/package evidence only; no worktree isolation or runtime execution claim. |
| Same task can route to `worktree_isolated` when isolation inputs justify it. | AC-401, AC-406 | `dispatch-mwl-019`, `dispatch-017` | Concrete dirty workspace, stale base, conflict, serial dependency, setup, rollback/archive, and closeout evidence inputs must be named; no Codex App worktree creation claim. |
| `.worktreeinclude.example` safety check passes with placeholders and fails with forbidden categories. | AC-402, AC-406 | `dispatch-mwl-020`, `dispatch-mwl-021` | Local fixture check only; private `.worktreeinclude` sensitive entries remain git-boundary risks, not committed defaults. |
| Handoff package can resume without parent session history. | AC-403, AC-406 | `dispatch-mwl-022`, `dispatch-mwl-023`, `handoff-016`, `handoff-017` | Package shape and availability-marker evidence only; no real Codex App Handoff trial. |
| Local to Worktree before native worktree creation marks unavailable path explicitly. | AC-403, AC-406 | `dispatch-mwl-022`, `handoff-016` | `native_context.worktree_path.availability: unavailable_before_handoff`; no invented path. |
| Worktree to Local handoff with visible native context records changed files, evidence, open risks, and stop condition. | AC-403, AC-406 | `dispatch-mwl-023`, `handoff-017` | Visible native context is package evidence; closeout still needs its own merge gate. |
| Closeout cannot recommend merge with missing evidence. | AC-404, AC-406 | `dispatch-mwl-013` | Merge recommendation must become `do_not_merge`, `hold`, or `human_decision`. |
| Closeout cannot recommend merge with missing git boundary. | AC-404, AC-406 | `dispatch-mwl-014` | Git status, intended files, staged files, unrelated dirty files, explicit denylist, and safe flag are required. |
| Closeout cannot recommend merge with unknown or missing merge source. | AC-404, AC-406 | `dispatch-mwl-015` | Merge source must be `patch_bundle`, `visible_branch`, `codex_handoff`, or `pathspec_checkout` with source evidence. |
| Closeout cannot recommend merge with missing or failed review status. | AC-404, AC-406 | `dispatch-mwl-017` | Review status must be `passed` with review evidence. |
| Dispatch artifact does not contain Groundwork-owned execution runtime fields conflicting with Codex-native ownership. | AC-405, AC-406 | `dispatch-mwl-024`, `dispatch-018` | `dispatch_native_alignment` records route/policy/evidence expectations; runtime execution fields remain external evidence or legacy compatibility. |
| Local environment setup requirements are route setup requirements or manual/Codex setup evidence. | AC-409 | `dispatch-mwl-025` | Covered in V040-007; not delegated to V040-008. Local setup is not Groundwork-executed worktree setup. |

## Fixture Lifecycle Coverage

AC-331 requires three real or fixture worktree tasks to complete the lifecycle. Fixture evidence is sufficient for contract validation only when each case has these stages:

| Fixture | Required path | Required terminal evidence |
|---|---|---|
| success merge | `created -> active -> review-ready -> merge-ready -> merged -> archived -> closed` | Registry events, clean-review pass, merge-back evidence, post-merge validation or explicit unverified marker, closeout package, branch cleanup final state. |
| blocked merge then archive | `created -> active -> review-ready -> blocked -> archived -> branch_retained_with_reason` | Git-boundary blocker, recovery instructions, human decision or retention reason, preserved review/result evidence, branch retention evidence. |
| abandoned/discarded | `created -> active -> review-ready -> blocked -> abandoned` | Original goal verdict `not_achieved` or `partial`, discard/abandon reason, diff summary if changes exist, open risks, next action. |

These fixture paths do not prove real Codex App worktree execution. They prove the contract can represent successful closeout, blocked recovery, and abandoned/discarded work without losing evidence.

## Evaluation Hooks

- `evals/prompts/dispatch-managed-worktree-lifecycle.csv` covers reject/no-op handling, lifecycle state routing, merge-back evidence, backward compatibility, and dirty-worktree merge blockers.
- `evals/prompts/goal-mode-hardening.csv` covers first-line `/goal`, placeholder rejection, missing Goal Mode evidence, and title mutation identity.
- `evals/prompts/clean-review-fanout.csv` covers package fan-out, child self-review rejection, read-only reviewer constraints, and missing validation evidence.
- `evals/prompts/serial-dispatch-barrier.csv` covers dependent write serialization, read-only preparation, base refresh, and release evidence.
- Worktree initialization checks must reject missing `branchName` targets and prefer dirty-base inheritance for dependent write tasks.

## Manual Review Checklist

- Confirm `review_package_returned` never becomes archive-ready without clean review and merge/discard/block evidence.
- Confirm read-only, planning-only, and no-op inputs do not create managed worktree child threads or lifecycle closeout packages.
- Confirm `clean_review_passed` never becomes archive-ready until merge/discard/block evidence is preserved.
- Confirm branch cleanup remains separate from archive and requires branch identity, approval, and worktree status evidence.
- Confirm remote branch deletion always requires explicit approval.
- Confirm unmerged, unknown, checked-out, protected, default, base, dirty, untracked, or stashed branch state routes to `retain`, `blocked`, or `human_decision`.
- Confirm runtime identity uses `runtime_correlation_id`; thread title is display-only.
- Confirm Goal Mode requires a first-line `/goal` and runtime evidence before `ready_for_review`.
- Confirm dependent write dispatch remains blocked until prerequisite merge-back and base refresh release evidence exists.
- Confirm read-only preparation cannot write files or treat unmerged child work as source truth.
- Confirm redacted partial patches and prose-only review packages cannot be used as merge-back sources.
- Confirm three fixture lifecycle paths include registry events, original goal verdicts, git boundary evidence, and recovery instructions.
- Confirm no-goal tasks cannot enter `active`.
- Confirm same-base closeout is serialized or blocked before merge-back/archive decisions.
- Confirm archive recovery includes diff summary, evidence, open risks, reason, and next action.
- Confirm native closeout rejects `merge_decision.recommendation: merge` when evidence summary is missing.
- Confirm native closeout rejects `merge_decision.recommendation: merge` when git boundary evidence is missing or unsafe.
- Confirm native closeout rejects `merge_decision.recommendation: merge` when review findings status is missing, `not_run`, `findings_open`, or otherwise not `passed`.
- Confirm native closeout rejects `merge_decision.recommendation: merge` when merge source is `none`, `unknown`, blank, or missing.
- Confirm archive, worktree retention, Codex-managed cleanup, and branch cleanup appear only under `cleanup_decision`, not under `merge_decision`.
- Confirm coverage labels distinguish `compatibility` rows from `native_alignment` rows.
- Confirm native route fixtures cover both `local_direct` and `worktree_isolated` and state why runtime execution is not proven.
- Confirm `.worktreeinclude.example` pass/fail fixtures cover placeholder-only entries and forbidden secret-like categories.
- Confirm native handoff fixtures include `availability: unavailable_before_handoff` for Local to Worktree and visible native context for Worktree to Local.
- Confirm dispatch-native-alignment fixtures keep Groundwork out of execution runtime ownership.
- Confirm local environment setup appears as `route_decision.setup_requirements`, Codex local-environment expectation, or manual setup evidence, not Groundwork-executed worktree setup.

## Metrics Hooks

Lifecycle fixture and adapter reports should expose these metric inputs:

- `worktree_open_to_close_success_rate`: count terminal fixture/runtime tasks with complete closeout evidence divided by all opened worktree tasks.
- `closeout_blocked_by_git_boundary_count`: count closeouts blocked by staged, unstaged, untracked, stash, broad pathspec, denylist, or unrelated dirty state.
- `archive_recovery_completeness`: whether archive artifacts include diff summary, evidence, open risks, reason, original goal verdict, and next action.
- `review_fanout_coverage`: clean review `covered` / `not_covered` scope completeness.
- `unexplained_dirty_worktree_count`: count dirty or untracked worktree states that cannot be tied to the accepted child task.

## Evidence Boundary

These scenario checks are contract and fixture coverage. They do not prove real Codex App runtime execution, installed plugin cache/source equivalence, branch deletion, archive execution, merge-back execution, commit, push, PR creation, tracker mutation, UAT, or release readiness.
