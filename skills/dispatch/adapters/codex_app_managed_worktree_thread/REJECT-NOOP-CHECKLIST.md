# Managed Worktree Reject And No-op Checklist

## Target Reader

Runtime adapters and dispatch reviewers deciding why no managed worktree child thread should be created.

## Reader Action Needed

Return a Result Package with the failing field or policy reason instead of creating a thread.

## Decision Supported

Whether a package should be rejected, no-oped, blocked, or sent back for remediation instead of creating a managed worktree child thread.

## Scope

Reject and no-op decisions for packages that are not admissible managed worktree write implementation tasks.

## Out of Scope

Runtime routing, package repair, thread creation, remote writes, and final readiness decisions.

## Evidence Level

Derived from Dispatch Package v2 admissibility rules, conflict preflight, and managed worktree adapter safety boundaries.

## Reject Or No-op Conditions

Do not create a managed worktree child thread for:

- `runtime_id != codex_app_managed_worktree_thread`
- `task_type = read_only_review`
- `task_type = planning_only`
- `task_type = hybrid` before a concrete write implementation subtask exists
- `readiness != ready_for_agent`
- missing or incomplete Goal Contract
- missing or incomplete source package
- missing `source_package.prd_excerpt`
- missing `source_package.issue_body`
- missing `goal_contract.preferred_runtime`
- missing or incomplete validation package
- `runtime_package.expected_output != review_package`
- `runtime_package.can_write_files != true`
- remote write requested without explicit approval
- destructive action requested without explicit approval
- unresolved conflict on shared files, schema, route, generated artifact, fixture, public contract, state machine, migration, or shared config
- branch cleanup requested as the only task for a managed worktree child thread
- branch cleanup request treats thread archive as branch deletion evidence
- local branch deletion requested for an unknown, unmerged, checked-out, protected, default, base, shared, or non-task-scoped branch
- local or remote branch deletion requested while staged changes, unstaged dirty changes, untracked files, or stash entries are unknown or may belong to the branch
- remote branch deletion requested without explicit approval
- force branch deletion requested without explicit human decision
- unresolved `pendingWorktreeId` for the same task or runtime correlation id without both a child thread id and worktree path
- parent/coordinator implementation requested or started for the same task while the managed worktree request is still pending
- manual git worktree fallback requested to bypass a pending Codex App managed worktree without explicit user approval for the topology change

## Branch Cleanup No-op And Block Rules

Branch cleanup is a closeout protocol, not a reason to create a managed worktree child implementation thread.

Use `BRANCH-CLEANUP-CHECKLIST.md` for branch cleanup decisions. If a package asks the adapter to create a child thread only to inspect or delete branches, do not create the child thread.

Return:

- `no_execution_needed` when evidence proves no associated branch exists or the branch is intentionally retained.
- `blocked` when branch evidence is missing and the package cannot make a safe cleanup recommendation.
- `needs_remediation` when the package conflates archive with branch cleanup or omits required branch cleanup fields.
- `human_decision` when cleanup would delete a remote branch, require force deletion, touch an unknown or high-risk branch, or delete a branch without fully evidenced local/task-scoped/merged status.

Never silently coerce a branch cleanup package into managed worktree execution or destructive git cleanup.

## Status Mapping

- Use `no_worktree_needed` for non-managed, read-only, planning-only, or pre-split hybrid work.
- Use `blocked` when source truth, approval, required tools, conflict resolution, or required package fields are missing.
- Use `needs_remediation` when the package is close but must be corrected before execution.
- Use `no_execution_needed` when the package intentionally required no runtime execution.
- Use `human_decision` when branch cleanup risk requires explicit approval, human retention/deletion choice, or a proposed fallback would change the requested managed-worktree/thread topology.

Never silently coerce a rejected package into managed worktree execution.
