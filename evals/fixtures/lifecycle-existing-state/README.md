# Lifecycle Existing State Fixture

This fixture validates handoff behavior when a workstream-scoped lifecycle
state file already exists.

The runtime row should reference `artifacts/admin-user-filter/STATE.md`, report
freshness or update needs, and avoid copying the full state body into the final
handoff response.
