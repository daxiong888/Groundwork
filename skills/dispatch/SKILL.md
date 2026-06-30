---
name: dispatch
description: Route accepted, ready tasks to the lightest appropriate runtime by producing Dispatch Package v2 and Result Package expectations. Use for runtime selection, execution matrixes, model/reasoning profile recommendations, managed worktree vs subagent decisions, and package-only runtime handoff. Dispatch is a router/package generator, not an executor.
---

# dispatch

## Target Reader

Groundwork users, coordinator threads, runtime adapter authors, and implementation/review threads that need a runtime routing package.

## Reader Action Needed

Use this skill to classify accepted tasks, select runtime routes, and produce package-only instructions that another runtime may execute only after explicit execution approval and available tools.

## Decision Supported

Which runtime should handle each task, why that runtime is appropriate, what package it receives, what result package it must return, and which tasks must stop, split, or return to triage.

## Scope

This skill covers dispatch-time runtime routing for `codex_app_managed_worktree_thread`, `codex_subagent`, `main_thread_direct`, `main_thread_readonly`, and `clean_reviewer`.

Out of scope: calling Codex App thread tools, spawning subagents, executing runtime tools, writing remotes, destructive actions, committing, pushing, opening PRs, closing issues, or claiming runtime execution occurred.

## Trigger Contract

Use this skill when the user asks to:

- distribute ready-for-agent issues to agents or runtimes
- decide which tasks need managed worktrees and which should use subagents or reviewers
- assign model profile, reasoning effort, or cost/latency bias per task
- generate an execution matrix
- generate a dispatch package
- plan multi-perspective review without creating worktrees
- decide whether tasks can run in parallel
- prepare runtime-specific child prompts or package-only handoffs
- route managed-worktree closeout cleanup decisions, including archived thread with remaining temp branch, remote branch cleanup approval, and unmerged or uncertain branch retention
- decide branch cleanup state without deleting local or remote branches
- route clean-review coordinator intake packages, including fanout to `clean_reviewer` or read-only `codex_subagent`
- reject clean-review direct-edit requests and route required writes as a separate dispatch write task
- classify missing validation evidence, hidden parent context, parent full-history fork, or nested reviewer topology as `blocked`, `unverified`, `needs_remediation`, or `human_decision`

Do not use this skill when:

- requirements are not accepted; use `to-prd`
- issues are not sliced; use `to-issues`
- readiness is unknown; use `triage`
- the user asks which enumerable runtime, model-profile, skill-route, or workflow option to choose before there is an accepted ready package; use `skills/_shared/DECISION-MAPPING.md` as a shared lens, while keeping runtime capability evidence boundaries explicit
- the user asks to implement one scoped task directly; use `implement`
- the user only asks for an implementation plan; use `write-plan`
- the user asks whether finished work is ready or verified; use `verify`

## Required Behavior

When maintaining the Groundwork repository itself, apply the repo-local `AGENTS.md` Done Definition before reporting the work complete.

Use `skills/_shared/RUNTIME-CAPABILITY.md` before recommending, requesting, or reporting runtime/model selection. Dispatch must keep capability seed facts, prompt preferences, runtime/tool evidence, official docs, and community evidence separate.

When dispatch templates inline `evidence_layer` values, they mirror the canonical runtime evidence layer enum in `skills/_shared/RUNTIME-CAPABILITY.md` and must be updated together with that source.

Use `skills/_shared/COGNITIVE-BUDGET.md` for `model_profile`, reasoning/thinking preference, cost/latency bias, and Spark final authority restrictions. Route by profile before mapping to a concrete model.

Use `skills/_shared/DECISION-MAPPING.md` only for pre-dispatch option comparison when the user needs to choose among enumerable runtime, model-profile, skill-route, or workflow paths. Preserve `dispatch` when accepted, ready tasks need runtime routing, an execution matrix, model/profile recommendations, package-only handoff, or Result Package expectations. A decision map can recommend a dispatch path, but it must not generate or execute the dispatch package and must not claim selector enforcement beyond prompt preference without runtime/tool evidence.

Use `skills/_shared/LLM-WIKI.md` when accepted work has relevant project wiki context. Dispatch may include wiki pages in the source package as orientation or claim inventory, but must label them as non-authoritative and require the executing role to inspect cited source, contract, test, runtime, or release evidence before using the claim. A missing wiki must not block dispatch. Wiki context must not become runtime execution evidence, implementation evidence, verification evidence, clean review evidence, selector-enforcement evidence, UAT evidence, release evidence, marketplace evidence, installed-plugin evidence, or cache-refresh evidence. Dispatch may include a `Wiki Update Candidate` only when the ready package identifies durable reusable knowledge and wiki maintenance is not the current execution task.

`dispatch` must:

- confirm source truth, issue set, readiness source, and evidence level before routing
- classify each task as `write_implementation`, `read_only_review`, `planning_only`, `hybrid`, `diagnosis`, `verification`, or `direct`
- consume the Goal Contract when present and identify missing required Goal Contract fields
- assign exactly one `runtime_id` per routed task
- assign exactly one v0.4.0 route decision per routed task: `local_direct`, `local_with_artifact`, `worktree_isolated`, `worktree_review_only`, or `automation_candidate`
- emit the v0.4.0 dispatch surface under `dispatch_native_alignment`: route decision, policy, source package, handoff expectation, closeout expectation, verification expectation, approval requirements, and runtime evidence ownership
- assign isolation level, execution profile, validation expectation, and expected Result Package
- identify parallelization eligibility and conflict/dependency groups when enough evidence exists
- preserve the distinction between `runtime_policy.max_parallel_units` as the package-wide concurrency ceiling and `tasks[].parallelization.max_parallel_group_size` as the group-level ceiling; effective concurrency must not exceed either value
- route read-only and planning-only tasks away from `worktree_isolated` and managed worktree runtimes
- split hybrid work before any write worktree package is generated
- default write implementation tasks to managed worktree only when readiness, Goal Contract, `dispatch_native_alignment.source_package`, `dispatch_native_alignment.verification_expectation`, and a concrete `worktree_isolated` route justification are present
- mark v0.3.3 custom lifecycle, registry, child-thread identity, selector-enforcement, and background-run fields as legacy compatibility unless adapter/runtime evidence exists
- keep `automation_candidate` recommendation-only; do not create, update, schedule, or archive automations from dispatch
- stop before execution unless the user explicitly requests execution and the current runtime exposes the required tools
- report selector enforcement transparently: use `tool_enforced` only when the adapter confirms selector support; otherwise use `prompt_preference`, `unavailable`, or `unknown`
- add `capability_status` and `selector_enforcement` whenever runtime/model selection is material; do not claim `tool_enforced` from prompt text, Goal Contract text, Dispatch Package text, model menu seeds, or routing profiles alone
- report Runtime mismatch when requested runtime and available/proposed runtime differ; do not silently substitute subagents for child-thread/worktree runtimes or child-thread/worktree runtimes for subagents
- treat user-observed model menu seeds as dated `user_supplied` capability facts, not universal runtime truth
- avoid permanent global concrete model tables; concrete model mapping is evidence-bound and secondary to profile routing
- keep wiki pages, wiki summaries, wiki audits, and external graph/search/index output as orientation or claim inventory only unless separately backed by source, contract, test, runtime, or release evidence
- apply `skills/_shared/ROLE-SEPARATION.md` when routing material work: separate designer/planner, implementer, clean reviewer, verifier, and coordinator roles; do not route a same-session implementer as clean reviewer or final verifier for its own material change
- include role-separation closeout expectations for material tasks using `Role`, `Design Source`, `Self-check Evidence`, `Clean Review Evidence`, `Independent Verification Evidence`, `Runtime Evidence`, `Browser Evidence`, `UAT Evidence`, `Release Evidence`, `Readiness Boundary`, and `Required Next Independent Role`
- when a clean-review claim is blocked, unverified, invalid, inherited from parent context, or requires a future fresh reviewer, do not emit current-state fields such as `clean_review: passed`, `clean_review_passed: true`, or `Clean Review Evidence: passed`; use explicit missing/required/fresh-pass-required wording instead

## Hard Stop Before Execution

Dispatch is a router and package generator. It must not:

- call Codex App thread tools
- create or manage child threads
- spawn subagents
- execute package contents
- write files in target runtimes
- mutate remotes or external trackers
- claim that runtime execution, validation, or review happened

If the user asks dispatch to execute, output the dispatch package plus an execution gate:

```text
Proposed Action:
Target Runtime:
Required Tool Capability:
Risk:
Rollback/Undo:
Approval Needed:
```

Proceed only after explicit approval and tool availability are both confirmed.

## Output Shape

````text
Dispatch Runtime Decision

Dispatch Summary

Source Truth
- PRD:
- Issue Set:
- Readiness Source:
- Evidence Level:

Runtime Capability Check
- capability_status: known | unknown | user_supplied | docs_reference | tool_enforced
- selector_enforcement: tool_enforced | prompt_preference | unavailable | unknown
- Evidence layer: prompt_preference | runtime_tool_evidence | user_observed_model_menu_seed | official_docs | community_evidence | local_characterization_eval
- Available / assumed runtimes:
- Runtime selectors available:
- Subagent execution available:
- Worktree thread execution available:
- Requested runtime:
- Available runtime:
- Runtime mismatch: yes | no | unknown
- Fallback proposed:
- User approval required:

Task Matrix
| Task | Type | Readiness | Runtime | Isolation | Parallelization | Goal | Execution Profile | Validation | Result Package | Approval Needed |
|---|---|---|---|---|---|---|---|---|---|---|

No-Execution / Blocked / Needs Split
- Task:
- Reason:
- Required next action:

Runtime Packages
Must conform to `skills/dispatch/DISPATCH-PACKAGE.md`. Do not duplicate the package schema in `SKILL.md`. Load `skills/dispatch/EXAMPLES.md` only when an example package is useful for the active route.

Expected Result Package
- Runtime:
- Output Type:
- Required Evidence:
- Role:
- Design Source:
- Self-check Evidence:
- Clean Review Evidence:
- Independent Verification Evidence:
- Runtime Evidence:
- Browser Evidence:
- UAT Evidence:
- Release Evidence:
- Readiness Boundary:
- Required Next Independent Role:

Next Action
````

## Package References

- Runtime capabilities: `RUNTIME-ADAPTERS.md`
- Dispatch schema and routing rules: `DISPATCH-PACKAGE.md`
- Runtime package examples: `EXAMPLES.md`
- Unified result envelope: `RESULT-PACKAGE.md`
- Clean review fan-out: `CLEAN-REVIEW-FANOUT.md`
- Managed worktree internal adapter contract: `adapters/codex_app_managed_worktree_thread/ADAPTER.md`
