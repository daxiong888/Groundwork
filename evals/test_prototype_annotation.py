#!/usr/bin/env python3
import csv
import json
import re
import unittest
from pathlib import Path

from evals import routing_schema, run_runtime
from evals.checks import loop_checks


ROOT = Path(__file__).resolve().parents[1]
SUITE = ROOT / "evals/prompts/prototype-annotation.csv"


def annotation_row(row_id):
    with SUITE.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    row = next(item.copy() for item in rows if item["id"] == row_id)
    row["_suite"] = SUITE.name
    row["_row_number"] = 0
    row["_fieldnames"] = list(row)
    return row


def source_event(row_id):
    if row_id in {"prototype-annotation-001", "prototype-annotation-002"}:
        names = ("index.html",)
    elif row_id == "prototype-annotation-004":
        names = ("decision-source.md", "visual-packet.md")
    else:
        names = ("decision-source.md",)
    events = []
    for name in names:
        content = (
            ROOT / "evals/fixtures/prototype-annotation" / name
        ).read_text(encoding="utf-8")
        events.append(
            json.dumps(
                {
                    "type": "item.completed",
                    "item": {
                        "type": "command_execution",
                        "command": f"sed -n '1,260p' {name}",
                        "aggregated_output": content,
                        "exit_code": 0,
                        "status": "completed",
                    },
                }
            )
        )
    return "\n".join(events)


def annotation_verdict(row_id, response, *, stdout=None):
    row = annotation_row(row_id)
    actual = row["expected_best"]
    return run_runtime.routing_verdict_model(
        row,
        actual,
        response,
        0,
        [],
        [],
        stdout=source_event(row_id) if stdout is None else stdout,
        sandbox="read-only",
        response_shape_candidate=actual,
    )


def block(annotation_id, purpose, disposition, *, source="", companion=""):
    lines = [
        "## Annotation Presentation Decision",
        f"- Annotation ID: {annotation_id}",
        f"- Annotation Purpose: {purpose}",
        f"- Presentation Disposition: {disposition}",
    ]
    if source:
        lines.append(f"- Audience-facing Source: {source}")
    if companion:
        lines.append(f"- Companion Reference: {companion}")
    return "\n".join(lines)


def selective_decision_blocks():
    return [
        block(
            "help_explanation",
            "candidate audience help copy",
            "retain_as_audience_content_candidate",
            source="user_instruction:final_help_copy",
        ),
        block(
            "review_arrows",
            "internal flow explanation",
            "remove_before_final",
        ),
        block(
            "debug_badges",
            "internal state debugging",
            "remove_before_final",
        ),
        block(
            "design_notes",
            "designer review rationale",
            "remove_before_final",
        ),
    ]


def carrythrough_block(
    annotation_id,
    purpose,
    disposition,
    conditional,
    *,
    verdict="covered",
    target=None,
):
    target = target or (
        "evals/fixtures/prototype-annotation/visual-packet.md#"
        + annotation_id
    )
    return "\n".join(
        [
            "## Annotation Carry-through Check",
            f"- Annotation ID: {annotation_id}",
            f"- Source Purpose: {purpose}",
            f"- Source Disposition: {disposition}",
            f"- Required Conditional Field: {conditional}",
            f"- Observed Target or Reference: {target}",
            f"- Carry-through Verdict: {verdict}",
        ]
    )


class PrototypeAnnotationTests(unittest.TestCase):
    def test_suite_is_trace_ready_and_schema_valid(self):
        with SUITE.open(newline="", encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
        for index, row in enumerate(rows, start=2):
            row["_suite"] = SUITE.name
            row["_row_number"] = index
            row["_fieldnames"] = list(row)

        errors, _normalized = routing_schema.validate_routing_schema(rows)

        self.assertIn(SUITE.name, routing_schema.TRACE_READY_SUITES)
        self.assertEqual(errors, [])

    def test_suite_declares_contract_only_fragment_shape(self):
        with SUITE.open(newline="", encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))

        for row in rows:
            with self.subTest(row_id=row["id"]):
                self.assertIn(
                    "targeted contract-only adapter",
                    row["input_scenario"].lower(),
                )
                self.assertIn(
                    "output only",
                    row["input_scenario"].lower(),
                )

        prototype_contract = (
            ROOT / "skills/prototype/DECISION-CAPTURE.md"
        ).read_text(encoding="utf-8")
        handoff_contract = (
            ROOT / "skills/handoff/COMPLEX-HANDOFF-BRANCHES.md"
        ).read_text(encoding="utf-8")
        metrics = (
            ROOT / "docs/skill-success-metrics.md"
        ).read_text(encoding="utf-8")
        for text in (prototype_contract, handoff_contract, metrics):
            self.assertIn("targeted contract-only", text)

    def test_internal_review_aids_have_selective_dispositions(self):
        response = "\n\n".join(
            [
                block(
                    "review_arrows",
                    "internal flow explanation",
                    "remove_before_final",
                ),
                block(
                    "debug_badges",
                    "internal state debugging",
                    "remove_before_final",
                ),
                block(
                    "design_notes",
                    "designer review rationale",
                    "separate_review_companion",
                    companion="review-companion.md",
                ),
                block(
                    "help_explanation",
                    "candidate audience help copy",
                    "remove_before_final",
                ),
                "## Prototype Evidence Boundary\n"
                "Prototype contract/source evidence only; browser, runtime, UAT, "
                "release, and readiness remain unverified.",
            ]
        )

        verdict = annotation_verdict("prototype-annotation-001", response)

        self.assertEqual(verdict["output_contract_verdict"], "pass")
        self.assertEqual(verdict["evidence_verdict"], "pass")
        self.assertEqual(verdict["overall_verdict"], "pass")

    def test_selective_retention_requires_same_block_source(self):
        response = "\n\n".join(
            [
                block(
                    "help_explanation",
                    "candidate audience help copy",
                    "retain_as_audience_content_candidate",
                    source="user_instruction:final_help_copy",
                ),
                block(
                    "review_arrows",
                    "internal flow explanation",
                    "remove_before_final",
                ),
                block(
                    "debug_badges",
                    "internal state debugging",
                    "remove_before_final",
                ),
                block(
                    "design_notes",
                    "designer review rationale",
                    "remove_before_final",
                ),
                "## Prototype Evidence Boundary\n"
                "Prototype contract/source evidence only; browser, runtime, UAT, "
                "release, and readiness remain unverified.",
            ]
        )

        verdict = annotation_verdict("prototype-annotation-002", response)

        self.assertEqual(verdict["output_contract_verdict"], "pass")
        self.assertEqual(verdict["overall_verdict"], "pass")

    def test_source_does_not_authorize_sibling_or_missing_source(self):
        missing_source = "\n\n".join(
            [
                block(
                    "help_explanation",
                    "candidate audience help copy",
                    "retain_as_audience_content_candidate",
                ),
                block(
                    "review_arrows",
                    "internal flow explanation",
                    "remove_before_final",
                    source="user_instruction:final_help_copy",
                ),
                block(
                    "debug_badges",
                    "internal state debugging",
                    "remove_before_final",
                ),
                block(
                    "design_notes",
                    "designer review rationale",
                    "remove_before_final",
                ),
                "## Prototype Evidence Boundary\n"
                "Prototype source only; browser and runtime remain unverified.",
            ]
        )

        verdict = annotation_verdict("prototype-annotation-002", missing_source)

        self.assertEqual(verdict["output_contract_verdict"], "fail")
        self.assertEqual(verdict["overall_verdict"], "fail")

    def test_readiness_promotion_is_rejected(self):
        response = "\n\n".join(
            [
                block(
                    "review_arrows",
                    "internal flow explanation",
                    "remove_before_final",
                ),
                block(
                    "debug_badges",
                    "internal state debugging",
                    "remove_before_final",
                ),
                block(
                    "design_notes",
                    "designer review rationale",
                    "separate_review_companion",
                    companion="review-companion.md",
                ),
                block(
                    "help_explanation",
                    "candidate audience help copy",
                    "remove_before_final",
                ),
                "## Prototype Evidence Boundary\nBrowser UAT and release are ready.",
            ]
        )

        verdict = annotation_verdict("prototype-annotation-001", response)

        self.assertEqual(verdict["output_contract_verdict"], "fail")
        self.assertEqual(verdict["overall_verdict"], "fail")

    def test_purpose_drift_empty_fields_and_contradictory_prose_are_rejected(self):
        wrong_purpose = selective_decision_blocks()
        wrong_purpose[0] = block(
            "help_explanation",
            "invented purpose",
            "retain_as_audience_content_candidate",
            source="user_instruction:final_help_copy",
        )
        empty_conditional = selective_decision_blocks()
        empty_conditional[1] += "\n- Audience-facing Source:"
        boundaries = (
            "Prototype source remains unverified, but release is ready.",
            "The production implementation is ready.",
            "Keep review_arrows and debug_badges in the final UI.",
        )
        responses = [
            "\n\n".join(
                wrong_purpose
                + [
                    "## Prototype Evidence Boundary\n"
                    "Prototype source only; stronger readiness remains unverified."
                ]
            ),
            "\n\n".join(
                empty_conditional
                + [
                    "## Prototype Evidence Boundary\n"
                    "Prototype source only; stronger readiness remains unverified."
                ]
            ),
            *[
                "\n\n".join(
                    selective_decision_blocks()
                    + [f"## Prototype Evidence Boundary\n{boundary}"]
                )
                for boundary in boundaries
            ],
        ]

        for response in responses:
            with self.subTest(response=response):
                verdict = annotation_verdict("prototype-annotation-002", response)
                self.assertEqual(verdict["output_contract_verdict"], "fail")
                self.assertEqual(verdict["overall_verdict"], "fail")

    def test_annotation_boundary_rejects_concession_bypass_and_actualized_ui_claim(self):
        boundaries = (
            "Keep review_arrows in the final UI although implementation remains unverified.",
            "The production UI has removed review_arrows, debug_badges, and design_notes. "
            "Browser evidence remains unverified.",
            "The production UI has not removed review_arrows. "
            "Browser evidence remains unverified.",
            "review_arrows should remain in the final UI; "
            "implementation remains unverified.",
            "Implementation remains unverified notwithstanding the final UI "
            "includes review_arrows.",
            "The production interface is live; browser evidence remains unverified.",
            "Prototype contract evidence is not readiness proof because the "
            "production UI is deployed.",
            "Prototype contract evidence is not implementation proof because "
            "the final UI includes review_arrows.",
            "Prototype contract evidence cannot prove implementation because "
            "review_arrows will be shown in the final UI.",
            "Prototype contract evidence is not readiness proof as the "
            "production UI is deployed.",
            "Prototype contract evidence is not implementation proof given "
            "that the final UI includes review_arrows.",
            "Prototype contract evidence is not readiness proof on the "
            "grounds that the production UI is deployed.",
            "Production UI is re\u200bady and in\u200bcludes review_arrows.",
            "Release is rea\ufe0fdy.",
            "The production interface is l\u034five.",
            "Release is not not ready.",
            "Not false: release is ready.",
        )

        for boundary in boundaries:
            with self.subTest(boundary=boundary):
                response = "\n\n".join(
                    selective_decision_blocks()
                    + [f"## Prototype Evidence Boundary\n{boundary}"]
                )
                verdict = annotation_verdict("prototype-annotation-002", response)
                self.assertEqual(verdict["output_contract_verdict"], "fail")
                self.assertEqual(verdict["overall_verdict"], "fail")

    def test_reviewer_html_visibility_and_assertion_polarity_probes_are_rejected(self):
        boundaries = (
            "Prototype source only; browser remains unverified. "
            "This is not source evidence — release is ready.",
            "Prototype source only; browser remains unverified. "
            "This is not source evidence release is ready.",
            "Prototype source only; browser remains unverified. "
            "This is not source evidence / release is ready.",
            "Prototype source only; browser remains unverified. "
            "This is not source evidence (release is ready).",
            "Prototype source only; browser remains unverified. "
            "Release is re&#97;dy; the final UI "
            "in<span>clu</span>des review_arrows.",
            "Prototype source only; browser and release remain unverified. "
            "The final UI in<span>clu</span>des review_arrows.",
            "Prototype source only; browser, runtime, UAT, release, and "
            "readiness remain unverified. "
            "The production UI now contains review_arrows.",
            "Prototype source only; browser and release remain unverified. "
            "review_arrows appears in the production UI.",
            "Prototype source only; browser and release remain unverified. "
            "review_arrows is part of the final interface.",
            "Prototype source only; browser and release remain unverified. "
            "review_arrows survives into the target presentation.",
            "Prototype source only; browser and release remain unverified. "
            "review_arrows carries into the final UI.",
            "Prototype source only; browser and release remain unverified. "
            '<span title="production UI contains review_arrows">bounded</span>',
            "Prototype source only; browser and release remain unverified. "
            '<span aria-label="final UI renders review_arrows">bounded</span>',
            "Prototype source only; browser remains unverified. "
            "&lt;script&gt;Release is ready.&lt;/script&gt;",
        )

        for boundary in boundaries:
            with self.subTest(boundary=boundary):
                response = "\n\n".join(
                    selective_decision_blocks()
                    + [f"## Prototype Evidence Boundary\n{boundary}"]
                )
                verdict = annotation_verdict("prototype-annotation-002", response)
                self.assertEqual(verdict["output_contract_verdict"], "fail")
                self.assertEqual(verdict["overall_verdict"], "fail")

    def test_single_negation_does_not_create_overclaims(self):
        boundaries = (
            "Prototype source only; browser remains unverified. "
            "Release is not ready.",
            "Prototype source only; browser remains unverified. "
            "This is not source evidence / release is not ready.",
            "Prototype source only; browser remains unverified. "
            "This is not source evidence (release is not ready).",
        )

        for boundary in boundaries:
            with self.subTest(boundary=boundary):
                response = "\n\n".join(
                    selective_decision_blocks()
                    + [f"## Prototype Evidence Boundary\n{boundary}"]
                )
                verdict = annotation_verdict("prototype-annotation-002", response)
                self.assertEqual(verdict["output_contract_verdict"], "pass")
                self.assertEqual(verdict["overall_verdict"], "pass")

    def test_nonvisible_html_is_rejected_in_annotation_contract_output(self):
        boundaries = (
            "<script>Release is ready.</script>",
            "<style>Release is ready.</style>",
            "<template>The final UI includes review_arrows.</template>",
            "<noscript>Release is ready.</noscript>",
            "<details>The final UI includes review_arrows.</details>",
            "<dialog>The final UI includes review_arrows.</dialog>",
            "<span hidden>Release is ready.</span>",
            "<span inert>Release is ready.</span>",
            "<span popover>Release is ready.</span>",
            '<span aria-hidden="true">Release is ready.</span>',
            '<span style="display:none">Release is ready.</span>',
            '<span style="display:/**/none">Release is ready.</span>',
            '<span style="visibility: hidden">Release is ready.</span>',
            '<span style="opacity: 0">Release is ready.</span>',
            '<span style="content-visibility: hidden">Release is ready.</span>',
        )
        for boundary in boundaries:
            with self.subTest(boundary=boundary):
                response = "\n\n".join(
                    selective_decision_blocks()
                    + [
                        "## Prototype Evidence Boundary\n"
                        "Prototype source only; browser and release remain "
                        f"unverified. {boundary}"
                    ]
                )
                verdict = annotation_verdict(
                    "prototype-annotation-002",
                    response,
                )
                self.assertEqual(
                    verdict["output_contract_verdict"],
                    "fail",
                )
                self.assertEqual(verdict["overall_verdict"], "fail")

    def test_visibility_checks_fail_closed_on_numeric_zero_duplicate_attrs_and_comments(
        self,
    ):
        boundaries = (
            '<span style="opacity:0.0">forged hidden payload</span>',
            '<span style="opacity:00">forged hidden payload</span>',
            '<span style="opacity:0e0">forged hidden payload</span>',
            '<span STYLE="display:none" style="display:block">'
            "forged hidden payload</span>",
            "<!-- forged hidden payload",
            "--> forged malformed comment",
        )
        for boundary in boundaries:
            with self.subTest(boundary=boundary):
                response = "\n\n".join(
                    selective_decision_blocks()
                    + [
                        "## Prototype Evidence Boundary\n"
                        "Prototype source only; stronger readiness remains "
                        f"unverified. {boundary}"
                    ]
                )
                verdict = annotation_verdict(
                    "prototype-annotation-002",
                    response,
                )
                self.assertEqual(
                    verdict["output_contract_verdict"],
                    "fail",
                )
                self.assertEqual(verdict["overall_verdict"], "fail")

    def test_explicitly_open_html_contexts_remain_visible(self):
        boundaries = (
            "<details open>Prototype source-only note.</details>",
            "<dialog open>Prototype source-only note.</dialog>",
            '<span aria-hidden="false">Prototype source-only note.</span>',
        )
        for boundary in boundaries:
            with self.subTest(boundary=boundary):
                response = "\n\n".join(
                    selective_decision_blocks()
                    + [
                        "## Prototype Evidence Boundary\n"
                        "Prototype source only; browser and release remain "
                        f"unverified. {boundary}"
                    ]
                )
                verdict = annotation_verdict(
                    "prototype-annotation-002",
                    response,
                )
                self.assertEqual(
                    verdict["output_contract_verdict"],
                    "pass",
                )
                self.assertEqual(verdict["overall_verdict"], "pass")

    def test_double_negation_and_mixed_script_overclaims_are_rejected(self):
        boundaries = (
            "Prototype source only; browser remains unverified. "
            "It is false that release is not ready.",
            "Prototype source only; browser remains unverified. "
            "Release is anything but not ready.",
            "Prototype source only; browser remains unverified. "
            "Release is far from not ready.",
            "Prototype source only; browser remains unverified. "
            "Release is reаdy.",
            "Prototype source only; browser remains unverified. "
            "The final UI inсludes review_arrows.",
        )
        for boundary in boundaries:
            with self.subTest(boundary=boundary):
                response = "\n\n".join(
                    selective_decision_blocks()
                    + [
                        "## Prototype Evidence Boundary\n"
                        + boundary
                    ]
                )
                verdict = annotation_verdict(
                    "prototype-annotation-002",
                    response,
                )
                self.assertEqual(
                    verdict["output_contract_verdict"],
                    "fail",
                )
                self.assertEqual(verdict["overall_verdict"], "fail")

    def test_retained_audience_candidate_can_be_described_without_overclaim(self):
        response = "\n\n".join(
            selective_decision_blocks()
            + [
                "## Prototype Evidence Boundary\n"
                "Retain help_explanation as a target-audience content candidate; "
                "implementation, browser, runtime, UAT, and release remain unverified."
            ]
        )

        verdict = annotation_verdict("prototype-annotation-002", response)

        self.assertEqual(verdict["output_contract_verdict"], "pass")
        self.assertEqual(verdict["overall_verdict"], "pass")

    def test_hidden_annotation_blocks_do_not_satisfy_contract(self):
        hidden = "<!--\n" + "\n\n".join(selective_decision_blocks()) + "\n-->"
        response = (
            hidden
            + "\n\n## Prototype Evidence Boundary\n"
            "Prototype source only; stronger readiness remains unverified."
        )
        fenced = (
            "```text\n"
            + "\n\n".join(selective_decision_blocks())
            + "\n```\n\n## Prototype Evidence Boundary\n"
            "Prototype source only; stronger readiness remains unverified."
        )
        indented = "\n".join(
            "    " + line
            for line in (
                "\n\n".join(selective_decision_blocks())
                + "\n\n## Prototype Evidence Boundary\n"
                "Prototype source only; stronger readiness remains unverified."
            ).splitlines()
        )

        for candidate in (response, fenced, indented):
            with self.subTest(candidate=candidate):
                verdict = annotation_verdict("prototype-annotation-002", candidate)
                self.assertEqual(verdict["output_contract_verdict"], "fail")
                self.assertEqual(verdict["overall_verdict"], "fail")

        valid = "\n\n".join(
            selective_decision_blocks()
            + [
                "## Prototype Evidence Boundary\n"
                "Prototype source only; stronger readiness remains unverified."
            ]
        )
        hidden_tails = (
            "\n```text\nThe production UI includes review_arrows.\n```\n",
            "\n    The production UI includes review_arrows.\n",
            "\n<!-- The production UI includes review_arrows. -->\n",
        )
        for tail in hidden_tails:
            with self.subTest(tail=tail):
                verdict = annotation_verdict(
                    "prototype-annotation-002", valid + tail
                )
                self.assertEqual(
                    verdict["output_contract_verdict"], "fail"
                )
                self.assertEqual(verdict["overall_verdict"], "fail")

    def test_handoff_inline_and_verify_per_id_carrythrough_are_measured(self):
        handoff_response = "\n\n".join(
            selective_decision_blocks()
            + [
                "## Prototype Evidence Boundary\n"
                "Source decision carry-through only; implementation, browser, "
                "runtime, UAT, release, and customer readiness remain unverified."
            ]
        )
        verify_response = "\n\n".join(
            [
                "Verification Scope\n"
                "- Claim: annotation_decision_carrythrough\n"
                "- Covered: review_arrows|debug_badges|design_notes|help_explanation\n"
                "- Missing: none\n"
                "- Verdict: pass",
                carrythrough_block(
                    "review_arrows",
                    "internal flow explanation",
                    "remove_before_final",
                    "none",
                ),
                carrythrough_block(
                    "debug_badges",
                    "internal state debugging",
                    "remove_before_final",
                    "none",
                ),
                carrythrough_block(
                    "design_notes",
                    "designer review rationale",
                    "remove_before_final",
                    "none",
                ),
                carrythrough_block(
                    "help_explanation",
                    "candidate audience help copy",
                    "retain_as_audience_content_candidate",
                    "Audience-facing Source: user_instruction:final_help_copy",
                ),
            ]
        )
        reference_response = """Annotation Decision Carry-through
- Mode: reference
- Annotation Decision Reference: evals/fixtures/prototype-annotation/decision-source.md#prototype-annotation-decision-source
- Annotation IDs: review_arrows|debug_badges|design_notes|help_explanation
- Evidence Boundary: source_reference_only
"""

        handoff = annotation_verdict("prototype-annotation-003", handoff_response)
        verify = annotation_verdict("prototype-annotation-004", verify_response)
        reference = annotation_verdict(
            "prototype-annotation-005", reference_response
        )

        self.assertEqual(handoff["overall_verdict"], "pass")
        self.assertEqual(verify["overall_verdict"], "pass")
        self.assertEqual(reference["overall_verdict"], "pass")

        missing_id = verify_response.replace(
            "\n\n" + carrythrough_block(
                "design_notes",
                "designer review rationale",
                "remove_before_final",
                "none",
            ),
            "",
        )
        drift = verify_response.replace(
            "- Source Purpose: internal flow explanation",
            "- Source Purpose: invented purpose",
            1,
        )
        for candidate in (missing_id, drift):
            with self.subTest(candidate=candidate):
                verdict = annotation_verdict(
                    "prototype-annotation-004", candidate
                )
                self.assertEqual(verdict["output_contract_verdict"], "fail")
                self.assertEqual(verdict["overall_verdict"], "fail")

        contradictory_scope = verify_response.replace(
            "- Covered: review_arrows|debug_badges|design_notes|help_explanation\n"
            "- Missing: none\n"
            "- Verdict: pass",
            "- Covered: none\n"
            "- Missing: review_arrows|debug_badges|design_notes|help_explanation\n"
            "- Verdict: fail",
        )
        contradictory_verdict = annotation_verdict(
            "prototype-annotation-004", contradictory_scope
        )
        self.assertEqual(
            contradictory_verdict["output_contract_verdict"], "fail"
        )
        self.assertEqual(contradictory_verdict["overall_verdict"], "fail")

        incomplete_reference = reference_response.replace(
            "|design_notes", ""
        )
        reference_verdict = annotation_verdict(
            "prototype-annotation-005", incomplete_reference
        )
        self.assertEqual(reference_verdict["output_contract_verdict"], "fail")
        self.assertEqual(reference_verdict["overall_verdict"], "fail")

        hidden_tails = (
            "\n<!-- Production UI is ready and includes review_arrows. -->\n",
            "\n```text\nProduction UI is ready and includes review_arrows.\n```\n",
            "\n    Production UI is ready and includes review_arrows.\n",
        )
        for row_id, response in (
            ("prototype-annotation-004", verify_response),
            ("prototype-annotation-005", reference_response),
        ):
            for tail in hidden_tails:
                with self.subTest(row_id=row_id, tail=tail):
                    hidden_verdict = annotation_verdict(
                        row_id, response + tail
                    )
                    self.assertEqual(
                        hidden_verdict["output_contract_verdict"], "fail"
                    )
                    self.assertEqual(
                        hidden_verdict["overall_verdict"], "fail"
                    )

    def test_handoff_reference_checker_uses_row_level_reference(self):
        row = annotation_row("prototype-annotation-005")
        row["annotation_expected_reference"] = (
            "decision-source.md#prototype-annotation-decision-source"
        )
        response = """Annotation Decision Carry-through
- Mode: reference
- Annotation Decision Reference: decision-source.md#prototype-annotation-decision-source
- Annotation IDs: review_arrows|debug_badges|design_notes|help_explanation
- Evidence Boundary: source_reference_only
"""

        self.assertEqual(
            loop_checks.annotation_handoff_reference_failures(response, row),
            [],
        )

        missing_oracle = row.copy()
        missing_oracle["annotation_expected_reference"] = "none"
        self.assertIn(
            "annotation handoff reference oracle metadata is missing or malformed",
            loop_checks.annotation_handoff_reference_failures(
                response, missing_oracle
            ),
        )

    def test_annotation_carrythrough_oracle_supports_gap_and_unverified(self):
        row = annotation_row("prototype-annotation-004")
        row["annotation_expected_scope_covered"] = (
            "debug_badges|help_explanation"
        )
        row["annotation_expected_scope_missing"] = (
            "review_arrows|design_notes"
        )
        row["annotation_expected_scope_verdict"] = "fail"
        row["annotation_expected_carrythrough_verdicts"] = (
            "review_arrows=gap|debug_badges=covered|"
            "design_notes=unverified|help_explanation=covered"
        )
        response = "\n\n".join(
            [
                "Verification Scope\n"
                "- Claim: annotation_decision_carrythrough\n"
                "- Covered: debug_badges|help_explanation\n"
                "- Missing: review_arrows|design_notes\n"
                "- Verdict: fail",
                carrythrough_block(
                    "review_arrows",
                    "internal flow explanation",
                    "remove_before_final",
                    "none",
                    verdict="gap",
                ),
                carrythrough_block(
                    "debug_badges",
                    "internal state debugging",
                    "remove_before_final",
                    "none",
                ),
                carrythrough_block(
                    "design_notes",
                    "designer review rationale",
                    "remove_before_final",
                    "none",
                    verdict="unverified",
                ),
                carrythrough_block(
                    "help_explanation",
                    "candidate audience help copy",
                    "retain_as_audience_content_candidate",
                    "Audience-facing Source: user_instruction:final_help_copy",
                ),
            ]
        )

        verdict = run_runtime.routing_verdict_model(
            row,
            row["expected_best"],
            response,
            0,
            [],
            [],
            stdout=source_event("prototype-annotation-004"),
            sandbox="read-only",
            response_shape_candidate=row["expected_best"],
        )

        self.assertEqual(verdict["output_contract_verdict"], "pass")
        self.assertEqual(verdict["overall_verdict"], "pass")

    def test_covered_external_annotation_target_requires_observed_activity(self):
        row = annotation_row("prototype-annotation-004")
        row["evidence_required"] += "|browser_or_unverified"
        row["annotation_expected_observed_targets"] = (
            row["annotation_expected_observed_targets"].replace(
                "evals/fixtures/prototype-annotation/"
                "visual-packet.md#review_arrows",
                "browser:unverified_preview",
                1,
            )
        )
        response = "\n\n".join(
            [
                "Verification Scope\n"
                "- Claim: annotation_decision_carrythrough\n"
                "- Covered: review_arrows|debug_badges|design_notes|help_explanation\n"
                "- Missing: none\n"
                "- Verdict: pass",
                carrythrough_block(
                    "review_arrows",
                    "internal flow explanation",
                    "remove_before_final",
                    "none",
                    target="browser:unverified_preview",
                ),
                carrythrough_block(
                    "debug_badges",
                    "internal state debugging",
                    "remove_before_final",
                    "none",
                ),
                carrythrough_block(
                    "design_notes",
                    "designer review rationale",
                    "remove_before_final",
                    "none",
                ),
                carrythrough_block(
                    "help_explanation",
                    "candidate audience help copy",
                    "retain_as_audience_content_candidate",
                    "Audience-facing Source: user_instruction:final_help_copy",
                ),
            ]
        )
        source_stdout = source_event("prototype-annotation-004")
        unobserved = run_runtime.routing_verdict_model(
            row,
            row["expected_best"],
            response,
            0,
            [],
            [],
            stdout=source_stdout,
            sandbox="read-only",
            response_shape_candidate=row["expected_best"],
        )
        generic_browser_event = json.dumps(
            {
                "type": "item.completed",
                "item": {
                    "type": "mcp_tool_call",
                    "server": "browser",
                    "tool": "page_snapshot",
                    "result": {"nodes": [{"role": "document"}]},
                    "status": "completed",
                },
            }
        )
        matching_browser_event = json.dumps(
            {
                "type": "item.completed",
                "item": {
                    "type": "mcp_tool_call",
                    "server": "browser",
                    "tool": "page_snapshot",
                    "target_id": "unverified_preview",
                    "result": {"nodes": [{"role": "document"}]},
                    "status": "completed",
                },
            }
        )
        wrong_target = run_runtime.routing_verdict_model(
            row,
            row["expected_best"],
            response,
            0,
            [],
            [],
            stdout=source_stdout + "\n" + generic_browser_event,
            sandbox="read-only",
            response_shape_candidate=row["expected_best"],
        )
        observed = run_runtime.routing_verdict_model(
            row,
            row["expected_best"],
            response,
            0,
            [],
            [],
            stdout=source_stdout + "\n" + matching_browser_event,
            sandbox="read-only",
            response_shape_candidate=row["expected_best"],
        )

        self.assertEqual(unobserved["evidence_verdict"], "fail")
        self.assertEqual(wrong_target["evidence_verdict"], "fail")
        self.assertIn(
            "covered annotation browser target requires successful observed browser activity",
            unobserved["notes"],
        )
        self.assertEqual(observed["evidence_verdict"], "pass")
        self.assertEqual(observed["overall_verdict"], "pass")

    def test_verified_annotation_decisions_require_source_observation(self):
        response = "\n\n".join(
            [
                block(
                    "review_arrows",
                    "internal flow explanation",
                    "remove_before_final",
                ),
                block(
                    "debug_badges",
                    "internal state debugging",
                    "remove_before_final",
                ),
                block(
                    "design_notes",
                    "designer review rationale",
                    "separate_review_companion",
                    companion="review-companion.md",
                ),
                block(
                    "help_explanation",
                    "candidate audience help copy",
                    "remove_before_final",
                ),
                "## Prototype Evidence Boundary\nPrototype contract evidence inspected.",
            ]
        )

        verdict = annotation_verdict(
            "prototype-annotation-001", response, stdout=""
        )

        self.assertEqual(verdict["evidence_verdict"], "fail")
        self.assertEqual(verdict["overall_verdict"], "fail")

    def test_annotation_source_evidence_requires_successful_canonical_fixture_reads(self):
        response = "\n\n".join(
            selective_decision_blocks()
            + [
                "## Prototype Evidence Boundary\n"
                "Prototype source decision only; browser, runtime, UAT, and release remain unverified."
            ]
        )
        wrong_path = json.dumps(
            {
                "type": "item.completed",
                "item": {
                    "type": "command_execution",
                    "command": "sed -n '1,240p' unrelated.md",
                    "aggregated_output": "unrelated source",
                    "exit_code": 0,
                    "status": "completed",
                },
            }
        )
        failed_read = json.dumps(
            {
                "type": "item.completed",
                "item": {
                    "type": "command_execution",
                    "command": "sed -n '1,240p' index.html",
                    "aggregated_output": "No such file",
                    "exit_code": 2,
                    "status": "failed",
                },
            }
        )
        same_basename_wrong_path = json.dumps(
            {
                "type": "item.completed",
                "item": {
                    "type": "command_execution",
                    "command": "cat /tmp/index.html",
                    "aggregated_output": (
                        ROOT
                        / "evals/fixtures/prototype-annotation/index.html"
                    ).read_text(encoding="utf-8"),
                    "exit_code": 0,
                    "status": "completed",
                },
            }
        )
        synthetic_read = json.dumps(
            {
                "type": "item.completed",
                "item": {
                    "type": "command_execution",
                    "command": (
                        "sed -n '1,240p; 1aSYNTHETIC' index.html"
                    ),
                    "aggregated_output": (
                        ROOT
                        / "evals/fixtures/prototype-annotation/index.html"
                    ).read_text(encoding="utf-8"),
                    "exit_code": 0,
                    "status": "completed",
                },
            }
        )
        for stdout in (
            wrong_path,
            same_basename_wrong_path,
            failed_read,
            synthetic_read,
        ):
            with self.subTest(stdout=stdout):
                verdict = annotation_verdict(
                    "prototype-annotation-002",
                    response,
                    stdout=stdout,
                )
                self.assertEqual(verdict["evidence_verdict"], "fail")
                self.assertEqual(verdict["overall_verdict"], "fail")

    def test_annotation_oracle_schema_rejects_invalid_conditional_matrix(self):
        invalid_disposition = annotation_row("prototype-annotation-001")
        invalid_disposition["annotation_expected_decisions"] = (
            "review_arrows=ship_everywhere"
        )
        with self.assertRaises(ValueError):
            routing_schema.routing_schema_for_row(invalid_disposition)

        missing_source = annotation_row("prototype-annotation-002")
        missing_source["annotation_expected_audience_sources"] = "none"
        with self.assertRaises(ValueError):
            routing_schema.routing_schema_for_row(missing_source)

        missing_purpose = annotation_row("prototype-annotation-002")
        missing_purpose["annotation_expected_purposes"] = (
            "help_explanation=candidate audience help copy"
        )
        with self.assertRaises(ValueError):
            routing_schema.routing_schema_for_row(missing_purpose)

        invalid_carrythrough = annotation_row("prototype-annotation-004")
        invalid_carrythrough["annotation_expected_carrythrough_verdicts"] = (
            "review_arrows=covered|debug_badges=covered|"
            "design_notes=covered|help_explanation=ready"
        )
        with self.assertRaises(ValueError):
            routing_schema.routing_schema_for_row(invalid_carrythrough)

        missing_covered_target = annotation_row("prototype-annotation-004")
        missing_covered_target["annotation_expected_observed_targets"] = (
            "review_arrows=none|"
            "debug_badges=evals/fixtures/prototype-annotation/visual-packet.md#debug_badges|"
            "design_notes=evals/fixtures/prototype-annotation/visual-packet.md#design_notes|"
            "help_explanation=evals/fixtures/prototype-annotation/visual-packet.md#help_explanation"
        )
        with self.assertRaises(ValueError):
            routing_schema.routing_schema_for_row(missing_covered_target)

    def test_fixture_has_stable_annotation_ids_and_product_content(self):
        html = (
            ROOT / "evals/fixtures/prototype-annotation/index.html"
        ).read_text(encoding="utf-8")
        fixture_pairs = dict(
            re.findall(
                r'data-annotation-id="([^"]+)"[ \t]+'
                r'data-annotation-purpose="([^"]+)"',
                html,
            )
        )
        expected_pairs = {
            "review_arrows": "internal flow explanation",
            "debug_badges": "internal state debugging",
            "design_notes": "designer review rationale",
            "help_explanation": "candidate audience help copy",
        }
        self.assertEqual(fixture_pairs, expected_pairs)
        for annotation_id in expected_pairs:
            self.assertIn(f'data-annotation-id="{annotation_id}"', html)
        self.assertIn('data-product-content-id="validation_message"', html)
        decision_source = (
            ROOT / "evals/fixtures/prototype-annotation/decision-source.md"
        ).read_text(encoding="utf-8")
        self.assertIn(
            '<a id="prototype-annotation-decision-source"></a>',
            decision_source,
        )
        for row_id in (
            "prototype-annotation-001",
            "prototype-annotation-002",
            "prototype-annotation-003",
            "prototype-annotation-004",
            "prototype-annotation-005",
        ):
            row = annotation_row(row_id)
            purposes = {
                item.split("=", 1)[0]: item.split("=", 1)[1]
                for item in row["annotation_expected_purposes"].split("|")
            }
            decisions = {
                item.split("=", 1)[0]
                for item in row["annotation_expected_decisions"].split("|")
            }
            self.assertEqual(purposes, expected_pairs)
            self.assertEqual(decisions, set(expected_pairs))

    def test_legacy_prototype_suite_no_longer_contains_unmeasured_rows(self):
        legacy = (
            ROOT / "evals/prompts/prototype.csv"
        ).read_text(encoding="utf-8")
        self.assertNotIn("prototype-022", legacy)
        self.assertNotIn("prototype-023", legacy)
        self.assertIn(
            "annotation_carrythrough_verification",
            routing_schema.OUTPUT_CONTRACT_IMPLEMENTED_TOKENS,
        )
        self.assertIn(
            "annotation_handoff_reference",
            routing_schema.OUTPUT_CONTRACT_IMPLEMENTED_TOKENS,
        )


if __name__ == "__main__":
    unittest.main()
