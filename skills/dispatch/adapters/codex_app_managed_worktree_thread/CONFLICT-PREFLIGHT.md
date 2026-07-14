# Managed Worktree Conflict Preflight

Target Reader: Groundwork dispatch users, coordinators, and managed worktree adapter reviewers deciding whether write tasks can run in parallel.
Reader Action Needed: Identify overlapping write surfaces, dependency barriers, base-refresh requirements, and release evidence before creating a managed worktree child thread.
Decision Supported: Whether a write task can dispatch now, must serialize behind prerequisite merge-back/base refresh, can proceed as read-only preparation only, or needs human approval.
Scope: Pre-dispatch conflict and dependency checks for tasks addressed to `codex_app_managed_worktree_thread`.
Out of Scope: Runtime execution, child thread creation, merge-back execution, branch cleanup, archive, commits, pushes, PRs, tracker mutation, release readiness, UAT readiness, and final acceptance.
Evidence Level: Derived from PRD v0.3.3 FR-8, Dispatch Package v2 dependency barriers, and the managed worktree merge-back protocol.

## Required Shape

```yaml
conflict_preflight:
  task_id: ""
  runtime_correlation_id: ""
  write_surface:
    intended_pathspecs: []
    shared_contracts: []
    generated_artifacts: []
    fixtures_or_eval_suites: []
    public_interfaces: []
    state_machines: []
  conflict_group: ""
  dependency_barrier:
    depends_on_task_ids: []
    blocked_until:
      result_outcome: ready_for_review | no_execution_needed | not_required
      review_status: passed | not_required
      merge_back_status: applied | discarded | not_required
      verification: pass | partial_allowed | not_required
      base_refresh: completed | not_required
    required_base:
      branch: ""
      commit_after_merge: ""
    re_triage_required_after_merge: true | false
    goal_contract_refresh_required: true | false
    dispatch_allowed_now: true | false
    block_reason: ""
    release_evidence: ""
  parallel_decision: parallel_allowed | serialize | read_only_preparation_only | human_decision | blocked
```

## Core Rules

- Conflict preflight runs before managed worktree child thread creation.
- Dependent write tasks must stay blocked until prerequisite merge-back and base refresh are complete.
- If dependency state is unknown, stale, or only present in an unmerged child worktree, choose `serialize`, `blocked`, or `human_decision`, not parallel write dispatch.
- Same-conflict-group write tasks must not run in parallel unless explicit approval or a merge-order plan serializes their write boundaries.
- Goal Contracts for dependent write tasks must be generated or refreshed after the prerequisite merge when the prerequisite changed source, contracts, fixtures, or generated artifacts.
- Read-only preparation may run before merge-back only when it does not assume unmerged code as source truth and cannot write files.
- Low-risk independent tasks remain parallelizable when they have no dependency barrier, no overlapping write surface, no shared conflict group, and current source truth.
- Worktree initialization preflight must still run after conflict preflight and before child thread creation. Conflict independence does not prove that a branch start state is valid.

## Worktree Start-State Interaction

Use conflict and dependency evidence to choose the safest worktree start state:

- When a write task depends on previous clean-reviewed coordinator worktree changes that are not committed, release the dependent task only with a `working-tree` start state or equivalent dirty-base inheritance evidence.
- When a package requests an `existing-branch` start state, confirm the branch already exists and that no dirty coordinator base must be inherited.
- If a requested branch is missing, unknown, stale, or used to bypass dirty-base inheritance, choose `blocked`, `needs_remediation`, or `human_decision` before child thread creation.
- Do not create a dependent child thread merely because a worktree request is queued. `pendingWorktreeId` is not release evidence.
- Do not treat `pendingWorktreeId` as permission to continue the same write task in the parent/coordinator thread. Until it resolves to a child thread id and worktree path, the coordinator must wait/poll/resolve or choose `blocked`/`human_decision`.
- Do not create a manual git worktree fallback to bypass a pending Codex App managed worktree. Such a fallback changes execution topology and requires explicit user approval before any implementation starts.

## Overlap Signals

Treat these as conflict or serialization signals:

- overlapping intended pathspecs;
- shared package schemas, adapter contracts, public interfaces, state machines, or generated artifacts;
- shared fixture, eval suite, route, migration, config, or lockfile surface;
- dependency on a prior task's changed source, tests, docs contract, result package shape, or merge-back protocol;
- same `conflict_group` without an explicit merge-order hint;
- unknown base, unknown merge-back state, unknown clean-review state, or unknown base-refresh state.
- unresolved `pendingWorktreeId` for the same task or runtime correlation id.

## Release Rules

Set `dependency_barrier.dispatch_allowed_now: true` only when:

- every prerequisite task has reached the required `blocked_until` states;
- prerequisite merge-back is complete or not required;
- base refresh is complete or not required;
- the dependent source package and Goal Contract were regenerated or confirmed against `required_base.commit_after_merge` when a prerequisite changed the base;
- `release_evidence` cites the prerequisite task, post-merge base, and refreshed/confirmed Goal Contract.

When those conditions are not met, keep write dispatch blocked. Do not create a managed worktree child thread for the dependent write task.

## Read-only Exception

Read-only preparation may route to `main_thread_readonly`, `codex_subagent`, or `clean_reviewer` while the write task remains blocked.

The read-only package must state:

- no file edits are allowed;
- unmerged child work is context only, not source truth;
- any findings must return to dispatch or triage before a write task is released.

## Reporting Rules

When reporting conflict preflight, include:

- `parallel_decision`;
- conflict group and overlapping write surface;
- dependency barrier status;
- blocked-until fields;
- base-refresh status;
- release evidence or block reason;
- whether read-only preparation is allowed while write dispatch remains blocked.

Do not report `parallel_allowed` merely because tasks are in separate child threads. Parallel write dispatch requires independent source truth, independent write surfaces, and no unmet dependency barrier.
