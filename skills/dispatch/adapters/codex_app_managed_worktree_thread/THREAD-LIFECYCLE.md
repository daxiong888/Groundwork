# Managed Worktree Thread Lifecycle

## Target Reader

Groundwork dispatch maintainers, runtime adapter authors, coordinators, and reviewers handling `codex_app_managed_worktree_thread` results.

## Reader Action Needed

Use this lifecycle to decide whether a managed worktree child thread may continue running, needs remediation, is ready for clean review or merge-back, may be archived, or must remain available for a human decision.

## Decision Supported

Whether archive, branch cleanup, remediation, merge-back, discard, or human decision is the next legal action for one managed worktree child task.

## Scope

Lifecycle states and legal transitions for one Codex App managed worktree child thread after a Dispatch Package v2 task has been admitted.

## Out of Scope

Public skills, automatic thread tool execution from `dispatch`, automatic archive, branch deletion, commit, push, PR creation, tracker mutation, release readiness, UAT readiness, and replacing `verify` or `triage`.

## Evidence Level

Derived from PRD v0.3.3 FR-1, Dispatch Package v2, managed worktree review/result package contracts, Groundwork git-boundary rules, and observed Codex App managed worktree closeout risks.

## Core Rules

- A child thread must not archive itself.
- A child thread must not delete local or remote branches.
- A child thread must not stage, commit, push, open PRs, close issues, mutate trackers, or change remote state unless separately approved.
- `review_package_returned` is not enough for `archive_ready`.
- `clean_review_pending` is not enough for `archive_ready`.
- `needs_remediation` is not enough for `archive_ready` unless remediation is explicitly moved to a new task and the current child worktree is intentionally discarded.
- `archived` does not imply `branch_cleaned`.
- Branch cleanup is a separate lifecycle path with separate evidence and approval requirements.
- `pendingWorktreeId` is not success evidence. It may only represent pending initialization until it resolves to both a child thread identifier and a worktree path.
- While initialization is pending, the coordinator must wait/poll/resolve or route to `blocked`/`human_decision`. It must not implement the same task in the parent thread and must not create a manual git worktree fallback without explicit user approval for the topology change.

## Lifecycle States

```text
package_admitted
worktree_init_pending
child_thread_created
prompt_delivered
running
review_package_returned
clean_review_pending
clean_review_passed
needs_remediation
blocked
merge_pending
discard_pending
merged_to_main_worktree
discarded
archive_ready
archived
branch_cleanup_pending
branch_cleaned
branch_retained_with_reason
closed
```

## Worktree Thread Registry Record

Each managed worktree child thread must have a recoverable registry record before it can enter `running` or any later active work state. This is not a project-global task database; it is adapter/coordinator lifecycle evidence for one dispatched runtime task.

Required fields:

```yaml
worktree_thread_registry:
  runtime_correlation_id: ""
  task_id: ""
  branch: ""
  base_ref: ""
  worktree_path: ""
  artifact_path: ""
  owner_skill: "dispatch"
  current_status: created | active | review-ready | blocked | merge-ready | merged | archive-ready | archived | branch-cleanup-pending | branch-cleaned | branch-retained | closed | abandoned
  created_at: ""
  last_checked_at: ""
```

The registry identity is `runtime_correlation_id`. `task_id`, branch, and thread title are supporting evidence only and must not replace the correlation ID.

Status mapping:

| Registry status | Lifecycle states |
|---|---|
| `created` | `package_admitted`, `worktree_init_pending`, `child_thread_created`, `prompt_delivered` |
| `active` | `running` |
| `review-ready` | `review_package_returned`, `clean_review_pending`, `clean_review_passed` |
| `blocked` | `needs_remediation`, `blocked`, `discard_pending` |
| `merge-ready` | `merge_pending` |
| `merged` | `merged_to_main_worktree` |
| `archive-ready` | `archive_ready` |
| `archived` | `archived` |
| `branch-cleanup-pending` | `branch_cleanup_pending` |
| `branch-cleaned` | `branch_cleaned` |
| `branch-retained` | `branch_retained_with_reason` |
| `closed` | `closed` |
| `abandoned` | `discarded`, `blocked` with human decision, or retained evidence that the child work is intentionally not continued |

`worktree_init_pending` may be recorded as an initialization trace with `pendingWorktreeId`, but it does not satisfy the recoverable registry record required for `running` or later active work because the child thread identifier and worktree path are still missing.

## Registry Event Rule

Every status change must preserve an event in the task artifact path or another adapter-visible trace log before the previous state can be forgotten:

```yaml
registry_event:
  runtime_correlation_id: ""
  task_id: ""
  from_status: ""
  to_status: ""
  reason: ""
  evidence_refs: []
  artifact_path: ""
  recorded_at: ""
```

If no artifact path or trace log is available, route to `blocked` or `human_decision` instead of advancing lifecycle state. A natural-language summary without event identity, timestamp, and evidence references is not enough for closeout recovery.

## State Definitions

| State | Meaning | Required Evidence |
|---|---|---|
| `package_admitted` | Adapter admissibility checks passed and execution approval/capability gates may be evaluated. | Dispatch Package v2 identity, admissibility result, execution gate status. |
| `worktree_init_pending` | Codex App returned a pending worktree request that has not resolved to an executable child thread/worktree. | `pendingWorktreeId`, intended runtime correlation id, wait/poll plan or blocker, and evidence that no parent implementation or manual fallback is being used. |
| `child_thread_created` | Runtime created a Codex App child thread. | Thread identifier and runtime evidence. |
| `prompt_delivered` | Adapter delivered the child prompt to the child thread. | Delivered prompt identity, task ID, and runtime evidence. |
| `running` | Child thread is executing or has not returned a terminal package. | Last observed status or runtime timestamp when available. |
| `review_package_returned` | Child returned a managed worktree review package. | Review package presence and completeness status. |
| `clean_review_pending` | Returned package needs fresh-context review before merge/discard/archive decision. | Intake decision and clean-review route. |
| `clean_review_passed` | Fresh clean reviewer found no blocking implementation-conformance issue. | Fresh review findings package and clean-review evidence. |
| `needs_remediation` | Evidence shows a scoped fix is still needed. | Failed check, unmet acceptance criterion, or review finding with remediation path. |
| `blocked` | Progress cannot continue without missing source truth, tool, permission, approval, environment, or human decision. | Blocker list and next-route recommendation. |
| `merge_pending` | Clean review passed and changes are eligible to apply into the main worktree, but merge-back is not complete. | Merge-back source and git-boundary preconditions. |
| `discard_pending` | Coordinator intends to discard child work, but discard evidence or approval is incomplete. | Discard reason and pending approval/evidence. |
| `merged_to_main_worktree` | Changes were applied to the main worktree. | Merge-back evidence, changed pathspecs, and validation status or validation gap. |
| `discarded` | Child work was intentionally not merged. | Discard reason and preserved review/result evidence. |
| `archive_ready` | Archive may be recommended because evidence is preserved and merge/discard/blocked-with-human-decision is complete. | Closeout package with `archive_ready: true`. |
| `archived` | Runtime evidence shows the child thread was archived. | Adapter/runtime archive evidence. |
| `branch_cleanup_pending` | A branch might remain and needs separate cleanup handling. | Branch state evidence or unknown branch state. |
| `branch_cleaned` | Branch cleanup completed with evidence and approval where required. | Branch cleanup evidence. |
| `branch_retained_with_reason` | Branch cleanup was skipped intentionally. | Retention reason, owner, or human decision. |
| `closed` | Thread lifecycle is closed and branch state is cleaned, retained, or not applicable. | Closeout package plus archive/branch final state evidence. |

## Legal Transitions

```text
package_admitted
  -> worktree_init_pending
  -> child_thread_created
  -> blocked

worktree_init_pending
  -> child_thread_created only after both child thread identifier and worktree path are known
  -> blocked

child_thread_created
  -> prompt_delivered
  -> blocked

prompt_delivered
  -> running
  -> blocked

running
  -> review_package_returned
  -> needs_remediation
  -> blocked

review_package_returned
  -> clean_review_pending
  -> needs_remediation
  -> blocked

clean_review_pending
  -> clean_review_passed
  -> needs_remediation
  -> blocked

clean_review_passed
  -> merge_pending
  -> discard_pending
  -> blocked

needs_remediation
  -> running
  -> discard_pending
  -> blocked

merge_pending
  -> merged_to_main_worktree
  -> blocked

discard_pending
  -> discarded
  -> blocked

merged_to_main_worktree
  -> archive_ready

discarded
  -> archive_ready

blocked
  -> archive_ready only when preserved evidence exists and a human decision says the worktree no longer needs retention

archive_ready
  -> archived
  -> blocked

archived
  -> branch_cleanup_pending
  -> branch_retained_with_reason
  -> closed only when branch cleanup is proven not applicable or branch state is otherwise finalized

branch_cleanup_pending
  -> branch_cleaned
  -> branch_retained_with_reason
  -> blocked

branch_cleaned
  -> closed

branch_retained_with_reason
  -> closed
```

No transition may skip evidence preservation. If the current state is unknown, route to `blocked` or `human_decision` through the closeout package instead of inferring a later state. After `archived`, `closed` is legal only when branch cleanup is not applicable, branch state is otherwise finalized, or the branch cleanup route has reached `branch_cleaned` or `branch_retained_with_reason` as applicable.

## Archive Readiness Gate

`archive_ready` is legal only after one of these conditions is true:

- `merged_to_main_worktree` with merge-back evidence;
- `discarded` with discard reason and preserved review/result evidence;
- `blocked` with preserved review/result evidence and a human decision that retaining the child worktree is not needed.

Before recommending archive, the closeout package must name preserved evidence:

- review package status;
- result package status;
- clean-review status;
- merge-back or discard status;
- unresolved blockers and human decision when blocked.

## Archive And Branch Cleanup Boundary

Thread archive may remove a Codex-managed worktree, but it is not branch cleanup evidence. A lifecycle may reach `archived` while still requiring `branch_cleanup_pending`, `branch_cleaned`, or `branch_retained_with_reason`; direct `archived -> closed` requires evidence that branch cleanup is not applicable or branch state is already finalized.

Use a later branch cleanup checklist when branch state is known or unknown. Unknown branch state must not be converted into `branch_cleaned`.

## Later Eval Hooks

Future lifecycle evals should reject:

- child prompts or results that tell the child to archive itself;
- `pendingWorktreeId -> child_thread_created` without resolved child thread identifier and worktree path;
- pending initialization that continues implementation in the parent/coordinator thread or creates a manual git worktree fallback without explicit user approval;
- `review_package_returned -> archive_ready` without merge, discard, or blocked-with-human-decision evidence;
- `clean_review_pending -> archive_ready`;
- `archived -> closed` when branch state is known to require cleanup;
- any claim that `archived` implies branch cleanup.

Managed worktree review/result templates expose lifecycle status for v0.3.3 closeout routing while preserving backward compatibility for v0.3.2 packages.
