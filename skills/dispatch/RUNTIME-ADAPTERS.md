# Dispatch Runtime Adapters

## Target Reader

Groundwork dispatch users, runtime adapter authors, and reviewers validating runtime route fit.

## Reader Action Needed

Use capability profiles to choose a runtime and state what it may and may not do.

## Decision Supported

Whether a task should become managed worktree package, subagent package, main-thread action, read-only coordinator review, or clean-review assignment.

## Scope

Initial dispatch runtime capability profiles. This document does not execute tools or prove runtime availability in the current Codex surface.

## Out of Scope

Runtime execution, Codex App thread creation, subagent spawning, manual worktree creation, remote writes, tracker mutation, and final readiness decisions.

## Evidence Level

Derived from dispatch runtime router contracts, routing profiles, conflict preflight, and Dispatch Package v2 rules.

## Capability Profiles

| runtime_id | Fit | Can Write | Isolation | Required Output | Avoid / Hard Stops |
| --- | --- | --- | --- | --- | --- |
| `codex_app_managed_worktree_thread` | independent accepted write tasks needing isolated diff/validation/review package | true | thread + Codex-managed worktree | `review_package` | no read-only/planning/hybrid pre-split work; no missing Goal Contract/source package/verification expectation; no runtime execution claim without adapter evidence |
| `codex_subagent` | read-only parallel review, exploration, diagnosis, multi-perspective critique | false by default | subagent prompt; filesystem tool-dependent | `findings_package` or `diagnosis_package` | no automatic spawn; no file edits unless explicitly requested, approved, supported, and evidenced |
| `main_thread_direct` | tiny edits, direct answers, one-off low-risk fixes, coordination | true | current workspace | `direct_result` | no parallel isolation or independent lifecycle claims |
| `main_thread_readonly` | PRD/dispatch/architecture/security/QA review, planning, decision support | false | none | `findings_package` | no implementation or package execution |
| `clean_reviewer` | review completed package/diff/evidence set | false | review package | `review_findings` | no remediation edits, merge/archive/branch cleanup, final readiness, or hidden parent context |

## Managed Worktree Admissibility

Package addressed to `codex_app_managed_worktree_thread` requires exactly one concrete write task with:

- `route_decision.route = worktree_isolated`;
- `task_type = write_implementation`, `readiness = ready_for_agent`;
- `isolation.filesystem = codex_managed_worktree`;
- concrete isolation input such as dirty workspace, unrelated staged files, stale base, shared-file conflict, serial dependency, setup requirement, rollback/archive need, or material write risk;
- complete Goal Contract, native source package, verification expectation, and `runtime_package.expected_output = review_package`.

Reject or reroute read-only, planning-only, hybrid pre-split, wrong-runtime, missing-truth, missing-Goal-Contract, missing-source-package, missing-verification, or non-review-package tasks to `needs_info`, `needs_split`, `main_thread_readonly`, or human decision.

## Execution Boundary

Groundwork defines routing requirements and package contracts only. Creating managed worktrees/threads, placing `/goal`, monitoring lifecycle, collecting review packages, and applying selectors belong to execution-capable adapters. Do not claim worktree/thread creation, validation, selector enforcement, stage, commit, push, or PR without adapter evidence. `runtime_surface.codex_app_worktree_available` is availability metadata, not execution proof.

## Subagent Boundary

Phase 1 subagent dispatch is package-only unless capability detection, explicit execution request/approval, and runtime evidence exist. Subagent package must include role, context package, prompt, constraints, expected output, stop/pause conditions, result schema, capability detection result, and execution status.

## Direct / Read-only / Clean Review Boundary

Use current workspace direct only when workspace status and risk are clear. Use read-only main thread for coordinator-level review/planning only. Use clean reviewer for fresh-context inspection of completed packages; reviewer output is findings only and must cite supplied package evidence.
