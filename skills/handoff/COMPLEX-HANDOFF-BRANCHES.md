# Complex Handoff Branches

Target Reader: Codex preparing handoff for managed worktree, role separation, visual packet, runtime/cache/release/wiki, or clean-review-sensitive continuation.
Reader Action Needed: Preserve continuation state and ownership boundaries without upgrading evidence.
Decision Supported: Which claims remain open gaps, which next role owns them, and which references must be cited for continuation.
Artifact Type: branch-specific handoff reference
Source of Truth: `skills/handoff/SKILL.md`, `skills/_shared/EVIDENCE-BOUNDARY.md`, `skills/_shared/ROLE-SEPARATION.md`, and `skills/dispatch/COMPLEX-WORK-SEPARATION.md`.
Scope: Complex handoff evidence boundaries, visual packet rules, wiki boundaries, release/runtime/cache continuation, and clean-review gaps.
Out of Scope: Runtime execution, clean review, verification, coordinator closeout, archive, branch cleanup, commit, push, PR, tracker mutation, or native Handoff Git operations.
Evidence Level: Source-validation rule only.
Safe to Share / Redaction Notes: Safe to share after redacting secrets, credentials, PII, sensitive logs, screenshots, requests, and database rows.

## Complex Work Separation

For managed worktree or material role-separated work, handoff preserves state and ownership boundaries only. It may name the next owning role and cite evidence needed for that role, but must not become runtime executor, clean reviewer, verifier, coordinator closeout, merge-back owner, archive owner, branch cleanup owner, commit path, push path, PR path, tracker mutation path, or native Handoff Git-operation owner.

Use:

- `skills/dispatch/COMPLEX-WORK-SEPARATION.md` for managed worktree separation and closeout boundaries.
- `skills/_shared/ROLE-SEPARATION.md` for designer/planner, implementer, clean reviewer, verifier, and coordinator role boundaries.
- `skills/_shared/REVIEW-LOOP.md` when previous clean review is missing, stale, or findings remain.

## Evidence Boundaries

- Runtime/cache/release/UAT/marketplace/cache-refresh claims require `skills/_shared/RELEASE-EVIDENCE-CLAIM.md`. If the handoff only references source-validation or continuation evidence, set stronger claims to `unverified` or `not_applicable`.
- Runtime/model selector claims require `skills/_shared/RUNTIME-CAPABILITY.md`; do not claim selector enforcement from prompt preference or package text.
- Visual packets require `skills/_shared/VISUAL-HANDOFF-PACKET.md`. Put unsupported API/schema/source, browser, runtime, UAT, release, and customer-readiness claims under `Do-Not-Assume` unless separate qualifying evidence is named.
- Wiki pages are orientation or claim inventory only. Apply `skills/_shared/LLM-WIKI.md`; do not turn every handoff into a wiki diary or update wiki pages without explicit wiki-maintenance scope.

## Material Clean Review Gap

When a P1, public API, migration, schema, security, privacy, auth, permissions, data correctness, shared contract, package schema, adapter contract, state machine, weak-validation, or multi-package change is handed off without fresh clean review evidence, record that as an open gap or do-not-assume item.

Never describe self-check evidence as clean review. A prior clean review becomes stale when material files changed after it.

## Compactness Rule

Small, low-risk continuation notes should remain compact. Do not force a full separation package when no separation threshold applies and a concise handoff can safely identify source truth, current state, gaps, and next action.
