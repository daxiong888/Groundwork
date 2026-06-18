# Dispatch Package v2

## Target Reader

Groundwork dispatch users, child runtime adapters, and reviewers checking whether a runtime package is complete enough to execute.

## Reader Action Needed

Generate, inspect, or consume Dispatch Package v2 without treating package generation as execution.

## Decision Supported

Whether a task is ready for a specific runtime, what constraints the runtime must obey, and what result package it must return.

## Scope

This schema covers dispatch package generation for the initial runtime set. It records parallelization, conflict preflight, and dependency barrier fields needed to decide whether write dispatch may proceed now.

## Out of Scope

Runtime execution, Codex App thread creation, subagent spawning, remote writes, tracker mutation, and final readiness decisions.

## Evidence Level

Derived from Groundwork dispatch runtime router contracts, Goal Contract requirements, and routing reliability fixtures.

## Schema

```yaml
dispatch_version: 2

source:
  prd: ""
  issue_set: ""
  readiness_source: ""
  source_truth_status: accepted | external_accepted | issue_ready | mixed | unknown
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
  runtime_candidates_by_route:
    local_direct:
      - main_thread_direct
    local_with_artifact:
      - main_thread_readonly
      - main_thread_direct
      - codex_subagent
    worktree_isolated:
      - codex_app_managed_worktree_thread
    worktree_review_only:
      - clean_reviewer
      - main_thread_readonly
      - codex_subagent
    automation_candidate:
      - not_applicable

model_policy:
  selector_enforcement: tool_if_available_else_prompt_preference

tasks:
  - task_id: ""
    title: ""
    task_type: write_implementation | read_only_review | planning_only | hybrid | diagnosis | verification | direct
    readiness: ready_for_agent | ready_for_human | needs_info | blocked | needs_split | accepted_direct
    runtime_id: codex_app_managed_worktree_thread | codex_subagent | main_thread_direct | main_thread_readonly | clean_reviewer | not_applicable
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
        relevant_comments: ""
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
      verification_expectation:
        fastest_signal: ""
        required_evidence: ""
        release_readiness_claimed: false
        release_evidence_claim:
          claim_type: runtime | cache | release | uat | marketplace | cache_refresh | not_applicable
          claim: ""
          evidence_status: verified | unverified | not_applicable
          installed_plugin_root: ""
          source_root: ""
          cache_or_source_refresh:
            method: refresh_step | source_equivalence | not_run | not_applicable
            evidence: ""
          run_scope: targeted | full | not_run | not_applicable
          commands_or_trials: []
          limitations: []
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
        parent_thread_identifier: "" # replace with native_context.thread_ref availability when visible
        child_thread_identifier: "" # replace with native_context.thread_ref availability when visible
        initial_thread_title: "" # display-only; not identity
        current_thread_title: "" # display-only; not identity
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
      context: thread | subagent_prompt | none | review_package
      filesystem: codex_managed_worktree | current_workspace | none | tool_dependent
      diff_surface: required | not_required | optional

    parallelization:
      eligible: true
      conflict_group: ""
      dependency_group: ""
      max_parallel_group_size: 1
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
      runtime_goal_mode_evidence_expected: present | not_required

    execution_profile:
      model_profile: ""
      reasoning_effort: low | medium | high
      cost_latency_bias: fast | balanced | quality
      routing_reason: ""
      selector_enforcement: tool_if_available_else_prompt_preference

    validation:
      deprecated_by: dispatch_native_alignment.verification_expectation

    runtime_package:
      status: legacy_adapter_package_shape_only
      adapter: ""
      thread_title: ""
      subagent_role: ""
      subagent_prompt: ""
      can_write_files: false
      expected_output: review_package | findings_package | diagnosis_package | direct_result | review_findings
      subagent_package:
        runtime_id: codex_subagent
        task_id: ""
        role: product_reviewer | security_reviewer | qa_reviewer | codebase_explorer | root_cause_diagnoser | planner
        can_write_files: false
        context_package: ""
        prompt: ""
        constraints: ""
        expected_output: findings_package | diagnosis_package
        max_iterations: 1
        stop_when: ""
        pause_if: ""
        result_schema: findings_package | diagnosis_package
        capability_detection_required: true
        execution_request: none | explicitly_requested | approval_required
        execution_status: package_only | capability_missing | approved_for_execution | executed_by_adapter

    approval:
      required: false
      reason: ""
```

## Core Rules

- `runtime_id` determines which adapter may consume the package.
- Dispatch Package v2 is package-only until explicit execution is requested and tool availability is confirmed.
- `remote_writes_allowed` defaults to `false`.
- `destructive_actions_allowed` defaults to `false`.
- Runtime packages must preserve source truth and redaction status.
- Product truth must not be invented to fill missing Goal Contract, source, validation, or acceptance fields.
- `dispatch_native_alignment` is the v0.4.0 dispatch output surface. It records route decision, source package, policy, expected handoff package, expected closeout package, verification expectation, approval requirements, and runtime evidence ownership.
- `dispatch_native_alignment.route_decision` records the v0.4.0 route policy input and recommendation. It does not prove runtime execution, Codex App worktree creation, automation creation, validation, archive, cleanup, or closeout.
- `dispatch_native_alignment.closeout_expected.merge_gate` must be `evidence_git_boundary_review_and_merge_source_required` whenever merge readiness is in scope.
- `dispatch_native_alignment.handoff_expected.package_ref` must reference `native_handoff_package` when a Local to Worktree or Worktree to Local transfer is expected; package generation must not claim that Handoff was executed.
- `legacy_compatibility` fields exist only to read or downgrade v0.3.3 managed-worktree packages. They are not Codex-native execution state and must not be used as proof of worktree creation, child-thread identity, archive, cleanup, runtime success, cache refresh, release readiness, or UAT readiness.

## Route Policy Rules

Route decisions choose the lightest safe topology before selecting an implementation runtime:

| Route | Use When | Must Not Claim |
| --- | --- | --- |
| `local_direct` | Small, low-risk work can run in the current workspace with clear git boundary. | Worktree isolation, runtime execution, or background handoff. |
| `local_with_artifact` | Durable PRD, issue map, plan, verify report, or handoff artifact is needed but isolated execution is not. | Isolated runtime safety. |
| `worktree_isolated` | Concrete write work benefits from filesystem isolation, clean diff boundaries, dirty-workspace separation, stale-base control, conflict isolation, serial dependency handling, or parallelizable implementation. | That Codex App worktree creation happened without runtime evidence. |
| `worktree_review_only` | A returned or external worktree result needs read-only inspection, clean review, or merge-readiness evaluation. | That review can mutate files or that reviewed work is merged. |
| `automation_candidate` | Recurring monitoring, reminders, scheduled checks, or wakeups may be useful. | Automation creation or update unless the user separately approves and the automation tool executes. |

Policy rules:

- `read_only_review` and `planning_only` must not route to `worktree_isolated`; use `worktree_review_only`, `local_with_artifact`, `main_thread_readonly`, `clean_reviewer`, or `codex_subagent` depending on the evidence need.
- `worktree_isolated` is valid only for concrete write work with known scope, expected touched files, acceptance criteria, and verification expectations.
- Dirty workspace, unrelated staged files, stale base, shared-file conflicts, or serial dependencies can justify `worktree_isolated` only when `dispatch_native_alignment.route_decision.workspace_state`, `base_state`, or `conflict` names the concrete input that changed the route.
- `automation_candidate` is recommendation-only. Dispatch may record the recommendation, but must not create, update, schedule, or archive automations.
- `automation_candidate` uses `runtime_id: not_applicable` unless a later user-approved automation execution step selects a real automation tool. It must not borrow `main_thread_readonly`, `codex_subagent`, or a worktree runtime just to satisfy schema shape.
- A route decision that lacks status/base/conflict evidence must say `unknown`, `needs_info`, `blocked`, or `human_decision` rather than inventing state.
- Any runtime, cache, release, UAT, marketplace, or cache-refresh claim must include `dispatch_native_alignment.verification_expectation.release_evidence_claim`. If evidence is missing or out of scope, set `evidence_status: unverified` or `not_applicable`; do not rely on `release_readiness_claimed` alone.

## Legacy Compatibility Rules

`legacy_compatibility` keeps v0.3.3 package readers from losing safety coverage while dispatch moves to `dispatch_native_alignment`.

- Custom lifecycle fields are `legacy_compatibility_only`. Native closeout owns verdict, merge decision, cleanup decision, blockers, and next route.
- Registry fields are `deprecated_in_place`. They may preserve old evidence references, but Groundwork dispatch must not treat registry status as Codex-native runtime state.
- Child-thread identity fields are replaced by native context availability markers when visible. If the native identifier is unavailable, say `unavailable_before_handoff`, `unavailable_in_current_surface`, or `redacted`; do not invent IDs.
- Selector enforcement remains `tool_if_available_else_prompt_preference`, `prompt_preference`, `unavailable`, or `unknown` unless an executing adapter reports stronger support.
- Background-run, automation, subagent execution, archive, cleanup, cache refresh, and release-readiness fields are package or recommendation metadata only unless runtime evidence exists.

## Runtime Routing Rules

- `read_only_review` must not route to `codex_app_managed_worktree_thread`.
- `planning_only` must not route to `codex_app_managed_worktree_thread`.
- `hybrid` must route to `needs_split` or split first. Investigation may route to `codex_subagent` or `main_thread_readonly`; write worktree routing waits until a concrete write implementation subtask exists.
- `write_implementation` with `readiness = ready_for_agent`, complete Goal Contract, native source package, verification expectation, and a concrete route input may choose `worktree_isolated` / `codex_app_managed_worktree_thread` unless the task is trivial, safer as `local_direct`, or the user overrides.
- `codex_app_managed_worktree_thread` requires `dispatch_native_alignment.route_decision.route = worktree_isolated`, `task_type = write_implementation`, `readiness = ready_for_agent`, `isolation.filesystem = codex_managed_worktree`, a complete Goal Contract, native source package, verification expectation, and `expected_output = review_package`.
- `codex_subagent` defaults to `can_write_files = false`.
- A subagent may write only when the user explicitly requests write-capable subagent execution and the runtime confirms safe support.
- Phase 1 `codex_subagent` dispatch is package-only: it may produce `subagent_package`, but it must not spawn a subagent or claim execution unless runtime capability detection and an explicit execution request or approval are both present.
- A `subagent_package` must be self-contained and role-specific: it must include the role, context package, prompt, constraints, expected output, stop condition, pause condition, and result schema.
- When subagent execution capability is unavailable, unknown, or not approved, set `execution_status = package_only` or `capability_missing` and report no runtime execution.
- `main_thread_readonly` and `clean_reviewer` must not produce file edits.

## Managed Worktree Package Rules

`dispatch` may generate a managed worktree package only when all required fields are present:

```yaml
task_type: write_implementation
readiness: ready_for_agent
runtime_id: codex_app_managed_worktree_thread
dispatch_native_alignment:
  route_decision:
    route: worktree_isolated
    why_worktree_if_selected: present
    workspace_state:
      status_checked: true
    base_state:
      base_stale: false | unknown
    conflict:
      shared_files: []
      serial_dependency: none | blocked_until_merge | human_decision
    runtime_surface:
      codex_app_worktree_available: true | unknown
    rollback_or_archive_path: present
    evidence_required_before_closeout: present
  source_package: present
  handoff_expected:
    required: true | false
    package_ref: native_handoff_package | not_applicable
  closeout_expected:
    required: true
    package_ref: native_closeout_package
    merge_gate: evidence_git_boundary_review_and_merge_source_required
  verification_expectation:
    fastest_signal: present
    required_evidence: present
    release_readiness_claimed: false
    release_evidence_claim:
      claim_type: not_applicable | runtime | cache | release | uat | marketplace | cache_refresh
      evidence_status: not_applicable | unverified | verified
      installed_plugin_root: present_or_empty
      source_root: present_or_empty
      cache_or_source_refresh:
        method: not_applicable | not_run | source_equivalence | refresh_step
        evidence: present_or_empty
      run_scope: not_applicable | not_run | targeted | full
      commands_or_trials: []
      limitations: present
  approval_requirements:
    remote_writes_allowed: false
    destructive_actions_allowed: false
  runtime_evidence:
    evidence_owner: codex_runtime | adapter | user_supplied | not_applicable
    worktree_creation_claimed: false
    handoff_execution_claimed: false
    archive_or_cleanup_claimed: false
    runtime_success_claimed: false
    cache_refresh_claimed: false
isolation:
  context: thread
  filesystem: codex_managed_worktree
  diff_surface: required
goal_contract:
  goal_command: present
  outcome: present
  source_truth: present
  acceptance_criteria_mapping: present
  verification: present
  constraints: present
  boundaries: present
  iteration_policy: present
  stop_when: present
  pause_if: present
  non_goals: present
  risk_gate: present
  preferred_runtime: present
  result_package_expected: review_package
goal_mode:
  required: true
  goal_contract_lint: pass
  child_prompt_lint: pass
  rendered_prompt_first_non_empty_line: starts_with_goal
  runtime_goal_mode_evidence_expected: present
runtime_package:
  status: legacy_adapter_package_shape_only
  adapter: codex_app_managed_worktree_thread
  can_write_files: true
  expected_output: review_package
legacy_compatibility:
  status: deprecated_in_place_for_v0_3_3_compatibility
  runtime_identity:
    runtime_correlation_id: present
  worktree_registry:
    base_ref: present
    artifact_path: present
    current_status: legacy_compatibility_only
```

`dispatch` must not generate or send a managed worktree package when any of these conditions apply:

- `task_type = read_only_review`
- `task_type = planning_only`
- `task_type = hybrid` before a concrete write subtask exists
- `runtime_id != codex_app_managed_worktree_thread`
- `dispatch_native_alignment.route_decision.route != worktree_isolated`
- `readiness != ready_for_agent`
- `dispatch_native_alignment.route_decision` does not name the concrete dirty workspace, staged-file, stale-base, shared-file, serial-dependency, risk, or setup input that justifies isolation
- Goal Contract is missing or incomplete
- `goal_mode` is missing, nested under `runtime_package`, or does not record Goal Contract and rendered prompt lint evidence
- `goal_contract.result_package_expected != review_package`
- `dispatch_native_alignment.source_package` is missing or incomplete
- `dispatch_native_alignment.verification_expectation` is missing or incomplete
- `runtime_package.expected_output != review_package`
- `dispatch_native_alignment.closeout_expected.merge_gate` is missing or weaker than `evidence_git_boundary_review_and_merge_source_required` when merge readiness is in scope
- legacy `runtime_identity.runtime_correlation_id` is missing when the package still targets a v0.3.3 managed-worktree adapter

For these cases, route to a non-worktree runtime, `needs_info`, `needs_split`, or human decision, and report `no_worktree_needed`, `unsupported_runtime`, or the specific missing package field. Do not silently coerce the task into a managed worktree package.

Managed worktree legacy compatibility rules:

- `legacy_compatibility.runtime_identity.runtime_correlation_id` is a compatibility correlation key for old adapter packages, not Codex-native child-thread identity.
- `legacy_compatibility.worktree_registry` is deprecated in place. It may name the base ref and artifact path for old package recovery, but registry status is not Codex-native lifecycle state.
- In package-only route decisions, `legacy_compatibility.worktree_registry.current_status` and `dispatch_native_alignment.route_decision.runtime_surface.codex_app_worktree_available` are not proof that Codex App created a worktree or child thread. Treat them as compatibility/package fields unless an execution-capable adapter returns evidence.
- Thread titles are display-only labels. Do not use `runtime_package.thread_title`, `legacy_compatibility.runtime_identity.initial_thread_title`, or `legacy_compatibility.runtime_identity.current_thread_title` as package identity.
- If a visible thread title changes after dispatch, keep the same `runtime_correlation_id`, update `current_thread_title` when available, and set `title_mutation_detected = true`.
- For backward compatibility, older v0.3.2 packages without `legacy_compatibility.runtime_identity` remain readable. If lifecycle closeout or managed worktree correlation is requested and the field is absent, route to `needs_remediation`, `blocked`, or `human_decision` instead of inferring identity from title.
If legacy registry fields are missing for v0.3.3 managed worktree closeout, route to `needs_remediation`, `blocked`, or `human_decision` rather than fabricating branch, base, artifact, or status evidence.

Groundwork defines this admissibility contract only. Adapter contract details live under `skills/dispatch/adapters/codex_app_managed_worktree_thread/`. Execution mechanics, including Codex App worktree creation, thread creation, child prompt delivery, lifecycle monitoring, review package collection, and selector application, require an execution-capable runtime adapter and explicit execution approval.

Legacy managed worktree initialization preflight:

- Use `working-tree` start state when the child task must inherit a reviewed dirty coordinator base.
- Use `existing-branch` start state only when the branch already exists and dirty-base inheritance is not required.
- Do not use `branchName` as a new-branch creation request.
- Treat `worktree_init_preflight` as legacy route setup evidence only. It is not Codex App worktree creation evidence.
- A `pendingWorktreeId` is not enough to claim a child thread was created; native child-thread identity and worktree path require runtime or user-supplied evidence.
- Failed or unknown worktree initialization routes to `blocked`, `needs_remediation`, or corrected preflight retry. Do not keep a failed worktree in pending state.

## Dependency Barrier Rules

Dispatch must serialize dependent write tasks until prerequisite merge-back and base refresh are complete.

Use `dependency_barrier` when any task depends on a prior child worktree result, changed source, shared contract, generated artifact, fixture, schema, or merge-order hint.

Dependent write dispatch is allowed only when:

- every prerequisite task in `depends_on_task_ids` has the required `blocked_until` evidence;
- prerequisite merge-back is `completed` or `not_required`;
- base refresh is `completed` or `not_required`;
- `required_base.commit_after_merge` names the base the dependent task will use, when the prerequisite changed files or contracts;
- the dependent task `dispatch_native_alignment.source_package` and Goal Contract were generated or refreshed against that post-merge base when `goal_contract_refresh_required: true`;
- `dispatch_allowed_now: true` includes `release_evidence`.

If dependency state is unknown, stale, or only present in an unmerged child worktree, set `dispatch_allowed_now: false`, record `block_reason`, and route to serialization, re-triage, or human decision instead of parallelizing write work.

Read-only preparation may run before prerequisite merge-back only when it does not treat unmerged child work as source truth and cannot write files. In that case, keep the write task blocked and use a read-only runtime.

Same-conflict-group write tasks must not run in parallel unless an explicit approval or merge-order plan serializes their write boundaries. Low-risk independent tasks with no dependency barrier, no shared conflict group, and no shared write surface remain parallelizable.

## Selector Enforcement Rules

- Dispatch may request a model profile, reasoning effort, and cost/latency bias.
- Dispatch must record selector enforcement as `tool_if_available_else_prompt_preference` unless a runtime adapter confirms stronger support.
- Result packages must not report `tool_enforced` unless the adapter confirms it.

## Required Package Completeness

A package is complete enough to hand to an adapter only when it includes:

- `dispatch_native_alignment.source_package` and readiness source
- task type, readiness, runtime_id, and runtime reason
- isolation and parallelization fields
- Goal Contract or a clear reason the task is non-executable/read-only
- execution profile and selector enforcement expectation
- validation expectation
- expected output type
- approval gate state

If these fields are missing for executable agent work, route to `needs_info`, `needs_split`, or human decision instead of generating an executable runtime package.
