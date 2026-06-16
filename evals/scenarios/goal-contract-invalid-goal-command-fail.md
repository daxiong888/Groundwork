# Goal Contract Invalid Goal Command Fail Fixture

Target Reader: Goal Contract linter maintainers and Groundwork reviewers.
Reader Action Needed: Use this fixture to confirm `Goal Command` must start with `/goal`.
Decision Supported: Whether `scripts/lint_goal_contract.py` rejects a Goal Command value that lacks the required command prefix even when `/goal` appears elsewhere.
Scope: Negative linter fixture only.
Out of Scope: Runtime execution, dispatch package generation, and product acceptance.
Evidence Level: Derived from `docs/prd-dispatch-runtime-router.md` FR-8 and AC-9.

## Goal Contract

- Goal Command: Please implement Issue 1 after reading the source package.
- Outcome: Add focused linter behavior for Goal Contract command validation.
- Source Truth: `docs/prd-dispatch-runtime-router.md`, `skills/_shared/GOAL-CONTRACT.md`, and review findings for PR #56.
- Acceptance Criteria Mapping: AC-9 requires the executable Goal Command value itself to start with `/goal`.
- Verification: Run `python3 scripts/lint_goal_contract.py evals/scenarios/goal-contract-invalid-goal-command-fail.md` and confirm it fails.
- Constraints: Keep edits scoped to Goal Contract docs, linter behavior, and fixture coverage.
- Boundaries: Do not edit production data, secrets, dependency files, `.groundwork/`, `.trellis/`, `refer/`, or unrelated docs.
- Iteration Policy: Make one focused remediation pass; pause after two failed attempts without new evidence.
- Stop When: This fixture prints `Goal Contract Lint: fail` with a `Goal Command` finding.
- Pause If: The linter cannot distinguish extracted field values from unrelated text.
- Non-goals: Do not implement runtime execution, task CRUD, hooks, MCP servers, or external tracker synchronization.
- Risk / Gate: This fixture intentionally includes `/goal` outside the Goal Command field to prevent whole-file substring false positives.
- Preferred Runtime: codex_app_managed_worktree_thread
- Result Package Expected: review_package

```text
Mentioning /goal here must not satisfy the Goal Command field rule.
```
