#!/usr/bin/env python3
"""Run a sealed, pairwise Candidate trial for a local Codex plugin.

This module is deliberately transport-only.  It binds packages and execution
inputs, runs actors in fresh workspaces, records receipts, and cleans up.  It
does not score responses or make a Candidate decision.
"""

from __future__ import annotations

import argparse
import dataclasses
import datetime as dt
import hashlib
import json
import os
import re
import shutil
import signal
import subprocess
import sys
import time
import tomllib
import uuid
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping, Sequence


EVIDENCE_CLASS = "candidate_direction"
PHASES = ("d1", "heldback")
IDENTIFIER = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")


class TrialError(RuntimeError):
    """A fail-closed trial configuration or transport error."""

    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code


@dataclasses.dataclass(frozen=True)
class ProcessResult:
    argv: tuple[str, ...]
    returncode: int
    stdout: str
    stderr: str
    timed_out: bool
    duration_seconds: float


@dataclasses.dataclass(frozen=True)
class Arm:
    name: str
    source_root: Path
    source_sha256: str
    marketplace: str


@dataclasses.dataclass(frozen=True)
class Project:
    name: str
    root: Path
    skeleton_sha256: str
    workspace_parent: Path


@dataclasses.dataclass(frozen=True)
class Case:
    name: str
    prompt_path: Path
    prompt_sha256: str
    rubric_path: Path
    rubric_sha256: str
    task_state_root: Path
    task_state_sha256: str


@dataclasses.dataclass(frozen=True)
class Slot:
    slot_id: str
    phase: str
    pair: str
    case: str
    arm: str
    project: str
    order: int


@dataclasses.dataclass(frozen=True)
class Actor:
    model: str
    profile: str
    sandbox: str
    approval_policy: str
    timeout_seconds: float


@dataclasses.dataclass(frozen=True)
class TrialConfig:
    path: Path
    epoch_id: str
    trial_root: Path
    plugin_id: str
    codex_binary: str
    auth_identity_label: str
    actor: Actor
    arms: Mapping[str, Arm]
    projects: Mapping[str, Project]
    cases: Mapping[str, Case]
    slots: tuple[Slot, ...]
    gate_receipt_path: Path
    d1_binary_fact_names: tuple[str, ...]


ProcessRunner = Callable[[Sequence[str], Path | None, str | None, float], ProcessResult]


def _required_text(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise TrialError("config_invalid", f"{field} must be a non-empty string")
    return value.strip()


def _identifier(value: Any, field: str) -> str:
    text = _required_text(value, field)
    if not IDENTIFIER.fullmatch(text):
        raise TrialError("config_invalid", f"{field} must be a safe identifier")
    return text


def _selector_component(value: Any, field: str) -> str:
    text = _required_text(value, field)
    if "@" in text or text.startswith("-"):
        raise TrialError("config_invalid", f"{field} is not a safe plugin selector component")
    return text


def _required_int(value: Any, field: str, *, minimum: int = 0) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
        raise TrialError("config_invalid", f"{field} must be an integer >= {minimum}")
    return value


def _required_number(value: Any, field: str, *, minimum: float = 0.0) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or value <= minimum:
        raise TrialError("config_invalid", f"{field} must be greater than {minimum}")
    return float(value)


def _absolute_path(value: Any, field: str) -> Path:
    raw = _required_text(value, field)
    path = Path(raw).expanduser()
    if not path.is_absolute():
        raise TrialError("config_invalid", f"{field} must be an absolute path")
    return path.resolve(strict=False)


def _relative_path(value: Any, field: str) -> Path:
    raw = _required_text(value, field)
    path = Path(raw)
    if path.is_absolute() or any(part in ("", ".", "..") for part in path.parts):
        raise TrialError("config_invalid", f"{field} must be a safe relative path")
    return path


def _sha256(value: Any, field: str) -> str:
    digest = _required_text(value, field).lower()
    if len(digest) != 64 or any(ch not in "0123456789abcdef" for ch in digest):
        raise TrialError("config_invalid", f"{field} must be a SHA-256 hex digest")
    return digest


def _mapping(value: Any, field: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise TrialError("config_invalid", f"{field} must be a table")
    return value


def _is_within(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
    except ValueError:
        return False
    return True


def file_digest(path: Path) -> str:
    if not path.is_file():
        raise TrialError("input_missing", f"required file is missing: {path}")
    hasher = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def tree_digest(root: Path, excluded: Iterable[Path] = ()) -> str:
    """Hash path names, file bytes, and symlink targets for a directory tree."""

    if not root.is_dir():
        raise TrialError("input_missing", f"required directory is missing: {root}")
    excluded_parts = tuple(path.parts for path in excluded)

    def is_excluded(relative: Path) -> bool:
        parts = relative.parts
        return any(parts[: len(prefix)] == prefix for prefix in excluded_parts)

    hasher = hashlib.sha256()
    entries = sorted(root.rglob("*"), key=lambda path: path.relative_to(root).as_posix())
    for path in entries:
        relative = path.relative_to(root)
        if is_excluded(relative):
            continue
        encoded_path = relative.as_posix().encode("utf-8")
        if path.is_symlink():
            hasher.update(b"L\0" + encoded_path + b"\0")
            hasher.update(os.readlink(path).encode("utf-8") + b"\0")
        elif path.is_file():
            hasher.update(b"F\0" + encoded_path + b"\0")
            with path.open("rb") as handle:
                for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                    hasher.update(chunk)
            hasher.update(b"\0")
    return hasher.hexdigest()


def reject_symlinks(root: Path, label: str, excluded: Iterable[Path] = ()) -> None:
    excluded_parts = tuple(path.parts for path in excluded)

    def allowed(path: Path) -> bool:
        parts = path.relative_to(root).parts
        return any(parts[: len(prefix)] == prefix for prefix in excluded_parts)

    if any(path.is_symlink() and not allowed(path) for path in root.rglob("*")):
        raise TrialError("symlink_not_allowed", f"{label} must not contain symlinks")


def _parse_actor(raw: Mapping[str, Any]) -> Actor:
    actor = _mapping(raw.get("actor"), "actor")
    sandbox = _required_text(actor.get("sandbox"), "actor.sandbox")
    if sandbox not in {"read-only", "workspace-write"}:
        raise TrialError("config_invalid", "actor.sandbox must not use danger-full-access")
    return Actor(
        model=_required_text(actor.get("model"), "actor.model"),
        profile=_required_text(actor.get("profile"), "actor.profile"),
        sandbox=sandbox,
        approval_policy=_required_text(actor.get("approval_policy"), "actor.approval_policy"),
        timeout_seconds=_required_number(actor.get("timeout_seconds"), "actor.timeout_seconds"),
    )


def _parse_arms(raw: Mapping[str, Any]) -> Mapping[str, Arm]:
    arms_raw = _mapping(raw.get("arms"), "arms")
    if set(arms_raw) != {"baseline", "candidate"}:
        raise TrialError("config_invalid", "arms must contain exactly baseline and candidate")
    arms: dict[str, Arm] = {}
    for name in ("baseline", "candidate"):
        item = _mapping(arms_raw[name], f"arms.{name}")
        arms[name] = Arm(
            name=name,
            source_root=_absolute_path(item.get("source_root"), f"arms.{name}.source_root"),
            source_sha256=_sha256(item.get("source_sha256"), f"arms.{name}.source_sha256"),
            marketplace=_selector_component(
                item.get("marketplace"), f"arms.{name}.marketplace"
            ),
        )
    if arms["baseline"].source_sha256 == arms["candidate"].source_sha256:
        raise TrialError("config_invalid", "baseline and candidate package hashes must differ")
    return arms


def _parse_projects(raw: Mapping[str, Any]) -> Mapping[str, Project]:
    projects_raw = _mapping(raw.get("projects"), "projects")
    if len(projects_raw) != 2:
        raise TrialError("config_invalid", "exactly two neutral projects are required")
    projects: dict[str, Project] = {}
    for name, value in projects_raw.items():
        item = _mapping(value, f"projects.{name}")
        workspace_parent = _relative_path(
            item.get("workspace_parent"), f"projects.{name}.workspace_parent"
        )
        if len(workspace_parent.parts) != 1:
            raise TrialError(
                "config_invalid", f"projects.{name}.workspace_parent must be one path component"
            )
        if "mutable_paths" in item:
            raise TrialError("config_invalid", "mutable_paths is not supported")
        projects[name] = Project(
            name=name,
            root=_absolute_path(item.get("root"), f"projects.{name}.root"),
            skeleton_sha256=_sha256(
                item.get("skeleton_sha256"), f"projects.{name}.skeleton_sha256"
            ),
            workspace_parent=workspace_parent,
        )
    if len({project.root for project in projects.values()}) != 2:
        raise TrialError("config_invalid", "neutral project roots must be distinct")
    return projects


def _parse_cases(raw: Mapping[str, Any]) -> Mapping[str, Case]:
    cases_raw = _mapping(raw.get("cases"), "cases")
    required = {"D1", "H1", "S1"}
    if set(cases_raw) != required:
        raise TrialError("config_invalid", "cases must contain exactly D1, H1, and S1")
    cases: dict[str, Case] = {}
    for name in sorted(required):
        item = _mapping(cases_raw[name], f"cases.{name}")
        cases[name] = Case(
            name=name,
            prompt_path=_absolute_path(item.get("prompt_path"), f"cases.{name}.prompt_path"),
            prompt_sha256=_sha256(item.get("prompt_sha256"), f"cases.{name}.prompt_sha256"),
            rubric_path=_absolute_path(item.get("rubric_path"), f"cases.{name}.rubric_path"),
            rubric_sha256=_sha256(item.get("rubric_sha256"), f"cases.{name}.rubric_sha256"),
            task_state_root=_absolute_path(
                item.get("task_state_root"), f"cases.{name}.task_state_root"
            ),
            task_state_sha256=_sha256(
                item.get("task_state_sha256"), f"cases.{name}.task_state_sha256"
            ),
        )
    return cases


def _parse_slots(raw: Mapping[str, Any]) -> tuple[Slot, ...]:
    slots_raw = raw.get("slots")
    if not isinstance(slots_raw, list) or not slots_raw:
        raise TrialError("config_invalid", "slots must be a non-empty array of tables")
    slots: list[Slot] = []
    for index, value in enumerate(slots_raw):
        item = _mapping(value, f"slots[{index}]")
        phase = _required_text(item.get("phase"), f"slots[{index}].phase")
        if phase not in PHASES:
            raise TrialError("config_invalid", f"slots[{index}].phase is invalid")
        slots.append(
            Slot(
                slot_id=_identifier(item.get("id"), f"slots[{index}].id"),
                phase=phase,
                pair=_required_text(item.get("pair"), f"slots[{index}].pair"),
                case=_required_text(item.get("case"), f"slots[{index}].case"),
                arm=_required_text(item.get("arm"), f"slots[{index}].arm"),
                project=_required_text(item.get("project"), f"slots[{index}].project"),
                order=_required_int(item.get("order"), f"slots[{index}].order", minimum=1),
            )
        )
    if len({slot.slot_id for slot in slots}) != len(slots):
        raise TrialError("config_invalid", "slot ids must be unique")
    return tuple(slots)


def load_trial_config(path: Path) -> TrialConfig:
    path = path.expanduser().resolve(strict=True)
    with path.open("rb") as handle:
        raw = tomllib.load(handle)
    retired = {"transport_retry_total", "dispatch_budget", "wall_budget_seconds", "cleanup_allowlist"}
    if retired.intersection(raw):
        raise TrialError("config_invalid", "retry, global budgets, and cleanup_allowlist are not supported")
    heldback = _mapping(raw.get("heldback"), "heldback")
    fact_names_raw = heldback.get("binary_fact_names")
    if not isinstance(fact_names_raw, list) or not fact_names_raw:
        raise TrialError("config_invalid", "heldback.binary_fact_names must be a non-empty array")
    fact_names = tuple(_identifier(value, "heldback.binary_fact_names") for value in fact_names_raw)
    if len(set(fact_names)) != len(fact_names):
        raise TrialError("config_invalid", "heldback.binary_fact_names must be unique")
    config = TrialConfig(
        path=path,
        epoch_id=_identifier(raw.get("epoch_id"), "epoch_id"),
        trial_root=_absolute_path(raw.get("trial_root"), "trial_root"),
        plugin_id=_selector_component(raw.get("plugin_id"), "plugin_id"),
        codex_binary=_required_text(raw.get("codex_binary"), "codex_binary"),
        auth_identity_label=_required_text(
            raw.get("auth_identity_label"), "auth_identity_label"
        ),
        actor=_parse_actor(raw),
        arms=_parse_arms(raw),
        projects=_parse_projects(raw),
        cases=_parse_cases(raw),
        slots=_parse_slots(raw),
        gate_receipt_path=_absolute_path(
            heldback.get("gate_receipt_path"), "heldback.gate_receipt_path"
        ),
        d1_binary_fact_names=fact_names,
    )
    _validate_config_boundaries(config)
    validate_schedule(config)
    return config


def _validate_config_boundaries(config: TrialConfig) -> None:
    repo_root = Path(__file__).resolve().parent.parent
    if _is_within(config.trial_root, repo_root):
        raise TrialError("config_invalid", "trial_root must be outside the source repository")
    if not _is_within(config.path, config.trial_root):
        raise TrialError("config_invalid", "trial.toml must be inside trial_root")
    if not _is_within(config.gate_receipt_path, config.trial_root):
        raise TrialError("config_invalid", "heldback gate receipt must be inside trial_root")
    for case in config.cases.values():
        for path in (case.prompt_path, case.rubric_path, case.task_state_root):
            if not _is_within(path, config.trial_root):
                raise TrialError("config_invalid", "case material must be inside trial_root")
    for project in config.projects.values():
        if _is_within(project.root, repo_root):
            raise TrialError("config_invalid", "neutral project roots must be outside the source repository")
        if _is_within(config.trial_root, project.root) or _is_within(project.root, config.trial_root):
            raise TrialError("config_invalid", "trial_root and neutral project roots must not overlap")
    for slot in config.slots:
        if slot.arm not in config.arms or slot.project not in config.projects or slot.case not in config.cases:
            raise TrialError("config_invalid", f"slot {slot.slot_id} references an unknown arm, project, or case")


def validate_schedule(config: TrialConfig) -> None:
    for phase in PHASES:
        phase_slots = sorted((slot for slot in config.slots if slot.phase == phase), key=lambda s: s.order)
        if len({slot.order for slot in phase_slots}) != len(phase_slots):
            raise TrialError("schedule_invalid", f"{phase} slot order values must be unique")
        pairs: dict[str, list[Slot]] = {}
        for slot in phase_slots:
            pairs.setdefault(slot.pair, []).append(slot)
        if phase == "d1":
            if len(phase_slots) != 4 or len(pairs) != 2 or {slot.case for slot in phase_slots} != {"D1"}:
                raise TrialError("schedule_invalid", "d1 requires exactly two D1 pairs and four slots")
            sequences: set[tuple[str, str]] = set()
            pair_projects: set[str] = set()
            for pair_slots in pairs.values():
                ordered = sorted(pair_slots, key=lambda s: s.order)
                if len(ordered) != 2 or {slot.arm for slot in ordered} != {"baseline", "candidate"}:
                    raise TrialError("schedule_invalid", "each d1 pair requires one baseline and one candidate")
                if len({slot.project for slot in ordered}) != 1:
                    raise TrialError("schedule_invalid", "both arms in a d1 pair must use the same project")
                sequences.add((ordered[0].arm, ordered[1].arm))
                pair_projects.add(ordered[0].project)
            if sequences != {("baseline", "candidate"), ("candidate", "baseline")}:
                raise TrialError("schedule_invalid", "d1 pairs must freeze one AB and one BA order")
            if len(pair_projects) != 2:
                raise TrialError("schedule_invalid", "the two d1 pairs must use different projects")
        else:
            if len(phase_slots) != 4 or len(pairs) != 2 or {slot.case for slot in phase_slots} != {"H1", "S1"}:
                raise TrialError("schedule_invalid", "heldback requires one H1 pair and one S1 pair")
            for pair_slots in pairs.values():
                if len(pair_slots) != 2 or {slot.arm for slot in pair_slots} != {"baseline", "candidate"}:
                    raise TrialError("schedule_invalid", "each heldback pair requires one baseline and one candidate")
                if len({slot.project for slot in pair_slots}) != 1 or len({slot.case for slot in pair_slots}) != 1:
                    raise TrialError("schedule_invalid", "a heldback pair must keep one case and project")


def validate_case_material(case: Case) -> None:
    reject_symlinks(case.task_state_root, f"case {case.name} task state")
    checks = (
        (file_digest(case.prompt_path), case.prompt_sha256, "prompt_hash_mismatch"),
        (file_digest(case.rubric_path), case.rubric_sha256, "rubric_hash_mismatch"),
        (tree_digest(case.task_state_root), case.task_state_sha256, "task_state_hash_mismatch"),
    )
    for actual, expected, code in checks:
        if actual != expected:
            raise TrialError(code, f"sealed input hash mismatch for case {case.name}")


def validate_project_skeleton(project: Project) -> None:
    excluded = (project.workspace_parent,)
    reject_symlinks(project.root, f"neutral project {project.name}", excluded)
    actual = tree_digest(project.root, excluded)
    if actual != project.skeleton_sha256:
        raise TrialError("project_skeleton_drift", f"neutral project skeleton drifted: {project.name}")


def _read_jsonl(path: Path, error_code: str) -> list[Mapping[str, Any]]:
    if path.is_symlink():
        raise TrialError(error_code, "results.jsonl must not be a symlink")
    records: list[Mapping[str, Any]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        try:
            record = json.loads(line)
        except json.JSONDecodeError as exc:
            raise TrialError(error_code, f"results.jsonl line {line_number} is invalid") from exc
        if not isinstance(record, Mapping):
            raise TrialError(error_code, "results.jsonl records must be objects")
        records.append(record)
    return records


def _append_jsonl(path: Path, record: Mapping[str, Any]) -> None:
    if path.is_symlink():
        raise TrialError("results_invalid", "results.jsonl must not be a symlink")
    flags = os.O_WRONLY | os.O_CREAT | os.O_APPEND
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    try:
        descriptor = os.open(path, flags, 0o600)
    except OSError as exc:
        raise TrialError("results_invalid", "results.jsonl could not be opened safely") from exc
    with os.fdopen(descriptor, "a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")
        handle.flush()
        os.fsync(handle.fileno())


def _slot_bindings(config: TrialConfig, slot: Slot) -> Mapping[str, Any]:
    arm = config.arms[slot.arm]
    case = config.cases[slot.case]
    return {
        "epoch_id": config.epoch_id,
        "plugin_id": config.plugin_id,
        "marketplace": arm.marketplace,
        "package_sha256": arm.source_sha256,
        "case": case.name,
        "prompt_sha256": case.prompt_sha256,
        "rubric_sha256": case.rubric_sha256,
        "task_state_sha256": case.task_state_sha256,
        "actor": {
            "launcher": config.codex_binary,
            "auth_identity_label": config.auth_identity_label,
            "model": config.actor.model,
            "profile": config.actor.profile,
            "sandbox": config.actor.sandbox,
            "approval_policy": config.actor.approval_policy,
            "timeout_seconds": config.actor.timeout_seconds,
        },
    }


def _validate_d1_attempt_binding(
    config: TrialConfig, slot: Slot, attempt: Mapping[str, Any], d1_run_id: str
) -> None:
    arm = config.arms[slot.arm]
    expected_attempt = {
        "run_id": d1_run_id, "slot_id": slot.slot_id,
        "arm": slot.arm, "project": slot.project,
        "model_dispatches": 1, "valid": True,
        "failure_code": None, "cleanup_ok": True,
    }
    if any(attempt.get(field) != expected for field, expected in expected_attempt.items()):
        raise TrialError("heldback_gate_invalid", "D1 attempt identity differs from the frozen slot")
    if attempt.get("bindings") != _slot_bindings(config, slot):
        raise TrialError("heldback_gate_invalid", "D1 attempt bindings differ from the frozen config")
    if attempt.get("plugin_idle_before") is not True:
        raise TrialError("heldback_gate_invalid", "D1 idle probe binding is invalid")
    probe = attempt.get("zero_model_binding_probe")
    expected_probe = {
        "model_dispatches": 0, "plugin_id": config.plugin_id,
        "marketplace": arm.marketplace, "source_sha256": arm.source_sha256,
        "installed_sha256": arm.source_sha256,
    }
    if not isinstance(probe, Mapping) or any(
        probe.get(field) != expected for field, expected in expected_probe.items()
    ):
        raise TrialError("heldback_gate_invalid", "D1 package probe differs from the frozen arm")
    actor = attempt.get("actor")
    if not isinstance(actor, Mapping):
        raise TrialError("heldback_gate_invalid", "D1 actor receipt is missing")
    if not isinstance(actor.get("launcher_version"), str) or not actor["launcher_version"].strip():
        raise TrialError("heldback_gate_invalid", "D1 launcher version is missing")


def validate_gate_receipt(config: TrialConfig) -> Mapping[str, Any]:
    """Validate D1 authorization without opening any held-back case file."""

    path = config.gate_receipt_path
    if not path.is_file():
        raise TrialError("heldback_gate_invalid", "operator D1 gate receipt is missing")
    with path.open("rb") as handle:
        receipt = tomllib.load(handle)
    expected_scalar = {
        "epoch_id": config.epoch_id,
        "d1_case_sha256": config.cases["D1"].prompt_sha256,
        "d1_rubric_sha256": config.cases["D1"].rubric_sha256,
        "baseline_package_sha256": config.arms["baseline"].source_sha256,
        "candidate_package_sha256": config.arms["candidate"].source_sha256,
        "d1_gate": "pass",
        "heldback_unopened": True,
    }
    for field, expected in expected_scalar.items():
        if receipt.get(field) != expected:
            raise TrialError("heldback_gate_invalid", f"D1 gate field does not match: {field}")
    for field in ("operator_label", "created_at"):
        _required_text(receipt.get(field), f"gate.{field}")
    d1_run_id = _required_text(receipt.get("d1_run_id"), "gate.d1_run_id")
    hashes = receipt.get("valid_attempt_receipt_hashes")
    if (
        not isinstance(hashes, list)
        or len(hashes) != 4
        or len(set(hashes)) != 4
    ):
        raise TrialError("heldback_gate_invalid", "D1 gate must bind four unique valid attempt hashes")
    try:
        frozen_hashes = {_sha256(value, "gate.valid_attempt_receipt_hashes") for value in hashes}
    except TrialError as exc:
        raise TrialError("heldback_gate_invalid", str(exc)) from exc
    binary_facts = receipt.get("binary_facts")
    if not isinstance(binary_facts, Mapping) or set(binary_facts) != set(config.d1_binary_fact_names):
        raise TrialError("heldback_gate_invalid", "D1 gate binary fact names differ from the frozen config")
    if any(value not in ("yes", "no") for value in binary_facts.values()):
        raise TrialError("heldback_gate_invalid", "D1 binary facts must be yes or no")

    results_path = config.trial_root / "results.jsonl"
    if not results_path.is_file():
        raise TrialError("heldback_gate_invalid", "D1 results are missing")
    d1_records = [
        record
        for record in _read_jsonl(results_path, "heldback_gate_invalid")
        if (
            record.get("record_type") == "slot_result"
            and record.get("evidence_class") == EVIDENCE_CLASS
            and record.get("epoch_id") == config.epoch_id
            and record.get("phase") == "d1"
            and record.get("run_id") == d1_run_id
        )
    ]
    if len(d1_records) != 4 or any(record.get("valid") is not True for record in d1_records):
        raise TrialError("heldback_gate_invalid", "D1 run must contain exactly four valid slot records")
    expected_slots = {
        slot.slot_id: slot for slot in config.slots if slot.phase == "d1"
    }
    if {record.get("slot_id") for record in d1_records} != set(expected_slots):
        raise TrialError("heldback_gate_invalid", "D1 results do not match the frozen slot set")
    for record in d1_records:
        slot = expected_slots[str(record["slot_id"])]
        if any(
            record.get(field) != expected
            for field, expected in {
                "pair": slot.pair,
                "case": slot.case,
                "arm": slot.arm,
                "project": slot.project,
                "order": slot.order,
            }.items()
        ):
            raise TrialError("heldback_gate_invalid", "D1 result binding differs from the frozen schedule")
        attempt = record.get("attempt")
        if not isinstance(attempt, Mapping):
            raise TrialError("heldback_gate_invalid", "D1 result must contain one attempt receipt")
        final_attempt = dict(attempt)
        recorded_attempt_hash = final_attempt.pop("receipt_sha256", None)
        if (
            final_attempt.get("valid") is not True
            or recorded_attempt_hash != _canonical_hash(final_attempt)
            or record.get("valid_attempt_receipt_hash") != recorded_attempt_hash
        ):
            raise TrialError("heldback_gate_invalid", "D1 attempt receipt integrity check failed")
        _validate_d1_attempt_binding(config, slot, attempt, d1_run_id)
    recorded_hashes = {record.get("valid_attempt_receipt_hash") for record in d1_records}
    if recorded_hashes != frozen_hashes:
        raise TrialError("heldback_gate_invalid", "D1 attempt hashes do not match results.jsonl")
    return receipt


def _terminate_process_group(pid: int) -> None:
    try:
        os.killpg(pid, signal.SIGTERM)
    except ProcessLookupError:
        return
    deadline = time.monotonic() + 0.25
    while time.monotonic() < deadline:
        try:
            os.killpg(pid, 0)
        except ProcessLookupError:
            return
        time.sleep(0.01)
    try:
        os.killpg(pid, signal.SIGKILL)
    except ProcessLookupError:
        pass


def run_process(argv: Sequence[str], cwd: Path | None, stdin_text: str | None, timeout: float) -> ProcessResult:
    started = time.monotonic()
    process = subprocess.Popen(
        list(argv),
        cwd=str(cwd) if cwd else None,
        stdin=subprocess.PIPE if stdin_text is not None else subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        start_new_session=True,
    )
    try:
        stdout, stderr = process.communicate(stdin_text, timeout=timeout)
        timed_out = False
    except subprocess.TimeoutExpired:
        os.killpg(process.pid, signal.SIGTERM)
        try:
            stdout, stderr = process.communicate(timeout=5)
        except subprocess.TimeoutExpired:
            os.killpg(process.pid, signal.SIGKILL)
            stdout, stderr = process.communicate()
        timed_out = True
    finally:
        _terminate_process_group(process.pid)
    return ProcessResult(
        argv=tuple(str(item) for item in argv),
        returncode=process.returncode,
        stdout=stdout,
        stderr=stderr,
        timed_out=timed_out,
        duration_seconds=round(time.monotonic() - started, 6),
    )


def _json_object(result: ProcessResult, stage: str) -> Mapping[str, Any]:
    if result.timed_out or result.returncode != 0:
        raise TrialError(f"{stage}_failed", f"{stage} command did not complete successfully")
    try:
        value = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise TrialError(f"{stage}_invalid_json", f"{stage} did not return JSON") from exc
    if not isinstance(value, Mapping):
        raise TrialError(f"{stage}_invalid_json", f"{stage} JSON must be an object")
    return value


def _matching_plugins(payload: Mapping[str, Any], plugin_id: str) -> list[Mapping[str, Any]]:
    installed = payload.get("installed")
    if not isinstance(installed, list):
        raise TrialError("plugin_inventory_invalid", "plugin list JSON has no installed array")
    matches: list[Mapping[str, Any]] = []
    for value in installed:
        if not isinstance(value, Mapping):
            continue
        plugin_key = value.get("pluginId")
        name = value.get("name")
        if name == plugin_id or plugin_key == plugin_id or (
            isinstance(plugin_key, str) and plugin_key.startswith(f"{plugin_id}@")
        ):
            matches.append(value)
    return matches


def _require_idle(payload: Mapping[str, Any], plugin_id: str) -> None:
    if _matching_plugins(payload, plugin_id):
        raise TrialError("plugin_not_idle", f"plugin {plugin_id} is already present")


def _require_exact_one_active(
    payload: Mapping[str, Any], plugin_id: str, marketplace: str
) -> Mapping[str, Any]:
    matches = _matching_plugins(payload, plugin_id)
    if len(matches) != 1:
        raise TrialError("plugin_binding_invalid", "zero-model inventory did not find exact-one plugin")
    match = matches[0]
    if match.get("installed") is not True or match.get("enabled") is not True:
        raise TrialError("plugin_binding_invalid", "the exact plugin is not installed and enabled")
    if match.get("marketplaceName") != marketplace:
        raise TrialError("plugin_binding_invalid", "active plugin marketplace differs from the frozen arm")
    return match


def _installed_path(payload: Mapping[str, Any]) -> Path:
    candidates: list[Any] = [payload.get("installedPath")]
    for key in ("plugin", "data", "result"):
        nested = payload.get(key)
        if isinstance(nested, Mapping):
            candidates.append(nested.get("installedPath"))
    for candidate in candidates:
        if isinstance(candidate, str) and candidate:
            path = Path(candidate).expanduser()
            if not path.is_absolute():
                raise TrialError("plugin_binding_invalid", "installedPath must be absolute")
            return path.resolve(strict=False)
    raise TrialError("plugin_binding_invalid", "plugin add JSON did not expose installedPath")


def _canonical_hash(value: Mapping[str, Any]) -> str:
    encoded = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _usage_from_jsonl(output: str) -> Mapping[str, Any] | str:
    usage: Mapping[str, Any] | None = None
    for line in output.splitlines():
        try:
            item = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(item, Mapping) and isinstance(item.get("usage"), Mapping):
            usage = item["usage"]
    return usage if usage is not None else "unavailable"


class TrialRunner:
    def __init__(self, config: TrialConfig, process_runner: ProcessRunner = run_process):
        self.config = config
        self.process_runner = process_runner
        self.run_id = uuid.uuid4().hex
        self.launcher_version = "unavailable"
        self.results_path = config.trial_root / "results.jsonl"

    def _invoke(
        self,
        argv: Sequence[str],
        *,
        cwd: Path | None = None,
        stdin_text: str | None = None,
        timeout: float = 30,
    ) -> ProcessResult:
        try:
            return self.process_runner(argv, cwd, stdin_text, timeout)
        except OSError as exc:
            raise TrialError("transport_launch_failed", f"could not launch transport command: {argv[0]}") from exc

    def _list_plugins(self, project: Project) -> tuple[ProcessResult, Mapping[str, Any]]:
        result = self._invoke(
            (self.config.codex_binary, "plugin", "list", "--json"), cwd=project.root
        )
        return result, _json_object(result, "plugin_list")

    def _validate_all_projects(self) -> None:
        for project in self.config.projects.values():
            validate_project_skeleton(project)
            workspace_base = project.root / project.workspace_parent
            if workspace_base.is_symlink() or (workspace_base.exists() and not workspace_base.is_dir()):
                raise TrialError(
                    "workspace_boundary_invalid",
                    f"workspace parent is not a local directory: {project.name}",
                )
            if workspace_base.exists():
                reject_symlinks(workspace_base, f"workspace parent {project.name}")
                if next(workspace_base.iterdir(), None) is not None:
                    raise TrialError("workspace_residue", f"workspace parent contains residue: {project.name}")

    def _actor_command(self, workspace: Path, output_path: Path) -> tuple[str, ...]:
        actor = self.config.actor
        return (
            self.config.codex_binary,
            "exec",
            "--json",
            "--ephemeral",
            "--ignore-rules",
            "--skip-git-repo-check",
            "-C",
            str(workspace),
            "-m",
            actor.model,
            "-p",
            actor.profile,
            "-s",
            actor.sandbox,
            "-c",
            f"approval_policy={json.dumps(actor.approval_policy)}",
            "-o",
            str(output_path),
            "-",
        )

    def _slot_identity(self, slot: Slot) -> dict[str, Any]:
        return {
            "evidence_class": EVIDENCE_CLASS, "epoch_id": self.config.epoch_id,
            "run_id": self.run_id, "phase": slot.phase, "pair": slot.pair,
            "slot_id": slot.slot_id, "case": slot.case, "arm": slot.arm,
            "project": slot.project, "order": slot.order,
        }

    def _physical_attempt(self, slot: Slot) -> dict[str, Any]:
        config = self.config
        arm = config.arms[slot.arm]
        project = config.projects[slot.project]
        case = config.cases[slot.case]
        attempt_root = project.root / project.workspace_parent / config.epoch_id / self.run_id / slot.slot_id / "attempt-1"
        workspace = attempt_root / "workspace"
        output_path = attempt_root / "last-message.txt"
        receipt: dict[str, Any] = {
            "run_id": self.run_id,
            "slot_id": slot.slot_id,
            "arm": slot.arm,
            "project": slot.project,
            "workspace": str(workspace),
            "model_dispatches": 0,
            "valid": False,
            "failure_code": None,
            "cleanup_ok": False,
            "bindings": _slot_bindings(config, slot),
        }
        installed_path: Path | None = None
        add_started = False
        attempt_root_created = False
        command_receipts: list[dict[str, Any]] = []

        def record(stage: str, result: ProcessResult) -> None:
            command_receipts.append(
                {
                    "stage": stage,
                    "argv": list(result.argv),
                    "returncode": result.returncode,
                    "timed_out": result.timed_out,
                    "duration_seconds": result.duration_seconds,
                }
            )

        try:
            self._validate_all_projects()
            if attempt_root.exists():
                raise TrialError("workspace_reuse", f"attempt root already exists: {attempt_root}")
            attempt_root.mkdir(parents=True)
            attempt_root_created = True
            shutil.copytree(case.task_state_root, workspace)
            if tree_digest(workspace) != case.task_state_sha256:
                raise TrialError("workspace_copy_mismatch", "fresh workspace differs from sealed task state")
            reject_symlinks(arm.source_root, f"{slot.arm} source package")
            source_hash = tree_digest(arm.source_root)
            if source_hash != arm.source_sha256:
                raise TrialError("source_package_hash_mismatch", f"{slot.arm} source package drifted")

            list_result, idle_payload = self._list_plugins(project)
            record("plugin_list_idle", list_result)
            _require_idle(idle_payload, config.plugin_id)
            receipt["plugin_idle_before"] = True

            selector = f"{config.plugin_id}@{arm.marketplace}"
            add_started = True
            add_result = self._invoke(
                (config.codex_binary, "plugin", "add", selector, "--json"), cwd=project.root
            )
            record("plugin_add", add_result)
            add_payload = _json_object(add_result, "plugin_add")
            installed_path = _installed_path(add_payload)
            installed_hash = tree_digest(installed_path)
            if installed_hash != arm.source_sha256:
                raise TrialError("installed_package_hash_mismatch", "installed package digest differs from frozen source")

            active_result, active_payload = self._list_plugins(project)
            record("plugin_list_active", active_result)
            active_plugin = _require_exact_one_active(
                active_payload, config.plugin_id, arm.marketplace
            )
            receipt["zero_model_binding_probe"] = {
                "model_dispatches": 0,
                "plugin_id": config.plugin_id,
                "marketplace": arm.marketplace,
                "installed_path": str(installed_path),
                "source_sha256": source_hash,
                "installed_sha256": installed_hash,
                "inventory": dict(active_plugin),
            }

            prompt = case.prompt_path.read_text(encoding="utf-8")
            _append_jsonl(
                self.results_path,
                {
                    "record_type": "attempt_started",
                    **self._slot_identity(slot),
                    "bindings": receipt["bindings"],
                    "launcher_version": self.launcher_version,
                    "recorded_at": dt.datetime.now(dt.timezone.utc).isoformat(),
                },
            )
            receipt["model_dispatches"] = 1
            actor_result = self._invoke(
                self._actor_command(workspace, output_path),
                cwd=workspace,
                stdin_text=prompt,
                timeout=config.actor.timeout_seconds,
            )
            record("actor", actor_result)
            if actor_result.timed_out or actor_result.returncode != 0:
                raise TrialError("actor_transport_failure", "actor transport did not complete")
            if not output_path.is_file():
                raise TrialError("actor_output_missing", "actor did not write the final response")
            final_response = output_path.read_text(encoding="utf-8")
            if not final_response.strip():
                raise TrialError("actor_output_missing", "actor final response is empty")
            receipt["actor"] = {
                "launcher_version": self.launcher_version,
                "runtime_identity_limitation": "host_did_not_expose_observed_model_or_profile",
                "usage": _usage_from_jsonl(actor_result.stdout),
                "final_response": final_response,
            }
            receipt["valid"] = True
        except TrialError as exc:
            receipt["failure_code"] = exc.code
        except (OSError, UnicodeError) as exc:
            receipt["failure_code"] = "attempt_io_failure"
        finally:
            cleanup_errors: list[str] = []
            if add_started:
                selector = f"{config.plugin_id}@{arm.marketplace}"
                try:
                    remove_result = self._invoke(
                        (config.codex_binary, "plugin", "remove", selector, "--json"),
                        cwd=project.root,
                    )
                    record("plugin_remove", remove_result)
                    if remove_result.timed_out or remove_result.returncode != 0:
                        cleanup_errors.append("official_remove_failed")
                except TrialError as exc:
                    cleanup_errors.append(exc.code)
                try:
                    idle_result, idle_payload = self._list_plugins(project)
                    record("plugin_list_cleanup", idle_result)
                    _require_idle(idle_payload, config.plugin_id)
                except TrialError as exc:
                    cleanup_errors.append(exc.code)
                if installed_path is not None and os.path.lexists(installed_path):
                    cleanup_errors.append("installed_path_remains")
            try:
                if attempt_root_created and attempt_root.exists():
                    shutil.rmtree(attempt_root)
                if attempt_root_created:
                    for empty_parent in attempt_root.parents[:3]:
                        if empty_parent.exists():
                            empty_parent.rmdir()
            except OSError:
                cleanup_errors.append("attempt_workspace_remains")
            try:
                self._validate_all_projects()
            except TrialError as exc:
                cleanup_errors.append(exc.code)
            receipt["commands"] = command_receipts
            receipt["cleanup_errors"] = cleanup_errors
            receipt["cleanup_ok"] = not cleanup_errors
            if cleanup_errors:
                receipt["valid"] = False
                receipt["failure_code"] = "cleanup_incomplete"

        receipt["receipt_sha256"] = _canonical_hash(receipt)
        return receipt
    def run_slot(self, slot: Slot) -> dict[str, Any]:
        attempt = self._physical_attempt(slot)
        record = {
            "record_type": "slot_result",
            **self._slot_identity(slot),
            "attempt": attempt,
            "valid_attempt_receipt_hash": attempt["receipt_sha256"] if attempt["valid"] else None,
            "valid": attempt["valid"],
        }
        if not attempt["valid"]:
            record["failure_code"] = attempt["failure_code"]
        return record

    def run_phase(self, phase: str) -> list[dict[str, Any]]:
        if phase not in PHASES:
            raise TrialError("phase_invalid", f"unsupported phase: {phase}")
        if phase == "heldback":
            validate_gate_receipt(self.config)
        results_path = self.results_path
        if results_path.is_symlink():
            raise TrialError("results_invalid", "results.jsonl must not be a symlink")
        if results_path.is_file():
            for prior in _read_jsonl(results_path, "results_invalid"):
                if (
                    prior.get("epoch_id") == self.config.epoch_id
                    and prior.get("phase") == phase
                ):
                    raise TrialError(
                        "phase_already_started",
                        f"phase {phase} already has a receipt for epoch {self.config.epoch_id}",
                    )
        phase_slots = sorted(
            (slot for slot in self.config.slots if slot.phase == phase), key=lambda slot: slot.order
        )
        for case_name in sorted({slot.case for slot in phase_slots}):
            validate_case_material(self.config.cases[case_name])
        for arm in self.config.arms.values():
            reject_symlinks(arm.source_root, f"{arm.name} source package")
            if tree_digest(arm.source_root) != arm.source_sha256:
                raise TrialError("source_package_hash_mismatch", f"{arm.name} source package drifted")
        self._validate_all_projects()
        version_result = self._invoke((self.config.codex_binary, "--version"))
        if version_result.timed_out or version_result.returncode != 0 or not version_result.stdout.strip():
            raise TrialError("launcher_identity_missing", "Codex launcher version is unavailable")
        self.launcher_version = version_result.stdout.strip()

        self.config.trial_root.mkdir(parents=True, exist_ok=True)
        records: list[dict[str, Any]] = []
        for slot in phase_slots:
            record = self.run_slot(slot)
            record["recorded_at"] = dt.datetime.now(dt.timezone.utc).isoformat()
            _append_jsonl(results_path, record)
            records.append(record)
            if not record["valid"]:
                raise TrialError(
                    str(record.get("failure_code") or "slot_invalid"),
                    f"slot failed closed: {slot.slot_id}",
                )
        return records


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True, type=Path, help="absolute path to trial.toml")
    parser.add_argument("--phase", required=True, choices=PHASES)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        config = load_trial_config(args.config)
        TrialRunner(config).run_phase(args.phase)
    except (OSError, tomllib.TOMLDecodeError, TrialError) as exc:
        code = exc.code if isinstance(exc, TrialError) else "trial_io_error"
        print(json.dumps({"error": code, "message": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
