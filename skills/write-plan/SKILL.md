---
name: write-plan
description: Write a concise implementation plan for an accepted task, including dependencies, stop conditions, and verification checkpoints before edits. Not for raw requirements, slicing, direct implementation, readiness verification, dispatch routing, or wiki maintenance.
---

# write-plan

## Trigger Contract

Use when an accepted task is ready for implementation planning but edits have not started.

Route away:

- Unclear requirements -> `to-prd`.
- Work not split -> `to-issues`.
- Enumerable option choice before implementation path is accepted -> `skills/_shared/DECISION-MAPPING.md`.
- Readiness check -> `triage`.
- Code edits now -> `implement` with `skills/implement/LIGHTWEIGHT-PLAN.md`.
- Post-change proof -> `verify`.
- Runtime/subagent assignment -> `dispatch`.

## Required Evidence

Use accepted task/PRD/spec/issue, source references, lifecycle state when relevant, roadmap, and verification expectations. Do not invent exact paths, APIs, schemas, owners, commands, dependencies, or tests before inspection; plan the first inspection step instead.

For Groundwork repo maintenance, apply repo-local `AGENTS.md` before reporting complete.

Load only when needed:

- `skills/_shared/DECISION-MAPPING.md` only before an implementation path is accepted or when the user explicitly asks option comparison.
- `skills/_shared/LIFECYCLE-STATE.md` only for multi-stage, multi-session, release/UAT-gated, or existing lifecycle-state workstreams.
- `skills/_shared/CONTRACT-NOTES.md` only when API/DB/state/frontend/docs alignment affects implementation; uninspected contract facts stay unverified. Contract validation/readiness belongs to `verify`; throwaway interaction exploration belongs to `prototype`.

## Workflow

1. State task source and accepted goal.
2. Read `STATE.md` / `ROADMAP.md` only when multi-stage, cross-session, or release/UAT-gated.
3. Check canonical sources before trusting lifecycle state.
4. Inspect source when exact paths, APIs, schemas, commands, or tests matter.
5. List focused steps, dependencies, risks/gates, stop conditions, and verification checkpoints.
6. Recommend `implement` only when executable.

## Hard Stops

- Stop before a full plan unless context is accepted enough: accepted PRD/spec, issue, task brief, or user-confirmed implementation goal with boundaries.
- Stop before naming exact files/APIs/schemas/commands/tests unless inspected or provided by canonical source.
- Stop before recommending implementation unless dependencies, stop conditions, and verification checkpoints are clear.
- Keep small implementation tasks in `implement` with the lightweight mini-plan.
- Do not create lifecycle artifacts or durable plan artifacts for ordinary single-session plans.

## Output Shape

```text
Plan Summary
Source
Assumptions
Lifecycle Inputs (only when relevant)
- STATE.md:
- ROADMAP.md:
- Stale State Risk: none / low / medium / high / unknown
- Roadmap Needed: yes / no
- Roadmap Threshold Met:
Files / Areas Inspected
Implementation Steps
Contract Notes
Risks / Gates
Verification Checkpoints
Stop Condition
Next Action
Artifact Recommendation
```

## Stop Condition

Stop when steps, dependencies, risks, verification checkpoints, and stop condition are clear enough for implementation. If What/Why/Files/Test/Risk is sufficient, keep the plan inside `implement`.

## Artifact Rule

Default to conversation output. Write a plan artifact only when it will guide execution, review, handoff, or later verification. Follow `skills/_shared/AUDIENCE-FIRST-ARTIFACT.md` and `skills/_shared/ARTIFACT-DIRECTORY-POLICY.md`. Redact secrets, credentials, PII, sensitive logs, screenshots, private payloads, and database rows.
