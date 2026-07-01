---
name: to-issues
description: Slice an accepted PRD/spec/plan into vertical task drafts with acceptance, blockers, task-state fields, and verification expectations. Not for raw ideas, ambiguous requirements, implementation, readiness verification, or one-off planning.
---

# to-issues

## Trigger Contract

Use when accepted PRD/spec/plan intent needs vertical work units or paste-ready issue drafts.

Route away:

- Raw/draft/conversation-only intent without acceptance -> `to-prd`.
- Existing task readiness -> `triage`.
- Implementation steps for one accepted task -> `write-plan`.
- Code edits -> `implement`.
- Release/UAT/evidence proof -> `verify`.
- Runtime/subagent/worktree assignment -> `dispatch`.

## Required Evidence

Start from the accepted source. If blockers, source context, contract impact, runtime-routing inputs, Goal Contract inputs, or verification expectations are missing, record them in missing-field buckets; do not fabricate readiness.

For Groundwork repo maintenance, apply repo-local `AGENTS.md` before reporting complete.

Load only when needed:

- `skills/_shared/LIFECYCLE-PREFLIGHT.md` and `ARTIFACT-PROMOTION.md` before splitting source that will drive another session, remote issue creation, implementation, verification, or handoff.
- `skills/_shared/LOCALE-GUARD.md` for user-visible titles, headings, and issue bodies.
- Runtime candidate fields are advisory only; final readiness belongs to `triage`, final execution routing to `dispatch`.

`accepted enough` means canonical artifact, accepted PRD/spec/plan, issue-ready artifact, or named external task source with acceptance state/owner; clear acceptance criteria; no unresolved mixed source truth; conversation-only accepted material promoted or tied to an external source before downstream use.

## Runtime Routing Candidate Rules

Emit the advisory block only when the accepted source supports it. It is not a Goal Contract, dispatch package, readiness verdict, or execution proof.

- `read_only_review`: do not suggest `codex_app_managed_worktree_thread`; prefer read-only/subagent/clean-review options.
- `planning_only`: do not suggest write worktree.
- `hybrid`: split first or mark `triage_required`; only concrete write subtasks can become managed-worktree candidates.
- `write_implementation`: managed-worktree candidate only when source context, write boundary, acceptance, and verification are clear enough for later Goal Contract generation.
- `diagnosis`: may suggest read-only subagent when independent.

## Workflow

1. Confirm source truth and acceptance state.
2. Stop at source-of-truth or artifact-promotion gate if not accepted enough.
3. Apply locale guard.
4. Split vertical behavior-visible slices, not layer buckets.
5. For each slice include acceptance, blockers, risk, AFK/HITL recommendation, contract impact, verification evidence needed, runtime candidate fields, Goal Contract/runtime/ready-for-agent missing fields, and triage recommendation candidate.
6. Keep tracker-neutral markdown; do not call tracker APIs.
7. Recommend `triage` for final readiness or `write-plan` for an accepted slice.

## Hard Stops

- Stop before splitting unless source is `prd_accepted`, `issue_ready`, or named external accepted source with owner/authority.
- Stop before drafting issue criteria unless source criteria are clear; if AC IDs are missing but criteria exist, preserve text and record missing stable IDs.
- Stop before ready-for-agent candidates unless each slice is vertical, behavior-visible, and independently verifiable.
- Stop before downstream issue creation, implementation handoff, or multi-session use when accepted source remains conversation-only.
- Do not invent AC IDs, owners, blockers, contract impact, verification evidence, runtime facts, or readiness.
- Do not mark final readiness or emit executable Goal Contracts.

## Output Shape

```text
Issue Set Summary
Source
Issue Drafts
- Title
- Goal
- Acceptance Criteria
- Evidence / Source
- Blockers
- Execution: AFK / HITL
- Contract Impact: API / DB / UI state / docs / verification contract / none
- Verification Evidence Needed
- Runtime Routing Candidate
- Ready-for-Agent Missing Fields
- Triage Recommendation Candidate: ready-for-agent candidate / needs-info recommendation / ready-for-human recommendation
Ordering Notes
Next Action
Artifact Recommendation
```

Runtime candidate block, when used:

```text
Runtime Routing Candidate
- recommendation_only: true
- source_support:
- implementation_task_type_candidate:
- runtime_candidate:
- product_runtime_surface_candidate:
- isolation_candidate:
- parallelization_candidate:
- goal_contract_status: not_generated_by_to_issues / missing_fields / ready_for_triage_contract_generation
- goal_contract_missing_fields:
- runtime_missing_fields:
- not_readiness_evidence: true
- missing_fields:
```

## Stop Condition

Stop when each issue draft has a vertical slice, acceptance criteria, blockers, execution type, contract impact, verification evidence needed, runtime candidate fields, missing fields, triage recommendation, and next action.

## Artifact Rule

Follow `skills/_shared/AUDIENCE-FIRST-ARTIFACT.md`, `skills/_shared/ARTIFACT-DIRECTORY-POLICY.md`, and `skills/_shared/ARTIFACT-PROMOTION.md`. Do not call tracker APIs. Write local issue artifacts only when no better source owns the work and durable state is useful. Redact secrets, credentials, PII, sensitive logs, screenshots, private payloads, and database rows.
