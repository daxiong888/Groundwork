# Minimal Task Search Fixture

This fixture gives Groundwork runtime trials a tiny, deterministic codebase for
`write-plan`, `implement`, and `verify`.

It intentionally contains one small bug: `filterTasks` supports activity-name
filtering but ignores the phone filter.

## Files

- `TASK.md` defines the accepted task and boundaries.
- `src/taskSearch.mjs` contains the buggy implementation.
- `test/taskSearch.test.mjs` contains focused tests.

## Commands

Run from this directory:

```bash
node test/taskSearch.test.mjs
```

Expected before implementation:

- activity-name filtering passes
- phone filtering fails

Expected after implementation:

- all tests pass

## Boundaries

- No package install is required.
- No network access is required.
- No external write is required.
- Do not push, deploy, mutate trackers, or write remote data from this fixture.
