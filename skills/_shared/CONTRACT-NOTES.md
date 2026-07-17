Target Reader: Groundwork planners, implementers, reviewers, and maintainers.
Reader Action Needed: Use the compact fields for contract alignment; add lineage only when ownership or representation crosses a material boundary.
Decision Supported: Whether planning, diagnosis, or review has enough inspected contract evidence to proceed and where the first confirmed divergence belongs.
Artifact Type: shared contract reference.
Source of Truth: Groundwork contract-planning, first-principles, verification-lens, and evidence-boundary rules.
Scope: Inline Contract Notes plus optional cross-boundary lineage for planning, diagnosis, and review.
Out of Scope: Public skill routing, full contract documentation, runtime evidence, release readiness, or automatic fix ownership.
Evidence Level: Source-validation policy only. Contract Notes do not prove source/runtime/UAT/release readiness unless separately verified.
Safe to Share / Redaction Notes: Safe to share as-is; contains no secrets, credentials, PII, private logs, or production payloads.

# Contract Notes

Use this field set inline when a plan depends on API, DB, state, frontend, docs, or verification-contract alignment:

```text
Contract Notes
- Contract surface:
- Source inspected:
- Verified facts:
- Unverified assumptions:
- Risk if wrong:
- Next verification route:
```

## Contract Lineage (cross-boundary only)

Use this optional block only when a claim crosses ownership or representation boundaries, such as callbacks, imports/exports, indexes, mappings, or raw/derived/display/fallback semantics. Omit it for ordinary single-boundary contracts.

```text
Contract Lineage
- Canonical Owner / Source:
- Hops:
- First Confirmed Divergence:
- Fix Owner / Boundary:
- Unverified / Branched Hops:
```

Rules:

- `contract` is an internal planning concern, not a public skill route.
- `Source inspected` must name the source, artifact, test, schema, or explicit user confirmation that supports the note, or say `not inspected`.
- `Verified facts` must not include exact endpoints, fields, schemas, states, or commands unless they were inspected or provided by a canonical source.
- `Unverified assumptions` must remain assumptions until `verify`, source inspection, runtime/browser evidence, or explicit confirmation resolves them.
- `Next verification route` should usually be `verify` for source-truth/readiness claims, or `prototype` when a throwaway artifact is needed before source truth exists.
- `Canonical Owner / Source` names the accepted contract, schema, inspected source, or contract-scoped confirmation; a producer is not authoritative merely because it appears first.
- `Hops` may branch and may include producer, persistence/index, transforms/mappings, consumer/API, display/export, and fallback only when applicable. The machine token is `hop_id(verified|unverified|not_applicable)`; use `>` for ordered stages and `|` only for sibling branches. Do not add empty branches, repeat a hop ID, split tokens with whitespace, or substitute the prose spelling `not applicable`.
- `First Confirmed Divergence` is the earliest inspected hop whose actual meaning contradicts the canonical contract. If an earlier material hop is uninspected, keep the divergence and fix owner `unverified`.
- Fix ownership follows the first confirmed divergence. Producer-first inspection is not producer-first blame, and an intentional source-backed raw-to-display transform is not itself a failure.
- Do not infer semantics from field names or copy internal lineage details into consumer-facing contract docs unless that reader needs them.

## Route-owned Lineage Companions

When `Contract Lineage` is emitted as a machine-checked route output, preserve the route's ordinary result under exactly one owning section. Do not put these fields in code fences, HTML comments, or unrelated prose.

`implement`:

```text
Diagnosis Outcome
- Confirmed Cause: <must name First Confirmed Divergence>
- Decisive Evidence: <must bind Canonical Owner / Source and First Confirmed Divergence>
- Smallest Safe Next Action: <must name Fix Owner / Boundary>
```

`verify`:

```text
Verification Continuation
- Next Check: <must name Fix Owner / Boundary>
```

`write-plan`:

```text
Implementation Plan
- Accepted Goal:
- Ordered Steps:
- Dependencies / Gates:
- Verification Checkpoints:
- Stop Condition:
```

When lineage ownership or a material hop remains unverified, the plan companion must preserve the exact unresolved hop IDs and an explicit `unverified` or `blocked` gate. The structured lineage sections and their route companion must not be followed by a contradictory recommendation.
