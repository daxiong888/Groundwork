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

Start from accepted source. Put missing blockers, source context, contract impact, acceptance details, or verification expectations into missing-field buckets; do not fabricate readiness.

Load `skills/_shared/FIRST-PRINCIPLES.md` only when accepted source still needs vertical slices tied to the primitive problem, hard constraints, minimal behavior change, and falsifiable verification signal. Load `skills/_shared/ADVERSARIAL-REVIEW.md` only when slicing could hide cross-layer contract risk, unsupported readiness, unverified source truth, or non-independent verification.

Before splitting, classify both source authority and downstream intent. Load `skills/_shared/LIFECYCLE-PREFLIGHT.md` and apply artifact promotion for durable save, paste-ready tracker use, remote issue creation, cross-session/agent use, implementation, verification, handoff, git/remote mutation, or unknown/ambiguous downstream intent. Paste-ready output is downstream intent unless the user explicitly requests format preview for current-conversation review only and says it will not be used externally.

The only full-preflight no-load branch requires a canonical accepted local artifact or an external accepted source with explicit owner/authority, clear ACs, no mixed or conflicting source truth, current-conversation review only, and explicitly no downstream intent. Still run the local source, acceptance, criteria, artifact, and downstream-intent checks, and state in ordinary visible text that the drafts are current-review-only and not downstream-ready. Load locale guard for user-visible text. Final readiness belongs to `triage`; runtime and package routing belong to `dispatch` after readiness. `accepted enough` means a canonical accepted local artifact, issue-ready artifact, or named external accepted task with owner/authority, clear ACs, and no unresolved mixed source truth; a conversation-only accepted PRD must be promoted or assigned an external canonical source before any issue split.

## Workflow

Confirm source/acceptance, stop if not accepted enough, apply locale, split vertical behavior-visible slices, include acceptance/blockers/risk/AFK-HITL/contract impact/verification/missing fields/triage candidate, keep tracker-neutral markdown, and recommend `triage` or `write-plan`.

## Hard Stops

- Stop before splitting unless source is a canonical local artifact in `prd_accepted` or `issue_ready` state, or a named external accepted source with owner/authority.
- Stop before drafting issue criteria unless source criteria are clear; if AC IDs are missing but criteria exist, preserve text and record missing stable IDs.
- Stop before ready-for-agent candidates unless each slice is vertical, behavior-visible, and independently verifiable.
- Stop before any issue split when accepted source remains conversation-only; require artifact promotion or a named external canonical source.
- Do not invent AC IDs, owners, blockers, contract impact, verification evidence, runtime facts, or readiness.
- Do not mark final readiness or emit executable Goal Contracts.

## Output Shape

Default to tracker-neutral drafts containing title/goal, ACs, blockers or dependencies, and the canonical Markdown field `Verification Expectation`. A verification expectation describes a future verification signal; `verification evidence` means an already run, observed, and citable result, not a second issue-draft field. State the accepted source once for the package. For the narrow no-load branch, also state that the drafts are current-review-only and not downstream-ready. Add AFK/HITL, contract impact, missing fields, triage candidate, ordering, next action, or artifact recommendation only when it changes execution or review. Do not add runtime, model, worktree, isolation, or parallelization candidates; `dispatch` owns those decisions after `triage` establishes readiness.

## Stop Condition

Stop when each draft has a vertical slice, ACs, material blockers/dependencies, and a `Verification Expectation`. Require execution type, contract impact, triage recommendation, or next action only when applicable.

## Artifact Rule

Follow audience/artifact promotion policy. Do not call tracker APIs. Write local issue artifacts only when no better source owns the work and durable state is useful. Redact sensitive data.
