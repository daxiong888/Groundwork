Target Reader: Implementers, clean reviewers, verifiers, coordinators, dispatchers, and maintainers.
Reader Action Needed: Use this contract for materiality, role authority, clean-review evidence, remediation, re-review, and low-risk coordinator intake.
Decision Supported: Whether implementation evidence needs independent review, may use the low-risk intake exception, needs remediation or re-review, is blocked, or requires a human decision.
Artifact Type: shared guardrail
Source of Truth: This file is the canonical review contract; route-specific references may add triggers or output fields but must not redefine its authority, materiality, or evidence rules.
Scope: Materiality, fan-out base rules, role authority, review-loop states, evidence labels, low-risk eligibility, remediation, and forbidden authority upgrades.
Out of Scope: Runtime execution, automatic reviewer spawning, final readiness approval, release/UAT approval, archive, branch cleanup, commits, pushes, PRs, or tracker mutation.
Evidence Level: Source-validation policy only. This contract does not prove runtime, browser, UAT, release, marketplace, installed-plugin, cache-refresh, selector-enforcement, or customer readiness.
Safe to Share / Redaction Notes: Safe to share as-is; contains no secrets, credentials, PII, private logs, or production payloads.

# Review Loop

## Core Rule

The same role or session that designs or implements a material change must not be the authority that clean-reviews, independently verifies, or accepts that change. Self-checks remain useful implementation evidence, but they are not independent review or readiness evidence.

Material implementation follows this loop:

```text
implementation + self-check
-> fresh read-only clean review
-> scoped remediation when findings exist
-> self-check the remediation
-> fresh read-only clean review of the latest diff
-> verify/readiness only when the claimed boundary needs it
```

The loop governs evidence and authority; it does not prove that a reviewer, child thread, subagent, runtime, browser run, cache refresh, release gate, or remote mutation actually happened.

## Materiality and Fan-Out

Independent role separation and clean-review fan-out are required when a change affects any of these areas:

- a public skill, skill-routing policy, shared guardrail, adapter contract, package template, schema, shared fixture, state machine, or shared config;
- runtime, router, selector, model, hook, or installed-package policy;
- API/schema, security, permissions, privacy, data correctness, migration, or data-write behavior;
- broad eval behavior, cross-module workflow behavior, or frontend/backend contract truth;
- release, UAT, customer, runtime, browser, marketplace, cache-refresh, skill-quality, or public-surface approval.

Fan out when any additional trigger applies: a P0/P1 finding; customer-visible or release/UAT risk; validation skipped, failed, partial, environment-limited, or followed by a validation-fix iteration; missing or materially redacted diff/evidence; stale or compacted coordinator context; multiple concurrent returns; the user requested independent review; a reviewer edited the change; or a previous review became stale after a material fix.

Route-specific policies may add fan-out triggers but must not narrow this base. A non-material bounded edit may remain in the same session only as self-check evidence; it does not gain independent review or readiness status.

## Role Authority

- **Designer / Planner:** may shape the design and accepted source. It must not clean-review, independently verify, or approve its own material design. Acceptance by a maintainer may authorize implementation but does not make the designer an independent reviewer.
- **Implementer:** may inspect, edit, test, and self-review scoped work. Its checks are `Self-check Evidence`; it must not upgrade them to independent evidence.
- **Clean Reviewer:** a clean review requires a fresh-context independent reviewer that remains read-only for the reviewed change. If the reviewer edits, patches, or directly fixes a finding, it becomes an implementer and its clean-review authority is spent; a new independent reviewer is required.
- **Verifier:** starts from explicit claim scope and separates covered from not-covered evidence. It must block or mark unverified any readiness claim supported only by same-session work, self-checks, old evidence, or prompt text.
- **Coordinator:** may route and synthesize received evidence, but must not invent evidence, upgrade labels, or close material work while required independent evidence is missing.

Any material fix after clean review makes the previous clean review stale for the latest diff. Record `previous_review_stale_reason`, set `next_review_required: true`, and require fresh review.

For material work, reports name `Role`, `Self-check Evidence`, `Clean Review Evidence`, `Independent Verification Evidence`, `Readiness Boundary`, and `Required Next Independent Role`. Use `not applicable` only below the materiality threshold; use `missing`, `not provided`, `unverified`, or `blocked` when required evidence is absent.

## Evidence Rules

- `Self-check Evidence`: checks, tests, diff inspection, and conformance notes produced by the same role/session that designed or implemented the change.
- `Clean Review Evidence`: findings or pass evidence from a fresh read-only independent reviewer that did not edit the reviewed material. A finding must trace to supplied source truth, an AC, contract, invariant, or required evidence and name a consequence reachable through supported use, current data, or a stated trust boundary; `findings: []` is valid, and theoretical possibilities, optional confidence work, duplicate validation, style preferences, or manufactured P3s are not findings.
- `Independent Verification Evidence`: explicit-scope evidence from an independent verifier or qualifying tool-backed run for the claimed boundary.
- A clean-review pass means no grounded P0-P2 conformance finding remains within supplied scope; grounded P3 observations may accompany `pass` but are not remediation requirements. It is implementation-conformance evidence only, not final readiness, UAT, release, runtime, browser, merge, archive, branch cleanup, commit, push, PR, or customer approval. Requested security, migration, verification, role separation, fresh review after material remediation, and evidence boundaries remain required.

## Review Loop States

Use the smallest applicable state:

```text
self_check_complete
clean_review_pending
clean_review_passed
needs_remediation
remediation_in_progress
remediation_self_check_complete
blocked
human_decision
low_risk_coordinator_intake
```

Loop exit states are limited to `clean_review_passed`, `blocked`, `human_decision`, and `low_risk_coordinator_intake`.

Reviewable result packages carry:

```yaml
review_loop:
  status: "self_check_complete | clean_review_pending | clean_review_passed | needs_remediation | remediation_in_progress | remediation_self_check_complete | blocked | human_decision | low_risk_coordinator_intake"
  latest_material_change_id: ""
  previous_review_stale_reason: ""
  findings_addressed: []
  next_review_required: "true | false"
  next_route: "clean_reviewer | dispatch_write_task | verify | triage | human_decision | done"
```

Set `next_review_required: true` whenever the latest material change lacks current clean-review evidence. Source loop state in a review input package is context, not proof that review passed. Before requesting another check or review round, name the live uncertainty and how different outcomes change the next action; unchanged material, evidence, and claim scope stop only coordinator-generated confidence loops, while an explicit user request for another independent review remains a fan-out trigger.

## Low-Risk Coordinator Intake

`low_risk_coordinator_intake` is a narrow exception that may close coordinator intake only when all conditions hold:

- exactly one package is self-contained and does not depend on hidden parent context;
- the return is read-only/no-diff or changes 0-2 low-risk files in docs-only, tests-only, typo-only, non-shared config, or another explicitly justified low-risk class;
- validation status is `pass` or `not_applicable_with_reason`, with current evidence references;
- no materiality or fan-out trigger applies;
- the coordinator records its reason, evidence references, and remaining risks.

Record the decision explicitly:

```yaml
low_risk_coordinator_intake:
  eligible: "true | false"
  package_count: 1
  changed_files_count: "0-2 low-risk files"
  changed_file_classes: []
  validation_required:
    status: "pass | not_applicable_with_reason"
    evidence_refs: []
  coordinator_decision:
    reason: ""
    evidence_refs: []
    remaining_risks: []
```

This status is not `clean_review_passed`, independent verification, readiness, merge, archive, cleanup, commit, push, PR, runtime, browser, release, UAT, or final acceptance. If any eligibility field is missing or any disqualifier applies, use `clean_review_pending` or `blocked` and require fan-out.

## Remediation Flow

When review returns findings:

1. Keep review read-only and route writes through the owning implementation path.
2. Fix only cited findings or explicitly accepted gap-closure items.
3. Rerun the failed check or the smallest check proving the finding closed.
4. Record addressed findings, self-check evidence, checks not run, and remaining risks.
5. Mark the previous review stale when material files changed.
6. Route the latest diff to a fresh independent reviewer unless the complete low-risk exception applies.

Do not expand a review finding into unrelated cleanup or let the reviewer directly fix and approve the same material change.

## Hard Failures

- Self-review or self-run tests are labeled clean review or independent verification.
- A reviewer edits the change and still claims clean-review authority for it.
- A previous review is reused after a material fix.
- Low-risk intake is used for material work, without complete eligibility, or as clean-review/readiness evidence.
- A pass omits reviewed scope or covered/not-covered evidence, or a reviewer manufactures findings, severity, or a coordinator-generated repeat without a grounded violation, live evidence gap, or material delta.
- Prompt preference is presented as reviewer, subagent, child-thread, runtime, cache, or selector execution evidence.

## Skill Ownership

- `implement` owns implementation, scoped remediation, and self-check evidence.
- `dispatch` owns routing and may add route-specific fan-out mechanics without redefining this contract.
- A read-only clean reviewer owns clean-review findings.
- `verify` owns explicit-scope evidence sufficiency and readiness claims.
- `handoff` may preserve loop state but must not upgrade evidence or close the loop.
