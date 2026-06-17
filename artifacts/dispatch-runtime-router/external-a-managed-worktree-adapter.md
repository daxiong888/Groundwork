# Superseded: Managed Worktree Adapter Task Package

Status: superseded by `skills/dispatch/adapters/codex_app_managed_worktree_thread/`

Target Reader: Groundwork maintainers and follow-up agents inspecting dispatch-runtime-router history.
Reader Action Needed: Do not use this file as the current implementation task package; use the internal adapter contract under `skills/dispatch/adapters/codex_app_managed_worktree_thread/`.
Decision Supported: Whether old External A work should still be routed to a separate repository.
Scope: Archived historical task package for the earlier external-adapter plan.
Out of Scope: Current implementation instructions, runtime execution, external repository updates, remote writes, tracker mutation, or public skill creation.
Evidence Level: Superseded by PR #58 adapter co-location work and the current dispatch adapter contract files.

## Current Canonical Source

The current managed worktree adapter contract is maintained inside Groundwork:

```text
skills/dispatch/adapters/codex_app_managed_worktree_thread/ADAPTER.md
skills/dispatch/adapters/codex_app_managed_worktree_thread/DISPATCH-PACKAGE-CONTRACT.md
skills/dispatch/adapters/codex_app_managed_worktree_thread/THREAD-PROMPT-TEMPLATE.md
skills/dispatch/adapters/codex_app_managed_worktree_thread/REVIEW-PACKAGE-TEMPLATE.md
skills/dispatch/adapters/codex_app_managed_worktree_thread/RESULT-PACKAGE-TEMPLATE.md
skills/dispatch/adapters/codex_app_managed_worktree_thread/REJECT-NOOP-CHECKLIST.md
skills/dispatch/adapters/codex_app_managed_worktree_thread/SELECTOR-ENFORCEMENT.md
skills/dispatch/adapters/codex_app_managed_worktree_thread/RATIONALE.md
```

`dispatch` remains the public skill and remains package-only. It must not create Codex App threads, create worktrees, spawn subagents, stage, commit, push, open PRs, close issues, or mutate trackers by default.

## Superseded Historical Context

This artifact originally described a separate External A task package for a standalone managed worktree adapter repository. That plan is no longer the current source of truth for Groundwork.

Do not route new implementation work from this file. If future work needs the managed worktree adapter contract, start from the internal adapter contract path above and the current dispatch package/result contracts:

```text
skills/dispatch/DISPATCH-PACKAGE.md
skills/dispatch/RESULT-PACKAGE.md
skills/dispatch/RUNTIME-ADAPTERS.md
docs/runtime-dispatch-workflow.md
```

## Current Execution Boundary

Groundwork owns routing, package generation, conflict preflight, expected result-package shape, and no-execution boundaries.

An execution-capable runtime adapter may create Codex App managed worktree child threads only after:

- the package is addressed to `runtime_id = codex_app_managed_worktree_thread`
- the package passes `DISPATCH-PACKAGE-CONTRACT.md`
- explicit execution approval is present
- required Codex App thread capabilities are available
- remote writes and destructive actions remain disabled unless separately approved

This archived artifact provides no active Goal Contract, no active task package, and no current verification checklist.
