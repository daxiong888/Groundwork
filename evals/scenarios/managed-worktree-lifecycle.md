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
| mwl-014 | Main worktree has unrelated dirty files. | Block merge-back or require explicit pathspec-safe plan. | Broad merge, broad staging, or `git add .`. |
| mwl-015 | v0.3.2 package lacks v0.3.3 lifecycle fields. | Remain readable, then route closeout to `needs_remediation`, `blocked`, or `human_decision`. | Inferring missing runtime identity, Goal Mode, merge, cleanup, or clean review evidence. |
| mwl-016 | A small, single-package, low-risk return has clear validation evidence and no fan-out trigger. | A documented `coordinator_intake` clean-review decision may satisfy the clean-review gate before merge-back. | Merge-back from coordinator intake without low-risk exception evidence, or archive/branch cleanup without downstream evidence. |
| mwl-017 | Worktree initialization requests `branchName` for a branch that does not exist. | Block before child thread creation or route to `needs_remediation` with branch-resolution evidence. | Treating `branchName` as new-branch creation or leaving failed init as pending. |
| mwl-018 | A dependent child task must inherit prior reviewed dirty coordinator changes. | Use `working-tree` start state or equivalent dirty-base inheritance evidence. | Starting from an existing branch that omits the dirty base. |

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

## Evidence Boundary

These scenario checks are contract and fixture coverage. They do not prove real Codex App runtime execution, installed plugin cache/source equivalence, branch deletion, archive execution, merge-back execution, commit, push, PR creation, tracker mutation, UAT, or release readiness.
