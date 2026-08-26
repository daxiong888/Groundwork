import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts.build_local_marketplace import ensure_safe_output, write_runtime_manifest
from scripts.check_runtime_package_boundary import (
    public_entry_reference_depth,
    validate_runtime_markdown_references,
)


REPO = Path(__file__).resolve().parents[1]
BUILDER = REPO / "scripts" / "build_local_marketplace.py"
CHECKER = REPO / "scripts" / "check_runtime_package_boundary.py"
CONTRACT = REPO / "scripts" / "runtime_package_manifest.json"


class RuntimePackageManifestTests(unittest.TestCase):
    def build(self, root: Path) -> Path:
        output = root / "marketplace"
        subprocess.run(
            [sys.executable, "-B", str(BUILDER), "--output", str(output)],
            cwd=REPO,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        return output / "plugins" / "groundwork"

    def check(self, package_root: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, "-B", str(CHECKER), "--package-root", str(package_root)],
            cwd=REPO,
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )

    def test_builder_and_checker_share_one_exact_file_contract(self):
        contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
        with tempfile.TemporaryDirectory() as tmp:
            package_root = self.build(Path(tmp))
            result = self.check(package_root)

            self.assertEqual(result.returncode, 0, result.stdout)
            for relative, expected in contract["exact_files"].items():
                observed = {
                    path.relative_to(package_root / relative).as_posix()
                    for path in (package_root / relative).rglob("*")
                    if path.is_file()
                }
                self.assertEqual(observed, set(expected))

    def test_builder_delegates_package_validation_to_the_checker(self):
        source = BUILDER.read_text(encoding="utf-8")

        self.assertIn("validate_package(plugin_root, report=False)", source)
        self.assertNotIn("def assert_runtime_package_boundary", source)
        self.assertNotIn("def validate_hooks_config", source)

    def test_builder_rejects_repository_source_directories_as_output(self):
        with self.assertRaises(SystemExit):
            ensure_safe_output(REPO / "skills")
        with self.assertRaises(SystemExit):
            ensure_safe_output(REPO / "dist")

        self.assertEqual(
            ensure_safe_output(REPO / "dist" / "safe-marketplace"),
            (REPO / "dist" / "safe-marketplace").resolve(),
        )

    def test_builder_does_not_delete_unowned_existing_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "marketplace"
            output.mkdir()
            protected = output / "keep.txt"
            protected.write_text("keep\n", encoding="utf-8")

            result = subprocess.run(
                [sys.executable, "-B", str(BUILDER), "--output", str(output)],
                cwd=REPO,
                check=False,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("not owned by this builder", result.stdout)
            self.assertEqual(protected.read_text(encoding="utf-8"), "keep\n")

    def test_builder_can_replace_its_own_existing_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "marketplace"
            first = subprocess.run(
                [sys.executable, "-B", str(BUILDER), "--output", str(output)],
                cwd=REPO,
                check=False,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
            )
            second = subprocess.run(
                [sys.executable, "-B", str(BUILDER), "--output", str(output)],
                cwd=REPO,
                check=False,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
            )

            self.assertEqual(first.returncode, 0, first.stdout)
            self.assertEqual(second.returncode, 0, second.stdout)

    def test_builder_refuses_markerless_marketplace_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "marketplace"
            initial = subprocess.run(
                [sys.executable, "-B", str(BUILDER), "--output", str(output)],
                cwd=REPO,
                check=False,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
            )
            self.assertEqual(initial.returncode, 0, initial.stdout)
            (output / ".groundwork-marketplace-output").unlink()

            result = subprocess.run(
                [sys.executable, "-B", str(BUILDER), "--output", str(output)],
                cwd=REPO,
                check=False,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("not owned by this builder", result.stdout)
            self.assertTrue((output / "plugins/groundwork/.codex-plugin/plugin.json").is_file())

    def test_builder_rejects_markerless_output_with_recomputed_inventory(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "marketplace"
            initial = subprocess.run(
                [sys.executable, "-B", str(BUILDER), "--output", str(output)],
                cwd=REPO,
                check=False,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
            )
            self.assertEqual(initial.returncode, 0, initial.stdout)
            (output / ".groundwork-marketplace-output").unlink()
            protected = output / "plugins/groundwork/UNOWNED-KEEP.txt"
            protected.write_text("keep\n", encoding="utf-8")
            write_runtime_manifest(output / "plugins/groundwork")

            result = subprocess.run(
                [sys.executable, "-B", str(BUILDER), "--output", str(output)],
                cwd=REPO,
                check=False,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("not owned by this builder", result.stdout)
            self.assertEqual(protected.read_text(encoding="utf-8"), "keep\n")

    def test_content_tamper_invalidates_runtime_provenance(self):
        with tempfile.TemporaryDirectory() as tmp:
            package_root = self.build(Path(tmp))
            readme = package_root / "README.md"
            readme.write_text(readme.read_text(encoding="utf-8") + "\ntampered\n", encoding="utf-8")

            result = self.check(package_root)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Runtime manifest content hash mismatch", result.stdout)
            self.assertIn("Runtime manifest README hash mismatch", result.stdout)

    def test_runtime_manifest_schema_tamper_invalidates_provenance(self):
        with tempfile.TemporaryDirectory() as tmp:
            package_root = self.build(Path(tmp))
            manifest_path = package_root / ".codex-plugin" / "runtime-manifest.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["schema_version"] = "tampered.v999"
            manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

            result = self.check(package_root)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Runtime manifest schema_version mismatch", result.stdout)

    def test_plugin_default_prompts_fit_codex_manifest_limit(self):
        plugin = json.loads((REPO / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8"))
        prompts = plugin["interface"]["defaultPrompt"]

        self.assertTrue(prompts)
        self.assertEqual(
            [len(prompt) for prompt in prompts if len(prompt) > 128],
            [],
            "Codex ignores defaultPrompt entries longer than 128 characters",
        )

    def test_runtime_package_contains_child_prompt_linter(self):
        with tempfile.TemporaryDirectory() as tmp:
            package_root = self.build(Path(tmp))
            linter = package_root / "skills/_shared/tools/lint_child_goal_prompt.py"
            template = package_root / (
                "skills/dispatch/adapters/codex_app_managed_worktree_thread/THREAD-PROMPT-TEMPLATE.md"
            )

            result = subprocess.run(
                [sys.executable, "-B", str(linter), "--template", str(template)],
                cwd=package_root,
                check=False,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
            )

            self.assertTrue(linter.is_file())
            self.assertEqual(result.returncode, 0, result.stdout)

    def test_runtime_reference_check_rejects_missing_package_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            package_root = Path(tmp)
            skill = package_root / "skills/example/SKILL.md"
            skill.parent.mkdir(parents=True)
            skill.write_text(
                "Run `python3 skills/_shared/tools/missing_linter.py input.md`.\n",
                encoding="utf-8",
            )
            errors: list[str] = []

            validate_runtime_markdown_references(package_root, errors)

            self.assertEqual(
                errors,
                [
                    "Runtime Markdown references a missing packaged file: "
                    "skills/example/SKILL.md:1 -> skills/_shared/tools/missing_linter.py"
                ],
            )

    def test_runtime_reference_check_rejects_missing_relative_code_ref_and_markdown_link(self):
        with tempfile.TemporaryDirectory() as tmp:
            package_root = Path(tmp)
            skill = package_root / "skills/example/SKILL.md"
            skill.parent.mkdir(parents=True)
            skill.write_text(
                'Load `MISSING.md` and then open [the next contract](OTHER.md "contract title").\n',
                encoding="utf-8",
            )
            errors: list[str] = []

            validate_runtime_markdown_references(package_root, errors)

            self.assertEqual(
                errors,
                [
                    "Runtime Markdown references a missing packaged file: "
                    "skills/example/SKILL.md:1 -> MISSING.md",
                    "Runtime Markdown references a missing packaged file: "
                    "skills/example/SKILL.md:1 -> OTHER.md",
                ],
            )

    def test_absent_artifact_marker_does_not_hide_other_missing_references(self):
        with tempfile.TemporaryDirectory() as tmp:
            package_root = Path(tmp)
            skill = package_root / "skills/example/SKILL.md"
            skill.parent.mkdir(parents=True)
            skill.write_text(
                "Use [required contract](MISSING.md), but do not create `TASK.md`.\n",
                encoding="utf-8",
            )
            errors: list[str] = []

            validate_runtime_markdown_references(package_root, errors)

            self.assertEqual(
                errors,
                [
                    "Runtime Markdown references a missing packaged file: "
                    "skills/example/SKILL.md:1 -> MISSING.md"
                ],
            )

    def test_maintainer_marker_does_not_hide_another_missing_script_reference(self):
        with tempfile.TemporaryDirectory() as tmp:
            package_root = Path(tmp)
            skill = package_root / "skills/example/SKILL.md"
            skill.parent.mkdir(parents=True)
            skill.write_text(
                "`scripts/maintainer-only.py` is maintainer-only, but "
                "use `scripts/codex-hooks/required-but-missing.py`.\n",
                encoding="utf-8",
            )
            errors: list[str] = []

            validate_runtime_markdown_references(package_root, errors)

            self.assertEqual(
                errors,
                [
                    "Runtime Markdown references a missing packaged file: "
                    "skills/example/SKILL.md:1 -> scripts/codex-hooks/required-but-missing.py"
                ],
            )

    def test_runtime_reference_check_ignores_non_runtime_markdown_and_marked_maintainer_command(self):
        with tempfile.TemporaryDirectory() as tmp:
            package_root = Path(tmp)
            skill = package_root / "skills/example/SKILL.md"
            skill.parent.mkdir(parents=True)
            canonical = package_root / "skills/_shared/tools/canonical.py"
            canonical.parent.mkdir(parents=True)
            canonical.write_text("pass\n", encoding="utf-8")
            skill.write_text(
                "Installed runtime uses `skills/_shared/tools/canonical.py`; source-repo maintainers may run "
                "`python3 scripts/maintainer_only.py input.md`.\n",
                encoding="utf-8",
            )
            example = package_root / "examples/example.md"
            example.parent.mkdir(parents=True)
            example.write_text("Run `python3 skills/example/not_packaged.py`.\n", encoding="utf-8")
            errors: list[str] = []

            validate_runtime_markdown_references(package_root, errors)

            self.assertEqual(errors, [])

    def test_reference_depth_starts_at_public_skill_entries(self):
        with tempfile.TemporaryDirectory() as tmp:
            skills_root = Path(tmp) / "skills"
            public_entry = skills_root / "verify/SKILL.md"
            public_branch = skills_root / "verify/BRANCH.md"
            shared_root = skills_root / "_shared/ROOT.md"
            shared_middle = skills_root / "_shared/MIDDLE.md"
            shared_leaf = skills_root / "_shared/LEAF.md"
            for path in (public_entry, public_branch, shared_root, shared_middle, shared_leaf):
                path.parent.mkdir(parents=True, exist_ok=True)
            public_entry.write_text("Read `BRANCH.md`.\n", encoding="utf-8")
            public_branch.write_text("Done.\n", encoding="utf-8")
            shared_root.write_text("See `MIDDLE.md`.\n", encoding="utf-8")
            shared_middle.write_text("See `LEAF.md`.\n", encoding="utf-8")
            shared_leaf.write_text("Done.\n", encoding="utf-8")

            self.assertEqual(public_entry_reference_depth(skills_root), 2)

    def test_reference_depth_includes_markdown_links_with_titles(self):
        with tempfile.TemporaryDirectory() as tmp:
            skills_root = Path(tmp) / "skills"
            public_entry = skills_root / "verify/SKILL.md"
            middle = skills_root / "verify/MIDDLE.md"
            leaf = skills_root / "verify/LEAF.md"
            for path in (public_entry, middle, leaf):
                path.parent.mkdir(parents=True, exist_ok=True)
            public_entry.write_text('[middle](MIDDLE.md "next")\n', encoding="utf-8")
            middle.write_text("[leaf](LEAF.md)\n", encoding="utf-8")
            leaf.write_text("Done.\n", encoding="utf-8")

            self.assertEqual(public_entry_reference_depth(skills_root), 3)


if __name__ == "__main__":
    unittest.main()
