#!/usr/bin/env python3
import contextlib
import io
import json
import unittest
from pathlib import Path

from evals import schema_validation
from evals import routing_schema


ROOT = Path(__file__).resolve().parents[1]
SCORE_SCHEMA = ROOT / "schemas" / "groundwork-eval-score.schema.json"
VALID_SCORE = ROOT / "evals" / "fixtures" / "score" / "valid-eval-score.json"
INVALID_SCORE = ROOT / "evals" / "fixtures" / "score" / "invalid-eval-score.json"
ROUTER_SCORE_SCHEMA = ROOT / "schemas" / "groundwork-router-score.schema.json"
VALID_ROUTER_SCORE = ROOT / "evals" / "fixtures" / "score" / "valid-router-score.json"
INVALID_ROUTER_SCORE = ROOT / "evals" / "fixtures" / "score" / "invalid-router-score.json"


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

    def test_valid_router_score_fixture_passes(self):
        self.assertEqual(
            schema_validation.validate_json_file(ROUTER_SCORE_SCHEMA, VALID_ROUTER_SCORE),
            [],
        )

    def test_invalid_router_score_fixture_reports_schema_error(self):
        errors = schema_validation.validate_json_file(ROUTER_SCORE_SCHEMA, INVALID_ROUTER_SCORE)

        self.assertTrue(errors)
        self.assertTrue(any("$.score_eligibility" in str(error) for error in errors))

    def test_router_score_schema_enums_match_python_vocabulary(self):
        schema = json.loads(ROUTER_SCORE_SCHEMA.read_text(encoding="utf-8"))
        properties = schema["properties"]

        self.assertEqual(
            set(properties["score_eligibility"]["enum"]),
            routing_schema.SCORE_ELIGIBILITY,
        )
        self.assertEqual(
            set(properties["execution_profile_verdict"]["enum"]),
            routing_schema.EXECUTION_PROFILE_VERDICTS,
        )
        self.assertEqual(
            set(properties["selector_enforcement"]["enum"]),
            routing_schema.SELECTOR_ENFORCEMENT,
        )

    def test_common_workflow_route_schema_matches_python_routes(self):
        schema = json.loads((ROOT / "schemas" / "groundwork-common.schema.json").read_text(encoding="utf-8"))
        workflow_routes = set(schema["$defs"]["workflow_route"]["enum"])
        expected_routes = routing_schema.WORKFLOW_ROUTES

        self.assertEqual(workflow_routes, expected_routes)


if __name__ == "__main__":
    unittest.main()
