# Groundwork To Runtime Dispatch Scenario

Target Reader: Groundwork eval reviewers and maintainers validating the Phase 1 runtime dispatch workflow.
Reader Action Needed: Use this scenario to check that docs and runtime-routing behavior cover the full accepted flow without claiming execution.
Decision Supported: Whether GW-7 covers PRD AC-15 and Suggested Implementation Issue 7.
Scope: Scenario-level coverage for `to-prd -> to-issues -> triage -> dispatch -> runtime adapter -> verify/triage` and four representative task types.
Out of Scope: Executing subagents, creating Codex App child threads, implementing runtime adapters, remote writes, README exposure, or changing dispatch contracts.
Evidence Level: Scenario derived from `docs/runtime-dispatch-workflow.md`, the dispatch package/result contracts, and the accepted dispatch runtime router PRD.

## Scenario

Given an accepted PRD has been processed by `to-prd`
And `to-issues` has produced vertical work units with acceptance criteria, non-goals, verification evidence, AFK/HITL classification, and runtime candidates
And `triage` has produced readiness decisions, Goal Contract fields for ready agent work, and Preferred Runtime recommendations
When Groundwork runs `dispatch`
Then dispatch produces Dispatch Package v2 entries without executing runtime tools
And each task has exactly one `runtime_id`
And each executable package states validation expectations and expected Result Package type
And Phase 1 policy keeps `remote_writes_allowed = false`
And dispatch does not automatically spawn subagents
And dispatch does not call Codex App thread tools
And dispatch may reference the internal managed worktree adapter contract without executing runtime tools.

## Expected Runtime Matrix

| Example | Task Type | Expected Runtime | Required Output | Return Path |
|---|---|---|---|---|
| Write implementation | `write_implementation` | `codex_app_managed_worktree_thread` | `review_package` | `verify`, then `triage` |
| Read-only review | `read_only_review` | `codex_subagent`, `main_thread_readonly`, or `clean_reviewer` | `findings_package` or `review_findings` | `triage`, with optional `verify` if evidence sufficiency is in scope |
| Hybrid diagnosis | `hybrid` | split first; diagnosis via `codex_subagent` or `main_thread_readonly` | `diagnosis_package` first | `triage`, then optional dispatch of a concrete write task |
| High-risk migration | `write_implementation` | `codex_app_managed_worktree_thread` with conflict preflight and high reasoning request | `review_package` | `verify`, then `triage` |

## Acceptance Checks

- The write implementation example requires a complete Goal Contract, source package, validation package, managed worktree filesystem isolation, and `expected_output = review_package`.
- The read-only review example avoids managed worktree routing and returns findings or reviewer findings instead of a write diff.
- The hybrid diagnosis example requires split-first routing and does not create a managed worktree package before a concrete write subtask exists.
- The high-risk migration example keeps remote writes disabled, requests high reasoning, includes conflict preflight, and serializes conflicting work.
- Result packages return to `verify` for acceptance evidence review and to `triage` for lifecycle state decisions.
- The Phase 1 boundary is explicit: no automatic subagent spawn, no Codex App thread tool execution by Groundwork dispatch, and no remote writes.
- The managed worktree adapter contract may be referenced as an internal dispatch adapter contract, but the scenario does not imply runtime execution.

## Failure Cases

- Fail if dispatch claims that a package was executed without runtime evidence.
- Fail if a read-only review routes to `codex_app_managed_worktree_thread`.
- Fail if hybrid diagnosis is sent to a managed worktree before a concrete write implementation subtask exists.
- Fail if remote writes are enabled by default.
- Fail if Groundwork dispatch claims to create child threads or spawn subagents in Phase 1.
