# Groundwork Project Definition

For v0.1, `docs/prd.md` is the product source of truth. This file describes the broader project intent and should not expand MVP implementation scope beyond the PRD.

## One-Liner

Groundwork is a Codex-native personal base for evidence-first R&D work: turn product intent into managed tasks, ground execution in real project evidence, and produce verified deliverables that can be resumed.

## Why This Exists

Existing AI coding workflow frameworks each contain useful pieces:

- Trellis makes project work structured and persistent.
- Superpowers enforces disciplined planning and TDD.
- gstack brings specialist review perspectives.
- GSD manages long-running autonomous development.
- mattpocock/skills keeps skills small, composable, human-controlled, and issue-source-first without owning a task database.

Groundwork exists to turn those useful pieces into a personal Codex-native R&D base. It should absorb the patterns that help daily work, exclude the parts that add unnecessary installation, ceremony, role-play, or runtime complexity, and evolve over time as real tasks expose new needs.

The current product shape can be stated plainly: Superpowers is the Codex plugin skeleton reference, mattpocock/skills is the strongest skill/workflow behavior reference, and Groundwork is the curated R&D base that decides what to keep, rename, merge, or reject.

## Target User

The primary user is a pragmatic engineering/product operator who uses Codex across:

- backend/frontend implementation
- evidence-backed PRD writing
- task slicing and task-state management
- static prototype creation and review
- UAT validation and release notes
- frontend integration documentation
- local tool and skill/plugin development

The user values direct execution, but only after the facts are grounded.

## Product Boundary

Groundwork should provide:

- conservative workflow selection
- PRD/spec creation and refinement
- lightweight task context and issue-source-first task management, with `.groundwork/tasks/<task-id>/` only as a local fallback
- implementation planning
- evidence-first diagnosis
- requirement and delivery-slice clarification
- handoff and continuation summaries
- plugin-local skills, scripts, templates, and optional hooks that do not pollute shared global skill surfaces

Groundwork should not provide:

- a universal autonomous coding agent
- a mandatory process for every task
- a loose aggregation of Superpowers and mattpocock skills without Groundwork-native boundaries
- a large role-playing organization
- project-specific adapters in the core plugin
- hidden remote state changes
- speculative document rewrites without source evidence
- market-positioning work against other frameworks

## Success Criteria

Groundwork is working when:

- small tasks stay small
- ambiguous tasks become clear enough to act on
- PRD/spec, task, plan, implementation, verification, and handoff state stay linked when a task is managed
- suspected issues are verified before being modified
- frontend/API/DB/state-flow documents match code truth
- UAT and customer-facing summaries separate verified links from data or environment risk
- long work can resume without rediscovering context
- subagents are used only when they materially improve throughput and remain controlled
- new patterns from other frameworks can be adopted incrementally without replacing the base

## Initial Product Question

What is the smallest useful personal R&D base that can absorb good framework ideas over time without making Codex feel trapped inside a framework?
