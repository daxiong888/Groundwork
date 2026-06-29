Target Reader: Groundwork coordinators, dispatch package authors, clean-review routers, implementers, and maintainers.
Reader Action Needed: Decide whether a returned implementation package may stay in coordinator intake instead of fanning out to clean review.
Decision Supported: Whether `low_risk_coordinator_intake` is eligible, what evidence must be recorded, and what claims remain forbidden.
Artifact Type: shared guardrail
Source of Truth: `skills/_shared/REVIEW-LOOP.md`, `skills/dispatch/CLEAN-REVIEW-FANOUT.md`, and `skills/_shared/ROLE-SEPARATION.md`.
Scope: Low-risk coordinator-intake eligibility, disqualifiers, validation evidence, package fields, and forbidden authority upgrades.
Out of Scope: Clean review execution, runtime execution, archive, branch cleanup, merge approval, release/UAT approval, final readiness, or replacing independent review when fan-out triggers exist.
Evidence Level: Source-validation policy only. This contract does not prove runtime, browser, UAT, release, marketplace, installed-plugin, cache-refresh, selector-enforcement, or customer readiness.
Safe to Share / Redaction Notes: Safe to share as-is; contains no secrets, credentials, PII, private logs, or production payloads.

# Low-Risk Coordinator Intake

## Core Rule

`low_risk_coordinator_intake` is a narrow exception to fan-out. It can close the coordinator intake step for a small, self-contained return only when no fan-out trigger applies and current validation evidence is clear.

It is not `clean_review_passed`. It must not be serialized as clean review evidence, independent verification, release readiness, UAT readiness, archive readiness, branch cleanup readiness, merge approval, commit approval, push approval, PR approval, or final acceptance.

## Eligibility Shape

Record the decision in this shape when using the exception:

```yaml
low_risk_coordinator_intake:
  eligible: true | false
  package_count: 1
  changed_files_count: 0-2
  changed_file_classes:
    - docs_only | tests_only | typo_only | non_shared_config | source_code
  disallowed_if_any:
    - P0_or_P1
    - security_or_privacy
    - customer_visible
    - migration_or_data_write
    - public_interface_or_schema
    - shared_fixture_or_state_machine
    - shared_config
    - adapter_contract_or_package_template
    - validation_skipped_failed_partial
    - validation_fix_iteration
    - missing_or_redacted_needed_diff
    - coordinator_context_stale_or_compacted
    - multiple_concurrent_returns
    - user_requested_independent_review
  validation_required:
    status: pass | not_applicable_with_reason
    evidence_refs: []
  coordinator_decision:
    reason: ""
    evidence_refs: []
    remaining_risks: []
```

## Required Conditions

All must be true:

- exactly one package is being handled;
- the package is self-contained and does not depend on hidden parent context;
- changed files are limited to 0-2 low-risk files, or the package is read-only/no-diff;
- changed file classes are docs-only, tests-only, typo-only, or otherwise explicitly low risk;
- validation passed, or validation is not applicable with a specific reason;
- no fan-out trigger from `skills/dispatch/CLEAN-REVIEW-FANOUT.md` applies;
- the coordinator records the reason, evidence references, and remaining risks.

## Disqualifiers

Fan out to `clean_reviewer` or read-only `codex_subagent` when any condition is true:

- P0/P1 finding, severity, or blocker;
- security, privacy, migration, data write, customer-visible, release, or UAT risk;
- public interface, API/schema, shared fixture, state machine, shared config, adapter contract, package template, or public skill surface change;
- validation skipped, failed, partial, environment-limited, or followed by validation-fix iterations;
- diff or evidence is missing, redacted when needed for review, or not self-contained;
- coordinator context is stale, compacted, or handling multiple concurrent returns;
- the user asked for independent review;
- a clean reviewer edited files or a prior clean review is stale after a material fix.

## Output Boundary

When the exception is used, write:

```text
Review Loop:
- status: low_risk_coordinator_intake
- previous_review_stale_reason:
- findings_addressed:
- next_review_required: false
- next_route:
Clean Review Evidence: not applicable; low-risk coordinator intake recorded, not clean_review_passed
Readiness Boundary: coordinator intake only; no release, UAT, archive, cleanup, merge, runtime, or final readiness claim
```

Use `next_review_required: true` when any disqualifier exists or when the exception cannot be fully recorded.

## Hard Negatives

Fail or mark blocked when:

- multiple packages use low-risk coordinator intake;
- a package touching adapter contracts, package templates, shared fixtures, state machines, shared config, public interfaces, schema, migrations, or public skill surface uses low-risk intake;
- a P0/P1, security/privacy, customer-visible, data-write, migration, UAT, or release-risk package uses low-risk intake;
- validation is skipped, failed, partial, or environment-limited and the package still uses low-risk intake;
- a validation-fix iteration, stale clean review, or reviewer edit is closed with low-risk intake;
- low-risk intake is relabeled as `clean_review_passed` or used for release/UAT/archive/branch-cleanup/merge/final readiness.
