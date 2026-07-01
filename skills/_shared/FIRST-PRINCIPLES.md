# First-Principles Lens

Target Reader: Groundwork skill authors, routers, implementers, reviewers, and verifiers deciding whether a request needs root-cause construction before planning, editing, or claiming evidence.
Reader Action Needed: Reduce a request, bug, design, contract, or claim to primitive facts, hard constraints, causal mechanism, root cause, minimal solution, and falsifiable verification.
Decision Supported: Whether the current conclusion is grounded enough to plan, implement, verify, hand off, or narrow scope.
Artifact Type: shared workflow reference.
Source of Truth: `docs/product-principles.md`, `skills/_shared/EVIDENCE-BOUNDARY.md`, `skills/implement/SKILL.md`, and source-validation policy.
Scope: First-principles decomposition for requirements, bugs, implementation plans, contracts, source-backed docs, and evidence claims.
Out of Scope: Public skill creation, readiness approval, runtime/cache/release/UAT evidence, clean review, or replacing source inspection.
Evidence Level: Source-validation guidance only until paired with named source, test, runtime, browser, data, UAT, release, or clean-review evidence.
Safe to Share / Redaction Notes: Safe to share as-is; contains no secrets, credentials, private payloads, PII, or production data.

## Public Surface Boundary

Do not create `skills/first-principles/SKILL.md` for this behavior by default. First-principles work is a shared lens inside existing routes unless an accepted public-surface scope proves a distinct invocation moment, route negatives, hard-negative evals, skill-quality review, and maintainer acceptance.

## Core Definition

First-principles analysis reduces a request, bug, design, or claim to primitive facts, non-negotiable constraints, causal mechanisms, and the smallest verifiable solution.

It does not replace source inspection, implementation, verification, or clean review. It is the construction half of the loop: build the strongest evidence-grounded explanation before editing or claiming support.

## Use When

Use this lens when:

- the task depends on root cause, not just surface symptoms;
- PRD/spec intent risks copying desired fields or workflow names without source authority;
- implementation order depends on causal path, state machine, contract, schema, permission, runtime, or environment constraints;
- a bug fix could become speculative without a confirmed mechanism;
- a handoff must preserve why the solution is minimal and what remains unverified.

Do not use it for tiny mechanical edits, direct factual answers, simple rewrites, accepted implementation work with already inspected source and clear checks, or ceremonial restatement that does not change scope, route, or verification.

## Process

```text
First-Principles Lens
1. Phenomenon / Goal
   - What is the user-visible symptom, requested outcome, or claim?

2. Primitive Facts
   - Which facts are supported by source, docs, tests, API/schema, runtime/browser/data/UAT evidence, user-provided artifacts, or command output?

3. Non-Negotiable Constraints
   - Which API contracts, DB schemas, permissions, state machines, performance constraints, compatibility rules, release boundaries, or user decisions cannot be bypassed?

4. Invariants
   - What must remain true regardless of implementation choice?

5. Causal Mechanism
   - How do input, state, code path, data, environment, and output produce the observed behavior or required outcome?

6. Root Cause / Core Bottleneck
   - What is the smallest cause or need? Which observations are symptoms, triggers, or unsupported interpretations?

7. Minimal Sufficient Solution
   - What is the smallest scoped change, decision, or artifact that addresses the cause while preserving constraints?

8. Falsifiable Verification Signal
   - What test, runtime/browser/data/UAT check, source inspection, or review evidence would disprove or support the solution?

9. Remaining Unknowns
   - Which facts remain unverified and cannot be upgraded into readiness, contract truth, release confidence, or customer/UAT claims?
```

## Bug Root-Cause Ladder

Use this compact ladder for nontrivial bug diagnosis before edits:

```text
Bug Root-Cause Ladder
- Symptom:
- Reproduction / Inspection:
- Primitive Facts:
- Constraints / Invariants:
- Causal Chain:
- Root Cause:
- Minimal Fix:
- Verification Signal:
- Remaining Hypotheses:
```

If the root cause cannot be confirmed, stop before speculative edits or make only the smallest source-level diagnostic change with an explicit verification gap.

## Combined Loop

Pair this lens with `skills/_shared/ADVERSARIAL-REVIEW.md` for high-risk bugs, material skill changes, readiness claims, release/UAT claims, or Groundwork mechanism changes:

```text
Construct -> Attack -> Narrow -> Verify
```

- Construct from primitive facts, constraints, mechanism, root cause, minimal solution, and falsifiable signal.
- Attack the conclusion with counterexamples, missing evidence, edge states, hidden assumptions, and scope creep.
- Narrow unsupported actions and downgrade claims that evidence does not prove.
- Verify through the owning Groundwork route without upgrading source-validation into runtime/cache/UAT/release evidence.

## Evidence Boundary

First-principles output is reasoning structure plus source-validation unless paired with named evidence. It cannot prove installed-plugin behavior, selector enforcement, browser behavior, runtime behavior, data correctness, UAT readiness, release readiness, customer readiness, marketplace behavior, cache refresh, clean review, or independent verification by itself.
