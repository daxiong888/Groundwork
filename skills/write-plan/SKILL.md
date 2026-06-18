---
name: write-plan
description: Write a concise implementation plan for accepted task context with dependencies stop conditions and verification checkpoints. Use for 写实现计划, plan accepted work, sequence changes, or prepare execution before edits without inventing paths.
---

# write-plan

## Trigger Contract

Use this skill when a task is accepted enough to plan implementation but code edits have not started.

Should trigger:

- "给这个任务写实现计划"
- "先 plan 一下怎么做"
- "这个 ready-for-agent 任务怎么落地"
- "按这个 issue 写执行步骤"
- "实现前列一下改动顺序和验证点"

Should not trigger:

- Requirements are unclear; use `to-prd`.
- Work units are not split; use `to-issues`.
- The user asks whether the task is ready; use `triage`.
- The user asks to make code changes now; use `implement`.
- The user asks to implement now and only needs an inline mini-plan; `implement` uses `skills/implement/LIGHTWEIGHT-PLAN.md`.
- The user asks for proof after changes; use `verify`.

## Required Evidence

Use the accepted task, PRD/spec, issue, current source references, existing lifecycle state, roadmap, and known verification expectations. Do not invent exact file paths, APIs, schemas, or commands before inspection. If the workspace has no source or tests, say so and plan first inspection or validation steps instead of naming fictional files.

When maintaining the Groundwork repository itself, apply the repo-local `AGENTS.md` Done Definition before reporting the work complete.

Use `skills/_shared/LIFECYCLE-STATE.md` when planning a multi-stage or multi-session workstream. Do not create lifecycle files or recommend lifecycle artifacts for ordinary implementation plans.

## Workflow

1. State the task source and accepted goal.
2. Read existing `STATE.md` / `ROADMAP.md` when the workstream is multi-stage, cross-session, or release/UAT gated.
3. Check canonical sources before trusting lifecycle state.
4. Inspect source when exact paths, APIs, schemas, or commands matter.
5. Add inline `Contract Notes` when API/DB/state/frontend/docs alignment matters.
   - `contract` is an internal planning concern, not a public skill route.
   - If contract facts are uninspected, mark them as unverified and plan the next source check instead of naming exact endpoints, fields, schemas, or state transitions.
   - If the user asks to validate contract truth or readiness, route to `verify`.
   - If the user asks to explore a throwaway interaction, UI state, or business-rule question before source truth exists, route to `prototype`.
6. List focused implementation steps and dependencies.
7. Include stop conditions and verification checkpoints.
8. Recommend `implement` only when the plan is executable.

## CHECKPOINTS

- STOP before writing a full plan unless the task context is accepted enough: accepted PRD/spec, issue, task brief, or user-confirmed implementation goal with boundaries.
- STOP before naming exact files, APIs, schemas, commands, or tests unless they were inspected or provided by a canonical source; otherwise plan the first inspection step.
- STOP before recommending `implement` unless dependencies, stop conditions, and verification checkpoints are clear enough for execution.
- Keep small scoped implementation tasks in `implement` with `skills/implement/LIGHTWEIGHT-PLAN.md` when the inline mini-plan is sufficient.

## Failure Branches

| Trigger | Action | Output Requirement |
|---|---|---|
| Task context is raw, draft-only, or readiness is unknown | Stop planning and route to `to-prd`, `to-issues`, or `triage`. | State the missing acceptance or readiness evidence. |
| Dependencies or ordering cannot be resolved from available evidence | Keep the plan at inspection/checkpoint level. | Mark unresolved dependencies and the next evidence-gathering step; do not invent sequence certainty. |
| Verification path or stop condition is missing | Stop before executable handoff. | Ask for the missing check or include it as a blocking plan gap. |

## Do Not

- Do not force a full `write-plan` workflow for small implementation tasks that only need the `implement` lightweight plan.
- Do not invent source paths, commands, schemas, owners, dependencies, or verification evidence to make the plan look executable.
- Do not create lifecycle artifacts, `STATE.md`, `ROADMAP.md`, or durable plan artifacts for ordinary implementation plans or ordinary single-session work.

## Output Shape

Use this as the maximum field set for a full implementation plan. For ordinary lightweight plans, omit conditional lifecycle, contract, and artifact fields that do not affect execution.

```text
Plan Summary
Source
Assumptions
Lifecycle Inputs (only when multi-stage, multi-session, release/UAT gated, or existing lifecycle state is relevant)
- STATE.md:
- ROADMAP.md:
- Stale State Risk:
- Roadmap Needed:
Files / Areas Inspected
Implementation Steps
Contract Notes (include inline when API/DB/state/frontend/docs alignment or uncertainty affects implementation)
Risks / Gates
Verification Checkpoints
Stop Condition
Next Action
Artifact Recommendation (only when artifact promotion is required or useful; otherwise omit; if a boundary decision is needed, say conversation-only)
```

## Stop Condition

Stop when steps, dependencies, risks, verification checkpoints, and stop condition are clear enough for implementation.

If implementation can safely proceed with only What, Why, Files, Test, and Risk, keep the plan inside `implement` instead of forcing this full-plan workflow.

## Artifact Rule


Follow `skills/_shared/AUDIENCE-FIRST-ARTIFACT.md`: every new or materially updated durable artifact must include the required audience-first header fields exactly.
Follow `skills/_shared/ARTIFACT-DIRECTORY-POLICY.md`: local artifact placement must follow the directory policy, and `.groundwork/*` runtime directories are ignored by default and not committed unless explicitly approved.
Default to conversation output. Write a plan artifact only when it will guide execution, review, handoff, or later verification.

Redact secrets, credentials, PII, sensitive logs, screenshots, requests, and database rows before writing or quoting artifacts.
