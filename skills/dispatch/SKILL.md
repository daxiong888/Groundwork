---
name: dispatch
description: Use when routing accepted, ready tasks to the lightest appropriate runtime by producing Dispatch Package v2 and Result Package expectations. Use for runtime selection, execution matrixes, model/reasoning profile recommendations, managed worktree vs subagent decisions, and package-only runtime handoff. Do not use when requirements are not accepted, readiness is unknown, the user asks to implement directly, or the user asks for verification.
---

# dispatch

## Use When

Use this skill when accepted, ready work needs package-only runtime routing.

Examples:

- distribute ready-for-agent issues to agents or runtimes
- choose managed worktree vs subagent vs read-only reviewer
- assign model profile, reasoning effort, or cost/latency bias
- generate an execution matrix, Dispatch Package v2, or runtime-specific child prompt
- plan clean-review fanout without creating worktrees
- classify cleanup, hidden parent context, missing validation, or nested reviewer topology as blocked/unverified/remediation/human-decision

## Do Not Use When

- Requirements are not accepted; use `to-prd`.
- Issues are not sliced; use `to-issues`.
- Readiness is unknown; use `triage`.
- The user asks to implement one scoped task directly; use `implement`.
- The user only asks for an implementation plan; use `write-plan`.
- The user asks whether finished work is ready or verified; use `verify`.
- The user asks which option to choose before accepted ready work exists; use `skills/_shared/DECISION-MAPPING.md` as a shared lens.

## Runtime Mode Router

Dispatch is a router and package generator, not an executor.

- `lite matrix`: for small accepted task sets where the user needs a runtime recommendation and no full package. Emit source truth, runtime capability boundary, task matrix, blocked/split items, expected result package, and next action.
- `full dispatch package`: for worktree/subagent/runtime execution handoff. Load `DISPATCH-PACKAGE.md`; include source package, validation expectation, approval requirements, runtime evidence ownership, and result-package expectation.
- `clean review fanout`: for fresh read-only review routing. Load `CLEAN-REVIEW-FANOUT.md`; reviewers must not edit files.
- `complex separation`: for managed worktree, merge-back, cleanup, role separation, release/cache, or multi-role handoff boundaries. Load `COMPLEX-WORK-SEPARATION.md`, `RUNTIME-ADAPTERS.md`, and `RESULT-PACKAGE.md` as needed.

## Minimal Evidence Boundary

Confirm source truth, issue set, readiness source, and evidence level before routing. Dispatch may recommend only from evidence it can name; it must not claim runtime execution, selector enforcement, cache refresh, clean review, closeout, branch cleanup, UAT, release, or customer readiness from package text alone.

Apply only the shared contract needed by the active route:

- `skills/_shared/NON-EXECUTOR-BOUNDARY.md` before emitting runtime packages or execution gates.
- `skills/_shared/RUNTIME-CAPABILITY.md` and `skills/_shared/COGNITIVE-BUDGET.md` when runtime/model selection is material.
- `skills/_shared/EVIDENCE-BOUNDARY.md`, `skills/_shared/ROLE-SEPARATION.md`, `skills/_shared/RELEASE-EVIDENCE-CLAIM.md`, and `skills/_shared/LLM-WIKI.md` only when the route makes those claims.
- `skills/_shared/DECISION-MAPPING.md` only for pre-dispatch option comparison.

## Required Output

Use this compact shape unless a full package is requested:

```text
Dispatch Runtime Decision

Dispatch Summary

Source Truth
- PRD:
- Issue Set:
- Readiness Source:
- Evidence Level:

Runtime Capability Check
- capability_status:
- selector_enforcement:
- Evidence layer:
- Available / assumed runtimes:
- Runtime selectors available:
- Requested runtime:
- Available runtime:
- Runtime mismatch:
- Fallback proposed:
- User approval required:

Task Matrix
| Task | Type | Readiness | Runtime | Isolation | Parallelization | Goal | Execution Profile | Validation | Result Package | Approval Needed |
|---|---|---|---|---|---|---|---|---|---|---|

No-Execution / Blocked / Needs Split

Runtime Packages
- Package Ref:
- Source Package:
- Validation Expectation:
- Approval Requirements:

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
```

Full package payloads must conform to `DISPATCH-PACKAGE.md`; do not duplicate the full schema in this entry file.

## Stop Conditions

- Stop before routing when source truth, issue set, readiness source, or evidence level is unknown.
- Split hybrid work before emitting a write worktree package.
- Route read-only and planning-only tasks away from `worktree_isolated`.
- Stop before execution unless the user explicitly requests execution and the current runtime exposes the required tools.
- Stop or mark unverified when selector support, managed worktree availability, cache refresh, clean review, release/UAT evidence, or runtime execution is not evidenced.

## Reference Loading Rules

Load only the reference matching the active route.

- Full schema and routing fields: `DISPATCH-PACKAGE.md`.
- Unified result envelope: `RESULT-PACKAGE.md`.
- Runtime capabilities and adapter boundaries: `RUNTIME-ADAPTERS.md`.
- Routing profiles: `ROUTING-PROFILES.md`.
- Runtime package examples: `EXAMPLES.md`.
- Clean review fanout: `CLEAN-REVIEW-FANOUT.md`.
- Managed worktree, role separation, and closeout boundaries: `COMPLEX-WORK-SEPARATION.md`.
- Conflict/dependency preflight: `CONFLICT-PREFLIGHT.md`.
- Entry-router behavior and hard-stop details: `DISPATCH-ROUTER-BRANCHES.md`.

## Gate Rule

If the user asks dispatch to execute, output the package plus `Proposed Action`, `Target Runtime`, `Required Tool Capability`, `Risk`, `Rollback/Undo`, and `Approval Needed`. Proceed only after explicit approval and tool availability are both confirmed.

## Artifact Rule

Write dispatch artifacts only when package review, execution handoff, or later verification needs a stable file. New or materially updated durable artifacts must follow `skills/_shared/AUDIENCE-FIRST-ARTIFACT.md` and `skills/_shared/ARTIFACT-DIRECTORY-POLICY.md`. Redact secrets, credentials, PII, sensitive logs, screenshots, requests, and database rows.
