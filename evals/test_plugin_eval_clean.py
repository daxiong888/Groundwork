#!/usr/bin/env python3
import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import run_plugin_eval_clean  # noqa: E402
import check_plugin_eval_clean_regression  # noqa: E402


def write_runtime_log(result_root: Path, events: list[dict]) -> Path:
    log_path = (
        result_root
        / "target-plugin-eval-output"
        / "runs"
        / "run"
        / "01-scenario"
        / "codex.stdout.jsonl"
    )
    log_path.parent.mkdir(parents=True)
    log_path.write_text(
        "\n".join(json.dumps(event) for event in events) + "\n",
        encoding="utf-8",
    )
    return log_path


def write_usage(result_root: Path, input_tokens: int = 100, output_tokens: int = 25) -> dict:
    usage_path = result_root / "observed-usage.jsonl"
    usage_path.parent.mkdir(parents=True, exist_ok=True)
    usage_path.write_text(
        json.dumps({
            "id": "sample",
            "usage": {
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "total_tokens": input_tokens + output_tokens,
            },
        }) + "\n",
        encoding="utf-8",
    )
    return run_plugin_eval_clean.read_observed_usage(usage_path)


def write_benchmark_result(
    result_root: Path,
    scenario_status: str = "completed",
    input_tokens: int = 100,
    final_message: bool = True,
    failed_scenarios: int = 0,
    raw_usage: dict | None = None,
) -> Path:
    usage = raw_usage or {
        "input_tokens": input_tokens,
        "output_tokens": 25,
        "total_tokens": input_tokens + 25,
    }
    final_message_path = result_root / "target-plugin-eval-output" / "final-message.txt"
    if final_message:
        final_message_path.parent.mkdir(parents=True, exist_ok=True)
        final_message_path.write_text("## Outcome\n\nDone.\n", encoding="utf-8")
    scenario = {
        "id": "sample",
        "status": scenario_status,
        "finalMessagePath": str(final_message_path) if final_message else None,
        "finalMessagePreview": "done" if final_message else None,
        "usage": usage,
    }
    result = {
        "usageLogPath": str(result_root / "observed-usage.jsonl"),
        "resultPath": str(result_root / "benchmark-result.json"),
        "summary": {
            "completedScenarios": 1 if scenario_status == "completed" else 0,
            "failedScenarios": failed_scenarios,
        },
        "scenarios": [scenario],
    }
    result_path = result_root / "benchmark-result.json"
    result_path.write_text(json.dumps(result) + "\n", encoding="utf-8")
    return result_path


def scenario_result(
    name: str,
    input_tokens: int,
    package_files_read: list[str] | None = None,
    status: str = "completed",
    valid_for_usage_regression: bool = True,
    turns: int = 1,
    nested: int = 0,
    forbidden_scans: int = 0,
    broad_scans: int = 0,
    external_memory_reads: int = 0,
    visible_characters: int = 1200,
    visible_lines: int = 18,
    visible_sections: int = 4,
    placeholder_fields: int = 0,
    final_response_status: str = "present",
) -> dict:
    return {
        "scenario": name,
        "result_root": f"/tmp/{name}",
        "benchmark": {
            "status": status,
            "valid_for_usage_regression": valid_for_usage_regression,
            "observed_usage": {
                "status": "present",
                "input_tokens": input_tokens,
                "output_tokens": 100,
                "total_tokens": input_tokens + 100,
            },
            "final_response": {
                "status": final_response_status,
                "source": "full_message",
                "path": f"/tmp/{name}/final-message.txt",
                "character_count": visible_characters,
                "nonempty_line_count": visible_lines,
                "section_count": visible_sections,
                "placeholder_field_count": placeholder_fields,
            },
            "runtime_trace": {
                "model_turn_count": turns,
                "command_execution_count": 2,
                "nested_command_count": nested,
                "forbidden_source_scan_count": forbidden_scans,
                "broad_scan_count": broad_scans,
                "external_memory_read_count": external_memory_reads,
                "package_files_read": package_files_read or [],
            },
        },
    }


class PluginEvalCleanBenchmarkConfigTests(unittest.TestCase):
    def test_dispatch_config_is_non_recursive_blind_task(self):
        with tempfile.TemporaryDirectory() as tmp:
            result_root = Path(tmp) / "results" / "dispatch"
            config_path = run_plugin_eval_clean.write_benchmark_config(
                ROOT,
                "dispatch",
                result_root,
            )

            config = json.loads(config_path.read_text(encoding="utf-8"))
            workspace_source = Path(config["workspace"]["sourcePath"])
            user_input = config["scenarios"][0]["userInput"]

            self.assertEqual(workspace_source, result_root / "workspace-source")
            self.assertTrue((workspace_source / "ACCEPTED-TASK.md").is_file())
            self.assertIn("produce a Dispatch Package v2", user_input)
            self.assertIn("compact package skeleton", user_input)
            self.assertNotIn("plugins/groundwork/skills/", user_input)
            self.assertIn("Do not run plugin-eval", user_input)
            self.assertIn("Do not run scripts/run_plugin_eval_clean.py", user_input)
            self.assertNotIn("Run the Groundwork dispatch benchmark scenario", user_input)

            task = (workspace_source / "ACCEPTED-TASK.md").read_text(encoding="utf-8")
            self.assertIn("compact package skeleton", task)
            self.assertIn("Do not produce an adapter-ready package", task)
            self.assertIn("discover only the minimum local plugin guidance", task)
            self.assertNotIn("plugins/groundwork/skills/", task)
            self.assertNotIn("expected result package fields", task)
            self.assertNotIn("select the lightest appropriate runtime", task)

    def test_to_prd_config_does_not_reveal_expected_read_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            result_root = Path(tmp) / "results" / "to-prd"
            config_path = run_plugin_eval_clean.write_benchmark_config(
                ROOT,
                "to-prd",
                result_root,
            )

            config = json.loads(config_path.read_text(encoding="utf-8"))
            workspace_source = Path(config["workspace"]["sourcePath"])
            user_input = config["scenarios"][0]["userInput"]
            task = (workspace_source / "TASK.md").read_text(encoding="utf-8")

            self.assertTrue((workspace_source / "TASK.md").is_file())
            self.assertNotIn("plugins/groundwork/skills/", user_input)
            self.assertNotIn("plugins/groundwork/skills/", task)
            self.assertIn("discover only the minimum local plugin guidance", task)
            self.assertNotIn("Run the Groundwork to-prd benchmark scenario", user_input)

    def test_verify_config_does_not_reveal_expected_read_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            result_root = Path(tmp) / "results" / "verify"
            config_path = run_plugin_eval_clean.write_benchmark_config(
                ROOT,
                "verify",
                result_root,
            )

            config = json.loads(config_path.read_text(encoding="utf-8"))
            workspace_source = Path(config["workspace"]["sourcePath"])
            user_input = config["scenarios"][0]["userInput"]
            claim = (workspace_source / "CLAIM.md").read_text(encoding="utf-8")

            self.assertTrue((workspace_source / "CLAIM.md").is_file())
            self.assertTrue((workspace_source / "EVIDENCE.md").is_file())
            self.assertNotIn("plugins/groundwork/skills/", user_input)
            self.assertNotIn("plugins/groundwork/skills/", claim)
            self.assertIn("discover only the minimum local plugin guidance", claim)
            self.assertNotIn("Run the Groundwork verify benchmark scenario", user_input)

    def test_default_config_does_not_prompt_nested_benchmark(self):
        with tempfile.TemporaryDirectory() as tmp:
            result_root = Path(tmp) / "results" / "custom"
            config_path = run_plugin_eval_clean.write_benchmark_config(
                ROOT,
                "custom",
                result_root,
            )

            config = json.loads(config_path.read_text(encoding="utf-8"))
            user_input = config["scenarios"][0]["userInput"]
            checklist = "\n".join(config["scenarios"][0]["successChecklist"])

            self.assertIn("TASK.md", user_input)
            self.assertIn("Do not run plugin-eval", user_input)
            self.assertNotIn("benchmark scenario", user_input)
            self.assertIn("No nested Plugin Eval", checklist)

    def test_read_observed_usage_calculates_total_when_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            usage_path = Path(tmp) / "observed-usage.jsonl"
            usage_path.write_text(
                json.dumps({
                    "id": "sample",
                    "usage": {
                        "input_tokens": 100,
                        "output_tokens": 25,
                    },
                }) + "\n",
                encoding="utf-8",
            )

            usage = run_plugin_eval_clean.read_observed_usage(usage_path)

            self.assertEqual(usage["status"], "present")
            self.assertEqual(usage["sample_count"], 1)
            self.assertEqual(usage["input_tokens"], 100)
            self.assertEqual(usage["output_tokens"], 25)
            self.assertEqual(usage["total_tokens"], 125)

    def test_runtime_trace_summary_counts_clean_command_log(self):
        with tempfile.TemporaryDirectory() as tmp:
            result_root = Path(tmp) / "results" / "to-prd"
            log_path = (
                result_root
                / "target-plugin-eval-output"
                / "runs"
                / "run"
                / "01-to-prd"
                / "codex.stdout.jsonl"
            )
            log_path.parent.mkdir(parents=True)
            log_path.write_text(
                "\n".join([
                    json.dumps({"type": "turn.started"}),
                    json.dumps({
                        "type": "item.completed",
                        "item": {
                            "type": "command_execution",
                            "command": "/bin/zsh -lc \"sed -n '1,240p' plugins/groundwork/skills/to-prd/SKILL.md\"",
                        },
                    }),
                    json.dumps({
                        "type": "item.completed",
                        "item": {
                            "type": "command_execution",
                            "command": "/bin/zsh -lc \"sed -n '1,220p' TASK.md\"",
                        },
                    }),
                ]) + "\n",
                encoding="utf-8",
            )

            summary = run_plugin_eval_clean.read_runtime_trace_summary(result_root)

            self.assertEqual(summary["status"], "present")
            self.assertEqual(summary["model_turn_count"], 1)
            self.assertEqual(summary["command_execution_count"], 2)
            self.assertEqual(summary["nested_command_count"], 0)
            self.assertEqual(summary["broad_scan_count"], 0)
            self.assertEqual(
                summary["package_files_read"],
                ["plugins/groundwork/skills/to-prd/SKILL.md"],
            )
            self.assertEqual(run_plugin_eval_clean.benchmark_status(0, summary), "completed")

    def test_runtime_trace_summary_counts_eval_only_memory_and_broad_reads(self):
        with tempfile.TemporaryDirectory() as tmp:
            result_root = Path(tmp) / "results" / "dispatch"
            log_path = result_root / "target-plugin-eval-output" / "runs" / "run" / "codex.stdout.jsonl"
            log_path.parent.mkdir(parents=True)
            commands = [
                "/bin/zsh -lc \"sed -n '1,80p' /Users/example/.codex/memories/MEMORY.md\"",
                "/bin/zsh -lc \"find . -maxdepth 2 -type f\"",
                "/bin/zsh -lc \"sed -n '1,80p' plugins/groundwork/skills/dispatch/CLEAN-REVIEW-FANOUT.md\"",
            ]
            log_path.write_text(
                "\n".join(
                    json.dumps(
                        {
                            "type": "item.completed",
                            "item": {"type": "command_execution", "command": command},
                        }
                    )
                    for command in commands
                )
                + "\n",
                encoding="utf-8",
            )

            summary = run_plugin_eval_clean.read_runtime_trace_summary(result_root)

            self.assertEqual(summary["external_memory_read_count"], 1)
            self.assertEqual(summary["broad_scan_count"], 1)
            self.assertIn(
                "plugins/groundwork/skills/dispatch/CLEAN-REVIEW-FANOUT.md",
                summary["package_files_read"],
            )

    def test_package_read_detector_covers_common_read_commands(self):
        commands = [
            "python3 - <<'PY' plugins/groundwork/skills/verify/SKILL.md",
            "/usr/bin/python3 - <<'PY' plugins/groundwork/skills/verify/SKILL.md",
            "/bin/cat plugins/groundwork/skills/to-prd/SKILL.md",
            "head -40 plugins/groundwork/skills/to-prd/SKILL.md",
            "tail -20 plugins/groundwork/skills/dispatch/DISPATCH-PACKAGE.md",
            "grep -n scope plugins/groundwork/skills/verify/VERIFY-SCOPE.md",
            "rg -n scope plugins/groundwork/skills/verify/SCOPE-EVIDENCE-TEMPLATE.md",
            "perl -ne 'print' plugins/groundwork/skills/wiki/SKILL.md",
            "node -e 'console.log()' plugins/groundwork/.codex-plugin/plugin.json",
        ]

        reads = set()
        for command in commands:
            reads.update(run_plugin_eval_clean.extract_package_file_reads(command))

        self.assertEqual(
            reads,
            {
                "plugins/groundwork/skills/verify/SKILL.md",
                "plugins/groundwork/skills/to-prd/SKILL.md",
                "plugins/groundwork/skills/dispatch/DISPATCH-PACKAGE.md",
                "plugins/groundwork/skills/verify/VERIFY-SCOPE.md",
                "plugins/groundwork/skills/verify/SCOPE-EVIDENCE-TEMPLATE.md",
                "plugins/groundwork/skills/wiki/SKILL.md",
                "plugins/groundwork/.codex-plugin/plugin.json",
            },
        )

    def test_package_read_detector_ignores_non_read_commands(self):
        self.assertEqual(
            run_plugin_eval_clean.extract_package_file_reads(
                "echo plugins/groundwork/skills/to-prd/SKILL.md"
            ),
            set(),
        )

    def test_validate_benchmark_run_accepts_only_complete_usage_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            result_root = Path(tmp) / "results" / "to-prd"
            write_runtime_log(
                result_root,
                [
                    {"type": "turn.started"},
                    {"type": "item.completed", "item": {"type": "agent_message", "text": "done"}},
                    {"type": "turn.completed", "usage": {"input_tokens": 100, "output_tokens": 25}},
                ],
            )
            observed_usage = write_usage(result_root)
            write_benchmark_result(result_root)

            validation = run_plugin_eval_clean.validate_benchmark_run(
                exit_code=0,
                scenario_result_root=result_root,
                runtime_trace=run_plugin_eval_clean.read_runtime_trace_summary(result_root),
                observed_usage=observed_usage,
            )

            self.assertEqual(validation["status"], "completed")
            self.assertTrue(validation["valid_for_usage_regression"])
            self.assertEqual(validation["evidence_category"], "valid_runs")
            self.assertEqual(validation["reason"], "all validity checks passed")

    def test_final_response_metrics_reads_relocated_full_message(self):
        with tempfile.TemporaryDirectory() as tmp:
            result_root = Path(tmp) / "results" / "dispatch"
            relocated = result_root / "target-plugin-eval-output" / "runs" / "run" / "final.md"
            relocated.parent.mkdir(parents=True)
            relocated.write_text(
                "## Outcome\n\nCompact package.\n\n## Gaps\n\n- None: n/a\n",
                encoding="utf-8",
            )
            payload = {
                "scenarios": [{
                    "finalMessagePath": "/tmp/target/.plugin-eval/runs/run/final.md",
                    "finalMessagePreview": "truncated",
                }]
            }
            (result_root / "benchmark-result.json").write_text(
                json.dumps(payload) + "\n",
                encoding="utf-8",
            )

            metrics = run_plugin_eval_clean.read_final_response_metrics(result_root)

            self.assertEqual(metrics["status"], "present")
            self.assertEqual(metrics["source"], "full_message")
            self.assertEqual(metrics["section_count"], 2)
            self.assertEqual(metrics["nonempty_line_count"], 4)
            self.assertEqual(metrics["placeholder_field_count"], 1)

    def test_visible_response_metrics_ignores_yaml_container_keys(self):
        metrics = run_plugin_eval_clean.visible_response_metrics(
            "source:\n"
            "  artifact: ACCEPTED-TASK.md\n"
            "tasks:\n"
            "  - task_id: docs-update\n"
            "policy:\n"
            "  remote_writes_allowed: false\n"
        )

        self.assertEqual(metrics["placeholder_field_count"], 0)

    def test_visible_response_metrics_detects_markdown_and_chinese_placeholders(self):
        metrics = run_plugin_eval_clean.visible_response_metrics(
            "**Gaps:** None\n"
            "**Unverified Claims**: N/A\n"
            "- **缺口：** 无\n"
            "- 风险：待定\n"
        )

        self.assertEqual(metrics["placeholder_field_count"], 4)

    def test_visible_response_metrics_ignores_bold_container_keys(self):
        metrics = run_plugin_eval_clean.visible_response_metrics(
            "**source:**\n"
            "  artifact: ACCEPTED-TASK.md\n"
        )

        self.assertEqual(metrics["placeholder_field_count"], 0)

    def test_validate_benchmark_run_discards_transport_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            result_root = Path(tmp) / "results" / "verify"
            write_runtime_log(
                result_root,
                [
                    {"type": "turn.started"},
                    {
                        "type": "error",
                        "message": (
                            "Reconnecting... 5/5 (stream disconnected before completion: "
                            "failed to lookup address information)"
                        ),
                    },
                    {
                        "type": "turn.failed",
                        "error": {
                            "message": (
                                "stream disconnected before completion: error sending request "
                                "for url (https://chatgpt.com/backend-api/codex/responses)"
                            )
                        },
                    },
                ],
            )
            observed_usage = write_usage(result_root, input_tokens=0, output_tokens=0)
            write_benchmark_result(
                result_root,
                scenario_status="failed",
                input_tokens=0,
                final_message=False,
                failed_scenarios=1,
                raw_usage={
                    "input_tokens": 0,
                    "output_tokens": 0,
                    "total_tokens": 0,
                    "raw": {
                        "message": (
                            "stream disconnected before completion: error sending request "
                            "for url (https://chatgpt.com/backend-api/codex/responses)"
                        )
                    },
                },
            )

            validation = run_plugin_eval_clean.validate_benchmark_run(
                exit_code=0,
                scenario_result_root=result_root,
                runtime_trace=run_plugin_eval_clean.read_runtime_trace_summary(result_root),
                observed_usage=observed_usage,
            )

            self.assertEqual(validation["status"], "invalid-run")
            self.assertFalse(validation["valid_for_usage_regression"])
            self.assertEqual(validation["evidence_category"], "discarded_runs")
            self.assertEqual(validation["invalid_run_class"], "invalid_transport_failure")

    def test_validate_benchmark_run_separates_plugin_failure_from_transport(self):
        with tempfile.TemporaryDirectory() as tmp:
            result_root = Path(tmp) / "results" / "dispatch"
            write_runtime_log(
                result_root,
                [
                    {"type": "turn.started"},
                    {"type": "item.completed", "item": {"type": "agent_message", "text": "failed"}},
                    {"type": "turn.completed", "usage": {"input_tokens": 100, "output_tokens": 25}},
                ],
            )
            observed_usage = write_usage(result_root)
            write_benchmark_result(
                result_root,
                scenario_status="failed",
                final_message=True,
                failed_scenarios=1,
            )

            validation = run_plugin_eval_clean.validate_benchmark_run(
                exit_code=0,
                scenario_result_root=result_root,
                runtime_trace=run_plugin_eval_clean.read_runtime_trace_summary(result_root),
                observed_usage=observed_usage,
            )

            self.assertEqual(validation["status"], "failed-plugin-run")
            self.assertFalse(validation["valid_for_usage_regression"])
            self.assertEqual(validation["evidence_category"], "failed_plugin_runs")
            self.assertEqual(validation["invalid_run_class"], "plugin_scenario_failed")

    def test_validate_benchmark_run_rejects_missing_benchmark_result(self):
        with tempfile.TemporaryDirectory() as tmp:
            result_root = Path(tmp) / "results" / "to-prd"
            write_runtime_log(
                result_root,
                [
                    {"type": "turn.started"},
                    {"type": "turn.completed", "usage": {"input_tokens": 100, "output_tokens": 25}},
                ],
            )
            observed_usage = write_usage(result_root)

            validation = run_plugin_eval_clean.validate_benchmark_run(
                exit_code=0,
                scenario_result_root=result_root,
                runtime_trace=run_plugin_eval_clean.read_runtime_trace_summary(result_root),
                observed_usage=observed_usage,
            )

            self.assertEqual(validation["status"], "invalid-run")
            self.assertEqual(validation["evidence_category"], "discarded_runs")
            self.assertEqual(validation["invalid_run_class"], "invalid_missing_result")

    def test_benchmark_run_categories_groups_evidence_classes(self):
        categories = run_plugin_eval_clean.benchmark_run_categories([
            {
                "scenario": "to-prd",
                "result_root": "/tmp/to-prd",
                "benchmark": {
                    "status": "completed",
                    "valid_for_usage_regression": True,
                    "evidence_category": "valid_runs",
                    "reason": "all validity checks passed",
                    "validation": {"invalid_run_class": None},
                },
            },
            {
                "scenario": "verify",
                "result_root": "/tmp/verify",
                "benchmark": {
                    "status": "invalid-run",
                    "valid_for_usage_regression": False,
                    "evidence_category": "discarded_runs",
                    "reason": "invalid_transport_failure",
                    "validation": {"invalid_run_class": "invalid_transport_failure"},
                },
            },
            {
                "scenario": "dispatch",
                "result_root": "/tmp/dispatch",
                "benchmark": {
                    "status": "failed-plugin-run",
                    "valid_for_usage_regression": False,
                    "evidence_category": "failed_plugin_runs",
                    "reason": "scenario_status_not_completed: failed",
                    "validation": {"invalid_run_class": "plugin_scenario_failed"},
                },
            },
        ])

        self.assertEqual([item["scenario"] for item in categories["valid_runs"]], ["to-prd"])
        self.assertEqual([item["scenario"] for item in categories["discarded_runs"]], ["verify"])
        self.assertEqual([item["scenario"] for item in categories["failed_plugin_runs"]], ["dispatch"])
        self.assertFalse(categories["discarded_runs"][0]["valid_for_usage_regression"])

    def test_clean_regression_gate_accepts_threshold_baseline(self):
        scenarios = {
            "to-prd": scenario_result(
                "to-prd",
                24493,
                ["plugins/groundwork/skills/to-prd/SKILL.md"],
            ),
            "verify": scenario_result(
                "verify",
                39702,
                [
                    "plugins/groundwork/skills/verify/SKILL.md",
                    "plugins/groundwork/skills/verify/VERIFY-SCOPE.md",
                ],
            ),
            "dispatch": scenario_result(
                "dispatch",
                36333,
                [
                    "plugins/groundwork/skills/dispatch/SKILL.md",
                    "plugins/groundwork/skills/dispatch/DISPATCH-PACKAGE.md",
                ],
            ),
        }

        result = check_plugin_eval_clean_regression.validate_scenarios(scenarios)

        self.assertEqual(result["status"], "pass")
        self.assertEqual(result["total_input_tokens"], 100528)
        self.assertEqual(result["failures"], [])

    def test_clean_regression_gate_rejects_token_regression(self):
        scenarios = {
            "to-prd": scenario_result("to-prd", 35001),
            "verify": scenario_result("verify", 39702),
            "dispatch": scenario_result("dispatch", 36333),
        }

        result = check_plugin_eval_clean_regression.validate_scenarios(scenarios)

        self.assertEqual(result["status"], "fail")
        self.assertIn("to-prd: input_tokens 35001 exceeds threshold 35000", result["failures"])

    def test_clean_regression_gate_rejects_visible_output_regression(self):
        scenarios = {
            "to-prd": scenario_result("to-prd", 24493, visible_lines=46),
            "verify": scenario_result("verify", 39702, placeholder_fields=1),
            "dispatch": scenario_result("dispatch", 36333, final_response_status="preview_only"),
        }

        result = check_plugin_eval_clean_regression.validate_scenarios(scenarios)

        self.assertEqual(result["status"], "fail")
        self.assertIn("to-prd: visible nonempty lines 46 exceeds threshold 28", result["failures"])
        self.assertIn("verify: placeholder fields 1 exceeds threshold 0", result["failures"])
        self.assertIn(
            "dispatch: final_response status is preview_only, expected present full message",
            result["failures"],
        )

    def test_clean_regression_gate_scopes_dispatch_read_path_guards_to_eval(self):
        scenarios = {
            "to-prd": scenario_result("to-prd", 24493),
            "verify": scenario_result("verify", 39702),
            "dispatch": scenario_result(
                "dispatch",
                36333,
                broad_scans=1,
                external_memory_reads=1,
            ),
        }

        result = check_plugin_eval_clean_regression.validate_scenarios(scenarios)

        self.assertEqual(result["status"], "fail")
        self.assertIn("dispatch: broad_scan_count 1 != 0 for compact-default eval", result["failures"])
        self.assertIn("dispatch: external_memory_read_count 1 != 0 for compact-default eval", result["failures"])

    def test_clean_regression_gate_rejects_unexpected_read_paths(self):
        scenarios = {
            "to-prd": scenario_result(
                "to-prd",
                24493,
                ["plugins/groundwork/README.md"],
            ),
            "verify": scenario_result("verify", 39702),
            "dispatch": scenario_result(
                "dispatch",
                36333,
                ["plugins/groundwork/skills/dispatch/DISPATCH-PACKAGE-DETAILS.md"],
            ),
        }

        result = check_plugin_eval_clean_regression.validate_scenarios(scenarios)

        self.assertEqual(result["status"], "fail")
        self.assertIn("to-prd: unexpected package reads: plugins/groundwork/README.md", result["failures"])
        self.assertIn(
            "dispatch: unexpected package reads: plugins/groundwork/skills/dispatch/DISPATCH-PACKAGE-DETAILS.md",
            result["failures"],
        )

    def test_clean_regression_gate_rejects_verify_extra_read_paths(self):
        scenarios = {
            "to-prd": scenario_result(
                "to-prd",
                24493,
                ["plugins/groundwork/skills/to-prd/SKILL.md"],
            ),
            "verify": scenario_result(
                "verify",
                39702,
                [
                    "plugins/groundwork/skills/verify/SKILL.md",
                    "plugins/groundwork/skills/verify/VERIFY-SCOPE.md",
                    "plugins/groundwork/skills/verify/RUNTIME-CAPABILITY-BRANCH.md",
                ],
            ),
            "dispatch": scenario_result(
                "dispatch",
                36333,
                [
                    "plugins/groundwork/skills/dispatch/SKILL.md",
                    "plugins/groundwork/skills/dispatch/DISPATCH-PACKAGE.md",
                ],
            ),
        }

        result = check_plugin_eval_clean_regression.validate_scenarios(scenarios)

        self.assertEqual(result["status"], "fail")
        self.assertIn(
            "verify: unexpected package reads: plugins/groundwork/skills/verify/RUNTIME-CAPABILITY-BRANCH.md",
            result["failures"],
        )

    def test_clean_regression_gate_collects_multiple_manifests(self):
        manifests = [
            {"_manifest_path": "/tmp/to-prd/results/run-manifest.json", "scenarios": [scenario_result("to-prd", 24493)]},
            {"_manifest_path": "/tmp/verify/results/run-manifest.json", "scenarios": [scenario_result("verify", 39702)]},
            {"_manifest_path": "/tmp/dispatch/results/run-manifest.json", "scenarios": [scenario_result("dispatch", 36333)]},
        ]

        scenarios = check_plugin_eval_clean_regression.collect_scenarios(manifests)
        result = check_plugin_eval_clean_regression.validate_scenarios(scenarios)

        self.assertEqual(sorted(scenarios), ["dispatch", "to-prd", "verify"])
        self.assertEqual(result["status"], "pass")

    def test_runtime_trace_summary_fails_nested_benchmark_command(self):
        with tempfile.TemporaryDirectory() as tmp:
            result_root = Path(tmp) / "results" / "dispatch"
            log_path = (
                result_root
                / "target-plugin-eval-output"
                / "runs"
                / "run"
                / "01-dispatch"
                / "codex.stdout.jsonl"
            )
            log_path.parent.mkdir(parents=True)
            log_path.write_text(
                "\n".join([
                    json.dumps({"type": "turn.started"}),
                    json.dumps({
                        "type": "item.completed",
                        "item": {
                            "type": "command_execution",
                            "command": "/bin/zsh -lc 'plugin-eval benchmark . --config .plugin-eval/benchmark.json'",
                        },
                    }),
                ]) + "\n",
                encoding="utf-8",
            )

            summary = run_plugin_eval_clean.read_runtime_trace_summary(result_root)

            self.assertEqual(summary["model_turn_count"], 1)
            self.assertEqual(summary["command_execution_count"], 1)
            self.assertEqual(summary["nested_command_count"], 1)
            self.assertEqual(run_plugin_eval_clean.benchmark_status(0, summary), "invalid-run")

    def test_benchmark_status_fails_when_runtime_trace_missing(self):
        summary = run_plugin_eval_clean.read_runtime_trace_summary(Path("/tmp/no-such-result-root"))

        self.assertEqual(summary["status"], "not_found")
        self.assertEqual(run_plugin_eval_clean.benchmark_status(0, summary), "invalid-run")

    def test_runtime_trace_summary_fails_source_repo_scan(self):
        with tempfile.TemporaryDirectory() as tmp:
            result_root = Path(tmp) / "results" / "verify"
            log_path = (
                result_root
                / "target-plugin-eval-output"
                / "runs"
                / "run"
                / "01-verify"
                / "codex.stdout.jsonl"
            )
            log_path.parent.mkdir(parents=True)
            log_path.write_text(
                "\n".join([
                    json.dumps({"type": "turn.started"}),
                    json.dumps({
                        "type": "item.completed",
                        "item": {
                            "type": "command_execution",
                            "command": "/bin/zsh -lc 'rg -n \"verify\" docs evals scripts'",
                        },
                    }),
                ]) + "\n",
                encoding="utf-8",
            )

            summary = run_plugin_eval_clean.read_runtime_trace_summary(result_root)

            self.assertEqual(summary["nested_command_count"], 0)
            self.assertEqual(summary["forbidden_source_scan_count"], 1)
            self.assertEqual(run_plugin_eval_clean.benchmark_status(0, summary), "invalid-run")

    def test_command_classifiers_distinguish_patterns_from_paths(self):
        self.assertFalse(
            run_plugin_eval_clean.is_nested_benchmark_command(
                "/bin/zsh -lc 'rg -n benchmark ACCEPTED-TASK.md'"
            )
        )
        self.assertFalse(
            run_plugin_eval_clean.is_nested_benchmark_command(
                "/bin/zsh -lc 'rg -n plugin-eval TASK.md'"
            )
        )
        self.assertFalse(
            run_plugin_eval_clean.is_nested_benchmark_command(
                "/bin/zsh -lc 'rg -n run_plugin_eval_clean.py TASK.md'"
            )
        )
        self.assertFalse(
            run_plugin_eval_clean.is_nested_benchmark_command(
                "/bin/zsh -lc 'rg -n scripts/run_plugin_eval_clean.py TASK.md'"
            )
        )
        self.assertFalse(
            run_plugin_eval_clean.is_nested_benchmark_command(
                "/bin/zsh -lc 'grep -n scripts/run_plugin_eval_clean.py TASK.md'"
            )
        )
        self.assertTrue(
            run_plugin_eval_clean.is_nested_benchmark_command(
                "/bin/zsh -lc 'python3 scripts/run_plugin_eval_clean.py --help'"
            )
        )
        self.assertTrue(
            run_plugin_eval_clean.is_nested_benchmark_command(
                "/bin/zsh -lc 'scripts/run_plugin_eval_clean.py --help'"
            )
        )
        self.assertTrue(
            run_plugin_eval_clean.is_nested_benchmark_command(
                "/bin/zsh -lc './scripts/run_plugin_eval_clean.py --help'"
            )
        )
        self.assertTrue(
            run_plugin_eval_clean.is_nested_benchmark_command(
                f"/bin/zsh -lc '{ROOT / 'scripts' / 'run_plugin_eval_clean.py'} --help'"
            )
        )
        self.assertTrue(
            run_plugin_eval_clean.is_nested_benchmark_command(
                "/bin/zsh -lc 'command -v plugin-eval'"
            )
        )
        self.assertTrue(
            run_plugin_eval_clean.is_nested_benchmark_command(
                "/bin/zsh -lc 'node /tmp/plugin-eval/scripts/plugin-eval.js benchmark .'"
            )
        )
        self.assertTrue(
            run_plugin_eval_clean.is_nested_benchmark_command(
                "/bin/zsh -lc 'python3 scripts/sample_benchmark.py'"
            )
        )
        self.assertFalse(
            run_plugin_eval_clean.is_forbidden_source_scan_command(
                "/bin/zsh -lc 'rg -n \"scripts\" TASK.md'"
            )
        )
        self.assertFalse(
            run_plugin_eval_clean.is_forbidden_source_scan_command(
                "/bin/zsh -lc 'rg --files -g \"CLAIM.md\" -g \"EVIDENCE.md\" .'"
            )
        )
        self.assertTrue(
            run_plugin_eval_clean.is_forbidden_source_scan_command(
                "/bin/zsh -lc 'rg -n \"verify\" docs evals scripts'"
            )
        )
        self.assertTrue(
            run_plugin_eval_clean.is_forbidden_source_scan_command(
                "/bin/zsh -lc 'ls -la docs'"
            )
        )
        self.assertTrue(
            run_plugin_eval_clean.is_forbidden_source_scan_command(
                f"/bin/zsh -lc 'rg -n verify {ROOT / 'docs'}'"
            )
        )


if __name__ == "__main__":
    unittest.main()
