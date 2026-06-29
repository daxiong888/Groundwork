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

    def test_review_clean_review_structured_release_ready_fails(self):
        result = forbidden_patterns.check_clean_review_readiness_claim(
            "clean_review_passed: true\nrelease_ready: true"
        )

        self.assertEqual(result["verdict"], "fail")

    def test_review_clean_review_not_release_ready_passes(self):
        result = forbidden_patterns.check_clean_review_readiness_claim(
            "Clean review passed but release readiness still requires separate evidence."
        )

        self.assertEqual(result["verdict"], "pass")

    def test_review_loop_claims_returns_first_failure(self):
        result = forbidden_patterns.check_review_loop_claims(
            "自检通过，所以 clean review 已通过。"
        )

        self.assertEqual(result["checker_id"], "review.self_check_as_clean_review")
        self.assertEqual(result["verdict"], "fail")


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
