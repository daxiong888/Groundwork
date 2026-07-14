# Dispatch Package v2 Details

## Target Reader

Groundwork dispatch users, child runtime adapters, and reviewers checking whether a package is adapter-ready.

## Reader Action Needed

Use this only when the compact `DISPATCH-PACKAGE.md` skeleton is not enough because the prompt needs full schema, adapter contract, managed-worktree admissibility, dependency barrier, legacy compatibility, or field-level validation.

## Decision Supported

Whether a Dispatch Package v2 payload is complete enough for adapter handoff without treating package generation as execution evidence.

## Scope

Extended package completeness, route policy, adapter deltas, dependency barriers, selector enforcement, and result expectations.

## Out of Scope

Runtime execution, Codex App thread creation, subagent spawning, remote writes, tracker mutation, branch cleanup, merge, archive, cache refresh, UAT/release/customer readiness, or final verification.

## Evidence Level

Source-validation contract derived from Groundwork dispatch runtime router contracts, Goal Contract requirements, routing reliability fixtures, adapter contracts, and the compact default contract in `DISPATCH-PACKAGE.md`.

## Schema

Dispatch Package v2 has this extended shape. Omit optional sections only when the task is non-executable/read-only and the omission is explicitly explained.

```yaml
dispatch_version: 2
adapter_completeness: skeleton_only | adapter_ready
source: {prd, issue_set, readiness_source, source_truth_status, redactions_applied}
runtime_policy:
  allow_parallel: true | false
  max_parallel_units: 1
  remote_writes_allowed: false
  destructive_actions_allowed: false
  route_enum: [local_direct, local_with_artifact, worktree_isolated, worktree_review_only, automation_candidate]
model_policy:
  selector_policy: tool_if_available_else_prompt_preference | prompt_preference_only | unavailable | unknown
tasks:
  - task_id: ""
    title: ""
    task_type: write_implementation | read_only_review | planning_only | hybrid | diagnosis | verification | direct
    readiness: ready_for_agent | ready_for_human | needs_info | blocked | needs_split | accepted_direct
    runtime_id: codex_app_managed_worktree_thread | codex_subagent | main_thread_direct | main_thread_readonly | clean_reviewer | not_applicable
    runtime_reason: ""
    runtime_identity: {runtime_correlation_id, dispatch_id, task_id}
    route_decision: {route, reason, why_not_worktree, why_worktree_if_selected, expected_touched_files, workspace_state, base_state, conflict, runtime_surface, risk}
    source_package: {prd_excerpt, issue_body, relevant_comments, known_source_or_first_inspection_step, redactions_applied}
    policy: {remote_writes_allowed: false, destructive_actions_allowed: false, approval_required}
    handoff_expected: {required, direction, artifact_path, package_ref}
    closeout_expected: {required, package_ref, merge_gate}
    verification_expectation: {fastest_signal, required_evidence, release_readiness_claimed, release_evidence_claim}
    approval_requirements: {required, reason, remote_writes_allowed: false, destructive_actions_allowed: false}
    runtime_evidence: {evidence_owner, worktree_creation_claimed: false, handoff_execution_claimed: false, archive_or_cleanup_claimed: false, runtime_success_claimed: false, cache_refresh_claimed: false}
    isolation: {context, filesystem, diff_surface}
    parallelization: {eligible, conflict_group, dependency_group, max_parallel_group_size, merge_order_hint}
    dependency_barrier: {depends_on_task_ids, blocked_until, required_base, re_triage_required_after_merge, goal_contract_refresh_required, dispatch_allowed_now, block_reason, release_evidence}
    goal_contract: {goal_command, outcome, source_truth, acceptance_criteria_mapping, verification, constraints, boundaries, iteration_policy, stop_when, pause_if, non_goals, risk_gate, preferred_runtime, result_package_expected}
    goal_mode: {required, goal_contract_lint, child_prompt_lint, rendered_prompt_first_non_empty_line, runtime_goal_mode_evidence_expected}
    execution_profile: {model_profile, reasoning_effort, cost_latency_bias, routing_reason, selector_policy}
    runtime_package: {status, adapter, subagent_role, subagent_prompt, can_write_files, expected_output, subagent_package}
    adapter_extension: {}
approval: {required, reason}
```

## Core Rules

- Dispatch Package v2 is package-only until execution is explicitly requested and a runtime adapter confirms capability.
- `remote_writes_allowed` and `destructive_actions_allowed` default to `false`.
- The task-level fields in this schema are the canonical Dispatch Package base. Adapters may constrain their values and add only runtime-specific fields under `adapter_extension`; they must not wrap or redefine the base shape.
- `runtime_identity.runtime_correlation_id` is the cross-package identity when runtime correlation is needed. Runtime-specific thread, worktree, or display-title fields belong in `adapter_extension`.
- Product truth must not be invented to fill missing Goal Contract, source, validation, acceptance, or evidence fields.

## Field Matrix

| Area | Required For | Hard Rule |
| --- | --- | --- |
| `source` | every package | Name source truth, readiness source, and redaction status. Unknown source routes to `needs_info` or `human_decision`. |
| `runtime_policy` | every package | Use `max_parallel_units` for package-wide concurrency. Never use `max_parallel_group_size` here. |
| `tasks[].parallelization` | parallel or conflict-aware packages | Use `max_parallel_group_size` only at task/group level and keep it below package ceiling. |
| `route_decision` | every task | Record route, why/why-not worktree, expected touched files, workspace/base/conflict/risk inputs when they affect routing. |
| `verification_expectation` | every task | Runtime/cache/release/UAT/marketplace/cache-refresh claims require `release_evidence_claim`; missing evidence is `unverified` or `not_applicable`. |
| `adapter_extension` | adapter-addressed tasks only | Add runtime-only fields. It must not duplicate or override canonical base fields. |
| `goal_contract` | executable agent work | Required for write execution packages; non-executable/read-only tasks may explain why not applicable. |
| `goal_mode` | managed worktree package | Must be top-level under the task, not nested under `runtime_package`; records Goal Contract and rendered prompt lint evidence. |
| `runtime_package.subagent_package` | subagent package | Self-contained role, context package, prompt, constraints, expected output, stop/pause conditions, result schema, capability detection, and execution status. |
| `dependency_barrier` | dependent write work | Required when prior child results, shared files, generated artifacts, schemas, or merge order can affect dispatch. |

## Route Policy Rules

Choose the lightest safe topology before selecting a runtime.

| Route | Use When | Must Not Claim |
| --- | --- | --- |
| `local_direct` | Small low-risk work can run in the current workspace with clear git boundary. | Worktree isolation, background handoff, or runtime execution evidence. |
| `local_with_artifact` | Durable PRD, issue map, plan, verify report, or handoff artifact is needed without isolated execution. | Isolated runtime safety. |
| `worktree_isolated` | Concrete write work needs filesystem isolation, clean diff boundaries, dirty-workspace separation, stale-base control, conflict isolation, serial dependency handling, or parallelizable implementation. | That Codex App created a worktree without runtime/user evidence. |
| `worktree_review_only` | A returned/external worktree result needs read-only inspection, clean review, or merge-readiness evaluation. | That review may mutate files or that reviewed work is merged. |
| `automation_candidate` | Recurring checks, reminders, scheduled work, or wakeups may be useful. | Automation creation/update without separate approval and an automation tool execution. |

Hard negatives:

- `read_only_review` and `planning_only` must not route to `worktree_isolated`.
- `hybrid` must route to `needs_split` until a concrete write subtask exists.
- Dirty workspace, stale base, shared-file conflicts, serial dependencies, or risk can justify isolation only when named in `route_decision`.
- `automation_candidate` uses `runtime_id: not_applicable` unless a later approved automation step selects a real tool.
- `selector_policy` is a request-side policy. Actual `selector_enforcement` appears only in returned runtime evidence and follows `skills/_shared/RUNTIME-CAPABILITY.md`.

## Managed Worktree Package Rules

The generic base does not redefine managed-worktree mechanics. For `runtime_id: codex_app_managed_worktree_thread`, first satisfy every base field above, then load `adapters/codex_app_managed_worktree_thread/DISPATCH-PACKAGE-CONTRACT.md` for the fixed values, admissibility gates, and runtime-only `adapter_extension` delta.

Do not generate or send that adapter package for read-only, planning-only, pre-split hybrid, wrong-route, missing-source, missing-verification, incomplete-Goal-Contract, or missing-Goal-Mode work. Route to a non-worktree runtime, `needs_info`, `needs_split`, `blocked`, or `human_decision` and name the exact failing base or adapter field.

Thread/worktree creation, pending initialization, registry, and display-title evidence are adapter concerns. They do not alter this base schema and do not prove runtime execution without adapter evidence and explicit execution approval.

## Dependency Barrier Rules

Use `dependency_barrier` when a task depends on prior child work, changed source, shared contracts, generated artifacts, fixtures, schemas, or merge order.

Dependent write dispatch is allowed only when prerequisite result package, clean review, merge-back, verification, and base refresh requirements are satisfied or marked `not_required`; `required_base.commit_after_merge` names the refreshed base when source changed; source package and Goal Contract were refreshed when required; and `dispatch_allowed_now: true` names release evidence or explains why not applicable.

Unknown, stale, unmerged, or partial prerequisite state means `dispatch_allowed_now: false` with `block_reason`, then route to serialization, read-only preparation, re-triage, or human decision. Same-conflict-group write tasks do not run in parallel without explicit serialization/approval.

## Required Package Completeness

An adapter-ready package includes:

- source truth, readiness source, redaction status;
- task type, readiness, runtime id, runtime reason;
- route decision with needed workspace/base/conflict/risk inputs;
- isolation and parallelization fields;
- Goal Contract or a clear non-executable/read-only reason;
- execution profile and selector enforcement expectation;
- verification expectation and release evidence claim status;
- expected output type, approval gate state, and runtime evidence ownership.

If any required field is missing for executable agent work, route to `needs_info`, `needs_split`, `blocked`, or human decision instead of generating an executable runtime package.
