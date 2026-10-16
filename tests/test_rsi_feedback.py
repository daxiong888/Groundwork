import json
from pathlib import Path
import tempfile
import unittest

from scripts.rsi.feedback import EXECUTION_SCHEMA, handle_feedback
from scripts.rsi.schema import RSIError, canonical, digest
from scripts.rsi.store import Store


NOW = 2_000_000_000.0


class FeedbackTest(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(dir="/private/tmp")
        self.project = Path(self.temporary.name)
        self.target = self.project / "target.md"
        self.execution = self.project / "execution.json"
        self.tool_output = self.project / "tool.out"
        self.trial = self.project / "trial.json"
        self.target.write_bytes(b"A\n")
        self.execution.write_text("{}", encoding="utf-8")
        self.tool_output.write_bytes(b"PASS\n")
        self.trial.write_bytes(b'{"result":"candidate-direction"}\n')
        self.store = Store(self.project, clock=lambda: NOW)
        self.scope = "scope-1"
        self.candidate = "candidate-1"
        self.baseline = digest(b"A\n")
        self.body = {
            "trigger": "event_observation",
            "problem": "A bounded synthetic problem",
            "facts": [{"ref": "fact-1"}],
            "inferences": ["The current rule may be too broad"],
            "applicable_requirement": "Keep the rule bounded",
            "actual_outcome": "A synthetic outcome",
            "unknowns": [],
            "counterevidence": [],
            "normal_explanation": "The current behavior could be intentional",
            "target": {
                "asset_id": "target",
                "location": "rule",
                "owner": "maintainer",
                "baseline_digest": self.baseline,
            },
            "action": "narrow",
            "change": "Narrow one rule",
            "mechanism": "Avoid the synthetic false positive",
            "acceptance": [{"id": "ac-1", "description": "The focused check passes"}],
            "counterexamples": ["A normal retry"],
            "cost": "small",
            "risk": "low",
            "rollback": "Restore A",
            "behavior_evidence_required": False,
        }
        self.proposal = digest(self.body)
        self.policy = {
            "expires_at": NOW + 3600,
            "budgets": {"facts_days": 14, "capacity_bytes": 1024 * 1024},
            "assets": [
                {"id": "target", "path": str(self.target)},
                {"id": "execution-receipt", "path": str(self.execution)},
                {"id": "tool-output", "path": str(self.tool_output)},
                {"id": "trial-receipt", "path": str(self.trial)},
            ],
            "sources": [],
        }
        with self.store.tx() as db:
            db.execute(
                "INSERT INTO scopes(id,generation,state,policy,created,updated,projection,cleanup) "
                "VALUES(?,?,?,?,?,?,?,?)",
                (self.scope, 1, "active", canonical(self.policy), NOW, NOW, "active", "pending"),
            )
            db.execute(
                "INSERT INTO work(id,scope,kind,revision,state,updated,body,expires) VALUES(?,?,?,?,?,?,?,?)",
                ("work-1", self.scope, "event_observation", 1, "done", NOW, canonical({"fact": "fact-1"}), NOW + 3600),
            )
            self._insert_candidate(db)

    def tearDown(self):
        self.store.close()
        self.temporary.cleanup()

    def _insert_candidate(self, db, *, revision=1, state="ready", expires=None):
        db.execute(
            "INSERT INTO candidates(id,scope,merge_key,revision,state,proposal_digest,body,work_id,"
            "evidence_revision,created,updated,expires) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)",
            (
                self.candidate, self.scope, "merge-1", revision, state, self.proposal,
                canonical(self.body), "work-1", 1, NOW, NOW,
                NOW + 3600 if expires is None else expires,
            ),
        )

    def _origin(self, *, origin_id="origin-1", binding=None):
        binding = binding or digest({
            "candidate": self.candidate,
            "revision": 1,
            "proposal_digest": self.proposal,
            "scope": self.scope,
        })
        return {
            "id": origin_id,
            "source": "codex_user_interaction",
            "recorded_by": "assistant",
            "thread_ref": None,
            "message_ref": None,
            "summary": "The user accepted this candidate revision.",
            "scope": self.scope,
            "binding": binding,
        }

    def _decision(self, *, record_id="decision-1", decision="accept", origin=None):
        return {
            "id": record_id,
            "kind": "decision",
            "scope": self.scope,
            "proposal_digest": self.proposal,
            "decision": decision,
            "origin": origin or self._origin(),
        }

    def _accept(self):
        return handle_feedback(self.store, self.scope, self.candidate, 1, self._decision())

    def _common_receipt(self, record_id, receipt_format):
        return {
            "id": record_id,
            "kind": "receipt",
            "scope": self.scope,
            "candidate": self.candidate,
            "revision": 1,
            "proposal_digest": self.proposal,
            "format": receipt_format,
            "decision_id": "decision-1",
        }

    def _start(self, current_digest, *, record_id="start-1"):
        record = self._common_receipt(record_id, "implementation_start")
        record.update({"baseline_digest": self.baseline, "current_digest": current_digest})
        return handle_feedback(self.store, self.scope, self.candidate, 1, record)

    def _implementation(self, actual_digest, *, start_id="start-1", record_id="implementation-1"):
        record = self._common_receipt(record_id, "implementation")
        record.update({
            "baseline_digest": self.baseline,
            "actual_digest": actual_digest,
            "start_id": start_id,
        })
        return handle_feedback(self.store, self.scope, self.candidate, 1, record)

    def _write_execution(self, kind, result_digest, *, invocation_id, check_id, exit_code=0,
                         evidence_class="source_check", acceptance_id=None, layer=None,
                         artifact_digest=None, event_ref=None, trigger_matched=None,
                         effective_layer=None, effective_digest=None, output_digest=None):
        receipt = {
            "schema": EXECUTION_SCHEMA,
            "kind": kind,
            "execution_source": "codex_tool",
            "invocation_id": invocation_id,
            "check_id": check_id,
            "result_digest": result_digest,
            "exit_code": exit_code,
            "evidence_class": evidence_class,
            "output": {
                "asset_id": "tool-output",
                "digest": output_digest or digest(self.tool_output.read_bytes()),
            },
        }
        if kind == "check":
            receipt["acceptance_id"] = acceptance_id
        elif kind == "adoption":
            receipt.update({"layer": layer, "artifact_digest": artifact_digest})
        else:
            receipt.update({
                "event_ref": event_ref,
                "trigger_matched": trigger_matched,
                "effective_layer": effective_layer,
                "effective_digest": effective_digest,
            })
        self.execution.write_text(canonical(receipt), encoding="utf-8")
        return receipt

    def _check_record(self, result_digest, *, record_id="check-1", exit_code=0,
                      evidence_class="source_check", output_digest=None):
        invocation_id = "invocation-" + record_id
        self._write_execution(
            "check", result_digest, invocation_id=invocation_id, check_id="focused-check",
            exit_code=exit_code, evidence_class=evidence_class, acceptance_id="ac-1",
            output_digest=output_digest,
        )
        record = self._common_receipt(record_id, "check")
        record.update({
            "result_digest": result_digest,
            "acceptance_id": "ac-1",
            "check_id": "focused-check",
            "execution_source": "codex_tool",
            "invocation_id": invocation_id,
            "output_asset_id": "execution-receipt",
        })
        return record

    def _check(self, result_digest, **options):
        record = self._check_record(result_digest, **options)
        return handle_feedback(self.store, self.scope, self.candidate, 1, record)

    def _adoption_record(self, result_digest, layer, artifact_digest, *, record_id, exit_code=0):
        invocation_id = "invocation-" + record_id
        check_id = layer + "-identity-check"
        self._write_execution(
            "adoption", result_digest, invocation_id=invocation_id, check_id=check_id,
            exit_code=exit_code, evidence_class="adoption", layer=layer,
            artifact_digest=artifact_digest,
        )
        record = self._common_receipt(record_id, "adoption")
        record.update({
            "result_digest": result_digest,
            "layer": layer,
            "artifact_digest": artifact_digest,
            "check_id": check_id,
            "execution_source": "codex_tool",
            "invocation_id": invocation_id,
            "output_asset_id": "execution-receipt",
        })
        return record

    def _adoption(self, result_digest, layer, artifact_digest, *, record_id, exit_code=0):
        record = self._adoption_record(
            result_digest, layer, artifact_digest, record_id=record_id, exit_code=exit_code,
        )
        return handle_feedback(self.store, self.scope, self.candidate, 1, record)

    def _recurrence_record(self, result_digest, event_ref, *, record_id,
                           trigger_matched, effective_layer, effective_digest, exit_code=0):
        invocation_id = "invocation-" + record_id
        self._write_execution(
            "recurrence", result_digest, invocation_id=invocation_id,
            check_id="recurrence-binding-check", exit_code=exit_code,
            evidence_class="recurrence", event_ref=event_ref,
            trigger_matched=trigger_matched, effective_layer=effective_layer,
            effective_digest=effective_digest,
        )
        record = self._common_receipt(record_id, "recurrence")
        record.update({
            "result_digest": result_digest,
            "event_ref": event_ref,
            "check_id": "recurrence-binding-check",
            "execution_source": "codex_tool",
            "invocation_id": invocation_id,
            "output_asset_id": "execution-receipt",
        })
        return record

    def _implemented_b(self):
        self._accept()
        start = self._start(self.baseline)
        self.assertEqual("implementation_started", start["reason"])
        self.target.write_bytes(b"B\n")
        result_digest = digest(b"B\n")
        response = self._implementation(result_digest)
        self.assertEqual("validating", response["state"])
        return result_digest

    def _watching_b(self):
        result_digest = self._implemented_b()
        self._check(result_digest)
        loaded = digest(b"loaded-B")
        response = self._adoption(result_digest, "loaded", loaded, record_id="adoption-loaded")
        self.assertEqual("watching", response["state"])
        return result_digest, loaded

    def _fact(self, fact_id, body, *, expires=None):
        with self.store.tx() as db:
            db.execute(
                "INSERT INTO facts(id,scope,source,generation,position,identity,fingerprint,work_id,body,created,expires) "
                "VALUES(?,?,?,?,?,?,?,?,?,?,?)",
                (
                    fact_id, self.scope, "synthetic-source", "generation-1", fact_id, fact_id,
                    digest(body), None, canonical(body), NOW, NOW + 3600 if expires is None else expires,
                ),
            )

    def _write_trial_slot(self, change_digest, expectation_digest, model, *, cleanup_ok=True):
        attempt = {
            "run_id": "run-1",
            "slot_id": "slot-1",
            "arm": "candidate",
            "project": "project-1",
            "model_dispatches": 1,
            "valid": cleanup_ok,
            "failure_code": None if cleanup_ok else "cleanup_incomplete",
            "cleanup_ok": cleanup_ok,
            "cleanup_errors": [] if cleanup_ok else ["attempt_workspace_remains"],
            "bindings": {
                "package_sha256": change_digest,
                "rubric_sha256": expectation_digest,
                "actor": {"model": model},
            },
        }
        attempt["receipt_sha256"] = digest(attempt)
        slot = {
            "record_type": "slot_result",
            "evidence_class": "candidate_direction",
            "run_id": "run-1",
            "slot_id": "slot-1",
            "arm": "candidate",
            "valid": cleanup_ok,
            "valid_attempt_receipt_hash": attempt["receipt_sha256"] if cleanup_ok else None,
            "attempt": attempt,
        }
        raw = (canonical(slot) + "\n").encode("utf-8")
        self.trial.write_bytes(raw)
        return digest(raw)

    def test_decision_origin_idempotency_and_bounded_coverage(self):
        record = self._decision()
        first = handle_feedback(self.store, self.scope, self.candidate, 1, record)
        second = handle_feedback(self.store, self.scope, self.candidate, 1, record)
        self.assertEqual(first, second)
        self.assertEqual("accepted", first["state"])
        self.assertEqual("candidate_feedback", first["coverage"]["scope"])
        self.assertEqual(self.candidate, first["coverage"]["candidate"])

        conflicting = json.loads(json.dumps(record))
        conflicting["origin"]["summary"] = "A different summary."
        with self.assertRaisesRegex(RSIError, "idempotency_conflict"):
            handle_feedback(self.store, self.scope, self.candidate, 1, conflicting)

    def test_scope_candidate_and_origin_are_rechecked(self):
        with self.assertRaisesRegex(RSIError, "decision_binding_mismatch"):
            handle_feedback(
                self.store, self.scope, self.candidate, 1,
                self._decision(origin=self._origin(binding=digest({"wrong": True}))),
            )
        with self.store.tx() as db:
            db.execute("UPDATE candidates SET expires=? WHERE id=?", (NOW - 1, self.candidate))
        with self.assertRaisesRegex(RSIError, "candidate_expired"):
            self._accept()

    def test_scope_expiry_is_rechecked_before_idempotent_replay(self):
        record = self._decision()
        handle_feedback(self.store, self.scope, self.candidate, 1, record)
        self.policy["expires_at"] = NOW - 1
        with self.store.tx() as db:
            db.execute("UPDATE scopes SET policy=? WHERE id=?", (canonical(self.policy), self.scope))
        with self.assertRaisesRegex(RSIError, "policy_expired"):
            handle_feedback(self.store, self.scope, self.candidate, 1, record)

    def test_one_decision_per_revision_and_new_revision_can_reopen(self):
        rejected = handle_feedback(
            self.store, self.scope, self.candidate, 1, self._decision(decision="reject"),
        )
        self.assertEqual("closed", rejected["state"])
        with self.assertRaisesRegex(RSIError, "decision_already_recorded"):
            handle_feedback(
                self.store, self.scope, self.candidate, 1,
                self._decision(record_id="decision-2", origin=self._origin(origin_id="origin-2")),
            )

        revised_body = dict(self.body)
        revised_body["facts"] = [{"ref": "fact-2"}]
        revised_proposal = digest(revised_body)
        with self.store.tx() as db:
            db.execute(
                "UPDATE candidates SET revision=2,state='ready',proposal_digest=?,body=? WHERE id=?",
                (revised_proposal, canonical(revised_body), self.candidate),
            )
        origin = self._origin(binding=digest({
            "candidate": self.candidate,
            "revision": 2,
            "proposal_digest": revised_proposal,
            "scope": self.scope,
        }))
        record = self._decision(record_id="decision-2", origin=origin)
        record["proposal_digest"] = revised_proposal
        reopened = handle_feedback(self.store, self.scope, self.candidate, 2, record)
        self.assertEqual("accepted", reopened["state"])

    def test_implementation_start_detects_drift_before_write(self):
        self._accept()
        self.target.write_bytes(b"external\n")
        response = self._start(self.baseline)
        self.assertEqual("target_drift", response["reason"])
        self.assertEqual("collecting", response["state"])
        work = self.store.db.execute("SELECT state,revision FROM work WHERE id='work-1'").fetchone()
        self.assertEqual(("pending", 2), (work["state"], work["revision"]))

    def test_collecting_does_not_repopulate_expired_work(self):
        self._accept()
        with self.store.tx() as db:
            db.execute("UPDATE work SET expires=? WHERE id='work-1'", (NOW - 1,))
        self.target.write_bytes(b"external\n")
        response = self._start(self.baseline)
        self.assertEqual("collecting", response["state"])
        work = self.store.db.execute("SELECT state,revision FROM work WHERE id='work-1'").fetchone()
        self.assertEqual(("done", 1), (work["state"], work["revision"]))

    def test_collecting_does_not_repopulate_work_without_body(self):
        self._accept()
        with self.store.tx() as db:
            db.execute("UPDATE work SET body=NULL WHERE id='work-1'")
        self.target.write_bytes(b"external\n")
        response = self._start(self.baseline)
        self.assertEqual("collecting", response["state"])
        work = self.store.db.execute("SELECT state,revision FROM work WHERE id='work-1'").fetchone()
        self.assertEqual(("done", 1), (work["state"], work["revision"]))

    def test_implementation_requires_one_unused_start(self):
        self._accept()
        self.target.write_bytes(b"B\n")
        result_b = digest(b"B\n")
        with self.assertRaisesRegex(RSIError, "implementation_start_missing"):
            self._implementation(result_b, start_id="missing-start")

        self.target.write_bytes(b"A\n")
        self._start(self.baseline)
        self.target.write_bytes(b"B\n")
        self._implementation(result_b)
        self.target.write_bytes(b"B2\n")
        with self.assertRaisesRegex(RSIError, "implementation_start_used"):
            self._implementation(digest(b"B2\n"), record_id="implementation-2")

    def test_normal_b2_reuses_decision_but_invalidates_b1_evidence(self):
        result_b, _ = self._watching_b()
        self._start(result_b, record_id="start-2")
        self.target.write_bytes(b"B2\n")
        result_b2 = digest(b"B2\n")
        response = self._implementation(result_b2, start_id="start-2", record_id="implementation-2")
        self.assertEqual("validating", response["state"])
        row = self.store.db.execute("SELECT adoption FROM candidates WHERE id=?", (self.candidate,)).fetchone()
        self.assertIsNone(row["adoption"])
        with self.assertRaisesRegex(RSIError, "receipt_result_mismatch"):
            self._check(result_b, record_id="stale-b1-check")

    def test_execution_receipt_is_structured_and_all_bindings_match(self):
        result_b = self._implemented_b()
        self.execution.write_text("plain PASS", encoding="utf-8")
        record = self._common_receipt("plain-check", "check")
        record.update({
            "result_digest": result_b,
            "acceptance_id": "ac-1",
            "check_id": "focused-check",
            "execution_source": "codex_tool",
            "invocation_id": "invocation-plain",
            "output_asset_id": "execution-receipt",
        })
        with self.assertRaisesRegex(RSIError, "invalid_execution_receipt"):
            handle_feedback(self.store, self.scope, self.candidate, 1, record)

        mismatched = self._check_record(result_b, record_id="binding-mismatch")
        receipt = json.loads(self.execution.read_text(encoding="utf-8"))
        receipt["check_id"] = "different-check"
        self.execution.write_text(canonical(receipt), encoding="utf-8")
        with self.assertRaisesRegex(RSIError, "check_binding_mismatch"):
            handle_feedback(self.store, self.scope, self.candidate, 1, mismatched)

        bad_output = self._check_record(
            result_b, record_id="bad-output", output_digest=digest(b"other output\n"),
        )
        with self.assertRaisesRegex(RSIError, "execution_output_mismatch"):
            handle_feedback(self.store, self.scope, self.candidate, 1, bad_output)

        bool_exit = self._check_record(result_b, record_id="bool-exit", exit_code=True)
        with self.assertRaisesRegex(RSIError, "invalid_exit_code"):
            handle_feedback(self.store, self.scope, self.candidate, 1, bool_exit)

    def test_execution_exit_code_is_read_from_json_and_invocation_is_unique(self):
        result_b = self._implemented_b()
        failed = self._check(result_b, record_id="failed-check", exit_code=7)
        self.assertEqual(7, failed["exit_code"])
        self.assertEqual("validating", failed["state"])

        reused = self._check_record(result_b, record_id="new-record")
        reused["invocation_id"] = "invocation-failed-check"
        receipt = json.loads(self.execution.read_text(encoding="utf-8"))
        receipt["invocation_id"] = "invocation-failed-check"
        self.execution.write_text(canonical(receipt), encoding="utf-8")
        with self.assertRaisesRegex(RSIError, "execution_invocation_reused"):
            handle_feedback(self.store, self.scope, self.candidate, 1, reused)

    def test_latest_check_result_controls_state(self):
        result_b, loaded = self._watching_b()
        failed = self._check(result_b, record_id="check-latest-fail", exit_code=2)
        self.assertEqual("validating", failed["state"])
        passed = self._check(result_b, record_id="check-latest-pass")
        self.assertEqual("watching", passed["state"])
        self.assertEqual(digest(b"loaded-B"), loaded)

    def test_behavior_gate_requires_current_behavior_check(self):
        self.body["behavior_evidence_required"] = True
        self.proposal = digest(self.body)
        with self.store.tx() as db:
            db.execute("UPDATE candidates SET proposal_digest=?,body=? WHERE id=?",
                       (self.proposal, canonical(self.body), self.candidate))
        result_b = self._implemented_b()
        self._check(result_b, record_id="source-check")
        loaded = self._adoption(result_b, "loaded", digest(b"loaded-B"), record_id="adoption-loaded")
        self.assertEqual("validating", loaded["state"])
        behavior = self._check(result_b, record_id="behavior-check", evidence_class="behavior")
        self.assertEqual("watching", behavior["state"])

    def test_adoption_layers_remain_separate(self):
        result_b = self._implemented_b()
        self._check(result_b)
        source = self._adoption(result_b, "source", result_b, record_id="adoption-source")
        installed_digest = digest(b"installed-B")
        installed = self._adoption(result_b, "installed", installed_digest, record_id="adoption-installed")
        loaded_digest = digest(b"loaded-B")
        loaded = self._adoption(result_b, "loaded", loaded_digest, record_id="adoption-loaded")
        self.assertEqual("validating", source["state"])
        self.assertEqual("validating", installed["state"])
        self.assertEqual("watching", loaded["state"])
        adoption = json.loads(self.store.db.execute(
            "SELECT adoption FROM candidates WHERE id=?", (self.candidate,),
        ).fetchone()["adoption"])
        self.assertEqual({"source", "installed", "loaded"}, set(adoption["layers"]))

    def test_recurrence_requires_a_live_scope_fact_with_matching_evidence(self):
        result_b, loaded_digest = self._watching_b()
        record = self._recurrence_record(
            result_b, "missing-fact", record_id="recurrence-1",
            trigger_matched=True, effective_layer="loaded", effective_digest=loaded_digest,
        )
        with self.assertRaisesRegex(RSIError, "recurrence_fact_missing"):
            handle_feedback(self.store, self.scope, self.candidate, 1, record)

        p0_fact = {"kind": "event_observation", "completion": "unknown", "result_present": True}
        self._fact("fact-expired", p0_fact, expires=NOW - 1)
        expired = self._recurrence_record(
            result_b, "fact-expired", record_id="recurrence-expired",
            trigger_matched=True, effective_layer="loaded", effective_digest=loaded_digest,
        )
        with self.assertRaisesRegex(RSIError, "recurrence_fact_expired"):
            handle_feedback(self.store, self.scope, self.candidate, 1, expired)

        self._fact("fact-unknown", p0_fact)
        unknown = self._recurrence_record(
            result_b, "fact-unknown", record_id="recurrence-unknown",
            trigger_matched=True, effective_layer=None, effective_digest=None,
        )
        response = handle_feedback(self.store, self.scope, self.candidate, 1, unknown)
        self.assertEqual("recurrence_unattributed", response["reason"])
        self.assertEqual("watching", response["state"])

        self._fact("fact-confirmed", p0_fact)
        confirmed = self._recurrence_record(
            result_b, "fact-confirmed", record_id="recurrence-confirmed",
            trigger_matched=True, effective_layer="loaded", effective_digest=loaded_digest,
        )
        response = handle_feedback(self.store, self.scope, self.candidate, 1, confirmed)
        self.assertEqual("recurrence_confirmed", response["reason"])
        self.assertEqual("collecting", response["state"])
        work = self.store.db.execute("SELECT state,revision FROM work WHERE id='work-1'").fetchone()
        self.assertEqual(("pending", 2), (work["state"], work["revision"]))

    def test_expired_feedback_bodies_fail_closed(self):
        result_b = self._implemented_b()
        decision_body = self.store.db.execute(
            "SELECT body FROM feedback WHERE id='decision-1'",
        ).fetchone()["body"]
        with self.store.tx() as db:
            db.execute("UPDATE feedback SET body=NULL WHERE id='decision-1'")
        with self.assertRaisesRegex(RSIError, "feedback_evidence_expired"):
            self._start(result_b, record_id="start-expired-decision")
        with self.store.tx() as db:
            db.execute("UPDATE feedback SET body=? WHERE id='decision-1'", (decision_body,))

        self._check(result_b)
        with self.store.tx() as db:
            db.execute("UPDATE feedback SET body=NULL WHERE id='check-1'")
        record = self._adoption_record(result_b, "loaded", digest(b"loaded-B"), record_id="adoption-loaded")
        with self.assertRaisesRegex(RSIError, "feedback_evidence_expired"):
            handle_feedback(self.store, self.scope, self.candidate, 1, record)

    def test_asset_reads_are_bounded_and_unreferenced_assets_are_not_read(self):
        self.policy["budgets"]["capacity_bytes"] = 2
        with self.store.tx() as db:
            db.execute("UPDATE scopes SET policy=? WHERE id=?", (canonical(self.policy), self.scope))
        accepted = self._accept()
        self.assertEqual("accepted", accepted["state"])
        self._start(self.baseline)
        self.target.write_bytes(b"B is too large\n")
        with self.assertRaisesRegex(RSIError, "asset_over_limit"):
            self._implementation(digest(b"B is too large\n"))

    def test_candidate_trial_remains_an_attachment(self):
        result_b = self._implemented_b()
        change_digest = digest(b"candidate-package")
        expectation_digest = digest(b"frozen-rubric")
        model = "synthetic-model"
        receipt_digest = self._write_trial_slot(change_digest, expectation_digest, model)
        record = self._common_receipt("trial-1", "candidate_trial")
        record.update({
            "result_digest": result_b,
            "change_digest": change_digest,
            "expectation_digest": expectation_digest,
            "model": model,
            "run_id": "run-1",
            "slot_id": "slot-1",
            "receipt_asset_id": "trial-receipt",
            "receipt_digest": receipt_digest,
        })
        response = handle_feedback(self.store, self.scope, self.candidate, 1, record)
        self.assertEqual("receipt_attached", response["reason"])
        self.assertEqual("candidate_direction", response["evidence_class"])
        self.assertEqual("validating", response["state"])

        mismatched = dict(record, id="trial-model-mismatch", model="different-model")
        response = handle_feedback(self.store, self.scope, self.candidate, 1, mismatched)
        self.assertEqual("attachment_unknown", response["reason"])
        self.assertEqual("unknown", response["evidence_class"])

        failed_digest = self._write_trial_slot(change_digest, expectation_digest, model, cleanup_ok=False)
        failed = dict(record, id="trial-cleanup-failed", receipt_digest=failed_digest)
        response = handle_feedback(self.store, self.scope, self.candidate, 1, failed)
        self.assertEqual("attachment_unknown", response["reason"])
        self.assertEqual("slot_result_binding_mismatch", response["attachment_reason"])


if __name__ == "__main__":
    unittest.main()
