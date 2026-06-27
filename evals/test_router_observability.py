#!/usr/bin/env python3
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from evals.router_observability import backfill_row
from evals import report
from evals.routing_summary import summarize_routing_results
from evals.verdict_model import normalize_execution_profile, render_router_card, score_turn


ROOT = Path(__file__).resolve().parents[1]
HOOKS = ROOT / "scripts" / "codex-hooks"


def run_hook(script, event, cwd):
    return subprocess.run(
        [sys.executable, str(HOOKS / script)],
        input=json.dumps(event),
        text=True,
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )


class RouterObservabilityTests(unittest.TestCase):
    def test_hooks_manifest_uses_official_command_handler_shape(self):
        manifest = json.loads((ROOT / "hooks" / "hooks.json").read_text(encoding="utf-8"))

        self.assertIsInstance(manifest.get("hooks"), dict)
        for event_name, matcher_groups in manifest["hooks"].items():
            self.assertIsInstance(event_name, str)
            self.assertIsInstance(matcher_groups, list)
            self.assertTrue(matcher_groups)
            for group in matcher_groups:
                self.assertIn("hooks", group)
                self.assertNotIn("command", group)
                self.assertIsInstance(group["hooks"], list)
                self.assertTrue(group["hooks"])
                for handler in group["hooks"]:
                    self.assertEqual(handler.get("type"), "command")
                    self.assertIsInstance(handler.get("command"), str)
                    self.assertTrue(handler["command"])

    def write_config(self, root, **overrides):
        config = {
            "enabled": True,
            "mode": "observe_only",
            "raw_capture": False,
            "snippet_capture": False,
        }
        config.update(overrides)
        path = root / ".groundwork" / "harness" / "router-observability" / "config.json"
        path.parent.mkdir(parents=True)
        path.write_text(json.dumps(config), encoding="utf-8")
        return path

    def turn_dir(self, root):
        return root / ".groundwork" / "harness" / "router-observability" / "s1" / "t1"

    def test_user_prompt_hook_noops_without_project_opt_in(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            result = run_hook(
                "user_prompt_submit_groundwork_entry.py",
                {"cwd": str(root), "session_id": "s1", "turn_id": "t1", "prompt": "按 PRD 实施"},
                root,
            )

            self.assertEqual(result.stdout, "")
            self.assertFalse((root / ".groundwork").exists())

    def test_observe_only_hook_writes_decision_without_additional_context(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_config(root)

            result = run_hook(
                "user_prompt_submit_groundwork_entry.py",
                {
                    "cwd": str(root),
                    "session_id": "s1",
                    "turn_id": "t1",
                    "prompt": "按 PRD 实施 docs/foo.md token=secret-123",
                },
                root,
            )

            self.assertEqual(result.stdout, "")
            decision = json.loads((self.turn_dir(root) / "router-decision.json").read_text(encoding="utf-8"))
            prompt_metadata = json.loads((self.turn_dir(root) / "prompt-metadata.json").read_text(encoding="utf-8"))
            self.assertEqual(decision["decision_mode"], "observe_only")
            self.assertEqual(decision["decision_source"], "heuristic")
            self.assertFalse(decision["router_hint_emitted"])
            self.assertEqual(decision["entry_decision"]["expected_best"], "implement")
            self.assertEqual(prompt_metadata["raw_prompt_storage"], "disabled")
            self.assertEqual(prompt_metadata["snippet_capture"], "disabled")
            self.assertEqual(prompt_metadata["prompt_snippet"], "")
            self.assertNotIn("secret-123", json.dumps(prompt_metadata))
            self.assertNotIn("secret-123", json.dumps(decision))
            self.assertFalse((self.turn_dir(root) / "prompt.raw.json").exists())

    def test_guided_hint_mode_emits_context_and_excludes_baseline(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_config(root, mode="guided_hint_trial")

            result = run_hook(
                "user_prompt_submit_groundwork_entry.py",
                {"cwd": str(root), "session_id": "s1", "turn_id": "t1", "prompt": "先写实现计划，不要编辑文件"},
                root,
            )

            output = json.loads(result.stdout)
            self.assertEqual(output["hookSpecificOutput"]["hookEventName"], "UserPromptSubmit")
            self.assertIn("additionalContext", output["hookSpecificOutput"])
            decision = json.loads((self.turn_dir(root) / "router-decision.json").read_text(encoding="utf-8"))
            self.assertEqual(decision["entry_decision"]["expected_best"], "write-plan")
            score = score_turn(decision, "Implementation Mini-Plan", [])
            self.assertEqual(score["score_eligibility"], "guided_hint_excluded")

    def test_tool_and_stop_hooks_write_score_and_card(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_config(root)
            base_event = {"cwd": str(root), "session_id": "s1", "turn_id": "t1"}
            run_hook(
                "user_prompt_submit_groundwork_entry.py",
                {**base_event, "prompt": "按 PRD 实施 docs/foo.md"},
                root,
            )
            run_hook(
                "post_tool_use_groundwork_trace.py",
                {**base_event, "tool_name": "Bash", "tool_input": {"command": "git status --short"}, "status": "pass"},
                root,
            )
            result = run_hook(
                "stop_groundwork_score.py",
                {**base_event, "last_assistant_message": "Implementation Summary\nFiles Changed\nChecks Run token=secret-456"},
                root,
            )

            self.assertEqual(result.stdout, "")
            score = json.loads((self.turn_dir(root) / "router-score.json").read_text(encoding="utf-8"))
            final_metadata = json.loads((self.turn_dir(root) / "final-metadata.json").read_text(encoding="utf-8"))
            card = (self.turn_dir(root) / "router-card.md").read_text(encoding="utf-8")
            self.assertEqual(score["expected_route"], "implement")
            self.assertEqual(score["actual_route"], "implement")
            self.assertEqual(final_metadata["snippet_capture"], "disabled")
            self.assertEqual(final_metadata["final_snippet"], "")
            self.assertNotIn("secret-456", json.dumps(final_metadata))
            self.assertEqual(score["score_eligibility"], "insufficient_evidence")
            self.assertIn("expected_route_source", score["notes"])
            self.assertTrue(score["checker_results"])
            self.assertIn("Groundwork Router Decision", card)

    def test_tool_permission_and_stop_hooks_noop_without_opt_in(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            base_event = {"cwd": str(root), "session_id": "s1", "turn_id": "t1"}

            for script, event in [
                ("post_tool_use_groundwork_trace.py", {**base_event, "tool_name": "Bash"}),
                ("permission_request_groundwork_trace.py", {**base_event, "permission": "Bash"}),
                ("stop_groundwork_score.py", {**base_event, "final_response": "Implementation Summary"}),
            ]:
                result = run_hook(script, event, root)
                self.assertEqual(result.stdout, "")

            self.assertFalse((root / ".groundwork").exists())

    def test_permission_events_include_coverage_and_feed_stop_score(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_config(root)
            base_event = {"cwd": str(root), "session_id": "s1", "turn_id": "t1"}
            run_hook(
                "user_prompt_submit_groundwork_entry.py",
                {**base_event, "prompt": "按 PRD 实施 docs/foo.md"},
                root,
            )
            run_hook(
                "permission_request_groundwork_trace.py",
                {**base_event, "permission": "Bash", "tool_input": {"command": "git add docs/foo.md"}},
                root,
            )
            run_hook(
                "stop_groundwork_score.py",
                {**base_event, "final_response": "Implementation Summary\nFiles Changed\nChecks Run"},
                root,
            )

            permission_event = json.loads((self.turn_dir(root) / "permission-events.jsonl").read_text(encoding="utf-8"))
            score = json.loads((self.turn_dir(root) / "router-score.json").read_text(encoding="utf-8"))
            self.assertEqual(permission_event["coverage_status"], "observed_supported")
            self.assertIn("git_write", permission_event["risk_markers"])
            self.assertEqual(score["tool_coverage_status"], "supported_events_observed")

    def test_partial_coverage_is_not_baseline_eligible(self):
        decision = {
            "session_id": "s1",
            "turn_id": "t1",
            "decision_mode": "observe_only",
            "decision_source": "fixture",
            "router_hint_emitted": False,
            "entry_decision": {
                "expected_best": "implement",
                "acceptable_routes": ["implement"],
                "forbidden_routes": ["verify"],
                "route_boundary": "entry-contract",
            },
        }

        score = score_turn(
            decision,
            "Implementation Summary\nFiles Changed\nChecks Run",
            [{"coverage_status": "observed_supported"}, {"coverage_status": "unsupported"}],
        )

        self.assertEqual(score["tool_coverage_status"], "partial")
        self.assertEqual(score["score_eligibility"], "insufficient_evidence")
        self.assertIn("tool_coverage_status", score["notes"])

    def test_fixture_source_with_supported_events_can_be_baseline_eligible(self):
        decision = {
            "session_id": "s1",
            "turn_id": "t1",
            "decision_mode": "observe_only",
            "decision_source": "fixture",
            "router_hint_emitted": False,
            "entry_decision": {
                "expected_best": "implement",
                "acceptable_routes": ["implement"],
                "forbidden_routes": ["verify"],
                "route_boundary": "entry-contract",
            },
        }

        score = score_turn(
            decision,
            "Implementation Summary\nFiles Changed\nChecks Run",
            [{"coverage_status": "observed_supported"}],
        )

        self.assertEqual(score["score_eligibility"], "baseline_eligible")
        self.assertTrue(score["checker_results"])

    def test_deterministic_classifier_requires_evidence_before_baseline(self):
        decision = {
            "session_id": "s1",
            "turn_id": "t1",
            "decision_mode": "observe_only",
            "decision_source": "deterministic_entry_classifier",
            "router_hint_emitted": False,
            "entry_decision": {
                "expected_best": "implement",
                "acceptable_routes": ["implement"],
                "forbidden_routes": ["verify"],
                "route_boundary": "entry-contract",
            },
        }

        score = score_turn(
            decision,
            "Implementation Summary\nFiles Changed\nChecks Run",
            [{"coverage_status": "observed_supported"}],
        )

        self.assertEqual(score["score_eligibility"], "insufficient_evidence")
        self.assertIn("classifier_evidence", score["notes"])

    def test_dispatch_prompt_writes_dispatch_decision(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_config(root)

            run_hook(
                "user_prompt_submit_groundwork_entry.py",
                {"cwd": str(root), "session_id": "s1", "turn_id": "t1", "prompt": "dispatch this clean review"},
                root,
            )

            dispatch_decision = json.loads((self.turn_dir(root) / "dispatch-decision.json").read_text(encoding="utf-8"))
            profile = dispatch_decision["execution_profile"]
            self.assertEqual(dispatch_decision["decision_source"], "heuristic_dispatch_candidate")
            self.assertFalse(dispatch_decision["actual_dispatch_output_observed"])
            self.assertEqual(dispatch_decision["score_eligibility"], "insufficient_evidence")
            self.assertEqual(dispatch_decision["execution_claim"], "not_executed_by_dispatch")
            card = render_router_card({"session_id": "s1", "turn_id": "t1"}, {}, dispatch_decision)
            self.assertIn("## Dispatch Candidate", card)
            self.assertIn("Actual dispatch output observed: `False`", card)
            self.assertEqual(profile["model_profile"], "exhaustive_review")
            self.assertEqual(profile["reasoning_effort"], "high")
            self.assertEqual(profile["cost_latency_bias"], "quality")
            self.assertEqual(profile["selector_enforcement"], "prompt_preference")
            self.assertEqual(profile["evidence_layer"], "prompt_preference")

    def test_tool_enforced_selector_requires_runtime_evidence(self):
        decision = {
            "session_id": "s1",
            "turn_id": "t1",
            "decision_mode": "observe_only",
            "decision_source": "fixture",
            "router_hint_emitted": False,
            "entry_decision": {
                "expected_best": "dispatch",
                "acceptable_routes": ["dispatch"],
                "forbidden_routes": ["implement"],
                "route_boundary": "entry-contract",
            },
        }
        dispatch_decision = {
            "runtime_id": "clean_reviewer",
            "route_decision": "worktree_review_only",
            "execution_claim": "not_executed_by_dispatch",
            "execution_profile": {
                "model_profile": "exhaustive_review",
                "reasoning_effort": "high",
                "cost_latency_bias": "quality",
                "selector_enforcement": "tool_enforced",
                "evidence_layer": "prompt_preference",
            },
            "selector_evidence": {"runtime_reported": False},
        }

        score = score_turn(
            decision,
            "Dispatch Package\nDispatch Runtime Decision",
            [{"coverage_status": "observed_supported"}],
            dispatch_decision,
        )

        self.assertEqual(score["execution_profile_verdict"], "insufficient_evidence")
        self.assertEqual(score["selector_mismatch_reason"], "selector_unverified")
        self.assertEqual(score["score_eligibility"], "insufficient_evidence")

    def test_tool_enforced_selector_requires_runtime_evidence_layer(self):
        decision = {
            "session_id": "s1",
            "turn_id": "t1",
            "decision_mode": "observe_only",
            "decision_source": "fixture",
            "router_hint_emitted": False,
            "entry_decision": {
                "expected_best": "dispatch",
                "acceptable_routes": ["dispatch"],
                "forbidden_routes": ["implement"],
                "route_boundary": "entry-contract",
            },
        }
        dispatch_decision = {
            "runtime_id": "clean_reviewer",
            "route_decision": "worktree_review_only",
            "execution_claim": "not_executed_by_dispatch",
            "execution_profile": {
                "model_profile": "exhaustive_review",
                "reasoning_effort": "high",
                "cost_latency_bias": "quality",
                "selector_enforcement": "tool_enforced",
                "evidence_layer": "prompt_preference",
            },
            "selector_evidence": {"runtime_reported": True},
        }

        score = score_turn(
            decision,
            "Dispatch Package\nDispatch Runtime Decision",
            [{"coverage_status": "observed_supported"}],
            dispatch_decision,
        )

        self.assertEqual(score["execution_profile_verdict"], "insufficient_evidence")
        self.assertEqual(score["score_eligibility"], "insufficient_evidence")

    def test_tool_enforced_selector_requires_runtime_or_tool_source(self):
        decision = {
            "session_id": "s1",
            "turn_id": "t1",
            "decision_mode": "observe_only",
            "decision_source": "fixture",
            "router_hint_emitted": False,
            "entry_decision": {
                "expected_best": "dispatch",
                "acceptable_routes": ["dispatch"],
                "forbidden_routes": ["implement"],
                "route_boundary": "entry-contract",
            },
        }
        dispatch_decision = {
            "runtime_id": "clean_reviewer",
            "route_decision": "worktree_review_only",
            "execution_claim": "not_executed_by_dispatch",
            "execution_profile": {
                "model_profile": "exhaustive_review",
                "reasoning_effort": "high",
                "cost_latency_bias": "quality",
                "selector_enforcement": "tool_enforced",
                "evidence_layer": "runtime_tool_evidence",
            },
            "selector_evidence": {"runtime_reported": True, "source": "dispatch_package"},
        }

        score = score_turn(
            decision,
            "Dispatch Package\nDispatch Runtime Decision",
            [{"coverage_status": "observed_supported"}],
            dispatch_decision,
        )

        self.assertEqual(score["execution_profile_verdict"], "insufficient_evidence")
        self.assertEqual(score["score_eligibility"], "insufficient_evidence")

    def test_verify_right_route_wrong_output_contract_fails(self):
        decision = {
            "session_id": "s1",
            "turn_id": "t1",
            "decision_mode": "observe_only",
            "decision_source": "fixture",
            "router_hint_emitted": False,
            "entry_decision": {
                "expected_best": "verify",
                "acceptable_routes": ["verify"],
                "forbidden_routes": ["implement"],
                "route_boundary": "implementation-vs-readiness",
            },
        }

        score = score_turn(
            decision,
            "Verification Scope\n- In Scope: local diff only",
            [{"coverage_status": "observed_supported"}],
        )

        self.assertEqual(score["actual_route"], "verify")
        self.assertEqual(score["routing_verdict"], "pass")
        self.assertEqual(score["output_contract_verdict"], "fail")
        self.assertEqual(score["overall_verdict"], "fail")
        self.assertEqual(score["failure_type"], "output_contract_failure")
        self.assertEqual(score["fix_locus"], "skill_output_contract")
        self.assertEqual(score["score_eligibility"], "baseline_eligible")

    def test_debug_hook_failure_uses_stderr_not_system_message(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            result = subprocess.run(
                [sys.executable, str(HOOKS / "user_prompt_submit_groundwork_entry.py")],
                input="{not json",
                text=True,
                cwd=root,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env={**__import__("os").environ, "GROUNDWORK_ROUTER_OBSERVABILITY_DEBUG": "1"},
                check=True,
            )

            self.assertEqual(result.stdout, "")
            self.assertIn("Groundwork router observability hook failed", result.stderr)

    def test_routing_summary_excludes_insufficient_scores_from_baseline_metrics(self):
        summary = summarize_routing_results(
            [
                {
                    "id": "live-insufficient",
                    "suite": "routing-reliability.csv",
                    "expected_route": "implement",
                    "actual_route": "implement",
                    "acceptable_routes": ["implement"],
                    "forbidden_routes": ["verify"],
                    "overall_verdict": "blocked",
                    "routing_verdict": "blocked",
                    "score_eligibility": "insufficient_evidence",
                },
                {
                    "id": "fixture-pass",
                    "suite": "routing-reliability.csv",
                    "expected_route": "verify",
                    "actual_route": "verify",
                    "acceptable_routes": ["verify"],
                    "forbidden_routes": ["implement"],
                    "overall_verdict": "pass",
                    "routing_verdict": "pass",
                    "score_eligibility": "baseline_eligible",
                },
            ]
        )

        self.assertEqual(summary["rows"], 2)
        self.assertEqual(summary["baseline_eligible_rows"], 1)
        self.assertEqual(summary["best_route_hit_at_1"], {"count": 1, "total": 1, "rate": 1.0})
        self.assertNotIn("implement -> implement", summary["route_pair_confusion"])

    def test_execution_profile_normalization_keeps_selector_as_preference(self):
        profile = normalize_execution_profile(
            "Read-only multi-perspective review -> reviewer profile / medium/high / balanced/quality",
            task_shape="clean review",
        )

        self.assertEqual(profile["model_profile"], "exhaustive_review")
        self.assertEqual(profile["reasoning_effort"], "high")
        self.assertEqual(profile["cost_latency_bias"], "quality")
        self.assertEqual(profile["selector_enforcement"], "prompt_preference")

    def test_backfill_row_drafts_csv_without_raw_prompt(self):
        score = {
            "turn_id": "t1",
            "expected_route": "write-plan",
            "actual_route": "implement",
            "acceptable_routes": ["write-plan"],
            "forbidden_routes": ["implement"],
            "failure_type": "forbidden_route",
            "notes": "secret token=abc123 should not be copied",
        }

        row, missing = backfill_row.row_from_score(score)

        self.assertEqual(missing, [])
        self.assertEqual(row["expected_best"], "write-plan")
        self.assertIn("raw prompt is not copied", row["input_scenario"])
        self.assertIn("implement", row["forbidden_routes"])
        self.assertNotIn("token=abc123", row["expected_behavior"])

    def test_backfill_preserves_verify_output_contract_failure(self):
        score = {
            "turn_id": "t1",
            "expected_route": "verify",
            "actual_route": "verify",
            "acceptable_routes": ["verify"],
            "forbidden_routes": ["implement"],
            "failure_type": "output_contract_failure",
            "checker_results": [
                {
                    "checker_id": "router_observability.verify_scope_full",
                    "verdict": "fail",
                }
            ],
        }

        row, missing = backfill_row.row_from_score(score)

        self.assertEqual(missing, [])
        self.assertEqual(row["output_contract"], "verify_scope_full")

    def test_report_includes_router_observability_section(self):
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = Path(tmp)
            score_dir = run_dir / "router-observability" / "s1" / "t1"
            score_dir.mkdir(parents=True)
            (run_dir / "summary.json").write_text('{"counts":{"pass":1},"suites":["smoke.csv"]}\n', encoding="utf-8")
            (run_dir / "results.jsonl").write_text('{"id":"pass","suite":"smoke.csv","verdict":"pass"}\n', encoding="utf-8")
            (score_dir / "router-score.json").write_text(
                json.dumps(
                    {
                        "expected_route": "dispatch",
                        "actual_route": "dispatch",
                        "overall_verdict": "pass",
                        "score_eligibility": "baseline_eligible",
                        "execution_profile_verdict": "pass",
                        "selector_enforcement": "prompt_preference",
                    }
                ),
                encoding="utf-8",
            )

            output = report.render_report(run_dir)

        self.assertIn("## Router Observability", output)
        self.assertIn("Router score artifact count: 1", output)
        self.assertIn("Execution profile verdict counts", output)
        self.assertIn("prompt_preference", output)


if __name__ == "__main__":
    unittest.main()
