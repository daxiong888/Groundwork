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
  - ready_for_review: validation passed, or validation is not applicable and the reason is reviewable; if Goal Mode is required, runtime Goal Mode evidence is present.
  - needs_remediation: validation failed, acceptance criteria are unmet, or a scoped fix direction remains.
  - blocked: source, tool, permission, environment, thread delivery, approval, or review evidence is incomplete.
  - Child threads must not output review_passed.

Runtime:
- Runtime ID: codex_app_managed_worktree_thread
- Adapter: codex_app_managed_worktree_thread
- runtime_correlation_id:
- dispatch_id:
- runtime_identity.task_id:
- parent_thread_identifier:
- child_thread_identifier:
- initial_thread_title:
- current_thread_title:
- title_mutation_detected: true | false | unknown
- Title identity rule: thread title is display-only; correlate this package by Runtime Correlation ID.
- Worktree type: Codex-managed
- Thread identifier:
- Thread title display label:
- Worktree path if available, or unavailable:

Registry:
- Base ref:
- Branch:
- Artifact path:
- Owner skill: dispatch
- Current status: created | active | review-ready | blocked | merge-ready | merged | archived | abandoned
- State event ref:
- Created at:
- Last checked at:

Lifecycle:
- Current state: package_admitted | child_thread_created | prompt_delivered | running | review_package_returned | needs_remediation | blocked
- Archive ready: false
- Archive blockers:
- Closeout recommendation: clean_review_pending | needs_remediation | blocked | human_decision
- Lifecycle recommendation: clean_review | needs_remediation | blocked | human_decision
- Lifecycle evidence:

Merge-back evidence:
- Merge source available: worktree_path | patch_bundle | branch_or_head | unavailable | not_applicable
- Merge source:
- Merge source evidence:
- Reliable source: yes | no | unknown
- Applied to main worktree: yes | no | not_attempted | unknown
- Changed pathspecs:
- Validation after merge: pass | fail | skipped | unverified | not_applicable
- Merge-back blockers:

Branch cleanup evidence:
- Branch detected: yes | no | unknown
- Branch name:
- Branch identity evidence:
- Cleanup recommendation: delete_local | delete_remote | retain | human_decision | no_branch_detected | not_applicable
- Cleanup approval required: yes | no
- Cleanup approval evidence:
- Cleanup completed: yes | no | not_attempted | unknown
- Cleanup evidence:

Clean review handoff:
- Clean review required: yes | no
- Suggested reviewer context: fresh | not_required | unknown
- Clean review status: pending | not_required
- Clean review evidence:

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

Goal Mode evidence:
- Goal Mode required: yes | no
- Goal command first line: yes | no | unknown
- Lint passed before delivery: yes | no | unknown
- Runtime Goal Mode evidence: present | absent | unavailable | unknown
- Evidence:
- Failure action: none | corrective_resend | blocked | needs_remediation

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

When Goal Mode is required, missing runtime Goal Mode evidence means the review package status must be `blocked` or `needs_remediation`, not `ready_for_review`.

`review_package_returned` or an equivalent child status is not archive-ready evidence. Archive readiness is a coordinator closeout decision after clean review and merge/discard/block evidence.

Registry fields must match the lifecycle state and must point to the artifact/log event that recorded the latest status transition. If the child cannot name the base ref, artifact path, or event evidence, closeout must route to `blocked`, `needs_remediation`, or `human_decision`.

Do not claim merge-back completed, main-worktree application, or post-merge validation unless the merge source is reliable and the package includes evidence for the applied change.

Do not claim branch cleanup completed unless the branch identity, required approval, and cleanup evidence are present. If branch identity or approval is uncertain, recommend `human_decision` or `blocked`.

Child implementation threads must not mark clean review as passed. Use `pending` unless a separate fresh clean reviewer has already supplied clean-review evidence. A valid `low_risk_coordinator_intake` exception belongs under `review_loop.status = low_risk_coordinator_intake`; it is not clean-review evidence and must not set clean review to passed.

Child implementation packages must not recommend `merge_back`, `branch_cleanup`, or `retain` as direct lifecycle actions. Those are coordinator-only downstream decisions after clean-review evidence and lifecycle closeout evidence exist.

Older v0.3.2 review packages remain readable when these v0.3.3 fields are absent. If lifecycle closeout is requested and runtime identity, Goal Mode, merge source, branch info, lifecycle recommendation, or clean-review evidence is missing, route to `needs_remediation`, `blocked`, or `human_decision`.
