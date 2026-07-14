---
name: to-issues
description: Slice accepted PRD/spec/plan into vertical task drafts with acceptance, blockers, state, and verification expectations. Not for raw/ambiguous requirements, raw ideas asking to split issues for agents, incomplete-info blocked/handoff judgment, implementation, readiness, or one-off planning.
---

# to-issues

## Trigger Contract

Use when accepted PRD/spec/plan intent needs vertical work units or paste-ready issue drafts.

Route away:

- Raw/draft/conversation-only intent without acceptance, including "split issues for agents" requests -> `to-prd`.
- Incomplete-info blocker, readiness, or whether-to-handoff/blocked judgment -> `triage` or `handoff`.
- Existing issue/task readiness, AFK/HITL, or "which issues can go to agents" judgment -> `triage`.
- Implementation steps for one accepted task -> `write-plan`.
- Code edits -> `implement`.
- Release/UAT/evidence proof -> `verify`.
- Runtime/subagent/worktree assignment -> `dispatch`.

## Required Evidence

Start from accepted source. Put missing blockers, source context, contract impact, runtime inputs, Goal Contract inputs, or verification expectations into missing-field buckets; do not fabricate readiness.

For Groundwork repo maintenance, apply repo-local `AGENTS.md` before reporting complete.

Load `skills/_shared/FIRST-PRINCIPLES.md` only when accepted source still needs vertical slices tied to the primitive problem, hard constraints, minimal behavior change, and falsifiable verification signal. Load `skills/_shared/ADVERSARIAL-REVIEW.md` only when slicing could hide cross-layer contract risk, unsupported readiness, unverified source truth, or non-independent verification.

Load lifecycle/artifact promotion only before splitting source that will drive another session, remote issue creation, implementation, verification, or handoff. Load locale guard for user-visible text. Runtime candidate fields are advisory; final readiness belongs to `triage`, execution routing to `dispatch`.

`accepted enough` means canonical artifact, accepted PRD/spec/plan, issue-ready artifact, or named external task with owner/authority, clear ACs, and no unresolved mixed source truth.

## Runtime Routing Candidate Rules

Emit the advisory block only when source supports it. It is not a Goal Contract, dispatch package, readiness verdict, or execution proof.

Rules: read-only/planning tasks must not suggest write worktrees; hybrid tasks split first or mark `triage_required`; write tasks can name managed-worktree candidacy only when source context, write boundary, acceptance, and verification can support later Goal Contract generation; diagnosis may suggest read-only subagent when independence helps.

## Workflow

Confirm source/acceptance, stop if not accepted enough, apply locale, split vertical behavior-visible slices, include acceptance/blockers/risk/AFK-HITL/contract impact/verification/runtime candidate/missing fields/triage candidate, keep tracker-neutral markdown, and recommend `triage` or `write-plan`.

## Hard Stops

- Stop before splitting unless source is `prd_accepted`, `issue_ready`, or named external accepted source with owner/authority.
- Stop before drafting issue criteria unless source criteria are clear; if AC IDs are missing but criteria exist, preserve text and record missing stable IDs.
- Stop before ready-for-agent candidates unless each slice is vertical, behavior-visible, and independently verifiable.
- Stop before downstream issue creation, implementation handoff, or multi-session use when accepted source remains conversation-only.
- Do not invent AC IDs, owners, blockers, contract impact, verification evidence, runtime facts, or readiness.
- Do not mark final readiness or emit executable Goal Contracts.

## Output Shape

Default to tracker-neutral drafts containing title/goal, ACs, blockers or dependencies, and verification expectation. State the accepted source once for the package. Add AFK/HITL, contract impact, runtime candidate, missing fields, triage candidate, ordering, next action, or artifact recommendation only when it changes execution or review.

Runtime candidate block, when used, must include `recommendation_only: true`, source support, task/runtime/isolation/parallelization candidates, Goal Contract status/missing fields, runtime missing fields, `not_readiness_evidence: true`.

## Stop Condition

Stop when each draft has a vertical slice, ACs, material blockers/dependencies, and verification evidence needed. Require execution type, contract impact, runtime candidate, triage recommendation, or next action only when applicable.

## Artifact Rule

Follow audience/artifact promotion policy. Do not call tracker APIs. Write local issue artifacts only when no better source owns the work and durable state is useful. Redact sensitive data.
