# QA Fix QA Loop

Target Reader: Codex running `verify` or `implement` after a verification failure.
Reader Action Needed: Turn a failed check into a scoped fix loop without broadening the task.
Decision Supported: Whether the failure is understood enough to fix and what must be rechecked.
Scope: Verification failure reporting, minimal diagnosis, scoped fix planning, regression check, and re-QA.
Out of Scope: Broad refactors, speculative fixes, release approval, or unrelated bug sweeps.
Evidence Level: Groundwork issue #8 acceptance criteria and existing verify/implement contracts.

## Verify Failure Report

When verification fails, report:

```text
QA Failure
- Expected:
- Actual:
- Reproduction:
- Severity: P0 / P1 / P2 / P3
- Minimal Diagnosis:
- Fix Plan:
- Re-QA Required:
```

Rules:

- Keep diagnosis minimal and evidence-backed.
- If cause is uncertain, say what is confirmed and what is still hypothesis.
- Do not skip `Expected`, `Actual`, or `Reproduction` for behavior failures.
- Do not hide severity in prose.
- Re-QA must name the original failing check or manual reproduction that has to be rerun.

## Implement Fix Loop

When `implement` receives a verify failure:

1. Confirm the failure report has expected, actual, reproduction, severity, minimal diagnosis, fix plan, and re-QA requirement.
2. Fix only the scoped failure.
3. Rerun the original failing check after the fix.
4. Add or update a focused regression test/check when feasible.
5. Report any unresolved gap back to `verify`.

Do not turn one failed check into broad cleanup or unrelated behavior changes.
