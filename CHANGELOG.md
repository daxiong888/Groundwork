# Changelog

All notable changes to Groundwork are documented in this file.

## v0.2.0 - Unreleased

### Added

- Added v0.2 skill reliability fixtures for `implement`, `write-plan`, `verify`, and `prototype`.
- Added `evals/prompts/reliability.csv` as a cross-skill prompt set for natural invocation and adjacent-boundary drift.
- Added small fixture workspaces for empty-source planning, no-tests planning, and static HTML prototype review.
- Added local fixture validation and runtime trial baselines for the v0.2 reliability prompt set.

### Changed

- Bumped plugin metadata to `0.2.0` for runtime testing of the reliability-hardening cut.
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
