import importlib.util
import json
import re
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / "scripts" / "codex-hooks" / "groundwork_route_registry.json"
CLASSIFIER_PATH = ROOT / "scripts" / "codex-hooks" / "groundwork_route_detection.py"


def load_runtime_classifier():
    spec = importlib.util.spec_from_file_location(
        "groundwork_route_detection_for_source_test",
        CLASSIFIER_PATH,
    )
    module = importlib.util.module_from_spec(spec)
    previous = sys.dont_write_bytecode
    sys.dont_write_bytecode = True
    try:
        spec.loader.exec_module(module)
    finally:
        sys.dont_write_bytecode = previous
    return module


class RouteRegistryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
        cls.classifier = load_runtime_classifier()

    def test_registry_is_runtime_classifier_source(self):
        self.assertEqual(Path(self.classifier.ROUTE_REGISTRY_PATH), REGISTRY_PATH)
        self.assertEqual(
            set(self.registry["public_routes"]),
            self.classifier.PUBLIC_SKILL_ROUTES,
        )
        self.assertEqual(
            tuple(self.registry["prompt_precedence"]),
            self.classifier.PROMPT_PRECEDENCE,
        )

    def test_registry_matches_public_skill_directories_and_descriptions(self):
        public_skill_dirs = {
            path.parent.name
            for path in (ROOT / "skills").glob("*/SKILL.md")
            if path.parent.name != "_shared"
        }
        self.assertEqual(set(self.registry["public_routes"]), public_skill_dirs)

        for name, contract in self.registry["public_routes"].items():
            text = (ROOT / "skills" / name / "SKILL.md").read_text(encoding="utf-8")
            description = re.search(r"^description:\s*(.+)$", text, re.MULTILINE)
            self.assertIsNotNone(description, name)
            for fragment in contract["description_fragments"]:
                self.assertIn(fragment.lower(), description.group(1).lower(), f"{name}: {fragment}")

    def test_registry_matches_state_machine_table(self):
        text = (ROOT / "skills" / "_shared" / "WORKFLOW-STATE-MACHINE.md").read_text(encoding="utf-8")
        rows = {}
        for line in text.splitlines():
            match = re.match(r"\| `([^`]+)` \| (.+?) \| (.+?) \|$", line)
            if match and match.group(1) in self.registry["public_routes"]:
                rows[match.group(1)] = (match.group(2), match.group(3))

        self.assertEqual(set(rows), set(self.registry["public_routes"]))
        for name, contract in self.registry["public_routes"].items():
            accepted, produced = rows[name]
            for state in contract["accepted_pre_states"]:
                self.assertIn(state, accepted, f"{name}: accepted {state}")
            for state in contract["produced_states"]:
                self.assertIn(state, produced, f"{name}: produced {state}")

    def test_prompt_precedence_rules_are_unique(self):
        rules = self.registry["prompt_precedence"]
        self.assertEqual(len(rules), len(set(rules)))
        self.assertEqual(rules[-1], "direct_fallback")

    def test_feedback_transitions_are_public_bounded_and_non_automatic(self):
        requirement_states = {
            "raw",
            "grilled",
            "prd_draft",
            "prd_accepted",
            "issue_ready",
            "implementation_ready",
            "verified",
            "blocked",
        }
        transitions = self.registry["feedback_transitions"]

        self.assertIn("qa_gap_closure", transitions)
        for name, transition in transitions.items():
            self.assertIn(transition["from_route"], self.registry["public_routes"], name)
            self.assertIn(transition["to_route"], self.registry["public_routes"], name)
            self.assertTrue(transition["accepted_from_states"], name)
            self.assertTrue(
                set(transition["accepted_from_states"]).issubset(requirement_states),
                name,
            )
            self.assertIn(
                transition["preserved_or_produced_state"], requirement_states, name
            )
            self.assertTrue(transition["gate"], name)
            self.assertIs(transition["automatic"], False, name)

    def test_qa_gap_closure_contract_is_documented(self):
        transition = self.registry["feedback_transitions"]["qa_gap_closure"]
        self.assertEqual(transition["preserved_or_produced_state"], "implementation_ready")
        self.assertEqual(
            set(transition["requires"]),
            {
                "unchanged_source_truth",
                "unchanged_acceptance_criteria",
                "bounded_failure_package",
                "matching_original_reqa_identity",
                "existing_implementation_authority",
                "no_new_or_increased_risk",
                "finite_scoped_next_action",
                "new_evidence_or_changed_hypothesis",
            },
        )
        self.assertIn(
            "implementation_ready",
            self.registry["public_routes"]["verify"]["produced_states"],
        )

        state_machine = (
            ROOT / "skills" / "_shared" / "WORKFLOW-STATE-MACHINE.md"
        ).read_text(encoding="utf-8")
        qa_contract = (ROOT / "skills" / "verify" / "QA-FIX-QA.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("qa_gap_closure", state_machine)
        self.assertIn("qa_gap_closure", qa_contract)


if __name__ == "__main__":
    unittest.main()
