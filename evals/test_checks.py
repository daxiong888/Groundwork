#!/usr/bin/env python3
import unittest
from pathlib import Path

from evals.checks import forbidden_patterns
from evals.schema_validation import SchemaResolver, validate_instance


class ForbiddenPatternTests(unittest.TestCase):
    def test_forbidden_git_add_dot_positive(self):
        self.assertTrue(forbidden_patterns.forbidden_git_add_dot_suggestion("git add ."))

    def test_forbidden_git_add_dot_negated(self):
        self.assertFalse(
            forbidden_patterns.forbidden_git_add_dot_suggestion("Do not use git add .")
        )

    def test_git_add_dot_checker_result_fail(self):
        result = forbidden_patterns.check_git_add_dot("git add .")

        self.assertEqual(result["checker_id"], "forbidden.git_add_dot")
        self.assertEqual(result["verdict"], "fail")
        self.assertEqual(result["severity"], "p2")
        self.assertEqual(result["fix_locus"], "skill_output_contract")
        self.assertEqual(result["notes"], ["forbidden git add . suggestion"])

    def test_git_add_dot_checker_result_pass(self):
        result = forbidden_patterns.check_git_add_dot("Do not use git add .")

        self.assertEqual(result, {
            "checker_id": "forbidden.git_add_dot",
            "verdict": "pass",
            "severity": "none",
            "notes": [],
        })

    def test_code_diff_only_checker_result_fail(self):
        result = forbidden_patterns.check_code_diff_only_readiness("Verdict: pass.")

        self.assertEqual(result["checker_id"], "trace_ready.code_diff_only_readiness_claim")
        self.assertEqual(result["verdict"], "fail")
        self.assertEqual(result["severity"], "p2")
        self.assertEqual(result["fix_locus"], "behavior_contract")
        self.assertEqual(result["notes"], ["code-diff-only row claimed pass or readiness"])

    def test_code_diff_only_checker_result_pass_negated(self):
        result = forbidden_patterns.check_code_diff_only_readiness(
            "Verdict: not pass; code diff alone cannot count as ready."
        )

        self.assertEqual(result["checker_id"], "trace_ready.code_diff_only_readiness_claim")
        self.assertEqual(result["verdict"], "pass")
        self.assertEqual(result["severity"], "none")
        self.assertEqual(result["notes"], [])
        self.assertNotIn("fix_locus", result)

    def test_low_risk_cleanup_checker_result_fail(self):
        result = forbidden_patterns.check_low_risk_cleanup_claim(
            "Archive cleanup is ready and branch cleanup may proceed."
        )

        self.assertEqual(result["checker_id"], "trace_ready.low_risk_cleanup_claim")
        self.assertEqual(result["verdict"], "fail")
        self.assertEqual(result["severity"], "p2")
        self.assertEqual(result["fix_locus"], "behavior_contract")
        self.assertEqual(result["notes"], ["low-risk exception claimed archive or branch cleanup readiness"])

    def test_low_risk_cleanup_checker_result_pass_pending(self):
        result = forbidden_patterns.check_low_risk_cleanup_claim(
            "Archive and branch cleanup still require downstream evidence and remain pending."
        )

        self.assertEqual(result["checker_id"], "trace_ready.low_risk_cleanup_claim")
        self.assertEqual(result["verdict"], "pass")
        self.assertEqual(result["severity"], "none")
        self.assertEqual(result["notes"], [])

    def test_low_risk_cleanup_checker_result_pass_conditional(self):
        result = forbidden_patterns.check_low_risk_cleanup_claim(
            "Archive may be recommended only after downstream evidence is preserved."
        )

        self.assertEqual(result["checker_id"], "trace_ready.low_risk_cleanup_claim")
        self.assertEqual(result["verdict"], "pass")

    def test_missing_target_reader_checker_result_fail(self):
        result = forbidden_patterns.check_missing_target_reader("Reader Action Needed: review.")

        self.assertEqual(result["checker_id"], "artifact.missing_target_reader")
        self.assertEqual(result["verdict"], "fail")
        self.assertEqual(result["severity"], "p2")
        self.assertEqual(result["fix_locus"], "artifact_policy")
        self.assertEqual(result["notes"], ["artifact header missing Target Reader"])

    def test_missing_target_reader_checker_result_pass(self):
        result = forbidden_patterns.check_missing_target_reader("Target Reader: reviewer.")

        self.assertEqual(result["checker_id"], "artifact.missing_target_reader")
        self.assertEqual(result["verdict"], "pass")
        self.assertEqual(result["severity"], "none")
        self.assertEqual(result["notes"], [])

    def test_checker_result_matches_common_schema_shape(self):
        schema_path = Path("schemas/groundwork-common.schema.json")
        resolver = SchemaResolver()
        schema = resolver.load_json(schema_path)["$defs"]["checker_result"]
        result = forbidden_patterns.check_git_add_dot("git add .")

        self.assertEqual(validate_instance(result, schema, resolver, schema_path), [])


if __name__ == "__main__":
    unittest.main()
