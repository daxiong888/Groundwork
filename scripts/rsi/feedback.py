"""Candidate decisions and evidence-bound feedback receipts."""

import hashlib
import json
from pathlib import Path
import re

from .schema import DEFAULTS, RSIError, canonical, decision_origin, digest, fields, identifier, require, result
from .security import open_regular, read_bytes


DECISIONS = {"accept": "accepted", "reject": "closed", "observe": "observing"}
RECEIPT_FORMATS = {
    "implementation_start", "implementation", "check", "adoption", "recurrence", "candidate_trial",
}
ADOPTION_LAYERS = {"source", "installed", "loaded"}
EXECUTION_SCHEMA = "groundwork_rsi_execution_receipt.v1"


def _sha256(value, reason="invalid_digest"):
    require(isinstance(value, str) and re.fullmatch(r"[0-9a-f]{64}", value), reason)
    return value


def _text(value, reason, limit=2048):
    require(isinstance(value, str) and 0 < len(value) <= limit, reason)
    return value


def _integer(value, reason):
    require(isinstance(value, int) and not isinstance(value, bool), reason)
    return value


def _file_digest(path, limit):
    value = hashlib.sha256()
    total = 0
    with open_regular(path) as stream:
        while True:
            chunk = stream.read(min(65536, limit - total + 1))
            if not chunk:
                break
            total += len(chunk)
            require(total <= limit, "asset_over_limit")
            value.update(chunk)
    return value.hexdigest()


def _policy_assets(scope_row):
    policy = json.loads(scope_row["policy"])
    assets = policy.get("assets")
    require(isinstance(assets, list), "policy_assets_required")
    result_assets = {}
    for asset in assets:
        require(isinstance(asset, dict) and set(asset) == {"id", "path"}, "invalid_policy_asset")
        identifier(asset["id"])
        require(asset["id"] not in result_assets, "duplicate_policy_asset")
        require(isinstance(asset["path"], str) and Path(asset["path"]).is_absolute(),
                "authorized_absolute_path_required")
        result_assets[asset["id"]] = asset["path"]
    configured = policy.get("budgets", {}).get("capacity_bytes", DEFAULTS["capacity_bytes"])
    _integer(configured, "invalid_asset_limit")
    require(configured > 0, "invalid_asset_limit")
    return result_assets, min(configured, DEFAULTS["capacity_bytes"])


def _asset_digest(assets, asset_id, limit):
    identifier(asset_id)
    require(asset_id in assets, "asset_not_authorized")
    return _file_digest(assets[asset_id], limit)


def _candidate_body(row):
    require(row["body"] is not None, "candidate_body_expired")
    try:
        body = json.loads(row["body"])
    except (TypeError, json.JSONDecodeError):
        raise RSIError("candidate_body_invalid") from None
    require(isinstance(body, dict), "candidate_body_invalid")
    target = body.get("target")
    require(isinstance(target, dict), "candidate_target_missing")
    require(set(target) == {"asset_id", "location", "owner", "baseline_digest"}, "candidate_target_invalid")
    identifier(target["asset_id"])
    _sha256(target["baseline_digest"], "candidate_baseline_invalid")
    acceptance = body.get("acceptance")
    require(isinstance(acceptance, list) and acceptance, "candidate_acceptance_missing")
    acceptance_ids = set()
    for item in acceptance:
        require(isinstance(item, dict) and set(item) == {"id", "description"}, "candidate_acceptance_invalid")
        identifier(item["id"])
        _text(item["description"], "candidate_acceptance_invalid")
        require(item["id"] not in acceptance_ids, "duplicate_acceptance_id")
        acceptance_ids.add(item["id"])
    require(isinstance(body.get("behavior_evidence_required"), bool), "behavior_evidence_flag_required")
    return body, target, acceptance_ids


def _binding(scope, candidate_id, revision, proposal_digest):
    return digest({
        "candidate": candidate_id,
        "revision": revision,
        "proposal_digest": proposal_digest,
        "scope": scope,
    })


def _base_record(record, scope, candidate_id, revision, proposal_digest):
    identifier(record["id"])
    require(record["scope"] == scope, "feedback_scope_mismatch")
    require(record["proposal_digest"] == proposal_digest, "proposal_digest_mismatch")
    if "candidate" in record:
        require(record["candidate"] == candidate_id, "candidate_binding_mismatch")
    if "revision" in record:
        require(record["revision"] == revision, "candidate_revision_mismatch")


def _decision_record(record, scope, candidate_id, revision, proposal_digest):
    fields(record, ("id", "kind", "scope", "proposal_digest", "decision", "origin"),
           ("candidate", "revision"))
    require(record["kind"] == "decision", "unsupported_feedback_kind")
    _base_record(record, scope, candidate_id, revision, proposal_digest)
    require(record["decision"] in DECISIONS, "invalid_decision")
    decision_origin(record["origin"], scope, _binding(scope, candidate_id, revision, proposal_digest))


def _receipt_record(record, scope, candidate_id, revision, proposal_digest):
    common = {"id", "kind", "scope", "candidate", "revision", "proposal_digest", "format", "decision_id"}
    by_format = {
        "implementation_start": ({"baseline_digest", "current_digest"}, set()),
        "implementation": ({"baseline_digest", "actual_digest", "start_id"}, set()),
        "check": ({"result_digest", "acceptance_id", "check_id", "execution_source", "invocation_id",
                   "output_asset_id"}, set()),
        "adoption": ({"result_digest", "layer", "artifact_digest", "check_id", "execution_source",
                      "invocation_id", "output_asset_id"}, set()),
        "recurrence": ({"result_digest", "event_ref", "check_id", "execution_source", "invocation_id",
                        "output_asset_id"}, set()),
        "candidate_trial": ({"result_digest", "change_digest", "expectation_digest", "model",
                             "run_id", "slot_id", "receipt_asset_id", "receipt_digest"}, set()),
    }
    require(isinstance(record, dict), "object_required")
    receipt_format = record.get("format")
    require(receipt_format in RECEIPT_FORMATS, "unsupported_receipt_format")
    required, optional = by_format[receipt_format]
    require(common | required <= record.keys(), "missing_fields")
    require(record.keys() <= common | required | optional, "unexpected_fields")
    require(record["kind"] == "receipt", "unsupported_feedback_kind")
    _base_record(record, scope, candidate_id, revision, proposal_digest)
    identifier(record["decision_id"])

    if receipt_format == "implementation_start":
        _sha256(record["baseline_digest"])
        _sha256(record["current_digest"])
    elif receipt_format == "implementation":
        _sha256(record["baseline_digest"])
        _sha256(record["actual_digest"])
        identifier(record["start_id"])
    elif receipt_format == "check":
        _sha256(record["result_digest"])
        identifier(record["acceptance_id"])
        identifier(record["check_id"])
        identifier(record["execution_source"])
        identifier(record["invocation_id"])
        identifier(record["output_asset_id"])
    elif receipt_format == "adoption":
        _sha256(record["result_digest"])
        require(record["layer"] in ADOPTION_LAYERS, "invalid_adoption_layer")
        _sha256(record["artifact_digest"], "invalid_artifact_digest")
        identifier(record["check_id"])
        identifier(record["execution_source"])
        identifier(record["invocation_id"])
        identifier(record["output_asset_id"])
    elif receipt_format == "recurrence":
        _sha256(record["result_digest"])
        identifier(record["event_ref"])
        identifier(record["check_id"])
        identifier(record["execution_source"])
        identifier(record["invocation_id"])
        identifier(record["output_asset_id"])
    else:
        _sha256(record["result_digest"])
        _sha256(record["change_digest"])
        _sha256(record["expectation_digest"], "invalid_expectation_digest")
        _text(record["model"], "invalid_model", 256)
        identifier(record["run_id"])
        identifier(record["slot_id"])
        identifier(record["receipt_asset_id"])
        _sha256(record["receipt_digest"], "invalid_receipt_digest")


def _json(value, reason):
    require(value is not None, "feedback_evidence_expired")
    try:
        parsed = json.loads(value)
    except (TypeError, json.JSONDecodeError):
        raise RSIError(reason) from None
    require(isinstance(parsed, dict), reason)
    return parsed


def _accepted_decision(db, candidate_id, revision, decision_id, proposal_digest):
    row = db.execute(
        "SELECT * FROM feedback WHERE id=? AND candidate=? AND revision=? AND kind='decision'",
        (decision_id, candidate_id, revision),
    ).fetchone()
    require(row is not None, "accepted_decision_missing")
    record = _json(row["body"], "feedback_body_invalid")
    recorded_result = _json(row["result"], "feedback_result_invalid")
    require(record.get("decision") == "accept" and record.get("proposal_digest") == proposal_digest
            and recorded_result.get("state") == "accepted", "accepted_decision_mismatch")
    return row


def _receipts(db, candidate_id, revision):
    rows = db.execute(
        "SELECT rowid,body,result FROM feedback "
        "WHERE candidate=? AND revision=? AND kind='receipt' ORDER BY created,rowid",
        (candidate_id, revision),
    )
    return [(_json(row["body"], "feedback_body_invalid"),
             _json(row["result"], "feedback_result_invalid")) for row in rows]


def _checks_passed(records, result_digest, acceptance_ids, behavior_required, current=None):
    latest = {}
    for record, response in records + ([] if current is None else [current]):
        if record.get("format") == "check" and record.get("result_digest") == result_digest:
            latest[record.get("acceptance_id")] = response
    complete = all(item in latest and latest[item].get("exit_code") == 0 for item in acceptance_ids)
    behavior = any(
        item in latest and latest[item].get("exit_code") == 0
        and latest[item].get("evidence_class") == "behavior"
        for item in acceptance_ids
    )
    return complete and (not behavior_required or behavior)


def _adoption(value, result_digest):
    if not value:
        return {"result_digest": result_digest, "layers": {}}
    try:
        adoption = json.loads(value)
    except (TypeError, json.JSONDecodeError):
        raise RSIError("adoption_evidence_invalid") from None
    require(isinstance(adoption, dict), "adoption_evidence_invalid")
    if adoption.get("result_digest") != result_digest or not isinstance(adoption.get("layers"), dict):
        return {"result_digest": result_digest, "layers": {}}
    return adoption


def _execution_receipt(record, expected_kind, assets, asset_limit):
    receipt_path = assets.get(record["output_asset_id"])
    require(receipt_path is not None, "asset_not_authorized")
    raw = read_bytes(receipt_path, min(DEFAULTS["record_bytes"], asset_limit))
    try:
        receipt = json.loads(raw)
    except (UnicodeError, json.JSONDecodeError):
        raise RSIError("invalid_execution_receipt") from None
    required = {
        "schema", "kind", "execution_source", "invocation_id", "check_id", "result_digest",
        "exit_code", "evidence_class", "output",
    }
    if expected_kind == "check":
        required.add("acceptance_id")
    elif expected_kind == "adoption":
        required.update({"layer", "artifact_digest"})
    else:
        required.update({"event_ref", "trigger_matched", "effective_layer", "effective_digest"})
    require(isinstance(receipt, dict) and set(receipt) == required, "invalid_execution_receipt")
    require(receipt["schema"] == EXECUTION_SCHEMA and receipt["kind"] == expected_kind,
            "invalid_execution_receipt")
    require(receipt["execution_source"] == record["execution_source"]
            and receipt["invocation_id"] == record["invocation_id"], "execution_binding_mismatch")
    require(receipt["check_id"] == record["check_id"]
            and receipt["result_digest"] == record["result_digest"], "check_binding_mismatch")
    _integer(receipt["exit_code"], "invalid_exit_code")
    expected_classes = {
        "check": {"source_check", "behavior"},
        "adoption": {"adoption"},
        "recurrence": {"recurrence"},
    }
    require(receipt["evidence_class"] in expected_classes[expected_kind], "invalid_evidence_class")
    if expected_kind == "check":
        require(receipt["acceptance_id"] == record["acceptance_id"], "check_binding_mismatch")
    elif expected_kind == "adoption":
        require(receipt["layer"] == record["layer"]
                and receipt["artifact_digest"] == record["artifact_digest"], "adoption_binding_mismatch")
    else:
        require(receipt["event_ref"] == record["event_ref"], "recurrence_binding_mismatch")
        require(isinstance(receipt["trigger_matched"], bool), "invalid_trigger_match")
        require(receipt["effective_layer"] is None or receipt["effective_layer"] == "loaded",
                "invalid_effective_layer")
        require(receipt["effective_digest"] is None
                or isinstance(receipt["effective_digest"], str)
                and re.fullmatch(r"[0-9a-f]{64}", receipt["effective_digest"]),
                "invalid_effective_digest")
    output = receipt["output"]
    require(isinstance(output, dict) and set(output) == {"asset_id", "digest"}, "invalid_execution_output")
    identifier(output["asset_id"])
    _sha256(output["digest"], "invalid_output_digest")
    require(_asset_digest(assets, output["asset_id"], asset_limit) == output["digest"],
            "execution_output_mismatch")
    return receipt, digest(raw)


def _ensure_invocation_unused(records, record):
    for prior, _ in records:
        if prior.get("format") in {"check", "adoption", "recurrence"}:
            require(not (prior.get("execution_source") == record["execution_source"]
                         and prior.get("invocation_id") == record["invocation_id"]),
                    "execution_invocation_reused")


def _implementation_start(db, candidate_id, revision, start_id, proposal_digest, decision_id):
    row = db.execute(
        "SELECT body,result FROM feedback WHERE id=? AND candidate=? AND revision=? AND kind='receipt'",
        (start_id, candidate_id, revision),
    ).fetchone()
    require(row is not None, "implementation_start_missing")
    record = _json(row["body"], "feedback_body_invalid")
    response = _json(row["result"], "feedback_result_invalid")
    require(record.get("format") == "implementation_start"
            and record.get("proposal_digest") == proposal_digest
            and record.get("decision_id") == decision_id
            and response.get("reason") == "implementation_started", "implementation_start_mismatch")
    return record


def _ensure_start_unused(records, start_id):
    require(not any(record.get("format") == "implementation" and record.get("start_id") == start_id
                    for record, _ in records), "implementation_start_used")


def _recurrence_fact(db, scope, event_ref, now):
    row = db.execute("SELECT body,expires FROM facts WHERE id=? AND scope=?", (event_ref, scope)).fetchone()
    require(row is not None, "recurrence_fact_missing")
    require(row["expires"] > now, "recurrence_fact_expired")
    return _json(row["body"], "recurrence_fact_invalid")


def _candidate_trial(record, assets, asset_limit):
    path = assets.get(record["receipt_asset_id"])
    require(path is not None, "asset_not_authorized")
    raw = read_bytes(path, min(asset_limit, DEFAULTS["record_bytes"] * 16))
    actual_digest = digest(raw)
    if actual_digest != record["receipt_digest"]:
        return False, "receipt_digest_mismatch", actual_digest
    try:
        parsed = json.loads(raw)
        records = [parsed]
    except (UnicodeError, json.JSONDecodeError):
        records = []
        try:
            for line in raw.decode("utf-8").splitlines():
                if line.strip():
                    records.append(json.loads(line))
        except (UnicodeError, json.JSONDecodeError):
            return False, "unsupported_slot_result", actual_digest
    matches = [
        item for item in records
        if isinstance(item, dict)
        and item.get("record_type") == "slot_result"
        and item.get("run_id") == record["run_id"]
        and item.get("slot_id") == record["slot_id"]
    ]
    if len(matches) != 1:
        return False, "slot_result_not_unique", actual_digest
    slot = matches[0]
    attempt = slot.get("attempt")
    if not isinstance(attempt, dict):
        return False, "attempt_missing", actual_digest
    bindings = attempt.get("bindings")
    actor = bindings.get("actor") if isinstance(bindings, dict) else None
    recorded_hash = attempt.get("receipt_sha256")
    attempt_body = dict(attempt)
    attempt_body.pop("receipt_sha256", None)
    valid = (
        slot.get("evidence_class") == "candidate_direction"
        and slot.get("arm") == "candidate"
        and slot.get("valid") is True
        and slot.get("valid_attempt_receipt_hash") == recorded_hash
        and attempt.get("run_id") == record["run_id"]
        and attempt.get("slot_id") == record["slot_id"]
        and attempt.get("arm") == "candidate"
        and attempt.get("valid") is True
        and attempt.get("failure_code") is None
        and attempt.get("cleanup_ok") is True
        and attempt.get("cleanup_errors") == []
        and attempt.get("model_dispatches") == 1
        and recorded_hash == digest(attempt_body)
        and isinstance(bindings, dict)
        and bindings.get("package_sha256") == record["change_digest"]
        and bindings.get("rubric_sha256") == record["expectation_digest"]
        and isinstance(actor, dict)
        and actor.get("model") == record["model"]
    )
    return valid, "valid_slot_result" if valid else "slot_result_binding_mismatch", actual_digest


def _response(reason, candidate_id, revision, state, **values):
    coverage = {
        "status": "complete", "scope": "candidate_feedback", "candidate": candidate_id, "revision": revision,
    }
    return result(reason, coverage, candidate=candidate_id, revision=revision, state=state, **values)


def _reopen_work(store, row):
    store.db.execute(
        "UPDATE work SET state='pending',revision=revision+1,updated=? "
        "WHERE id=? AND scope=? AND expires>? AND body IS NOT NULL",
        (store.now(), row["work_id"], row["scope"], store.now()),
    )


def _collecting(store, row, record, candidate_id, revision, reason="target_drift"):
    store.db.execute("UPDATE candidates SET state='collecting',adoption=NULL,updated=? WHERE id=?",
                     (store.now(), candidate_id))
    _reopen_work(store, row)
    response = _response(reason, candidate_id, revision, "collecting")
    store.save_feedback(row["scope"], record, response, candidate_id, revision)
    return response


def handle_feedback(store, scope, candidate_id, revision, record):
    """Validate and record one candidate decision or bounded feedback receipt."""
    identifier(scope)
    identifier(candidate_id)
    _integer(revision, "invalid_revision")
    require(isinstance(record, dict), "object_required")
    require(record.get("kind") in {"decision", "receipt"}, "unsupported_feedback_kind")

    with store.tx() as db:
        scope_row = store.scope(scope)
        row = db.execute("SELECT * FROM candidates WHERE id=? AND scope=?", (candidate_id, scope)).fetchone()
        require(row is not None, "candidate_missing")
        require(row["expires"] > store.now(), "candidate_expired")
        require(row["revision"] == revision, "candidate_revision_mismatch")
        proposal_digest = row["proposal_digest"]
        body, target, acceptance_ids = _candidate_body(row)
        assets, asset_limit = _policy_assets(scope_row)
        require(target["asset_id"] in assets, "candidate_asset_not_authorized")

        if record["kind"] == "decision":
            _decision_record(record, scope, candidate_id, revision, proposal_digest)
        else:
            _receipt_record(record, scope, candidate_id, revision, proposal_digest)
        replay = store.feedback_replay(record)
        if replay is not None:
            return replay

        if record["kind"] == "decision":
            existing = db.execute(
                "SELECT id FROM feedback WHERE candidate=? AND revision=? AND kind='decision'",
                (candidate_id, revision),
            ).fetchone()
            require(existing is None, "decision_already_recorded")
            require(row["state"] == "ready", "candidate_not_ready")
            if record["decision"] == "accept" and _asset_digest(
                    assets, target["asset_id"], asset_limit) != target["baseline_digest"]:
                return _collecting(store, row, record, candidate_id, revision)
            state = DECISIONS[record["decision"]]
            db.execute("UPDATE candidates SET state=?,updated=? WHERE id=?", (state, store.now(), candidate_id))
            response = _response("decision_recorded", candidate_id, revision, state,
                                 decision=record["decision"], decision_id=record["id"])
            store.save_feedback(scope, record, response, candidate_id, revision)
            return response

        _accepted_decision(db, candidate_id, revision, record["decision_id"], proposal_digest)
        receipt_format = record["format"]
        require(row["state"] in {"accepted", "validating", "watching"}, "candidate_not_accepted")

        if receipt_format == "implementation_start":
            require(record["baseline_digest"] == target["baseline_digest"], "implementation_baseline_mismatch")
            expected = row["result_digest"] or target["baseline_digest"]
            require(record["current_digest"] == expected, "implementation_current_mismatch")
            if _asset_digest(assets, target["asset_id"], asset_limit) != expected:
                return _collecting(store, row, record, candidate_id, revision)
            response = _response("implementation_started", candidate_id, revision, row["state"],
                                 start_id=record["id"], current_digest=expected)
            store.save_feedback(scope, record, response, candidate_id, revision)
            return response

        if receipt_format == "implementation":
            require(record["baseline_digest"] == target["baseline_digest"], "implementation_baseline_mismatch")
            start = _implementation_start(
                db, candidate_id, revision, record["start_id"], proposal_digest, record["decision_id"],
            )
            records = _receipts(db, candidate_id, revision)
            _ensure_start_unused(records, record["start_id"])
            expected = row["result_digest"] or target["baseline_digest"]
            require(start["current_digest"] == expected, "implementation_start_stale")
            actual = _asset_digest(assets, target["asset_id"], asset_limit)
            require(actual == record["actual_digest"], "implementation_result_mismatch")
            require(actual != expected, "implementation_unchanged")
            db.execute(
                "UPDATE candidates SET state='validating',result_digest=?,adoption=NULL,updated=? WHERE id=?",
                (actual, store.now(), candidate_id),
            )
            response = _response("implementation_recorded", candidate_id, revision, "validating",
                                 result_digest=actual, start_id=record["start_id"])
            store.save_feedback(scope, record, response, candidate_id, revision)
            return response

        require(row["result_digest"] is not None, "implementation_missing")
        if _asset_digest(assets, target["asset_id"], asset_limit) != row["result_digest"]:
            return _collecting(store, row, record, candidate_id, revision)
        require(record["result_digest"] == row["result_digest"], "receipt_result_mismatch")

        if receipt_format == "check":
            require(record["acceptance_id"] in acceptance_ids, "unknown_acceptance_id")
            records = _receipts(db, candidate_id, revision)
            _ensure_invocation_unused(records, record)
            execution, execution_digest = _execution_receipt(record, "check", assets, asset_limit)
            observed = {"exit_code": execution["exit_code"], "evidence_class": execution["evidence_class"]}
            adoption = _adoption(row["adoption"], row["result_digest"])
            watching = (
                _checks_passed(records, row["result_digest"], acceptance_ids,
                               body["behavior_evidence_required"], (record, observed))
                and "loaded" in adoption["layers"]
            )
            state = "watching" if watching else "validating"
            db.execute("UPDATE candidates SET state=?,updated=? WHERE id=?", (state, store.now(), candidate_id))
            reason = "watching" if watching else ("check_recorded" if execution["exit_code"] == 0 else "check_failed")
            response = _response(
                reason, candidate_id, revision, state, result_digest=row["result_digest"],
                acceptance_id=record["acceptance_id"], exit_code=execution["exit_code"],
                evidence_class=execution["evidence_class"], execution_receipt_digest=execution_digest,
                execution_output=execution["output"],
            )

        elif receipt_format == "adoption":
            records = _receipts(db, candidate_id, revision)
            _ensure_invocation_unused(records, record)
            execution, execution_digest = _execution_receipt(record, "adoption", assets, asset_limit)
            if record["layer"] == "source":
                require(record["artifact_digest"] == row["result_digest"], "source_adoption_mismatch")
            adoption = _adoption(row["adoption"], row["result_digest"])
            if execution["exit_code"] == 0:
                adoption["layers"][record["layer"]] = {
                    "artifact_digest": record["artifact_digest"],
                    "receipt_id": record["id"],
                    "invocation_id": record["invocation_id"],
                }
            else:
                adoption["layers"].pop(record["layer"], None)
            watching = (
                _checks_passed(records, row["result_digest"], acceptance_ids,
                               body["behavior_evidence_required"])
                and "loaded" in adoption["layers"]
            )
            state = "watching" if watching else "validating"
            db.execute("UPDATE candidates SET state=?,adoption=?,updated=? WHERE id=?",
                       (state, canonical(adoption), store.now(), candidate_id))
            reason = "watching" if watching else (
                "adoption_recorded" if execution["exit_code"] == 0 else "adoption_check_failed"
            )
            response = _response(
                reason, candidate_id, revision, state, result_digest=row["result_digest"],
                adoption_layer=record["layer"], exit_code=execution["exit_code"],
                evidence_class="adoption", execution_receipt_digest=execution_digest,
                execution_output=execution["output"],
            )

        elif receipt_format == "candidate_trial":
            valid, attachment_reason, actual_digest = _candidate_trial(record, assets, asset_limit)
            response = _response(
                "receipt_attached" if valid else "attachment_unknown",
                candidate_id, revision, row["state"], result_digest=row["result_digest"],
                evidence_class="candidate_direction" if valid else "unknown",
                attachment_reason=attachment_reason, receipt_digest=actual_digest,
                trial_run_id=record["run_id"], trial_slot_id=record["slot_id"],
            )

        else:
            require(row["state"] == "watching", "candidate_not_watching")
            _recurrence_fact(db, scope, record["event_ref"], store.now())
            records = _receipts(db, candidate_id, revision)
            _ensure_invocation_unused(records, record)
            execution, execution_digest = _execution_receipt(record, "recurrence", assets, asset_limit)
            adoption = _adoption(row["adoption"], row["result_digest"])
            loaded = adoption["layers"].get("loaded")
            attributed = (
                execution["exit_code"] == 0
                and execution["trigger_matched"] is True
                and execution["effective_layer"] == "loaded"
                and loaded is not None
                and execution["effective_digest"] == loaded["artifact_digest"]
            )
            state = "collecting" if attributed else "watching"
            db.execute("UPDATE candidates SET state=?,updated=? WHERE id=?", (state, store.now(), candidate_id))
            if attributed:
                _reopen_work(store, row)
            response = _response("recurrence_confirmed" if attributed else "recurrence_unattributed",
                                 candidate_id, revision, state, result_digest=row["result_digest"],
                                 event_ref=record["event_ref"], attributed=attributed,
                                 exit_code=execution["exit_code"], evidence_class="recurrence",
                                 execution_receipt_digest=execution_digest,
                                 execution_output=execution["output"])

        store.save_feedback(scope, record, response, candidate_id, revision)
        return response
