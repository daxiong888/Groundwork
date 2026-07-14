# Verify Scope And Evidence Template

Purpose: proportional scope/evidence opening for `verify`; source-validation template only, not proof that checks ran.

## Compact Required Opening

Default final `verify` report:

```text
Verification Scope
- Claim:
- Covered:
- Missing:

Verdict: pass | partial | fail | blocked
```

Rules:

- The first line of the final report body is exactly `Verification Scope`.
- `Claim`, `Covered`, and `Missing` are the minimum semantic fields. Keep each concise.
- `Missing: none` is allowed only after inspection supports it; do not emit unchecked empty/`N/A` placeholders.
- Add `Out of Scope` when an excluded area could be mistaken for covered evidence.
- Add `Evidence Sources` when source identity or evidence layer is not clear from `Covered`.
- Use the extended six-field legacy-compatible opening only for high-risk, multi-claim, durable, machine-consumed, or explicitly requested reports:

```text
Verification Scope
- In Scope:
- Out of Scope:
- Covered:
- Not Covered:
- Evidence Sources:
- User-visible Claim Being Verified:
```

The compact and extended forms are semantic equivalents. Do not print both.

## Claim Evidence Matrix

Use a matrix only for three or more independently judged material claims:

```text
| Claim / AC | Evidence | Result | Gap | Severity |
| --- | --- | --- | --- | --- |
| ... | ... | pass / partial / fail / blocked / unverified | ... | P0 / P1 / P2 / P3 / none |
```

## Evidence Source Types

- `source`: code, schema, config, docs, or fixtures inspected directly.
- `diff`: changed files inspected directly; never sufficient alone for readiness.
- `test`: automated test command and result.
- `runtime/browser`: CLI, server, app, browser, or UI behavior observed directly.
- `data/environment`: fixture, database, API, migration, deploy target, flags, or dependency state.
- `UAT/customer`: actual bounded user/customer validation.
- `git-boundary`: staged/unstaged and intended delivery scope.

## Verdict Rule

- `pass`: every in-scope material claim is supported.
- `partial`: some claims are supported but material gaps remain.
- `fail`: evidence contradicts a material claim.
- `blocked`: required evidence needs unavailable access, approval, system state, or scope expansion.

After the verdict, report only material findings and the next useful check.
