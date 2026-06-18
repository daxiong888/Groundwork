# Audience-First Artifact Contract

Use this contract whenever a skill creates or materially updates a durable artifact.

## Required Header Fields (exact)

Every new or materially updated durable artifact must include these fields exactly:

- Target Reader
- Reader Action Needed
- Decision Supported
- Artifact Type
- Source of Truth
- Scope
- Out of Scope
- Evidence Level
- Safe to Share / Redaction Notes

## Notes

- Keep each field concise and decision-oriented.
- `Artifact Type` should name the artifact family, such as PRD, issue map, contract note, verification report, handoff, lifecycle state, baseline, or maintainer doc.
- `Source of Truth` should name the canonical source type or path when known. Use `mixed` or `unknown` only when the uncertainty is intentional and visible.
- `Safe to Share / Redaction Notes` must say whether the artifact can be shared as-is or what was redacted or excluded.
- If the user requests a different layout, preserve their layout but keep these exact field names present.
- Do not add sensitive values (secrets, credentials, tokens, PII, sensitive logs) into headers or artifact bodies.
