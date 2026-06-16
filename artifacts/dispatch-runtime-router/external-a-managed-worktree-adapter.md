# External A: Managed Worktree Adapter Task Package

Target Reader: `codex-managed-worktree-threads` maintainers and the coordinator assigning work in that repository.
Reader Action Needed: Use this package as the source task for updating the external managed worktree adapter repository.
Decision Supported: Whether the external adapter is ready to consume Groundwork Dispatch Package v2 entries for `runtime_id = codex_app_managed_worktree_thread`.
Scope: External repository work only. This package is not part of the Groundwork local implementation queue.
Out of Scope: Groundwork skill edits, Groundwork eval edits, automatic runtime execution from Groundwork, remote writes without explicit approval, tracker APIs, task databases, hooks, MCP servers, or subagent adapter implementation.
Evidence Level: Derived from `docs/prd-dispatch-runtime-router.md` FR-11, AC-2, AC-5, AC-9, AC-13, AC-14, and the Groundwork dispatch contracts.

## Task

Slim `codex-managed-worktree-threads` into the runtime adapter for:

```text
runtime_id = codex_app_managed_worktree_thread
```

The adapter should consume only eligible managed worktree write implementation packages, create Codex App managed worktree child threads only after the package is admissible, place `/goal` only in child thread prompts, and return review evidence in a Result Package compatible shape.

## Target Repository

Repository: `codex-managed-worktree-threads`

Before implementation, confirm in that repository:

- target path
- current branch
- dirty worktree state
- available tests, evals, or validation commands
- whether existing thread prompt / review package templates already have compatible fields

Do not complete this task from Groundwork-only changes.

## Acceptance Criteria

- Update `codex-managed-worktree-threads/SKILL.md`.
- Add or update `codex-managed-worktree-threads/references/dispatch-package-contract.md`.
- Update `codex-managed-worktree-threads/references/thread-prompt-template.md`.
- Update `codex-managed-worktree-threads/references/review-package-template.md`.
- Add or update `codex-managed-worktree-threads/references/result-package-template.md`.
- Update `codex-managed-worktree-threads/references/rationale.md`.
- Update `codex-managed-worktree-threads/README.md`.
- The adapter accepts only `runtime_id = codex_app_managed_worktree_thread` packages for `task_type = write_implementation`.
- Accepted packages require `readiness = ready_for_agent`, `isolation.filesystem = codex_managed_worktree`, present Goal Contract, present source package, present validation package, and `expected_output = review_package`.
- The adapter rejects or no-ops non-managed-runtime, read-only, planning-only, hybrid-before-split, incomplete, or non-review-package inputs.
- The child prompt states that the coordinator/main thread remains coordinator and does not enter Goal Mode.
- `/goal` appears only in the child implementation thread prompt, not in the coordinator prompt or external task package.
- Selector enforcement status is reported transparently: use `tool_enforced` only when the adapter confirms model/reasoning selectors were applied by tool or API; otherwise report prompt preference, unavailable, or unknown.
- Runtime output is returned as a Result Package / review package with runtime identity, changed files, validation evidence, risks, blockers, and recommended next route.

## Source Evidence

- PRD FR-11: Slim `codex-managed-worktree-threads`.
- PRD AC-2: managed worktree adapter slimming.
- PRD AC-5: write implementation defaults to managed worktree only when ready and complete.
- PRD AC-9: Goal Contract required for executable agent tasks.
- PRD AC-13: selector enforcement transparency.
- PRD AC-14: runtime result wrapped as Result Package.
- Groundwork contracts:
  - `skills/dispatch/RUNTIME-ADAPTERS.md`
  - `skills/dispatch/DISPATCH-PACKAGE.md`
  - `skills/dispatch/RESULT-PACKAGE.md`
  - `docs/runtime-dispatch-workflow.md`

## Package Admissibility

The adapter may execute only if all of these are true:

```text
runtime_id = codex_app_managed_worktree_thread
task_type = write_implementation
readiness = ready_for_agent
isolation.filesystem = codex_managed_worktree
goal_contract present
source_package present
validation present
expected_output = review_package
remote_writes_allowed = false unless separately approved
destructive_actions_allowed = false unless separately approved
```

## Reject Or No-op Conditions

The adapter must not create a managed worktree child thread for:

```text
runtime_id != codex_app_managed_worktree_thread
task_type = read_only_review
task_type = planning_only
task_type = hybrid before a concrete write implementation subtask exists
readiness != ready_for_agent
goal_contract missing
source_package missing
validation missing
expected_output != review_package
remote write requested without explicit approval
destructive action requested without explicit approval
```

For rejected/no-op packages, return evidence explaining the package field or policy reason. Do not silently coerce non-write work into managed worktree execution.

## Child Prompt Requirements

The child implementation thread prompt should include:

- task identity and single-issue scope
- source package
- Goal Contract
- validation package
- allowed and disallowed files or behavior
- no subagent delegation
- no manual worktrees
- no stage, commit, push, PR, issue close, archive, or remote mutation unless separately approved
- required review package output
- `/goal` command for the child objective
- explicit statement that the coordinator/main thread remains coordinator and does not enter Goal Mode

## Result Requirements

The adapter result should include:

- `runtime_id`
- status: `ready_for_review`, `needs_remediation`, `blocked`, `no_execution_needed`, or `no_worktree_needed`
- output type: `review_package`
- Goal Contract evidence
- changed files
- diff summary or redacted patch evidence
- validation commands and results
- checks not run and reason
- selector enforcement status
- remaining risks
- blockers
- recommended next route for Groundwork `verify` / `triage`

## Verification Evidence Needed

Run the fastest relevant checks in the `codex-managed-worktree-threads` repository, including:

- repository status before and after edits
- template or doc checks available in that project
- checks proving reject/no-op conditions are represented
- checks proving `/goal` appears only in the child prompt path
- checks proving selector enforcement is not overclaimed

If no automated checks exist, provide manual inspection evidence with exact files and line-level rationale.

## Execution Classification

Implementation Task Type Candidate: `write_implementation`

Implementation Runtime Candidate: `separate_repo_required`

Product Runtime Covered: `codex_app_managed_worktree_thread`

Isolation Needed for implementation:

- context: `thread`
- filesystem: `external_repo`
- diff surface: `required`

Parallelization Candidate:

- eligible: yes only after Groundwork Dispatch Package v2 contract is stable and the external repo scope is confirmed
- conflict group: `external-managed-worktree-adapter`
- dependency group: `dispatch-public-skill`
- merge order hint: implement outside Groundwork after Groundwork dispatch contracts are stable

Goal Contract Status:

- Not generated by this artifact.
- Generate a concrete Goal Contract in the external repository implementation thread before execution.

Triage Recommendation Candidate: `ready-for-human` until target repo path, branch, dirty state, and checks are confirmed; then `ready-for-agent candidate`.
