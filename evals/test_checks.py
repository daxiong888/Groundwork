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
