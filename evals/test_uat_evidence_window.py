#!/usr/bin/env python3
import csv
import unittest
from pathlib import Path

from evals import routing_schema, run_runtime
from evals.checks import loop_checks


ROOT = Path(__file__).resolve().parents[1]
SUITE = ROOT / "evals/prompts/uat-evidence-window.csv"


def read(relative_path):
    return (ROOT / relative_path).read_text(encoding="utf-8")


def uat_row(row_id):
    with SUITE.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    row = next(item.copy() for item in rows if item["id"] == row_id)
    row["_suite"] = SUITE.name
    row["_row_number"] = 0
    row["_fieldnames"] = list(row)
    return row


def release_claim_for(row_id, **overrides):
    row = uat_row(row_id)
    values = {
        "claim_type": row["release_expected_claim_type"],
        "claim": row["release_expected_claim"],
        "evidence_status": row["release_expected_evidence_status"],
        "installed_plugin_root": row["release_expected_installed_plugin_root"],
        "source_root": row["release_expected_source_root"],
        "refresh_method": row["release_expected_refresh_method"],
        "refresh_evidence": row["release_expected_refresh_evidence"],
        "run_scope": row["release_expected_run_scope"],
        "commands_or_trials": row["release_expected_commands_or_trials"],
        "limitations": row["release_expected_limitations"],
    }
    values.update(overrides)

    def inline_list(value):
        if value in {"none", "[]"}:
            return "[]"
        return "[" + ", ".join(value.split("|")) + "]"

    return f"""```yaml
release_evidence_claim:
  claim_type: {values['claim_type']}
  claim: {values['claim']}
  evidence_status: {values['evidence_status']}
  installed_plugin_root: {values['installed_plugin_root']}
  source_root: {values['source_root']}
  cache_or_source_refresh:
    method: {values['refresh_method']}
    evidence: {values['refresh_evidence']}
  run_scope: {values['run_scope']}
  commands_or_trials: {inline_list(values['commands_or_trials'])}
  limitations: {inline_list(values['limitations'])}
```"""


def with_release_claim(row_id, response, **overrides):
    return response.rstrip() + "\n\n" + release_claim_for(row_id, **overrides) + "\n"


def uat_verdict(row_id, response, actual=None):
    row = uat_row(row_id)
    return run_runtime.routing_verdict_model(
        row, actual or row["expected_best"], response, 0, [], []
    )


class UatEvidenceWindowTests(unittest.TestCase):
    def test_suite_is_trace_ready_and_schema_valid(self):
        with SUITE.open(newline="", encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
        for index, row in enumerate(rows, start=2):
            row["_suite"] = SUITE.name
            row["_row_number"] = index
            row["_fieldnames"] = list(row)

        errors, _normalized = routing_schema.validate_routing_schema(rows)

        self.assertIn(SUITE.name, routing_schema.TRACE_READY_SUITES)
        self.assertEqual(errors, [])

    def test_contract_is_conditional_and_cross_skill(self):
        release_claim = read("skills/_shared/RELEASE-EVIDENCE-CLAIM.md")
        release_branch = read("skills/verify/RELEASE-READINESS-BRANCH.md")
        ui_branch = read("skills/verify/UI-READINESS-BRANCH.md")
        ui_router = read("skills/verify/UI-TOOL-ROUTER.md")
        handoff = read("skills/handoff/COMPLEX-HANDOFF-BRANCHES.md")

        for field in (
            "Claim / Delivery Scope",
            "Relevant SUT Fingerprint",
            "Preconditions",
            "Window Stability",
            "Coverage Basis",
            "Result / Missing",
            "Rerun Of / Supersedes",
        ):
            self.assertIn(field, release_claim)
        self.assertIn("conditional", release_claim.lower())
        self.assertIn("current behavior observation", release_claim.lower())
        self.assertIn("new evidence window", release_branch.lower())
        self.assertIn("declared delivery scope", release_branch.lower())
        self.assertIn("UAT Evidence Window", ui_branch)
        self.assertIn("UAT Evidence Window", ui_router)
        self.assertIn("canonical UAT evidence-window reference", handoff)
        self.assertIn("closeout", handoff.lower())
        self.assertIn("does not invalidate", handoff.lower())

    def test_valid_version_bound_window_passes(self):
        response = """Verification Scope
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
"""

        verdict = uat_verdict(
            "uat-window-001", with_release_claim("uat-window-001", response)
        )

        self.assertEqual(verdict["output_contract_verdict"], "pass")
        self.assertEqual(verdict["overall_verdict"], "pass")

    def test_material_uat_window_requires_matching_release_evidence_claim(self):
        response = """Verification Scope
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
"""

        missing_claim = uat_verdict("uat-window-001", response)
        mismatched_claim = uat_verdict(
            "uat-window-001",
            with_release_claim(
                "uat-window-001", response, evidence_status="unverified"
            ),
        )

        self.assertEqual(missing_claim["output_contract_verdict"], "fail")
        self.assertEqual(mismatched_claim["output_contract_verdict"], "fail")

    def test_mid_window_change_cannot_be_rewritten_as_pass(self):
        response = """Verification Scope
- Claim: rc1_uat_window_stability
- Covered: preconditions|runtime_pass_before_change|runtime_pass_after_change|browser_before_change|browser_after_change
- Missing: none
- Verdict: pass

UAT Evidence Window
- Claim / Delivery Scope: release_candidate_rc1
- Relevant SUT Fingerprint: frontend:s1
- Preconditions: satisfied
- Window Stability: stable
- Coverage Basis: declared_scope|uat_plan
- Result / Missing: pass|none
- Rerun Of / Supersedes: none
"""

        verdict = uat_verdict(
            "uat-window-002", with_release_claim("uat-window-002", response)
        )

        self.assertEqual(verdict["output_contract_verdict"], "fail")
        self.assertEqual(verdict["overall_verdict"], "fail")

    def test_bounded_partial_and_rerun_oracles_pass(self):
        cases = {
            "uat-window-002": """Verification Scope
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
""",
            "uat-window-003": """Verification Scope
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
""",
            "uat-window-004": """Verification Scope
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
""",
            "uat-window-005": """Verification Scope
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
""",
        }

        for row_id, response in cases.items():
            with self.subTest(row_id=row_id):
                verdict = uat_verdict(row_id, with_release_claim(row_id, response))
                self.assertEqual(verdict["output_contract_verdict"], "pass")
                self.assertEqual(verdict["overall_verdict"], "pass")

    def test_fix_closure_requires_new_fingerprint_and_rerun_link(self):
        response = """Verification Scope
- Claim: finding_f1_closure
- Covered: runtime_pass|browser|new_fingerprint|original_check|regression_scope
- Missing: none
- Verdict: pass

UAT Evidence Window
- Claim / Delivery Scope: fix_c1|finding_f1
- Relevant SUT Fingerprint: frontend:s0|api:b4
- Preconditions: satisfied
- Window Stability: stable
- Coverage Basis: finding:f1|regression_scope
- Result / Missing: pass|none
- Rerun Of / Supersedes: none
"""

        verdict = uat_verdict(
            "uat-window-004", with_release_claim("uat-window-004", response)
        )

        self.assertEqual(verdict["output_contract_verdict"], "fail")

    def test_uat_oracle_fields_are_fail_closed(self):
        row = uat_row("uat-window-001")
        row["uat_expected_window_stability"] = ""

        with self.assertRaises(ValueError):
            routing_schema.routing_schema_for_row(row)

        row = uat_row("uat-window-001")
        row["release_expected_evidence_status"] = ""
        with self.assertRaises(ValueError):
            routing_schema.routing_schema_for_row(row)

        row = uat_row("uat-window-001")
        row["output_contract"] = "verify_scope|uat_evidence_window"
        with self.assertRaises(ValueError):
            routing_schema.routing_schema_for_row(row)

        row = uat_row("uat-window-007")
        row["uat_handoff_expected_next_owner_action"] = ""
        with self.assertRaises(ValueError):
            routing_schema.routing_schema_for_row(row)

        row = uat_row("uat-window-007")
        row["output_contract"] = "entry_decision|uat_handoff_reference"
        with self.assertRaises(ValueError):
            routing_schema.routing_schema_for_row(row)

        row = uat_row("uat-window-006")
        row["output_contract"] = "verify_scope|uat_evidence_window_forbidden"
        with self.assertRaises(ValueError):
            routing_schema.routing_schema_for_row(row)

        row = uat_row("uat-window-006")
        row["output_contract"] = (
            "verify_scope|release_evidence_claim|uat_evidence_window|"
            "uat_evidence_window_forbidden"
        )
        with self.assertRaises(ValueError):
            routing_schema.routing_schema_for_row(row)

    def test_structured_window_rejects_extra_prose(self):
        response = """Verification Scope
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

This extra prose contradicts the bounded machine-consumed contract.
"""

        verdict = uat_verdict(
            "uat-window-001", with_release_claim("uat-window-001", response)
        )

        self.assertEqual(verdict["output_contract_verdict"], "fail")

    def test_plain_observation_does_not_require_window_block(self):
        response = """Verification Scope
- Claim: current immutable preview flow_y behavior
- Covered: browser observation on the commit-bound preview URL
- Missing: broader release attribution
- Verdict: partial
"""

        verdict = uat_verdict(
            "uat-window-006", with_release_claim("uat-window-006", response)
        )

        self.assertEqual(verdict["output_contract_verdict"], "pass")
        self.assertEqual(verdict["overall_verdict"], "pass")

    def test_plain_observation_rejects_forced_window_block(self):
        response = """Verification Scope
- Claim: current immutable preview flow_y behavior
- Covered: browser observation on the commit-bound preview URL
- Missing: broader release attribution
- Verdict: partial

UAT Evidence Window
- Claim / Delivery Scope: current_flow_y
- Relevant SUT Fingerprint: immutable_preview
- Preconditions: satisfied
- Window Stability: stable
- Coverage Basis: current_flow_only
- Result / Missing: observed_only|none
- Rerun Of / Supersedes: none
"""

        verdict = uat_verdict(
            "uat-window-006", with_release_claim("uat-window-006", response)
        )

        self.assertEqual(verdict["output_contract_verdict"], "fail")
        self.assertEqual(verdict["overall_verdict"], "fail")

    def test_plain_observation_rejects_incomplete_window_block(self):
        response = """Verification Scope
- Claim: current immutable preview flow_y behavior
- Covered: browser observation on the commit-bound preview URL
- Missing: broader release attribution
- Verdict: partial

UAT Evidence Window
- Claim / Delivery Scope: current_flow_y
- Relevant SUT Fingerprint: immutable_preview
- Preconditions: satisfied
- Window Stability: stable
- Coverage Basis: current_flow_only
- Result / Missing: observed_only|none
"""

        verdict = uat_verdict(
            "uat-window-006", with_release_claim("uat-window-006", response)
        )

        self.assertEqual(verdict["output_contract_verdict"], "fail")
        self.assertEqual(verdict["overall_verdict"], "fail")

    def test_plain_observation_rejects_orphan_window_fields(self):
        response = """Verification Scope
- Claim: current immutable preview flow_y behavior
- Covered: browser observation on the commit-bound preview URL
- Missing: broader release attribution
- Verdict: partial

- Claim / Delivery Scope: current_flow_y
- Relevant SUT Fingerprint: immutable_preview
- Window Stability: stable
"""

        verdict = uat_verdict(
            "uat-window-006", with_release_claim("uat-window-006", response)
        )

        self.assertEqual(verdict["output_contract_verdict"], "fail")
        self.assertEqual(verdict["overall_verdict"], "fail")

    def test_plain_observation_rejects_variant_window_heading(self):
        response = """Verification Scope
- Claim: current immutable preview flow_y behavior
- Covered: browser observation on the commit-bound preview URL
- Missing: broader release attribution
- Verdict: partial

## UAT Evidence-Window
"""

        verdict = uat_verdict(
            "uat-window-006", with_release_claim("uat-window-006", response)
        )

        self.assertEqual(verdict["output_contract_verdict"], "fail")
        self.assertEqual(verdict["overall_verdict"], "fail")

    def test_plain_observation_rejects_annotated_window_heading(self):
        response = """Verification Scope
- Claim: current immutable preview flow_y behavior
- Covered: browser observation on the commit-bound preview URL
- Missing: broader release attribution
- Verdict: partial

## UAT Evidence Window (optional)
"""

        verdict = uat_verdict(
            "uat-window-006", with_release_claim("uat-window-006", response)
        )

        self.assertEqual(verdict["output_contract_verdict"], "fail")
        self.assertEqual(verdict["overall_verdict"], "fail")

    def test_compact_handoff_reference_is_mechanically_bounded(self):
        response = """UAT Evidence-Window Continuation
- Canonical Reference: artifacts/workstream/verification.md#w1
- Claim / Delivery Scope: completed_uat_observation
- Relevant SUT Fingerprint: frontend:s1|api:b4
- Window Stability: stable
- Missing / Closeout Gap: canonical_final_state_writeback_pending
- Rerun Of / Supersedes: none
- Next Owner Action: owner:uat_lead|writeback_final_state
- Execution Boundary: reference_only|groundwork_non_executor
"""

        verdict = uat_verdict(
            "uat-window-007", with_release_claim("uat-window-007", response)
        )

        self.assertEqual(verdict["output_contract_verdict"], "pass")
        self.assertEqual(verdict["overall_verdict"], "pass")

    def test_handoff_cannot_claim_groundwork_executed_or_omit_resume_state(self):
        response = """UAT Evidence-Window Continuation
- Canonical Reference: none
- Claim / Delivery Scope: completed_uat_observation
- Relevant SUT Fingerprint: frontend:s1|api:b4
- Window Stability: stable
- Missing / Closeout Gap: none
- Rerun Of / Supersedes: none
- Next Owner Action: none
- Execution Boundary: groundwork_deployed_reran_and_wrote_back
"""

        verdict = uat_verdict(
            "uat-window-007", with_release_claim("uat-window-007", response)
        )

        self.assertEqual(verdict["output_contract_verdict"], "fail")
        self.assertEqual(verdict["overall_verdict"], "fail")

    def test_checker_is_wired_into_runtime_output_contract(self):
        self.assertTrue(hasattr(loop_checks, "release_evidence_claim_failures"))
        self.assertTrue(hasattr(loop_checks, "uat_evidence_window_failures"))
        self.assertTrue(hasattr(loop_checks, "uat_handoff_reference_failures"))
        self.assertIn(
            "release_evidence_claim",
            routing_schema.OUTPUT_CONTRACT_IMPLEMENTED_TOKENS,
        )
        self.assertIn(
            "uat_evidence_window", routing_schema.OUTPUT_CONTRACT_IMPLEMENTED_TOKENS
        )
        self.assertIn(
            "uat_evidence_window_forbidden",
            routing_schema.OUTPUT_CONTRACT_IMPLEMENTED_TOKENS,
        )
        self.assertIn(
            "uat_handoff_reference",
            routing_schema.OUTPUT_CONTRACT_IMPLEMENTED_TOKENS,
        )


if __name__ == "__main__":
    unittest.main()
