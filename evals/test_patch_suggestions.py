#!/usr/bin/env python3
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from evals import patch_suggestions, report


FIXTURE = Path("evals/fixtures/patch-suggestions")


class PatchSuggestionTests(unittest.TestCase):
    def test_generates_suggestion_from_failed_checker_score(self):
        artifact = patch_suggestions.generate_patch_suggestions(FIXTURE)

        self.assertEqual(len(artifact["suggestions"]), 1)
        suggestion = artifact["suggestions"][0]
        self.assertEqual(suggestion["suggestion_id"], "ps-001")
        self.assertEqual(suggestion["triggering_cases"], ["trace-ready-forbidden-behavior"])
        self.assertEqual(suggestion["failure_type"], "forbidden_behavior")
        self.assertEqual(suggestion["fix_locus"], "behavior_contract")
        self.assertEqual(suggestion["checker_ids"], ["trace_ready.code_diff_only_readiness_claim"])
        self.assertEqual(
            suggestion["observation_key"],
            "trace-ready-forbidden-behavior|forbidden_behavior|behavior_contract|trace_ready.code_diff_only_readiness_claim",
        )
        self.assertEqual(suggestion["occurrence_count"], 1)

    def test_does_not_generate_for_pass_case(self):
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = Path(tmp)
            (run_dir / "results.jsonl").write_text(
                '{"id":"pass-001","suite":"smoke.csv","verdict":"pass","failure_type":"none"}\n',
                encoding="utf-8",
            )

            artifact = patch_suggestions.generate_patch_suggestions(run_dir)

        self.assertEqual(artifact["suggestions"], [])

    def test_auto_apply_is_always_false(self):
        artifact = patch_suggestions.generate_patch_suggestions(FIXTURE)

        self.assertTrue(artifact["suggestions"])
        self.assertTrue(all(item["auto_apply"] is False for item in artifact["suggestions"]))

    def test_generated_suggestion_stays_observed(self):
        artifact = patch_suggestions.generate_patch_suggestions(FIXTURE)

        self.assertTrue(artifact["suggestions"])
        for suggestion in artifact["suggestions"]:
            self.assertEqual(suggestion["learning_status"], "observed")
            self.assertEqual(suggestion["promotion_target"], "none")
            self.assertEqual(suggestion["human_decision"], "none")
            self.assertIn("cross-run evidence delta", suggestion["evidence_delta"])
            self.assertIn("reproduction are unknown", suggestion["evidence_delta"])

    def test_generator_never_accepts_or_promotes(self):
        artifact = patch_suggestions.generate_patch_suggestions(FIXTURE)

        serialized = json.dumps(artifact, sort_keys=True)
        self.assertNotIn('"learning_status": "accepted"', serialized)
        self.assertNotIn('"learning_status": "promoted"', serialized)
        self.assertNotIn('"promotion_target": "source_patch"', serialized)
        self.assertNotIn('"human_decision": "accepted"', serialized)

    def test_unclassified_without_checker_is_skipped(self):
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = Path(tmp)
            (run_dir / "results.jsonl").write_text(
                '{"id":"unknown-001","suite":"smoke.csv","verdict":"fail","failure_type":"unknown","notes":"needs classification"}\n',
                encoding="utf-8",
            )

            artifact = patch_suggestions.generate_patch_suggestions(run_dir)

        self.assertEqual(artifact["suggestions"], [])

    def test_cli_outputs_json_to_stdout(self):
        proc = subprocess.run(
            [
                sys.executable,
                "evals/patch_suggestions.py",
                "--run-dir",
                str(FIXTURE),
            ],
            check=True,
            capture_output=True,
            text=True,
        )

        artifact = json.loads(proc.stdout)
        self.assertEqual(len(artifact["suggestions"]), 1)
        self.assertFalse(artifact["suggestions"][0]["auto_apply"])
        self.assertEqual(artifact["suggestions"][0]["learning_status"], "observed")

    def test_expected_fixture_matches_generated_artifact(self):
        expected = json.loads((FIXTURE / "expected-patch-suggestions.json").read_text(encoding="utf-8"))

        self.assertEqual(patch_suggestions.generate_patch_suggestions(FIXTURE), expected)

    def test_secret_like_notes_are_redacted(self):
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = Path(tmp)
            (run_dir / "results.jsonl").write_text(
                '{"id":"secret-001","suite":"smoke.csv","verdict":"fail",'
                '"failure_type":"forbidden_behavior","fix_locus":"behavior_contract",'
                '"notes":"Authorization: Bearer super-secret-token token=abc123"}\n',
                encoding="utf-8",
            )

            artifact = patch_suggestions.generate_patch_suggestions(run_dir)

        notes = " ".join(artifact["suggestions"][0]["notes"])
        self.assertIn("Authorization: Bearer [REDACTED]", notes)
        self.assertIn("token=[REDACTED]", notes)
        self.assertNotIn("super-secret-token", notes)
        self.assertNotIn("abc123", notes)

    def test_report_summarizes_existing_patch_suggestions(self):
        output = report.render_report(FIXTURE)

        self.assertIn("Patch suggestion count: 1", output)
        self.assertIn("`ps-001`", output)
        self.assertIn("learning_status `observed`", output)
        self.assertIn("promotion_target `none`", output)
        self.assertIn("auto_apply `False`", output)


if __name__ == "__main__":
    unittest.main()
