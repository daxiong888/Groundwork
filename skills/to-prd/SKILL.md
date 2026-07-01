---
name: to-prd
description: Shape raw or ambiguous product/engineering intent into a compact PRD/spec before slicing or implementation. Not for tiny rewrites, accepted tasks, implementation, verification, handoff, dispatch, or wiki maintenance.
---

# to-prd

## Trigger Contract

Use when rough intent, prototype notes, feedback, or unclear requirements need PRD/spec intent and acceptance criteria. Route direct rewrites to direct answer, option comparison to decision mapping, accepted PRD/spec to `to-issues`, code edits to `implement`, evidence proof to `verify`, and wiki maintenance to `wiki`.

Raw plugin install/upgrade, marketplace, runtime, workflow, version, or skill-selection ideas remain `to-prd` until accepted or bypassed.

## Fast Path: Prompt-Provided Compact PRD

Hard default for a named small task/request artifact (`TASK.md`, pasted requirements, ticket excerpt, prototype notes) asking for compact PRD/spec or ACs.

- Read only the named task artifact and this active `to-prd` contract.
- Do not inspect Groundwork plugin README, `.codex-plugin/plugin.json`, plugin manifests, package internals, unrelated skill files, or shared lifecycle/evidence references.
- Do not load lifecycle, evidence, grilling, or PRD template references by default.
- Package self-inspection only when asked to inspect, evaluate, debug, install, package, or prove current Groundwork source/package behavior.
- Use the compact conversation PRD/spec shape below.
- Mark missing product facts as **NEEDS CLARIFICATION**; do not search package internals or invent truth.

Do not use the generic fast path for Groundwork-internal maintenance requests involving install/upgrade, marketplace behavior, runtime behavior, workflow changes, version enhancements, or skill-selection behavior. Use the Groundwork maintenance compact path below.

Escalate only for durable PRD artifacts, source-backed product truth, wiki-backed context, explicit lifecycle/workflow gates, requested source inspection, or ambiguity that blocks drafting.

## Groundwork Maintenance Compact Path

Use for Groundwork-internal compact drafts/specs, not source-backed proof or durable PRD writes.

- Read only the named task artifact and this active `to-prd` contract unless source/package behavior inspection is explicitly requested.
- Do not inspect Groundwork plugin README, `.codex-plugin/plugin.json`, plugin manifests, installed package internals, or unrelated skill files by default.
- Preserve lifecycle-state framing: Requirement State, Source Truth / Evidence Level, Visible User Value, Acceptance Criteria, Evidence Needed Before Implementation, Open Questions, Downstream Gate.
- Mark unprovided package/runtime/workflow facts as **NEEDS CLARIFICATION**.
- Load lifecycle/evidence/template refs only for durable artifacts, source-backed product truth, accepted release/version/workflow/runtime truth, or explicit lifecycle gate evaluation.

## Required Evidence

Use user context first. Inspect source/docs/prototypes/tickets/data only for material questions or requested source-backed truth. For Groundwork maintenance, apply repo-local `AGENTS.md`. Full path refs: lifecycle for durable/source-backed/accepted workflow truth; Plan Mode for raw PRD/spec/grill intake without write claims; grilling/domain/wiki refs only when material.

## Workflow

Choose fast path, Groundwork maintenance compact path, or full path; state target reader, decision, facts, assumptions, open questions, and evidence level; ask one clarification only if blocked; mark unknown backend/business/acceptance facts as **NEEDS CLARIFICATION**; keep AC IDs stable; recommend `to-issues` only when accepted enough; add wiki candidates only for durable reusable knowledge.

## Hard Stops

- Stop before drafting if target reader, decision, known facts, assumptions, open questions, or needs confirmation are missing unless justified as `None`.
- Stop before writing a durable PRD file unless requested, artifact promotion is justified, the route is write-capable, and audience-first header fields are present.
- Stop before recommending `to-issues` while blocking **NEEDS CLARIFICATION** remains.
- Do not invent backend fields, states, APIs, metrics, owners, timelines, or acceptance details.
- Do not promote prototype-only, wiki-only, glossary-only, stale, uncited, or external-search claims beyond their evidence layer.
- Do not create new public grill/socratic/domain-language skills for this behavior.

## Output Shape

Default compact conversation PRD/spec: Problem / Intent, Target Reader, Decision Supported, Known Facts, Assumptions, Acceptance Criteria, Open Questions, Not In Scope, Next Step.

Groundwork maintenance compact spec adds Requirement State, Source Truth / Evidence Level, Evidence Needed Before Implementation, and Downstream Gate.

Durable PRD artifact: load `PRD-TEMPLATE.md`, apply audience-first artifact fields, and include the full source/evidence/lifecycle boundary only when artifact promotion is justified.

Plan Mode durable artifact gate: Plan Mode Durable Artifact Promotion Gate, Proposed Action, Target, Approval Needed, Write-capable Route, Promotion Condition, Canonical Target Path, Post-Plan Owner.

Full durable PRD fields live in `GRILL-BEFORE-WRITE.md` and `PRD-TEMPLATE.md`.

## Stop / Artifact Rule

Stop when intent, ACs, open questions, evidence boundary, and next action are reviewable. Default to conversation output. Write/update PRD files only when requested, source-of-truth useful, or artifact promotion is justified. Follow audience/artifact policy and redact sensitive data.
