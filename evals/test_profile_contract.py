import csv
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class ProfileContractTests(unittest.TestCase):
    def read(self, relative):
        return (ROOT / relative).read_text(encoding="utf-8")

    def test_cognitive_and_runtime_vocabularies_have_single_owners(self):
        cognitive = self.read("skills/_shared/COGNITIVE-BUDGET.md")
        runtime = self.read("skills/_shared/RUNTIME-CAPABILITY.md")
        decision = self.read("skills/_shared/DECISION-MAPPING.md")

        self.assertIn(
            "model_profile: fast_scan | balanced_work | strong_reasoning | exhaustive_review | spark_iteration",
            cognitive,
        )
        self.assertNotIn("selector_enforcement: tool_enforced |", cognitive)
        self.assertIn("selector_enforcement: tool_enforced | prompt_preference | unavailable | unknown", runtime)
        self.assertIn("only runtime contract that owns", runtime)
        self.assertNotIn("model_profile:", decision)
        self.assertNotIn("selector_enforcement:", decision)

    def test_dispatch_separates_request_policy_from_result_evidence(self):
        details = self.read("skills/dispatch/DISPATCH-PACKAGE-DETAILS.md")
        result = self.read("skills/dispatch/RESULT-PACKAGE.md")
        prompt = self.read(
            "skills/dispatch/adapters/codex_app_managed_worktree_thread/THREAD-PROMPT-TEMPLATE.md"
        )
        selector_delta = self.read(
            "skills/dispatch/adapters/codex_app_managed_worktree_thread/SELECTOR-ENFORCEMENT.md"
        )

        self.assertIn("selector_policy: tool_if_available_else_prompt_preference", details)
        self.assertIn("routing_reason, selector_policy", details)
        self.assertNotIn("routing_reason, selector_enforcement", details)
        self.assertIn("Selector request policy: {execution_profile.selector_policy}", prompt)
        self.assertIn("selector_enforcement is returned evidence", result.replace("`", ""))
        self.assertIn("does not redefine them", selector_delta)

    def test_dispatch_profile_defaults_use_canonical_profile_tokens(self):
        profiles = self.read("skills/dispatch/ROUTING-PROFILES.md")

        for profile in ("fast_scan", "balanced_work", "strong_reasoning", "exhaustive_review"):
            self.assertIn(f"`{profile}`", profiles)
        self.assertNotIn("fast coding model", profiles)
        self.assertNotIn("balanced coding model", profiles)
        self.assertNotIn("strongest coding/reasoning available", profiles)

    def test_request_side_sources_do_not_reintroduce_selector_enforcement(self):
        verdict_model = self.read("evals/verdict_model.py")
        prd = self.read("docs/prd-dispatch-runtime-router.md")
        with (ROOT / "evals/prompts/v0.5-runtime-capability.csv").open(
            encoding="utf-8", newline=""
        ) as handle:
            rows = {row["id"]: row for row in csv.DictReader(handle)}
        expected_behavior = rows["v050-runtime-capability-001"]["expected_behavior"]

        self.assertIn('selector_policy="tool_if_available_else_prompt_preference"', verdict_model)
        self.assertNotIn("selector_enforcement_policy", verdict_model)
        self.assertEqual(prd.count("selector_policy: tool_if_available_else_prompt_preference"), 2)
        self.assertNotIn("selector_enforcement: tool_if_available_else_prompt_preference", prd)
        self.assertIn("selector_policy", expected_behavior)
        self.assertIn("result-side selector_enforcement", expected_behavior)
        self.assertNotIn("record the request as model profile plus selector_enforcement", expected_behavior)


if __name__ == "__main__":
    unittest.main()
