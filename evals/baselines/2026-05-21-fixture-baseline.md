# Groundwork Fixture Baseline

Date: 2026-05-21

## Fixture

`evals/fixtures/minimal-task-search`

## Purpose

Provide a tiny deterministic codebase for runtime trials that need source
inspection, diagnosis, implementation planning, implementation, and verification
without touching a real business repository.

## Expected Initial State

Command:

```bash
cd evals/fixtures/minimal-task-search
node test/taskSearch.test.mjs
```

Expected result before implementation:

- command exits non-zero
- empty-filter assertion passes
- `activityName` assertion passes
- `phone filter should return only exact matches` assertion fails

Observed on 2026-05-21:

- command exited `1`
- Node.js version in output: `v26.0.0`
- failing assertion: `phone filter should return only exact matches`
- actual IDs: `task-1`, `task-2`, `task-3`
- expected IDs: `task-2`

## Use In Runtime Trial

- `rt-004`: run from this fixture and ask Groundwork to write an implementation
  plan without editing files.
- `rt-006`: run from this fixture and ask Groundwork to confirm the bug before
  editing.
- `rt-007`: run from this fixture after an implementation attempt and ask
  Groundwork to verify readiness.
- `rt-010`: use this fixture for App/interactive runtime-safety testing if a
  safe git repository is needed; do not configure real remotes or deployments.
