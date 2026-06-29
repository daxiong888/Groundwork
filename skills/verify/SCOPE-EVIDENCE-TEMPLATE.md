# Verify Scope And Evidence Template

Target Reader: Codex running the Groundwork `verify` skill.
Reader Action Needed: Start every verification report with explicit scope and evidence coverage.
Decision Supported: Whether a claim is supported, partial, failed, blocked, or still unverified.
Artifact Type: shared verification template
Source of Truth: Groundwork issue #5 acceptance criteria and `docs/prd.md` verification contract.
Scope: Scope-first verification reports, claim-to-evidence mapping, and missing-evidence handling.
Out of Scope: Running checks, implementing fixes, or creating customer-facing summaries as the primary output.
Evidence Level: Groundwork issue #5 acceptance criteria and `docs/prd.md` verification contract.
Safe to Share / Redaction Notes: Safe to share as-is; contains no secrets, credentials, PII, private logs, or production payloads.

## Required Report Opening

Every final `verify` report starts with this complete block before any summary, verdict, findings list, contract review, UI evidence, git-boundary note, QA failure block, approval gate, or subagent prompt:

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

- The first line of the final verification report must be exactly `Verification Scope`.
- Accepted criterion: the final non-empty verification report body starts with the complete `Verification Scope` block.
- Not required: the absolute first user-visible assistant line starts with `Verification Scope`; brief progress or tool-use prefaces are allowed under the preface rule below.
- The full six-field block is mandatory. A bare `Verification Scope` heading is not compliant.
- Keep every field even when information is missing; write `not provided` for absent prompt context and `unverified` for facts not checked.
- A brief progress or tool-use preface may appear before the final report only if it contains no verdict, findings, specialized payload, contract conclusion, QA decision, UI tool recommendation, approval decision, or subagent prompt body.
- Do not write report-body prefaces such as `Conclusion`, `Findings`, `Frontend Contract Review`, `Reviewed against`, or `UI Evidence` before the scope block.
- Specialized formats such as `Frontend Contract Review`, `UI Evidence`, `Git Boundary`, `Subagent Review Package`, or `QA Failure` appear after the scope block, never instead of it.
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

Severity uses the shared enum in `skills/_shared/SEVERITY.md`. In `verify`, severity describes the evidence, claim, and acceptance-criterion gap for the user-visible claim being verified.

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
