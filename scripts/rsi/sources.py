"""Bounded incremental adapters for P0 telemetry and private native locators."""

import json
import os
from pathlib import Path
import re
import uuid
from datetime import datetime

from .control import locator_path
from .schema import RSIError, canonical, digest, require
from .security import ReadMeter, normalized, open_regular, read_bytes, within


EVENT_SCHEMAS = {
    "router_telemetry.tool_event.v1", "router_telemetry.permission_event.v1",
    "router_telemetry.prompt_metadata.v1", "router_telemetry.final_metadata.v1",
}
FILENAMES = {"tool-events.jsonl", "permission-events.jsonl", "prompt-events.jsonl", "stop-events.jsonl", "prompt-metadata.json", "final-metadata.json"}
COUNTERS = {"captured_record_count", "parsed_event_count", "unique_captured_event_count", "unique_event_count", "excluded_correlation_event_count", "duplicate_event_count", "conflicting_event_identity_count", "classified_event_count", "tool_events", "permission_events", "malformed_event_count", "observed_supported_event_count", "observed_unsupported_event_count", "unclassified_event_count"}


def component(value):
    if value is None:
        return "_unresolved-session"
    reserved = {"config.json", "active-turn.json", "tool-turns", "semantic-source-policy.json", "semantic-locators", "session-unknown", "con", "prn", "aux", "nul"}
    if (isinstance(value, str) and re.fullmatch(r"[a-z0-9][a-z0-9._-]{0,198}[a-z0-9_-]|[a-z0-9]", value)
            and value not in reserved and value.split(".")[0] not in reserved
            and not re.fullmatch(r"(?:[0-9a-f]{16}|com[1-9](?:\..*)?|lpt[1-9](?:\..*)?)", value)):
        return value
    import hashlib
    return "~" + hashlib.sha256(str(value).encode()).hexdigest()


def coverage(path, meter=None):
    try:
        if meter:
            with open_regular(path) as stream:
                size = os.fstat(stream.fileno()).st_size
                require(size <= 8192, "invalid_coverage")
                raw = meter.read(stream, size)
                require(len(raw) == size, "read_budget_exhausted")
                require(os.fstat(stream.fileno()).st_size == size, "coverage_changed_during_read")
        else:
            raw = read_bytes(path, 8192)
        value = json.loads(raw)
        require(isinstance(value, dict), "invalid_coverage")
        status = value.get("snapshot_status", "legacy")
        snapshot = value.get("snapshot_id")
        if status != "current" or not isinstance(snapshot, str) or not snapshot:
            return {"snapshot_status": status if status in {"stale", "legacy"} else "invalid", "snapshot_id": snapshot if isinstance(snapshot, str) else None}
        counts = {key: value[key] for key in COUNTERS if key in value and type(value[key]) is int and value[key] >= 0}
        return {"snapshot_status": "current", "snapshot_id": snapshot, "counts": counts, "completeness": "unknown"}
    except FileNotFoundError:
        return {"snapshot_status": "missing", "snapshot_id": None}
    except RSIError as exc:
        if exc.reason in {"read_budget_exhausted", "coverage_changed_during_read"}:
            return {"snapshot_status": "unavailable", "snapshot_id": None, "reason": exc.reason}
        return {"snapshot_status": "invalid", "snapshot_id": None}
    except OSError:
        return {"snapshot_status": "unavailable", "snapshot_id": None, "reason": "coverage_unreadable"}
    except ValueError:
        return {"snapshot_status": "invalid", "snapshot_id": None}


def event_adapter(value, path, telemetry_root):
    require(isinstance(value, dict) and value.get("schema_version") in EVENT_SCHEMAS, "unsupported_schema")
    session, turn = value.get("session_id"), value.get("turn_id")
    require(session is None or isinstance(session, str), "invalid_identity")
    require(turn is None or isinstance(turn, str), "invalid_identity")
    expected = telemetry_root / component(session) / (component(turn) if turn else "_unresolved")
    require(path.parent == expected, "historical_or_mismatched_directory")
    identity_source = value.get("turn_id_source", "unknown")
    native = identity_source == "turn_id" and session is not None and turn is not None
    status = value.get("tool_response_status")
    status = status if isinstance(status, str) and status in {"completed", "success", "failed", "error", "running", "in_progress", "pending", "cancelled", "canceled", "timeout", "timed_out"} else "unknown"
    code = value.get("tool_response_exit_code")
    data = {
        "producer": "groundwork_p0", "schema": value["schema_version"],
        "session_id": session, "turn_id": turn, "turn_id_source": identity_source,
        "association": "native" if native else "capture_time_only_unverified",
        "correlation_status": value.get("correlation_status", "unknown"),
        "tool_use_id": value.get("tool_use_id") or None,
        "event": value.get("hook_event_name", "prompt" if "prompt" in value["schema_version"] else "stop"),
        "event_time": value.get("created_at"), "observed_at_ns": value.get("observed_at_ns"),
        "completion": status, "exit_code": code if type(code) is int else None,
        "result_present": value.get("tool_response_present") if type(value.get("tool_response_present")) is bool else None,
        "completion_source": value.get("tool_response_status_sources", []),
        "exit_code_source": value.get("tool_response_exit_code_sources", []),
        "family": "unknown", "actual_model": "unknown", "loaded_version": "unknown",
        "acceptance": "unknown", "skill_load": "unknown",
    }
    # P0 native invocation + phase + original payload fingerprint is a replay key;
    # event_uuid and source_event_key alone are explicitly insufficient.
    identity = None
    if native and data["tool_use_id"] and data["event"] in {"PreToolUse", "PostToolUse"} and value.get("source_event_sha256"):
        identity = digest([session, turn, data["tool_use_id"], data["event"]])
    return data, identity, value.get("source_event_sha256") or digest(value)


def register(store, scope, sid, kind, path, config):
    row = store.db.execute("SELECT id,config FROM sources WHERE id=?", (sid,)).fetchone()
    if row:
        changed = json.loads(row["config"]).get("policy_generation") != config["policy_generation"]
        store.db.execute("UPDATE sources SET config=?,status=CASE WHEN ? OR status='policy_removed' THEN 'new' ELSE status END WHERE id=?", (canonical(config), changed, sid))
        return
    offset = 0
    signature = None
    generation = uuid.uuid4().hex
    if path.exists():
        with open_regular(path) as stream:
            st = os.fstat(stream.fileno())
            if "backfill_from" not in config and st.st_mtime < config["enabled_at"]:
                offset = st.st_size
            signature = {"dev": st.st_dev, "ino": st.st_ino, "anchor": digest(b"") if offset == 0 else None}
    store.db.execute("INSERT INTO sources(id,scope,kind,path,config,generation,offset,signature,updated) VALUES(?,?,?,?,?,?,?,?,?)", (sid, scope, kind, str(path), canonical(config), generation, offset, canonical(signature), store.now()))


def discover(store, scope):
    row = store.scope(scope)
    policy = json.loads(row["policy"])
    root = store.project / ".groundwork/harness/router-observability"
    with store.tx():
        store.scope(scope, row["generation"])
        active = set()
        for spec in policy["sources"]:
            base = within(spec["path"], root)
            paths = [base] if spec["kind"] == "telemetry" else []
            if spec["kind"] == "telemetry_tree" and base.exists():
                for directory, directories, files in os.walk(base, followlinks=False):
                    directories[:] = sorted(name for name in directories if name not in {"tool-turns", "semantic-locators"} and not (Path(directory) / name).is_symlink())
                    paths.extend(Path(directory) / name for name in sorted(files) if name in FILENAMES)
                    if len(paths) > 2000:
                        store.diagnostic(scope, "discovery_limit", spec["id"])
                        break
            for path in paths[:2000]:
                sid = scope + ":telemetry:" + digest(str(path))
                active.add(sid)
                source_config = {"enabled_at": row["updated"], "policy_generation": row["generation"]}
                if "backfill_from" in spec:
                    source_config["backfill_from"] = spec["backfill_from"]
                register(store, scope, sid, "telemetry", path, source_config)
        if policy["semantic_source_locator"]:
            sid = scope + ":locators"
            active.add(sid)
            register(store, scope, sid, "locator", locator_path(store, scope), {"enabled_at": row["updated"], "policy_generation": row["generation"]})
        # Removed policy sources cannot continue intake through old cursors.
        for source in store.db.execute("SELECT id FROM sources WHERE scope=? AND kind IN ('telemetry','locator')", (scope,)).fetchall():
            if source["id"] not in active:
                registered = store.db.execute("SELECT path,kind FROM sources WHERE id=?", (source["id"],)).fetchone()
                allowed = registered["kind"] == "telemetry" and any(
                    Path(registered["path"]).is_relative_to(Path(spec["path"])) if spec["kind"] == "telemetry_tree"
                    else registered["path"] == spec["path"] for spec in policy["sources"])
                if not allowed:
                    store.db.execute("UPDATE sources SET status='policy_removed' WHERE id=?", (source["id"],))


def file_signature(stream, offset, floor=0):
    st = os.fstat(stream.fileno())
    end = min(offset, st.st_size)
    length = min(64, max(0, end - floor))
    stream.seek(max(floor, end - 64))
    anchor = stream.read(length)
    require(len(anchor) == length, "read_budget_exhausted")
    return {"dev": st.st_dev, "ino": st.st_ino, "anchor": digest(anchor)}


def put_work(store, scope, wid, kind, body, expiry):
    old = store.db.execute("SELECT * FROM work WHERE id=?", (wid,)).fetchone()
    if old and old["expires"] <= store.now():
        return False
    revision = old["revision"] + 1 if old else 1
    store.db.execute("""INSERT INTO work VALUES(?,?,?,?,?,?,?,?) ON CONFLICT(id) DO UPDATE SET
        revision=excluded.revision,state='pending',updated=excluded.updated,body=excluded.body""",
        (wid, scope, kind, revision, "pending", store.now(), canonical(body), expiry))
    if old:
        for candidate in store.db.execute("SELECT id,revision,notified_revision FROM candidates WHERE work_id=? AND state IN ('ready','closed','observing')", (wid,)).fetchall():
            store.db.execute("UPDATE candidates SET state='collecting',revision=revision+1,updated=? WHERE id=?", (store.now(), candidate["id"]))
            if candidate["notified_revision"]:
                store.diagnostic(scope, "candidate_correction", candidate["id"])
    return True


def locator_adapter(store, scope, value):
    policy_row = store.scope(scope)
    policy = json.loads(policy_row["policy"])
    require(value.get("schema_version") == "groundwork.semantic_source_locator.v1", "unsupported_locator")
    require(value.get("scope") == scope and value.get("policy_generation") == policy_row["generation"], "old_locator_generation")
    require(value.get("project_root") == str(store.project) and value.get("session_id"), "locator_binding_denied")
    path = normalized(value.get("transcript_path", ""))
    require(any(path.is_relative_to(normalized(root)) for root in policy["transcript_roots"]), "locator_root_denied")
    require(value.get("format") in {"codex.session_jsonl.v1", "unknown"}, "unsupported_locator")
    binding = next((item for item in policy.get("transcript_bindings", []) if item["session_id"] == value["session_id"] and item["path"] == str(path)), None)
    require("transcript_bindings" not in policy or binding is not None, "locator_binding_denied")
    sid = scope + ":transcript:" + digest([str(path), value["session_id"], policy_row["generation"]])
    existing = store.db.execute("SELECT config FROM sources WHERE id=?", (sid,)).fetchone()
    config = {"session_id": value["session_id"], "format": value["format"], "policy_generation": policy_row["generation"], "host_version": value.get("host_version", "unknown")}
    if binding:
        config.update(format=binding["format"], format_source="interactive_host_schema_check", host_declared_format=value["format"], qualification=binding)
    if existing:
        previous = json.loads(existing["config"])
        require(all(previous.get(key) == value for key, value in config.items()), "locator_conflict")
        config = previous
    turn = value.get("turn_id")
    if isinstance(turn, str) and turn:
        config["authorized_turns"] = sorted(set(config.get("authorized_turns", [])) | {turn})
        config.setdefault("turn_expiries", {}).setdefault(turn, store.now() + policy["budgets"]["derived_days"] * 86400)
    store.db.execute("INSERT OR IGNORE INTO sources(id,scope,kind,path,config,updated,status) VALUES(?,?,'transcript',?,?,?,'registered')", (sid, scope, str(path), canonical(config), store.now()))
    if existing:
        store.db.execute("UPDATE sources SET config=?,updated=? WHERE id=?", (canonical(config), store.now(), sid))


def consume_row(store, source, raw, position, generation, policy):
    value = json.loads(raw)
    scope = source["scope"]
    if source["kind"] == "locator":
        locator_adapter(store, scope, value)
        return
    body, identity, fingerprint = event_adapter(value, Path(source["path"]), store.project / ".groundwork/harness/router-observability")
    event_time = value.get("observed_at_ns")
    source_config = json.loads(source["config"])
    backfill = source_config.get("backfill_from")
    captured = event_time / 1e9 if type(event_time) is int else None
    if captured is None and isinstance(value.get("created_at"), str):
        try:
            captured = datetime.fromisoformat(value["created_at"].replace("Z", "+00:00")).timestamp()
        except ValueError:
            pass
    if backfill is None:
        require(captured is not None, "historical_boundary_unknown")
        if captured < source_config["enabled_at"]:
            return
    elif captured is not None and captured < backfill:
        return
    if identity:
        previous = store.db.execute("SELECT fingerprint FROM facts WHERE scope=? AND identity=?", (scope, identity)).fetchall()
        if any(row["fingerprint"] == fingerprint for row in previous):
            return
        if previous:
            store.diagnostic(scope, "source_identity_conflict", source["id"])
    fid = digest([source["id"], generation, position])
    if store.db.execute("SELECT id FROM facts WHERE id=?", (fid,)).fetchone():
        return
    wid = digest([scope, body["session_id"], body["turn_id"]]) if body["association"] == "native" else digest([scope, source["id"], generation, position])
    prior_work = store.db.execute("SELECT expires FROM work WHERE id=?", (wid,)).fetchone()
    if prior_work and prior_work["expires"] <= store.now():
        store.diagnostic(scope, "evidence_expired", source["id"])
        return
    # Only a recorded exact maintenance invocation can be excluded. Never a whole thread.
    maintenance = policy["schedule"].get("maintenance_turns", [])
    wake = store.db.execute("SELECT wake_id FROM maintenance_invocations WHERE scope=? AND thread_ref=? AND turn_ref=?", (scope, body["session_id"], body["turn_id"])).fetchone()
    if wake or [body["session_id"], body["turn_id"]] in maintenance:
        store.diagnostic(scope, "maintenance_health_event", source["id"])
        return
    expiry = store.now() + policy["budgets"]["facts_days"] * 86400
    store.db.execute("INSERT INTO facts VALUES(?,?,?,?,?,?,?,?,?,?,?)", (fid, scope, source["id"], generation, str(position), identity, fingerprint, wid, canonical(body), store.now(), expiry))
    put_work(store, scope, wid, "event_observation", {"session_id": body["session_id"], "turn_id": body["turn_id"], "family": body["family"]}, expiry)


def intake(store, scope, *, relevant=None, freshness=False, include_locators=False, meter=None, failures=None):
    """Charge I/O durably, then atomically commit facts/work and the cursor.

    An interrupted parse cannot roll back physical read costs. Concurrent readers
    may do duplicate bounded I/O, but compare the original cursor before commit.
    """
    discover(store, scope)
    complete = True
    row = store.scope(scope)
    policy = json.loads(row["policy"])
    budget = policy["budgets"]
    phase_meter = meter
    if store.size() >= int(budget["capacity_bytes"] * .8):
        with store.tx():
            store.diagnostic(scope, "capacity_backpressure")
        return False
    sources = store.db.execute("SELECT * FROM sources WHERE scope=? AND kind IN ('telemetry','locator') AND status NOT IN ('unsupported','policy_removed') ORDER BY updated,id", (scope,)).fetchall()
    if relevant is not None:
        parents = {Path(source["path"]).parent for source in sources if source["id"] in relevant}
        relevant = set(relevant) | {source["id"] for source in sources if source["kind"] == "telemetry" and Path(source["path"]).parent in parents}
        if include_locators:
            relevant.update(source["id"] for source in sources if source["kind"] == "locator" and Path(source["path"]).exists())
    for source in sources:
        if relevant is not None and source["id"] not in relevant:
            continue
        if store.size() >= int(budget["capacity_bytes"] * .8):
            with store.tx():
                store.diagnostic(scope, "capacity_backpressure")
            complete = False
            break
        try:
            store.scope(scope, row["generation"])
            usage = store.usage(scope)
            remaining = budget["daily_bytes"] - usage["bytes"] - usage["reserved"] - (0 if freshness else budget["freshness_bytes"])
            if phase_meter:
                remaining = min(remaining, phase_meter.remaining)
            require(remaining > 128 and usage["records"] < budget["daily_records"], "intake_budget_exhausted")
            meter = phase_meter.child(remaining) if phase_meter else ReadMeter(store, scope, remaining)
            records, gaps = [], []
            offset, generation, skipping = source["offset"], source["generation"], source["skipping"]
            snapshot = source["snapshot"]
            with open_regular(source["path"]) as raw_stream:
                stream = meter.wrap(raw_stream)
                before = os.fstat(stream.fileno())
                signature = file_signature(stream, offset)
                old_signature = json.loads(source["signature"]) if source["signature"] else None
                changed = old_signature and any(old_signature.get(key) is not None and old_signature.get(key) != signature[key] for key in signature)
                if before.st_size < offset or changed:
                    gaps.append("source_gap_replaced_or_truncated")
                    generation, offset, skipping = uuid.uuid4().hex, 0, 0
                if not source["path"].endswith(".jsonl"):
                    stream.seek(0)
                    data = stream.read(min(meter.limit - meter.used - 64, budget["record_bytes"] + 1))
                    if len(data) < before.st_size or len(data) > budget["record_bytes"]:
                        complete = False
                        gaps.append("oversized_record" if before.st_size > budget["record_bytes"] else "intake_budget_exhausted")
                        if failures is not None:
                            failures.append(gaps[-1])
                    elif snapshot != digest(data):
                        records.append((data, digest(data)))
                        snapshot = digest(data)
                    offset = before.st_size
                else:
                    stream.seek(offset)
                    while meter.used < meter.limit - 64 and len(records) < budget["daily_records"] - usage["records"]:
                        start = stream.tell()
                        chunk = stream.readline(min(meter.limit - meter.used - 64, budget["record_bytes"] + 1))
                        if not chunk:
                            break
                        if skipping or len(chunk) > budget["record_bytes"]:
                            if not skipping:
                                gaps.append("oversized_record")
                            skipping = 0 if chunk.endswith(b"\n") else 1
                            offset = stream.tell()
                            continue
                        if not chunk.endswith(b"\n"):
                            complete = False
                            break
                        offset = stream.tell()
                        records.append((chunk, start))
                    if offset < os.fstat(stream.fileno()).st_size:
                        complete = False
                        reason = "intake_budget_exhausted" if meter.remaining <= 64 else (
                            "intake_record_limit" if len(records) >= budget["daily_records"] - usage["records"] else "incomplete_record")
                        gaps.append(reason)
                        if failures is not None:
                            failures.append(reason)
                signature = file_signature(stream, offset)
                current = normalized(source["path"]).stat()
                require((current.st_dev, current.st_ino) == (before.st_dev, before.st_ino), "source_replaced_during_read")
            with store.tx():
                store.scope(scope, row["generation"])
                current = store.db.execute("SELECT * FROM sources WHERE id=?", (source["id"],)).fetchone()
                require(current and (current["generation"], current["offset"], current["snapshot"]) == (source["generation"], source["offset"], source["snapshot"]), "source_cursor_advanced")
                require(store.usage(scope)["records"] + len(records) <= budget["daily_records"], "intake_budget_exhausted")
                for gap in gaps:
                    store.diagnostic(scope, gap, source["id"])
                for raw, position in records:
                    try:
                        consume_row(store, source, raw, position, generation, policy)
                    except (json.JSONDecodeError, UnicodeError, TypeError, ValueError):
                        store.diagnostic(scope, "malformed_record", source["id"])
                    except RSIError as exc:
                        store.diagnostic(scope, exc.reason, source["id"])
                        if exc.reason == "unsupported_schema":
                            store.db.execute("UPDATE sources SET status='unsupported' WHERE id=?", (source["id"],))
                            complete = False
                            break
                store.charge(scope, records=len(records))
                store.db.execute("UPDATE sources SET generation=?,offset=?,skipping=?,signature=?,snapshot=?,updated=?,status=CASE WHEN status='unsupported' THEN status ELSE 'current' END WHERE id=?", (generation, offset, skipping, canonical(signature), snapshot, store.now(), source["id"]))
        except (OSError, RSIError, ValueError) as exc:
            complete = False
            reason = exc.reason if isinstance(exc, RSIError) else "source_gap_unreadable"
            if failures is not None:
                failures.append(reason)
            with store.tx():
                store.diagnostic(scope, reason, source["id"])
    return complete


def drain_locators(store, scope):
    """Remove consumed locator bytes under the same short file lock as hooks."""
    import fcntl
    from .security import parent_fd
    path = locator_path(store, scope)
    if not path.exists():
        return
    lock_path = path.parent / ".telemetry.lock"
    try:
        with parent_fd(lock_path, create=True) as (parent, name):
            lock = os.open(name, os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW, 0o600, dir_fd=parent)
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            with store.tx():
                row = store.db.execute("SELECT * FROM sources WHERE scope=? AND kind='locator'", (scope,)).fetchone()
                if row:
                    with parent_fd(path) as (parent, name):
                        fd = os.open(name, os.O_RDWR | os.O_NOFOLLOW, dir_fd=parent)
                    with os.fdopen(fd, "r+b") as stream:
                        info = os.fstat(stream.fileno())
                        recorded = json.loads(row["signature"])
                        if info.st_size == row["offset"] and (info.st_dev, info.st_ino) == (recorded["dev"], recorded["ino"]):
                            stream.truncate(0)
                            signature = file_signature(stream, 0)
                            store.db.execute("UPDATE sources SET offset=0,signature=?,generation=? WHERE id=?", (canonical(signature), uuid.uuid4().hex, row["id"]))
        finally:
            os.close(lock)
    except (OSError, RSIError):
        # No claim of deletion: the next entry can retry without blocking a hook.
        with store.tx():
            store.diagnostic(scope, "locator_cleanup_pending")
