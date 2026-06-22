#!/usr/bin/env python3
import tempfile
import unittest
from pathlib import Path

from evals import report


FIXTURE = Path("evals/fixtures/report")


class ReportTests(unittest.TestCase):
    def render_fixture(self):
        return report.render_report(FIXTURE)

    def test_report_renders_summary_counts(self):
        output = self.render_fixture()

        self.assertIn("## Summary Counts", output)
        self.assertIn("- fail: 1", output)
        self.assertIn("- pass: 1", output)

    def test_report_lists_nonpass_cases(self):
        output = self.render_fixture()

        self.assertIn("## Non-pass Cases", output)
        self.assertIn("`trace-ready-forbidden-behavior`", output)
        self.assertIn("forbidden_behavior", output)

    def test_report_mentions_score_artifacts(self):
        output = self.render_fixture()

        self.assertIn("## Score Artifacts", output)
        self.assertIn("Score artifact count: 1", output)
        self.assertIn("score/trace-ready-forbidden-behavior.score.json", output)

    def test_report_mentions_trace_diagnostics(self):
        output = self.render_fixture()

        self.assertIn("## Trace Diagnostics", output)
        self.assertIn("command-related events: 6", output)
        self.assertIn("Trace command thrashing: True", output)

    def test_report_tolerates_missing_score_dir(self):
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = Path(tmp)
            (run_dir / "summary.json").write_text('{"counts":{"pass":1},"suites":["smoke.csv"]}\n', encoding="utf-8")
            (run_dir / "results.jsonl").write_text('{"id":"pass-001","suite":"smoke.csv","verdict":"pass"}\n', encoding="utf-8")

            output = report.render_report(run_dir)

        self.assertIn("Score artifacts missing or empty.", output)
        self.assertIn("score artifacts missing: score/ directory not found", output)

    def test_report_tolerates_invalid_results_jsonl(self):
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = Path(tmp)
            (run_dir / "summary.json").write_text('{"counts":{"pass":1},"suites":["smoke.csv"]}\n', encoding="utf-8")
            (run_dir / "results.jsonl").write_text('{"id":"pass-001","suite":"smoke.csv","verdict":"pass"}\nnot-json\n', encoding="utf-8")

            output = report.render_report(run_dir)

        self.assertIn("invalid JSON", output)
        self.assertIn("- pass: 1", output)

    def test_report_contains_evidence_boundary(self):
        output = self.render_fixture()

        self.assertIn(report.EVIDENCE_BOUNDARY, output)
        self.assertIn("not runtime, cache-refresh, release, UAT, or customer-readiness evidence", output)

    def test_report_summarizes_existing_patch_suggestions(self):
        output = report.render_report(Path("evals/fixtures/patch-suggestions"))

        self.assertIn("Patch suggestion count: 1", output)
        self.assertIn("`ps-001`", output)
        self.assertIn("auto_apply `False`", output)


if __name__ == "__main__":
    unittest.main()
