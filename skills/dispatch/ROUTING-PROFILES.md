# Dispatch Routing Profiles

## Target Reader

Groundwork dispatch users, coordinator threads, runtime adapter authors, and reviewers checking why a task was routed to a runtime.

## Reader Action Needed

Choose the lightest appropriate runtime, execution profile, and selector request policy before generating Dispatch Package v2.

## Decision Supported

Whether a task should run in the main thread, managed worktree thread, subagent, or clean-review path, and which model/reasoning profile should be requested.

## Scope

Default routing and execution profile recommendations. This document does not execute tools, prove runtime availability, or guarantee selector enforcement.

## Out of Scope

Calling thread tools, spawning subagents, creating worktrees, mutating remotes/trackers/data/runtime state, or claiming selectors were applied.

## Artifact Type

Dispatch routing reference.

## Source of Truth

`skills/dispatch/RUNTIME-ADAPTERS.md`, `skills/_shared/COGNITIVE-BUDGET.md`, `skills/_shared/RUNTIME-CAPABILITY.md`, and `skills/_shared/REVIEW-LOOP.md`.

## Evidence Level

Source-validation routing guidance only; runtime availability and selector application require adapter/tool evidence.

## Safe to Share / Redaction Notes

Safe to share as-is; generated packages still require source and payload redaction.

## Routing Table

| Task Shape | Default Runtime | Reason |
| --- | --- | --- |
| Tiny answer/edit | `main_thread_direct` | Runtime overhead not justified. |
| Accepted independent write issue | `codex_app_managed_worktree_thread` | Needs isolation, durable diff, validation evidence, review package. |
| Accepted dependent write issue | serialize until barrier release | Needs prerequisite merge-back, base refresh, refreshed Goal Contract. |
| High-risk schema/API/migration/security/data write | managed worktree plus fresh clean review | Needs isolated write and independent review. |
| Complex role-separated work | role-separated route | Planner, implementer, clean reviewer, verifier, coordinator boundaries. |
| Read-only multi-perspective review/exploration/diagnosis | `codex_subagent` or `clean_reviewer` | Needs context or role isolation without writes. |
| Planning/critique/decision support | `main_thread_readonly` or `codex_subagent` | No file edits expected. |
| Completed package review | `clean_reviewer` | Result/review package is source under inspection. |
| Shared-file/conflict work | serialize or ask approval | Do not parallelize conflicting writes by default. |

## Execution Profile Defaults

| Task Shape | Model Profile | Reasoning | Bias |
| --- | --- | --- | --- |
| tiny direct/doc/config | `fast_scan` | low | fast |
| normal clear feature | `balanced_work` | medium | balanced |
| cross-cutting, migration, schema, API, security | `strong_reasoning` | high | quality |
| independent high-risk review | `exhaustive_review` | high or xhigh when available | quality |
| bounded exploration/diagnosis | `fast_scan` or `balanced_work` | low or medium | fast or balanced |

`skills/_shared/COGNITIVE-BUDGET.md` owns the allowed `model_profile`, `reasoning_effort`, and `cost_latency_bias` values. Each task adds `routing_reason`, connecting task shape, risk, source truth, and validation expectation to the requested profile.

## Selector Request And Evidence

Dispatch records a request-side `selector_policy`; it does not predeclare execution. Result packages use the canonical `selector_enforcement` evidence status from `skills/_shared/RUNTIME-CAPABILITY.md`. Package preferences such as "strongest available" are not enforcement proof.

## Write Routing Defaults

Default write work to managed worktree only when accepted write source, readiness evidence, source package, complete Goal Contract, validation package, and released conflict/dependency barrier are present. Otherwise return `needs_info`, `needs_split`, `main_thread_readonly`, serialization, or human decision.

Fresh role separation is required when `skills/_shared/REVIEW-LOOP.md` says materiality or fan-out triggers apply. Implementer self-check is not clean review.

## Read-only / Hybrid / Conflict Defaults

Read-only review, critique, exploration, and planning must not default to managed worktree. Use `codex_subagent`, `main_thread_readonly`, or `clean_reviewer` based on evidence need.

Hybrid work splits first: diagnose via subagent/read-only route, require a concrete write subtask with source truth/AC/boundaries/validation, then run conflict preflight.

Independent writes may run in parallel only when no dependency barrier, overlapping write surface, shared conflict group, stale base, or merge-order hint applies. Dependent/conflicting writes serialize or require explicit approval. Read-only preparation may run in parallel only when it cannot write and does not treat unmerged child work as source truth.
