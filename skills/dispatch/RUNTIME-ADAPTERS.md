# Dispatch Runtime Adapters

## Target Reader

Groundwork dispatch users, runtime adapter authors, and reviewers validating whether a task was routed to an appropriate runtime.

## Reader Action Needed

Use these capability profiles to choose a runtime and to state what the selected runtime may and may not do.

## Decision Supported

Whether a task should become a managed worktree package, subagent package, main-thread action, read-only coordinator review, or clean reviewer assignment.

## Scope

This document defines the initial dispatch runtime capability profiles. It does not execute tools or prove that a runtime is available in the current Codex surface.

## Runtime Capability Profiles

### Runtime: Codex App managed worktree thread

```yaml
runtime_id: codex_app_managed_worktree_thread
display_name: Codex App Managed Worktree Thread
supports_parallel: true
context_isolation: thread
filesystem_isolation: codex_managed_worktree
can_write_files: true
diff_review_surface: strong
lifecycle_visibility: strong
supports_long_running_tasks: true
supports_goal_mode: true
supports_model_selector: tool_if_available
supports_reasoning_selector: tool_if_available
best_for:
  - independent write implementation
  - feature issue
  - bug fix
  - migration with isolated worktree
  - task requiring durable diff
  - task requiring validation evidence
avoid_for:
  - read-only review
  - planning-only work
  - tiny direct edits
  - hybrid investigation before a concrete write subtask exists
  - tasks with shared-file conflict unless serialized
required_output:
  - review_package
package_admissibility:
  required_task_type: write_implementation
  required_readiness: ready_for_agent
  required_filesystem_isolation: codex_managed_worktree
  required_goal_contract: present
  required_source_package: present
  required_validation_package: present
  required_expected_output: review_package
```

Groundwork-side package requirements:

- A package addressed to `codex_app_managed_worktree_thread` must describe exactly one concrete write implementation task.
- The task must have `task_type = write_implementation`, `readiness = ready_for_agent`, and `isolation.filesystem = codex_managed_worktree`.
- The package must include a complete Goal Contract, source package, validation package, and `runtime_package.expected_output = review_package`.
- `dispatch` may request model/reasoning preferences, but selector enforcement remains unconfirmed until the runtime adapter reports it.

Groundwork-side rejection / no-package conditions:

- Do not send read-only, planning-only, or hybrid pre-split tasks as managed worktree packages.
- Do not send tasks for any runtime other than `codex_app_managed_worktree_thread` to the managed worktree adapter.
- Do not send packages with missing Goal Contract, missing source package, missing validation package, or `expected_output != review_package`.
- Do not send worktree packages when product truth, readiness, or validation expectations are missing; route to `needs_info`, `needs_split`, `main_thread_readonly`, or human decision instead.

Execution boundary:

- Groundwork defines routing requirements and package contracts only.
- Creating Codex App managed worktrees, creating child threads, placing `/goal` in the child prompt, monitoring thread lifecycle, collecting review packages, and applying model/reasoning selectors belong to the external `codex-managed-worktree-threads` runtime adapter.
- Groundwork must not claim that a worktree, thread, validation run, selector enforcement, stage, commit, push, or PR happened unless an executing adapter returns evidence.

### Runtime: Codex subagent

```yaml
runtime_id: codex_subagent
display_name: Codex Subagent
phase_1_mode: package_only
supports_parallel: true
context_isolation: subagent_prompt
filesystem_isolation: none_or_tool_dependent
can_write_files: false
diff_review_surface: weak_to_medium
lifecycle_visibility: medium_or_tool_dependent
supports_long_running_tasks: limited_or_tool_dependent
supports_goal_mode: prompt_level
supports_model_selector: tool_if_available
supports_reasoning_selector: tool_if_available
requires_capability_detection: true
requires_explicit_execution_request: true
requires_user_approval_unless_directly_requested: true
best_for:
  - read-only parallel review
  - independent codebase exploration
  - independent test failure diagnosis
  - multi-perspective review
  - root-cause investigation
  - findings or plan output
avoid_for:
  - high-risk writes
  - tasks requiring durable diff surface
  - tasks requiring isolated filesystem
  - tasks needing reliable cleanup unless runtime confirms support
required_output:
  - findings_package
  - diagnosis_package
package_requirements:
  - self_contained_context_package
  - role_specific_prompt
  - explicit_constraints
  - expected_output_type
  - stop_when
  - pause_if
execution_boundary:
  - dispatch_outputs_package_only
  - no_automatic_subagent_spawn
  - no_execution_claim_without_runtime_evidence
  - no_file_edits_unless_explicit_write_execution_is_requested_approved_and_supported
```

### Runtime: Main thread direct

```yaml
runtime_id: main_thread_direct
display_name: Main Thread Direct
supports_parallel: false
context_isolation: none
filesystem_isolation: current_workspace
can_write_files: true
diff_review_surface: current_session
lifecycle_visibility: strong
supports_long_running_tasks: limited
supports_goal_mode: no_for_child_goal
best_for:
  - tiny edits
  - direct answers
  - one-off low-risk fixes
  - coordination
avoid_for:
  - multi-task parallel work
  - isolated experiments
  - work requiring independent lifecycle
required_output:
  - direct_result
```

### Runtime: Main thread read-only

```yaml
runtime_id: main_thread_readonly
display_name: Main Thread Read-only
supports_parallel: false
context_isolation: none
filesystem_isolation: none
can_write_files: false
diff_review_surface: none
lifecycle_visibility: strong
best_for:
  - PRD review
  - dispatch matrix review
  - architecture critique
  - user-facing decision support
  - planning-only output
avoid_for:
  - implementation
  - package execution
required_output:
  - findings_package
```

### Runtime: Clean reviewer

```yaml
runtime_id: clean_reviewer
display_name: Clean Reviewer
supports_parallel: maybe
context_isolation: review_package
filesystem_isolation: none
can_write_files: false
diff_review_surface: input_package_only
lifecycle_visibility: medium
best_for:
  - review package inspection
  - diff conformance review
  - security lens
  - QA lens
  - product lens
avoid_for:
  - implementation
  - runtime package execution
required_output:
  - review_findings
```

## Selection Rules

- Choose `codex_app_managed_worktree_thread` when code writes, filesystem isolation, durable diff review, and validation evidence are required.
- Choose `codex_subagent` when the task is read-only, exploratory, diagnostic, perspective-based, or can return findings without durable file edits.
- Choose `main_thread_direct` for trivial direct work where the coordinator can safely complete the task without runtime isolation.
- Choose `main_thread_readonly` for coordinator-level reviews, decisions, dispatch matrix generation, or planning-only work.
- Choose `clean_reviewer` when reviewing a completed result package, diff, or evidence set from a fresh perspective.

## Selector Enforcement

Runtime selector enforcement must be reported as evidence, not assumed.

- `tool_enforced`: the adapter confirms that model/reasoning selectors were applied by tool or runtime API.
- `prompt_preference`: the package included selector preferences, but tool enforcement is unavailable or unconfirmed.
- `unavailable`: the adapter cannot apply selectors.
- `unknown`: dispatch cannot inspect selector support.

Do not claim `tool_enforced` from dispatch alone.
