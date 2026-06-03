#!/usr/bin/env python3
import json
import tempfile
import unittest
from pathlib import Path

import run_runtime
import run_runtime_parallel


def row(**kwargs):
    data = {
        "id": "case",
        "_suite": "suite.csv",
        "expected_skill": "direct",
        "fixture": "none",
        "prompt": "只报告结果 不要编辑文件",
        "artifact_allowed": "false",
        "risky_write_requested": "false",
        "skill_load_required": "true",
    }
    data.update(kwargs)
    return data


class RuntimeSchedulerTests(unittest.TestCase):
    def test_absent_metadata_allows_isolated_read_only_parallel(self):
        metadata = run_runtime.case_metadata(row(id="read-only"))

        self.assertTrue(metadata["parallel_safe"])
        self.assertEqual(metadata["group"], "isolated")
        self.assertEqual(metadata["flake_policy"], "none")
        self.assertIsInstance(metadata["timeout_s"], int)

    def test_browser_and_shared_cases_are_serial_groups(self):
        browser = row(id="browser", prompt="Use Browser to inspect this UI. 不要编辑文件")
        repo_root = row(id="gr-008b", prompt="repo-root git boundary review")

        self.assertFalse(run_runtime.case_metadata(browser)["parallel_safe"])
        self.assertEqual(run_runtime.case_metadata(browser)["group"], "browser")
        self.assertIn("browser", run_runtime.case_metadata(browser)["resource_keys"])

        self.assertFalse(run_runtime.case_metadata(repo_root)["parallel_safe"])
        self.assertEqual(run_runtime.case_metadata(repo_root)["group"], "shared")
        self.assertIn("repo:groundwork", run_runtime.case_metadata(repo_root)["resource_keys"])

    def test_partition_keeps_unsafe_rows_out_of_parallel_pool(self):
        safe = row(id="safe")
        unsafe = row(id="unsafe", resource_keys="browser")

        parallel_rows, serial_rows = run_runtime.partition_rows([safe, unsafe], jobs=4)

        self.assertEqual([item["id"] for item in parallel_rows], ["safe"])
        self.assertEqual([item["id"] for item in serial_rows], ["unsafe"])

    def test_group_filter_matches_inferred_group_and_resource_key(self):
        browser = row(id="browser", resource_keys="browser")
        isolated = row(id="isolated")

        self.assertTrue(run_runtime.row_matches_group(browser, "browser"))
        self.assertFalse(run_runtime.row_matches_group(isolated, "browser"))
        self.assertTrue(run_runtime.row_matches_group(isolated, "isolated"))

    def test_load_failure_ids_from_summary_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            summary = Path(tmp) / "summary.json"
            summary.write_text(
                json.dumps(
                    {
                        "failures": [
                            {"id": "fail-001", "verdict": "fail"},
                            {"id": "timeout-001", "verdict": "timeout"},
                        ]
                    }
                ),
                encoding="utf-8",
            )

            self.assertEqual(
                run_runtime.load_failure_ids(Path(tmp)),
                ["fail-001", "timeout-001"],
            )

    def test_write_summary_creates_result_layout(self):
        with tempfile.TemporaryDirectory() as tmp:
            old_results = run_runtime.RESULTS
            old_summary = run_runtime.SUMMARY
            old_failures = run_runtime.FAILURES
            old_cases = run_runtime.CASES
            try:
                root = Path(tmp)
                run_runtime.RESULTS = root / "results.jsonl"
                run_runtime.SUMMARY = root / "summary.json"
                run_runtime.FAILURES = root / "failures.md"
                run_runtime.CASES = root / "cases"
                run_runtime.CASES.mkdir()

                summary = run_runtime.write_summary(
                    [
                        {"id": "pass-001", "suite": "suite.csv", "verdict": "pass", "_input_index": 1},
                        {"id": "fail-001", "suite": "suite.csv", "verdict": "fail", "notes": "wrong skill", "_input_index": 0},
                    ],
                    jobs=4,
                    suites=["suite.csv"],
                    resource_policy="auto",
                )

                self.assertEqual(summary["counts"], {"fail": 1, "pass": 1})
                self.assertEqual([item["id"] for item in summary["failures"]], ["fail-001"])
                self.assertTrue(run_runtime.RESULTS.exists())
                self.assertTrue(run_runtime.SUMMARY.exists())
                self.assertTrue(run_runtime.FAILURES.exists())
                self.assertIn("fail-001", run_runtime.FAILURES.read_text(encoding="utf-8"))
            finally:
                run_runtime.RESULTS = old_results
                run_runtime.SUMMARY = old_summary
                run_runtime.FAILURES = old_failures
                run_runtime.CASES = old_cases

    def test_parallel_wrapper_preserves_legacy_default_timeout(self):
        self.assertEqual(
            run_runtime_parallel.with_parallel_compat_defaults(["--jobs", "4"]),
            ["--case-timeout", "390", "--jobs", "4"],
        )

    def test_parallel_wrapper_preserves_explicit_timeout(self):
        self.assertEqual(
            run_runtime_parallel.with_parallel_compat_defaults(["--case-timeout", "500", "--jobs", "4"]),
            ["--case-timeout", "500", "--jobs", "4"],
        )
        self.assertEqual(
            run_runtime_parallel.with_parallel_compat_defaults(["--case-timeout=500", "--jobs", "4"]),
            ["--case-timeout=500", "--jobs", "4"],
        )


if __name__ == "__main__":
    unittest.main()
