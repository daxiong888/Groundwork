# Subagent Review Branch

Target Reader: Codex running `verify` to prepare a fresh-context subagent review prompt.
Reader Action Needed: Emit the verification scope first, then a bounded fresh-context subagent package.
Decision Supported: Whether a delegated review package is bounded, read-only, evidence-backed, and safe to run.
Artifact Type: branch-specific verification reference
Source of Truth: `skills/_shared/SUBAGENT-DELEGATION.md`, `skills/_shared/ROLE-SEPARATION.md`, and `skills/verify/SCOPE-EVIDENCE-TEMPLATE.md`.
Scope: Fresh-context subagent review packages, read-only clean review boundaries, parent-history isolation, and runtime mismatch handling.
Out of Scope: Spawning subagents by default, nested delegation, file mutation by reviewers, runtime selector enforcement claims, or final readiness approval.
Evidence Level: Source-validation policy only unless an actual runtime/subagent tool reports execution evidence.
Safe to Share / Redaction Notes: Safe to share as-is; contains no secrets, credentials, PII, private logs, or production payloads.

## Required References

- Load `SCOPE-EVIDENCE-TEMPLATE.md` before preparing the review package.
- Load `skills/_shared/SUBAGENT-DELEGATION.md` for the `Subagent Review Package` shape.
- Load `skills/_shared/RUNTIME-CAPABILITY.md` when requested and available runtime may differ.

## Branch Rules

- The final verify report starts with `Verification Scope`; the subagent prompt package comes after it.
- The reviewer receives fresh context only and must not rely on parent session memory or hidden context.
- Clean review delegation must disable full-history forks when the runtime exposes that control.
- File edits are not allowed unless explicitly delegated; clean review is read-only by default.
- The subagent must not spawn more agents or child threads unless the user explicitly delegates that.
- Findings must cite supplied package sections, paths, commands, or observations.
- Missing evidence must be reported as `unverified` or `blocked`, not invented.
