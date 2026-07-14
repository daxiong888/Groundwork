# Verify Scope Branch

Purpose: claim-first `verify` behavior for evidence sufficiency; source-validation guidance only, not readiness evidence.

## Required Opening

Load `SCOPE-EVIDENCE-TEMPLATE.md` and use its compact `Verification Scope` block. Use the extended form only for high-risk, multi-claim, durable, machine-consumed, or explicitly requested reports.

Apply `EB-VERIFY-001` from `skills/_shared/EVIDENCE-BOUNDARY.md` before using code diff, implementation summary, source-validation checks, or old evidence for readiness.

## Code-Diff-Only / No-Command Branch

Questions asking whether limited evidence can support a stronger label run as `verify-lite` unless the user explicitly asks for TASK/PRD conformance, runtime/cache/release readiness, or another strict branch.

Read only the claim, user-provided evidence/paths, and current conversation evidence. Do not search historical baselines, artifacts, research, examples, old handoffs, or broad PRDs unless explicitly requested or directly cited by current source.

Use this safe shape:

```text
Verification Scope
- Claim: code diff without runtime or browser evidence can count as ready
- Covered: evidence-sufficiency judgment from the supplied diff boundary
- Missing: runtime, browser, data, environment, release, and UAT evidence

Verdict: blocked
Code diff alone cannot support the stronger readiness claim.
Next check: run the narrowest relevant runtime/API/browser check, then re-verify.
```

Code diff, implementation summary, historical evidence, or source-validation checks alone do not prove runtime, browser, data, environment, release, UAT, or customer readiness.

Keep labeled verdict lines mechanically safe: use `pass`, `partial`, `fail`, or `blocked` alone. Put readiness wording in clearly bounded prose after the verdict.
