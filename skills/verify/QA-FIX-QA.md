# QA Fix QA Loop

Target Reader: Codex running `verify` or `implement` after a verification failure.
Reader Action Needed: Turn a failed check into a scoped fix loop without broadening the task.
Decision Supported: Whether the failure is understood enough to fix and what must be rechecked.
Scope: Verification failure reporting, minimal diagnosis, scoped fix planning, regression check, and re-QA.
Out of Scope: Broad refactors, speculative fixes, release approval, or unrelated bug sweeps.
Evidence Level: Groundwork issue #8 acceptance criteria and existing verify/implement contracts.

## Verify Failure Report

When verification fails, or when the user asks for QA -> fix -> QA handling after a failure, report the failure in this exact shape after the `Verification Scope` block:

```text
QA Failure
- Expected:
- Actual:
- Reproduction:
- Severity: P0 / P1 / P2 / P3
- Minimal Diagnosis:
- Fix Plan:
- Gap Closure Plan:
- Re-QA Required:
- Regression Note:
- Scoped Next Action:
```

Rules:

- Hard instruction: keep every field in the shape even when information is missing. Use `not provided` for absent prompt details and `unverified` for details not checked. Do not replace this block with a generic QA process.
- Keep diagnosis minimal and evidence-backed.
- If cause is uncertain, say what is confirmed and what is still hypothesis.
- Do not skip `Expected`, `Actual`, or `Reproduction` for behavior failures.
- If the prompt does not provide concrete failure details, inspect the available fixture/checks when allowed. If details still cannot be confirmed, keep the field and write `not provided` or `unverified`; do not replace the report with a generic QA process.
- Do not hide severity in prose.
- Re-QA must name the original failing check or manual reproduction that has to be rerun.
- Gap closure plan must name the minimum scoped change or evidence update needed before verdict can change.
- Regression note must state the smallest adjacent behavior that should be rechecked, or `not identified` when there is no evidence yet.
- Do not update a failure verdict to pass until the original reproduction/check has been re-QA'd or the missing re-QA evidence is explicitly reported as unresolved.
- Scoped next action must say whether the next step belongs to `implement`, `verify`, or a human decision, and must avoid broad refactors.

## Implement Fix Loop

When `implement` receives a verify failure:

1. Confirm the failure report has expected, actual, reproduction, severity, minimal diagnosis, fix plan, and re-QA requirement.
2. Fix only the scoped failure.
3. Rerun the original failing check after the fix.
4. Add or update a focused regression test/check when feasible.
5. Report any unresolved gap back to `verify`.

Do not turn one failed check into broad cleanup or unrelated behavior changes.
