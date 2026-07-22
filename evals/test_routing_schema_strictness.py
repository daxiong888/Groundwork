#!/usr/bin/env python3
import csv
import re
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from evals import routing_schema


ROOT = Path(__file__).resolve().parents[1]


def suite_row(suite_name, row_id):
    suite = ROOT / "evals" / "prompts" / suite_name
    with suite.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    row = next(item.copy() for item in rows if item["id"] == row_id)
    row["_suite"] = suite.name
    row["_row_number"] = 0
    row["_fieldnames"] = list(row)
    row["_prompt_source"] = str(suite)
    row["_prompt_source_kind"] = "registered_suite"
    return row


def validate_row(row):
    row["_fieldnames"] = list(row)
    return routing_schema.routing_schema_for_row(row)


def annotation_carrythrough_row():
    row = suite_row("prototype-annotation.csv", "prototype-annotation-004")
    annotation_ids = (
        "review_arrows",
        "debug_badges",
        "design_notes",
        "help_explanation",
    )
    row.update(
        annotation_expected_scope_claim="annotation_decision_carrythrough",
        annotation_expected_scope_covered="|".join(annotation_ids),
        annotation_expected_scope_missing="none",
        annotation_expected_scope_verdict="pass",
        annotation_expected_carrythrough_verdicts="|".join(
            f"{annotation_id}=covered" for annotation_id in annotation_ids
        ),
        annotation_expected_observed_targets="|".join(
            f"{annotation_id}=evals/fixtures/prototype-annotation/"
            f"visual-packet.md#{annotation_id}"
            for annotation_id in annotation_ids
        ),
    )
    return row


class RoutingSchemaStrictnessTests(unittest.TestCase):
    def test_contract_lineage_fixture_and_csv_oracles_are_bidirectionally_bound(
        self,
    ):
        for row_id in ("tf-cl-001", "tf-cl-002", "tf-cl-003"):
            with self.subTest(row_id=row_id, direction="baseline"):
                validate_row(suite_row("contract-lineage.csv", row_id))

        csv_mutations = {
            "lineage_expected_canonical_owner": "producer_mapping",
            "lineage_expected_divergence": "consumer",
            "lineage_expected_fix_owner": "consumer",
            "lineage_expected_hops": (
                "canonical_contract(verified)>producer_mapping(verified)"
                ">consumer_v2(verified)"
            ),
            "lineage_expected_unverified_hops": "audit_gap",
        }
        for field, value in csv_mutations.items():
            with self.subTest(field=field, direction="csv"):
                row = suite_row("contract-lineage.csv", "tf-cl-001")
                row[field] = value
                with self.assertRaisesRegex(
                    ValueError,
                    "canonical Contract Lineage facts do not match row oracle",
                ):
                    validate_row(row)

        scenario = (
            ROOT
            / "evals/fixtures/contract-lineage-producer/SCENARIO.md"
        ).read_text(encoding="utf-8")
        fixture_mutations = (
            (
                "- Canonical Owner / Source: canonical_contract",
                "- Canonical Owner / Source: producer_mapping",
            ),
            (
                "- Hops: canonical_contract(verified)>"
                "producer_mapping(verified)>consumer(verified)",
                "- Hops: canonical_contract(verified)>"
                "producer_mapping(verified)>consumer_v2(verified)",
            ),
            (
                "- First Confirmed Divergence: producer_mapping",
                "- First Confirmed Divergence: consumer",
            ),
            (
                "- Fix Owner / Boundary: producer",
                "- Fix Owner / Boundary: consumer",
            ),
            (
                "- Unverified / Branched Hops: none",
                "- Unverified / Branched Hops: audit_gap",
            ),
        )
        for original, replacement in fixture_mutations:
            with self.subTest(field=original, direction="fixture"):
                forged = scenario.replace(original, replacement, 1)
                with mock.patch.object(
                    routing_schema,
                    "_canonical_lineage_scenario_text",
                    return_value=forged,
                ):
                    with self.assertRaisesRegex(
                        ValueError,
                        "canonical Contract Lineage facts do not match row oracle",
                    ):
                        validate_row(
                            suite_row("contract-lineage.csv", "tf-cl-001")
                        )

    def test_annotation_downstream_oracles_bind_complete_decision_source_map(
        self,
    ):
        downstream_ids = (
            "prototype-annotation-003",
            "prototype-annotation-004",
            "prototype-annotation-005",
        )
        for row_id in downstream_ids:
            with self.subTest(row_id=row_id, direction="baseline"):
                validate_row(
                    suite_row("prototype-annotation.csv", row_id)
                )
            for field, old, new in (
                (
                    "annotation_expected_purposes",
                    "design_notes=designer review rationale",
                    "design_notes=forged review rationale",
                ),
                (
                    "annotation_expected_audience_sources",
                    "help_explanation=user_instruction:final_help_copy",
                    "help_explanation=forged_authority",
                ),
            ):
                with self.subTest(row_id=row_id, field=field):
                    row = suite_row(
                        "prototype-annotation.csv", row_id
                    )
                row[field] = row[field].replace(old, new, 1)
                expected_error = (
                    "canonical prototype index purpose map"
                    if field == "annotation_expected_purposes"
                    else "canonical annotation decision source does not "
                    "match row oracle map"
                )
                with self.assertRaisesRegex(
                    ValueError,
                    expected_error,
                ):
                    validate_row(row)

            disposition_drift = suite_row(
                "prototype-annotation.csv", row_id
            )
            disposition_drift[
                "annotation_expected_decisions"
            ] = disposition_drift[
                "annotation_expected_decisions"
            ].replace(
                "design_notes=remove_before_final",
                "design_notes=separate_review_companion",
                1,
            )
            disposition_drift[
                "annotation_expected_companions"
            ] = "design_notes=review-companion.md"
            with self.subTest(row_id=row_id, field="disposition"):
                with self.assertRaisesRegex(
                    ValueError,
                    "canonical annotation decision source does not match "
                    "row oracle map",
                ):
                    validate_row(disposition_drift)

        source_text = (
            ROOT
            / "evals/fixtures/prototype-annotation/decision-source.md"
        ).read_text(encoding="utf-8")
        for old, new in (
            (
                "- Annotation Purpose: designer review rationale",
                "- Annotation Purpose: forged review rationale",
            ),
            (
                "- Audience-facing Source: "
                "user_instruction:final_help_copy",
                "- Audience-facing Source: forged_authority",
            ),
        ):
            with self.subTest(direction="fixture", field=old):
                with mock.patch.object(
                    routing_schema,
                    "_canonical_annotation_decision_source_text",
                    return_value=source_text.replace(old, new, 1),
                ):
                    with self.assertRaisesRegex(
                        ValueError,
                        "canonical annotation decision source does not match "
                        "row oracle map",
                    ):
                        validate_row(
                            suite_row(
                                "prototype-annotation.csv",
                                "prototype-annotation-003",
                            )
                        )

    def test_annotation_references_and_targets_bind_complete_decision_fields(
        self,
    ):
        original_resolver = routing_schema._resolve_annotation_file_reference

        reference_row = suite_row(
            "prototype-annotation.csv", "prototype-annotation-005"
        )
        reference_region = original_resolver(
            reference_row,
            routing_schema.ANNOTATION_REFERENCE_EXPECTATION_FIELD,
            reference_row[
                routing_schema.ANNOTATION_REFERENCE_EXPECTATION_FIELD
            ],
        )
        forged_reference = reference_region.replace(
            "- Annotation Purpose: designer review rationale",
            "- Annotation Purpose: forged review rationale",
            1,
        )
        with mock.patch.object(
            routing_schema,
            "_resolve_annotation_file_reference",
            return_value=forged_reference,
        ):
            with self.assertRaisesRegex(
                ValueError, "target decision fields must match"
            ):
                validate_row(reference_row)

        carrythrough_row = annotation_carrythrough_row()

        def forged_target_resolver(row, field, value):
            region = original_resolver(row, field, value)
            if field.endswith("[review_arrows]"):
                return region.replace(
                    "- Annotation Purpose: internal flow explanation",
                    "- Annotation Purpose: forged flow explanation",
                    1,
                )
            return region

        with mock.patch.object(
            routing_schema,
            "_resolve_annotation_file_reference",
            side_effect=forged_target_resolver,
        ):
            with self.assertRaisesRegex(
                ValueError, "target decision fields must match"
            ):
                validate_row(carrythrough_row)

        for row_id in (
            "prototype-annotation-001",
            "prototype-annotation-002",
        ):
            with self.subTest(row_id=row_id, behavior="index-bound"):
                row = suite_row("prototype-annotation.csv", row_id)
                row["annotation_expected_purposes"] = row[
                    "annotation_expected_purposes"
                ].replace(
                    "designer review rationale",
                    "scenario-specific review rationale",
                    1,
                )
                with self.assertRaisesRegex(
                    ValueError,
                    "canonical prototype index purpose map",
                ):
                    validate_row(row)

    def test_canonical_uat_section_requires_one_visible_rendered_record(self):
        records = (
            ROOT / "evals/fixtures/uat-evidence-window/records.md"
        ).read_text(encoding="utf-8")
        section = routing_schema.canonical_uat_record_section_text(
            records, "uat-window-001"
        )
        self.assertTrue(section.startswith("## uat-window-001"))
        forged_visible = section.replace(
            "frontend:a1|api:b4",
            "frontend:forged|api:forged",
            1,
        )

        hidden_wrappers = (
            ("template", "<template>{}</template>", "non-rendered HTML"),
            ("script", "<script>{}</script>", "non-rendered HTML"),
            ("style", "<style>{}</style>", "non-rendered HTML"),
            ("details", "<details>{}</details>", "non-rendered HTML"),
            ("dialog", "<dialog>{}</dialog>", "non-rendered HTML"),
            ("hidden", "<div hidden>{}</div>", "hidden HTML attribute"),
            ("inert", "<div inert>{}</div>", "hidden HTML attribute"),
            ("popover", "<div popover>{}</div>", "hidden HTML attribute"),
            (
                "aria-hidden",
                '<div aria-hidden="true">{}</div>',
                "hidden HTML attribute",
            ),
            (
                "inline-style",
                '<div style="display:none">{}</div>',
                "CSS-hidden HTML",
            ),
            (
                "commented-inline-style",
                '<div style="display:/**/none">{}</div>',
                "CSS-hidden HTML",
            ),
            (
                "numeric-zero-opacity",
                '<div style="opacity:0.0">{}</div>',
                "CSS-hidden HTML",
            ),
            (
                "duplicate-normalized-style",
                '<div STYLE="display:none" style="display:block">{}</div>',
                "duplicate normalized HTML",
            ),
        )
        for label, wrapper, expected_error in hidden_wrappers:
            with self.subTest(label=label):
                forged_records = records.replace(
                    section,
                    wrapper.format(section) + "\n" + forged_visible,
                    1,
                )
                with mock.patch.object(
                    routing_schema,
                    "_canonical_uat_records_text",
                    return_value=forged_records,
                ):
                    with self.assertRaisesRegex(
                        ValueError, expected_error
                    ):
                        validate_row(
                            suite_row(
                                "uat-evidence-window.csv",
                                "uat-window-001",
                            )
                        )

        for visible_wrapper in (
            "<details open>{}</details>",
            "<dialog open>{}</dialog>",
            '<div aria-hidden="false">{}</div>',
        ):
            with self.subTest(visible_wrapper=visible_wrapper):
                routing_schema._validate_canonical_html_visibility(
                    visible_wrapper.format("visible source")
                )

        duplicated = records.replace(
            section, section + "\n" + section, 1
        )
        with mock.patch.object(
            routing_schema,
            "_canonical_uat_records_text",
            return_value=duplicated,
        ):
            with self.assertRaisesRegex(ValueError, "exactly once"):
                validate_row(
                    suite_row(
                        "uat-evidence-window.csv", "uat-window-001"
                    )
                )

        commented_shadow = records.replace(
            section,
            "<!--\n" + section + "\n-->\n" + section,
            1,
        )
        with mock.patch.object(
            routing_schema,
            "_canonical_uat_records_text",
            return_value=commented_shadow,
        ):
            with self.assertRaisesRegex(
                ValueError,
                "non-empty HTML comment",
            ):
                validate_row(
                    suite_row(
                        "uat-evidence-window.csv",
                        "uat-window-001",
                    )
                )

    def test_canonical_sources_reject_hidden_shadow_facts_globally(self):
        annotation_source = (
            ROOT
            / "evals/fixtures/prototype-annotation/decision-source.md"
        ).read_text(encoding="utf-8")
        annotation_shadow = (
            "<!--\n"
            "## Annotation Presentation Decision\n"
            "- Annotation ID: review_arrows\n"
            "- Annotation Purpose: forged hidden purpose\n"
            "- Presentation Disposition: remove_before_final\n"
            "-->\n"
        )
        with mock.patch.object(
            routing_schema,
            "_canonical_annotation_decision_source_text",
            return_value=annotation_shadow + annotation_source,
        ):
            with self.assertRaisesRegex(
                ValueError,
                "non-empty HTML comment",
            ):
                validate_row(
                    suite_row(
                        "prototype-annotation.csv",
                        "prototype-annotation-003",
                    )
                )

        lineage_source = (
            ROOT
            / "evals/fixtures/contract-lineage-producer/SCENARIO.md"
        ).read_text(encoding="utf-8")
        lineage_shadow = (
            "<!--\n"
            "## Canonical Lineage Facts\n"
            "- Canonical Owner / Source: forged\n"
            "- Hops: forged(verified)\n"
            "- First Confirmed Divergence: forged\n"
            "- Fix Owner / Boundary: forged\n"
            "- Unverified / Branched Hops: none\n"
            "-->\n"
        )
        with mock.patch.object(
            routing_schema,
            "_canonical_lineage_scenario_text",
            return_value=lineage_shadow + lineage_source,
        ):
            with self.assertRaisesRegex(
                ValueError,
                "non-empty HTML comment",
            ):
                validate_row(
                    suite_row("contract-lineage.csv", "tf-cl-001")
                )

        records = (
            ROOT / "evals/fixtures/uat-evidence-window/records.md"
        ).read_text(encoding="utf-8")
        section = routing_schema.canonical_uat_record_section_text(
            records,
            "uat-window-001",
        )
        forged_section = section.replace(
            "frontend:a1|api:b4",
            "frontend:forged|api:forged",
            1,
        )
        uat_mutations = (
            (
                "````md\n"
                + forged_section
                + "\n````\n"
                + section,
                "fenced hidden payload",
            ),
            (
                "    forged hidden UAT fact\n" + section,
                "indented hidden payload",
            ),
            (
                section + "\n<!-- malformed hidden fact",
                "malformed HTML comment",
            ),
        )
        for replacement, expected_error in uat_mutations:
            with self.subTest(expected_error=expected_error):
                forged_records = records.replace(
                    section,
                    replacement,
                    1,
                )
                with mock.patch.object(
                    routing_schema,
                    "_canonical_uat_records_text",
                    return_value=forged_records,
                ):
                    with self.assertRaisesRegex(
                        ValueError,
                        expected_error,
                    ):
                        validate_row(
                            suite_row(
                                "uat-evidence-window.csv",
                                "uat-window-001",
                            )
                        )

        release_block = re.search(
            r"(?ms)```yaml\nrelease_evidence_claim:.*?^```$",
            section,
        )
        self.assertIsNotNone(release_block)
        with mock.patch.object(
            routing_schema,
            "_canonical_uat_records_text",
            return_value=release_block.group(0) + "\n" + records,
        ):
            with self.assertRaisesRegex(
                ValueError,
                "must belong to one uat-window section",
            ):
                validate_row(
                    suite_row(
                        "uat-evidence-window.csv",
                        "uat-window-001",
                    )
                )

    def test_annotation_index_and_row_oracles_are_bidirectionally_bound(
        self,
    ):
        index_source = (
            ROOT / "evals/fixtures/prototype-annotation/index.html"
        ).read_text(encoding="utf-8")
        forged_index = index_source.replace(
            'data-annotation-purpose="designer review rationale"',
            'data-annotation-purpose="forged review rationale"',
            1,
        )
        with mock.patch.object(
            routing_schema,
            "_canonical_annotation_index_text",
            return_value=forged_index,
        ):
            with self.assertRaisesRegex(
                ValueError,
                "canonical prototype index purpose map",
            ):
                validate_row(
                    suite_row(
                        "prototype-annotation.csv",
                        "prototype-annotation-001",
                    )
                )

    def test_canonical_annotation_index_rejects_nonrendered_wrappers(self):
        source = (
            ROOT / "evals/fixtures/prototype-annotation/index.html"
        ).read_text(encoding="utf-8")
        wrappers = (
            ("<template>", "</template>", "non-rendered HTML"),
            ("<svg><defs>", "</defs></svg>", "non-rendered HTML"),
            ("<svg><symbol>", "</symbol></svg>", "non-rendered HTML"),
            ("<datalist>", "</datalist>", "non-rendered HTML"),
            ("<dialog>", "</dialog>", "non-rendered HTML"),
            ("<div hidden>", "</div>", "hidden HTML attribute"),
            ("<div inert>", "</div>", "hidden HTML attribute"),
            ("<div popover>", "</div>", "hidden HTML attribute"),
            (
                '<div style="opacity:0e0">',
                "</div>",
                "CSS-hidden HTML",
            ),
            (
                '<div STYLE="display:none" style="display:block">',
                "</div>",
                "duplicate normalized HTML",
            ),
        )
        for opener, closer, expected_error in wrappers:
            with self.subTest(opener=opener):
                hidden_source = source.replace(
                    "<body>",
                    "<body>\n" + opener,
                    1,
                ).replace(
                    "</body>",
                    closer + "\n</body>",
                    1,
                )
                with mock.patch.object(
                    routing_schema,
                    "_canonical_annotation_index_text",
                    return_value=hidden_source,
                ):
                    with self.assertRaisesRegex(
                        ValueError,
                        expected_error,
                    ):
                        validate_row(
                            suite_row(
                                "prototype-annotation.csv",
                                "prototype-annotation-001",
                            )
                        )

        for opener, closer in (
            ("<details open>", "</details>"),
            ("<dialog open>", "</dialog>"),
        ):
            with self.subTest(opener=opener):
                visible_source = source.replace(
                    "<body>",
                    "<body>\n" + opener,
                    1,
                ).replace(
                    "</body>",
                    closer + "\n</body>",
                    1,
                )
                with mock.patch.object(
                    routing_schema,
                    "_canonical_annotation_index_text",
                    return_value=visible_source,
                ):
                    validate_row(
                        suite_row(
                            "prototype-annotation.csv",
                            "prototype-annotation-001",
                        )
                    )

        visible_annotation = (
            '<aside data-annotation-id="design_notes" '
            'data-annotation-purpose="designer review rationale">\n'
            "      Compare spacing with the compact variant.\n"
            "    </aside>"
        )
        non_rendered_annotation_elements = (
            '<meta data-annotation-id="design_notes" '
            'data-annotation-purpose="designer review rationale">',
            '<link data-annotation-id="design_notes" '
            'data-annotation-purpose="designer review rationale">',
            '<base data-annotation-id="design_notes" '
            'data-annotation-purpose="designer review rationale">',
            '<title data-annotation-id="design_notes" '
            'data-annotation-purpose="designer review rationale">'
            "design notes</title>",
            '<head><div data-annotation-id="design_notes" '
            'data-annotation-purpose="designer review rationale">'
            "design notes</div></head>",
        )
        for replacement in non_rendered_annotation_elements:
            with self.subTest(replacement=replacement):
                non_rendered_source = source.replace(
                    visible_annotation,
                    replacement,
                    1,
                )
                with mock.patch.object(
                    routing_schema,
                    "_canonical_annotation_index_text",
                    return_value=non_rendered_source,
                ):
                    with self.assertRaisesRegex(
                        ValueError,
                        "renderable element inside body",
                    ):
                        validate_row(
                            suite_row(
                                "prototype-annotation.csv",
                                "prototype-annotation-001",
                            )
                        )

        annotation = (
            '<span data-annotation-id="a" '
            'data-annotation-purpose="review note">note</span>'
        )
        for wrapper in (
            "<svg><defs>{}</defs></svg>",
            "<svg><symbol>{}</symbol></svg>",
            "<datalist>{}</datalist>",
        ):
            with self.subTest(annotation_wrapper=wrapper):
                non_rendered_source = (
                    "<html><body>"
                    + wrapper.format(annotation)
                    + "</body></html>"
                )
                with mock.patch.object(
                    routing_schema,
                    "_validate_canonical_html_visibility",
                    return_value=None,
                ):
                    with self.assertRaisesRegex(
                        ValueError,
                        "renderable element inside body",
                    ):
                        routing_schema._canonical_annotation_index_purposes(
                            non_rendered_source
                        )

        visible_svg = (
            "<html><body><svg>"
            '<text data-annotation-id="a" '
            'data-annotation-purpose="review note">note</text>'
            "</svg></body></html>"
        )
        self.assertEqual(
            routing_schema._canonical_annotation_index_purposes(
                visible_svg
            ),
            {"a": "review note"},
        )

        malformed_comment = source.replace(
            "</body>",
            "<!-- unclosed hidden source\n</body>",
            1,
        )
        with mock.patch.object(
            routing_schema,
            "_canonical_annotation_index_text",
            return_value=malformed_comment,
        ):
            with self.assertRaisesRegex(
                ValueError,
                "malformed HTML comment",
            ):
                validate_row(
                    suite_row(
                        "prototype-annotation.csv",
                        "prototype-annotation-001",
                    )
                )

    def test_canonical_lineage_facts_reject_closed_dialog_but_allow_open_dialog(
        self,
    ):
        scenario = (
            ROOT
            / "evals/fixtures/contract-lineage-producer/SCENARIO.md"
        ).read_text(encoding="utf-8")
        facts = (
            "## Canonical Lineage Facts\n\n"
            "- Canonical Owner / Source: canonical_contract\n"
            "- Hops: canonical_contract(verified)>"
            "producer_mapping(verified)>consumer(verified)\n"
            "- First Confirmed Divergence: producer_mapping\n"
            "- Fix Owner / Boundary: producer\n"
            "- Unverified / Branched Hops: none\n"
        )
        for opener, should_pass in (
            ("<dialog>", False),
            ("<dialog open>", True),
        ):
            with self.subTest(opener=opener):
                wrapped = scenario.replace(
                    facts,
                    opener + "\n" + facts + "\n</dialog>\n",
                    1,
                )
                with mock.patch.object(
                    routing_schema,
                    "_canonical_lineage_scenario_text",
                    return_value=wrapped,
                ):
                    if should_pass:
                        validate_row(
                            suite_row(
                                "contract-lineage.csv",
                                "tf-cl-001",
                            )
                        )
                    else:
                        with self.assertRaisesRegex(
                            ValueError,
                            "non-rendered HTML",
                        ):
                            validate_row(
                                suite_row(
                                    "contract-lineage.csv",
                                    "tf-cl-001",
                                )
                            )

    def test_malformed_csv_rejects_exact_and_normalized_duplicate_headers(
        self,
    ):
        row = {
            "id": "duplicate-header-probe",
            "_suite": "duplicate-header.csv",
            "_row_number": 1,
        }
        header_sets = (
            ["id", "id"],
            ["Name", " name "],
            ["\ufeffID", " id "],
            [" \ufeffID ", "id"],
        )
        for fieldnames in header_sets:
            with self.subTest(fieldnames=fieldnames):
                candidate = row.copy()
                candidate["_fieldnames"] = fieldnames
                errors = routing_schema.malformed_csv_errors(candidate)
                self.assertTrue(
                    any(
                        "duplicate columns after "
                        "BOM/strip/casefold normalization" in error
                        for error in errors
                    ),
                    errors,
                )

    def test_malformed_csv_rejects_invisible_and_reserved_confusable_headers(
        self,
    ):
        row = {
            "id": "unicode-header-probe",
            "_suite": "unicode-header.csv",
            "_row_number": 1,
        }
        for fieldnames, expected in (
            (
                ["id", "output_contract", "output_contract\u200b"],
                "default-ignorable Unicode",
            ),
            (
                ["id", "output_contract", "оutput_contract"],
                "visually aliases a reserved field",
            ),
            (
                ["id", "oսtput_contract"],
                "canonical ASCII identifiers after NFKC",
            ),
            (
                ["id", "OUTPUT_CONTRACT"],
                "canonical reserved-field spelling",
            ),
            (
                ["id", "ｏｕｔｐｕｔ_contract"],
                "canonical ASCII identifiers after NFKC",
            ),
        ):
            with self.subTest(fieldnames=fieldnames):
                candidate = row.copy()
                candidate["_fieldnames"] = fieldnames
                errors = routing_schema.malformed_csv_errors(
                    candidate
                )
                self.assertIn(expected, "\n".join(errors))

        legacy_extra = row.copy()
        legacy_extra["_fieldnames"] = [
            "id",
            "legacy_extra_column",
        ]
        self.assertEqual(
            routing_schema.malformed_csv_errors(legacy_extra),
            [],
        )

    def test_csv_header_errors_is_row_independent(self):
        self.assertIn(
            "header is missing",
            "\n".join(
                routing_schema.csv_header_errors(
                    None,
                    "header-only.csv",
                )
            ),
        )
        self.assertIn(
            "visually aliases a reserved field",
            "\n".join(
                routing_schema.csv_header_errors(
                    ["id", "оutput_contract"],
                    "header-only.csv",
                )
            ),
        )
        self.assertEqual(
            routing_schema.csv_header_errors(
                ["id", "legacy_extra_column"],
                "header-only.csv",
            ),
            [],
        )

    def test_trace_ready_headers_require_every_routing_schema_field(self):
        baseline = suite_row("routing-reliability.csv", "rr-001")
        validate_row(baseline.copy())

        for missing_field, typo in (
            ("output_contract", "output_contarct"),
            ("evidence_required", "evidence_requried"),
        ):
            with self.subTest(missing_field=missing_field):
                candidate = baseline.copy()
                candidate[typo] = candidate.pop(missing_field)
                candidate["_fieldnames"] = [
                    typo if field == missing_field else field
                    for field in baseline["_fieldnames"]
                ]
                errors, normalized = (
                    routing_schema.validate_routing_schema([candidate])
                )
                self.assertIn(
                    "trace-ready CSV header is missing required columns: "
                    + missing_field,
                    "\n".join(errors),
                )
                self.assertEqual(
                    normalized[0][missing_field],
                    ["none"],
                )

    def test_row_ids_are_canonical_ascii_and_duplicates_use_canonical_identity(
        self,
    ):
        baseline = suite_row("contract-lineage.csv", "tf-cl-001")
        validate_row(baseline.copy())

        invalid_ids = (
            "tf-cl-001\u200b",
            "tf-cl-001\ufe0f",
            "ｔｆ-cl-001",
            " tf-cl-001",
        )
        for invalid_id in invalid_ids:
            with self.subTest(invalid_id=invalid_id):
                candidate = baseline.copy()
                candidate["id"] = invalid_id
                with self.assertRaisesRegex(
                    ValueError,
                    "id must use one canonical ASCII stable identifier",
                ):
                    validate_row(candidate)

        case_variant = baseline.copy()
        case_variant["id"] = "TF-CL-001"
        case_variant["_row_number"] = 3
        errors, _normalized = routing_schema.validate_routing_schema(
            [baseline.copy(), case_variant]
        )
        self.assertIn(
            "duplicate row id canonical identity",
            "\n".join(errors),
        )

    def test_legacy_fixture_only_internal_routes_are_narrowly_exempt(
        self,
    ):
        base = {
            "id": "legacy-fixture-route",
            "_suite": "goal-contract.csv",
            "_row_number": 2,
            "_prompt_source": str(
                (
                    ROOT
                    / "evals"
                    / "prompts"
                    / "goal-contract.csv"
                )
            ),
            "_prompt_source_kind": "registered_suite",
            "_fieldnames": [
                "id",
                "fixture_only",
                "skill",
                "output_contract",
            ],
            "fixture_only": "true",
            "skill": "goal-contract",
            "output_contract": "none",
        }
        errors, normalized = routing_schema.validate_routing_schema(
            [base.copy()]
        )
        self.assertEqual(errors, [])
        self.assertEqual(
            normalized[0]["expected_best"],
            "goal-contract",
        )

        for label, mutation in (
            (
                "not-fixture-only",
                {"fixture_only": "false"},
            ),
            (
                "trace-ready",
                {"_suite": "routing-reliability.csv"},
            ),
        ):
            with self.subTest(label=label):
                candidate = base.copy()
                candidate.update(mutation)
                errors, _normalized = (
                    routing_schema.validate_routing_schema([candidate])
                )
                self.assertIn(
                    "unknown expected_best route: goal-contract",
                    "\n".join(errors),
                )

        invalid_contract = base.copy()
        invalid_contract["output_contract"] = "unknown_contract"
        errors, _normalized = routing_schema.validate_routing_schema(
            [invalid_contract]
        )
        self.assertIn(
            "unknown output_contract: unknown_contract",
            "\n".join(errors),
        )

        legacy_route_list = base.copy()
        legacy_route_list["acceptable_routes"] = (
            "goal-contract|legacy-fixture-helper"
        )
        errors, _normalized = routing_schema.validate_routing_schema(
            [legacy_route_list]
        )
        self.assertIn(
            "unknown route: legacy-fixture-helper",
            "\n".join(errors),
        )

        arbitrary_suite = base.copy()
        arbitrary_suite["_suite"] = "attacker.csv"
        arbitrary_suite["skill"] = "new-public-looking-route"
        errors, _normalized = routing_schema.validate_routing_schema(
            [arbitrary_suite]
        )
        self.assertIn(
            "unknown expected_best route: new-public-looking-route",
            "\n".join(errors),
        )

        external_same_basename = base.copy()
        external_same_basename["_prompt_source"] = (
            "/tmp/external/goal-contract.csv"
        )
        external_same_basename["_prompt_source_kind"] = (
            "external_prompt_file"
        )
        errors, _normalized = routing_schema.validate_routing_schema(
            [external_same_basename]
        )
        self.assertIn(
            "unknown expected_best route: goal-contract",
            "\n".join(errors),
        )

        wrong_source_kind = base.copy()
        wrong_source_kind["_prompt_source_kind"] = (
            "external_prompt_file"
        )
        errors, _normalized = routing_schema.validate_routing_schema(
            [wrong_source_kind]
        )
        self.assertIn(
            "unknown expected_best route: goal-contract",
            "\n".join(errors),
        )

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            evals_root = root / "evals"
            prompts_root = evals_root / "prompts"
            external_root = root / "external"
            prompts_root.mkdir(parents=True)
            external_root.mkdir()
            external_target = external_root / "goal-contract.csv"
            external_target.write_text(
                "id,fixture_only,skill,output_contract\n"
                "legacy,true,goal-contract,none\n",
                encoding="utf-8",
            )

            external_symlink = external_root / "same-name.csv"
            external_symlink.symlink_to(
                ROOT / "evals" / "prompts" / "goal-contract.csv"
            )
            external_symlink_row = base.copy()
            external_symlink_row["_prompt_source"] = str(
                external_symlink
            )
            external_symlink_row["_prompt_source_kind"] = (
                "external_prompt_file"
            )
            errors, _normalized = (
                routing_schema.validate_routing_schema(
                    [external_symlink_row]
                )
            )
            self.assertIn(
                "unknown expected_best route: goal-contract",
                "\n".join(errors),
            )

            canonical_symlink = (
                prompts_root / "goal-contract.csv"
            )
            canonical_symlink.symlink_to(external_target)
            canonical_symlink_row = base.copy()
            canonical_symlink_row["_prompt_source"] = str(
                canonical_symlink
            )
            with mock.patch.object(
                routing_schema,
                "__file__",
                str(evals_root / "routing_schema.py"),
            ):
                errors, _normalized = (
                    routing_schema.validate_routing_schema(
                        [canonical_symlink_row]
                    )
                )
            self.assertIn(
                "unknown expected_best route: goal-contract",
                "\n".join(errors),
            )

        missing_source = base.copy()
        missing_source.pop("_prompt_source")
        errors, _normalized = routing_schema.validate_routing_schema(
            [missing_source]
        )
        self.assertIn(
            "unknown expected_best route: goal-contract",
            "\n".join(errors),
        )

        missing_source_kind = base.copy()
        missing_source_kind.pop("_prompt_source_kind")
        errors, _normalized = routing_schema.validate_routing_schema(
            [missing_source_kind]
        )
        self.assertIn(
            "unknown expected_best route: goal-contract",
            "\n".join(errors),
        )

        for label, mutation, expected_error in (
            (
                "blocked-expected",
                {"skill": "blocked"},
                "blocked is not a route",
            ),
            (
                "blocked-list",
                {"acceptable_routes": "goal-contract|blocked"},
                "blocked is not allowed in route lists",
            ),
            (
                "overlap",
                {
                    "acceptable_routes": "goal-contract",
                    "forbidden_routes": "goal-contract",
                },
                "acceptable_routes overlaps forbidden_routes",
            ),
            (
                "host-preemption",
                {
                    "acceptable_routes": (
                        "goal-contract|runtime-safety-gate"
                    )
                },
                "runtime-safety-gate route list requires",
            ),
        ):
            with self.subTest(label=label):
                candidate = base.copy()
                candidate.update(mutation)
                errors, _normalized = (
                    routing_schema.validate_routing_schema([candidate])
                )
                self.assertIn(expected_error, "\n".join(errors))

    def test_confusable_output_contract_header_cannot_silently_disable_measurement(
        self,
    ):
        row = suite_row("routing-reliability.csv", "rr-001")
        confusable_header = "oսtput_contract"
        row[confusable_header] = row.pop("output_contract")
        row["_fieldnames"] = [
            confusable_header if field == "output_contract" else field
            for field in row["_fieldnames"]
        ]

        errors, normalized = routing_schema.validate_routing_schema([row])

        self.assertIn(
            "canonical ASCII identifiers after NFKC",
            "\n".join(errors),
        )
        self.assertEqual(normalized[0]["output_contract"], ["none"])

    def test_measurement_tokens_reject_duplicates_and_none_mixtures(
        self,
    ):
        for value, expected in (
            (
                "verify_scope|verify_scope",
                "duplicate token",
            ),
            (
                "none|verify_scope",
                "token none must be used alone",
            ),
        ):
            with self.subTest(value=value):
                row = {
                    "id": "measurement-token-probe",
                    "_suite": "measurement-token.csv",
                    "_row_number": 1,
                    "output_contract": value,
                }
                with self.assertRaisesRegex(ValueError, expected):
                    routing_schema.measurement_tokens_for_row(
                        row,
                        "output_contract",
                        routing_schema.OUTPUT_CONTRACT_IMPLEMENTED_TOKENS,
                        routing_schema.OUTPUT_CONTRACT_FUTURE_TOKENS,
                    )

    def test_strict_output_contract_family_matrix_is_pairwise_exclusive(
        self,
    ):
        row = {
            "id": "strict-family-probe",
            "_suite": "strict-family.csv",
            "_row_number": 1,
        }
        strict_tokens = sorted(
            routing_schema.STRICT_OUTPUT_CONTRACT_FAMILY_TOKENS
        )
        for index, left in enumerate(strict_tokens):
            for right in strict_tokens[index + 1:]:
                with self.subTest(left=left, right=right):
                    with self.assertRaisesRegex(
                        ValueError, "incompatible strict families"
                    ):
                        routing_schema.require_output_contract_compatibility(
                            row, [left, right]
                        )

        legal_contracts = (
            ("verify_scope", "contract_lineage"),
            (
                "verify_scope",
                "release_evidence_claim",
                "uat_evidence_window",
            ),
            (
                "verify_scope",
                "release_evidence_claim",
                "uat_evidence_window_forbidden",
            ),
            (
                "entry_decision",
                "release_evidence_claim",
                "uat_handoff_reference",
            ),
            (
                "verify_scope",
                "annotation_carrythrough_verification",
            ),
            (
                "annotation_presentation_decision",
                "prototype_contract_boundary",
            ),
        )
        for contract in legal_contracts:
            with self.subTest(contract=contract):
                routing_schema.require_output_contract_compatibility(
                    row, contract
                )

        for suite_name, row_id in (
            ("contract-lineage.csv", "tf-cl-002"),
            ("uat-evidence-window.csv", "uat-window-001"),
            ("uat-evidence-window.csv", "uat-window-006"),
            ("uat-evidence-window.csv", "uat-window-007"),
            ("prototype-annotation.csv", "prototype-annotation-004"),
        ):
            with self.subTest(suite=suite_name, row_id=row_id):
                validate_row(suite_row(suite_name, row_id))

        impossible = suite_row(
            "prototype-annotation.csv", "prototype-annotation-005"
        )
        impossible["output_contract"] = (
            "annotation_handoff_reference|"
            "annotation_presentation_decision|prototype_contract_boundary"
        )
        with self.assertRaisesRegex(
            ValueError, "incompatible strict families"
        ):
            validate_row(impossible)

    def test_verified_plugin_bound_claims_require_distinct_subject_roots(
        self,
    ):
        base = suite_row("uat-evidence-window.csv", "uat-window-001")
        base.update(
            release_expected_evidence_status="verified",
            release_expected_installed_plugin_root="/tmp/installed-plugin",
            release_expected_source_root="/tmp/source-checkout",
            release_expected_refresh_evidence="refresh-proof",
            release_expected_run_scope="targeted",
            release_expected_commands_or_trials="subject-check",
            release_expected_limitations="none",
        )
        for claim_type in sorted(
            routing_schema.RELEASE_PLUGIN_BOUND_CLAIM_TYPES
        ):
            with self.subTest(claim_type=claim_type, state="distinct"):
                row = base.copy()
                row["release_expected_claim_type"] = claim_type
                row["release_expected_refresh_method"] = (
                    "refresh_step"
                    if claim_type == "cache_refresh"
                    else "source_equivalence"
                )
                routing_schema.require_release_evidence_claim_matrix(row)

            with self.subTest(claim_type=claim_type, state="same"):
                row = base.copy()
                row["release_expected_claim_type"] = claim_type
                row["release_expected_refresh_method"] = (
                    "refresh_step"
                    if claim_type == "cache_refresh"
                    else "source_equivalence"
                )
                row["release_expected_source_root"] = row[
                    "release_expected_installed_plugin_root"
                ]
                with self.assertRaisesRegex(
                    ValueError,
                    "distinct installed_plugin_root and source_root subjects",
                ):
                    routing_schema.require_release_evidence_claim_matrix(
                        row
                    )

        with tempfile.TemporaryDirectory() as temporary_directory:
            temporary_root = Path(temporary_directory)
            installed_root = temporary_root / "installed"
            source_root = temporary_root / "source"
            installed_root.mkdir()
            source_root.mkdir()
            installed_alias = temporary_root / "installed-alias"
            installed_alias.symlink_to(
                installed_root, target_is_directory=True
            )

            alias = base.copy()
            alias.update(
                release_expected_claim_type="runtime",
                release_expected_refresh_method="source_equivalence",
                release_expected_installed_plugin_root=str(installed_root),
                release_expected_source_root=str(installed_alias),
            )
            with self.assertRaisesRegex(
                ValueError,
                "distinct installed_plugin_root and source_root subjects",
            ):
                routing_schema.require_release_evidence_claim_matrix(alias)

            nested_source = installed_root / "source"
            nested_source.mkdir()
            nested = alias.copy()
            nested["release_expected_source_root"] = str(nested_source)
            with self.assertRaisesRegex(
                ValueError,
                "must not have an ancestor/descendant relationship",
            ):
                routing_schema.require_release_evidence_claim_matrix(
                    nested
                )

            nested_installed = source_root / "installed"
            nested_installed.mkdir()
            installed_inside_source = alias.copy()
            installed_inside_source[
                "release_expected_installed_plugin_root"
            ] = str(nested_installed)
            installed_inside_source[
                "release_expected_source_root"
            ] = str(source_root)
            with self.assertRaisesRegex(
                ValueError,
                "must not have an ancestor/descendant relationship",
            ):
                routing_schema.require_release_evidence_claim_matrix(
                    installed_inside_source
                )

            nested_installed_alias = temporary_root / "nested-installed-alias"
            nested_installed_alias.symlink_to(
                nested_installed,
                target_is_directory=True,
            )
            resolved_ancestry = installed_inside_source.copy()
            resolved_ancestry[
                "release_expected_installed_plugin_root"
            ] = str(nested_installed_alias)
            with self.assertRaisesRegex(
                ValueError,
                "must not have an ancestor/descendant relationship",
            ):
                routing_schema.require_release_evidence_claim_matrix(
                    resolved_ancestry
                )

    def test_dedicated_oracles_reject_removed_output_contract_tokens(self):
        reviewer_probes = (
            (
                "contract_lineage core",
                suite_row("contract-lineage.csv", "tf-cl-001"),
                "none",
            ),
            (
                "annotation base",
                suite_row(
                    "prototype-annotation.csv",
                    "prototype-annotation-001",
                ),
                "prototype_contract_boundary",
            ),
            (
                "UAT evidence window",
                suite_row("uat-evidence-window.csv", "uat-window-001"),
                "verify_scope|release_evidence_claim",
            ),
        )
        for label, row, output_contract in reviewer_probes:
            with self.subTest(label=label):
                row["output_contract"] = output_contract
                with self.assertRaisesRegex(
                    ValueError,
                    rf"{label} has stale oracle fields",
                ):
                    validate_row(row)

    def test_output_contract_oracle_matrix_rejects_all_stale_groups(self):
        lineage_scope = suite_row("contract-lineage.csv", "tf-cl-002")
        lineage_scope["output_contract"] = "contract_lineage"

        annotation_carrythrough = annotation_carrythrough_row()
        annotation_carrythrough["output_contract"] = (
            "verify_scope|annotation_presentation_decision"
        )

        annotation_reference = suite_row(
            "prototype-annotation.csv",
            "prototype-annotation-005",
        )
        annotation_reference["output_contract"] = (
            "annotation_presentation_decision"
        )

        uat_scope = suite_row(
            "uat-evidence-window.csv",
            "uat-window-006",
        )
        uat_scope["output_contract"] = (
            "verify_scope|release_evidence_claim"
        )

        uat_handoff = suite_row(
            "uat-evidence-window.csv",
            "uat-window-007",
        )
        uat_handoff["output_contract"] = (
            "entry_decision|release_evidence_claim"
        )

        release_claim = suite_row(
            "uat-evidence-window.csv",
            "uat-window-006",
        )
        release_claim["output_contract"] = (
            "verify_scope|uat_evidence_window_forbidden"
        )

        cases = (
            ("contract_lineage scope", lineage_scope),
            ("annotation carrythrough", annotation_carrythrough),
            ("annotation reference", annotation_reference),
            ("release evidence claim", release_claim),
            ("UAT verification scope", uat_scope),
            ("UAT handoff", uat_handoff),
        )
        for label, row in cases:
            with self.subTest(label=label):
                with self.assertRaisesRegex(
                    ValueError,
                    rf"{label} has stale oracle fields",
                ):
                    validate_row(row)

    def test_inactive_oracle_placeholders_do_not_trigger_stale_field_errors(self):
        row = suite_row(
            "prototype-annotation.csv",
            "prototype-annotation-001",
        )
        for field in routing_schema.ANNOTATION_CARRYTHROUGH_EXPECTATION_FIELDS:
            row[field] = "none"
        row[routing_schema.ANNOTATION_REFERENCE_EXPECTATION_FIELD] = " "
        validate_row(row)

    def test_lineage_allows_delimiter_padding_but_rejects_split_tokens(self):
        valid = suite_row("contract-lineage.csv", "tf-cl-001")
        valid["lineage_expected_hops"] = (
            "canonical_contract (verified) > producer_mapping(verified) "
            "> consumer(verified)"
        )
        validate_row(valid)

        invalid_values = (
            "canonical_ contract(verified)>producer_mapping(verified)>consumer(verified)",
            "canonical_contract(veri fied)>producer_mapping(verified)>consumer(verified)",
            "canonical_contract( verified)>producer_mapping(verified)>consumer(verified)",
            "canonical_contract(verified)>producer_mapping(verified)\n>consumer(verified)",
        )
        for value in invalid_values:
            with self.subTest(value=value):
                invalid = suite_row(
                    "contract-lineage.csv", "tf-cl-001"
                )
                invalid["lineage_expected_hops"] = value
                with self.assertRaisesRegex(ValueError, "invalid hop"):
                    validate_row(invalid)

    def test_lineage_rejects_duplicate_unverified_ids_before_set_conversion(self):
        row = suite_row("contract-lineage.csv", "tf-cl-003")
        row["lineage_expected_unverified_hops"] = (
            "canonical_owner|storage|storage"
        )

        with self.assertRaisesRegex(
            ValueError,
            "lineage_expected_unverified_hops contains duplicate "
            "token\\(s\\): storage",
        ):
            validate_row(row)

    def test_lineage_scope_verdict_cannot_pass_with_missing_evidence(self):
        row = suite_row("contract-lineage.csv", "tf-cl-002")
        row["lineage_expected_scope_verdict"] = "pass"

        with self.assertRaisesRegex(
            ValueError, "scope with missing evidence cannot pass"
        ):
            validate_row(row)

    def test_uat_window_stability_accepts_only_finite_productions(self):
        for row_id in ("uat-window-001", "uat-window-002", "uat-window-003"):
            with self.subTest(row_id=row_id):
                validate_row(suite_row("uat-evidence-window.csv", row_id))

        unverified = suite_row("uat-evidence-window.csv", "uat-window-003")
        unverified["fixture"] = "none"
        unverified["uat_expected_window_stability"] = "unverified"
        validate_row(unverified)

        invalid_productions = (
            "restart_required",
            "stability_unverified",
            "restart_required|changed",
            "changed|restart_required|unverified",
            "observed_at:t1",
            "stability_unverified|observed_at:t1",
            "observed_at:t1|stability_unverified|restart_required",
            "observed_at:t1|observed_at:t2|stability_unverified",
        )
        for production in invalid_productions:
            with self.subTest(production=production):
                row = suite_row("uat-evidence-window.csv", "uat-window-003")
                row["uat_expected_window_stability"] = production
                with self.assertRaisesRegex(
                    ValueError, "must use exactly one production"
                ):
                    validate_row(row)

    def test_verified_uat_adapter_requires_source_evidence_token(self):
        row = suite_row("uat-evidence-window.csv", "uat-window-001")
        row["evidence_required"] = "none"
        with self.assertRaisesRegex(
            ValueError,
            "verified UAT adapter requires source_or_unverified evidence",
        ):
            validate_row(row)

    def test_verified_uat_pass_requires_attributed_fingerprint(self):
        for fingerprint in (
            "unverified",
            "unknown",
            "none",
            "not_run",
            "not_applicable",
        ):
            with self.subTest(fingerprint=fingerprint):
                row = suite_row(
                    "uat-evidence-window.csv", "uat-window-001"
                )
                row["uat_expected_fingerprint"] = fingerprint
                with self.assertRaisesRegex(
                    ValueError, "must name an attributed fingerprint"
                ):
                    validate_row(row)

    def test_verified_uat_oracle_must_match_canonical_record(self):
        for field, value in (
            ("uat_expected_fingerprint", "frontend:forged|api:forged"),
            (
                "uat_expected_scope_covered",
                "fingerprint|forged_coverage",
            ),
            ("release_expected_source_root", "/workspace/forged"),
        ):
            with self.subTest(field=field):
                row = suite_row(
                    "uat-evidence-window.csv", "uat-window-001"
                )
                row[field] = value
                with self.assertRaisesRegex(
                    ValueError,
                    "canonical UAT record does not match row oracle",
                ):
                    validate_row(row)

    def test_canonical_uat_record_rejects_hidden_or_non_visible_oracles(self):
        records_path = (
            ROOT / "evals/fixtures/uat-evidence-window/records.md"
        )
        records = records_path.read_text(encoding="utf-8")
        insertion_point = (
            "Verification Scope\n"
            "- Claim: fix_c1_uat_attribution"
        )
        hidden_payloads = (
            (
                "<!-- - Claim: forged_hidden_claim -->\n\n"
                + insertion_point,
                "non-empty HTML comment",
            ),
            (
                "```text\n- Claim: forged_fenced_claim\n```\n\n"
                + insertion_point,
                "fenced hidden payload",
            ),
            (
                "    - Claim: forged_indented_claim\n\n"
                + insertion_point,
                "indented hidden payload",
            ),
        )
        for replacement, expected_error in hidden_payloads:
            with self.subTest(expected_error=expected_error):
                forged_records = records.replace(
                    insertion_point,
                    replacement,
                    1,
                )
                with mock.patch.object(
                    routing_schema,
                    "_canonical_uat_records_text",
                    return_value=forged_records,
                ):
                    with self.assertRaisesRegex(
                        ValueError, expected_error
                    ):
                        validate_row(
                            suite_row(
                                "uat-evidence-window.csv",
                                "uat-window-001",
                            )
                        )

        empty_comment = records.replace(
            insertion_point,
            "<!-- -->\n\n" + insertion_point,
            1,
        )
        with mock.patch.object(
            routing_schema,
            "_canonical_uat_records_text",
            return_value=empty_comment,
        ):
            validate_row(
                suite_row("uat-evidence-window.csv", "uat-window-001")
            )

    def test_verified_uat_pass_requires_material_claim_and_coverage(self):
        for field in (
            "uat_expected_scope_covered",
            "uat_expected_coverage_basis",
            "uat_expected_claim_scope",
        ):
            with self.subTest(field=field):
                row = suite_row(
                    "uat-evidence-window.csv", "uat-window-001"
                )
                row[field] = "none"
                with self.assertRaisesRegex(
                    ValueError, "must name concrete UAT evidence"
                ):
                    validate_row(row)

        missing_claim = suite_row(
            "uat-evidence-window.csv", "uat-window-001"
        )
        missing_claim["uat_expected_scope_claim"] = "none"
        missing_claim["release_expected_claim"] = "none"
        with self.assertRaisesRegex(
            ValueError, "must name concrete UAT evidence"
        ):
            validate_row(missing_claim)

    def test_verified_uat_handoff_requires_stable_attributed_window(self):
        validate_row(suite_row("uat-evidence-window.csv", "uat-window-007"))

        unstable = suite_row("uat-evidence-window.csv", "uat-window-007")
        unstable["uat_handoff_expected_window_stability"] = (
            "changed|restart_required"
        )
        with self.assertRaisesRegex(
            ValueError, "verified UAT handoff requires a stable window"
        ):
            validate_row(unstable)

        bounded_unstable = suite_row(
            "uat-evidence-window.csv", "uat-window-007"
        )
        bounded_unstable["fixture"] = "none"
        bounded_unstable["release_expected_evidence_status"] = "unverified"
        bounded_unstable["uat_handoff_expected_window_stability"] = (
            "changed|restart_required"
        )
        validate_row(bounded_unstable)

        malformed_unstable = bounded_unstable.copy()
        malformed_unstable["uat_handoff_expected_window_stability"] = (
            "restart_required"
        )
        with self.assertRaisesRegex(
            ValueError, "must use exactly one production"
        ):
            validate_row(malformed_unstable)

        for fingerprint in (
            "unverified",
            "unknown",
            "none",
            "not_run",
            "not_applicable",
        ):
            with self.subTest(fingerprint=fingerprint):
                unattributed = suite_row(
                    "uat-evidence-window.csv", "uat-window-007"
                )
                unattributed["uat_handoff_expected_fingerprint"] = fingerprint
                with self.assertRaisesRegex(
                    ValueError, "must name an attributed fingerprint"
                ):
                    validate_row(unattributed)

    def test_annotation_carrythrough_requires_complete_oracle_maps(self):
        validate_row(annotation_carrythrough_row())

        missing_field = annotation_carrythrough_row()
        missing_field["annotation_expected_observed_targets"] = ""
        with self.assertRaisesRegex(
            ValueError,
            "annotation_carrythrough_verification missing required oracle fields",
        ):
            validate_row(missing_field)

        missing_id = annotation_carrythrough_row()
        missing_id["annotation_expected_carrythrough_verdicts"] = (
            "review_arrows=covered|debug_badges=covered|"
            "design_notes=covered"
        )
        with self.assertRaisesRegex(
            ValueError,
            "carry-through verdict IDs must match decision IDs",
        ):
            validate_row(missing_id)

        missing_target_id = annotation_carrythrough_row()
        missing_target_id["annotation_expected_observed_targets"] = (
            "review_arrows=evals/fixtures/prototype-annotation/"
            "visual-packet.md#review_arrows|"
            "debug_badges=evals/fixtures/prototype-annotation/"
            "visual-packet.md#debug_badges|"
            "design_notes=evals/fixtures/prototype-annotation/"
            "visual-packet.md#design_notes"
        )
        with self.assertRaisesRegex(
            ValueError,
            "observed target IDs must match decision IDs",
        ):
            validate_row(missing_target_id)

        invalid_verdict = annotation_carrythrough_row()
        invalid_verdict["annotation_expected_carrythrough_verdicts"] = (
            invalid_verdict["annotation_expected_carrythrough_verdicts"].replace(
                "review_arrows=covered", "review_arrows=ready"
            )
        )
        with self.assertRaisesRegex(
            ValueError, "carry-through verdicts are invalid"
        ):
            validate_row(invalid_verdict)

    def test_annotation_reference_and_targets_must_resolve_and_align(self):
        reference = suite_row(
            "prototype-annotation.csv", "prototype-annotation-005"
        )
        validate_row(reference)

        fixture_relative = reference.copy()
        fixture_relative["annotation_expected_reference"] = (
            "decision-source.md#prototype-annotation-decision-source"
        )
        validate_row(fixture_relative)

        invalid_references = (
            (
                "evals/fixtures/prototype-annotation/missing.md"
                "#prototype-annotation-decision-source",
                "exactly one existing Markdown/HTML file",
            ),
            (
                "evals/fixtures/prototype-annotation/decision-source.md"
                "#missing-anchor",
                "anchor is missing or ambiguous",
            ),
            (
                "evals/fixtures/prototype-annotation/visual-packet.md"
                "#review_arrows",
                "target Annotation IDs must match",
            ),
        )
        for value, expected_error in invalid_references:
            with self.subTest(reference=value):
                invalid = reference.copy()
                invalid["annotation_expected_reference"] = value
                with self.assertRaisesRegex(ValueError, expected_error):
                    validate_row(invalid)

        target_cases = (
            (
                "evals/fixtures/prototype-annotation/missing.md"
                "#review_arrows",
                "exactly one existing Markdown/HTML file",
            ),
            (
                "evals/fixtures/prototype-annotation/visual-packet.md"
                "#missing-anchor",
                "anchor is missing or ambiguous",
            ),
            (
                "evals/fixtures/prototype-annotation/visual-packet.md"
                "#debug_badges",
                "target content must align with Annotation ID review_arrows",
            ),
        )
        for target, expected_error in target_cases:
            with self.subTest(target=target):
                invalid = annotation_carrythrough_row()
                invalid["annotation_expected_observed_targets"] = (
                    invalid["annotation_expected_observed_targets"].replace(
                        "evals/fixtures/prototype-annotation/"
                        "visual-packet.md#review_arrows",
                        target,
                        1,
                    )
                )
                with self.assertRaisesRegex(ValueError, expected_error):
                    validate_row(invalid)

    def test_annotation_reference_ids_ignore_hidden_markdown_content(self):
        visible = """
- Annotation ID: review_arrows
<!--
- Annotation ID: hidden_comment
<aside data-annotation-id="hidden_comment_html"></aside>
-->
```text
- Annotation ID: hidden_fence
<aside data-annotation-id="hidden_fence_html"></aside>
```
    - Annotation ID: hidden_indent
    <aside data-annotation-id="hidden_indent_html"></aside>
<aside data-annotation-id="help_explanation"></aside>
"""
        duplicate = """
- Annotation ID: review_arrows
- Annotation ID: review_arrows
"""

        self.assertEqual(
            routing_schema._annotation_ids_in_reference_region(visible),
            ["review_arrows", "help_explanation"],
        )
        self.assertEqual(
            routing_schema._annotation_ids_in_reference_region(duplicate),
            ["review_arrows", "review_arrows"],
        )

    def test_annotation_reference_html_parser_ignores_non_rendered_contexts(self):
        region = """
- Annotation ID: visible_markdown
<script>
const literal = '<aside data-annotation-id="script_literal"></aside>';
- Annotation ID: hidden_script_markdown
</script>
<style>
.example::before { content: '<i data-annotation-id="style_literal"></i>'; }
</style>
<template>
  <aside data-annotation-id="template_only"></aside>
  - Annotation ID: hidden_template_markdown
</template>
<aside data-annotation-id="visible_html"></aside>
"""
        self.assertEqual(
            routing_schema._annotation_ids_in_reference_region(region),
            ["visible_markdown", "visible_html"],
        )

    def test_annotation_reference_html_parser_preserves_real_duplicates(self):
        duplicate_elements = """
<aside data-annotation-id="duplicate_real"></aside>
<section data-annotation-id="duplicate_real"></section>
"""
        self.assertEqual(
            routing_schema._annotation_ids_in_reference_region(
                duplicate_elements
            ),
            ["duplicate_real", "duplicate_real"],
        )

    def test_annotation_reference_accepts_mixed_markdown_and_html_ids(self):
        mixed = """
- Annotation ID: markdown_control
<aside data-annotation-id="html_control"></aside>
"""
        self.assertEqual(
            routing_schema._annotation_ids_in_reference_region(mixed),
            ["markdown_control", "html_control"],
        )

    def test_annotation_non_file_targets_require_matching_evidence_token(self):
        for target_kind, evidence_token in (
            ("browser", "browser_or_unverified"),
            ("runtime", "runtime_or_unverified"),
        ):
            target = f"{target_kind}:annotation/review_arrows"
            row = annotation_carrythrough_row()
            row["annotation_expected_observed_targets"] = (
                row["annotation_expected_observed_targets"].replace(
                    "evals/fixtures/prototype-annotation/"
                    "visual-packet.md#review_arrows",
                    target,
                    1,
                )
            )
            with self.subTest(target_kind=target_kind, supported=False):
                with self.assertRaisesRegex(ValueError, evidence_token):
                    validate_row(row)

            supported = row.copy()
            supported["evidence_required"] += f"|{evidence_token}"
            with self.subTest(target_kind=target_kind, supported=True):
                validate_row(supported)

    def test_annotation_carrythrough_aggregation_supports_gap_and_unverified(self):
        gap = annotation_carrythrough_row()
        gap["annotation_expected_carrythrough_verdicts"] = (
            gap["annotation_expected_carrythrough_verdicts"].replace(
                "review_arrows=covered", "review_arrows=gap"
            )
        )
        gap["annotation_expected_scope_covered"] = (
            "debug_badges|design_notes|help_explanation"
        )
        gap["annotation_expected_scope_missing"] = "review_arrows"
        gap["annotation_expected_scope_verdict"] = "fail"
        validate_row(gap)

        unverified = annotation_carrythrough_row()
        unverified["annotation_expected_carrythrough_verdicts"] = (
            unverified["annotation_expected_carrythrough_verdicts"].replace(
                "review_arrows=covered", "review_arrows=unverified"
            )
        )
        unverified["annotation_expected_scope_covered"] = (
            "debug_badges|design_notes|help_explanation"
        )
        unverified["annotation_expected_scope_missing"] = "review_arrows"
        unverified["annotation_expected_scope_verdict"] = "partial"
        validate_row(unverified)

        inconsistent = annotation_carrythrough_row()
        inconsistent["annotation_expected_carrythrough_verdicts"] = (
            inconsistent["annotation_expected_carrythrough_verdicts"].replace(
                "review_arrows=covered", "review_arrows=gap"
            )
        )
        with self.assertRaisesRegex(
            ValueError,
            "scope covered IDs must match covered per-ID verdicts",
        ):
            validate_row(inconsistent)

        missing_mismatch = gap.copy()
        missing_mismatch["annotation_expected_scope_missing"] = "none"
        with self.assertRaisesRegex(
            ValueError,
            "scope missing IDs must match gap/unverified per-ID verdicts",
        ):
            validate_row(missing_mismatch)

        verdict_mismatch = gap.copy()
        verdict_mismatch["annotation_expected_scope_verdict"] = "partial"
        with self.assertRaisesRegex(
            ValueError,
            "annotation scope verdict must be fail, not partial",
        ):
            validate_row(verdict_mismatch)

    def test_annotation_carrythrough_fields_are_conditional(self):
        row = suite_row("prototype-annotation.csv", "prototype-annotation-001")
        for field in routing_schema.ANNOTATION_CARRYTHROUGH_EXPECTATION_FIELDS:
            row[field] = ""
        validate_row(row)


if __name__ == "__main__":
    unittest.main()
