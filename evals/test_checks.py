#!/usr/bin/env python3
import unittest
from pathlib import Path

from evals.checks import artifact_checks, common, forbidden_patterns
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
            artifact_checks.check_missing_target_reader("Reader Action Needed: review."),
        ]

        for result in fail_results:
            with self.subTest(checker_id=result["checker_id"]):
                self.assert_schema_valid_checker_result(result)

    def test_checker_result_shape_validates_for_pass_result(self):
        self.assert_schema_valid_checker_result(forbidden_patterns.check_git_add_dot("Do not use git add ."))


if __name__ == "__main__":
    unittest.main()
