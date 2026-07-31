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

## Acceptance Classification

- **Confirmed AC**: supported by the user or an inspected source. Source-preserving normalization is allowed, but must not change scope, behavior, channel, state transition, or business outcome.
- **Proposed AC — NEEDS CONFIRMATION**: useful for convergence but dependent on a new product decision.
- **Open Question**: names only a missing decision. Mark it **NEEDS CLARIFICATION** when blocking, and do not assign it an AC ID.
Split mixed product statements and group Confirmed and Proposed ACs separately when both exist. An Open Question may reference a Proposed AC to request confirmation; that semantic link is not itself duplication or a contract violation. Keep workflow, readiness, and slicing rules in Next Step or a gate, not in product ACs. Do not recommend or enter `to-issues` while any Proposed AC or blocking Open Question remains.

## Durable Write Gate

Write or update a durable PRD file only when all four conditions are true: (1) the user explicitly requested file persistence; (2) a source-of-truth artifact is useful or artifact promotion is justified; (3) the active route is write-capable; and (4) audience-first header fields are complete.
If any condition is false or unknown, keep the output in conversation and identify the unmet condition. After the gate passes, load `PRD-TEMPLATE.md` and include the source, evidence, and lifecycle boundary appropriate to the promoted artifact.

## Hard Stops

- Stop before drafting only when a missing target reader, decision, fact, or acceptance boundary would materially change the spec. Do not print empty fields merely to prove they were considered.
- Stop before writing or updating a durable PRD file unless the Durable Write Gate passes.
- Stop before recommending or entering `to-issues` while any Proposed AC or blocking **NEEDS CLARIFICATION** remains.
- Stop before promising or producing issue drafts, issue packs, agent-ready slices, or parallel agent work from raw requests to split issues for agents. For raw agent-slicing requests, output only compact PRD/spec shaping, missing fields, and the downstream acceptance gate until source is accepted enough.
- Do not invent backend fields, states, APIs, metrics, owners, timelines, or acceptance details.
- Do not promote prototype-only, wiki-only, glossary-only, stale, uncited, or external-search claims beyond their evidence layer.
- Do not create new public grill/socratic/domain-language skills for this behavior.

## Output Shape

Default compact conversation PRD/spec: Problem / Intent, ACs, material Open Questions, and Next Step. Add Target Reader, Decision Supported, Known Facts, Assumptions, or Not In Scope only when they change review or acceptance.

Durable PRD artifact: apply the Durable Write Gate.

Plan Mode durable artifact gate: Proposed Action, Target, Approval Needed, Write-capable Route, Promotion Condition, Canonical Target Path, Post-Plan Owner.

Full durable PRD fields live in `GRILL-BEFORE-WRITE.md` and `PRD-TEMPLATE.md`.

## Stop / Artifact Rule

Stop when intent, ACs, open questions, evidence boundary, and next action are reviewable, and the next route's material decisions are resolved or explicitly gated. Default to conversation output; durable writes are governed only by the Durable Write Gate. Redact sensitive data.
