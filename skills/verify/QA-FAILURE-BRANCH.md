# QA Failure Branch

Target Reader: Codex running `verify` for failed verification notes or QA -> fix -> QA handling.
Reader Action Needed: Preserve the structured QA failure payload after the required scope block.
Decision Supported: Whether a failed check has enough expected, actual, reproduction, severity, diagnosis, fix, and re-QA evidence to route to implementation or remain blocked.
Artifact Type: branch-specific verification reference
Source of Truth: `skills/verify/QA-FIX-QA.md` and `skills/verify/SCOPE-EVIDENCE-TEMPLATE.md`.
Scope: QA failure report shape, missing failure detail handling, severity boundary, and re-QA requirement.
Out of Scope: Implementing the fix, broad refactors, release approval, unrelated regression sweeps, or replacing the general verification report.
Evidence Level: Source-validation workflow only.
Safe to Share / Redaction Notes: Safe to share as-is; contains no secrets, credentials, PII, private logs, or production payloads.

## Required References

- Load `SCOPE-EVIDENCE-TEMPLATE.md` first.
- Apply `EB-VERIFY-001` from `skills/_shared/EVIDENCE-BOUNDARY.md` when re-QA, reproduction, or current check evidence is missing.
- Load `QA-FIX-QA.md` before emitting a `QA Failure` block.
- Use `skills/_shared/SEVERITY.md`; `none` is invalid in a `QA Failure` block.

## Branch Rules

- The `QA Failure` block appears after the `Verification Scope` block.
- Keep every `QA Failure` field from `QA-FIX-QA.md`.
- Use `not provided` for absent prompt details and `unverified` for unchecked facts.
- Do not replace missing failure details with a generic QA process.
- Do not update a failed or blocked verification to `pass` until the original reproduction/check has been re-QA'd or the missing re-QA evidence is explicitly reported as unresolved.
- Route fixes to `implement`; keep `verify` responsible for evidence sufficiency and re-QA.
