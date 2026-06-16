# Goal Contract Empty Last Field Fail Fixture

Target Reader: Goal Contract linter maintainers and Groundwork reviewers.
Reader Action Needed: Use this fixture to confirm an empty final Goal Contract field is not satisfied by later ordinary text.
Decision Supported: Whether `scripts/lint_goal_contract.py` rejects empty trailing fields even when notes, code fences, or footnotes follow the contract.
Scope: Negative linter fixture for trailing empty field parsing only.
Out of Scope: Runtime execution, dispatch package generation, and product acceptance.
Evidence Level: Derived from PR #56 review feedback on multiline field parsing.

## Goal Contract

- Goal Command: /goal Validate that an empty final Goal Contract field remains invalid.
- Outcome: Add regression coverage for trailing empty field parsing.
- Source Truth: PR #56 review feedback and `skills/_shared/GOAL-CONTRACT.md`.
- Acceptance Criteria Mapping: The final required field must have explicit content, not unrelated footer text.
- Verification: Run `python3 scripts/lint_goal_contract.py evals/scenarios/goal-contract-empty-last-field-fail.md` and confirm it fails.
- Constraints: Keep edits scoped to Goal Contract docs, linter behavior, and fixture coverage.
- Boundaries: Do not edit production data, secrets, dependency files, `.groundwork/`, `.trellis/`, `refer/`, or unrelated docs.
- Iteration Policy: Make one focused remediation pass; rerun the affected linter fixture after each change.
- Stop When: This fixture prints `Goal Contract Lint: fail` with a `Result Package Expected` finding.
- Pause If: The parser cannot distinguish contract field continuation from ordinary footer text.
- Non-goals: Do not implement runtime execution, task CRUD, hooks, MCP servers, or external tracker synchronization.
- Risk / Gate: Footer text must not be treated as a value for an empty final required field.
- Preferred Runtime: codex_app_managed_worktree_thread
- Result Package Expected:

This note is ordinary footer text and must not satisfy the empty field above.

```text
This code fence mentions review_package, but it is not the field value.
```

[example]: https://example.invalid/review-package
