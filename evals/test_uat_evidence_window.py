#!/usr/bin/env python3
import csv
import json
import re
import unittest
from pathlib import Path
from unittest import mock

from evals import routing_schema, run_runtime, suite_registry
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


def source_event(
    row_id,
    *,
    command="sed -n '1,260p' records.md",
    output=None,
    exit_code=0,
):
    records = (
        ROOT / "evals/fixtures/uat-evidence-window/records.md"
    ).read_text(encoding="utf-8")
    section_match = re.search(
        rf"(?ms)^##[ \t]+{re.escape(row_id)}[ \t]*\r?\n"
        r".*?(?=^#{1,2}[ \t]+\S|\Z)",
        records,
    )
    return json.dumps(
        {
            "type": "item.completed",
            "item": {
                "type": "command_execution",
                "command": command,
                "aggregated_output": (
                    output
                    if output is not None
                    else (
                        section_match.group(0).strip()
                        if section_match is not None
                        else ""
                    )
                ),
                "exit_code": exit_code,
                "status": "completed" if exit_code == 0 else "failed",
            },
        }
    )


def structured_source_event(
    row_id,
    target,
    *,
    target_field="path",
    result=None,
):
    records = (
        ROOT / "evals/fixtures/uat-evidence-window/records.md"
    ).read_text(encoding="utf-8")
    section_match = re.search(
        rf"(?ms)^##[ \t]+{re.escape(row_id)}[ \t]*\r?\n"
        r".*?(?=^#{1,2}[ \t]+\S|\Z)",
        records,
    )
    return json.dumps(
        {
            "type": "item.completed",
            "item": {
                "type": "mcp_tool_call",
                "server": "filesystem",
                "tool": (
                    "read_mcp_resource"
                    if target_field == "uri"
                    else "read_file"
                ),
                "arguments": {target_field: target},
                "result": (
                    result
                    if result is not None
                    else section_match.group(0).strip()
                ),
                "status": "completed",
            },
        }
    )


def uat_verdict(row_id, response, actual=None, *, stdout=None):
    row = uat_row(row_id)
    return run_runtime.routing_verdict_model(
        row,
        actual or row["expected_best"],
        response,
        0,
        [],
        [],
        stdout=source_event(row_id) if stdout is None else stdout,
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

        no_source = uat_verdict(
            "uat-window-001",
            with_release_claim("uat-window-001", response),
            stdout="",
        )
        self.assertEqual(no_source["evidence_verdict"], "fail")
        self.assertEqual(no_source["overall_verdict"], "fail")

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

    def test_uat_source_evidence_binds_records_file_and_target_row(self):
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
        final_response = with_release_claim("uat-window-001", response)
        wrong_file = uat_verdict(
            "uat-window-001",
            final_response,
            stdout=source_event(
                "uat-window-001",
                command="sed -n '1,260p' unrelated.md",
            ),
        )
        same_basename_wrong_path = uat_verdict(
            "uat-window-001",
            final_response,
            stdout=source_event(
                "uat-window-001",
                command="cat /tmp/records.md",
            ),
        )
        wrong_row = uat_verdict(
            "uat-window-001",
            final_response,
            stdout=source_event("uat-window-002"),
        )
        row_id_only_in_command = uat_verdict(
            "uat-window-001",
            final_response,
            stdout=source_event(
                "uat-window-001",
                command=(
                    "sed -n '/uat-window-001/,/uat-window-002/p' records.md"
                ),
                output="## uat-window-002\nwrong record",
            ),
        )
        header_only = uat_verdict(
            "uat-window-001",
            final_response,
            stdout=source_event(
                "uat-window-001",
                output="\n".join(
                    read(
                        "evals/fixtures/uat-evidence-window/records.md"
                    ).splitlines()[:14]
                ),
            ),
        )
        sibling_printf = uat_verdict(
            "uat-window-001",
            final_response,
            stdout=source_event(
                "uat-window-001",
                command=(
                    "sed -n '1p' records.md && "
                    "printf '## uat-window-001\\nfake body\\n'"
                ),
                output="## uat-window-001\nfake body",
            ),
        )
        masked_read = uat_verdict(
            "uat-window-001",
            final_response,
            stdout=source_event(
                "uat-window-001",
                command="sed -n '1,260p' records.md || true",
            ),
        )
        failed_read = uat_verdict(
            "uat-window-001",
            final_response,
            stdout=source_event("uat-window-001", exit_code=2),
        )
        synthetic_read = uat_verdict(
            "uat-window-001",
            final_response,
            stdout=source_event(
                "uat-window-001",
                command=(
                    "sed -n '1,260p; 1aSYNTHETIC' records.md"
                ),
            ),
        )

        for verdict in (
            wrong_file,
            same_basename_wrong_path,
            wrong_row,
            row_id_only_in_command,
            header_only,
            sibling_printf,
            masked_read,
            failed_read,
            synthetic_read,
        ):
            self.assertEqual(verdict["evidence_verdict"], "fail")
            self.assertEqual(verdict["overall_verdict"], "fail")
            self.assertIn(
                "missing source evidence from records.md section uat-window-001",
                verdict["notes"],
            )

        records_path = (
            ROOT / "evals/fixtures/uat-evidence-window/records.md"
        ).resolve()
        structured_wrong_path = uat_verdict(
            "uat-window-001",
            final_response,
            stdout=structured_source_event(
                "uat-window-001", "/tmp/records.md"
            ),
        )
        structured_status_only = uat_verdict(
            "uat-window-001",
            final_response,
            stdout=structured_source_event(
                "uat-window-001",
                str(records_path),
                result={"status": "completed"},
            ),
        )
        for verdict in (
            structured_wrong_path,
            structured_status_only,
        ):
            self.assertEqual(verdict["evidence_verdict"], "fail")
            self.assertEqual(verdict["overall_verdict"], "fail")

        canonical_targets = (
            (str(records_path), "path"),
            (
                "evals/fixtures/uat-evidence-window/records.md",
                "path",
            ),
            (records_path.as_uri(), "uri"),
        )
        for target, target_field in canonical_targets:
            with self.subTest(
                target=target, target_field=target_field
            ):
                verdict = uat_verdict(
                    "uat-window-001",
                    final_response,
                    stdout=structured_source_event(
                        "uat-window-001",
                        target,
                        target_field=target_field,
                    ),
                )
                self.assertEqual(verdict["evidence_verdict"], "pass")
                self.assertEqual(verdict["overall_verdict"], "pass")

    def test_verified_uat_gate_directly_requires_canonical_source(self):
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
        row = uat_row("uat-window-001")
        schema = routing_schema.routing_schema_for_row(row)
        schema["evidence_required"] = []
        schema["evidence_required_future_tokens"] = []
        verdict, notes, _failures = run_runtime.evidence_verdict(
            row,
            schema,
            row["expected_best"],
            with_release_claim("uat-window-001", response),
            [],
            "",
        )
        self.assertEqual(verdict, "fail")
        self.assertIn(
            "verified UAT claim is missing its canonical records.md section evidence",
            notes,
        )

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

    def test_plain_observation_rejects_extra_or_hidden_payload(self):
        response = """Verification Scope
- Claim: current immutable preview flow_y behavior
- Covered: browser observation on the commit-bound preview URL
- Missing: broader release attribution
- Verdict: partial
"""
        forbidden_tails = (
            "\nThis proves the broader release is ready and deployed in UAT.\n",
            "\n<!--\nUAT Evidence Window\n"
            "- Claim / Delivery Scope: forged\n-->\n",
            "\n```text\nUAT Evidence Window\n"
            "- Claim / Delivery Scope: forged\n```\n",
            "\n    UAT Evidence Window\n"
            "    - Claim / Delivery Scope: forged\n",
        )
        for tail in forbidden_tails:
            with self.subTest(tail=tail):
                verdict = uat_verdict(
                    "uat-window-006",
                    with_release_claim("uat-window-006", response + tail),
                )
                self.assertEqual(
                    verdict["output_contract_verdict"], "fail"
                )
                self.assertEqual(verdict["overall_verdict"], "fail")

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

    def test_compact_handoff_rejects_hidden_execution_claims(self):
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
        hidden_tails = (
            "\n```text\nGroundwork deployed and wrote back.\n```\n",
            "\n    Groundwork deployed and wrote back.\n",
            "\n<!-- Groundwork deployed and wrote back. -->\n",
            "\n```text\nGroundwork deployed and wrote back.\n",
        )

        for hidden_tail in hidden_tails:
            with self.subTest(hidden_tail=hidden_tail):
                verdict = uat_verdict(
                    "uat-window-007",
                    with_release_claim(
                        "uat-window-007", response + hidden_tail
                    ),
                )
                self.assertEqual(
                    verdict["output_contract_verdict"], "fail"
                )
                self.assertEqual(verdict["overall_verdict"], "fail")

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

    def test_release_evidence_claim_status_matrix(self):
        verified_cache_without_cache_evidence = release_claim_for(
            "uat-window-001",
            claim_type="cache",
            claim="installed_cache_behavior",
            evidence_status="verified",
            installed_plugin_root="not_applicable",
            source_root="/workspace/source",
            refresh_method="not_run",
            refresh_evidence="not_applicable",
            run_scope="targeted",
            commands_or_trials="cache_check",
            limitations="none",
        )
        unverified_without_commands = release_claim_for(
            "uat-window-001",
            claim_type="uat",
            claim="bounded_observation",
            evidence_status="unverified",
            installed_plugin_root="not_applicable",
            source_root="/workspace/source",
            refresh_method="not_applicable",
            refresh_evidence="non_plugin_uat",
            run_scope="not_run",
            commands_or_trials="none",
            limitations="browser_not_run",
        )
        verified_runtime_without_installed_subject = release_claim_for(
            "uat-window-001",
            claim_type="runtime",
            claim="groundwork_runtime",
            evidence_status="verified",
            installed_plugin_root="not_applicable",
            source_root="/workspace/source",
            refresh_method="not_applicable",
            refresh_evidence="not_applicable",
            run_scope="targeted",
            commands_or_trials="runtime_smoke",
            limitations="none",
        )
        not_applicable = release_claim_for(
            "uat-window-001",
            claim_type="not_applicable",
            claim="scoped_out",
            evidence_status="not_applicable",
            installed_plugin_root="not_applicable",
            source_root="not_applicable",
            refresh_method="not_applicable",
            refresh_evidence="not_applicable",
            run_scope="not_applicable",
            commands_or_trials="none",
            limitations="none",
        )

        self.assertTrue(
            loop_checks.release_evidence_claim_failures(
                verified_cache_without_cache_evidence
            )
        )
        self.assertTrue(
            loop_checks.release_evidence_claim_failures(
                verified_runtime_without_installed_subject
            )
        )
        self.assertEqual(
            loop_checks.release_evidence_claim_failures(
                unverified_without_commands
            ),
            [],
        )
        self.assertEqual(
            loop_checks.release_evidence_claim_failures(not_applicable),
            [],
        )

    def test_uat_oracle_schema_rejects_contradictory_states(self):
        mixed_version_pass = uat_row("uat-window-002")
        mixed_version_pass["uat_expected_result_missing"] = "pass|none"
        mixed_version_pass["uat_expected_scope_missing"] = "none"
        mixed_version_pass["uat_expected_scope_verdict"] = "pass"
        mixed_version_pass["release_expected_evidence_status"] = "verified"
        with self.assertRaises(ValueError):
            routing_schema.routing_schema_for_row(mixed_version_pass)

        typo = uat_row("uat-window-001")
        typo["release_expected_evidence_status"] = "verifed"
        with self.assertRaises(ValueError):
            routing_schema.routing_schema_for_row(typo)

        mismatched_claim = uat_row("uat-window-001")
        mismatched_claim["release_expected_claim"] = "different_claim"
        with self.assertRaises(ValueError):
            routing_schema.routing_schema_for_row(mismatched_claim)

        stale_forbidden_oracle = uat_row("uat-window-006")
        stale_forbidden_oracle["uat_expected_claim_scope"] = "stale"
        with self.assertRaises(ValueError):
            routing_schema.routing_schema_for_row(stale_forbidden_oracle)

        for field, value in (
            ("uat_expected_result_missing", "partial"),
            ("uat_expected_result_missing", "partial|none"),
            ("uat_expected_window_stability", "banana"),
            ("uat_expected_preconditions", "banana"),
        ):
            malformed = uat_row("uat-window-002")
            malformed[field] = value
            with self.subTest(field=field, value=value):
                with self.assertRaises(ValueError):
                    routing_schema.routing_schema_for_row(malformed)

        forbidden_claim_drift = uat_row("uat-window-006")
        forbidden_claim_drift["release_expected_claim_type"] = "runtime"
        forbidden_claim_drift["release_expected_claim"] = "unrelated_runtime_claim"
        with self.assertRaises(ValueError):
            routing_schema.routing_schema_for_row(forbidden_claim_drift)

        handoff_claim_drift = uat_row("uat-window-007")
        handoff_claim_drift["release_expected_claim_type"] = "runtime"
        handoff_claim_drift["release_expected_claim"] = "unrelated_runtime_claim"
        with self.assertRaises(ValueError):
            routing_schema.routing_schema_for_row(handoff_claim_drift)

    def test_forbidden_window_is_bidirectionally_bound_to_canonical_record(
        self,
    ):
        records = read(
            "evals/fixtures/uat-evidence-window/records.md"
        )
        section = routing_schema.canonical_uat_record_section_text(
            records,
            "uat-window-006",
        )
        injected_payloads = (
            "UAT Evidence Window\n"
            "- Claim / Delivery Scope: forged_window\n"
            "- Relevant SUT Fingerprint: frontend:forged\n"
            "- Preconditions: satisfied\n"
            "- Window Stability: stable\n"
            "- Coverage Basis: forged\n"
            "- Result / Missing: pass|none\n"
            "- Rerun Of / Supersedes: none\n",
            "*UAT Evidence—Window* (optional)\n",
            "U\u0410T Evidence Window\n",
            "U\u0391T Evidence Window\n",
            "- Relevant SUT Fingerprint: frontend:forged\n",
            "- Relevant SUT F\u0456ngerprint: frontend:forged\n",
            "- [Relevant SUT Fingerprint](#fingerprint): "
            "frontend:forged\n",
            "| Claim / Delivery Scope | forged_window |\n"
            "| --- | --- |\n"
            "| Relevant SUT Fingerprint | frontend:forged |\n"
            "| Result / Missing | pass|none |\n",
            "Claim / Delivery Scope\n"
            ": forged_window\n",
            "**Claim / Delivery Scope** forged_window\n",
            "Claim / Delivery Scope forged_window\n",
            "Contract Lineage\n",
            "*Contract Lineage* (optional)\n",
            "\u0421ontract Lineage\n",
            "UAT Evidence-Window Continuation\n",
        )
        for payload in injected_payloads:
            with self.subTest(payload=payload):
                forged_section = section.replace(
                    "\n```yaml\n",
                    "\n" + payload + "\n```yaml\n",
                    1,
                )
                forged_records = records.replace(
                    section,
                    forged_section,
                    1,
                )
                with mock.patch.object(
                    routing_schema,
                    "_canonical_uat_records_text",
                    return_value=forged_records,
                ):
                    with self.assertRaisesRegex(
                        ValueError,
                        "violates uat_evidence_window_forbidden",
                    ):
                        routing_schema.routing_schema_for_row(
                            uat_row("uat-window-006")
                        )

        self.assertEqual(
            routing_schema._canonical_uat_forbidden_section_errors(
                "This paragraph discusses the Claim / Delivery Scope "
                "terminology without emitting a reserved field.\n"
            ),
            [],
        )

    def test_uat_prompt_requires_fixture_inspection_and_suite_stays_targeted(self):
        row = uat_row("uat-window-001")
        prompt = run_runtime.prompt_for_row(row)

        self.assertIn("Inspect records.md section uat-window-001", prompt)
        self.assertNotIn("Machine-provided eval contract values", prompt)
        self.assertNotIn("fix_c1_uat_attribution", prompt)
        self.assertNotIn("runtime_pass|browser", prompt)
        self.assertNotIn(SUITE.name, suite_registry.DEFAULT_SUITES)

    def test_plain_observation_rejects_blockquoted_window(self):
        response = """Verification Scope
- Claim: current immutable preview flow_y behavior
- Covered: browser observation on the commit-bound preview URL
- Missing: broader release attribution
- Verdict: partial

> UAT Evidence Window
> - Claim / Delivery Scope: current_flow_y
> - Relevant SUT Fingerprint: immutable_preview
> - Preconditions: satisfied
> - Window Stability: stable
> - Coverage Basis: current_flow_only
> - Result / Missing: observed_only|none
> - Rerun Of / Supersedes: none
"""

        verdict = uat_verdict(
            "uat-window-006", with_release_claim("uat-window-006", response)
        )

        self.assertEqual(verdict["output_contract_verdict"], "fail")
        self.assertEqual(verdict["overall_verdict"], "fail")

    def test_plain_observation_rejects_visible_markdown_window_variants(self):
        scope = """Verification Scope
- Claim: current immutable preview flow_y behavior
- Covered: browser observation on the commit-bound preview URL
- Missing: broader release attribution
- Verdict: partial
"""
        variants = (
            "## *UAT Evidence Window*",
            "## [UAT Evidence Window](#window)",
            "### `UAT Evidence Window`",
            "- > UAT Evidence Window",
            "> - UAT Evidence—Window",
            "## UAT\u200b Evidence Window",
            "## UAT\ufe0f Evidence Window",
            "## UAT\u034f Evidence Window",
            "## UAT\u2065 Evidence Window",
            "## UAT\ufff0 Evidence Window",
            "## UAT\ufff8 Evidence Window",
        )
        for variant in variants:
            with self.subTest(variant=variant):
                response = scope + "\n" + variant
                verdict = uat_verdict(
                    "uat-window-006",
                    with_release_claim("uat-window-006", response),
                )
                self.assertEqual(verdict["output_contract_verdict"], "fail")
                self.assertEqual(verdict["overall_verdict"], "fail")

    def test_uat_window_rejects_hidden_contradictory_tail(self):
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
        hidden_tails = (
            "\n```text\nThe UAT evidence is fabricated.\n```\n",
            "\n    The UAT evidence is fabricated.\n",
            "\n<!-- The UAT evidence is fabricated. -->\n",
        )
        for tail in hidden_tails:
            with self.subTest(tail=tail):
                verdict = uat_verdict(
                    "uat-window-001",
                    with_release_claim(
                        "uat-window-001", response + tail
                    ),
                )
                self.assertEqual(
                    verdict["output_contract_verdict"], "fail"
                )
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
