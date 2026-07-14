import json
import re
import unittest
from pathlib import Path

from evals import route_detection, routing_schema


ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / "scripts" / "codex-hooks" / "groundwork_route_registry.json"


class RouteRegistryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))

    def test_registry_is_runtime_classifier_source(self):
        self.assertEqual(Path(route_detection.ROUTE_REGISTRY_PATH), REGISTRY_PATH)
        self.assertEqual(Path(routing_schema.ROUTE_REGISTRY_PATH), REGISTRY_PATH)
        self.assertEqual(set(self.registry["public_routes"]), route_detection.PUBLIC_SKILL_ROUTES)
        self.assertEqual(set(self.registry["public_routes"]), routing_schema.PUBLIC_SKILL_ROUTES)
        self.assertEqual(tuple(self.registry["prompt_precedence"]), route_detection.PROMPT_PRECEDENCE)

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


if __name__ == "__main__":
    unittest.main()
