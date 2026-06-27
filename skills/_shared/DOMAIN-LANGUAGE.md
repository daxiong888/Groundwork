Target Reader: Groundwork skill authors, PRD shapers, prototype authors, implementers, clean reviewers, verifiers, and handoff authors handling terminology that may affect product or engineering truth.
Reader Action Needed: Use this lightweight shared vocabulary to classify domain-language and term-conflict evidence boundaries without creating a persistent glossary or public skill.
Decision Supported: Whether a term is glossary-only, PRD truth, contract truth, source truth, runtime evidence, user-confirmed, or unknown before promoting it across artifacts or workflows.
Artifact Type: shared guardrail.
Source of Truth: `docs/prd-v0.5.1-socratic-grilling-expansion.md` FR-620 through FR-624 and AC-D.
Scope: Domain-language / term-conflict evidence layers, promotion blockers, and route boundaries for PRD shaping and regression touchpoints.
Out of Scope: Creating a public `domain-language` skill, maintaining a persistent project glossary, accepting PRDs, defining backend/API contracts, proving runtime behavior, or deciding readiness.
Evidence Level: Source-validation policy only. This file does not prove source, runtime, browser, UAT, release, marketplace, installed-plugin, cache-refresh, selector-enforcement, or customer readiness.
Safe to Share / Redaction Notes: Safe to share as-is; contains no secrets, credentials, PII, private payloads, or production data.

# Domain Language Boundary

## Core Rule

Domain-language alignment is evidence-boundary hygiene. It is not PRD acceptance, backend/API contract truth, source truth, implementation readiness, clean review, independent verification, runtime evidence, browser evidence, UAT evidence, release evidence, or customer readiness.

Use this vocabulary only when terminology materially affects acceptance, contract truth, source truth, prototype interpretation, verification, or handoff.

## Evidence Layers

Use exactly these labels when a material term conflict is reported:

| Evidence layer | Meaning | Must not be treated as |
| --- | --- | --- |
| `glossary_only` | Artifact-local wording alignment for discussion or handoff. | PRD truth, contract truth, source truth, readiness evidence. |
| `PRD_truth` | Term is accepted in PRD/spec intent or acceptance criteria. | Backend/API/schema/source truth unless separately backed. |
| `contract_truth` | Term is backed by an accepted API/schema/DB/frontend-backend contract or explicit user confirmation for that contract. | Runtime behavior, UAT, release, or customer readiness. |
| `source_truth` | Term is backed by inspected source code, schema, docs-as-source, or authoritative local artifact. | Runtime/browser/UAT/release behavior. |
| `runtime_evidence` | Term was observed in a named runtime/tool/API/browser run for the scoped claim. | Universal product truth outside that run. |
| `user_confirmed` | User explicitly confirmed the term or mapping for the stated boundary. | Broader contract/source/runtime truth unless the confirmation covers it. |
| `unknown` | No sufficient evidence yet. | Any promoted truth layer. |

## Term Conflict Shape

When terminology is material, report it compactly:

```text
Domain Language / Term Conflict
- User term:
- Existing repo/doc/API/UI term:
- Conflict:
- Canonical term for this artifact:
- Evidence layer: glossary_only | PRD_truth | contract_truth | source_truth | runtime_evidence | user_confirmed | unknown
- Promotion blocked until:
```

When no material term conflict exists, do not print a full bucket in normal conversation output. Durable PRDs may omit the section or write:

```text
Domain Language / Term Conflict: none material.
```

## Promotion Rules

1. Glossary-only alignment is not PRD acceptance.
2. PRD wording is not backend/API contract truth.
3. Prototype labels are not source truth.
4. UI labels are not API fields unless source-backed or explicitly confirmed.
5. Backend/API contract truth requires inspected backend/API source, API response, schema, accepted contract artifact, or explicit user confirmation for that contract boundary. PRD wording alone remains `PRD_truth` until separately backed by contract/source evidence or contract-scoped user confirmation.
6. Runtime, browser, UAT, release, customer, marketplace, installed-plugin, cache-refresh, and selector-enforcement claims require separate named evidence.
7. If user terminology conflicts with source truth, surface the conflict instead of silently choosing one.
8. Do not create backend fields, business states, APIs, metrics, permissions, owners, timelines, or acceptance details from term alignment alone.

## Route Boundaries

- `to-prd`: applies this vocabulary only when terminology materially affects PRD correctness, acceptance criteria, source truth, contract truth, prototype interpretation, verification, or handoff.
- `prototype`: keeps mock fields, illustrative labels, client-derived logic, proposed hypotheses, and unverified terms separate from backend/API truth.
- `verify`: tests term claims only inside a declared verification scope and marks glossary-only, PRD-only, prototype-only, or summary-only terms insufficient for readiness claims that require stronger evidence.
- `implement`: does not implement from glossary-only or unknown terms when acceptance, contract, source, or runtime truth is required.
- `handoff`: may use artifact-local canonical terms, but must preserve the evidence layer and promotion blocker.
- `wiki`: may store aliases, homonyms, and term pages as long-lived project orientation, but term pages remain claim inventory. `wiki` must not promote glossary-only, stale, contested, uncited, or unknown terms into PRD truth, contract truth, source truth, runtime evidence, verification evidence, release evidence, UAT evidence, or customer readiness.

## Public Surface Boundary

Do not create `skills/domain-language/SKILL.md` for this behavior in v0.5.1. A standalone glossary route would be easy to confuse with PRD/spec or contract truth and is out of scope.

The v0.5.2 public `wiki` route may maintain term pages as part of a broader project-level LLM Wiki lifecycle, but this does not change the evidence-layer promotion rules above.
