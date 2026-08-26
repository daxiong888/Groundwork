# Skill Quality Gate

Target Reader: Groundwork maintainers, skill authors, implementers, clean reviewers, and verifiers reviewing public skill changes.
Reader Action Needed: use before adding a public skill or approving material skill-quality changes.
Decision Supported: whether behavior belongs in public skill surface, shared reference, branch/workflow lens, router behavior, or one-off guide.
Artifact Type: shared guardrail.
Source of Truth: `docs/prd-v0.5-prototype-first-skill-expansion.md` FR-501 through FR-504, FR-542, section 12, V050-001, and V050-006A.
Scope: public skill expansion, routing/source/behavior gates, and evidence boundaries.
Out of Scope: creating public skills, release readiness, installed-plugin runtime behavior, plugin metadata changes, or replacing clean review/verification.
Evidence Level: source-validation guidance only until independently reviewed.

## Public Surface Rule

Create `skills/<candidate>/SKILL.md` only when an accepted PRD, scoped issue, or maintainer directive explicitly expands the public surface and the candidate passes this gate plus applicable routing/source/behavior checks.

Prefer a shared reference, branch/workflow lens, router behavior, or one-off guide when there is no distinct public invocation moment.

`FIRST-PRINCIPLES.md` and `ADVERSARIAL-REVIEW.md` are shared lenses by default. Do not promote them to public skills unless later accepted scope proves direct invocation value, route-conflict negatives, hard-negative behavior cases, clean skill-quality review, and maintainer acceptance.

## Classification

- Public skill: top-level `skills/<name>/SKILL.md` with distinct invocation, trigger/negative cases, failure branches, and checkable behavior cases.
- Shared reference: reusable policy, checklist, template, or workflow under `skills/_shared/`.
- Branch/workflow lens: bounded behavior inside an existing public route.
- Router behavior: selection, dispatch, or preflight logic that chooses existing workflow/runtime package.
- One-off guide: infrequent setup or maintainer documentation without persistent trigger.

## Merge Checklist

A public skill or material skill change may merge only when all apply:

1. Accepted scope explicitly authorizes the public-surface impact.
2. Invocation moment is distinct and not a synonym for an existing public skill.
3. Behavior cannot be safely handled as shared reference, branch lens, router behavior, or one-off guide.
4. Trigger and should-not-trigger cases are clear enough for routing review.
5. Completion criteria and failure branches are checkable.
6. Evidence boundaries cover runtime, browser, UAT, release, customer, marketplace, and installed-plugin/cache claims.
7. Minimum behavior-case coverage exists: three positive, three negative, plus hard negatives below.
8. Route-conflict negatives prove the skill does not steal direct answers, accepted implementation, verification, handoff, or neighboring public routes.
9. A separate clean review or skill-quality review checks the candidate; author/implementer self-check is not final approval.

For project-knowledge skills such as `wiki`, hard negatives must prove notes, page source lists, search/index/graph output, stale pages, uncited claims, and missing wiki roots are not upgraded into source truth, contract truth, implementation authority, verification evidence, release/UAT/customer readiness, marketplace evidence, installed-plugin evidence, or cache-refresh evidence.

## Required Audit Lens

Material public skill changes must use `skills/_shared/SKILL-AUDIT.md` before acceptance.

`skill-audit` is a required shared workflow/reference. Do not promote it to `skills/skill-audit/SKILL.md` unless a later accepted publicization slice proves direct invocation value, routing negatives pass, and maintainer acceptance authorizes public exposure.

Author self-audit is self-check only. Public skill approval, material skill-quality approval, and final acceptance require independent clean review or maintainer acceptance under `skills/_shared/REVIEW-LOOP.md`.

## Hard Negatives

Hard-negative source/behavior checks must fail when:

- no distinct invocation moment exists;
- a shared-reference candidate is promoted without accepted public exposure;
- trigger, should-not-trigger, route-conflict, or hard-negative behavior coverage is missing;
- `skill-audit` is treated as public before accepted public exposure and maintainer acceptance;
- wiki synthesis, page source lists, stale pages, uncited claims, missing roots, or search/index/graph output become source/contract/implementation/verification/release/UAT/customer/marketplace/installed-plugin/cache truth;
- prompt text alone is treated as runtime, selector, browser, UAT, release, customer, marketplace, or installed-plugin/cache evidence;
- first-principles reasoning or adversarial self-check is treated as clean review, independent verification, runtime/browser/UAT/release/customer/marketplace/installed-plugin/cache evidence, or public-skill authorization;
- author or same-session implementer approves their own material skill-quality change as final;
- any review exception violates the materiality, role-authority, low-risk eligibility, or evidence-label rules in `skills/_shared/REVIEW-LOOP.md`.

## Evidence Boundary

Source edits, docs checks, ordinary unit tests, and fixture inspection are source-validation evidence only. They do not prove installed-plugin runtime behavior, marketplace behavior, selector enforcement, UAT readiness, release readiness, or customer readiness without separately authorized direct evidence.
