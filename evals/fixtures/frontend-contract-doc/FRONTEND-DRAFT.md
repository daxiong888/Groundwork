# Frontend Draft With Noise

Target Reader: Frontend engineer.

Draft claims:

- Endpoint is `GET /api/tasks`.
- `phone` supports fuzzy matching and prefix matching.
- Response includes `id`, `phone`, `activityName`, and `backendMapperName`.
- Error `400 INVALID_FILTER` should show invalid filter copy.
- See PRD path `docs/internal/task-prd.md`.
- Backend module is `TaskSearchMapper`.
- SQL follow-up is needed for old archived migrations.
- The AI thinks frontend should expose backend module details for debugging.
