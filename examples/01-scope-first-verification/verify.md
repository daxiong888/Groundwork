# Verification Report: Scope-First Verification

Target Reader: Groundwork maintainer validating the scope-first verification case study.
Reader Action Needed: Review the claim-to-evidence mapping and decide whether the example is supported by repository evidence.
Decision Supported: Whether this is a real maintenance example rather than a hypothetical workflow.
Scope: Evidence already recorded in repository files for the v0.2.2/v0.2.3 `verify` hardening line.
Out of Scope: Re-running Codex runtime evals, refreshing plugin cache, or claiming current release readiness.
Evidence Level: Static repository evidence from changelog, skill files, and `evals/baselines/2026-05-25-v0.2.3-runtime-baseline.md`.

## Verification Scope

- In Scope: scope-first verification behavior and recorded v0.2.3 targeted closure evidence.
- Out of Scope: current plugin installation state, new runtime execution, release approval, and UAT approval.
- Covered: source docs, skill rules, changelog summary, and recorded runtime rows.
- Not Covered: a fresh runtime rerun for this example directory.
- Evidence Sources: `skills/verify/SKILL.md`, `skills/verify/SCOPE-EVIDENCE-TEMPLATE.md`, `skills/verify/LENSES.md`, `CHANGELOG.md`, and `evals/baselines/2026-05-25-v0.2.3-runtime-baseline.md`.
- User-visible Claim Being Verified: Groundwork has a real example where verification starts with explicit scope before readiness claims.

## Claim Evidence Matrix

| Claim / AC | Evidence | Result | Gap | Severity |
| --- | --- | --- | --- | --- |
| AC-1 and AC-2: final verification report starts with a full scope block | `skills/verify/SKILL.md` and `skills/verify/SCOPE-EVIDENCE-TEMPLATE.md` require the exact opening shape | pass | Fresh runtime is not rerun in this example | none |
| AC-3: specialized payloads stay after scope | `skills/verify/SKILL.md` names UI routing, contract review, QA failure, git boundary, approval gates, and subagent prompts as no-exception branches | pass | None for static evidence | none |
| AC-4: missing evidence remains explicit | `SCOPE-EVIDENCE-TEMPLATE.md` says missing tests, runtime/browser checks, data, environment, UAT, and customer validation remain unverified unless checked | pass | None for static evidence | none |
| AC-5: verdict vocabulary is bounded | `skills/verify/SKILL.md` and `SCOPE-EVIDENCE-TEMPLATE.md` use `pass`, `partial`, `fail`, and `blocked` | pass | None for static evidence | none |
| Targeted runtime closure exists | v0.2.3 baseline records targeted pass for `rel-002`, `gr-002`, `gr-005`, `gr-010`, and `gr-015` | pass | This example references recorded evidence rather than executing it again | P3 |

## Verdict

pass for repository-backed example status.

The example is supported as a historical Groundwork maintenance case. It is not a fresh release-readiness verification for the current checkout.

## Unverified Claims

- Current installed plugin cache behavior is not checked by this example.
- Current runtime behavior should be re-run before using this example as release-gating evidence.

