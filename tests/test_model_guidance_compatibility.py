"""Static skill-contract regressions, not model-execution or runtime evidence."""

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def section(path, heading):
    text = (ROOT / path).read_text(encoding="utf-8")
    return text.split(f"## {heading}\n", 1)[1].split("\n## ", 1)[0]


class ModelGuidanceCompatibilityTests(unittest.TestCase):
    def loading_clauses(self, text, pattern):
        clauses = [line for line in text.splitlines() if re.search(pattern, line)]
        self.assertTrue(clauses, f"No operative clause matching {pattern}")
        return clauses

    def test_lifecycle_load_requires_a_decision_in_caller_and_reference(self):
        workflow = section("skills/implement/IMPLEMENT-BRANCHES.md", "Source And Gate Workflow")
        verify = section("skills/verify/VERIFY-ROUTER-BRANCHES.md", "Branch Workflows")
        trigger = section("skills/_shared/LIFECYCLE-PREFLIGHT.md", "Trigger Policy")
        # Inspect the operative loading clauses, not examples or a distant disclaimer.
        # Check every matching clause so a second broad instruction cannot hide
        # behind the first correctly scoped reference.
        clauses = self.loading_clauses(workflow, r"LIFECYCLE-PREFLIGHT\.md")
        clauses += self.loading_clauses(verify, r"LIFECYCLE-PREFLIGHT\.md")
        clauses += self.loading_clauses(trigger, r"^(?:Run|Load) preflight\b")
        for clause in clauses:
            with self.subTest(clause=clause):
                self.assertRegex(clause, r"\bonly (?:when|for)\b")
                self.assertRegex(clause, r"\brecover\w*\b")
                self.assertRegex(clause, r"\b(?:state|transition)\b")
                self.assertRegex(clause, r"\b(?:decision|depends)\b")
                self.assertNotRegex(clause, r"when the task may (?:write|create|mutate)")
                # Only inspect the lifecycle condition; a separate topology rule
                # later in the same line must remain possible.
                condition = re.split(r"\bonly (?:when|for)\b", clause, maxsplit=1)[1]
                condition = re.split(r"[.;]", condition, maxsplit=1)[0]
                self.assertNotRegex(condition, r"\b(?:topology|implementation|shared-file|local tests)\b")
        self.assertRegex(verify, r"topology-only[^.]*GIT-TOPOLOGY-GATE\.md")

    def test_topology_load_condition_is_consistent_through_preflight(self):
        workflow = section("skills/implement/IMPLEMENT-BRANCHES.md", "Source And Gate Workflow")
        fields = section("skills/_shared/LIFECYCLE-PREFLIGHT.md", "Field Rules")
        modes = section("skills/_shared/LIFECYCLE-PREFLIGHT.md", "Mode Rules")
        clauses = self.loading_clauses(workflow, r"GIT-TOPOLOGY-GATE\.md")
        clauses += self.loading_clauses(fields, r"^\| `Execution Topology`")
        clauses += self.loading_clauses(modes, r"^- `implement`:")
        for clause in clauses:
            with self.subTest(clause=clause):
                self.assertRegex(clause, r"\bonly (?:when|for)\b")
                self.assertIn("PR-bound", clause)
                self.assertRegex(clause, r"\b(?:unresolved|unsafe)\b")
                self.assertNotRegex(clause, r"(?:run|use) (?:the )?git topology gate before writes")

    def test_ordinary_fix_retains_local_checks_without_lifecycle_state(self):
        entry = "skills/implement/SKILL.md"
        evidence = section(entry, "Evidence Boundary")
        workflow = section("skills/implement/IMPLEMENT-BRANCHES.md", "Source And Gate Workflow")
        policy = section("skills/_shared/LIFECYCLE-PREFLIGHT.md", "Trigger Policy")
        core = section("skills/_shared/LIFECYCLE-PREFLIGHT.md", "Core Rule")
        for requirement in (r"git state", r"relevant diffs", r"source truth", r"tests/checks/config"):
            self.assertRegex(evidence, requirement)
        self.assertRegex(workflow, r"Inspect current branch, dirty state, relevant diffs")
        self.assertRegex(workflow, r"ordinary-implementation[^\n]*lightweight plan")
        self.assertRegex(workflow, r"Run the fastest relevant checks")
        self.assertRegex(policy, r"Skip[^\n]*ordinary one-off fixes")
        self.assertRegex(policy, r"[Pp]reserve[^\n]*checkpoint[^\n]*host")
        self.assertRegex(policy, r"does not[^\n]*bypass recovery checks")
        self.assertRegex(core, r"transient[^\n]*not written by default")

    def test_state_machine_and_evidence_references_remain_claim_scoped(self):
        snapshot = section("skills/_shared/LIFECYCLE-PREFLIGHT.md", "Preflight Snapshot")
        for clause in self.loading_clauses(snapshot, r"WORKFLOW-STATE-MACHINE\.md"):
            self.assertRegex(clause, r"\bonly (?:when|for)\b")
            self.assertRegex(clause, r"transition legality")
        policy = section("skills/_shared/LIFECYCLE-PREFLIGHT.md", "Trigger Policy")
        self.assertRegex(policy, r"[Ee]vidence[^\n]*claim[^\n]*corresponding")
        boundary = section("skills/implement/IMPLEMENT-BRANCHES.md", "Evidence Claim Boundaries")
        for reference in ("RUNTIME-CAPABILITY.md", "RELEASE-EVIDENCE-CLAIM.md"):
            self.assertIn(reference, boundary)

    def test_explicit_implementation_does_not_need_a_new_prd_approval(self):
        route = section("skills/implement/SKILL.md", "Route First")
        for boundary in (
            "User instructions take precedence",
            "higher-priority instructions and host permissions",
            "without a separate PRD or bypass phrase",
            "Honor user-requested pauses and approval checkpoints",
            "material missing decision, expanded scope/risk, or required permission",
            "continue independent authorized work",
        ):
            self.assertIn(boundary, route)

    def test_gate_owners_preserve_authorization_and_preparation(self):
        for path, heading in (
            ("skills/implement/IMPLEMENT-BRANCHES.md", "Gated Actions"),
            ("skills/_shared/GIT-TOPOLOGY-GATE.md", "Pre-remote Gate"),
            ("skills/_shared/GIT-BOUNDARY.md", "Gate Boundary"),
            ("skills/_shared/LIFECYCLE-PREFLIGHT.md", "Field Rules"),
            ("skills/verify/SKILL.md", "Stop Conditions"),
        ):
            with self.subTest(path=path):
                gate = section(path, heading)
                self.assertIn("authorization", gate)
                self.assertIn("scope", gate)
                self.assertIn("risk", gate)
                self.assertNotIn("output the approval gate before action", gate)
        workflow = section("skills/implement/IMPLEMENT-BRANCHES.md", "Source And Gate Workflow")
        self.assertIn("Complete authorized local preparation and checks", workflow)
        self.assertNotIn("remote-write gates before editing", workflow)

    def test_local_shared_edits_do_not_imply_pr_delivery(self):
        definitions = section("skills/_shared/GIT-TOPOLOGY-GATE.md", "Definitions")
        self.assertIn("the user expects a PR", definitions)
        self.assertIn("applicable project instructions require a PR", definitions)
        self.assertIn("does not by itself imply PR delivery", definitions)
        self.assertNotIn("- the work changes shared project files;", definitions)

    def test_current_directory_instruction_preserves_dirty_file_boundary(self):
        topology = "skills/_shared/GIT-TOPOLOGY-GATE.md"
        core = section(topology, "Core Rule")
        self.assertIn("Follow the user's explicit branch/current-directory instruction", core)
        self.assertIn("stop only affected edits when safe separation is impossible", core)
        self.assertIn("does not authorize commit, push, PR creation, or deployment", core)
        prewrite = section(topology, "Pre-write Gate")
        self.assertIn("scoped edits can preserve unrelated changes", prewrite)
        self.assertIn("otherwise worktree_required or blocked", prewrite)

    def test_dirty_file_exception_does_not_override_required_pr_topology(self):
        prewrite = section("skills/_shared/GIT-TOPOLOGY-GATE.md", "Pre-write Gate")
        self.assertIn("main/master/trunk + PR-bound implementation", prewrite)
        self.assertIn("branch_required or worktree_required before edits", prewrite)
        self.assertIn("current_branch_ok only when preceding PR-bound topology requirements are satisfied", prewrite)
        self.assertNotIn("current_branch_ok when scoped edits can preserve unrelated changes", prewrite)

    def test_plain_evidence_question_does_not_load_lifecycle_by_topic(self):
        workflow = section("skills/verify/VERIFY-ROUTER-BRANCHES.md", "Branch Workflows")
        self.assertIn("only when the decision depends on lifecycle/task-state transition", workflow)
        self.assertIn("do not load lifecycle machinery solely because they mention source, UAT, or release", workflow)
        self.assertNotIn("task-state, source-truth, UAT/release, or closeout claims are in scope", workflow)

    def test_material_clarification_and_evidence_truth_are_retained(self):
        prd = section("skills/to-prd/SKILL.md", "Hard Stops")
        self.assertIn("would materially change the spec", prd)
        self.assertIn("Do not invent backend fields", prd)
        verify = section("skills/verify/SKILL.md", "Stop Conditions")
        self.assertIn("without fresh in-scope evidence", verify)
        self.assertIn("keep stronger claims unverified", verify)
        self.assertIn("Preserve user-requested pauses, approval checkpoints, and host permissions", verify)


if __name__ == "__main__":
    unittest.main()
