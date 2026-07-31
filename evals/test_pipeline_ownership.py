import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class PipelineOwnershipTests(unittest.TestCase):
    def read(self, path):
        return (ROOT / path).read_text(encoding="utf-8")

    def test_to_issues_does_not_select_runtime(self):
        skill = self.read("skills/to-issues/SKILL.md")

        self.assertNotIn("Runtime Routing Candidate Rules", skill)
        self.assertNotIn("Runtime candidate block", skill)
        self.assertIn("`dispatch` owns those decisions after `triage` establishes readiness", skill)

    def test_triage_defers_runtime_selection_to_dispatch(self):
        skill = self.read("skills/triage/SKILL.md")
        brief = self.read("skills/triage/AGENT-BRIEF.md")
        goal_contract = self.read("skills/_shared/GOAL-CONTRACT.md")

        self.assertIn("`Preferred Runtime` to `dispatch_may_choose`", skill)
        self.assertIn("`Preferred Runtime` to `dispatch_may_choose`", brief)
        self.assertNotIn("Execution Profile Recommendation", brief)
        self.assertIn("upstream producers must use `dispatch_may_choose`", goal_contract)

    def test_runtime_workflow_names_dispatch_as_single_owner(self):
        workflow = self.read("docs/runtime-dispatch-workflow.md")

        self.assertIn("`dispatch` is the sole post-readiness runtime/package route owner", workflow)
        self.assertNotIn("runtime candidate fields", workflow)

    def test_native_handoff_machine_and_display_owners_are_distinct(self):
        native = self.read("skills/handoff/NATIVE-HANDOFF-PACKAGE.md")
        review = self.read("skills/handoff/REVIEW-PACKAGE.md")
        scenario = self.read("evals/scenarios/native-handoff-package.md")

        self.assertIn("owns the canonical `native_handoff_package` machine schema", native)
        self.assertIn("`skills/handoff/SKILL.md` owns route selection", native)
        self.assertIn("`skills/handoff/REVIEW-PACKAGE.md` owns the human-readable display shape", native)
        self.assertIn("from `NATIVE-HANDOFF-PACKAGE.md`", review)
        self.assertIn("human-readable display labels only", review)
        self.assertIn("does not own or require a second label-to-key mapping", review)
        self.assertNotIn("from `skills/handoff/SKILL.md`", review)
        self.assertNotIn("map labels to the canonical snake_case keys", review)
        self.assertIn("owns the canonical `native_handoff_package` machine schema", scenario)

if __name__ == "__main__":
    unittest.main()
