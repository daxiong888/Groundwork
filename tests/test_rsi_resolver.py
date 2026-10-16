import json
import os
from unittest import mock

from scripts.rsi.control import locator_path
from scripts.rsi.engine import ingest, prepare
from scripts.rsi.resolver import transcript_messages
from scripts.rsi.schema import RSIError, digest
from scripts.rsi.security import ReadMeter
from scripts.rsi.sources import intake
from tests.rsi_support import RSITestCase
from tests.test_router_hooks import run_hook


class ResolverTests(RSITestCase):
    def append_context(self, path, turn="t1"):
        with path.open("a") as stream:
            stream.write(json.dumps({"type": "turn_context", "payload": {"cwd": str(self.root), "turn_id": turn}}) + "\n")

    def assert_late_gap_rejected(self, existing_gap=False, oversized=False):
        path = self.transcript()
        if existing_gap:
            with path.open("a") as stream:
                stream.write("{first malformed record}\n")
            self.append_context(path)
        self.hook(path)
        self.snapshot()
        packet = self.prepared()
        with path.open("a") as stream:
            stream.write((json.dumps({"type": "response_item", "payload": {"type": "function_call_output", "output": "x" * 70000}})
                          if oversized else "{new malformed record}") + "\n")
        self.append_context(path)
        response = ingest(self.store, packet["attempt"], self.analysis(packet, "candidate"))
        self.assertEqual(response["reason"], "freshness_unconfirmed")
        self.assertIn("transcript_evidence_changed", response["freshness_failures"])
        self.assertEqual(self.store.db.execute("SELECT COUNT(*) FROM candidates").fetchone()[0], 0)
        self.assertEqual(self.store.db.execute("SELECT state FROM attempts").fetchone()[0], "superseded")

    def test_new_malformed_record_invalidates_old_packet(self):
        self.assert_late_gap_rejected()

    def test_repeated_same_gap_kind_invalidates_old_packet(self):
        self.assert_late_gap_rejected(existing_gap=True)

    def test_new_oversized_record_invalidates_old_packet(self):
        self.assert_late_gap_rejected(oversized=True)

    def test_malformed_context_types_do_not_poison_recovery_or_claim(self):
        path = self.transcript()
        self.qualify(path)
        for bad in (["bad"], {"bad": "turn"}, 1, ""):
            self.append_context(path, bad)
            with path.open("a") as stream:
                stream.write(json.dumps({"type": "response_item", "payload": {"type": "message", "role": "user", "content": [{"type": "input_text", "text": "ambiguous"}]}}) + "\n")
        self.append_context(path)
        with path.open("a") as stream:
            stream.write(json.dumps({"type": "response_item", "payload": {"type": "message", "role": "user", "content": [{"type": "input_text", "text": "recovered"}]}}) + "\n")
        self.hook(path, transcript_format="unknown")
        packet = self.prepared()
        self.assertEqual([r["text"] for r in packet["references"] if r["ref"].startswith("message:")], ["recovered"])
        self.assertTrue(any(isinstance(g, dict) and g["status"] == "malformed_context" for g in packet["gaps"]))
        self.assertEqual(ingest(self.store, packet["attempt"], self.analysis(packet, "evidence_insufficient"))["reason"], "evidence_insufficient")

    def test_malformed_context_stays_cleared_across_scans(self):
        path = self.transcript()
        self.qualify(path)
        self.append_context(path, ["bad"])
        self.hook(path, transcript_format="unknown")
        intake(self.store, "test")
        source = self.store.db.execute("SELECT * FROM sources WHERE kind='transcript'").fetchone()
        first = transcript_messages(self.store, "test", source, "t1", 65536)
        self.assertTrue(first["scan_complete"])
        self.assertIn("malformed_context", first["gaps"])
        with path.open("a") as stream:
            stream.write(json.dumps({"type": "response_item", "payload": {"type": "message", "role": "user", "content": [{"type": "input_text", "text": "ambiguous"}]}}) + "\n")
        self.append_context(path)
        with path.open("a") as stream:
            stream.write(json.dumps({"type": "response_item", "payload": {"type": "message", "role": "user", "content": [{"type": "input_text", "text": "recovered"}]}}) + "\n")
        source = self.store.db.execute("SELECT * FROM sources WHERE kind='transcript'").fetchone()
        second = transcript_messages(self.store, "test", source, "t1", 65536)
        self.assertEqual([r["text"] for r in second["messages"]], ["recovered"])
        self.assertEqual(second["snapshot"], first["snapshot"])

    def test_valid_other_project_context_does_not_invalidate_packet(self):
        path = self.transcript()
        self.hook(path)
        self.snapshot()
        packet = self.prepared()
        with path.open("a") as stream:
            stream.write(json.dumps({"type": "turn_context", "payload": {"cwd": str(self.root / "other-project"), "turn_id": "other-turn"}}) + "\n")
            stream.write(json.dumps({"type": "response_item", "payload": {"type": "message", "role": "user", "content": [{"type": "input_text", "text": "unrelated other project"}]}}) + "\n")
        response = ingest(self.store, packet["attempt"], self.analysis(packet, "evidence_insufficient"))
        self.assertEqual(response["reason"], "evidence_insufficient")
        work = self.store.db.execute("SELECT revision FROM work WHERE id=?", (packet["work_id"],)).fetchone()
        self.assertEqual(work["revision"], packet["evidence_revision"])
        source = self.store.db.execute("SELECT config FROM sources WHERE kind='transcript'").fetchone()
        self.assertEqual(json.loads(source["config"])["scan_gaps"], [])

    def test_budget_exhaustion_preserves_qualified_cursor_anchor(self):
        from scripts.rsi.sources import file_signature
        path = self.transcript()
        self.qualify(path)
        with path.open("a") as stream:
            stream.write(json.dumps({"type": "response_item", "payload": {"type": "function_call_output", "output": "x" * 180000}}) + "\n")
            stream.write(json.dumps({"type": "turn_context", "payload": {"cwd": str(self.root), "turn_id": "t1"}}) + "\n")
            stream.write(json.dumps({"type": "response_item", "payload": {"type": "message", "role": "user", "content": [{"type": "input_text", "text": "Recovered context"}]}}) + "\n")
        self.hook(path, transcript_format="unknown")
        intake(self.store, "test")
        for _ in range(4):
            source = self.store.db.execute("SELECT * FROM sources WHERE kind='transcript'").fetchone()
            before = self.store.usage("test")["bytes"]
            resolved = transcript_messages(self.store, "test", source, "t1", 80000)
            self.assertLessEqual(self.store.usage("test")["bytes"] - before, 80000)
            source = self.store.db.execute("SELECT * FROM sources WHERE kind='transcript'").fetchone()
            with path.open("rb") as stream:
                actual = file_signature(stream, source["offset"], self.policy["transcript_bindings"][0]["start_offset"])
            self.assertEqual(json.loads(source["signature"]), actual)
            if resolved["scan_complete"]:
                break
        self.assertEqual(resolved["status"], "ok")
        self.assertIn("oversized_record", resolved["gaps"])
        self.assertEqual([m["text"] for m in resolved["messages"]], ["Recovered context"])

    def test_qualification_short_read_is_budget_gap_not_changed_source(self):
        path = self.transcript()
        self.qualify(path)
        self.hook(path, transcript_format="unknown")
        intake(self.store, "test")
        source = self.store.db.execute("SELECT * FROM sources WHERE kind='transcript'").fetchone()
        with self.assertRaisesRegex(RSIError, "read_budget_exhausted"):
            transcript_messages(self.store, "test", source, "t1", 10)
        latest = self.store.db.execute("SELECT * FROM sources WHERE id=?", (source["id"],)).fetchone()
        self.assertEqual((latest["offset"], latest["signature"]), (source["offset"], source["signature"]))

    def test_prepare_defers_large_scan_without_packet_or_poisoned_cursor(self):
        path = self.transcript()
        self.qualify(path)
        with path.open("a") as stream:
            stream.write(json.dumps({"type": "response_item", "payload": {"type": "function_call_output", "output": "x" * 2000000}}) + "\n")
        self.hook(path, transcript_format="unknown")
        self.snapshot()
        prepare(self.store, "test")
        self.clock[0] += 2
        response = prepare(self.store, "test")
        self.assertEqual(response["reason"], "limit")
        self.assertNotIn("packet", response)
        attempt = self.store.db.execute("SELECT * FROM attempts").fetchone()
        self.assertEqual(attempt["state"], "deferred")
        self.assertIsNone(attempt["packet"])
        self.assertEqual(self.store.usage("test")["reserved"], 0)
        self.assertEqual(self.store.db.execute("SELECT state FROM work LIMIT 1").fetchone()[0], "pending")

    def test_live_budget_shape_recovers_next_day_without_budget_expansion(self):
        self.policy["budgets"].update(daily_bytes=2097152, freshness_bytes=262144)
        path = self.transcript()
        with path.open("a") as stream:
            stream.write(json.dumps({"type": "response_item", "payload": {"type": "function_call_output", "output": "h" * 8280000}}) + "\n")
        self.qualify(path)
        with path.open("a") as stream:
            stream.write(json.dumps({"type": "response_item", "payload": {"type": "function_call_output", "output": "x" * 2000000}}) + "\n")
            stream.write(json.dumps({"type": "turn_context", "payload": {"cwd": str(self.root), "turn_id": "t1"}}) + "\n")
            stream.write(json.dumps({"type": "response_item", "payload": {"type": "message", "role": "user", "content": [{"type": "input_text", "text": "Bounded synthetic result"}]}}) + "\n")
        self.hook(path, transcript_format="unknown")
        for i in range(19):
            self.append(self.event(tool_use_id=f"fixture-{i}"))
        self.snapshot()
        with self.store.tx():
            self.store.charge("test", bytes=634295)
        prepare(self.store, "test")
        self.clock[0] += 2
        response = prepare(self.store, "test")
        self.assertEqual(response["reason"], "limit")
        self.assertNotIn("packet", response)
        self.assertLessEqual(self.store.usage("test")["bytes"], 2097152 - 262144)
        source = self.store.db.execute("SELECT * FROM sources WHERE kind='transcript'").fetchone()
        self.assertGreater(source["offset"], self.policy["transcript_bindings"][0]["start_offset"])
        self.assertEqual(source["skipping"], 1)
        self.clock[0] += 86400
        packet = prepare(self.store, "test")["packet"]
        self.assertEqual([r["text"] for r in packet["references"] if r["ref"].startswith("message:")], ["Bounded synthetic result"])
        self.assertTrue(all(s["snapshot_status"] == "current" for s in packet["source_snapshots"].values()))
        self.assertEqual(ingest(self.store, packet["attempt"], self.analysis(packet, "evidence_insufficient"))["reason"], "evidence_insufficient")
        self.assertLessEqual(self.store.usage("test")["bytes"], 2097152)

    def test_ingest_uses_one_freshness_budget_and_explains_rejection(self):
        self.policy["budgets"]["freshness_bytes"] = 4096
        self.enable("small-freshness")
        path = self.transcript()
        self.hook(path)
        self.snapshot()
        packet = self.prepared()
        for i in range(30):
            self.append(self.event(tool_use_id=f"late-{i}"))
        before = self.store.usage("test")["bytes"]
        response = ingest(self.store, packet["attempt"], self.analysis(packet, "evidence_insufficient"))
        self.assertLessEqual(self.store.usage("test")["bytes"] - before, 4096)
        self.assertEqual(response["reason"], "freshness_unconfirmed")
        self.assertIn("intake_incomplete", response["freshness_failures"])
        self.assertEqual(self.store.usage("test")["reserved"], 0)

    def test_completed_oversized_skip_returns_recovered_messages_with_gap(self):
        path = self.transcript()
        self.qualify(path)
        def message(text):
            return {"type": "response_item", "payload": {"type": "message", "role": "user", "content": [{"type": "input_text", "text": text}]}}
        rows = [message("before"), {"type": "response_item", "payload": {"type": "function_call_output", "output": "x" * 70000}},
                message("ambiguous after skipped context"), {"type": "turn_context", "payload": {"cwd": str(self.root), "turn_id": "t1"}}, message("recovered")]
        with path.open("a") as stream:
            stream.write("".join(json.dumps(row) + "\n" for row in rows))
        self.hook(path, transcript_format="unknown")
        packet = self.prepared()
        self.assertEqual([r["text"] for r in packet["references"] if r["ref"].startswith("message:")], ["before", "recovered"])
        self.assertTrue(any(isinstance(g, dict) and g["status"] == "oversized_record" for g in packet["gaps"]))
        self.assertEqual(ingest(self.store, packet["attempt"], self.analysis(packet, "evidence_insufficient"))["reason"], "evidence_insufficient")

    def test_scan_uses_opening_watermark_and_reports_concurrent_append(self):
        path = self.transcript()
        self.qualify(path)
        def message(text):
            return json.dumps({"type": "response_item", "payload": {"type": "message", "role": "user", "content": [{"type": "input_text", "text": text}]}}).encode() + b"\n"
        first, late = message("opening message"), message("late append")
        with path.open("ab") as stream:
            stream.write(first)
        self.hook(path, transcript_format="unknown")
        intake(self.store, "test")
        original = ReadMeter.read
        appended = []
        def read(meter, stream, size, line=False):
            raw = original(meter, stream, size, line)
            if raw == first and not appended:
                with path.open("ab") as writer:
                    writer.write(late)
                appended.append(True)
            return raw
        source = self.store.db.execute("SELECT * FROM sources WHERE kind='transcript'").fetchone()
        with mock.patch.object(ReadMeter, "read", read):
            resolved = transcript_messages(self.store, "test", source, "t1", 65536)
        self.assertEqual(resolved["status"], "source_advanced")
        self.assertFalse(resolved["scan_complete"])
        self.assertEqual(resolved["messages"], [])
        source = self.store.db.execute("SELECT * FROM sources WHERE kind='transcript'").fetchone()
        self.assertEqual(source["offset"], path.stat().st_size - len(late))
        resolved = transcript_messages(self.store, "test", source, "t1", 65536)
        self.assertEqual([r["text"] for r in resolved["messages"]], ["opening message", "late append"])

    def test_incomplete_line_keeps_cursor_and_recovers_when_completed(self):
        path = self.transcript()
        self.qualify(path)
        raw = json.dumps({"type": "response_item", "payload": {"type": "message", "role": "user", "content": [{"type": "input_text", "text": "finished later"}]}}).encode()
        boundary = path.stat().st_size
        with path.open("ab") as stream:
            stream.write(raw)
        self.hook(path, transcript_format="unknown")
        intake(self.store, "test")
        source = self.store.db.execute("SELECT * FROM sources WHERE kind='transcript'").fetchone()
        resolved = transcript_messages(self.store, "test", source, "t1", 65536)
        self.assertEqual(resolved["status"], "incomplete_record")
        source = self.store.db.execute("SELECT * FROM sources WHERE kind='transcript'").fetchone()
        self.assertEqual(source["offset"], boundary)
        with path.open("ab") as stream:
            stream.write(b"\n")
        resolved = transcript_messages(self.store, "test", source, "t1", 65536)
        self.assertEqual([r["text"] for r in resolved["messages"]], ["finished later"])

    def test_unrelated_tail_budget_failure_does_not_invent_evidence_revision(self):
        self.policy["budgets"]["freshness_bytes"] = 4096
        self.enable("small-tail-budget")
        path = self.transcript()
        self.hook(path)
        self.snapshot()
        packet = self.prepared()
        with path.open("a") as stream:
            stream.write(json.dumps({"type": "turn_context", "payload": {"cwd": str(self.root), "turn_id": "t2"}}) + "\n")
            stream.write(json.dumps({"type": "response_item", "payload": {"type": "function_call_output", "output": "x" * 70000}}) + "\n")
        response = ingest(self.store, packet["attempt"], self.analysis(packet, "evidence_insufficient"))
        self.assertEqual(response["reason"], "freshness_unconfirmed")
        self.assertIn("transcript:budget_exhausted", response["freshness_failures"])
        revision = self.store.db.execute("SELECT revision FROM work WHERE id=?", (packet["work_id"],)).fetchone()[0]
        self.assertEqual(revision, packet["evidence_revision"])

    def test_qualification_exception_still_counts_against_evidence_meter(self):
        from scripts.rsi.resolver import evidence
        from scripts.rsi.security import ReadMeter
        path = self.transcript()
        self.qualify(path)
        self.hook(path, transcript_format="unknown")
        intake(self.store, "test")
        work = self.store.db.execute("SELECT * FROM work LIMIT 1").fetchone()
        phase = ReadMeter(self.store, "test", 10)
        before = self.store.usage("test")["bytes"]
        refs, gaps, used = evidence(self.store, "test", work, 10, meter=phase)
        self.assertEqual(used, self.store.usage("test")["bytes"] - before)
        self.assertLessEqual(used, 10)
        self.assertTrue(any(isinstance(g, dict) and g["status"] == "read_budget_exhausted" for g in gaps))

    def transcript(self, **overrides):
        path = self.transcripts / "synthetic.jsonl"
        rows = [
            {"type": "session_meta", "payload": {"id": "s1", "cli_version": "fixture"}},
            {"type": "turn_context", "payload": {"turn_id": "t1", "cwd": str(self.root), "model": "fixture"}},
            {"type": "response_item", "payload": {"type": "message", "role": "user", "content": [{"type": "input_text", "text": "Find the applicable rule. <environment_context>private path</environment_context>"}]}},
            {"type": "response_item", "payload": {"type": "message", "role": "assistant", "channel": "analysis", "content": [{"type": "output_text", "text": "Hidden reasoning fixture"}]}},
            {"type": "response_item", "payload": {"type": "message", "role": "assistant", "channel": "final", "content": [{"type": "output_text", "text": "The current rule is scoped."}]}}
        ]
        if overrides:
            rows[1]["payload"].update(overrides)
        path.write_text("".join(json.dumps(row) + "\n" for row in rows))
        return path

    def hook(self, path, **extra):
        (self.telemetry / "config.json").write_text(json.dumps({"enabled": True, "raw_capture": False, "snippet_capture": False}))
        response = run_hook("UserPromptSubmit", {"cwd": str(self.root), "session_id": "s1", "turn_id": "t1", "transcript_path": str(path), "transcript_format": "codex.session_jsonl.v1", "prompt": "synthetic prompt", **extra}, self.root)
        self.assertEqual(response.stdout, "")
        self.assertEqual(response.stderr, "")

    def test_real_hook_entrypoint_registers_locator_and_auto_resolves_fixture(self):
        path = self.transcript()
        self.hook(path)
        self.assertTrue(locator_path(self.store, "test").exists())
        packet = self.prepared()
        messages = [ref for ref in packet["references"] if ref["ref"].startswith("message:")]
        self.assertEqual(len(messages), 2)
        self.assertNotIn(str(path), json.dumps(packet))
        self.assertNotIn("Hidden reasoning", json.dumps(packet))
        self.assertNotIn("private path", json.dumps(packet))
        response = ingest(self.store, packet["attempt"], self.analysis(packet))
        self.assertEqual(response["reason"], "not_candidate")

    def qualify(self, path):
        with path.open("rb") as stream:
            header = stream.readline()
            context_position = stream.tell()
            context = stream.readline()
        st = path.stat()
        self.policy["transcript_bindings"] = [{
            "session_id": "s1", "path": str(path), "format": "codex.session_jsonl.v1",
            "file_identity": [st.st_dev, st.st_ino, getattr(st, "st_birthtime", None)],
            "header_digest": digest(header), "context_position": context_position,
            "context_digest": digest(context), "start_offset": st.st_size,
            "verified_by": "interactive_host_schema_check",
        }]
        self.enable("qualify-current-host")

    def test_qualified_host_without_format_reads_only_after_enablement(self):
        path = self.transcript()
        self.qualify(path)
        with path.open("a") as stream:
            stream.write(json.dumps({"type": "response_item", "payload": {"type": "message", "role": "assistant", "channel": "commentary", "content": [{"type": "output_text", "text": "New authorized observation"}]}}) + "\n")
        self.hook(path, transcript_format="unknown")
        packet = self.prepared()
        messages = [ref for ref in packet["references"] if ref["ref"].startswith("message:")]
        self.assertEqual([ref["text"] for ref in messages], ["New authorized observation"])
        self.assertEqual(messages[0]["format_source"], "interactive_host_schema_check")
        self.assertEqual(ingest(self.store, packet["attempt"], self.analysis(packet))["reason"], "not_candidate")

    def test_qualified_host_rejects_other_session_or_file(self):
        path = self.transcript()
        self.qualify(path)
        self.hook(path, session_id="other-session", transcript_format="unknown")
        self.assertFalse(locator_path(self.store, "test").exists())
        other = path.with_name("other.jsonl")
        other.write_bytes(path.read_bytes())
        self.hook(other, transcript_format="unknown")
        self.assertFalse(locator_path(self.store, "test").exists())

    def test_qualified_host_replacement_cannot_reset_to_historical_content(self):
        path = self.transcript()
        self.qualify(path)
        self.hook(path, transcript_format="unknown")
        intake(self.store, "test")
        source = self.store.db.execute("SELECT * FROM sources WHERE kind='transcript'").fetchone()
        path.rename(path.with_suffix(".old"))
        self.transcript()
        with self.assertRaisesRegex(RSIError, "transcript_qualification_changed"):
            transcript_messages(self.store, "test", source, "t1", 65536)
        self.assertEqual(self.store.db.execute("SELECT COUNT(*) FROM messages").fetchone()[0], 0)

    def test_qualified_reads_do_not_cross_back_into_historical_messages(self):
        path = self.transcript()
        self.qualify(path)
        binding = self.policy["transcript_bindings"][0]
        with path.open("rb") as stream:
            stream.readline()
            stream.readline()
            metadata_end = stream.tell()
        with path.open("a") as stream:
            stream.write(json.dumps({"type": "response_item", "payload": {"type": "message", "role": "user", "content": [{"type": "input_text", "text": "New message"}]}}) + "\n")
        self.hook(path, transcript_format="unknown")
        intake(self.store, "test")
        original, ranges = ReadMeter.read, []
        def tracked(meter, stream, size, line=False):
            start = stream.tell()
            data = original(meter, stream, size, line)
            if data:
                ranges.append((start, start + len(data)))
            return data
        with mock.patch.object(ReadMeter, "read", tracked):
            for _ in range(2):
                source = self.store.db.execute("SELECT * FROM sources WHERE kind='transcript'").fetchone()
                self.assertEqual(transcript_messages(self.store, "test", source, "t1", 65536)["status"], "ok")
        self.assertTrue(ranges)
        self.assertTrue(all(end <= metadata_end or start >= binding["start_offset"] - 1 for start, end in ranges), ranges)

    def test_independent_locator_optin_unknown_format_and_no_join(self):
        path = self.transcript()
        self.policy["semantic_source_locator"] = False
        self.enable("disable-locator")
        self.hook(path)
        self.assertFalse(locator_path(self.store, "test").exists())
        self.policy["semantic_source_locator"] = True
        self.enable("reenable-locator")
        self.hook(path, transcript_format="unknown")
        intake(self.store, "test")
        source = self.store.db.execute("SELECT * FROM sources WHERE kind='transcript'").fetchone()
        with self.assertRaisesRegex(RSIError, "unsupported"):
            transcript_messages(self.store, "test", source, "t1", 65536)

    def test_cross_project_turn_and_missing_native_turn_are_not_guessed(self):
        path = self.transcript(cwd="/other/project")
        self.hook(path)
        packet = self.prepared()
        self.assertFalse(any(ref["ref"].startswith("message:") for ref in packet["references"]))
        self.assertIn("native_message_join_unavailable", packet["gaps"])

    def test_source_replacement_rejects_old_message_refs(self):
        path = self.transcript()
        self.hook(path)
        packet = self.prepared()
        path.rename(path.with_suffix(".old"))
        self.transcript()
        self.assertEqual(ingest(self.store, packet["attempt"], self.analysis(packet))["reason"], "freshness_unconfirmed")

    def test_late_native_message_invalidates_old_analysis(self):
        path = self.transcript()
        self.hook(path)
        packet = self.prepared()
        with path.open("a") as stream:
            stream.write(json.dumps({"type": "response_item", "payload": {"type": "message", "role": "user", "content": [{"type": "input_text", "text": "The requirement changed only now."}]}}) + "\n")
        self.assertEqual(ingest(self.store, packet["attempt"], self.analysis(packet))["reason"], "freshness_unconfirmed")

    def test_first_locator_arriving_after_prepare_is_ingested_before_ready(self):
        self.append()
        packet = self.prepared()
        self.assertFalse(any(r["ref"].startswith("message:") for r in packet["references"]))
        path = self.transcript()
        self.hook(path)
        response = ingest(self.store, packet["attempt"], self.analysis(packet, "candidate"))
        self.assertEqual(response["reason"], "freshness_unconfirmed")
        self.assertEqual(self.store.db.execute("SELECT COUNT(*) FROM sources WHERE kind='transcript'").fetchone()[0], 1)

    def test_secret_role_and_injection_filters(self):
        path = self.transcript()
        rows = [
            {"type": "response_item", "payload": {"type": "message", "role": "system", "content": [{"type": "input_text", "text": "forbidden"}]}},
            {"type": "response_item", "payload": {"type": "message", "role": "user", "content": [{"type": "input_text", "text": "password=synthetic-do-not-export"}]}},
            {"type": "response_item", "payload": {"type": "function_call_output", "role": "assistant", "content": [{"type": "output_text", "text": "raw tool content"}]}}
        ]
        with path.open("a") as stream:
            stream.write("".join(json.dumps(row) + "\n" for row in rows))
        self.hook(path)
        packet = self.prepared()
        value = json.dumps(packet)
        for forbidden in ("synthetic-do-not-export", "raw tool content", "forbidden"):
            self.assertNotIn(forbidden, value)

    def test_symlink_root_and_late_old_generation_locator_rejected(self):
        path = self.transcript()
        alias = self.transcripts / "alias.jsonl"
        alias.symlink_to(path)
        self.hook(alias)
        self.assertFalse(locator_path(self.store, "test").exists())
        self.hook(path)
        old = locator_path(self.store, "test").read_bytes()
        self.revoke()
        locator_path(self.store, "test").write_bytes(old)
        from scripts.rsi.control import recover
        recover(self.store)
        self.assertFalse(locator_path(self.store, "test").exists())
        self.assertEqual(self.store.db.execute("SELECT COUNT(*) FROM sources WHERE kind='transcript'").fetchone()[0], 0)
