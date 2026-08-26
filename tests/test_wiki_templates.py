import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TEMPLATES = ROOT / "skills" / "wiki" / "templates"
SHARED_CONTRACT = ROOT / "skills" / "_shared" / "LLM-WIKI.md"
INTEGRATION_DOC = ROOT / "docs" / "integrations" / "llm-wiki.md"
PRD = ROOT / "docs" / "prd-v0.5.2-public-wiki-skill.md"

LEGACY_PAGE_TEMPLATES = {
    "page-concept.md",
    "page-contract.md",
    "page-decision.md",
    "page-procedure.md",
    "page-query.md",
    "page-summary.md",
    "page-term.md",
}


class WikiTemplateTests(unittest.TestCase):
    def test_page_templates_use_one_base_and_one_type_contract(self):
        observed = {path.name for path in TEMPLATES.iterdir() if path.is_file()}

        self.assertEqual(
            observed,
            {"SCHEMA.md", "PAGE-TYPES.md", "error-book.md", "index.md", "log.md", "page.md"},
        )

    def test_page_base_keeps_required_frontmatter_and_claim_shape(self):
        page = (TEMPLATES / "page.md").read_text(encoding="utf-8")

        for field in (
            "type:",
            "status:",
            "target_reader:",
            "reader_action:",
            "default_evidence_layer:",
            "confidence:",
            "sources:",
            "last_updated:",
            "stale_risk:",
            "aliases:",
            "supersedes:",
            "superseded_by:",
            "contested_with:",
            "claim_policy:",
        ):
            self.assertIn(field, page)
        self.assertIn("Last checked: <YYYY-MM-DD>", page)
        self.assertIn("PAGE-TYPES.md", page)

    def test_type_contract_preserves_all_page_profiles_and_sections(self):
        profiles = (TEMPLATES / "PAGE-TYPES.md").read_text(encoding="utf-8")
        required_sections = {
            "concept": ["Summary", "Material Claims", "Related Pages", "Open Gaps"],
            "contract": [
                "Boundary",
                "Confirmed Contract Claims",
                "Unknown or Contested Claims",
                "Do Not Assume",
                "Open Gaps",
            ],
            "decision": ["Decision", "Rationale", "Material Claims", "Supersession", "Open Gaps"],
            "procedure": ["Prerequisites", "Steps", "Material Claims", "Failure Modes", "Open Gaps"],
            "query": ["Answer Boundary", "Answer", "Material Claims", "Follow-up Wiki Updates"],
            "summary": ["Summary Boundary", "Summary", "Material Claims", "Source Inventory", "Open Gaps"],
            "term": ["Meaning", "Aliases and Homonyms", "Material Claims", "Promotion Boundary"],
        }

        for page_type, sections in required_sections.items():
            match = re.search(
                rf"^### `{page_type}`\n(?P<body>.*?)(?=^### `|\Z)",
                profiles,
                flags=re.MULTILINE | re.DOTALL,
            )
            self.assertIsNotNone(match, page_type)
            for profile_field in (
                "Title prefix:",
                "Target reader:",
                "Reader action:",
                "Default evidence layer / stale risk:",
                "Section order:",
            ):
                self.assertIn(profile_field, match.group("body"), f"{page_type}: {profile_field}")
            for section in sections:
                self.assertIn(section, match.group("body"), f"{page_type}: {section}")

        self.assertIn("wiki_synthesis_only | source_backed | insufficient | blocked", profiles)
        self.assertIn("Glossary-only alignment is not PRD truth", profiles)

    def test_template_dates_are_explicit_placeholders(self):
        dated_files = [*TEMPLATES.glob("*.md"), SHARED_CONTRACT]

        for path in dated_files:
            text = path.read_text(encoding="utf-8")
            self.assertEqual(re.findall(r"\b20\d{2}-\d{2}-\d{2}\b", text), [], path.name)
            if "last_updated:" in text:
                self.assertIn('last_updated: "<YYYY-MM-DD>"', text, path.name)
        self.assertIn("### <YYYY-MM-DD>", (TEMPLATES / "log.md").read_text(encoding="utf-8"))
        prd = PRD.read_text(encoding="utf-8")
        self.assertNotRegex(prd, r"last_updated:\s+20\d{2}-\d{2}-\d{2}")
        self.assertIn('last_updated: "<YYYY-MM-DD>"', prd)

    def test_contract_and_docs_reference_only_consolidated_page_templates(self):
        references = "\n".join(
            path.read_text(encoding="utf-8") for path in (SHARED_CONTRACT, INTEGRATION_DOC, PRD)
        )

        self.assertIn("page.md", references)
        self.assertIn("PAGE-TYPES.md", references)
        for legacy_name in LEGACY_PAGE_TEMPLATES:
            self.assertNotIn(legacy_name, references)


if __name__ == "__main__":
    unittest.main()
