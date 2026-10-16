"""Minimal opt-in Groundwork telemetry for Codex hooks.

This runtime module records redacted/hash-based signals only. It does not inject
prompts, score routes, infer model profiles, or claim authoritative skill loads.
Maintainer-side analysis belongs in ordinary source tests and human-reviewed
proposal records; runtime telemetry emits candidate signals only.
"""

import hashlib
import importlib.util
import json
import os
import re
import stat
import time
import uuid
from functools import wraps
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path


def _load_route_detection_module():
    try:
        import groundwork_route_detection

        return groundwork_route_detection
    except ImportError:
        module_path = Path(__file__).with_name("groundwork_route_detection.py")
        spec = importlib.util.spec_from_file_location("groundwork_route_detection", module_path)
        if spec is None or spec.loader is None:
            raise
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module


_route_detection = _load_route_detection_module()
entry_decision_from_prompt = _route_detection.entry_decision_from_prompt
detect_route_from_text = _route_detection.detect_route_from_text
classify_command = _route_detection.classify_command
risk_markers = _route_detection.risk_markers
evidence_markers = _route_detection.evidence_markers


SENSITIVE_ASSIGNMENT_KEYS = r"(?:token|api[_-]?key|password|passwd|client[_-]?secret|aws_secret_access_key|cookie)"
SECRET_PATTERNS = (
    (re.compile(r"([\"']?Authorization[\"']?\s*:\s*[\"']?Bearer\s+)[^\"'\s,;}\]]+", re.I), r"\1[REDACTED]"),
    (
        re.compile(rf"([\"']?{SENSITIVE_ASSIGNMENT_KEYS}[\"']?\s*[:=]\s*)(?P<quote>[\"'])(?:(?:\\.)|(?!(?P=quote)).)*(?P=quote)", re.I),
        r"\1\g<quote>[REDACTED]\g<quote>",
    ),
    (re.compile(r"(cookie:\s*)[^\n]+", re.I), r"\1[REDACTED]"),
    (re.compile(rf"([\"']?{SENSITIVE_ASSIGNMENT_KEYS}[\"']?\s*[:=]\s*)[^\"'\s,;}}\]]+", re.I), r"\1[REDACTED]"),
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

DEFAULT_CONFIG = {"enabled": False, "mode": "observe_only", "raw_capture": False, "snippet_capture": False}
BOOLEAN_CONFIG_FIELDS = {"enabled", "raw_capture", "snippet_capture"}
TELEMETRY_RELATIVE_PATH = Path(".groundwork/harness/router-observability")


def utc_now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def redact_text(text, *, compact=False, limit=None):
    value = str(text or "")
    for pattern, replacement in SECRET_PATTERNS:
        value = pattern.sub(replacement, value)
    if compact:
        value = re.sub(r"\s+", " ", value).strip()
    if limit is not None and len(value) > limit:
        value = value[:limit] + "..."
    return value


def redacted_snippet(text, limit=120):
    return redact_text(text, compact=True, limit=limit)


def stable_hash(text):
    return hashlib.sha256(str(text or "").encode("utf-8")).hexdigest()


def cwd_from_event(event):
    return Path(event.get("cwd") or os.getcwd()).resolve()


def checked_telemetry_path(cwd, path):
    project_root = Path(cwd).resolve()
    telemetry_root = project_root / TELEMETRY_RELATIVE_PATH
    candidate = Path(path)
    candidate = candidate if candidate.is_absolute() else telemetry_root / candidate
    if not candidate.is_relative_to(telemetry_root):
        raise ValueError("router telemetry path escapes its project root")
    current = project_root
    for part in candidate.relative_to(project_root).parts:
        current /= part
        if current.is_symlink():
            raise ValueError(f"router telemetry path contains a symlink: {current}")
    if not candidate.resolve(strict=False).is_relative_to(telemetry_root.resolve(strict=False)):
        raise ValueError("router telemetry path resolves outside its project root")
    return candidate


def load_config(cwd):
    config = None
    source = "absent"
    try:
        path = checked_telemetry_path(cwd, Path(cwd).resolve() / TELEMETRY_RELATIVE_PATH / "config.json")
        payload = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            raise ValueError("config must be an object")
        if any(field in payload and not isinstance(payload[field], bool) for field in BOOLEAN_CONFIG_FIELDS):
            raise ValueError("config boolean fields must use JSON booleans")
        if "mode" in payload and not isinstance(payload["mode"], str):
            raise ValueError("config mode must be a string")
        config = {**DEFAULT_CONFIG, **payload}
        source = ".groundwork/harness/router-observability/config.json"
    except FileNotFoundError:
        pass
    except (json.JSONDecodeError, ValueError):
        source = "invalid_config"

    if os.environ.get("GROUNDWORK_ROUTER_OBSERVABILITY") == "1":
        config = {**DEFAULT_CONFIG, **(config or {}), "enabled": True}
        if source == "invalid_config":
            source = "invalid_config_env_force_enable"
        elif source == "absent":
            source = "env_force_enable"
        else:
            source = "env_force_enable_over_config"
    return config, source


def ids_from_event_with_sources(event):
    session_source, session_id = next(
        ((field, source_id(event, field)) for field in ("session_id", "conversation_id", "thread_id") if source_id(event, field)),
        ("fallback", None),
    )
    turn_id = source_id(event, "turn_id")
    return session_id, turn_id, session_source, "turn_id" if turn_id else "unresolved"


def source_id(event, field):
    value = event.get(field)
    return value if isinstance(value, str) and value.strip() else None


def safe_path_component(value):
    if value is None:
        return "_unresolved-session"
    text = str(value)
    # Preserve ordinary legacy IDs, but never reuse the old truncated-hash
    # namespace. Special legacy directories remain historical, not migrated.
    reserved = {"config.json", "active-turn.json", "tool-turns", "semantic-source-policy.json", "semantic-locators", "session-unknown", "con", "prn", "aux", "nul"}
    if (re.fullmatch(r"[a-z0-9][a-z0-9._-]{0,198}[a-z0-9_-]|[a-z0-9]", text)
            and text not in reserved and text.split(".")[0] not in reserved
            and not re.fullmatch(r"(?:[0-9a-f]{16}|com[1-9](?:\..*)?|lpt[1-9](?:\..*)?)", text)):
        return text
    return "~" + stable_hash(text)


def turn_dir(cwd, session_id, turn_id):
    return checked_telemetry_path(
        cwd, Path(safe_path_component(session_id)) / (safe_path_component(turn_id) if turn_id else "_unresolved")
    )


def correlated_ids(cwd, event, event_name):
    identity = correlation_metadata(cwd, event, event_name)
    return tuple(identity[key] for key in ("session_id", "turn_id", "session_id_source", "turn_id_source"))


def correlation_metadata(cwd, event, event_name):
    """Only native turns and unambiguous invocation bindings establish a turn.

    Call under the session lock when persisting events. Request/event ids are
    retained as source hashes, never interpreted as turns or active pointers.
    """
    session_id, turn_id, session_source, turn_source = ids_from_event_with_sources(event)
    reason = "" if turn_id else "missing_native_turn_id"
    binding_turns = []
    tool_id = source_id(event, "tool_use_id")
    # Only the documented invocation identity can bridge Pre/Post delivery order.
    if source_id(event, "session_id") and tool_id and event_name in {"PreToolUse", "PostToolUse"}:
        binding_path = checked_telemetry_path(
            cwd, turn_dir(cwd, session_id, None).parent / "tool-turns" / (stable_hash(tool_id) + ".json")
        )
        binding = read_json(binding_path) or {}
        binding_turns = binding.get("turn_ids", [])
        if turn_id:
            binding_turns = sorted(set(binding_turns) | {turn_id})
        if len(binding_turns) > 1:
            reason = "tool_use_id_turn_conflict"
        elif not turn_id and len(binding_turns) == 1:
            turn_id, turn_source, reason = binding_turns[0], "tool_use_id_binding", ""
        elif not turn_id:
            reason = "tool_use_id_unbound"
        # Exact replays keep their first capture bucket even if later evidence
        # could resolve them. This avoids cross-file moves and double counting.
        delivery = source_event_metadata(event, event_name)
        delivery_key = stable_hash(compact_jsonish([event_name, delivery["source_event_key"], delivery["source_event_sha256"]]))
        locations = binding.setdefault("event_turns", {})
        if not source_id(event, "turn_id") and delivery_key in locations:
            turn_id = locations[delivery_key]
            turn_source = "tool_use_id_binding" if turn_id else "unresolved"
            if not turn_id and len(binding_turns) <= 1:
                reason = "original_delivery_unresolved"
        locations.setdefault(delivery_key, turn_id)
        if binding.get("turn_ids", []) != binding_turns:
            for affected_turn in binding_turns:
                invalidate_coverage(cwd, turn_dir(cwd, session_id, affected_turn))
        write_json(binding_path, {**binding, "turn_ids": binding_turns})
    return {
        "session_id": session_id,
        "turn_id": turn_id,
        "session_id_source": session_source,
        "turn_id_source": turn_source,
        "correlation_scope": "capture_time_only",
        "correlation_status": "conflict" if len(binding_turns) > 1 else ("resolved" if turn_id else "unresolved"),
        "correlation_reason": reason,
        "source_identity_sha256": {
            key: stable_hash(source_id(event, key))
            for key in ("session_id", "conversation_id", "thread_id", "turn_id", "request_id", "event_id", "tool_use_id", "agent_id")
            if source_id(event, key)
        },
        "binding_turn_ids": binding_turns,
    }


@contextmanager
def session_lock(cwd, session_dir):
    lock_path = checked_telemetry_path(cwd, session_dir / ".telemetry.lock")
    with open_output(lock_path, os.O_RDWR | os.O_CREAT, "r+") as handle:
        if os.name == "nt":
            import msvcrt
            lock = lambda: msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
        else:
            import fcntl
            lock = lambda: fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
        deadline = time.monotonic() + 1
        while True:
            try:
                lock()
                break
            except (BlockingIOError, PermissionError):
                if time.monotonic() >= deadline:
                    raise TimeoutError("telemetry session lock unavailable")
                time.sleep(0.01)
        yield


def serialized_telemetry(handler):
    """Keep capture writes short; compute derived Stop coverage after unlocking."""
    @wraps(handler)
    def run(event, *args):
        cwd = cwd_from_event(event)
        config, source = load_config(cwd)
        if not config or not config.get("enabled"):
            return None
        # Separate authorization; never read transcripts or the maintainer DB.
        try:
            record_semantic_locator(cwd, event)
        except (OSError, ValueError, TypeError):
            pass  # Locator failure must not suppress ordinary telemetry.
        session_id, _, _, _ = ids_from_event_with_sources(event)
        with session_lock(cwd, turn_dir(cwd, session_id, None).parent):
            snapshot = handler(event, *args, cwd=cwd, config=config, source=source)
        if snapshot is not None:
            refresh_coverage(cwd, *snapshot)
        return None
    return run


def record_semantic_locator(cwd, event):
    """Bounded private locator write; projection is generated by the consumer.

    This intentionally does not share the consumer's DB lock. A revocation may
    race an in-flight append; the consumer rejects and removes old generations.
    """
    path = checked_telemetry_path(cwd, "semantic-source-policy.json")
    descriptor = os.open(path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | os.O_NONBLOCK)
    with os.fdopen(descriptor, "rb") as handle:
        if not stat.S_ISREG(os.fstat(handle.fileno()).st_mode):
            return
        raw = handle.read(16385)
    if len(raw) > 16384:
        return
    policy = json.loads(raw)
    if not isinstance(policy, dict) or policy.get("schema_version") != "groundwork.semantic_source_policy.v1":
        return
    transcript, session = source_id(event, "transcript_path"), source_id(event, "session_id")
    if not transcript or not session or len(transcript) > 4096 or len(session) > 256:
        return
    target = Path(transcript)
    if not target.is_absolute() or ".." in target.parts:
        return
    current = Path(target.anchor)
    for part in target.parts[1:]:
        current /= part
        if current.is_symlink():
            return
    descriptor = os.open(target, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | os.O_NONBLOCK)
    try:
        if not stat.S_ISREG(os.fstat(descriptor).st_mode):
            return
    finally:
        os.close(descriptor)
    entries = policy.get("scopes")
    if not isinstance(entries, list) or len(entries) > 20:
        return
    for entry in entries:
        if (not isinstance(entry, dict) or entry.get("semantic_source_locator") is not True
                or entry.get("project_root") != str(cwd)
                or type(entry.get("generation")) is not int
                or type(entry.get("expires_at")) not in {int, float}
                or entry["expires_at"] <= time.time()):
            continue
        scope, filename, roots = entry.get("scope"), entry.get("locator_file"), entry.get("transcript_roots")
        if (not isinstance(scope, str) or len(scope) > 128 or not isinstance(filename, str)
                or not re.fullmatch(r"[0-9a-f]{64}\.jsonl", filename)
                or not isinstance(roots, list)
                or not any(isinstance(root, str) and target.is_relative_to(Path(root)) for root in roots)):
            continue
        if entry.get("transcript_bindings") is not None and not any(
                item.get("session_id") == session and item.get("path") == str(target) for item in entry["transcript_bindings"]):
            continue
        locator_record = {
            "schema_version": "groundwork.semantic_source_locator.v1",
            "scope": scope, "policy_generation": entry["generation"],
            "project_root": str(cwd), "session_id": session, "transcript_path": str(target),
            "turn_id": source_id(event, "turn_id"),
            "format": event.get("transcript_format") if event.get("transcript_format") == "codex.session_jsonl.v1" else "unknown",
            "host_version": event.get("host_version") if isinstance(event.get("host_version"), str) and len(event["host_version"]) <= 80 else "unknown",
            "captured_at": utc_now(),
        }
        locator_output = checked_telemetry_path(cwd, Path("semantic-locators") / filename)
        with session_lock(cwd, locator_output.parent):
            append_jsonl(locator_output, locator_record)


def write_json(path, value):
    temporary = path.with_name(f".{path.name}.{uuid.uuid4().hex}.tmp")
    try:
        with open_output(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL, "w") as handle:
            handle.write(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def append_jsonl(path, value):
    with open_output(path, os.O_WRONLY | os.O_CREAT | os.O_APPEND, "a") as handle:
        handle.write(json.dumps(value, ensure_ascii=False, sort_keys=True) + "\n")


def open_output(path, flags, mode):
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor = os.open(path, flags | getattr(os, "O_NOFOLLOW", 0), 0o600)
    return os.fdopen(descriptor, mode, encoding="utf-8")


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


def ordered_events_for_stop(cwd, out_dir):
    tool_events, malformed_tool_events = read_jsonl_with_diagnostics(out_dir / "tool-events.jsonl")
    permission_events, malformed_permission_events = read_jsonl_with_diagnostics(out_dir / "permission-events.jsonl")
    captured_events = tool_events + permission_events
    events, seen = [], {}
    for event in captured_events:
        key, fingerprint = event.get("source_event_key"), event.get("source_event_sha256")
        if key and fingerprint:
            fingerprints = seen.setdefault(key, set())
            if fingerprint in fingerprints:
                continue
            fingerprints.add(fingerprint)
        events.append(event)
    unique_captured_count = len(events)
    current_events, bindings = [], {}
    for event in events:
        if event.get("turn_id_source") == "tool_use_id_binding":
            tool_id = event.get("tool_use_id")
            if tool_id not in bindings:
                binding_path = checked_telemetry_path(cwd, out_dir.parent / "tool-turns" / (stable_hash(tool_id) + ".json"))
                bindings[tool_id] = read_json(binding_path) or {}
            binding = bindings[tool_id]
            if binding.get("turn_ids") != [event.get("turn_id")]:
                continue
        current_events.append(event)
    events = current_events
    events.sort(key=lambda event: (int(event.get("observed_at_ns") or 0), str(event.get("event_uuid") or "")))
    for index, event in enumerate(events, start=1):
        event["event_index"] = index
    malformed_event_count = malformed_tool_events + malformed_permission_events
    supported_event_count = sum(event.get("coverage_status") == "observed_supported" for event in events)
    unsupported_event_count = sum(event.get("coverage_status") == "unsupported" for event in events)
    classified_event_count = supported_event_count + unsupported_event_count
    return events, {
        "schema_version": "router_telemetry.captured_event_coverage.v2",
        "coverage_scope": "captured_hook_records_only",
        "turn_event_completeness": "unknown",
        "captured_record_count": len(captured_events) + malformed_event_count,
        "parsed_event_count": len(captured_events),
        "unique_captured_event_count": unique_captured_count,
        "unique_event_count": len(events),
        "excluded_correlation_event_count": unique_captured_count - len(events),
        "duplicate_event_count": len(captured_events) - unique_captured_count,
        "conflicting_event_identity_count": sum(len(values) > 1 for values in seen.values()),
        "classified_event_count": classified_event_count,
        "tool_events": sum(event.get("hook_event_name") in {"PreToolUse", "PostToolUse"} for event in events),
        "permission_events": sum(event.get("hook_event_name") == "PermissionRequest" for event in events),
        "malformed_tool_events": malformed_tool_events,
        "malformed_permission_events": malformed_permission_events,
        "malformed_event_count": malformed_event_count,
        "event_ordering": "observed_at_ns,event_uuid",
        "observed_supported_event_count": supported_event_count,
        "observed_unsupported_event_count": unsupported_event_count,
        "unclassified_event_count": len(events) - classified_event_count,
    }


def event_metadata():
    return {"observed_at_ns": time.time_ns(), "pid": os.getpid(), "event_uuid": str(uuid.uuid4())}


def raw_capture_payload(key, value):
    return {
        key: redact_text(value),
        "redaction": {"status": "redacted", "notes": ["runtime raw capture is always redacted"]},
    }


def prompt_from_event(event):
    return event.get("prompt") or event.get("user_prompt") or event.get("input") or event.get("message") or ""


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
        return tool_input.get("command") or tool_input.get("cmd") or tool_input.get("patch") or tool_input.get("arguments") or ""
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
    present = response is not marker
    text = compact_jsonish(response) if present else ""
    prefix = "tool_response" if "tool_response" in event else "response"
    summary = {
        "tool_response_present": present,
        "tool_response_length": len(text),
        "tool_response_sha256": stable_hash(text) if present else "",
        # An execution result never supplies business acceptance evidence.
        "tool_response_acceptance": "unknown",
    }
    known_statuses = {"completed", "success", "failed", "error", "running", "in_progress", "pending", "cancelled", "canceled", "timeout", "timed_out"}
    for name, keys, valid, unknown in (
        ("status", ("status", "outcome"), lambda value: isinstance(value, str) and value in known_statuses, ""),
        ("exit_code", ("exit_code", "returncode", "rc"), lambda value: type(value) is int, None),
    ):
        fields = {key: response[key] for key in keys if key in response} if isinstance(response, dict) else {}
        reason = "response_missing" if not present else "unsupported_response_type"
        value = unknown
        if isinstance(response, dict):
            reason = "field_missing"
            if fields:
                if not all(valid(item) for item in fields.values()):
                    reason = "unrecognized_field_value"
                elif len(set(fields.values())) > 1:
                    reason = "conflicting_fields"
                else:
                    value, reason = next(iter(fields.values())), ""
        summary[f"tool_response_{name}"] = value
        summary[f"tool_response_{name}_sources"] = [f"{prefix}.{key}" for key in fields]
        summary[f"tool_response_{name}_unknown_reason"] = reason
    return summary


def source_event_metadata(event, event_name):
    session_id, tool_id = source_id(event, "session_id"), source_id(event, "tool_use_id")
    key = ""
    if session_id and tool_id and event_name in {"PreToolUse", "PostToolUse"}:
        key = stable_hash(compact_jsonish([session_id, source_id(event, "turn_id"), tool_id, event_name]))
    return {"source_event_key": key, "source_event_sha256": stable_hash(compact_jsonish(event))}


def invalidate_coverage(cwd, out_dir, *, create=False):
    path = checked_telemetry_path(cwd, out_dir / "coverage.json")
    if not create and not path.exists():
        return None
    snapshot_id = uuid.uuid4().hex
    # Drop obsolete counters, not just their label. Invalidate before mutating
    # records/bindings so interruption cannot leave an apparently current view.
    write_json(path, {
        "schema_version": "router_telemetry.captured_event_coverage.v2",
        "coverage_scope": "captured_hook_records_only",
        "turn_event_completeness": "unknown",
        "snapshot_status": "stale",
        "snapshot_id": snapshot_id,
        "stale_reason": "capture_or_binding_changed; recompute on Stop",
    })
    return snapshot_id


def refresh_coverage(cwd, out_dir, snapshot_id):
    """Optimistic snapshot: no capture lock during history/binding reads."""
    checked_telemetry_path(cwd, out_dir / "tool-events.jsonl")
    checked_telemetry_path(cwd, out_dir / "permission-events.jsonl")
    _, coverage = ordered_events_for_stop(cwd, out_dir)
    with session_lock(cwd, out_dir.parent):
        path = checked_telemetry_path(cwd, out_dir / "coverage.json")
        if (read_json(path) or {}).get("snapshot_id") == snapshot_id:
            write_json(path, {**coverage, "snapshot_status": "current", "snapshot_id": snapshot_id})


@serialized_telemetry
def handle_user_prompt_submit(event, *, cwd, config, source):
    identity = correlation_metadata(cwd, event, "UserPromptSubmit")
    session_id, turn_id = identity["session_id"], identity["turn_id"]
    prompt = prompt_from_event(event)
    decision = entry_decision_from_prompt(prompt)
    out_dir = turn_dir(cwd, session_id, turn_id)
    prompt_metadata = {
        "schema_version": "router_telemetry.prompt_metadata.v1",
        **identity,
        "created_at": utc_now(),
        "prompt_sha256": stable_hash(prompt),
        "prompt_length": len(str(prompt or "")),
        "prompt_snippet": redacted_snippet(prompt) if config.get("snippet_capture") else "",
        "snippet_capture": "enabled" if config.get("snippet_capture") else "disabled",
        "raw_prompt_storage": "enabled" if config.get("raw_capture") else "disabled",
    }
    router_decision = {
        "schema_version": "router_telemetry.prompt_candidate.v2",
        **identity,
        "created_at": utc_now(),
        "cwd_sha256": stable_hash(str(cwd)),
        "activation_source": source,
        "decision_mode": "observe_only",
        "requested_mode": str(config.get("mode") or "observe_only"),
        "behavior_intervention": False,
        "router_hint_emitted": False,
        "prompt_enhancement_emitted": False,
        "entry_decision": decision,
        "prompt_route_candidate": decision.get("expected_best", "unknown"),
        "decision_source": "prompt_classifier_candidate",
        "decision_evidence": [{"kind": "prompt_hash", "value": prompt_metadata["prompt_sha256"]}],
        "limitations": [
            "route candidate only; no requirement-state, source-truth, risk, lifecycle, actual route, or skill-load inference"
        ],
    }
    if turn_id is None:
        append_jsonl(checked_telemetry_path(cwd, out_dir / "prompt-events.jsonl"), {
            **prompt_metadata, **event_metadata(), "prompt_route_candidate": router_decision["prompt_route_candidate"],
            **(raw_capture_payload("prompt", prompt) if config.get("raw_capture") else {}),
        })
        return None
    write_json(checked_telemetry_path(cwd, out_dir / "prompt-metadata.json"), prompt_metadata)
    write_json(checked_telemetry_path(cwd, out_dir / "router-decision.json"), router_decision)
    if config.get("raw_capture"):
        write_json(checked_telemetry_path(cwd, out_dir / "prompt.raw.json"), raw_capture_payload("prompt", prompt))
    return None


@serialized_telemetry
def handle_tool_event(event, hook_event_name, *, cwd, config, source):
    tool_name = tool_name_from_event(event)
    command = command_from_event(event)
    identity = correlation_metadata(cwd, event, hook_event_name)
    session_id, turn_id = identity["session_id"], identity["turn_id"]
    tool_input = event.get("tool_input") or event.get("input") or {}
    row = {
        "schema_version": "router_telemetry.tool_event.v1",
        **identity,
        "hook_event_name": hook_event_name,
        "tool_name": tool_name,
        "tool_use_id": str(event.get("tool_use_id") or ""),
        "tool_input_sha256": stable_hash(compact_jsonish(tool_input)) if tool_input else "",
        "command_class": classify_command(command, tool_name),
        "coverage_status": "observed_supported" if tool_name in {"Bash", "apply_patch"} or tool_name.startswith("mcp__") else "unsupported",
        "risk_markers": risk_markers(command, tool_name),
        "evidence_markers": evidence_markers(command),
        **tool_response_summary(event),
        **source_event_metadata(event, hook_event_name),
        **event_metadata(),
    }
    out_dir = turn_dir(cwd, session_id, turn_id)
    invalidate_coverage(cwd, out_dir)
    append_jsonl(checked_telemetry_path(cwd, out_dir / "tool-events.jsonl"), row)
    return None


@serialized_telemetry
def handle_permission_event(event, *, cwd, config, source):
    identity = correlation_metadata(cwd, event, "PermissionRequest")
    session_id, turn_id = identity["session_id"], identity["turn_id"]
    tool_name = tool_name_from_event(event)
    command = command_from_event(event)
    row = {
        "schema_version": "router_telemetry.permission_event.v1",
        **identity,
        "hook_event_name": "PermissionRequest",
        "permission": str(event.get("permission") or event.get("action") or "unknown"),
        "command_class": classify_command(command, tool_name),
        "coverage_status": "observed_supported",
        "risk_markers": risk_markers(command, tool_name),
        "evidence_markers": evidence_markers(command),
        **event_metadata(),
    }
    out_dir = turn_dir(cwd, session_id, turn_id)
    invalidate_coverage(cwd, out_dir)
    append_jsonl(checked_telemetry_path(cwd, out_dir / "permission-events.jsonl"), row)
    return None


@serialized_telemetry
def handle_stop(event, *, cwd, config, source):
    identity = correlation_metadata(cwd, event, "Stop")
    session_id, turn_id = identity["session_id"], identity["turn_id"]
    out_dir = turn_dir(cwd, session_id, turn_id)
    snapshot_id = invalidate_coverage(cwd, out_dir, create=True)
    decision = read_json(checked_telemetry_path(cwd, out_dir / "router-decision.json"))
    if not isinstance(decision, dict):
        decision = {}
    final_message = final_message_from_event(event)
    response_route, _ = detect_route_from_text(final_message)
    final_metadata = {
        "schema_version": "router_telemetry.final_metadata.v1",
        **identity,
        "created_at": utc_now(),
        "final_sha256": stable_hash(final_message),
        "final_length": len(str(final_message or "")),
        "final_snippet": redacted_snippet(final_message) if config.get("snippet_capture") else "",
        "snippet_capture": "enabled" if config.get("snippet_capture") else "disabled",
        "raw_final_storage": "enabled" if config.get("raw_capture") else "disabled",
        "prompt_route_candidate": decision.get("prompt_route_candidate", "unknown"),
        "response_shape_candidate": response_route,
        "response_shape_source": "response_shape_heuristic",
        "authoritative_skill_load_trace": "unavailable",
        "skill_hits": [],
        "limitations": ["response shape is not actual route or skill-load evidence"],
    }
    if turn_id is None:
        append_jsonl(checked_telemetry_path(cwd, out_dir / "stop-events.jsonl"), {
            **final_metadata, **event_metadata(),
            **(raw_capture_payload("final", final_message) if config.get("raw_capture") else {}),
        })
        return out_dir, snapshot_id
    write_json(checked_telemetry_path(cwd, out_dir / "final-metadata.json"), final_metadata)
    if config.get("raw_capture"):
        final_raw = raw_capture_payload("final", final_message)
        with open_output(checked_telemetry_path(cwd, out_dir / "final.raw.txt"), os.O_WRONLY | os.O_CREAT | os.O_TRUNC, "w") as handle:
            handle.write(str(final_raw["final"] or ""))
        write_json(
            checked_telemetry_path(cwd, out_dir / "final.raw.meta.json"),
            {
                "schema_version": "router_telemetry.final_raw_metadata.v1",
                "session_id": final_metadata["session_id"],
                "turn_id": final_metadata["turn_id"],
                "created_at": utc_now(),
                "final_sha256": final_metadata["final_sha256"],
                "final_length": final_metadata["final_length"],
                "redaction": final_raw["redaction"],
            },
        )
    return out_dir, snapshot_id
