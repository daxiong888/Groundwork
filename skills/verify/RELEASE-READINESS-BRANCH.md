# Release Readiness Branch

Target Reader: Codex running `verify` for runtime, cache, release, UAT, customer, marketplace, installed-plugin, or cache-refresh claims.
Reader Action Needed: Require separate release/runtime/cache evidence and avoid upgrading source-validation checks into readiness.
Decision Supported: Whether a readiness claim has qualifying evidence or must remain unverified, partial, failed, or blocked.
Artifact Type: branch-specific verification reference
Source of Truth: `skills/_shared/RELEASE-EVIDENCE-CLAIM.md`, `skills/_shared/RUNTIME-CAPABILITY.md`, and `skills/verify/SCOPE-EVIDENCE-TEMPLATE.md`.
Scope: Release evidence claims, runtime/cache boundaries, installed plugin evidence, marketplace evidence, and UAT/customer readiness.
Out of Scope: Publishing releases, refreshing plugin cache, executing runtime tools, deploying, mutating remotes, or approving UAT/release.
Evidence Level: Source-validation policy only unless qualifying runtime/cache/release evidence is named in the active verification.
Safe to Share / Redaction Notes: Safe to share as-is; contains no secrets, credentials, PII, private logs, or production payloads.

## Required Evidence

When verifying runtime, cache, release, UAT, marketplace, installed-plugin, or cache-refresh claims, require the shared `release_evidence_claim` object from `skills/_shared/RELEASE-EVIDENCE-CLAIM.md` for each material claim.

Apply `EB-RUNTIME-001`, `EB-CACHE-001`, and `EB-RELEASE-001` from `skills/_shared/EVIDENCE-BOUNDARY.md`, and apply `skills/_shared/NON-EXECUTOR-BOUNDARY.md` before accepting any execution, cache-refresh, release, UAT, or customer claim.

Load `RUNTIME-CAPABILITY-BRANCH.md` when the claim also depends on model/runtime selection, selector enforcement, runtime mismatch, or runtime/tool capability status.

This branch runs as `verify-strict`. Start from the current claim and current qualifying evidence. Do not compensate for missing current `dist/`, installed cache, runtime/browser evidence, release evidence, or user-provided evidence by sweeping historical materials.

A verified runtime or cache claim must name:

- installed plugin root;
- local source root;
- cache/source refresh method or source-equivalence evidence;
- run scope, such as targeted or full;
- commands or runtime trials used;
- limitations.

## Branch Rules

- Documentation, schema, fixture, PRD, issue-pack, CSV parse, or git diff checks alone are source-validation evidence.
- Source-validation evidence must set runtime, cache, release, UAT, marketplace, and cache-refresh evidence to `unverified` or `not_applicable` unless qualifying evidence is named.
- Missing current `dist/`, installed cache, cache/source equivalence, runtime/browser evidence, release evidence, or user-provided evidence must be reported under `Not Covered`, `Unverified Claims`, or `blocked needs-info`.
- Historical baselines, old release notes, old handoffs, old runtime trials, and `evals/baselines/` may orient a strict verification only when the user explicitly asks for historical, eval, baseline, release-evidence, or Groundwork-maintainer evidence, or when a current source artifact cites a specific baseline path.
- Historical evidence never replaces current qualifying runtime, cache, release, UAT, marketplace, installed-plugin, or cache-refresh evidence.
- Release readiness is not inferred from PRD acceptance, issue-pack completion, fixture pass, package completeness, clean review, or implementation self-check.
- Codex App Handoff execution evidence is separate from Groundwork package/schema evidence and must be represented as commands or trials before it can support a release or handoff-readiness claim.
- Verify reports evidence sufficiency only; it does not refresh cache, publish release artifacts, approve UAT, or perform customer acceptance.
