# Shared Artifact Policy

Use this policy whenever a skill may produce or update a durable artifact.

## Audience-First Header (required)

Every newly written or materially updated artifact must start with this header block:

```text
Audience
Purpose
Use This For
Do Not Use This For
Source Of Truth
Update Trigger
Owner
```

Rules:

- Keep each line concise and explicit.
- `Audience` names the primary reader first (for example: PM, implementer, verifier, next-session owner).
- `Purpose` states the decision or action this artifact enables.
- `Use This For` and `Do Not Use This For` define boundaries to avoid misuse.
- `Source Of Truth` points to canonical upstream references instead of duplicating them.
- `Update Trigger` states when the artifact must be refreshed.
- `Owner` names the role that keeps it current.

If the user requests a different format, preserve their requested format and still include equivalent audience-first fields.

## Shared Directory Policy (required)

When creating local Groundwork artifacts, place them under:

- `.groundwork/tasks/<task-id>/` for task-scoped artifacts
- `.groundwork/shared/` for cross-task references reused by multiple tasks

Do not write durable artifacts outside these locations unless the user explicitly asks for a different target.

Additional rules:

- Prefer updating an existing canonical artifact over creating a duplicate.
- Do not create empty placeholder files.
- Keep filenames purpose-first (for example: `verification-summary.md`, `agent-brief.md`).
- Redact secrets, credentials, PII, sensitive logs, screenshots, requests, and database rows.

## Minimal Header Template

```markdown
## Artifact Header
- Audience: <primary reader>
- Purpose: <decision/action enabled>
- Use This For: <approved usage>
- Do Not Use This For: <out-of-scope usage>
- Source Of Truth: <canonical artifact links/paths>
- Update Trigger: <when to refresh>
- Owner: <maintaining role>
```
