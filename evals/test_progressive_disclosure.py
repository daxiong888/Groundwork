import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class ProgressiveDisclosureTests(unittest.TestCase):
    def read(self, path):
        return (ROOT / path).read_text(encoding="utf-8")

    def test_dispatch_skill_loads_examples_on_demand(self):
        skill = self.read("skills/dispatch/SKILL.md")
        examples = self.read("skills/dispatch/EXAMPLES.md")

        self.assertIn("EXAMPLES.md", skill)
        self.assertIn("Runtime package examples", skill)
        self.assertNotIn("## Runtime Package Examples", skill)
        self.assertNotIn("```yaml", skill)
        self.assertIn("## Runtime Package Examples", examples)
        self.assertIn("```yaml", examples)

    def test_verify_skill_routes_branch_templates_to_references(self):
        skill = self.read("skills/verify/SKILL.md")
        branch_files = [
            "VERIFY-SCOPE.md",
            "QA-FAILURE-BRANCH.md",
            "RELEASE-READINESS-BRANCH.md",
            "RUNTIME-CAPABILITY-BRANCH.md",
            "NATIVE-CLOSEOUT-BRANCH.md",
            "UI-READINESS-BRANCH.md",
            "SUBAGENT-REVIEW-BRANCH.md",
        ]

        for branch_file in branch_files:
            self.assertIn(branch_file, skill)

        self.assertNotIn(
            "Load `VERIFY-SCOPE.md` and `SCOPE-EVIDENCE-TEMPLATE.md` before producing any verification report body",
            skill,
        )
        self.assertNotIn("QA Failure\n- Expected:", skill)
        self.assertNotIn("release_evidence_claim:\n", skill)
        self.assertNotIn("UI Evidence\n- Tool:", skill)
        self.assertNotIn("Runtime Capability:\n  - capability_status:", skill)
        self.assertNotIn("Visual Packet Evidence Boundary", skill)
        self.assertNotIn("For code-diff-only rows, keep the labeled verdict line mechanically safe", skill)
        self.assertNotIn("keep labeled `Verdict`, `Result`, `Status`, `Recommendation`, and `Conclusion` lines", skill)
        self.assertIn("release state, UAT state", self.read("skills/verify/VERIFY-SCOPE.md"))
        self.assertIn("Claimed Behavior: code diff only sufficiency claim", self.read("skills/verify/VERIFY-SCOPE.md"))

    def test_verify_scope_branch_is_not_loaded_by_other_branch_files(self):
        non_scope_branch_files = [
            "skills/verify/QA-FAILURE-BRANCH.md",
            "skills/verify/RELEASE-READINESS-BRANCH.md",
            "skills/verify/RUNTIME-CAPABILITY-BRANCH.md",
            "skills/verify/NATIVE-CLOSEOUT-BRANCH.md",
            "skills/verify/UI-READINESS-BRANCH.md",
            "skills/verify/SUBAGENT-REVIEW-BRANCH.md",
        ]

        for path in non_scope_branch_files:
            self.assertNotIn("VERIFY-SCOPE.md", self.read(path), path)

    def test_branch_references_have_audience_first_headers(self):
        paths = [
            "skills/dispatch/EXAMPLES.md",
            "skills/verify/VERIFY-SCOPE.md",
            "skills/verify/QA-FAILURE-BRANCH.md",
            "skills/verify/RELEASE-READINESS-BRANCH.md",
            "skills/verify/RUNTIME-CAPABILITY-BRANCH.md",
            "skills/verify/NATIVE-CLOSEOUT-BRANCH.md",
            "skills/verify/UI-READINESS-BRANCH.md",
            "skills/verify/SUBAGENT-REVIEW-BRANCH.md",
        ]
        required_fields = [
            "Target Reader:",
            "Reader Action Needed:",
            "Decision Supported:",
            "Artifact Type:",
            "Source of Truth:",
            "Scope:",
            "Out of Scope:",
            "Evidence Level:",
            "Safe to Share / Redaction Notes:",
        ]

        for path in paths:
            text = self.read(path)
            missing = [field for field in required_fields if field not in text]
            self.assertEqual(missing, [], path)


if __name__ == "__main__":
    unittest.main()
