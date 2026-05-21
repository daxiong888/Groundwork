---
name: to-prd
description: Create or revise a compact PRD/spec from rough product or engineering intent, evidence, feedback, or unclear acceptance. Use for 整理成 PRD, 写需求说明, clarify acceptance, or shape ambiguous requirements before task slicing. Do not use for tiny title or wording rewrites.
---

# to-prd

## Trigger Contract

Use this skill when the user asks to turn rough intent, conversation, prototype notes, UAT feedback, source evidence, or unclear requirements into PRD/spec intent and acceptance.

Should trigger:

- "把这个需求整理成 PRD"
- "根据这些反馈写一个需求说明"
- "这个功能目标还不清楚，帮我收敛一下"
- "把原型评审结论沉淀成规格"
- "先把验收标准写清楚"

Should not trigger:

- A small direct answer or rewrite is enough.
- The PRD is already accepted and the user asks to split tasks; use `to-issues`.
- The user asks only whether a task is ready; use `triage`.
- The user asks for code edits; use `implement`.
- The user asks for verification evidence; use `verify`.

## Required Evidence

Use user-provided context first. Inspect source, docs, prototype output, tickets, or data only when they materially affect correctness. If evidence is missing, state the gap instead of inventing product truth.

## Workflow

1. Identify the target reader and decision the PRD must support.
2. Separate verified facts, assumptions, open questions, and inferred intent.
3. Use `scope` if acceptance or user intent is unclear.
4. Keep the PRD compact and implementation-ready.
5. Recommend `to-issues` only when the PRD/spec is accepted enough to slice.

## Output Shape

```text
PRD Summary
Problem
Goal
Users / Actors
Scope
Out Of Scope
Acceptance Criteria
Evidence
Assumptions
Open Questions
Next Action
Artifact Recommendation
```

## Stop Condition

Stop when the PRD/spec intent, acceptance criteria, open questions, and next action are clear enough for user review or task slicing.

## Artifact Rule


Follow `skills/_shared/AUDIENCE-FIRST-ARTIFACT.md`: every new or materially updated durable artifact must include the required audience-first header fields exactly.
Follow `skills/_shared/ARTIFACT-DIRECTORY-POLICY.md`: local artifact placement must follow the directory policy, and `.groundwork/*` runtime directories are ignored by default and not committed unless explicitly approved.
Default to conversation output. Write or update a PRD file only when the user asks, when the output needs review/reuse/handoff, or when it becomes a task source of truth.

Redact secrets, credentials, PII, sensitive logs, screenshots, requests, and database rows before writing or quoting artifacts.
