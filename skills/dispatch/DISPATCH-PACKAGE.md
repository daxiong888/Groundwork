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
  default_runtime_preference_order:
    - codex_app_managed_worktree_thread
    - codex_subagent
    - main_thread_direct
    - main_thread_readonly
    - clean_reviewer

model_policy:
  selector_enforcement: tool_if_available_else_prompt_preference

tasks:
  - task_id: ""
    title: ""
    task_type: write_implementation | read_only_review | planning_only | hybrid | diagnosis | verification | direct
    readiness: ready_for_agent | ready_for_human | needs_info | blocked | needs_split | accepted_direct
    runtime_id: codex_app_managed_worktree_thread | codex_subagent | main_thread_direct | main_thread_readonly | clean_reviewer
    runtime_reason: ""

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
      current_status: created | active | review-ready | blocked | merge-ready | merged | archived | abandoned
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
      prd_excerpt: ""
      issue_body: ""
      relevant_comments: ""
      known_source_or_first_inspection_step: ""
      redactions_applied: ""

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
      fastest_signal: ""
      required_evidence: ""

    runtime_package:
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

## Runtime Routing Rules

- `read_only_review` must not route to `codex_app_managed_worktree_thread`.
- `planning_only` must not route to `codex_app_managed_worktree_thread`.
- `hybrid` must route to `needs_split` or split first. Investigation may route to `codex_subagent` or `main_thread_readonly`; write worktree routing waits until a concrete write implementation subtask exists.
- `write_implementation` with `readiness = ready_for_agent`, complete Goal Contract, source package, and validation package defaults to `codex_app_managed_worktree_thread` unless the task is trivial or the user overrides.
- `codex_app_managed_worktree_thread` requires `task_type = write_implementation`, `readiness = ready_for_agent`, `isolation.filesystem = codex_managed_worktree`, a complete Goal Contract, present source package, present validation package, and `expected_output = review_package`.
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
isolation:
  context: thread
  filesystem: codex_managed_worktree
  diff_surface: required
source_package:
  prd_excerpt: present
  issue_body: present
  known_source_or_first_inspection_step: present
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
validation:
  fastest_signal: present
  required_evidence: present
runtime_package:
  adapter: codex_app_managed_worktree_thread
  can_write_files: true
  expected_output: review_package
runtime_identity:
  runtime_correlation_id: present
worktree_registry:
  base_ref: present
  artifact_path: present
  current_status: created
```

`dispatch` must not generate or send a managed worktree package when any of these conditions apply:

- `task_type = read_only_review`
- `task_type = planning_only`
- `task_type = hybrid` before a concrete write subtask exists
- `runtime_id != codex_app_managed_worktree_thread`
- `readiness != ready_for_agent`
- Goal Contract is missing or incomplete
- `goal_mode` is missing, nested under `runtime_package`, or does not record Goal Contract and rendered prompt lint evidence
- `goal_contract.result_package_expected != review_package`
- source package is missing or incomplete
- validation package is missing or incomplete
- `runtime_package.expected_output != review_package`
- `runtime_identity.runtime_correlation_id` is missing for a managed worktree package

For these cases, route to a non-worktree runtime, `needs_info`, `needs_split`, or human decision, and report `no_worktree_needed`, `unsupported_runtime`, or the specific missing package field. Do not silently coerce the task into a managed worktree package.

Managed worktree runtime identity rules:

- `runtime_identity.runtime_correlation_id` is the source-of-truth identity for correlating dispatch, child runtime, review, result wrapping, merge-back, closeout, and branch cleanup packages.
- `worktree_registry` is the recoverable lifecycle record for one child task. It must name the base ref, artifact path, owner skill, and current registry status before execution can advance past child-thread creation.
- Thread titles are display-only labels. Do not use `runtime_package.thread_title`, `runtime_identity.initial_thread_title`, or `runtime_identity.current_thread_title` as package identity.
- If a visible thread title changes after dispatch, keep the same `runtime_correlation_id`, update `current_thread_title` when available, and set `title_mutation_detected = true`.
- For backward compatibility, older v0.3.2 packages without `runtime_identity` remain readable. If lifecycle closeout or managed worktree correlation is requested and the field is absent, route to `needs_remediation`, `blocked`, or `human_decision` instead of inferring identity from title.
If registry fields are missing for v0.3.3 managed worktree closeout, route to `needs_remediation`, `blocked`, or `human_decision` rather than fabricating branch, base, artifact, or status evidence.

Groundwork defines this admissibility contract only. Adapter contract details live under `skills/dispatch/adapters/codex_app_managed_worktree_thread/`. Execution mechanics, including Codex App worktree creation, thread creation, child prompt delivery, lifecycle monitoring, review package collection, and selector application, require an execution-capable runtime adapter and explicit execution approval.

Managed worktree initialization preflight:

- Use `working-tree` start state when the child task must inherit a reviewed dirty coordinator base.
- Use `existing-branch` start state only when the branch already exists and dirty-base inheritance is not required.
- Do not use `branchName` as a new-branch creation request.
- A `pendingWorktreeId` is not enough to claim `child_thread_created`; a child thread identifier and worktree path are required.
- Failed worktree initialization routes to `blocked`, `needs_remediation`, or corrected preflight retry. Do not keep a failed worktree in pending state.

## Dependency Barrier Rules

Dispatch must serialize dependent write tasks until prerequisite merge-back and base refresh are complete.

Use `dependency_barrier` when any task depends on a prior child worktree result, changed source, shared contract, generated artifact, fixture, schema, or merge-order hint.

Dependent write dispatch is allowed only when:

- every prerequisite task in `depends_on_task_ids` has the required `blocked_until` evidence;
- prerequisite merge-back is `completed` or `not_required`;
- base refresh is `completed` or `not_required`;
- `required_base.commit_after_merge` names the base the dependent task will use, when the prerequisite changed files or contracts;
- the dependent task source package and Goal Contract were generated or refreshed against that post-merge base when `goal_contract_refresh_required: true`;
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

- source package and readiness source
- task type, readiness, runtime_id, and runtime reason
- isolation and parallelization fields
- Goal Contract or a clear reason the task is non-executable/read-only
- execution profile and selector enforcement expectation
- validation expectation
- expected output type
- approval gate state

If these fields are missing for executable agent work, route to `needs_info`, `needs_split`, or human decision instead of generating an executable runtime package.
