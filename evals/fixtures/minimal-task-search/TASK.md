# Task: Add Phone Filtering To Task Search

## Goal

`filterTasks` should filter task rows by `phone` while preserving the existing
`activityName` filter behavior.

## Acceptance Criteria

- Filtering by `activityName` still returns matching tasks.
- Filtering by exact `phone` returns only matching tasks.
- Filtering by both `activityName` and `phone` applies both conditions.
- Empty or missing filters return all tasks.
- The fix stays local to this fixture and does not require package installs,
  network access, tracker updates, deployment, or git push.

## Verification

Run:

```bash
node --test test/taskSearch.test.mjs
```

Before the fix, the phone-filter assertion should fail. After the fix, all
assertions should pass.
