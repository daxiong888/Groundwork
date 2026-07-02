#!/usr/bin/env python3
import json
import importlib.util
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from evals import schema_validation
from evals.router_observability import backfill_row
from evals import report
from evals.routing_summary import summarize_routing_results
from evals.verdict_model import normalize_execution_profile, render_router_card, score_turn


ROOT = Path(__file__).resolve().parents[1]
HOOKS = ROOT / "scripts" / "codex-hooks"
ROUTER_SCORE_SCHEMA = ROOT / "schemas" / "groundwork-router-score.schema.json"


def load_hooks_module():
    spec = importlib.util.spec_from_file_location(
        "groundwork_router_observability_for_test",
        HOOKS / "groundwork_router_observability.py",
    )
    module = importlib.util.module_from_spec(spec)
    previous = sys.dont_write_bytecode
    sys.dont_write_bytecode = True
    try:
        spec.loader.exec_module(module)
    finally:
        sys.dont_write_bytecode = previous
    return module


def run_hook(script, event, cwd, env=None):
    hook_env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}
    if env:
        hook_env.update(env)
    return subprocess.run(
        [sys.executable, str(HOOKS / script)],
        input=json.dumps(event),
        text=True,
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=hook_env,
        check=True,
    )


class RouterObservabilityTests(unittest.TestCase):
    def test_hooks_manifest_uses_official_command_handler_shape(self):
        manifest = json.loads((ROOT / "hooks" / "hooks.json").read_text(encoding="utf-8"))

        self.assertEqual(set(manifest), {"hooks"})
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
                    self.assertIn('[ -f "$PLUGIN_ROOT/scripts/codex-hooks/', handler["command"])
                    self.assertIn("PYTHONDONTWRITEBYTECODE=1 python3", handler["command"])
                    self.assertIn(" || true", handler["command"])
                    self.assertIsInstance(handler.get("timeout"), int)
                    self.assertGreater(handler["timeout"], 0)

    def test_hooks_manifest_commands_noop_when_plugin_root_entrypoints_are_missing(self):
        manifest = json.loads((ROOT / "hooks" / "hooks.json").read_text(encoding="utf-8"))

        with tempfile.TemporaryDirectory() as tmp:
            plugin_root = Path(tmp) / "missing-plugin-root"
            for matcher_groups in manifest["hooks"].values():
                for group in matcher_groups:
                    for handler in group["hooks"]:
                        result = subprocess.run(
                            handler["command"],
                            shell=True,
                            cwd=tmp,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            text=True,
                            env={**os.environ, "PLUGIN_ROOT": str(plugin_root)},
                            check=True,
                        )
                        self.assertEqual(result.stdout, "")
                        self.assertEqual(result.stderr, "")

    def test_hook_entrypoints_noop_when_observability_module_is_missing(self):
        entrypoints = [
            "user_prompt_submit_groundwork_entry.py",
            "pre_tool_use_groundwork_trace.py",
            "permission_request_groundwork_trace.py",
            "post_tool_use_groundwork_trace.py",
            "stop_groundwork_score.py",
        ]

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for entrypoint in entrypoints:
                script = root / entrypoint
                script.write_text((HOOKS / entrypoint).read_text(encoding="utf-8"), encoding="utf-8")
                result = subprocess.run(
                    [sys.executable, str(script)],
                    input=json.dumps({"cwd": str(root)}),
                    text=True,
                    cwd=root,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    env={**os.environ, "PYTHONPATH": ""},
                    check=True,
                )
                self.assertEqual(result.stdout, "")
                self.assertEqual(result.stderr, "")

    def test_packaged_hook_scripts_are_self_contained_without_evals_package(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            hook_root = root / "scripts" / "codex-hooks"
            hook_root.mkdir(parents=True)
            for script in HOOKS.glob("*.py"):
                (hook_root / script.name).write_text(script.read_text(encoding="utf-8"), encoding="utf-8")

            result = subprocess.run(
                [sys.executable, str(hook_root / "user_prompt_submit_groundwork_entry.py")],
                input=json.dumps(
                    {
                        "cwd": str(root),
                        "session_id": "s1",
                        "turn_id": "t1",
                        "prompt": "self-review 已经过了，可以当 clean review 吗？",
                    }
                ),
                text=True,
                cwd=root,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env={
                    **os.environ,
                    "PYTHONPATH": "",
                    "PYTHONDONTWRITEBYTECODE": "1",
                    "GROUNDWORK_ROUTER_OBSERVABILITY": "1",
                    "GROUNDWORK_ROUTER_OBSERVABILITY_MODE": "guided_hint_trial",
                },
                check=True,
            )

            output = json.loads(result.stdout)
            self.assertIn("Verification Scope", output["hookSpecificOutput"]["additionalContext"])
            decision = json.loads((self.turn_dir(root) / "router-decision.json").read_text(encoding="utf-8"))
            self.assertEqual(decision["entry_decision"]["expected_best"], "verify")
            self.assertEqual(result.stderr, "")

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

    def assert_router_score_schema_valid(self, score_or_path):
        if isinstance(score_or_path, (str, Path)):
            score_path = Path(score_or_path)
            errors = schema_validation.validate_json_file(ROUTER_SCORE_SCHEMA, score_path)
        else:
            with tempfile.TemporaryDirectory() as tmp:
                score_path = Path(tmp) / "router-score.json"
                score_path.write_text(json.dumps(score_or_path), encoding="utf-8")
                errors = schema_validation.validate_json_file(ROUTER_SCORE_SCHEMA, score_path)
        self.assertEqual([str(error) for error in errors], [])

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
            self.assertEqual(decision["activation_source"], ".groundwork/harness/router-observability/config.json")
            self.assertEqual(decision["turn_id_source"], "turn_id")
            self.assertFalse(decision["router_hint_emitted"])
            self.assertEqual(decision["entry_decision"]["expected_best"], "implement")
            self.assertEqual(prompt_metadata["raw_prompt_storage"], "disabled")
            self.assertEqual(prompt_metadata["snippet_capture"], "disabled")
            self.assertEqual(prompt_metadata["prompt_snippet"], "")
            self.assertNotIn("secret-123", json.dumps(prompt_metadata))
            self.assertNotIn("secret-123", json.dumps(decision))
            self.assertFalse((self.turn_dir(root) / "prompt.raw.json").exists())

    def test_env_force_enable_overrides_disabled_project_config(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_config(root, enabled=False, mode="observe_only", snippet_capture=True)

            result = run_hook(
                "user_prompt_submit_groundwork_entry.py",
                {"cwd": str(root), "session_id": "s1", "turn_id": "t1", "prompt": "按 PRD 实施 docs/foo.md"},
                root,
                env={**os.environ, "GROUNDWORK_ROUTER_OBSERVABILITY": "1"},
            )

            self.assertEqual(result.stdout, "")
            decision = json.loads((self.turn_dir(root) / "router-decision.json").read_text(encoding="utf-8"))
            prompt_metadata = json.loads((self.turn_dir(root) / "prompt-metadata.json").read_text(encoding="utf-8"))
            self.assertEqual(decision["activation_source"], "env_force_enable_over_config")
            self.assertEqual(decision["decision_mode"], "observe_only")
            self.assertEqual(prompt_metadata["snippet_capture"], "enabled")

    def test_env_force_enable_records_invalid_config_source(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            config = root / ".groundwork" / "harness" / "router-observability" / "config.json"
            config.parent.mkdir(parents=True)
            config.write_text("{not json", encoding="utf-8")

            result = run_hook(
                "user_prompt_submit_groundwork_entry.py",
                {"cwd": str(root), "session_id": "s1", "turn_id": "t1", "prompt": "按 PRD 实施 docs/foo.md"},
                root,
                env={**os.environ, "GROUNDWORK_ROUTER_OBSERVABILITY": "1"},
            )

            self.assertEqual(result.stdout, "")
            decision = json.loads((self.turn_dir(root) / "router-decision.json").read_text(encoding="utf-8"))
            self.assertEqual(decision["activation_source"], "invalid_config_env_force_enable")

    def test_thin_prompt_mode_emits_route_agnostic_context_and_excludes_baseline(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_config(root, mode="thin_prompt_trial")

            result = run_hook(
                "user_prompt_submit_groundwork_entry.py",
                {"cwd": str(root), "session_id": "s1", "turn_id": "t1", "prompt": "先写实现计划，不要编辑文件"},
                root,
            )

            output = json.loads(result.stdout)
            self.assertEqual(output["hookSpecificOutput"]["hookEventName"], "UserPromptSubmit")
            context = output["hookSpecificOutput"]["additionalContext"]
            self.assertIn("Preserve evidence boundaries", context)
            self.assertIn("Keep the user's requested task primary", context)
            self.assertNotIn("expected first route", context)
            self.assertNotIn("use verify", context)
            decision = json.loads((self.turn_dir(root) / "router-decision.json").read_text(encoding="utf-8"))
            self.assertEqual(decision["decision_mode"], "thin_prompt_trial")
            self.assertEqual(decision["entry_decision"]["expected_best"], "write-plan")
            self.assertFalse(decision["router_hint_emitted"])
            self.assertTrue(decision["prompt_enhancement_emitted"])
            score = score_turn(decision, "Implementation Mini-Plan", [])
            self.assertFalse(score["router_hint_emitted"])
            self.assertTrue(score["prompt_enhancement_emitted"])
            self.assertEqual(score["score_eligibility"], "thin_prompt_excluded")
            self.assert_router_score_schema_valid(score)

    def test_thin_prompt_mode_does_not_emit_context_for_direct_prompts(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_config(root, mode="thin_prompt_trial")

            result = run_hook(
                "user_prompt_submit_groundwork_entry.py",
                {"cwd": str(root), "session_id": "s1", "turn_id": "t1", "prompt": "改一下这句话里的错别字"},
                root,
            )

            self.assertEqual(result.stdout, "")
            decision = json.loads((self.turn_dir(root) / "router-decision.json").read_text(encoding="utf-8"))
            self.assertEqual(decision["decision_mode"], "thin_prompt_trial")
            self.assertEqual(decision["entry_decision"]["expected_best"], "direct")
            self.assertFalse(decision["router_hint_emitted"])
            self.assertFalse(decision["prompt_enhancement_emitted"])
            score = score_turn(decision, "Direct answer.", [])
            self.assertFalse(score["prompt_enhancement_emitted"])
            self.assert_router_score_schema_valid(score)

    def test_guided_hint_verify_evidence_label_upgrade_mentions_verification_scope(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_config(root, mode="guided_hint_trial")

            result = run_hook(
                "user_prompt_submit_groundwork_entry.py",
                {"cwd": str(root), "session_id": "s1", "turn_id": "t1", "prompt": "self-review 已经过了，可以当 clean review 吗？"},
                root,
            )

            output = json.loads(result.stdout)
            hint = output["hookSpecificOutput"]["additionalContext"]
            self.assertIn("use verify-lite", hint)
            self.assertIn("Verification Scope", hint)
            for field in [
                "In Scope",
                "Out of Scope",
                "Covered",
                "Not Covered",
                "Evidence Sources",
                "User-visible Claim Being Verified",
            ]:
                self.assertIn(field, hint)
            self.assertIn("Do not answer as direct", hint)
            decision = json.loads((self.turn_dir(root) / "router-decision.json").read_text(encoding="utf-8"))
            self.assertEqual(decision["entry_decision"]["expected_best"], "verify")
            score = score_turn(decision, "Verification Scope\nIn Scope\nOut of Scope\nCovered\nNot Covered\nEvidence Sources\nUser-visible Claim Being Verified", [])
            self.assertEqual(score["score_eligibility"], "guided_hint_excluded")

    def test_guided_hint_non_allowlisted_routes_do_not_emit_context(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_config(root, mode="guided_hint_trial")

            result = run_hook(
                "user_prompt_submit_groundwork_entry.py",
                {"cwd": str(root), "session_id": "s1", "turn_id": "t1", "prompt": "修这个 bug，别管原因，直接 patch"},
                root,
            )

            self.assertEqual(result.stdout, "")
            decision = json.loads((self.turn_dir(root) / "router-decision.json").read_text(encoding="utf-8"))
            self.assertEqual(decision["entry_decision"]["expected_best"], "implement")
            self.assertFalse(decision["router_hint_emitted"])
            self.assertFalse(decision["prompt_enhancement_emitted"])

    def test_observe_only_does_not_emit_additional_context(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_config(root, mode="observe_only")

            result = run_hook(
                "user_prompt_submit_groundwork_entry.py",
                {"cwd": str(root), "session_id": "s1", "turn_id": "t1", "prompt": "self-review 已经过了，可以当 clean review 吗？"},
                root,
            )

            self.assertEqual(result.stdout, "")
            decision = json.loads((self.turn_dir(root) / "router-decision.json").read_text(encoding="utf-8"))
            self.assertEqual(decision["entry_decision"]["expected_best"], "verify")
            self.assertFalse(decision["router_hint_emitted"])

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
                {
                    **base_event,
                    "tool_name": "Bash",
                    "tool_use_id": "tool-1",
                    "tool_input": {"command": "git status --short"},
                    "tool_response": {"status": "success", "output": "clean"},
                    "status": "pass",
                },
                root,
            )
            result = run_hook(
                "stop_groundwork_score.py",
                {**base_event, "last_assistant_message": "Implementation Summary\nFiles Changed\nChecks Run token=secret-456"},
                root,
            )

            self.assertEqual(result.stdout, "")
            score_path = self.turn_dir(root) / "router-score.json"
            self.assert_router_score_schema_valid(score_path)
            score = json.loads(score_path.read_text(encoding="utf-8"))
            final_metadata = json.loads((self.turn_dir(root) / "final-metadata.json").read_text(encoding="utf-8"))
            tool_event = json.loads((self.turn_dir(root) / "tool-events.jsonl").read_text(encoding="utf-8"))
            card = (self.turn_dir(root) / "router-card.md").read_text(encoding="utf-8")
            self.assertEqual(score["expected_route"], "implement")
            self.assertEqual(score["actual_route"], "implement")
            self.assertEqual(final_metadata["snippet_capture"], "disabled")
            self.assertEqual(final_metadata["final_snippet"], "")
            self.assertNotIn("secret-456", json.dumps(final_metadata))
            self.assertEqual(score["score_eligibility"], "display_only")
            self.assertIn("expected_route_source", score["notes"])
            self.assertEqual(score["routing_verdict"], "pass")
            self.assertEqual(tool_event["tool_use_id"], "tool-1")
            self.assertEqual(tool_event["tool_response_present"], True)
            self.assertEqual(tool_event["tool_response_status"], "success")
            self.assertTrue(tool_event["tool_input_sha256"])
            self.assertTrue(tool_event["tool_response_sha256"])
            self.assertTrue(score["checker_results"])
            self.assertIn("Groundwork Router Decision", card)
            self.assertIn("Live heuristic display-only", card)

    def test_tool_use_id_fallback_groups_pre_and_post_events(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_config(root)
            base_event = {"cwd": str(root), "session_id": "s1", "tool_use_id": "tool-1"}

            run_hook(
                "pre_tool_use_groundwork_trace.py",
                {**base_event, "tool_name": "Bash", "tool_input": {"command": "git status --short"}},
                root,
            )
            run_hook(
                "post_tool_use_groundwork_trace.py",
                {
                    **base_event,
                    "tool_name": "Bash",
                    "tool_input": {"command": "git status --short"},
                    "tool_response": {"status": "success"},
                },
                root,
            )

            router_root = root / ".groundwork" / "harness" / "router-observability" / "s1"
            turn_dirs = [path for path in router_root.iterdir() if path.is_dir()]
            self.assertEqual(len(turn_dirs), 1)
            rows = [
                json.loads(line)
                for line in (turn_dirs[0] / "tool-events.jsonl").read_text(encoding="utf-8").splitlines()
            ]
            self.assertEqual([row["hook_event_name"] for row in rows], ["PreToolUse", "PostToolUse"])
            self.assertEqual({row["turn_id_source"] for row in rows}, {"tool_use_id_fallback"})

    def test_tool_response_exit_code_zero_is_preserved_as_status(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_config(root)
            base_event = {"cwd": str(root), "session_id": "s1", "turn_id": "t1"}

            run_hook(
                "post_tool_use_groundwork_trace.py",
                {
                    **base_event,
                    "tool_name": "Bash",
                    "tool_input": {"command": "true"},
                    "tool_response": {"exit_code": 0},
                },
                root,
            )

            tool_event = json.loads((self.turn_dir(root) / "tool-events.jsonl").read_text(encoding="utf-8"))
            self.assertEqual(tool_event["tool_response_status"], "0")

    def test_tool_response_returncode_and_rc_are_status_aliases(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_config(root)
            base_event = {"cwd": str(root), "session_id": "s1", "turn_id": "t1"}

            run_hook(
                "post_tool_use_groundwork_trace.py",
                {
                    **base_event,
                    "tool_name": "Bash",
                    "tool_input": {"command": "false"},
                    "tool_response": {"returncode": 7},
                },
                root,
            )
            run_hook(
                "post_tool_use_groundwork_trace.py",
                {
                    **base_event,
                    "tool_name": "Bash",
                    "tool_input": {"command": "false"},
                    "tool_response": {"rc": 8},
                },
                root,
            )

            rows = [
                json.loads(line)
                for line in (self.turn_dir(root) / "tool-events.jsonl").read_text(encoding="utf-8").splitlines()
            ]
            self.assertEqual([row["tool_response_status"] for row in rows], ["7", "8"])

    def test_raw_capture_writes_redacted_raw_by_default(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_config(root, raw_capture=True)
            base_event = {"cwd": str(root), "session_id": "s1", "turn_id": "t1"}
            run_hook(
                "user_prompt_submit_groundwork_entry.py",
                {
                    **base_event,
                    "prompt": (
                        "按 PRD 实施 docs/foo.md "
                        "ghp_1234567890abcdef1234567890abcdef1234 "
                        "password=hunter2"
                    ),
                },
                root,
            )
            run_hook(
                "stop_groundwork_score.py",
                {
                    **base_event,
                    "last_assistant_message": (
                        "Implementation Summary\n"
                        "Files Changed\n"
                        "Checks Run sk-1234567890abcdef1234567890abcdef "
                        "client_secret=secret-client-value AWS_SECRET_ACCESS_KEY=secret-access-key"
                    ),
                },
                root,
            )

            out_dir = self.turn_dir(root)
            prompt_raw = json.loads((out_dir / "prompt.raw.json").read_text(encoding="utf-8"))
            final_metadata = json.loads((out_dir / "final-metadata.json").read_text(encoding="utf-8"))
            final_raw_metadata = json.loads((out_dir / "final.raw.meta.json").read_text(encoding="utf-8"))
            final_raw = (out_dir / "final.raw.txt").read_text(encoding="utf-8")
            self.assertEqual(prompt_raw["redaction"]["status"], "redacted")
            self.assertIn("[REDACTED_GITHUB_TOKEN]", prompt_raw["prompt"])
            self.assertIn("[REDACTED_OPENAI_KEY]", final_raw)
            self.assertNotIn("ghp_1234567890abcdef1234567890abcdef1234", json.dumps(prompt_raw))
            self.assertNotIn("hunter2", json.dumps(prompt_raw))
            self.assertNotIn("sk-1234567890abcdef1234567890abcdef", final_raw)
            self.assertNotIn("secret-client-value", final_raw)
            self.assertNotIn("secret-access-key", final_raw)
            self.assertTrue((out_dir / "final.raw.txt").exists())
            self.assertEqual(final_metadata["raw_final_storage"], "enabled")
            self.assertEqual(final_raw_metadata["redaction"]["status"], "redacted")
            self.assertEqual(final_raw_metadata["final_sha256"], final_metadata["final_sha256"])

    def test_secret_redaction_covers_common_token_prefixes(self):
        hooks = load_hooks_module()

        text = (
            "github_pat_1234567890abcdef1234567890abcdef "
            "AKIA1234567890ABCDEF "
            "xoxb-1234567890-abcdefghij "
            "sk-proj-1234567890abcdef1234567890abcdef "
            "sk-svcacct-1234567890abcdef1234567890abcdef "
            "password=hunter2 "
            "client_secret=secret-client-value "
            "AWS_SECRET_ACCESS_KEY=secret-access-key "
            "Authorization: Bearer secret-token"
        )

        redacted = hooks.redact_text(text)

        self.assertIn("[REDACTED_GITHUB_PAT]", redacted)
        self.assertIn("[REDACTED_AWS_ACCESS_KEY_ID]", redacted)
        self.assertIn("[REDACTED_SLACK_TOKEN]", redacted)
        self.assertEqual(redacted.count("[REDACTED_OPENAI_KEY]"), 2)
        self.assertIn("password=[REDACTED]", redacted)
        self.assertIn("client_secret=[REDACTED]", redacted)
        self.assertIn("AWS_SECRET_ACCESS_KEY=[REDACTED]", redacted)
        self.assertIn("Authorization: Bearer [REDACTED]", redacted)
        self.assertNotIn("github_pat_1234567890abcdef1234567890abcdef", redacted)
        self.assertNotIn("AKIA1234567890ABCDEF", redacted)
        self.assertNotIn("xoxb-1234567890-abcdefghij", redacted)
        self.assertNotIn("sk-proj-1234567890abcdef1234567890abcdef", redacted)
        self.assertNotIn("sk-svcacct-1234567890abcdef1234567890abcdef", redacted)
        self.assertNotIn("hunter2", redacted)
        self.assertNotIn("secret-client-value", redacted)
        self.assertNotIn("secret-access-key", redacted)

    def test_stop_orders_events_and_reports_malformed_jsonl(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_config(root)
            base_event = {"cwd": str(root), "session_id": "s1", "turn_id": "t1"}
            run_hook(
                "user_prompt_submit_groundwork_entry.py",
                {**base_event, "prompt": "按 PRD 实施 docs/foo.md"},
                root,
            )
            out_dir = self.turn_dir(root)
            (out_dir / "tool-events.jsonl").write_text(
                '{"coverage_status":"observed_supported","observed_at_ns":30,"event_uuid":"c"}\n'
                '{malformed}\n'
                '{"coverage_status":"observed_supported","observed_at_ns":10,"event_uuid":"a"}\n',
                encoding="utf-8",
            )
            (out_dir / "permission-events.jsonl").write_text(
                '{"coverage_status":"observed_supported","observed_at_ns":20,"event_uuid":"b"}\n',
                encoding="utf-8",
            )

            run_hook(
                "stop_groundwork_score.py",
                {**base_event, "last_assistant_message": "Implementation Summary\nFiles Changed\nChecks Run"},
                root,
            )

            coverage = json.loads((out_dir / "coverage.json").read_text(encoding="utf-8"))
            events, diagnostics = load_hooks_module().ordered_events_for_stop(out_dir)
            self.assertEqual([event["event_uuid"] for event in events], ["a", "b", "c"])
            self.assertEqual([event["event_index"] for event in events], [1, 2, 3])
            self.assertEqual(diagnostics["malformed_tool_events"], 1)
            self.assertEqual(coverage["malformed_tool_events"], 1)

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

    def test_fast_profile_mismatch_uses_structured_clean_review_signal(self):
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
        base_dispatch_decision = {
            "runtime_id": "fast_router",
            "route_decision": "local_with_artifact",
            "execution_claim": "not_executed_by_dispatch",
            "notes": ["the word clean appears in a non-authoritative note"],
            "execution_profile": {
                "model_profile": "fast_scan",
                "reasoning_effort": "low",
                "cost_latency_bias": "fast",
                "selector_enforcement": "prompt_preference",
                "evidence_layer": "prompt_preference",
            },
        }

        non_clean_score = score_turn(
            decision,
            "Dispatch Package\nDispatch Runtime Decision",
            [{"coverage_status": "observed_supported"}],
            base_dispatch_decision,
        )
        clean_score = score_turn(
            decision,
            "Dispatch Package\nDispatch Runtime Decision",
            [{"coverage_status": "observed_supported"}],
            {**base_dispatch_decision, "task_shape": "clean_review"},
        )

        self.assertEqual(non_clean_score["execution_profile_verdict"], "pass")
        self.assertEqual(clean_score["execution_profile_verdict"], "mismatch")
        self.assertEqual(clean_score["selector_mismatch_reason"], "profile_too_weak_for_risk")
        self.assert_router_score_schema_valid(clean_score)

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
        self.assert_router_score_schema_valid(score)

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
                env={
                    **os.environ,
                    "GROUNDWORK_ROUTER_OBSERVABILITY_DEBUG": "1",
                    "PYTHONDONTWRITEBYTECODE": "1",
                },
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

    def test_backfill_cli_runs_from_repo_root_without_pythonpath(self):
        with tempfile.TemporaryDirectory() as tmp:
            score_path = Path(tmp) / "router-score.json"
            score_path.write_text(
                json.dumps(
                    {
                        "turn_id": "t1",
                        "expected_route": "implement",
                        "actual_route": "implement",
                        "acceptable_routes": ["implement"],
                        "forbidden_routes": ["verify"],
                        "failure_type": "none",
                    }
                ),
                encoding="utf-8",
            )

            result = subprocess.run(
                [sys.executable, "evals/router_observability/backfill_row.py", "--score", str(score_path)],
                cwd=ROOT,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=True,
            )

            self.assertIn("ro-backfill-t1", result.stdout)
            self.assertEqual(result.stderr, "")

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
