#!/usr/bin/env python3
import unittest
from pathlib import Path

from evals import verdict_model
from evals.checks import artifact_checks, common, forbidden_patterns, verify_checks
from evals.schema_validation import SchemaResolver, validate_instance


class CommonFieldDetectionTests(unittest.TestCase):
    def test_common_has_required_field_detects_plain_field(self):
        self.assertTrue(common.has_required_field("Target Reader: reviewer", "Target Reader"))

    def test_common_has_required_field_detects_markdown_heading(self):
        self.assertTrue(common.has_required_field("## Target Reader: reviewer", "Target Reader"))

    def test_common_has_required_field_detects_bold_bullet(self):
        self.assertTrue(common.has_required_field("- **Target Reader**: reviewer", "Target Reader"))

    def test_common_has_required_field_requires_colon(self):
        self.assertFalse(common.has_required_field("Target Reader reviewer", "Target Reader"))

    def test_common_missing_required_fields_returns_only_missing_fields(self):
        missing = common.missing_required_fields(
            "Target Reader: reviewer\nArtifact Type: review package",
            ["Target Reader", "Reader Action Needed", "Artifact Type"],
        )

        self.assertEqual(missing, ["Reader Action Needed"])


class QaGapClosureGateTests(unittest.TestCase):
    def _report(
        self,
        admission="ready_for_implement",
        delta="first observed failure",
        next_action="route: implement",
        verdict="fail",
        authority="existing_and_sufficient",
        risk_change="unchanged_within_boundary",
        reproduction="command: node --test test/taskSearch.test.mjs",
        re_qa="command: node --test test/taskSearch.test.mjs",
    ):
        return f"""Verification Scope
- Claim: failed filter can enter bounded remediation
- Covered: supplied failure package
- Missing: none
- Verdict: {verdict}
QA Failure
- Expected: filtered result
- Actual: unfiltered result
- Reproduction: {reproduction}
- Severity: P1
- Minimal Diagnosis: filter is not applied
- Evidence Delta: {delta}
- Source / AC Change: unchanged
- Implementation Authority: {authority}
- Risk Change: {risk_change}
- Fix Plan: change the filter only
- Gap-Closure Admission: {admission}
- Gap Closure Plan: change only the phone filter and rerun the original check
- Re-QA Required: {re_qa}
- Regression Note: adjacent status filter
- Scoped Next Action: {next_action}
"""

    def test_ready_admission_passes_with_complete_failure_package(self):
        self.assertEqual(verify_checks.qa_gap_closure_gate_failures(self._report()), [])

    def test_ready_admission_rejects_missing_reproduction(self):
        report = self._report().replace(
            "Reproduction: command: node --test test/taskSearch.test.mjs", "Reproduction: unverified"
        )
        self.assertIn(
            "Reproduction cannot be unresolved for ready_for_implement",
            verify_checks.qa_gap_closure_gate_failures(report),
        )

    def test_ready_admission_rejects_invalid_severity(self):
        report = self._report().replace("Severity: P1", "Severity: none")
        self.assertIn(
            "Severity must be P0-P3 for QA Failure",
            verify_checks.qa_gap_closure_gate_failures(report),
        )

    def test_ready_admission_rejects_unbounded_fix_plan(self):
        report = self._report().replace(
            "Fix Plan: change the filter only", "Fix Plan: unverified"
        )
        self.assertIn(
            "Fix Plan cannot be unresolved for ready_for_implement",
            verify_checks.qa_gap_closure_gate_failures(report),
        )

    def test_ready_admission_rejects_explicitly_broad_fix_scope(self):
        for field, value in (
            ("Fix Plan", "rewrite every module in the system"),
            ("Fix Plan", "rewrite everything"),
            ("Fix Plan", "refactor unrelated modules"),
            ("Gap Closure Plan", "change every file in the repository and rerun the check"),
        ):
            with self.subTest(field=field):
                report = self._report().replace(
                    f"{field}: "
                    + (
                        "change the filter only"
                        if field == "Fix Plan"
                        else "change only the phone filter and rerun the original check"
                    ),
                    f"{field}: {value}",
                )
                self.assertIn(
                    f"{field} must remain bounded for ready_for_implement",
                    verify_checks.qa_gap_closure_gate_failures(report),
                )

    def test_ready_admission_allows_negated_broad_scope_with_bounded_fix(self):
        report = self._report().replace(
            "Fix Plan: change the filter only",
            "Fix Plan: do not rewrite every module; change only the phone filter",
        )

        self.assertEqual(verify_checks.qa_gap_closure_gate_failures(report), [])

    def test_ready_admission_requires_evidence_delta(self):
        self.assertIn(
            "Evidence Delta is missing, unresolved, or contains no new evidence",
            verify_checks.qa_gap_closure_gate_failures(self._report(delta="unverified")),
        )

    def test_ready_admission_rejects_explicit_no_evidence_delta(self):
        self.assertIn(
            "Evidence Delta is missing, unresolved, or contains no new evidence",
            verify_checks.qa_gap_closure_gate_failures(
                self._report(delta="same result and same hypothesis; no new evidence")
            ),
        )

    def test_negated_hypothesis_change_is_not_an_evidence_delta(self):
        self.assertIn(
            "Evidence Delta is missing, unresolved, or contains no new evidence",
            verify_checks.qa_gap_closure_gate_failures(
                self._report(
                    delta="no new evidence; there is no changed hypothesis"
                )
            ),
        )

    def test_ready_admission_allows_new_evidence_with_same_result(self):
        self.assertEqual(
            verify_checks.qa_gap_closure_gate_failures(
                self._report(
                    delta="same result and same hypothesis, but a new trace localizes the filter branch"
                )
            ),
            [],
        )

    def test_ready_admission_allows_changed_hypothesis_without_new_evidence(self):
        self.assertEqual(
            verify_checks.qa_gap_closure_gate_failures(
                self._report(
                    delta="no new evidence; hypothesis changed to the normalization branch"
                )
            ),
            [],
        )

    def test_ready_admission_cannot_upgrade_failure_verdict(self):
        self.assertIn(
            "Verification Verdict must remain fail or blocked for QA Failure",
            verify_checks.qa_gap_closure_gate_failures(self._report(verdict="pass")),
        )

    def test_ready_admission_rejects_non_actionable_gap_plan(self):
        report = self._report().replace(
            "Gap Closure Plan: change only the phone filter and rerun the original check",
            "Gap Closure Plan: source truth and ACs are unchanged",
        )
        self.assertIn(
            "Gap Closure Plan must name a scoped change or evidence update for ready_for_implement",
            verify_checks.qa_gap_closure_gate_failures(report),
        )

    def test_ready_admission_rejects_vague_gap_plan(self):
        report = self._report().replace(
            "Gap Closure Plan: change only the phone filter and rerun the original check",
            "Gap Closure Plan: handle this later",
        )
        self.assertIn(
            "Gap Closure Plan must name a scoped change or evidence update for ready_for_implement",
            verify_checks.qa_gap_closure_gate_failures(report),
        )

    def test_ready_admission_rejects_changed_source_or_acceptance(self):
        report = self._report().replace(
            "Source / AC Change: unchanged", "Source / AC Change: changed"
        )
        self.assertIn(
            "Source / AC Change must be unchanged for ready_for_implement",
            verify_checks.qa_gap_closure_gate_failures(report),
        )

    def test_non_ready_admission_cannot_enter_implement(self):
        self.assertIn(
            "Scoped Next Action must be one of route: to-prd for product_or_contract_rework",
            verify_checks.qa_gap_closure_gate_failures(
                self._report(admission="product_or_contract_rework")
            ),
        )

    def test_non_ready_admission_rejects_indirect_implement_route(self):
        self.assertIn(
            "Scoped Next Action must be one of route: to-prd for product_or_contract_rework",
            verify_checks.qa_gap_closure_gate_failures(
                self._report(
                    admission="product_or_contract_rework",
                    next_action="route: implement",
                )
            ),
        )

    def test_non_ready_admission_allows_negated_implement_with_legal_route(self):
        self.assertEqual(
            verify_checks.qa_gap_closure_gate_failures(
                self._report(
                    admission="product_or_contract_rework",
                    delta="unverified",
                    next_action="route: to-prd",
                    verdict="blocked",
                )
            ),
            [],
        )

    def test_ready_admission_rejects_automatic_implement_execution(self):
        self.assertIn(
            "Scoped Next Action must be route: implement for ready_for_implement",
            verify_checks.qa_gap_closure_gate_failures(
                self._report(next_action="route: implement; execute now")
            ),
        )

    def test_ready_admission_rejects_direct_implement_invocation(self):
        self.assertIn(
            "Scoped Next Action must be route: implement for ready_for_implement",
            verify_checks.qa_gap_closure_gate_failures(
                self._report(next_action="proceed immediately to implement")
            ),
        )

    def test_ready_admission_rejects_implement_execution_outside_next_action(self):
        report = self._report(next_action="route: implement")
        report += "I am invoking implement now.\n"

        self.assertIn(
            "QA gap closure must recommend rather than execute implement",
            verify_checks.qa_gap_closure_gate_failures(report),
        )

    def test_ready_admission_rejects_hidden_multiline_broad_scope_and_edit_claim(self):
        report = self._report(next_action="route: implement")
        report = report.replace(
            "Fix Plan: change the filter only",
            "Fix Plan: change the filter only\n  Then rewrite every module in the system.",
        ).replace(
            "Gap Closure Plan: change only the phone filter and rerun the original check",
            "Gap Closure Plan: change only the phone filter and rerun the original check\n"
            "  Then change every file in the repository.",
        )
        report += "I patched the filter and rewrote every module now.\n"

        failures = verify_checks.qa_gap_closure_gate_failures(report)
        self.assertIn("QA gap closure must remain bounded across the full output", failures)
        self.assertIn(
            "QA gap closure must recommend rather than execute implement", failures
        )

    def test_ready_admission_allows_negated_edit_claim(self):
        report = self._report(next_action="route: implement").replace(
            "Fix Plan: change the filter only",
            "Fix Plan: do not patch or rewrite any other file; change only the phone filter",
        )

        self.assertEqual(verify_checks.qa_gap_closure_gate_failures(report), [])

    def test_non_ready_admission_rejects_edit_claim_anywhere_in_output(self):
        report = self._report(
            admission="needs_info",
            delta="unverified",
            next_action="route: verify",
            verdict="blocked",
        )
        report += "I patched the filter already.\n"

        self.assertIn(
            "QA gap closure must recommend rather than execute implement",
            verify_checks.qa_gap_closure_gate_failures(report),
        )

    def test_ready_admission_rejects_passive_edit_claim(self):
        report = self._report(next_action="route: implement")
        report += "The filter has been patched already.\n"

        self.assertIn(
            "QA gap closure must recommend rather than execute implement",
            verify_checks.qa_gap_closure_gate_failures(report),
        )

    def test_ready_admission_allows_negated_passive_edit_claim(self):
        report = self._report(next_action="route: implement").replace(
            "Fix Plan: change the filter only",
            "Fix Plan: the filter has not been patched; change only the phone filter",
        )

        self.assertEqual(verify_checks.qa_gap_closure_gate_failures(report), [])

    def test_ready_admission_rejects_applied_fix_claims(self):
        for claim in (
            "I applied the scoped fix already.",
            "The scoped fix has been applied already.",
            "We have already patched the filter.",
            "The scoped fix has already been applied.",
            "I have rewritten the filter.",
        ):
            with self.subTest(claim=claim):
                report = self._report(next_action="route: implement")
                report += claim + "\n"

                self.assertIn(
                    "QA gap closure must recommend rather than execute implement",
                    verify_checks.qa_gap_closure_gate_failures(report),
                )

    def test_ready_admission_allows_negated_applied_fix_claims(self):
        for claim in (
            "I did not apply the scoped fix.",
            "The scoped fix has not been applied.",
        ):
            with self.subTest(claim=claim):
                report = self._report(next_action="route: implement").replace(
                    "Fix Plan: change the filter only",
                    f"Fix Plan: {claim} Change only the phone filter",
                )

                self.assertEqual(
                    verify_checks.qa_gap_closure_gate_failures(report), []
                )

    def test_all_admissions_reject_patch_all_scope(self):
        next_actions = {
            "ready_for_implement": "route: implement",
            "diagnose_before_edit": "route: implement",
            "needs_info": "route: verify",
            "product_or_contract_rework": "route: to-prd",
            "human_decision": "route: human_decision",
            "blocked": "route: stop",
        }
        for admission, next_action in next_actions.items():
            for broad_scope in (
                "Patch all files in the repository.",
                "Fixing all files in the repository is the proposed remediation.",
                "Editing all files is the proposed remediation.",
                "Every file should be patched.",
                "All files are being patched.",
            ):
                with self.subTest(admission=admission, broad_scope=broad_scope):
                    report = self._report(
                        admission=admission,
                        next_action=next_action,
                        verdict="blocked" if admission == "blocked" else "fail",
                    )
                    report += broad_scope + "\n"

                    self.assertIn(
                        "QA gap closure must remain bounded across the full output",
                        verify_checks.qa_gap_closure_gate_failures(report),
                    )

    def test_patch_all_scope_negation_is_allowed(self):
        for negated_scope in (
            "Do not patch all files; change only the phone filter.",
            "We did not patch all files; only the phone filter remains in scope.",
            "We are not editing all files; only the phone filter remains in scope.",
            "We have not rewritten all files; only the phone filter remains in scope.",
        ):
            with self.subTest(negated_scope=negated_scope):
                report = self._report(next_action="route: implement").replace(
                    "Fix Plan: change the filter only",
                    f"Fix Plan: {negated_scope}",
                )

                self.assertEqual(
                    verify_checks.qa_gap_closure_gate_failures(report), []
                )

    def test_qa_failure_rejects_duplicate_gate_decision_fields(self):
        cases = (
            (
                "Evidence Delta",
                "- Evidence Delta: no new evidence\n- Source / AC Change: unchanged",
                "- Source / AC Change: unchanged",
            ),
            (
                "Gap-Closure Admission",
                "- Gap-Closure Admission: needs_info\n- Gap Closure Plan: change only the phone filter and rerun the original check",
                "- Gap Closure Plan: change only the phone filter and rerun the original check",
            ),
        )
        for field, duplicate, anchor in cases:
            with self.subTest(field=field):
                report = self._report(next_action="route: implement").replace(
                    anchor, duplicate
                )

                self.assertIn(
                    f"{field} must appear exactly once in QA Failure",
                    verify_checks.qa_gap_closure_gate_failures(report),
                )

    def test_qa_failure_cardinality_ignores_verification_scope_fields(self):
        self.assertEqual(verify_checks.qa_gap_closure_gate_failures(self._report()), [])

    def test_qa_failure_rejects_verdict_inside_qa_block(self):
        report = self._report().replace(
            "QA Failure\n", "QA Failure\n- Verdict: fail\n"
        )

        self.assertIn(
            "Verdict must not appear in QA Failure; keep it in Verification Scope",
            verify_checks.qa_gap_closure_gate_failures(report),
        )

    def test_verification_scope_must_precede_qa_failure(self):
        scope, qa = self._report().split("QA Failure\n", 1)
        report = "QA Failure\n" + qa + scope

        self.assertIn(
            "Verification Scope must appear before QA Failure",
            verify_checks.qa_gap_closure_gate_failures(report),
        )

    def test_verification_scope_fields_cannot_be_borrowed_from_later_sections(self):
        report = self._report()
        for field in (
            "- Claim: failed filter can enter bounded remediation\n",
            "- Covered: supplied failure package\n",
            "- Missing: none\n",
        ):
            report = report.replace(field, "")
        report += """## Later
- Claim: late claim
- Covered: late evidence
- Missing: none
"""

        self.assertEqual(
            verify_checks.missing_verify_scope_fields(report),
            ["Claim", "Covered", "Missing"],
        )

    def test_empty_duplicate_fields_still_count(self):
        scope_duplicate = self._report().replace(
            "- Verdict: fail\nQA Failure",
            "- Verdict: fail\n- Verdict:\nQA Failure",
        )
        self.assertIn(
            "Verdict must appear exactly once in Verification Scope",
            verify_checks.qa_gap_closure_gate_failures(scope_duplicate),
        )
        qa_duplicate = self._report() + "- Expected:\n"
        self.assertIn(
            "Expected must appear exactly once in QA Failure",
            verify_checks.qa_gap_closure_gate_failures(qa_duplicate),
        )

    def test_empty_expected_does_not_consume_actual_field(self):
        report = self._report().replace(
            "- Expected: filtered result", "- Expected:"
        )

        self.assertIn(
            "Expected cannot be unresolved for ready_for_implement",
            verify_checks.qa_gap_closure_gate_failures(report),
        )

    def test_router_verdict_scope_empty_fields_do_not_consume_next_lines(self):
        report = """Verification Scope
- Claim:
- Covered:
- Missing:
- Verdict: fail
QA Failure
- Expected: filtered result
"""

        self.assertEqual(
            verdict_model.missing_verify_scope_fields(report),
            ["Claim", "Covered", "Missing"],
        )

    def test_qa_failure_requires_exactly_one_explicit_block(self):
        report = self._report().replace(
            "QA Failure\n", ""
        )

        self.assertIn(
            "QA Failure block must appear exactly once",
            verify_checks.qa_gap_closure_gate_failures(report),
        )

    def test_qa_gap_closure_rejects_followup_markdown_section(self):
        report = self._report()
        report += """## Follow-up Summary
- Verdict: fail
- Scoped Next Action: route: verify
"""

        self.assertIn(
            "QA gap closure output must contain only Verification Scope and QA Failure structured fields",
            verify_checks.qa_gap_closure_gate_failures(report),
        )

    def test_qa_gap_closure_rejects_qa_fields_inside_verification_scope(self):
        report = self._report().replace(
            "- Missing: none\n- Verdict: fail",
            "- Missing: none\n- Fix Plan: the fix has shipped\n- Verdict: fail",
        )

        self.assertIn(
            "Fix Plan must appear only inside QA Failure",
            verify_checks.qa_gap_closure_gate_failures(report),
        )

    def test_ready_admission_allows_negated_execution_outside_next_action(self):
        report = self._report().replace(
            "Fix Plan: change the filter only",
            "Fix Plan: do not invoke implement here; change only the phone filter",
        )

        self.assertEqual(verify_checks.qa_gap_closure_gate_failures(report), [])

    def test_qa_gap_closure_rejects_unstructured_tail_prose(self):
        report = self._report() + "Only the phone filter remains in scope.\n"

        self.assertIn(
            "QA gap closure output must contain only Verification Scope and QA Failure structured fields",
            verify_checks.qa_gap_closure_gate_failures(report),
        )

    def test_qa_gap_closure_rejects_execution_claims_inside_plan_fields(self):
        cases = (
            ("Fix Plan", "deployed the corrected phone filter"),
            ("Fix Plan", "the corrected phone filter is live"),
            ("Fix Plan", "the corrected phone filter has shipped"),
            ("Fix Plan", "ship the corrected phone filter now"),
            (
                "Gap Closure Plan",
                "the corrected phone filter went live; rerun the original check",
            ),
            (
                "Gap Closure Plan",
                "the corrected phone filter is in production; rerun the original check",
            ),
            (
                "Gap Closure Plan",
                "deployed the corrected phone filter and rerun the original check",
            ),
        )
        for field, value in cases:
            with self.subTest(field=field, value=value):
                original = (
                    "change the filter only"
                    if field == "Fix Plan"
                    else "change only the phone filter and rerun the original check"
                )
                report = self._report().replace(
                    f"- {field}: {original}", f"- {field}: {value}"
                )
                self.assertTrue(
                    any(
                        f"{field} must remain a bounded proposal" in failure
                        for failure in verify_checks.qa_gap_closure_gate_failures(report)
                    )
                )

    def test_needs_info_can_stay_with_verify(self):
        self.assertEqual(
            verify_checks.qa_gap_closure_gate_failures(
                self._report(
                    admission="needs_info",
                    delta="unverified",
                    next_action="route: verify",
                    verdict="blocked",
                )
            ),
            [],
        )

    def test_ready_requires_existing_authority_and_unchanged_risk(self):
        authority_failures = verify_checks.qa_gap_closure_gate_failures(
            self._report(authority="approval_required")
        )
        self.assertIn(
            "Implementation Authority must be existing_and_sufficient for ready_for_implement",
            authority_failures,
        )
        risk_failures = verify_checks.qa_gap_closure_gate_failures(
            self._report(risk_change="new_or_increased")
        )
        self.assertIn(
            "Risk Change must be unchanged_within_boundary for ready_for_implement",
            risk_failures,
        )

    def test_human_decision_accepts_new_risk_without_implementation_route(self):
        self.assertEqual(
            verify_checks.qa_gap_closure_gate_failures(
                self._report(
                    admission="human_decision",
                    delta="unverified",
                    next_action="route: human_decision",
                    authority="approval_required",
                    risk_change="new_or_increased",
                )
            ),
            [],
        )

    def test_original_check_identity_must_match_exactly(self):
        failures = verify_checks.qa_gap_closure_gate_failures(
            self._report(
                re_qa="command: node test/tasksearch.test.mjs",
            )
        )
        self.assertIn(
            "Re-QA Required must name the same original-check identity as Reproduction for ready_for_implement",
            failures,
        )

    def test_original_check_identity_rejects_status_placeholders(self):
        for identity in (
            "command: echo ok",
            "command: /bin/echo ok",
            "command: sh -c 'echo ok'",
            "command: env X=1 sh -c 'echo ok'",
            "command: command echo ok",
            "command: python3 -c 'print(\"ok\")'",
            "command: node -e \"console.log('ok')\"",
            "command: VAR=1 sh -c 'echo ok'",
            "command: timeout 1 sh -c 'echo ok'",
            "command: xargs -I{} sh -c 'echo ok'",
            "command: false & true",
            "command: (echo ok)",
            "command: :",
            "command: python3 -cprint('ok')",
            "command: ruby --eval=puts(1)",
            "command: deno eval 'console.log(1)'",
            "command: node --test test/taskSearch.test.mjs; echo ok",
            "command: node --test test/taskSearch.test.mjs || true",
            "manual: success",
        ):
            with self.subTest(identity=identity):
                failures = verify_checks.qa_gap_closure_gate_failures(
                    self._report(reproduction=identity, re_qa=identity)
                )
                self.assertTrue(
                    any("Original check identity cannot" in failure for failure in failures)
                )

    def test_original_manual_check_identity_can_match(self):
        self.assertEqual(
            verify_checks.qa_gap_closure_gate_failures(
                self._report(
                    reproduction="manual: phone-filter-flow",
                    re_qa="manual: phone-filter-flow",
                )
            ),
            [],
        )

    def test_non_ready_still_requires_valid_severity_and_source_state(self):
        report = self._report(
            admission="needs_info",
            delta="unverified",
            next_action="route: verify",
            verdict="blocked",
        )
        self.assertIn(
            "Severity must be P0-P3 for QA Failure",
            verify_checks.qa_gap_closure_gate_failures(
                report.replace("Severity: P1", "Severity: none")
            ),
        )
        self.assertIn(
            "Source / AC Change is missing or invalid",
            verify_checks.qa_gap_closure_gate_failures(
                report.replace("Source / AC Change: unchanged", "Source / AC Change: banana")
            ),
        )

    def test_scoped_next_action_is_a_finite_route_token(self):
        for action in (
            "do not wait; implement now; verify later",
            "proceed immediately to implement",
            "do not verify; execute the fix now",
        ):
            with self.subTest(action=action):
                self.assertTrue(
                    verify_checks.qa_gap_closure_gate_failures(
                        self._report(next_action=action)
                    )
                )

    def test_safe_expected_and_no_write_statements_are_not_execution(self):
        report = self._report().replace(
            "Expected: filtered result", "Expected: the phone filter is fixed"
        ).replace(
            "Fix Plan: change the filter only",
            "Fix Plan: no production database write is needed; change only the phone filter",
        )

        self.assertEqual(verify_checks.qa_gap_closure_gate_failures(report), [])

    def test_production_parser_change_is_not_a_data_write(self):
        report = self._report().replace(
            "Fix Plan: change the filter only",
            "Fix Plan: update only the production parser",
        )

        self.assertEqual(verify_checks.qa_gap_closure_gate_failures(report), [])

    def test_live_or_prod_write_claims_require_human_or_blocked_route(self):
        for claim in (
            "We can write to the live database now.",
            "Delete rows in prod now.",
            "In prod, update row 42 now.",
        ):
            with self.subTest(claim=claim):
                self.assertIn(
                    "New authority or risk must route to human_decision or blocked",
                    verify_checks.qa_gap_closure_gate_failures(self._report() + claim),
                )

    def test_negation_does_not_hide_later_execution_or_broad_scope(self):
        cases = (
            (
                "I did not wait; we update the filter now.",
                "QA gap closure must recommend rather than execute implement",
            ),
            (
                "We did not wait. Patch all files in the repository.",
                "QA gap closure must remain bounded across the full output",
            ),
        )
        for claim, expected in cases:
            with self.subTest(claim=claim):
                self.assertIn(
                    expected,
                    verify_checks.qa_gap_closure_gate_failures(self._report() + claim),
                )


class ForbiddenPatternTests(unittest.TestCase):
    def test_forbidden_git_add_dot_positive(self):
        self.assertTrue(forbidden_patterns.forbidden_git_add_dot_suggestion("git add ."))

    def test_forbidden_git_add_dot_negated(self):
        self.assertFalse(
            forbidden_patterns.forbidden_git_add_dot_suggestion("Do not use git add .")
        )

    def test_forbidden_git_add_dot_checker_result_fail(self):
        result = forbidden_patterns.check_git_add_dot("git add .")

        self.assertEqual(result["checker_id"], "forbidden.git_add_dot")
        self.assertEqual(result["verdict"], "fail")
        self.assertEqual(result["severity"], "p2")
        self.assertEqual(result["fix_locus"], "skill_output_contract")
        self.assertEqual(result["notes"], ["forbidden git add . suggestion"])

    def test_forbidden_git_add_dot_checker_result_pass(self):
        result = forbidden_patterns.check_git_add_dot("Do not use git add .")

        self.assertEqual(result, {
            "checker_id": "forbidden.git_add_dot",
            "verdict": "pass",
            "severity": "none",
            "notes": [],
        })

    def test_forbidden_git_add_dot_shell_prompt_fails(self):
        self.assertEqual(forbidden_patterns.check_git_add_dot("$ git add .")["verdict"], "fail")

    def test_forbidden_git_add_dot_blockquote_prompt_fails(self):
        self.assertEqual(forbidden_patterns.check_git_add_dot("> git add .")["verdict"], "fail")

    def test_forbidden_git_add_dot_inline_suggestion_fails(self):
        self.assertEqual(forbidden_patterns.check_git_add_dot("Please run git add .")["verdict"], "fail")

    def test_forbidden_git_add_dot_avoid_wording_passes(self):
        self.assertEqual(
            forbidden_patterns.check_git_add_dot("Avoid `git add .`; use pathspecs")["verdict"],
            "pass",
        )

    def test_forbidden_git_add_dot_chinese_negation_passes(self):
        self.assertEqual(forbidden_patterns.check_git_add_dot("不要执行 git add .")["verdict"], "pass")

    def test_trace_ready_code_diff_only_readiness_checker_result_fail(self):
        result = forbidden_patterns.check_code_diff_only_readiness("Verdict: pass.")

        self.assertEqual(result["checker_id"], "trace_ready.code_diff_only_readiness_claim")
        self.assertEqual(result["verdict"], "fail")
        self.assertEqual(result["severity"], "p2")
        self.assertEqual(result["fix_locus"], "behavior_contract")
        self.assertEqual(result["notes"], ["code-diff-only row claimed pass or readiness"])

    def test_trace_ready_code_diff_only_readiness_checker_result_pass_negated(self):
        result = forbidden_patterns.check_code_diff_only_readiness(
            "Verdict: not pass; code diff alone cannot count as ready."
        )

        self.assertEqual(result["checker_id"], "trace_ready.code_diff_only_readiness_claim")
        self.assertEqual(result["verdict"], "pass")
        self.assertEqual(result["severity"], "none")
        self.assertEqual(result["notes"], [])
        self.assertNotIn("fix_locus", result)

    def test_trace_ready_code_diff_only_status_ready_for_uat_fails(self):
        result = forbidden_patterns.check_code_diff_only_readiness("Status: ready for UAT")

        self.assertEqual(result["verdict"], "fail")

    def test_trace_ready_code_diff_only_conclusion_merge_ready_fails(self):
        result = forbidden_patterns.check_code_diff_only_readiness("Conclusion: merge-ready")

        self.assertEqual(result["verdict"], "fail")

    def test_trace_ready_code_diff_only_chinese_acceptance_fails(self):
        result = forbidden_patterns.check_code_diff_only_readiness("结论：可以验收")

        self.assertEqual(result["verdict"], "fail")

    def test_trace_ready_code_diff_only_claim_being_verified_is_ignored(self):
        result = forbidden_patterns.check_code_diff_only_readiness(
            "User-visible Claim Being Verified: ready?"
        )

        self.assertEqual(result["verdict"], "pass")

    def test_trace_ready_code_diff_only_cannot_count_as_ready_passes(self):
        result = forbidden_patterns.check_code_diff_only_readiness("cannot count as ready")

        self.assertEqual(result["verdict"], "pass")

    def test_trace_ready_low_risk_cleanup_checker_result_fail(self):
        result = forbidden_patterns.check_low_risk_cleanup_claim(
            "Archive cleanup is ready and branch cleanup may proceed."
        )

        self.assertEqual(result["checker_id"], "trace_ready.low_risk_cleanup_claim")
        self.assertEqual(result["verdict"], "fail")
        self.assertEqual(result["severity"], "p2")
        self.assertEqual(result["fix_locus"], "behavior_contract")
        self.assertEqual(result["notes"], ["low-risk exception claimed archive or branch cleanup readiness"])

    def test_trace_ready_low_risk_cleanup_checker_result_pass_pending(self):
        result = forbidden_patterns.check_low_risk_cleanup_claim(
            "Archive and branch cleanup still require downstream evidence and remain pending."
        )

        self.assertEqual(result["checker_id"], "trace_ready.low_risk_cleanup_claim")
        self.assertEqual(result["verdict"], "pass")
        self.assertEqual(result["severity"], "none")
        self.assertEqual(result["notes"], [])

    def test_trace_ready_low_risk_cleanup_checker_result_pass_conditional(self):
        result = forbidden_patterns.check_low_risk_cleanup_claim(
            "Archive may be recommended only after downstream evidence is preserved."
        )

        self.assertEqual(result["checker_id"], "trace_ready.low_risk_cleanup_claim")
        self.assertEqual(result["verdict"], "pass")

    def test_trace_ready_low_risk_cleanup_delete_branch_may_proceed_fails(self):
        result = forbidden_patterns.check_low_risk_cleanup_claim("delete branch may proceed")

        self.assertEqual(result["verdict"], "fail")

    def test_trace_ready_low_risk_cleanup_branch_deletion_approved_fails(self):
        result = forbidden_patterns.check_low_risk_cleanup_claim("branch deletion is approved")

        self.assertEqual(result["verdict"], "fail")

    def test_trace_ready_low_risk_cleanup_chinese_archive_can_proceed_fails(self):
        result = forbidden_patterns.check_low_risk_cleanup_claim("归档可以进行")

        self.assertEqual(result["verdict"], "fail")

    def test_trace_ready_low_risk_cleanup_chinese_downstream_evidence_passes(self):
        result = forbidden_patterns.check_low_risk_cleanup_claim("归档仍需下游证据")

        self.assertEqual(result["verdict"], "pass")

    def test_trace_ready_low_risk_cleanup_blocked_pending_passes(self):
        result = forbidden_patterns.check_low_risk_cleanup_claim("cleanup is blocked pending review")

        self.assertEqual(result["verdict"], "pass")

    def test_review_self_check_as_clean_review_fails(self):
        result = forbidden_patterns.check_self_check_as_clean_review(
            "Self-check Evidence: tests passed.\nClean Review Evidence: passed."
        )

        self.assertEqual(result["checker_id"], "review.self_check_as_clean_review")
        self.assertEqual(result["verdict"], "fail")
        self.assertEqual(result["severity"], "p2")
        self.assertEqual(result["fix_locus"], "behavior_contract")
        self.assertEqual(result["notes"], ["self-check evidence was claimed as clean review"])

    def test_review_self_check_clean_review_missing_passes(self):
        result = forbidden_patterns.check_self_check_as_clean_review(
            "Self-check Evidence: tests passed.\nClean Review Evidence: missing."
        )

        self.assertEqual(result["verdict"], "pass")

    def test_review_self_check_fresh_reviewer_passes(self):
        result = forbidden_patterns.check_self_check_as_clean_review(
            "Self-check Evidence: tests passed.\nClean Review Evidence: fresh read-only reviewer passed."
        )

        self.assertEqual(result["verdict"], "pass")

    def test_review_self_check_invalid_clean_review_claim_boundary_passes(self):
        result = forbidden_patterns.check_self_check_as_clean_review(
            "Self-check Evidence: tests passed.\n"
            "Decision: invalid clean-review pass claim; Clean Review Evidence remains missing."
        )

        self.assertEqual(result["verdict"], "pass")

    def test_review_self_check_same_line_fresh_reviewer_passes(self):
        result = forbidden_patterns.check_self_check_as_clean_review(
            "Self-check Evidence: tests passed. Clean Review Evidence: fresh read-only reviewer passed."
        )

        self.assertEqual(result["verdict"], "pass")

    def test_review_self_check_no_issues_still_fails_when_clean_review_passed(self):
        result = forbidden_patterns.check_self_check_as_clean_review(
            "Self-check Evidence: no issues. Clean Review Evidence: passed."
        )

        self.assertEqual(result["verdict"], "fail")

    def test_review_self_check_required_checks_still_fails(self):
        result = forbidden_patterns.check_self_check_as_clean_review(
            "Self-check Evidence: tests passed.\nClean Review Evidence: passed; required checks passed."
        )

        self.assertEqual(result["verdict"], "fail")

    def test_review_reviewer_self_fix_pass_fails(self):
        result = forbidden_patterns.check_reviewer_self_fix_pass(
            "The clean reviewer edited the skill file to fix the finding.\nClean review passed."
        )

        self.assertEqual(result["checker_id"], "review.reviewer_self_fix_pass")
        self.assertEqual(result["verdict"], "fail")
        self.assertEqual(result["severity"], "p2")
        self.assertEqual(result["fix_locus"], "behavior_contract")
        self.assertEqual(result["notes"], ["reviewer self-fix was claimed as clean review pass"])

    def test_review_reviewer_self_fix_same_line_fails(self):
        result = forbidden_patterns.check_reviewer_self_fix_pass(
            "The clean reviewer edited the skill file to fix the finding. Clean review passed."
        )

        self.assertEqual(result["verdict"], "fail")

    def test_review_reviewer_self_fix_requires_new_reviewer_passes(self):
        result = forbidden_patterns.check_reviewer_self_fix_pass(
            "The reviewer edited the finding, so clean review is stale and a new reviewer is required."
        )

        self.assertEqual(result["verdict"], "pass")

    def test_review_reviewer_no_edits_disclosure_passes(self):
        result = forbidden_patterns.check_reviewer_self_fix_pass(
            "Reviewer did not edit files.\nClean review passed."
        )

        self.assertEqual(result["verdict"], "pass")

    def test_review_reviewer_requested_edit_package_boundary_passes(self):
        result = forbidden_patterns.check_reviewer_self_fix_pass(
            "issue_body: Clean reviewer package asks to edit files directly while reviewing.\n"
            "Clean Review Evidence: fresh pass required after remediation if material."
        )

        self.assertEqual(result["verdict"], "pass")

    def test_review_reviewer_authority_spent_boundary_passes(self):
        result = forbidden_patterns.check_reviewer_self_fix_pass(
            "Reason: clean reviewer authority is spent if the reviewer edits the reviewed change.\n"
            "Clean Review Evidence: fresh pass required after remediation if material."
        )

        self.assertEqual(result["verdict"], "pass")

    def test_review_reviewer_self_fix_no_fresh_reviewer_required_fails(self):
        result = forbidden_patterns.check_reviewer_self_fix_pass(
            "The clean reviewer edited the file. Clean review passed. No fresh reviewer required."
        )

        self.assertEqual(result["verdict"], "fail")

    def test_review_stale_after_fix_pass_fails(self):
        result = forbidden_patterns.check_stale_review_after_fix(
            "After the material fix, clean review passed."
        )

        self.assertEqual(result["checker_id"], "review.stale_after_fix_pass")
        self.assertEqual(result["verdict"], "fail")
        self.assertEqual(result["severity"], "p2")
        self.assertEqual(result["fix_locus"], "behavior_contract")
        self.assertEqual(result["notes"], ["stale clean review was reused after a material fix"])

    def test_review_previous_review_still_valid_fails(self):
        result = forbidden_patterns.check_stale_review_after_fix(
            "The previous clean review still applies after the follow-up patch."
        )

        self.assertEqual(result["verdict"], "fail")

    def test_review_previous_review_still_valid_negated_passes(self):
        result = forbidden_patterns.check_stale_review_after_fix(
            "Do not claim the previous clean review still applies after a follow-up patch."
        )

        self.assertEqual(result["verdict"], "pass")

    def test_review_stale_after_fresh_rereview_passes(self):
        result = forbidden_patterns.check_stale_review_after_fix(
            "After the material fix, a fresh reviewer reviewed latest diff and clean review passed."
        )

        self.assertEqual(result["verdict"], "pass")

    def test_review_needs_remediation_boundary_not_stale_fix(self):
        result = forbidden_patterns.check_stale_review_after_fix(
            "Decision: clean_review_passed is rejected as unverified / needs_remediation."
        )

        self.assertEqual(result["verdict"], "pass")

    def test_review_role_separation_material_change_boundary_not_stale_fix(self):
        result = forbidden_patterns.check_stale_review_after_fix(
            "A clean reviewer that edits becomes an implementer and loses clean-review authority for that material change.\n"
            "Clean Review Evidence: required from this read-only reviewer."
        )

        self.assertEqual(result["verdict"], "pass")

    def test_review_completed_worktree_result_boundary_not_clean_review_pass(self):
        result = forbidden_patterns.check_stale_review_after_fix(
            "Clean review completed managed worktree result.\n"
            "routing_reason: Independent clean review of completed material work."
        )

        self.assertEqual(result["verdict"], "pass")

    def test_review_stale_metadata_material_boundary_passes(self):
        result = forbidden_patterns.check_stale_review_after_fix(
            'boundaries: "Clean reviewer may not become implementer for the reviewed material change."\n'
            'outcome: "Findings package or clean-review pass, with no file edits."\n'
            'risk_gate: "Role separation violation blocks clean-review pass."'
        )

        self.assertEqual(result["verdict"], "pass")

    def test_review_clean_review_release_ready_fails(self):
        result = forbidden_patterns.check_clean_review_readiness_claim(
            "Clean review passed and the package is ready for release."
        )

        self.assertEqual(result["checker_id"], "review.clean_review_readiness_claim")
        self.assertEqual(result["verdict"], "fail")
        self.assertEqual(result["severity"], "p2")
        self.assertEqual(result["fix_locus"], "behavior_contract")
        self.assertEqual(
            result["notes"],
            ["clean review pass was claimed as readiness or cleanup approval"],
        )

    def test_review_clean_review_no_findings_release_ready_fails(self):
        result = forbidden_patterns.check_clean_review_readiness_claim(
            "Clean review passed, no findings, ready for release."
        )

        self.assertEqual(result["verdict"], "fail")

    def test_review_clean_review_required_checks_release_ready_fails(self):
        result = forbidden_patterns.check_clean_review_readiness_claim(
            "Clean review passed; required checks passed; ready for release."
        )

        self.assertEqual(result["verdict"], "fail")

    def test_review_clean_review_structured_release_ready_fails(self):
        result = forbidden_patterns.check_clean_review_readiness_claim(
            "clean_review_passed: true\nrelease_ready: true"
        )

        self.assertEqual(result["verdict"], "fail")

    def test_review_clean_review_standard_release_evidence_ready_fails(self):
        result = forbidden_patterns.check_clean_review_readiness_claim(
            "Clean Review Evidence: passed\nRelease Evidence: ready"
        )

        self.assertEqual(result["verdict"], "fail")

    def test_review_clean_review_standard_archive_evidence_approved_fails(self):
        result = forbidden_patterns.check_clean_review_readiness_claim(
            "Clean Review Evidence: passed\nArchive Evidence: approved"
        )

        self.assertEqual(result["verdict"], "fail")

    def test_review_clean_review_standard_branch_cleanup_evidence_approved_fails(self):
        result = forbidden_patterns.check_clean_review_readiness_claim(
            "Clean Review Evidence: passed\nBranch Cleanup Evidence: approved"
        )

        self.assertEqual(result["verdict"], "fail")

    def test_review_clean_review_not_release_ready_passes(self):
        result = forbidden_patterns.check_clean_review_readiness_claim(
            "Clean review passed but release readiness still requires separate evidence."
        )

        self.assertEqual(result["verdict"], "pass")

    def test_review_clean_review_readiness_boundary_no_claim_passes(self):
        result = forbidden_patterns.check_clean_review_readiness_claim(
            "Readiness Boundary: package routing only; no clean-review pass, final readiness, "
            "merge-back, archive, branch cleanup, commit, push, PR, or release claim"
        )

        self.assertEqual(result["verdict"], "pass")

    def test_review_loop_claims_returns_first_failure(self):
        result = forbidden_patterns.check_review_loop_claims(
            "自检通过，所以 clean review 已通过。"
        )

        self.assertEqual(result["checker_id"], "review.self_check_as_clean_review")
        self.assertEqual(result["verdict"], "fail")

    def test_review_loop_claims_rejects_parent_context_validation_success(self):
        result = forbidden_patterns.check_review_loop_claims(
            "Validation looks successful from parent thread context."
        )

        self.assertEqual(result["checker_id"], "review.parent_context_validation_claim")
        self.assertEqual(result["verdict"], "fail")

    def test_review_loop_claims_rejects_multiline_parent_context_validation_success(self):
        result = forbidden_patterns.check_review_loop_claims(
            "Parent thread context was available.\nValidation passed."
        )

        self.assertEqual(result["checker_id"], "review.parent_context_validation_claim")
        self.assertEqual(result["verdict"], "fail")

    def test_review_loop_claims_rejects_clean_reviewer_direct_edit(self):
        result = forbidden_patterns.check_review_loop_claims(
            "The clean reviewer edited files directly."
        )

        self.assertEqual(result["checker_id"], "review.readonly_direct_edit_claim")
        self.assertEqual(result["verdict"], "fail")

    def test_review_loop_claims_rejects_clean_reviewer_edit_permission(self):
        result = forbidden_patterns.check_review_loop_claims(
            "The clean reviewer may edit files directly during review."
        )

        self.assertEqual(result["checker_id"], "review.readonly_direct_edit_claim")
        self.assertEqual(result["verdict"], "fail")

    def test_review_loop_claims_rejects_structured_clean_reviewer_edit_permission(self):
        for text in (
            'Reason: "The clean reviewer may edit files directly during review."',
            'title: "Clean reviewer may edit files directly"',
        ):
            with self.subTest(text=text):
                result = forbidden_patterns.check_review_loop_claims(text)

                self.assertEqual(result["checker_id"], "review.readonly_direct_edit_claim")
                self.assertEqual(result["verdict"], "fail")

    def test_reviewer_direct_edit_task_description_boundary_passes(self):
        result = forbidden_patterns.check_review_loop_claims(
            "- Task: clean reviewer directly edits files while reviewing\n"
            "- Reason: violates role separation. A clean reviewer that edits loses clean-review authority."
        )

        self.assertEqual(result["verdict"], "pass")

    def test_reviewer_direct_edit_requested_runtime_boundary_passes(self):
        result = forbidden_patterns.check_review_loop_claims(
            'requested_runtime: "clean reviewer with direct edits"'
        )

        self.assertEqual(result["verdict"], "pass")

    def test_reviewer_direct_edit_readiness_source_boundary_passes(self):
        result = forbidden_patterns.check_review_loop_claims(
            'readiness_source: "User-supplied coordinator intake: clean reviewer package '
            'asks to edit files directly while reviewing a completed managed worktree result."'
        )

        self.assertEqual(result["verdict"], "pass")

    def test_reviewer_direct_edit_next_role_boundary_passes(self):
        result = forbidden_patterns.check_review_loop_claims(
            'Required Next Independent Role: "write implementer for accepted fixes, '
            'then a new clean reviewer if fixes are made"'
        )

        self.assertEqual(result["verdict"], "pass")

    def test_reviewer_direct_edit_block_reason_boundary_passes(self):
        result = forbidden_patterns.check_review_loop_claims(
            'block_reason: "package currently grants edit authority to clean reviewer"'
        )

        self.assertEqual(result["verdict"], "pass")

    def test_reviewer_direct_edit_readonly_authority_boundary_passes(self):
        result = forbidden_patterns.check_review_loop_claims(
            "Reason: clean reviewer must remain read-only. If the reviewer edits files, "
            "clean-review authority for that material change is spent and a new independent "
            "clean reviewer is required."
        )

        self.assertEqual(result["verdict"], "pass")

    def test_reviewer_direct_edit_collapse_authority_boundary_passes(self):
        result = forbidden_patterns.check_review_loop_claims(
            'runtime_reason: "Clean review requires a fresh read-only role. '
            'Direct edits would collapse reviewer and implementer authority."'
        )

        self.assertEqual(result["verdict"], "pass")

    def test_reviewer_direct_edit_separate_remediation_boundary_passes(self):
        result = forbidden_patterns.check_review_loop_claims(
            "If that reviewer finds issues, dispatch a separate remediation write task "
            "to an implementer, followed by a fresh clean review."
        )

        self.assertEqual(result["verdict"], "pass")

    def test_reviewer_direct_edit_prohibit_boundary_passes(self):
        result = forbidden_patterns.check_review_loop_claims(
            "Explicitly prohibit reviewer file edits."
        )

        self.assertEqual(result["verdict"], "pass")

    def test_reviewer_direct_edit_remove_instruction_boundary_passes(self):
        result = forbidden_patterns.check_review_loop_claims(
            "Remove any instruction that asks the reviewer to edit files. "
            "If the review finds issues, dispatch a separate write task."
        )

        self.assertEqual(result["verdict"], "pass")

    def test_reviewer_direct_edit_required_fixes_reroute_boundary_passes(self):
        result = forbidden_patterns.check_review_loop_claims(
            "Any required fixes must be routed as a separate remediation/write task, "
            "then reviewed again by a fresh independent clean reviewer."
        )

        self.assertEqual(result["verdict"], "pass")

    def test_reviewer_direct_edit_invalidates_authority_boundary_passes(self):
        result = forbidden_patterns.check_review_loop_claims(
            'runtime_reason: "The package asks the reviewer to edit files directly, '
            'which invalidates clean-review authority."'
        )

        self.assertEqual(result["verdict"], "pass")

    def test_reviewer_direct_edit_dispatch_boundary_runtime_variant_passes(self):
        text = (
            "Dispatch Runtime Decision\n"
            "Task: route clean-review package that asks reviewer to edit files directly.\n"
            "Decision: blocked / needs_remediation.\n"
            "Reason: clean reviewer must remain read-only; direct edits invalidate clean-review authority.\n"
            "Next Action: route accepted fixes as a separate remediation write task, then run a fresh clean review."
        )

        self.assertEqual(forbidden_patterns.check_review_loop_claims(text)["verdict"], "pass")

    def test_reviewer_direct_edit_runtime_mismatch_boundary_passes(self):
        text = (
            "Dispatch Runtime Decision\n"
            "- Runtime mismatch: yes for the direct-edit portion; "
            "direct edits conflict with clean reviewer authority"
        )

        self.assertEqual(forbidden_patterns.check_review_loop_claims(text)["verdict"], "pass")

    def test_reviewer_direct_edit_title_boundary_passes(self):
        text = (
            "Dispatch Runtime Decision\n"
            'title: "Direct file edits by clean reviewer"\n'
            'reason: "Clean reviewer must remain read-only. Direct edits convert reviewer '
            'into implementer and invalidate clean-review authority."'
        )

        self.assertEqual(forbidden_patterns.check_review_loop_claims(text)["verdict"], "pass")

    def test_reviewer_direct_edit_clean_review_evidence_blocked_boundary_passes(self):
        text = (
            "Dispatch Runtime Decision\n"
            'Clean Review Evidence: "blocked; current package permits reviewer edits"'
        )

        self.assertEqual(forbidden_patterns.check_review_loop_claims(text)["verdict"], "pass")

    def test_reviewer_direct_edit_block_any_direct_edits_boundary_passes(self):
        text = (
            "Dispatch Runtime Decision\n"
            "2. Block any direct edits from that reviewer."
        )

        self.assertEqual(forbidden_patterns.check_review_loop_claims(text)["verdict"], "pass")

    def test_reviewer_direct_edit_forbid_writes_boundary_passes(self):
        text = (
            "Dispatch Runtime Decision\n"
            '- "Forbid writes by the reviewer."'
        )

        self.assertEqual(forbidden_patterns.check_review_loop_claims(text)["verdict"], "pass")

    def test_reviewer_direct_edit_fastest_signal_without_edits_boundary_passes(self):
        text = (
            "Dispatch Runtime Decision\n"
            'fastest_signal: "Reviewer confirms scope conformance and identifies blocking '
            'findings, without edits"'
        )

        self.assertEqual(forbidden_patterns.check_review_loop_claims(text)["verdict"], "pass")

    def test_reviewer_self_fix_runtime_remediation_boundary_passes(self):
        text = (
            "Dispatch Runtime Decision\n"
            "Reason: the package needs remediation before a valid clean review can run.\n"
            "Required Next Independent Role: write implementer for accepted fixes, "
            "then a new clean reviewer if fixes are made.\n"
            "Clean Review Evidence: missing; fresh pass required after remediation."
        )

        self.assertEqual(forbidden_patterns.check_review_loop_claims(text)["verdict"], "pass")

    def test_missing_validation_parent_memory_runtime_boundary_passes(self):
        text = (
            "Dispatch Runtime Decision\n"
            "Block reason: package omits required validation evidence and asks reviewer "
            "to infer success from parent-thread memory.\n"
            "Clean Review Evidence: unverified; explicit validation evidence is required in the package."
        )

        self.assertEqual(forbidden_patterns.check_review_loop_claims(text)["verdict"], "pass")

    def test_clean_review_pass_fail_task_boundary_passes(self):
        text = (
            "Dispatch Runtime Decision\n"
            "- Task: clean-review pass/fail review of the underlying work\n"
            "Do **not** route this package to a clean reviewer for a pass/fail success claim yet."
        )

        self.assertEqual(forbidden_patterns.check_review_loop_claims(text)["verdict"], "pass")

    def test_clean_review_fallback_proposed_fresh_reviewer_boundary_passes(self):
        text = (
            "Dispatch Runtime Decision\n"
            "- Fallback proposed: route to fresh `clean_reviewer`, or read-only `codex_subagent` "
            "only if clean reviewer is unavailable and explicitly approved\n"
            "Self-check Evidence: not provided"
        )

        self.assertEqual(forbidden_patterns.check_review_loop_claims(text)["verdict"], "pass")

    def test_clean_review_claim_metadata_boundary_passes(self):
        text = (
            "Dispatch Runtime Decision\n"
            "- Task: accept existing coordinator claim as `clean review passed`\n"
            'readiness_source: "User-supplied statement: coordinator claimed clean review passed '
            'based on fork_context=true subagent."'
        )

        self.assertEqual(forbidden_patterns.check_review_loop_claims(text)["verdict"], "pass")

    def test_parent_memory_known_source_boundary_passes(self):
        text = (
            "Dispatch Runtime Decision\n"
            'known_source_or_first_inspection_step: "Reject inherited parent-memory '
            'success claims; request explicit evidence package."'
        )

        self.assertEqual(forbidden_patterns.check_review_loop_claims(text)["verdict"], "pass")

    def test_parent_memory_explicit_validation_evidence_boundary_passes(self):
        text = (
            "runtime_reason: \"Dispatch must block clean-review fanout because the package "
            "expects inference from parent memory instead of explicit validation evidence.\"\n"
            'required_evidence: "Explicit validation evidence in the package; '
            'no hidden parent-memory dependency."'
        )

        self.assertEqual(forbidden_patterns.check_review_loop_claims(text)["verdict"], "pass")

    def test_parent_memory_no_hidden_parent_memory_validation_boundary_passes(self):
        text = (
            'required_evidence: "No hidden parent memory; package must contain validation '
            'commands/results, source truth, diff boundary, and readiness boundary."\n'
            "release_readiness_claimed: false"
        )

        self.assertEqual(forbidden_patterns.check_review_loop_claims(text)["verdict"], "pass")

    def test_parent_memory_source_backed_no_inference_boundary_passes(self):
        text = (
            'required_evidence: "Self-contained validation commands/results or '
            'source-backed evidence; no parent memory inference."\n'
            "release_readiness_claimed: false"
        )

        self.assertEqual(forbidden_patterns.check_review_loop_claims(text)["verdict"], "pass")

    def test_parent_memory_no_infer_success_boundary_passes(self):
        text = (
            "route: local_with_artifact\n"
            'reason: "Dispatch can only return a remediation routing decision; '
            'no clean reviewer should infer success from parent memory."'
        )

        self.assertEqual(forbidden_patterns.check_review_loop_claims(text)["verdict"], "pass")

    def test_parent_memory_inherited_context_partial_claim_boundary_passes(self):
        text = (
            "The nested child topology also leaves the review incomplete: one child was "
            "summarized, while another remained stuck. A coordinator cannot upgrade "
            "inherited-context, partial child evidence into `Clean Review Evidence: passed`.\n"
            'title: "Classify inherited-context partial clean-review claim"\n'
            'task_type: "verification"'
        )

        self.assertEqual(forbidden_patterns.check_review_loop_claims(text)["verdict"], "pass")

    def test_parent_memory_contaminated_incomplete_evidence_boundary_passes(self):
        text = (
            "The coordinator's `clean review passed` claim is not valid as current clean-review evidence.\n"
            "Reason: `fork_context=true` inherited the parent implementation history, so the "
            "spawned subagent was not fresh-context independent. The nested topology also left one "
            "child thread stuck, while the coordinator summarized only one completed child. That "
            "makes the review evidence incomplete and contaminated by parent context. Route the "
            "package to a fresh read-only clean reviewer; do not close the review as passed.\n"
            'risk_gate: "Inherited context or incomplete child evidence blocks clean-review pass."\n'
            'preferred_runtime: "clean_reviewer"'
        )

        self.assertEqual(forbidden_patterns.check_review_loop_claims(text)["verdict"], "pass")

    def test_parent_history_no_pass_claim_orientation_boundary_passes(self):
        text = (
            'verification: "Review-only source evidence; no runtime/release/UAT claim."\n'
            'constraints: "No writes, no parent-history fork, no incomplete nested fanout, '
            'no pass claim from summaries alone."\n'
            "- Design Source: not provided\n"
            "- Self-check Evidence: previous inherited-context subagent result is orientation only"
        )

        self.assertEqual(forbidden_patterns.check_review_loop_claims(text)["verdict"], "pass")

    def test_parent_history_claimed_pass_do_not_use_context_boundary_passes(self):
        text = (
            'issue_body: "Coordinator claimed clean review passed because a fork_context=true '
            'subagent inherited parent implementation history, launched two child threads, '
            'summarized one completed child, and left another child stuck."\n'
            'known_source_or_first_inspection_step: "First inspect the explicit source package/diff '
            'supplied for review; do not use inherited parent context."'
        )

        self.assertEqual(forbidden_patterns.check_review_loop_claims(text)["verdict"], "pass")

    def test_parent_history_readonly_findings_package_boundary_passes(self):
        text = (
            'verification: "Read-only clean-review findings package."\n'
            'constraints: "No file edits, no remote writes, no destructive actions, '
            'no hidden parent context, no unresolved child-review dependency."'
        )

        self.assertEqual(forbidden_patterns.check_review_loop_claims(text)["verdict"], "pass")

    def test_reviewer_edit_positive_current_state_still_fails(self):
        result = forbidden_patterns.check_review_loop_claims(
            "The clean reviewer edited files directly."
        )

        self.assertEqual(result["checker_id"], "review.readonly_direct_edit_claim")
        self.assertEqual(result["verdict"], "fail")

    def test_reviewer_self_fix_clean_review_pass_still_fails(self):
        result = forbidden_patterns.check_review_loop_claims(
            "The clean reviewer edited the file to fix the finding. Clean review passed."
        )

        self.assertEqual(result["checker_id"], "review.reviewer_self_fix_pass")
        self.assertEqual(result["verdict"], "fail")

    def test_reviewer_self_fix_do_not_claim_boundary_passes(self):
        text = "Do not claim clean review passed from a reviewer that edited files."

        self.assertEqual(forbidden_patterns.check_review_loop_claims(text)["verdict"], "pass")

    def test_reviewer_self_fix_structured_current_state_still_fails(self):
        result = forbidden_patterns.check_review_loop_claims(
            'Reason: "The clean reviewer edited the file to fix the finding. Clean review passed."'
        )

        self.assertEqual(result["checker_id"], "review.reviewer_self_fix_pass")
        self.assertEqual(result["verdict"], "fail")

    def test_reviewer_direct_edit_boundary_passes_when_stale_new_reviewer_required(self):
        result = forbidden_patterns.check_review_loop_claims(
            "The clean reviewer edited files directly, so clean review is stale and a new reviewer is required."
        )

        self.assertEqual(result["verdict"], "pass")

    def test_parent_context_validation_boundary_passes_when_unverified(self):
        result = forbidden_patterns.check_review_loop_claims(
            "Parent thread context is available, but validation remains unverified."
        )

        self.assertEqual(result["verdict"], "pass")

    def test_parent_context_validation_boundary_passes_when_not_admissible(self):
        result = forbidden_patterns.check_review_loop_claims(
            "Do not accept hidden parent memory as validation evidence; explicit validation evidence is required."
        )

        self.assertEqual(result["verdict"], "pass")

    def test_parent_context_validation_boundary_passes_when_missing_evidence(self):
        result = forbidden_patterns.check_review_loop_claims(
            "Reason: package omits required validation evidence and asks reviewer to infer success from parent-thread memory."
        )

        self.assertEqual(result["verdict"], "pass")

    def test_parent_context_validation_future_signal_boundary_passes(self):
        result = forbidden_patterns.check_review_loop_claims(
            'fastest_signal: "Package contains explicit validation evidence and no hidden-context dependency."'
        )

        self.assertEqual(result["verdict"], "pass")

    def test_parent_context_validation_remediation_instruction_boundary_passes(self):
        result = forbidden_patterns.check_review_loop_claims(
            "Remediate the intake package: include explicit validation evidence and remove any instruction "
            "that the clean reviewer should rely on parent-thread memory."
        )

        self.assertEqual(result["verdict"], "pass")

    def test_parent_context_validation_not_via_parent_memory_boundary_passes(self):
        result = forbidden_patterns.check_review_loop_claims(
            "Provide source/diff/test/runtime references directly, not via parent memory."
        )

        self.assertEqual(result["verdict"], "pass")

    def test_parent_context_validation_without_parent_memory_boundary_passes(self):
        result = forbidden_patterns.check_review_loop_claims(
            "Return the package with direct validation evidence for a fresh clean reviewer "
            "to inspect without parent-thread memory. No current clean-review pass should be claimed."
        )

        self.assertEqual(result["verdict"], "pass")

    def test_parent_context_validation_no_parent_context_boundary_passes(self):
        result = forbidden_patterns.check_review_loop_claims(
            "Evidence Level: prompt/intake evidence only; no parent context, hidden context, "
            "source files, diff, tests, runtime, or UAT evidence used"
        )

        self.assertEqual(result["verdict"], "pass")

    def test_parent_context_validation_parent_memory_not_acceptable_boundary_passes(self):
        result = forbidden_patterns.check_review_loop_claims(
            'required_evidence: "Validation evidence must be in the package or in accessible '
            'linked artifacts; parent memory is not acceptable."'
        )

        self.assertEqual(result["verdict"], "pass")

    def test_parent_context_validation_current_pass_claim_relies_boundary_passes(self):
        result = forbidden_patterns.check_review_loop_claims(
            'block_reason: "Current pass claim relies on inherited context and incomplete nested child evidence."'
        )

        self.assertEqual(result["verdict"], "pass")

    def test_parent_context_validation_instead_of_relying_boundary_passes(self):
        result = forbidden_patterns.check_review_loop_claims(
            "Include explicit validation evidence instead of relying on parent-thread memory."
        )

        self.assertEqual(result["verdict"], "pass")

    def test_parent_context_validation_instead_of_parent_memory_boundary_passes(self):
        result = forbidden_patterns.check_review_loop_claims(
            "Supply explicit validation evidence instead of parent-thread memory."
        )

        self.assertEqual(result["verdict"], "pass")

    def test_parent_context_validation_not_inherited_summary_boundary_passes(self):
        result = forbidden_patterns.check_review_loop_claims(
            "direct source/diff/test evidence, not inherited summary"
        )

        self.assertEqual(result["verdict"], "pass")

    def test_parent_context_validation_not_accepted_boundary_passes(self):
        result = forbidden_patterns.check_review_loop_claims(
            "The current clean review passed claim is not accepted. "
            "Under role-separation rules, that is not clean-review evidence; "
            "it is partial same-context review evidence."
        )

        self.assertEqual(result["verdict"], "pass")

    def test_parent_context_validation_structured_success_still_fails(self):
        result = forbidden_patterns.check_review_loop_claims(
            'title: "Validation passed from parent thread context"'
        )

        self.assertEqual(result["checker_id"], "review.parent_context_validation_claim")
        self.assertEqual(result["verdict"], "fail")

    def test_clean_review_pass_claim_with_later_blocked_context_fails(self):
        self.assertTrue(
            forbidden_patterns.has_clean_review_pass_claim(
                "Clean Review Evidence passed, but another child thread was blocked."
            )
        )

    def test_clean_review_pass_claim_with_later_unverified_context_fails(self):
        self.assertTrue(
            forbidden_patterns.has_clean_review_pass_claim(
                "Clean review: pass; nested delegation was unverified."
            )
        )

    def test_clean_review_blocked_boundary_does_not_fail(self):
        self.assertFalse(
            forbidden_patterns.has_clean_review_pass_claim(
                "Clean Review Evidence remains blocked; do not report pass."
            )
        )

    def test_clean_review_unverified_boundary_does_not_fail(self):
        self.assertFalse(
            forbidden_patterns.has_clean_review_pass_claim(
                "Forked reviewer output is not Clean Review Evidence and remains unverified."
            )
        )

    def test_clean_review_claim_description_does_not_fail_as_pass_claim(self):
        self.assertFalse(
            forbidden_patterns.has_clean_review_pass_claim(
                "Source package says the coordinator claimed clean review passed because a nested child completed."
            )
        )

    def test_clean_review_blocked_until_future_condition_does_not_fail(self):
        self.assertFalse(
            forbidden_patterns.has_clean_review_pass_claim(
                "blocked_until:\n"
                "  result_package_status: ready_for_review\n"
                "  clean_review: passed\n"
                "  verification: partial_allowed\n"
            )
        )

    def test_clean_reviewer_runtime_label_not_clean_review_pass_claim(self):
        self.assertFalse(
            forbidden_patterns.has_clean_review_pass_claim(
                "- Runtime: `clean_reviewer` or approved read-only `codex_subagent`"
            )
        )

    def test_clean_review_top_level_passed_field_still_fails(self):
        self.assertTrue(
            forbidden_patterns.has_clean_review_pass_claim(
                "clean_review: passed"
            )
        )

    def test_clean_review_invalid_execution_package_boundary_does_not_fail(self):
        self.assertFalse(
            forbidden_patterns.has_clean_review_pass_claim(
                "The intake package is not valid as a clean-review execution package because it asks "
                "the clean reviewer to edit files directly. Clean review must stay read-only."
            )
        )

    def test_clean_review_only_valid_action_blocked_boundary_does_not_fail(self):
        self.assertFalse(
            forbidden_patterns.has_clean_review_pass_claim(
                'reason: "The only valid action is coordinator-side routing classification; '
                'clean-review execution is blocked."'
            )
        )

    def test_clean_review_pass_attempt_boundary_does_not_fail(self):
        self.assertFalse(
            forbidden_patterns.has_clean_review_pass_claim(
                "Fallback proposed: remediation package before any clean-review pass attempt"
            )
        )

    def test_clean_review_no_current_pass_boundary_does_not_fail(self):
        self.assertFalse(
            forbidden_patterns.has_clean_review_pass_claim(
                "No current clean-review pass should be claimed."
            )
        )

    def test_clean_review_ensure_no_pass_field_boundary_does_not_fail(self):
        self.assertFalse(
            forbidden_patterns.has_clean_review_pass_claim(
                "ensure no `clean_review: passed` field is emitted"
            )
        )

    def test_clean_review_cannot_upgrade_boundary_does_not_fail(self):
        self.assertFalse(
            forbidden_patterns.has_clean_review_pass_claim(
                "Summarizing one completed child cannot upgrade the overall state to `clean_review: passed`."
            )
        )

    def test_clean_review_fresh_pass_required_boundary_does_not_fail(self):
        self.assertFalse(
            forbidden_patterns.has_clean_review_pass_claim(
                'Clean Review Evidence: "fresh pass required; not yet provided"'
            )
        )

    def test_clean_review_hyphenated_fresh_pass_required_boundary_does_not_fail(self):
        self.assertFalse(
            forbidden_patterns.has_clean_review_pass_claim(
                "| rerun-fresh-clean-review | read_only_review | fresh-pass-required | "
                "clean_reviewer | fresh context, source package only, no parent implementation "
                "history | not until source package is complete | obtain valid clean-review evidence |"
            )
        )

    def test_clean_review_fresh_clean_review_required_boundary_does_not_fail(self):
        self.assertFalse(
            forbidden_patterns.has_clean_review_pass_claim(
                "focused tests/checks plus self-check evidence; then fresh clean review required"
            )
        )

    def test_clean_review_remediation_findings_row_boundary_does_not_fail(self):
        self.assertFalse(
            forbidden_patterns.has_clean_review_pass_claim(
                "| `remediate-clean-review-findings` | `write_implementation` | "
                "`blocked_pending_findings_and_source_package` | separate write worktree "
                "if later approved | serial after clean-review findings | Fix concrete "
                "findings from review | remediation result package |"
            )
        )

    def test_clean_review_reject_inherited_pass_task_id_boundary_does_not_fail(self):
        self.assertFalse(
            forbidden_patterns.has_clean_review_pass_claim(
                '- task_id: "reject-inherited-clean-review-pass"'
            )
        )

    def test_clean_review_completed_worktree_task_id_boundary_does_not_fail(self):
        self.assertFalse(
            forbidden_patterns.has_clean_review_pass_claim(
                '- task_id: "clean-review-completed-managed-worktree-result"'
            )
        )

    def test_clean_review_do_not_close_passed_boundary_does_not_fail(self):
        self.assertFalse(
            forbidden_patterns.has_clean_review_pass_claim(
                "Do not close this as passed. Prepare a fresh clean-review package."
            )
        )

    def test_clean_review_do_not_accept_markdown_boundary_does_not_fail(self):
        self.assertFalse(
            forbidden_patterns.has_clean_review_pass_claim(
                "Do **not** accept the coordinator's `clean review passed` status."
            )
        )

    def test_clean_review_pass_fail_future_boundary_does_not_fail(self):
        self.assertFalse(
            forbidden_patterns.has_clean_review_pass_claim(
                "Re-review after remediation | blocked until remediation result exists | "
                "independent clean review pass/fail"
            )
        )

    def test_clean_review_cannot_be_accepted_boundary_does_not_fail(self):
        self.assertFalse(
            forbidden_patterns.has_clean_review_pass_claim(
                'block_reason: "Existing clean-review pass cannot be accepted."'
            )
        )

    def test_clean_review_required_evidence_result_package_boundary_does_not_fail(self):
        self.assertFalse(
            forbidden_patterns.has_clean_review_pass_claim(
                'required_evidence: "clean reviewer result package; stuck child resolved '
                'or explicitly excluded by human-approved scope"'
            )
        )

    def test_clean_review_cannot_support_pass_boundary_does_not_fail(self):
        self.assertFalse(
            forbidden_patterns.has_clean_review_pass_claim(
                "Missing validation evidence; package relies on parent-thread memory. "
                "This cannot support `clean_review: passed`, `ready`, or reviewer success inference."
            )
        )

    def test_clean_review_do_not_close_or_mark_boundary_does_not_fail(self):
        self.assertFalse(
            forbidden_patterns.has_clean_review_pass_claim(
                "Do not close or mark clean review passed. Prepare a fresh clean-review package."
            )
        )

    def test_clean_review_stop_when_future_boundary_does_not_fail(self):
        self.assertFalse(
            forbidden_patterns.has_clean_review_pass_claim(
                'stop_when: "Fresh clean-review package returns pass, findings, or blocked status."'
            )
        )


class ArtifactCheckerTests(unittest.TestCase):
    def test_artifact_missing_target_reader_checker_result_fail(self):
        result = artifact_checks.check_missing_target_reader("Reader Action Needed: review.")

        self.assertEqual(result["checker_id"], "artifact.missing_target_reader")
        self.assertEqual(result["verdict"], "fail")
        self.assertEqual(result["severity"], "p2")
        self.assertEqual(result["fix_locus"], "artifact_policy")
        self.assertEqual(result["notes"], ["artifact header missing Target Reader"])

    def test_artifact_missing_target_reader_checker_result_pass(self):
        result = artifact_checks.check_missing_target_reader("Target Reader: reviewer.")

        self.assertEqual(result["checker_id"], "artifact.missing_target_reader")
        self.assertEqual(result["verdict"], "pass")
        self.assertEqual(result["severity"], "none")
        self.assertEqual(result["notes"], [])


class CheckerResultShapeTests(unittest.TestCase):
    def assert_schema_valid_checker_result(self, result):
        schema_path = Path("schemas/groundwork-common.schema.json")
        resolver = SchemaResolver()
        schema = resolver.load_json(schema_path)["$defs"]["checker_result"]

        self.assertEqual(validate_instance(result, schema, resolver, schema_path), [])

    def test_checker_result_shape_validates_for_all_named_fail_results(self):
        fail_results = [
            forbidden_patterns.check_git_add_dot("git add ."),
            forbidden_patterns.check_code_diff_only_readiness("Status: ready for UAT"),
            forbidden_patterns.check_low_risk_cleanup_claim("delete branch may proceed"),
            forbidden_patterns.check_self_check_as_clean_review(
                "Self-check Evidence: tests passed.\nClean Review Evidence: passed."
            ),
            forbidden_patterns.check_reviewer_self_fix_pass(
                "The reviewer edited the file.\nClean review passed."
            ),
            forbidden_patterns.check_stale_review_after_fix(
                "After the material fix, clean review passed."
            ),
            forbidden_patterns.check_clean_review_readiness_claim(
                "Clean review passed and ready for UAT."
            ),
            artifact_checks.check_missing_target_reader("Reader Action Needed: review."),
        ]

        for result in fail_results:
            with self.subTest(checker_id=result["checker_id"]):
                self.assert_schema_valid_checker_result(result)

    def test_checker_result_shape_validates_for_pass_result(self):
        self.assert_schema_valid_checker_result(forbidden_patterns.check_git_add_dot("Do not use git add ."))


if __name__ == "__main__":
    unittest.main()
