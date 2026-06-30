Target Reader: Groundwork planners, implementers, reviewers, and maintainers.
Reader Action Needed: Use this compact field set when API, DB, state, frontend, docs, or verification alignment affects an implementation plan.
Decision Supported: Whether a plan has enough inspected contract evidence to proceed, or which verification route must run next.
Artifact Type: shared planning contract reference.
Source of Truth: `skills/write-plan/SKILL.md` contract-planning requirements and Groundwork evidence-boundary rules.
Scope: Inline Contract Notes for implementation planning.
Out of Scope: Public skill routing, source-truth verification, runtime evidence, release readiness, or full contract documentation.
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

Rules:

- `contract` is an internal planning concern, not a public skill route.
- `Source inspected` must name the source, artifact, test, schema, or explicit user confirmation that supports the note, or say `not inspected`.
- `Verified facts` must not include exact endpoints, fields, schemas, states, or commands unless they were inspected or provided by a canonical source.
- `Unverified assumptions` must remain assumptions until `verify`, source inspection, runtime/browser evidence, or explicit confirmation resolves them.
- `Next verification route` should usually be `verify` for source-truth/readiness claims, or `prototype` when a throwaway artifact is needed before source truth exists.
