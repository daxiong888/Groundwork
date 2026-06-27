# Artifact Directory Policy

When writing local artifacts, use the following locations:

- `artifacts/<feature-slug>/`
- `artifacts/<workstream-slug>/`
- `wiki/`
- `artifacts/wiki/`
- `.groundwork/wiki/`
- `.groundwork/runs/`
- `.groundwork/harness/`
- `.groundwork/tmp/`

Rules:

- Prefer `artifacts/<feature-slug>/` for durable reviewable artifacts tied to a feature.
- Use `artifacts/<workstream-slug>/STATE.md` and optional `artifacts/<workstream-slug>/ROADMAP.md` only for lifecycle state that meets `skills/_shared/LIFECYCLE-STATE.md` thresholds.
- Use `wiki/` only for accepted shared project wiki knowledge after storage-mode selection.
- Use `artifacts/wiki/` only when the project requires all durable knowledge under `artifacts/`.
- Use `.groundwork/wiki/` only for private scratch wiki content. It is ignored by default and must not be committed unless the user explicitly approves a redacted promotion path.
- Do not create any wiki for one-time scratch context.
- Do not copy repo source files wholesale into wiki raw sources.
- Treat wiki content as orientation and claim inventory, not source truth, implementation authority, verification evidence, release evidence, UAT evidence, customer readiness, marketplace evidence, installed-plugin evidence, cache-refresh evidence, or selector enforcement.
- Use `.groundwork/runs/`, `.groundwork/harness/`, and `.groundwork/tmp/` for runtime support files only.
- `.groundwork/*` runtime directories are ignored by default and are not committed unless the user explicitly approves committing them.
- Do not commit runtime contents from `.groundwork/*` without explicit approval.
- Prefer updating an existing canonical artifact over creating duplicates.
- Do not create empty placeholder files.
