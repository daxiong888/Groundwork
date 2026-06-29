# Managed Worktree Result Package Template

## Target Reader

Runtime adapters returning managed worktree execution, rejection, or no-op evidence to Groundwork.

## Reader Action Needed

Wrap the adapter outcome in this package before Groundwork routes the task to `verify`, `triage`, `dispatch_write_task`, `human_decision`, or `done`.

## Decision Supported

Whether a managed worktree task is ready for review, needs remediation, is blocked, or intentionally did not create a worktree.

## Scope

Result wrapping for managed worktree execution, rejection, or no-op outcomes.

## Out of Scope

Runtime execution itself, clean-review approval, final readiness, remote writes, and selector enforcement claims without adapter evidence.

## Evidence Level

Derived from Groundwork unified Result Package requirements and managed worktree adapter status rules.

```yaml
result_package:
  task_id: ""
  runtime_id: "codex_app_managed_worktree_thread"
  status: "ready_for_review | needs_remediation | blocked | no_execution_needed | no_worktree_needed"
  output_type: "review_package"

  runtime_identity:
    runtime_correlation_id: ""
    dispatch_id: ""
    task_id: ""
    parent_thread_identifier: ""
    child_thread_identifier: ""
    initial_thread_title: ""
    current_thread_title: ""
    title_mutation_detected: "true | false | unknown"
    title_identity_rule: "thread title is display-only; runtime_correlation_id is source-of-truth identity"

  registry:
    base_ref: ""
    branch: ""
    worktree_path: ""
    artifact_path: ""
    owner_skill: "dispatch"
    current_status: "created | active | review-ready | blocked | merge-ready | merged | archived | abandoned"
    state_event_ref: ""
    created_at: ""
    last_checked_at: ""

  goal_mode:
    required: "true | false"
    goal_command_first_line: "true | false | unknown"
    lint_passed_before_delivery: "true | false | unknown"
    runtime_goal_mode_evidence: "present | absent | unavailable | unknown"
    evidence: ""
    failure_action: "none | corrective_resend | blocked | needs_remediation"

  lifecycle:
    current_state: "package_admitted | worktree_init_pending | child_thread_created | prompt_delivered | running | review_package_returned | clean_review_pending | clean_review_passed | needs_remediation | blocked | merge_pending | discard_pending | merged_to_main_worktree | discarded | archive_ready | archived | branch_cleanup_pending | branch_cleaned | branch_retained_with_reason | closed"
    archive_ready: "true | false | unknown"
    archive_blockers: []
    closeout_decision: "archive | retain | discard | blocked | human_decision | not_applicable"
    next_lifecycle_route: "clean_reviewer | merge_back | branch_cleanup | triage | verify | human_decision | done"

  merge_back:
    source_available: "worktree_path | patch_bundle | branch_or_head | unavailable | not_applicable"
    source_evidence: ""
    reliable_source: "true | false | unknown"
    applied_to_main_worktree: "true | false | not_attempted | unknown"
    changed_pathspecs: []
    validation_after_merge: "pass | fail | skipped | unverified | not_applicable"
    evidence: ""

  branch_cleanup:
    branch_detected: "true | false | unknown"
    branch_name: ""
    cleanup_recommendation: "delete_local | delete_remote | retain | human_decision | no_branch_detected | not_applicable"
    approval_required: "true | false"
    approval_evidence: ""
    cleanup_completed: "true | false | not_attempted | unknown"
    evidence: ""

  clean_review:
    required: "true | false"
    reviewer_context: "fresh | coordinator_intake | not_required | unknown"
    status: "pending | passed | failed | blocked | not_required"
    findings: []
    evidence: ""

  review_loop:
    status: "self_check_complete | clean_review_pending | clean_review_passed | needs_remediation | remediation_in_progress | remediation_self_check_complete | blocked | human_decision | low_risk_coordinator_intake"
    latest_material_change_id: ""
    previous_review_stale_reason: ""
    findings_addressed: []
    next_review_required: "true | false"
    next_route: "clean_reviewer | dispatch_write_task | verify | triage | human_decision | done"

  task:
    title: ""
    task_type: ""
    readiness: ""
    goal_contract_used: "true | false"
    source_truth: ""
    rejection_or_noop_reason: ""

  runtime:
    adapter: "codex_app_managed_worktree_thread"
    init_status: "not_started | pending | child_thread_created | failed | blocked"
    pending_worktree_id: ""
    thread_identifier: ""
    thread_title_display_label: ""
    worktree_type: "Codex-managed | none"
    worktree_path: ""
    execution_profile_requested: ""
    execution_profile_actual: ""
    selector_enforcement: "tool_enforced | prompt_preference | unavailable | unknown"
    selector_enforcement_evidence: ""

  changes:
    changed_files: []
    diff_summary: ""
    diff_or_findings_completeness: "complete | redacted_complete | redacted_partial | not_applicable"
    redacted_patch_or_detail: ""

  validation:
    applicability: "applicable | not_applicable"
    commands_run: []
    results: ""
    checks_not_run: ""
    evidence: ""

  review_package:
    status: "present | absent | not_applicable"
    summary: ""
    location_or_inline_package: ""
    completeness: "complete | incomplete | not_applicable"

  risk:
    remaining_risks: []
    blockers: []
    recommended_next_route: "verify | triage | dispatch_write_task | human_decision | done"
```

## Status Rules

- `ready_for_review`: an accepted managed worktree child thread completed and returned a complete review package with validation evidence, or validation is not applicable and the reason is reviewable. If Goal Mode is required, `goal_mode.runtime_goal_mode_evidence` must be `present`.
- `needs_remediation`: execution or review package evidence is incomplete, validation failed, or acceptance criteria are unmet but a scoped remediation path exists.
- `blocked`: missing input, missing required package fields, missing tools, unsafe state, unresolved conflict, missing approval, or unresolved product truth prevents progress.
- `no_execution_needed`: the package intentionally required no runtime execution.
- `no_worktree_needed`: the package is non-managed-runtime, read-only, planning-only, hybrid before split, or otherwise intentionally should not create a managed worktree.

Incomplete managed-runtime packages must use `blocked` or `needs_remediation`, not `no_worktree_needed`.

`goal_contract_used` must be `true` for accepted managed worktree execution results, including `ready_for_review` and post-execution `needs_remediation`. Use `false` only for rejection, no-op, or blocked-before-execution results, and explain the reason in `rejection_or_noop_reason` or `risk.blockers`.

When Goal Mode is required, `goal_mode.goal_command_first_line` and `goal_mode.lint_passed_before_delivery` must be `true` before delivery. If `goal_mode.runtime_goal_mode_evidence` is `absent`, `unavailable`, or `unknown`, the result status must be `blocked` or `needs_remediation`, never `ready_for_review`. Normal prompt execution is not acceptable replacement evidence for Goal Mode.

`runtime_identity.runtime_correlation_id` must be echoed from the dispatch package for managed worktree results. Thread title fields are display-only labels and must not be used as source-of-truth identity. If the visible title changed, preserve the same `runtime_correlation_id`, report the observed current title when available, and set `title_mutation_detected` to `true`.

`registry.current_status` must map to `THREAD-LIFECYCLE.md` and `registry.state_event_ref` must point to the artifact/log event for the latest status transition. If the adapter cannot name base ref, artifact path, or event evidence, use `blocked` or `needs_remediation` for lifecycle closeout decisions.

When Codex App returns `pendingWorktreeId` but no child thread identifier or worktree path, set `runtime.init_status = pending`, set `runtime.pending_worktree_id`, set `lifecycle.current_state = worktree_init_pending`, keep `changes.changed_files` empty, and route the result to wait/poll/resolve, `blocked`, or `human_decision`. Do not report `child_thread_created`, `ready_for_review`, merge-back, archive readiness, or parent-thread implementation evidence from a pending id alone.

For closeout, map `runtime.init_status = child_thread_created` to `init_resolution_status.status = resolved` with `resolution_source = codex_managed_worktree`. Map `runtime.init_status = pending` to `init_resolution_status.status = pending`; it must stay non-mergeable until resolved, failed, blocked, or routed to human decision. If a user explicitly accepts a fallback topology, the closeout package must use `resolution_source = approved_topology_change` and preserve approval plus merge source evidence.

`lifecycle.current_state` must reflect the adapter-visible lifecycle evidence for the result package. `review_package_returned` is not enough for `archive_ready`; archive readiness requires clean review plus merge/discard evidence or a blocked-with-human-decision closeout path, and `archived` does not imply branch cleanup.

`merge_back.applied_to_main_worktree = true`, `lifecycle.current_state = merged_to_main_worktree`, or any equivalent merge-back claim requires `merge_back.reliable_source = true`, a source path/patch/branch or head that the coordinator can inspect, and merge evidence. Missing or unreliable source evidence must route to `needs_remediation`, `blocked`, or `human_decision`.

`branch_cleanup.cleanup_completed = true`, `lifecycle.current_state = branch_cleaned`, or any equivalent cleanup claim requires branch identity, required approval, and cleanup evidence. Missing approval or uncertain branch identity must route to `human_decision` or `blocked`, not `done`.

`clean_review.status = passed` requires fresh clean-review evidence or a documented `coordinator_intake` decision that satisfies the low-risk exception in `skills/dispatch/CLEAN-REVIEW-FANOUT.md`. A child result package, `review_package_returned`, or self-review cannot make the package archive-ready.

`review_loop.status` must reflect the latest material change, not the oldest returned package state. If a clean-review finding was fixed after review, set `previous_review_stale_reason` and `next_review_required = true` until the latest diff receives fresh clean review or a valid low-risk coordinator-intake exception. `findings_addressed` lists only cited findings or accepted gap-closure items that were actually fixed and rechecked.

Older v0.3.2 packages without `runtime_identity`, `goal_mode`, `lifecycle`, `merge_back`, `branch_cleanup`, or `clean_review` remain readable. If lifecycle closeout requires any missing v0.3.3 field, use `needs_remediation`, `blocked`, or `human_decision` rather than inferring identity, Goal Mode, merge-back, cleanup, or clean-review evidence.

Do not claim thread creation, worktree creation, validation execution, selector tool enforcement, stage, commit, push, PR creation, issue close, archive, or remote mutation unless the adapter has evidence for that action.
