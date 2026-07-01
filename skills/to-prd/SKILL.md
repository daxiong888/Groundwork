---
name: to-prd
description: Shape raw or ambiguous product/engineering intent into a compact PRD/spec before slicing or implementation. Not for tiny rewrites, accepted tasks, implementation, verification, handoff, dispatch, or wiki maintenance.
---

# to-prd

## Trigger Contract

Use when rough intent, prototype notes, feedback, or unclear requirements need PRD/spec intent and acceptance criteria.

Route away:

- Direct rewrite or small answer -> answer directly.
- Enumerable option comparison -> `skills/_shared/DECISION-MAPPING.md`.
- Accepted PRD/spec to tasks -> `to-issues`.
- Direct code edit -> `implement`.
- Readiness/evidence proof -> `verify`.
- Current wiki maintenance -> `wiki`.

Raw plugin install/upgrade, marketplace, runtime, workflow, version, or skill-selection ideas remain `to-prd` until accepted or explicitly bypassed.

## Fast Path: Prompt-Provided Compact PRD

Use this as the hard default when the user provides or names a small task/request artifact such as `TASK.md`, pasted requirements, ticket excerpt, or prototype notes and asks for a compact PRD/spec or acceptance criteria in the conversation.

- Read only the named task artifact and this active `to-prd` contract.
- Do not inspect Groundwork plugin README, `.codex-plugin/plugin.json`, plugin manifests, package internals, unrelated skill files, or shared lifecycle/evidence references.
- Do not load `skills/_shared/LIFECYCLE-PREFLIGHT.md`, `skills/_shared/EVIDENCE-BOUNDARY.md`, `skills/_shared/GRILLING.md`, `skills/to-prd/GRILL-BEFORE-WRITE.md`, or `skills/to-prd/PRD-TEMPLATE.md` by default.
- Package self-inspection is allowed only when the user explicitly asks to inspect, evaluate, debug, install, package, or prove current Groundwork source/package behavior.
- Use the compact conversation PRD/spec shape below.
- Mark missing product facts as **NEEDS CLARIFICATION** instead of searching package internals or inventing product truth.

Do not use the generic fast path for Groundwork-internal maintenance requests involving Groundwork plugin install/upgrade flows, marketplace behavior, runtime behavior, workflow changes, version enhancements, or skill-selection behavior. Use the Groundwork maintenance compact path below.

Escalate out of this fast path for durable PRD artifacts, source-backed product truth, wiki-backed context, explicit lifecycle/workflow gates, requested source inspection, or ambiguity that blocks drafting.

## Groundwork Maintenance Compact Path

Use when the task is about Groundwork itself and asks for a compact draft/spec, not source-backed proof or a durable PRD artifact.

- Read only the named task artifact and this active `to-prd` contract unless source/package behavior inspection is explicitly requested.
- Do not inspect Groundwork plugin README, `.codex-plugin/plugin.json`, plugin manifests, installed package internals, or unrelated skill files by default.
- Preserve lifecycle-state framing: Requirement State, Source Truth / Evidence Level, Visible User Value, Acceptance Criteria, Evidence Needed Before Implementation, Open Questions, Downstream Gate.
- Mark unprovided package/runtime/workflow facts as **NEEDS CLARIFICATION**.
- Load `skills/_shared/LIFECYCLE-PREFLIGHT.md`, `skills/_shared/EVIDENCE-BOUNDARY.md`, or `skills/to-prd/PRD-TEMPLATE.md` only for durable artifacts, source-backed product truth, accepted release/version/workflow/runtime truth, or explicit lifecycle gate evaluation.

## Required Evidence

Use user-provided context first. Inspect source, docs, prototypes, tickets, or data only when they can answer a material question or the user asks for source-backed truth. For Groundwork repo maintenance, apply repo-local `AGENTS.md` before reporting complete.

Full path only:

- Use `skills/_shared/LIFECYCLE-PREFLIGHT.md` for durable PRD files, source-backed product truth, accepted version/workflow/runtime/plugin changes, skill-selection changes, or product decisions needing lifecycle evidence.
- Use Codex Plan Mode when exposed for raw PRD/spec/grill intake. Plan Mode may shape boundary but must not write durable PRD files; if unavailable, run the same decision without `tool_enforced` claims.
- Use `skills/_shared/GRILLING.md` only when material ambiguity blocks PRD shaping and unknowns are not enumerable.
- Use `skills/_shared/DOMAIN-LANGUAGE.md` only when terminology affects acceptance, contract/source/runtime truth, verification, or handoff.
- Apply `EB-WIKI-001` / `EB-VERIFY-001` and `skills/_shared/LLM-WIKI.md` only when wiki-backed context is requested or supplied.

## Workflow

1. Choose fast path, Groundwork maintenance compact path, or full path.
2. State target reader, decision supported, known facts, assumptions, open questions, and source/evidence level.
3. Ask one highest-impact clarification question only if drafting is blocked.
4. Mark every unknown backend field, business state, unsupported ability, or missing acceptance detail as **NEEDS CLARIFICATION**.
5. Keep output compact, with stable `AC-1`, `AC-2` IDs when acceptance criteria are present.
6. Recommend `to-issues` only when the PRD/spec is accepted enough to slice.
7. Add `Wiki Update Candidate` only when durable reusable knowledge was produced; do not apply wiki updates unless explicitly requested.

## Hard Stops

- Stop before drafting if target reader, decision, known facts, assumptions, open questions, or needs confirmation are missing, unless explicitly justified as `None`.
- Stop before writing a durable PRD file unless the user requested it and artifact promotion is justified.
- Stop before durable PRD writes in Plan Mode, read-only, or chat-only; output the promotion gate instead.
- Stop before writing durable artifacts without the exact audience-first header fields from `skills/_shared/AUDIENCE-FIRST-ARTIFACT.md`.
- Stop before recommending `to-issues` while blocking **NEEDS CLARIFICATION** remains.
- Do not invent backend fields, states, APIs, metrics, owners, timelines, or acceptance details.
- Do not promote prototype-only, wiki-only, glossary-only, stale, uncited, or external-search claims beyond their evidence layer.
- Do not create new public grill/socratic/domain-language skills for this behavior.

## Output Shape

Default to a compact conversation PRD/spec:

```text
Problem / Intent
Target Reader
Decision Supported
Known Facts
Assumptions
Acceptance Criteria
Open Questions
Not In Scope
Next Step
```

Groundwork maintenance compact spec adds Requirement State, Source Truth / Evidence Level, Evidence Needed Before Implementation, and Downstream Gate.

Durable PRD artifact: load `PRD-TEMPLATE.md`, apply audience-first artifact fields, and include the full source/evidence/lifecycle boundary only when artifact promotion is justified.

Plan Mode durable artifact gate:

```text
Plan Mode Durable Artifact Promotion Gate
Proposed Action:
Target:
Risk:
Rollback/Undo:
Approval Needed:
Write-capable Route:
Promotion Condition:
Canonical Target Path:
Post-Plan Owner:
```

Full durable PRD field set is owned by `GRILL-BEFORE-WRITE.md` and `PRD-TEMPLATE.md`; load them only when needed.

## Stop Condition

Stop when PRD/spec intent, acceptance criteria, open questions, evidence boundary, and next action are clear enough for user review or task slicing.

## Artifact Rule

Default to conversation output. Write or update a PRD file only when requested, needed as source of truth, or artifact promotion is justified. Follow `skills/_shared/AUDIENCE-FIRST-ARTIFACT.md` and `skills/_shared/ARTIFACT-DIRECTORY-POLICY.md`. Redact secrets, credentials, PII, sensitive logs, screenshots, private payloads, and database rows.
