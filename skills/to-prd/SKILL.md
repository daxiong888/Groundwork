---
name: to-prd
description: Use shared grilling before write when raw, draft, new, or ambiguous product/engineering intent needs clarification, then shape it into a compact PRD/spec before task slicing or implementation without inventing product truth. Use for 新需求, 需求收敛, 整理成 PRD, 写需求说明, clarify acceptance, UAT feedback, draft PRDs before acceptance, raw 方案/solution ideas, raw issue-split requests, vague urgency like 先做起来, or raw product, plugin install/upgrade, marketplace, runtime, version, workflow capability, and skill-selection changes. Do not use for tiny title or wording rewrites.
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
- Raw or draft solution ideas about product behavior, PRD artifacts before acceptance, plugin install/upgrade flows, marketplace behavior, runtime behavior, workflow changes, version enhancements, or skill-selection behavior before PRD/spec acceptance.
- Raw requests to split issues or tasks from "刚说的想法" or conversation-only intent before PRD/spec acceptance.
- Urgent raw ideas where the user has not clearly asked to bypass PRD/spec shaping.

Should not trigger:

- A small direct answer or rewrite is enough.
- The user asks to choose among enumerable options, compare tradeoffs, dependencies, decision criteria, or consequences without asking for a PRD/spec; use `skills/_shared/DECISION-MAPPING.md` as the shared lens instead.
- The user explicitly asks for grilling but the request is a tiny direct task, a repo-doc-answerable question, an accepted implementation task, an enumerable decision comparison, or a concrete prototype question; use the narrower route from `skills/_shared/GRILLING.md`.
- The PRD is already accepted and the user asks to split tasks; use `to-issues`.
- The user clearly says to skip PRD/spec shaping and implement directly; use `implement`, which still owns lifecycle, source, git, test, and risk gates.
- The user asks only whether a task is ready; use `triage`.
- The user asks for code edits; use `implement`.
- The user asks for verification evidence; use `verify`.

## Required Evidence

Use user-provided context first. Inspect source, docs, prototype output, tickets, or data when they can answer a question or materially affect correctness. If evidence is missing, state the gap and tag unknowns as **NEEDS CLARIFICATION** instead of inventing product truth.

When maintaining the Groundwork repository itself, apply the repo-local `AGENTS.md` Done Definition before reporting the work complete.

Use `skills/_shared/LIFECYCLE-PREFLIGHT.md` before shaping new requirements, version enhancements, workflow changes, runtime changes, plugin changes, skill-selection changes, or product decisions. Treat raw requirements and raw solution ideas as `Requirement State: raw` and route to shared grilling / PRD shaping by default. Do not proceed directly to implementation or issue splitting until the requirement is accepted enough to move downstream, unless the user explicitly requests that bypass.

Use `skills/_shared/GRILLING.md` when material ambiguity blocks PRD shaping and the unknowns are not yet enumerable. Ask one highest-impact question at a time, inspect repo/source evidence before asking when it can answer the question, and treat the result as clarification only. Shared grilling may prepare a PRD route, but it is not PRD acceptance, implementation readiness, clean review, independent verification, or runtime/browser/UAT/release evidence.

Use `skills/_shared/DOMAIN-LANGUAGE.md` when terminology materially affects acceptance, contract truth, source truth, prototype interpretation, verification, or handoff. Do not print a full `Domain Language / Term Conflict` bucket when no material term conflict exists. Keep glossary-only alignment separate from PRD truth, contract truth, source truth, runtime evidence, user confirmation, and unknown terms.

Use `skills/_shared/DECISION-MAPPING.md` when the options are already enumerable and the user needs a comparison of tradeoffs, dependencies, decision criteria, or consequences before choosing a path. Decision mapping is a shared reference, not a public `decision-map` skill, and it must not replace PRD shaping when the user explicitly asks to write requirements, acceptance criteria, or a spec.

## Workflow

1. Identify the target reader and decision the PRD must support.
2. Run lifecycle preflight and apply `skills/_shared/GRILLING.md` when material ambiguity blocks drafting: explicitly list target reader, decision supported, known facts, assumptions, open questions, and needs confirmation before drafting.
3. Inspect local code/docs/tickets/data first when they can answer a clarification question.
4. Ask one highest route-impact clarification question at a time. Use multiple questions only when the user asks for a non-interactive questionnaire or written PRD gap list.
5. Include a recommended answer or default decision and impact for each clarification question when evidence supports one.
6. Mark every unknown backend field, business state, unsupported ability, or missing acceptance detail as **NEEDS CLARIFICATION**; never invent product truth or mutate it from prototype-only mock data.
7. Apply `Domain Language / Term Conflict` only when terms materially affect acceptance, contract truth, source truth, prototype interpretation, verification, or handoff; omit it or mark `none material` in durable PRDs when no material conflict exists.
8. Use the evidence-layer labels `glossary_only`, `PRD_truth`, `contract_truth`, `source_truth`, `runtime_evidence`, `user_confirmed`, and `unknown` for material term conflicts.
9. Use the internal scope-shaping branch owned by `to-prd` if acceptance or user intent is unclear. Do not present `scope` as a public skill or route.
10. Keep the PRD compact and implementation-ready.
11. Include stable acceptance criteria IDs such as `AC-1`, `AC-2`.
12. Recommend `to-issues` only when the PRD/spec is accepted enough to slice.

## CHECKPOINTS

- STOP before drafting PRD content if the target reader, decision supported, known facts, assumptions, Open Questions bucket, or Needs Confirmation bucket is missing. The Open Questions and Needs Confirmation buckets may be `None` only when explicitly justified.
- STOP before creating or updating a PRD file unless the user asked for a durable artifact, the output must become a source of truth, or artifact promotion is explicitly justified.
- STOP before writing a durable PRD artifact unless the exact audience-first header fields are present: `Target Reader`, `Reader Action Needed`, `Decision Supported`, `Artifact Type`, `Source of Truth`, `Scope`, `Out of Scope`, `Evidence Level`, and `Safe to Share / Redaction Notes`.
- STOP before recommending `to-issues` when the PRD/spec is raw, draft-only, or still has blocking **NEEDS CLARIFICATION** items.
- STOP before promoting a term conflict when its evidence layer is missing or when glossary-only alignment is being treated as contract/source/runtime/readiness truth.

## Failure Branches

| Trigger | Action | Output Requirement |
|---|---|---|
| Available evidence is missing | Mark source truth as `unknown` and ask the highest-impact clarification question. | Keep unknown fields as **NEEDS CLARIFICATION**. |
| Evidence conflicts with user input | Name the conflict and separate verified facts from assumptions. | Do not choose product truth unless a canonical source is clear. |
| User terminology conflicts with repo/source/API/UI terminology | Add a material `Domain Language / Term Conflict` only if correctness is affected; otherwise keep normal output compact. | Use `glossary_only`, `PRD_truth`, `contract_truth`, `source_truth`, `runtime_evidence`, `user_confirmed`, or `unknown` and name the promotion blocker. |
| User asks for a PRD file but facts are incomplete | Produce a draft with blocking gaps or stop for clarification. | Do not present the artifact as accepted or issue-ready. |
| User asks for a PRD artifact from sensitive source material | Redact secret values, private URLs, credentials, PII, sensitive logs, screenshots, requests, and database rows before drafting or writing. | Preserve only stable non-secret identifiers, source types, and decisions needed for review. |
| User asks to split issues from raw intent | Stop before `to-issues`. | State that PRD/spec acceptance is required first. |
| User gives a raw solution idea or vague urgency as if it were implementation-ready | Keep ownership in `to-prd`. | State that urgency or a proposed solution is not an explicit PRD bypass, then shape the requirement or ask the highest-impact clarification question. |

## Do Not

- Do not turn raw, draft-only, or contradictory requirements into accepted product truth.
- Do not invent backend fields, business states, metrics, owners, timelines, APIs, or acceptance details.
- Do not promote prototype-only mock data into confirmed source truth.
- Do not treat glossary-only alignment as accepted PRD truth, backend/API contract truth, source truth, implementation readiness, verification evidence, UAT evidence, release evidence, or customer readiness.
- Do not create `skills/socratic/SKILL.md`, `skills/grill/SKILL.md`, `skills/domain-language/SKILL.md`, or `skills/grill-with-docs/SKILL.md` for v0.5.1 MVP behavior.
- Do not write or update a durable PRD file just because the output looks reusable; require user intent, source-of-truth need, or artifact promotion.
- Do not recommend `to-issues` or `implement` while blocking **NEEDS CLARIFICATION** items remain unresolved.
- Recommend `verify` only for evidence/consistency review, not for readiness or downstream delivery, while blocking **NEEDS CLARIFICATION** items remain.
- Do not carry all grilling behavior inside `to-prd` without the shared boundary; apply `skills/_shared/GRILLING.md` and route direct answers, decision mapping, prototype exploration, accepted implementation work, and readiness checks away from PRD shaping when they are the narrower fit.
- Do not expose secrets, credentials, PII, sensitive logs, screenshots, private request payloads, or database rows in PRD artifacts.

## Output Shape

Use `GRILL-BEFORE-WRITE.md` and `PRD-TEMPLATE.md` as the default structure. `Domain Language / Term Conflict` is conditional: omit it in normal conversation output when no material term conflict exists, and omit it or mark `none material` in durable PRDs.

```text
Target Reader
Reader Action Needed
Decision Supported
Artifact Type
Source of Truth
Scope
Out of Scope
Evidence Level
Safe to Share / Redaction Notes
Known Facts
Assumptions
Open Questions
Needs Confirmation
Domain Language / Term Conflict
PRD Summary
Problem
Goal
Users / Actors
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
When a durable PRD is produced, place the audience-first header before the PRD body and keep its fields concise enough for a reviewer to decide what to do next. `Scope` and `Out of Scope` in the header may summarize the detailed PRD body sections, but the exact field names must remain present.

Redact secrets, credentials, PII, sensitive logs, screenshots, requests, and database rows before writing or quoting artifacts.
