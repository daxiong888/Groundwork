# First-Principles Lens

Purpose: internal first-principles construction for material causal decisions; source-validation guidance until paired with named evidence.

## Public Surface Boundary

Do not create `skills/first-principles/SKILL.md` for this behavior by default. First-principles work is a shared lens inside existing routes unless an accepted public-surface scope proves a distinct invocation moment, route negatives, hard-negative behavior evidence, skill-quality review, and maintainer acceptance.

## Core Definition

First-principles analysis reduces a request, bug, design, or claim to primitive facts, non-negotiable constraints, causal mechanisms, and the smallest sufficient, verifiable solution.

It does not replace source inspection, implementation, verification, or clean review. It is the construction half of the loop: build the strongest evidence-grounded explanation before editing or claiming support.

## Minimal Means Sufficient First

Evaluate candidate solutions in this order:

1. **Sufficiency:** the solution addresses the confirmed cause or core need, restores the affected invariants, and has a falsifiable verification signal.
2. **Scope:** among sufficient solutions, choose the one with the lowest justified blast radius, complexity, and unrelated change.

Line count, file count, and implementation convenience are not sufficiency criteria. A smaller patch is invalid when it only masks a symptom, moves the failure to another layer, duplicates logic around a broken shared mechanism, or leaves a known affected path inconsistent.

If every sufficient solution exceeds the accepted scope, authority, or risk gate, stop and surface the required expansion or decision. Do not silently downgrade to a superficial workaround and call it minimal.

## Use When

Use this lens when:

- the task depends on root cause, not just surface symptoms;
- PRD/spec intent risks copying desired fields or workflow names without source authority;
- implementation order depends on causal path, state machine, contract, schema, permission, runtime, or environment constraints;
- a bug fix could become speculative without a confirmed mechanism;
- a handoff must preserve why the solution is minimal and what remains unverified.

Do not use it for tiny mechanical edits, direct factual answers, simple rewrites, accepted implementation work with already inspected source and clear checks, or ceremonial restatement that does not change scope, route, or verification.

## Process

Use the questions internally. Surface only facts, causal conclusions, or unknowns that change the decision; do not print the full numbered scaffold by default.

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
   - For cross-boundary contract behavior, use the optional `Contract Lineage` shape in `skills/_shared/CONTRACT-NOTES.md` to trace applicable hops and identify the first confirmed divergence before choosing a fix owner. Producer-first inspection is not producer-first blame.

6. Root Cause / Core Bottleneck
   - What is the smallest cause or need? Which observations are symptoms, triggers, or unsupported interpretations?

7. Minimal Sufficient Solution
   - Which candidates actually address the cause and restore the invariants? Among those sufficient candidates, which has the lowest justified blast radius?

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
- Minimal Sufficient Fix:
- Verification Signal:
- Remaining Hypotheses:
```

If the root cause cannot be confirmed, stop before speculative edits or make only the smallest source-level diagnostic change with an explicit verification gap.

## Adversarial Pairing

For high-risk bugs, material skill changes, readiness claims, release/UAT claims, or Groundwork mechanism changes, pair this lens with the canonical Combined Loop in `skills/_shared/ADVERSARIAL-REVIEW.md`.

## Evidence Boundary

First-principles output is reasoning structure plus source-validation unless paired with named evidence. It cannot prove installed-plugin behavior, selector enforcement, browser behavior, runtime behavior, data correctness, UAT readiness, release readiness, customer readiness, marketplace behavior, cache refresh, clean review, or independent verification by itself.
