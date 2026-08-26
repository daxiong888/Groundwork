# Managed Worktree Thread Lifecycle

Target Reader: Groundwork dispatch maintainers, runtime adapter authors, coordinators, and reviewers handling `codex_app_managed_worktree_thread` results.

Reader Action Needed: Use this lifecycle to report only managed worktree thread execution state. Track review, merge-back, archive, and branch cleanup on their independent Result Package axes.

Decision Supported: Whether one managed worktree child thread is admitted, initializing, active, or has returned/failed/blocked, without inferring downstream review or cleanup state.

Scope: Thread-only states and legal transitions for one Codex App managed worktree child after Dispatch Package v2 admission.

Out of Scope: Public skills, automatic thread tool execution from `dispatch`, automatic archive, branch deletion, commit, push, PR creation, tracker mutation, release readiness, UAT readiness, and replacing `verify` or `triage`.

Evidence Level: Derived from PRD v0.3.3 FR-1, Dispatch Package v2, managed worktree review/result package contracts, Groundwork git-boundary rules, and Codex App closeout risks.

## Core Rules

- A child thread must not archive itself, delete branches, stage, commit, push, open PRs, close issues, mutate trackers, or change remote state unless separately approved.
- Thread completion is not review pass, merge-back, archive readiness, or branch cleanup.
- Review, merge-back, archive, and branch cleanup each require their own status and evidence under the canonical Result Package.
- `pendingWorktreeId` is pending initialization evidence only. It must resolve to both child thread identifier and worktree path before success can be claimed.
- While initialization is pending, coordinator waits/polls/resolves or routes to `blocked`/`human_decision`; it must not implement the same task in the parent thread or create manual fallback worktrees without explicit topology approval.

## Thread Lifecycle States

```text
package_admitted -> worktree_init_pending | child_thread_created | blocked
worktree_init_pending -> child_thread_created | failed | blocked
child_thread_created -> prompt_delivered | failed | blocked
prompt_delivered -> running | failed | blocked
running -> result_returned | failed | blocked
```

`result_returned`, `failed`, and `blocked` end the current runtime attempt. A corrected retry starts from a new, evidenced admission attempt; it must not rewrite prior events. No transition may skip evidence preservation. Unknown state routes to `blocked` or `human_decision` rather than inferring a later state.

## Independent Status Axes

These axes are not lifecycle transitions:

| Axis | Owner | Key Safety Rule |
| --- | --- | --- |
| `review` | fresh reviewer or explicit coordinator intake | `result_returned` does not mean review passed; child self-check is not clean review. |
| `merge_back` | coordinator closeout | Review pass does not mean changes were applied; merge/discard needs source and git-boundary evidence. |
| `archive` | coordinator closeout | Merge/discard/retention evidence may support archive readiness, but never proves archive execution. |
| `branch_cleanup` | coordinator plus required approver | Archive does not imply cleanup; unknown, remote, protected, or force deletion routes to `human_decision`. |

Each axis records its own status and evidence using `skills/dispatch/RESULT-PACKAGE.md`. A coordinator may evaluate axes in parallel or sequence, but must not encode them as thread states.

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
  thread_status: init_pending | created | prompt_delivered | active | result_returned | failed | blocked
  created_at: ""
  last_checked_at: ""
```

Identity is `runtime_correlation_id`; task id, branch, and title are supporting evidence only. `worktree_init_pending` may record `pendingWorktreeId`, but it is not a recoverable active-work registry record until child thread id and worktree path exist.

Every thread status change must preserve an event with correlation id, task id, from/to status, reason, evidence refs, artifact path, and timestamp. If no artifact path or trace log exists, route to `blocked` or `human_decision`. Review, merge, archive, and cleanup statuses must not be written into `thread_status`.

## State Evidence

| State Group | Required Evidence |
| --- | --- |
| Admission/init | Dispatch Package identity, admissibility result, execution gate, pending id or resolved child thread/worktree evidence. |
| Active run | Delivered prompt identity, last runtime status, and blockers. |
| Result return | Returned review/result package, validation status, changed-file evidence, and blockers. |

## Archive Readiness Gate

Archive readiness is not a thread state. Set `archive.status: ready` only after a closeout package cites the input result outcome, review status, merge/discard/retention status, unresolved blockers, and any required human decision. A blocked runtime may support archive readiness only when evidence is preserved and a human decision confirms retention is unnecessary.

Thread archive may remove a Codex-managed worktree, but it is not branch cleanup evidence. Record `archive.status` and `branch_cleanup.status` independently even when both are finalized in one approved closeout operation.

## Regression Boundaries

Reject child prompts/results that self-archive; advance `pendingWorktreeId` to `child_thread_created` without resolved child thread/worktree path; combine pending init with parent-thread implementation/manual fallback without approval; put review/merge/archive/cleanup values in `thread_status`; or claim that runtime return, review pass, merge, archive, or branch cleanup implies another axis.
