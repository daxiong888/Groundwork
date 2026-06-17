# Managed Worktree Closeout Package Template

## Target Reader

Groundwork coordinators, runtime adapter authors, clean reviewers, and maintainers deciding whether a managed worktree child thread can be archived or must remain available.

## Reader Action Needed

Fill this package after review/result package intake and before any thread archive recommendation or closeout decision.

## Decision Supported

Whether the managed worktree child thread should be archived, retained, discarded, blocked for human decision, or routed to branch cleanup, triage, verify, done, or human decision.

## Scope

Closeout evidence for one `codex_app_managed_worktree_thread` task after runtime result intake.

## Out of Scope

Branch deletion, automatic archive execution, remote writes, commits, pushes, PR creation, tracker mutation, release readiness, UAT readiness, and final acceptance.

## Evidence Level

Derived from PRD v0.3.3 FR-2, the managed worktree lifecycle protocol, and Groundwork result/review package boundaries.

## Creation Rule

Create the closeout package after review/result package intake, not before. A closeout package may recommend archive, but it must not claim archive occurred unless adapter/runtime evidence proves it.

## Required Shape

```yaml
closeout_package:
  runtime_correlation_id: ""
  task_id: ""
  runtime_id: "codex_app_managed_worktree_thread"

  lifecycle:
    current_state: ""
    closeout_decision: "archive | retain | discard | blocked | human_decision"
    closeout_reason: ""
    archive_ready: "true | false"
    archive_blockers: []
    preserved_evidence:
      review_package: "present | absent | incomplete"
      result_package: "present | absent | incomplete"
      clean_review: "passed | failed | not_run | not_applicable"
      merge_back: "completed | not_attempted | failed | not_applicable"

  runtime:
    thread_identifier: ""
    initial_thread_title: ""
    current_thread_title: ""
    worktree_type: "Codex-managed | none | unknown"
    worktree_path: ""

  approval:
    archive_approval_required: "true | false"
    archive_approval_status: "approved | not_requested | rejected | not_required"
    reason: ""

  next:
    branch_cleanup_required: "true | false | unknown"
    recommended_next_route: "branch_cleanup | triage | verify | done | human_decision"
```

## Field Rules

- `runtime_correlation_id` is the stable runtime identity. Thread title is display-only and must not be used as the source-of-truth identifier.
- `current_state` must be one lifecycle state from `THREAD-LIFECYCLE.md`.
- `closeout_decision = archive` requires `archive_ready: true`.
- `closeout_decision = retain` keeps the child thread or worktree available for review, remediation, merge-back, or human inspection.
- `closeout_decision = discard` means child work is intentionally not merged and the discard reason is recorded.
- `closeout_decision = blocked` means closeout cannot proceed because required evidence, approval, or source truth is missing.
- `closeout_decision = human_decision` means the next step depends on an explicit human choice.
- `archive_approval_required` is `true` when archive execution is not already explicitly approved by the user or adapter policy.
- `branch_cleanup_required` is separate from archive readiness and remains `unknown` when branch state is not proven.

## Archive Readiness Rules

`archive_ready: true` is allowed only after one of:

- merge-back completed and evidence is preserved;
- discard decision completed with reason and preserved review/result evidence;
- blocked state has preserved review/result evidence and a human decision that worktree retention is not needed.

These states must keep `archive_ready: false`:

- `review_package_returned` without clean review and merge/discard/blocked-with-human-decision evidence;
- `clean_review_pending`;
- `needs_remediation` unless remediation is moved to a new task and this child worktree is intentionally discarded;
- `merge_pending`;
- `discard_pending`;
- `blocked` without preserved evidence or human decision.

## Preservation Requirements

Before archive recommendation, the package must state:

- whether the review package is present, absent, or incomplete;
- whether the result package is present, absent, or incomplete;
- whether clean review passed, failed, was not run, or is not applicable;
- whether merge-back completed, failed, was not attempted, or is not applicable;
- why any missing evidence does not block closeout, or the blocker that prevents closeout.

## Archive And Branch Cleanup Boundary

Archive and branch cleanup are separate decisions:

- `archive_ready: true` does not mean a branch can be deleted.
- `archived` does not imply `branch_cleaned`.
- unknown branch state must route to `branch_cleanup` or `human_decision`, not `done`.
- remote branch deletion, force deletion, protected/default branch handling, and unknown branch state require the later branch cleanup checklist and approval rules.

## Later Eval Hooks

Future closeout evals should reject:

- archive recommendations without preserved review/result evidence;
- archive recommendations before merge-back, discard, or blocked-with-human-decision evidence;
- packages that treat thread archive as branch cleanup;
- packages that claim archive occurred without adapter/runtime evidence;
- `recommended_next_route: done` when branch cleanup is required or unknown.
