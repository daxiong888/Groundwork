"""Synthetic RSI fixtures; no real user transcripts or model calls."""

import json
from pathlib import Path
import tempfile
import time
import unittest

from scripts.rsi.control import policy_feedback, source_feedback
from scripts.rsi.schema import digest
from scripts.rsi.store import Store


class RSITestCase(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name).resolve()
        self.clock = [time.time()]
        self.store = Store(self.root, clock=lambda: self.clock[0])
        self.addCleanup(self.store.close)
        self.asset = self.root / "rule.md"
        self.asset.write_text("Read the relevant source before changing behavior.\n")
        self.transcripts = self.root / "transcripts"
        self.transcripts.mkdir()
        self.telemetry = self.root / ".groundwork/harness/router-observability"
        self.telemetry.mkdir(exist_ok=True)
        self.policy = {
            "project_root": str(self.root), "profile": "semantic",
            "service": {"provider": "codex", "profile": "high", "configured_model": "test_model"},
            "expires_at": self.clock[0] + 30 * 86400,
            "assets": [{"id": "rule", "path": str(self.asset)}],
            "sources": [{"id": "events", "kind": "telemetry_tree", "path": str(self.telemetry), "backfill_from": 0}],
            "transcript_roots": [str(self.transcripts)], "semantic_source_locator": True,
            "schedule": {"state": "not_registered", "timezone": "Asia/Shanghai"},
            "budgets": {"quiet_seconds": 1},
        }
        self.enable()

    def origin(self, binding, rid="decision-1"):
        return {"id": rid, "source": "codex_user_interaction", "recorded_by": "assistant", "thread_ref": None,
                "message_ref": None, "summary": "Synthetic limited-input authorization", "scope": "test", "binding": binding}

    def enable(self, rid="enable-1"):
        record = {"id": rid, "kind": "policy", "scope": "test", "operation": "enable", "policy": self.policy}
        record["origin"] = self.origin(digest({"scope": "test", "operation": "enable", "policy": self.policy}), rid)
        return policy_feedback(self.store, "test", record)

    def revoke(self):
        record = {"id": "revoke-1", "kind": "policy", "scope": "test", "operation": "revoke"}
        record["origin"] = self.origin(digest({"scope": "test", "operation": "revoke", "policy": None}), "revoke-1")
        return policy_feedback(self.store, "test", record)

    def event(self, turn="t1", **fields):
        return {"schema_version": "router_telemetry.tool_event.v1", "session_id": "s1", "turn_id": turn,
                "turn_id_source": "turn_id" if turn else "unresolved", "correlation_status": "resolved" if turn else "unresolved",
                "hook_event_name": "PostToolUse", "tool_response_status": "completed",
                "tool_response_exit_code": 0, "tool_response_present": True, **fields}

    def append(self, event=None, name="tool-events.jsonl", turn="t1"):
        directory = self.telemetry / "s1" / (turn or "_unresolved")
        directory.mkdir(parents=True, exist_ok=True)
        path = directory / name
        with path.open("a") as stream:
            stream.write(json.dumps(event or self.event(turn)) + "\n")
        return path

    def snapshot(self, status="current", **extra):
        path = self.telemetry / "s1/t1/coverage.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({"snapshot_status": status, "snapshot_id": "snap1", "unique_event_count": 1, **extra}))

    def official(self):
        record = {"id": "source-1", "kind": "source", "scope": "test", "source_id": "guide",
                  "url": "https://developers.openai.com/api/docs/guides/latest-model", "checked_at": self.clock[0],
                  "expires_at": self.clock[0] + 10 * 86400, "product": "Codex", "version": "observed",
                  "notes": "Review restrictive rules for applicability.", "substance_id": "applicability-v1",
                  "assets": ["rule"], "question": "Does the current rule block an already authorized action?",
                  "verified_by": "codex_host_web_tool"}
        source_feedback(self.store, "test", record)
        return record

    def analysis(self, packet, outcome="not_candidate"):
        analysis = {"schema_version": "groundwork.rsi.analysis.v1", "attempt": packet["attempt"],
                    "outcome": outcome, "model": "synthetic_pipeline_only", "thread_ref": "fixture",
                    "context": "current_thread", "references": [{"ref": r["ref"], "digest": r["digest"]} for r in packet["references"]],
                    "assessment": "Normal self repair is not evidence of a defect."}
        if outcome == "candidate":
            asset = next(r for r in packet["references"] if r["ref"] == "asset:rule")
            analysis["candidate"] = {
                "trigger": packet["trigger"], "problem": "Synthetic applicability question",
                "facts": [asset["ref"]], "inferences": ["Potentially overbroad rule"],
                "applicable_requirement": "Read relevant source", "actual_outcome": "No failure asserted",
                "unknowns": ["Behavior benefit"], "counterevidence": [], "normal_explanation": "Rule may already be sufficiently scoped",
                "target": {"asset_id": "rule", "location": "rule.md:1", "owner": "maintainer", "baseline_digest": asset["digest"]},
                "action": "narrow", "change": "Limit a rule to relevant source", "mechanism": "scope_condition",
                "acceptance": [{"id": "scope-check", "description": "Relevant source remains required"}],
                "counterexamples": ["Unrelated files should not require inspection"], "cost": "One source edit",
                "risk": "Missing a dependency", "rollback": "Restore accepted baseline", "behavior_evidence_required": False,
            }
        return analysis

    def prepared(self):
        from scripts.rsi.engine import prepare
        prepare(self.store, "test")
        self.clock[0] += 2
        return prepare(self.store, "test")["packet"]
