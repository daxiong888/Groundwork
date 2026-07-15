---
name: to-prd
description: Shape raw or ambiguous product/engineering intent into compact PRD/spec before slicing, agent delegation, or implementation. Includes raw ideas asking to split issues for agents. Not for rewrites, accepted tasks, implementation, verification, handoff, dispatch, or wiki.
---

# to-prd

## Trigger Contract

Use when rough intent, prototype notes, feedback, or unclear requirements need PRD/spec intent and ACs, including raw requests to split issues for agents before accepted source exists. Route rewrites direct, decisions to decision mapping, accepted specs to `to-issues`, code edits to `implement`, evidence proof to `verify`, wiki work to `wiki`.

Raw plugin install/upgrade, marketplace, runtime, workflow, version, or skill-selection ideas remain `to-prd` until accepted or bypassed.

## Fast Path: Prompt-Provided Compact PRD

Hard default for a named small artifact (`TASK.md`, pasted requirements, ticket excerpt, prototype notes) asking for compact PRD/spec or ACs.

- Read only the named task artifact and this active `to-prd` contract.
- Do not inspect plugin/package READMEs, manifests, package internals, unrelated skill files, or shared lifecycle/evidence references by default.
- Do not load lifecycle, evidence, grilling, first-principles, adversarial-review, or PRD template references by default.
- Leave this fast path only for explicit plugin/package self-inspection or when source/package behavior evidence is required by the requested decision.
- Use the compact conversation PRD/spec shape below.
- Mark missing product facts as **NEEDS CLARIFICATION**; do not search package internals or invent truth.

Leave the fast path when the requested decision itself concerns plugin/package self-inspection, install or upgrade, marketplace, runtime, workflow, version, skill-selection, or source/package behavior. This permits requested source inspection; it does not make package internals a default context source.

Escalate only for durable PRD artifacts, source-backed product truth, wiki context, lifecycle/workflow gates, requested source inspection, or drafting blockers.

## Required Evidence

Use user context first. Inspect source/docs/prototypes/tickets/data only for material questions or requested source-backed truth. Load `skills/_shared/LIFECYCLE-PREFLIGHT.md` for durable/source-backed/accepted workflow truth; Plan Mode for raw PRD/spec/grill intake without write claims; grilling/domain/wiki refs only when material.

Load `skills/_shared/FIRST-PRINCIPLES.md` only when PRD shaping must separate primitive facts, constraints, root cause/core need, minimal valuable scope, and falsifiable success signal. Load `skills/_shared/ADVERSARIAL-REVIEW.md` only when the PRD may turn unsupported wording, prototype labels, glossary terms, or old docs into contract truth, implementation readiness, or stronger evidence than the source supports.

## Workflow

Choose the compact or full path. State target reader, decision, facts, assumptions, open questions, and evidence level; ask only if blocked; mark unknown backend/business/acceptance facts as **NEEDS CLARIFICATION**; keep AC IDs stable; recommend `to-issues` only when accepted enough.

When a raw or ambiguous recurring workflow or multi-turn clarification still has one material decision blocking the next route, use the Spec Convergence Loop from `skills/_shared/GRILLING.md`: resolve one material decision per turn, canonically write back the decision, and continue only when a new blocker remains. A clear recurring spec and an explicitly requested non-interactive gap list stay on their normal paths. Use the workflow loop lens conditionally; do not manufacture triggers, schedules, checkpoints, AI steps, or artifacts the requirement does not need.

## Hard Stops

- Stop before drafting only when a missing target reader, decision, fact, or acceptance boundary would materially change the spec. Do not print empty fields merely to prove they were considered.
- Stop before writing a durable PRD file unless requested, artifact promotion is justified, the route is write-capable, and audience-first header fields are present.
- Stop before recommending `to-issues` while blocking **NEEDS CLARIFICATION** remains.
- Stop before promising or producing issue drafts, issue packs, agent-ready slices, or parallel agent work from raw requests to split issues for agents. For raw agent-slicing requests, output only compact PRD/spec shaping, missing fields, and the downstream acceptance gate until source is accepted enough.
- Do not invent backend fields, states, APIs, metrics, owners, timelines, or acceptance details.
- Do not promote prototype-only, wiki-only, glossary-only, stale, uncited, or external-search claims beyond their evidence layer.
- Do not create new public grill/socratic/domain-language skills for this behavior.

## Output Shape

Default compact conversation PRD/spec: Problem / Intent, ACs, material Open Questions, and Next Step. Add Target Reader, Decision Supported, Known Facts, Assumptions, or Not In Scope only when they change review or acceptance.

Durable PRD artifact: load `PRD-TEMPLATE.md`, apply audience-first artifact fields, and include the full source/evidence/lifecycle boundary only when artifact promotion is justified.

Plan Mode durable artifact gate: Proposed Action, Target, Approval Needed, Write-capable Route, Promotion Condition, Canonical Target Path, Post-Plan Owner.

Full durable PRD fields live in `GRILL-BEFORE-WRITE.md` and `PRD-TEMPLATE.md`.

## Stop / Artifact Rule

Stop when intent, ACs, open questions, evidence boundary, and next action are reviewable, and the next route's material decisions are resolved or explicitly gated. Default to conversation output. Write/update PRD files only when requested, source-of-truth useful, or artifact promotion is justified. Redact sensitive data.
