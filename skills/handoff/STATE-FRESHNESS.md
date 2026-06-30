# Handoff State Freshness

Target Reader: Codex preparing handoff when lifecycle recovery state may already exist.
Reader Action Needed: Decide whether `artifacts/<workstream-slug>/STATE.md` is fresh, stale, or unknown without copying the full state file.
Decision Supported: Whether to reference existing state, recommend state update, or keep lifecycle state out of scope.
Artifact Type: branch-specific handoff reference
Source of Truth: `skills/_shared/LIFECYCLE-STATE.md`, `skills/_shared/ARTIFACT-PROMOTION.md`, and `skills/handoff/SKILL.md`.
Scope: Freshness algorithm, state-reference mode, and missing/conflicting evidence handling.
Out of Scope: Writing lifecycle state by default or treating lifecycle state as stronger than source truth.
Evidence Level: Source-validation rule only.
Safe to Share / Redaction Notes: Safe to share as-is; contains no secrets, credentials, PII, private logs, or production payloads.

## State Freshness Algorithm

Use this algorithm before reporting `State Freshness` for an existing `artifacts/<workstream-slug>/STATE.md`:

1. Read the existing state file enough to inspect `Last Updated`, `Canonical Sources`, current risks/gaps, and next action. Do not copy the full state into the handoff.
2. Verify `Last Updated` is comparable:
   - ISO 8601 timestamp with timezone; or
   - exact date plus source-order evidence that can be compared.
3. Verify `Canonical Sources` is present, readable, and points to artifacts, issue, PRD, code, tests, runtime evidence, or user-confirmed decisions that currently own truth.
4. Compare state claims against canonical sources available in the current handoff scope.
5. Report one of:
   - `fresh` only when `Last Updated` is comparable, `Canonical Sources` are readable and resolvable, all checked canonical sources are not newer/conflicting or newer sources are explicitly irrelevant, and the handoff names the checked source set.
   - `stale` when a checked canonical source conflicts with `STATE.md`, a later source supersedes it, or a verified gap/risk changed after `Last Updated`.
   - `unknown` when the file cannot be read, `Last Updated` is missing/unreadable/not comparable, `Canonical Sources` is missing/unreadable/unresolvable, canonical sources conflict, checked source set is not named, or freshness cannot be evidenced.

Default to `State Freshness: unknown` and `State Update Needed: yes` unless freshness is evidenced. Do not infer freshness from path existence, confidence, or absence of known conflicts.

## Actionable Unknowns

When freshness is `stale` or `unknown`, keep the handoff actionable:

- name the missing field, unreadable section, conflicting source, or unavailable check;
- follow canonical source truth over lifecycle state;
- put unverifiable claims in `Open Gaps`, `Risks`, or `Do-Not-Assume`;
- recommend updating `STATE.md` only when the lifecycle-state threshold still applies.
