---
name: dispatch
description: Package-only routing for accepted ready tasks: model/profile, matrix, Dispatch Package, result expectations. Not for execution, worktrees, subagents, branch mutation, readiness, or raw tasks.
---

# dispatch

## Use When

Use when accepted, ready work needs package-only runtime routing: recommendation, model/profile choice, matrix, Dispatch Package v2, clean-review fanout, or expected Result Package. Do not use for raw/unsliced/unknown-readiness work, implementation, planning-only requests, or readiness verification.

## Route First

Dispatch is a router/package generator, not executor. Routes: `lite matrix`, `full dispatch package` loading only `DISPATCH-PACKAGE.md` by default, `clean review fanout`, and `complex separation` for managed worktree, merge-back, cleanup, role, release/cache, or multi-role boundaries.

## Default Dispatch Package v2 Path

When the user provides an accepted task artifact and asks for Dispatch Package v2, default boundary: Read only the accepted task artifact and `DISPATCH-PACKAGE.md`.

Default output: compact dispatch matrix plus package skeleton. Preserve source truth, readiness source, package-only status, expected output, approval gates, and missing-evidence handling. Do not execute, spawn subagents, create worktrees, or mutate branches.

Do not load result, adapter, profile, examples, complex, clean-review, or conflict-preflight refs for the default package path unless prompt-material.

## Evidence Boundary

Confirm source truth, issue set, readiness source, and evidence level. Recommend only from named evidence. Never claim runtime execution, selector enforcement, cache refresh, clean review, closeout, branch cleanup, UAT, release, or customer readiness from package text alone.

If runtime/model selection is material, prefer `model_profile` before concrete models and label selector enforcement as `tool_enforced`, `prompt_preference`, `unavailable`, or `unknown` from current tool evidence.

## Required Output

For lite routes, emit source truth, runtime capability boundary, task matrix, blocked/split items, expected result package, next action.

Full payloads conform to `DISPATCH-PACKAGE.md`; do not duplicate schema here. Default `adapter_completeness: skeleton_only` unless adapter-ready is explicit. Missing fields become `needs_info`, `needs_split`, `blocked`, or `human_decision`; do not search package internals.

## Load Only What Fits

- Default Dispatch Package v2 contract: `DISPATCH-PACKAGE.md`.
- Load `DISPATCH-PACKAGE-DETAILS.md` only when the prompt requires full schema, adapter contract, or field-level validation.
- Load `RESULT-PACKAGE.md` only when the prompt asks for result package expectations or returned evidence.
- Load `RUNTIME-ADAPTERS.md` only when runtime adapter, runtime capability, or selector behavior is in scope.
- Load `ROUTING-PROFILES.md` only when model/profile selection is material.
- Runtime package examples: Load `EXAMPLES.md` only when the user asks for examples or format ambiguity blocks output.
- Load `DISPATCH-ROUTER-BRANCHES.md` only when route selection or hard-stop branching is ambiguous.
- Load `CLEAN-REVIEW-FANOUT.md` only for clean review fanout routing.
- Load `COMPLEX-WORK-SEPARATION.md` only for managed worktree, merge-back, cleanup, role separation, release/cache, or multi-role boundaries.
- Load `CONFLICT-PREFLIGHT.md` only when dependency barriers, shared files, stale base, or parallel write conflicts affect routing.

Apply shared non-executor/runtime/role/release/evidence/wiki/decision refs only when the active route makes that claim.

## Stop Conditions

- Stop before routing when source truth, issue set, readiness source, or evidence level is unknown.
- Split hybrid work before emitting a write worktree package.
- Route read-only and planning-only tasks away from `worktree_isolated`.
- If asked to execute, stop at the package plus approval gate and route execution to the owning runtime, thread/worktree tool, or implementation owner.
- Stop or mark unverified when selector support, managed worktree availability, cache refresh, clean review, release/UAT evidence, or runtime execution is not evidenced.
