from __future__ import annotations

import dataclasses
import json
import shutil
import sys
import tempfile
import time
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import run_plugin_candidate_trial as trial  # noqa: E402


def _toml_string(value: str | Path) -> str:
    return json.dumps(str(value))


def _records(path: Path) -> list[dict[str, object]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def _slot_results(path: Path) -> list[dict[str, object]]:
    return [record for record in _records(path) if record.get("record_type") == "slot_result"]


class FakeCodex:
    def __init__(self, sources: dict[str, Path], cache_root: Path):
        self.sources = sources
        self.cache_root = cache_root
        self.active: list[dict[str, object]] = []
        self.installed_path: Path | None = None
        self.actor_codes: list[int] = []
        self.actor_calls = 0
        self.remove_fails = False
        self.mutate_installed = False
        self.duplicate_inventory = False
        self.inventory_marketplace_override: str | None = None
        self.mutate_project_root: Path | None = None
        self.leave_dangling_installed_path = False
        self.crash_on_actor = False
        self.version_output = "codex-cli 9.9.9\n"
        self.calls: list[tuple[tuple[str, ...], Path | None, str | None]] = []

    def __call__(
        self,
        argv: list[str] | tuple[str, ...],
        cwd: Path | None,
        stdin_text: str | None,
        timeout: float,
    ) -> trial.ProcessResult:
        del timeout
        command = tuple(str(value) for value in argv)
        self.calls.append((command, cwd, stdin_text))
        stdout = ""
        stderr = ""
        returncode = 0
        timed_out = False
        if command[1:] == ("--version",):
            stdout = self.version_output
        elif command[1:4] == ("plugin", "list", "--json"):
            installed = list(self.active)
            if self.duplicate_inventory and installed:
                installed.append(dict(installed[0]))
            stdout = json.dumps({"installed": installed})
        elif command[1:3] == ("plugin", "add"):
            selector = command[3]
            plugin_id, marketplace = selector.split("@", 1)
            source = self.sources[marketplace]
            self.installed_path = self.cache_root / marketplace
            if self.installed_path.exists():
                shutil.rmtree(self.installed_path)
            shutil.copytree(source, self.installed_path)
            if self.mutate_installed:
                (self.installed_path / "unexpected.txt").write_text("drift", encoding="utf-8")
            self.active = [
                {
                    "pluginId": f"{plugin_id}@{marketplace}",
                    "name": plugin_id,
                    "installed": True,
                    "enabled": True,
                    "marketplaceName": self.inventory_marketplace_override or marketplace,
                }
            ]
            stdout = json.dumps({"installedPath": str(self.installed_path)})
        elif command[1:3] == ("plugin", "remove"):
            if self.remove_fails:
                returncode = 1
                stderr = "remove failed"
            else:
                self.active = []
                if self.installed_path and self.installed_path.exists():
                    shutil.rmtree(self.installed_path)
                if self.leave_dangling_installed_path and self.installed_path:
                    self.installed_path.symlink_to(self.cache_root / "missing-target")
                stdout = json.dumps({"removed": True})
        elif command[1] == "exec":
            self.actor_calls += 1
            if self.crash_on_actor:
                raise KeyboardInterrupt("simulated actor-process crash")
            code = self.actor_codes.pop(0) if self.actor_codes else 0
            returncode = code
            if code == 0:
                output_path = Path(command[command.index("-o") + 1])
                output_path.write_text(f"actor response {self.actor_calls}", encoding="utf-8")
                stdout = json.dumps({"type": "turn.completed", "usage": {"input_tokens": 7}})
            else:
                stderr = "temporary transport failure"
            if self.mutate_project_root is not None:
                (self.mutate_project_root / "anchor.txt").write_text("drift", encoding="utf-8")
        else:
            raise AssertionError(f"unexpected command: {command}")
        return trial.ProcessResult(
            argv=command,
            returncode=returncode,
            stdout=stdout,
            stderr=stderr,
            timed_out=timed_out,
            duration_seconds=0.01,
        )


class TrialFixture:
    def __init__(self, base: Path):
        self.base = base
        self.trial_root = base / "trial"
        self.trial_root.mkdir(parents=True)
        self.cache_root = base / "cache"
        self.sources = {
            "baseline-market": base / "sources" / "baseline",
            "candidate-market": base / "sources" / "candidate",
        }
        for name, path in self.sources.items():
            path.mkdir(parents=True)
            (path / "plugin.txt").write_text(name, encoding="utf-8")
        self.projects = {"p1": base / "projects" / "p1", "p2": base / "projects" / "p2"}
        for name, path in self.projects.items():
            path.mkdir(parents=True)
            (path / "anchor.txt").write_text(name, encoding="utf-8")
        self.cases: dict[str, dict[str, Path]] = {}
        for name in ("D1", "H1", "S1"):
            root = self.trial_root / "cases" / name
            task = root / "task"
            task.mkdir(parents=True)
            prompt = root / "prompt.txt"
            rubric = root / "rubric.md"
            prompt.write_text(f"prompt {name}", encoding="utf-8")
            rubric.write_text(f"rubric {name}", encoding="utf-8")
            (task / "input.txt").write_text(f"task {name}", encoding="utf-8")
            self.cases[name] = {"prompt": prompt, "rubric": rubric, "task": task}
        self.gate_path = self.trial_root / "d1-gate.toml"
        self.config_path = self.trial_root / "trial.toml"
        self.write_config()
        self.config = trial.load_trial_config(self.config_path)
        self.write_valid_gate()

    def write_config(
        self,
        *,
        actor_profile: str = "sealed-profile",
        actor_sandbox: str = "workspace-write",
    ) -> None:
        arm_hashes = {name: trial.tree_digest(path) for name, path in self.sources.items()}
        project_hashes = {
            name: trial.tree_digest(path, (Path(".trial-workspaces"),))
            for name, path in self.projects.items()
        }
        lines = [
            'epoch_id = "epoch-001"',
            f"trial_root = {_toml_string(self.trial_root)}",
            'plugin_id = "sample-plugin"',
            'codex_binary = "codex"',
            'auth_identity_label = "shared-test-auth"',
            "",
            "[actor]",
            'model = "sample-model"',
            f"profile = {_toml_string(actor_profile)}",
            f"sandbox = {_toml_string(actor_sandbox)}",
            'approval_policy = "never"',
            "timeout_seconds = 30",
        ]
        for arm, marketplace in (("baseline", "baseline-market"), ("candidate", "candidate-market")):
            lines.extend(
                [
                    "",
                    f"[arms.{arm}]",
                    f"source_root = {_toml_string(self.sources[marketplace])}",
                    f"source_sha256 = {_toml_string(arm_hashes[marketplace])}",
                    f"marketplace = {_toml_string(marketplace)}",
                ]
            )
        for name, root in self.projects.items():
            lines.extend(
                [
                    "",
                    f"[projects.{name}]",
                    f"root = {_toml_string(root)}",
                    f"skeleton_sha256 = {_toml_string(project_hashes[name])}",
                    'workspace_parent = ".trial-workspaces"',
                ]
            )
        for name, paths in self.cases.items():
            lines.extend(
                [
                    "",
                    f"[cases.{name}]",
                    f"prompt_path = {_toml_string(paths['prompt'])}",
                    f"prompt_sha256 = {_toml_string(trial.file_digest(paths['prompt']))}",
                    f"rubric_path = {_toml_string(paths['rubric'])}",
                    f"rubric_sha256 = {_toml_string(trial.file_digest(paths['rubric']))}",
                    f"task_state_root = {_toml_string(paths['task'])}",
                    f"task_state_sha256 = {_toml_string(trial.tree_digest(paths['task']))}",
                ]
            )
        slots = (
            ("d1-a-1", "d1", "d1-a", "D1", "baseline", "p1", 1),
            ("d1-a-2", "d1", "d1-a", "D1", "candidate", "p1", 2),
            ("d1-b-1", "d1", "d1-b", "D1", "candidate", "p2", 3),
            ("d1-b-2", "d1", "d1-b", "D1", "baseline", "p2", 4),
            ("h1-1", "heldback", "h1", "H1", "baseline", "p1", 1),
            ("h1-2", "heldback", "h1", "H1", "candidate", "p1", 2),
            ("s1-1", "heldback", "s1", "S1", "candidate", "p2", 3),
            ("s1-2", "heldback", "s1", "S1", "baseline", "p2", 4),
        )
        for slot_id, phase, pair, case, arm, project, order in slots:
            lines.extend(
                [
                    "",
                    "[[slots]]",
                    f"id = {_toml_string(slot_id)}",
                    f"phase = {_toml_string(phase)}",
                    f"pair = {_toml_string(pair)}",
                    f"case = {_toml_string(case)}",
                    f"arm = {_toml_string(arm)}",
                    f"project = {_toml_string(project)}",
                    f"order = {order}",
                ]
            )
        lines.extend(
            [
                "",
                "[heldback]",
                f"gate_receipt_path = {_toml_string(self.gate_path)}",
                'binary_fact_names = ["candidate_contract", "baseline_missed"]',
            ]
        )
        self.config_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    def write_valid_gate(
        self,
        *,
        epoch_id: str = "epoch-001",
        d1_run_id: str = "unbound-run",
        receipt_hashes: list[str] | None = None,
    ) -> None:
        d1 = self.config.cases["D1"]
        receipt_hashes = receipt_hashes or [str(index) * 64 for index in range(1, 5)]
        lines = [
            f"epoch_id = {_toml_string(epoch_id)}",
            f"d1_run_id = {_toml_string(d1_run_id)}",
            f"d1_case_sha256 = {_toml_string(d1.prompt_sha256)}",
            f"d1_rubric_sha256 = {_toml_string(d1.rubric_sha256)}",
            f"baseline_package_sha256 = {_toml_string(self.config.arms['baseline'].source_sha256)}",
            f"candidate_package_sha256 = {_toml_string(self.config.arms['candidate'].source_sha256)}",
            'd1_gate = "pass"',
            "heldback_unopened = true",
            'operator_label = "operator"',
            'created_at = "2026-08-25T00:00:00Z"',
            "valid_attempt_receipt_hashes = [",
            *[f"  {_toml_string(value)}," for value in receipt_hashes],
            "]",
            "",
            "[binary_facts]",
            'candidate_contract = "yes"',
            'baseline_missed = "yes"',
        ]
        self.gate_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    def fake(self) -> FakeCodex:
        return FakeCodex(self.sources, self.cache_root)


class PluginCandidateTrialTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.fixture = TrialFixture(Path(self.temp.name).resolve())

    def test_schedule_freezes_ab_ba_and_pair_project_symmetry(self) -> None:
        d1 = sorted(
            (slot for slot in self.fixture.config.slots if slot.phase == "d1"),
            key=lambda slot: slot.order,
        )
        self.assertEqual([slot.arm for slot in d1], ["baseline", "candidate", "candidate", "baseline"])
        self.assertEqual([slot.project for slot in d1], ["p1", "p1", "p2", "p2"])
        changed = dataclasses.replace(d1[1], project="p2")
        config = dataclasses.replace(
            self.fixture.config,
            slots=tuple(changed if slot.slot_id == changed.slot_id else slot for slot in self.fixture.config.slots),
        )
        with self.assertRaisesRegex(trial.TrialError, "same project"):
            trial.validate_schedule(config)

    def test_full_d1_records_exact_binding_fresh_workspaces_and_no_decision(self) -> None:
        fake = self.fixture.fake()
        records = trial.TrialRunner(self.fixture.config, fake).run_phase("d1")
        self.assertEqual(len(records), 4)
        self.assertTrue(all(record["valid"] for record in records))
        workspaces = [record["attempt"]["workspace"] for record in records]
        self.assertEqual(len(set(workspaces)), 4)
        self.assertTrue(all(not Path(path).exists() for path in workspaces))
        self.assertEqual(fake.active, [])
        self.assertEqual(fake.actor_calls, 4)
        for record in records:
            attempt = record["attempt"]
            self.assertEqual(attempt["zero_model_binding_probe"]["model_dispatches"], 0)
            self.assertEqual(attempt["bindings"]["actor"]["model"], "sample-model")
        serialized = json.dumps(records)
        for forbidden in ("verdict", "score", "promote", "reject", "win_rate"):
            self.assertNotIn(f'"{forbidden}"', serialized)

    def test_wrong_installed_package_fails_before_actor_and_is_cleaned(self) -> None:
        fake = self.fixture.fake()
        fake.mutate_installed = True
        runner = trial.TrialRunner(self.fixture.config, fake)
        with self.assertRaisesRegex(trial.TrialError, "slot failed closed"):
            runner.run_phase("d1")
        self.assertEqual(fake.actor_calls, 0)
        self.assertEqual(fake.active, [])
        record = _slot_results(self.fixture.trial_root / "results.jsonl")[0]
        self.assertEqual(record["failure_code"], "installed_package_hash_mismatch")
        self.assertTrue(record["attempt"]["cleanup_ok"])

    def test_actor_transport_failure_is_recorded_once_and_never_retried(self) -> None:
        fake = self.fixture.fake()
        fake.actor_codes = [75, 0]
        runner = trial.TrialRunner(self.fixture.config, fake)
        with self.assertRaises(trial.TrialError):
            runner.run_phase("d1")
        records = _slot_results(self.fixture.trial_root / "results.jsonl")
        self.assertEqual(len(records), 1)
        self.assertFalse(records[0]["valid"])
        self.assertEqual(fake.actor_calls, 1)

    def test_cleanup_failure_invalidates_an_otherwise_successful_actor(self) -> None:
        fake = self.fixture.fake()
        fake.remove_fails = True
        with self.assertRaises(trial.TrialError):
            trial.TrialRunner(self.fixture.config, fake).run_phase("d1")
        record = _slot_results(self.fixture.trial_root / "results.jsonl")[0]
        self.assertEqual(record["failure_code"], "cleanup_incomplete")
        self.assertFalse(record["attempt"]["cleanup_ok"])
        self.assertIn("official_remove_failed", record["attempt"]["cleanup_errors"])

    def test_dangling_installed_path_invalidates_cleanup(self) -> None:
        fake = self.fixture.fake()
        fake.leave_dangling_installed_path = True
        runner = trial.TrialRunner(self.fixture.config, fake)
        slot = min(
            (slot for slot in self.fixture.config.slots if slot.phase == "d1"),
            key=lambda slot: slot.order,
        )
        record = runner.run_slot(slot)
        self.assertFalse(record["valid"])
        self.assertEqual(record["failure_code"], "cleanup_incomplete")
        self.assertIn("installed_path_remains", record["attempt"]["cleanup_errors"])
        self.assertIsNotNone(fake.installed_path)
        self.assertTrue(fake.installed_path.is_symlink())
        self.assertFalse(fake.installed_path.exists())

    def test_project_skeleton_drift_after_actor_fails_closed(self) -> None:
        fake = self.fixture.fake()
        fake.mutate_project_root = self.fixture.projects["p1"]
        with self.assertRaises(trial.TrialError):
            trial.TrialRunner(self.fixture.config, fake).run_phase("d1")
        record = _slot_results(self.fixture.trial_root / "results.jsonl")[0]
        self.assertEqual(record["failure_code"], "cleanup_incomplete")
        self.assertIn("project_skeleton_drift", record["attempt"]["cleanup_errors"])

    def test_workspace_reuse_fails_without_deleting_preexisting_state(self) -> None:
        fake = self.fixture.fake()
        runner = trial.TrialRunner(self.fixture.config, fake)
        runner.run_id = "fixed-run"
        slot = min((slot for slot in self.fixture.config.slots if slot.phase == "d1"), key=lambda s: s.order)
        project = self.fixture.config.projects[slot.project]
        attempt_root = (
            project.root
            / project.workspace_parent
            / self.fixture.config.epoch_id
            / runner.run_id
            / slot.slot_id
            / "attempt-1"
        )
        attempt_root.mkdir(parents=True)
        sentinel = attempt_root / "sentinel.txt"
        sentinel.write_text("keep", encoding="utf-8")
        record = runner.run_slot(slot)
        self.assertFalse(record["valid"])
        self.assertEqual(record["failure_code"], "cleanup_incomplete")
        self.assertIn("workspace_residue", record["attempt"]["cleanup_errors"])
        self.assertTrue(sentinel.is_file())
        self.assertEqual(fake.actor_calls, 0)

    def test_sealed_task_state_drift_stops_before_cli(self) -> None:
        (self.fixture.cases["D1"]["task"] / "input.txt").write_text("drift", encoding="utf-8")
        fake = self.fixture.fake()
        with self.assertRaisesRegex(trial.TrialError, "sealed input hash mismatch"):
            trial.TrialRunner(self.fixture.config, fake).run_phase("d1")
        self.assertEqual(fake.calls, [])

    def test_wrong_gate_is_rejected_before_heldback_case_is_opened(self) -> None:
        self.fixture.write_valid_gate(epoch_id="wrong-epoch")
        self.fixture.cases["H1"]["prompt"].unlink()
        fake = self.fixture.fake()
        with self.assertRaisesRegex(trial.TrialError, "D1 gate field") as caught:
            trial.TrialRunner(self.fixture.config, fake).run_phase("heldback")
        self.assertEqual(caught.exception.code, "heldback_gate_invalid")
        self.assertEqual(fake.calls, [])

    def test_heldback_gate_must_match_one_exact_four_receipt_d1_run(self) -> None:
        fake = self.fixture.fake()
        d1_records = trial.TrialRunner(self.fixture.config, fake).run_phase("d1")
        self.fixture.write_valid_gate(
            d1_run_id=d1_records[0]["run_id"],
            receipt_hashes=[record["valid_attempt_receipt_hash"] for record in d1_records],
        )
        heldback = trial.TrialRunner(self.fixture.config, fake).run_phase("heldback")
        self.assertEqual(len(heldback), 4)
        self.assertTrue(all(record["valid"] for record in heldback))

    def test_heldback_gate_rejects_tampered_attempt_receipt(self) -> None:
        fake = self.fixture.fake()
        d1_records = trial.TrialRunner(self.fixture.config, fake).run_phase("d1")
        self.fixture.write_valid_gate(
            d1_run_id=d1_records[0]["run_id"],
            receipt_hashes=[record["valid_attempt_receipt_hash"] for record in d1_records],
        )
        results_path = self.fixture.trial_root / "results.jsonl"
        records = _records(results_path)
        slot_record = next(record for record in records if record.get("record_type") == "slot_result")
        slot_record["attempt"]["actor"]["final_response"] = "tampered"
        results_path.write_text(
            "\n".join(json.dumps(record) for record in records) + "\n", encoding="utf-8"
        )
        with self.assertRaisesRegex(trial.TrialError, "integrity check failed"):
            trial.validate_gate_receipt(self.fixture.config)

    def test_same_epoch_phase_cannot_be_replayed(self) -> None:
        fake = self.fixture.fake()
        trial.TrialRunner(self.fixture.config, fake).run_phase("d1")
        second_fake = self.fixture.fake()
        with self.assertRaisesRegex(trial.TrialError, "already has a receipt"):
            trial.TrialRunner(self.fixture.config, second_fake).run_phase("d1")
        self.assertEqual(second_fake.calls, [])

    def test_exact_one_zero_model_probe_is_required(self) -> None:
        fake = self.fixture.fake()
        fake.duplicate_inventory = True
        with self.assertRaises(trial.TrialError):
            trial.TrialRunner(self.fixture.config, fake).run_phase("d1")
        self.assertEqual(fake.actor_calls, 0)
        record = _slot_results(self.fixture.trial_root / "results.jsonl")[0]
        self.assertEqual(record["failure_code"], "plugin_binding_invalid")

    def test_zero_model_probe_rejects_the_wrong_marketplace(self) -> None:
        fake = self.fixture.fake()
        fake.inventory_marketplace_override = "other-market"
        with self.assertRaises(trial.TrialError):
            trial.TrialRunner(self.fixture.config, fake).run_phase("d1")
        self.assertEqual(fake.actor_calls, 0)
        record = _slot_results(self.fixture.trial_root / "results.jsonl")[0]
        self.assertEqual(record["failure_code"], "plugin_binding_invalid")

    def test_required_actor_identity_and_launcher_identity_fail_closed(self) -> None:
        self.fixture.write_config(actor_profile="")
        with self.assertRaisesRegex(trial.TrialError, "actor.profile"):
            trial.load_trial_config(self.fixture.config_path)
        self.fixture.write_config()
        config = trial.load_trial_config(self.fixture.config_path)
        fake = self.fixture.fake()
        fake.version_output = ""
        with self.assertRaisesRegex(trial.TrialError, "launcher version"):
            trial.TrialRunner(config, fake).run_phase("d1")

    def test_retired_config_surface_and_danger_full_access_are_rejected(self) -> None:
        original = self.fixture.config_path.read_text(encoding="utf-8")
        variants = {
            "retry": original.replace(
                'auth_identity_label = "shared-test-auth"',
                'auth_identity_label = "shared-test-auth"\ntransport_retry_total = 1',
            ),
            "mutable": original.replace(
                'workspace_parent = ".trial-workspaces"',
                'workspace_parent = ".trial-workspaces"\nmutable_paths = ["ignored"]',
                1,
            ),
            "sandbox": original.replace(
                'sandbox = "workspace-write"', 'sandbox = "danger-full-access"'
            ),
        }
        for name, content in variants.items():
            with self.subTest(name=name):
                self.fixture.config_path.write_text(content, encoding="utf-8")
                with self.assertRaises(trial.TrialError):
                    trial.load_trial_config(self.fixture.config_path)
        self.fixture.config_path.write_text(original, encoding="utf-8")

    def test_config_requires_exactly_two_projects(self) -> None:
        third = self.fixture.base / "projects" / "p3"
        third.mkdir()
        (third / "anchor.txt").write_text("p3", encoding="utf-8")
        with self.fixture.config_path.open("a", encoding="utf-8") as handle:
            handle.write(
                "\n[projects.p3]\n"
                f"root = {_toml_string(third)}\n"
                f"skeleton_sha256 = {_toml_string(trial.tree_digest(third))}\n"
                'workspace_parent = ".trial-workspaces"\n'
            )
        with self.assertRaisesRegex(trial.TrialError, "exactly two"):
            trial.load_trial_config(self.fixture.config_path)

    def test_actor_crash_leaves_attempt_started_and_phase_cannot_rerun(self) -> None:
        fake = self.fixture.fake()
        fake.crash_on_actor = True
        with self.assertRaises(KeyboardInterrupt):
            trial.TrialRunner(self.fixture.config, fake).run_phase("d1")
        records = _records(self.fixture.trial_root / "results.jsonl")
        self.assertEqual([record["record_type"] for record in records], ["attempt_started"])
        second = self.fixture.fake()
        with self.assertRaisesRegex(trial.TrialError, "already has a receipt"):
            trial.TrialRunner(self.fixture.config, second).run_phase("d1")
        self.assertEqual(second.calls, [])

    def test_gate_rejects_rehashed_actor_binding_mismatch(self) -> None:
        fake = self.fixture.fake()
        d1_records = trial.TrialRunner(self.fixture.config, fake).run_phase("d1")
        results_path = self.fixture.trial_root / "results.jsonl"
        records = _records(results_path)
        slot_record = next(record for record in records if record.get("record_type") == "slot_result")
        attempt = slot_record["attempt"]
        attempt["bindings"]["actor"]["model"] = "different-model"
        unhashed = dict(attempt)
        unhashed.pop("receipt_sha256")
        attempt["receipt_sha256"] = trial._canonical_hash(unhashed)
        slot_record["valid_attempt_receipt_hash"] = attempt["receipt_sha256"]
        results_path.write_text(
            "\n".join(json.dumps(record) for record in records) + "\n", encoding="utf-8"
        )
        result_records = [record for record in records if record.get("record_type") == "slot_result"]
        self.fixture.write_valid_gate(
            d1_run_id=d1_records[0]["run_id"],
            receipt_hashes=[record["valid_attempt_receipt_hash"] for record in result_records],
        )
        with self.assertRaisesRegex(trial.TrialError, "frozen config"):
            trial.validate_gate_receipt(self.fixture.config)

    def test_gate_binary_fact_names_are_frozen_by_config(self) -> None:
        fake = self.fixture.fake()
        d1_records = trial.TrialRunner(self.fixture.config, fake).run_phase("d1")
        self.fixture.write_valid_gate(
            d1_run_id=d1_records[0]["run_id"],
            receipt_hashes=[record["valid_attempt_receipt_hash"] for record in d1_records],
        )
        gate = self.fixture.gate_path.read_text(encoding="utf-8").replace(
            'baseline_missed = "yes"', 'invented_fact = "yes"'
        )
        self.fixture.gate_path.write_text(gate, encoding="utf-8")
        with self.assertRaisesRegex(trial.TrialError, "fact names"):
            trial.validate_gate_receipt(self.fixture.config)

    def test_runner_is_plugin_agnostic_and_trial_output_is_repo_external(self) -> None:
        source = Path(trial.__file__).read_text(encoding="utf-8").lower()
        self.assertNotIn("groundwork", source)
        self.assertNotIn("to-prd", source)
        repo_root = Path(trial.__file__).resolve().parent.parent
        bad = dataclasses.replace(self.fixture.config, trial_root=repo_root / "scratch")
        with self.assertRaisesRegex(trial.TrialError, "outside the source repository"):
            trial._validate_config_boundaries(bad)

    def test_workspace_parent_symlink_is_rejected_without_touching_target(self) -> None:
        outside = self.fixture.base / "outside"
        outside.mkdir()
        sentinel = outside / "sentinel.txt"
        sentinel.write_text("keep", encoding="utf-8")
        (self.fixture.projects["p1"] / ".trial-workspaces").symlink_to(outside, target_is_directory=True)
        fake = self.fixture.fake()
        with self.assertRaises(trial.TrialError):
            trial.TrialRunner(self.fixture.config, fake).run_phase("d1")
        self.assertTrue(sentinel.is_file())
        self.assertEqual(fake.actor_calls, 0)

    def test_nested_workspace_symlink_is_rejected_without_touching_target(self) -> None:
        outside = self.fixture.base / "nested-outside"
        outside.mkdir()
        sentinel = outside / "sentinel.txt"
        sentinel.write_text("keep", encoding="utf-8")
        workspace_parent = self.fixture.projects["p1"] / ".trial-workspaces"
        workspace_parent.mkdir()
        (workspace_parent / "epoch-001").symlink_to(outside, target_is_directory=True)
        fake = self.fixture.fake()
        with self.assertRaisesRegex(trial.TrialError, "must not contain symlinks"):
            trial.TrialRunner(self.fixture.config, fake).run_phase("d1")
        self.assertTrue(sentinel.is_file())
        self.assertEqual(fake.actor_calls, 0)

    def test_workspace_parent_residue_is_rejected_without_deleting_it(self) -> None:
        workspace_parent = self.fixture.projects["p1"] / ".trial-workspaces"
        workspace_parent.mkdir()
        sentinel = workspace_parent / "leftover.txt"
        sentinel.write_text("keep", encoding="utf-8")
        fake = self.fixture.fake()
        with self.assertRaisesRegex(trial.TrialError, "workspace parent contains residue"):
            trial.TrialRunner(self.fixture.config, fake).run_phase("d1")
        self.assertEqual(sentinel.read_text(encoding="utf-8"), "keep")
        self.assertEqual(fake.actor_calls, 0)

    def test_results_symlink_is_rejected_before_cli(self) -> None:
        outside = self.fixture.base / "outside-results.jsonl"
        outside.write_text("sentinel\n", encoding="utf-8")
        (self.fixture.trial_root / "results.jsonl").symlink_to(outside)
        fake = self.fixture.fake()
        with self.assertRaisesRegex(trial.TrialError, "must not be a symlink"):
            trial.TrialRunner(self.fixture.config, fake).run_phase("d1")
        self.assertEqual(outside.read_text(encoding="utf-8"), "sentinel\n")
        self.assertEqual(fake.calls, [])

    def test_run_process_terminates_surviving_child_group_after_parent_success(self) -> None:
        ready = self.fixture.base / "child-ready"
        terminated = self.fixture.base / "child-terminated"
        child_code = (
            "import pathlib,signal,time\n"
            f"ready=pathlib.Path({str(ready)!r}); stopped=pathlib.Path({str(terminated)!r})\n"
            "signal.signal(signal.SIGTERM, lambda *_: (stopped.write_text('yes'), raise_exit()))\n"
            "def raise_exit(): raise SystemExit(0)\n"
            "ready.write_text('yes')\n"
            "while True: time.sleep(1)\n"
        )
        parent_code = (
            "import pathlib,subprocess,sys,time\n"
            f"subprocess.Popen([sys.executable, '-c', {child_code!r}], "
            "stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)\n"
            f"ready=pathlib.Path({str(ready)!r})\n"
            "deadline=time.time()+2\n"
            "while not ready.exists() and time.time()<deadline: time.sleep(0.01)\n"
        )
        result = trial.run_process((sys.executable, "-c", parent_code), None, None, 3)
        deadline = time.time() + 1
        while not terminated.exists() and time.time() < deadline:
            time.sleep(0.01)
        self.assertEqual(result.returncode, 0)
        self.assertFalse(result.timed_out)
        self.assertTrue(terminated.is_file())


if __name__ == "__main__":
    unittest.main()
