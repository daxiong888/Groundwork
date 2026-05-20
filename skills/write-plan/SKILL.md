---
name: write-plan
description: Write a concise implementation plan for accepted task context with dependencies stop conditions and verification checkpoints. Use when the user asks to 写实现计划, plan accepted work, sequence changes, or prepare execution before edits.
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
- The user asks for proof after changes; use `verify`.

## Required Evidence

Use the accepted task, PRD/spec, issue, current source references, and known verification expectations. Do not invent exact file paths, APIs, schemas, or commands before inspection.

## Workflow

1. State the task source and accepted goal.
2. Inspect source when exact paths, APIs, schemas, or commands matter.
3. Use `contract` if API/DB/state/frontend/docs alignment matters.
4. List focused implementation steps and dependencies.
5. Include stop conditions and verification checkpoints.
6. Recommend `implement` only when the plan is executable.

## Output Shape

```text
Plan Summary
Source
Assumptions
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

Stop when steps, dependencies, risks, verification checkpoints, and stop condition are clear enough for implementation.

## Artifact Rule

Default to conversation output. Write a plan artifact only when it will guide execution, review, handoff, or later verification.

Redact secrets, credentials, PII, sensitive logs, screenshots, requests, and database rows before writing or quoting artifacts.
