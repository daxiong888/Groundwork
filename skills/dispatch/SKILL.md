---
name: dispatch
description: Package-only routing for accepted ready tasks: model/profile, matrix, Dispatch Package, clean-review fanout, and result expectations. Not for execution, ordinary audits, worktrees, subagents, branch mutation, readiness, raw tasks, or doing the delegated work itself.
---

# dispatch

## Use When

Use when accepted, ready work explicitly needs package-only runtime routing: recommendation, model/profile choice, matrix, Dispatch Package v2, clean-review fanout, or expected Result Package. A read-only audit uses dispatch only when the user explicitly asks to route, package, fan out, or delegate that audit. Multi-perspective audit packaging is not clean-review fanout unless the user explicitly requests clean review or supplies a completed result/review package. Do not intercept an ordinary request to perform or report an audit. Do not use for raw/unsliced/unknown-readiness work, implementation, planning-only requests, or readiness verification.

## Route First

Dispatch is a router/package generator, not executor. Routes: `lite matrix`, `full dispatch package` loading only `DISPATCH-PACKAGE.md` by default, `clean review fanout`, and `complex separation` for managed worktree, merge-back, cleanup, role, release/cache, or multi-role boundaries.

## Default Dispatch Package v2 Path

When the user provides an accepted task artifact and asks for Dispatch Package v2, default boundary: Read only the accepted task artifact and `DISPATCH-PACKAGE.md`.

Default output: one compact package skeleton. Preserve source truth, readiness source, package-only status, route, expected output, stop condition, and missing-evidence handling. Do not repeat the same facts in a separate prose matrix. Do not execute, spawn subagents, create worktrees, or mutate branches.

Do not load result, adapter, profile, examples, complex, clean-review, or conflict-preflight refs for the default package path unless prompt-material.

## Default Output Budget

For lite routes and the default skeleton-only package, target at most 2,800 characters and 26 non-empty lines. This is a regression budget, not a truncation rule. Required fields and semantic completeness take precedence. Every Dispatch output, including lite and split decisions, must start the final response at `dispatch_version: 2`; include no prose before or after the package. Do not wrap the package in a code fence. If a complete package cannot fit, do not truncate or silently omit tasks, required evidence, or stop conditions; emit a compact `needs_split` routing decision with the next action, or load the prompt-material route-specific contract and produce a complete extended package. This default budget does not apply to adapter-ready, clean-review fanout, complex separation, field-level validation, or an explicitly requested full schema; keep those outputs concise but complete under their owning contract.

## Evidence Boundary

Confirm source truth, issue set or audit scope, readiness source, and evidence level. When there is missing source truth or audit scope, emit only a lite `needs_info` decision with missing inputs and next action; do not invent generic task lenses. Recommend only from named evidence. Never claim runtime execution, selector enforcement, cache refresh, clean review, closeout, branch cleanup, UAT, release, customer readiness, or completed audit findings from package text alone.

If runtime/model selection is material, prefer `model_profile` before concrete models and label selector enforcement as `tool_enforced`, `prompt_preference`, `unavailable`, or `unknown` from current tool evidence.

## Required Output

For lite routes, emit only the route decision, reason, blocked/split items, expected result type, and next action. Omit empty and not-applicable fields.

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

- Stop before routing when source truth, issue set or audit scope, readiness source, or evidence level is unknown.
- Split hybrid work before emitting a write worktree package.
- Route read-only and planning-only tasks away from `worktree_isolated`.
- If asked to execute, stop at the package plus approval gate and route execution to the owning runtime, thread/worktree tool, or implementation owner.
- Stop or mark unverified when selector support, managed worktree availability, cache refresh, clean review, release/UAT evidence, or runtime execution is not evidenced.
