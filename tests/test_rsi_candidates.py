import json
from concurrent.futures import ThreadPoolExecutor
from unittest import mock

from scripts.rsi.control import recover
from scripts.rsi.engine import ingest, prepare, status
from scripts.rsi.schema import RSIError
from scripts.rsi.sources import intake
from tests.rsi_support import RSITestCase
from scripts.rsi.store import Store


class CandidateTests(RSITestCase):
    def test_official_candidate_roundtrip_idempotence_and_no_decision(self):
        self.official()
        packet = self.prepared()
        analysis = self.analysis(packet, "candidate")
        response = ingest(self.store, packet["attempt"], analysis)
        self.assertEqual(response["reason"], "candidate")
        self.assertEqual(status(self.store, "test")["candidates"][0]["state"], "ready")
        self.assertTrue(ingest(self.store, packet["attempt"], analysis)["replay"])
        self.assertEqual(self.store.db.execute("SELECT COUNT(*) FROM candidates").fetchone()[0], 1)
        analysis["assessment"] = "changed"
        with self.assertRaisesRegex(RSIError, "idempotency_conflict"):
            ingest(self.store, packet["attempt"], analysis)

    def test_busy_late_evidence_and_stale_coverage(self):
        self.append()
        self.snapshot()
        packet = self.prepared()
        self.assertEqual(prepare(self.store, "test")["reason"], "busy")
        self.snapshot("stale", snapshot_id="snap2")
        response = ingest(self.store, packet["attempt"], self.analysis(packet))
        self.assertEqual(response["reason"], "freshness_unconfirmed")
        self.assertEqual(self.store.db.execute("SELECT COUNT(*) FROM candidates").fetchone()[0], 0)

    def test_late_evidence_supersedes_analysis_without_stale_counts(self):
        self.append()
        packet = self.prepared()
        self.append(self.event(tool_response_exit_code=1))
        response = ingest(self.store, packet["attempt"], self.analysis(packet))
        self.assertEqual(response["reason"], "superseded")

    def test_revoke_after_resolution_before_publish_blocks_all_body(self):
        self.append()
        prepare(self.store, "test")
        self.clock[0] += 2
        output = []
        with self.assertRaisesRegex(RSIError, "policy_inactive"):
            prepare(self.store, "test", publisher=output.append, before_publish=self.revoke)
        self.assertEqual(output, [])
        response = status(self.store, "test")
        self.assertEqual(response["consumer"], "disabled")
        self.assertNotIn("candidates", response)

    def test_revoke_recovery_phases_and_old_attempt(self):
        self.append()
        packet = self.prepared()
        with mock.patch("scripts.rsi.control.project_projection", side_effect=OSError("synthetic fault")):
            response = self.revoke()
            self.assertEqual(response["reason"], "policy_revoking")
            self.assertEqual(response["consumer"], "disabled")
            self.assertEqual(response["locator_projection"], "pending")
        generation = response["generation"]
        recover(self.store)
        response = status(self.store, "test")
        self.assertEqual(response["generation"], generation)
        self.assertEqual(response["reason"], "policy_revoked")
        with self.assertRaises(RSIError):
            ingest(self.store, packet["attempt"], self.analysis(packet))

    def test_revoke_completes_when_unpublished_output_parent_is_absent(self):
        output = self.store.root / "views/packet.json"
        response = prepare(self.store, "test", output=str(output))
        self.assertEqual(response["reason"], "degraded")
        self.assertFalse(output.parent.exists())
        self.assertEqual(self.store.db.execute("SELECT COUNT(*) FROM exports").fetchone()[0], 1)
        response = self.revoke()
        self.assertEqual(response["reason"], "policy_revoked")
        self.assertEqual(response["consumer"], "disabled")
        self.assertEqual(response["locator_projection"], "disabled")
        self.assertEqual(response["cleanup"], "complete")
        self.assertEqual(self.store.db.execute("SELECT COUNT(*) FROM exports").fetchone()[0], 0)
        self.assertFalse(output.parent.exists())

    def test_revoke_retains_pending_cleanup_on_output_permission_error(self):
        from scripts.rsi.security import parent_fd
        output = self.store.root / "views/packet.json"
        prepare(self.store, "test", output=str(output))
        def guarded_parent(path, create=False):
            if path == output:
                raise PermissionError("synthetic denied")
            return parent_fd(path, create=create)
        with mock.patch("scripts.rsi.security.parent_fd", side_effect=guarded_parent):
            response = self.revoke()
        self.assertEqual(response["reason"], "policy_revoking")
        self.assertEqual(response["consumer"], "disabled")
        self.assertEqual(response["locator_projection"], "disabled")
        self.assertEqual(response["cleanup"], "pending")
        recover(self.store)
        self.assertEqual(status(self.store, "test")["reason"], "policy_revoked")

    def test_analysis_rejects_privilege_and_unregistered_refs(self):
        self.official()
        packet = self.prepared()
        analysis = self.analysis(packet)
        analysis["accepted"] = True
        with self.assertRaisesRegex(RSIError, "unexpected_fields"):
            ingest(self.store, packet["attempt"], analysis)
        del analysis["accepted"]
        analysis["references"][0]["ref"] = "/tmp/secret"
        with self.assertRaisesRegex(RSIError, "invalid_reference"):
            ingest(self.store, packet["attempt"], analysis)
        self.assertEqual(self.store.db.execute("SELECT state FROM attempts").fetchone()[0], "invalid")

    def test_policy_shrink_denies_previous_body(self):
        self.official()
        packet = self.prepared()
        ingest(self.store, packet["attempt"], self.analysis(packet, "candidate"))
        self.policy.update(profile="metadata_only", assets=[], sources=[], transcript_roots=[], semantic_source_locator=False)
        self.enable("shrink")
        response = status(self.store, "test")
        self.assertTrue(all(item["body"] is None for item in response["candidates"]))
        self.assertTrue(all(row[0] is None for row in self.store.db.execute("SELECT packet FROM attempts")))

    def test_expiry_removes_views_and_does_not_refill(self):
        self.official()
        prepare(self.store, "test")
        self.clock[0] += 2
        view = self.store.root / "views/packet.json"
        packet = prepare(self.store, "test", output=view)["packet"]
        response = ingest(self.store, packet["attempt"], self.analysis(packet, "candidate"))
        self.assertTrue(view.exists())
        self.clock[0] += 8 * 86400
        recover(self.store)
        self.assertFalse(view.exists())
        self.assertIsNone(status(self.store, "test")["candidates"][0]["body"])
        self.assertNotEqual(prepare(self.store, "test")["reason"], "prepared")

    def test_source_snapshot_body_has_no_indefinite_copy(self):
        self.official()
        self.clock[0] += 15 * 86400
        recover(self.store)
        config = json.loads(self.store.db.execute("SELECT config FROM sources WHERE kind='official'").fetchone()[0])
        self.assertNotIn("notes", config)
        self.assertNotIn("question", config)
        self.assertLessEqual(config["expires_at"], self.clock[0])

    def test_capacity_leaves_feedback_and_revocation_available(self):
        self.append()
        with mock.patch.object(self.store, "size", return_value=100 * 1024 * 1024):
            self.assertEqual(prepare(self.store, "test")["reason"], "degraded")
            self.assertEqual(self.revoke()["consumer"], "disabled")

    def test_bounded_supplement_fetches_requested_asset_lines(self):
        self.asset.write_text("first line\n" + "normal line\n" * 400 + "requested final line\n")
        self.official()
        packet = self.prepared()
        analysis = self.analysis(packet, "evidence_request")
        analysis["requests"] = [{"ref": "asset:rule", "start_line": 402, "line_count": 1}]
        self.assertEqual(ingest(self.store, packet["attempt"], analysis)["reason"], "evidence_request")
        self.clock[0] += 2
        followup = prepare(self.store, "test")["packet"]
        self.assertEqual(followup["references"][0]["text"], "requested final line\n")
        self.assertEqual(self.store.usage("test")["packets"], 2)

    def test_rejected_secret_reads_still_consume_daily_bytes(self):
        self.policy["assets"] = []
        for i in range(20):
            path = self.root / f"asset-{i}.md"
            path.write_text("password=synthetic\n" + "x" * 60000)
            self.policy["assets"].append({"id": f"asset-{i}", "path": str(path)})
        self.enable("many-assets")
        self.append()
        prepare(self.store, "test")
        self.clock[0] += 2
        response = prepare(self.store, "test")
        usage = self.store.usage("test")
        self.assertGreater(usage["bytes"], 800000)
        self.assertLessEqual(usage["bytes"], 1024 * 1024)
        self.assertEqual(response["reason"], "limit")
        self.assertNotIn("packet", response)
        self.assertEqual(usage["reserved"], 0)

    def test_concurrent_prepare_has_one_lease_and_repeated_busy_costs_no_intake(self):
        self.append()
        prepare(self.store, "test")
        self.clock[0] += 2
        def run():
            store = Store(self.root, clock=lambda: self.clock[0])
            try:
                return prepare(store, "test")["reason"]
            finally:
                store.close()
        with ThreadPoolExecutor(max_workers=2) as executor:
            outcomes = list(executor.map(lambda _: run(), range(2)))
        self.assertEqual(sorted(outcomes), ["busy", "prepared"])
        usage = dict(self.store.usage("test"))
        self.assertEqual(prepare(self.store, "test")["reason"], "busy")
        self.assertEqual(dict(self.store.usage("test")), usage)

    def test_expired_claim_reallocates_and_rejects_old_result(self):
        self.official()
        packet = self.prepared()
        self.clock[0] += 1201
        next_packet = prepare(self.store, "test")["packet"]
        self.assertNotEqual(packet["attempt"], next_packet["attempt"])
        self.assertEqual(self.store.usage("test")["packets"], 2)
        with self.assertRaisesRegex(RSIError, "lease_expired_or_superseded"):
            ingest(self.store, packet["attempt"], self.analysis(packet))

    def test_new_file_same_native_turn_is_checked_for_late_evidence(self):
        self.append()
        packet = self.prepared()
        self.append(self.event(), name="permission-events.jsonl")
        response = ingest(self.store, packet["attempt"], self.analysis(packet))
        self.assertIn(response["reason"], {"superseded", "freshness_unconfirmed"})

    def test_failed_final_freshness_read_keeps_durable_charge(self):
        from scripts.rsi.security import ReadMeter
        self.append()
        self.snapshot()
        prepare(self.store, "test")
        self.clock[0] += 2
        actual = [0]
        original = ReadMeter.read
        def tracked(meter, *args, **kwargs):
            data = original(meter, *args, **kwargs)
            actual[0] += len(data)
            return data
        before = self.store.usage("test")["bytes"]
        with mock.patch.object(ReadMeter, "read", tracked):
            response = prepare(self.store, "test", before_publish=lambda: self.snapshot("stale"))
        self.assertEqual(response["reason"], "degraded")
        self.assertEqual(response["gaps"], ["coverage_changed"])
        self.assertNotIn("packet", response)
        self.assertEqual(self.store.usage("test")["reserved"], 0)
        self.assertEqual(self.store.usage("test")["bytes"] - before, actual[0])

    def test_final_snapshot_budget_loss_defers_without_invalid_packet(self):
        self.append()
        self.snapshot()
        prepare(self.store, "test")
        self.clock[0] += 2
        def consume_available():
            with self.store.tx():
                usage = self.store.usage("test")
                self.store.charge("test", bytes=1048576 - usage["bytes"] - usage["reserved"])
        response = prepare(self.store, "test", before_publish=consume_available)
        self.assertEqual(response["reason"], "limit")
        self.assertEqual(response["gaps"], ["read_budget_exhausted"])
        self.assertNotIn("packet", response)
        self.assertEqual(self.store.usage("test")["reserved"], 0)
        self.assertIsNone(self.store.db.execute("SELECT packet FROM attempts").fetchone()[0])

    def test_normal_counterexamples_do_not_become_programmatic_defects(self):
        # These are mechanical outcomes only; they do not evaluate a real model's classification.
        self.append(self.event(tool_response_exit_code=1, tool_response_status="failed"))
        packet = self.prepared()
        for label in ("normal_self_repair", "later_requirement", "external_recovery", "missing_post", "expected_red_test", "family_not_independent"):
            self.assertIn(label, packet["analysis_contract"]["required_counterexamples"])
        response = ingest(self.store, packet["attempt"], self.analysis(packet))
        self.assertEqual(response["reason"], "not_candidate")
        self.assertEqual(self.store.db.execute("SELECT COUNT(*) FROM candidates").fetchone()[0], 0)
