# Changelog

All notable changes to Groundwork are documented in this file.

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
