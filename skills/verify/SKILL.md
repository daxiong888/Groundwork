---
name: verify
description: Use for evidence-sufficiency questions: "验证通过吗?", diff summary sufficiency, whether self-review can count as clean review, readiness/release/UAT/runtime support, UI evidence, and evidence packages. Not for code edits, raw requirements, slicing, or conformance review without evidence/readiness judgment.
---

# verify

## Use When

Use this skill for claim-scoped evidence judgment: readiness, evidence sufficiency, diff-summary sufficiency, whether self-review can count as clean review, self-review versus clean-review boundaries, UAT/SIT, runtime behavior, release confidence, source-truth validation, frontend handoff confidence, git-boundary review, QA failure handling, UI evidence/tool choice, or fresh-context review prompt preparation.

Do not use for code edits, raw requirement shaping, task slicing, planning before edits, prototype contract-boundary classification, wiki queries, or implementation conformance review when readiness/evidence judgment is explicitly out of scope.

## Route First

Choose the lightest branch that can answer the claim:

- `verify-lite`: no-command prompts, code-diff-only sufficiency questions, or "现有证据够不够" checks.
- `verify-standard`: implementation acceptance or TASK/PRD conformance with readiness/evidence claims.
- `verify-strict`: release, UAT, customer, runtime, cache, marketplace, installed-plugin, selector-enforcement, package-readiness, or browser/UI claims.

Historical baselines are allowed only when the user explicitly asks for historical/eval/baseline/release evidence or a current source artifact cites a specific historical path.

## Default Path: Named Evidence Verification

Use this path for generic claim-evidence verification when the prompt names `CLAIM.md`, `EVIDENCE.md`, a scope artifact, or explicit evidence artifact paths and does not ask to evaluate, debug, install, package, release, cache-check, or maintain Groundwork itself.

Read only:

- this active `verify` contract;
- the user-named claim, evidence, scope, or check-output artifacts;
- `VERIFY-SCOPE.md` and `SCOPE-EVIDENCE-TEMPLATE.md` when needed for the required scope-first report.

Do not inspect Groundwork plugin README, `.codex-plugin/plugin.json`, plugin manifests, package internals, other skill `SKILL.md` files, or repository-wide docs/source by default. Leave this path only when the user explicitly asks for Groundwork maintenance, plugin/package/install/cache/release verification, or when a named in-scope artifact cites a specific additional path that must be checked.

Scenario workspace allowlisted file discovery is allowed and may be reported as a warning when noisy; do not treat allowlisted discovery of the named evidence files as a hard failure.

Even on this fast path, keep the full verify safety boundary: concrete scope, `Covered`, `Not Covered`, `Evidence Sources`, missing evidence, and bounded support/readiness judgment remain mandatory.

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
- Adversarial evidence sufficiency, strongest-counterexample, edge-state, or claim-boundary review: `skills/_shared/ADVERSARIAL-REVIEW.md`.

Apply shared evidence, role-separation, runtime, release, wiki, cognitive-budget, or visual-handoff contracts only when the active claim depends on that evidence type.

## Stop Conditions

- Stop before any verdict unless `Verification Scope` has concrete `Covered`, `Not Covered`, and `Evidence Sources` fields.
- Do not claim `pass`, readiness, UAT, release, runtime, browser, data, environment, or customer confidence without fresh in-scope evidence.
- If only source, doc, diff, summary, or historical evidence is available, state that boundary and keep stronger claims unverified.
- If verification is paired with push, deploy, publish, migration, destructive command, data write, remote tracker mutation, or shared skill mutation, output the approval gate before action.
