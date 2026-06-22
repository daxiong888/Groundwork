# PRD v0.4.x: Trace-first Eval Platform Roadmap

Target Reader: Groundwork maintainers, eval harness implementers, future implementation agents, and reviewers planning the post-v0.4.1 trace-first evaluation track.
Reader Action Needed: Use this roadmap PRD to decide which v0.4.x increments should follow the compact v0.4.1 trace-ready verify/review suite, and to avoid treating the full eval platform as already delivered by v0.4.1.
Decision Supported: Whether Groundwork should continue the v0.4.x line from compact trace-ready coverage into schema-backed score JSON, modular deterministic checks, trace diagnostics, report generation, and CI release gates.
Artifact Type: roadmap PRD.
Source of Truth: PR #63 compact v0.4.1 scope, `docs/prd-v0.4.1-trace-first-verify-review-eval.md`, `evals/run_runtime.py`, `docs/skill-success-metrics.md`, v0.4.0 native worktree/handoff governance boundaries, and the earlier Groundwork iteration research note recommending nightly evaluation plus patch proposals without automatic skill mutation.
Scope: v0.4.2 through v0.4.5 planning for schema-backed scoring, deterministic checker modularization, trace artifact/diagnostics, eval reports, patch suggestions, CI gates, and release-evidence boundaries.
Out of Scope: Public skill expansion, runtime ownership, automatic Codex worktree creation, default subagent spawning, automation scheduling, MCP/hooks/task CRUD, dashboards/databases, automatic skill mutation, automatic PR/issue creation, release readiness claims from docs or schema edits alone, and v0.5 product packaging decisions.
Evidence Level: Planning artifact derived from current repository contracts and PR #63 validation notes. No runtime baseline, installed-plugin cache equivalence, release readiness, UAT readiness, or customer readiness is claimed by this document.
Safe to Share / Redaction Notes: Safe to share as a design artifact. It contains no secrets, credentials, private URLs, browser cookies, PII, raw traces, logs, or production data.
Status: Draft for maintainer review.
Version Track: v0.4.x after compact v0.4.1.
Last Updated: 2026-06-22.

---

## 1. Lifecycle Preflight

Intent: roadmap_planning.
Suggested Workflow Mode: to-prd / roadmap.
Locale: Chinese user discussion; English repository identifiers and artifact text.
Source of Truth: mixed, with PR #63 as current release scope and prior research as strategic guidance.
Requirement State: roadmap_draft.
Artifact Promotion: required, because this roadmap should become the source for later issue slicing.
Execution Topology: local_with_artifact for planning only.
Risk Gate: git_write for docs-only branch changes.
Verification Strategy: documentation review, `git diff --check`, and later issue-specific validation.
Lifecycle State: not_needed for this bounded planning artifact.
Stop Condition: roadmap and issue map are clear enough for later triage and implementation slices.

---

## 2. Interpretation of Version Track

The user asked for the `4.0.x` follow-up direction. This document interprets that as the existing Groundwork `v0.4.x` line because the current repository is using `v0.4.0` and `v0.4.1` version targets.

v0.4.1 is now intentionally compact:

```text
v0.4.1 = compact trace-ready verify/review eval suite
          + default runner wiring
          + maintainer evidence-boundary docs
```

The remaining trace-first eval platform work should be planned as follow-up v0.4.x increments, not retroactively added to v0.4.1.

---

## 3. Executive Summary

v0.4.0 made Groundwork smaller and more precise around Codex-native worktree and handoff governance. v0.4.1 added the first compact trace-ready verify/review eval slice, making high-risk verification and clean-review boundaries observable in the existing routing verdict model.

The rest of the v0.4.x line should turn that compact slice into a durable eval platform in four controlled increments:

```text
v0.4.2  Schema-backed score foundation
v0.4.3  Modular deterministic checks and behavior hardening
v0.4.4  Trace artifacts, diagnostics, reports, and patch suggestions
v0.4.5  CI minimum gate and release-evidence policy
```

The key product rule remains the same: Groundwork learns through evidence and patch proposals, but it does not automatically mutate main skills, spawn subagents, schedule automations, create worktrees, or claim release readiness without runtime evidence.

---

## 4. Problem Statement

PR #63 proves that trace-ready rows can extend the existing runner without expanding Groundwork runtime ownership. However, the current implementation is still a compact slice:

- route and evidence checks are still largely runner-local;
- score output is not yet a stable JSON artifact;
- schemas are not yet explicit files;
- deterministic checks are not yet modular;
- raw trace diagnostics are not yet first-class;
- report generation and patch suggestions are not yet durable artifacts;
- CI gates are not yet defined as schema-only versus runtime-optional layers.

If these are all attempted in one release, the version becomes too broad and hard to verify. If they are not planned, later work may re-expand v0.4.1 or blur evidence boundaries. The v0.4.x roadmap exists to keep each increment small, reviewable, and honest about what evidence it actually adds.

---

## 5. Goals

1. Preserve v0.4.1 as a compact, mergeable trace-ready suite release.
2. Define v0.4.2 through v0.4.5 as explicit follow-up increments.
3. Convert runner verdicts into schema-backed score JSON without breaking current results and routing summaries.
4. Move deterministic checks from ad hoc runner logic toward reusable modules with tests.
5. Add trace artifact and diagnostics support without committing sensitive raw logs by default.
6. Generate eval reports and patch suggestions as reviewable artifacts only.
7. Add CI gates that can run without secrets and keep runtime Codex eval optional until installed-plugin evidence exists.
8. Keep all v0.4.x work inside Groundwork governance and eval boundaries, not runtime execution ownership.

---

## 6. Non-goals

The v0.4.x follow-up track must not:

- add or rename public skills;
- create a public `review` skill;
- turn `dispatch` into a runtime executor;
- create worktrees or perform Codex App Handoff;
- spawn subagents by default;
- create or schedule automations;
- auto-apply patch suggestions;
- open PRs, mutate remote trackers, push branches, or close issues automatically;
- require secrets for default CI validation;
- claim runtime/cache/release/UAT/customer readiness from local docs, schema, or source checks;
- build dashboards, databases, MCP servers, hooks, or task CRUD in v0.4.x.

---

## 7. Users and User Stories

### Maintainer

As a maintainer, I want every eval increment to be small enough to review and validate, so I can merge improvements without accidentally expanding runtime ownership.

### Reviewer

As a reviewer, I want schema-backed score JSON and deterministic check names, so I can see exactly why a case passed, failed, blocked, or produced a patch suggestion.

### Product owner

As a product owner, I want a version-by-version roadmap that explains what is in v0.4.2, v0.4.3, v0.4.4, and v0.4.5, so I do not treat compact v0.4.1 as the full trace-first eval platform.

### Future implementation agent

As a future implementation agent, I want issue slices with dependencies, verification commands, and explicit non-goals, so I can implement one safe slice without broad refactors.

---

## 8. Version Plan

### 8.1 v0.4.2 — Schema-backed Score Foundation

Purpose:

Make the trace-ready verdict model durable by adding explicit JSON schemas and score JSON artifacts.

Primary deliverables:

```text
schemas/groundwork-common.schema.json
schemas/groundwork-verify.schema.json
schemas/groundwork-review.schema.json
schemas/groundwork-routing.schema.json
schemas/groundwork-closeout.schema.json
schemas/groundwork-eval-score.schema.json

evals/schema_validation.py
evals/scoring.py
```

Required behavior:

- Existing `evals/run_runtime.py --validate-schema` continues to work.
- Trace-ready rows can produce per-case score dictionaries that validate against `groundwork-eval-score.schema.json`.
- Legacy `results.jsonl`, `summary.json`, and `routing_summary` remain backward compatible.
- Unknown future fields block or validate through explicit extension points; they must not silently pass.

Exit criteria:

- JSON schema files are valid JSON.
- A schema-only validation command runs without Codex runtime or secrets.
- A sample score fixture validates.
- v0.4.1 compact suite still validates with `trace_ready_rows: 8`.

Deferred from v0.4.2:

- full trace parser;
- report generator;
- GitHub Actions gate;
- runtime baseline.

### 8.2 v0.4.3 — Modular Deterministic Checks and Behavior Hardening

Purpose:

Move high-value deterministic checks into reusable modules and add tests for the trace-ready hard negatives.

Primary deliverables:

```text
evals/checks/common.py
evals/checks/verify_checks.py
evals/checks/review_checks.py
evals/checks/routing_checks.py
evals/checks/closeout_checks.py
evals/checks/forbidden_patterns.py
```

Required behavior:

- Preserve existing checks for verify scope, QA Failure shape, gate fields, artifact header, `git add .`, lifecycle artifacts, and trace-ready forbidden behavior.
- Keep the v0.4.1 fixes for code-diff-only readiness claims and low-risk cleanup claims.
- Add stable checker ids in score JSON, such as `verify_scope_full`, `code_diff_only_readiness_claim`, and `low_risk_cleanup_claim`.
- Add unit tests for positive, negative, and negated/conditional wording.

Exit criteria:

- `python -m unittest evals.test_run_runtime_scheduler` or equivalent passes.
- Existing default suites still pass schema validation.
- Checker outputs include ids, verdicts, notes, and fix locus where applicable.

Deferred from v0.4.3:

- raw trace diagnostics;
- patch suggestion generation;
- CI workflow.

### 8.3 v0.4.4 — Trace Artifacts, Diagnostics, Reports, and Patch Suggestions

Purpose:

Add the first durable trace/report layer while keeping raw trace promotion safe and optional.

Primary deliverables:

```text
docs/eval-trace-artifacts.md
evals/checks/trace_diagnostics.py
evals/report.py
artifacts/evals/<run-id>/report.md
artifacts/evals/<run-id>/patch-suggestions.json
```

Required behavior:

- Define promoted artifact layout for trace, final output, score JSON, summary, report, and patch suggestions.
- Raw JSONL traces remain runtime scratch unless explicitly promoted after redaction.
- Trace diagnostics can compute or report unknown for command count, duplicate command count, evidence latency, blocked reason, and trace thrashing.
- Reports list top regressions, deterministic failures, schema failures, trace diagnostics, and patch suggestions.
- Patch suggestions must include affected files, failure type, fix locus, rollback, and `auto_apply: false`.

Exit criteria:

- Report generation works from a local run directory or sample fixtures.
- Patch suggestions are emitted as artifacts only.
- Redaction boundary is documented and tested with at least one secret-looking fixture.

Deferred from v0.4.4:

- CI enforcement;
- broad runtime suite expansion;
- dashboard or database.

### 8.4 v0.4.5 — CI Minimum Gate and Release Evidence Policy

Purpose:

Make the trace-first eval platform usable as a merge/release support gate without requiring secrets by default.

Primary deliverables:

```text
.github/workflows/evals.yml  # if accepted by maintainers
or docs/ci-eval-gate.md      # if workflow addition is deferred

docs/release-evidence-claim-boundary.md
```

Required behavior:

- Schema-only CI runs without secrets.
- Deterministic checker unit tests run without Codex runtime.
- Optional Codex runtime eval is gated by explicit credentials/runtime availability.
- Release evidence claims must name installed plugin root, source root, refresh/equivalence method, run scope, commands/trials, limitations, and missing evidence.
- CI must not imply runtime/cache/release/UAT/customer readiness by itself.

Exit criteria:

- Default CI path passes without Codex secrets.
- Runtime eval instructions are opt-in and evidence-bound.
- Release evidence template exists and blocks unsupported readiness claims.

Deferred from v0.4.5:

- complete 20+ fixture platform release;
- public release automation;
- dashboards/databases;
- automatic skill patch PR creation.

### 8.5 v0.5.0 Candidate — Trace-first Eval Platform Promotion

Purpose:

Promote the v0.4.x work into a coherent platform only after repeated real usage proves the schema, checks, reports, and CI gates are stable.

Possible promotion criteria:

- At least 20 targeted fixtures across verify, review lens, routing, closeout, artifact header, redaction, and patch suggestions.
- At least one real runtime baseline with installed plugin root and source/cache evidence.
- No unclassified P1/P2 eval failures.
- Patch suggestions produce useful human-reviewed patches without automatic mutation.
- Maintainers agree the platform is ready to advertise beyond internal governance.

---

## 9. Product Architecture Direction

The v0.4.x eval platform should be layered:

```text
Prompt CSV / fixture row
  -> trace-ready routing schema normalization
  -> codex exec final output capture when runtime is available
  -> deterministic checks
  -> schema-backed score JSON
  -> optional trace diagnostics
  -> run summary
  -> report + patch suggestions
  -> human decision
```

The platform must preserve three boundaries:

1. **Score is not runtime evidence.** Score JSON can say a local source check passed, but it cannot claim installed plugin runtime behavior.
2. **Patch suggestion is not mutation.** Suggestions name candidate changes and rollback, but do not edit main skill files automatically.
3. **Trace is sensitive by default.** Raw JSONL traces may contain command output, paths, logs, or user content; they require redaction policy before durable promotion.

---

## 10. Functional Requirements by Track

### FR-421 Schema Foundation

Add common and product JSON schemas for score, verify, review, routing, and closeout outputs.

### FR-422 Score JSON Generation

Emit or validate per-case score JSON containing route, evidence, output contract, behavior verdict, checker results, and normalized `overall_verdict`.

### FR-423 Backward Compatibility

Keep existing `results.jsonl`, `summary.json`, `routing_summary`, `trace_ready_rows`, and legacy-compatible `routing_rows` output stable unless a migration note is included.

### FR-431 Modular Deterministic Checks

Extract deterministic checks into reusable modules while preserving current behavior.

### FR-432 Trace-ready Forbidden Behavior Checks

Keep and expand checks for code-diff-only readiness pass claims, low-risk cleanup claims, invented contracts, missing target reader, positive `git add .`, default subagent spawning, automation creation claims, and worktree creation claims without evidence.

### FR-441 Trace Artifact Layout

Document and implement an optional promoted layout for trace, final output, score JSON, summary, report, and patch suggestions.

### FR-442 Trace Diagnostics

Parse raw JSONL traces when available to compute command thrashing, duplicate commands, failed commands, evidence latency, and blocked reason taxonomy.

### FR-443 Eval Report and Patch Suggestions

Generate a human-readable report plus `patch-suggestions.json`, with `auto_apply: false` enforced.

### FR-451 CI Minimum Gate

Add schema-only and deterministic test CI that requires no secrets.

### FR-452 Runtime Evidence Policy

Define the evidence shape required for runtime/cache/release/UAT/customer-readiness claims.

---

## 11. Metrics

v0.4.2 metrics:

- `schema_validation_success_rate`
- `score_json_validation_success_rate`
- `trace_ready_rows_count`
- `legacy_summary_compatibility_preserved`

v0.4.3 metrics:

- `deterministic_checker_count`
- `forbidden_behavior_detection_count`
- `checker_unit_test_count`
- `unclassified_behavior_failure_count`

v0.4.4 metrics:

- `trace_diagnostics_present_rate`
- `trace_redaction_success_rate`
- `trace_command_thrashing_rate`
- `median_evidence_latency_seconds`
- `patch_suggestion_count`
- `auto_patch_attempt_count`, expected always `0`

v0.4.5 metrics:

- `ci_schema_gate_success_rate`
- `ci_checker_gate_success_rate`
- `runtime_eval_opt_in_runs`
- `release_evidence_claim_completeness_rate`

---

## 12. Release Gates

v0.4.2 gates:

- JSON schemas validate.
- Score JSON sample validates.
- v0.4.1 compact suite still validates.
- No runtime readiness claim is made.

v0.4.3 gates:

- Deterministic checker unit tests pass.
- Existing runner validation passes.
- Trace-ready forbidden behavior checks have positive and negative tests.
- No public skill surface change is made.

v0.4.4 gates:

- Report generator works on sample or local run output.
- Patch suggestions are generated without modifying files.
- Redaction boundary is documented.
- Trace diagnostics tolerate unknown event shapes.

v0.4.5 gates:

- CI or CI-equivalent command runs without secrets.
- Runtime eval remains opt-in.
- Release evidence claim template exists.
- Documentation states that CI source checks are not runtime/cache/release/UAT/customer-readiness evidence.

---

## 13. Open Questions

1. Should v0.4.2 introduce schemas under `schemas/` or under `evals/schemas/`?
2. Should score JSON be written during every runtime run or only when an explicit `--score-json` option is enabled first?
3. Should deterministic checks remain callable from `evals/run_runtime.py` or become an importable package with a small CLI?
4. Should raw trace promotion default to `.groundwork/harness/` and copy only redacted summaries into `artifacts/evals/`?
5. Should CI workflow be added in v0.4.5, or should the first version document local CI-equivalent commands only?
6. Should `review` remain only a schema/lens name for the entire v0.4.x line, with no public skill until a separate accepted PRD?
7. Which v0.4.x increment should own the larger 20+ fixture suite: v0.4.4, v0.4.5, or v0.5.0 promotion?

---

## 14. Next Action

Use the companion issue map at `artifacts/v0.4.x-trace-first-eval-platform-roadmap/issue-map.md` to decide whether v0.4.2 should start with schema files or a score JSON spike. Do not start CI or trace diagnostics before the score contract is stable.
