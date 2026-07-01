---
name: dispatch
description: Use when accepted ready tasks need package-only runtime routing, model/profile recommendation, execution matrix, or result-package expectations. Do not use to execute work, create worktrees, call subagents, mutate branches, verify readiness, or route raw/uncertain tasks.
---

# dispatch

## Use When

Use this skill when accepted, ready work needs package-only runtime routing: a runtime recommendation, model/profile choice, execution matrix, Dispatch Package v2, clean-review fanout plan, or expected Result Package.

Do not use when requirements are raw, issues are unsliced, readiness is unknown, the user asks to implement directly, the user asks only for a plan, or the user asks whether finished work is ready/verified.

## Route First

Dispatch is a router and package generator, not an executor.

- `lite matrix`: small accepted task sets needing a runtime recommendation and no full package.
- `full dispatch package`: accepted task artifact to Dispatch Package v2. Load `DISPATCH-PACKAGE.md` only by default.
- `clean review fanout`: fresh read-only review routing. Reviewers must not edit files.
- `complex separation`: managed worktree, merge-back, cleanup, role separation, release/cache, or multi-role handoff boundaries.

## Default Dispatch Package v2 Path

When the user provides an accepted task artifact and asks for Dispatch Package v2, use this default read boundary: Read only the accepted task artifact and `DISPATCH-PACKAGE.md`.

Default output: compact dispatch matrix plus package skeleton. Preserve source truth, readiness source, package-only status, expected output type, approval gates, and missing-evidence handling. Do not execute, spawn subagents, create worktrees, or mutate branches.

Do not load result, runtime adapter, routing profile, examples, complex separation, clean-review, or conflict-preflight references for the default package path unless the prompt explicitly makes that reference material.

## Evidence Boundary

Confirm source truth, issue set, readiness source, and evidence level before routing. Dispatch may recommend only from evidence it can name. It must not claim runtime execution, selector enforcement, cache refresh, clean review, closeout, branch cleanup, UAT, release, or customer readiness from package text alone.

If runtime/model selection is material, prefer `model_profile` before concrete models and label selector enforcement as `tool_enforced`, `prompt_preference`, `unavailable`, or `unknown` based on current tool evidence.

## Required Output

For lite routes, emit only the fields needed to make the routing decision clear: source truth, runtime capability boundary, task matrix, blocked/split items, expected result package, and next action.

Full package payloads must conform to the compact default contract in `DISPATCH-PACKAGE.md`; do not duplicate the full schema in this entry file. The default compact package is `adapter_completeness: skeleton_only` unless the prompt explicitly needs an adapter-ready package. If required package fields are missing, mark `needs_info`, `needs_split`, `blocked`, or `human_decision` instead of searching unrelated package internals.

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

Apply non-executor, runtime-capability, cognitive-budget, role-separation, release-evidence, evidence-boundary, wiki, or decision-mapping references only when the active route makes that claim.

## Stop Conditions

- Stop before routing when source truth, issue set, readiness source, or evidence level is unknown.
- Split hybrid work before emitting a write worktree package.
- Route read-only and planning-only tasks away from `worktree_isolated`.
- If the user asks dispatch to execute, stop at the package plus approval gate and route execution to the owning runtime, thread/worktree tool, or implementation owner.
- Stop or mark unverified when selector support, managed worktree availability, cache refresh, clean review, release/UAT evidence, or runtime execution is not evidenced.
