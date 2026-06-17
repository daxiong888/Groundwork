# Managed Worktree Dispatch Package Contract

## Target Reader

Groundwork dispatch users and runtime adapters validating a Dispatch Package v2 task entry addressed to `codex_app_managed_worktree_thread`.

## Reader Action Needed

Check every admissibility field before any managed worktree child thread is created.

## Decision Supported

Whether the package may execute in a Codex App managed worktree thread, must return no-op evidence, or is blocked until corrected.

## Scope

This contract validates one Dispatch Package v2 task entry addressed to `codex_app_managed_worktree_thread`.

## Out of Scope

Task routing, readiness decisions, runtime tool calls, manual worktree creation, remote writes, and final readiness decisions.

## Evidence Level

Derived from Groundwork Dispatch Package v2, Goal Contract requirements, conflict preflight rules, and the prior managed-worktree adapter contract.

## Accepted Runtime

This adapter handles only:

```yaml
runtime_id: codex_app_managed_worktree_thread
```

## Required Package Shape

An executable managed worktree package must include:

```yaml
dispatch_version: 2
runtime_policy:
  remote_writes_allowed: false
  destructive_actions_allowed: false
model_policy:
  selector_enforcement: tool_if_available_else_prompt_preference
tasks:
  - task_id: present
    title: present
    task_type: write_implementation
    readiness: ready_for_agent
    runtime_id: codex_app_managed_worktree_thread
    runtime_reason: present
    isolation:
      context: thread
      filesystem: codex_managed_worktree
      diff_surface: required
    parallelization:
      eligible: true | false
      conflict_group: present_or_empty
      dependency_group: present_or_empty
      merge_order_hint: present_or_empty
    source_package:
      prd_excerpt: present
      issue_body: present
      known_source_or_first_inspection_step: present
      redactions_applied: present
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
    execution_profile:
      model_profile: present_or_empty
      reasoning_effort: low | medium | high
      cost_latency_bias: fast | balanced | quality
      routing_reason: present
      selector_enforcement: tool_if_available_else_prompt_preference
    validation:
      fastest_signal: present
      required_evidence: present
    runtime_package:
      adapter: codex_app_managed_worktree_thread
      thread_title: present_or_derivable
      can_write_files: true
      expected_output: review_package
    approval:
      required: false_or_satisfied
      reason: present_or_empty
```

## Admissibility Checklist

All checks must pass before creating a child thread:

- `runtime_id = codex_app_managed_worktree_thread`
- `task_type = write_implementation`
- `readiness = ready_for_agent`
- `isolation.context = thread`
- `isolation.filesystem = codex_managed_worktree`
- `isolation.diff_surface = required`
- `source_package.prd_excerpt` is present.
- `source_package.issue_body` is present.
- `source_package.known_source_or_first_inspection_step` is present.
- Goal Contract is present and complete enough to execute, including `preferred_runtime` and `result_package_expected = review_package`.
- Validation package includes `fastest_signal` and `required_evidence`.
- `runtime_package.expected_output = review_package`
- `runtime_package.can_write_files = true`
- remote writes are `false` or separately approved
- destructive actions are `false` or separately approved
- conflicts are absent, already serialized by dependency group and merge-order hint, or explicitly approved
- unresolved unknown or shared conflicts without serialization or approval are blocked

## Rejection And No-op

Return a Result Package without creating a child thread when any condition in `REJECT-NOOP-CHECKLIST.md` applies. Do not silently rewrite a non-admissible package into managed worktree execution.

## Output Contract

Executed packages must produce:

- a child review package using `REVIEW-PACKAGE-TEMPLATE.md`
- an adapter Result Package using `RESULT-PACKAGE-TEMPLATE.md`

Rejected or no-op packages must still produce a Result Package with task identity, the rejected field or policy reason, empty changed files, validation-not-run reason, selector enforcement status, remaining risks or blockers, and a recommended next route.
