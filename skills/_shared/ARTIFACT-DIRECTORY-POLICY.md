# Artifact Directory Policy

When writing local artifacts, use the following locations:

- `artifacts/<feature-slug>/`
- `artifacts/<workstream-slug>/`
- `.groundwork/runs/`
- `.groundwork/harness/`
- `.groundwork/tmp/`

Rules:

- Prefer `artifacts/<feature-slug>/` for durable reviewable artifacts tied to a feature.
- Use `artifacts/<workstream-slug>/STATE.md` and optional `artifacts/<workstream-slug>/ROADMAP.md` only for lifecycle state that meets `skills/_shared/LIFECYCLE-STATE.md` thresholds.
- Use `.groundwork/runs/`, `.groundwork/harness/`, and `.groundwork/tmp/` for runtime support files only.
- `.groundwork/*` runtime directories are ignored by default and are not committed unless the user explicitly approves committing them.
- Do not commit runtime contents from `.groundwork/*` without explicit approval.
- Prefer updating an existing canonical artifact over creating duplicates.
- Do not create empty placeholder files.
