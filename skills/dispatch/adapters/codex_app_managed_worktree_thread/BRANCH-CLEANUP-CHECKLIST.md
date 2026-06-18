# Managed Worktree Branch Cleanup Checklist

Target Reader: Groundwork coordinators, runtime adapter authors, and reviewers deciding whether branch cleanup evidence can support `native_closeout_package.cleanup_decision.branch_action`.
Reader Action Needed: Fill this checklist after closeout, archive, merge-back, discard, or blocked-with-human-decision evidence has been preserved, and before any branch cleanup recommendation is made.
Decision Supported: Whether `cleanup_decision.branch_action` should be `not_applicable`, `retain_branch`, `delete_local_branch`, or `human_decision`.
Artifact Type: branch cleanup checklist
Source of Truth: `docs/prd-v0.4.0-codex-native-worktree-handoff-alignment.md` FR-404/AC-404, `CLOSEOUT-PACKAGE-TEMPLATE.md`, V040-005 in `artifacts/v0.4.0-codex-native-worktree-handoff/issue-map.md`, and v0.3.3 branch-cleanup compatibility rules.
Scope: Branch identity, branch scope, merge/discard status, protected/default/base branch checks, worktree status evidence, approval gates, and mapping to native closeout branch cleanup decisions.
Out of Scope: Thread archive, managed worktree deletion, merge-back, force deletion execution, remote branch deletion execution, commits, pushes, pull requests, tracker mutation, runtime execution, release readiness, UAT readiness, and final acceptance.
Evidence Level: Local checklist evidence only. It does not execute git commands and does not prove branch deletion or runtime cleanup occurred.
Safe to Share / Redaction Notes: Safe to share as a checklist template. Do not include secrets, credentials, private URLs, browser cookies, PII, raw logs, private request payloads, or long diffs in package instances.

## Native Closeout Mapping

This checklist supplies evidence for `native_closeout_package.cleanup_decision.branch_action`.

- `cleanup_decision.branch_action: delete_local_branch` is allowed only when this checklist fully supports a local, task-scoped, safe deletion recommendation.
- `cleanup_decision.branch_action: retain_branch` is used when branch retention is safer, branch cleanup is not currently needed, or evidence supports keeping the branch for review, audit, rollback, remediation, or human inspection.
- `cleanup_decision.branch_action: human_decision` is used when branch existence, ownership, scope, merge state, protection state, worktree status, remote cleanup, force deletion, or approval evidence is missing or high risk.
- `cleanup_decision.branch_action: not_applicable` is used only when evidence proves no associated branch exists or branch cleanup is outside the closeout scope.
- Branch cleanup evidence must not set or imply `merge_decision.recommendation`.
- Thread archive and worktree retention are handled by `cleanup_decision.thread_action` and `cleanup_decision.worktree_action`, not by this branch checklist.

## Required Shape

```yaml
branch_cleanup:
  runtime_correlation_id: ""
  task_id: ""
  branch_detected: true | false | unknown
  branch_name: ""
  branch_scope: local | remote | both | unknown
  branch_created_by_child: true | false | unknown
  branch_checked_out_in_worktree: true | false | unknown
  branch_points_to_head: true | false | unknown
  merged_to_target: true | false | unknown
  protected_or_default_branch: true | false | unknown
  cleanup_recommendation: delete_local | delete_remote | retain | human_decision | no_branch_detected
  approval_required: true | false
  evidence:
    status_command: ""
    branch_command: ""
    merge_check: ""
    worktree_status:
      staged_changes: true | false | unknown
      unstaged_dirty_changes: true | false | unknown
      untracked_files: true | false | unknown
      stash_entries: true | false | unknown
      may_belong_to_branch: true | false | unknown
  risk:
    reason_to_retain: ""
    blockers: []

  native_closeout_mapping:
    branch_action: delete_local_branch | retain_branch | human_decision | not_applicable
    mapping_reason: ""
    completed_cleanup_evidence: []
```

`branch_cleanup.cleanup_recommendation` is a legacy v0.3.3 compatibility field. Native closeout packages should consume `native_closeout_mapping.branch_action` as `cleanup_decision.branch_action` and must not use a broad `cleanup_action` field.

## Core Rules

- Branch cleanup is never inferred from thread archive, managed worktree removal, closeout, merge-back, discard, or review pass.
- Branch cleanup is a cleanup decision only. It is not a merge recommendation and must not appear under `merge_decision`.
- `runtime_correlation_id` is the stable cleanup identity. Thread title and branch name are not enough to correlate cleanup with the child runtime.
- Unknown branch state must route to `human_decision` or `retain`.
- High-risk branch state must block deletion until the risk is resolved or a human explicitly decides retention or cleanup.
- Protected, default, and base branches must never be deleted.
- Remote branch deletion always requires explicit approval.
- Force deletion always requires an explicit human decision, even for local task branches.
- Staged changes, unstaged dirty changes, untracked files, and stash entries are branch-retention evidence until proven unrelated.
- A cleanup recommendation is not execution evidence. Use adapter/runtime evidence only when reporting that cleanup actually occurred.

## Local Branch Rules

Recommend `delete_local` only when all of these are evidenced:

- `branch_detected: true`
- `branch_scope: local`
- `branch_created_by_child: true`
- `branch_checked_out_in_worktree: false`
- `protected_or_default_branch: false`
- the branch is not the repository default branch, base branch, release branch, protected branch, or shared integration branch
- `merged_to_target: true`, or the child work was intentionally discarded and branch retention is not required
- no open blocker indicates unknown ownership, unknown merge state, dirty worktree dependency, staged changes, unstaged dirty changes, untracked files, stash entries, missing review/result evidence, or pending human decision
- worktree status evidence shows no staged changes, no unstaged dirty changes, no untracked files, no stash entries, or proves any such state cannot belong to this branch

Use `retain` or `human_decision` instead of `delete_local` when the branch is unmerged, checked out, shared, protected/default/base, not clearly task-scoped, or still needed for review, merge-back, audit, or remediation.

## Remote Branch Rules

Recommend `delete_remote` only as a human-approved next action, never as automatic cleanup.

Remote cleanup requires evidence that:

- the remote branch exists and matches the task-scoped branch identity;
- the branch is not protected, default, base, release, or shared integration state;
- the branch is merged to the intended target, or a human has explicitly decided to discard the remote branch;
- no PR, review, rollback, audit, or recovery workflow still needs the branch;
- worktree status evidence proves staged changes, unstaged dirty changes, untracked files, and stash entries are absent or cannot belong to the branch;
- explicit approval for remote branch deletion is present.

If any remote evidence is missing, set `cleanup_recommendation: human_decision` or `retain` and `approval_required: true`.

## Unknown Or High-Risk Conditions

Use `human_decision` or `retain` when any of these is true:

- `branch_detected: unknown`
- `branch_scope: unknown`
- `branch_created_by_child: unknown`
- `branch_checked_out_in_worktree: true | unknown`
- `merged_to_target: false | unknown`
- `protected_or_default_branch: true | unknown`
- branch name is empty, ambiguous, reused, or not task-scoped
- branch appears on both local and remote and remote cleanup approval is missing
- cleanup would require force deletion
- closeout evidence does not prove whether branch retention is still needed
- staged changes are present or unknown and may belong to the branch
- unstaged dirty changes are present or unknown and may belong to the branch
- untracked files are present or unknown and may belong to the branch
- stash entries are present or unknown and may belong to the branch

Use `no_branch_detected` only when evidence shows no associated local or remote branch exists.

## Worktree Status Rules

Branch cleanup must inspect worktree status separately from merge and branch identity evidence.

Record status for:

- staged changes;
- unstaged dirty changes;
- untracked files;
- stash entries.

If any status is `unknown`, or if any status is present and may belong to the branch being cleaned, then `delete_local` and `delete_remote` are blocked. Use `retain` or `human_decision` until the status is proven unrelated, preserved elsewhere, or explicitly handled by a human decision.

Do not treat a clean branch merge check as proof that untracked files or stash entries are safe. Untracked files and stash entries are not represented by ordinary merge checks and must be handled as separate retention evidence.

## Approval Rules

Set `approval_required: true` for:

- any remote branch deletion;
- any force deletion;
- any cleanup where branch ownership, merge state, protection/default/base status, or retention need is not fully evidenced;
- any branch that might be shared across tasks, releases, PRs, reviews, audits, or rollback paths.

Set `approval_required: false` only for `no_branch_detected`, `retain` when the decision is explicitly to keep the branch and perform no deletion, or a fully evidenced local task-scoped merged branch deletion recommendation that does not use force deletion and does not touch remote state.

## Status Mapping

| Evidence | Legacy recommendation | Native closeout mapping |
|---|---|---|
| No associated branch exists | `no_branch_detected` | `cleanup_decision.branch_action: not_applicable` |
| Unknown branch existence, owner, scope, merge state, protection state, or worktree status | `human_decision` or `retain` | `cleanup_decision.branch_action: human_decision` or `retain_branch` |
| Local task branch, merged or intentionally discarded, not checked out, not protected/default/base | `delete_local` | `cleanup_decision.branch_action: delete_local_branch` |
| Local branch unmerged, checked out, shared, protected/default/base, or still needed | `retain` or `human_decision` | `cleanup_decision.branch_action: retain_branch` or `human_decision` |
| Staged, unstaged dirty, untracked, or stash state is unknown or may belong to the branch | `retain` or `human_decision` | `cleanup_decision.branch_action: retain_branch` or `human_decision` |
| Remote branch exists and deletion approval is missing | `human_decision` | `cleanup_decision.branch_action: human_decision` |
| Remote branch exists and explicit deletion approval is present | `delete_remote` as the approved next action | `cleanup_decision.branch_action: human_decision`; remote deletion remains a separately approved action |
| Force deletion would be needed | `human_decision` | `cleanup_decision.branch_action: human_decision` |

## Reporting Rules

When reporting branch cleanup state:

- say whether this is a recommendation, approval gate, or completed runtime action;
- cite the exact evidence fields used for local/remote/default/protected/unmerged decisions;
- state that archive and branch cleanup are separate if archive evidence is also present;
- state that branch cleanup is separate from merge decision and does not make `merge_decision.recommendation: merge` safe;
- do not claim branch cleanup completed without adapter/runtime evidence and approval where required.

## Checklist And Eval Hooks

Branch cleanup checklist validation and evals should reject:

- packages that treat `archived` as `branch_cleaned`;
- local deletion recommendations for unknown, checked-out, unmerged, protected, default, base, shared, or non-task-scoped branches;
- local or remote deletion recommendations when staged changes, unstaged dirty changes, untracked files, or stash entries are unknown or may belong to the branch;
- remote deletion recommendations without explicit approval;
- force deletion recommendations without explicit human decision;
- `no_branch_detected` when branch evidence is missing rather than proven absent.
- packages that express branch cleanup through a broad native `cleanup_action` field instead of `cleanup_decision.branch_action`.
