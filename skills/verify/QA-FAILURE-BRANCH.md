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
- Keep `Verdict: fail` or `Verdict: blocked` exactly once in `Verification Scope`; never put `Verdict` inside `QA Failure`.
- Keep every `QA Failure` field from `QA-FIX-QA.md`.
- Use `not provided` for absent prompt details and `unverified` for unchecked facts.
- Do not replace missing failure details with a generic QA process.
- Do not update a failed or blocked verification to `pass` until the original reproduction/check has been re-QA'd or the missing re-QA evidence is explicitly reported as unresolved.
- Apply `qa_gap_closure` from `QA-FIX-QA.md` before routing a fix to `implement`; keep `verify` responsible for evidence sufficiency and re-QA.
- For `ready_for_implement` or `diagnose_before_edit`, `Reproduction` and `Re-QA Required` must be the same non-placeholder `command:` or `manual:` original-check identity, `Implementation Authority` must be `existing_and_sufficient`, and `Risk Change` must be `unchanged_within_boundary`.
- Missing or mismatched original-check identity stays with `verify`; changed product/contract truth routes to `to-prd` or the source owner; `approval_required` or `new_or_increased` routes to `human_decision` or `blocked`; missing authority routes to `blocked`.
- Keep `Scoped Next Action` to the exact finite `route:` token defined by the selected admission in `QA-FIX-QA.md`; never append execution prose.
- Do not recommend another identical attempt when no new evidence or changed hypothesis exists.
