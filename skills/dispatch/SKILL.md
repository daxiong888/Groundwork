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
- `full dispatch package`: worktree/subagent/runtime handoff instructions. Load the package schema only for this route.
- `clean review fanout`: fresh read-only review routing. Reviewers must not edit files.
- `complex separation`: managed worktree, merge-back, cleanup, role separation, release/cache, or multi-role handoff boundaries.

## Evidence Boundary

Confirm source truth, issue set, readiness source, and evidence level before routing. Dispatch may recommend only from evidence it can name. It must not claim runtime execution, selector enforcement, cache refresh, clean review, closeout, branch cleanup, UAT, release, or customer readiness from package text alone.

If runtime/model selection is material, prefer `model_profile` before concrete models and label selector enforcement as `tool_enforced`, `prompt_preference`, `unavailable`, or `unknown` based on current tool evidence.

## Required Output

For lite routes, emit only the fields needed to make the routing decision clear: source truth, runtime capability boundary, task matrix, blocked/split items, expected result package, and next action.

Full package payloads must conform to `DISPATCH-PACKAGE.md`; do not duplicate the full schema in this entry file.

## Load Only What Fits

- Entry-route behavior and hard stops: `DISPATCH-ROUTER-BRANCHES.md`.
- Full schema and routing fields: `DISPATCH-PACKAGE.md`.
- Unified result envelope: `RESULT-PACKAGE.md`.
- Runtime capabilities and adapter boundaries: `RUNTIME-ADAPTERS.md`.
- Routing profiles: `ROUTING-PROFILES.md`.
- Runtime package examples: `EXAMPLES.md`.
- Clean review fanout: `CLEAN-REVIEW-FANOUT.md`.
- Managed worktree, role separation, and closeout boundaries: `COMPLEX-WORK-SEPARATION.md`.
- Conflict/dependency preflight: `CONFLICT-PREFLIGHT.md`.

Apply non-executor, runtime-capability, cognitive-budget, role-separation, release-evidence, evidence-boundary, wiki, or decision-mapping references only when the active route makes that claim.

## Stop Conditions

- Stop before routing when source truth, issue set, readiness source, or evidence level is unknown.
- Split hybrid work before emitting a write worktree package.
- Route read-only and planning-only tasks away from `worktree_isolated`.
- If the user asks dispatch to execute, stop at the package plus approval gate and route execution to the owning runtime, thread/worktree tool, or implementation owner.
- Stop or mark unverified when selector support, managed worktree availability, cache refresh, clean review, release/UAT evidence, or runtime execution is not evidenced.
