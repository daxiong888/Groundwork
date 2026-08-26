Target Reader: skill authors, implementers, clean reviewers, verifiers, coordinators, and maintainers auditing public skill additions or material skill changes.
Reader Action Needed: apply this workflow before approving public skill additions or material skill-quality changes.
Decision Supported: whether trigger clarity, hierarchy, progressive disclosure, failure handling, behavior evidence, and role-separated evidence are sufficient.
Artifact Type: shared workflow/reference.
Source of Truth: `docs/prd-v0.5-prototype-first-skill-expansion.md` section 12, FR-542, AC-A3, AC-C1, AC-C2, AC-C7, AC-D1, and V050-006A.
Scope: public skill candidates, public skill additions, and material skill changes.
Out of Scope: creating public `skill-audit`, accepting public exposure, replacing clean review/maintainer acceptance, or claiming runtime/browser/UAT/release readiness.
Evidence Level: source-validation workflow. Self-audit is self-check unless produced by an independent read-only clean reviewer.

# Skill Audit

## Invocation Class

`skill-audit` is a required shared workflow/reference before public skill additions and material skill changes are accepted. Do not create or rely on `skills/skill-audit/SKILL.md` unless a later accepted publicization slice proves direct invocation value, routing negatives pass, and maintainer acceptance authorizes public exposure.

Classify first:

- Public model-invoked skill: top-level `skills/<name>/SKILL.md`.
- User-invoked public skill: distinct user-facing invocation.
- Shared reference: reusable guardrail/checklist/template/workflow under `skills/_shared/`.
- Branch/workflow lens: bounded branch inside an existing public skill.
- Router behavior: selection/dispatch behavior that should not become public skill surface.

## Trigger Audit

For public candidates and material trigger changes, verify:

- leading name/phrase is stable and distinct;
- should-trigger cases describe a real invocation moment;
- should-not-trigger cases protect direct answers, accepted implementation, verification, handoff, dispatch, and neighbors;
- route-conflict negatives prove established routes are not stolen;
- public exposure is blocked when shared reference, branch lens, router behavior, or one-off guide fits better.

## Workflow

1. Confirm accepted source truth and public-surface impact.
2. Classify invocation class.
3. Review trigger and should-not-trigger coverage.
4. Review workflow, stop condition, and completion criteria.
5. Review hierarchy and progressive disclosure.
6. Remove duplicated guidance, no-op prose, and hidden route expansion.
7. Review failure branches.
8. Apply `skills/_shared/EVIDENCE-BOUNDARY.md` and role separation.
9. Review positive, negative, route-conflict, and hard-negative behavior evidence appropriate to the scoped change.
10. Label evidence role: self-check, clean review, independent verification, or maintainer acceptance.

## Hierarchy And Progressive Disclosure

Public `SKILL.md` keeps universal invocation rules. Branch-specific procedures, templates, detailed checklists, examples, and long domain references move to files loaded only when needed.

Shared cross-skill rules belong under `skills/_shared/`; candidate-specific detail belongs with the candidate only after public exposure is accepted.

Fail audit when simple routes require broad always-load context that can be split into focused references without losing correctness.

## Duplication

Remove duplicate trigger language, repeated role-separation prose, copied policy blocks, and no-op instructions. Prefer one canonical shared reference over divergent local copies.

## Failure Branches

Block, mark unverified, or return to implementation when:

- author audits and approves own public/material skill change as final;
- same-session self-check is offered as clean review, independent verification, readiness, final acceptance, or maintainer acceptance;
- clean reviewer edits the reviewed change and still claims clean review authority for that fixed change;
- shared reference is promoted to public skill surface without accepted exposure and maintainer acceptance;
- required trigger, should-not-trigger, route-conflict, or hard-negative behavior evidence is skipped;
- prompt text, source diff, or fixture inspection is used as runtime, browser, UAT, release, marketplace, installed-plugin/cache, or customer evidence;
- Spark or another fast/profile-limited run is used as final clean reviewer, verifier, public skill approver, release authority, or UAT authority.

## Evidence Boundary

Apply `EB-ROLE-001`, `EB-VERIFY-001`, `EB-RUNTIME-001`, `EB-CACHE-001`, and `EB-RELEASE-001` from `skills/_shared/EVIDENCE-BOUNDARY.md`.

Public skill approval remains blocked until independent clean review or maintainer acceptance exists for the public-surface claim. Maintainer acceptance is required before this shared `skill-audit` reference can become a public `skill-audit` skill.

## Behavior Evidence

Public skill additions and material skill changes need:

- positive cases for intended trigger/workflow;
- negative cases for should-not-trigger behavior;
- route-conflict negatives against neighbors and direct answers;
- hard negatives for dangerous overclaims.

These cases may be source-backed contract examples, ordinary deterministic tests, or a separately authorized Candidate Trial Pack. They do not imply a repository default suite, numeric score, or permanent case platform.

Minimum public-skill hard negatives fail when:

- author approves own public/material skill change;
- shared audit reference is treated as public before maintainer acceptance;
- required trigger, should-not-trigger, or hard-negative behavior review is skipped.

Source examples, deterministic tests, and fixture inspection are source-validation evidence only. Installed-plugin runtime behavior requires installed plugin root, cache/source refresh or equivalence evidence, and run scope.
