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
    runtime_identity:
      runtime_correlation_id: present
      dispatch_id: present_or_empty
      task_id: present_or_empty
      parent_thread_identifier: present_or_empty
      child_thread_identifier: present_or_empty
      initial_thread_title: present_or_empty
      current_thread_title: present_or_empty
      title_mutation_detected: true | false | unknown
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
    goal_mode:
      required: true
      goal_contract_lint: passed_before_delivery
      child_prompt_lint: passed_before_delivery
      rendered_prompt_first_non_empty_line: starts_with_goal
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
      required: false_or_package_gate_satisfied
      reason: present_or_empty
```

`approval.required = false` is sufficient only for package generation. It is not execution approval and must not be treated as permission to create a child thread.

`runtime_identity.runtime_correlation_id` is the source-of-truth identity for correlating dispatch, child runtime, review, result wrapping, merge-back, closeout, and branch cleanup packages. `runtime_package.thread_title` is a display-only, derivable label and must never be used as source-of-truth identity.

Older v0.3.2 packages without `runtime_identity` remain readable. If managed worktree lifecycle closeout or runtime correlation is requested and `runtime_identity.runtime_correlation_id` is absent, route to remediation, block, or human decision rather than inferring identity from `thread_title`.

Thread creation also requires a separate execution gate outside the Dispatch Package fields:

```text
explicit_execution_approval = satisfied_before_thread_creation
required_thread_capability = present
worktree_init_preflight = passed
```

## Worktree Initialization Preflight

Before calling Codex App worktree or child-thread tools, the execution-capable adapter must record the intended start state and evidence:

```yaml
worktree_init:
  starting_state: working-tree | existing-branch
  dirty_base_required: true | false
  branch_name: ""
  branch_resolved: true | false | not_applicable
  branch_evidence: ""
  pending_worktree_id: ""
  child_thread_identifier: ""
  worktree_path: ""
  init_status: not_started | pending | child_thread_created | failed | blocked
  failure_action: retry_with_corrected_state | needs_remediation | blocked | human_decision | none
  evidence: ""
```

Rules:

- Use `starting_state = working-tree` when the child task must inherit the current reviewed dirty base, such as prior clean-reviewed waves that were merged into the coordinator worktree but not committed.
- Use `starting_state = existing-branch` only when no dirty base inheritance is required and `branch_name` already resolves before the tool call.
- Do not treat `startingState.branchName` as a request to create a new branch. If the named branch does not resolve, block before child thread creation or route to `needs_remediation`.
- Detached HEAD in a Codex-managed worktree is acceptable. Child implementation threads must not create a branch only to continue work.
- A `pendingWorktreeId` is not success evidence and not child-thread evidence. The lifecycle may enter `child_thread_created` only after the pending worktree resolves to both a child thread identifier and a worktree path.
- While `init_status = pending`, the coordinator must wait, poll, resolve, or stop with `blocked`/`human_decision` evidence. It must not implement the same task in the parent thread.
- A corrected retry is legal only after the prior pending request has resolved, failed, or been explicitly abandoned through `blocked`/`human_decision` evidence. It must use the same approved Codex App managed-worktree topology and must not create a parallel implementation path.
- A manual git worktree fallback is forbidden while a Codex-managed worktree request for the same task is pending. Any fallback that changes filesystem isolation, thread ownership, or runtime topology requires explicit user approval before execution and must be reported as a topology change, not as managed-worktree evidence.
- If initialization fails, report `init_status = failed`, preserve the failure evidence, and route to `blocked`, `needs_remediation`, or a corrected preflight retry. Do not keep treating a failed worktree as pending.

## Admissibility Checklist

All checks must pass before creating a child thread:

- `runtime_id = codex_app_managed_worktree_thread`
- `task_type = write_implementation`
- `readiness = ready_for_agent`
- `runtime_identity.runtime_correlation_id` is present.
- `isolation.context = thread`
- `isolation.filesystem = codex_managed_worktree`
- `isolation.diff_surface = required`
- `source_package.prd_excerpt` is present.
- `source_package.issue_body` is present.
- `source_package.known_source_or_first_inspection_step` is present.
- Goal Contract is present and complete enough to execute, including `preferred_runtime` and `result_package_expected = review_package`.
- `goal_contract.goal_command` starts with `/goal`, is not a placeholder such as `/goal <one executable task>`, and passes `python3 skills/_shared/tools/lint_goal_contract.py <goal-contract-file>` before delivery. Source-repo maintainers may use the compatibility wrapper `python3 scripts/lint_goal_contract.py <goal-contract-file>`.
- The rendered child prompt passes `python3 scripts/lint_child_goal_prompt.py <rendered-child-prompt-file>` before delivery: its first non-empty line starts with `/goal`, `/goal` is not wrapped in a fenced code block, and no prose precedes `/goal`.
- Validation package includes `fastest_signal` and `required_evidence`.
- `runtime_package.expected_output = review_package`
- `runtime_package.can_write_files = true`
- explicit execution approval is present; package-level `approval.required = false` is not enough to create a child thread
- required Codex App thread capabilities are available
- worktree initialization preflight passed
- no unresolved `pendingWorktreeId` exists for the same runtime correlation id unless it has resolved to both `child_thread_identifier` and `worktree_path`
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

If Goal Mode is required and either Goal Contract lint or rendered child prompt lint fails, do not create the child thread. Return `blocked` or `needs_remediation` with the failing field and remediation path.
