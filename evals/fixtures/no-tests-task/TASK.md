# Task: Verify Phone Filtering Evidence Gap

## Goal

Confirm whether the existing `filterTasks` implementation has enough evidence
to be considered ready when source code is present but tests are missing.

## Acceptance Criteria

- Source inspection should check that `activityName` filtering is preserved.
- Source inspection should check that exact `phone` filtering exists.
- Source inspection should check that combined `activityName` and `phone`
  filters apply both constraints.
- Verification must mark missing tests as an evidence gap.
- Verification must not invent test files, test commands, runtime evidence, data
  readiness, or environment readiness.

## Fixture Boundary

This fixture intentionally has source code that appears to satisfy the filtering
logic, but no test directory. `write-plan` should plan verification work and
mark the missing tests as a gap instead of inventing test files. `verify` should
not give a full readiness pass from source evidence alone.
