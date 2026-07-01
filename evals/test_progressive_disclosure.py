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

    def test_dispatch_default_package_path_conditions_heavy_references(self):
        skill = self.read("skills/dispatch/SKILL.md")
        package = self.read("skills/dispatch/DISPATCH-PACKAGE.md")
        details_path = ROOT / "skills/dispatch/DISPATCH-PACKAGE-DETAILS.md"
        self.assertTrue(details_path.exists())
        details = details_path.read_text(encoding="utf-8")

        self.assertIn("## Default Dispatch Package v2 Path", skill)
        self.assertIn("Read only the accepted task artifact and `DISPATCH-PACKAGE.md`", skill)
        self.assertIn("Default output: compact dispatch matrix plus package skeleton", skill)
        self.assertIn("Do not execute, spawn subagents, create worktrees, or mutate branches", skill)
        default_section = skill.split("## Default Dispatch Package v2 Path", 1)[1].split("## Evidence Boundary", 1)[0]
        self.assertNotIn("DISPATCH-PACKAGE-DETAILS.md", default_section)
        self.assertNotIn("RESULT-PACKAGE.md", default_section)
        self.assertNotIn("RUNTIME-ADAPTERS.md", default_section)
        self.assertNotIn("ROUTING-PROFILES.md", default_section)
        self.assertNotIn("EXAMPLES.md", default_section)
        self.assertIn("Load `DISPATCH-PACKAGE-DETAILS.md` only when", skill)
        self.assertIn("full schema, adapter contract, or field-level validation", skill)
        self.assertIn("Load `RESULT-PACKAGE.md` only when", skill)
        self.assertIn("result package expectations or returned evidence", skill)
        self.assertIn("Load `RUNTIME-ADAPTERS.md` only when", skill)
        self.assertIn("runtime adapter, runtime capability, or selector behavior", skill)
        self.assertIn("Load `ROUTING-PROFILES.md` only when", skill)
        self.assertIn("model/profile selection is material", skill)
        self.assertIn("Load `EXAMPLES.md` only when", skill)
        self.assertIn("asks for examples or format ambiguity blocks output", skill)

        default_path_index = skill.index("## Default Dispatch Package v2 Path")
        load_only_index = skill.index("## Load Only What Fits")
        self.assertLess(default_path_index, load_only_index)

        self.assertIn("## Compact Default Contract", package)
        self.assertLessEqual(len(package.splitlines()), 150)
        self.assertIn("package-only", package)
        self.assertIn("must not execute", package)
        self.assertIn("human-reviewable package skeleton", package)
        self.assertIn("not adapter-complete until extended fields are supplied", package)
        self.assertIn("adapter_completeness: skeleton_only | adapter_ready", package)
        self.assertIn("adapter_ready requires `DISPATCH-PACKAGE-DETAILS.md`", package)
        self.assertIn("Do not load `RESULT-PACKAGE.md`", package)
        self.assertIn("Do not load `RUNTIME-ADAPTERS.md`", package)
        self.assertIn("Do not load `ROUTING-PROFILES.md`", package)
        self.assertIn("Do not load `EXAMPLES.md`", package)
        self.assertNotIn("## Schema", package)
        self.assertNotIn("## Required Package Completeness", package)
        self.assertNotIn("## Managed Worktree Package Rules", package)
        self.assertNotIn("legacy_compatibility:", package)

        self.assertIn("## Schema", details)
        self.assertIn("## Required Package Completeness", details)
        self.assertIn("## Managed Worktree Package Rules", details)
        self.assertIn("legacy_compatibility:", details)

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

    def test_verify_has_named_evidence_default_path_without_package_self_inspection(self):
        skill = self.read("skills/verify/SKILL.md")

        self.assertIn("## Default Path: Named Evidence Verification", skill)
        self.assertIn("`CLAIM.md`", skill)
        self.assertIn("`EVIDENCE.md`", skill)
        self.assertIn("this active `verify` contract", skill)
        self.assertIn("the user-named claim, evidence, scope, or check-output artifacts", skill)
        self.assertIn("`VERIFY-SCOPE.md` and `SCOPE-EVIDENCE-TEMPLATE.md`", skill)
        self.assertIn("Do not inspect Groundwork plugin README", skill)
        self.assertIn("`.codex-plugin/plugin.json`", skill)
        self.assertIn("other skill `SKILL.md` files", skill)
        self.assertIn("Scenario workspace allowlisted file discovery is allowed", skill)
        self.assertIn("do not treat allowlisted discovery of the named evidence files as a hard failure", skill)
        self.assertIn("keep the full verify safety boundary", skill)
        self.assertIn("missing evidence", skill)
        self.assertIn("bounded support/readiness judgment", skill)

        default_section = skill.split("## Default Path: Named Evidence Verification", 1)[1].split("## Evidence Boundary", 1)[0]
        read_only_section = default_section.split("Read only:", 1)[1].split("Do not inspect", 1)[0]
        self.assertNotIn("README", read_only_section)
        self.assertNotIn(".codex-plugin/plugin.json", read_only_section)
        self.assertNotIn("plugin manifests", read_only_section)
        self.assertNotIn("package internals", read_only_section)
        self.assertNotIn("other skill `SKILL.md`", read_only_section)

        default_path_index = skill.index("## Default Path: Named Evidence Verification")
        evidence_boundary_index = skill.index("## Evidence Boundary")
        load_only_index = skill.index("## Load Only What Fits")
        self.assertLess(default_path_index, evidence_boundary_index)
        self.assertLess(evidence_boundary_index, load_only_index)

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

    def test_to_prd_has_prompt_provided_compact_fast_path(self):
        skill = self.read("skills/to-prd/SKILL.md")

        self.assertIn("## Fast Path: Prompt-Provided Compact PRD", skill)
        self.assertIn("Read only the named task artifact and this active `to-prd` contract.", skill)
        self.assertIn("Do not inspect Groundwork plugin README", skill)
        self.assertIn("`.codex-plugin/plugin.json`", skill)
        self.assertIn("unrelated skill files", skill)
        self.assertIn("shared lifecycle/evidence references", skill)
        self.assertIn("Groundwork Maintenance Compact Path", skill)
        self.assertIn("Do not use the generic fast path for Groundwork-internal maintenance requests", skill)
        self.assertIn("runtime behavior, workflow changes, version enhancements, or skill-selection behavior", skill)
        self.assertIn("Preserve lifecycle-state framing", skill)
        self.assertIn("Requirement State, Source Truth / Evidence Level", skill)
        self.assertIn("source/package behavior", skill)
        self.assertIn("compact conversation PRD/spec", skill)
        self.assertIn("durable PRD artifact", skill)
        self.assertIn("load `PRD-TEMPLATE.md`, apply audience-first artifact fields", skill)
        self.assertIn("Mark missing product facts as **NEEDS CLARIFICATION**", skill)
        self.assertNotIn("proposed plugin or workflow change remains fast path", skill)

        fast_path_index = skill.index("## Fast Path: Prompt-Provided Compact PRD")
        maintenance_path_index = skill.index("## Groundwork Maintenance Compact Path")
        required_evidence_index = skill.index("## Required Evidence")

        self.assertLess(fast_path_index, required_evidence_index)
        self.assertLess(fast_path_index, maintenance_path_index)
        self.assertLess(maintenance_path_index, required_evidence_index)

    def test_branch_references_have_audience_first_headers(self):
        paths = [
            "skills/dispatch/EXAMPLES.md",
            "skills/dispatch/DISPATCH-ROUTER-BRANCHES.md",
            "skills/implement/IMPLEMENT-BRANCHES.md",
            "skills/verify/VERIFY-SCOPE.md",
            "skills/verify/VERIFY-ROUTER-BRANCHES.md",
            "skills/verify/QA-FAILURE-BRANCH.md",
            "skills/verify/RELEASE-READINESS-BRANCH.md",
            "skills/verify/RUNTIME-CAPABILITY-BRANCH.md",
            "skills/verify/NATIVE-CLOSEOUT-BRANCH.md",
            "skills/verify/UI-READINESS-BRANCH.md",
            "skills/verify/SUBAGENT-REVIEW-BRANCH.md",
            "skills/handoff/COMPLEX-HANDOFF-BRANCHES.md",
            "skills/handoff/NATIVE-HANDOFF-PACKAGE.md",
            "skills/handoff/STATE-FRESHNESS.md",
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
