# PRD: Groundwork Router Observability and Self-Improvement Harness

Target Reader: Groundwork maintainers, Codex harness implementers, eval authors, runtime adapter authors, and reviewers deciding how Groundwork should make router decisions observable before adding more routing behavior.

Reader Action Needed: Review and accept, revise, or split this PRD into scoped implementation issues. Use it as the source of truth for a Hook-first router observability increment and the follow-on self-improvement proposal loop.

Decision Supported: Whether Groundwork should add a live observability harness around existing routing and dispatch layers, using Codex hooks for turn-level trace capture, `codex exec --json` for replayable evals, GitHub Actions for optional regression gates, and Codex Automations for periodic proposal-only summaries.

Artifact Type: PRD / architecture decision record.

Source of Truth: Current Groundwork repository guidance, `skills/dispatch/SKILL.md`, `docs/prd-dispatch-runtime-router.md`, `docs/prd-routing-reliability.md`, `docs/skill-success-metrics.md`, `docs/eval-trace-artifacts.md`, `docs/nightly-harness.md`, `evals/run_runtime.py`, `evals/prompts/routing-reliability.csv`, `evals/report.py`, `evals/checks/trace_diagnostics.py`, and official Codex documentation for hooks, non-interactive mode, automations, and GitHub Action.

Scope: Live router decision visibility, turn-level trace capture, reuse of existing routing/verdict vocabulary, local scratch artifacts, redacted promoted artifacts, replay path from real traces into eval rows, proposal-only self-improvement, and harness selection boundaries.

Out of Scope: New public Groundwork skills, learned routing, embedding/reranker service, MCP server, task database, dashboard, automatic skill mutation, automatic PR/issue creation, automatic tracker writes, default subagent spawning, default managed worktree execution, runtime adapter execution, plugin release, marketplace packaging, cache refresh, UAT/customer readiness, or claims that hook traces alone prove release readiness.

Evidence Level: Product design grounded in inspected repository files and official Codex documentation as of 2026-06-27. This PRD does not add runtime evidence, cache/source equivalence evidence, release evidence, UAT evidence, or customer-readiness evidence.

Safe to Share / Redaction Notes: Safe to share as a planning artifact. It contains architecture and schema examples only; no secrets, credentials, PII, private traces, browser logs, or production payloads.

Status: Draft PRD for maintainer review.

Last Updated: 2026-06-27.

---

## 1. Lifecycle Preflight

Intent: product_architecture / harness_planning.

Suggested Workflow Mode: to-prd, then to-issues after acceptance.

Locale: Chinese product discussion; repository identifiers, schema fields, and file paths remain English.

Source of Truth: mixed, with Groundwork repo docs and official Codex documentation as canonical references for their own surfaces.

Requirement State: PRD draft.

Artifact Promotion: required. This document is the durable planning artifact for the router observability workstream.

Execution Topology: local_with_artifact / docs-only branch.

Risk Gate: git_write for documentation branch changes only.

Verification Strategy: source review, line-level diff review, `git diff --check` when implemented locally, and later schema/runtime checks when implementation slices are created.

Lifecycle State: no runtime state change.

Stop Condition: PRD is complete enough to split into implementation issues.

---

## 2. Executive Summary

Groundwork already has router-like behavior. The current problem is not that routing is absent. The problem is that route selection, runtime selection, route hit detection, and contract adherence are still too opaque during normal Codex use.

This PRD defines **Router Observability v0**:

```text
existing Groundwork routing and dispatch decisions
  -> live hook trace
  -> router decision card
  -> shared route/verdict scoring
  -> replayable eval rows
  -> report and patch suggestions
  -> human-reviewed self-improvement proposal
```

The central product decision is:

```text
Router owns semantic decisions.
Harness owns visibility, replay, scoring, and governance.
```

Groundwork should not add another public router skill. Instead, it should expose and score the decisions made by the existing routing reliability layer and the existing `dispatch` runtime router.

The recommended harness order is:

1. **Hooks** for live turn-level observability.
2. **`codex exec --json`** for replayable eval and regression evidence.
3. **GitHub Action** for optional CI regression gates.
4. **Codex Automation** for periodic proposal-only summaries after trace data exists.

Automation should not lead the first implementation. Without live trace and scoring, automation would only summarize another blind box.

---

## 3. Current State

### 3.1 Groundwork Public Surface

Groundwork's repository guidance says the public skill surface is intentionally small and currently includes `to-prd`, `to-issues`, `triage`, `write-plan`, `prototype`, `implement`, `verify`, `handoff`, `dispatch`, and `wiki`.

This PRD does not add a public skill.

### 3.2 Dispatch Runtime Router Exists

`dispatch` is already a public skill for runtime routing and package generation. It is scoped to runtime selection and package-only handoff for routes such as:

```text
codex_app_managed_worktree_thread
codex_subagent
main_thread_direct
main_thread_readonly
clean_reviewer
```

It must not execute runtime tools, create child threads, spawn subagents, write files in target runtimes, mutate remotes, or claim runtime execution happened.

### 3.3 Routing Reliability Layer Exists

`docs/prd-routing-reliability.md` already defines a Groundwork Entry Contract that decides:

```text
Should this prompt stay direct, or does it need a Groundwork workflow?
If workflow is needed, which existing public skill owns the first step?
What stop condition prevents unsafe downstream action?
```

It also defines route vocabulary, expected/acceptable/forbidden routes, host-preemption classification, output/evidence/behavior verdicts, and route-pair reporting.

### 3.4 Runtime Eval Runner Exists

`evals/run_runtime.py` already runs Codex via `codex exec --ephemeral --json`, captures logs/final output/changed files, classifies actual route, runs verdict dimensions, and emits `results.jsonl`, `summary.json`, per-case JSON, and routing summaries.

This is a strong offline eval harness, but it is not yet a live interactive observability harness.

### 3.5 Trace/Report/Proposal Scaffolding Exists

Groundwork already has:

- trace artifact policy in `docs/eval-trace-artifacts.md`;
- nightly harness boundary in `docs/nightly-harness.md`;
- metrics vocabulary in `docs/skill-success-metrics.md`;
- report generation in `evals/report.py`;
- trace diagnostics in `evals/checks/trace_diagnostics.py`.

The missing product layer is a live trace path that turns normal Codex sessions into route-scored evidence.

---

## 4. Problem Statement

The user-visible pain is:

```text
Groundwork has done a lot of design,
but during actual Codex use it is unclear whether Codex recognized the design,
which router decision was made,
which skill or runtime was actually hit,
and whether the selected contract shaped the final behavior.
```

This creates four specific problems.

### 4.1 Router Choice Is a Blind Box

A route may be selected correctly or incorrectly, but the user does not see the decision object:

```text
intent_kind
requirement_state
source_truth
risk_gate
expected_best
acceptable_routes
forbidden_routes
expected_stop_condition
```

The user only sees the eventual assistant response.

### 4.2 Actual Hit Detection Is Mostly Post-hoc

Current eval code can infer `actual_route` from runtime output markers, final response, and changed-file evidence. That is valuable for evals, but normal interactive use still lacks a stable live trace that records:

- expected first route before the model acts;
- whether a public skill was actually loaded;
- whether multiple skills were touched;
- whether a runtime route was proposed;
- whether the result obeyed output, evidence, and behavior contracts.

### 4.3 Routing and Execution Failures Are Easy to Confuse

A bad outcome may be caused by:

- wrong route;
- forbidden route;
- right route but wrong output shape;
- missing evidence;
- invalid host preemption;
- tool/runtime block;
- behavior violation;
- missing artifact promotion or redaction boundary.

Without per-turn verdicts, these collapse into a vague feeling that Groundwork was not used.

### 4.4 Self-Improvement Has No Trustworthy Live Sample Feed

Groundwork can generate patch suggestions only when failures are reproducible, scoped, and reviewable. If live sessions do not emit a normalized route/score artifact, self-improvement must rely on memory, manual anecdotes, or sparse eval fixtures.

---

## 5. Product Goals

1. Make every Groundwork-relevant Codex turn explainable with a compact Router Decision Card.
2. Reuse existing route and verdict vocabulary instead of inventing a parallel taxonomy.
3. Capture live traces safely in ignored local scratch by default.
4. Keep promoted artifacts redacted, reviewable, and explicitly non-release evidence unless separate runtime/cache evidence exists.
5. Separate router decision, runtime decision, tool behavior, output contract, evidence contract, and behavior contract.
6. Make `dispatch` runtime decisions visible without turning `dispatch` into an executor.
7. Convert repeated live failures into regression rows and proposal-only patch suggestions.
8. Allow Codex Automation to summarize evidence only after hooks and eval replay produce trustworthy artifacts.
9. Preserve Groundwork's public skill surface and evidence-first governance.
10. Avoid broad dashboards or databases until local trace/report artifacts prove the need.

---

## 6. Non-Goals

This workstream must not:

- add a new public `router`, `observability`, `monitor`, or `self-improve` skill;
- replace existing `routing-reliability` or `dispatch` decisions;
- claim Codex host internals that hooks do not expose;
- rely on transcript format as a stable API;
- auto-edit skill docs based on trace failures;
- auto-apply patch suggestions;
- create, update, or close tracker issues automatically;
- create PRs automatically;
- mutate `main` automatically;
- write committed raw traces;
- commit ignored `.groundwork` scratch output;
- collect secrets, cookies, browser logs, PII, or private payloads into durable artifacts;
- claim release, UAT, customer, runtime, cache, or marketplace readiness from hooks, score JSON, reports, or this PRD alone;
- default to subagents or managed worktrees for observability tasks;
- make Codex Automation the first-line monitor before live traces exist.

---

## 7. Users and User Stories

### 7.1 Groundwork Maintainer

As a maintainer, I want each Codex session to leave behind a compact route/score artifact, so I can tell whether a failure came from routing, contract adherence, evidence collection, or runtime behavior.

### 7.2 Daily Groundwork User

As a daily user, I want to see why Groundwork chose a workflow and whether Codex actually used it, so I do not have to infer routing from the final answer.

### 7.3 Eval Author

As an eval author, I want to convert real blind-box failures into regression rows with `expected_best`, `acceptable_routes`, `forbidden_routes`, `output_contract`, and `evidence_required`, so failures become reproducible.

### 7.4 Runtime Adapter Author

As a runtime adapter author, I want dispatch decisions and result expectations to be recorded separately from execution traces, so runtime routing can be reviewed without falsely claiming execution.

### 7.5 Future Automation Reviewer

As an automation reviewer, I want daily or weekly summaries to cite trace scores and eval artifacts, so automation output is proposal evidence rather than unsupported model opinion.

---

## 8. Core Concepts

### 8.1 Entry Decision

The Entry Decision is the pre-skill semantic decision for a turn.

Minimum shape:

```json
{
  "route": "direct | to-prd | to-issues | triage | write-plan | prototype | implement | verify | handoff | dispatch | wiki",
  "requirement_state": "raw | grilled | prd_draft | prd_accepted | issue_ready | implementation_ready | verified | blocked",
  "source_truth": "conversation | accepted_prd | local_artifact | external_issue | source_code | test_evidence | runtime_evidence | state_md | mixed | unknown",
  "stop_condition": "continue | ask_clarification | require_prd_acceptance | require_artifact_promotion | require_gate | direct_answer | blocked"
}
```

### 8.2 Intent Frame

The Intent Frame is the semantic object being routed. It should reuse the existing fields from routing reliability:

```text
intent_kind
requirement_state
source_truth
risk_gate
expected_state_transition
expected_stop_condition
route_boundary
case_kind
case_source
```

For live hooks, `case_kind` and `case_source` may use live-only values if added through schema review, for example:

```text
case_kind = live_observation
case_source = user_session
```

If schema expansion is deferred, live artifacts may store these as metadata outside eval-row schema until backfilled into CSV fixtures.

### 8.3 Router Decision Card

A Router Decision Card is the human-readable summary of expected route, actual route, verdicts, failure type, and fix locus.

It is not a dashboard. It is a compact per-turn artifact.

Minimum card:

```text
Groundwork Router Decision

Expected first route: write-plan
Actual route: implement
Route boundary: requirement-state-vs-implementation
Runtime route: not_applicable

Verdicts:
- routing_verdict: fail
- host_preemption_verdict: not_applicable
- output_contract_verdict: pass
- evidence_verdict: fail
- behavior_verdict: fail
- overall_verdict: fail

Failure:
- failure_type: route_miss
- fix_locus: routing_surface

Why:
- User asked for a plan and no file edits.
- Actual route entered implementation path.
- No-file-change evidence was required.
```

### 8.4 Runtime Decision Card

When `dispatch` is involved, the card must also expose the runtime decision without claiming execution:

```text
Dispatch Runtime Decision

Task: RR-007
Task type: write_implementation
Runtime: codex_app_managed_worktree_thread
Route decision: worktree_isolated
Isolation: codex_managed_worktree
Selector enforcement: prompt_preference | unknown | tool_enforced
Result package expected: review_package
Execution status: not_executed_by_dispatch
```

### 8.5 Groundwork Turn Trace

A Groundwork Turn Trace is a local scratch record for one Codex turn. It ties together:

```text
prompt input
entry decision
optional dispatch decision
tool events
permission or risk events
final assistant message
changed file snapshot
router score
router card
```

It should live under ignored local scratch by default.

### 8.6 Router Score

A Router Score is a machine-readable verdict for one turn. It should reuse the existing verdict dimensions:

```text
routing_verdict
host_preemption_verdict
output_contract_verdict
evidence_verdict
behavior_verdict
overall_verdict
failure_type
fix_locus
notes
```

### 8.7 Self-Improvement Proposal

A Self-Improvement Proposal is a review artifact created from repeated failures. It may suggest docs, eval, frontmatter, or runner changes, but it must not auto-apply them.

It must include:

```text
problem
observed failures
route-pair confusion
failure_type counts
fix_locus hypothesis
affected files
proposed patch scope
new or updated eval rows
rollback
human decision
```

---

## 9. Harness Architecture

### 9.1 Layer Map

```text
Layer 0: Groundwork source contracts
  - skill docs
  - routing reliability PRD
  - dispatch PRD
  - eval schemas

Layer 1: Live hook capture
  - SessionStart
  - UserPromptSubmit
  - PreToolUse / PermissionRequest
  - PostToolUse
  - Stop

Layer 2: Shared routing and verdict model
  - routing schema
  - route detection
  - output/evidence/behavior checks
  - summary metrics

Layer 3: Replayable eval harness
  - codex exec --json
  - routing-reliability.csv
  - focused runtime evals
  - trace-derived regression rows

Layer 4: Reports and proposals
  - report.md
  - patch-suggestions.json
  - self-improvement proposal

Layer 5: Governance harnesses
  - optional GitHub Action gate
  - periodic Codex Automation summary
  - human review
```

### 9.2 Harness Selection Matrix

| Harness | Primary Role | Use First For | Do Not Use For |
| --- | --- | --- | --- |
| Codex Hooks | Live observability | per-turn trace, entry decision, tool/evidence capture, Stop-time score | auto-patching, background aggregation, learned routing |
| `codex exec --json` | Replayable eval | focused regression, baseline, fixture replay, route-pair confusion | live explanation for interactive sessions |
| GitHub Action | CI gate | schema checks, deterministic checker tests, optional PR regression gate | turn-level monitoring |
| Codex Automation | Periodic proposal summary | daily/weekly drift report after traces exist | first-line monitor, automatic skill edits |
| Managed worktree | Isolated implementation | ready write tasks with durable diff | read-only observability |
| Subagent | Parallel read-only lens | review, diagnosis, failure clustering | final verifier for own work, default file mutation |
| MCP/App Server/SDK | Future integration | cross-surface service or adapter backend | v0 local blind-box reduction |

### 9.3 Why Hook First

Hooks run at the point where the blind box occurs: before and after a Codex turn and around tool use. They can expose the expected route before action, and then score the final behavior after action.

Hooks must remain conservative:

- use command handlers only;
- avoid relying on async handlers;
- avoid assuming transcript format stability;
- avoid broad blocking behavior;
- avoid Stop continuation loops;
- write local scratch artifacts first;
- use `systemMessage` or additional context only for compact route hints and warnings.

### 9.4 Why Automation Later

Automations are useful after there is evidence to summarize. They are not the source of truth for per-turn route choice.

Recommended future automation:

```text
$groundwork-router-drift-report

Cadence: daily or weekly.
Input: recent redacted router-score.json and summary artifacts.
Output: report and proposal-only suggestions.
Allowed writes: local report artifact only, if explicitly configured.
Forbidden: skill mutation, branch mutation, PR creation, tracker mutation.
```

---

## 10. Functional Requirements

### FR-1: Extract Shared Routing/Verdict Library

Groundwork should extract reusable route and verdict code from `evals/run_runtime.py` before hooks duplicate logic.

Proposed modules:

```text
evals/routing_schema.py
evals/route_detection.py
evals/verdict_model.py
evals/routing_summary.py
```

Required behavior:

- preserve current `evals/run_runtime.py` CLI behavior;
- preserve `results.jsonl`, `summary.json`, and `routing_summary` compatibility;
- keep existing failure type and fix locus vocabulary stable unless docs are updated;
- expose pure functions that hooks can call without invoking Codex runtime;
- avoid new runtime dependencies unless accepted in implementation issues.

Acceptance criteria:

- Unit tests cover old and new import paths.
- `evals/run_runtime.py --validate-schema` still works.
- Existing routing summary fields remain backward compatible.
- Hooks can import the shared library without executing a runtime eval.

### FR-2: Define Live Trace Scratch Layout

Add a policy target for live router observability scratch output:

```text
.groundwork/harness/router-observability/<session-id>/<turn-id>/
  prompt.json
  router-decision.json
  dispatch-decision.json          # optional
  tool-events.jsonl
  permission-events.jsonl
  file-snapshot-before.json       # optional / path-only by default
  file-snapshot-after.json        # optional / path-only by default
  final.txt
  router-score.json
  router-card.md
  diagnostics.json                # optional
```

Rules:

- This directory is ignored local scratch.
- Raw traces are not committed.
- Raw command output, browser logs, private payloads, cookies, and secrets must not be promoted.
- Promoted artifacts must follow `docs/eval-trace-artifacts.md`.

Acceptance criteria:

- Layout is documented.
- Redaction boundary is explicit.
- No implementation commits `.groundwork/harness` runtime output.

### FR-3: UserPromptSubmit Entry Decision Hook

Implement a repo-local hook script for `UserPromptSubmit` that computes and records an Entry Decision before Codex acts.

Proposed file:

```text
.codex/hooks/user_prompt_submit_groundwork_entry.py
```

Input:

- hook JSON stdin;
- `prompt`;
- `cwd`;
- optional repository state inspection;
- optional existing Groundwork artifacts.

Output:

- `router-decision.json` in local scratch;
- optional JSON hook output with `hookSpecificOutput.additionalContext` containing a compact route hint.

The additional context must be short and bounded, for example:

```text
Groundwork route hint: expected first route write-plan; no file edits expected; use scope, assumptions, steps, verification, risks, handoff boundary.
```

Acceptance criteria:

- Hook can run in dry mode from stdin fixture.
- Hook never writes committed repository files except local scratch.
- Hook does not block normal prompts by default.
- Hook can be disabled by config or environment variable.
- Hook records `expected_best`, `acceptable_routes`, `forbidden_routes`, `route_boundary`, and source of inference when known.

### FR-4: Tool and Permission Event Capture

Implement hook scripts for tool and permission events.

Proposed files:

```text
.codex/hooks/pre_tool_use_groundwork_trace.py
.codex/hooks/permission_request_groundwork_trace.py
.codex/hooks/post_tool_use_groundwork_trace.py
```

Captured fields:

```json
{
  "session_id": "...",
  "turn_id": "...",
  "hook_event_name": "PostToolUse",
  "tool_name": "Bash",
  "risk_markers": ["git_write"],
  "evidence_markers": ["git_status"],
  "status": "pass | fail | unknown",
  "redaction": {
    "status": "not_reviewed",
    "notes": []
  }
}
```

Rules:

- Store only the minimum needed for scoring.
- Prefer command category and evidence markers over raw output.
- Never store secrets or full private payloads by default.
- If raw output is needed for local debugging, keep it scratch-only and redaction-required.

Acceptance criteria:

- Tool events are append-only JSONL.
- Tool capture is robust when fields are absent.
- Secret-looking values are redacted or omitted.
- Evidence markers are compatible with existing `trace_diagnostics.py` where possible.

### FR-5: Stop-Time Router Score Hook

Implement a Stop hook that scores the turn after Codex produces a final assistant message.

Proposed file:

```text
.codex/hooks/stop_groundwork_score.py
```

Inputs:

- `router-decision.json`;
- `tool-events.jsonl`;
- `permission-events.jsonl`;
- final assistant message from hook input when available;
- changed-file snapshot if available;
- optional runtime stdout/final file for replay mode.

Outputs:

- `final.txt`;
- `router-score.json`;
- `router-card.md`;
- optional `systemMessage` when a severe failure is detected.

Stop hook behavior:

- It should not auto-continue by default.
- Continuation should be gated behind an explicit opt-in and loop guard.
- Severe failures may be surfaced as a warning, not as hidden mutation.

Acceptance criteria:

- Correctly classifies `route_miss`, `forbidden_route`, `output_contract_failure`, `evidence_failure`, `invalid_host_preemption`, and `forbidden_behavior` when fixture data supports it.
- Writes a human-readable card for every scored turn.
- Does not claim release readiness or runtime readiness.
- Does not modify user code.

### FR-6: Dispatch Runtime Decision Observability

When `dispatch` is selected or mentioned, observability must record runtime route decisions separately from entry route decisions.

Required fields:

```json
{
  "dispatch_version": 2,
  "task_id": "...",
  "task_type": "write_implementation | read_only_review | planning_only | hybrid | diagnosis | verification | direct",
  "runtime_id": "codex_app_managed_worktree_thread | codex_subagent | main_thread_direct | main_thread_readonly | clean_reviewer",
  "route_decision": "local_direct | local_with_artifact | worktree_isolated | worktree_review_only | automation_candidate",
  "selector_enforcement": "tool_enforced | prompt_preference | unavailable | unknown",
  "capability_status": "known | unknown | user_supplied | docs_reference | tool_enforced",
  "expected_result_package": "review_package | findings_package | diagnosis_package | direct_result | review_findings",
  "execution_claim": "not_executed_by_dispatch"
}
```

Rules:

- Dispatch may produce package expectations.
- Dispatch observability must not imply execution.
- Runtime adapter execution evidence must be separate.
- `automation_candidate` remains recommendation-only unless a future accepted issue explicitly implements an automation adapter.

Acceptance criteria:

- Router card shows dispatch route and execution boundary when dispatch is involved.
- `dispatch` failures are separable from public skill entry failures.
- No dispatch hook creates worktrees, subagents, automations, PRs, issues, commits, or pushes.

### FR-7: Trace-Derived Regression Row Generator

Add a command or script that converts a reviewed router-score failure into a draft eval row.

Possible command:

```text
python3 evals/router_observability/backfill_row.py --score <router-score.json>
```

Output:

- CSV row draft for `evals/prompts/routing-reliability.csv`; or
- markdown proposal with row fields if direct CSV mutation is deferred.

Required fields:

```text
id
route_boundary
case_kind
case_source
intent_kind
requirement_state
source_truth
risk_gate
expected_state_transition
expected_stop_condition
expected_best
acceptable_routes
forbidden_routes
input_scenario
expected_behavior
forbidden_behavior
output_contract
evidence_required
```

Acceptance criteria:

- Does not mutate CSV by default.
- Produces a complete row draft or explains missing fields.
- Marks real user traces as redacted/summarized; never copies sensitive prompt payloads without review.

### FR-8: Report Integration

Extend `evals/report.py` or add a companion report assembler that can read router observability scratch or promoted artifacts.

Report sections:

```text
Run Metadata
Route Metrics
Route Pair Confusion
Forbidden Route Hits
Output/Evidence/Behavior Failures
Dispatch Runtime Decisions
Trace Diagnostics
Top Regressions
Patch Suggestions
Limitations
```

Acceptance criteria:

- Existing eval report behavior remains intact.
- Reports can include live router-score artifacts after redaction review.
- Reports preserve evidence boundaries.

### FR-9: Proposal-Only Patch Suggestions

Generate patch suggestions from repeated failure clusters only after there are reproducible traces or eval rows.

Suggestion shape:

```json
{
  "suggestion_id": "router-observability-001",
  "failure_type": "route_miss",
  "fix_locus": "routing_surface",
  "affected_files": ["skills/implement/SKILL.md", "evals/prompts/routing-reliability.csv"],
  "problem": "Raw requirement urgency was treated as implementation bypass.",
  "evidence": ["score path or eval row id"],
  "proposed_change": "Add hard-negative row and minimal trigger wording adjustment.",
  "rollback": "Revert affected docs/eval row change.",
  "auto_apply": false,
  "human_decision": "none"
}
```

Acceptance criteria:

- `auto_apply` is always false.
- Suggestions name affected files and rollback.
- Suggestions distinguish eval-row additions from runtime-visible text changes.
- Suggestions do not open PRs, push branches, mutate trackers, or edit skills automatically.

### FR-10: Codex Automation Summary

After live trace and report artifacts exist, define an optional automation prompt for periodic router drift summaries.

Automation input:

- recent promoted reports; or
- local scratch summaries if the user explicitly allows local access.

Automation output:

- drift summary;
- top route-pair confusion;
- repeated failure clusters;
- candidate regression rows;
- patch suggestions with `auto_apply=false`;
- missing evidence list.

Acceptance criteria:

- Automation is optional and not required for v0 live observability.
- Automation does not become the source of truth for route decisions.
- Automation cannot claim runtime, cache, release, UAT, or customer readiness.
- Automation prompt includes stop conditions and no-mutation boundaries.

### FR-11: Optional GitHub Action Gate

A later implementation may add or update GitHub Action checks for source validation and optional runtime eval.

Recommended gate levels:

```text
Level 1: schema/source only
  - JSON schema validation
  - CSV parse
  - deterministic checker unit tests

Level 2: focused runtime eval, optional
  - requires explicit OpenAI key and runner policy
  - records installed plugin/source/cache boundary

Level 3: release evidence, deferred
  - requires cache/source equivalence or supported refresh
  - requires baseline artifact and limitation statement
```

Acceptance criteria:

- Source-only CI does not imply runtime readiness.
- Runtime eval is opt-in and evidence-bound.
- PR checks fail on forbidden route hits, invalid host preemption, or unclassified non-pass only when the relevant gate is explicitly enabled.

---

## 11. Data Model

### 11.1 `router-decision.json`

```json
{
  "schema_version": "router_observability.v0",
  "session_id": "...",
  "turn_id": "...",
  "created_at": "2026-06-27T00:00:00Z",
  "cwd": "...",
  "entry_decision": {
    "expected_best": "write-plan",
    "acceptable_routes": ["write-plan"],
    "forbidden_routes": ["implement", "verify", "direct"],
    "route_boundary": "entry-contract",
    "intent_kind": "plan",
    "requirement_state": "issue_ready",
    "source_truth": "local_artifact",
    "risk_gate": "none",
    "expected_state_transition": "plan",
    "expected_stop_condition": "continue"
  },
  "decision_evidence": [
    {
      "kind": "prompt_marker",
      "value": "先别写代码"
    }
  ],
  "confidence": "high | medium | low | unknown",
  "limitations": []
}
```

### 11.2 `tool-events.jsonl`

Each row:

```json
{
  "schema_version": "router_observability.tool_event.v0",
  "session_id": "...",
  "turn_id": "...",
  "event_index": 1,
  "hook_event_name": "PostToolUse",
  "tool_name": "Bash",
  "command_class": "git | test | file_read | file_write | browser | unknown",
  "risk_markers": ["git_write"],
  "evidence_markers": ["git_status"],
  "status": "pass | fail | blocked | unknown",
  "redaction": {
    "status": "not_reviewed",
    "notes": []
  }
}
```

### 11.3 `router-score.json`

```json
{
  "schema_version": "router_observability.score.v0",
  "session_id": "...",
  "turn_id": "...",
  "expected_route": "write-plan",
  "actual_route": "implement",
  "acceptable_routes": ["write-plan"],
  "forbidden_routes": ["implement", "verify", "direct"],
  "routing_verdict": "fail",
  "host_preemption_verdict": "not_applicable",
  "output_contract_verdict": "pass",
  "evidence_verdict": "fail",
  "behavior_verdict": "fail",
  "overall_verdict": "fail",
  "failure_type": "route_miss",
  "fix_locus": "routing_surface",
  "changed_files": [],
  "skill_hits": [],
  "dispatch_decisions": [],
  "notes": "expected route write-plan, loaded implement",
  "evidence_boundary": "local hook score only; not release evidence"
}
```

### 11.4 `router-card.md`

Required sections:

```text
Groundwork Router Decision
Input Summary
Expected Route
Actual Route
Dispatch Runtime Decision, if applicable
Verdicts
Failure Classification
Evidence Used
Limitations
Next Suggested Action
```

### 11.5 Self-Improvement Proposal

Recommended markdown shape:

```markdown
# Groundwork Self-Improvement Proposal

Target Reader:
Reader Action Needed:
Evidence Boundary:

## Problem
## Evidence
## Failure Cluster
## Route Pair Confusion
## Fix Locus
## Proposed Change
## Files Affected
## Eval Backfill
## Rollback
## Risks
## Human Decision
```

---

## 12. Routing and Dispatch Scoring Rules

### 12.1 Route Selection Pass

A route selection passes when:

- `actual_route == expected_best`; or
- `actual_route` is in `acceptable_routes`; and
- `actual_route` is not in `forbidden_routes`; and
- host preemption is valid or not applicable.

### 12.2 Best Route Still Matters

`acceptable_routes` may allow safe alternatives, but `best_route_hit_at_1` remains a trend signal. Broadening acceptable routes must not hide unclear ownership.

### 12.3 Forbidden Route Hit

A forbidden route hit fails even when the final answer looks plausible.

Example:

```text
Expected: write-plan
Forbidden: implement
Actual: implement
Result: fail, even if the implementation was competent
```

### 12.4 Right Route, Wrong Path

If the right skill is selected but output/evidence/behavior contracts fail, the route verdict may pass while overall verdict fails.

Example:

```text
Expected route: verify
Actual route: verify
Output contract: fail because response does not start with Verification Scope
Overall: fail
Fix locus: skill_output_contract
```

### 12.5 Dispatch Does Not Execute

A dispatch decision is scored for package correctness, runtime fit, capability evidence, selector enforcement transparency, and result expectation.

It is not scored as execution evidence unless a runtime adapter separately reports execution.

---

## 13. Hook Behavior Boundaries

Official Codex hook behavior imposes product constraints that this PRD must respect.

### 13.1 Command Handlers Only

The first implementation should use command hooks only. It must not depend on prompt or agent hook handlers.

### 13.2 No Async Hook Assumption

Do not rely on async command hooks. Treat hook work as bounded and fast.

### 13.3 Concurrent Matching Hooks

Multiple matching hooks may run for the same event. A Groundwork hook must not assume it can serialize all other hooks or prevent another matching hook from starting.

### 13.4 Transcript Is Convenient, Not Stable

Hook input may include `transcript_path`, but transcript format should not be treated as a stable API. Prefer hook input fields, generated scratch artifacts, and explicit final message fields where available.

### 13.5 Stop Hook Loop Guard

A Stop hook can request continuation. Groundwork should not do that by default. If continuation is enabled later, it must have:

- per-turn loop guard;
- max continuation count;
- explicit reason;
- no file mutation by the hook itself;
- clear user-visible warning.

---

## 14. Privacy, Redaction, and Artifact Promotion

### 14.1 Default Storage

Live trace output belongs in local scratch:

```text
.groundwork/harness/router-observability/
```

It must not be committed.

### 14.2 Promotion Boundary

Promoted artifacts belong under:

```text
artifacts/evals/<run-id>/
```

only after review and redaction. Promotion is optional and should be minimal.

### 14.3 Forbidden Promoted Content

Promoted artifacts must not include:

- secrets;
- credentials;
- tokens;
- cookies;
- private keys;
- PII;
- private URLs unless explicitly approved;
- raw browser logs;
- production payloads;
- unredacted command output with sensitive paths or payloads.

### 14.4 Evidence Boundary

Hook traces, score JSON, router cards, and reports are review evidence. They are not release, runtime, UAT, customer, marketplace, or cache-refresh evidence unless separate evidence is named.

---

## 15. Success Metrics

### 15.1 Live Observability Metrics

- Percentage of Groundwork-relevant turns with `router-decision.json`.
- Percentage of scored turns with `router-score.json`.
- Percentage of scored turns with `actual_route != unknown`.
- Percentage of non-pass turns with `failure_type` and `fix_locus` populated.
- Median hook overhead per event.
- Count of hook failures by event type.
- Count of traces blocked from promotion by redaction policy.

### 15.2 Routing Metrics

Reuse existing routing summary metrics:

- `best_route_hit_at_1`;
- `acceptable_route_coverage`;
- `forbidden_route_hits`;
- `invalid_host_preemption`;
- `route_pair_confusion`;
- `verdict_dimension_counts`;
- `failure_type_counts`;
- `unclassified_nonpass`.

### 15.3 Self-Improvement Metrics

- Number of live failures converted into reviewed regression rows.
- Number of patch suggestions generated.
- Number of patch suggestions accepted, rejected, or deferred.
- Number of accepted patches with focused eval evidence.
- Number of repeated failures after a patch.

### 15.4 Safety Metrics

- Zero committed raw trace files.
- Zero committed `.groundwork/harness` runtime scratch output.
- Zero automatic skill mutations.
- Zero automatic tracker/PR/remote mutations.
- Zero release readiness claims without runtime/cache evidence.

---

## 16. Implementation Plan

### RO-001: Accept Router Observability PRD

Goal: Accept this PRD or revise it until it is ready for issue slicing.

Touch targets:

```text
docs/prd-router-observability-and-self-improvement.md
```

Acceptance criteria:

- PRD explains why this is observability around existing routers, not a new public router.
- PRD assigns harness roles to hooks, `codex exec`, GitHub Action, and Automation.
- PRD defines data artifacts and redaction boundary.
- PRD contains enough detail for issue slicing.

Verification:

- Markdown review.
- `git diff --check` when local checkout is available.

### RO-002: Extract Shared Route/Verdict Modules

Goal: Split route schema, route detection, verdict model, and summary metrics from `evals/run_runtime.py` into reusable modules.

Touch targets:

```text
evals/routing_schema.py
evals/route_detection.py
evals/verdict_model.py
evals/routing_summary.py
evals/run_runtime.py
evals/test_*.py
```

Acceptance criteria:

- Runner behavior remains backward compatible.
- Existing routing-reliability suite validates.
- Shared modules expose pure functions usable by hooks.
- No Codex runtime invocation is needed for unit tests.

Verification:

- CSV/schema validation.
- Unit tests for extracted modules.
- Focused runner dry validation.

### RO-003: Document Hook Configuration and Trace Layout

Goal: Add maintainer docs for enabling/disabling hooks and handling local trace scratch.

Touch targets:

```text
docs/router-observability-harness.md
docs/eval-trace-artifacts.md   # only if needed
```

Acceptance criteria:

- Documents hook install/config pattern.
- Documents scratch layout and redaction boundary.
- Documents how to disable hooks.
- Does not require global Codex config mutation in repo tests.

Verification:

- Markdown review.
- Redaction policy review.

### RO-004: Implement UserPromptSubmit Dry Hook

Goal: Create first hook that records Entry Decision and optionally injects compact additional context.

Touch targets:

```text
.codex/hooks/user_prompt_submit_groundwork_entry.py
evals/fixtures/router-observability/
evals/test_router_observability_hooks.py
```

Acceptance criteria:

- Reads hook JSON from stdin.
- Writes `router-decision.json` to local scratch.
- Produces compact additional context when enabled.
- Has dry-run tests with fixture prompts.
- Does not modify source files or committed artifacts at runtime.

Verification:

- Unit tests.
- Manual dry-run with fixture JSON.

### RO-005: Implement Tool Event Capture Hooks

Goal: Capture tool and permission events as redaction-aware JSONL markers.

Touch targets:

```text
.codex/hooks/pre_tool_use_groundwork_trace.py
.codex/hooks/permission_request_groundwork_trace.py
.codex/hooks/post_tool_use_groundwork_trace.py
evals/test_router_observability_hooks.py
```

Acceptance criteria:

- Appends JSONL events.
- Records command class, risk markers, and evidence markers.
- Avoids raw output by default.
- Handles missing fields gracefully.

Verification:

- Unit tests with synthetic hook inputs.
- Redaction fixture checks.

### RO-006: Implement Stop Scoring Hook

Goal: Score a turn at Stop using shared verdict logic and write router card.

Touch targets:

```text
.codex/hooks/stop_groundwork_score.py
evals/test_router_observability_hooks.py
evals/test_verdict_model.py
```

Acceptance criteria:

- Reads prior decision and event artifacts.
- Produces `router-score.json` and `router-card.md`.
- Uses shared route/verdict model.
- Does not auto-continue by default.
- Has fixture coverage for pass, route miss, forbidden route, evidence failure, and output contract failure.

Verification:

- Unit tests.
- Manual dry-run fixture.

### RO-007: Add Trace-Derived Eval Row Drafting

Goal: Draft regression rows from reviewed router-score failures.

Touch targets:

```text
evals/router_observability/backfill_row.py
docs/router-observability-harness.md
evals/test_router_observability_backfill.py
```

Acceptance criteria:

- Generates complete row drafts or reports missing fields.
- Does not mutate CSV by default.
- Preserves redaction boundary.
- Supports human review.

Verification:

- Unit tests.
- Fixture score-to-row conversion.

### RO-008: Integrate Reports and Patch Suggestions

Goal: Include router observability artifacts in reports and proposal-only suggestions.

Touch targets:

```text
evals/report.py
evals/patch_suggestions.py     # if created
schemas/*                      # only if score schema extension is needed
docs/skill-success-metrics.md  # only if metrics vocabulary changes
```

Acceptance criteria:

- Report can include route decision cards and live scores.
- Patch suggestions remain `auto_apply=false`.
- Reports preserve evidence boundaries.
- Existing report behavior remains backward compatible.

Verification:

- Report fixture tests.
- Schema validation if schemas change.

### RO-009: Define Optional Automation Prompt

Goal: Add a maintained prompt/template for periodic router drift summary.

Touch targets:

```text
docs/router-observability-automation.md
```

Acceptance criteria:

- Prompt reads existing trace/report artifacts.
- Prompt produces proposal-only summary.
- Prompt forbids automatic mutation.
- Prompt explains local vs worktree automation risks.

Verification:

- Documentation review.
- No runtime automation is created by this issue.

### RO-010: Optional CI Gate Decision

Goal: Decide whether router observability checks enter CI.

Touch targets:

```text
.github/workflows/evals.yml    # only if accepted
docs/ci-eval-gate.md           # if workflow change is deferred
```

Acceptance criteria:

- Source-only checks do not imply runtime readiness.
- Optional runtime gate requires explicit secrets/runtime setup.
- Gate behavior is documented.

Verification:

- CI syntax/source review if workflow is touched.
- Local schema/unit checks.

---

## 17. Migration Strategy

### Phase 0: PRD Acceptance

Accept this document and split issues.

### Phase 1: Shared Library Before Hooks

Extract route/verdict code first so hooks and runner share one model.

### Phase 2: Hook Dry Mode

Implement hooks with fixture tests and local scratch writes. Do not enable blocking or continuation.

### Phase 3: Live Local Trial

Run hooks locally for a small number of real Groundwork sessions. Collect router cards and score JSON in scratch.

Trial evidence must record:

- source branch;
- local checkout path;
- hook config used;
- trace scratch path;
- whether raw traces were promoted;
- limitations.

### Phase 4: Replay and Backfill

Convert reviewed real failures into routing-reliability row drafts. Add only redacted and reviewable cases.

### Phase 5: Proposal Loop

Generate patch suggestions from repeated failures. Apply only through normal reviewed PR flow.

### Phase 6: Optional Automation and CI

Only after live trace and replay paths are stable, add optional Automation summary and CI gates.

---

## 18. Risks and Mitigations

### Risk: Hooks Become Another Blind Box

Mitigation: Every hook writes transparent JSON and a card. Hook failures are recorded. Hook output is never the only source of truth.

### Risk: Hook Overhead Slows Codex

Mitigation: Keep hooks standard-library only, bounded, and marker-based. Avoid heavy file scans. Add timing fields.

### Risk: Transcript Format Changes

Mitigation: Do not depend on transcript format as stable API. Prefer hook input fields and generated artifacts.

### Risk: Sensitive Data Enters Artifacts

Mitigation: Scratch by default, redaction-required promotion, omit raw output unless explicitly needed, and reuse trace artifact policy.

### Risk: Stop Hook Causes Loops

Mitigation: No continuation by default. Future continuation requires explicit opt-in and loop guard.

### Risk: Automation Mutates Groundwork

Mitigation: Automation prompt is proposal-only. It may not edit skills, open PRs, mutate trackers, or write remotes.

### Risk: Acceptable Routes Hide Ownership Drift

Mitigation: Continue reporting Best-route Hit@1 and route-pair confusion. Acceptable routes require review.

### Risk: Dispatch Observability Implies Execution

Mitigation: Runtime Decision Card includes `execution_claim: not_executed_by_dispatch` unless runtime adapter evidence exists.

---

## 19. Open Questions

No blocking open questions for PRD acceptance.

Deferred implementation questions:

1. Whether live-only `case_kind` / `case_source` tokens should be added to schema or kept outside eval rows until backfill.
2. Whether hook scripts should live under `.codex/hooks/` or `scripts/codex-hooks/` with `.codex/hooks/` examples.
3. Whether Stop hook warnings should use `systemMessage` for all non-pass results or only severe failures.
4. Whether changed-file snapshots should be path-only by default or include hashes for stronger evidence.
5. Whether router cards should be shown to the user every turn or only written to scratch unless non-pass.
6. Whether Automation summaries should run in local project mode or dedicated background worktree mode.

---

## 20. References

Groundwork repository references:

- `AGENTS.md`
- `skills/dispatch/SKILL.md`
- `docs/prd-dispatch-runtime-router.md`
- `docs/prd-routing-reliability.md`
- `docs/routing-reliability-issues.md`
- `docs/skill-success-metrics.md`
- `docs/eval-trace-artifacts.md`
- `docs/nightly-harness.md`
- `docs/prd-v0.4.x-trace-first-eval-platform-roadmap.md`
- `evals/run_runtime.py`
- `evals/prompts/routing-reliability.csv`
- `evals/report.py`
- `evals/checks/trace_diagnostics.py`

Official Codex references checked on 2026-06-27:

- Codex Hooks: https://developers.openai.com/codex/hooks
- Codex Non-interactive mode: https://developers.openai.com/codex/noninteractive
- Codex Automations: https://developers.openai.com/codex/app/automations
- Codex GitHub Action: https://developers.openai.com/codex/github-action

---

## 21. Acceptance Summary

This PRD is accepted when maintainers agree that the next workstream should:

1. keep existing Groundwork routers;
2. add Hook-first live observability;
3. reuse the existing route/verdict model;
4. keep traces local and redacted by default;
5. replay failures through `codex exec --json` and eval rows;
6. generate self-improvement proposals without auto-applying them;
7. defer Automation and CI until live trace and replay evidence exist.
