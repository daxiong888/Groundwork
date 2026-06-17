# Child Thread Prompt Template

## Target Reader

Runtime adapters creating or messaging a Codex App background implementation thread for an admissible Dispatch Package v2 entry.

## Reader Action Needed

Fill this template from the accepted task package and send it to the managed worktree child thread.

## Decision Supported

Whether the child thread received enough source truth, Goal Contract, validation expectation, and scope controls to execute exactly one write task.

## Scope

Prompt construction for an already-admissible managed worktree write implementation package.

## Out of Scope

Package routing, package admissibility, tool discovery, thread creation approval, remote writes, and clean-review approval.

## Evidence Level

Derived from Groundwork Dispatch Package v2, Goal Contract fields, and managed worktree review package requirements.

`goal_contract.goal_command` must already start with `/goal`; do not prepend another `/goal` when filling this template.

```text
{goal_contract.goal_command}

You are working in a Codex App background thread with a Codex-managed worktree.

Coordinator boundary:
- The coordinator/main thread remains coordinator and does not enter Goal Mode.
- This child thread owns only the single implementation task below.
- Return a review package; do not claim clean-review approval.

Task identity:
- Dispatch version: {dispatch_version}
- Runtime ID: codex_app_managed_worktree_thread
- Task ID: {task_id}
- Title: {title}
- Task type: write_implementation
- Readiness: ready_for_agent
- Thread title: {runtime_package.thread_title_or_task_id_title}

Source package:
{source_package}

Goal Contract:
{goal_contract}

Validation package:
{validation}

Execution profile:
- Requested model profile: {execution_profile.model_profile}
- Requested reasoning effort: {execution_profile.reasoning_effort}
- Requested cost/latency bias: {execution_profile.cost_latency_bias}
- Selector enforcement expectation: {execution_profile.selector_enforcement}
- Routing reason: {execution_profile.routing_reason}

Scope controls:
- Allowed files or behavior: {allowed_files_or_behavior}
- Disallowed files or behavior: {disallowed_files_or_behavior}
- Non-goals: {goal_contract.non_goals}
- Approval gates: remote writes and destructive actions are disallowed unless separately approved.

Rules:
- Before editing, verify this task against the source package, Goal Contract, and validation package above.
- Do not use subagents for implementation.
- Do not manually create git worktrees.
- Do not stage, commit, push, open PRs, close issues, archive threads, mutate trackers, or change remote state unless separately approved.
- Do one focused implementation pass, then run the fastest relevant validation.
- If the requested behavior already exists or no code change is needed, do not edit; return a review package with evidence, validation status, and changed files = none.
- If validation exposes an issue introduced by your changes, make only the narrow fix needed for that failure and rerun the relevant validation.
- Do not broaden scope or start unrelated cleanup during validation-fix iterations.
- Do not claim a check passed unless it actually ran.
- Report selector enforcement as tool_enforced only when the model or reasoning selectors were applied by a tool or runtime API; otherwise use prompt_preference, unavailable, or unknown.
- If blocked, stop and report the blocker with evidence.
- The final review package, diff detail, and output transcript must be redacted. Use summarized excerpts when raw content contains secrets, credentials, private URLs, personal data, customer-sensitive data, or unnecessary full logs.

Required final output:
Return exactly the review package shape from REVIEW-PACKAGE-TEMPLATE.md.
The coordinator or adapter must paste the current review package template below this prompt before sending it.
```
