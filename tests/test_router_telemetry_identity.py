#!/usr/bin/env python3
"""Synthetic hook subprocess regressions for event identity and delivery order."""

import hashlib
import importlib.util
import json
import tempfile
import threading
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from unittest import mock

from tests.test_router_hooks import HOOKS, run_hook


class RouterTelemetryIdentityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        spec = importlib.util.spec_from_file_location("telemetry_identity_tests", HOOKS / "groundwork_router_telemetry.py")
        cls.module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.module)

    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.telemetry = self.root / ".groundwork" / "harness" / "router-observability"
        self.telemetry.mkdir(parents=True)
        (self.telemetry / "config.json").write_text(
            json.dumps({
                "enabled": True,
                "mode": "observe_only",
                "raw_capture": False,
                "snippet_capture": False,
            }),
            encoding="utf-8",
        )

    def event(self, **fields):
        return {"cwd": str(self.root), "session_id": "s1", **fields}

    def tool_event(self, *, tool_id="tool-1", **fields):
        return self.event(
            tool_name="Bash",
            tool_use_id=tool_id,
            tool_input={"command": "git status --short"},
            **fields,
        )

    def emit(self, event_name, event):
        result = run_hook(
            event_name, event, self.root,
            env={"GROUNDWORK_ROUTER_OBSERVABILITY_DEBUG": "1"},
        )
        self.assertEqual(result.stdout, "")
        self.assertEqual(result.stderr, "")
        return result

    def directory(self, turn_id="t1", session_id="s1"):
        return self.telemetry / session_id / turn_id

    def rows(self, filename="tool-events.jsonl", *, turn_id="t1", session_id="s1"):
        path = self.directory(turn_id, session_id) / filename
        return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]

    def document(self, filename, *, turn_id="t1", session_id="s1"):
        return json.loads(
            (self.directory(turn_id, session_id) / filename).read_text(encoding="utf-8")
        )

    def assert_stale(self, *, turn_id="t1"):
        coverage = self.document("coverage.json", turn_id=turn_id)
        self.assertEqual(coverage["snapshot_status"], "stale")
        self.assertTrue(coverage["snapshot_id"])
        self.assertNotIn("captured_record_count", coverage)
        self.assertNotIn("unique_event_count", coverage)
        self.assertNotIn("tool_events", coverage)

    def test_request_ids_do_not_establish_or_override_native_turns(self):
        for request_id in ("request-1", "request-2"):
            self.emit("UserPromptSubmit", self.event(request_id=request_id, prompt="按 PRD 实施"))
            self.emit("Stop", self.event(request_id=request_id, last_assistant_message="done"))

        for filename in ("prompt-events.jsonl", "stop-events.jsonl"):
            rows = self.rows(filename, turn_id="_unresolved")
            self.assertEqual(len(rows), 2)
            self.assertTrue(all(row["turn_id"] is None for row in rows))
            self.assertTrue(all(row["correlation_status"] == "unresolved" for row in rows))
            self.assertEqual(
                [row["source_identity_sha256"]["request_id"] for row in rows],
                [hashlib.sha256(value.encode()).hexdigest() for value in ("request-1", "request-2")],
            )
        self.assertFalse(self.directory("request-1").exists())
        self.assertFalse((self.directory("_unresolved") / "router-decision.json").exists())

        native = self.event(turn_id="t1", request_id="different-request-id")
        self.emit("UserPromptSubmit", {**native, "prompt": "按 PRD 实施"})
        self.emit("Stop", {**native, "last_assistant_message": "done"})
        for filename in ("prompt-metadata.json", "final-metadata.json"):
            row = self.document(filename)
            self.assertEqual(row["turn_id"], "t1")
            self.assertEqual(row["turn_id_source"], "turn_id")
            self.assertEqual(row["correlation_status"], "resolved")

    def test_new_prompt_does_not_capture_late_post_with_native_pre(self):
        self.emit("UserPromptSubmit", self.event(turn_id="t1", prompt="old prompt"))
        self.emit("PreToolUse", self.tool_event(turn_id="t1"))
        self.emit("UserPromptSubmit", self.event(turn_id="t2", prompt="new prompt"))
        self.emit("PostToolUse", self.tool_event(
            request_id="late-request", tool_response={"exit_code": 0},
        ))

        rows = self.rows()
        self.assertEqual([row["hook_event_name"] for row in rows], ["PreToolUse", "PostToolUse"])
        late = rows[-1]
        self.assertEqual(late["turn_id"], "t1")
        self.assertEqual(late["turn_id_source"], "tool_use_id_binding")
        self.assertNotIn("turn_id", late["source_identity_sha256"])
        self.assertEqual(late["binding_turn_ids"], ["t1"])
        self.assertFalse((self.directory("t2") / "tool-events.jsonl").exists())

    def test_new_prompt_does_not_capture_late_post_without_native_pre(self):
        self.emit("UserPromptSubmit", self.event(turn_id="t1", prompt="old prompt"))
        self.emit("PreToolUse", self.tool_event(request_id="old-request"))
        self.emit("UserPromptSubmit", self.event(turn_id="t2", prompt="new prompt"))
        self.emit("PostToolUse", self.tool_event(request_id="old-request", tool_response="done"))

        rows = self.rows(turn_id="_unresolved")
        self.assertEqual(len(rows), 2)
        self.assertTrue(all(row["turn_id"] is None for row in rows))
        self.assertTrue(all(row["correlation_reason"] == "tool_use_id_unbound" for row in rows))
        for turn_id in ("t1", "t2"):
            self.assertFalse((self.directory(turn_id) / "tool-events.jsonl").exists())

    def test_native_post_establishes_binding_without_a_pre_event(self):
        self.emit("UserPromptSubmit", self.event(turn_id="t2", prompt="new prompt"))
        self.emit("PostToolUse", self.tool_event(turn_id="t1", tool_response="done"))
        self.emit("PostToolUse", self.tool_event(tool_response="done"))
        rows = self.rows()
        self.assertEqual([row["turn_id_source"] for row in rows], ["turn_id", "tool_use_id_binding"])
        self.assertTrue(all(row["turn_id"] == "t1" for row in rows))
        self.assertFalse((self.directory("t2") / "tool-events.jsonl").exists())

    def test_stale_active_pointer_and_non_turn_ids_cannot_resolve_an_event(self):
        self.emit("UserPromptSubmit", self.event(turn_id="t1", prompt="prompt"))
        active_path = self.directory().parent / "active-turn.json"
        active_path.write_text(json.dumps({"turn_id": "t1"}), encoding="utf-8")
        for fields in ({}, {"request_id": "t1"}, {"event_id": "t1"}, {"turn_id": 123}):
            self.emit("PostToolUse", self.event(tool_name="Bash", **fields))

        rows = self.rows(turn_id="_unresolved")
        self.assertEqual(len(rows), 4)
        self.assertTrue(all(row["turn_id"] is None for row in rows))
        self.assertTrue(all(row["correlation_reason"] == "missing_native_turn_id" for row in rows))
        self.assertFalse((self.directory() / "tool-events.jsonl").exists())
        self.assertEqual(json.loads(active_path.read_text(encoding="utf-8")), {"turn_id": "t1"})

    def test_conflicting_tool_binding_preserves_native_turns_and_rejects_inference(self):
        self.emit("PreToolUse", self.tool_event(turn_id="t1"))
        self.emit("PreToolUse", self.tool_event(turn_id="t2"))
        self.emit("PostToolUse", self.tool_event(tool_response="ambiguous"))
        self.emit("PostToolUse", self.tool_event(turn_id="t1", tool_response="native"))

        native = self.rows()[-1]
        self.assertEqual(native["turn_id"], "t1")
        self.assertEqual(native["turn_id_source"], "turn_id")
        self.assertEqual(native["correlation_status"], "conflict")
        self.assertEqual(self.rows(turn_id="t2")[0]["turn_id"], "t2")
        unresolved = self.rows(turn_id="_unresolved")[0]
        self.assertIsNone(unresolved["turn_id"])
        self.assertEqual(unresolved["correlation_status"], "conflict")
        self.assertEqual(unresolved["correlation_reason"], "tool_use_id_turn_conflict")
        self.assertEqual(unresolved["binding_turn_ids"], ["t1", "t2"])

    def test_bindings_require_native_session_and_stay_inside_that_session(self):
        self.emit("PreToolUse", self.tool_event(turn_id="t1"))
        self.emit("PostToolUse", self.tool_event(session_id="s2", tool_response="different session"))
        self.emit("PostToolUse", self.tool_event(
            session_id=None, conversation_id="s1", tool_response="fallback session",
        ))
        for session_id in ("s1", "s2"):
            row = self.rows(turn_id="_unresolved", session_id=session_id)[0]
            self.assertIsNone(row["turn_id"])
            self.assertEqual(row["correlation_status"], "unresolved")
        self.assertEqual(len(self.rows()), 1)

    def test_late_identity_conflict_invalidates_prior_inference_and_its_replay(self):
        self.emit("PreToolUse", self.tool_event(turn_id="t1"))
        late = self.tool_event(tool_response="delayed result")
        self.emit("PostToolUse", late)
        self.emit("Stop", self.event(turn_id="t1"))
        self.assertEqual(self.document("coverage.json")["unique_event_count"], 2)
        original = self.rows()[-1]

        self.emit("PreToolUse", self.tool_event(turn_id="t2"))
        self.assert_stale()
        self.emit("Stop", self.event(turn_id="t1"))
        coverage = self.document("coverage.json")
        self.assertEqual(coverage["unique_event_count"], 1)
        self.assertEqual(coverage["excluded_correlation_event_count"], 1)
        self.assertEqual(coverage["tool_events"], 1)
        self.assertEqual(self.rows()[-1], original)
        self.assertEqual(original["correlation_scope"], "capture_time_only")

        self.emit("PostToolUse", late)
        self.assert_stale()
        self.emit("Stop", self.event(turn_id="t1"))
        coverage = self.document("coverage.json")
        self.assertEqual(coverage["captured_record_count"], 3)
        self.assertEqual(coverage["unique_event_count"], 1)
        self.assertEqual(coverage["excluded_correlation_event_count"], 1)
        self.assertEqual(coverage["duplicate_event_count"], 1)
        self.assertEqual(self.rows()[-1]["correlation_status"], "conflict")
        self.assertFalse((self.directory("_unresolved") / "tool-events.jsonl").exists())

    def test_replay_after_binding_stays_in_original_unresolved_bucket(self):
        post = self.tool_event(tool_response="delayed result")
        self.emit("PostToolUse", post)
        self.emit("Stop", self.event())
        self.emit("PreToolUse", self.tool_event(turn_id="t1"))
        self.emit("PostToolUse", post)
        self.emit("Stop", self.event(turn_id="t1"))
        self.assert_stale(turn_id="_unresolved")
        self.emit("Stop", self.event())
        unresolved = self.document("coverage.json", turn_id="_unresolved")
        native = self.document("coverage.json")
        self.assertEqual(unresolved["unique_event_count"], 1)
        self.assertEqual(unresolved["duplicate_event_count"], 1)
        self.assertEqual(native["unique_event_count"], 1)
        self.assertEqual(native["duplicate_event_count"], 0)
        rows = self.rows(turn_id="_unresolved")
        self.assertEqual(rows[0]["source_event_key"], rows[1]["source_event_key"])
        self.assertEqual(rows[0]["source_event_sha256"], rows[1]["source_event_sha256"])
        self.assertEqual(rows[-1]["correlation_reason"], "original_delivery_unresolved")

    def test_stop_before_prompt_and_tools_preserves_final_but_expires_coverage(self):
        self.emit("Stop", self.event(turn_id="t1", last_assistant_message="early final"))
        final = self.document("final-metadata.json")
        self.assertEqual(final["turn_id"], "t1")
        self.assertEqual(final["prompt_route_candidate"], "unknown")
        self.assertEqual(self.document("coverage.json")["captured_record_count"], 0)

        self.emit("UserPromptSubmit", self.event(turn_id="t1", prompt="late prompt"))
        self.emit("PreToolUse", self.tool_event(turn_id="t1"))
        self.emit("PostToolUse", self.tool_event(turn_id="t1", tool_response={"exit_code": 0}))
        self.assertEqual(self.document("final-metadata.json"), final)
        self.assertEqual(self.document("prompt-metadata.json")["turn_id"], "t1")
        self.assert_stale()
        self.emit("Stop", self.event(turn_id="t1"))
        coverage = self.document("coverage.json")
        self.assertEqual(coverage["captured_record_count"], 2)
        self.assertEqual(coverage["unique_event_count"], 2)
        self.assertEqual(coverage["turn_event_completeness"], "unknown")

    def test_dedup_preserves_phases_distinct_calls_and_conflicting_payloads(self):
        pre = self.tool_event(turn_id="t1")
        post = {**pre, "tool_response": {"exit_code": 0}}
        for event_name, event in (
            ("PreToolUse", pre),
            ("PostToolUse", post),
            ("PostToolUse", post),
            ("PostToolUse", {**post, "tool_use_id": "tool-2"}),
            ("PostToolUse", {**post, "tool_response": {"exit_code": 1}}),
        ):
            self.emit(event_name, event)
        self.emit("Stop", self.event(turn_id="t1", last_assistant_message="done"))

        rows = self.rows()
        self.assertEqual(len(rows), 5)
        self.assertEqual(len({row["event_uuid"] for row in rows}), 5)
        coverage = self.document("coverage.json")
        self.assertEqual(coverage["captured_record_count"], 5)
        self.assertEqual(coverage["unique_event_count"], 4)
        self.assertEqual(coverage["duplicate_event_count"], 1)
        self.assertEqual(coverage["conflicting_event_identity_count"], 1)
        self.assertEqual(coverage["tool_events"], 4)

    def test_same_tool_with_native_and_inferred_source_turns_is_not_a_replay(self):
        self.emit("PreToolUse", self.tool_event(turn_id="t1"))
        self.emit("PostToolUse", self.tool_event(turn_id="t1", tool_response="done"))
        self.emit("PostToolUse", self.tool_event(tool_response="done"))
        self.emit("Stop", self.event(turn_id="t1", last_assistant_message="done"))
        coverage = self.document("coverage.json")
        self.assertEqual(coverage["unique_event_count"], 3)
        self.assertEqual(coverage["duplicate_event_count"], 0)
        self.assertEqual(coverage["conflicting_event_identity_count"], 0)

    def test_permission_events_without_stable_identity_are_not_deduplicated(self):
        permission = self.event(turn_id="t1", tool_name="Bash", tool_input={"command": "git status --short"})
        for _ in range(2):
            self.emit("PermissionRequest", permission)
        self.emit("Stop", self.event(turn_id="t1", last_assistant_message="done"))
        coverage = self.document("coverage.json")
        self.assertEqual(len(self.rows("permission-events.jsonl")), 2)
        self.assertEqual(coverage["permission_events"], 2)
        self.assertEqual(coverage["unique_event_count"], 2)
        self.assertEqual(coverage["duplicate_event_count"], 0)

    def test_concurrent_duplicate_posts_preserve_raw_records_and_coverage(self):
        self.emit("Stop", self.event(turn_id="t1", last_assistant_message="early final"))
        events = [
            self.tool_event(turn_id="t1", tool_id=tool_id, tool_response={"exit_code": 0})
            for tool_id in ("tool-1", "tool-2")
            for _ in range(8)
        ]
        barrier = threading.Barrier(8)

        def deliver(event):
            barrier.wait(timeout=10)
            return run_hook(
                "PostToolUse", event, self.root,
                env={"GROUNDWORK_ROUTER_OBSERVABILITY_DEBUG": "1"},
            )

        with ThreadPoolExecutor(max_workers=8) as executor:
            results = list(executor.map(deliver, events))
        for result in results:
            self.assertEqual(result.stdout, "")
            self.assertEqual(result.stderr, "")

        rows = self.rows()
        self.assertEqual(len(rows), 16)
        self.assertEqual(len({row["event_uuid"] for row in rows}), 16)
        self.assertTrue(all(row["turn_id"] == "t1" for row in rows))
        self.assert_stale()
        self.emit("Stop", self.event(turn_id="t1"))
        coverage = self.document("coverage.json")
        self.assertEqual(coverage["captured_record_count"], 16)
        self.assertEqual(coverage["unique_event_count"], 2)
        self.assertEqual(coverage["duplicate_event_count"], 14)
        self.assertEqual(coverage["conflicting_event_identity_count"], 0)
        self.assertEqual(coverage["malformed_event_count"], 0)

    def test_internal_names_case_and_encoded_looking_ids_stay_separate(self):
        unsafe = "turn/a"
        legacy_hash = hashlib.sha256(unsafe.encode()).hexdigest()[:16]
        encoded = self.module.safe_path_component(unsafe)
        ids = [".telemetry.lock", "active-turn.json", "tool-turns", "_unresolved", "config.json", unsafe,
               legacy_hash, encoded, "t1", "T1", "é", "e\u0301", "x" * 300]
        components = [self.module.safe_path_component(value) for value in ids]
        self.assertEqual(len(set(value.casefold() for value in components)), len(ids))
        self.assertEqual(self.module.safe_path_component("s1"), "s1")
        self.assertEqual(self.module.safe_path_component("t1"), "t1")
        # An old ambiguous directory remains untouched and is never a fallback.
        legacy = self.directory(legacy_hash)
        legacy.mkdir(parents=True)
        marker = legacy / "prompt-metadata.json"
        marker.write_text('{"historical": true}', encoding="utf-8")
        active = legacy.parent / "active-turn.json"
        active.write_text('{"turn_id": "legacy-fallback"}', encoding="utf-8")
        for value in ids:
            self.emit("UserPromptSubmit", self.event(turn_id=value, prompt="synthetic prompt"))
            self.emit("PostToolUse", self.tool_event(turn_id=value, tool_id=value))
        for value, component in zip(ids, components):
            row = self.document("prompt-metadata.json", turn_id=component)
            self.assertEqual(row["turn_id"], value)
            self.assertEqual(self.rows(turn_id=component)[0]["turn_id"], value)
        self.assertEqual(json.loads(marker.read_text()), {"historical": True})
        self.assertEqual(json.loads(active.read_text()), {"turn_id": "legacy-fallback"})

    def test_session_encoding_separates_config_case_and_missing_identity(self):
        identities = [None, "session-unknown", "_unresolved-session", "config.json", "s1", "S1", "session/a"]
        for session_id in identities:
            self.emit("PostToolUse", self.tool_event(session_id=session_id, turn_id="t1"))
        directories = [self.module.turn_dir(self.root, value, "t1") for value in identities]
        self.assertEqual(len(set(str(path).casefold() for path in directories)), len(identities))
        for session_id, directory in zip(identities, directories):
            row = json.loads((directory / "tool-events.jsonl").read_text())
            self.assertEqual(row["session_id"], session_id)
        self.assertTrue(json.loads((self.telemetry / "config.json").read_text())["enabled"])

    def test_late_capture_does_not_rescan_history(self):
        self.emit("Stop", self.event(turn_id="t1"))
        with mock.patch.object(self.module, "ordered_events_for_stop", side_effect=AssertionError("history scan during capture")):
            self.module.handle_tool_event(self.tool_event(turn_id="t1"), "PostToolUse")
            self.module.handle_permission_event(self.event(turn_id="t1", tool_name="Bash"))
        self.assertEqual(len(self.rows()), 1)
        self.assertEqual(len(self.rows("permission-events.jsonl")), 1)
        self.assert_stale()

    def test_snapshot_computation_does_not_lock_capture_or_publish_stale_counts(self):
        self.emit("PreToolUse", self.tool_event(turn_id="t1"))
        self.emit("PostToolUse", self.tool_event(tool_response="inferred"))
        original = self.module.ordered_events_for_stop
        for conflict in (False, True):
            with self.subTest(conflict=conflict):
                computed, resume = threading.Event(), threading.Event()

                def paused(*args):
                    result = original(*args)
                    computed.set()
                    self.assertTrue(resume.wait(10))
                    return result

                with mock.patch.object(self.module, "ordered_events_for_stop", side_effect=paused):
                    with ThreadPoolExecutor(max_workers=1) as pool:
                        stop = pool.submit(self.module.handle_stop, self.event(turn_id="t1"))
                        try:
                            self.assertTrue(computed.wait(10))
                            if conflict:
                                self.emit("PreToolUse", self.tool_event(turn_id="t2"))
                            else:
                                self.emit("PostToolUse", self.tool_event(turn_id="t1", tool_id="new-call"))
                        finally:
                            resume.set()
                        stop.result(timeout=10)
                self.assert_stale()
                self.emit("Stop", self.event(turn_id="t1"))
                coverage = self.document("coverage.json")
                self.assertEqual(coverage["snapshot_status"], "current")
                self.assertEqual(coverage["unique_event_count"], 2 if conflict else 3)
                self.assertEqual(coverage["excluded_correlation_event_count"], 1 if conflict else 0)

    def test_long_inferred_history_does_not_drop_concurrent_late_events(self):
        directory = self.directory()
        directory.mkdir(parents=True)
        bindings = directory.parent / "tool-turns"
        bindings.mkdir()
        with (directory / "tool-events.jsonl").open("w", encoding="utf-8") as trace:
            for index in range(2000):
                tool_id = f"seed-{index}"
                event = self.tool_event(tool_id=tool_id)
                row = {"turn_id": "t1", "turn_id_source": "tool_use_id_binding", "tool_use_id": tool_id,
                       "hook_event_name": "PostToolUse", "coverage_status": "observed_supported",
                       **self.module.source_event_metadata(event, "PostToolUse"), **self.module.event_metadata()}
                trace.write(json.dumps(row) + "\n")
                (bindings / (self.module.stable_hash(tool_id) + ".json")).write_text(json.dumps({"turn_ids": ["t1"]}))
        (directory / "coverage.json").write_text('{"snapshot_status":"current","unique_event_count":2000}')
        self.assertEqual(len(self.rows()), 2000)
        barrier = threading.Barrier(8)

        def deliver(index):
            barrier.wait(timeout=10)
            return self.emit("PostToolUse", self.tool_event(turn_id="t1", tool_id=f"late-{index}"))

        with ThreadPoolExecutor(max_workers=8) as pool:
            list(pool.map(deliver, range(8)))
        self.assertEqual(len(self.rows()), 2008)
        self.assert_stale()
        self.emit("Stop", self.event(turn_id="t1"))
        coverage = self.document("coverage.json")
        self.assertEqual(coverage["snapshot_status"], "current")
        self.assertEqual(coverage["unique_event_count"], 2008)
        self.assertEqual(coverage["malformed_event_count"], 0)


if __name__ == "__main__":
    unittest.main()
