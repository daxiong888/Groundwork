# Verify Scope And Evidence Template

Target Reader: Codex running the Groundwork `verify` skill.
Reader Action Needed: Start every verification report with explicit scope and evidence coverage.
Decision Supported: Whether a claim is supported, partial, failed, blocked, or still unverified.
Scope: Scope-first verification reports, claim-to-evidence mapping, and missing-evidence handling.
Out of Scope: Running checks, implementing fixes, or creating customer-facing summaries as the primary output.
Evidence Level: Groundwork issue #5 acceptance criteria and `docs/prd.md` verification contract.

## Required Opening

Every `verify` output starts with this block before any summary or verdict:

```text
Verification Scope
- In Scope:
- Out of Scope:
- Covered:
- Not Covered:
- Evidence Sources:
- User-visible Claim Being Verified:
```

Rules:

- Keep scope concrete enough that another reviewer can tell what was and was not checked.
- Put known exclusions in `Out of Scope` or `Not Covered`; do not hide them in risks.
- Treat missing tests, runtime/browser checks, data readiness, environment readiness, UAT evidence, and customer validation as `unverified` unless actually checked.
- A diff summary or implementation summary alone is not readiness evidence.
- Customer-facing wording, when useful, is secondary to engineering evidence.

## Claim Evidence Matrix

Use this matrix for nontrivial verification:

```text
| Claim / AC | Evidence | Result | Gap | Severity |
| --- | --- | --- | --- | --- |
| ... | ... | pass / partial / fail / blocked / unverified | ... | P0 / P1 / P2 / P3 / none |
```

Severity guide:

- `P0`: blocks release, unsafe action, data loss, security/privacy issue, or clearly broken primary workflow.
- `P1`: blocks the stated acceptance criteria or a required handoff/UAT path.
- `P2`: important gap with workaround or limited blast radius.
- `P3`: low-risk polish, evidence hygiene, or follow-up improvement.
- `none`: claim is supported and no material gap remains.

## Evidence Source Types

Use the most specific source label available:

- `source`: code, schema, config, docs, or fixtures inspected directly.
- `diff`: changed files inspected directly; never sufficient alone for readiness.
- `test`: automated test command and result.
- `runtime/browser`: browser, UI, CLI, server, or app behavior observed directly.
- `data`: fixture, database, API payload, or migration evidence, redacted when needed.
- `environment`: deploy target, feature flag, credentials availability, dependency state, or tenant readiness.
- `UAT/customer`: actual user/customer validation or a clearly bounded UAT artifact.
- `git-boundary`: staged/unstaged file boundary and intended commit scope.

## Verdict Rule

Give one verdict after the scope and evidence matrix:

- `pass`: every in-scope material claim is supported by adequate evidence.
- `partial`: some claims are supported, but material gaps remain.
- `fail`: evidence contradicts a material claim.
- `blocked`: required evidence cannot be obtained without a decision, approval, unavailable system, or scope expansion.

