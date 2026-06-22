# PRD v0.4.1 Trace-First Verify / Review Eval

Target Reader: Groundwork maintainers and runtime-eval authors.
Reader Action Needed: Use this PRD to implement the v0.4.1 trace-first eval slice for verify readiness and clean-review separation.
Decision Supported: Whether v0.4.1 can add targeted eval coverage and default-suite wiring without expanding the public skill surface.
Artifact Type: PRD
Source of Truth: User request on 2026-06-18 plus existing `skills/verify/SKILL.md`, `skills/dispatch/CLEAN-REVIEW-FANOUT.md`, and `evals/run_runtime.py` contracts.
Scope: Trace-ready runtime eval rows for verify scope-first reports and dispatch clean-review fan-out boundaries; runner default-suite inclusion; maintainer documentation for suite intent.
Out of Scope: New public skills, new runtime dependencies, package metadata version bumps, marketplace/cache refresh claims, live runtime baselines, remote tracker writes, and edits outside docs/evals needed for this slice.
Evidence Level: Local source-truth synthesis from existing repository contracts; no installed-plugin runtime evidence is claimed by this PRD.
Safe to Share / Redaction Notes: Safe to share as-is; contains no secrets, credentials, PII, raw logs, or private payloads.

## Problem

Groundwork already has targeted prompt rows for `verify` and clean-review fan-out, but those rows live in separate legacy suites with suite-specific columns. v0.4.1 needs a trace-first regression slice that makes the critical readiness and review boundaries observable through the same trace-ready verdict model used by routing reliability.

## Goals

1. Add a compact targeted eval suite whose rows include stable ids, route boundary, case kind, source, expected/acceptable/forbidden routes, output contracts, evidence contracts, and forbidden behavior.
2. Cover the highest-risk v0.4.1 behaviors:
   - `verify` reports must begin with the complete six-field `Verification Scope` block.
   - Code-diff-only readiness must not become a readiness pass without runtime/browser evidence.
   - QA failure reports must keep `Verification Scope` before the `QA Failure` block.
   - Dispatch clean-review fan-out must reject child self-review, reviewer edits, hidden parent context, and missing validation inference.
   - Low-risk coordinator intake remains allowed only with explicit low-risk exception evidence.
3. Wire the suite into `evals/run_runtime.py` default suites so maintainers do not have to remember a separate targeted command for the v0.4.1 smoke path.
4. Document that local CSV/schema checks are source checks only and are not runtime, cache-refresh, release, or UAT evidence.

## Non-Goals

- Do not add, remove, or rename public skills.
- Do not change `.codex-plugin/plugin.json` or bump package versions.
- Do not claim installed-plugin runtime behavior from local CSV edits.
- Do not introduce a package manager, lockfile, or external eval dependency.

## Acceptance Criteria

- AC-1: `evals/prompts/trace-first-verify-review.csv` exists with trace-ready routing schema fields.
- AC-2: The suite contains targeted rows for verify scope-first readiness and dispatch clean-review boundaries.
- AC-3: Rows use finite measurement tokens already supported by `evals/run_runtime.py`.
- AC-4: `evals/run_runtime.py` includes the new suite in `DEFAULT_SUITES`.
- AC-5: Maintainer docs name the suite, its trace-first purpose, and its evidence limitations.
- AC-6: CSV parsing and whitespace checks pass locally.

## Evidence Boundary

This PRD is satisfied by local source changes and local validation commands. A future runtime baseline may be recorded only after the installed plugin root and source/cache equivalence or supported refresh are named.
