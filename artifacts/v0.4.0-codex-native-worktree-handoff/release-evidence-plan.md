# V040-009 Release Evidence Plan

Target Reader: Groundwork maintainers, verification reviewers, release coordinators, and V040-010 execution agents.
Reader Action Needed: Use this plan to decide what evidence must exist before any v0.4.0 runtime, cache, release, UAT, marketplace, cache-refresh, or handoff-trial claim can be marked verified.
Decision Supported: Whether a claim is backed by release-gate evidence, remains unverified, or is not applicable.
Artifact Type: release evidence plan
Source of Truth: `docs/prd-v0.4.0-codex-native-worktree-handoff-alignment.md` FR-408 / AC-408 / release gates and V040-009 / V040-010 in `artifacts/v0.4.0-codex-native-worktree-handoff/issue-map.md`.
Scope: Claim boundary schema, required handoff trial fields, release-gate evidence separation, and V040-010 execution handoff.
Out of Scope: Executing Codex App Handoff, creating worktrees, running real handoff trials, refreshing plugin cache, publishing marketplace artifacts, claiming release readiness, UAT readiness, runtime readiness, or cache equivalence.
Evidence Level: Documentation and evidence-planning only. Runtime, cache, release, marketplace, UAT, cache-refresh, and Codex App Handoff execution evidence remain unverified until V040-010 or a later release-gate task records real evidence.
Safe to Share / Redaction Notes: Safe to share as a planning artifact. It contains schema fields and file paths only; no secrets, credentials, private URLs, browser cookies, PII, logs, or production data.

## Canonical Boundary

`release_evidence_claim` is the only supported shape for runtime, cache, release, UAT, marketplace, or cache-refresh readiness claims in this workstream:

```yaml
release_evidence_claim:
  claim_type: runtime | cache | release | uat | marketplace | cache_refresh | not_applicable
  claim: ""
  evidence_status: verified | unverified | not_applicable
  installed_plugin_root: ""
  source_root: ""
  cache_or_source_refresh:
    method: refresh_step | source_equivalence | not_run | not_applicable
    evidence: ""
  run_scope: targeted | full | not_run | not_applicable
  commands_or_trials: []
  limitations: []
```

Documentation, schema, fixture, PRD, issue-pack, package-generation, and clean-review evidence can support contract conformance. They do not verify runtime, cache, release, UAT, marketplace, cache-refresh, or Codex App Handoff execution claims by themselves.

For V040-009, the current claim state is:

```yaml
release_evidence_claim:
  claim_type: release
  claim: "v0.4.0 native worktree handoff alignment is release-ready"
  evidence_status: unverified
  installed_plugin_root: ""
  source_root: "/Users/daxiong/.codex/worktrees/e318/Groundwork"
  cache_or_source_refresh:
    method: not_run
    evidence: "V040-009 defines docs/schema boundaries only; no plugin cache refresh or source/cache equivalence check is in scope."
  run_scope: not_run
  commands_or_trials: []
  limitations:
    - "Real Local to Worktree and Worktree to Local Codex App Handoff trials are delegated to V040-010."
    - "Codex App Handoff execution evidence is separate from Groundwork package/schema evidence."
    - "Release readiness is not inferred from PRD acceptance, issue-pack completion, fixture pass, or documentation/schema edits."
```

## Required Handoff Trial Fields

Each real trial collected by V040-010 must record:

- `trial_id`: stable identifier for the trial.
- `direction`: `local_to_worktree` or `worktree_to_local`.
- `executor`: user, Codex App, runtime adapter, or other actor that performed the actual Handoff operation.
- `execution_surface`: Codex App Handoff surface used, including whether the operation was user-approved or user-performed.
- `base_ref`: branch, tag, or ref used before the trial.
- `base_commit`: commit hash before the trial.
- `source_root`: repository/source root used by the trial.
- `installed_plugin_root`: installed plugin root when the claim depends on plugin runtime/cache behavior.
- `cache_or_source_refresh`: refresh step, source equivalence evidence, or explicit not-run reason.
- `native_context_available`: thread, worktree, associated worktree, and handoff context that the Codex App surface actually exposes.
- `native_context_unavailable`: native IDs, paths, or state not exposed by the surface, recorded without inventing values.
- `handoff_package_path`: path to the Groundwork package used to continue the task.
- `changed_files`: changed files observed or transferred when applicable.
- `commands_or_trials`: commands, UI operations, screenshots, logs, or trial notes that directly evidence the operation.
- `evidence_status`: `verified`, `unverified`, or `not_applicable` for the specific claim.
- `open_risks`: unresolved runtime, git, package, source/cache, UAT, release, or data risks.
- `closeout_result`: continued, blocked, discarded, merged, no-op, or human-decision result, with evidence.
- `limitations`: scope limits and missing checks.

## V040-010 Delegation

V040-010 owns actual real handoff trial execution and evidence collection:

- one Local to Worktree trial;
- one Worktree to Local trial;
- any user approval or user-performed Codex App Handoff operation needed for those trials;
- any release-gate decision that depends on trial evidence.

V040-009 does not execute Handoff, does not create Codex App worktrees, does not refresh plugin cache, and does not claim runtime/cache/release/UAT/marketplace readiness. Its output is limited to claim schema, documentation, and this evidence plan.

## Review Checklist

- Every runtime, cache, release, UAT, marketplace, or cache-refresh claim has a `release_evidence_claim`.
- Documentation and schema-only claims use `evidence_status: unverified` or `not_applicable`.
- Verified runtime/cache claims name installed plugin root, source root, refresh/equivalence method, run scope, commands or trials, and limitations.
- Release readiness is not inferred from PRD acceptance, issue-pack completion, fixture pass, package completeness, or clean review.
- Codex App Handoff execution evidence is recorded separately from Groundwork package/schema evidence.
- Real handoff trials remain delegated to V040-010 until trial evidence exists.
