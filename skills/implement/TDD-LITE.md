# Implement TDD-Lite

Target Reader: Codex running the Groundwork `implement` skill.
Reader Action Needed: Prefer a failing check or reproduction before changing behavior, then make the smallest fix.
Decision Supported: Whether the implementation is evidence-backed rather than speculative.
Scope: Focused bug fixes and behavior changes where a local test or reproduction is feasible.
Out of Scope: Full test strategy, broad refactors, or claiming final readiness.
Evidence Level: Groundwork issue #6 acceptance criteria and existing runtime fixture patterns.

Use this loop when behavior changes:

```text
RED
- Failing test, failing command, failing reproduction, or confirmed source-level contradiction:

GREEN
- Minimal change that addresses the confirmed failure:

REFACTOR
- Optional cleanup only after green, and only when it reduces real complexity:
```

Rules:

- Do not claim TDD or RED if no failing test or reproduction was run.
- If a failing check is not feasible, give a no-test justification before editing.
- If the issue is suspected but not confirmed, diagnose first and separate confirmed cause from hypothesis.
- After the fix, rerun the original failing check when available.
- Add or update a focused regression test/check when feasible and proportional to risk.
- Keep refactors scoped to the changed behavior; unrelated cleanup waits.

No-test justification format:

```text
No-Test Justification
- Missing check:
- Why not feasible now:
- Alternative evidence:
- Follow-up verification:
```
