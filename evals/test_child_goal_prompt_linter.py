import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from skills._shared.tools.lint_goal_contract import lint as lint_goal_contract

REPO = Path(__file__).resolve().parents[1]
CANONICAL = REPO / "skills" / "_shared" / "tools" / "lint_child_goal_prompt.py"
WRAPPER = REPO / "scripts" / "lint_child_goal_prompt.py"


class ChildGoalPromptLinterTests(unittest.TestCase):
    def run_linter(self, script: Path, text: str, *args: str) -> subprocess.CompletedProcess[str]:
        with tempfile.TemporaryDirectory() as tmp:
            prompt = Path(tmp) / "prompt.md"
            prompt.write_text(text, encoding="utf-8")
            return subprocess.run(
                [sys.executable, "-B", str(script), *args, str(prompt)],
                cwd=REPO,
                check=False,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
            )

    def test_canonical_linter_accepts_executable_goal(self):
        result = self.run_linter(CANONICAL, "/goal implement the accepted task\n\nConstraints follow.\n")

        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertEqual(result.stdout, "Child Goal Prompt Lint: pass\n")

    def test_canonical_linter_rejects_placeholder_goal(self):
        result = self.run_linter(CANONICAL, "/goal <one executable task>\n")

        self.assertEqual(result.returncode, 1)
        self.assertIn("goal command must be executable, not a placeholder", result.stdout)

    def test_canonical_linter_rejects_goal_prefix_that_is_not_the_goal_command(self):
        result = self.run_linter(CANONICAL, "/goalkeeper do unrelated work\n")

        self.assertEqual(result.returncode, 1)
        self.assertIn("first non-empty line must start with /goal", result.stdout)

    def test_goal_contract_linter_uses_the_same_goal_command_boundary(self):
        findings = lint_goal_contract("Goal Command: /goalkeeper do unrelated work\n")

        self.assertIn(("Goal Command", "Goal Command must start with /goal"), findings)

    def test_source_repo_wrapper_matches_canonical_linter(self):
        text = "Intro before /goal\n/goal implement the accepted task\n"

        canonical = self.run_linter(CANONICAL, text)
        wrapper = self.run_linter(WRAPPER, text)

        self.assertEqual((wrapper.returncode, wrapper.stdout), (canonical.returncode, canonical.stdout))

    def test_template_mode_accepts_canonical_prompt_block(self):
        template = (
            "Do not prepend prose. Do not wrap the rendered prompt in a fenced code block.\n\n"
            "```text\n{goal_contract.goal_command}\n\nConstraints follow.\n```\n"
        )

        result = self.run_linter(CANONICAL, template, "--template")

        self.assertEqual(result.returncode, 0, result.stdout)

    def test_template_mode_rejects_goal_prefix_that_is_not_the_goal_command(self):
        template = (
            "Do not prepend prose. Do not wrap the rendered prompt in a fenced code block.\n\n"
            "```text\n/goalkeeper do unrelated work\n```\n"
        )

        result = self.run_linter(CANONICAL, template, "--template")

        self.assertEqual(result.returncode, 1)


if __name__ == "__main__":
    unittest.main()
