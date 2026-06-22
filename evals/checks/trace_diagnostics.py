"""Tolerant diagnostics for raw or synthetic trace JSONL events."""

import json
import re
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path


TEXT_KEYS = ("message", "text", "content", "output", "stderr", "stdout")
COMMAND_TEXT_RE = re.compile(r"^\s*\$\s*(.+)")
WHITESPACE_RE = re.compile(r"\s+")
EVIDENCE_MARKERS = (
    "git status",
    "git diff",
    "test",
    "tests",
    "pytest",
    "unittest",
    "npm test",
    "browser",
    "screenshot",
    "runtime evidence",
    "evidence source",
    "verification scope",
    "source evidence",
    "unverified",
)
FAILURE_MARKERS = (
    "command failed",
    "exit 1",
    "timeout",
    "permission denied",
)
ROLLBACK_MARKERS = (
    "git revert",
    "git reset",
    "rollback",
    "roll back",
    "revert",
)
COMMAND_EVENT_MARKERS = (
    "command",
    "exec",
    "tool",
    "shell",
    "terminal",
)
SHELL_TOOL_MARKERS = (
    "shell",
    "exec",
    "terminal",
    "bash",
    "zsh",
    "sh",
)
BLOCKED_REASON_MARKERS = (
    ("timeout", ("timeout", "timed out")),
    ("sandbox_denied", ("sandbox denied", "sandbox_denied", "permission denied", "operation not permitted")),
    ("missing_source_truth", ("missing source", "missing_source_truth", "no source truth", "source truth missing")),
    ("missing_runtime_evidence", ("missing runtime", "missing browser", "runtime evidence missing", "browser evidence missing")),
    ("schema_validation_error", ("schema validation error", "schema_validation_error", "schema_validation=fail")),
    ("forbidden_behavior", ("forbidden behavior", "forbidden_behavior")),
    ("redaction_failed", ("redaction failed", "redaction_failed")),
    ("tool_unavailable", ("tool unavailable", "command not found", "no such file or directory")),
    ("codex_exit", ("codex exit", "codex_exit")),
)


def parse_jsonl_trace(path):
    events = []
    for line_number, line in enumerate(Path(path).read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError as exc:
            events.append(
                {
                    "__unsupported_event__": True,
                    "__parse_error__": str(exc),
                    "__line_number__": line_number,
                }
            )
            continue
        if isinstance(event, dict):
            events.append(event)
        else:
            events.append(
                {
                    "__unsupported_event__": True,
                    "__non_dict_event__": True,
                    "__line_number__": line_number,
                    "content": repr(event),
                }
            )
    return events


def _first_path(event, paths):
    for path in paths:
        current = event
        for key in path:
            if not isinstance(current, dict) or key not in current:
                current = None
                break
            current = current[key]
        if current is not None:
            return current
    return None


def _stringify(value):
    if value is None:
        return None
    if isinstance(value, str):
        return value
    if isinstance(value, (int, float, bool)):
        return str(value)
    return json.dumps(value, sort_keys=True, ensure_ascii=False)


def _join_text_parts(event):
    parts = []
    for key in TEXT_KEYS:
        if key in event:
            text = _stringify(event.get(key))
            if text:
                parts.append(text)
    payload = event.get("payload")
    if isinstance(payload, dict):
        for key in TEXT_KEYS:
            if key in payload:
                text = _stringify(payload.get(key))
                if text:
                    parts.append(text)
    return "\n".join(parts)


def _parse_timestamp(value):
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if not isinstance(value, str):
        return None
    text = value.strip()
    if not text:
        return None
    try:
        return float(text)
    except ValueError:
        pass
    try:
        return datetime.fromisoformat(text.replace("Z", "+00:00")).timestamp()
    except ValueError:
        return None


def _normalize_command_text(command):
    text = str(command or "").strip()
    shell_match = COMMAND_TEXT_RE.match(text)
    if shell_match:
        text = shell_match.group(1)
    return WHITESPACE_RE.sub(" ", text).strip()


def normalize_event(event):
    if not isinstance(event, dict):
        event = {"__unsupported_event__": True, "content": repr(event)}

    event_type = _first_path(event, (("type",), ("event",), ("payload", "type"), ("payload", "event")))
    timestamp = _first_path(event, (("timestamp",), ("time",), ("created_at",), ("payload", "timestamp"), ("payload", "time")))
    command = _first_path(event, (("command",), ("cmd",), ("payload", "command"), ("payload", "cmd")))
    exit_code = _first_path(event, (("exit_code",), ("returncode",), ("rc",), ("payload", "exit_code"), ("payload", "returncode"), ("payload", "rc")))
    status = _first_path(event, (("status",), ("result",), ("payload", "status"), ("payload", "result")))
    tool_name = _first_path(event, (("tool_name",), ("tool",), ("name",), ("payload", "tool_name"), ("payload", "tool")))
    text = _join_text_parts(event)

    if command is None:
        match = COMMAND_TEXT_RE.match(text or "")
        if match:
            command = match.group(1)

    recognized = any(
        value is not None and value != ""
        for value in (event_type, timestamp, command, exit_code, status, tool_name, text)
    )

    return {
        "type": _stringify(event_type) or "",
        "timestamp": _parse_timestamp(timestamp),
        "command": _normalize_command_text(command) if command is not None else "",
        "exit_code": _coerce_exit_code(exit_code),
        "status": (_stringify(status) or "").lower(),
        "tool_name": (_stringify(tool_name) or "").lower(),
        "text": text or "",
        "unsupported": bool(event.get("__unsupported_event__")) or not recognized,
        "parse_error": event.get("__parse_error__"),
    }


def _coerce_exit_code(value):
    if value is None or value == "":
        return None
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, (int, float)):
        return int(value)
    try:
        return int(str(value).strip())
    except ValueError:
        return None


def _is_command_event(normalized):
    event_type = normalized["type"].lower()
    tool_name = normalized["tool_name"]
    text = normalized["text"]
    return bool(
        normalized["command"]
        or COMMAND_TEXT_RE.match(text)
        or any(marker in event_type for marker in COMMAND_EVENT_MARKERS)
        or any(marker in tool_name for marker in SHELL_TOOL_MARKERS)
    )


def _is_failure(normalized):
    if normalized["exit_code"] not in (None, 0):
        return True
    status = normalized["status"]
    text = normalized["text"].lower()
    if status in {"failed", "failure", "error", "timeout", "timed_out"}:
        return True
    return any(marker in text for marker in FAILURE_MARKERS)


def _has_evidence_marker(normalized):
    text = "\n".join(
        item
        for item in (
            normalized["command"],
            normalized["type"],
            normalized["tool_name"],
            normalized["status"],
            normalized["text"],
        )
        if item
    ).lower()
    return any(marker in text for marker in EVIDENCE_MARKERS)


def _has_rollback_marker(normalized):
    text = "\n".join(
        item for item in (normalized["command"], normalized["text"]) if item
    ).lower()
    return any(marker in text for marker in ROLLBACK_MARKERS)


def _blocked_reason(normalized_events):
    combined = "\n".join(
        " ".join(
            item
            for item in (
                event["command"],
                event["status"],
                event["text"],
                event["type"],
            )
            if item
        )
        for event in normalized_events
    ).lower()
    for reason, markers in BLOCKED_REASON_MARKERS:
        if any(marker in combined for marker in markers):
            return reason
    return "unknown"


def diagnose_trace_events(events):
    normalized_events = [normalize_event(event) for event in events]
    unsupported_event_count = sum(1 for event in normalized_events if event["unsupported"])
    parse_error_count = sum(1 for event in normalized_events if event["parse_error"])
    notes = []
    if parse_error_count:
        notes.append(f"invalid JSON lines: {parse_error_count}")
    if unsupported_event_count:
        notes.append(f"unsupported events: {unsupported_event_count}")

    command_events = [event for event in normalized_events if _is_command_event(event)]
    command_count = len(command_events)
    command_counter = Counter(event["command"] or event["text"].strip() for event in command_events)
    duplicate_command_count = sum(count - 1 for count in command_counter.values() if count > 1)
    failed_command_count = sum(1 for event in command_events if _is_failure(event))
    rollback_or_revert_count = sum(1 for event in normalized_events if _has_rollback_marker(event))

    failed_by_command = defaultdict(int)
    for event in command_events:
        if _is_failure(event):
            failed_by_command[event["command"] or event["text"].strip()] += 1

    first_evidence_index = None
    first_evidence_seconds = None
    start_timestamp = next((event["timestamp"] for event in normalized_events if event["timestamp"] is not None), None)
    for index, event in enumerate(normalized_events):
        if _has_evidence_marker(event):
            first_evidence_index = index
            if start_timestamp is not None and event["timestamp"] is not None:
                first_evidence_seconds = max(0.0, event["timestamp"] - start_timestamp)
            break

    if first_evidence_index is None:
        evidence_status = "not_applicable" if not normalized_events else "missing"
    else:
        evidence_status = "present"

    repeated_failed_command = any(
        command_counter.get(command, 0) >= 3 and failed_count >= 2
        for command, failed_count in failed_by_command.items()
    )
    trace_command_thrashing = bool(
        repeated_failed_command
        or (failed_command_count >= 3 and evidence_status == "missing")
        or rollback_or_revert_count >= 2
    )
    thrashing_notes = []
    if repeated_failed_command:
        thrashing_notes.append("same command repeated at least three times with multiple failures")
    if failed_command_count >= 3 and evidence_status == "missing":
        thrashing_notes.append("multiple failed commands before explicit evidence")
    if rollback_or_revert_count >= 2:
        thrashing_notes.append("multiple rollback or revert markers")

    return {
        "trace_event_count": len(normalized_events),
        "command_count": command_count,
        "duplicate_command_count": duplicate_command_count,
        "failed_command_count": failed_command_count,
        "rollback_or_revert_count": rollback_or_revert_count,
        "trace_command_thrashing": trace_command_thrashing,
        "thrashing_notes": thrashing_notes,
        "evidence_latency": {
            "first_evidence_event_index": first_evidence_index,
            "first_evidence_seconds": first_evidence_seconds,
            "status": evidence_status,
        },
        "blocked_reason": _blocked_reason(normalized_events),
        "unsupported_event_count": unsupported_event_count,
        "notes": notes,
    }


def diagnose_jsonl_trace(path):
    return diagnose_trace_events(parse_jsonl_trace(path))
