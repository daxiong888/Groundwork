# Goal Contract Multiline Pass Fixture

Target Reader: Goal Contract linter maintainers and Groundwork reviewers.
Reader Action Needed: Use this fixture to confirm readable multiline Goal Contract fields pass the lightweight linter.
Decision Supported: Whether `scripts/lint_goal_contract.py` accepts block values after required labels.
Scope: Positive linter fixture only.
Out of Scope: Runtime execution, dispatch package generation, and product acceptance.
Evidence Level: Derived from `docs/prd-dispatch-runtime-router.md` FR-8 and AC-9.

## Goal Contract

- Goal Command:
  /goal Implement Issue 1 by tightening Goal Contract lint behavior and fixture coverage.
- Outcome:
  Add focused linter behavior that accepts readable multiline fields while rejecting incomplete executable goals.
- Source Truth:
  `docs/prd-dispatch-runtime-router.md`, `skills/_shared/GOAL-CONTRACT.md`, and review findings for PR #56.
- Acceptance Criteria Mapping:
  - AC-9: executable agent tasks require a `/goal` command, verification, constraints, boundaries, iteration policy, stop condition, and pause condition.
  - AC-10: missing product truth must pause instead of being invented.
- Verification:
  - Run command `python3 scripts/lint_goal_contract.py evals/scenarios/goal-contract-multiline-pass.md`.
  - Run command `git diff --check origin/main...HEAD`.
- Constraints:
  - Keep edits limited to Goal Contract docs, linter behavior, and fixture coverage.
  - Do not modify remotes, credentials, production systems, or unrelated dependency files.
- Boundaries:
  - Do not change public runtime adapters beyond dispatch contract documentation.
  - Do not edit `.groundwork/`, `.trellis/`, `refer/`, or unrelated docs.
- Iteration Policy:
  Make one focused remediation pass; rerun the affected linter fixture after each change, and pause after two failed attempts without new evidence.
- Stop When:
  The multiline fixture prints `Goal Contract Lint: pass` and the invalid Goal Command fixture prints `Goal Contract Lint: fail`.
- Pause If:
  Existing markdown conventions conflict with block field parsing, validation commands are unavailable, or scope would require dependency installation.
- Non-goals:
  Do not implement runtime execution, task CRUD, hooks, MCP servers, or external tracker synchronization.
- Risk / Gate:
  The linter remains lightweight and does not validate a full Markdown AST.
- Preferred Runtime:
  codex_app_managed_worktree_thread
- Result Package Expected:
  review_package
