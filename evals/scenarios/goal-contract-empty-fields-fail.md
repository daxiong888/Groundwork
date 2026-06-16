# Goal Contract Empty Fields Fail Fixture

Target Reader: Goal Contract linter maintainers and Groundwork reviewers.
Reader Action Needed: Use this fixture to confirm required labels with empty same-line values fail the lightweight linter.
Decision Supported: Whether `scripts/lint_goal_contract.py` rejects empty required fields instead of accepting label-only contracts.
Scope: Negative linter fixture for empty required fields only.
Out of Scope: Runtime execution, dispatch package generation, and product acceptance.
Evidence Level: Derived from clean-review remediation feedback for GW-1.

## Goal Contract

- Goal Command: /goal Validate that empty required Goal Contract fields fail lint.
- Outcome:
- Source Truth: clean review finding for GW-1.
- Acceptance Criteria Mapping: Empty required fields must fail lint.
- Verification: Run `python3 scripts/lint_goal_contract.py evals/scenarios/goal-contract-empty-fields-fail.md`.
- Constraints:
- Boundaries:
- Iteration Policy:
- Stop When:
- Pause If:
- Non-goals: Do not implement dispatch, triage, or to-issues behavior.
- Risk / Gate: Empty same-line values must be treated as missing contract content.
- Preferred Runtime:
- Result Package Expected: review_package
