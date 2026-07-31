import csv
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def normalize_markdown_heading(value):
    value = value.strip()
    attribute_token = (
        r"(?:[#.][\w:-]+|"
        r"[A-Za-z_:][\w:.-]*=(?:\"[^\"]*\"|'[^']*'|[^\s{}]+))"
    )
    attributes = re.search(r"[ \t]*\{([^{}\n]+)\}[ \t]*$", value)
    if attributes is not None and re.fullmatch(
        rf"{attribute_token}(?:[ \t]+{attribute_token})*",
        attributes.group(1),
    ):
        value = value[: attributes.start()].rstrip()

    code_spans = []
    inline_code = re.compile(r"(?<!`)(`+)(?!`)(.*?)(?<!`)\1(?!`)")

    def preserve_inline_code(match):
        content = match.group(2).replace("\r\n", " ").replace("\r", " ").replace("\n", " ")
        if (
            content.startswith(" ")
            and content.endswith(" ")
            and content.strip(" ")
        ):
            content = content[1:-1]
        placeholder = f"\x00code-span-{len(code_spans)}\x00"
        code_spans.append((placeholder, content))
        return placeholder

    value = inline_code.sub(preserve_inline_code, value)
    value = markdown_link_visible_text(value)

    simple_emphasis = re.compile(
        r"(?<!\w)(\*\*|__|\*|_)(?=\S)(.+?)(?<=\S)\1(?!\w)"
    )
    previous = None
    while value != previous:
        previous = value
        value = simple_emphasis.sub(r"\2", value).strip()
    for placeholder, content in code_spans:
        value = value.replace(placeholder, content)
    return " ".join(value.split())


def matching_markdown_delimiter(value, start, opener, closer):
    depth = 0
    index = start
    while index < len(value):
        character = value[index]
        if character == "\\" and index + 1 < len(value):
            index += 2
            continue
        if character == opener:
            depth += 1
        elif character == closer:
            depth -= 1
            if depth == 0:
                return index
        index += 1
    return None


def markdown_link_visible_text(value):
    visible = []
    index = 0
    while index < len(value):
        if value[index] == "\\" and index + 1 < len(value):
            visible.append(value[index + 1])
            index += 2
            continue

        image = value[index] == "!" and index + 1 < len(value) and value[index + 1] == "["
        label_start = index + 1 if image else index
        if value[label_start] != "[":
            visible.append(value[index])
            index += 1
            continue

        label_end = matching_markdown_delimiter(value, label_start, "[", "]")
        if label_end is None:
            visible.append(value[index])
            index += 1
            continue

        consumed_end = label_end + 1
        if consumed_end < len(value) and value[consumed_end] == "(":
            destination_end = matching_markdown_delimiter(
                value, consumed_end, "(", ")"
            )
            if destination_end is not None:
                consumed_end = destination_end + 1
        else:
            reference_start = consumed_end
            while (
                reference_start < len(value)
                and value[reference_start] in " \t"
            ):
                reference_start += 1
            if (
                reference_start < len(value)
                and value[reference_start] == "["
            ):
                reference_end = matching_markdown_delimiter(
                    value, reference_start, "[", "]"
                )
                if reference_end is not None:
                    consumed_end = reference_end + 1

        label = value[label_start + 1 : label_end]
        visible.append(markdown_link_visible_text(label))
        index = consumed_end
    return "".join(visible)


def markdown_fence_opener(line):
    fence = re.match(r" {0,3}(`{3,}|~{3,})(.*)$", line)
    if fence is None:
        return None
    marker, info_string = fence.groups()
    if marker.startswith("`") and "`" in info_string:
        return None
    return marker


def markdown_headings(text, levels=range(1, 7)):
    allowed_levels = set(levels)
    headings = []
    fence_char = None
    fence_length = 0
    setext_candidate = None
    for line in text.splitlines():
        if fence_char is not None:
            if re.fullmatch(
                rf" {{0,3}}{re.escape(fence_char)}{{{fence_length},}}[ \t]*",
                line,
            ):
                fence_char = None
                fence_length = 0
            continue

        marker = markdown_fence_opener(line)
        if marker is not None:
            fence_char = marker[0]
            fence_length = len(marker)
            setext_candidate = None
            continue

        heading = re.fullmatch(
            r" {0,3}(#{1,6})(?!#)(?:[ \t]+(.*?))?[ \t]*",
            line,
        )
        if heading is not None:
            level = len(heading.group(1))
            value = (heading.group(2) or "").strip()
            value = re.sub(r"[ \t]+#+[ \t]*$", "", value).strip()
            if level in allowed_levels:
                headings.append(normalize_markdown_heading(value))
            setext_candidate = None
            continue

        setext_underline = re.fullmatch(r" {0,3}(-+|=+)[ \t]*", line)
        if setext_underline is not None:
            level = 1 if setext_underline.group(1).startswith("=") else 2
            if setext_candidate is not None and level in allowed_levels:
                headings.append(normalize_markdown_heading(setext_candidate))
            setext_candidate = None
            continue

        if line.strip() and not re.match(r"(?: {4}|\t)", line):
            setext_candidate = line.strip()
        else:
            setext_candidate = None
    return headings


def markdown_h2_headings(text):
    return markdown_headings(text, levels=(2,))


def markdown_heading_owners(documents, heading):
    heading_key = heading.casefold()
    return [
        path
        for path, text in documents
        if heading_key
        in {
            candidate.casefold()
            for candidate in markdown_headings(text)
        }
    ]


def artifact_header_h2_conflicts(text, fields):
    heading_keys = {
        heading.casefold()
        for heading in markdown_h2_headings(text)
    }
    return [
        field
        for field in fields
        if field.casefold() in heading_keys
    ]


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
        self.assertIn("Default output: one compact package skeleton", skill)
        self.assertIn("Do not execute, spawn subagents, create worktrees, or mutate branches", skill)
        self.assertIn("## Default Output Budget", skill)
        self.assertIn("at most 2,800 characters and 26 non-empty lines", skill)
        self.assertIn("regression budget, not a truncation rule", skill)
        self.assertIn("Required fields and semantic completeness take precedence", skill)
        self.assertIn("Every Dispatch output, including lite and split decisions", skill)
        self.assertIn("start the final response at `dispatch_version: 2`", skill)
        self.assertIn("no prose before or after the package", skill)
        self.assertIn("Do not wrap the package in a code fence", skill)
        self.assertIn("do not truncate or silently omit tasks, required evidence, or stop conditions", skill)
        self.assertIn("`needs_split`", skill)
        self.assertIn("route-specific contract", skill)
        self.assertIn("does not apply to adapter-ready, clean-review fanout, complex separation", skill)
        self.assertIn("missing source truth or audit scope", skill)
        self.assertIn("only a lite `needs_info` decision", skill)
        self.assertIn("do not invent generic task lenses", skill)
        self.assertIn("Multi-perspective audit packaging is not clean-review fanout unless", skill)
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
        self.assertLessEqual(len(package.splitlines()), 80)
        self.assertIn("package-only", package)
        self.assertIn("must not execute", package)
        self.assertIn("human-reviewable package skeleton", package)
        self.assertIn("not adapter-complete until extended fields are supplied", package)
        self.assertIn("## Default Output Budget", package)
        self.assertIn("at most 2,800 characters and 26 non-empty lines", package)
        self.assertIn("regression budget, not a truncation rule", package)
        self.assertIn("Every Dispatch output, including lite and split decisions", package)
        self.assertIn("start at `dispatch_version: 2`", package)
        self.assertIn("without prose before or after", package)
        self.assertIn("Do not wrap it in a code fence", package)
        self.assertIn("do not truncate or silently omit", package)
        self.assertIn("needs_split", package)
        self.assertIn("route-specific contract", package)
        self.assertIn("adapter_completeness: skeleton_only | adapter_ready", package)
        self.assertIn("readiness_source:", package)
        self.assertIn("redactions_applied:", package)
        self.assertIn(
            "route: local_direct | local_with_artifact | worktree_isolated | worktree_review_only | automation_candidate",
            package,
        )
        self.assertNotIn("| clean_review", package)
        self.assertIn("clean review is not a separate route", package)
        self.assertNotIn("dispatch_native_alignment:", package)
        self.assertNotIn("goal_contract:", package)
        self.assertNotIn("runtime_package:", package)
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
        self.assertNotIn("legacy_compatibility:", details)

        compact_route_line = next(
            line.strip() for line in package.splitlines() if line.strip().startswith("route:")
        )
        compact_routes = {value.strip() for value in compact_route_line.split(":", 1)[1].split("|")}
        details_route_line = next(
            line.strip() for line in details.splitlines() if line.strip().startswith("route_enum:")
        )
        details_routes = {
            value.strip()
            for value in details_route_line.split("[", 1)[1].rstrip("]").split(",")
        }
        self.assertEqual(compact_routes, details_routes)

    def test_dispatch_approval_gate_never_authorizes_dispatch_execution(self):
        branches = self.read("skills/dispatch/DISPATCH-ROUTER-BRANCHES.md")
        with (ROOT / "evals/prompts/dispatch.csv").open(newline="", encoding="utf-8") as handle:
            rows = {row["id"]: row for row in csv.DictReader(handle)}

        self.assertIn("Dispatch stops after emitting the approval gate", branches)
        self.assertIn("record the gate as satisfied", branches)
        self.assertIn("do not ask for the same approval again", branches)
        self.assertIn("Only the owning executor or runtime may proceed", branches)
        self.assertNotIn("Proceed only after explicit approval", branches)
        self.assertIn("execution remains with the owning runtime or operator", rows["dispatch-009"]["expected_behavior"])
        self.assertIn("approval gate as satisfied", rows["dispatch-022"]["expected_behavior"])
        self.assertIn("only the owning executor or runtime may proceed", rows["dispatch-022"]["expected_behavior"])

    def test_dispatch_and_result_contracts_have_one_base_schema_with_adapter_deltas(self):
        details = self.read("skills/dispatch/DISPATCH-PACKAGE-DETAILS.md")
        examples = self.read("skills/dispatch/EXAMPLES.md")
        runtimes = self.read("skills/dispatch/RUNTIME-ADAPTERS.md")
        adapter_dispatch = self.read(
            "skills/dispatch/adapters/codex_app_managed_worktree_thread/DISPATCH-PACKAGE-CONTRACT.md"
        )
        result = self.read("skills/dispatch/RESULT-PACKAGE.md")
        adapter_result = self.read(
            "skills/dispatch/adapters/codex_app_managed_worktree_thread/RESULT-PACKAGE-TEMPLATE.md"
        )

        self.assertNotIn("dispatch_native_alignment", details + examples + runtimes + adapter_dispatch)
        self.assertIn("route_decision:", details)
        self.assertIn("source_package:", details)
        self.assertIn("verification_expectation:", details)
        self.assertIn("adapter_extension: {}", details)
        self.assertIn("Start with the canonical task schema", adapter_dispatch)
        self.assertIn("legacy_compatibility:", adapter_dispatch)
        self.assertNotIn("\n    legacy_compatibility:", examples)
        self.assertNotIn("\ndispatch_version: 2\n", adapter_dispatch)
        self.assertNotIn("\ntasks:\n", adapter_dispatch)

        result_envelope = result.split("```yaml", 1)[1].split("```", 1)[0]
        self.assertIn(
            "outcome: ready_for_review | needs_remediation | blocked | human_decision | no_execution_needed",
            result_envelope,
        )
        self.assertNotIn("\n  status:", result_envelope)
        self.assertNotIn("no_worktree_needed", result_envelope)
        for axis in ("runtime_lifecycle", "review", "review_loop", "merge_back", "archive", "branch_cleanup"):
            self.assertIn(f"  {axis}:", result_envelope)

        adapter_delta = adapter_result.split("```yaml", 1)[1].split("```", 1)[0]
        self.assertIn("adapter_extension:", adapter_delta)
        self.assertNotIn("result_package:", adapter_delta)
        self.assertNotIn("outcome:", adapter_delta)
        self.assertNotIn("review_loop:", adapter_delta)
        self.assertIn("Start with the complete envelope", adapter_result)
        runtime_package_line = next(
            line for line in details.splitlines() if line.strip().startswith("runtime_package:")
        )
        self.assertNotIn("thread_title", runtime_package_line)
        self.assertIn("initial_thread_title:", adapter_delta)
        self.assertIn("current_thread_title:", adapter_delta)

    def test_current_dispatch_workflow_and_eval_cases_use_the_base_delta_contract(self):
        workflow = self.read("docs/runtime-dispatch-workflow.md")
        dispatch_cases = self.read("evals/prompts/dispatch.csv")
        lifecycle_cases = self.read("evals/prompts/dispatch-managed-worktree-lifecycle.csv")
        lifecycle_scenario = self.read("evals/scenarios/managed-worktree-lifecycle.md")
        current_sources = workflow + dispatch_cases + lifecycle_cases + lifecycle_scenario

        self.assertNotIn("dispatch_native_alignment", current_sources)
        self.assertIn("adapter_extension", workflow)
        self.assertIn("single canonical base", workflow)
        self.assertIn("outcome: no_execution_needed", lifecycle_scenario)
        self.assertIn("legacy no_worktree_needed", lifecycle_cases)
        self.assertNotIn("choose no_worktree_needed or", lifecycle_cases)

    def test_managed_worktree_lifecycle_axes_and_child_prompt_linter_are_canonical(self):
        lifecycle = self.read(
            "skills/dispatch/adapters/codex_app_managed_worktree_thread/THREAD-LIFECYCLE.md"
        )
        prompt = self.read(
            "skills/dispatch/adapters/codex_app_managed_worktree_thread/THREAD-PROMPT-TEMPLATE.md"
        )
        adapter_dispatch = self.read(
            "skills/dispatch/adapters/codex_app_managed_worktree_thread/DISPATCH-PACKAGE-CONTRACT.md"
        )

        thread_states = lifecycle.split("## Thread Lifecycle States", 1)[1].split(
            "## Independent Status Axes", 1
        )[0]
        self.assertIn("running -> result_returned | failed | blocked", thread_states)
        for downstream_state in (
            "clean_review_pending",
            "merge_pending",
            "archive_ready",
            "branch_cleanup_pending",
        ):
            self.assertNotIn(downstream_state, thread_states)
        self.assertIn("| `review` |", lifecycle)
        self.assertIn("| `merge_back` |", lifecycle)
        self.assertIn("| `archive` |", lifecycle)
        self.assertIn("| `branch_cleanup` |", lifecycle)
        self.assertIn("thread_status:", lifecycle)
        self.assertNotIn("current_status: created", lifecycle)

        canonical_linter = "python3 skills/_shared/tools/lint_child_goal_prompt.py"
        self.assertIn(canonical_linter, prompt)
        self.assertIn(canonical_linter, adapter_dispatch)
        self.assertNotIn("python3 scripts/lint_child_goal_prompt.py", prompt + adapter_dispatch)
        self.assertIn(
            "{adapter_extension.codex_app_managed_worktree_thread.initial_thread_title}",
            prompt,
        )
        self.assertIn(
            "{adapter_extension.codex_app_managed_worktree_thread.current_thread_title}",
            prompt,
        )
        self.assertIn(
            "{adapter_extension.codex_app_managed_worktree_thread.parent_thread_identifier}",
            prompt,
        )
        self.assertIn(
            "{adapter_extension.codex_app_managed_worktree_thread.worktree_init.child_thread_identifier}",
            prompt,
        )
        self.assertIn(
            "{adapter_extension.codex_app_managed_worktree_thread.title_mutation_detected}",
            prompt,
        )
        for invalid_base_path in (
            "{runtime_identity.parent_thread_identifier}",
            "{runtime_identity.child_thread_identifier}",
            "{runtime_identity.title_mutation_detected}",
        ):
            self.assertNotIn(invalid_base_path, prompt)
        self.assertNotIn("runtime_package.thread_title", prompt + adapter_dispatch)

    def test_dispatch_read_path_eval_names_an_existing_task_fixture(self):
        with (ROOT / "evals/prompts/routing-blind.csv").open(newline="", encoding="utf-8") as handle:
            rows = {row["id"]: row for row in csv.DictReader(handle)}

        row = rows["blind-dispatch-read-path-001"]
        fixture = ROOT / row["fixture"] / "ACCEPTED-TASK.md"
        self.assertTrue(fixture.is_file())
        self.assertIn("ACCEPTED-TASK.md", row["input_scenario"])

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
        verify_scope = self.read("skills/verify/VERIFY-SCOPE.md")
        self.assertIn("- Claim:", verify_scope)
        self.assertIn("- Covered:", verify_scope)
        self.assertIn("- Missing:", verify_scope)
        self.assertIn("Verdict: blocked", verify_scope)
        self.assertIn("Code diff alone cannot support", verify_scope)

    def test_verify_has_named_evidence_default_path_without_package_self_inspection(self):
        skill = self.read("skills/verify/SKILL.md")

        self.assertIn("## Default Path: Named Evidence Verification", skill)
        self.assertIn("`CLAIM.md`", skill)
        self.assertIn("`EVIDENCE.md`", skill)
        self.assertIn("this active `verify` contract", skill)
        self.assertIn("the user-named claim, evidence, scope, or check-output artifacts", skill)
        self.assertIn("`VERIFY-SCOPE.md` and `SCOPE-EVIDENCE-TEMPLATE.md`", skill)
        self.assertIn("plugin/package self-inspection", skill)
        self.assertIn("explicitly asks", skill)
        self.assertIn("other skill `SKILL.md` files", skill)
        self.assertIn("Scenario workspace allowlisted file discovery is allowed", skill)
        self.assertIn("do not treat allowlisted discovery of the named evidence files as a hard failure", skill)
        self.assertIn("keep the verify safety boundary", skill)
        self.assertIn("concrete claim, `Covered`, `Missing`", skill)
        self.assertIn("missing evidence", skill)
        self.assertIn("bounded verdict", skill)

        default_section = skill.split("## Default Path: Named Evidence Verification", 1)[1].split("## Evidence Boundary", 1)[0]
        read_only_section = default_section.split("Read only:", 1)[1].split("Do not inspect", 1)[0]
        self.assertNotIn("README", read_only_section)
        self.assertNotIn(".codex-plugin/plugin.json", read_only_section)
        self.assertNotIn("plugin manifests", read_only_section)
        self.assertNotIn("package internals", read_only_section)
        self.assertNotIn("other skill `SKILL.md`", read_only_section)
        self.assertNotIn("Groundwork", default_section)

        default_path_index = skill.index("## Default Path: Named Evidence Verification")
        evidence_boundary_index = skill.index("## Evidence Boundary")
        load_only_index = skill.index("## Load Only What Fits")
        self.assertLess(default_path_index, evidence_boundary_index)
        self.assertLess(evidence_boundary_index, load_only_index)

    def test_verify_contract_lineage_reference_is_conditional_and_within_entry_budget(self):
        skill = self.read("skills/verify/SKILL.md")
        default_section = skill.split(
            "## Default Path: Named Evidence Verification", 1
        )[1].split("## Evidence Boundary", 1)[0]
        load_only_section = skill.split("## Load Only What Fits", 1)[1].split(
            "## Stop Conditions", 1
        )[0]

        self.assertIn("Cross-boundary contract lineage or fix-owner tracing", load_only_section)
        self.assertIn("skills/_shared/CONTRACT-NOTES.md", load_only_section)
        self.assertIn(
            "only when the claim crosses ownership or representation boundaries",
            load_only_section,
        )
        self.assertIn("do not load it for ordinary verification", load_only_section)
        self.assertEqual(skill.count("skills/_shared/CONTRACT-NOTES.md"), 1)
        self.assertNotIn("CONTRACT-NOTES.md", default_section)
        self.assertLessEqual(len(skill.splitlines()), 140)

    def test_prototype_annotation_hard_stop_preserves_the_conditional_contract(self):
        skill = self.read("skills/prototype/SKILL.md")
        required_evidence = skill.split("## Required Evidence", 1)[1].split(
            "## Workflow", 1
        )[0]
        hard_stops = skill.split("## Hard Stops", 1)[1].split(
            "## Failure Handling", 1
        )[0]

        self.assertIn("DECISION-CAPTURE.md", required_evidence)
        self.assertIn("author/reviewer annotation layer", required_evidence)
        self.assertIn("stable `Annotation ID`", hard_stops)
        self.assertIn("purpose, presentation disposition", hard_stops)
        self.assertIn(
            "when applicable, the same-block `Audience-facing Source` or `Companion Reference`",
            hard_stops,
        )

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
        self.assertIn("plugin/package self-inspection", skill)
        self.assertIn("unrelated skill files", skill)
        self.assertIn("shared lifecycle/evidence references", skill)
        self.assertNotIn("Maintenance Compact Path", skill)
        self.assertIn("source/package behavior", skill)
        self.assertIn("compact conversation PRD/spec", skill)
        self.assertIn("durable PRD artifact", skill)
        self.assertIn("## Durable Write Gate", skill)
        self.assertIn("Write or update a durable PRD file only when all four conditions are true", skill)
        self.assertIn("If any condition is false or unknown, keep the output in conversation", skill)
        self.assertIn("Mark missing product facts as **NEEDS CLARIFICATION**", skill)

        durable_gate_index = skill.index("Durable Write Gate")
        template_index = skill.index("`PRD-TEMPLATE.md`")
        self.assertLess(durable_gate_index, template_index)
        self.assertRegex(
            skill[durable_gate_index : template_index + len("`PRD-TEMPLATE.md`")],
            r"\bloads? `PRD-TEMPLATE\.md`",
        )

        fast_path_index = skill.index("## Fast Path: Prompt-Provided Compact PRD")
        required_evidence_index = skill.index("## Required Evidence")
        fast_path = skill[fast_path_index:required_evidence_index]

        self.assertLess(fast_path_index, required_evidence_index)
        for cue in ("install", "marketplace", "runtime", "workflow", "version", "skill-selection"):
            self.assertIn(cue, fast_path)

    def test_public_runtime_contracts_do_not_embed_repo_specific_maintenance_rules(self):
        paths = [
            "skills/to-prd/SKILL.md",
            "skills/write-plan/SKILL.md",
            "skills/prototype/SKILL.md",
            "skills/implement/SKILL.md",
            "skills/verify/SKILL.md",
            "skills/handoff/SKILL.md",
            "skills/wiki/SKILL.md",
        ]

        for path in paths:
            skill = self.read(path)
            self.assertNotIn("Groundwork", skill, path)
            self.assertNotIn("AGENTS.md", skill, path)

        for path in ROOT.glob("skills/*/SKILL.md"):
            self.assertNotIn("AGENTS.md", path.read_text(encoding="utf-8"), str(path))

    def test_lifecycle_preflight_has_explicit_lazy_load_paths(self):
        references = [
            "skills/to-prd/SKILL.md",
            "skills/to-issues/SKILL.md",
            "skills/wiki/SKILL.md",
            "skills/implement/IMPLEMENT-BRANCHES.md",
            "skills/verify/VERIFY-ROUTER-BRANCHES.md",
        ]

        for path in references:
            self.assertIn("skills/_shared/LIFECYCLE-PREFLIGHT.md", self.read(path), path)

        lifecycle = self.read("skills/_shared/LIFECYCLE-PREFLIGHT.md")
        to_issues = self.read("skills/to-issues/SKILL.md")
        promotion = self.read("skills/_shared/ARTIFACT-PROMOTION.md")

        self.assertIn("The only issue/task-splitting lazy-load exception is `to-issues`", lifecycle)
        self.assertIn("current-conversation review", lifecycle)
        self.assertIn("explicitly no durable, paste-ready tracker use, remote, cross-session/agent", lifecycle)
        self.assertIn("A format-only paste-ready preview explicitly limited to current-conversation review with no external use is not downstream intent", lifecycle)
        self.assertIn("Unknown or ambiguous downstream intent does not qualify", lifecycle)
        self.assertIn("does not bypass artifact promotion", lifecycle)
        self.assertIn("The only full-preflight no-load branch", to_issues)
        self.assertIn("unknown/ambiguous downstream intent", to_issues)
        self.assertIn("current-review-only and not downstream-ready", to_issues)
        self.assertIn("Paste-ready output is downstream intent unless", to_issues)
        self.assertIn("before any issue split", to_issues)
        self.assertIn("promote it first or explicitly cite an external issue/PR as canonical", promotion)

    def test_to_issues_active_fixtures_force_full_preflight_for_downstream_or_unknown_use(self):
        with (ROOT / "evals/prompts/to-issues.csv").open(newline="", encoding="utf-8") as handle:
            rows = {row["id"]: row for row in csv.DictReader(handle)}

        for row_id in ("to-issues-003", "to-issues-007"):
            behavior = rows[row_id]["expected_behavior"]
            self.assertIn("Run full lifecycle preflight", behavior, row_id)
            self.assertIn("paste-ready tracker use is downstream intent", behavior, row_id)
            self.assertIn("do not use the current-review-only no-load branch", behavior, row_id)

        unknown_behavior = rows["to-issues-020"]["expected_behavior"]
        self.assertIn("Run full lifecycle preflight", unknown_behavior)
        self.assertIn("downstream intent is unknown or ambiguous", unknown_behavior)
        self.assertIn("do not use the current-review-only no-load branch", unknown_behavior)

    def test_branch_references_have_audience_first_headers(self):
        paths = [
            "skills/dispatch/EXAMPLES.md",
            "skills/dispatch/DISPATCH-ROUTER-BRANCHES.md",
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

    def test_dispatch_reference_headers_use_compact_single_line_fields(self):
        decision_fields = (
            "Target Reader",
            "Reader Action Needed",
            "Decision Supported",
        )
        scoped_fields = (
            *decision_fields,
            "Scope",
            "Out of Scope",
            "Evidence Level",
        )
        compact_fields = {
            "skills/dispatch/CONFLICT-PREFLIGHT.md": (
                *decision_fields,
                "Artifact Type",
                "Source of Truth",
                "Scope",
                "Evidence Level",
                "Safe to Share / Redaction Notes",
            ),
            "skills/dispatch/DISPATCH-PACKAGE-DETAILS.md": scoped_fields,
            "skills/dispatch/RESULT-PACKAGE.md": scoped_fields,
            "skills/dispatch/ROUTING-PROFILES.md": (
                *decision_fields,
                "Scope",
                "Out of Scope",
                "Artifact Type",
                "Source of Truth",
                "Evidence Level",
                "Safe to Share / Redaction Notes",
            ),
            "skills/dispatch/RUNTIME-ADAPTERS.md": scoped_fields,
            "skills/dispatch/adapters/codex_app_managed_worktree_thread/ADAPTER.md": (
                *decision_fields,
                "Scope",
                "Evidence Level",
            ),
            "skills/dispatch/adapters/codex_app_managed_worktree_thread/DISPATCH-PACKAGE-CONTRACT.md": scoped_fields,
            "skills/dispatch/adapters/codex_app_managed_worktree_thread/RATIONALE.md": scoped_fields,
            "skills/dispatch/adapters/codex_app_managed_worktree_thread/REJECT-NOOP-CHECKLIST.md": scoped_fields,
            "skills/dispatch/adapters/codex_app_managed_worktree_thread/RESULT-PACKAGE-TEMPLATE.md": scoped_fields,
            "skills/dispatch/adapters/codex_app_managed_worktree_thread/THREAD-LIFECYCLE.md": scoped_fields,
            "skills/dispatch/adapters/codex_app_managed_worktree_thread/THREAD-PROMPT-TEMPLATE.md": scoped_fields,
        }
        self.assertEqual(sum(len(fields) for fields in compact_fields.values()), 76)
        sections_after_scope = {
            "skills/dispatch/CONFLICT-PREFLIGHT.md": ("## Out of Scope",),
            "skills/dispatch/adapters/codex_app_managed_worktree_thread/ADAPTER.md": (
                "In scope:",
                "## Out of Scope",
            ),
        }

        for path, fields in compact_fields.items():
            text = self.read(path)
            lines = text.splitlines()
            self.assertTrue(lines[0].startswith("# "), path)
            self.assertEqual(lines[1], "", path)
            cursor = 2

            for field in fields:
                self.assertRegex(
                    lines[cursor],
                    rf"^{re.escape(field)}: \S(?:.*\S)?$",
                    (path, field),
                )
                cursor += 1
                self.assertEqual(lines[cursor], "", (path, field))
                cursor += 1

                markers = sections_after_scope.get(path, ()) if field == "Scope" else ()
                for marker in markers:
                    self.assertEqual(lines[cursor], marker, (path, marker))
                    cursor += 1
                    self.assertEqual(lines[cursor], "", (path, marker))
                    cursor += 1
                    first_bullet = cursor
                    while cursor < len(lines) and lines[cursor].startswith("- "):
                        cursor += 1
                    self.assertGreater(cursor, first_bullet, (path, marker))
                    self.assertEqual(lines[cursor], "", (path, marker))
                    cursor += 1

            self.assertLess(cursor, len(lines), path)
            self.assertNotEqual(lines[cursor], "", path)

            for field in fields:
                indexes = [
                    index
                    for index, line in enumerate(lines)
                    if line.startswith(f"{field}:")
                ]
                self.assertEqual(len(indexes), 1, (path, field))
            self.assertEqual(artifact_header_h2_conflicts(text, fields), [], path)

        self.assertIn("## Target Reader", self.read("skills/to-prd/PRD-TEMPLATE.md"))

    def test_markdown_h2_parser_handles_fences_setext_and_normalization(self):
        self.assertEqual(
            markdown_h2_headings(
                "````md\n"
                "```not-a-close\n"
                "## Combined Loop ##\n"
                "_Combined Loop_ {.hidden}\n"
                "--------------------------\n"
                "````\n"
                "~~~md\n"
                "## **Combined Loop** {#also-hidden}\n"
                "~~~\n"
                "## **Combined Loop** {#combined-loop} ##\n"
                "_CoMbInEd LoOp_ {.alias}\n"
                "--------------------------\n"
                "  ## Real Heading ###"
            ),
            ["Combined Loop", "CoMbInEd LoOp", "Real Heading"],
        )

    def test_markdown_heading_parser_covers_all_atx_and_setext_levels_outside_fences(self):
        self.assertEqual(
            markdown_headings(
                "```md\n"
                "# Hidden ATX One\n"
                "Hidden Setext One\n"
                "=================\n"
                "```\n"
                "# ATX One\n"
                "## ATX Two\n"
                "### ATX Three\n"
                "#### ATX Four\n"
                "##### ATX Five\n"
                "###### ATX Six\n"
                "####### Not A Heading\n"
                "Setext One\n"
                "==========\n"
                "Setext Two\n"
                "----------"
            ),
            [
                "ATX One",
                "ATX Two",
                "ATX Three",
                "ATX Four",
                "ATX Five",
                "ATX Six",
                "Setext One",
                "Setext Two",
            ],
        )

    def test_markdown_h2_parser_normalizes_link_and_inline_code_visible_text(self):
        self.assertEqual(
            markdown_h2_headings(
                "## [Target Reader](https://example.test/a_(b))\n"
                "## `Reader Action Needed`\n"
                "**[Decision Supported][decision]**\n"
                "----------------------------------"
            ),
            ["Target Reader", "Reader Action Needed", "Decision Supported"],
        )

    def test_markdown_h2_parser_normalizes_nested_destinations_labels_and_references(self):
        self.assertEqual(
            markdown_h2_headings(
                "## [Target Reader](https://example.test/a_(b_(c)))\n"
                "## [Reader [Action] Needed](https://example.test/action)\n"
                "**[Decision [Supported]][decision[nested]]**\n"
                "------------------------------------------"
            ),
            ["Target Reader", "Reader Action Needed", "Decision Supported"],
        )

        for hidden_heading in (
            "[Target Reader](https://example.test/a_(b_(c)))",
            "[Target [Reader]](https://example.test/reader)",
            "[Target [Reader]][target[nested]]",
        ):
            with self.subTest(hidden_heading=hidden_heading):
                self.assertEqual(
                    artifact_header_h2_conflicts(
                        f"## {hidden_heading}",
                        ("Target Reader", "Reader Action Needed"),
                    ),
                    ["Target Reader"],
                )

    def test_markdown_h2_parser_rejects_backtick_info_string_with_backtick(self):
        self.assertEqual(
            markdown_h2_headings(
                "```python `invalid-info`\n"
                "## Target Reader"
            ),
            ["Target Reader"],
        )

    def test_artifact_header_h2_conflicts_are_case_insensitive(self):
        self.assertEqual(
            artifact_header_h2_conflicts(
                "## TARGET READER\n"
                "## unrelated",
                ("Target Reader", "Reader Action Needed"),
            ),
            ["Target Reader"],
        )

    def test_combined_loop_has_one_canonical_owner(self):
        first_principles = self.read("skills/_shared/FIRST-PRINCIPLES.md")
        adversarial_review = self.read("skills/_shared/ADVERSARIAL-REVIEW.md")
        owners = markdown_heading_owners(
            (
                (
                    path.relative_to(ROOT).as_posix(),
                    path.read_text(encoding="utf-8"),
                )
                for path in sorted(ROOT.glob("skills/**/*.md"))
            ),
            "Combined Loop",
        )

        self.assertEqual(owners, ["skills/_shared/ADVERSARIAL-REVIEW.md"])
        self.assertIn("Construct -> Attack -> Narrow -> Verify", adversarial_review)
        self.assertNotIn("FIRST-PRINCIPLES.md", adversarial_review)
        self.assertIn("skills/_shared/ADVERSARIAL-REVIEW.md", first_principles)
        self.assertNotIn("## Combined Loop", first_principles)
        self.assertNotIn("Construct -> Attack -> Narrow -> Verify", first_principles)

    def test_combined_loop_owner_detection_catches_h1_and_h3_reintroduction(self):
        canonical = ("skills/_shared/ADVERSARIAL-REVIEW.md", "## Combined Loop")
        for duplicate_heading in ("# Combined Loop", "### Combined Loop"):
            with self.subTest(duplicate_heading=duplicate_heading):
                owners = markdown_heading_owners(
                    (
                        canonical,
                        ("skills/_shared/DUPLICATE.md", duplicate_heading),
                    ),
                    "Combined Loop",
                )
                self.assertEqual(
                    owners,
                    [
                        "skills/_shared/ADVERSARIAL-REVIEW.md",
                        "skills/_shared/DUPLICATE.md",
                    ],
                )

    def test_hot_path_runtime_references_use_compact_purpose_headers(self):
        paths = [
            "skills/implement/IMPLEMENT-BRANCHES.md",
            "skills/implement/LIGHTWEIGHT-PLAN.md",
            "skills/implement/SELF-REVIEW.md",
            "skills/implement/TDD-LITE.md",
            "skills/verify/VERIFY-SCOPE.md",
            "skills/verify/SCOPE-EVIDENCE-TEMPLATE.md",
            "skills/_shared/FIRST-PRINCIPLES.md",
            "skills/_shared/ADVERSARIAL-REVIEW.md",
        ]

        for path in paths:
            text = self.read(path)
            self.assertIn("Purpose:", text, path)
            self.assertNotIn("Target Reader:", text, path)


if __name__ == "__main__":
    unittest.main()
