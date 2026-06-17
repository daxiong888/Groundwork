# Goal Contract Embedded Placeholder Fail Fixture

Target Reader: Goal Contract linter maintainers and Groundwork reviewers.
Reader Action Needed: Use this fixture to confirm embedded placeholders inside otherwise executable-looking Goal Commands fail.
Decision Supported: Whether `scripts/lint_goal_contract.py` rejects templated Goal Commands such as `/goal Implement <task> [acceptance]`.
Scope: Negative linter fixture only.
Out of Scope: Runtime execution, dispatch package generation, and product acceptance.
Evidence Level: Derived from v0.3.3 Goal Mode hardening and PR review feedback.

## Goal Contract

- Goal Command: /goal Implement <task> [acceptance]
- Outcome: Add focused linter behavior for embedded placeholder command validation.
- Source Truth: `skills/_shared/GOAL-CONTRACT.md` and PR #59 review feedback.
- Acceptance Criteria Mapping: Goal Mode hardening requires executable Goal Commands with no template placeholders.
- Verification: Run `python3 scripts/lint_goal_contract.py evals/scenarios/goal-contract-embedded-placeholder-fail.md` and confirm it fails.
- Constraints: Keep edits scoped to Goal Contract lint behavior and fixture coverage.
- Boundaries: Do not edit production data, secrets, dependency files, `.groundwork/`, `.trellis/`, `refer/`, or unrelated docs.
- Iteration Policy: Make one focused remediation pass; pause after two failed attempts without new evidence.
- Stop When: This fixture prints `Goal Contract Lint: fail` with a `Goal Command` finding.
- Pause If: The linter cannot distinguish extracted field values from unrelated text.
- Non-goals: Do not implement runtime execution, task CRUD, hooks, MCP servers, or external tracker synchronization.
- Risk / Gate: The linter is intentionally lightweight and checks structurally detectable placeholder tokens.
- Preferred Runtime: codex_app_managed_worktree_thread
- Result Package Expected: review_package
