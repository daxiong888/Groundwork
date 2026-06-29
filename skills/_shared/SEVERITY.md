Target Reader: Groundwork triage authors, verifiers, QA-fix handlers, implementers, clean reviewers, and maintainers.
Reader Action Needed: Apply one shared severity vocabulary while preserving skill-specific context.
Decision Supported: Whether a current blocker, evidence gap, QA failure, or verification gap is P0, P1, P2, P3, or none.
Artifact Type: shared guardrail
Source of Truth: `skills/triage/SKILL.md`, `skills/verify/SCOPE-EVIDENCE-TEMPLATE.md`, and `skills/verify/QA-FIX-QA.md`.
Scope: Shared severity enum, definitions, contextual usage notes, and `none` validity by output shape.
Out of Scope: Product priority scoring, roadmap priority, business value ranking, release approval, UAT approval, or replacing skill-specific verdicts.
Evidence Level: Source-validation policy only. Severity labels do not prove runtime, browser, UAT, release, marketplace, installed-plugin, cache-refresh, or customer readiness.
Safe to Share / Redaction Notes: Safe to share as-is; contains no secrets, credentials, PII, private logs, or production payloads.

# Severity

## Shared Enum

Use these labels exactly:

- `P0`: release-blocking, unsafe or destructive action, data loss, security/privacy issue, or clearly broken primary workflow.
- `P1`: major acceptance, data, UAT/release/handoff, or cross-layer gap that blocks the stated workflow.
- `P2`: important gap with workaround or limited blast radius.
- `P3`: low-risk polish, evidence hygiene, wording, or follow-up improvement.
- `none`: no material blocker or gap remains.

## Context Notes

- `triage`: severity describes the current blocker or gap impact, not product priority.
- `verify`: severity describes the evidence, claim, and acceptance-criterion gap for the user-visible claim being verified.
- `implement`: severity on findings describes implementation-conformance risk only, not UAT or release readiness unless that evidence is in scope.
- `clean review`: severity describes review findings within supplied package evidence.
- `QA Failure`: `none` is invalid because the block is emitted only for failed or blocked verification. If no material failure remains, omit the `QA Failure` block and use a normal verification verdict instead.

## Hard Negatives

Fail or mark invalid when:

- severity is treated as product priority;
- `none` is used inside a `QA Failure` block;
- a P0/P1/security/privacy/data-loss/destructive gap is downgraded to P2/P3 because it has a workaround;
- a verification or triage report invents release/UAT/customer readiness from a severity of `none` without corresponding evidence.
