#!/usr/bin/env python3
import json
import tempfile
import unittest
from pathlib import Path

from evals import schema_validation, scoring


ROOT = Path(__file__).resolve().parents[1]
SCORE_SCHEMA = ROOT / "schemas" / "groundwork-eval-score.schema.json"
RUNNER_RESULT = ROOT / "evals" / "fixtures" / "score" / "runner-result.json"


class ScoringTests(unittest.TestCase):
    def validate_score(self, score):
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".json") as handle:
            json.dump(score, handle)
            handle.flush()
            return schema_validation.validate_json_file(SCORE_SCHEMA, Path(handle.name))

    def test_forbidden_behavior_runner_result_becomes_valid_score(self):
        result = json.loads(RUNNER_RESULT.read_text(encoding="utf-8"))

        score = scoring.score_from_result(result)

        self.assertEqual(score["failure_type"], "forbidden_behavior")
        self.assertEqual(score["fix_locus"], "behavior_contract")
        self.assertEqual(score["score_subject"], "verify")
        self.assertEqual(self.validate_score(score), [])

    def test_missing_optional_fields_produce_valid_generic_score(self):
        score = scoring.score_from_result(
            {
                "id": "minimal",
                "suite": "smoke.csv",
                "verdict": "pass",
            }
        )

        self.assertEqual(score["expected_skill"], "unknown")
        self.assertEqual(score["triggered_skill"], "unknown")
        self.assertEqual(score["score_subject"], "generic")
        self.assertEqual(score["failure_type"], "none")
        self.assertNotIn("fix_locus", score)
        self.assertEqual(self.validate_score(score), [])

    def test_unknown_or_empty_failure_type_normalizes(self):
        empty = scoring.score_from_result({"id": "empty", "suite": "suite.csv", "failure_type": ""})
        unknown = scoring.score_from_result(
            {"id": "unknown", "suite": "suite.csv", "failure_type": "not_current_runner_value"}
        )

        self.assertEqual(empty["failure_type"], "none")
        self.assertEqual(unknown["failure_type"], "unknown")
        self.assertEqual(self.validate_score(empty), [])
        self.assertEqual(self.validate_score(unknown), [])

    def test_timeout_overall_verdict_normalizes_to_blocked(self):
        score = scoring.score_from_result(
            {
                "id": "timeout",
                "suite": "routing-reliability.csv",
                "verdict": "timeout",
                "failure_type": "codex_timeout",
                "fix_locus": "runtime_environment",
            }
        )

        self.assertEqual(score["overall_verdict"], "blocked")
        self.assertEqual(score["failure_type"], "codex_timeout")
        self.assertEqual(self.validate_score(score), [])

    def test_clean_review_boundary_infers_review_subject(self):
        score = scoring.score_from_result(
            {
                "id": "clean-review",
                "suite": "trace-first-verify-review.csv",
                "expected_route": "dispatch",
                "actual_route": "dispatch",
                "route_boundary": "clean-review-fanout",
                "verdict": "pass",
            }
        )

        self.assertEqual(score["score_subject"], "review")
        self.assertEqual(self.validate_score(score), [])


if __name__ == "__main__":
    unittest.main()
