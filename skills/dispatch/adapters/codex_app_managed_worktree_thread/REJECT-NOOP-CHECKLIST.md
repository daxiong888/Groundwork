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

## Status Mapping

- Use `no_worktree_needed` for non-managed, read-only, planning-only, or pre-split hybrid work.
- Use `blocked` when source truth, approval, required tools, conflict resolution, or required package fields are missing.
- Use `needs_remediation` when the package is close but must be corrected before execution.
- Use `no_execution_needed` when the package intentionally required no runtime execution.

Never silently coerce a rejected package into managed worktree execution.
