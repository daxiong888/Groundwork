# Codex App Managed Worktree Thread Adapter

## Target Reader

Groundwork dispatch users, runtime adapter authors, and reviewers inspecting packages addressed to `codex_app_managed_worktree_thread`.

## Reader Action Needed

Use this adapter contract to validate an addressed Dispatch Package v2 task, construct the child-thread prompt, and return a Groundwork-compatible Result Package when an execution-capable runtime is explicitly approved and available.

## Decision Supported

Whether a managed worktree child thread may be created for a package, what prompt and review package shape it must use, and how rejected or no-op inputs are reported back to Groundwork.

## Scope

This is an internal dispatch runtime adapter contract. It is intentionally not a public skill and must not contain skill frontmatter.

In scope:

- validating packages addressed to `runtime_id = codex_app_managed_worktree_thread`
- rejecting or no-oping non-admissible packages with evidence
- constructing a child implementation thread prompt
- requiring a self-contained review package from child threads
- wrapping execution, rejection, or no-op evidence in a Result Package
- tracking managed worktree lifecycle status
- preparing closeout package evidence before archive recommendation
- reporting selector enforcement truthfully

## Out of Scope

- deciding PRD scope, task slicing, readiness, or runtime route
- calling Codex App thread tools from `dispatch`
- creating manual git worktrees
- spawning subagents for implementation
- staging, committing, pushing, opening PRs, closing issues, archiving threads, or mutating trackers without explicit approval
- claiming worktree, thread, validation, selector, or remote-write execution without adapter evidence

## Evidence Level

Derived from Groundwork Dispatch Package v2, Result Package, Goal Contract, and the prior `codex-managed-worktree-threads` adapter contract.

## Ownership Boundary

`dispatch` owns:

- task type classification
- readiness and source-truth consumption
- Goal Contract consumption
- runtime selection
- conflict preflight
- Dispatch Package v2 generation
- expected Result Package requirements
- package-only and no-execution boundaries

This adapter owns:

- addressed package admissibility checks
- child-thread prompt construction
- review package requirements
- rejection and no-op Result Package requirements
- selector enforcement evidence requirements
- managed worktree lifecycle state and archive-readiness gates
- closeout package requirements after review/result package intake
- runtime evidence fields when an execution-capable Codex App thread adapter runs

## Required References

Load only the reference needed for the current step:

- `DISPATCH-PACKAGE-CONTRACT.md` for package admissibility, worktree initialization preflight, and rejection/no-op decisions.
- `THREAD-PROMPT-TEMPLATE.md` for child-thread prompt construction.
- `REVIEW-PACKAGE-TEMPLATE.md` when asking a child implementation thread for final output or preparing clean review.
- `RESULT-PACKAGE-TEMPLATE.md` when returning runtime output to Groundwork.
- `REJECT-NOOP-CHECKLIST.md` when an input must not create a managed worktree.
- `CONFLICT-PREFLIGHT.md` when a write task may overlap another task or depends on prerequisite merge-back/base refresh before child thread creation.
- `SELECTOR-ENFORCEMENT.md` when model or reasoning selector status is reported.
- `THREAD-LIFECYCLE.md` when reporting lifecycle state, archive readiness, or legal next transitions.
- `MERGE-BACK-PROTOCOL.md` when applying clean-reviewed child worktree changes back into the main worktree.
- `CLOSEOUT-PACKAGE-TEMPLATE.md` after review/result package intake and before any archive recommendation.
- `BRANCH-CLEANUP-CHECKLIST.md` when branch state is known or unknown after closeout/archive and cleanup must be recommended, retained, or routed to human decision.
- `RATIONALE.md` only when the adapter boundary is disputed.

## Execution Gate

Groundwork `dispatch` remains package-only. If a user asks to execute managed worktree packages, output the dispatch package plus:

```text
Proposed Action:
Target Runtime:
Required Tool Capability:
Risk:
Rollback/Undo:
Approval Needed:
```

Proceed only when explicit execution approval and the required Codex App thread capabilities are both present.

Before any Codex App worktree or child thread creation call, apply the worktree initialization preflight in `DISPATCH-PACKAGE-CONTRACT.md`. `startingState.branchName` is valid only for an already-existing branch. When a task must inherit the current reviewed dirty base, prefer a `working-tree` start state and treat detached HEAD as acceptable; merge-back must later use worktree path and explicit pathspec evidence, not implicit branch advancement.

## Lifecycle And Closeout Boundary

Use `THREAD-LIFECYCLE.md` to report the current managed worktree state and legal next transition. A child implementation thread must not archive itself and must not delete local or remote branches.

Use `CLOSEOUT-PACKAGE-TEMPLATE.md` after review/result package intake. Archive readiness is blocked until one of these has evidence:

- merge-back completed into the main worktree;
- child work intentionally discarded with reason;
- blocked state has preserved review/result evidence and a human decision that worktree retention is not needed.

`review_package_returned`, `clean_review_pending`, `needs_remediation`, `merge_pending`, and `discard_pending` are not archive-ready by themselves.

Archive and branch cleanup remain separate. `archived` does not imply branch cleanup, and branch deletion requires a later branch-cleanup checklist and the relevant approval gates.
