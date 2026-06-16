# Dispatch Package v2

## Target Reader

Groundwork dispatch users, child runtime adapters, and reviewers checking whether a runtime package is complete enough to execute.

## Reader Action Needed

Generate, inspect, or consume Dispatch Package v2 without treating package generation as execution.

## Decision Supported

Whether a task is ready for a specific runtime, what constraints the runtime must obey, and what result package it must return.

## Scope

This schema covers dispatch package generation for the initial runtime set. It does not define advanced routing profiles or conflict-preflight mechanics beyond the core fields required to record them.

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
  result_package_expected: present
validation:
  fastest_signal: present
  required_evidence: present
runtime_package:
  adapter: codex_app_managed_worktree_thread
  can_write_files: true
  expected_output: review_package
```

`dispatch` must not generate or send a managed worktree package when any of these conditions apply:

- `task_type = read_only_review`
- `task_type = planning_only`
- `task_type = hybrid` before a concrete write subtask exists
- `runtime_id != codex_app_managed_worktree_thread`
- `readiness != ready_for_agent`
- Goal Contract is missing or incomplete
- source package is missing or incomplete
- validation package is missing or incomplete
- `runtime_package.expected_output != review_package`

For these cases, route to a non-worktree runtime, `needs_info`, `needs_split`, or human decision, and report `no_worktree_needed`, `unsupported_runtime`, or the specific missing package field. Do not silently coerce the task into a managed worktree package.

Groundwork defines this admissibility contract only. Adapter execution mechanics, including Codex App worktree creation, thread creation, child prompt delivery, lifecycle monitoring, review package collection, and selector application, belong to `codex-managed-worktree-threads`.

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
