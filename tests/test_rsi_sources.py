import json
import os
from unittest import mock

from scripts.rsi.sources import coverage, intake
from scripts.rsi.schema import RSIError
from tests.rsi_support import RSITestCase


class SourcesTests(RSITestCase):
    def count(self):
        return self.store.db.execute("SELECT COUNT(*) FROM facts").fetchone()[0]

    def test_positions_are_distinct_and_stable_native_replay_is_idempotent(self):
        self.append()
        self.append()
        intake(self.store, "test")
        self.assertEqual(self.count(), 2)
        intake(self.store, "test")
        self.assertEqual(self.count(), 2)
        stable = self.event(tool_use_id="inv1", source_event_sha256="a" * 64)
        self.append(stable)
        self.append(stable)
        intake(self.store, "test")
        self.assertEqual(self.count(), 3)
        self.append(self.event(tool_use_id="inv2", source_event_sha256="a" * 64))
        intake(self.store, "test")
        self.assertEqual(self.count(), 4)

    def test_half_line_cursor_and_atomic_rollback(self):
        path = self.append()
        path.write_bytes(json.dumps(self.event()).encode())
        intake(self.store, "test")
        self.assertEqual(self.count(), 0)
        self.assertEqual(self.store.db.execute("SELECT offset FROM sources WHERE kind='telemetry'").fetchone()[0], 0)
        with path.open("ab") as stream:
            stream.write(b"\n")
        with mock.patch("scripts.rsi.sources.put_work", side_effect=RuntimeError("synthetic crash")):
            with self.assertRaises(RuntimeError):
                intake(self.store, "test")
        self.assertEqual(self.count(), 0)
        self.assertEqual(self.store.db.execute("SELECT offset FROM sources WHERE kind='telemetry'").fetchone()[0], 0)
        intake(self.store, "test")
        self.assertEqual(self.count(), 1)

    def test_rotation_truncation_and_missing_record_gap(self):
        path = self.append()
        intake(self.store, "test")
        path.unlink()
        self.assertFalse(intake(self.store, "test"))
        self.append(self.event(tool_response_exit_code=1))
        intake(self.store, "test")
        self.assertEqual(self.count(), 2)
        self.assertTrue(self.store.db.execute("SELECT reason FROM diagnostics WHERE reason LIKE 'source_gap%'").fetchone())

    def test_oversized_record_skips_and_other_source_continues(self):
        path = self.append()
        path.write_bytes(b"x" * (1100000) + b"\n" + json.dumps(self.event()).encode() + b"\n")
        self.append(self.event("t2"), turn="t2")
        intake(self.store, "test")
        source = self.store.db.execute("SELECT * FROM sources WHERE path=?", (str(path),)).fetchone()
        self.assertEqual(source["skipping"], 1)
        self.assertGreater(source["offset"], 65536)
        self.clock[0] += 86400
        intake(self.store, "test")
        self.assertEqual(self.count(), 2)
        self.assertEqual(self.store.db.execute("SELECT skipping FROM sources WHERE path=?", (str(path),)).fetchone()[0], 0)

    def test_coverage_only_current_and_native_identity_preserved(self):
        self.append(self.event(tool_response_status="completed", tool_response_exit_code=5))
        self.snapshot()
        intake(self.store, "test")
        body = json.loads(self.store.db.execute("SELECT body FROM facts").fetchone()[0])
        self.assertEqual((body["completion"], body["exit_code"]), ("completed", 5))
        path = self.telemetry / "s1/t1/coverage.json"
        self.assertEqual(coverage(path)["counts"]["unique_event_count"], 1)
        self.snapshot("stale")
        self.assertNotIn("counts", coverage(path))
        path.write_text('{"unique_event_count": 99}')
        self.assertEqual(coverage(path)["snapshot_status"], "legacy")
        path.write_text("broken")
        self.assertEqual(coverage(path)["snapshot_status"], "invalid")

    def test_coverage_budget_short_read_is_not_invalid_content(self):
        from scripts.rsi.security import ReadMeter
        self.snapshot()
        path = self.telemetry / "s1/t1/coverage.json"
        for limit in (0, 10):
            value = coverage(path, ReadMeter(self.store, "test", limit))
            self.assertEqual(value["snapshot_status"], "unavailable")
            self.assertEqual(value["reason"], "read_budget_exhausted")
            self.assertNotIn("counts", value)
        self.assertEqual(coverage(path)["snapshot_status"], "current")

    def test_snapshots_read_shared_coverage_once(self):
        from scripts.rsi.engine import snapshots
        from scripts.rsi.security import ReadMeter
        for name in ("tool-events.jsonl", "permission-events.jsonl", "prompt-events.jsonl", "stop-events.jsonl", "prompt-metadata.json", "final-metadata.json"):
            self.append(name=name)
        self.snapshot(padding="x" * 7400)
        intake(self.store, "test")
        wid = self.store.db.execute("SELECT id FROM work LIMIT 1").fetchone()[0]
        meter = ReadMeter(self.store, "test", 32768)
        values = snapshots(self.store, wid, meter=meter)
        self.assertEqual(len(values), 6)
        self.assertTrue(all(v["snapshot_status"] == "current" for v in values.values()))
        self.assertEqual(meter.used, (self.telemetry / "s1/t1/coverage.json").stat().st_size)

    def test_file_signature_short_read_never_becomes_empty_anchor(self):
        from scripts.rsi.sources import file_signature
        from scripts.rsi.security import ReadMeter
        path = self.append()
        meter = ReadMeter(self.store, "test", 10)
        with path.open("rb") as stream, self.assertRaisesRegex(RSIError, "read_budget_exhausted"):
            file_signature(meter.wrap(stream), path.stat().st_size)
        self.assertEqual(meter.used, 10)

    def test_shared_meter_charges_once_and_keeps_failed_read_allocation(self):
        import io
        from scripts.rsi.security import ReadMeter
        phase = ReadMeter(self.store, "test", 60)
        first, second = phase.child(40), phase.child(60)
        before = self.store.usage("test")["bytes"]
        self.assertEqual(len(first.read(io.BytesIO(b"x" * 80), 40)), 40)
        self.assertEqual(len(second.read(io.BytesIO(b"x" * 80), 60)), 20)
        with self.assertRaisesRegex(RSIError, "read_budget_exhausted"):
            second.read(io.BytesIO(b"x"), 1)
        self.assertEqual((phase.used, first.used, second.used), (60, 40, 20))
        self.assertEqual(self.store.usage("test")["bytes"] - before, 60)
        phase = ReadMeter(self.store, "test", 20)
        child = phase.child(10)
        stream = mock.Mock(read=mock.Mock(side_effect=OSError("synthetic mid-read failure")))
        before = self.store.usage("test")["bytes"]
        with self.assertRaises(OSError):
            child.read(stream, 10)
        self.assertEqual((phase.used, child.used), (10, 10))
        self.assertEqual(self.store.usage("test")["bytes"] - before, 10)

    def test_unresolved_and_legacy_special_directories(self):
        self.append(self.event(None), turn=None, name="prompt-events.jsonl")
        self.append(self.event("Bad/ID"), turn="legacyhash")
        intake(self.store, "test")
        self.assertEqual(self.count(), 1)
        body = json.loads(self.store.db.execute("SELECT body FROM facts").fetchone()[0])
        self.assertEqual(body["association"], "capture_time_only_unverified")
        self.assertIsNone(body["turn_id"])

    def test_metadata_only_and_unknown_source_do_not_mean_success(self):
        self.policy["profile"] = "metadata_only"
        self.policy["semantic_source_locator"] = False
        self.enable("enable-metadata")
        self.append({"schema_version": "unsupported"})
        from scripts.rsi.engine import prepare
        response = prepare(self.store, "test")
        self.assertEqual(response["reason"], "metadata_only")
        self.assertEqual(response["coverage"]["status"], "degraded")

    def test_scope_binding_and_symlink_rejected(self):
        self.policy["assets"][0]["path"] = str(self.root / "link")
        (self.root / "link").symlink_to(self.asset)
        with self.assertRaisesRegex(RSIError, "symlink_denied"):
            self.enable("bad-link")

    def test_default_forward_boundary_rejects_old_or_unknown_event_time(self):
        del self.policy["sources"][0]["backfill_from"]
        self.enable("forward-only")
        self.append(self.event(observed_at_ns=int((self.clock[0] - 86400) * 1e9)))
        self.append(self.event(observed_at_ns=int((self.clock[0] + 1) * 1e9)))
        self.append(self.event())
        intake(self.store, "test")
        self.assertEqual(self.count(), 1)
        self.assertTrue(self.store.db.execute("SELECT reason FROM diagnostics WHERE reason='historical_boundary_unknown'").fetchone())

    def test_one_remaining_byte_and_rollback_cannot_refund_reads(self):
        self.append()
        intake(self.store, "test")
        with self.store.tx():
            self.store.charge("test", bytes=1048575-self.store.usage("test")["bytes"])
        self.assertFalse(intake(self.store, "test", freshness=True))
        self.assertEqual(self.store.usage("test")["bytes"], 1048575)
        self.clock[0] += 86400
        self.append()
        before = self.store.usage("test")["bytes"]
        with mock.patch("scripts.rsi.sources.put_work", side_effect=RuntimeError("after actual read")):
            with self.assertRaises(RuntimeError):
                intake(self.store, "test")
        self.assertGreater(self.store.usage("test")["bytes"], before)

    def test_forward_policy_update_replaces_old_source_authorization(self):
        path = self.append(self.event(created_at="2000-01-01T00:00:00Z"))
        path.write_bytes(path.read_bytes().rstrip(b"\n"))
        intake(self.store, "test")
        self.assertEqual(self.count(), 0)
        del self.policy["sources"][0]["backfill_from"]
        self.enable("remove-backfill")
        with path.open("ab") as stream:
            stream.write(b"\n")
        intake(self.store, "test")
        self.assertEqual(self.count(), 0)
        source = self.store.db.execute("SELECT config FROM sources WHERE kind='telemetry'").fetchone()
        self.assertEqual(json.loads(source["config"])["policy_generation"], 2)
        self.assertNotIn("backfill_from", json.loads(source["config"]))

    def test_expiry_recovers_physical_capacity_with_cursors_preserved(self):
        from scripts.rsi.control import recover
        self.policy["budgets"].update(capacity_bytes=600000, facts_days=1, derived_days=1)
        self.enable("small-capacity")
        for i in range(200):
            self.append(self.event(f"turn-{i}"), turn=f"turn-{i}")
        intake(self.store, "test")
        before = self.store.size()
        preserved = self.count()
        self.assertGreaterEqual(before, 480000)
        self.clock[0] += 86401
        recover(self.store)
        self.assertLess(self.store.size(), before)
        self.assertLess(self.store.size(), 480000)
        self.assertEqual(self.count(), 0)
        self.assertTrue(self.store.db.execute("SELECT id FROM sources WHERE offset>0").fetchone())
        self.assertEqual(self.store.db.execute("SELECT COUNT(*) FROM facts WHERE body IS NOT NULL").fetchone()[0], 0)
        self.append(self.event("new-turn"), turn="new-turn")
        intake(self.store, "test")
        self.assertGreater(self.count(), 0)
