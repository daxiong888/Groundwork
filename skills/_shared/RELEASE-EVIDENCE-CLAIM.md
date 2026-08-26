Target Reader: Groundwork verifiers, dispatch package authors, implementers, handoff authors, and reviewers.
Reader Action Needed: Use this shared object whenever a runtime, cache, release, UAT, marketplace, installed-plugin, or cache-refresh claim is made or explicitly scoped out.
Decision Supported: Whether a claim has direct, claim-specific evidence or must remain unverified/not applicable.
Artifact Type: shared evidence claim contract.
Source of Truth: `skills/verify/SKILL.md`, `skills/dispatch/DISPATCH-PACKAGE.md`, and `skills/_shared/RUNTIME-CAPABILITY.md` evidence-boundary rules.
Scope: Machine-readable evidence inventory for runtime/cache/release/UAT/marketplace/cache-refresh claims.
Out of Scope: Running checks, refreshing plugin caches, publishing releases, approving UAT, or proving customer readiness by itself.
Evidence Level: Source contract only. A populated object does not create evidence; it binds evidence produced by separately authorized direct activity.
Safe to Share / Redaction Notes: Safe to share as-is; redact private paths, tokens, private URLs, credentials, customer data, and sensitive logs before embedding real evidence.

Use this exact object when a material claim touches runtime, cache, release, UAT, marketplace, installed-plugin, or cache-refresh evidence:

```yaml
release_evidence_claim:
  claim_type: runtime | cache | release | uat | marketplace | cache_refresh | not_applicable
  claim: ""
  evidence_status: verified | unverified | not_applicable
  evidence_class: release_runtime_verification | claim_specific_direct_evidence | not_applicable
  installed_plugin_root: ""
  source_root: ""
  cache_or_source_refresh: {method: refresh_step | source_equivalence | not_run | not_applicable, evidence: ""}
  run_scope: targeted | full | not_run | not_applicable
  commands_or_trials: []
  receipt_binding: {authorization: "", released_package_digest: "", task_or_fixture_hash: "", expectation_source_hash: "", installed_source_equivalence: "", runtime_environment_identity: "", direct_outcome: "", validity: "", scope: ""}
  limitations: []
```
## Candidate / Release Firewall

> [!IMPORTANT]
> A Plugin Candidate Trial receipt has `evidence_class: candidate_direction`. It compares a Baseline and Candidate for a human proposal decision only. It must not verify runtime, cache, marketplace, release, UAT, customer readiness, or an installed package. Human promotion, an A/B material win, package equivalence, or a claim that the scopes match does not cross this boundary.

A verified Groundwork runtime/cache/marketplace/cache-refresh behavior claim requires a separately authorized, directly executed receipt with `evidence_class: release_runtime_verification`. The receipt must bind the released package digest, task or fixture hash, original acceptance/invariant source hash, installed/source equivalence, runtime and environment identity, direct outcome, validity, scope, and limitations. If any required binding is absent or the direct activity did not run, set `evidence_status: unverified` and name the gap. The Candidate Trial runner is not a release phase or canonical release evidence; an authorized host may produce a direct receipt, but prose cannot manufacture one.
## Rules

- Documentation, schemas, fixtures, PRDs, issue packs, implementation summaries, handoffs, wikis, diffs, source tests, package builds, Candidate Trial receipts, hook telemetry, and clean review are not direct runtime/release/UAT evidence.
- `evidence_status: verified` requires named qualifying evidence for the exact claim. Groundwork plugin-bound claims must include the installed plugin root, independent source root, refresh/equivalence evidence, targeted/full scope, direct commands or trials, complete receipt binding, and limitations.
- `evidence_status: unverified` must name at least one concrete limitation. Record incomplete or non-qualifying activity without upgrading the status.
- `claim_type: not_applicable`, `evidence_status: not_applicable`, and `evidence_class: not_applicable` must appear together. Use `not_applicable` for roots, refresh method/evidence, run scope, and receipt fields; keep `commands_or_trials: []`.
- Installed/source equivalence compares complete independent roots. Identical, ancestor/descendant, realpath-alias, excluded, normalized, partial, dry-run, or no-op comparisons do not qualify.
- Runtime/environment identity must bind the launcher and relevant non-secret execution controls. A debug hook-trust bypass, untrusted launcher, mutable workspace, zero-execution result, empty output, or unverifiable environment leaves the claim `unverified`.
- Generic `release` claims require a separate maintainer decision in addition to direct runtime evidence. Generic `uat` claims require their claim-specific canonical UAT evidence. Non-plugin UAT may use `installed_plugin_root: not_applicable` and refresh `not_applicable`, but still requires a concrete source root, scope, direct trial, and `evidence_class: claim_specific_direct_evidence`.
- The final response cannot create observed evidence merely by writing `passed`, `verified`, `runtime`, or a command name. Evidence must come from user-provided source truth, an inspected canonical record, or completed tool/runtime activity outside the claim text.
- Release readiness is not inferred from PRD acceptance, issue-pack completion, fixture pass, clean review, source-validation checks, package completeness, Candidate promotion, or Codex App Handoff packaging alone.
## Conditional UAT Evidence Window

After the required `release_evidence_claim`, add this block when UAT behavior is attributed to a fix/artifact/deployed version, the environment can change, the run crosses sessions, or a finding is fixed, redeployed, and rerun:

```text
UAT Evidence Window
- Claim / Delivery Scope:
- Relevant SUT Fingerprint:
- Preconditions:
- Window Stability:
- Coverage Basis:
- Result / Missing:
- Rerun Of / Supersedes:
```

Bind only causally relevant SUT identities. Use exactly one stability value: `stable`, `changed|restart_required`, `unverified`, or `observed_at:<id>|stability_unverified`. Partition or invalidate evidence after an identity change and create a new fingerprint/window after redeploy. The block binds inspected evidence; it is not deployment, runtime, browser, UAT, or release evidence by itself.
