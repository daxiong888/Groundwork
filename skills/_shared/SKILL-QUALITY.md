# Skill Quality Gate

Target Reader: Groundwork maintainers, skill authors, implementers, clean reviewers, and verifiers evaluating public skill changes.
Reader Action Needed: Use this checklist before adding a public skill or approving a material skill-quality change.
Decision Supported: Whether a candidate belongs in the public skill surface, a shared reference, a branch/workflow lens, router behavior, or a one-off guide.
Artifact Type: shared guardrail.
Source of Truth: `docs/prd-v0.5-prototype-first-skill-expansion.md` FR-501 through FR-504, FR-542, section 12, V050-001, and V050-006A in `artifacts/v0.5-prototype-first-skill-expansion/issue-map.md`.
Scope: Public skill expansion policy, shared skill-quality checks, routing/eval gates, and evidence boundaries for public skill merge decisions.
Out of Scope: Creating public skills, deciding release readiness, claiming installed-plugin runtime behavior, changing plugin metadata, or replacing clean review and independent verification.
Evidence Level: Source-validation policy. This file is local guidance only until separately reviewed and verified.
Safe to Share / Redaction Notes: Safe to share as-is; contains no secrets, credentials, private payloads, or personal data.

## Public Surface Rule

Groundwork may expand the public skill surface only when an accepted PRD, scoped issue, or maintainer directive explicitly expands that surface and the candidate passes the skill-quality, routing, and eval gates below.

Do not create `skills/<candidate>/SKILL.md` for a behavior that can be handled as a shared reference, branch/workflow lens, router behavior, or one-off guide.

## Candidate Classification

- Public skill: a top-level `skills/<name>/SKILL.md` contract with a distinct invocation moment, trigger contract, should-not-trigger cases, failure branches, and eval coverage.
- Shared reference: a reusable policy, checklist, template, or workflow under `skills/_shared/` that existing public skills can cite without expanding the public surface.
- Branch/workflow lens: a bounded behavior inside an existing public skill route, used when the user is already in that skill's workflow.
- Router behavior: routing, dispatch, or preflight logic that selects an existing workflow or runtime package without creating a user-invoked public skill.
- One-off guide: documentation for infrequent setup or maintainer decisions that does not justify a persistent public trigger.

## Public Skill Checklist

A new public skill may be merged only when all of these are true:

1. Accepted scope explicitly authorizes public surface expansion.
2. The skill has a distinct invocation moment that is not already owned by an existing skill.
3. The leading name is not merely a synonym for an existing public skill.
4. The behavior cannot be safely implemented as a shared reference, branch/workflow lens, router behavior, or one-off guide.
5. The trigger contract and should-not-trigger cases are clear enough for routing review.
6. Completion criteria and failure branches are checkable.
7. Evidence boundaries state what the skill can and cannot claim, including runtime, browser, UAT, release, customer, marketplace, and installed-plugin cache claims.
8. Minimum eval coverage exists before merge: at least three positive fixtures, three negative fixtures, and hard-negative fixtures for the candidate's most dangerous overclaims.
9. Route-conflict negatives prove the skill does not steal direct answers, accepted implementation work, verification, handoff, or another public skill's route.
10. A separate clean review or skill-quality review checks the candidate before merge; the author or implementer self-check is not final approval.

## Required Skill-audit Lens

Public skill additions and material skill changes must use `skills/_shared/SKILL-AUDIT.md` as the shared audit workflow/reference before they can be accepted.

`skill-audit` is classified as a required shared workflow/reference first. It must not be promoted to `skills/skill-audit/SKILL.md` or treated as a public skill unless a later accepted publicization slice proves direct invocation value, routing negatives pass, and maintainer acceptance explicitly authorizes public exposure.

The shared audit lens covers invocation class, trigger description, workflow, information hierarchy, progressive disclosure, duplication, failure branches, evidence boundary, and eval coverage. Author self-audit is useful self-check evidence only; public skill approval, material skill-quality approval, and final acceptance require an independent clean review or maintainer acceptance according to `skills/_shared/ROLE-SEPARATION.md`.

## Hard-negative Expectations

Every public skill candidate must include hard negatives that fail when:

- a candidate without a distinct invocation moment is approved;
- a shared-reference candidate is promoted to `skills/<name>/SKILL.md` without accepted public exposure;
- trigger or should-not-trigger coverage is missing;
- routing negatives are skipped or treated as optional;
- hard-negative eval expectations are omitted;
- a public skill addition skips trigger, should-not-trigger, or hard-negative eval review;
- the shared `skill-audit` reference is treated as a public skill before accepted public exposure and maintainer acceptance;
- prompt text alone is treated as runtime, selector, browser, UAT, release, customer, marketplace, or installed-plugin cache evidence;
- the author or same-session implementer approves their own material skill-quality change as final.

## Evidence Boundary

Source edits, docs checks, CSV parse checks, and local fixture inspection are source-validation evidence only. They do not prove installed-plugin runtime behavior, marketplace packaging, selector enforcement, UAT readiness, release readiness, or customer readiness unless the specific runtime/cache/marketplace evidence is separately produced and named.
