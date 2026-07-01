# Managed Worktree Result Package Template

## Target Reader

Runtime adapters returning managed worktree execution, rejection, or no-op evidence to Groundwork.

## Reader Action Needed

Wrap adapter outcome before Groundwork routes to `verify`, `triage`, `dispatch_write_task`, `human_decision`, or `done`.

## Decision Supported

Whether a managed worktree task is ready for review, needs remediation, is blocked, or intentionally did not create a worktree.

## Scope

Result wrapping for managed worktree execution, rejection, or no-op outcomes.

## Out of Scope

Runtime execution itself, clean-review approval, final readiness, remote writes, selector enforcement without adapter evidence, cache refresh, release readiness, and UAT readiness.

## Evidence Level

Derived from Groundwork unified Result Package requirements and managed worktree adapter status rules.

## Required Shape

```yaml
result_package:
  task_id: ""
  runtime_id: codex_app_managed_worktree_thread
  status: ready_for_review | needs_remediation | blocked | no_execution_needed | no_worktree_needed
  output_type: review_package
  runtime_identity: {runtime_correlation_id, dispatch_id, task_id, parent_thread_identifier, child_thread_identifier, initial_thread_title, current_thread_title, title_mutation_detected}
  registry: {base_ref, branch, worktree_path, artifact_path, owner_skill: dispatch, current_status, state_event_ref, created_at, last_checked_at}
  goal_mode: {required, goal_command_first_line, lint_passed_before_delivery, runtime_goal_mode_evidence, evidence, failure_action}
  lifecycle: {current_state, archive_ready, archive_blockers, closeout_decision, next_lifecycle_route}
  merge_back: {source_available, source_evidence, reliable_source, applied_to_main_worktree, changed_pathspecs, validation_after_merge, evidence}
  branch_cleanup: {branch_detected, branch_name, cleanup_recommendation, approval_required, approval_evidence, cleanup_completed, evidence}
  clean_review: {required, reviewer_context, status, findings, evidence}
  review_loop: {status, latest_material_change_id, previous_review_stale_reason, findings_addressed, next_review_required, next_route}
  task: {title, task_type, readiness, goal_contract_used, source_truth, rejection_or_noop_reason}
  runtime: {adapter, init_status, pending_worktree_id, thread_identifier, thread_title_display_label, worktree_type, worktree_path, execution_profile_requested, execution_profile_actual, selector_enforcement, selector_enforcement_evidence}
  changes: {changed_files, diff_summary, diff_or_findings_completeness, redacted_patch_or_detail}
  validation: {applicability, commands_run, results, checks_not_run, evidence}
  review_package: {status, summary, location_or_inline_package, completeness}
  risk: {remaining_risks, blockers, recommended_next_route}
```

## Status Rules

- `ready_for_review`: accepted managed worktree child completed and returned a complete review package with validation evidence or a reviewable not-applicable reason. Required Goal Mode evidence must be `present`.
- `needs_remediation`: execution/review package incomplete, validation failed, ACs unmet, or scoped remediation exists.
- `blocked`: missing input, required fields, tools, safe state, approval, conflict resolution, or product truth prevents progress.
- `no_execution_needed`: package intentionally required no runtime execution.
- `no_worktree_needed`: non-managed-runtime, read-only, planning-only, unsplit hybrid, or otherwise intentionally no managed worktree.

Incomplete managed-runtime packages use `blocked` or `needs_remediation`, not `no_worktree_needed`.

## Evidence Rules

- `goal_contract_used` is `true` for accepted managed worktree execution results, including post-execution remediation. Use `false` only for rejection/no-op/blocked-before-execution and explain why.
- Required Goal Mode needs first-line goal command, pre-delivery lint, and runtime Goal Mode evidence. Missing Goal Mode evidence blocks `ready_for_review`.
- `runtime_identity.runtime_correlation_id` is source-of-truth identity. Thread titles are display labels only; title changes keep the same correlation id and set mutation evidence.
- `registry.current_status` maps to `THREAD-LIFECYCLE.md`; `state_event_ref` points to latest event evidence. Missing base/artifact/event evidence blocks lifecycle closeout.
- `pendingWorktreeId` without child thread id and worktree path means `runtime.init_status: pending`, `lifecycle.current_state: worktree_init_pending`, no changed files, and route to wait/poll/resolve, `blocked`, or `human_decision`.
- Closeout maps `child_thread_created` to resolved Codex-managed worktree evidence and `pending` to non-mergeable pending state. Approved fallback topology requires explicit approval and merge-source evidence.
- `review_package_returned` is not enough for archive readiness; `archived` does not imply branch cleanup.
- Merge-back claims require reliable source, inspectable source path/patch/branch/head, changed pathspecs, and merge evidence.
- Branch cleanup completion requires branch identity, approval where required, and cleanup evidence.
- `clean_review.status: passed` requires fresh independent review. Low-risk coordinator intake is recorded under `review_loop.status`, not as clean review passed.
- Review-loop status reflects the latest material change; fixes after review make previous review stale until fresh review or valid low-risk intake.

Older v0.3.2 packages remain readable, but missing v0.3.3 identity, Goal Mode, lifecycle, merge-back, branch cleanup, or clean-review fields route to `needs_remediation`, `blocked`, or `human_decision` instead of inferred evidence.

Do not claim thread/worktree creation, validation execution, selector tool enforcement, stage, commit, push, PR creation, issue close, archive, cleanup, cache refresh, release readiness, UAT readiness, or remote mutation unless adapter evidence proves it.
