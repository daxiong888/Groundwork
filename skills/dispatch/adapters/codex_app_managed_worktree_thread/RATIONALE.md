# Managed Worktree Adapter Rationale

Target Reader: Maintainers deciding whether `codex_app_managed_worktree_thread` belongs inside Groundwork dispatch or as a separate public skill.

Reader Action Needed: Use this rationale only when the adapter boundary is disputed.

Decision Supported: Whether `codex_app_managed_worktree_thread` should remain an internal dispatch adapter contract instead of becoming another public skill.

Scope: Design rationale for adapter co-location, package-only boundaries, and non-substitute runtime workflows.

Out of Scope: Runtime execution, public skill creation, tracker integration, remote writes, and current external repository maintenance.

Evidence Level: Derived from Groundwork v0.3.1 dispatch boundaries, Dispatch Package v2, Result Package, Goal Contract, and the prior managed-worktree adapter design.

## Decision

Groundwork keeps `dispatch` as the public skill and maintains `codex_app_managed_worktree_thread` as an internal adapter contract under `skills/dispatch/adapters/`.

## Why This Is Not A Public Skill

The adapter consumes packages after Groundwork has already decided source truth, readiness, task type, runtime route, Goal Contract, and validation expectations. Exposing it as a separate public skill would widen the trigger surface, invite users to bypass `to-prd -> to-issues -> triage -> dispatch`, and blur the Phase 1 package-only safety boundary.

## Why It Lives With Dispatch

The adapter must stay synchronized with:

- Dispatch Package v2 fields
- Goal Contract expectations
- Result Package shape
- conflict preflight and package admissibility
- selector enforcement terminology
- dispatch regression cases

Keeping those contracts in the same repository makes dispatch the source of truth while still preventing default runtime execution.

## Non-substitutes

Do not replace this adapter boundary with:

- manual `git worktree add`
- tmux panes or terminal multiplexing
- Codex CLI worker orchestration
- subagents doing implementation work
- guessed filesystem paths for child thread worktrees
- Groundwork-only changes that claim runtime execution happened

Those workflows may be useful elsewhere, but they do not provide the same Codex App managed-thread, diff, review, and lifecycle evidence surface.
