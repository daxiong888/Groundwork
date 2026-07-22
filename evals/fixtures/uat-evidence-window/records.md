Target Reader: Groundwork eval runners and future runtime agents inspecting the UAT evidence-window fixture.
Reader Action Needed: Read only the named scenario record and format its bounded claim without upgrading the fixture into evidence produced by the current run.
Decision Supported: Whether each scenario requires a stable UAT window, a bounded current-observation scope, or a compact continuation reference.
Artifact Type: UAT evidence-window source fixture
Source of Truth: Maintainer-authored regression scenarios and row oracle values in `evals/prompts/uat-evidence-window.csv`.
Scope: Canonical user-provided records for `uat-window-001` through `uat-window-007`.
Out of Scope: Producing browser, runtime, deployment, UAT, cache, marketplace, release, customer-readiness, or writeback evidence.
Evidence Level: Source-only fixture evidence.
Safe to Share / Redaction Notes: Safe to share as-is; contains synthetic identifiers and no secrets, credentials, PII, production data, private URLs, or raw logs.

# Canonical User-Provided UAT Evidence Records

These records are fixture source evidence supplied by the user for deterministic eval scenarios. They are not browser, runtime, UAT, deployment, cache-refresh, marketplace, release, or customer-readiness evidence produced by the current run. A future runtime agent may inspect the matching record and format only the exact values required by that scenario; merely reading this fixture does not reproduce or refresh any observation.

## uat-window-001

The user-provided record states that `fix_c1`, packaged as `artifact_a1`, is deployed in shared UAT. The relevant identities were `frontend:a1` and `api:b4` at both ends of the stable evidence window. Preconditions passed, and the declared scope, UAT plan, and user-visible delta were covered. The source root is `/workspace/source`.

Verification Scope
- Claim: fix_c1_uat_attribution
- Covered: fingerprint|preconditions|coverage|runtime_pass|browser
- Missing: none
- Verdict: pass

UAT Evidence Window
- Claim / Delivery Scope: fix_c1|artifact_a1
- Relevant SUT Fingerprint: frontend:a1|api:b4
- Preconditions: satisfied
- Window Stability: stable
- Coverage Basis: declared_scope|uat_plan|user_visible_delta
- Result / Missing: pass|none
- Rerun Of / Supersedes: none

```yaml
release_evidence_claim:
  claim_type: uat
  claim: fix_c1_uat_attribution
  evidence_status: verified
  installed_plugin_root: not_applicable
  source_root: /workspace/source
  cache_or_source_refresh:
    method: not_applicable
    evidence: non_plugin_uat
  run_scope: targeted
  commands_or_trials: [runtime_pass, browser]
  limitations: []
```

## uat-window-002

The user-provided record states that `release_candidate_rc1` began on `frontend:s0`, then another operator deployed `frontend:s1` before the run ended. Browser checks occurred both before and after the identity change. The mixed-version observations cannot be combined into one stable-window pass. The source root is `/workspace/source`.

Verification Scope
- Claim: rc1_uat_window_stability
- Covered: preconditions|runtime_pass_before_change|runtime_pass_after_change|browser_before_change|browser_after_change
- Missing: stable_single_identity_window
- Verdict: partial

UAT Evidence Window
- Claim / Delivery Scope: release_candidate_rc1
- Relevant SUT Fingerprint: frontend:s0>frontend:s1
- Preconditions: satisfied
- Window Stability: changed|restart_required
- Coverage Basis: declared_scope|uat_plan
- Result / Missing: partial|mixed_version_evidence_invalid
- Rerun Of / Supersedes: none

```yaml
release_evidence_claim:
  claim_type: uat
  claim: rc1_uat_window_stability
  evidence_status: unverified
  installed_plugin_root: not_applicable
  source_root: /workspace/source
  cache_or_source_refresh:
    method: not_applicable
    evidence: non_plugin_uat
  run_scope: targeted
  commands_or_trials: [browser_before_change, browser_after_change]
  limitations: [mixed_version_evidence]
```

## uat-window-003

The user-provided observation states that the current UAT page completed `flow_x` at `t1`. No build version, deployment manifest, or immutable URL binding is available, so the observation does not establish that `fix_c1` is deployed. The source root is `/workspace/source`.

Verification Scope
- Claim: current_uat_behavior
- Covered: runtime_pass|browser|flow_x_observed
- Missing: fix_c1_deployment_identity
- Verdict: partial

UAT Evidence Window
- Claim / Delivery Scope: current_flow_x
- Relevant SUT Fingerprint: unverified
- Preconditions: satisfied
- Window Stability: observed_at:t1|stability_unverified
- Coverage Basis: current_flow_only
- Result / Missing: observed_only|version_attribution_unverified
- Rerun Of / Supersedes: none

```yaml
release_evidence_claim:
  claim_type: uat
  claim: current_uat_behavior
  evidence_status: unverified
  installed_plugin_root: not_applicable
  source_root: /workspace/source
  cache_or_source_refresh:
    method: not_applicable
    evidence: non_plugin_uat
  run_scope: targeted
  commands_or_trials: [browser, flow_x_observed]
  limitations: [version_attribution_unverified]
```

## uat-window-004

The user-provided record states that finding `f1` was recorded in window `w0` on `frontend:s0`. Fix `c1` was deployed as `frontend:s1` with `api:b4`; the original check and affected regression scope were rerun in a new stable window. The source root is `/workspace/source`.

Verification Scope
- Claim: finding_f1_closure
- Covered: runtime_pass|browser|new_fingerprint|original_check|regression_scope
- Missing: none
- Verdict: pass

UAT Evidence Window
- Claim / Delivery Scope: fix_c1|finding_f1
- Relevant SUT Fingerprint: frontend:s1|api:b4
- Preconditions: satisfied
- Window Stability: stable
- Coverage Basis: finding:f1|regression_scope
- Result / Missing: pass|none
- Rerun Of / Supersedes: rerun_of:f1|supersedes:w0

```yaml
release_evidence_claim:
  claim_type: uat
  claim: finding_f1_closure
  evidence_status: verified
  installed_plugin_root: not_applicable
  source_root: /workspace/source
  cache_or_source_refresh:
    method: not_applicable
    evidence: non_plugin_uat
  run_scope: targeted
  commands_or_trials: [browser, original_check, regression_scope]
  limitations: []
```

## uat-window-005

The user-provided coverage record states that the canonical UAT plan passed, but the declared delivery scope also contains a newly committed user-visible delta that the plan does not cover. The uncovered delta keeps the overall delivery-scope verdict partial. The source root is `/workspace/source`.

Verification Scope
- Claim: rc2_uat_coverage
- Covered: source|browser|uat_plan
- Missing: latest_user_visible_delta
- Verdict: partial

UAT Evidence Window
- Claim / Delivery Scope: delivery_scope_rc2
- Relevant SUT Fingerprint: frontend:rc2
- Preconditions: satisfied
- Window Stability: stable
- Coverage Basis: declared_scope|uat_plan|user_visible_delta
- Result / Missing: partial|user_visible_delta_uncovered
- Rerun Of / Supersedes: none

```yaml
release_evidence_claim:
  claim_type: uat
  claim: rc2_uat_coverage
  evidence_status: unverified
  installed_plugin_root: not_applicable
  source_root: /workspace/source
  cache_or_source_refresh:
    method: not_applicable
    evidence: non_plugin_uat
  run_scope: targeted
  commands_or_trials: [source, browser, uat_plan]
  limitations: [user_visible_delta_uncovered]
```

## uat-window-006

The user-provided observation records these current-observation facts:

- `flow_y` worked at immutable preview URL `https://preview.invalid/commit/abc123`.
- The immutable URL binds the observation to one commit.
- No version attribution beyond the current observation is requested.
- There is no redeploy, rerun, or cross-session continuation.
- The source root is `/workspace/source`.

For this bounded observation, a `UAT Evidence Window` block and orphan window fields are forbidden. The ordinary scope is:

Verification Scope
- Claim: current immutable preview flow_y behavior
- Covered: browser observation on the commit-bound preview URL
- Missing: broader release attribution
- Verdict: partial

```yaml
release_evidence_claim:
  claim_type: uat
  claim: current immutable preview flow_y behavior
  evidence_status: verified
  installed_plugin_root: not_applicable
  source_root: /workspace/source
  cache_or_source_refresh:
    method: not_applicable
    evidence: non_plugin_uat
  run_scope: targeted
  commands_or_trials: [browser, immutable_preview]
  limitations: [broader_release_attribution_unverified]
```

## uat-window-007

The user-provided canonical UAT evidence-window reference is `artifacts/workstream/verification.md#w1`. It records the completed observation on stable `frontend:s1|api:b4`, while canonical final-state writeback remains pending. This compact continuation is reference-only; Groundwork did not deploy, rerun, or write back the state. The source root is `/workspace/source`.

UAT Evidence-Window Continuation
- Canonical Reference: artifacts/workstream/verification.md#w1
- Claim / Delivery Scope: completed_uat_observation
- Relevant SUT Fingerprint: frontend:s1|api:b4
- Window Stability: stable
- Missing / Closeout Gap: canonical_final_state_writeback_pending
- Rerun Of / Supersedes: none
- Next Owner Action: owner:uat_lead|writeback_final_state
- Execution Boundary: reference_only|groundwork_non_executor

```yaml
release_evidence_claim:
  claim_type: uat
  claim: completed_uat_observation
  evidence_status: verified
  installed_plugin_root: not_applicable
  source_root: /workspace/source
  cache_or_source_refresh:
    method: not_applicable
    evidence: non_plugin_uat
  run_scope: targeted
  commands_or_trials: [canonical_window:w1, runtime_observation]
  limitations: [canonical_writeback_pending]
```
