---
name: verify
description: Use when the user asks whether a specific claim, implementation, runtime behavior, release/UAT readiness, UI behavior, or evidence package is supported by current evidence. Do not use for plain code edits, raw requirement shaping, task slicing, or implementation conformance review without readiness/evidence judgment.
---

# verify

## Use When

Use this skill for claim-scoped evidence judgment: readiness, evidence sufficiency, UAT/SIT, runtime behavior, release confidence, source-truth validation, frontend handoff confidence, git-boundary review, QA failure handling, UI evidence/tool choice, or fresh-context review prompt preparation.

Do not use for code edits, raw requirement shaping, task slicing, planning before edits, prototype contract-boundary classification, wiki queries, or implementation conformance review when readiness/evidence judgment is explicitly out of scope.

## Route First

Choose the lightest branch that can answer the claim:

- `verify-lite`: no-command prompts, code-diff-only sufficiency questions, or "现有证据够不够" checks.
- `verify-standard`: implementation acceptance or TASK/PRD conformance with readiness/evidence claims.
- `verify-strict`: release, UAT, customer, runtime, cache, marketplace, installed-plugin, selector-enforcement, package-readiness, or browser/UI claims.

Historical baselines are allowed only when the user explicitly asks for historical/eval/baseline/release evidence or a current source artifact cites a specific historical path.

## Evidence Boundary

Start from the user-visible claim and the smallest current evidence set that can prove or disprove it: user-provided evidence or paths, current source/diff/tests/check output, named artifacts, runtime/browser evidence when requested, and installed cache or local `dist/` only when the claim concerns plugin install, cache, marketplace, package, or release readiness.

Do not default to `evals/baselines/`, `artifacts/`, `research/`, `examples/`, historical release notes, old handoffs, old runtime trials, or broad `docs/prd-v*` archaeology.

## Required Output

Every final verification report starts with the complete six-field block from `SCOPE-EVIDENCE-TEMPLATE.md`. The first line is exactly:

```text
Verification Scope
```

Do not rename, translate, decorate, or replace that opening block. After it, use a compact claim-to-evidence summary unless a branch reference requires a fuller payload.

## Load Only What Fits

- Scope-first or no-command: `VERIFY-SCOPE.md` and `SCOPE-EVIDENCE-TEMPLATE.md`.
- Full branch workflow, failure handling, optional task/lifecycle blocks: `VERIFY-ROUTER-BRANCHES.md`.
- QA failure or QA -> fix -> QA advice: `QA-FAILURE-BRANCH.md` and `QA-FIX-QA.md`.
- Runtime/model selector or mismatch: `RUNTIME-CAPABILITY-BRANCH.md` and `skills/_shared/RUNTIME-CAPABILITY.md`.
- Runtime/cache/release/UAT/customer/marketplace/installed-plugin readiness: `RELEASE-READINESS-BRANCH.md` and `skills/_shared/RELEASE-EVIDENCE-CLAIM.md`.
- Native closeout, merge readiness, cleanup separation, or closeout git-boundary: `NATIVE-CLOSEOUT-BRANCH.md`.
- Browser-visible, responsive, interaction, visual, console, or network evidence: `UI-READINESS-BRANCH.md` and `UI-TOOL-ROUTER.md`.
- Fresh-context subagent review prompts: `SUBAGENT-REVIEW-BRANCH.md` and `skills/_shared/SUBAGENT-DELEGATION.md`.
- Frontend-facing contract docs: `CONTRACT-DOC-REVIEW.md`.
- Named lens selection: `LENSES.md`.

Apply shared evidence, role-separation, runtime, release, wiki, cognitive-budget, or visual-handoff contracts only when the active claim depends on that evidence type.

## Stop Conditions

- Stop before any verdict unless `Verification Scope` has concrete `Covered`, `Not Covered`, and `Evidence Sources` fields.
- Do not claim `pass`, readiness, UAT, release, runtime, browser, data, environment, or customer confidence without fresh in-scope evidence.
- If only source, doc, diff, summary, or historical evidence is available, state that boundary and keep stronger claims unverified.
- If verification is paired with push, deploy, publish, migration, destructive command, data write, remote tracker mutation, or shared skill mutation, output the approval gate before action.
