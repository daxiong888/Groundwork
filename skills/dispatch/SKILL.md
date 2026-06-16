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
    isolation:
      context: ""
      filesystem: ""
      diff_surface: ""
    parallelization:
      eligible: false
      conflict_group: ""
      dependency_group: ""
      merge_order_hint: ""
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
    execution_profile:
      model_profile: ""
      reasoning_effort: "" # low | medium | high
      cost_latency_bias: "" # low_cost | balanced | low_latency | high_confidence
      routing_reason: ""
      selector_enforcement: "" # tool_enforced | prompt_preference | unavailable | unknown
    validation:
      fastest_signal: ""
      required_evidence: ""
    runtime_package:
      adapter: ""
      expected_output: ""
      can_write_files: false
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
      context: subagent
      filesystem: none
      diff_surface: none
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

Managed worktree packages are valid only when the task is a ready write implementation and Goal Contract, source package, and validation package are all present:

```yaml
tasks:
  - task_id: "issue-4a"
    task_type: write_implementation
    readiness: ready_for_agent
    runtime_id: codex_app_managed_worktree_thread
    runtime_reason: "Accepted write implementation with complete Goal Contract, source package, and validation package."
    isolation:
      context: thread
      filesystem: codex_managed_worktree
      diff_surface: required
    goal_contract:
      goal_command: "/goal <one executable task>"
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
    validation:
      fastest_signal: "<present>"
      required_evidence: "<present>"
    runtime_package:
      adapter: codex_app_managed_worktree_thread
      expected_output: review_package
      can_write_files: true
```

## Package References

- Runtime capabilities: `RUNTIME-ADAPTERS.md`
- Dispatch schema and routing rules: `DISPATCH-PACKAGE.md`
- Unified result envelope: `RESULT-PACKAGE.md`
