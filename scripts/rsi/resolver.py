"""Reference-only evidence resolution. Native turn context is an explicit join."""

import json
import os

from .schema import RSIError, canonical, digest, require, result
from .security import ReadMeter, filtered_text, normalized, open_regular


def valid_context(context):
    return (isinstance(context, dict) and isinstance(context.get("cwd"), str)
            and bool(context["cwd"].strip()) and isinstance(context.get("turn_id"), str)
            and bool(context["turn_id"].strip()))


def resolve_asset(store, scope, asset_id, limit, selection=None, meter=None):
    policy = json.loads(store.scope(scope)["policy"])
    require(policy["profile"] == "semantic", "semantic_authorization_required")
    asset = next((item for item in policy["assets"] if item["id"] == asset_id), None)
    require(asset is not None, "asset_denied")
    meter = meter.child(limit) if meter else ReadMeter(store, scope, limit)
    try:
        with open_regular(asset["path"]) as stream:
            size = os.fstat(stream.fileno()).st_size
            require(size <= 65536, "over_limit")
            require(size <= limit, "read_budget_exhausted")
            raw = meter.read(stream, size)
            require(len(raw) == size, "read_budget_exhausted")
        decoded = raw.decode("utf-8")
        if selection:
            lines = decoded.splitlines(keepends=True)
            start = selection["start_line"] - 1
            decoded = "".join(lines[start:start + selection["line_count"]])
        text, filters = filtered_text(decoded, policy["budgets"]["snippet_bytes"], asset=True)
        return {"status": "ok", "ref": "asset:" + asset_id, "asset_id": asset_id, "digest": digest(raw),
                "filtered_digest": digest(text.encode()), "text": text, "filters": filters,
                "role": "asset_data", "instruction_authority": "none", "bytes_read": meter.used}
    except FileNotFoundError:
        return {"status": "missing", "ref": "asset:" + asset_id, "bytes_read": meter.used}
    except (OSError, UnicodeError, RSIError) as exc:
        status = exc.reason if isinstance(exc, RSIError) and exc.reason in {"over_limit", "read_budget_exhausted"} else "denied"
        return {"status": status, "ref": "asset:" + asset_id, "bytes_read": meter.used}


def qualified_context(stream, config, project, initial, meter):
    """Verify exact host metadata and a future-only boundary, never infer a format."""
    binding = config["qualification"]
    identity = [initial.st_dev, initial.st_ino, initial.st_birthtime if hasattr(initial, "st_birthtime") else None]
    require(identity == binding["file_identity"] and initial.st_size >= binding["start_offset"], "transcript_qualification_changed")
    stream.seek(0)
    header = stream.readline(65537)
    require(header.endswith(b"\n") or meter.available() > 0, "read_budget_exhausted")
    require(header.endswith(b"\n") and digest(header) == binding["header_digest"], "transcript_qualification_changed")
    value = json.loads(header)
    require(value.get("type") == "session_meta" and value.get("payload", {}).get("id") == config["session_id"], "session_binding_denied")
    version = value["payload"].get("cli_version", "unknown")
    stream.seek(binding["context_position"])
    raw = stream.readline(65537)
    require(raw.endswith(b"\n") or meter.available() > 0, "read_budget_exhausted")
    require(raw.endswith(b"\n") and digest(raw) == binding["context_digest"] and stream.tell() <= binding["start_offset"], "transcript_qualification_changed")
    value = json.loads(raw)
    require(value.get("type") == "turn_context", "unsupported")
    context = {key: value.get("payload", {}).get(key) for key in ("cwd", "turn_id", "model")}
    require(valid_context(context) and context["cwd"] == str(project), "locator_binding_denied")
    stream.seek(binding["start_offset"] - 1)
    require(stream.read(1) == b"\n", "invalid_transcript_boundary")
    return config["session_id"], context, version


def transcript_messages(store, scope, source, turn_id, limit, meter=None):
    """Read only the registered locator; no glob/search or nearest-message fallback.

    v1 recognizes session_meta, turn_context and plain response_item messages.
    Any ambiguous context resets the join; hidden reasoning/tool records are ignored.
    Scan one fixed file watermark, retaining recoverable cursors and explicit gaps.
    """
    row = store.scope(scope)
    policy = json.loads(row["policy"])
    config = json.loads(source["config"])
    require(policy["profile"] == "semantic" and policy["semantic_source_locator"], "semantic_authorization_required")
    require(config["policy_generation"] == row["generation"], "old_locator_generation")
    require(config["format"] == "codex.session_jsonl.v1" and turn_id, "unsupported")
    path = normalized(source["path"])
    require(any(path.is_relative_to(normalized(root)) for root in policy["transcript_roots"]), "locator_root_denied")
    messages = []
    gaps = set(config.get("scan_gaps", []))
    gap_digest = config.get("scan_gap_digest", digest(sorted(gaps)))
    saved = config.get("cursor_context", {})
    session, context, version = saved.get("session"), saved.get("turn"), saved.get("version")
    offset, skipping = source["offset"], source["skipping"]
    context_position = saved.get("context_position")
    context_digest = saved.get("context_digest")
    meter = meter.child(limit) if meter else ReadMeter(store, scope, limit)
    with open_regular(path) as raw_stream:
        stream = meter.wrap(raw_stream)
        initial = os.fstat(stream.fileno())
        # Append does not change generation; replacement/truncation invalidates refs.
        generation = digest([initial.st_dev, initial.st_ino, initial.st_birthtime if hasattr(initial, "st_birthtime") else None])
        def record_gap(reason, position):
            nonlocal gap_digest
            gaps.add(reason)
            # Bounded history distinguishes repeated gaps without retaining raw data.
            gap_digest = digest([gap_digest, generation, position, reason])

        qualification = config.get("qualification")
        if qualification:
            seed = qualified_context(stream, config, store.project, initial, meter)
            require(source["generation"] in {None, generation}, "transcript_qualification_changed")
            if source["generation"] is None:
                offset = qualification["start_offset"]
                session, context, version = seed
                context_position, context_digest = qualification["context_position"], qualification["context_digest"]
        from .sources import file_signature
        signature = file_signature(stream, offset, qualification["start_offset"] if qualification else 0)
        prior = json.loads(source["signature"]) if source["signature"] else None
        if qualification:
            require(initial.st_size >= offset and (prior is None or prior == signature), "transcript_qualification_changed")
        elif source["generation"] != generation or initial.st_size < offset or prior and prior != signature:
            offset, skipping, session, context = 0, 0, None, None
            context_position, context_digest = None, None
            gaps.clear()
            gap_digest = digest([])
            with store.tx():
                store.scope(scope, row["generation"])
                if source["generation"]:
                    store.diagnostic(scope, "transcript_generation_changed", source["id"])
                store.db.execute("DELETE FROM messages WHERE source=?", (source["id"],))
        if context is not None:
            if not valid_context(context):
                record_gap("malformed_context", context_position)
                context = None
            elif context["cwd"] != str(store.project):
                context = None
        stream.seek(offset)
        scan_status = "ok"
        # Final signature is part of this call's allocation, including when skipping.
        while stream.tell() < initial.st_size and meter.available() > 64:
            position = stream.tell()
            size = min(65537, meter.available() - 64, initial.st_size - position)
            raw = stream.readline(size)
            if not raw:
                break
            if skipping or len(raw) > 65536:
                if not skipping:
                    record_gap("oversized_record", position)
                skipping = 0 if raw.endswith(b"\n") else 1
                offset = stream.tell()
                context = None
                continue
            if not raw.endswith(b"\n"):
                scan_status = "budget_exhausted" if stream.tell() < initial.st_size else "incomplete_record"
                break
            offset = stream.tell()
            try:
                record = json.loads(raw)
                require(isinstance(record, dict), "unsupported")
                payload = record.get("payload")
                require(isinstance(payload, dict), "unsupported")
            except (ValueError, RSIError):
                context = None
                record_gap("malformed_record", position)
                continue
            kind = record.get("type")
            if kind == "session_meta":
                require(session is None, "session_binding_conflict")
                require(payload.get("id") == config["session_id"], "session_binding_denied")
                session, version = payload["id"], payload.get("cli_version", "unknown")
            elif kind == "turn_context":
                context = {key: payload.get(key) for key in ("cwd", "turn_id", "model")}
                if not valid_context(context):
                    record_gap("malformed_context", position)
                    context = None
                elif context["cwd"] != str(store.project):
                    context = None
                context_position, context_digest = position, digest(raw)
            elif kind == "response_item" and session and context and config.get("turn_expiries", {}).get(context["turn_id"], 0) > store.now():
                if payload.get("type") != "message" or payload.get("role") not in ("user", "assistant"):
                    continue
                if payload.get("channel") not in (None, "final", "commentary"):
                    continue
                content = payload.get("content")
                if not isinstance(content, list) or not content or any(not isinstance(block, dict) or block.get("type") not in ("input_text", "output_text") or not isinstance(block.get("text"), str) for block in content):
                    continue
                text = "\n".join(block["text"] for block in content)
                try:
                    filtered, filters = filtered_text(text, policy["budgets"]["snippet_bytes"])
                except RSIError:
                    continue
                if not filtered.strip():
                    continue
                fingerprint = digest(raw)
                reference = "message:" + digest([source["id"], generation, position, payload["role"], fingerprint])
                messages.append({"ref": reference, "source_id": source["id"], "generation": generation,
                                 "position": position, "role": payload["role"], "order": position,
                                 "session_id": session, "turn_id": context["turn_id"], "digest": fingerprint,
                                 "context_position": context_position, "context_digest": context_digest,
                                 "filtered_digest": digest(filtered.encode()), "text": filtered,
                                 "filters": filters, "host_version": version,
                                 "format_source": config.get("format_source", "host_declared"),
                                 "actual_model": context.get("model", "unknown")})
        final = os.fstat(stream.fileno())
        current = path.stat()
        require((current.st_dev, current.st_ino) == (initial.st_dev, initial.st_ino) and final.st_size >= initial.st_size, "source_replaced")
        if skipping:
            scan_status = "budget_exhausted" if offset < initial.st_size else "incomplete_record"
        elif offset < initial.st_size and scan_status == "ok":
            scan_status = "budget_exhausted"
        if final.st_size > initial.st_size and scan_status == "ok":
            scan_status = "source_advanced"
        signature = file_signature(stream, offset, qualification["start_offset"] if qualification else 0)
    with store.tx():
        store.scope(scope, row["generation"])
        expiry = min(policy["expires_at"], store.now() + policy["budgets"]["derived_days"] * 86400)
        for message in messages:
            # Store positions and already filtered blocks only. Expired refs are never refreshed.
            store.db.execute("INSERT OR IGNORE INTO messages VALUES(?,?,?,?,?,?,?,?)", (message["ref"], scope, source["id"], generation, message["position"], message["turn_id"], canonical(message), expiry))
        config["cursor_context"] = {"session": session, "turn": context, "version": version, "context_position": context_position, "context_digest": context_digest}
        config["scan_gaps"] = sorted(gaps)
        config["scan_gap_digest"] = gap_digest
        store.db.execute("UPDATE sources SET offset=?,generation=?,signature=?,skipping=?,config=? WHERE id=?", (offset, generation, canonical(signature), skipping, canonical(config), source["id"]))
        selected = [json.loads(item["body"]) for item in store.db.execute("SELECT body FROM messages WHERE source=? AND generation=? AND turn_id=? AND body IS NOT NULL AND expires>? ORDER BY position", (source["id"], generation, turn_id, store.now()))]
    return {"status": scan_status if scan_status != "ok" else ("ok" if selected else "unsupported"),
            "scan_complete": scan_status == "ok", "gaps": sorted(gaps),
            "snapshot": {"generation": generation, "gap_digest": gap_digest},
            "bytes_read": meter.used, "messages": selected if scan_status == "ok" else []}


def evidence(store, scope, work, remaining, meter=None, transcript_snapshots=None):
    policy = json.loads(store.scope(scope)["policy"])
    refs, gaps = [], []
    meter = meter.child(remaining) if meter else ReadMeter(store, scope, remaining)
    selections = {item["ref"]: item for item in json.loads(work["body"]).get("supplement_requests", [])}
    for asset in policy["assets"]:
        if meter.available() <= 0:
            gaps.append("resolve_budget_exhausted")
            break
        item = resolve_asset(store, scope, asset["id"], min(meter.remaining, 65536), selections.get("asset:" + asset["id"]), meter=meter)
        item.pop("bytes_read", 0)
        if item["status"] == "ok":
            refs.append(item)
        else:
            gaps.append({"ref": item["ref"], "status": item["status"]})
    if work["kind"] == "event_observation":
        body = json.loads(work["body"])
        for source in store.db.execute("SELECT * FROM sources WHERE scope=? AND kind='transcript'", (scope,)).fetchall():
            if json.loads(source["config"])["session_id"] != body["session_id"]:
                continue
            try:
                item = transcript_messages(store, scope, source, body["turn_id"], meter.remaining, meter=meter)
                if transcript_snapshots is not None:
                    transcript_snapshots[source["id"]] = item["snapshot"]
                refs.extend(item["messages"])
                if item["status"] != "ok":
                    gaps.append({"source_id": source["id"], "status": item["status"]})
                gaps.extend({"source_id": source["id"], "status": gap} for gap in item["gaps"])
            except (OSError, RSIError) as exc:
                gaps.append({"source_id": source["id"], "status": exc.reason if isinstance(exc, RSIError) else "source_unreadable"})
        if not any(item["ref"].startswith("message:") for item in refs):
            gaps.append("native_message_join_unavailable")
    return refs, gaps, meter.used


def verify_refs(store, scope, packet, limit, meter=None):
    """Check the precise earlier record, not the latest nearby response."""
    phase = meter.child(limit) if meter else ReadMeter(store, scope, limit)
    used = 0
    for ref in packet["references"]:
        if ref["ref"].startswith("asset:"):
            item = resolve_asset(store, scope, ref["asset_id"], min(65536, phase.remaining), meter=phase)
            used = phase.used
            if item.get("digest") != ref["digest"]:
                return False, used
        elif ref["ref"].startswith("message:"):
            source = store.db.execute("SELECT * FROM sources WHERE id=? AND scope=?", (ref["source_id"], scope)).fetchone()
            if not source:
                return False, used
            path = normalized(source["path"])
            meter = phase.child(phase.remaining)
            with open_regular(path) as raw_stream:
                stream = meter.wrap(raw_stream)
                st = os.fstat(stream.fileno())
                generation = digest([st.st_dev, st.st_ino, st.st_birthtime if hasattr(st, "st_birthtime") else None])
                if generation != ref["generation"]:
                    return False, used
                stream.seek(ref["position"])
                raw = stream.readline(min(65537, max(0, limit - used)))
                used += len(raw)
                if digest(raw) != ref["digest"] or not raw.endswith(b"\n"):
                    return False, used
                stream.seek(ref["context_position"])
                raw = stream.readline(min(65537, max(0, limit - used)))
                used += len(raw)
                if digest(raw) != ref["context_digest"]:
                    return False, used
        if used > limit:
            return False, used
    return True, used
