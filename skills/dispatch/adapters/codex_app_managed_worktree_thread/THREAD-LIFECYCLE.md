# Managed Worktree Thread Lifecycle

## Target Reader

Groundwork dispatch maintainers, runtime adapter authors, coordinators, and reviewers handling `codex_app_managed_worktree_thread` results.

## Reader Action Needed

Use this lifecycle to decide whether a managed worktree child thread may continue, needs remediation, is ready for clean review/merge-back, may be archived, or must remain available for human decision.

## Decision Supported

Whether archive, branch cleanup, remediation, merge-back, discard, or human decision is the next legal action for one managed worktree child task.

## Scope

Lifecycle states and legal transitions for one Codex App managed worktree child thread after Dispatch Package v2 admission.

## Out of Scope

Public skills, automatic thread tool execution from `dispatch`, automatic archive, branch deletion, commit, push, PR creation, tracker mutation, release readiness, UAT readiness, and replacing `verify` or `triage`.

## Evidence Level

Derived from PRD v0.3.3 FR-1, Dispatch Package v2, managed worktree review/result package contracts, Groundwork git-boundary rules, and Codex App closeout risks.

## Core Rules

- A child thread must not archive itself, delete branches, stage, commit, push, open PRs, close issues, mutate trackers, or change remote state unless separately approved.
- `review_package_returned`, `clean_review_pending`, and `needs_remediation` are not enough for `archive_ready`.
- `archived` does not imply `branch_cleaned`; branch cleanup is separate evidence and approval.
- `pendingWorktreeId` is pending initialization evidence only. It must resolve to both child thread identifier and worktree path before success can be claimed.
- While initialization is pending, coordinator waits/polls/resolves or routes to `blocked`/`human_decision`; it must not implement the same task in the parent thread or create manual fallback worktrees without explicit topology approval.

## Lifecycle States

```text
package_admitted -> worktree_init_pending -> child_thread_created -> prompt_delivered -> running
running -> review_package_returned | needs_remediation | blocked
review_package_returned -> clean_review_pending | needs_remediation | blocked
clean_review_pending -> clean_review_passed | needs_remediation | blocked
clean_review_passed -> merge_pending | discard_pending | blocked
needs_remediation -> running | discard_pending | blocked
merge_pending -> merged_to_main_worktree | blocked
discard_pending -> discarded | blocked
merged_to_main_worktree | discarded -> archive_ready
blocked -> archive_ready only with preserved evidence and human decision that retention is not needed
archive_ready -> archived | blocked
archived -> branch_cleanup_pending | branch_retained_with_reason | closed only when branch cleanup is not applicable/finalized
branch_cleanup_pending -> branch_cleaned | branch_retained_with_reason | blocked
branch_cleaned | branch_retained_with_reason -> closed
```

No transition may skip evidence preservation. Unknown state routes to `blocked` or `human_decision` through closeout rather than inferring a later state.

## Registry Record

Each managed worktree child needs a recoverable adapter/coordinator registry record before `running` or later active states:

```yaml
worktree_thread_registry:
  runtime_correlation_id: ""
  task_id: ""
  branch: ""
  base_ref: ""
  worktree_path: ""
  artifact_path: ""
  owner_skill: dispatch
  current_status: created | active | review-ready | blocked | merge-ready | merged | archive-ready | archived | branch-cleanup-pending | branch-cleaned | branch-retained | closed | abandoned
  created_at: ""
  last_checked_at: ""
```

Identity is `runtime_correlation_id`; task id, branch, and title are supporting evidence only. `worktree_init_pending` may record `pendingWorktreeId`, but it is not a recoverable active-work registry record until child thread id and worktree path exist.

Every status change must preserve an event with correlation id, task id, from/to status, reason, evidence refs, artifact path, and timestamp. If no artifact path or trace log exists, route to `blocked` or `human_decision`.

## State Evidence

| State Group | Required Evidence |
| --- | --- |
| Admission/init | Dispatch Package identity, admissibility result, execution gate, pending id or resolved child thread/worktree evidence. |
| Running/result | Delivered prompt identity, last runtime status, returned review/result package, validation status, blockers. |
| Review/remediation | Fresh clean-review evidence, failed check/unmet AC, remediation path, or blocker list. |
| Merge/discard | Merge-back source and git boundary preconditions, or discard reason and preserved evidence. |
| Archive | Closeout package showing merge/discard/blocked-with-human-decision complete and evidence preserved. |
| Branch cleanup | Branch checklist evidence, approval where required, or retention/not-applicable reason. |

## Archive Readiness Gate

`archive_ready` is legal only after merge-back evidence, discard evidence, or blocked-with-human-decision evidence proves the child worktree no longer needs retention. Before recommending archive, closeout names review package status, result package status, clean-review status, merge/discard status, unresolved blockers, and any human decision.

Thread archive may remove a Codex-managed worktree, but it is not branch cleanup evidence. Direct `archived -> closed` requires evidence that branch cleanup is not applicable or already finalized.

## Eval Hooks

Reject child prompts/results that self-archive; `pendingWorktreeId -> child_thread_created` without resolved child thread/worktree path; pending init plus parent-thread implementation/manual fallback without approval; `review_package_returned` or `clean_review_pending` directly to `archive_ready`; `archived -> closed` when branch cleanup remains; or any claim that archive implies branch cleanup.
