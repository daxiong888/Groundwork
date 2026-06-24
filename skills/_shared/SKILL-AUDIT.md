Target Reader: Groundwork skill authors, implementers, clean reviewers, verifiers, coordinators, and maintainers auditing public skill additions or material skill changes.
Reader Action Needed: Apply this shared audit workflow before approving public skill additions or material skill-quality changes.
Decision Supported: Whether the change has enough trigger clarity, hierarchy, progressive disclosure, failure handling, eval coverage, and role-separated evidence to proceed.
Artifact Type: shared workflow/reference.
Source of Truth: `docs/prd-v0.5-prototype-first-skill-expansion.md` section 12, FR-542, AC-A3, AC-C1, AC-C2, AC-C7, AC-D1, and V050-006A in `artifacts/v0.5-prototype-first-skill-expansion/issue-map.md`.
Scope: Shared skill-audit workflow for public skill candidates, public skill additions, and material skill changes.
Out of Scope: Creating a public `skill-audit` skill, accepting public skill exposure, replacing independent clean review, replacing maintainer acceptance, or claiming runtime/browser/UAT/release readiness.
Evidence Level: Source-validation workflow. Self-audit output is self-check evidence only unless produced by an independent clean reviewer in a read-only role.
Safe to Share / Redaction Notes: Safe to share as-is; contains no secrets, credentials, private payloads, or personal data.

# Skill Audit

## Invocation Class

`skill-audit` is a required shared workflow/reference before public skill additions and material skill changes are accepted.

It is not a public skill in this reference-first state. Do not create or rely on `skills/skill-audit/SKILL.md` unless a later accepted publicization slice proves direct invocation value, routing negatives pass, and maintainer acceptance explicitly authorizes public exposure.

Classify the audited change before reviewing details:

- Public model-invoked skill: a top-level `skills/<name>/SKILL.md` loaded by routing.
- User-invoked public skill: a public skill with a distinct user-facing invocation moment.
- Shared reference: a reusable guardrail, checklist, template, or workflow under `skills/_shared/`.
- Branch/workflow lens: a bounded branch inside an existing public skill.
- Router behavior: selection or dispatch behavior that should not become user-facing skill surface.

## Trigger Description

For public candidates and material trigger changes, audit the trigger contract before workflow prose:

- The leading name or phrase is stable and meaningfully distinct.
- Should-trigger examples describe a real invocation moment, not a synonym for an existing skill.
- Should-not-trigger examples protect direct answers, accepted implementation, verification, handoff, dispatch, and neighboring public skills.
- Route-conflict negatives prove the candidate does not steal established routes.
- Public exposure is blocked when the behavior is better represented as a shared reference, branch/workflow lens, router behavior, or one-off guide.

## Workflow

Use this order:

1. Confirm accepted source truth for the public skill addition or material skill change.
2. Classify the invocation class and public-surface impact.
3. Review trigger and should-not-trigger coverage.
4. Review workflow steps, stop condition, and checkable completion criteria.
5. Review information hierarchy and progressive disclosure.
6. Remove duplicated guidance, no-op prose, and hidden route expansion.
7. Review failure branches for likely misuse.
8. Review evidence boundary and role separation.
9. Review positive, negative, route-conflict, and hard-negative eval coverage.
10. Label the audit evidence according to role: self-check, clean review, independent verification, or maintainer acceptance.

## Information Hierarchy

Keep universal invocation rules in the public skill `SKILL.md`.

Move branch-specific procedures, templates, detailed checklists, examples, and long domain references into referenced files that are loaded only when needed.

Shared rules that affect multiple skills belong under `skills/_shared/`, not duplicated across public skills. Candidate-specific detail belongs with the candidate only after public exposure is accepted.

## Progressive Disclosure

The skill must load only the references required by the active branch. A public skill should not require users or agents to read unrelated references, eval histories, templates, or implementation notes before a simple route can proceed.

An audit fails when a candidate depends on broad always-load context that can be split into a focused shared reference or branch file without losing correctness.

## Duplication

Remove duplicate trigger language, repeated role-separation prose, copied policy blocks, and no-op instructions that restate platform behavior without changing a decision.

Prefer a single canonical shared reference when multiple skills need the same rule. Link to the shared reference instead of preserving divergent local copies.

## Failure Branches

Block, mark unverified, or return to implementation when any of these occur:

- A skill author audits and approves its own public skill addition or material skill-quality change as final.
- Same-session self-check is offered as clean review, independent verification, readiness, final acceptance, or maintainer acceptance.
- A clean reviewer edits the reviewed skill change and still claims clean review authority for the fixed change.
- A shared reference is promoted to public skill surface without accepted public exposure and maintainer acceptance.
- Trigger, should-not-trigger, route-conflict, or hard-negative eval coverage is skipped.
- Prompt text, local source diff, or CSV parse output is used as runtime, browser, UAT, release, marketplace, installed-plugin cache, or customer evidence.
- Spark or another fast/profile-limited run is used as final clean reviewer, final verifier, public skill approver, release authority, or UAT authority.

## Evidence Boundary

Self-audit by the author or implementer is `Self-check Evidence` only.

Clean review evidence must come from a separate read-only role/session that did not author or edit the audited change. If that reviewer edits the change, its clean-review authority for the edited change is spent.

Independent verification evidence must start from explicit scope and separate covered and not-covered claims. Runtime, browser, UAT, release, marketplace, and installed-plugin cache claims require their own named evidence.

Public skill approval remains blocked until independent clean review or maintainer acceptance exists for the relevant public-surface claim. Maintainer acceptance is required before this shared `skill-audit` reference can become a public `skill-audit` skill.

## Eval Coverage

Public skill additions and material skill changes need focused eval coverage proportional to risk:

- positive fixtures for the intended trigger or workflow;
- negative fixtures for should-not-trigger cases;
- route-conflict negatives against neighboring public skills and direct answers;
- hard negatives for the most dangerous overclaims.

At minimum, public skill additions must include hard negatives that fail when:

- the skill author approves its own public/material skill change;
- a shared audit reference is treated as a public skill before maintainer acceptance;
- trigger, should-not-trigger, or hard-negative eval review is skipped.

Eval parse checks and targeted fixture inspection are source-validation evidence only. They do not prove installed-plugin runtime behavior unless the installed plugin root, cache/source refresh or equivalence evidence, and run scope are separately named.
