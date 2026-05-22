# Backend Source Truth

Endpoint / Method: `GET /api/tasks`

Request fields:

- `phone`: optional string; exact match after trimming.
- `activityName`: optional string; exact match after trimming.

Response fields:

- `id`: string task id.
- `phone`: string customer phone.
- `activityName`: string activity display name.

Error code / error copy:

- `400 INVALID_FILTER`: filter value is invalid.

Call rules:

- Omit empty filters.
- When both filters are present, apply both constraints.

Boundary conditions:

- No partial phone matching is supported.
- No backend module names or SQL follow-up tasks are frontend contract.
