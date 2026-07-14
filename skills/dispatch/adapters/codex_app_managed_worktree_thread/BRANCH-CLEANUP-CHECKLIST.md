# Managed Worktree Branch Cleanup Checklist

Target Reader: Groundwork coordinators, runtime adapter authors, and reviewers deciding whether branch cleanup evidence can support `native_closeout_package.branch_cleanup`.
Reader Action Needed: Fill this checklist after closeout/archive/merge/discard evidence has been preserved and before any branch cleanup recommendation.
Decision Supported: Whether branch action should be `not_applicable`, `retain_branch`, `delete_local_branch`, or `human_decision`.
Artifact Type: branch cleanup checklist
Source of Truth: `CLOSEOUT-PACKAGE-TEMPLATE.md`, v0.4.0 native closeout requirements, and v0.3.3 branch-cleanup compatibility rules.
Scope: Branch identity, scope, merge/discard status, protected/default/base checks, worktree status evidence, approval gates, and native closeout mapping.
Out of Scope: Thread archive, managed worktree deletion, merge-back, force deletion execution, remote branch deletion execution, commits, pushes, PRs, tracker mutation, runtime execution, release readiness, UAT readiness, and final acceptance.
Evidence Level: Local checklist evidence only. It does not execute git commands or prove branch deletion/runtime cleanup occurred.
Safe to Share / Redaction Notes: Safe to share as a checklist template. Do not include secrets, credentials, private URLs, cookies, PII, raw logs, request payloads, or long diffs.

## Native Closeout Mapping

- `delete_local_branch`: only for fully evidenced local, task-scoped, safe deletion recommendation.
- `retain_branch`: safer retention, no current cleanup need, or review/audit/rollback/remediation needs remain.
- `human_decision`: missing or high-risk branch existence, ownership, scope, merge state, protection, worktree status, remote cleanup, force deletion, or approval.
- `not_applicable`: evidence proves no associated branch exists or branch cleanup is outside scope.

Branch cleanup must not imply merge readiness, thread archive, worktree cleanup, runtime execution, release readiness, or UAT readiness.

## Required Shape

```yaml
branch_cleanup:
  status: not_applicable | pending | cleaned | retained | blocked | human_decision | unverified
  recommendation: delete_local_branch | retain_branch | human_decision | not_applicable
  runtime_correlation_id: ""
  task_id: ""
  branch_detected: true | false | unknown
  branch_name: ""
  branch_scope: local | remote | both | unknown
  branch_created_by_child: true | false | unknown
  branch_checked_out_in_worktree: true | false | unknown
  merged_to_target: true | false | unknown
  protected_or_default_branch: true | false | unknown
  approval_required: true | false
  evidence: {status_command, branch_command, merge_check, worktree_status}
  risk: {reason_to_retain, blockers}
```

## Deletion Rules

Recommend local deletion only when all are evidenced: branch exists, local-only or local action only, child-created/task-scoped, not checked out, not protected/default/base/release/shared, merged or intentionally discarded, no retention blocker, and worktree status proves staged/unstaged/untracked/stash state is absent or unrelated.

Use `retain` or `human_decision` when branch existence/scope/owner/merge/protection/worktree status is unknown, branch is unmerged/checked out/shared/protected/default/base, branch may be needed for review/audit/rollback/remediation, or deletion would require force.

Remote deletion is never automatic. It requires explicit approval, remote branch identity, protected/default/base/release/shared checks, merge/discard evidence, no PR/review/rollback/audit need, clean worktree status evidence, and human approval. If any item is missing, use `human_decision` or `retain`.

## Status Mapping

| Evidence | Native closeout mapping |
| --- | --- |
| No associated branch exists | `branch_cleanup.status: not_applicable`, `recommendation: not_applicable` |
| Unknown branch existence, owner, scope, merge state, protection, or worktree status | `human_decision` or `retain_branch` |
| Local task branch, merged/discarded, not checked out, not protected/default/base | `delete_local_branch` |
| Branch unmerged, checked out, shared, protected/default/base, or still needed | `retain_branch` or `human_decision` |
| Dirty/untracked/stash state unknown or may belong to branch | `retain_branch` or `human_decision` |
| Remote deletion approval missing or force deletion needed | `human_decision` |

## Reporting And Eval Hooks

Report whether this is a recommendation, approval gate, or completed runtime action; cite branch/protection/merge/worktree evidence; keep archive, worktree cleanup, branch cleanup, and merge-back separate. Reject packages that treat archive as branch cleanup, delete unknown/high-risk branches, delete remote branches without approval, force-delete without human decision, or use broad `cleanup_action` instead of `branch_cleanup`.
