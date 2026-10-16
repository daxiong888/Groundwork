"""Shared wire contracts. JSON objects are data, never executable instructions."""

import hashlib
import json
import re


class RSIError(Exception):
    def __init__(self, reason):
        self.reason = reason
        super().__init__(reason)


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def digest(value):
    data = value if isinstance(value, bytes) else canonical(value).encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def require(condition, reason):
    if not condition:
        raise RSIError(reason)


def identifier(value):
    require(isinstance(value, str) and re.fullmatch(r"[a-zA-Z0-9][a-zA-Z0-9_.:-]{0,127}", value), "invalid_identifier")
    return value


def fields(value, required, optional=()):
    require(isinstance(value, dict), "object_required")
    require(set(required) <= value.keys(), "missing_fields")
    require(value.keys() <= set(required) | set(optional), "unexpected_fields")


def decision_origin(value, scope, binding):
    fields(value, ("id", "source", "recorded_by", "thread_ref", "message_ref", "summary", "scope", "binding"))
    identifier(value["id"])
    require(value["source"] == "codex_user_interaction" and value["recorded_by"] == "assistant", "interaction_decision_required")
    require(value["scope"] == scope and value["binding"] == binding, "decision_binding_mismatch")
    require(isinstance(value["summary"], str) and 0 < len(value["summary"]) <= 2000, "decision_summary_required")
    for key in ("thread_ref", "message_ref"):
        require(value[key] is None or isinstance(value[key], str) and len(value[key]) <= 256, "invalid_interaction_ref")


def result(reason, coverage=None, **values):
    return {"reason": reason, "coverage": coverage if coverage is not None else {"status": "unknown"}, **values}


DEFAULTS = {
    "daily_records": 500, "daily_bytes": 1024 * 1024, "record_bytes": 65536,
    "daily_packets": 2, "daily_packet_bytes": 24576, "daily_ready": 2,
    "lease_seconds": 1200, "quiet_seconds": 120, "derived_days": 7,
    "facts_days": 14, "capacity_bytes": 100 * 1024 * 1024,
    "freshness_bytes": 131072, "snippet_bytes": 4096,
    "backlog_seconds": 86400,
}

OFFICIAL_URLS = {
    "https://developers.openai.com/api/docs/guides/latest-model",
    "https://openai.com/index/harness-engineering/",
    "https://learn.chatgpt.com/docs/hooks",
    "https://learn.chatgpt.com/docs/automations",
    "https://www.anthropic.com/engineering/writing-tools-for-agents",
    "https://claude.com/blog/the-ai-native-sdlc-playbook",
    "https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents",
}
