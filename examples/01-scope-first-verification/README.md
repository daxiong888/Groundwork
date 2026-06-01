# Example: Scope-First Verification

Target Reader: Open-source maintainers reviewing how Groundwork handles readiness and UAT questions.
Reader Action Needed: Use this case study to understand why `verify` starts with explicit scope before any readiness verdict.
Decision Supported: Whether scope-first verification prevents Codex-assisted maintenance from overstating release or UAT confidence.
Scope: The v0.2.2 and v0.2.3 `verify` hardening documented in repository changelog and runtime baselines.
Out of Scope: New verification behavior, new eval rows, new runtime execution, or release claims beyond the recorded baseline evidence.
Evidence Level: `CHANGELOG.md` v0.2.2/v0.2.3, `skills/verify/SKILL.md`, `skills/verify/SCOPE-EVIDENCE-TEMPLATE.md`, `skills/verify/LENSES.md`, and `evals/baselines/2026-05-25-v0.2.3-runtime-baseline.md`.

This example shows how Groundwork helps a maintainer answer a readiness question without overclaiming.

## Maintainer Request

```text
Can this change be sent to UAT?
```

## Groundwork Loop

```text
to-prd -> implement -> verify -> handoff
```

## What Changed

The `verify` workflow was hardened so final verification reports begin with the complete `Verification Scope` block before any verdict, finding, contract review, UI note, QA package, approval gate, or subagent prompt.

Changed areas:

- `skills/verify/SKILL.md`
- `skills/verify/SCOPE-EVIDENCE-TEMPLATE.md`
- `skills/verify/LENSES.md`
- `evals/prompts/guardrails-regression.csv`
- `evals/baselines/2026-05-25-v0.2.3-runtime-baseline.md`

## Artifacts

- [`prd.md`](prd.md) describes the maintainer problem and acceptance criteria.
- [`implement.md`](implement.md) records the implementation evidence from the real hardening line.
- [`verify.md`](verify.md) maps claims to repository evidence.
- [`handoff.md`](handoff.md) packages the case for another maintainer.

## Maintainer Value

Scope-first verification makes the difference between "looks good" and "verified within this explicit scope." It keeps missing runtime, data, environment, and UAT evidence visible instead of turning partial checks into release confidence.

