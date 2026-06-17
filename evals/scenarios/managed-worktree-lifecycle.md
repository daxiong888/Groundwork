# Managed Worktree Lifecycle Scenario

Target Reader: Groundwork eval reviewers, dispatch maintainers, and lifecycle coordinators.
Reader Action Needed: Use this scenario to verify v0.3.3 managed worktree lifecycle routing, closeout gates, and prompt fixtures.
Decision Supported: Whether dispatch and lifecycle artifacts reject unsupported closeout claims and route missing evidence to remediation, block, or human decision.
Scope: Scenario-level coverage for managed worktree lifecycle states, Goal Mode hardening, runtime identity, clean review fan-out, merge-back, branch cleanup, serial barriers, and backward compatibility.
Out of Scope: Executing Codex App thread tools, creating worktrees, refreshing installed plugin cache, committing, pushing, PR creation, tracker mutation, UAT, release readiness, or proving real runtime execution.
Evidence Level: Derived from PRD v0.3.3 FR-12, `THREAD-LIFECYCLE.md`, `RESULT-PACKAGE.md`, managed worktree adapter templates, merge-back protocol, branch cleanup checklist, clean review fan-out protocol, and conflict preflight protocol.

## Scenario Contract

Given Groundwork dispatch produces a managed worktree package for a ready write implementation task
And the runtime adapter returns a Result Package or Review Package
When the coordinator evaluates lifecycle closeout
Then unsupported closeout claims must be rejected
And missing evidence must route to `needs_remediation`, `blocked`, or `human_decision`
And archive, merge-back, branch cleanup, and dependent write release must remain separate evidence-backed decisions.

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

## Metrics Hooks

Lifecycle fixture and adapter reports should expose these metric inputs:

- `worktree_open_to_close_success_rate`: count terminal fixture/runtime tasks with complete closeout evidence divided by all opened worktree tasks.
- `closeout_blocked_by_git_boundary_count`: count closeouts blocked by staged, unstaged, untracked, stash, broad pathspec, denylist, or unrelated dirty state.
- `archive_recovery_completeness`: whether archive artifacts include diff summary, evidence, open risks, reason, original goal verdict, and next action.
- `review_fanout_coverage`: clean review `covered` / `not_covered` scope completeness.
- `unexplained_dirty_worktree_count`: count dirty or untracked worktree states that cannot be tied to the accepted child task.

## Evidence Boundary

These scenario checks are contract and fixture coverage. They do not prove real Codex App runtime execution, installed plugin cache/source equivalence, branch deletion, archive execution, merge-back execution, commit, push, PR creation, tracker mutation, UAT, or release readiness.
