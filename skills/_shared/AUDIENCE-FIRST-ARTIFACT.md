# Audience-First Artifact Contract

Use this contract whenever a skill creates or materially updates a durable artifact.

## Required Header Fields (exact)

Every new or materially updated durable artifact must include these fields exactly:

- Target Reader
- Reader Action Needed
- Decision Supported
- Scope
- Out of Scope
- Evidence Level

## Notes

- Keep each field concise and decision-oriented.
- If the user requests a different layout, preserve their layout but keep these exact field names present.
- Do not add sensitive values (secrets, credentials, tokens, PII, sensitive logs) into headers or artifact bodies.
