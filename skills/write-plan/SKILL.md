---
name: write-plan
description: Concise implementation plan for an accepted task before edits: dependencies, stops, verification checkpoints. Not for raw requirements, slicing, implementation, readiness, dispatch, or wiki.
---

# write-plan

## Trigger Contract

Use when an accepted task is ready for implementation planning and edits have not started.

Route away:

- Unclear requirements -> `to-prd`.
- Work not split -> `to-issues`.
- Enumerable option choice before implementation path is accepted -> `skills/_shared/DECISION-MAPPING.md`.
- Readiness check -> `triage`.
- Code edits now -> `implement` with `skills/implement/LIGHTWEIGHT-PLAN.md`.
- Post-change proof -> `verify`.
- Runtime/subagent assignment -> `dispatch`.

## Required Evidence

Use accepted task/PRD/spec/issue, source refs, relevant lifecycle state/roadmap, and verification expectations. Do not invent exact paths, APIs, schemas, owners, commands, dependencies, or tests before inspection; plan the first inspection step instead.

Load only when needed:

- `skills/_shared/DECISION-MAPPING.md` only before implementation path acceptance or explicit option comparison.
- `skills/_shared/LIFECYCLE-STATE.md` only for multi-stage, multi-session, release/UAT-gated, or existing lifecycle-state workstreams.
- `skills/_shared/CONTRACT-NOTES.md` only when API/DB/state/frontend/docs alignment affects implementation; uninspected contract facts stay unverified. Contract validation/readiness belongs to `verify`; throwaway exploration to `prototype`.
- `skills/_shared/FIRST-PRINCIPLES.md` only when the plan must establish causal path, constraints, root cause/core bottleneck, smallest sufficient change, or falsifiable verification before edits.
- `skills/_shared/ADVERSARIAL-REVIEW.md` only when plan risk depends on hidden assumptions, edge states, missing evidence, scope creep, or claim boundaries.

## Workflow

1. State task source and accepted goal.
2. Read `STATE.md` / `ROADMAP.md` only when multi-stage, cross-session, or release/UAT-gated.
3. Check canonical sources before trusting lifecycle state.
4. Inspect source when exact paths, APIs, schemas, commands, or tests matter.
5. List steps, dependencies, risks/gates, stop conditions, and verification checkpoints.
6. Recommend `implement` only when executable.

## Hard Stops

- Stop before a full plan unless context is accepted enough: accepted PRD/spec, issue, task brief, or user-confirmed implementation goal with boundaries.
- Stop before naming exact files/APIs/schemas/commands/tests unless inspected or provided by canonical source.
- Stop before recommending implementation unless dependencies, stop conditions, and verification checkpoints are clear.
- Keep small implementation tasks in `implement` with the lightweight mini-plan.
- Do not create lifecycle artifacts or durable plan artifacts for ordinary single-session plans.

## Output Shape

Default to accepted goal, ordered implementation steps, material dependencies or gates, verification checkpoints, and stop condition. Add source, assumptions, lifecycle inputs, inspected files, contract notes, next action, or artifact recommendation only when they affect execution.

## Stop Condition

Stop when steps, dependencies, risks, verification checkpoints, and stop condition are clear enough for implementation. If What/Why/Files/Test/Risk is sufficient, keep the plan inside `implement`.

## Artifact Rule

Default to conversation output. Write a plan artifact only when it will guide execution, review, handoff, or later verification. Follow audience/artifact policy and redact sensitive data.
