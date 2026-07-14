# Managed Worktree Adapter Contract Scenario

Target Reader: Groundwork eval reviewers and maintainers validating the internal managed worktree adapter contract.
Reader Action Needed: Use this scenario to check that dispatch references the internal adapter contract without widening public skill surface or loosening package admissibility.
Decision Supported: Whether `codex_app_managed_worktree_thread` remains an internal dispatch adapter delta that constrains, but does not redefine, the canonical Dispatch Package v2 base.
Scope: Scenario-level coverage for internal adapter location, public-surface guardrails, base/delta ownership, managed-worktree admissibility, no-execution boundaries, and selector evidence language.
Out of Scope: Executing Codex App thread tools, creating managed worktrees, modifying runtime adapter implementations, remote writes, or proving installed plugin cache equivalence.
Evidence Level: Scenario derived from `skills/dispatch/DISPATCH-PACKAGE.md`, `skills/dispatch/RUNTIME-ADAPTERS.md`, `skills/dispatch/RESULT-PACKAGE.md`, and `skills/dispatch/adapters/codex_app_managed_worktree_thread/`.

## Scenario

Given Groundwork has an internal adapter contract under `skills/dispatch/adapters/codex_app_managed_worktree_thread/`
And `dispatch` remains the public skill responsible for routing and package generation
When Groundwork dispatch routes a ready write implementation task to `codex_app_managed_worktree_thread`
Then it must reference the internal adapter contract without creating a public skill entry
And it must not execute Codex App thread tools, create worktrees, spawn subagents, stage, commit, push, open PRs, or mutate trackers.

## Public Surface Checks

- The adapter directory must not contain a nested `SKILL.md`.
- Adapter reference files must not use skill frontmatter such as `---`, `name:`, or `description:`.
- Public dispatch skill references may point to `adapters/codex_app_managed_worktree_thread/ADAPTER.md`, but the adapter remains an internal contract package.

## Base And Delta Checks

A managed worktree package first satisfies the canonical base in `skills/dispatch/DISPATCH-PACKAGE-DETAILS.md`. The adapter may constrain those values and add only managed-worktree initialization data under `adapter_extension.codex_app_managed_worktree_thread`.

It is admissible only when the base includes:

- `task_type = write_implementation`
- `readiness = ready_for_agent`
- `runtime_id = codex_app_managed_worktree_thread`
- `isolation.context = thread`
- `isolation.filesystem = codex_managed_worktree`
- `isolation.diff_surface = required`
- a self-contained accepted `source_package`, including PRD/issue material or an explicit equivalent accepted source
- `source_package.known_source_or_first_inspection_step = present`
- complete Goal Contract including `preferred_runtime = present`
- `goal_contract.result_package_expected = review_package`
- validation package with `fastest_signal` and `required_evidence`
- `parallelization.eligible = true` for independent write tasks, or `false` for serialized conflicting write tasks with explicit dependency/merge order
- `runtime_package.adapter = codex_app_managed_worktree_thread`
- `runtime_package.can_write_files = true`
- `runtime_package.expected_output = review_package`
- explicit execution approval before child thread creation; package-level `approval.required = false` is not execution approval
- no duplicated route, source, policy, verification, approval, Goal Contract, Goal Mode, or closeout fields inside `adapter_extension`

## Failure Cases

- Fail if an executable package lacks self-contained accepted source truth or a first inspection step.
- Fail if adapter docs duplicate or override canonical base fields under `adapter_extension`.
- Fail if adapter docs omit `goal_contract.preferred_runtime`.
- Fail if adapter docs require `parallelization.eligible = true` for all managed worktree packages and thereby reject serialized conflicting write tasks.
- Fail if child prompt templates can produce `/goal /goal ...` when filled with `goal_contract.goal_command`.
- Fail if child prompt templates use scope placeholders that are not backed by Dispatch Package v2 or Goal Contract fields.
- Fail if adapter docs treat package-level `approval.required = false` as sufficient approval to create a child thread.
- Fail if incomplete managed-runtime packages emit legacy `no_worktree_needed` instead of canonical `blocked`, `needs_remediation`, or `human_decision` outcomes.
- Fail if accepted managed worktree execution result templates default `goal_contract_used` to `false`.
- Fail if adapter docs imply `tool_enforced` selector status without runtime adapter evidence.
- Fail if dispatch claims package generation created a thread, worktree, validation run, commit, push, PR, or issue close.
- Fail if read-only, planning-only, or hybrid pre-split work can be routed to managed worktree execution.
