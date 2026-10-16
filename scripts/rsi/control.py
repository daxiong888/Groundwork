"""Interactive policy/source records, derived hook projection and recovery."""

import json
import sqlite3
from pathlib import Path

from .schema import DEFAULTS, OFFICIAL_URLS, RSIError, canonical, decision_origin, digest, fields, identifier, require, result
from .security import atomic_write, filtered_text, normalized, read_json, remove, within


PROJECTION = ".groundwork/harness/router-observability/semantic-source-policy.json"


def locator_path(store, scope):
    return store.project / ".groundwork/harness/router-observability/semantic-locators" / (digest(scope) + ".jsonl")


def validate_policy(store, policy):
    fields(policy, ("project_root", "profile", "service", "expires_at", "assets", "sources", "transcript_roots", "semantic_source_locator", "schedule"), ("budgets", "transcript_bindings"))
    require(normalized(policy["project_root"]) == store.project, "project_mismatch")
    require(policy["profile"] in {"semantic", "metadata_only"}, "invalid_profile")
    require(type(policy["semantic_source_locator"]) is bool, "invalid_locator_option")
    require(type(policy["expires_at"]) in {int, float} and policy["expires_at"] > store.now(), "invalid_expiry")
    fields(policy["service"], ("provider", "profile", "configured_model"))
    require(policy["service"]["provider"] == "codex", "unsupported_semantic_service")
    require(all(isinstance(v, str) and v for v in policy["service"].values()), "service_required")
    require(isinstance(policy["schedule"], dict), "schedule_required")
    require(not policy["semantic_source_locator"] or policy["profile"] == "semantic" and policy["transcript_roots"], "semantic_authorization_required")
    budgets = {**DEFAULTS, **policy.get("budgets", {})}
    require(budgets.keys() == DEFAULTS.keys(), "unknown_budget")
    require(all(type(value) is int and value > 0 for value in budgets.values()), "invalid_budget")
    require(budgets["record_bytes"] <= 65536 and budgets["freshness_bytes"] < budgets["daily_bytes"], "invalid_read_budget")
    require(budgets["derived_days"] <= budgets["facts_days"], "invalid_retention")
    assets, sources, roots = [], [], []
    require(isinstance(policy["assets"], list) and len(policy["assets"]) <= 50, "asset_limit")
    for asset in policy["assets"]:
        fields(asset, ("id", "path"))
        assets.append({"id": identifier(asset["id"]), "path": str(within(asset["path"], store.project))})
    require(len({a["id"] for a in assets}) == len(assets), "duplicate_asset")
    require(isinstance(policy["sources"], list) and len(policy["sources"]) <= 20, "source_limit")
    for source in policy["sources"]:
        fields(source, ("id", "kind", "path"), ("backfill_from",))
        require(source["kind"] in {"telemetry_tree", "telemetry"}, "unsupported_source")
        item = {**source, "id": identifier(source["id"]), "path": str(within(source["path"], store.project / ".groundwork/harness/router-observability"))}
        if "backfill_from" in source:
            require(type(source["backfill_from"]) in {int, float} and source["backfill_from"] <= store.now(), "invalid_backfill")
        sources.append(item)
    require(len({s["id"] for s in sources}) == len(sources), "duplicate_source")
    require(isinstance(policy["transcript_roots"], list) and len(policy["transcript_roots"]) <= 5, "transcript_root_limit")
    for root in policy["transcript_roots"]:
        path = normalized(root)
        require(path.is_dir() and path != Path(path.anchor), "invalid_transcript_root")
        roots.append(str(path))
    if "transcript_bindings" in policy:
        bindings = policy["transcript_bindings"]
        require(isinstance(bindings, list) and 0 < len(bindings) <= 5, "invalid_transcript_binding")
        for binding in bindings:
            fields(binding, ("session_id", "path", "format", "file_identity", "header_digest", "start_offset", "context_position", "context_digest", "verified_by"))
            identifier(binding["session_id"])
            path = normalized(binding["path"])
            require(str(path) == binding["path"] and any(path.is_relative_to(Path(root)) for root in roots), "locator_root_denied")
            require(binding["format"] == "codex.session_jsonl.v1" and binding["verified_by"] == "interactive_host_schema_check", "unsupported")
            require(isinstance(binding["file_identity"], list) and len(binding["file_identity"]) == 3, "invalid_transcript_binding")
            require(all(isinstance(binding[key], str) and len(binding[key]) == 64 and all(c in "0123456789abcdef" for c in binding[key]) for key in ("header_digest", "context_digest")), "invalid_transcript_binding")
            require(type(binding["context_position"]) is int and type(binding["start_offset"]) is int and 0 < binding["context_position"] < binding["start_offset"] <= path.stat().st_size, "invalid_transcript_binding")
        require(len({b["session_id"] for b in bindings}) == len(bindings), "duplicate_transcript_binding")
    return {**policy, "project_root": str(store.project), "assets": assets, "sources": sources, "transcript_roots": roots, "budgets": budgets}


def project_projection(store):
    """Caller holds the SQLite write transaction, including final replacement."""
    entries = []
    for row in store.db.execute("SELECT * FROM scopes WHERE state='active'"):
        policy = json.loads(row["policy"])
        if policy["semantic_source_locator"] and policy["expires_at"] > store.now():
            entries.append({"scope": row["id"], "generation": row["generation"], "project_root": policy["project_root"],
                            "transcript_roots": policy["transcript_roots"], "transcript_bindings": policy.get("transcript_bindings"), "expires_at": policy["expires_at"],
                            "semantic_source_locator": True, "locator_file": locator_path(store, row["id"]).name})
    path = store.project / PROJECTION
    atomic_write(path, canonical({"schema_version": "groundwork.semantic_source_policy.v1", "scopes": entries}))
    require(read_json(path) == {"schema_version": "groundwork.semantic_source_policy.v1", "scopes": entries}, "projection_verification_failed")
    store.db.execute("UPDATE scopes SET projection='disabled' WHERE state!='active'")
    store.db.execute("UPDATE scopes SET projection='enabled' WHERE state='active'")


def cleanup_scope(store, scope):
    for row in store.db.execute("SELECT path FROM exports WHERE scope=?", (scope,)).fetchall():
        remove(within(row["path"], store.root / "views"))
    path = locator_path(store, scope)
    if path.exists():
        remove(path)
    for table in ("facts", "work", "attempts", "sources", "exports", "messages"):
        store.db.execute(f"DELETE FROM {table} WHERE scope=?", (scope,))
    store.db.execute("UPDATE usage SET reserved=0 WHERE scope=?", (scope,))
    store.db.execute("UPDATE candidate_history SET body=NULL WHERE candidate IN (SELECT id FROM candidates WHERE scope=?)", (scope,))
    store.db.execute("UPDATE candidates SET body=NULL,adoption=NULL,state='closed' WHERE scope=?", (scope,))
    store.db.execute("UPDATE feedback SET body=NULL,result=? WHERE scope=?", (canonical(result("record_body_removed")), scope))
    store.db.execute("UPDATE scopes SET cleanup='complete',state='revoked' WHERE id=? AND state='revoking'", (scope,))


def recover(store):
    """Every command retries revocation; a failure never reopens consumers."""
    with store.tx():
        rows = store.db.execute("SELECT * FROM scopes WHERE state='active'").fetchall()
        for row in rows:
            if json.loads(row["policy"])["expires_at"] <= store.now():
                store.db.execute("UPDATE scopes SET state='revoking',generation=generation+1,projection='pending',cleanup='pending' WHERE id=?", (row["id"],))
    for row in store.db.execute("SELECT id,state FROM scopes WHERE state IN ('revoking','revoked')").fetchall():
        try:
            with store.tx():
                project_projection(store)
            with store.tx():
                cleanup_scope(store, row["id"])
        except (OSError, RSIError):
            with store.tx():
                store.diagnostic(row["id"], "revocation_recovery_incomplete")
    expire(store)


def expire(store):
    erased = 0
    with store.tx():
        for row in store.db.execute("SELECT path FROM exports WHERE expires<=?", (store.now(),)).fetchall():
            try:
                remove(within(row["path"], store.root / "views"))
                store.db.execute("DELETE FROM exports WHERE path=?", (row["path"],))
            except (OSError, RSIError):
                # Access is already denied by expiry; retry physical cleanup later.
                continue
        for table in ("facts", "work", "candidates", "candidate_history", "feedback", "messages"):
            erased += store.db.execute(f"UPDATE {table} SET body=NULL WHERE expires<=? AND body IS NOT NULL", (store.now(),)).rowcount
        store.db.execute("UPDATE candidates SET state='observing',adoption=NULL WHERE expires<=? AND state!='closed'", (store.now(),))
        store.db.execute("UPDATE work SET state='evidence_expired' WHERE expires<=?", (store.now(),))
        for scope in store.db.execute("SELECT id,policy FROM scopes").fetchall():
            policy = json.loads(scope["policy"])
            cutoff = store.now() - policy["budgets"]["derived_days"] * 86400
            for attempt in store.db.execute("SELECT * FROM attempts WHERE scope=? AND created<=? AND packet IS NOT NULL", (scope["id"], cutoff)).fetchall():
                store.release_attempt(attempt)
                store.db.execute("UPDATE attempts SET packet=NULL,result=NULL,state=CASE WHEN state='prepared' THEN 'expired' ELSE state END WHERE id=?", (attempt["id"],))
                erased += 1
            cutoff = store.now() - policy["budgets"]["facts_days"] * 86400
            # Source cursors remain the delivery tombstones; expired content and
            # historical summaries do not grow without the policy's retention bound.
            for table in ("facts", "messages"):
                erased += store.db.execute(f"DELETE FROM {table} WHERE scope=? AND expires<=?", (scope["id"], store.now())).rowcount
            store.db.execute("DELETE FROM diagnostics WHERE scope=? AND updated<=? AND reason!='cleanup_compaction_pending'", (scope["id"], cutoff))
            store.db.execute("DELETE FROM maintenance_invocations WHERE scope=? AND observed<=?", (scope["id"], cutoff))
            store.db.execute("DELETE FROM feedback WHERE scope=? AND expires<=? AND kind!='policy'", (scope["id"], store.now()))
            store.db.execute("DELETE FROM candidate_history WHERE candidate IN (SELECT id FROM candidates WHERE scope=?) AND created<=?", (scope["id"], cutoff))
            store.db.execute("DELETE FROM candidates WHERE scope=? AND created<=? AND body IS NULL", (scope["id"], cutoff))
            for source in store.db.execute("SELECT id,config FROM sources WHERE scope=? AND kind='official'", (scope["id"],)).fetchall():
                snapshot = json.loads(source["config"])
                if snapshot["expires_at"] <= store.now() or snapshot.get("checked_at", 0) <= cutoff:
                    if "notes" in snapshot or "question" in snapshot:
                        minimized = {key: snapshot[key] for key in ("identity", "url", "expires_at")}
                        minimized["expires_at"] = min(minimized["expires_at"], store.now())
                        store.db.execute("UPDATE sources SET config=?,status='stale' WHERE id=?", (canonical(minimized), source["id"]))
                        erased += 1
    # NULL removes content immediately; VACUUM reclaims sparse pages so expired
    # material cannot leave permanent physical-size backpressure. No live body or
    # deduplication tombstone is discarded to create room.
    capacities = [json.loads(row[0])["budgets"]["capacity_bytes"] for row in store.db.execute("SELECT policy FROM scopes")]
    pending = store.db.execute("SELECT 1 FROM diagnostics WHERE reason='cleanup_compaction_pending'").fetchone()
    if (erased or pending) and capacities and store.size() >= int(min(capacities) * .8):
        try:
            store.db.execute("VACUUM")
            store.db.execute("DELETE FROM diagnostics WHERE reason='cleanup_compaction_pending'")
        except sqlite3.Error:
            with store.tx():
                for row in store.db.execute("SELECT id FROM scopes").fetchall():
                    store.diagnostic(row["id"], "cleanup_compaction_pending")


def policy_feedback(store, scope, record):
    fields(record, ("id", "kind", "scope", "operation", "origin"), ("policy",))
    require(record["scope"] == scope and record["kind"] == "policy", "scope_mismatch")
    identifier(scope)
    identifier(record["id"])
    require(record["operation"] in {"enable", "revoke"}, "invalid_policy_operation")
    binding = digest({"scope": scope, "operation": record["operation"], "policy": record.get("policy")})
    decision_origin(record["origin"], scope, binding)
    with store.tx():
        replay = store.feedback_replay(record)
        if replay:
            return policy_status(store, scope)
        old = store.db.execute("SELECT * FROM scopes WHERE id=?", (scope,)).fetchone()
        if record["operation"] == "enable":
            require(not old or old["state"] != "revoking", "revocation_pending")
            policy = validate_policy(store, record.get("policy"))
            generation = old["generation"] + 1 if old else 1
            if old:
                # A changed authorization never carries old semantic material into
                # the new generation. Keep cursor/tombstone identity, not old body.
                for table in ("facts", "work", "messages", "candidates"):
                    store.db.execute(f"UPDATE {table} SET body=NULL WHERE scope=?", (scope,))
                store.db.execute("UPDATE work SET state='evidence_expired',expires=MIN(expires,?) WHERE scope=?", (store.now(), scope))
                store.db.execute("UPDATE candidates SET state='observing',adoption=NULL,expires=MIN(expires,?) WHERE scope=?", (store.now(), scope))
                store.db.execute("UPDATE candidate_history SET body=NULL WHERE candidate IN (SELECT id FROM candidates WHERE scope=?)", (scope,))
                store.db.execute("UPDATE attempts SET packet=NULL,result=NULL WHERE scope=?", (scope,))
                store.db.execute("UPDATE exports SET expires=? WHERE scope=?", (store.now(), scope))
            store.db.execute("""INSERT INTO scopes(id,generation,state,policy,created,updated) VALUES(?,?,'active',?,?,?)
                ON CONFLICT(id) DO UPDATE SET generation=excluded.generation,state='active',policy=excluded.policy,
                updated=excluded.updated,projection='pending',cleanup='pending'""",
                (scope, generation, canonical(policy), store.now(), store.now()))
            # Generation changes invalidate pending work; re-registration preserves existing cursors.
            for attempt in store.db.execute("SELECT * FROM attempts WHERE scope=? AND state='prepared'", (scope,)).fetchall():
                store.release_attempt(attempt)
                store.db.execute("UPDATE attempts SET state='superseded',packet=NULL WHERE id=?", (attempt["id"],))
            store.db.execute("UPDATE work SET state='pending' WHERE scope=? AND state='claimed'", (scope,))
        else:
            require(old is not None, "scope_missing")
            if old["state"] not in {"revoking", "revoked"}:
                store.db.execute("UPDATE scopes SET state='revoking',generation=generation+1,updated=?,projection='pending',cleanup='pending' WHERE id=?", (store.now(), scope))
        store.save_feedback(scope, record, result("policy_recorded"))
    # The revoking generation is committed before any projection/cleanup I/O.
    if record["operation"] == "revoke":
        recover(store)
    else:
        try:
            with store.tx():
                store.scope(scope, generation)
                project_projection(store)
            expire(store)
        except (OSError, RSIError):
            with store.tx():
                store.diagnostic(scope, "projection_incomplete")
    return policy_status(store, scope)


def policy_status(store, scope):
    row = store.scope(scope, active=False)
    return result("policy_" + row["state"], generation=row["generation"], consumer="enabled" if row["state"] == "active" else "disabled",
                  locator_projection=row["projection"], cleanup=row["cleanup"], schedule=json.loads(row["policy"])["schedule"])


def source_feedback(store, scope, record):
    fields(record, ("id", "kind", "scope", "source_id", "url", "checked_at", "expires_at", "product", "version", "notes", "substance_id", "assets", "question", "verified_by"))
    require(record["kind"] == "source" and record["scope"] == scope, "scope_mismatch")
    identifier(record["id"])
    identifier(record["source_id"])
    require(record["url"] in OFFICIAL_URLS, "official_source_denied")
    require(record["verified_by"] == "codex_host_web_tool", "source_verification_required")
    require(type(record["checked_at"]) in {int, float} and record["checked_at"] <= store.now() < record["expires_at"], "stale_source")
    filtered_text(record["notes"], 4096)
    require(len(record["notes"].encode()) <= 4096 and isinstance(record["question"], str) and record["question"], "invalid_source_snapshot")
    with store.tx():
        policy = json.loads(store.scope(scope)["policy"])
        replay = store.feedback_replay(record)
        if replay:
            return replay
        require(set(record["assets"]) <= {a["id"] for a in policy["assets"]} and record["assets"], "asset_denied")
        sid = scope + ":official:" + record["source_id"]
        old = store.db.execute("SELECT config FROM sources WHERE id=?", (sid,)).fetchone()
        # An interactive semantic substance identity prevents check-time or paraphrase-only reruns.
        identity = digest([record["url"], record["product"], record["version"], record["substance_id"], record["assets"]])
        snapshot = {**record, "notes_digest": digest(record["notes"]), "identity": identity}
        store.db.execute("""INSERT INTO sources(id,scope,kind,config,updated,status) VALUES(?,?,'official',?,?,'current')
            ON CONFLICT(id) DO UPDATE SET config=excluded.config,updated=excluded.updated,status='current'""", (sid, scope, canonical(snapshot), store.now()))
        response = result("source_unchanged" if old and json.loads(old["config"])["identity"] == identity else "source_registered")
        store.save_feedback(scope, record, response)
        return response
