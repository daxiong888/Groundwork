#!/usr/bin/env python3
import json
import os
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HOOKS = ROOT / "scripts" / "codex-hooks"
HOOK_ENTRYPOINT = "groundwork_router_event.py"


def run_hook(event_name, event, cwd, env=None):
    hook_env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}
    if env:
        hook_env.update(env)
    return subprocess.run(
        [sys.executable, str(HOOKS / HOOK_ENTRYPOINT), event_name],
        input=json.dumps(event),
        text=True,
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=hook_env,
        check=True,
    )


class RouterHookTests(unittest.TestCase):
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

    def test_packaged_hook_scripts_are_self_contained_without_evals_imports(self):
        import_pattern = re.compile(r"(?m)^\s*(?:from|import)\s+evals(?:\.|\s|$)")
        for script in HOOKS.glob("*.py"):
            self.assertNotRegex(script.read_text(encoding="utf-8"), import_pattern)

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            hook_root = root / "scripts" / "codex-hooks"
            hook_root.mkdir(parents=True)
            for source in HOOKS.iterdir():
                if source.is_file():
                    (hook_root / source.name).write_text(
                        source.read_text(encoding="utf-8"),
                        encoding="utf-8",
                    )

            result = subprocess.run(
                [sys.executable, str(hook_root / HOOK_ENTRYPOINT), "UserPromptSubmit"],
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
                },
                check=True,
            )

            decision = json.loads(
                (self.turn_dir(root) / "router-decision.json").read_text(encoding="utf-8")
            )
            self.assertEqual(result.stdout, "")
            self.assertEqual(result.stderr, "")
            self.assertEqual(decision["entry_decision"]["expected_best"], "verify")
            self.assertEqual(decision["decision_mode"], "observe_only")
            self.assertFalse(decision["behavior_intervention"])

    def test_user_prompt_hook_noops_without_project_opt_in(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            result = run_hook(
                "UserPromptSubmit",
                {
                    "cwd": str(root),
                    "session_id": "s1",
                    "turn_id": "t1",
                    "prompt": "按 PRD 实施",
                },
                root,
            )

            self.assertEqual(result.stdout, "")
            self.assertEqual(result.stderr, "")
            self.assertFalse((root / ".groundwork").exists())

    def test_observe_only_records_telemetry_without_score_or_card(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_config(root)
            base_event = {"cwd": str(root), "session_id": "s1", "turn_id": "t1"}
            run_hook(
                "UserPromptSubmit",
                {**base_event, "prompt": "按 PRD 实施 docs/foo.md token=secret-123"},
                root,
            )
            run_hook(
                "PostToolUse",
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
                "Stop",
                {
                    **base_event,
                    "last_assistant_message": (
                        "Implementation Summary\nFiles Changed\nChecks Run token=secret-456"
                    ),
                },
                root,
            )

            turn_dir = self.turn_dir(root)
            decision = json.loads((turn_dir / "router-decision.json").read_text(encoding="utf-8"))
            final_metadata = json.loads(
                (turn_dir / "final-metadata.json").read_text(encoding="utf-8")
            )
            tool_event = json.loads(
                (turn_dir / "tool-events.jsonl").read_text(encoding="utf-8")
            )
            self.assertEqual(result.stdout, "")
            self.assertEqual(decision["decision_source"], "prompt_classifier_candidate")
            self.assertEqual(decision["entry_decision"]["candidate_scope"], "route_only")
            self.assertNotIn("secret-123", json.dumps(decision))
            self.assertNotIn("secret-456", json.dumps(final_metadata))
            self.assertEqual(tool_event["tool_use_id"], "tool-1")
            self.assertIs(tool_event["tool_response_present"], True)
            self.assertEqual(tool_event["tool_response_status"], "success")
            self.assertTrue(tool_event["tool_input_sha256"])
            self.assertTrue(tool_event["tool_response_sha256"])
            self.assertFalse((turn_dir / "router-score.json").exists())
            self.assertFalse((turn_dir / "router-card.md").exists())
            self.assertFalse((turn_dir / "dispatch-decision.json").exists())

    def test_hooks_do_not_follow_symlinked_fixed_output_files(self):
        with self.subTest(output="prompt-metadata.json"), tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_config(root)
            out_dir = self.turn_dir(root)
            out_dir.mkdir(parents=True)
            victim = root / "victim.json"
            victim.write_text("untouched", encoding="utf-8")
            (out_dir / "prompt-metadata.json").symlink_to(victim)

            run_hook(
                "UserPromptSubmit",
                {
                    "cwd": str(root),
                    "session_id": "s1",
                    "turn_id": "t1",
                    "prompt": "按 PRD 实施",
                },
                root,
            )

            self.assertEqual(victim.read_text(encoding="utf-8"), "untouched")

        with self.subTest(output="final.raw.txt"), tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_config(root, raw_capture=True)
            base_event = {"cwd": str(root), "session_id": "s1", "turn_id": "t1"}
            run_hook("UserPromptSubmit", {**base_event, "prompt": "按 PRD 实施"}, root)
            out_dir = self.turn_dir(root)
            victim = root / "victim.txt"
            victim.write_text("untouched", encoding="utf-8")
            (out_dir / "final.raw.txt").symlink_to(victim)

            run_hook(
                "Stop",
                {**base_event, "last_assistant_message": "Implementation Summary"},
                root,
            )

            self.assertEqual(victim.read_text(encoding="utf-8"), "untouched")

    def test_raw_capture_is_always_redacted(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_config(root, raw_capture=True)
            base_event = {"cwd": str(root), "session_id": "s1", "turn_id": "t1"}
            github_token = "ghp_1234567890abcdef1234567890abcdef1234"
            openai_key = "sk-1234567890abcdef1234567890abcdef"
            run_hook(
                "UserPromptSubmit",
                {**base_event, "prompt": f"按 PRD 实施 {github_token} password=hunter2"},
                root,
            )
            run_hook(
                "Stop",
                {**base_event, "last_assistant_message": f"Checks Run {openai_key}"},
                root,
            )

            out_dir = self.turn_dir(root)
            prompt_raw = json.loads((out_dir / "prompt.raw.json").read_text(encoding="utf-8"))
            final_raw = (out_dir / "final.raw.txt").read_text(encoding="utf-8")
            self.assertIn("[REDACTED_GITHUB_TOKEN]", prompt_raw["prompt"])
            self.assertIn("[REDACTED_OPENAI_KEY]", final_raw)
            self.assertNotIn(github_token, json.dumps(prompt_raw))
            self.assertNotIn("hunter2", json.dumps(prompt_raw))
            self.assertNotIn(openai_key, final_raw)


if __name__ == "__main__":
    unittest.main()
