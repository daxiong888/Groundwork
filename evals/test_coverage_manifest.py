#!/usr/bin/env python3
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from evals import check_coverage_manifest, routing_schema


class CoverageManifestTests(unittest.TestCase):
    def test_manifest_references_existing_rows_and_public_skills(self):
        errors = check_coverage_manifest.validate_manifest(
            check_coverage_manifest.DEFAULT_MANIFEST,
        )
        self.assertEqual(errors, [])

    def test_repository_manifest_route_negatives_pass_explicit_ownership_gate(self):
        manifest = check_coverage_manifest.parse_manifest(
            check_coverage_manifest.DEFAULT_MANIFEST,
        )
        rows = check_coverage_manifest.load_rows()
        errors = []

        for skill, contract in manifest.items():
            for reference in contract["route_negatives"]:
                path, row_id, _marker = check_coverage_manifest.split_reference(reference)
                check_coverage_manifest.validate_route_negative(
                    skill,
                    reference,
                    rows[(path, row_id)],
                    errors,
                )

        self.assertEqual(errors, [])

    def test_manifest_parser_rejects_non_array_contract_values(self):
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "coverage.toml"
            path.write_text('[public_skills.dispatch]\npositives = "not-an-array"\n', encoding="utf-8")

            with self.assertRaises(check_coverage_manifest.ManifestError):
                check_coverage_manifest.parse_manifest(path)

    def test_coverage_route_resolution_matches_shared_legacy_precedence(self):
        row = {
            "expected_best": "",
            "expected_skill": "",
            "should_trigger": "false",
            "expected_behavior": "Should route to to-prd",
            "skill": "verify",
        }

        self.assertEqual(routing_schema.expected_skill_for_row(row), "to-prd")
        self.assertEqual(check_coverage_manifest.expected_route(row), "to-prd")

    def test_coverage_route_negative_uses_shared_strict_list_parser(self):
        row = {
            "id": "coverage-route-negative",
            "_suite": "coverage.csv",
            "_row_number": "2",
            "expected_best": "direct",
            "acceptable_routes": "direct,verify",
        }
        errors = []

        check_coverage_manifest.validate_route_negative(
            "verify",
            "evals/prompts/coverage.csv::coverage-route-negative",
            row,
            errors,
        )

        self.assertIn("must use '|' separators", "\n".join(errors))

    def test_coverage_route_negative_rejects_legacy_negative_owned_by_another_skill(self):
        row = {
            "id": "cross-skill-negative",
            "skill": "wiki",
            "should_trigger": "false",
            "expected_behavior": "Should route to direct",
        }
        errors = []

        check_coverage_manifest.validate_route_negative(
            "dispatch",
            "evals/prompts/coverage.csv::cross-skill-negative",
            row,
            errors,
        )

        self.assertEqual(
            errors,
            [
                "dispatch: route_negative "
                "evals/prompts/coverage.csv::cross-skill-negative "
                "is owned by 'wiki', not 'dispatch'"
            ],
        )

    def test_coverage_route_negative_keeps_unstructured_legacy_ownership_only(self):
        row = {
            "id": "legacy-negative",
            "skill": "dispatch",
            "should_trigger": "false",
            "expected_behavior": "Should route to direct",
        }
        errors = []

        check_coverage_manifest.validate_route_negative(
            "dispatch",
            "evals/prompts/coverage.csv::legacy-negative",
            row,
            errors,
        )

        self.assertEqual(errors, [])

    def test_coverage_route_negative_rejects_structured_should_trigger_false_self_route(self):
        row = {
            "id": "structured-negative",
            "_suite": "routing-reliability.csv",
            "_row_number": "2",
            "skill": "dispatch",
            "should_trigger": "false",
            "expected_best": "dispatch",
            "acceptable_routes": "dispatch",
            "forbidden_routes": "to-prd",
        }
        errors = []

        check_coverage_manifest.validate_route_negative(
            "dispatch",
            "evals/prompts/routing-reliability.csv::structured-negative",
            row,
            errors,
        )

        self.assertEqual(
            errors,
            [
                "dispatch: route_negative "
                "evals/prompts/routing-reliability.csv::structured-negative "
                "still expects 'dispatch'; structured negatives must route elsewhere",
                "dispatch: route_negative "
                "evals/prompts/routing-reliability.csv::structured-negative allows 'dispatch'",
                "dispatch: route_negative "
                "evals/prompts/routing-reliability.csv::structured-negative "
                "does not explicitly forbid 'dispatch'",
            ],
        )

    def test_coverage_route_negative_rejects_structured_row_that_does_not_forbid_skill(self):
        row = {
            "id": "rr-001",
            "_suite": "routing-reliability.csv",
            "_row_number": "2",
            "expected_best": "direct",
            "acceptable_routes": "direct",
            "forbidden_routes": "to-prd|to-issues|write-plan|implement",
        }
        errors = []

        check_coverage_manifest.validate_route_negative(
            "dispatch",
            "evals/prompts/routing-reliability.csv::rr-001",
            row,
            errors,
        )

        self.assertEqual(
            errors,
            [
                "dispatch: route_negative "
                "evals/prompts/routing-reliability.csv::rr-001 "
                "does not explicitly forbid 'dispatch'"
            ],
        )


if __name__ == "__main__":
    unittest.main()
