# Adversarial Review Lens

Purpose: internal falsification lens for material claims; source-validation guidance until paired with named evidence and never a clean-review substitute.

## Public Surface Boundary

Do not create `skills/adversarial-review/SKILL.md` for this behavior by default. Adversarial review is a shared lens inside existing routes unless an accepted public-surface scope proves a distinct invocation moment, route negatives, hard-negative evals, skill-quality review, and maintainer acceptance.

## Core Definition

Adversarial review challenges claims, not people. It tries to falsify the current conclusion by looking for the strongest counterexample, missing evidence, hidden assumption, edge state, and scope boundary failure.

It does not replace `verify`, clean review, role separation, runtime/cache evidence, UAT evidence, release evidence, or human maintainer judgment.

## Use When

Use this lens when:

- a PRD/spec may turn unsupported wording into contract or implementation truth;
- a plan may hide a dependency, edge case, or wrong first inspection step;
- an implementation self-check may miss a failure mode or overstate readiness;
- `verify` is judging evidence sufficiency, readiness, UAT, release, runtime, marketplace, cache, UI, or customer-facing claims;
- handoff must preserve the strongest remaining risk and do-not-assume boundary;
- public skill, shared guardrail, adapter contract, package template, schema, fixture, state-machine, or shared-config changes need stricter review.

Do not use it as ceremony for tiny mechanical edits, direct answers, or low-risk local changes where no material claim, route, artifact, or evidence boundary would change.

## Lens Questions

Use the questions internally. Surface only adversarial findings that change scope, verdict, evidence needs, or remaining risk; do not print the full lens by default.

```text
Adversarial Review Lens
1. Strongest Counterexample
   - If this conclusion is wrong, what concrete example most likely breaks it?

2. Missing Evidence
   - Which source, test, runtime, browser, data, environment, UAT, release, customer, marketplace, or installed-cache evidence is absent?

3. Hidden Assumption
   - Which unstated assumption supports the conclusion, plan, or readiness claim?

4. Edge State / Edge Data
   - Which empty, duplicated, stale, cached, concurrent, permissioned, environment-specific, or migration state can fail?

5. Scope Creep
   - Did a bug fix become a refactor, a PRD become platform redesign, or source-validation become release/runtime/UAT evidence?

6. Reviewer Objection
   - What would a fresh-context clean reviewer most likely flag as P0/P1?

7. Claim Boundary
   - Which claims must stay `unverified`, `not covered`, `partial`, or `blocked`?
```

## Output Add-On

Use this compact add-on only when the active route needs visible adversarial findings:

```text
Adversarial Findings
- Strongest Counterexample:
- Missing Evidence:
- Hidden Assumption:
- Edge Cases Not Covered:
- Claims Downgraded To Unverified:
- Required Next Check:
```

Do not place this block before the required `Verification Scope` block in `verify` reports.

## Combined Loop

Use this canonical loop for high-risk bugs, material skill changes, readiness claims, release/UAT claims, or Groundwork mechanism changes:

```text
Construct -> Attack -> Narrow -> Verify
```

- Construct the explanation from primitive facts, constraints, causal mechanism, root cause, minimal solution, and falsifiable signal.
- Attack the conclusion with this adversarial lens.
- Narrow scope, remove unsupported actions, and downgrade unsupported claims.
- Verify through the owning Groundwork route with explicit covered/not-covered evidence.

## Evidence Boundary

Adversarial review is self-check or review-structure evidence unless performed by a separate reviewer with source access and an explicit review scope. It cannot be renamed into clean review, independent verification, runtime/browser/UAT/release evidence, installed-plugin/cache evidence, marketplace evidence, or customer readiness.
