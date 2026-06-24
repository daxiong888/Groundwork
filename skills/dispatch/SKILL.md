---
name: dispatch
description: Route accepted, ready tasks to the lightest appropriate runtime by producing Dispatch Package v2 and Result Package expectations. Use for runtime selection, execution matrixes, model/reasoning profile recommendations, managed worktree vs subagent decisions, and package-only runtime handoff. Dispatch is a router/package generator, not an executor.
---

# dispatch

## Target Reader

Groundwork users, coordinator threads, runtime adapter authors, and implementation/review threads that need a runtime routing package.

## Reader Action Needed

Use this skill to classify accepted tasks, select runtime routes, and produce package-only instructions that another runtime may execute only after explicit execution approval and available tools.

## Decision Supported

Which runtime should handle each task, why that runtime is appropriate, what package it receives, what result package it must return, and which tasks must stop, split, or return to triage.

## Scope

This skill covers dispatch-time runtime routing for `codex_app_managed_worktree_thread`, `codex_subagent`, `main_thread_direct`, `main_thread_readonly`, and `clean_reviewer`.

Out of scope: calling Codex App thread tools, spawning subagents, executing runtime tools, writing remotes, destructive actions, committing, pushing, opening PRs, closing issues, or claiming runtime execution occurred.

## Trigger Contract

Use this skill when the user asks to:

- distribute ready-for-agent issues to agents or runtimes
- decide which tasks need managed worktrees and which should use subagents or reviewers
- assign model profile, reasoning effort, or cost/latency bias per task
- generate an execution matrix
- generate a dispatch package
- plan multi-perspective review without creating worktrees
- decide whether tasks can run in parallel
- prepare runtime-specific child prompts or package-only handoffs

Do not use this skill when:

- requirements are not accepted; use `to-prd`
- issues are not sliced; use `to-issues`
- readiness is unknown; use `triage`
- the user asks which enumerable runtime, model-profile, skill-route, or workflow option to choose before there is an accepted ready package; use `skills/_shared/DECISION-MAPPING.md` as a shared lens, while keeping runtime capability evidence boundaries explicit
- the user asks to implement one scoped task directly; use `implement`
- the user only asks for an implementation plan; use `write-plan`
- the user asks whether finished work is ready or verified; use `verify`

## Required Behavior

When maintaining the Groundwork repository itself, apply the repo-local `AGENTS.md` Done Definition before reporting the work complete.

Use `skills/_shared/RUNTIME-CAPABILITY.md` before recommending, requesting, or reporting runtime/model selection. Dispatch must keep capability seed facts, prompt preferences, runtime/tool evidence, official docs, and community evidence separate.

Use `skills/_shared/COGNITIVE-BUDGET.md` for `model_profile`, reasoning/thinking preference, cost/latency bias, and Spark final authority restrictions. Route by profile before mapping to a concrete model.

Use `skills/_shared/DECISION-MAPPING.md` only for pre-dispatch option comparison when the user needs to choose among enumerable runtime, model-profile, skill-route, or workflow paths. Preserve `dispatch` when accepted, ready tasks need runtime routing, an execution matrix, model/profile recommendations, package-only handoff, or Result Package expectations. A decision map can recommend a dispatch path, but it must not generate or execute the dispatch package and must not claim selector enforcement beyond prompt preference without runtime/tool evidence.

`dispatch` must:

- confirm source truth, issue set, readiness source, and evidence level before routing
- classify each task as `write_implementation`, `read_only_review`, `planning_only`, `hybrid`, `diagnosis`, `verification`, or `direct`
- consume the Goal Contract when present and identify missing required Goal Contract fields
- assign exactly one `runtime_id` per routed task
- assign exactly one v0.4.0 route decision per routed task: `local_direct`, `local_with_artifact`, `worktree_isolated`, `worktree_review_only`, or `automation_candidate`
- emit the v0.4.0 dispatch surface under `dispatch_native_alignment`: route decision, policy, source package, handoff expectation, closeout expectation, verification expectation, approval requirements, and runtime evidence ownership
- assign isolation level, execution profile, validation expectation, and expected Result Package
- identify parallelization eligibility and conflict/dependency groups when enough evidence exists
- route read-only and planning-only tasks away from `worktree_isolated` and managed worktree runtimes
- split hybrid work before any write worktree package is generated
- default write implementation tasks to managed worktree only when readiness, Goal Contract, `dispatch_native_alignment.source_package`, `dispatch_native_alignment.verification_expectation`, and a concrete `worktree_isolated` route justification are present
- mark v0.3.3 custom lifecycle, registry, child-thread identity, selector-enforcement, and background-run fields as legacy compatibility unless adapter/runtime evidence exists
- keep `automation_candidate` recommendation-only; do not create, update, schedule, or archive automations from dispatch
- stop before execution unless the user explicitly requests execution and the current runtime exposes the required tools
- report selector enforcement transparently: use `tool_enforced` only when the adapter confirms selector support; otherwise use `prompt_preference`, `unavailable`, or `unknown`
- add `capability_status` and `selector_enforcement` whenever runtime/model selection is material; do not claim `tool_enforced` from prompt text, Goal Contract text, Dispatch Package text, model menu seeds, or routing profiles alone
- report Runtime mismatch when requested runtime and available/proposed runtime differ; do not silently substitute subagents for child-thread/worktree runtimes or child-thread/worktree runtimes for subagents
- treat user-observed model menu seeds as dated `user_supplied` capability facts, not universal runtime truth
- avoid permanent global concrete model tables; concrete model mapping is evidence-bound and secondary to profile routing
- apply `skills/_shared/ROLE-SEPARATION.md` when routing material work: separate designer/planner, implementer, clean reviewer, verifier, and coordinator roles; do not route a same-session implementer as clean reviewer or final verifier for its own material change
- include role-separation closeout expectations for material tasks using `Role`, `Design Source`, `Self-check Evidence`, `Clean Review Evidence`, `Independent Verification Evidence`, `Runtime Evidence`, `Browser Evidence`, `UAT Evidence`, `Release Evidence`, `Readiness Boundary`, and `Required Next Independent Role`

## Hard Stop Before Execution

Dispatch is a router and package generator. It must not:

- call Codex App thread tools
- create or manage child threads
- spawn subagents
- execute package contents
- write files in target runtimes
- mutate remotes or external trackers
- claim that runtime execution, validation, or review happened

If the user asks dispatch to execute, output the dispatch package plus an execution gate:

```text
Proposed Action:
Target Runtime:
Required Tool Capability:
Risk:
Rollback/Undo:
Approval Needed:
```

Proceed only after explicit approval and tool availability are both confirmed.

## Output Shape

````text
Dispatch Summary

Source Truth
- PRD:
- Issue Set:
- Readiness Source:
- Evidence Level:

Runtime Capability Check
- capability_status: known | unknown | user_supplied | docs_reference | tool_enforced
- selector_enforcement: tool_enforced | prompt_preference | unavailable | unknown
- Evidence layer: prompt_preference | runtime_tool_evidence | user_observed_model_menu_seed | official_docs | community_evidence | local_characterization_eval
- Available / assumed runtimes:
- Runtime selectors available:
- Subagent execution available:
- Worktree thread execution available:
- Requested runtime:
- Available runtime:
- Runtime mismatch: yes | no | unknown
- Fallback proposed:
- User approval required:

Task Matrix
| Task | Type | Readiness | Runtime | Isolation | Parallelization | Goal | Execution Profile | Validation | Result Package | Approval Needed |
|---|---|---|---|---|---|---|---|---|---|---|

No-Execution / Blocked / Needs Split
- Task:
- Reason:
- Required next action:

Runtime Packages
```yaml
dispatch_version: 2
source:
  prd: ""
  issue_set: ""
  readiness_source: ""
runtime_policy:
  remote_writes_allowed: false
  destructive_actions_allowed: false
tasks:
  - dispatch_native_alignment:
      policy:
        remote_writes_allowed: false
        destructive_actions_allowed: false
```

Expected Result Package
- Runtime:
- Output Type:
- Required Evidence:
- Role:
- Design Source:
- Self-check Evidence:
- Clean Review Evidence:
- Independent Verification Evidence:
- Runtime Evidence:
- Browser Evidence:
- UAT Evidence:
- Release Evidence:
- Readiness Boundary:
- Required Next Independent Role:

Next Action
````

## Runtime Package YAML Skeleton

```yaml
dispatch_version: 2

source:
  prd: ""
  issue_set: ""
  readiness_source: ""
  source_truth_status: "" # accepted | external_accepted | issue_ready | mixed | unknown
  redactions_applied: ""

runtime_policy:
  allow_parallel: true
  max_parallel_units: 3
  remote_writes_allowed: false
  destructive_actions_allowed: false
  route_enum:
    - local_direct
    - local_with_artifact
    - worktree_isolated
    - worktree_review_only
    - automation_candidate

model_policy:
  capability_status: unknown
  selector_enforcement: unknown
  selector_enforcement_policy: tool_if_available_else_prompt_preference
  evidence_layer: prompt_preference
  concrete_model_mapping: evidence_bound
  permanent_global_model_table: forbidden

tasks:
  - task_id: ""
    title: ""
    task_type: "" # write_implementation | read_only_review | planning_only | hybrid | diagnosis | verification | direct
    readiness: ""
    runtime_id: ""
    runtime_reason: ""
    dispatch_native_alignment:
      route_decision:
        route: local_direct | local_with_artifact | worktree_isolated | worktree_review_only | automation_candidate
        reason: ""
        why_not_worktree: ""
        why_worktree_if_selected: ""
        expected_touched_files: []
        workspace_state:
          current_branch: ""
          dirty_files: []
          unrelated_dirty_files: []
          staged_files: []
          untracked_files: []
          status_checked: true | false
        base_state:
          base_ref: ""
          base_commit: ""
          base_stale: true | false | unknown
          base_refresh_required: true | false | unknown
        conflict:
          conflict_group: ""
          shared_files: []
          serial_dependency: none | blocked_until_merge | human_decision
        runtime_surface:
          codex_app_worktree_available: true | false | unknown
          local_environment_required: true | false | unknown
          automation_surface_available: true | false | unknown
          subagent_available: true | false | unknown
          capability_status: known | unknown | user_supplied | docs_reference | tool_enforced
          selector_enforcement: tool_enforced | prompt_preference | unavailable | unknown
          evidence_layer: prompt_preference | runtime_tool_evidence | user_observed_model_menu_seed | official_docs | community_evidence | local_characterization_eval
          requested_runtime: ""
          available_runtime: ""
          runtime_mismatch: yes | no | unknown
          fallback_proposed: ""
          user_approval_required: true | false
        risk:
          git_write: true | false
          remote_write: true | false
          destructive: true | false
          secrets_or_pii: true | false
          customer_visible: true | false
        setup_requirements: []
        required_local_files: []
        rollback_or_archive_path: ""
        evidence_required_before_closeout: []
      source_package:
        prd_excerpt: ""
        issue_body: ""
        known_source_or_first_inspection_step: ""
        redactions_applied: ""
      policy:
        remote_writes_allowed: false
        destructive_actions_allowed: false
        approval_required: true | false
      handoff_expected:
        required: true | false
        direction: local_to_worktree | worktree_to_local | not_applicable
        artifact_path: ""
        package_ref: native_handoff_package | not_applicable
      closeout_expected:
        required: true | false
        package_ref: native_closeout_package | review_package | not_applicable
        merge_gate: evidence_git_boundary_review_and_merge_source_required | not_applicable
        role_separation:
          Role: coordinator | designer_planner | implementer | clean_reviewer | verifier | not_applicable
          Design Source: ""
          Self-check Evidence: ""
          Clean Review Evidence: ""
          Independent Verification Evidence: ""
          Runtime Evidence: ""
          Browser Evidence: ""
          UAT Evidence: ""
          Release Evidence: ""
          Readiness Boundary: ""
          Required Next Independent Role: ""
      verification_expectation:
        fastest_signal: ""
        required_evidence: ""
        release_readiness_claimed: false
      approval_requirements:
        required: true | false
        reason: ""
        remote_writes_allowed: false
        destructive_actions_allowed: false
      runtime_evidence:
        codex_native_required: true | false
        evidence_owner: codex_runtime | adapter | user_supplied | not_applicable
        worktree_creation_claimed: false
        handoff_execution_claimed: false
        archive_or_cleanup_claimed: false
        runtime_success_claimed: false
        cache_refresh_claimed: false
    legacy_compatibility:
      status: deprecated_in_place_for_v0_3_3_compatibility
      runtime_identity:
        runtime_correlation_id: ""
        dispatch_id: ""
        task_id: ""
        parent_thread_identifier: ""
        child_thread_identifier: ""
        initial_thread_title: ""
        current_thread_title: ""
        title_mutation_detected: true | false | unknown
      worktree_registry:
        base_ref: ""
        branch: ""
        artifact_path: ""
        owner_skill: "dispatch"
        current_status: legacy_compatibility_only
        created_at: ""
        last_checked_at: ""
    isolation:
      context: ""
      filesystem: ""
      diff_surface: ""
    parallelization:
      eligible: false
      conflict_group: ""
      dependency_group: ""
      merge_order_hint: ""
    dependency_barrier:
      depends_on_task_ids: []
      blocked_until:
        result_package_status: ready_for_review | not_required
        clean_review: passed | not_required
        merge_back: completed | not_required
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
    source_package:
      deprecated_by: dispatch_native_alignment.source_package
    goal_contract:
      goal_command: ""
      outcome: ""
      source_truth: ""
      acceptance_criteria_mapping: ""
      verification: ""
      constraints: ""
      boundaries: ""
      iteration_policy: ""
      stop_when: ""
      pause_if: ""
      non_goals: ""
      risk_gate: ""
      preferred_runtime: ""
      result_package_expected: ""
    goal_mode:
      status: legacy_adapter_prompt_evidence_only
      required: true | false
      goal_contract_lint: pass | fail | not_run
      child_prompt_lint: pass | fail | not_run
      rendered_prompt_first_non_empty_line: starts_with_goal | missing | invalid
      runtime_goal_mode_evidence_expected: present
    execution_profile:
      model_profile: "" # fast_scan | balanced_work | strong_reasoning | exhaustive_review | spark_iteration
      concrete_model: ""
      reasoning_effort: "" # low | medium | high | xhigh | unknown
      cost_latency_bias: "" # fast | balanced | quality
      routing_reason: ""
      capability_status: "" # known | unknown | user_supplied | docs_reference | tool_enforced
      selector_enforcement: "" # tool_enforced | prompt_preference | unavailable | unknown
      evidence_layer: "" # prompt_preference | runtime_tool_evidence | user_observed_model_menu_seed | official_docs | community_evidence | local_characterization_eval
    validation:
      deprecated_by: dispatch_native_alignment.verification_expectation
    runtime_package:
      status: legacy_adapter_package_shape_only
      adapter: ""
      expected_output: ""
      can_write_files: false
      worktree_init_preflight:
        status: legacy_route_setup_evidence_only
        starting_state: working-tree | existing-branch | unknown
        branch_name: ""
        dirty_base_inheritance_required: true | false
        branch_exists_verified: true | false | not_required
        init_status: not_started | passed | failed | blocked
      lifecycle_expectation:
        status: legacy_compatibility_only
        returned_state: review_package_returned
        next_state: clean_review_pending | needs_remediation | blocked
        child_may_self_archive: false
        branch_cleanup_separate: true
    approval:
      required: false
      reason: ""
```

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

## Package References

- Runtime capabilities: `RUNTIME-ADAPTERS.md`
- Dispatch schema and routing rules: `DISPATCH-PACKAGE.md`
- Unified result envelope: `RESULT-PACKAGE.md`
- Clean review fan-out: `CLEAN-REVIEW-FANOUT.md`
- Managed worktree internal adapter contract: `adapters/codex_app_managed_worktree_thread/ADAPTER.md`
