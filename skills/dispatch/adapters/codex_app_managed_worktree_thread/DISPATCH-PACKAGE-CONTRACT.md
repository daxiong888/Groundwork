# Managed Worktree Dispatch Package Contract

Target Reader: Groundwork dispatch users and runtime adapters validating a Dispatch Package v2 task entry addressed to `codex_app_managed_worktree_thread`.

Reader Action Needed: Check every admissibility field before any managed worktree child thread is created.

Decision Supported: Whether the package may execute in a Codex App managed worktree thread, must return no-op evidence, or is blocked until corrected.

Scope: This contract validates one Dispatch Package v2 task entry addressed to `codex_app_managed_worktree_thread`.

Out of Scope: Task routing, readiness decisions, runtime tool calls, manual worktree creation, remote writes, and final readiness decisions.

Evidence Level: Derived from Groundwork Dispatch Package v2, Goal Contract requirements, conflict preflight rules, and the prior managed-worktree adapter contract.

## Base Contract And Adapter Delta

Start with the canonical task schema in `../../DISPATCH-PACKAGE-DETAILS.md`. This adapter does not redefine package metadata, task identity, route, source, policy, handoff, closeout, verification, approval, Goal Contract, Goal Mode, execution profile, or runtime-package fields.

The following base fields have fixed values or additional constraints for this adapter:

| Base Field | Required Value Or Constraint |
| --- | --- |
| `task_type` | `write_implementation` |
| `readiness` | `ready_for_agent` |
| `runtime_id` | `codex_app_managed_worktree_thread` |
| `route_decision.route` | `worktree_isolated` with a concrete isolation reason and touched-file/risk inputs |
| `runtime_identity.runtime_correlation_id` | present; cross-package identity |
| `isolation` | `context: thread`, `filesystem: codex_managed_worktree`, `diff_surface: required` |
| `source_package` | self-contained source truth, including PRD/issue context or an explicit equivalent accepted source |
| `verification_expectation` | `fastest_signal` and `required_evidence` present |
| `goal_contract` | complete; `preferred_runtime` names this adapter and `result_package_expected: review_package` |
| `goal_mode` | required, both lints passed before delivery, first non-empty rendered line starts with `/goal` |
| `runtime_package` | this adapter, `can_write_files: true`, `expected_output: review_package` |

Only managed-worktree-specific dispatch fields belong in the delta:

```yaml
adapter_extension:
  codex_app_managed_worktree_thread:
    parent_thread_identifier: ""
    initial_thread_title: ""
    current_thread_title: ""
    title_mutation_detected: true | false | unknown
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
    legacy_compatibility:
      status: deprecated_in_place_for_v0_3_3_compatibility
      runtime_identity: {runtime_correlation_id, dispatch_id, task_id, parent_thread_identifier, child_thread_identifier, title_mutation_detected}
      worktree_registry: {base_ref, branch, artifact_path, owner_skill: dispatch, current_status: legacy_compatibility_only}
```

Do not duplicate canonical base fields inside `adapter_extension`. The adapter's initial/current title fields are display-only and must never replace `runtime_identity.runtime_correlation_id`.

Older packages without canonical runtime identity remain readable at intake. If correlation or closeout is required and the correlation id is absent, route to `needs_remediation`, `blocked`, or `human_decision` instead of inferring identity from a title.

Thread creation also requires a separate execution gate outside the Dispatch Package fields:

```text
explicit_execution_approval = satisfied_before_thread_creation
required_thread_capability = present
worktree_init_preflight = passed
```

## Worktree Initialization Preflight

Before calling Codex App worktree or child-thread tools, the execution-capable adapter must fill the delta's `worktree_init` object and record the intended start state and evidence.

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
- `source_package` contains the accepted source truth needed to execute without hidden context.
- `source_package.known_source_or_first_inspection_step` is present.
- Goal Contract is present and complete enough to execute, including `preferred_runtime` and `result_package_expected = review_package`.
- `goal_contract.goal_command` starts with `/goal`, is not a placeholder such as `/goal <one executable task>`, and passes `python3 skills/_shared/tools/lint_goal_contract.py <goal-contract-file>` before delivery. Source-repo maintainers may use the compatibility wrapper `python3 scripts/lint_goal_contract.py <goal-contract-file>`.
- The rendered child prompt passes `python3 skills/_shared/tools/lint_child_goal_prompt.py <rendered-child-prompt-file>` before delivery: its first non-empty line starts with `/goal`, `/goal` is not wrapped in a fenced code block, and no prose precedes `/goal`.
- `verification_expectation` includes `fastest_signal` and `required_evidence`.
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

Rejected or no-op packages must still produce the canonical Result Package with task identity, `outcome`, the rejected field or policy reason, empty changed files, validation-not-run reason, selector enforcement status, remaining risks or blockers, and a recommended next route. Adapter-only evidence stays under the adapter delta.

If Goal Mode is required and either Goal Contract lint or rendered child prompt lint fails, do not create the child thread. Return `blocked` or `needs_remediation` with the failing field and remediation path.
