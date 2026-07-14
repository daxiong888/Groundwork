import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


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

    def test_content_tamper_invalidates_runtime_provenance(self):
        with tempfile.TemporaryDirectory() as tmp:
            package_root = self.build(Path(tmp))
            readme = package_root / "README.md"
            readme.write_text(readme.read_text(encoding="utf-8") + "\ntampered\n", encoding="utf-8")

            result = self.check(package_root)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Runtime manifest content hash mismatch", result.stdout)
            self.assertIn("Runtime manifest README hash mismatch", result.stdout)

    def test_plugin_default_prompts_fit_codex_manifest_limit(self):
        plugin = json.loads((REPO / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8"))
        prompts = plugin["interface"]["defaultPrompt"]

        self.assertTrue(prompts)
        self.assertEqual(
            [len(prompt) for prompt in prompts if len(prompt) > 128],
            [],
            "Codex ignores defaultPrompt entries longer than 128 characters",
        )


if __name__ == "__main__":
    unittest.main()
