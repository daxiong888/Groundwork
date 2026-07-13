# Task: Normalize Phone Matching At The Shared Seam

## Goal

Phone matching must treat spaces and hyphens as formatting in both list filtering and exact lookup.

## Acceptance Criteria

- `filterTasks` matches a stored digits-only phone when the filter contains supported spaces or hyphens.
- `findTaskByPhone` applies the same comparison contract.
- Existing `activityName` filtering remains unchanged.
- The fix repairs the shared phone-normalization invariant instead of duplicating normalization in one caller.
- The change stays inside this fixture and does not add dependencies, network access, remote writes, or unrelated refactors.

## Verification

Run:

```bash
node test/taskSearch.test.mjs
```

Before the fix, the formatted-phone assertions fail in both call paths. After the fix, all assertions pass.
