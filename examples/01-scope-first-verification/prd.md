# PRD: Scope-First Verification

Target Reader: Groundwork maintainer reviewing readiness behavior in `verify`.
Reader Action Needed: Decide whether verification reports should start by declaring scope and evidence coverage.
Decision Supported: Whether the v0.2.x hardening should require a complete scope block before readiness verdicts.
Scope: `verify` outputs for readiness, UAT, release, implementation evidence, contract review, UI routing, QA failure, git boundary, and subagent review prompts.
Out of Scope: Implementing application features, creating customer-facing UAT reports, or replacing CI/runtime checks.
Evidence Level: `docs/prd.md` verification contract, `CHANGELOG.md` v0.2.2/v0.2.3, and v0.2.3 runtime baseline rows.

## Problem

When a maintainer asks whether work is ready for review, UAT, or release, an assistant can overstate readiness if it does not first declare what was actually checked.

## Goal

Make `verify` start with explicit scope, evidence sources, covered areas, not-covered areas, and the user-visible claim being verified.

## Acceptance Criteria

- AC-1: Every final verification report begins with `Verification Scope`.
- AC-2: The opening block includes `In Scope`, `Out of Scope`, `Covered`, `Not Covered`, `Evidence Sources`, and `User-visible Claim Being Verified`.
- AC-3: Specialized payloads such as contract review, UI evidence, QA failure, git boundary, approval gate, and subagent prompt appear after the scope block.
- AC-4: Missing tests, runtime, browser, data, environment, UAT, and customer evidence are marked as unverified when not checked.
- AC-5: Verification gives a bounded verdict of `pass`, `partial`, `fail`, or `blocked`.

## Non-Goals

- Do not require the absolute first user-visible assistant line to be `Verification Scope`; progress prefaces are allowed when they contain no verdict.
- Do not claim readiness from a diff summary alone.
- Do not close tasks directly from `verify`; closeout remains a later task-state decision.

