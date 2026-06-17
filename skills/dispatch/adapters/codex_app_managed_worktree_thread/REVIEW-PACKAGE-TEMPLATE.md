# Managed Worktree Review Package Template

## Target Reader

Child implementation threads returning evidence for clean review and Groundwork Result Package wrapping.

## Reader Action Needed

Return this package after implementation, validation, or a blocker. Do not return `review_passed`; only the coordinator may assign that state after clean review.

## Decision Supported

Whether the coordinator has enough redacted, self-contained evidence to run clean review and route the result to `verify`, `triage`, `dispatch_write_task`, `human_decision`, or `done`.

## Scope

Review evidence from a managed worktree child thread for one accepted write implementation package.

## Out of Scope

Clean-review approval, release readiness, UAT readiness, remote writes, and claims not supported by child-thread evidence.

## Evidence Level

Derived from Groundwork Result Package requirements and the prior managed-worktree review package template.

```text
Review package:
- Output type: review_package
- Status: ready_for_review | needs_remediation | blocked
- Status rules:
  - ready_for_review: validation passed, or validation is not applicable and the reason is reviewable.
  - needs_remediation: validation failed, acceptance criteria are unmet, or a scoped fix direction remains.
  - blocked: source, tool, permission, environment, thread delivery, approval, or review evidence is incomplete.
  - Child threads must not output review_passed.

Runtime:
- Runtime ID: codex_app_managed_worktree_thread
- Adapter: codex_app_managed_worktree_thread
- Worktree type: Codex-managed
- Thread identifier:
- Thread title:
- Worktree path if available, or unavailable:

Task:
- Dispatch version:
- ID:
- Title:
- Task type: write_implementation
- Readiness: ready_for_agent
- Source link or path, or redacted source identifier if private or sensitive:
- Redacted self-contained source package:
- Acceptance criteria:
- Acceptance criteria checked:
- Non-goals:
- Base branch:
- Base commit:

Goal Contract evidence:
- Goal Contract present: yes | no
- Outcome targeted:
- Source truth used:
- Acceptance criteria mapping:
- Verification followed:
- Constraints and boundaries followed:
- Iteration policy followed:
- Stop condition reached:
- Pause conditions encountered:
- Risk gate result:

Selector enforcement:
- Requested model profile:
- Requested reasoning effort:
- Requested cost/latency bias:
- Enforcement status: tool_enforced | prompt_preference | unavailable | unknown
- Evidence for enforcement status:

Changes:
- Changed files:
- Diff summary:
- Diff base:
- Diff completeness: complete | redacted_complete | redacted_partial | not_applicable
- Completeness assertion: all behavior-changing hunks are included or summarized; omitted hunks are non-behavioral or sensitive and listed below.
- Redacted patch or detail with enough surrounding context to review each changed behavior:
- Omitted diff hunks and why omission is safe:

Validation:
- Applicability: applicable | not_applicable
- Skipped category: not_applicable | missing_dependency | permission | tool_unavailable | environment_failure | none
- Skipped/not-applicable reason:
- Commands run:
- Results:
- Redacted relevant output transcript:
- Checks not run and reason:

Risk and route:
- Remaining risks:
- Blockers:
- Recommended next route: verify | triage | dispatch_write_task | human_decision | done
```

Clean review should use this package as the task source and must not require direct filesystem access to the child thread's managed worktree.
