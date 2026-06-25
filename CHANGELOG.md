# Changelog

All notable changes to Groundwork are documented in this file.

## Unreleased

## v0.5.1 - 2026-06-25

### Added

- Added shared Socratic grilling guidance for route-impact question selection, compact interactive output, route-after-answer behavior, and bad-question anti-patterns.
- Added `skills/_shared/DOMAIN-LANGUAGE.md` as a lightweight evidence-boundary vocabulary for term conflicts and promotion blockers.
- Added `evals/prompts/v0.5.1-socratic-grilling.csv` as the focused canonical v0.5.1 suite for positive-value and hard-negative Socratic grilling behavior.

### Changed

- Bumped plugin metadata to `0.5.1` for the Socratic grilling and domain-language workflow hardening source-validation release.
- Updated `to-prd` grilling and PRD template guidance so `Domain Language / Term Conflict` is conditional and does not promote PRD-only wording into backend/API contract truth.
- Added scoped regression prompt rows for grilling, prototype, verify, skill-audit, and guardrail boundaries while keeping `socratic`, `grill`, and `domain-language` out of the public skill surface.

### Notes

- This release is source-validation focused. Local source checks, CSV parsing, GitHub schema/source gate, and clean review do not prove runtime, selector-enforcement, browser, UAT, release, customer, marketplace, or installed-plugin cache behavior by themselves.
- Runtime/cache claims require a named installed plugin root, source root, refresh or source/cache equivalence method, run scope, commands/trials, limitations, and missing evidence.

## v0.5.0 - 2026-06-25

### Added

- Added the v0.5 prototype-first public skill expansion policy:
  - quality-gated public skill expansion through `SKILL-QUALITY`;
  - role separation for implementation self-check, clean review, independent verification, runtime evidence, browser evidence, UAT evidence, and release evidence;
  - lazy runtime capability and selector-enforcement evidence boundaries;
  - capability seed documentation for dated, user-supplied model menu observations;
  - shared references for grilling, decision mapping, skill-audit, visual handoff packets, prototype decision capture, UI variants, and logic/state labs.
- Added v0.5 eval prompt fixtures for role separation, runtime capability, shared grilling, shared decision mapping, shared skill-audit, prototype lab, and aggregate skill expansion hard negatives.

### Changed

- Bumped plugin metadata to `0.5.0` for the prototype-first skill expansion source-validation release.
- Updated `dispatch`, `implement`, `verify`, `handoff`, `prototype`, `to-prd`, and `write-plan` guidance to preserve source-validation, role-separation, runtime/cache, browser, UAT, release, and customer-readiness evidence boundaries.
- Kept `grill`, `decision-map`, and `skill-audit` as shared references or workflows rather than public skills pending explicit maintainer public-exposure acceptance.

### Notes

- This release is source-validation focused. CSV parsing, source inspection, GitHub schema/source gate, and documentation checks do not prove installed plugin runtime behavior, selector enforcement, marketplace readiness, browser behavior, UAT readiness, release readiness, or customer readiness.
- Runtime/cache claims still require a named installed plugin root, source root, refresh or source/cache equivalence method, run scope, commands/trials, limitations, and missing evidence.
- The v0.5 prompt CSVs are fixture/source coverage; they are not default runtime-suite evidence unless explicitly passed to `evals/run_runtime.py` or later added to `DEFAULT_SUITES` with installed-plugin/source-equivalence evidence.

## v0.4.2 - 2026-06-23

### Added

- Added the v0.4.x trace-first eval platform source-validation layer:
  - JSON Schema 2020-12 definitions under `schemas/` for common definitions, verify/review/routing/closeout outputs, and eval score objects.
  - Dependency-free schema validation helpers and score dict adapter support for runner result dictionaries.
  - Modular deterministic checks with stable checker ids, checker result objects, direct tests, and fixture authoring documentation.
  - Trace artifact layout and redaction policy documentation for scratch versus promoted eval artifacts.
  - Trace diagnostics, report generation, and proposal-only patch suggestion helpers for local eval artifacts.
  - Schema/source CI gate workflow and optional runtime eval gate documentation.
  - Release evidence claim boundary template for source/runtime/cache/release/UAT/customer evidence separation.

### Changed

- Bumped plugin metadata to `0.4.2` for the trace-first eval platform source-validation release.
- Updated the v0.4.x eval platform roadmap status to reflect that V042 through V045 source-validation slices have landed.
- Documented that the current v0.4.x evidence status is `source_validation`: local schema/source/tests/report/patch-suggestion checks support implementation conformance review, but do not prove runtime, cache, release, UAT, customer, marketplace, or package readiness.

### Notes

- Hosted GitHub Actions run evidence is not attached in this repository state; the workflow file has been added, but hosted CI execution remains separate evidence.
- Runtime evidence still requires a named installed plugin root, source root, refresh or source/cache equivalence method, run scope, commands/trials, limitations, and missing evidence.
- No marketplace package readiness, plugin cache refresh, release readiness, UAT readiness, customer readiness, automatic skill mutation, automatic patch application, or runtime artifact promotion is claimed by these source-validation changes.

## v0.4.1 - 2026-06-22

### Added

- Added `evals/prompts/trace-first-verify-review.csv` as a compact trace-ready verify/review eval slice for v0.4.1.
- Added targeted rows for verify scope-first reports, code-diff-only readiness boundaries, QA failure shape, clean-review fan-out, self-review blocking, read-only clean review, missing validation, and low-risk coordinator intake exceptions.
- Added deterministic runner behavior checks for code-diff-only readiness pass claims and low-risk archive or branch-cleanup readiness claims.

### Changed

- Bumped plugin metadata to `0.4.1` for the compact trace-ready verify/review eval slice.
- Wired `trace-first-verify-review.csv` into `DEFAULT_SUITES` and the trace-ready routing summary path while preserving the legacy `routing_rows` summary field.
- Renamed the runner's primary trace-ready row helper to `is_trace_ready_row()` and retained `is_routing_reliability_row()` as a compatibility alias.
- Documented that the v0.4.1 trace-first suite is a compact targeted smoke path, not the full v0.4.x schema, score, report, or trace-diagnostics platform.

### Notes

- This release does not add public skills, runtime dependencies, task databases, hooks, MCP servers, marketplace behavior, or a full trace/schema/report platform.
- Local schema, syntax, CSV, and runner tests support the compact v0.4.1 scope; real runtime baseline evidence still requires installed plugin cache/source equivalence or a supported refresh step before being treated as release-gating evidence.

## v0.3.4 - 2026-06-18

### Added

- Added governance baseline coverage for the current nine-skill public surface, including `dispatch` smoke coverage as a package-only runtime router.
- Added full audience-first artifact header requirements across shared artifact rules, PRD templates, and verify document review lenses.
- Added `Needs Confirmation` and recommended-answer impact guidance to `to-prd` grill-before-write flow.
- Added `Contract Sources` and stricter confirmed-backend versus mock-field separation to prototype contract-boundary guidance.
- Added QA failure `Gap Closure Plan` and re-QA requirements for the verify -> implement -> verify loop.

### Changed

- Bumped plugin metadata to `0.3.4` for the governance baseline and skill guardrail release.
- Extended repo-local `AGENTS.md` with layout, build/test/lint, review, done definition, git boundary, artifact, and forbidden-behavior rules.
- Required all nine public skills, including `dispatch`, to apply the repo-local `AGENTS.md` Done Definition when maintaining this repository.
- Tightened `implement` mini-plan wording to `What / Why / Files / Test / Risk` and added unverified-claims reporting.
- Tightened `verify` runtime smoke output so final verification reports start with the literal six-field `Verification Scope` block.
- Extended handoff review packages with goal, current decision, and git boundary fields.
- Updated smoke and guardrail regression prompts for v0.3.4 governance coverage.

### Notes

- No new public skill, runtime executor, task database, automation, hook, MCP server, or plugin split is added in this release.
- `dispatch` remains a public package generator and router; it does not execute runtime tools, spawn subagents, create worktrees, push, open PRs, close issues, or mutate remotes.
- Runtime release evidence requires refreshing the installed plugin cache and checking cache/source equivalence before using `evals/run_runtime.py` results as release-gating evidence.

## v0.3.3 - 2026-06-17

### Changed

- Tightened the v0.3.3 managed worktree closeout contract with registry records, state-change events, original-goal verdicts, same-base serial closeout fields, archive recovery evidence, review coverage reporting, and metric inputs.
- Extended managed worktree lifecycle fixtures to cover three closeout paths, no-goal active blocking, same-base closeout serialization, and archive recovery completeness.
- Recorded a v0.3.3 managed worktree closeout lifecycle trial baseline covering supported cache refresh, source/cache equivalence, child worktree review package return, archive execution, worktree removal observation, no-branch cleanup decision, controlled local merge-back, and branch/worktree deletion cleanup.

## v0.3.2 - 2026-06-17

### Changed

- Co-located the `codex_app_managed_worktree_thread` adapter contract under `skills/dispatch/adapters/codex_app_managed_worktree_thread/` as an internal dispatch adapter contract while keeping `dispatch` package-only and no-execution by default.
- Marked the earlier External A managed worktree adapter task package as superseded so maintainers do not treat the separate-repository plan as the current source of truth.
- Added managed worktree adapter scenario coverage and runtime harness support for single-file fixtures used by dispatch scenario rows.

## v0.3.1 - 2026-06-16

### Added

- Added `dispatch` as the ninth public skill for package-only runtime routing across managed worktree threads, subagent packages, direct main-thread work, read-only main-thread work, and clean reviewer routes.
- Added Dispatch Package v2, Result Package, runtime adapter, routing profile, and conflict preflight contracts under `skills/dispatch/`.
- Added the shared Goal Contract spec, lightweight Goal Contract linter, and focused pass/fail fixtures.
- Added dispatch and Goal Contract prompt/scenario fixtures for targeted evaluation and linter coverage.
- Promoted `routing-reliability.csv` into the default runtime suite for personal and team-internal Groundwork regression coverage.
- Added a promotion baseline record for the routing reliability default-suite decision.

### Changed

- Bumped plugin metadata to `0.3.1` for the dispatch public skill release, cache-visible skill surface change, and routing reliability default-suite promotion.
- Extended `to-issues` and `triage` outputs with runtime-routing candidates, Goal Contract fields, Preferred Runtime, and Result Package expectations.
- Documented the dispatch runtime workflow from PRD/task slicing through triage, dispatch, runtime adapter output, and verification.
- Marked dispatch runtime prompts as targeted-only and Goal Contract prompts as fixture-only so default runtime eval discovery can skip them unless explicitly requested.
- Updated runtime trial guidance so routing reliability remains targeted for promotion review, but is part of default coverage starting in v0.3.1.

### Notes

- `dispatch` is package-only in this release: it routes accepted work and prepares runtime packages, but it does not call runtime tools, spawn subagents, create worktrees, push, open PRs, close issues, or mutate remotes.
- Full runtime eval against `dispatch` requires reinstalling or refreshing the plugin cache so Codex loads `groundwork@0.3.1` with the new public skill surface.
- At v0.3.1 release time, `codex-managed-worktree-threads` adapter implementation changes remained external to this repository. Later unreleased work co-locates the Groundwork adapter contract under `skills/dispatch/adapters/` while still keeping runtime execution gated and non-default.
- This is not a public SLA, learned routing service, hook, MCP server, tracker integration, or task CRUD expansion.

## v0.3.0 - 2026-05-26

### Added

- Added `skills/_shared/LIFECYCLE-STATE.md` as a narrow shared lifecycle state contract.
- Defined optional workstream-scoped `artifacts/<workstream-slug>/STATE.md` for resumable multi-session R&D work.
- Defined optional `artifacts/<workstream-slug>/ROADMAP.md` for multi-milestone or multi-stage initiatives.
- Added lifecycle state boundary references to `handoff`, `verify`, `triage`, and `write-plan`.
- Added `evals/prompts/lifecycle-state.csv` regression prompts for small-task no-state behavior, pause/resume, verify gap closure, re-verify closure, multi-milestone roadmap, stale-state conflict, and GSD clone prevention.

### Changed

- Bumped plugin metadata to `0.3.0` for the lifecycle-state contract release.
- Clarified that lifecycle state is opt-in durable artifact state, not a project task database.
- Clarified that `handoff` references lifecycle state but does not own it.
- Clarified that `.groundwork/*` remains runtime scratch and is not the default durable lifecycle artifact location.
- Clarified legacy `.groundwork/tasks/<task-id>/` wording where it could be confused with lifecycle state.

### Notes

- No new public skill, public CLI, installed hook, runtime daemon, task CRUD, tracker integration, statusline hook, MCP server, `.planning`, `.gsd`, or project-global lifecycle `STATE.md` is added.

## v0.2.3 - 2026-05-25

### Changed

- Tightened `verify` final-report opening compliance so every verify-loaded report body starts with the full `Verification Scope` block, including UI routing, contract review, QA failure handling, git-boundary review, verify-owned approval gates, release readiness, and subagent prompt preparation. Runtime safety gates that preempt skill loading are treated as no-execution gate evidence, not verify scope-first evidence.
- Required the full `Verification Scope` field block before specialized verify payloads, and clarified routing boundaries so implementation conformance review stays in `implement` while prototype contract-boundary review stays in `prototype`.
- Front-loaded the exact `QA Failure` shape in `verify` and made missing failure details explicit as `not provided` or `unverified`.
- Split the git-boundary regression prompt into isolated fixture context (`gr-008a`) and repo-root context (`gr-008b`) with explicit intended and unrelated file scopes.
- Bumped plugin metadata to `0.2.3` for the runtime-drift hardening cut.

### Notes

- No `STATE.md`, CLI, new public skill, hook, MCP server, task CRUD, tracker integration, marketplace publishing flow, or standalone `review` skill is added.

## v0.2.2 - 2026-05-25

### Added

- Added reader-first artifact policy, artifact directory policy, implementation notes policy, nightly harness design, skill success metrics, and quarantined learning guidance.
- Added guardrail regression prompts and frontend contract fixture coverage for verify, implement, to-prd, prototype, handoff, and git-boundary behavior.
- Added `evals/baselines/2026-05-22-v0.2.2-runtime-baseline.md` as the real Codex CLI runtime baseline and drift report for the v0.2.x runtime.

### Changed

- Tightened verify scope-first output, QA-fix-QA shape, contract review, UI tool routing, subagent delegation, and git-boundary guidance.
- Hardened `to-prd` grill-before-write behavior, prototype contract-boundary handling, implementation mini-plan/self-review flow, and handoff review-package shape.

### Notes

- The v0.2.2 runtime report recorded the then-current `0.2.0` manifest as observed evidence. v0.2.3 updates the manifest and closes the remaining runtime-drift metadata gap.

## v0.2.0 - 2026-05-21

### Added

- Added v0.2 skill reliability fixtures for `implement`, `write-plan`, `verify`, and `prototype`.
- Added `evals/prompts/reliability.csv` as a cross-skill prompt set for natural invocation and adjacent-boundary drift.
- Added small fixture workspaces for empty-source planning, no-tests planning, and static HTML prototype review.
- Added local fixture validation and runtime trial baselines for the v0.2 reliability prompt set.
- Added a per-row runtime evidence summary to the v0.2 runtime trial baseline.

### Changed

- Bumped plugin metadata to `0.2.0` for the reliability-hardening cut.
- Tightened target skill instructions for implementation review, no-invented-path planning, skeptical verification, and prototype evidence reporting.
- Patched v0.2 reliability prompts after runtime drift so `implement` and `write-plan` load naturally without explicit skill invocation.

### Notes

- No new public skills, CLI, hooks, MCP server, tracker API integration, task CRUD, public `gate` skill, standalone `review` skill, or marketplace publishing flow is added.

## v0.1.1 - 2026-05-21

### Added

- Added structured explicit invocation smoke fixtures in `evals/prompts/smoke.csv`.
- Added second-batch safety prompt fixtures in `evals/prompts/safety.csv` for migration, destructive command, remote tracker mutation, shared skill mutation, publish/push gate, and sensitive handoff redaction scenarios.
- Added the `evals/baselines/2026-05-21-v0.1.1-runtime-trial.md` runtime-trial baseline.

### Changed

- Bumped plugin metadata to `0.1.1` and filled `homepage` / `repository` with the GitHub repository URL.
- Updated runtime trial guidance to point to structured smoke and safety fixtures while keeping full runtime execution manual.

### Notes

- No public skill surface, CLI, hooks, MCP server, tracker API integration, task CRUD, public `gate` skill, or standalone `review` skill is added in this hardening cut.

## v0.1.0 - 2026-05-21

Initial tagged release of Groundwork as a Codex-native personal R&D workflow base.

### Added

- Added Codex plugin packaging through `.codex-plugin/plugin.json`.
- Added eight public skills: `to-prd`, `to-issues`, `triage`, `write-plan`, `prototype`, `implement`, `verify`, and `handoff`.
- Added embedded workflow branches for `scope`, `contract`, `artifact`, `diagnose`, `gate`, and `standards`.
- Added first-cut supporting skill assets: `triage/AGENT-BRIEF.md`, `prototype/LOGIC.md`, and `prototype/UI.md`.
- Added PRD, architecture, product principles, workflow taxonomy, borrowed-source decisions, framework comparison, and user scenario research docs.
- Added prompt fixtures, R&D scenario fixtures, runtime trial checklist, and baseline records under `evals/`.
- Added the `minimal-task-search` runtime fixture for stable `write-plan`, `implement`, and `verify` trials.

### Validated

- Verified local plugin discovery and the eight-skill public surface.
- Verified explicit invocation smoke prompts for all eight public skills.
- Verified representative workflow prompts from PRD shaping through handoff.
- Verified direct fallback for small title or wording rewrite work.
- Verified fixture-driven `write-plan`, `implement`, and `verify` behavior against the `minimal-task-search` fixture.
- Verified Codex App approval / Auto Review blocks an external push in the `rt-010-app` safety trial.

### Safety

- Added artifact restraint rules so files are written only when reuse, review, execution, verification, or handoff justifies them.
- Added redaction requirements for secrets, credentials, PII, sensitive logs, screenshots, requests, and database rows before writing or quoting artifacts.
- Added embedded gate rules for risky writes, including push, deploy, publish, migration, destructive command, data write, remote tracker mutation, and shared skill mutation.
- Clarified that Groundwork `gate` is a workflow preflight and communication contract, while execution safety remains the responsibility of Codex sandboxing, approval, Auto Review, and host permissions.

### Not Included

- No standalone agent runtime, CLI, hooks, MCP server, tracker API integration, task CRUD, marketplace publishing flow, public `gate` skill, or standalone `review` skill.
- No production-hardened skill behavior or broad release thresholds.
