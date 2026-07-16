# Managed Worktree Result Package Template

Target Reader: Runtime adapters returning managed worktree execution, rejection, or no-op evidence to Groundwork.

Reader Action Needed: Wrap adapter outcome before Groundwork routes to `verify`, `triage`, `dispatch_write_task`, `human_decision`, or `done`.

Decision Supported: Whether a managed worktree task is ready for review, needs remediation, is blocked, or intentionally did not create a worktree.

Scope: Result wrapping for managed worktree execution, rejection, or no-op outcomes.

Out of Scope: Runtime execution itself, clean-review approval, final readiness, remote writes, selector enforcement without adapter evidence, cache refresh, release readiness, and UAT readiness.

Evidence Level: Derived from Groundwork unified Result Package requirements and managed worktree adapter outcome rules.

## Base Contract And Adapter Delta

Start with the complete envelope in `../../RESULT-PACKAGE.md`. This template does not redefine `outcome` or the generic task, runtime, lifecycle, review, review-loop, merge-back, archive, branch-cleanup, changes, validation, findings, or risk fields.

For this adapter, set base `runtime_id: codex_app_managed_worktree_thread`, `output_type: review_package`, and use `THREAD-LIFECYCLE.md` states in `runtime_lifecycle.state`.

Add only the managed-worktree evidence delta:

```yaml
adapter_extension:
  codex_app_managed_worktree_thread:
    runtime_identity:
      parent_thread_identifier: ""
      child_thread_identifier: ""
      initial_thread_title: ""
      current_thread_title: ""
      title_mutation_detected: true | false | unknown
    worktree_init: {status, pending_worktree_id, resolution_source, evidence}
    registry: {base_ref, branch, worktree_path, artifact_path, owner_skill: dispatch, thread_status, state_event_ref, created_at, last_checked_at}
    review_package: {summary, location_or_inline_package, completeness}
    merge_source: {source_available, source_evidence, reliable_source}
    selector_enforcement_evidence: ""
```

Do not copy generic Result Package fields into this object. Adapter identity extends, but never replaces, the base `runtime_identity.runtime_correlation_id`.

## Adapter Outcome Mapping

Use the canonical outcomes and meanings from `../../RESULT-PACKAGE.md`. Adapter-specific constraints are: `ready_for_review` requires a complete review package plus required Goal Mode evidence; `no_execution_needed` requires a preserved non-admission/no-op reason; and incomplete executable packages use `blocked` or `needs_remediation`.

## Evidence Rules

- `goal_contract_used` is `true` for accepted managed worktree execution results, including post-execution remediation. Use `false` only for rejection/no-op/blocked-before-execution and explain why.
- Required Goal Mode needs first-line goal command, pre-delivery lint, and runtime Goal Mode evidence. Missing Goal Mode evidence blocks `ready_for_review`.
- Base `runtime_identity.runtime_correlation_id` is source-of-truth identity. Thread titles are display labels only; title changes keep the same correlation id and set mutation evidence in the delta.
- `registry.thread_status` maps only to `THREAD-LIFECYCLE.md`; `state_event_ref` points to the latest thread event. It must not carry review, merge, archive, or branch-cleanup status.
- `pendingWorktreeId` without child thread id and worktree path means `runtime_lifecycle.status: pending`, `runtime_lifecycle.state: worktree_init_pending`, no changed files, and route to wait/poll/resolve, `blocked`, or `human_decision`.
- Closeout maps `child_thread_created` to resolved Codex-managed worktree evidence and `pending` to non-mergeable pending state. Approved fallback topology requires explicit approval and merge-source evidence.
- `runtime_lifecycle.status: result_returned` is not review pass, merge, or archive readiness; `archived` does not imply branch cleanup.
- Merge-back claims require reliable source, inspectable source path/patch/branch/head, changed pathspecs, and merge evidence.
- Branch cleanup completion requires branch identity, approval where required, and cleanup evidence.
- `review.kind: clean` with `review.status: passed` requires fresh independent review. Low-risk coordinator intake is recorded in the base `review_loop` and base review axis as coordinator intake, not clean-review pass.
- Base `review.reviewed_material_change_id` carries the reviewed snapshot and must equal base `review_loop.latest_material_change_id` for a clean-review pass; this adapter must not duplicate either field in its delta.
- Base `review_loop.status` reflects the latest material change; fixes after review make previous review stale until fresh review or valid low-risk intake.

Older v0.3.2 packages remain readable, but missing v0.3.3 identity, Goal Mode, lifecycle, merge-back, branch cleanup, or clean-review fields route to `needs_remediation`, `blocked`, or `human_decision` instead of inferred evidence.

Do not claim thread/worktree creation, validation execution, selector tool enforcement, stage, commit, push, PR creation, issue close, archive, cleanup, cache refresh, release readiness, UAT readiness, or remote mutation unless adapter evidence proves it.
