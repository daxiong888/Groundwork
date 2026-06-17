Target Reader: Groundwork implementers, maintainers, and follow-up Codex execution threads.
Reader Action Needed: Use this issue map to triage or plan implementation slices for the Dispatch Runtime Router PRD; do not treat it as a final Dispatch Package.
Decision Supported: Which slices can proceed independently, which slices must wait for upstream contracts, which historical external-adapter work has been superseded, and which verification evidence is required before closeout.
Scope: Issue decomposition for `docs/prd-dispatch-runtime-router.md`, covering Groundwork source preflight, Goal Contract, `to-issues`, `triage`, `dispatch`, subagent package contracts, internal managed worktree adapter contract expectations, and end-to-end docs/evals.
Out of Scope: Implementing the slices, calling tracker APIs, creating remote issues, committing files, executing runtime adapters, or dispatching child runtime work directly from this map.
Evidence Level: Derived from local PRD `docs/prd-dispatch-runtime-router.md`, current repository file inspection on 2026-06-16, and review notes supplied in `pasted-text.txt`.
Canonical Sources:
- `docs/prd-dispatch-runtime-router.md`
- `skills/to-issues/SKILL.md`
- `skills/triage/AGENT-BRIEF.md`
- `evals/prompts/to-issues.csv`
- `evals/prompts/triage.csv`
Source Status: `docs/prd-dispatch-runtime-router.md` is currently an untracked local file.

# Dispatch Runtime Router Issue Map

## Issue 集合摘要

本 issue map 将 `docs/prd-dispatch-runtime-router.md` 拆为 Groundwork 本地可推进的 v0 slice。它是 `to-issues` 层的 candidate map，不是最终 Dispatch Package；每个可执行 slice 在进入 `dispatch` 或 managed worktree 子线程前，还需要由 `triage` / `write-plan` 生成具体 Goal Contract。

推荐第一可执行 slice 是 Issue 1：Goal Contract shared spec + linter。Issue 4A/4B、Issue 5、Issue 7 不应在 Issue 1-3 稳定前并行启动。原 External A 单独仓库任务包已被内部 adapter contract 取代，当前 canonical adapter contract 是 `skills/dispatch/adapters/codex_app_managed_worktree_thread/ADAPTER.md`。

## Field Semantics

- Implementation Task Type Candidate: describes the work needed to implement this issue map slice.
- Implementation Runtime Candidate: describes the recommended runtime for executing this implementation slice.
- Product Runtime Covered: describes the runtime capability introduced, documented, or constrained by the slice.
- `codex_subagent` in Product Runtime Covered does not mean this issue itself must be executed by a subagent.
- Goal Contract Status: records whether this map already contains an executable Goal Contract. In this v0 map, it does not.
- Expected Result Package: describes the result envelope expected from the implementation runtime, not the product runtime being defined.

## 来源

- Canonical source: `docs/prd-dispatch-runtime-router.md`
- Requirement state: `prd_accepted` candidate, based on the explicit user request to split this PRD into issues.
- AC source: PRD section `# 8. Acceptance Criteria`, AC-1 through AC-15.
- Existing repo context: `skills/to-issues/SKILL.md`, `skills/triage/AGENT-BRIEF.md`, `evals/prompts/to-issues.csv`, and `evals/prompts/triage.csv` exist.
- Missing repo context observed before issue creation: `skills/dispatch/`, `scripts/lint_goal_contract.py`, and `skills/_shared/GOAL-CONTRACT.md` are not present.
- Public skill authorization: resolved for this workstream. The user confirmed on 2026-06-16 that `docs/prd-dispatch-runtime-router.md` is sufficient authorization and may override the repo-local "GitHub issue required" gate for `dispatch`.

## Issue 草案

### 0. Confirm / promote canonical PRD source

Goal: Resolve source-truth risk before multi-session or child-runtime execution uses this PRD and issue map.

Acceptance Criteria:
- Confirm `docs/prd-dispatch-runtime-router.md` is the accepted source for this workstream.
- If implementation spans sessions or child threads, ensure the PRD file is tracked or explicitly provided in the source package.
- Confirm this file is the canonical local issue map, not a transient planning note.
- Record that remote tracker IDs are not required for local implementation and should only be added before remote issue creation.

Evidence / Source:
- Current `git status --short` shows `docs/prd-dispatch-runtime-router.md` is untracked.
- This file is the promoted local issue map under `artifacts/dispatch-runtime-router/`.

Blockers:
- None for local planning. Implementation handoff or child-thread dispatch should not proceed until the source package includes both the PRD and this issue map.

Execution: AFK candidate.

Contract Impact: docs / source-truth / verification contract.

Expected Result Package: `review_package`

Files Expected To Touch:
- `docs/prd-dispatch-runtime-router.md`
- `artifacts/dispatch-runtime-router/issue-map.md`
- Optional tracker or source package references if remote issues are created later.

Verification Evidence Needed:
- `git status --short`
- PRD and issue map are both present in the intended source package for any follow-up execution thread.

Ready-for-Agent Missing Fields:
- None for local implementation. Stable remote issue ID is not required unless remote tracker issues are created.

Implementation Task Type Candidate: `write_implementation`

Implementation Runtime Candidate: `main_thread_direct`

Product Runtime Covered: `none`

Isolation Needed for implementation:
- context: `none`
- filesystem: `current_workspace`
- diff surface: `optional`

Parallelization Candidate:
- eligible: no
- conflict group: `source-truth-preflight`
- dependency group: none
- merge order hint: complete before dispatching implementation work.

Runtime Missing Fields:
- None.

Goal Contract Status:
- Not generated by this issue map.
- Must be generated by `triage` / `write-plan` before dispatch execution.

Triage Recommendation Candidate: `ready-for-agent candidate`

### 1. 新增 `GOAL-CONTRACT.md` 与 Goal Contract linter

Goal: 建立 Groundwork 共享的可执行目标合同规范，并提供最小 lint 工具，防止 `/goal`、验证、边界、暂停条件等字段缺失或空泛。

Acceptance Criteria:
- Covers PRD FR-7, FR-8, AC-9, and AC-10.
- Add `skills/_shared/GOAL-CONTRACT.md`.
- `GOAL-CONTRACT.md` defines `Goal Command`, `Outcome`, `Source Truth`, `Acceptance Criteria Mapping`, `Verification`, `Constraints`, `Boundaries`, `Iteration Policy`, `Stop When`, `Pause If`, `Non-goals`, `Risk / Gate`, `Preferred Runtime`, and `Result Package Expected`.
- Add `scripts/lint_goal_contract.py`.
- The linter accepts a Markdown file path and scans the full file for required labels and `/goal`.
- If fenced code blocks exist, the linter scans the full file instead of trying to parse block boundaries.
- Future structured parsing is out of scope.
- The linter fails on missing `/goal`, missing verification, missing constraints, missing boundaries, missing iteration policy, missing stop condition, missing pause condition, missing `Preferred Runtime`, and placeholders such as `TODO`, `TBD`, and `待定`.
- Chinese labels or Chinese content are supported without translating code identifiers or repo field names.
- Add at least one pass fixture and one fail fixture, or equivalent coverage in `evals/prompts/goal-contract.csv` or a scenario file.

Evidence / Source:
- PRD FR-7, FR-8.
- PRD Suggested Implementation Issue 1.
- PRD AC-9, AC-10.

Blockers:
- None for local implementation.

Execution: AFK candidate.

Contract Impact: docs / verification contract / scripts.

Expected Result Package: `review_package`

Files Expected To Touch:
- `skills/_shared/GOAL-CONTRACT.md`
- `scripts/lint_goal_contract.py`
- `evals/prompts/goal-contract.csv`
- Optional pass/fail fixture or scenario files.

Verification Evidence Needed:
- `python3 scripts/lint_goal_contract.py <pass-fixture>` prints `Goal Contract Lint: pass`.
- `python3 scripts/lint_goal_contract.py <fail-fixture>` prints `Goal Contract Lint: fail`.
- `git diff --check`
- CSV parse smoke if eval CSV files are added or changed.

Ready-for-Agent Missing Fields:
- Fixture paths should be chosen during implementation.
- Stable remote issue ID is not required for local implementation.

Implementation Task Type Candidate: `write_implementation`

Implementation Runtime Candidate: `codex_app_managed_worktree_thread`

Product Runtime Covered: `goal_contract`

Isolation Needed for implementation:
- context: `thread`
- filesystem: `codex_managed_worktree`
- diff surface: `required`

Parallelization Candidate:
- eligible: yes after file ownership is confirmed.
- conflict group: `goal-contract-core`
- dependency group: none
- merge order hint: execute before `triage`, `to-issues`, and `dispatch` contract changes.

Runtime Missing Fields:
- None for package generation; implementation still needs current repo checks.

Goal Contract Status:
- Not generated by this issue map.
- Must be generated by `triage` / `write-plan` before dispatch execution.

Triage Recommendation Candidate: `ready-for-agent candidate`

### 2. 扩展 `to-issues` 输出 runtime candidate / isolation / parallelization 字段

Goal: Let `to-issues` emit runtime candidate, isolation, and parallelization fields while preserving its non-final readiness boundary.

Acceptance Criteria:
- Covers PRD FR-10 and the upstream classification behavior required by AC-3, AC-4, AC-5, and AC-6.
- Update `skills/to-issues/SKILL.md`.
- Update `evals/prompts/to-issues.csv`.
- Each issue draft can include `Implementation Task Type Candidate`, `Implementation Runtime Candidate`, `Product Runtime Covered`, `Isolation Needed`, `Parallelization Candidate`, `Goal Contract Status`, `Runtime Missing Fields`, and `Verification Evidence Needed`.
- `read_only_review` must not suggest `codex_app_managed_worktree_thread` as the product route.
- `planning_only` must not suggest `codex_app_managed_worktree_thread` as the product route.
- `hybrid` must suggest split first or `triage_required`.
- `write_implementation` may suggest `codex_app_managed_worktree_thread` only when source context and verification expectations are clear.
- `to-issues` still does not final-mark `ready-for-agent`.

Evidence / Source:
- PRD FR-10.
- PRD Suggested Implementation Issue 3.
- PRD AC-3 through AC-6.

Blockers:
- Depends on Issue 1 for shared Goal Contract field names.
- Need to confirm whether the current eval runner validates text expectations only or enforces a structured schema.

Execution: AFK candidate after Issue 1.

Contract Impact: docs / verification contract / evals.

Expected Result Package: `review_package`

Files Expected To Touch:
- `skills/to-issues/SKILL.md`
- `evals/prompts/to-issues.csv`

Verification Evidence Needed:
- `python3 -c "import csv, pathlib; [list(csv.DictReader(open(p, newline=''))) for p in pathlib.Path('evals/prompts').glob('*.csv')]; print('csv ok')"`
- Targeted coverage for `evals/prompts/to-issues.csv`.
- `git diff --check`

Ready-for-Agent Missing Fields:
- Stable remote issue ID is not required for local implementation.
- Structured schema expectations, if any, must be confirmed from the runtime runner before final verification.

Implementation Task Type Candidate: `write_implementation`

Implementation Runtime Candidate: `codex_app_managed_worktree_thread`

Product Runtime Covered: `to_issues_runtime_candidates`

Isolation Needed for implementation:
- context: `thread`
- filesystem: `codex_managed_worktree`
- diff surface: `required`

Parallelization Candidate:
- eligible: yes after Issue 1 establishes shared field names.
- conflict group: `issue-output-contract`
- dependency group: `goal-contract-core`
- merge order hint: can run near Issue 3 if field names are coordinated.

Runtime Missing Fields:
- Runtime enum naming should match the future `dispatch` contract.

Goal Contract Status:
- Not generated by this issue map.
- Must be generated by `triage` / `write-plan` before dispatch execution.

Triage Recommendation Candidate: `ready-for-agent candidate`

### 3. 扩展 `triage` Agent Brief，生成 Goal Contract 与 Preferred Runtime recommendation

Goal: Make `triage` produce a Goal Contract and execution profile recommendation for `ready-for-agent + AFK` tasks, without emitting fake executable child goals for `needs-info`, `ready-for-human`, or HITL-only tasks.

Acceptance Criteria:
- Covers PRD FR-9, AC-5, AC-9, AC-10, and AC-12.
- Update `skills/triage/AGENT-BRIEF.md`.
- Update `skills/triage/SKILL.md`.
- Update `evals/prompts/triage.csv`.
- `ready-for-agent + AFK` includes Goal Contract fields.
- `needs-info` and `ready-for-human` do not include executable child goals.
- HITL tasks may include a human-decision brief, not a dispatchable child goal.
- `Pause If` maps to AFK/HITL decision points.
- `Preferred Runtime` is a recommendation only; `dispatch` makes the final route.
- `triage` must not claim selector enforcement; it may only recommend execution profile preferences.

Evidence / Source:
- PRD FR-9.
- PRD Suggested Implementation Issue 2.
- PRD AC-9, AC-10, AC-12.

Blockers:
- Depends on Issue 1 for the canonical Goal Contract field set.
- Must preserve the existing `triage` readiness gate.

Execution: AFK candidate after Issue 1.

Contract Impact: docs / verification contract / evals.

Expected Result Package: `review_package`

Files Expected To Touch:
- `skills/triage/AGENT-BRIEF.md`
- `skills/triage/SKILL.md`
- `evals/prompts/triage.csv`

Verification Evidence Needed:
- Targeted coverage for `evals/prompts/triage.csv`.
- CSV parse smoke.
- `git diff --check`

Ready-for-Agent Missing Fields:
- Stable remote issue ID is not required for local implementation.
- Execution profile values should remain abstract unless the runtime exposes concrete model/profile selectors.

Implementation Task Type Candidate: `write_implementation`

Implementation Runtime Candidate: `codex_app_managed_worktree_thread`

Product Runtime Covered: `triage_goal_contract`

Isolation Needed for implementation:
- context: `thread`
- filesystem: `codex_managed_worktree`
- diff surface: `required`

Parallelization Candidate:
- eligible: yes after Issue 1.
- conflict group: `triage-agent-brief`
- dependency group: `goal-contract-core`
- merge order hint: coordinate with Issue 2 to keep field names consistent.

Runtime Missing Fields:
- Concrete selector enforcement is runtime-dependent and should not be claimed by `triage`.

Goal Contract Status:
- Not generated by this issue map.
- Must be generated by `triage` / `write-plan` before dispatch execution.

Triage Recommendation Candidate: `ready-for-agent candidate`

### 4A. 新增 `dispatch` skill skeleton 与核心 runtime/package/result contracts

Goal: Add the first-cut `dispatch` public skill skeleton and core runtime/package/result contracts without adding advanced routing profile or conflict preflight coverage yet.

Acceptance Criteria:
- Covers the core of PRD FR-1, FR-2, FR-3, FR-4, AC-1, AC-3, AC-4, AC-5, AC-6, AC-9, AC-13, and AC-14.
- Add `skills/dispatch/SKILL.md`.
- Add `skills/dispatch/RUNTIME-ADAPTERS.md`.
- Add `skills/dispatch/DISPATCH-PACKAGE.md`.
- Add `skills/dispatch/RESULT-PACKAGE.md`.
- Add minimal `evals/prompts/dispatch.csv` coverage for explicit invocation, adjacent false-positive, and package-only no-execution behavior.
- `dispatch` assigns `runtime_id` per task and does not assume all tasks use `codex_app_managed_worktree_thread`.
- `dispatch` can represent `codex_app_managed_worktree_thread`, `codex_subagent`, `main_thread_direct`, `main_thread_readonly`, and `clean_reviewer`.
- `dispatch` outputs Dispatch Package v2 and Result Package expectations.
- `dispatch` does not call Codex App thread tools, automatically spawn subagents, write remotes, or execute runtime tools.
- `.codex-plugin/plugin.json` is inspected before deciding whether public skill exposure requires metadata changes.

Evidence / Source:
- PRD FR-1 through FR-4.
- PRD Suggested Implementation Issue 4.
- PRD AC-1, AC-3, AC-4, AC-5, AC-6, AC-9, AC-13, AC-14.
- User confirmation on 2026-06-16 that the PRD may authorize the new public skill.

Blockers:
- Depends on Issues 1 through 3 so `dispatch` can consume stable upstream fields.

Execution: AFK candidate after Issues 1 through 3.

Contract Impact: docs / verification contract / evals / public skill surface.

Expected Result Package: `review_package`

Files Expected To Touch:
- `skills/dispatch/SKILL.md`
- `skills/dispatch/RUNTIME-ADAPTERS.md`
- `skills/dispatch/DISPATCH-PACKAGE.md`
- `skills/dispatch/RESULT-PACKAGE.md`
- `evals/prompts/dispatch.csv`
- `.codex-plugin/plugin.json` only if inspection proves metadata exposure is required.

Verification Evidence Needed:
- `python3 -m json.tool .codex-plugin/plugin.json >/dev/null`
- CSV parse smoke.
- Targeted dispatch eval.
- `git diff --check`
- Manual inspection that `dispatch` stops before runtime execution.

Ready-for-Agent Missing Fields:
- Whether `.codex-plugin/plugin.json` needs to expose the new public skill must be confirmed from plugin structure during implementation.
- Runtime selector enforcement can only be claimed when the runtime confirms tool support.

Implementation Task Type Candidate: `write_implementation`

Implementation Runtime Candidate: `codex_app_managed_worktree_thread`

Product Runtime Covered: `dispatch_core`

Isolation Needed for implementation:
- context: `thread`
- filesystem: `codex_managed_worktree`
- diff surface: `required`

Parallelization Candidate:
- eligible: no until Issues 1 through 3 establish stable inputs.
- conflict group: `dispatch-public-skill`
- dependency group: `goal-contract-core`, `issue-output-contract`, `triage-agent-brief`
- merge order hint: implement after upstream contract fields stabilize.

Runtime Missing Fields:
- Public skill exposure and selector-enforcement reporting require repo inspection during implementation.

Goal Contract Status:
- Not generated by this issue map.
- Must be generated by `triage` / `write-plan` before dispatch execution.

Triage Recommendation Candidate: `ready-for-agent candidate`

### 4B. 新增 dispatch routing profiles、conflict preflight 与 scenario coverage

Goal: Extend the dispatch skeleton with routing profile defaults, conflict preflight rules, and scenario coverage after the core contracts exist.

Acceptance Criteria:
- Covers PRD FR-5, FR-6, AC-11, AC-12, and the scenario foundation for AC-15.
- Add `skills/dispatch/ROUTING-PROFILES.md`.
- Add `skills/dispatch/CONFLICT-PREFLIGHT.md`.
- Expand `evals/prompts/dispatch.csv` for routing profiles, selector transparency, and conflict grouping.
- Add `evals/scenarios/groundwork-runtime-router.md`.
- Conflict preflight groups likely shared-file, API, DB, schema, generated-artifact, fixture, public type, state machine, and shared config conflicts.
- Same conflict group must not be parallelized as write tasks by default.

Evidence / Source:
- PRD FR-5, FR-6.
- PRD AC-11, AC-12, AC-15.

Blockers:
- Depends on Issue 4A.
- Should not run in parallel with Issue 5 if both touch `skills/dispatch/*` contracts.

Execution: AFK candidate after Issue 4A.

Contract Impact: docs / verification contract / evals.

Expected Result Package: `review_package`

Files Expected To Touch:
- `skills/dispatch/ROUTING-PROFILES.md`
- `skills/dispatch/CONFLICT-PREFLIGHT.md`
- `evals/prompts/dispatch.csv`
- `evals/scenarios/groundwork-runtime-router.md`

Verification Evidence Needed:
- CSV parse smoke.
- Targeted dispatch eval.
- Scenario smoke if supported by the runner.
- `git diff --check`

Ready-for-Agent Missing Fields:
- Stable remote issue ID is not required for local implementation.

Implementation Task Type Candidate: `write_implementation`

Implementation Runtime Candidate: `codex_app_managed_worktree_thread`

Product Runtime Covered: `dispatch_routing_profiles`

Isolation Needed for implementation:
- context: `thread`
- filesystem: `codex_managed_worktree`
- diff surface: `required`

Parallelization Candidate:
- eligible: no with Issue 5.
- conflict group: `dispatch-runtime-contracts`
- dependency group: `dispatch-public-skill`
- merge order hint: implement after Issue 4A.

Runtime Missing Fields:
- Concrete selector enforcement remains runtime-dependent.

Goal Contract Status:
- Not generated by this issue map.
- Must be generated by `triage` / `write-plan` before dispatch execution.

Triage Recommendation Candidate: `ready-for-agent candidate`

### 5. 增加 `codex_subagent` package-only route 与 capability gate

Goal: Represent `codex_subagent` as a supported dispatch runtime route while keeping Phase 1 package-only and capability-gated.

Acceptance Criteria:
- Covers PRD FR-12, AC-7, AC-8, AC-14, and the subagent route in AC-15.
- `skills/dispatch/RUNTIME-ADAPTERS.md` defines the `codex_subagent` capability profile.
- `skills/dispatch/DISPATCH-PACKAGE.md` includes a `subagent_package` schema.
- `skills/dispatch/RESULT-PACKAGE.md` defines subagent result output as `findings_package` or `diagnosis_package`.
- Add `evals/scenarios/subagent-readonly-review.md` or equivalent scenario coverage.
- `can_write_files` defaults to false.
- The package is self-contained and role-specific.
- Subagent execution requires capability detection and explicit execution request or approval.
- `dispatch` must not claim subagent execution happened when it only produced a package.

Evidence / Source:
- PRD FR-12.
- PRD Suggested Implementation Issue 6.
- PRD AC-7, AC-8, AC-14.

Blockers:
- Depends on Issue 4A.
- Must avoid making subagent writes a default capability.
- Must not run in parallel with Issue 4B if both touch the same dispatch contracts.

Execution: AFK candidate after Issue 4A, or merge into Issue 4B if maintainers prefer fewer slices.

Contract Impact: docs / verification contract / evals.

Expected Result Package: `review_package`

Files Expected To Touch:
- `skills/dispatch/RUNTIME-ADAPTERS.md`
- `skills/dispatch/DISPATCH-PACKAGE.md`
- `skills/dispatch/RESULT-PACKAGE.md`
- `evals/scenarios/subagent-readonly-review.md`
- Optional dispatch eval rows for subagent package-only behavior.

Verification Evidence Needed:
- Targeted dispatch coverage for read-only review routing.
- Manual inspection that `can_write_files` defaults false.
- `git diff --check`

Ready-for-Agent Missing Fields:
- No concrete local subagent execution API is specified. Phase 1 should record this as package-only.

Implementation Task Type Candidate: `write_implementation`

Implementation Runtime Candidate: `codex_app_managed_worktree_thread`

Product Runtime Covered: `codex_subagent`

Isolation Needed for implementation:
- context: `thread`
- filesystem: `codex_managed_worktree`
- diff surface: `required`

Runtime Behavior Being Specified:
- context: `subagent_prompt`
- filesystem: `none_or_tool_dependent`
- can_write_files: false by default
- output: `findings_package` / `diagnosis_package`

Parallelization Candidate:
- eligible: no with Issue 4B.
- conflict group: `dispatch-runtime-contracts`
- dependency group: `dispatch-public-skill`
- merge order hint: implement after Issue 4A, or fold into Issue 4B.

Runtime Missing Fields:
- Subagent capability detection remains runtime-dependent.

Goal Contract Status:
- Not generated by this issue map.
- Must be generated by `triage` / `write-plan` before dispatch execution.

Triage Recommendation Candidate: `ready-for-agent candidate` after Issue 4A; otherwise `needs-info recommendation`.

### 6A. Document managed worktree adapter expectations in Groundwork dispatch contracts

Goal: Maintain the Groundwork-side internal contract for the `codex_app_managed_worktree_thread` runtime adapter without making it a public skill or default runtime executor.

Acceptance Criteria:
- Covers the Groundwork-side parts of PRD FR-11, AC-2, AC-5, AC-9, AC-13, and AC-14.
- Groundwork dispatch contracts state that `codex_app_managed_worktree_thread` packages require `task_type = write_implementation`, `readiness = ready_for_agent`, `isolation.filesystem = codex_managed_worktree`, present Goal Contract, present source package, present validation package, and `expected_output = review_package`.
- Groundwork dispatch contracts state that read-only, planning-only, hybrid, non-managed-runtime, missing Goal Contract, missing source package, missing validation, or non-review-package inputs must not be sent as managed worktree packages.
- Groundwork docs clearly state that adapter contract mechanics live under `skills/dispatch/adapters/codex_app_managed_worktree_thread/`, while runtime execution remains gated and non-default.

Evidence / Source:
- PRD FR-11.
- PRD AC-2, AC-5, AC-9, AC-13, AC-14.

Blockers:
- Depends on Issue 4A's Dispatch Package contract.

Execution: AFK candidate after Issue 4A.

Contract Impact: docs / runtime adapter contract / verification contract.

Expected Result Package: `review_package`

Files Expected To Touch:
- `skills/dispatch/RUNTIME-ADAPTERS.md`
- `skills/dispatch/DISPATCH-PACKAGE.md`
- `skills/dispatch/RESULT-PACKAGE.md`
- Optional workflow docs that reference adapter responsibilities.

Verification Evidence Needed:
- Manual inspection that Groundwork does not claim to execute or own adapter mechanics.
- Targeted dispatch eval or scenario rows for managed worktree package rejection/no-op conditions, if supported.
- `git diff --check`

Ready-for-Agent Missing Fields:
- Stable remote issue ID is not required for local implementation.

Implementation Task Type Candidate: `write_implementation`

Implementation Runtime Candidate: `codex_app_managed_worktree_thread`

Product Runtime Covered: `codex_app_managed_worktree_thread`

Isolation Needed for implementation:
- context: `thread`
- filesystem: `codex_managed_worktree`
- diff surface: `required`

Parallelization Candidate:
- eligible: no with Issue 4A or Issue 5 if they touch the same dispatch contracts.
- conflict group: `dispatch-runtime-contracts`
- dependency group: `dispatch-public-skill`
- merge order hint: implement after Issue 4A.

Runtime Missing Fields:
- Runtime execution implementation remains outside `dispatch`; the adapter contract source now lives under `skills/dispatch/adapters/codex_app_managed_worktree_thread/`.

Goal Contract Status:
- Not generated by this issue map.
- Must be generated by `triage` / `write-plan` before dispatch execution.

Triage Recommendation Candidate: `ready-for-agent candidate` after Issue 4A.

### Superseded External A. Slim `codex-managed-worktree-threads` into managed worktree adapter

The earlier External A task package is superseded by the internal adapter contract:

- Superseded task package: `artifacts/dispatch-runtime-router/external-a-managed-worktree-adapter.md`
- Current canonical adapter contract: `skills/dispatch/adapters/codex_app_managed_worktree_thread/ADAPTER.md`
- Groundwork local queue status: internal contract co-located under `dispatch`
- Groundwork execution rule: do not treat this as runtime execution; `dispatch` remains package-only
- Source coverage: PRD FR-11, AC-2, AC-5, AC-9, AC-13, and AC-14

This issue map keeps this section only as historical context. New work should use the internal adapter contract path above and must preserve the no-execution boundary unless an execution-capable runtime adapter is explicitly approved.

### 7. 端到端 workflow 文档与 scenario eval

Goal: Document and verify the complete `to-prd -> to-issues -> triage -> dispatch -> runtime adapter -> verify/triage` flow.

Acceptance Criteria:
- Covers PRD AC-15 and Suggested Implementation Issue 7.
- Add or update `docs/runtime-dispatch-workflow.md`.
- Add or update `evals/scenarios/groundwork-to-runtime-dispatch.md`.
- Update `README.md` only if maintainers decide the new public workflow should be surfaced there.
- Include examples for write implementation, read-only review, hybrid diagnosis, and high-risk migration.
- Show how results return to `verify` and `triage`.
- State Phase 1 boundaries: no automatic subagent spawn, no thread tool execution by Groundwork dispatch, and no remote writes.
- It may reference the internal managed worktree adapter contract without implying runtime execution.

Evidence / Source:
- PRD Suggested Implementation Issue 7.
- PRD AC-15.
- PRD Final Product Decision.

Blockers:
- Depends on stable fields from Issues 1 through 5.
- Managed worktree adapter execution remains gated and non-default; the internal contract path is the current source for package and result expectations.

Execution: AFK candidate after core contracts.

Contract Impact: docs / eval scenario / verification contract.

Expected Result Package: `review_package`

Files Expected To Touch:
- `docs/runtime-dispatch-workflow.md`
- `evals/scenarios/groundwork-to-runtime-dispatch.md`
- `README.md` only if maintainers decide it should surface the workflow.

Verification Evidence Needed:
- Stale-state pass over changed docs for unresolved markers: `TODO`, `TBD`, `待定`, `待确认`, `open question`, and `NEEDS CLARIFICATION`.
- CSV or scenario parse smoke if supported.
- `git diff --check`

Ready-for-Agent Missing Fields:
- Whether `README.md` should be updated is a maintainer decision.
- Whether the end-to-end scenario should enter a default eval suite is unresolved.

Implementation Task Type Candidate: `write_implementation`

Implementation Runtime Candidate: `codex_app_managed_worktree_thread`

Product Runtime Covered: `end_to_end_dispatch_workflow`

Isolation Needed for implementation:
- context: `thread`
- filesystem: `codex_managed_worktree`
- diff surface: `required`

Parallelization Candidate:
- eligible: no until core contracts are stable.
- conflict group: `workflow-docs-and-scenario`
- dependency group: `goal-contract-core`, `issue-output-contract`, `triage-agent-brief`, `dispatch-public-skill`
- merge order hint: implement after Issues 1 through 5.

Runtime Missing Fields:
- Default-suite promotion decision is not specified by the PRD.

Goal Contract Status:
- Not generated by this issue map.
- Must be generated by `triage` / `write-plan` before dispatch execution.

Triage Recommendation Candidate: `ready-for-agent candidate` after Issues 1 through 5.

## Ordering Notes

Recommended implementation order:

1. Issue 0: Confirm or promote source truth for the PRD and issue map.
2. Issue 1: Establish Goal Contract and linter.
3. Issue 2 and Issue 3: Extend `to-issues` and `triage`; these can run near each other if field names are coordinated.
4. Issue 4A: Add `dispatch` skeleton and core runtime/package/result contracts.
5. Issue 4B: Add routing profiles, conflict preflight, dispatch eval rows, and scenario coverage.
6. Issue 5: Add the package-only `codex_subagent` route, either folded into Issue 4B or executed strictly after Issue 4A.
7. Issue 6A: Document managed worktree adapter expectations on the Groundwork side.
8. Issue 7: Add end-to-end workflow documentation and scenario coverage.
9. Superseded External A: historical separate-repository plan; current contract lives under `skills/dispatch/adapters/codex_app_managed_worktree_thread/`.

Do not parallelize Issue 4B, Issue 5, Issue 6A, or Issue 7 until the core dispatch contracts are stable. Do not treat the superseded External A artifact as a current Groundwork managed worktree dispatch package.

## Artifact Recommendation

Use this file as the canonical local issue map for the dispatch runtime router workstream. Before remote issue creation or child-thread dispatch, include `docs/prd-dispatch-runtime-router.md` and this issue map in the source package. Stable remote issue IDs are not required for local implementation.
