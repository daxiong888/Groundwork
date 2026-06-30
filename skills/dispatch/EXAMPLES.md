# Dispatch Examples

Target Reader: Groundwork dispatch users and reviewers who need concrete package examples after choosing an active dispatch branch.
Reader Action Needed: Load only when an example package is useful; otherwise use `SKILL.md` and `DISPATCH-PACKAGE.md`.
Decision Supported: How read-only review, hybrid diagnosis, and managed worktree package examples express the dispatch contract without claiming execution.
Artifact Type: branch-specific examples
Source of Truth: `skills/dispatch/SKILL.md` progressive-disclosure boundary and `skills/dispatch/DISPATCH-PACKAGE.md`.
Scope: Dispatch package examples for common routing branches.
Out of Scope: Runtime execution, package schema ownership, Codex App thread creation, subagent spawning, remote mutation, release readiness, UAT readiness, or installed-plugin cache evidence.
Evidence Level: Source-validation examples only.
Safe to Share / Redaction Notes: Safe to share as-is; contains no secrets, credentials, PII, private logs, or production payloads.

## Runtime Package Examples

Read-only review packages must not default to a managed worktree:

```yaml
tasks:
  - task_id: "review-api-contract"
    task_type: read_only_review
    readiness: ready_for_agent
    runtime_id: codex_subagent
    runtime_reason: "Independent read-only review with no file edits required."
    dispatch_native_alignment:
      route_decision:
        route: worktree_review_only
        reason: "Fresh-context review can inspect evidence without a write diff."
        why_not_worktree: "Read-only review is forbidden from worktree_isolated."
        why_worktree_if_selected: ""
        expected_touched_files: []
    isolation:
      context: subagent_prompt
      filesystem: none
      diff_surface: not_required
    runtime_package:
      adapter: codex_subagent
      expected_output: findings_package
      can_write_files: false
```

Hybrid tasks must split diagnosis from write work before a write package is generated:

```yaml
tasks:
  - task_id: "diagnose-router-regression"
    task_type: hybrid
    readiness: needs_split
    runtime_id: main_thread_readonly
    runtime_reason: "First inspect evidence and produce a concrete write slice or a no-change finding."
    dispatch_native_alignment:
      route_decision:
        route: local_with_artifact
        reason: "Hybrid work must produce a diagnosis artifact before any write slice can be routed."
        why_not_worktree: "No concrete write subtask exists yet."
        why_worktree_if_selected: ""
        expected_touched_files: []
    runtime_package:
      adapter: main_thread_readonly
      expected_output: diagnosis_package
      can_write_files: false
```

Managed worktree packages are valid only when the task is a ready write implementation and `dispatch_native_alignment` has native source, handoff, closeout, verification, approval, and runtime-evidence expectations:

```yaml
tasks:
  - task_id: "issue-4a"
    title: "Update managed worktree runtime identity contract"
    task_type: write_implementation
    readiness: ready_for_agent
    runtime_id: codex_app_managed_worktree_thread
    runtime_reason: "Accepted write implementation with a concrete worktree_isolated route decision, complete Goal Contract, native source package, verification expectation, and legacy compatibility correlation."
    dispatch_native_alignment:
      route_decision:
        route: worktree_isolated
        reason: "Concrete write task touches shared dispatch contracts and needs isolated diff review."
        why_not_worktree: ""
        why_worktree_if_selected: "Shared contract files and dependent lifecycle templates need clean diff boundaries."
        expected_touched_files:
          - "skills/dispatch/DISPATCH-PACKAGE.md"
          - "skills/dispatch/RESULT-PACKAGE.md"
        workspace_state:
          current_branch: "<present_or_unknown>"
          dirty_files: []
          unrelated_dirty_files: []
          staged_files: []
          untracked_files: []
          status_checked: true
        base_state:
          base_ref: "<current_base_or_empty>"
          base_commit: "<present_or_unknown>"
          base_stale: false
          base_refresh_required: false
        conflict:
          conflict_group: "managed-worktree-runtime-identity"
          shared_files:
            - "skills/dispatch/DISPATCH-PACKAGE.md"
          serial_dependency: none
        runtime_surface:
          codex_app_worktree_available: unknown
          local_environment_required: false
          automation_surface_available: false
        risk:
          git_write: true
          remote_write: false
          destructive: false
          secrets_or_pii: false
          customer_visible: false
        setup_requirements: []
        required_local_files: []
        rollback_or_archive_path: "Return review_package; coordinator decides merge, hold, or archive later."
        evidence_required_before_closeout:
          - "review_package"
          - "git boundary"
          - "validation result"
      source_package:
        prd_excerpt: "PRD v0.4.0 FR-405 requires dispatch runtime surface reduction."
        issue_body: "Shrink dispatch output to route, policy, source, handoff, closeout, verification, approval, and runtime evidence ownership."
        known_source_or_first_inspection_step: "Read DISPATCH-PACKAGE.md, native handoff contract, and native closeout contract before editing."
        redactions_applied: "none"
      policy:
        remote_writes_allowed: false
        destructive_actions_allowed: false
        approval_required: false
      handoff_expected:
        required: true
        direction: local_to_worktree
        artifact_path: "artifacts/<workstream>/issue-4a/native-handoff-package.md"
        package_ref: native_handoff_package
      closeout_expected:
        required: true
        package_ref: native_closeout_package
        merge_gate: evidence_git_boundary_review_and_merge_source_required
      verification_expectation:
        fastest_signal: "<present>"
        required_evidence: "<present>"
        release_readiness_claimed: false
      approval_requirements:
        required: false
        reason: ""
        remote_writes_allowed: false
        destructive_actions_allowed: false
      runtime_evidence:
        codex_native_required: true
        evidence_owner: adapter
        worktree_creation_claimed: false
        handoff_execution_claimed: false
        archive_or_cleanup_claimed: false
        runtime_success_claimed: false
        cache_refresh_claimed: false
    legacy_compatibility:
      status: deprecated_in_place_for_v0_3_3_compatibility
      runtime_identity:
        runtime_correlation_id: "gw:<workstream>:issue-4a:001:<short_hash>"
        dispatch_id: "<present>"
        task_id: "issue-4a"
        parent_thread_identifier: "<availability_marker_or_empty>"
        child_thread_identifier: "<availability_marker_or_empty>"
        initial_thread_title: "<display_only_or_empty>"
        current_thread_title: "<display_only_or_empty>"
        title_mutation_detected: unknown
      worktree_registry:
        base_ref: "<base_branch_or_commit>"
        branch: "<child_branch_or_empty>"
        artifact_path: "artifacts/<workstream>/issue-4a/"
        owner_skill: dispatch
        current_status: legacy_compatibility_only
        created_at: "<timestamp>"
        last_checked_at: "<timestamp>"
    isolation:
      context: thread
      filesystem: codex_managed_worktree
      diff_surface: required
    parallelization:
      eligible: false
      conflict_group: "managed-worktree-runtime-identity"
      dependency_group: ""
      merge_order_hint: "before dependent managed worktree lifecycle templates"
    dependency_barrier:
      depends_on_task_ids: []
      blocked_until:
        result_package_status: not_required
        clean_review: not_required
        merge_back: not_required
        verification: not_required
        base_refresh: not_required
      required_base:
        branch: "<current_base_or_empty>"
        commit_after_merge: "<not_required_or_present>"
      re_triage_required_after_merge: false
      goal_contract_refresh_required: false
      dispatch_allowed_now: true
      block_reason: ""
      release_evidence: "No prerequisite managed worktree task is required for this example package."
    source_package:
      deprecated_by: dispatch_native_alignment.source_package
    goal_contract:
      goal_command: "/goal Add stable runtime identity fields to the managed worktree dispatch package templates"
      outcome: "<present>"
      source_truth: "<present>"
      acceptance_criteria_mapping: "<present>"
      verification: "<present>"
      constraints: "<present>"
      boundaries: "<present>"
      iteration_policy: "<present>"
      stop_when: "<present>"
      pause_if: "<present>"
      non_goals: "<present>"
      risk_gate: "<present>"
      preferred_runtime: "<present>"
      result_package_expected: review_package
    goal_mode:
      status: legacy_adapter_prompt_evidence_only
      required: true
      goal_contract_lint: pass
      child_prompt_lint: pass
      rendered_prompt_first_non_empty_line: starts_with_goal
      runtime_goal_mode_evidence_expected: present
    validation:
      deprecated_by: dispatch_native_alignment.verification_expectation
    execution_profile:
      model_profile: "<present_or_empty>"
      concrete_model: ""
      reasoning_effort: medium
      cost_latency_bias: balanced
      routing_reason: "<present>"
      capability_status: unknown
      selector_enforcement: prompt_preference
      evidence_layer: prompt_preference
    runtime_package:
      status: legacy_adapter_package_shape_only
      adapter: codex_app_managed_worktree_thread
      thread_title: "Add stable runtime identity fields"
      expected_output: review_package
      can_write_files: true
      worktree_init_preflight:
        status: legacy_route_setup_evidence_only
        starting_state: working-tree
        branch_name: ""
        dirty_base_inheritance_required: false
        branch_exists_verified: not_required
        init_status: passed
      lifecycle_expectation:
        status: legacy_compatibility_only
        returned_state: review_package_returned
        next_state: clean_review_pending
        child_may_self_archive: false
        branch_cleanup_separate: true
    approval:
      required: false_or_package_gate_satisfied
      reason: "<present_or_empty>"
```
