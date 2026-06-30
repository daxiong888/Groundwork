"""Codex hook helpers for Groundwork router observability v0."""

import hashlib
import json
import os
import re
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from evals.route_detection import (  # noqa: E402
    classify_command,
    entry_decision_from_prompt,
    evidence_markers,
    risk_markers,
)
from evals.verdict_model import dispatch_decision_from_entry, render_router_card, score_turn  # noqa: E402


SECRET_PATTERNS = (
    (re.compile(r"(Authorization:\s*Bearer\s+)[^\s,;]+", re.I), r"\1[REDACTED]"),
    (re.compile(r"(token=)[^\s,;]+", re.I), r"\1[REDACTED]"),
    (re.compile(r"(api[_-]?key=)[^\s,;]+", re.I), r"\1[REDACTED]"),
    (re.compile(r"(cookie:\s*)[^\n]+", re.I), r"\1[REDACTED]"),
    (re.compile(r"\b(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9_]{20,}\b"), "[REDACTED_GITHUB_TOKEN]"),
    (re.compile(r"\bgithub_pat_[A-Za-z0-9_]{20,}\b"), "[REDACTED_GITHUB_PAT]"),
    (re.compile(r"\bAKIA[0-9A-Z]{16}\b"), "[REDACTED_AWS_ACCESS_KEY_ID]"),
    (re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}\b"), "[REDACTED_SLACK_TOKEN]"),
    (re.compile(r"\bsk-(?:[A-Za-z0-9]+-)?[A-Za-z0-9_-]{20,}\b"), "[REDACTED_OPENAI_KEY]"),
    (
        re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----.*?-----END [A-Z ]*PRIVATE KEY-----", re.S),
        "[REDACTED_PRIVATE_KEY]",
    ),
)

DEFAULT_CONFIG = {
    "enabled": False,
    "mode": "observe_only",
    "raw_capture": False,
    "snippet_capture": False,
}


def utc_now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_stdin_event():
    raw = sys.stdin.read()
    if not raw.strip():
        return {}
    return json.loads(raw)


def redact_text(text, *, compact=False, limit=None):
    value = str(text or "")
    for pattern, replacement in SECRET_PATTERNS:
        value = pattern.sub(replacement, value)
    if compact:
        value = " ".join(value.split())
    if limit is not None:
        value = value[:limit]
    return value


def redacted_snippet(text, limit=120):
    return redact_text(text, compact=True, limit=limit)


def stable_hash(text):
    return hashlib.sha256(str(text or "").encode("utf-8")).hexdigest()


def cwd_from_event(event):
    value = event.get("cwd") or event.get("working_dir") or event.get("workspace_dir") or os.getcwd()
    return Path(value).resolve()


def config_path(cwd):
    return cwd / ".groundwork" / "harness" / "router-observability" / "config.json"


def load_config(cwd):
    if os.environ.get("GROUNDWORK_ROUTER_OBSERVABILITY_DISABLED"):
        return None, "env_disabled"
    config = dict(DEFAULT_CONFIG)
    path = config_path(cwd)
    config_source = "absent"
    if path.exists():
        try:
            loaded = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            if os.environ.get("GROUNDWORK_ROUTER_OBSERVABILITY") != "1":
                return None, "invalid_config"
            config_source = "invalid_config_env_force_enable"
        else:
            if isinstance(loaded, dict):
                config.update(loaded)
                config_source = str(path.relative_to(cwd))
    if os.environ.get("GROUNDWORK_ROUTER_OBSERVABILITY") == "1":
        config["enabled"] = True
        config["mode"] = os.environ.get("GROUNDWORK_ROUTER_OBSERVABILITY_MODE", config.get("mode") or "observe_only")
        if config_source == "absent":
            return config, "env"
        if config_source == "invalid_config_env_force_enable":
            return config, config_source
        return config, "env_force_enable_over_config"
    if config_source != "absent":
        return config, config_source
    return None, "absent"


def ids_from_event_with_sources(event):
    session_source = "session_id"
    session_id = event.get("session_id")
    if not session_id:
        session_source = "conversation_id"
        session_id = event.get("conversation_id")
    if not session_id:
        session_source = "thread_id"
        session_id = event.get("thread_id")
    if not session_id:
        session_source = "fallback"
        session_id = "session-unknown"

    turn_source = "turn_id"
    turn_id = event.get("turn_id")
    if not turn_id:
        turn_source = "event_id"
        turn_id = event.get("event_id")
    if not turn_id:
        turn_source = "request_id"
        turn_id = event.get("request_id")
    if not turn_id and event.get("tool_use_id"):
        turn_source = "tool_use_id_fallback"
        turn_id = stable_hash(f"{session_id}:tool:{event.get('tool_use_id')}")[:12]
    if not turn_id and event.get("transcript_path"):
        turn_source = "transcript_path_fallback"
        turn_id = stable_hash(f"{session_id}:transcript:{event.get('transcript_path')}")[:12]
    if not turn_id:
        turn_source = "event_hash_fallback"
        turn_id = stable_hash(json.dumps(event, sort_keys=True))[:12]
    return str(session_id), str(turn_id), session_source, turn_source


def is_enabled(config):
    return bool(config and config.get("enabled"))


def ids_from_event(event):
    session_id, turn_id, _, _ = ids_from_event_with_sources(event)
    return session_id, turn_id


def turn_dir(cwd, event):
    session_id, turn_id = ids_from_event(event)
    return cwd / ".groundwork" / "harness" / "router-observability" / session_id / turn_id


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def append_jsonl(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(value, ensure_ascii=False, sort_keys=True) + "\n")


def read_json(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None


def read_jsonl_with_diagnostics(path):
    rows = []
    malformed = 0
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except FileNotFoundError:
        return rows, malformed
    for line in lines:
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError:
            malformed += 1
            continue
        if isinstance(value, dict):
            rows.append(value)
    return rows, malformed


def read_jsonl(path):
    rows, _malformed = read_jsonl_with_diagnostics(path)
    return rows


def event_metadata():
    return {
        "observed_at_ns": time.time_ns(),
        "pid": os.getpid(),
        "event_uuid": str(uuid.uuid4()),
    }


def raw_capture_allows_unredacted():
    return os.environ.get("GROUNDWORK_ROUTER_OBSERVABILITY_ALLOW_UNREDACTED_RAW_CAPTURE") == "1"


def raw_capture_payload(key, value):
    if raw_capture_allows_unredacted():
        return {
            key: value,
            "redaction": {"status": "unredacted_explicitly_allowed", "notes": []},
        }
    return {
        key: redact_text(value),
        "redaction": {
            "status": "redacted",
            "notes": ["set GROUNDWORK_ROUTER_OBSERVABILITY_ALLOW_UNREDACTED_RAW_CAPTURE=1 to store unredacted raw text"],
        },
    }


def ordered_events_for_stop(out_dir):
    tool_events, malformed_tool_events = read_jsonl_with_diagnostics(out_dir / "tool-events.jsonl")
    permission_events, malformed_permission_events = read_jsonl_with_diagnostics(out_dir / "permission-events.jsonl")
    events = tool_events + permission_events
    events.sort(
        key=lambda event: (
            int(event.get("observed_at_ns") or 0),
            str(event.get("event_uuid") or ""),
        )
    )
    for index, event in enumerate(events, start=1):
        event["event_index"] = index
    diagnostics = {
        "schema_version": "router_observability.coverage.v0",
        "tool_events": len(tool_events),
        "permission_events": len(permission_events),
        "malformed_tool_events": malformed_tool_events,
        "malformed_permission_events": malformed_permission_events,
        "event_ordering": "observed_at_ns,event_uuid",
    }
    return events, diagnostics


def prompt_from_event(event):
    return (
        event.get("prompt")
        or event.get("user_prompt")
        or event.get("input")
        or event.get("message")
        or ""
    )


def final_message_from_event(event):
    return (
        event.get("last_assistant_message")
        or event.get("final_response")
        or event.get("assistant_response")
        or event.get("final_message")
        or event.get("message")
        or ""
    )


def tool_name_from_event(event):
    return str(event.get("tool_name") or event.get("tool") or event.get("name") or "unknown")


def command_from_event(event):
    tool_input = event.get("tool_input") or event.get("input") or {}
    if isinstance(tool_input, dict):
        return (
            tool_input.get("command")
            or tool_input.get("cmd")
            or tool_input.get("patch")
            or tool_input.get("arguments")
            or ""
        )
    return str(tool_input or event.get("command") or "")


def compact_jsonish(value):
    try:
        return json.dumps(value, ensure_ascii=False, sort_keys=True)
    except TypeError:
        return str(value or "")


def tool_response_summary(event):
    marker = object()
    response = event.get("tool_response", marker)
    if response is marker:
        response = event.get("response", marker)
    if response is marker:
        return {
            "tool_response_present": False,
            "tool_response_status": "",
            "tool_response_length": 0,
            "tool_response_sha256": "",
        }
    text = compact_jsonish(response)
    status = ""
    if isinstance(response, dict):
        for key in ("status", "outcome", "exit_code", "returncode", "rc"):
            if key in response and response.get(key) is not None:
                status = str(response.get(key))
                break
    return {
        "tool_response_present": True,
        "tool_response_status": status,
        "tool_response_length": len(text),
        "tool_response_sha256": stable_hash(text),
    }


def handle_user_prompt_submit(event):
    cwd = cwd_from_event(event)
    config, source = load_config(cwd)
    if not is_enabled(config):
        return None
    session_id, turn_id, session_id_source, turn_id_source = ids_from_event_with_sources(event)
    mode = str(config.get("mode") or "observe_only")
    raw_capture = bool(config.get("raw_capture"))
    snippet_capture = bool(config.get("snippet_capture"))
    prompt = prompt_from_event(event)
    decision = entry_decision_from_prompt(prompt)
    router_hint_emitted = mode == "guided_hint_trial"
    out_dir = turn_dir(cwd, event)
    prompt_metadata = {
        "schema_version": "router_observability.prompt_metadata.v0",
        "session_id": session_id,
        "turn_id": turn_id,
        "session_id_source": session_id_source,
        "turn_id_source": turn_id_source,
        "created_at": utc_now(),
        "prompt_sha256": stable_hash(prompt),
        "prompt_length": len(str(prompt or "")),
        "prompt_snippet": redacted_snippet(prompt) if snippet_capture else "",
        "snippet_capture": "enabled" if snippet_capture else "disabled",
        "raw_prompt_storage": "enabled" if raw_capture else "disabled",
    }
    router_decision = {
        "schema_version": "router_observability.v0",
        "session_id": session_id,
        "turn_id": turn_id,
        "session_id_source": session_id_source,
        "turn_id_source": turn_id_source,
        "created_at": utc_now(),
        "cwd": str(cwd),
        "deployment_target": "personal_maintainer_cross_project_trial",
        "hook_packaging": "plugin_bundled",
        "project_opt_in": True,
        "activation_source": source,
        "decision_mode": mode,
        "router_hint_emitted": router_hint_emitted,
        "raw_prompt_storage": "enabled" if raw_capture else "disabled",
        "snippet_capture": "enabled" if snippet_capture else "disabled",
        "entry_decision": decision,
        "decision_evidence": [{"kind": "prompt_hash", "value": prompt_metadata["prompt_sha256"]}],
        "decision_source": "heuristic",
        "confidence": "medium" if decision["expected_best"] != "unknown" else "low",
        "limitations": [
            "heuristic live candidate; fixture-backed replay required for route truth",
            "prompt and final snippets are disabled by default unless snippet_capture is explicitly enabled",
        ],
    }
    write_json(out_dir / "prompt-metadata.json", prompt_metadata)
    write_json(out_dir / "router-decision.json", router_decision)
    dispatch_decision = dispatch_decision_from_entry(
        {
            **router_decision,
            "prompt_snippet": prompt_metadata["prompt_snippet"],
            "prompt_text_for_detection": prompt,
        }
    )
    if dispatch_decision:
        write_json(out_dir / "dispatch-decision.json", dispatch_decision)
    if raw_capture:
        write_json(out_dir / "prompt.raw.json", raw_capture_payload("prompt", prompt))
    if router_hint_emitted:
        hint = (
            f"Groundwork route hint: expected first route {decision['expected_best']}; "
            "keep scope, evidence, verification, and stop-condition boundaries explicit."
        )
        return {"hookSpecificOutput": {"hookEventName": "UserPromptSubmit", "additionalContext": hint}}
    return None


def handle_tool_event(event, hook_event_name):
    cwd = cwd_from_event(event)
    config, _ = load_config(cwd)
    if not is_enabled(config):
        return None
    out_dir = turn_dir(cwd, event)
    tool_name = tool_name_from_event(event)
    command = command_from_event(event)
    session_id, turn_id, session_id_source, turn_id_source = ids_from_event_with_sources(event)
    tool_input = event.get("tool_input") or event.get("input") or {}
    event_row = {
        "schema_version": "router_observability.tool_event.v0",
        "session_id": session_id,
        "turn_id": turn_id,
        "session_id_source": session_id_source,
        "turn_id_source": turn_id_source,
        "hook_event_name": hook_event_name,
        "tool_name": tool_name,
        "tool_use_id": str(event.get("tool_use_id") or ""),
        "tool_input_sha256": stable_hash(compact_jsonish(tool_input)) if tool_input else "",
        "command_class": classify_command(command, tool_name),
        "coverage_status": "observed_supported" if tool_name in {"Bash", "apply_patch"} or tool_name.startswith("mcp__") else "unsupported",
        "coverage_limitations": ["hooks do not prove complete shell, WebSearch, non-shell, or non-MCP coverage"],
        "risk_markers": risk_markers(command, tool_name),
        "evidence_markers": evidence_markers(command),
        "status": str(event.get("status") or "unknown"),
        **tool_response_summary(event),
        "redaction": {"status": "not_reviewed", "notes": []},
        **event_metadata(),
    }
    append_jsonl(out_dir / "tool-events.jsonl", event_row)
    return None


def handle_permission_event(event):
    cwd = cwd_from_event(event)
    config, _ = load_config(cwd)
    if not is_enabled(config):
        return None
    out_dir = turn_dir(cwd, event)
    session_id, turn_id, session_id_source, turn_id_source = ids_from_event_with_sources(event)
    row = {
        "schema_version": "router_observability.permission_event.v0",
        "session_id": session_id,
        "turn_id": turn_id,
        "session_id_source": session_id_source,
        "turn_id_source": turn_id_source,
        "hook_event_name": "PermissionRequest",
        "permission": str(event.get("permission") or event.get("action") or "unknown"),
        "command_class": classify_command(command_from_event(event), tool_name_from_event(event)),
        "coverage_status": "observed_supported",
        "coverage_limitations": ["permission hooks do not prove complete tool or shell coverage"],
        "risk_markers": risk_markers(command_from_event(event), tool_name_from_event(event)),
        "evidence_markers": evidence_markers(command_from_event(event)),
        "status": str(event.get("status") or "unknown"),
        "redaction": {"status": "not_reviewed", "notes": []},
        **event_metadata(),
    }
    append_jsonl(out_dir / "permission-events.jsonl", row)
    return None


def handle_stop(event):
    cwd = cwd_from_event(event)
    config, _ = load_config(cwd)
    if not is_enabled(config):
        return None
    out_dir = turn_dir(cwd, event)
    decision = read_json(out_dir / "router-decision.json")
    if not isinstance(decision, dict):
        return None
    final_message = final_message_from_event(event)
    snippet_capture = bool(config.get("snippet_capture"))
    final_metadata = {
        "schema_version": "router_observability.final_metadata.v0",
        "session_id": decision.get("session_id", "unknown"),
        "turn_id": decision.get("turn_id", "unknown"),
        "created_at": utc_now(),
        "final_sha256": stable_hash(final_message),
        "final_length": len(str(final_message or "")),
        "final_snippet": redacted_snippet(final_message) if snippet_capture else "",
        "snippet_capture": "enabled" if snippet_capture else "disabled",
        "raw_final_storage": "enabled" if config.get("raw_capture") else "disabled",
    }
    write_json(out_dir / "final-metadata.json", final_metadata)
    if config.get("raw_capture"):
        final_raw = raw_capture_payload("final", final_message)
        (out_dir / "final.raw.txt").write_text(str(final_raw["final"] or ""), encoding="utf-8")
        write_json(
            out_dir / "final.raw.meta.json",
            {
                "schema_version": "router_observability.final_raw_metadata.v0",
                "session_id": final_metadata["session_id"],
                "turn_id": final_metadata["turn_id"],
                "created_at": utc_now(),
                "final_sha256": final_metadata["final_sha256"],
                "final_length": final_metadata["final_length"],
                "redaction": final_raw["redaction"],
            },
        )
    events, coverage = ordered_events_for_stop(out_dir)
    write_json(out_dir / "coverage.json", coverage)
    dispatch_decision = read_json(out_dir / "dispatch-decision.json")
    score = score_turn({**decision, "final_sha256": final_metadata["final_sha256"]}, final_message, events, dispatch_decision)
    write_json(out_dir / "router-score.json", score)
    (out_dir / "router-card.md").write_text(
        render_router_card(score, decision, dispatch_decision),
        encoding="utf-8",
    )
    return None


def run_handler(handler, event_name=None):
    try:
        event = load_stdin_event()
        output = handler(event) if event_name is None else handler(event, event_name)
    except Exception as exc:  # Hooks must not break normal Codex use.
        output = None
        if os.environ.get("GROUNDWORK_ROUTER_OBSERVABILITY_DEBUG"):
            print(f"Groundwork router observability hook failed: {exc}", file=sys.stderr)
    if output is not None:
        print(json.dumps(output, ensure_ascii=False, sort_keys=True))
    return 0
