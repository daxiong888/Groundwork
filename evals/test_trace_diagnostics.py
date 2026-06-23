#!/usr/bin/env python3
import tempfile
import unittest
from pathlib import Path

from evals.checks import trace_diagnostics


FIXTURES = Path("evals/fixtures/trace")


class TraceDiagnosticsTests(unittest.TestCase):
    def diagnose_fixture(self, name):
        return trace_diagnostics.diagnose_jsonl_trace(FIXTURES / name)

    def test_empty_trace_returns_missing_or_unknown(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "empty.jsonl"
            path.write_text("", encoding="utf-8")

            diagnostics = trace_diagnostics.diagnose_jsonl_trace(path)

        self.assertEqual(diagnostics["trace_event_count"], 0)
        self.assertEqual(diagnostics["command_count"], 0)
        self.assertEqual(diagnostics["evidence_latency"]["status"], "not_applicable")
        self.assertEqual(diagnostics["blocked_reason"], "unknown")

    def test_basic_command_count(self):
        diagnostics = self.diagnose_fixture("basic-command-trace.jsonl")

        self.assertEqual(diagnostics["trace_event_count"], 3)
        self.assertEqual(diagnostics["command_count"], 3)
        self.assertEqual(diagnostics["duplicate_command_count"], 1)
        self.assertEqual(diagnostics["failed_command_count"], 0)
        self.assertFalse(diagnostics["trace_command_thrashing"])

    def test_duplicate_failed_command_triggers_thrashing(self):
        diagnostics = self.diagnose_fixture("thrashing-trace.jsonl")

        self.assertEqual(diagnostics["command_count"], 6)
        self.assertGreaterEqual(diagnostics["duplicate_command_count"], 4)
        self.assertEqual(diagnostics["failed_command_count"], 3)
        self.assertTrue(diagnostics["trace_command_thrashing"])
        self.assertIn(
            "same command repeated at least three times with multiple failures",
            diagnostics["thrashing_notes"],
        )

    def test_evidence_latency_detects_first_evidence(self):
        diagnostics = self.diagnose_fixture("evidence-latency-trace.jsonl")

        self.assertEqual(diagnostics["evidence_latency"]["status"], "present")
        self.assertEqual(diagnostics["evidence_latency"]["first_evidence_event_index"], 2)
        self.assertEqual(diagnostics["evidence_latency"]["first_evidence_seconds"], 12.0)

    def test_invalid_json_line_does_not_crash(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "invalid.jsonl"
            path.write_text('{"type":"message","text":"hello"}\nnot json\n', encoding="utf-8")

            diagnostics = trace_diagnostics.diagnose_jsonl_trace(path)

        self.assertEqual(diagnostics["trace_event_count"], 2)
        self.assertEqual(diagnostics["unsupported_event_count"], 1)
        self.assertIn("invalid JSON lines: 1", diagnostics["notes"])

    def test_timeout_maps_blocked_reason(self):
        diagnostics = trace_diagnostics.diagnose_trace_events(
            [
                {
                    "type": "tool_result",
                    "tool_name": "shell",
                    "payload": {
                        "command": "python3 slow_test.py",
                        "status": "error",
                        "text": "Command failed: timeout",
                    },
                }
            ]
        )

        self.assertEqual(diagnostics["failed_command_count"], 1)
        self.assertEqual(diagnostics["blocked_reason"], "timeout")

    def test_unknown_event_shape_is_tolerated(self):
        diagnostics = trace_diagnostics.diagnose_trace_events(
            [
                {"unexpected": {"nested": True}},
                ["not", "a", "dict"],
            ]
        )

        self.assertEqual(diagnostics["trace_event_count"], 2)
        self.assertEqual(diagnostics["unsupported_event_count"], 2)
        self.assertEqual(diagnostics["command_count"], 0)
        self.assertEqual(diagnostics["blocked_reason"], "unknown")


if __name__ == "__main__":
    unittest.main()
