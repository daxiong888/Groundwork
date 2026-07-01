# Dispatch Examples

Target Reader: Groundwork dispatch users and reviewers who need concrete package examples after choosing an active dispatch branch.
Reader Action Needed: Load only when an example package is useful; otherwise use `SKILL.md` and `DISPATCH-PACKAGE.md`.
Decision Supported: How read-only review, hybrid diagnosis, and managed worktree examples express the dispatch contract without claiming execution.
Artifact Type: branch-specific examples
Source of Truth: `skills/dispatch/SKILL.md` progressive-disclosure boundary and `skills/dispatch/DISPATCH-PACKAGE.md`.
Scope: Compact examples for common routing branches.
Out of Scope: Runtime execution, package schema ownership, Codex App thread creation, subagent spawning, remote mutation, release readiness, UAT readiness, or installed-plugin cache evidence.
Evidence Level: Source-validation examples only.
Safe to Share / Redaction Notes: Safe to share as-is; contains no secrets, credentials, PII, private logs, or production payloads.

## Runtime Package Examples

Read-only review packages must not default to a managed worktree:

```yaml
tasks:
  - task_id: review-api-contract
    task_type: read_only_review
    readiness: ready_for_agent
    runtime_id: codex_subagent
    runtime_reason: Independent read-only review; no file edits.
    dispatch_native_alignment:
      route_decision:
        route: worktree_review_only
        why_not_worktree: Read-only review is forbidden from worktree_isolated.
        expected_touched_files: []
    isolation: {context: subagent_prompt, filesystem: none, diff_surface: not_required}
    runtime_package: {adapter: codex_subagent, expected_output: findings_package, can_write_files: false}
```

Hybrid work must split diagnosis from write work before a write package exists:

```yaml
tasks:
  - task_id: diagnose-router-regression
    task_type: hybrid
    readiness: needs_split
    runtime_id: main_thread_readonly
    runtime_reason: Inspect evidence first; return a concrete write slice or no-change finding.
    dispatch_native_alignment:
      route_decision:
        route: local_with_artifact
        why_not_worktree: No concrete write subtask exists yet.
        expected_touched_files: []
    runtime_package: {adapter: main_thread_readonly, expected_output: diagnosis_package, can_write_files: false}
```

Managed worktree packages are valid only for ready write implementation with native source, route, handoff, closeout, verification, approval, runtime-evidence, Goal Contract, and legacy compatibility fields:

```yaml
tasks:
  - task_id: issue-4a
    title: Update managed worktree runtime identity contract
    task_type: write_implementation
    readiness: ready_for_agent
    runtime_id: codex_app_managed_worktree_thread
    runtime_reason: Accepted write task needs isolated diff review.
    dispatch_native_alignment:
      route_decision:
        route: worktree_isolated
        why_worktree_if_selected: Shared dispatch contract files need clean diff boundaries.
        expected_touched_files:
          - skills/dispatch/DISPATCH-PACKAGE.md
          - skills/dispatch/RESULT-PACKAGE.md
        workspace_state: {status_checked: true, dirty_files: [], staged_files: []}
        base_state: {base_ref: main, base_stale: false, base_refresh_required: false}
        conflict: {conflict_group: managed-worktree-runtime-identity, shared_files: [skills/dispatch/DISPATCH-PACKAGE.md], serial_dependency: none}
      source_package: {known_source_or_first_inspection_step: Read dispatch package contracts before editing., redactions_applied: none}
      policy: {remote_writes_allowed: false, destructive_actions_allowed: false, approval_required: false}
      handoff_expected: {required: true, direction: local_to_worktree, package_ref: native_handoff_package}
      closeout_expected: {required: true, package_ref: native_closeout_package, merge_gate: evidence_git_boundary_review_and_merge_source_required}
      verification_expectation: {fastest_signal: present, required_evidence: present, release_readiness_claimed: false}
      runtime_evidence: {evidence_owner: adapter, worktree_creation_claimed: false, runtime_success_claimed: false}
    isolation: {context: thread, filesystem: codex_managed_worktree, diff_surface: required}
    goal_contract:
      goal_command: /goal Add stable runtime identity fields to the managed worktree dispatch package templates
      outcome: present
      source_truth: present
      acceptance_criteria_mapping: present
      verification: present
      stop_when: present
      result_package_expected: review_package
    runtime_package: {adapter: codex_app_managed_worktree_thread, expected_output: review_package, can_write_files: true}
    legacy_compatibility:
      status: deprecated_in_place_for_v0_3_3_compatibility
      runtime_identity: {runtime_correlation_id: present, task_id: issue-4a, title_mutation_detected: unknown}
```

Example hard negatives:

- Do not route `read_only_review`, `planning_only`, or unsplit `hybrid` tasks to `codex_app_managed_worktree_thread`.
- Do not claim worktree/thread creation, subagent execution, cache refresh, release readiness, UAT readiness, or clean review from package text.
- Do not use thread titles as identity; use legacy correlation only for old adapter compatibility.
