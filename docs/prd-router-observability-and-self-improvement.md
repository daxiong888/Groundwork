# PRD: Groundwork Router Observability and Self-Improvement Harness

Target Reader: Groundwork maintainers, especially the personal maintainer running the v0 cross-project trial, Codex harness implementers, eval authors, runtime adapter authors, and reviewers deciding how Groundwork should make router decisions observable before adding more routing behavior.

Reader Action Needed: Review and accept, revise, or split this PRD into scoped implementation issues. Use it as the source of truth for a Hook-first router observability increment whose first acceptance target is a personal maintainer cross-project trial, followed by the self-improvement proposal loop.

Decision Supported: Whether Groundwork should add a live observability harness around existing routing and dispatch layers, using Codex hooks for turn-level trace capture, `codex exec --json` for replayable evals, GitHub Actions for optional regression gates, and Codex Automations for periodic proposal-only summaries.

Artifact Type: PRD / architecture decision record.

Source of Truth: Current Groundwork repository guidance, `skills/dispatch/SKILL.md`, `skills/dispatch/ROUTING-PROFILES.md`, `skills/_shared/COGNITIVE-BUDGET.md`, `skills/_shared/RUNTIME-CAPABILITY.md`, `docs/prd-dispatch-runtime-router.md`, `docs/prd-routing-reliability.md`, `docs/skill-success-metrics.md`, `docs/eval-trace-artifacts.md`, `docs/nightly-harness.md`, `evals/run_runtime.py`, `evals/prompts/routing-reliability.csv`, `evals/report.py`, `evals/checks/trace_diagnostics.py`, and official Codex documentation for hooks, non-interactive mode, automations, and GitHub Action.

Scope: Personal maintainer cross-project trial, plugin-bundled dormant hook entrypoints, per-project opt-in activation, observe-only live router decision visibility by default, turn-level trace capture with explicit coverage limitations, reuse of existing routing/verdict vocabulary, dispatch runtime decision observability, dispatch execution profile observability for model profile / reasoning effort / cost-latency bias, local scratch artifacts, redacted promoted artifacts, replay path from reviewed real traces into eval rows, proposal-only self-improvement, and harness selection boundaries.

Out of Scope: New public Groundwork skills, learned routing, embedding/reranker service, MCP server, task database, dashboard, automatic skill mutation, automatic model or reasoning selector mutation, automatic PR/issue creation, automatic tracker writes, automatic trace capture merely because the plugin is installed or updated, default route-hint injection, default prompt blocking, default Stop continuation, default subagent spawning, default managed worktree execution, runtime adapter execution, applying selector enforcement from Groundwork, general-user automatic activation, plugin release, marketplace packaging, cache refresh, UAT/customer readiness, or claims that hook traces alone prove release readiness.

Evidence Level: Product design grounded in inspected repository files and official Codex documentation as of 2026-06-27. This PRD does not add runtime evidence, cache/source equivalence evidence, release evidence, UAT evidence, or customer-readiness evidence.

Safe to Share / Redaction Notes: Safe to share as a planning artifact. It contains architecture and schema examples only; no secrets, credentials, PII, private traces, browser logs, or production payloads.

Status: Draft PRD for maintainer review. v0 acceptance target is personal maintainer cross-project trial only.

Last Updated: 2026-06-27.

---

## 1. Lifecycle Preflight

Intent: product_architecture / harness_planning.

Suggested Workflow Mode: to-prd, then to-issues after acceptance.

Locale: Chinese product discussion; repository identifiers, schema fields, and file paths remain English.

Source of Truth: mixed, with Groundwork repo docs and official Codex documentation as canonical references for their own surfaces.

Requirement State: PRD draft.

Artifact Promotion: required. This document is the durable planning artifact for the router observability workstream.

Execution Topology: personal_cross_project_trial / plugin_bundled_dormant_hooks / project_opt_in / local_with_artifact / docs-only branch.

Risk Gate: git_write for documentation branch changes only.

Verification Strategy: source review, line-level diff review, `git diff --check` when implemented locally, and later schema/runtime checks when implementation slices are created.

Lifecycle State: no runtime state change.

Stop Condition: PRD is complete enough to split into implementation issues.

---

## 2. Executive Summary

Groundwork already has router-like behavior. The current problem is not that routing is absent. The problem is that route selection, runtime selection, execution profile selection, route hit detection, and contract adherence are still too opaque during normal Codex use.

This PRD defines **Router Observability v0**:

```text
existing Groundwork routing and dispatch decisions
  -> observe-only live hook trace
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

Groundwork should not add another public router skill. Instead, it should expose and score the decisions made by the existing routing reliability layer, the existing `dispatch` runtime router, and the existing dispatch execution profile policy for model profile, reasoning effort, and cost-latency bias.

The v0 acceptance target is intentionally personal and cross-project:

```text
accepted v0 = maintainer can install/update the Groundwork plugin,
              review and trust the current dormant hook definitions
              for the installed plugin version when Codex requires it,
              opt selected projects into observe-only tracking,
              inspect route cards and score JSON,
              and decide which failures deserve eval backfill.
```

v0 defaults to dormant hook entrypoints plus `observe_only` when a project explicitly opts in. Installing or updating the plugin may make hook entrypoints available, but it must not start trace capture by itself.

Install/update in v0 means the maintainer uses an existing local plugin install or supported plugin update path. This PRD does not create marketplace release packaging or claim marketplace readiness.

In `observe_only`, hooks may write scratch artifacts and cards for opted-in projects, but they must not inject route hints, block prompts, rewrite tool calls, request Stop continuation, create warnings in normal passing cases, or change model behavior.

Route hints are allowed only as a later explicit `guided_hint_trial` mode. Guided trials must be labeled separately and must not be mixed into passive observability baselines, because the hint changes the behavior being measured.

The recommended harness order is:

1. **Hooks** for observe-only live turn-level observability.
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

### 3.6 Hook Coverage Is Partial

Official Codex hooks support turn-scoped events such as `UserPromptSubmit`, `PreToolUse`, `PermissionRequest`, `PostToolUse`, and `Stop`, but tool hooks are not a complete trace boundary. Current hook behavior covers supported tools such as Bash, `apply_patch`, and MCP tool calls; it does not guarantee interception of every shell pathway, WebSearch, or every non-shell/non-MCP tool.

Therefore live router observability must record coverage status and source strength. A hook trace can say what it observed. It must not silently infer that unobserved tool paths did not happen, that a public skill was certainly loaded, or that an `actual_route` is known when the supporting signal is absent.

### 3.7 Plugin-Bundled Entry Points Need Project Opt-In

For cross-project personal use, the hook entrypoints should be bundled with the Groundwork plugin so the maintainer does not have to hand-wire every project to a moving plugin cache path.

Bundling entrypoints is not the same as enabling tracking. Plugin install or update may make hook definitions discoverable and may require Codex hook trust review, but every hook must no-op unless the current project explicitly opts in.

The opt-in should be project-local and reviewable, for example:

```json
{
  "enabled": true,
  "mode": "observe_only",
  "raw_capture": false,
  "snippet_capture": false
}
```

The exact file path is an implementation detail, but the first implementation should prefer a local project config under `.groundwork/harness/router-observability/` or another clearly documented local-only location. If a project intentionally commits opt-in policy later, that must be a separate governance decision.

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
11. Keep passive observability separate from behavior-shaping route hints.
12. Make unknown or partial coverage explicit in every score that depends on live hook evidence.
13. Make hook entrypoints available across the maintainer's projects without automatically tracking any project.

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
- enable route hints by default;
- collect traces merely because Groundwork was installed or updated;
- treat hook coverage as complete;
- mark a score as baseline-pass when `expected_route_source`, `actual_route_source`, or `tool_coverage_status` is insufficient.

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

### 8.1 Entry Decision Candidate

The Entry Decision Candidate is the pre-skill semantic decision candidate for a live turn.

For fixture-backed evals, `expected_best` is source truth from the row. For live hooks, v0 must treat the decision as a candidate unless it is produced by an accepted deterministic classifier with its own eval evidence.

Minimum shape:

```json
{
  "decision_mode": "observe_only | guided_hint_trial",
  "decision_source": "fixture | deterministic_entry_classifier | heuristic | unknown",
  "route": "direct | to-prd | to-issues | triage | write-plan | prototype | implement | verify | handoff | dispatch | wiki",
  "requirement_state": "raw | grilled | prd_draft | prd_accepted | issue_ready | implementation_ready | verified | blocked",
  "source_truth": "conversation | accepted_prd | local_artifact | external_issue | source_code | test_evidence | runtime_evidence | state_md | mixed | unknown",
  "stop_condition": "continue | ask_clarification | require_prd_acceptance | require_artifact_promotion | require_gate | direct_answer | blocked",
  "router_hint_emitted": false
}
```

In `observe_only`, `router_hint_emitted` must be `false`.

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

A Router Decision Card is the human-readable summary of expected route candidate, actual route signal, verdicts, failure type, fix locus, and evidence limitations.

It is not a dashboard. It is a compact per-turn artifact.

Minimum card:

```text
Groundwork Router Decision

Expected first route: write-plan
Expected route source: deterministic_entry_classifier
Actual route: implement
Actual route source: final_message_marker
Tool coverage: partial
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

### 8.4 Runtime Candidate Card

When `dispatch` is involved, the card must expose the runtime candidate without claiming execution:

```text
Dispatch Candidate

Task: RR-007
Task type: write_implementation
Runtime: codex_app_managed_worktree_thread
Route decision: worktree_isolated
Isolation: codex_managed_worktree
Selector enforcement: prompt_preference | unknown | tool_enforced
Execution profile: strong_reasoning / high / quality
Result package expected: review_package
Execution status: not_executed_by_dispatch
```

### 8.5 Execution Profile Decision

An Execution Profile Decision is the dispatch-level recommendation for model profile, reasoning effort, and cost-latency bias. It is not proof that a runtime applied those selectors.

Minimum shape:

```json
{
  "model_profile": "fast_scan | balanced_work | strong_reasoning | exhaustive_review | spark_iteration | unknown",
  "reasoning_effort": "low | medium | high | xhigh | unknown",
  "cost_latency_bias": "fast | balanced | quality | unknown",
  "profile_source": "dispatch_routing_profile | task_package | user_request | unknown",
  "profile_source_value": "original source text or empty",
  "profile_options": {
    "model_profiles": ["exhaustive_review"],
    "reasoning_efforts": ["medium", "high"],
    "cost_latency_biases": ["balanced", "quality"]
  },
  "normalization_reason": "why the selected normalized values fit this task",
  "selector_enforcement": "tool_enforced | prompt_preference | unavailable | unknown",
  "capability_status": "known | unknown | user_supplied | docs_reference | tool_enforced",
  "evidence_layer": "prompt_preference | runtime_tool_evidence | user_observed_model_menu_seed | official_docs | community_evidence | local_characterization_eval",
  "concrete_model": "evidence_bound_or_empty"
}
```

Rules:

- Profile recommendations are observable dispatch intent.
- The primary `model_profile`, `reasoning_effort`, and `cost_latency_bias` fields store normalized selected values from `skills/_shared/COGNITIVE-BUDGET.md`.
- If `skills/dispatch/ROUTING-PROFILES.md` provides natural language or range values such as `reviewer profile`, `medium/high`, or `balanced/quality`, the trace must preserve the original source in `profile_source_value`, list candidates in `profile_options`, choose one normalized value for the material task, and explain the choice in `normalization_reason`.
- `tool_enforced` requires runtime adapter or tool evidence for the specific run.
- Prompt/package preferences remain `prompt_preference`, `unavailable`, or `unknown` unless selector application is reported by the runtime.
- v0 must not expose or require model internal reasoning content; `reasoning_effort` means selector preference only.
- v0 must not auto-change model or reasoning settings.

### 8.6 Groundwork Turn Trace

A Groundwork Turn Trace is a local scratch record for one Codex turn. It ties together:

```text
prompt input metadata
prompt deterministic metadata and hash
entry decision
optional dispatch decision
tool events
permission or risk events
final assistant message metadata
final deterministic metadata and hash
checker evidence
execution profile decision, if dispatch is involved
changed file snapshot
router score
router card
```

It should live under ignored local scratch by default. Raw prompt and raw final text are disabled by default. They require explicit opt-in, stay scratch-only, and must be excluded from promotion unless redacted and reviewed.

### 8.7 Router Score

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

Every live Router Score must also record source strength:

```text
expected_route_source
actual_route_source
skill_hit_source
tool_coverage_status
execution_profile_source
selector_enforcement
score_eligibility
```

If the source strength is insufficient, the score must use `unknown`, `partial`, `display_only`, or `insufficient_evidence` instead of converting uncertainty into baseline passing evidence.

### 8.8 Self-Improvement Proposal

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
  - SessionStart, deferred unless RO-003 proves session-level metadata is needed
  - UserPromptSubmit
  - PreToolUse / PermissionRequest
  - PostToolUse
  - Stop

Layer 2: Shared routing and verdict model
  - routing schema
  - route detection
  - dispatch execution profile schema
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

- run a project opt-in preflight before writing any trace;
- use command handlers only;
- avoid relying on async handlers;
- avoid assuming transcript format stability;
- avoid assuming complete tool coverage;
- avoid broad blocking behavior;
- avoid Stop continuation loops;
- write local scratch artifacts first;
- keep `observe_only` as the default mode;
- use `systemMessage` or additional context only for opt-in guided trials and warnings.

### 9.3.1 Observe-Only vs Guided Hint Trial

`observe_only` is the v0 default and the only mode eligible for the first passive baseline. It writes trace artifacts and cards but does not change the model's prompt context.

`dormant` is the default state for every project that has not opted in. Dormant hooks must return success without writing trace artifacts, emitting context, blocking prompts, or surfacing warnings.

`guided_hint_trial` is optional and explicit. It may emit compact `additionalContext` route hints, but every artifact from that mode must record:

```text
decision_mode = guided_hint_trial
router_hint_emitted = true
score_eligibility = guided_hint_excluded
```

Guided trial results may show whether hints improve behavior, but they cannot prove passive router observability or baseline route accuracy.

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
  prompt-metadata.json
  prompt.raw.json                 # optional / explicit opt-in only
  router-decision.json
  dispatch-decision.json          # optional
  tool-events.jsonl
  permission-events.jsonl
  file-snapshot-before.json       # optional / path-only by default
  file-snapshot-after.json        # optional / path-only by default
  final-metadata.json
  final.raw.txt                   # optional / explicit opt-in only
  final.raw.meta.json             # optional / explicit raw-capture metadata
  router-score.json
  router-card.md
  coverage.json                   # written by Stop hook with event replay diagnostics
  diagnostics.json                # optional
```

Rules:

- Hooks must check project opt-in before creating this directory.
- This directory is ignored local scratch.
- Raw traces are not committed.
- Raw prompt and raw final text are disabled by default.
- Prompt/final metadata should use deterministic, minimized fields such as stable non-sensitive markers, hashes, lengths, checker inputs, capture-status fields, and decision evidence. It is not LLM summarization.
- Short prompt/final snippets are disabled by default and require explicit `snippet_capture=true`.
- Raw prompt/final capture requires a separate explicit maintainer opt-in and must record retention and redaction status.
- Raw command output, browser logs, private payloads, cookies, and secrets must not be promoted.
- Promoted artifacts must follow `docs/eval-trace-artifacts.md`.

Acceptance criteria:

- Layout is documented.
- Redaction boundary is explicit.
- Default artifacts are useful without storing raw prompt or raw final text.
- No implementation commits `.groundwork/harness` runtime output.

### FR-3: UserPromptSubmit Entry Decision Hook

Implement a plugin-bundled hook script for `UserPromptSubmit` that records an Entry Decision Candidate before Codex acts only when the current project opts in.

Proposed file:

```text
hooks/hooks.json
scripts/codex-hooks/user_prompt_submit_groundwork_entry.py
```

The plugin should bundle hook entrypoints so they are available across the maintainer's projects. The entrypoint must no-op unless project opt-in is present. A personal `.codex/hooks.json` or `config.toml` example may remain as a fallback for local development, but it must not be the primary cross-project setup.

Input:

- hook JSON stdin;
- `prompt`;
- `cwd`;
- optional repository state inspection;
- optional existing Groundwork artifacts.

Output:

- no output and no trace write when the project has not opted in;
- `router-decision.json` in local scratch;
- no hook output by default in `observe_only`;
- optional JSON hook output with `hookSpecificOutput.additionalContext` only when `guided_hint_trial` is explicitly enabled.

When guided hint mode is enabled, the additional context must be short and bounded, for example:

```text
Groundwork route hint: expected first route write-plan; no file edits expected; use scope, assumptions, steps, verification, risks, handoff boundary.
```

Acceptance criteria:

- Hook can run in dry mode from stdin fixture.
- Hook no-ops when project opt-in is absent.
- Hook never writes committed repository files except local scratch.
- Hook does not block normal prompts by default.
- Hook can be disabled by config or environment variable.
- In default `observe_only`, hook does not emit `additionalContext`.
- Guided hints are opt-in, recorded with `decision_mode=guided_hint_trial`, and excluded from passive baseline metrics.
- Hook records `expected_best` candidate, `acceptable_routes`, `forbidden_routes`, `route_boundary`, `decision_source`, and source of inference when known.

### FR-4: Tool and Permission Event Capture

Implement hook scripts for tool and permission events.

Proposed files:

```text
hooks/hooks.json
scripts/codex-hooks/pre_tool_use_groundwork_trace.py
scripts/codex-hooks/permission_request_groundwork_trace.py
scripts/codex-hooks/post_tool_use_groundwork_trace.py
```

Captured fields:

```json
{
  "session_id": "...",
  "turn_id": "...",
  "hook_event_name": "PostToolUse",
  "tool_name": "Bash",
  "coverage_status": "observed_supported | unsupported | unknown",
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

- No-op when project opt-in is absent.
- Store only the minimum needed for scoring.
- Prefer command category and evidence markers over raw output.
- Never store secrets or full private payloads by default.
- If raw output is needed for local debugging, keep it scratch-only and redaction-required.
- Record hook coverage limitations. Current hooks must not claim complete interception of all shell, WebSearch, non-shell, or non-MCP tool paths.
- Missing hook events must produce `unknown` or `partial` evidence, not a passing route claim.

Acceptance criteria:

- Tool events are append-only JSONL.
- Tool hooks do not write JSONL until project opt-in is present.
- Tool capture is robust when fields are absent.
- Secret-looking values are redacted or omitted.
- Evidence markers are compatible with existing `trace_diagnostics.py` where possible.
- Coverage status is present for every event-derived score.

### FR-5: Stop-Time Router Score Hook

Implement a Stop hook that scores the turn after Codex produces a final assistant message.

Proposed file:

```text
hooks/hooks.json
scripts/codex-hooks/stop_groundwork_score.py
```

Inputs:

- `router-decision.json`;
- `tool-events.jsonl`;
- `permission-events.jsonl`;
- final assistant message from hook input when available;
- changed-file snapshot if available;
- optional runtime stdout/final file for replay mode.

Outputs:

- `final-metadata.json`;
- `final.raw.txt` only when explicit raw capture is enabled;
- `final.raw.meta.json` with redaction metadata when explicit raw capture is enabled;
- `router-score.json`;
- `router-card.md`;
- optional `systemMessage` only when an explicit warning mode is enabled.

Stop hook behavior:

- It should no-op when project opt-in is absent.
- It should not auto-continue by default.
- Continuation should be gated behind an explicit opt-in and loop guard.
- Severe failures may be surfaced as a warning, not as hidden mutation.
- In baseline mode, insufficient route evidence must produce `actual_route=unknown` or `overall_verdict=blocked`, not `pass`.

Acceptance criteria:

- Correctly classifies `route_miss`, `forbidden_route`, `output_contract_failure`, `evidence_failure`, `invalid_host_preemption`, and `forbidden_behavior` when fixture data supports it.
- Correctly classifies insufficient live evidence as `unknown`, `partial`, or `blocked`.
- Writes a human-readable card for every scored turn.
- Does not claim release readiness or runtime readiness.
- Does not modify user code.

### FR-6: Dispatch Runtime and Execution Profile Observability

When `dispatch` is selected or mentioned, observability must record runtime route decisions and execution profile recommendations separately from entry route decisions.

Required fields:

```json
{
  "dispatch_version": 2,
  "task_id": "...",
  "task_type": "write_implementation | read_only_review | planning_only | hybrid | diagnosis | verification | direct",
  "runtime_id": "codex_app_managed_worktree_thread | codex_subagent | main_thread_direct | main_thread_readonly | clean_reviewer",
  "route_decision": "local_direct | local_with_artifact | worktree_isolated | worktree_review_only | automation_candidate",
  "execution_profile": {
    "model_profile": "fast_scan | balanced_work | strong_reasoning | exhaustive_review | spark_iteration | unknown",
    "reasoning_effort": "low | medium | high | xhigh | unknown",
    "cost_latency_bias": "fast | balanced | quality | unknown",
    "profile_source": "dispatch_routing_profile | task_package | user_request | unknown",
    "profile_source_value": "original source text or empty",
    "profile_options": {
      "model_profiles": ["exhaustive_review"],
      "reasoning_efforts": ["medium", "high"],
      "cost_latency_biases": ["balanced", "quality"]
    },
    "normalization_reason": "why the selected normalized values fit this task",
    "concrete_model": "",
    "capability_status": "known | unknown | user_supplied | docs_reference | tool_enforced",
    "selector_enforcement": "tool_enforced | prompt_preference | unavailable | unknown",
    "selector_enforcement_policy": "tool_if_available_else_prompt_preference",
    "evidence_layer": "prompt_preference | runtime_tool_evidence | user_observed_model_menu_seed | official_docs | community_evidence | local_characterization_eval"
  },
  "expected_result_package": "review_package | findings_package | diagnosis_package | direct_result | review_findings",
  "execution_claim": "not_executed_by_dispatch"
}
```

Rules:

- Dispatch may produce package expectations.
- Dispatch observability must not imply execution.
- Runtime adapter execution evidence must be separate.
- Execution profile recommendations are routing intent, not proof that a concrete model or reasoning selector was applied.
- Execution profile fields must be normalized to the canonical profile vocabulary from `skills/_shared/COGNITIVE-BUDGET.md`.
- Natural language or range defaults from `skills/dispatch/ROUTING-PROFILES.md` must be preserved in `profile_source_value` and `profile_options`; the selected normalized value must be justified in `normalization_reason`.
- A model/profile claim may report `tool_enforced` only when a runtime adapter or tool confirms selector application for that specific run.
- `reasoning_effort` means selector preference or adapter-reported selector status only; it must not capture, request, expose, or summarize model internal reasoning content.
- v0 must not auto-change model, reasoning effort, or cost-latency bias.
- `automation_candidate` remains recommendation-only unless a future accepted issue explicitly implements an automation adapter.

Acceptance criteria:

- Router card shows dispatch route, execution profile, selector enforcement status, and execution boundary when dispatch is involved.
- Natural language or range profile defaults are normalized to canonical profile fields while preserving source value, candidate options, and normalization reason.
- `dispatch` failures are separable from public skill entry failures.
- Execution profile mismatch is separable from runtime route mismatch and public skill entry failures.
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
Dispatch Candidates
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
  "session_id_source": "session_id | conversation_id | thread_id | fallback",
  "turn_id_source": "turn_id | event_id | request_id | tool_use_id_fallback | transcript_path_fallback | event_hash_fallback",
  "created_at": "2026-06-27T00:00:00Z",
  "cwd": "...",
  "deployment_target": "personal_maintainer_cross_project_trial",
  "hook_packaging": "plugin_bundled",
  "project_opt_in": true,
  "activation_source": ".groundwork/harness/router-observability/config.json | env | env_force_enable_over_config | invalid_config_env_force_enable | local_config | unknown",
  "decision_mode": "observe_only",
  "router_hint_emitted": false,
  "raw_prompt_storage": "disabled",
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
  "decision_source": "deterministic_entry_classifier | fixture | heuristic | unknown",
  "confidence": "high | medium | low | unknown",
  "limitations": []
}
```

### 11.2 `dispatch-decision.json`

Created only when `dispatch` is selected, mentioned, or produces a package recommendation. In v0 hook output this file is a heuristic dispatch candidate unless actual dispatch output is separately observed.

```json
{
  "schema_version": "router_observability.dispatch_decision.v0",
  "session_id": "...",
  "turn_id": "...",
  "dispatch_version": 2,
  "task_id": "...",
  "task_type": "write_implementation | read_only_review | planning_only | hybrid | diagnosis | verification | direct",
  "runtime_id": "codex_app_managed_worktree_thread | codex_subagent | main_thread_direct | main_thread_readonly | clean_reviewer",
  "route_decision": "local_direct | local_with_artifact | worktree_isolated | worktree_review_only | automation_candidate",
  "decision_source": "heuristic_dispatch_candidate | dispatch_output | runtime_adapter",
  "actual_dispatch_output_observed": false,
  "score_eligibility": "insufficient_evidence | baseline_eligible",
  "evidence_boundary": "heuristic dispatch candidate only; not actual dispatch skill output or runtime adapter evidence",
  "execution_profile": {
    "model_profile": "fast_scan | balanced_work | strong_reasoning | exhaustive_review | spark_iteration | unknown",
    "reasoning_effort": "low | medium | high | xhigh | unknown",
    "cost_latency_bias": "fast | balanced | quality | unknown",
    "profile_source": "dispatch_routing_profile | task_package | user_request | unknown",
    "profile_source_value": "Read-only multi-perspective review -> reviewer profile / medium/high / balanced/quality",
    "profile_options": {
      "model_profiles": ["exhaustive_review"],
      "reasoning_efforts": ["medium", "high"],
      "cost_latency_biases": ["balanced", "quality"]
    },
    "normalization_reason": "selected high and quality because this is a material clean review",
    "concrete_model": "",
    "capability_status": "known | unknown | user_supplied | docs_reference | tool_enforced",
    "selector_enforcement": "tool_enforced | prompt_preference | unavailable | unknown",
    "selector_enforcement_policy": "tool_if_available_else_prompt_preference",
    "evidence_layer": "prompt_preference | runtime_tool_evidence | user_observed_model_menu_seed | official_docs | community_evidence | local_characterization_eval"
  },
  "expected_result_package": "review_package | findings_package | diagnosis_package | direct_result | review_findings",
  "execution_claim": "not_executed_by_dispatch",
  "selector_evidence": {
    "runtime_reported": false,
    "source": "dispatch_package | runtime_adapter | tool_report | unknown",
    "notes": []
  }
}
```

### 11.3 `tool-events.jsonl`

Each row:

```json
{
  "schema_version": "router_observability.tool_event.v0",
  "session_id": "...",
  "turn_id": "...",
  "session_id_source": "session_id | conversation_id | thread_id | fallback",
  "turn_id_source": "turn_id | event_id | request_id | tool_use_id_fallback | transcript_path_fallback | event_hash_fallback",
  "event_index": 1,
  "hook_event_name": "PostToolUse",
  "tool_name": "Bash",
  "tool_use_id": "...",
  "tool_input_sha256": "...",
  "tool_response_present": true,
  "tool_response_status": "success",
  "tool_response_length": 1234,
  "tool_response_sha256": "...",
  "command_class": "git | test | file_read | file_write | browser | unknown",
  "coverage_status": "observed_supported | unsupported | unknown",
  "coverage_limitations": [],
  "risk_markers": ["git_write"],
  "evidence_markers": ["git_status"],
  "status": "pass | fail | blocked | unknown",
  "redaction": {
    "status": "not_reviewed",
    "notes": []
  }
}
```

### 11.4 `router-score.json`

```json
{
  "schema_version": "router_observability.score.v0",
  "session_id": "...",
  "turn_id": "...",
  "expected_route": "write-plan",
  "actual_route": "implement",
  "expected_route_source": "deterministic_entry_classifier | fixture | heuristic | unknown",
  "actual_route_source": "hook_event | final_message_marker | codex_exec_json | changed_file_snapshot | unknown",
  "skill_hit_source": "hook_event | codex_exec_json | final_message_marker | unknown",
  "tool_coverage_status": "supported_events_observed | partial | unsupported | unknown",
  "score_eligibility": "baseline_eligible | display_only | guided_hint_excluded | insufficient_evidence",
  "acceptable_routes": ["write-plan"],
  "forbidden_routes": ["implement", "verify", "direct"],
  "routing_verdict": "fail",
  "host_preemption_verdict": "not_applicable",
  "execution_profile_verdict": "mismatch | pass | insufficient_evidence | not_applicable",
  "execution_profile_source": "dispatch_decision | runtime_adapter | final_message_marker | unknown",
  "selector_enforcement": "prompt_preference | tool_enforced | unavailable | unknown",
  "selector_mismatch_reason": "profile_too_weak_for_risk | profile_too_expensive_for_scope | selector_unavailable | selector_unverified | none",
  "output_contract_verdict": "pass",
  "evidence_verdict": "fail",
  "behavior_verdict": "fail",
  "overall_verdict": "fail",
  "failure_type": "route_miss",
  "fix_locus": "routing_surface",
  "changed_files": [],
  "skill_hits": [],
  "dispatch_decisions": [],
  "router_hint_emitted": false,
  "checker_results": [
    {
      "checker_id": "verify_scope_full",
      "verdict": "fail",
      "evidence": {
        "first_line_class": "not_verification_scope",
        "missing_fields": ["Covered", "Not Covered"]
      }
    }
  ],
  "notes": "expected route write-plan, loaded implement",
  "evidence_boundary": "local hook score only; not release evidence"
}
```

### 11.5 `router-card.md`

Required sections:

```text
Groundwork Router Decision
Input Summary
Expected Route
Expected Route Source
Actual Route
Actual Route Source
Tool Coverage
Dispatch Candidate, if applicable
Execution Profile Decision, if applicable
Selector Enforcement Evidence, if applicable
Verdicts
Failure Classification
Evidence Used
Limitations
Score Eligibility
Next Suggested Action
```

### 11.6 Self-Improvement Proposal

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

### 12.1 Live Score Authority Gate

Live hook scores must pass an authority gate before they can contribute to passive baseline routing metrics.

A live score is `baseline_eligible` only when all of these are true:

- `decision_mode = observe_only`;
- `router_hint_emitted = false`;
- `expected_route_source` is `fixture` or `deterministic_entry_classifier`;
- if `expected_route_source = deterministic_entry_classifier`, the classifier version has accepted fixture or eval evidence;
- `actual_route_source` is not `unknown`;
- `skill_hit_source` is not required for the claim, or is not `unknown`;
- `tool_coverage_status` is `supported_events_observed`, or the missing coverage is irrelevant to the score claim;
- if the score claims model profile, reasoning effort, or cost-latency selector correctness, `execution_profile_source` is not `unknown`;
- if the score claims selector application, `selector_enforcement = tool_enforced`;
- if the score claims only selector recommendation quality, `selector_enforcement = prompt_preference | tool_enforced` is acceptable and the card must label it as recommendation evidence, not execution evidence;
- raw prompt/final capture is not required to reproduce the checker result, or `checker_results` contains enough deterministic evidence.

If any required source-strength condition is missing:

- `score_eligibility = display_only` for live heuristic candidates that should preserve candidate route verdicts for human review;
- `score_eligibility = insufficient_evidence` for non-heuristic scores that cannot support baseline scoring;
- `routing_verdict = blocked` only when the score cannot preserve a meaningful candidate route verdict;
- the turn must not count toward `best_route_hit_at_1`, `acceptable_route_coverage`, or passive route-pair confusion;
- the router card must explain which source, coverage, or selector-evidence field blocked baseline scoring.

Heuristic live candidates may still help diagnosis, but they are not route truth.

### 12.2 Route Selection Pass

For fixture-backed eval rows and live scores that pass the authority gate, route selection passes when:

- `actual_route == expected_best`; or
- `actual_route` is in `acceptable_routes`; and
- `actual_route` is not in `forbidden_routes`; and
- host preemption is valid or not applicable.

### 12.3 Best Route Still Matters

`acceptable_routes` may allow safe alternatives, but `best_route_hit_at_1` remains a trend signal. Broadening acceptable routes must not hide unclear ownership.

### 12.4 Forbidden Route Hit

A forbidden route hit fails even when the final answer looks plausible.

Example:

```text
Expected: write-plan
Forbidden: implement
Actual: implement
Result: fail, even if the implementation was competent
```

### 12.5 Right Route, Wrong Path

If the right skill is selected but output/evidence/behavior contracts fail, the route verdict may pass while overall verdict fails.

Example:

```text
Expected route: verify
Actual route: verify
Output contract: fail because response does not start with Verification Scope
Overall: fail
Fix locus: skill_output_contract
```

### 12.6 Dispatch Does Not Execute

A dispatch decision is scored for package correctness, runtime fit, capability evidence, selector enforcement transparency, and result expectation.

It is not scored as execution evidence unless a runtime adapter separately reports execution.

### 12.7 Execution Profile Scoring

Execution profile scoring is separate from runtime route scoring.

An execution profile passes when:

- `model_profile`, `reasoning_effort`, and `cost_latency_bias` are present when dispatch makes them material;
- `profile_source` is `dispatch_routing_profile`, `task_package`, or `user_request`;
- natural language or range source values are normalized to the canonical profile vocabulary, with `profile_source_value`, `profile_options`, and `normalization_reason` populated when needed;
- `selector_enforcement` is reported truthfully as `tool_enforced`, `prompt_preference`, `unavailable`, or `unknown`;
- `evidence_layer` matches the enforcement claim;
- the profile is not weaker than the risk, review, or validation expectation in the task shape.

It fails or becomes `insufficient_evidence` when:

- a high-risk, public API, migration, security, privacy, data-correctness, clean-review, or release-adjacent claim uses a fast or weak profile as final authority;
- dispatch claims `tool_enforced` without runtime adapter or tool evidence;
- source profile ranges are collapsed without preserving candidate options or explaining the normalized choice;
- a concrete model is treated as permanent runtime truth instead of evidence-bound mapping;
- `reasoning_effort` is treated as captured model reasoning content rather than selector preference.

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

Default live trace output must be content-minimized:

- store deterministic prompt metadata, hashes, and decision evidence instead of full prompts;
- store deterministic final metadata and hashes instead of full assistant messages;
- store path-only changed-file snapshots by default;
- keep raw prompt, raw final text, raw command output, and raw tool responses disabled unless the maintainer explicitly enables raw capture for a local debugging session;
- record raw-capture status and retention expectations in the trace metadata.

`prompt-metadata.json` and `final-metadata.json` are deterministic minimized metadata files, not LLM-generated summaries.

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
- unredacted command output with sensitive paths or payloads;
- unredacted raw prompt or raw final text from live sessions.

### 14.4 Evidence Boundary

Hook traces, score JSON, router cards, and reports are review evidence. They are not release, runtime, UAT, customer, marketplace, or cache-refresh evidence unless separate evidence is named.

Hook traces with `decision_mode=guided_hint_trial` are behavior-shaping trial evidence. They must not be counted as passive observability baseline evidence.

---

## 15. Success Metrics

### 15.1 Live Observability Metrics

- Percentage of Groundwork-relevant turns with `router-decision.json`.
- Percentage of scored turns with `router-score.json`.
- Percentage of scored turns with `actual_route != unknown`.
- Percentage of dispatch-involved turns with `dispatch-decision.json`.
- Percentage of dispatch-involved turns with complete execution profile fields.
- Percentage of scored turns with `score_eligibility=baseline_eligible`.
- Percentage of scored turns with `score_eligibility=display_only`.
- Percentage of scored turns with `score_eligibility=insufficient_evidence`.
- Percentage of events with `coverage_status=unsupported | unknown`.
- Percentage of non-pass turns with `failure_type` and `fix_locus` populated.
- Median hook overhead per event.
- Count of hook failures by event type.
- Count of traces blocked from promotion by redaction policy.
- Count of traces that enabled raw prompt or raw final capture.
- Count of guided hint trials excluded from passive baseline metrics.

No-op behavior for non-opted-in projects is verified by fixture and unit tests. Live non-opted-in projects must not produce per-project no-op metrics by default. Optional global hook diagnostics may count aggregate no-op events only when explicitly enabled, and must not include project path, project name, prompt text, or final text unless that project separately opts in.

### 15.2 Routing Metrics

Reuse existing routing summary metrics:

- `best_route_hit_at_1`;
- `acceptable_route_coverage`;
- `forbidden_route_hits`;
- `invalid_host_preemption`;
- `route_pair_confusion`;
- `verdict_dimension_counts`;
- `execution_profile_verdict_counts`;
- `selector_enforcement_counts`;
- `selector_mismatch_reason_counts`;
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
- Zero trace writes in projects without opt-in.
- Zero raw prompt/final capture in default mode.
- Zero route-hint injection in default `observe_only` mode.
- Zero passive-baseline scores from guided hint trials.
- Zero automatic model or reasoning-effort changes.
- Zero `tool_enforced` selector claims without runtime adapter or tool evidence.
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
- PRD covers public skill entry route, dispatch runtime route, and dispatch execution profile observability.
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
- Shared schemas cover route/verdict fields and dispatch execution profile fields.
- No Codex runtime invocation is needed for unit tests.

Verification:

- CSV/schema validation.
- Unit tests for extracted modules.
- Focused runner dry validation.

### RO-003: Document Hook Configuration and Trace Layout

Goal: Add maintainer docs for plugin-bundled dormant hook entrypoints, project opt-in, disabling hooks, and local trace scratch.

Touch targets:

```text
docs/router-observability-harness.md
docs/eval-trace-artifacts.md   # only if needed
```

Acceptance criteria:

- Documents hook install/config pattern.
- Documents that v0 is a personal maintainer cross-project trial with plugin-bundled dormant entrypoints.
- Documents project opt-in config, no-op behavior when absent, and how to disable tracking for one project.
- Documents that plugin install/update uses an existing local install or supported update path and does not create marketplace release packaging.
- Documents that `SessionStart` is deferred unless session-level metadata is accepted as necessary.
- Documents scratch layout and redaction boundary.
- Documents default `observe_only`, optional `guided_hint_trial`, raw-capture opt-in, and snippet-capture opt-in.
- Documents how to disable hooks.
- Does not require global Codex config mutation in repo tests.

Verification:

- Markdown review.
- Redaction policy review.

### RO-004: Implement UserPromptSubmit Dry Hook

Goal: Create first hook that records an Entry Decision Candidate in `observe_only` by default.

Touch targets:

```text
hooks/hooks.json
scripts/codex-hooks/user_prompt_submit_groundwork_entry.py
evals/fixtures/router-observability/
evals/test_router_observability_hooks.py
```

Acceptance criteria:

- Reads hook JSON from stdin.
- No-ops when project opt-in is absent.
- Writes `router-decision.json` to local scratch.
- Does not produce `additionalContext` in default `observe_only`.
- Produces compact additional context only when explicit `guided_hint_trial` mode is enabled.
- Records `decision_mode`, `decision_source`, `router_hint_emitted`, and raw-capture status.
- Has dry-run tests with fixture prompts.
- Does not modify source files or committed artifacts at runtime.

Verification:

- Unit tests.
- Manual dry-run with fixture JSON.

### RO-005: Implement Tool Event Capture Hooks

Goal: Capture tool and permission events as redaction-aware JSONL markers.

Touch targets:

```text
hooks/hooks.json
scripts/codex-hooks/pre_tool_use_groundwork_trace.py
scripts/codex-hooks/permission_request_groundwork_trace.py
scripts/codex-hooks/post_tool_use_groundwork_trace.py
evals/test_router_observability_hooks.py
```

Acceptance criteria:

- Appends JSONL events.
- No-ops when project opt-in is absent.
- Records command class, risk markers, and evidence markers.
- Records coverage status and limitations.
- Uses `observed_supported | unsupported | unknown` for event coverage status.
- Avoids raw output by default.
- Handles missing fields gracefully.

Verification:

- Unit tests with synthetic hook inputs.
- Redaction fixture checks.

### RO-006: Implement Stop Scoring Hook

Goal: Score a turn at Stop using shared verdict logic, source-strength rules, and a router card.

Touch targets:

```text
hooks/hooks.json
scripts/codex-hooks/stop_groundwork_score.py
evals/test_router_observability_hooks.py
evals/test_verdict_model.py
```

Acceptance criteria:

- Reads prior decision and event artifacts.
- No-ops when project opt-in is absent.
- Produces `router-score.json` and `router-card.md`.
- Uses shared route/verdict model.
- Records `expected_route_source`, `actual_route_source`, `skill_hit_source`, `tool_coverage_status`, `execution_profile_source`, `selector_enforcement`, and `score_eligibility`.
- Scores `execution_profile_verdict` separately from route and runtime verdicts.
- Refuses to claim selector application without runtime adapter or tool evidence.
- Applies the Live Score Authority Gate before marking a live score `baseline_eligible`.
- Emits `checker_results` with deterministic evidence when raw final text is not stored.
- Refuses to mark insufficient live evidence as baseline-pass.
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

Accept this document for a personal maintainer cross-project trial and split issues.

### Phase 1: Shared Library Before Hooks

Extract route/verdict code first so hooks and runner share one model.

### Phase 2: Hook Dry Mode

Implement plugin-bundled dormant hook entrypoints with fixture tests and local scratch writes. Default to no-op when project opt-in is absent. For opted-in projects, default to `observe_only`. Do not enable blocking, route hints, raw prompt/final capture, warnings, or continuation.

### Phase 3: Live Local Trial

Run observe-only hooks in a small number of opted-in projects and Groundwork sessions. Collect router cards and score JSON in scratch.

Trial evidence must record:

- source branch;
- local checkout path;
- plugin root or source root that provided hook entrypoints;
- installed plugin version or source commit;
- hook definition trust state observed by Codex;
- hook config used;
- deployment target: personal maintainer cross-project trial;
- project opt-in source;
- decision mode;
- raw-capture status;
- execution profile fields when dispatch is involved;
- selector enforcement status and evidence layer when model or reasoning selectors are material;
- trace scratch path;
- tool coverage limitations;
- whether raw traces were promoted;
- limitations.

The trial succeeds when cards make route uncertainty visible, not when every live turn receives a known actual route.

### Phase 3A: Optional Guided Hint Trial

Only after an observe-only baseline exists, run an explicit `guided_hint_trial` if the maintainer wants to test route hints.

Guided hint evidence must be separated from passive baseline evidence and must record `router_hint_emitted=true`.

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

### Risk: Hook Coverage Looks Complete When It Is Not

Mitigation: Every event-derived score records coverage status and source strength. Unsupported or unobserved paths become `unknown`, `partial`, or `insufficient_evidence`, never silent pass evidence.

### Risk: Route Hints Change the Thing Being Measured

Mitigation: v0 defaults to `observe_only`. `guided_hint_trial` is explicit, recorded, and excluded from passive baseline metrics.

### Risk: Hook Overhead Slows Codex

Mitigation: Keep hooks standard-library only, bounded, and marker-based. Avoid heavy file scans. Add timing fields.

### Risk: Transcript Format Changes

Mitigation: Do not depend on transcript format as stable API. Prefer hook input fields and generated artifacts.

### Risk: Sensitive Data Enters Artifacts

Mitigation: Content-minimized scratch by default, raw prompt/final capture disabled by default, redaction-required promotion, omit raw output unless explicitly needed, record retention expectations, and reuse trace artifact policy.

### Risk: Stop Hook Causes Loops

Mitigation: No continuation by default. Future continuation requires explicit opt-in and loop guard.

### Risk: Automation Mutates Groundwork

Mitigation: Automation prompt is proposal-only. It may not edit skills, open PRs, mutate trackers, or write remotes.

### Risk: Acceptable Routes Hide Ownership Drift

Mitigation: Continue reporting Best-route Hit@1 and route-pair confusion. Acceptable routes require review.

### Risk: Dispatch Observability Implies Execution

Mitigation: Runtime Decision Card includes `execution_claim: not_executed_by_dispatch` unless runtime adapter evidence exists.

### Risk: Plugin-Bundled Hooks Start Tracking Too Broadly

Mitigation: v0 may bundle hook entrypoints in the plugin, but every hook no-ops unless the current project explicitly opts in. Plugin install, plugin update, and hook trust review are not tracking consent.

---

## 19. Open Questions

No blocking open questions for PRD acceptance.

Deferred implementation questions:

1. Whether live-only `case_kind` / `case_source` tokens should be added to schema or kept outside eval rows until backfill.
2. Whether later general-user rollout should keep local-only opt-in, support committed project policy, or add a UI/config helper.
3. Whether `guided_hint_trial` should graduate into a supported mode after passive baseline evidence exists.
4. Whether Stop hook warnings should use `systemMessage` for severe failures after observe-only scoring is stable.
5. Whether changed-file snapshots should be path-only by default or include hashes for stronger evidence.
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
2. target personal maintainer cross-project trial first;
3. bundle dormant hook entrypoints so the maintainer can opt selected projects into tracking;
4. require review/trust of the current hook definitions for the installed plugin version when Codex requires it;
5. require project opt-in before any trace write or model-visible hook output;
6. add Hook-first live observability in default `observe_only` mode for opted-in projects;
7. keep route hints opt-in and excluded from passive baseline metrics;
8. reuse the existing route/verdict model with explicit source-strength and coverage fields;
9. observe dispatch execution profile recommendations for model profile, reasoning effort, and cost-latency bias without mutating selectors;
10. keep selector enforcement evidence separate from prompt/package preference;
11. apply the Live Score Authority Gate before counting passive routing metrics;
12. keep traces local, content-minimized, and redacted by default;
13. replay reviewed failures through `codex exec --json` and eval rows;
14. generate self-improvement proposals without auto-applying them;
15. defer Automation, CI, general-user activation, and release claims until live trace and replay evidence exist.
