# Frontend Contract Doc Fixture

This fixture checks that `verify` reviews frontend-facing contract docs against source truth instead of accepting a noisy draft by shape alone.

## Files

- `BACKEND-SOURCE.md` is the source-backed contract.
- `FRONTEND-DRAFT.md` is intentionally noisy and includes unsupported/internal claims.

## Expected Behavior

- Inspect `BACKEND-SOURCE.md` before accepting frontend contract claims.
- Keep frontend output limited to endpoint, method, request fields, response fields, error copy, call rules, and boundary conditions.
- Mark unsupported claims from `FRONTEND-DRAFT.md` as `unverified` or remove them from the frontend-facing contract.
- Do not expose backend modules, PRD paths, SQL follow-ups, or AI narration as frontend contract.
