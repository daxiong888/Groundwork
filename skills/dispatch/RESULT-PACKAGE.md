# Result Package

## Target Reader

Groundwork verify/triage/handoff users, dispatch reviewers, and runtime adapters returning work to a coordinator.

## Reader Action Needed

Wrap runtime output before claiming a task is ready for review, needs remediation, is blocked, or can move to the next route.

## Decision Supported

Whether output is a review package, findings package, diagnosis package, direct result, or reviewer findings, and which Groundwork route owns the next step.

## Scope

Unified result envelope and runtime-specific output requirements. Runtime execution mechanics are out of scope.

## Out of Scope

Runtime execution, clean-review approval, UAT/release readiness, remote writes, tracker mutation, and selector enforcement without adapter evidence.

## Evidence Level

Derived from dispatch contracts, managed worktree package rules, and runtime result envelope requirements.

## Unified Envelope

```yaml
result_package:
  task_id: ""
  runtime_id: ""
  status: ready_for_review | needs_remediation | blocked | no_execution_needed | no_worktree_needed
  output_type: review_package | findings_package | diagnosis_package | direct_result | review_findings
  runtime_identity: {runtime_correlation_id, dispatch_id, task_id, parent_thread_identifier, child_thread_identifier, initial_thread_title, current_thread_title, title_mutation_detected}
  goal_mode: {required, goal_command_first_line, lint_passed_before_delivery, runtime_goal_mode_evidence, evidence, failure_action}
  lifecycle: {current_state, archive_ready, archive_blockers, next_lifecycle_route}
  merge_back: {source_available, source_evidence, reliable_source, applied_to_main_worktree, changed_pathspecs, validation_after_merge, evidence}
  branch_cleanup: {branch_detected, branch_name, cleanup_recommendation, approval_required, approval_evidence, cleanup_completed, evidence}
  clean_review: {required, reviewer_context, status, findings, evidence}
  task: {title, task_type, goal_contract_used, source_truth}
  runtime: {adapter, execution_profile_requested, execution_profile_actual, selector_enforcement}
  changes: {changed_files, diff_summary, diff_or_findings_completeness}
  validation: {applicability, commands_run, results, checks_not_run, evidence}
  findings: {summary, details, citations_or_paths}
  risk: {remaining_risks, blockers, recommended_next_route}
```

## Selector Enforcement

`selector_enforcement` is evidence, not an assumption. Use `tool_enforced` only when the runtime adapter confirms selectors were applied. Use `prompt_preference`, `unavailable`, or `unknown` otherwise. Dispatch Package content alone cannot prove enforcement.

## Runtime Output Requirements

| Runtime | Output Type | Required Evidence | Must Not Claim |
| --- | --- | --- | --- |
| `codex_app_managed_worktree_thread` | `review_package` | accepted write task, worktree isolation, Goal Contract, source package, verification package, correlation id, changed files, diff summary, validation, lifecycle/merge/branch/clean-review fields when closeout may follow | read-only/planning/hybrid pre-split execution, missing Goal Contract/source/validation, thread/worktree/validation/selector/merge/cleanup evidence not returned by adapter |
| `codex_subagent` | `findings_package` or `diagnosis_package` | role/lens, package id, inspected evidence, findings/diagnosis, confidence/gaps, no-edit confirmation unless write execution was approved and evidenced, capability/approval status | `review_package`, execution/validation/review claims when only a package was generated, file edits without explicit approved support |
| `main_thread_direct` | `direct_result` | action/answer, files changed if any, validation or no-test reason, risks, next route | independent review, runtime isolation, selector enforcement |
| `main_thread_readonly` | `findings_package` | reviewed scope, evidence inspected, findings, no file edits | implementation or package execution |
| `clean_reviewer` | `review_findings` | supplied package scope, coverage covered/not covered, findings, missing evidence, no edits | final readiness, merge/archive/branch cleanup, runtime execution |

## Managed Worktree Rules

- Valid managed worktree results must correspond to a package with `task_type = write_implementation`, `readiness = ready_for_agent`, `isolation.filesystem = codex_managed_worktree`, Goal Contract, source package, validation package, and `expected_output = review_package`.
- Echo `runtime_identity.runtime_correlation_id`; thread titles are display-only. If title changes, preserve correlation id and set mutation evidence.
- Goal Mode evidence is required when requested; absent/unavailable/unknown Goal Mode evidence routes to `blocked` or `needs_remediation`, not `ready_for_review`.
- `pendingWorktreeId` alone is pending init, not child-thread/worktree success.
- `review_package_returned` is not archive-ready; archive readiness requires clean review plus merge/discard evidence or blocked-with-human-decision closeout. `archived` does not imply branch cleanup.
- Merge-back claims require reliable source, applied-to-main evidence, changed pathspecs, and validation status.
- Branch cleanup completion requires branch identity, approval where needed, and cleanup evidence.
- `clean_review.status = passed` requires fresh independent review. Low-risk coordinator intake is recorded as `review_loop.status = low_risk_coordinator_intake`, not clean-review pass.

Older v0.3.2 result packages remain readable. If lifecycle closeout needs missing v0.3.3 fields, route to `needs_remediation`, `blocked`, or `human_decision` instead of inferring evidence.
