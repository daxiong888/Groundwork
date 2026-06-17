# Runtime Dispatch Workflow

Target Reader: Groundwork coordinators, dispatch reviewers, and runtime adapter authors.
Reader Action Needed: Use this workflow to move accepted work from PRD slicing through runtime routing and back into verification or lifecycle triage.
Decision Supported: Whether a task should route through `dispatch`, which runtime package shape is valid, and how runtime results return to Groundwork.
Scope: End-to-end `to-prd -> to-issues -> triage -> dispatch -> runtime adapter -> verify/triage` workflow for Phase 1 dispatch.
Out of Scope: Automatic subagent spawning, Codex App thread tool execution by Groundwork dispatch, remote writes, runtime execution implementation, tracker APIs, and README exposure.
Evidence Level: Derived from `docs/prd-dispatch-runtime-router.md`, `artifacts/dispatch-runtime-router/issue-map.md`, and the dispatch contract files under `skills/dispatch/`.

## Workflow

```mermaid
flowchart LR
  A["to-prd<br/>accepted source truth"] --> B["to-issues<br/>vertical work units"]
  B --> C["triage<br/>readiness and Goal Contract"]
  C --> D["dispatch<br/>router and package generator"]
  D --> E["runtime adapter<br/>executes only if approved and supported"]
  E --> F["Result Package<br/>evidence envelope"]
  F --> G["verify<br/>acceptance evidence review"]
  F --> H["triage<br/>lifecycle state decision"]
  G --> H
```

`dispatch` is the routing boundary. It consumes accepted, ready task inputs and produces Dispatch Package v2 plus expected Result Package requirements. It does not execute the package.

## Phase 1 Boundaries

> [!IMPORTANT]
> Phase 1 dispatch is package-only. Groundwork `dispatch` must not automatically spawn subagents, must not call Codex App thread tools, and must not perform remote writes.

- No automatic subagent spawn: `codex_subagent` packages remain package-only unless an execution-capable runtime is explicitly requested, approved, and evidenced.
- No thread tool execution by Groundwork dispatch: creating managed worktree child threads, inserting child prompts, lifecycle monitoring, and selector enforcement belong to an execution-capable runtime adapter. Groundwork includes the internal adapter contract and templates under `skills/dispatch/adapters/codex_app_managed_worktree_thread/`.
- No remote writes: commits, pushes, PR creation, tracker mutation, deployment, or data writes require a separate explicit approval gate and runtime evidence.
- No execution claims from package generation: `dispatch` may state routing intent, package completeness, and expected output only.
- Internal adapter contract boundary: Groundwork co-locates the managed worktree adapter contract with dispatch, but `dispatch` remains package-only unless an execution-capable runtime is explicitly requested, approved, and evidenced.

## Inputs And Gates

1. `to-prd` establishes accepted source truth.
2. `to-issues` turns accepted source truth into vertical work units with acceptance criteria, non-goals, blockers, verification evidence, AFK/HITL classification, and runtime candidate fields.
3. `triage` decides whether the work is `ready_for_agent`, `ready_for_human`, `needs_info`, or blocked. Ready agent work may include a Goal Contract and Preferred Runtime recommendation.
4. `dispatch` makes the final runtime route. Preferred Runtime is an input signal, not an execution command.
5. Runtime adapters return a Result Package. Groundwork uses that evidence for `verify` and the lifecycle decision in `triage`.

## Runtime Examples

### Write Implementation

- Task type: `write_implementation`
- Readiness: `ready_for_agent`
- Runtime: `codex_app_managed_worktree_thread`
- Required package: complete Goal Contract, source package, validation package, `isolation.filesystem = codex_managed_worktree`, and `runtime_package.expected_output = review_package`
- Result returns as: `review_package`
- Next Groundwork route: `verify` checks acceptance evidence, then `triage` records `ready_for_clean_review`, `needs_remediation`, `blocked`, or the next lifecycle state.

This route is for concrete write work that needs isolated filesystem state, durable diff review, and validation evidence. Groundwork dispatch may request model or reasoning preferences, but selector enforcement is evidence only when the runtime adapter confirms it.

### Read-Only Review

- Task type: `read_only_review`
- Runtime: `codex_subagent`, `main_thread_readonly`, or `clean_reviewer`
- Required package: self-contained review scope, evidence targets, constraints, expected findings schema, stop condition, and pause condition
- Result returns as: `findings_package` or `review_findings`
- Next Groundwork route: `triage` decides whether findings create a write task, require human decision, or are complete; `verify` is used only when acceptance evidence needs review.

Read-only review must not route to `codex_app_managed_worktree_thread` because no durable write diff is required.

### Hybrid Diagnosis

- Task type: `hybrid`
- Runtime: split first
- Required package: diagnosis package for the read-only portion, followed by a separate write implementation package only after the diagnosis identifies a concrete fix
- Result returns as: `diagnosis_package` first; optional later `review_package` for the split write task
- Next Groundwork route: `triage` decides whether to dispatch a write subtask, ask for human decision, or stop as blocked.

Hybrid work must not be coerced into a managed worktree package before the write subtask exists.

### High-Risk Migration

- Task type: `write_implementation`
- Runtime: `codex_app_managed_worktree_thread`
- Required package: complete Goal Contract, high reasoning request, conflict preflight, serialized merge order, validation package, rollback or stop condition, and no remote-write authorization unless separately approved
- Result returns as: `review_package`
- Next Groundwork route: `verify` reviews migration acceptance and evidence gaps; `triage` decides whether the result is ready for clean review, needs remediation, blocked, or requires human decision.

High-risk migration can use managed worktree isolation, but dispatch must still serialize conflicting files and keep remote writes disabled.

## Result Return Path

Runtime output must be wrapped in the unified Result Package envelope:

- `review_package` from managed worktree write implementation routes to `verify` first when acceptance evidence is material.
- `findings_package` and `diagnosis_package` route to `triage` when the decision is whether to split, block, continue investigation, or create a write task.
- `review_findings` routes to `triage` for remediation decisions or to `verify` when evidence sufficiency is the question.
- `direct_result` may route to `triage` or finish when no additional evidence review is needed.

`verify` owns evidence sufficiency. `triage` owns lifecycle state and next-route decisions. Neither should treat package generation as runtime execution.
