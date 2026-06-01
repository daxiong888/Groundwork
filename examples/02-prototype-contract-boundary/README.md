# Example: Prototype Contract Boundary

Target Reader: Open-source maintainers using prototypes to discuss product, UI, or integration behavior.
Reader Action Needed: Use this case study to keep prototype output separate from backend contract truth.
Decision Supported: Whether Groundwork helps maintainers share useful prototypes without inventing API fields, statuses, or server-owned rules.
Scope: Prototype contract-boundary behavior in Groundwork v0.2.x and recorded runtime evidence.
Out of Scope: Backend implementation, frontend contract approval, UI polish, or current runtime reruns.
Evidence Level: `skills/prototype/SKILL.md`, `skills/prototype/CONTRACT-BOUNDARY.md`, `CHANGELOG.md` v0.2.2, and v0.2.2/v0.2.3 runtime baseline rows.

This example shows how Groundwork prevents a UI or logic prototype from becoming a false backend contract.

## Maintainer Request

```text
Build a prototype that explains this product rule to frontend reviewers.
```

## Groundwork Loop

```text
to-prd -> prototype / implement -> verify -> handoff
```

## What Changed

Prototype guidance was hardened so prototype artifacts classify backend contract candidates, confirmed backend fields, mock fields, and client-derived logic separately.

Changed areas:

- `skills/prototype/SKILL.md`
- `skills/prototype/CONTRACT-BOUNDARY.md`
- `evals/prompts/guardrails-regression.csv`
- v0.2.2 and v0.2.3 runtime baseline reports

## Artifacts

- [`prd.md`](prd.md) describes why prototype boundaries matter.
- [`implement.md`](implement.md) records the implementation behavior and real evidence.
- [`verify.md`](verify.md) maps boundary claims to repository evidence.
- [`handoff.md`](handoff.md) packages the example for future maintainers.

## Maintainer Value

Maintainers can use prototypes to make behavior reviewable without accidentally approving fake backend fields, statuses, or server rules. Mock and client-derived values stay labeled as illustrative and not backend contract.

