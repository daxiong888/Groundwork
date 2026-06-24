Target Reader: Groundwork designers/planners, implementers, clean reviewers, verifiers, coordinators, dispatchers, and handoff authors.
Reader Action Needed: Keep material design, implementation, clean review, verification, and closeout authority separated.
Decision Supported: Whether a role may make, review, verify, or close a material change, and which evidence labels must appear in final reports.
Artifact Type: shared guardrail
Source of Truth: docs/prd-v0.5-prototype-first-skill-expansion.md section 9 and artifacts/v0.5-prototype-first-skill-expansion/issue-map.md V050-001A.
Scope: Role identities, materiality threshold, evidence taxonomy, closeout fields, and hard stops for same-session authority collapse.
Out of Scope: Creating public skills, spawning reviewers, implementing runtime execution, approving releases, or replacing skill-specific output contracts.
Evidence Level: Local PRD and issue-map contract evidence only; runtime, browser, UAT, release, marketplace, and cache evidence are not implied.
Safe to Share / Redaction Notes: Safe to share as-is; contains no secrets, credentials, PII, logs, or private payloads.

# Role Separation

## Core Rule

The same AI role/session that designs or implements a material change must not be the authority that clean-reviews, independently verifies, or accepts that same change.

Self-checks are useful implementation hygiene. They are not clean review, independent verification, readiness evidence, UAT evidence, release evidence, or customer acceptance.

```text
self-check evidence != clean review evidence
self-run tests != independent verification evidence
implementation summary != acceptance evidence
same-session review != independent clean review
same-session design -> implementation -> verification != allowed material closeout
```

## Materiality Threshold

Role separation is required when the change affects any of these areas:

- public skill surface or skill-routing policy;
- shared guardrails;
- runtime, router, selector, or model policy;
- release, UAT, customer, runtime, browser, marketplace, or cache-refresh readiness claims;
- schema, API, security, permissions, privacy, data correctness, or migrations;
- broad eval behavior;
- frontend/backend contract truth;
- cross-module workflow behavior;
- skill-quality approval or public-skill acceptance.

Non-material bounded edits may proceed in the same session after source truth is accepted, but final reports must label the evidence as self-check only and must not claim independent readiness.

## Role Authority

### Designer / Planner

May produce PRDs, decision maps, prototypes, architecture options, task slices, or skill designs.

Must not implement, clean-review, independently verify, or approve its own material design unless a maintainer has accepted the design or an independent accepted source package exists. Even after implementation is allowed, the designer/planner still cannot clean-review or independently verify that material change.

### Implementer

May inspect source truth, edit scoped files, run tests/checks, self-review, and report local evidence.

Must label self-run checks as `Self-check Evidence`. Must not claim `Clean Review Evidence`, `Independent Verification Evidence`, readiness, release, UAT, customer, marketplace, runtime, browser, or cache-refresh evidence unless that evidence was produced by the correct independent role or tool.

### Clean Reviewer

Must be read-only for the reviewed change. It may assess scope, source conformance, diff quality, regression risk, missing tests, git boundary, and whether the implementation evidence supports a follow-up verification attempt.

If the clean reviewer fixes a finding or otherwise becomes an implementer, its clean-review authority for that material change is spent. A new independent clean reviewer is required before a clean-review pass can be claimed.

### Verifier

Must start with explicit scope and separate covered/not-covered evidence.

Must block or mark `unverified` when a material readiness claim relies only on same-session design, same-session implementation, self-checks, implementation summaries, old evidence, or prompt text.

### Coordinator

May route work, synthesize received evidence, maintain dependency order, and identify the next independent role.

Must not invent evidence, upgrade self-checks into independent evidence, claim clean review or verification it did not receive, or close a material change when required independent evidence is absent.

## Evidence Taxonomy

- `Self-check Evidence`: checks, tests, review notes, and consistency inspection performed by the same role/session that designed or implemented the change.
- `Clean Review Evidence`: read-only fresh review evidence from an independent reviewer that did not edit the reviewed material change.
- `Independent Verification Evidence`: verification evidence from an independent verifier or tool-backed run that starts from explicit scope and covers the claimed readiness boundary.
- `Runtime Evidence`: command, adapter, or runtime output proving runtime behavior for the specific claim.
- `Browser Evidence`: browser, UI automation, screenshot, DOM, network, console, or visual evidence proving the specific browser/UI claim.
- `UAT Evidence`: explicit user/customer/UAT environment evidence for the UAT claim.
- `Release Evidence`: release-gate evidence for the release claim.

## Required Closeout Fields

Material implementation, verification, dispatch, handoff, prototype contract-boundary, and coordinator closeout reports must include these fields when role separation applies:

```text
Role:
Design Source:
Self-check Evidence:
Clean Review Evidence:
Independent Verification Evidence:
Runtime Evidence:
Browser Evidence:
UAT Evidence:
Release Evidence:
Readiness Boundary:
Required Next Independent Role:
```

Use `not applicable` only when the role-separation materiality threshold is not met. Use `not provided`, `missing`, `unverified`, or `blocked` when the threshold applies but evidence is absent.

## Hard Stops

Block or mark unverified when:

- same-session self-check is offered as independent readiness evidence;
- a reviewer fixes its own finding and declares clean review passed;
- a same-session designer implements and independently verifies its own material design;
- a skill author approves its own material skill-quality change;
- a coordinator closeout package omits independent clean review or independent verification status for a material change.
