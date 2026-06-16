# Goal Contract Pass Fixture

Target Reader: Goal Contract linter maintainers and Groundwork reviewers.
Reader Action Needed: Use this fixture to confirm a complete Goal Contract passes the lightweight linter.
Decision Supported: Whether `scripts/lint_goal_contract.py` accepts a contract with all required fields, concrete verification, bounded writes, bounded iteration, and Chinese content.
Scope: Positive linter fixture only.
Out of Scope: Runtime execution, dispatch package generation, and product acceptance.
Evidence Level: Derived from `docs/prd-dispatch-runtime-router.md` FR-7, FR-8, AC-9, and AC-10.

## Goal Contract

- Goal Command: /goal Implement Issue 1 by adding the shared Goal Contract spec, linter, and fixture coverage in the Groundwork repository.
- Outcome: Add one shared contract document and one lightweight linter that reject incomplete executable goals.
- Source Truth: `docs/prd-dispatch-runtime-router.md` and `artifacts/dispatch-runtime-router/issue-map.md`.
- Acceptance Criteria Mapping: FR-7, FR-8, AC-9, and AC-10 are mapped to the checks below.
  - FR-7: `skills/_shared/GOAL-CONTRACT.md` defines the required fields and quality bar.
  - FR-8: `scripts/lint_goal_contract.py` scans Markdown files for required labels, `/goal`, placeholders, and vague contract text.
  - AC-9: executable agent tasks require `/goal`, verification, constraints, boundaries, iteration policy, stop condition, and pause condition.
  - AC-10: unclear product truth must route to human clarification instead of invented acceptance.
- Verification: Run `python3 scripts/lint_goal_contract.py evals/scenarios/goal-contract-pass.md`, `python3 scripts/lint_goal_contract.py evals/scenarios/goal-contract-fail.md`, the CSV parse smoke, and `git diff --check`.
- Constraints: Keep edits limited to Goal Contract docs, the linter script, and focused eval fixtures. Do not stage, commit, push, or modify remote systems.
- Boundaries: Do not modify `skills/to-issues/`, `skills/triage/`, dispatch behavior, dependency files, `.groundwork/`, `.trellis`, `refer/`, or unrelated docs.
- Iteration Policy: Make one focused implementation pass; if validation fails because of these changes, make one narrow remediation and rerun the relevant check.
- Stop When: The linter prints `Goal Contract Lint: pass` for this fixture and `Goal Contract Lint: fail` for the negative fixture, and repository diff checks complete.
- Pause If: Required file locations conflict with existing repo conventions, validation tooling is missing, or the implementation would require remote writes or dependency installation.
- Non-goals: Do not implement dispatch, runtime adapters, task databases, hooks, or public skill behavior changes.
- Risk / Gate: The linter is intentionally lightweight and scans full Markdown text; structured block parsing is deferred.
- Preferred Runtime: codex_app_managed_worktree_thread
- Result Package Expected: review_package

```text
Fenced code blocks are included so the linter confirms it scans the full file.
```
