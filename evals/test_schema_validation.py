#!/usr/bin/env python3
import contextlib
import io
import unittest
from pathlib import Path

from evals import schema_validation


ROOT = Path(__file__).resolve().parents[1]
SCORE_SCHEMA = ROOT / "schemas" / "groundwork-eval-score.schema.json"
VALID_SCORE = ROOT / "evals" / "fixtures" / "score" / "valid-eval-score.json"
INVALID_SCORE = ROOT / "evals" / "fixtures" / "score" / "invalid-eval-score.json"


class SchemaValidationTests(unittest.TestCase):
    def test_valid_eval_score_fixture_passes(self):
        self.assertEqual(
            schema_validation.validate_json_file(SCORE_SCHEMA, VALID_SCORE),
            [],
        )

    def test_invalid_eval_score_fixture_reports_schema_error(self):
        errors = schema_validation.validate_json_file(SCORE_SCHEMA, INVALID_SCORE)

        self.assertTrue(errors)
        self.assertTrue(any("$.failure_type" in str(error) for error in errors))

    def test_cli_returns_nonzero_for_invalid_fixture(self):
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(
                schema_validation.main([str(SCORE_SCHEMA), str(VALID_SCORE)]),
                0,
            )
            self.assertEqual(
                schema_validation.main([str(SCORE_SCHEMA), str(INVALID_SCORE)]),
                1,
            )


if __name__ == "__main__":
    unittest.main()
