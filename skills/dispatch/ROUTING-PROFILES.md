# Dispatch Routing Profiles

## Target Reader

Groundwork dispatch users, coordinator threads, runtime adapter authors, and reviewers checking why a task was routed to a runtime.

## Reader Action Needed

Use these routing profiles to choose the lightest appropriate runtime, execution profile, and selector enforcement statement before generating Dispatch Package v2.

## Decision Supported

Whether a task should run in the main thread, a managed worktree thread, a subagent, or a clean reviewer path, and which model/reasoning profile should be requested.

## Scope

This document defines default routing and execution profile recommendations for dispatch. It does not execute runtime tools, prove runtime availability, or guarantee selector enforcement.

## Out of Scope

- Calling Codex App thread tools.
- Spawning subagents.
- Creating worktrees.
- Mutating remotes, trackers, data, or runtime state.
- Claiming model or reasoning selectors were applied by a runtime.

## Routing Table

| Task Shape | Default Runtime | Reason |
|---|---|---|
| Small direct answer or tiny low-risk edit | `main_thread_direct` | Runtime overhead is not justified. |
| Accepted independent write issue | `codex_app_managed_worktree_thread` | Needs filesystem isolation, durable diff review, validation evidence, and review package output. |
| High-risk schema/API/migration/security/data correctness write | `codex_app_managed_worktree_thread` | Needs isolated write execution and high-quality review evidence. |
| Read-only multi-perspective review | `codex_subagent` or `clean_reviewer` | Needs role or context isolation without write execution. |
| PRD / architecture / security / QA critique | `codex_subagent` or `main_thread_readonly` | Usually read-only decision support. |
| Independent codebase exploration | `codex_subagent` | Benefits from context isolation without worktree overhead. |
| Independent test failure diagnosis | `codex_subagent` | One problem domain can be investigated independently. |
| Hybrid investigation + possible fix | `codex_subagent` first, then dispatch write subtask | Avoid premature worktree creation before a concrete write task exists. |
| Planning-only | `main_thread_readonly` or `codex_subagent` | No file edits are expected. |
| Review completed worktree package | `clean_reviewer` | The completed result or review package is the source under inspection. |
| Shared-file or shared-contract conflicts | serialize / ask approval | Do not parallelize conflicting write tasks by default. |

## Execution Profile Defaults

| Task Shape | Model Profile | Reasoning Effort | Cost/Latency Bias |
|---|---|---|---|
| Tiny direct or doc/config change | fast coding model | low | fast |
| Normal feature issue with clear AC | balanced coding model | medium | balanced |
| Cross-cutting feature | strongest coding/reasoning available | high | quality |
| Migration/schema/API/security | strongest coding/reasoning available | high | quality |
| Read-only multi-perspective review | reviewer profile | medium/high | balanced/quality |
| Codebase exploration | fast/balanced reasoning profile | medium | balanced |
| High-risk clean review | strongest reviewer/reasoning available | high | quality |

## Profile Field Rules

Each routed task must include:

- `model_profile`
- `reasoning_effort`
- `cost_latency_bias`
- `routing_reason`

The `routing_reason` must connect the task shape, risk level, source truth, and validation expectation to the selected runtime and execution profile. Do not use generic reasons such as "best runtime" without naming the task evidence.

## Selector Enforcement

Selector enforcement is an evidence field, not an assumption.

- If the runtime exposes model/reasoning selectors and the adapter confirms they were applied, the result package may report `tool_enforced`.
- If the runtime does not expose selectors or dispatch cannot confirm support, include the execution profile in the runtime prompt or package and report `prompt_preference`, `unavailable`, or `unknown`.
- Dispatch must not claim `tool_enforced` from routing profiles alone.
- A package preference such as `strongest coding/reasoning available` is not proof of runtime enforcement.

## Write Routing Defaults

Default a write task to `codex_app_managed_worktree_thread` only when all of these are true:

- The task is an accepted independent write issue or high-risk write issue.
- Readiness evidence is present.
- Source package is present.
- Goal Contract is complete or the package clearly marks missing fields.
- Validation package is present.
- Conflict preflight does not require serialization or approval first.

If any of those fields are missing, dispatch should return `needs_info`, `needs_split`, `main_thread_readonly`, or a human decision instead of generating an executable worktree package.

## Read-only Routing Defaults

Read-only review, critique, exploration, and planning routes must not default to `codex_app_managed_worktree_thread`.

Allowed defaults:

- `codex_subagent` for isolated read-only review, exploration, diagnosis, or multi-perspective critique.
- `main_thread_readonly` for coordinator-level planning or decision support.
- `clean_reviewer` for review of a completed package, diff, or evidence set.

## Hybrid Routing Defaults

Hybrid tasks must split before write parallelization.

Default sequence:

1. Route investigation or diagnosis to `codex_subagent` or `main_thread_readonly`.
2. Require a concrete write subtask with source truth, AC, boundaries, and validation.
3. Run conflict preflight on the write subtask.
4. Dispatch the write subtask only after the write scope is concrete.

## Conflict-sensitive Routing

When `CONFLICT-PREFLIGHT.md` assigns the same conflict group to multiple write tasks, dispatch must serialize them or ask for explicit approval before parallelizing. Read-only subagent reviews may run in parallel even when they inspect the same files or contracts.
