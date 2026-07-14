import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REVIEW_LOOP = ROOT / "skills/_shared/REVIEW-LOOP.md"
ROLE_COMPAT = ROOT / "skills/_shared/ROLE-SEPARATION.md"
LOW_RISK_COMPAT = ROOT / "skills/_shared/LOW-RISK-COORDINATOR-INTAKE.md"
RESULT_PACKAGE = ROOT / "skills/dispatch/RESULT-PACKAGE.md"
RUNTIME_WORKFLOW = ROOT / "docs/runtime-dispatch-workflow.md"
ADAPTER_RESULT = (
    ROOT
    / "skills/dispatch/adapters/codex_app_managed_worktree_thread/RESULT-PACKAGE-TEMPLATE.md"
)
CLOSEOUT = (
    ROOT
    / "skills/dispatch/adapters/codex_app_managed_worktree_thread/CLOSEOUT-PACKAGE-TEMPLATE.md"
)
MERGE_BACK = (
    ROOT
    / "skills/dispatch/adapters/codex_app_managed_worktree_thread/MERGE-BACK-PROTOCOL.md"
)


class ReviewContractTests(unittest.TestCase):
    def read(self, path: Path) -> str:
        return path.read_text(encoding="utf-8")

    def test_review_loop_is_the_single_canonical_contract(self):
        review = self.read(REVIEW_LOOP)
        source_line = next(line for line in review.splitlines() if line.startswith("Source of Truth:"))

        self.assertIn("canonical review contract", source_line)
        self.assertNotIn("ROLE-SEPARATION.md", source_line)
        self.assertNotIn("LOW-RISK-COORDINATOR-INTAKE.md", source_line)
        for heading in (
            "## Materiality and Fan-Out",
            "## Role Authority",
            "## Review Loop States",
            "## Low-Risk Coordinator Intake",
            "## Remediation Flow",
        ):
            self.assertIn(heading, review)

    def test_canonical_contract_preserves_review_authority_and_staleness(self):
        review = self.read(REVIEW_LOOP)

        for rule in (
            "fresh-context independent reviewer",
            "becomes an implementer",
            "authority is spent",
            "material fix",
            "previous clean review stale",
            "Self-check Evidence",
            "Clean Review Evidence",
            "Independent Verification Evidence",
        ):
            self.assertIn(rule, review)

    def test_canonical_contract_preserves_materiality_and_low_risk_boundary(self):
        review = self.read(REVIEW_LOOP)

        for trigger in (
            "public skill",
            "shared guardrail",
            "adapter contract",
            "package template",
            "security",
            "migration",
            "validation skipped, failed, partial",
            "multiple concurrent returns",
            "user requested independent review",
        ):
            self.assertIn(trigger, review)
        for eligibility in (
            "exactly one package",
            "0-2 low-risk files",
            "not_applicable_with_reason",
            "no materiality or fan-out trigger",
            "not `clean_review_passed`",
        ):
            self.assertIn(eligibility, review)

    def test_legacy_entries_are_short_one_way_compatibility_routes(self):
        for path in (ROLE_COMPAT, LOW_RISK_COMPAT):
            text = self.read(path)
            source_line = next(line for line in text.splitlines() if line.startswith("Source of Truth:"))

            self.assertEqual(source_line, "Source of Truth: `skills/_shared/REVIEW-LOOP.md`.")
            self.assertLessEqual(len(text.splitlines()), 22, path.name)
            self.assertNotIn("```", text, path.name)
            self.assertNotIn("## Materiality", text, path.name)
            self.assertNotIn("## Role Authority", text, path.name)
            self.assertNotIn("## Eligibility", text, path.name)
        self.assertNotIn("LOW-RISK-COORDINATOR-INTAKE.md", self.read(ROLE_COMPAT))
        self.assertNotIn("ROLE-SEPARATION.md", self.read(LOW_RISK_COMPAT))

    def test_runtime_non_dispatch_references_use_canonical_review_contract(self):
        excluded = {REVIEW_LOOP, ROLE_COMPAT, LOW_RISK_COMPAT}
        offenders = []
        for path in (ROOT / "skills").rglob("*.md"):
            if path in excluded or "dispatch" in path.parts:
                continue
            text = self.read(path)
            if "ROLE-SEPARATION.md" in text or "LOW-RISK-COORDINATOR-INTAKE.md" in text:
                offenders.append(path.relative_to(ROOT).as_posix())

        self.assertEqual(offenders, [])

    def test_managed_worktree_merge_gate_preserves_clean_review_authority_and_freshness(self):
        closeout = self.read(CLOSEOUT)
        merge_back = self.read(MERGE_BACK)

        for rule in (
            "review: {kind, required, status, reviewer_context, reviewed_material_change_id, findings, evidence}",
            "review_loop: {status, latest_material_change_id, previous_review_stale_reason, findings_addressed, next_review_required, next_route}",
            "`review.kind: clean`",
            "`review.reviewed_material_change_id` equal to `review_loop.latest_material_change_id`",
            "`review_loop.status: clean_review_passed`",
            "`review_loop.next_review_required: false`",
            "Coordinator intake, self-review, stale review evidence",
        ):
            self.assertIn(rule, closeout)

        for rule in (
            "review_kind: clean | coordinator_intake | self_check | not_applicable",
            "reviewed_material_change_id: \"\"",
            "latest_material_change_id: \"\"",
            "review_loop_status:",
            "next_review_required: true | false",
            "equal non-empty `reviewed_material_change_id` and `latest_material_change_id`",
            "stale evidence must not set `clean_review_passed: true`",
        ):
            self.assertIn(rule, merge_back)

    def test_result_package_base_owns_reviewed_material_change_freshness(self):
        result = self.read(RESULT_PACKAGE)
        adapter = self.read(ADAPTER_RESULT)
        workflow = self.read(RUNTIME_WORKFLOW)
        review_shape = (
            "review: {kind, required, status, reviewer_context, "
            "reviewed_material_change_id, findings, evidence}"
        )

        self.assertIn(review_shape, result)
        self.assertIn(
            "`review.reviewed_material_change_id` must equal "
            "`review_loop.latest_material_change_id`",
            result,
        )
        self.assertNotIn(review_shape, adapter)
        self.assertIn("Base `review.reviewed_material_change_id`", adapter)
        self.assertIn("`review.reviewed_material_change_id`", workflow)


if __name__ == "__main__":
    unittest.main()
