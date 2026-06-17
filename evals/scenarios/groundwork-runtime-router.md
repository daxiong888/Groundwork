# Groundwork Runtime Router Scenarios

These scenarios complement `evals/prompts/dispatch.csv`. The CSV fixtures test trigger boundaries and required fields; this file tests end-to-end dispatch routing behavior for accepted Groundwork workstreams.

## Scenario 1: Accepted Write Implementation Issue

Prompt:

```text
这个 accepted ready-for-agent issue 有清晰 AC、source package、Goal Contract 和 validation package。请生成 dispatch package。
```

Expected first skill: `dispatch`

Expected route: `codex_app_managed_worktree_thread`

Expected execution profile: balanced coding model, `reasoning_effort = medium`, `cost_latency_bias = balanced`, with a concrete `routing_reason`.

Expected selector enforcement: `tool_if_available_else_prompt_preference` in the package, or `prompt_preference` / `unknown` in any result summary unless a runtime adapter confirms selector support.

Parallelization expectation: allowed only when conflict preflight finds `conflict_group = none` or an approved independent group.

Risk / gate: no execution. Dispatch produces a package only.

## Scenario 2: Read-only Multi-perspective Review

Prompt:

```text
这个任务只要求产品、安全和 QA 三个视角评审，不要创建 worktree，也不要改文件。
```

Expected first skill: `dispatch`

Expected route: `codex_subagent` or `clean_reviewer`

Expected execution profile: reviewer profile, `reasoning_effort = medium` or `high`, `cost_latency_bias = balanced` or `quality`, with a concrete `routing_reason`.

Expected selector enforcement: selector preference may be included in the prompt/package, but dispatch must not claim `tool_enforced`.

Parallelization expectation: read-only review may run in parallel even when reviewers inspect the same source area.

Risk / gate: no execution. If execution is requested, require explicit approval and runtime capability evidence.

## Scenario 3: Hybrid Diagnosis Then Possible Fix

Prompt:

```text
这个 issue 可能要修代码 但现在只知道测试失败 先判断是不是代码问题 再决定要不要改。
```

Expected first skill: `dispatch`

Expected route: diagnosis first to `codex_subagent` or `main_thread_readonly`

Expected execution profile: fast/balanced reasoning profile, `reasoning_effort = medium`, `cost_latency_bias = balanced`.

Expected behavior: must not create a write worktree package until the concrete write subtask exists with source truth, AC, boundaries, and validation.

Parallelization expectation: hybrid tasks must split before write parallelization.

Risk / gate: possible future write task requires a new dispatch decision and conflict preflight.

## Scenario 4: High-risk Migration Issue

Prompt:

```text
这个 ready-for-agent issue 要改 migration、DB schema 和 API response contract，请安排 runtime 并说明并行风险。
```

Expected first skill: `dispatch`

Expected route: `codex_app_managed_worktree_thread`

Expected execution profile: strongest coding/reasoning available, `reasoning_effort = high`, `cost_latency_bias = quality`, with a routing reason naming migration, DB schema, API contract, and validation risk.

Expected conflict preflight: assign conflict groups such as `migration`, `db-schema`, and `api-contract`. Same-group write tasks must not be parallelized by default.

Expected merge order hint: required for conflicting write tasks, for example "merge schema migration before API and fixture updates".

Risk / gate: no execution. Remote writes, destructive actions, migrations, and deployment remain disallowed unless separately approved.

## Scenario 5: Conflicting Shared Public Type Writes

Prompt:

```text
Issue A 和 Issue B 都要改同一个 exported interface。请判断是否能并行。
```

Expected first skill: `dispatch`

Expected route: serialize or ask approval before parallel write execution.

Expected conflict preflight: assign `conflict_group = public-type`, `eligible = false`, `max_parallel_group_size = 1`, and a merge order hint naming the shared exported interface.

Expected selector enforcement: unchanged by conflict preflight. Do not claim `tool_enforced`.

Risk / gate: explicit approval is required to parallelize same-group write tasks.

## Scenario 6: Managed Worktree Package Rejection

Prompt:

```text
这些任务里有 read-only review、planning-only、hybrid 调查、一个缺 Goal Contract 的写任务、一个缺 validation package 的写任务，以及一个 expected_output = findings_package 的写任务。请生成 dispatch package，但不要创建 managed worktree。
```

Expected first skill: `dispatch`

Expected behavior:

- Do not generate managed worktree packages for read-only, planning-only, or hybrid pre-split tasks.
- Do not generate managed worktree packages when Goal Contract, source package, validation package, or `expected_output = review_package` is missing.
- A valid `codex_app_managed_worktree_thread` package requires `task_type = write_implementation`, `readiness = ready_for_agent`, `isolation.filesystem = codex_managed_worktree`, complete Goal Contract, source package, validation package, and `expected_output = review_package`.
- Route rejected tasks to `needs_info`, `needs_split`, `main_thread_readonly`, `codex_subagent`, `clean_reviewer`, or human decision as appropriate.

Risk / gate:

Dispatch produces package expectations only. Codex App worktree creation, child thread execution, selector application, lifecycle monitoring, and review package collection belong to an execution-capable runtime adapter described by the internal `codex_app_managed_worktree_thread` contract, not Groundwork dispatch.
