# Managed Worktree Merge-back Protocol

Target Reader: Groundwork coordinators, dispatch maintainers, and reviewers applying accepted child worktree changes back into the main worktree.
Reader Action Needed: Confirm clean-review evidence, choose a reliable merge-back source, apply only scoped changes, and preserve evidence for validation, remediation, or human decision.
Decision Supported: Whether managed worktree changes can be merged back automatically, need remediation, need a rebase or merge plan, or must stop for manual review only.
Scope: Local merge-back from one clean-reviewed accepted `codex_app_managed_worktree_thread` child result into the coordinator's main worktree.
Out of Scope: Public skills, remote push, PR creation, issue closeout, branch deletion, archive execution, release readiness, UAT readiness, and manual rewrite from prose.
Evidence Level: PRD v0.3.3 FR-4, Groundwork git-boundary rules, and managed worktree lifecycle package contracts.

## Required Package Shape

```yaml
merge_back:
  runtime_correlation_id: ""
  task_id: ""
  source:
    base_branch: ""
    base_commit: ""
    child_head_commit: ""
    child_branch: ""
    worktree_path: ""
    patch_bundle_path: ""
    patch_completeness: complete | redacted_complete | redacted_partial | unavailable

  strategy:
    selected: codex_checkout | git_apply_patch | git_merge_branch | git_checkout_pathspec | manual_review_only
    reason: ""
    approval_required: true | false

  preconditions:
    clean_review_passed: true | false
    clean_review_evidence: ""
    main_worktree_status_checked: true | false
    main_worktree_clean_enough: true | false | unknown
    base_matches: true | false | unknown
    base_refresh_required: true | false
    base_refresh_completed: true | false | not_required
    intended_pathspecs: []
    denylist_checked: true | false
    conflicts_expected: true | false | unknown

  dependency_barrier:
    dependent_task_ids: []
    blocked_until:
      merge_back: completed | not_required
      base_refresh: completed | not_required
    dependent_write_dispatch_allowed: true | false
    release_evidence: ""

  result:
    attempted: true | false
    applied: true | false | not_attempted
    conflicts_detected: true | false | unknown
    validation_required: true | false
    evidence: ""
    preserve_child_thread: true | false
    preserve_child_worktree: true | false
    next_route: verify | remediation_original_child_thread | blocked | human_decision
```

## Clean Review Gate

Merge-back may start only after fresh clean-review evidence is recorded and the merge-back package records `clean_review_passed: true` with `clean_review_evidence`.

- `review_package_returned` is only an intake state and does not permit merge-back.
- Child self-review does not permit merge-back.
- Fresh clean review is the default evidence source.
- `low_risk_coordinator_intake` is not clean-review evidence and does not permit merge-back. It may close coordinator intake only when it satisfies `skills/_shared/LOW-RISK-COORDINATOR-INTAKE.md`; it must not set `clean_review_passed: true`.
- Coordinator intake without fresh clean-review evidence does not permit merge-back.
- A child implementation thread must not output or claim `review_passed`; only the coordinator or clean reviewer may record clean-review pass evidence before the merge barrier.
- If clean review fails or is missing, set `result.attempted: false`, `result.applied: not_attempted`, preserve the original child thread and child worktree, and route to `remediation_original_child_thread` when the fix remains in scope. Route to `blocked` or `human_decision` only when remediation cannot proceed without missing source truth, approval, or a human merge decision.

## Strategy Priority

Use the first strategy whose source is complete, whose preconditions are proven, and whose risk gate is satisfied:

1. `codex_checkout`: Codex App checkout or apply-changes operation into the local main worktree, when the runtime supports it and evidence names the applied source, target worktree, and changed pathspecs.
2. `git_apply_patch`: complete patch bundle from the child worktree, applied with explicit pathspec review and three-way support when safe.
3. `git_checkout_pathspec`: visible child branch or head commit, checked out by explicit pathspec only after base and conflict preconditions are checked.
4. `git_merge_branch`: visible child branch merged only when the entire child branch is already scope-contained, clean review confirms no unrelated changes exist, and full-branch merge risk is explicitly accepted. Git merge does not accept pathspec operands, so this strategy must not be described or executed as a pathspec-limited merge.
5. `manual_review_only`: review-only fallback when no reliable merge source exists. This is not a merge strategy and must not produce main-worktree file changes.

Do not skip to a lower-priority strategy unless the package records why each higher-priority strategy is unavailable or unsafe.

## Source Completeness Rules

- `patch_completeness: redacted_partial` is not mergeable.
- `patch_completeness: unavailable` is not mergeable.
- `patch_completeness: redacted_complete` may support review, but it is not an apply source when redaction changes exact file bytes. It requires a separate complete patch bundle, child worktree path, branch, or head commit before merge-back can apply changes.
- Review package prose, summaries, acceptance maps, screenshots, terminal excerpts, or narrative descriptions must not be used to rewrite changes manually into the main worktree.
- If no reliable source exists, set `strategy.selected: manual_review_only`, `result.applied: not_attempted`, and route to `human_decision` or `blocked`.

## Git Boundary Requirements

Merge-back that changes files in the main worktree must follow `skills/_shared/GIT-BOUNDARY.md`.

Before applying changes, collect and record:

```text
git status --short
Intended file allowlist:
Explicit denylist:
git diff --name-only
git diff --cached --name-only
```

Required behavior:

- Use explicit pathspecs for checkout, apply review, and any later staging.
- Never recommend, approve, or run `git add .` for merge-back.
- Keep unrelated modified, untracked, ignored, runtime, `.groundwork/*`, `.trellis/*`, `refer/*`, dependency, lock, secret, log, and production-data files out of the merge-back boundary.
- Stop if intended pathspecs are empty, overbroad, conflict with the denylist, or do not match the accepted child task.
- Preserve child source evidence and main-worktree changed pathspecs in the merge-back package.

## Base And Conflict Rules

- `base_matches: false` blocks automatic merge-back.
- `base_matches: unknown` blocks automatic merge-back unless a human explicitly accepts a rebase or merge plan.
- A base mismatch routes to `blocked` with the original child thread and child worktree preserved until a human decision or documented rebase/merge plan exists. Do not silently apply child changes onto a different base.
- Expected conflicts require a plan before apply. Unexpected conflicts stop the merge-back, preserve the original child thread and child worktree, and route to `remediation_original_child_thread` when a scoped child-side fix is possible; otherwise route to `blocked` or `human_decision`.
- If the main worktree is not clean enough for the intended pathspecs, stop before apply, preserve the original child thread and child worktree, and report unrelated dirty files instead of mixing scopes.
- If conflicts or dirty-base conditions cannot be resolved automatically within the accepted scope, keep the child worktree atomic and route to `remediation_original_child_thread` when a scoped child-side fix is possible; otherwise route to `blocked` or `human_decision` with preserved evidence.

## Dependency Barrier Release

Dependent write tasks must remain blocked until prerequisite merge-back and base refresh are both complete.

Use `dependency_barrier.blocked_until` to record the release condition:

```yaml
dependency_barrier:
  dependent_task_ids: []
  blocked_until:
    merge_back: completed | not_required
    base_refresh: completed | not_required
  dependent_write_dispatch_allowed: true | false
  release_evidence: ""
```

Release dependent write dispatch only when:

- prerequisite merge-back has `result.applied: true`;
- base refresh has `base_refresh_completed: true` or `not_required`;
- dependent task source truth, Goal Contract, and intended base have been regenerated or confirmed against the post-merge base;
- `dependent_write_dispatch_allowed: true` includes release evidence naming the post-merge base.

Read-only preparation for dependent tasks may continue before release only when it does not treat unmerged child work as source truth. If merge-back or base refresh status is unknown, dependent write dispatch remains blocked.

## Validation Rule

After successful merge-back, run the fastest relevant validation for the accepted task. If validation cannot run, set:

```yaml
validation_required: true
evidence: "unverified: <reason>"
next_route: verify
```

Do not report `merged_to_main_worktree` without either validation evidence or an explicit unverified marker.

If validation fails after merge-back, preserve the original child thread and child worktree until the coordinator decides whether to remediate in the original child thread, create a scoped follow-up, revert the merge-back, or route to human decision. Failed validation must not be treated as archive-ready closeout.
