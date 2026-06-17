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
- the user asks to implement one scoped task directly; use `implement`
- the user only asks for an implementation plan; use `write-plan`
- the user asks whether finished work is ready or verified; use `verify`

## Required Behavior

`dispatch` must:

- confirm source truth, issue set, readiness source, and evidence level before routing
- classify each task as `write_implementation`, `read_only_review`, `planning_only`, `hybrid`, `diagnosis`, `verification`, or `direct`
- consume the Goal Contract when present and identify missing required Goal Contract fields
- assign exactly one `runtime_id` per routed task
- assign isolation level, execution profile, validation expectation, and expected Result Package
- identify parallelization eligibility and conflict/dependency groups when enough evidence exists
- route read-only and planning-only tasks away from managed worktree runtimes
- split hybrid work before any write worktree package is generated
- default write implementation tasks to managed worktree only when readiness, Goal Contract, source package, and validation package are present
- stop before execution unless the user explicitly requests execution and the current runtime exposes the required tools
- report selector enforcement transparently: use `tool_enforced` only when the adapter confirms selector support; otherwise use `prompt_preference`, `unavailable`, or `unknown`

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
- Available / assumed runtimes:
- Runtime selectors available:
- Subagent execution available:
- Worktree thread execution available:
- Fallback behavior:

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
tasks: []
```

Expected Result Package
- Runtime:
- Output Type:
- Required Evidence:

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

model_policy:
  selector_enforcement: tool_if_available_else_prompt_preference

tasks:
  - task_id: ""
    title: ""
    task_type: "" # write_implementation | read_only_review | planning_only | hybrid | diagnosis | verification | direct
    readiness: ""
    runtime_id: ""
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
      prd_excerpt: ""
      issue_body: ""
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
      runtime_goal_mode_evidence_expected: present
    execution_profile:
      model_profile: ""
      reasoning_effort: "" # low | medium | high
      cost_latency_bias: "" # fast | balanced | quality
      routing_reason: ""
      selector_enforcement: "" # tool_enforced | prompt_preference | unavailable | unknown
    validation:
      fastest_signal: ""
      required_evidence: ""
    runtime_package:
      adapter: ""
      expected_output: ""
      can_write_files: false
      worktree_init_preflight:
        starting_state: working-tree | existing-branch | unknown
        branch_name: ""
        dirty_base_inheritance_required: true | false
        branch_exists_verified: true | false | not_required
        init_status: not_started | passed | failed | blocked
      lifecycle_expectation:
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
    runtime_package:
      adapter: main_thread_readonly
      expected_output: diagnosis_package
      can_write_files: false
```

Managed worktree packages are valid only when the task is a ready write implementation and runtime identity, Goal Contract, source package, and validation package are all present:

```yaml
tasks:
  - task_id: "issue-4a"
    title: "Update managed worktree runtime identity contract"
    task_type: write_implementation
    readiness: ready_for_agent
    runtime_id: codex_app_managed_worktree_thread
    runtime_reason: "Accepted write implementation with runtime identity, complete Goal Contract, source package, and validation package."
    runtime_identity:
      runtime_correlation_id: "gw:<workstream>:issue-4a:001:<short_hash>"
      dispatch_id: "<present>"
      task_id: "issue-4a"
      parent_thread_identifier: "<present_or_empty>"
      child_thread_identifier: "<present_or_empty>"
      initial_thread_title: "<display_only_or_empty>"
      current_thread_title: "<display_only_or_empty>"
      title_mutation_detected: unknown
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
      prd_excerpt: "PRD v0.3.3 FR-5 requires stable runtime identity for managed worktree packages."
      issue_body: "Add runtime identity fields and stop using thread title as source-of-truth identity."
      known_source_or_first_inspection_step: "Read DISPATCH-PACKAGE.md, RESULT-PACKAGE.md, and managed worktree adapter templates before editing."
      redactions_applied: "none"
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
      required: true
      goal_contract_lint: pass
      child_prompt_lint: pass
      rendered_prompt_first_non_empty_line: starts_with_goal
      runtime_goal_mode_evidence_expected: present
    validation:
      fastest_signal: "<present>"
      required_evidence: "<present>"
    execution_profile:
      model_profile: "<present_or_empty>"
      reasoning_effort: medium
      cost_latency_bias: balanced
      routing_reason: "<present>"
      selector_enforcement: tool_if_available_else_prompt_preference
    runtime_package:
      adapter: codex_app_managed_worktree_thread
      thread_title: "Add stable runtime identity fields"
      expected_output: review_package
      can_write_files: true
      worktree_init_preflight:
        starting_state: working-tree
        branch_name: ""
        dirty_base_inheritance_required: false
        branch_exists_verified: not_required
        init_status: passed
      lifecycle_expectation:
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
