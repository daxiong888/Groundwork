---
name: to-prd
description: Use grill-before-write to shape raw or ambiguous product/engineering intent into a compact PRD/spec before task slicing or implementation, without inventing product truth. Use for 新需求, 需求收敛, 整理成 PRD, 写需求说明, clarify acceptance, UAT feedback, or version/workflow changes. Do not use for tiny title or wording rewrites.
---

# to-prd

## Trigger Contract

Use this skill when the user asks to turn rough intent, conversation, prototype notes, UAT feedback, source evidence, or unclear requirements into PRD/spec intent and acceptance.

Should trigger:

- "新需求：先帮我梳理需求和验收"
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

Use user-provided context first. Inspect source, docs, prototype output, tickets, or data when they can answer a question or materially affect correctness. If evidence is missing, state the gap and tag unknowns as **NEEDS CLARIFICATION** instead of inventing product truth.

Use `skills/_shared/LIFECYCLE-PREFLIGHT.md` before shaping new requirements, version enhancements, workflow changes, or product decisions. Treat raw requirements as `Requirement State: raw` and route to grill-before-write / PRD shaping by default. Do not proceed directly to implementation or issue splitting until the requirement is accepted enough to move downstream, unless the user explicitly requests that bypass.

## Workflow

1. Identify the target reader and decision the PRD must support.
2. Run lifecycle preflight and the grill-before-write gate: explicitly list target reader, decision supported, known facts, assumptions, and open questions before drafting.
3. Inspect local code/docs/tickets/data first when they can answer a clarification question.
4. Ask at most 5 high-impact clarification questions; in interactive work, ask one question at a time.
5. Include a recommended answer or default decision for each clarification question when evidence supports one.
6. Mark every unknown backend field, business state, unsupported ability, or missing acceptance detail as **NEEDS CLARIFICATION**; never invent product truth or mutate it from prototype-only mock data.
7. Use `scope` if acceptance or user intent is unclear.
8. Keep the PRD compact and implementation-ready.
9. Include stable acceptance criteria IDs such as `AC-1`, `AC-2`.
10. Recommend `to-issues` only when the PRD/spec is accepted enough to slice.

## CHECKPOINTS

- STOP before drafting PRD content if target reader, decision supported, known facts, assumptions, or open questions are missing.
- STOP before creating or updating a PRD file unless the user asked for a durable artifact, the output must become a source of truth, or artifact promotion is explicitly justified.
- STOP before recommending `to-issues` when the PRD/spec is raw, draft-only, or still has blocking **NEEDS CLARIFICATION** items.

## Failure Branches

| Trigger | Action | Output Requirement |
|---|---|---|
| Available evidence is missing | Mark source truth as `unknown` and ask the highest-impact clarification question. | Keep unknown fields as **NEEDS CLARIFICATION**. |
| Evidence conflicts with user input | Name the conflict and separate verified facts from assumptions. | Do not choose product truth unless a canonical source is clear. |
| User asks for a PRD file but facts are incomplete | Produce a draft with blocking gaps or stop for clarification. | Do not present the artifact as accepted or issue-ready. |
| User asks to split issues from raw intent | Stop before `to-issues`. | State that PRD/spec acceptance is required first. |

## Do Not

- Do not turn raw, draft-only, or contradictory requirements into accepted product truth.
- Do not invent backend fields, business states, metrics, owners, timelines, APIs, or acceptance details.
- Do not promote prototype-only mock data into confirmed source truth.
- Do not write or update a durable PRD file just because the output looks reusable; require user intent, source-of-truth need, or artifact promotion.
- Do not recommend `to-issues`, `implement`, or `verify` while blocking **NEEDS CLARIFICATION** items remain unresolved.
- Do not expose secrets, credentials, PII, sensitive logs, screenshots, private request payloads, or database rows in PRD artifacts.

## Output Shape

Use `GRILL-BEFORE-WRITE.md` and `PRD-TEMPLATE.md` as the default structure.

```text
Target Reader
Decision Supported
Known Facts
Assumptions
Open Questions
PRD Summary
Problem
Goal
Users / Actors
Scope
Out Of Scope
Acceptance Criteria (AC IDs required)
Evidence
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
