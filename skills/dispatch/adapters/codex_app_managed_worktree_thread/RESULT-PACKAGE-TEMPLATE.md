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

  task:
    title: ""
    task_type: ""
    readiness: ""
    goal_contract_used: "true | false"
    source_truth: ""
    rejection_or_noop_reason: ""

  runtime:
    adapter: "codex_app_managed_worktree_thread"
    thread_identifier: ""
    thread_title: ""
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

- `ready_for_review`: an accepted managed worktree child thread completed and returned a complete review package with validation evidence, or validation is not applicable and the reason is reviewable.
- `needs_remediation`: execution or review package evidence is incomplete, validation failed, or acceptance criteria are unmet but a scoped remediation path exists.
- `blocked`: missing input, missing required package fields, missing tools, unsafe state, unresolved conflict, missing approval, or unresolved product truth prevents progress.
- `no_execution_needed`: the package intentionally required no runtime execution.
- `no_worktree_needed`: the package is non-managed-runtime, read-only, planning-only, hybrid before split, or otherwise intentionally should not create a managed worktree.

Incomplete managed-runtime packages must use `blocked` or `needs_remediation`, not `no_worktree_needed`.

`goal_contract_used` must be `true` for accepted managed worktree execution results, including `ready_for_review` and post-execution `needs_remediation`. Use `false` only for rejection, no-op, or blocked-before-execution results, and explain the reason in `rejection_or_noop_reason` or `risk.blockers`.

Do not claim thread creation, worktree creation, validation execution, selector tool enforcement, stage, commit, push, PR creation, issue close, archive, or remote mutation unless the adapter has evidence for that action.
