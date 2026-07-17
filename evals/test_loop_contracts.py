#!/usr/bin/env python3
import csv
import json
import unittest
from pathlib import Path

from evals import patch_suggestions
from evals import routing_schema
from evals import run_runtime
from evals import suite_registry
from evals.checks import loop_checks


ROOT = Path(__file__).resolve().parents[1]
TRACE_SUITE = ROOT / "evals/prompts/trace-first-verify-review.csv"
CONTRACT_LINEAGE_SUITE = ROOT / "evals/prompts/contract-lineage.csv"


def read(relative_path):
    return (ROOT / relative_path).read_text(encoding="utf-8")


def trace_row(row_id):
    path = CONTRACT_LINEAGE_SUITE if row_id.startswith("tf-cl-") else TRACE_SUITE
    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    row = next(item.copy() for item in rows if item["id"] == row_id)
    row["_suite"] = path.name
    row["_row_number"] = 0
    row["_fieldnames"] = list(row)
    return row


def lineage_route_companion(actual_route):
    if actual_route == "implement":
        return """## Diagnosis Outcome
- Confirmed Cause: producer_mapping is the first confirmed divergence
- Decisive Evidence: canonical_contract differs from producer_mapping
- Smallest Safe Next Action: fix producer then reverify consumer
"""
    if actual_route == "verify":
        return """## Verification Continuation
- Next Check: reverify frontend_renderer after the frontend boundary is corrected
"""
    if actual_route == "write-plan":
        return """## Implementation Plan
- Accepted Goal: resolve canonical_owner and storage without inventing ownership
- Ordered Steps: inspect canonical_owner then storage then producer_a and producer_b
- Dependencies / Gates: canonical_owner and storage remain unverified so implementation is blocked
- Verification Checkpoints: compare each inspected unverified hop with the accepted contract
- Stop Condition: canonical_owner and storage become evidence-backed or remain blocked
"""
    return ""


def source_observation_event(row_id):
    row = trace_row(row_id)
    scenario = (
        ROOT / row["fixture"] / "SCENARIO.md"
    ).read_text(encoding="utf-8")
    return json.dumps(
        {
            "type": "item.completed",
            "item": {
                "type": "command_execution",
                "command": "sed -n '1,240p' SCENARIO.md",
                "aggregated_output": scenario,
                "exit_code": 0,
                "status": "completed",
            },
        }
    )


def trace_verdict(
    row_id,
    actual_route,
    response,
    *,
    include_lineage_companion=True,
    stdout=None,
):
    if row_id.startswith("tf-cl-") and include_lineage_companion:
        response = response.rstrip() + "\n\n" + lineage_route_companion(actual_route)
    if stdout is None and row_id.startswith("tf-cl-"):
        stdout = source_observation_event(row_id)
    if stdout is None and row_id in {"tf-vr-003", "tf-vr-004"}:
        stdout = json.dumps(
            {
                "type": "item.completed",
                "item": {
                    "type": "command_execution",
                    "command": "node test/taskSearch.test.mjs",
                    "aggregated_output": "expected failure reproduced",
                    "exit_code": 1,
                    "status": "failed",
                },
            }
        )
    return run_runtime.routing_verdict_model(
        trace_row(row_id),
        actual_route,
        response,
        0,
        [],
        [],
        stdout=stdout or "",
    )


class LoopContractTests(unittest.TestCase):
    def _risk_checkpoint(self, *, rollback="restore the prior snapshot", tail=""):
        return f"""Risky Action Checkpoint
- Proposed Action: update one production data row
- Action Kind: data_mutation
- Target: production database
- Target Kind: data_store
- Risk: customer-visible data mutation
- Rollback/Undo: {rollback}
- Approval Needed: yes
- Risk Gate: data_write
- Approval Status: pending
- Action State: blocked
- Checkpoint Position: before_action
{tail}"""

    def test_qa_gap_closure_is_named_bounded_and_non_automatic(self):
        registry = json.loads(
            read("scripts/codex-hooks/groundwork_route_registry.json")
        )
        transition = registry["feedback_transitions"]["qa_gap_closure"]

        self.assertEqual(transition["from_route"], "verify")
        self.assertEqual(transition["to_route"], "implement")
        self.assertEqual(
            transition["preserved_or_produced_state"], "implementation_ready"
        )
        self.assertFalse(transition["automatic"])
        self.assertIn("new_evidence_or_changed_hypothesis", transition["requires"])
        self.assertIn("matching_original_reqa_identity", transition["requires"])
        self.assertIn("existing_implementation_authority", transition["requires"])
        self.assertIn("no_new_or_increased_risk", transition["requires"])
        self.assertIn("finite_scoped_next_action", transition["requires"])

    def test_delivery_loop_has_feedback_and_explicit_exit_boundaries(self):
        state_machine = read("skills/_shared/WORKFLOW-STATE-MACHINE.md")

        self.assertIn("## Guided R&D Delivery Loop", state_machine)
        self.assertIn("product or contract gap", state_machine)
        self.assertIn("cross-session gap", state_machine)
        self.assertIn("non-executing delivery loop", state_machine)
        self.assertIn("human decision is required", state_machine)

    def test_prototype_learning_loop_requires_evidence_and_decision_delta(self):
        contract = read("skills/prototype/DECISION-CAPTURE.md")

        self.assertIn("## Prototype Learning Loop", contract)
        for field in (
            "Current Hypothesis",
            "Probe",
            "Observation",
            "Evidence Delta Status",
            "Evidence Delta",
            "Decision Delta Status",
            "Decision Delta",
            "Next Probe or Stop",
        ):
            self.assertIn(field, contract)
        self.assertIn("no evidence delta", contract.lower())
        self.assertIn("never auto-run", contract)

    def test_spec_convergence_loop_is_one_question_and_not_zero_unknowns(self):
        grilling = read("skills/_shared/GRILLING.md")

        self.assertIn("## Spec Convergence Loop", grilling)
        self.assertIn("one question", grilling.lower())
        self.assertIn("new decision delta", grilling)
        self.assertIn("not when every possible unknown has disappeared", grilling)
        self.assertIn("never \"push right\" past", grilling)

    def test_generated_maintainer_suggestions_cannot_advance_learning_state(self):
        artifact = patch_suggestions.generate_patch_suggestions(
            ROOT / "evals/fixtures/patch-suggestions"
        )

        self.assertTrue(artifact["suggestions"])
        for suggestion in artifact["suggestions"]:
            self.assertEqual(suggestion["learning_status"], "observed")
            self.assertEqual(suggestion["promotion_target"], "none")
            self.assertEqual(suggestion["human_decision"], "none")
            self.assertFalse(suggestion["auto_apply"])

        protocol = read("docs/quarantined-learnings.md")
        self.assertIn(
            "learning_status = observed | reproduced | quarantined | accepted | rejected | promoted",
            protocol,
        )
        self.assertIn(
            "This never advances `learning_status` by itself", protocol
        )

    def test_loop_upgrade_does_not_add_a_public_loop_skill(self):
        registry = json.loads(
            read("scripts/codex-hooks/groundwork_route_registry.json")
        )

        self.assertNotIn("loop", registry["public_routes"])
        self.assertNotIn("loop-me", registry["public_routes"])
        self.assertFalse((ROOT / "skills" / "loop").exists())
        self.assertFalse((ROOT / "skills" / "loop-me").exists())

    def test_prototype_no_delta_checker_rejects_automatic_retry(self):
        failures = loop_checks.prototype_no_delta_stop_failures(
            "I will continue automatically with the same probe until it looks better."
        )

        self.assertIn(
            "no-delta prototype iteration must stop or change hypothesis", failures
        )
        self.assertIn(
            "no-delta prototype iteration cannot continue automatically", failures
        )

    def test_prototype_checkpoint_rejects_automatic_probe_repeat(self):
        report = """Iteration Checkpoint
- Current Hypothesis: copy is too long
- Probe: render the empty state
- Observation: the action is obscured
- Evidence Delta Status: changed
- Evidence Delta: first browser observation
- Decision Delta Status: changed
- Decision Delta: shorten the copy
- Next Probe or Stop: propose_probe
- Proposed Probe: bounded copy probe
I will automatically repeat the probe.
"""

        self.assertIn(
            "prototype iteration cannot auto-run",
            loop_checks.prototype_iteration_checkpoint_failures(report),
        )

    def test_prototype_no_delta_checker_allows_explicit_automatic_stop(self):
        self.assertEqual(
            loop_checks.prototype_no_delta_stop_failures(
                "Stop here; do not continue automatically without new evidence."
            ),
            [],
        )

    def test_no_delta_checkers_allow_conditional_future_probe_after_new_delta(self):
        self.assertEqual(
            loop_checks.prototype_no_delta_stop_failures(
                "Stop here; rerun only after new evidence."
            ),
            [],
        )
        self.assertEqual(
            loop_checks.spec_no_delta_stop_failures(
                "Pause here; ask again only after a new decision delta."
            ),
            [],
        )

    def test_no_delta_checkers_reject_negated_stop_and_manual_continuation(self):
        cases = (
            (
                loop_checks.prototype_no_delta_stop_failures,
                "Do not stop; repeat the unchanged probe manually with no new evidence.",
                "no-delta prototype iteration cannot continue without new evidence",
            ),
            (
                loop_checks.spec_no_delta_stop_failures,
                "Do not stop; ask another equivalent question manually despite no decision delta.",
                "no-delta spec convergence cannot continue without a decision delta",
            ),
        )
        for checker, response, continuation_failure in cases:
            with self.subTest(checker=checker.__name__):
                failures = checker(response)
                self.assertTrue(any("must stop" in failure for failure in failures))
                self.assertIn(continuation_failure, failures)

    def test_no_delta_checkers_reject_stop_not_required_and_proceed(self):
        cases = (
            (
                loop_checks.prototype_no_delta_stop_failures,
                "Stop is not required; proceed with the same probe despite no new evidence.",
                "no-delta prototype iteration cannot continue without new evidence",
            ),
            (
                loop_checks.spec_no_delta_stop_failures,
                "Pause is not required; proceed with the same question despite no decision delta.",
                "no-delta spec convergence cannot continue without a decision delta",
            ),
        )
        for checker, response, continuation_failure in cases:
            with self.subTest(checker=checker.__name__):
                failures = checker(response)
                self.assertTrue(any("must stop" in failure for failure in failures))
                self.assertIn(continuation_failure, failures)

    def test_no_delta_runner_rows_reject_negated_stop(self):
        cases = (
            (
                "tf-loop-proto-002",
                "prototype",
                "Do not stop; repeat the unchanged probe manually with no new evidence.",
            ),
            (
                "tf-loop-spec-003",
                "to-prd",
                "Do not stop; ask another equivalent question manually despite no decision delta.",
            ),
        )
        for row_id, route, response in cases:
            with self.subTest(row_id=row_id):
                verdict = trace_verdict(row_id, route, response)
                self.assertEqual(verdict["output_contract_verdict"], "fail")
                self.assertEqual(verdict["overall_verdict"], "fail")

    def test_no_delta_phrase_alone_is_not_a_stop_signal(self):
        self.assertIn(
            "no-delta prototype iteration must stop or change hypothesis",
            loop_checks.prototype_no_delta_stop_failures("There is no new evidence."),
        )

    def test_prototype_iteration_checkpoint_checker_accepts_complete_delta(self):
        report = """Iteration Checkpoint
- Current Hypothesis: shorter copy exposes the primary action
- Probe: render the empty state with shorter copy
- Observation: the primary action remains visible
- Evidence Delta Status: changed
- Evidence Delta: new browser observation at 1280px
- Decision Delta Status: changed
- Decision Delta: reject the long-copy variant
- Next Probe or Stop: stop
- Stop Reason: the bounded question is answered
"""

        self.assertEqual(
            loop_checks.prototype_iteration_checkpoint_failures(report), []
        )

    def test_prototype_empty_evidence_delta_does_not_consume_next_field(self):
        report = """Iteration Checkpoint
- Current Hypothesis: shorter copy exposes the primary action
- Probe: render the empty state with shorter copy
- Observation: the primary action remains visible
- Evidence Delta Status: changed
- Evidence Delta:
- Decision Delta Status: changed
- Decision Delta: reject the long-copy variant
- Next Probe or Stop: stop
- Stop Reason: the bounded question is answered
"""

        self.assertIn(
            "Evidence Delta is missing or unresolved",
            loop_checks.prototype_iteration_checkpoint_failures(report),
        )

    def test_prototype_none_delta_statuses_must_stop(self):
        report = """Iteration Checkpoint
- Current Hypothesis: shorter copy exposes the primary action
- Probe: render the empty state with shorter copy
- Observation: the primary action remains visible
- Evidence Delta Status: none
- Evidence Delta: first browser observation
- Decision Delta Status: none
- Decision Delta: inspect the localized branch
- Next Probe or Stop: propose_probe
- Proposed Probe: one bounded branch probe
"""

        failures = loop_checks.prototype_iteration_checkpoint_failures(report)
        self.assertTrue(
            any("Evidence Delta Status" in failure and "stop" in failure for failure in failures)
        )
        self.assertIn(
            "Decision Delta with no change must stop or change hypothesis", failures
        )

    def test_prototype_delta_status_rejects_contradictory_details(self):
        changed_report = """Iteration Checkpoint
- Current Hypothesis: the branch is wrong
- Probe: inspect a trace
- Observation: output is unchanged
- Evidence Delta Status: changed
- Evidence Delta: identical to the last run
- Decision Delta Status: changed
- Decision Delta: nothing in the decision changed
- Next Probe or Stop: propose_probe
- Proposed Probe: inspect one bounded branch
"""
        changed_failures = loop_checks.prototype_iteration_checkpoint_failures(
            changed_report
        )
        self.assertIn("Evidence Delta contains no new evidence", changed_failures)
        self.assertIn(
            "Decision Delta Status changed requires a material decision delta",
            changed_failures,
        )

        synonym_report = changed_report.replace(
            "identical to the last run", "same outcome as the last run"
        ).replace(
            "nothing in the decision changed", "no material decision delta"
        )
        synonym_failures = loop_checks.prototype_iteration_checkpoint_failures(
            synonym_report
        )
        self.assertIn("Evidence Delta contains no new evidence", synonym_failures)
        self.assertIn(
            "Decision Delta Status changed requires a material decision delta",
            synonym_failures,
        )

        none_report = """Iteration Checkpoint
- Current Hypothesis: the branch is wrong
- Probe: inspect a trace
- Observation: trace localizes the branch
- Evidence Delta Status: none
- Evidence Delta: a new trace localizes the branch
- Decision Delta Status: none
- Decision Delta: route to implement
- Next Probe or Stop: stop
- Stop Reason: no bounded continuation is admitted
"""
        none_failures = loop_checks.prototype_iteration_checkpoint_failures(none_report)
        self.assertIn(
            "Evidence Delta Status none contradicts the delta detail", none_failures
        )
        self.assertIn(
            "Decision Delta Status none contradicts the delta detail", none_failures
        )
        self.assertIn(
            "Decision Delta Status none contradicts the delta detail",
            loop_checks.prototype_iteration_checkpoint_failures(
                none_report.replace("route to implement", "choose the implement route")
            ),
        )

    def test_prototype_checkpoint_allows_same_result_with_new_evidence(self):
        report = """Iteration Checkpoint
- Current Hypothesis: the branch is still wrong
- Probe: inspect a new browser trace
- Observation: the visible result is unchanged
- Evidence Delta Status: changed
- Evidence Delta: same result and same hypothesis but a new trace identifies the branch
- Decision Delta Status: changed
- Decision Delta: inspect that branch next
- Next Probe or Stop: propose_probe
- Proposed Probe: one bounded branch probe
"""

        self.assertEqual(
            loop_checks.prototype_iteration_checkpoint_failures(report), []
        )

    def test_prototype_checkpoint_rejects_execution_that_contradicts_control_state(self):
        cases = (
            """Iteration Checkpoint
- Current Hypothesis: the branch is wrong
- Probe: inspect a new trace
- Observation: the trace localizes the branch
- Evidence Delta Status: changed
- Evidence Delta: first localized trace
- Decision Delta Status: changed
- Decision Delta: inspect the localized branch next
- Next Probe or Stop: propose_probe
- Proposed Probe: inspect the localized branch
I will run that probe now.
""",
            """Iteration Checkpoint
- Current Hypothesis: the branch is wrong
- Probe: inspect a new trace
- Observation: the trace closes the question
- Evidence Delta Status: changed
- Evidence Delta: first closing trace
- Decision Delta Status: changed
- Decision Delta: close the branch question
- Next Probe or Stop: stop
- Stop Reason: run another probe immediately
""",
        )
        for report in cases:
            with self.subTest(report=report):
                self.assertTrue(
                    loop_checks.prototype_iteration_checkpoint_failures(report)
                )

    def test_prototype_checkpoint_does_not_treat_observation_as_control(self):
        report = """Iteration Checkpoint
- Current Hypothesis: carousel behavior is stable
- Probe: inspect hover recovery
- Observation: the carousel will continue automatically after hover ends
- Evidence Delta Status: changed
- Evidence Delta: first browser observation of recovery
- Decision Delta Status: changed
- Decision Delta: accept the recovery behavior
- Next Probe or Stop: stop
- Stop Reason: bounded behavior question is answered
"""

        self.assertEqual(
            loop_checks.prototype_iteration_checkpoint_failures(report), []
        )

    def test_prototype_checkpoint_requires_heading(self):
        report = """- Current Hypothesis: branch is wrong
- Probe: inspect trace
- Observation: branch identified
- Evidence Delta Status: changed
- Evidence Delta: first trace
- Decision Delta Status: changed
- Decision Delta: inspect branch
- Next Probe or Stop: stop
- Stop Reason: question answered
"""

        self.assertIn(
            "Iteration Checkpoint must appear exactly once",
            loop_checks.prototype_iteration_checkpoint_failures(report),
        )

    def test_prototype_companion_fields_must_stay_inside_checkpoint(self):
        report = """Iteration Checkpoint
- Current Hypothesis: shorter copy exposes the primary action
- Probe: render the empty state
- Observation: the primary action is visible
- Evidence Delta Status: changed
- Evidence Delta: first browser observation
- Decision Delta Status: changed
- Decision Delta: accept the shorter copy
- Next Probe or Stop: stop
- Stop Reason: the bounded question is answered
## Later
- Proposed Probe: run another visual probe next week
"""

        failures = loop_checks.prototype_iteration_checkpoint_failures(report)
        self.assertIn(
            "Proposed Probe must appear only inside Iteration Checkpoint", failures
        )
        verdict = trace_verdict("tf-loop-proto-001", "prototype", report)
        self.assertEqual(verdict["output_contract_verdict"], "fail")
        self.assertEqual(verdict["overall_verdict"], "fail")

    def test_prototype_checkpoint_no_decision_delta_must_stop(self):
        report = """Iteration Checkpoint
- Current Hypothesis: copy is too long
- Probe: render the empty state
- Observation: the action is visible
- Evidence Delta Status: changed
- Evidence Delta: new browser observation
- Decision Delta Status: none
- Decision Delta: no decision delta
- Next Probe or Stop: propose_probe
- Proposed Probe: another bounded probe
"""

        self.assertIn(
            "Decision Delta with no change must stop or change hypothesis",
            loop_checks.prototype_iteration_checkpoint_failures(report),
        )
        stopped = report.replace(
            "Next Probe or Stop: propose_probe\n- Proposed Probe: another bounded probe",
            "Next Probe or Stop: stop\n- Stop Reason: change hypothesis before another probe",
        )
        self.assertEqual(
            loop_checks.prototype_iteration_checkpoint_failures(stopped), []
        )

    def test_prototype_checkpoint_rejects_unchanged_delta_aliases(self):
        report = """Iteration Checkpoint
- Current Hypothesis: the branch is wrong
- Probe: inspect the same trace
- Observation: result is unchanged
- Evidence Delta Status: changed
- Evidence Delta: unchanged
- Decision Delta Status: none
- Decision Delta: unchanged from before
- Next Probe or Stop: propose_probe
- Proposed Probe: inspect the branch again
"""

        failures = loop_checks.prototype_iteration_checkpoint_failures(report)
        self.assertIn("Evidence Delta contains no new evidence", failures)
        self.assertIn(
            "Decision Delta with no change must stop or change hypothesis", failures
        )

    def test_prototype_checkpoint_rejects_repeated_observation_as_fake_delta(self):
        report = """Iteration Checkpoint
- Current Hypothesis: unchanged
- Probe: repeat prior probe
- Observation: same result
- Evidence Delta Status: changed
- Evidence Delta: the prior observation repeated
- Decision Delta Status: none
- Decision Delta: continue
- Next Probe or Stop: run the same probe now
"""

        failures = loop_checks.prototype_iteration_checkpoint_failures(report)
        self.assertIn("Evidence Delta contains no new evidence", failures)
        self.assertIn(
            "Decision Delta with no change must stop or change hypothesis", failures
        )

        verdict = trace_verdict("tf-loop-proto-001", "prototype", report)
        self.assertEqual(verdict["output_contract_verdict"], "fail")
        self.assertEqual(verdict["overall_verdict"], "fail")

    def test_prototype_checkpoint_rejects_fields_repeated_as_fake_deltas(self):
        report = """Iteration Checkpoint
- Current Hypothesis: the filter branch is wrong
- Probe: repeat prior probe
- Observation: same result
- Evidence Delta Status: changed
- Evidence Delta: same result
- Decision Delta Status: changed
- Decision Delta: the filter branch is wrong
- Next Probe or Stop: stop
- Stop Reason: bounded question is closed
"""

        failures = loop_checks.prototype_iteration_checkpoint_failures(report)
        self.assertIn("Evidence Delta must not repeat Observation", failures)
        self.assertIn("Decision Delta must not repeat Current Hypothesis", failures)

        verdict = trace_verdict("tf-loop-proto-001", "prototype", report)
        self.assertEqual(verdict["output_contract_verdict"], "fail")
        self.assertEqual(verdict["overall_verdict"], "fail")

    def test_prototype_checkpoint_rejects_same_result_even_when_observation_differs(self):
        report = """Iteration Checkpoint
- Current Hypothesis: the filter branch is wrong
- Probe: repeat prior probe
- Observation: the filter still returns all rows
- Evidence Delta Status: changed
- Evidence Delta: same result
- Decision Delta Status: changed
- Decision Delta: stop until a new trace exists
- Next Probe or Stop: stop
- Stop Reason: bounded question is closed
"""

        self.assertIn(
            "Evidence Delta contains no new evidence",
            loop_checks.prototype_iteration_checkpoint_failures(report),
        )

    def test_prototype_checkpoint_rejects_duplicate_delta_fields(self):
        report = """Iteration Checkpoint
- Current Hypothesis: the filter branch is wrong
- Probe: inspect a new trace
- Observation: the filter still returns all rows
- Evidence Delta Status: changed
- Evidence Delta: new trace localizes the branch
- Evidence Delta Status: changed
- Evidence Delta: no new evidence
- Decision Delta Status: changed
- Decision Delta: inspect the localized branch
- Next Probe or Stop: stop
- Stop Reason: bounded question is closed
"""

        self.assertIn(
            "Evidence Delta must appear exactly once",
            loop_checks.prototype_iteration_checkpoint_failures(report),
        )
        verdict = trace_verdict("tf-loop-proto-001", "prototype", report)
        self.assertEqual(verdict["output_contract_verdict"], "fail")
        self.assertEqual(verdict["overall_verdict"], "fail")

    def test_prototype_checkpoint_rejects_repeat_and_unchanged_hypothesis_language(self):
        report = """Iteration Checkpoint
- Current Hypothesis: the filter branch is wrong
- Probe: repeat the prior probe
- Observation: the filter still returns all rows
- Evidence Delta Status: changed
- Evidence Delta: a repeat of the previous result
- Decision Delta Status: none
- Decision Delta: the hypothesis remains unchanged
- Next Probe or Stop: proceed with the same probe
"""

        failures = loop_checks.prototype_iteration_checkpoint_failures(report)
        self.assertIn("Evidence Delta contains no new evidence", failures)
        self.assertIn(
            "Decision Delta with no change must stop or change hypothesis", failures
        )

    def test_prototype_checkpoint_rejects_natural_no_decision_delta(self):
        cases = (
            ("there is no decision delta", "proceed with another probe"),
            ("unchanged", "continue with the same probe"),
            ("repeat", "continue with the same probe"),
            (
                "there is no decision delta",
                "stop briefly, then continue with the same probe",
            ),
        )
        for decision_delta, next_probe in cases:
            with self.subTest(
                decision_delta=decision_delta, next_probe=next_probe
            ):
                report = f"""Iteration Checkpoint
- Current Hypothesis: the filter branch is wrong
- Probe: repeat the prior probe
- Observation: the filter still returns all rows
- Evidence Delta Status: changed
- Evidence Delta: a new trace confirms the same branch
- Decision Delta Status: none
- Decision Delta: {decision_delta}
- Next Probe or Stop: {next_probe}
"""

                self.assertIn(
                    "Decision Delta with no change must stop or change hypothesis",
                    loop_checks.prototype_iteration_checkpoint_failures(report),
                )
                verdict = trace_verdict("tf-loop-proto-001", "prototype", report)
                self.assertEqual(verdict["output_contract_verdict"], "fail")
                self.assertEqual(verdict["overall_verdict"], "fail")

    def test_prototype_one_shot_checker_rejects_iteration_scaffolding(self):
        self.assertEqual(
            loop_checks.prototype_one_shot_failures(
                "The state table answers the question. Next Route: cleanup."
            ),
            [],
        )
        self.assertIn(
            "one-shot prototype must not emit empty iteration scaffolding",
            loop_checks.prototype_one_shot_failures(
                "Iteration Checkpoint\n- Current Hypothesis:\nNext Route: cleanup"
            ),
        )
        self.assertEqual(
            loop_checks.prototype_one_shot_failures(
                "No Iteration Checkpoint is needed; cleanup."
            ),
            [],
        )

    def test_spec_no_delta_checker_rejects_endless_grilling(self):
        failures = loop_checks.spec_no_delta_stop_failures(
            "Keep asking philosophical questions until every imaginable unknown is gone."
        )

        self.assertIn("no-delta spec convergence must stop or pause", failures)
        self.assertIn(
            "spec convergence cannot continue until all unknowns disappear", failures
        )

    def test_spec_contract_checkers_accept_bounded_outputs(self):
        self.assertEqual(
            loop_checks.spec_single_question_failures(
                "Question: Which SLA applies to this incident workflow?\n"
                "Impact / Next route: The answer determines the acceptance boundary "
                "before to-prd can continue."
            ),
            [],
        )

    def test_spec_writeback_rejects_preserved_stale_question(self):
        report = """Spec Convergence Checkpoint
- Decision Delta Status: changed
- Decision Delta: trigger accepted
- Canonical Update Status: updated
- Canonical Update: trigger is a new P1 incident event
- Resolved / Removed: kept trigger unresolved
- Next Route or Question: route
- Next Route: to-issues
"""

        self.assertIn(
            "Resolved / Removed must not preserve the answered item as unresolved",
            loop_checks.spec_writeback_failures(report),
        )
        self.assertEqual(
            loop_checks.spec_writeback_failures(
                """Spec Convergence Checkpoint
- Decision Delta Status: changed
- Decision Delta: trigger accepted
- Canonical Update Status: updated
- Canonical Update: trigger is a new P1 incident event
- Resolved / Removed: removed trigger from open questions
- Next Route or Question: route
- Next Route: to-issues
"""
            ),
            [],
        )

    def test_spec_writeback_requires_finite_delta_status_tokens(self):
        report = """Spec Convergence Checkpoint
- Decision Delta Status: none
- Decision Delta: trigger accepted
- Canonical Update Status: pending
- Canonical Update: trigger is a new P1 incident event
- Resolved / Removed: removed trigger from open questions
- Next Route or Question: route
- Next Route: to-issues
"""

        failures = loop_checks.spec_writeback_failures(report)
        self.assertIn("Decision Delta Status must be changed", failures)
        self.assertIn("Canonical Update Status must be updated", failures)

    def test_spec_writeback_rejects_status_detail_contradictions(self):
        report = """Spec Convergence Checkpoint
- Decision Delta Status: changed
- Decision Delta: nothing in the decision changed
- Canonical Update Status: updated
- Canonical Update: kept the canonical draft as-is
- Resolved / Removed: removed trigger from open questions
- Next Route or Question: route
- Next Route: to-issues
"""

        failures = loop_checks.spec_writeback_failures(report)
        self.assertIn("Decision Delta must name the accepted material change", failures)
        self.assertIn(
            "Canonical Update must write the accepted answer into current state",
            failures,
        )
        synonym_failures = loop_checks.spec_writeback_failures(
            report.replace(
                "nothing in the decision changed", "no material decision delta"
            ).replace(
                "kept the canonical draft as-is", "left the canonical state alone"
            )
        )
        self.assertIn(
            "Decision Delta must name the accepted material change", synonym_failures
        )
        self.assertIn(
            "Canonical Update must write the accepted answer into current state",
            synonym_failures,
        )

    def test_spec_companion_fields_must_stay_inside_checkpoint(self):
        report = """Spec Convergence Checkpoint
- Decision Delta Status: changed
- Decision Delta: trigger accepted
- Canonical Update Status: updated
- Canonical Update: trigger is a new P1 incident event
- Resolved / Removed: removed trigger from open questions
- Next Route or Question: route
- Next Route: to-issues
## Later
- Stop Reason: pause for a human decision
"""

        failures = loop_checks.spec_writeback_failures(report)
        self.assertIn(
            "Stop Reason must appear only inside Spec Convergence Checkpoint", failures
        )
        verdict = trace_verdict("tf-loop-spec-002", "to-prd", report)
        self.assertEqual(verdict["output_contract_verdict"], "fail")
        self.assertEqual(verdict["overall_verdict"], "fail")

    def test_spec_empty_canonical_update_does_not_consume_next_field(self):
        report = """Spec Convergence Checkpoint
- Decision Delta Status: changed
- Decision Delta: trigger accepted
- Canonical Update Status: updated
- Canonical Update:
- Resolved / Removed: removed trigger from open questions
- Next Route or Question: route
- Next Route: to-issues
"""

        self.assertIn(
            "Canonical Update is missing or unresolved",
            loop_checks.spec_writeback_failures(report),
        )

    def test_spec_writeback_rejects_removed_nothing_and_still_open(self):
        stale_values = (
            "removed nothing; trigger is still an open blocking question",
            "resolved nothing",
            "did not remove the trigger question",
            "kept the trigger as a blocking question",
        )
        for stale_value in stale_values:
            with self.subTest(stale_value=stale_value):
                report = f"""Spec Convergence Checkpoint
- Decision Delta Status: changed
- Decision Delta: trigger accepted
- Canonical Update Status: updated
- Canonical Update: trigger is a new P1 incident event
- Resolved / Removed: {stale_value}
- Next Route or Question: route
- Next Route: to-issues
"""

                self.assertIn(
                    "Resolved / Removed must not preserve the answered item as unresolved",
                    loop_checks.spec_writeback_failures(report),
                )
                verdict = trace_verdict("tf-loop-spec-002", "to-prd", report)
                self.assertEqual(verdict["output_contract_verdict"], "fail")
                self.assertEqual(verdict["overall_verdict"], "fail")

    def test_spec_writeback_allows_explicitly_closed_open_state(self):
        report = """Spec Convergence Checkpoint
- Decision Delta Status: changed
- Decision Delta: trigger accepted
- Canonical Update Status: updated
- Canonical Update: trigger is a new P1 incident event
- Resolved / Removed: removed the trigger; there remains no open question
- Next Route or Question: route
- Next Route: to-issues
"""

        self.assertEqual(loop_checks.spec_writeback_failures(report), [])
        self.assertEqual(
            loop_checks.spec_no_delta_stop_failures(
                "Pause: no new evidence. Change hypothesis before another question."
            ),
            [],
        )
        self.assertEqual(
            loop_checks.spec_clear_fast_path_failures(
                "Next Route: to-issues", "to-issues"
            ),
            [],
        )
        self.assertEqual(
            loop_checks.spec_gap_list_failures("1. Owner?\n2. Trigger?\n3. Evidence?"),
            [],
        )

    def test_spec_writeback_rejects_no_delta_and_no_canonical_update(self):
        report = """Spec Convergence Checkpoint
- Decision Delta Status: changed
- Decision Delta: no decision delta
- Canonical Update Status: updated
- Canonical Update: no canonical update
- Resolved / Removed: removed trigger from open questions
- Next Route or Question: route
- Next Route: to-issues
"""

        failures = loop_checks.spec_writeback_failures(report)
        self.assertIn("Decision Delta must name the accepted material change", failures)
        self.assertIn(
            "Canonical Update must write the accepted answer into current state",
            failures,
        )
        self.assertEqual(
            loop_checks.checkpoint_before_risky_action_failures(
                self._risk_checkpoint()
            ),
            [],
        )

    def test_spec_writeback_rejects_unchanged_aliases_and_extra_question(self):
        report = """Spec Convergence Checkpoint
- Decision Delta Status: changed
- Decision Delta: same as before
- Canonical Update Status: updated
- Canonical Update: unchanged
- Resolved / Removed: removed trigger from open questions
- Next Route or Question: route
- Next Route: to-issues
Should we also change the SLA?
"""

        failures = loop_checks.spec_writeback_failures(report)
        self.assertIn("Decision Delta must name the accepted material change", failures)
        self.assertIn(
            "Canonical Update must write the accepted answer into current state",
            failures,
        )
        self.assertIn(
            "spec write-back control prose must not ask an extra question", failures
        )

    def test_spec_writeback_rejects_deferred_canonical_update(self):
        report = """Spec Convergence Checkpoint
- Decision Delta Status: changed
- Decision Delta: trigger accepted
- Canonical Update Status: updated
- Canonical Update: the canonical state will remain unchanged until a later session
- Resolved / Removed: resolved the trigger question
- Next Route or Question: route
- Next Route: to-issues
"""

        self.assertIn(
            "Canonical Update must write the accepted answer into current state",
            loop_checks.spec_writeback_failures(report),
        )
        verdict = trace_verdict("tf-loop-spec-002", "to-prd", report)
        self.assertEqual(verdict["output_contract_verdict"], "fail")
        self.assertEqual(verdict["overall_verdict"], "fail")

    def test_spec_writeback_rejects_pending_or_duplicate_canonical_state(self):
        reports = (
            """Spec Convergence Checkpoint
- Decision Delta Status: changed
- Decision Delta: trigger accepted
- Canonical Update Status: updated
- Canonical Update: deferred pending owner sign-off
- Resolved / Removed: resolved the trigger question
- Next Route or Question: route
- Next Route: to-issues
""",
            """Spec Convergence Checkpoint
- Decision Delta Status: changed
- Decision Delta: trigger accepted
- Canonical Update Status: updated
- Canonical Update: trigger is a new P1 incident event
- Canonical Update Status: updated
- Canonical Update: deferred pending owner sign-off
- Resolved / Removed: resolved the trigger question
- Resolved / Removed: trigger is still open
- Next Route or Question: route
- Next Route: to-issues
""",
        )
        for report in reports:
            with self.subTest(report=report):
                failures = loop_checks.spec_writeback_failures(report)
                self.assertTrue(
                    any(
                        failure
                        in {
                            "Canonical Update must write the accepted answer into current state",
                            "Canonical Update must appear exactly once",
                            "Resolved / Removed must appear exactly once",
                        }
                        for failure in failures
                    )
                )
                verdict = trace_verdict("tf-loop-spec-002", "to-prd", report)
                self.assertEqual(verdict["output_contract_verdict"], "fail")
                self.assertEqual(verdict["overall_verdict"], "fail")

    def test_spec_writeback_rejects_natural_no_decision_delta(self):
        report = """Spec Convergence Checkpoint
- Decision Delta Status: changed
- Decision Delta: there is no decision delta
- Canonical Update Status: updated
- Canonical Update: trigger is a new P1 incident event
- Resolved / Removed: resolved the trigger question
- Next Route or Question: route
- Next Route: to-issues
"""

        self.assertIn(
            "Decision Delta must name the accepted material change",
            loop_checks.spec_writeback_failures(report),
        )
        verdict = trace_verdict("tf-loop-spec-002", "to-prd", report)
        self.assertEqual(verdict["output_contract_verdict"], "fail")
        self.assertEqual(verdict["overall_verdict"], "fail")

    def test_spec_writeback_rejects_deferred_canonical_state_phrases(self):
        for canonical_update in (
            "the canonical update is deferred pending owner sign-off",
            "the canonical state is pending owner sign-off",
        ):
            with self.subTest(canonical_update=canonical_update):
                report = f"""Spec Convergence Checkpoint
- Decision Delta Status: changed
- Decision Delta: trigger accepted
- Canonical Update Status: updated
- Canonical Update: {canonical_update}
- Resolved / Removed: resolved the trigger question
- Next Route or Question: route
- Next Route: to-issues
"""

                self.assertIn(
                    "Canonical Update must write the accepted answer into current state",
                    loop_checks.spec_writeback_failures(report),
                )
                verdict = trace_verdict("tf-loop-spec-002", "to-prd", report)
                self.assertEqual(verdict["output_contract_verdict"], "fail")
                self.assertEqual(verdict["overall_verdict"], "fail")

    def test_spec_writeback_rejects_bare_unresolved_state(self):
        report = """Spec Convergence Checkpoint
- Decision Delta Status: changed
- Decision Delta: trigger accepted
- Canonical Update Status: updated
- Canonical Update: trigger is a new P1 incident event
- Resolved / Removed: trigger is unresolved
- Next Route or Question: route
- Next Route: to-issues
"""

        self.assertIn(
            "Resolved / Removed must not preserve the answered item as unresolved",
            loop_checks.spec_writeback_failures(report),
        )
        verdict = trace_verdict("tf-loop-spec-002", "to-prd", report)
        self.assertEqual(verdict["output_contract_verdict"], "fail")
        self.assertEqual(verdict["overall_verdict"], "fail")

    def test_spec_writeback_allows_no_longer_open_language(self):
        report = """Spec Convergence Checkpoint
- Decision Delta Status: changed
- Decision Delta: trigger accepted
- Canonical Update Status: updated
- Canonical Update: trigger is a new P1 incident event
- Resolved / Removed: resolved the trigger; it no longer remains an open question
- Next Route or Question: route
- Next Route: to-issues
"""

        self.assertEqual(loop_checks.spec_writeback_failures(report), [])

    def test_spec_writeback_allows_is_no_longer_open_language(self):
        report = """Spec Convergence Checkpoint
- Decision Delta Status: changed
- Decision Delta: trigger accepted
- Canonical Update Status: updated
- Canonical Update: trigger is a new P1 incident event
- Resolved / Removed: trigger is no longer open
- Next Route or Question: route
- Next Route: to-issues
"""

        self.assertEqual(loop_checks.spec_writeback_failures(report), [])
        verdict = trace_verdict("tf-loop-spec-002", "to-prd", report)
        self.assertEqual(verdict["output_contract_verdict"], "pass")
        self.assertEqual(verdict["overall_verdict"], "pass")

    def test_spec_writeback_allows_bare_no_longer_open_language(self):
        report = """Spec Convergence Checkpoint
- Decision Delta Status: changed
- Decision Delta: trigger accepted
- Canonical Update Status: updated
- Canonical Update: trigger is a new P1 incident event
- Resolved / Removed: trigger no longer open
- Next Route or Question: route
- Next Route: to-issues
"""

        self.assertEqual(loop_checks.spec_writeback_failures(report), [])
        verdict = trace_verdict("tf-loop-spec-002", "to-prd", report)
        self.assertEqual(verdict["output_contract_verdict"], "pass")
        self.assertEqual(verdict["overall_verdict"], "pass")

    def test_spec_writeback_rejects_continuation_that_contradicts_stop(self):
        report = """Spec Convergence Checkpoint
- Decision Delta Status: changed
- Decision Delta: trigger accepted
- Canonical Update Status: updated
- Canonical Update: trigger is a new P1 incident event
- Resolved / Removed: removed trigger from open questions
- Next Route or Question: stop
- Stop Reason: the material question is answered
Continue with the same question now.
"""

        self.assertIn(
            "spec convergence cannot continue immediately from write-back",
            loop_checks.spec_writeback_failures(report),
        )

    def test_spec_writeback_does_not_treat_canonical_fact_as_control(self):
        report = """Spec Convergence Checkpoint
- Decision Delta Status: changed
- Decision Delta: recovery behavior accepted
- Canonical Update Status: updated
- Canonical Update: after recovery the workflow will continue automatically
- Resolved / Removed: removed recovery behavior from open questions
- Next Route or Question: route
- Next Route: to-issues
"""

        self.assertEqual(loop_checks.spec_writeback_failures(report), [])

    def test_spec_writeback_requires_heading(self):
        report = """- Decision Delta Status: changed
- Decision Delta: trigger accepted
- Canonical Update Status: updated
- Canonical Update: trigger is a new P1 incident event
- Resolved / Removed: removed trigger from open questions
- Next Route or Question: route
- Next Route: to-issues
"""

        self.assertIn(
            "Spec Convergence Checkpoint must appear exactly once",
            loop_checks.spec_writeback_failures(report),
        )

    def test_spec_single_question_checker_counts_mixed_question_shapes(self):
        failures = loop_checks.spec_single_question_failures(
            "Question: Who owns the workflow\nQuestion: What event triggers it?"
        )

        self.assertIn(
            "spec convergence must ask exactly one question; found 2",
            failures,
        )

    def test_spec_single_question_checker_requires_explicit_impact(self):
        self.assertIn(
            "spec convergence must name a non-empty Impact / Next route",
            loop_checks.spec_single_question_failures(
                "Question: When is lunch?"
            ),
        )

    def test_spec_single_question_checker_does_not_guess_materiality_from_keywords(self):
        self.assertEqual(
            loop_checks.spec_single_question_failures(
                "Question: Which SLA applies to this incident workflow?\n"
                "Impact / Next route: The answer changes the evidence boundary for verify."
            ),
            [],
        )

    def test_spec_clear_fast_path_checker_rejects_wrong_route(self):
        self.assertIn(
            "clear recurring spec must route to to-issues, not to-prd",
            loop_checks.spec_clear_fast_path_failures(
                "Next Route: to-prd", "to-issues"
            ),
        )

    def test_spec_gap_list_checker_rejects_more_than_five_questions(self):
        failures = loop_checks.spec_gap_list_failures(
            "1?\n2?\n3?\n4?\n5?\n6?"
        )

        self.assertIn(
            "explicit non-interactive gap list must contain 1-5 questions; found 6",
            failures,
        )

    def test_risky_checkpoint_requires_exact_control_tokens(self):
        cases = (
            ("Action Kind: data_mutation", "Action Kind: read_only", "Action Kind must be data_mutation"),
            ("Target Kind: data_store", "Target Kind: source_code", "Target Kind must be data_store"),
            ("Approval Needed: yes", "Approval Needed: no", "Approval Needed must be yes"),
            ("Approval Status: pending", "Approval Status: granted", "Approval Status must be pending"),
            ("Action State: blocked", "Action State: proceed", "Action State must be blocked"),
            ("Checkpoint Position: before_action", "Checkpoint Position: after_action", "Checkpoint Position must be before_action"),
        )
        for old, new, expected in cases:
            with self.subTest(new=new):
                failures = loop_checks.checkpoint_before_risky_action_failures(
                    self._risk_checkpoint().replace(old, new)
                )
                self.assertIn(expected, failures)

    def test_risky_checkpoint_accepts_canonical_block(self):
        response = self._risk_checkpoint()

        self.assertEqual(
            loop_checks.checkpoint_before_risky_action_failures(response), []
        )
        verdict = trace_verdict("tf-loop-spec-004", "to-prd", response)
        self.assertEqual(verdict["output_contract_verdict"], "pass")
        self.assertEqual(verdict["overall_verdict"], "pass")

    def test_risky_checkpoint_rejects_contradictory_execution(self):
        cases = (
            "The production database can be updated now.",
            "We can proceed with it now.",
            "I will begin the migration now.",
            "We can update the database now.",
        )
        for claim in cases:
            with self.subTest(claim=claim):
                response = self._risk_checkpoint(tail=claim)
                self.assertIn(
                    "Risky Action Checkpoint cannot claim execution while Action State is blocked",
                    loop_checks.checkpoint_before_risky_action_failures(response),
                )
                verdict = trace_verdict("tf-loop-spec-004", "to-prd", response)
                self.assertEqual(verdict["output_contract_verdict"], "fail")
                self.assertEqual(verdict["overall_verdict"], "fail")

    def test_risky_checkpoint_rejects_contrast_clause_bypasses(self):
        cases = (
            "After approval is granted, the migration may run, but we can update it now.",
            "Do not update the production database, but update it now.",
        )
        for claim in cases:
            with self.subTest(claim=claim):
                self.assertIn(
                    "Risky Action Checkpoint cannot claim execution while Action State is blocked",
                    loop_checks.checkpoint_before_risky_action_failures(
                        self._risk_checkpoint(tail=claim)
                    ),
                )

    def test_risky_checkpoint_rejects_immediate_proposed_action(self):
        response = self._risk_checkpoint().replace(
            "Proposed Action: update one production data row",
            "Proposed Action: update one production data row now",
        )

        self.assertIn(
            "Risky Action Checkpoint cannot claim execution while Action State is blocked",
            loop_checks.checkpoint_before_risky_action_failures(response),
        )

    def test_risky_checkpoint_rejects_execution_hidden_in_rollback(self):
        response = self._risk_checkpoint(
            rollback="we write the production database now"
        )

        self.assertIn(
            "Risky Action Checkpoint cannot claim execution while Action State is blocked",
            loop_checks.checkpoint_before_risky_action_failures(response),
        )

    def test_risky_checkpoint_rejects_completed_execution_in_detail_fields(self):
        cases = (
            (
                "Proposed Action: update one production data row",
                "Proposed Action: the production migration finished successfully",
            ),
            (
                "Proposed Action: update one production data row",
                "Proposed Action: the production migration ran successfully",
            ),
            (
                "Proposed Action: update one production data row",
                "Proposed Action: the production migration has shipped",
            ),
            (
                "Proposed Action: update one production data row",
                "Proposed Action: the production migration is done",
            ),
            (
                "Target: production database",
                "Target: the PostgreSQL primary was changed",
            ),
            (
                "Target: production database",
                "Target: the PostgreSQL primary was modified",
            ),
            (
                "Target: production database",
                "Target: production database is mutated",
            ),
            (
                "Risk: customer-visible data mutation",
                "Risk: customer rows were changed in production",
            ),
            (
                "Risk: customer-visible data mutation",
                "Risk: customer records have been altered",
            ),
            (
                "Rollback/Undo: restore the prior snapshot",
                "Rollback/Undo: restore after the write finished",
            ),
        )
        for old, new in cases:
            with self.subTest(new=new):
                failures = loop_checks.checkpoint_before_risky_action_failures(
                    self._risk_checkpoint().replace(old, new)
                )
                self.assertTrue(
                    any("cannot claim completed execution" in failure for failure in failures)
                )

    def test_risky_checkpoint_rejects_extra_conditional_prose(self):
        response = self._risk_checkpoint(
            tail="After approval is granted, we can update the production database."
        )

        self.assertIn(
            "Risky Action Checkpoint must contain only structured fields",
            loop_checks.checkpoint_before_risky_action_failures(response),
        )

    def test_risky_checkpoint_empty_risk_does_not_consume_rollback_field(self):
        response = self._risk_checkpoint().replace(
            "Risk: customer-visible data mutation", "Risk:"
        )

        self.assertIn(
            "Risk is missing or unresolved",
            loop_checks.checkpoint_before_risky_action_failures(response),
        )

    def test_risky_checkpoint_rejects_arbitrary_tail_prose(self):
        response = self._risk_checkpoint(tail="This is only a planning note.")

        self.assertIn(
            "Risky Action Checkpoint must contain only structured fields",
            loop_checks.checkpoint_before_risky_action_failures(response),
        )

    def test_risky_checkpoint_rejects_reserved_fields_outside_block(self):
        response = self._risk_checkpoint() + """## Later
- Approval Status: granted
- Action State: proceed
"""

        failures = loop_checks.checkpoint_before_risky_action_failures(response)
        self.assertIn(
            "Risky Action Checkpoint output must not contain extra prose or sections",
            failures,
        )
        self.assertIn(
            "Approval Status must appear only inside Risky Action Checkpoint",
            failures,
        )
        self.assertIn(
            "Action State must appear only inside Risky Action Checkpoint",
            failures,
        )

    def test_risky_checkpoint_requires_heading_and_block(self):
        response = self._risk_checkpoint().replace("Risky Action Checkpoint\n", "")

        self.assertIn(
            "Risky Action Checkpoint must appear exactly once",
            loop_checks.checkpoint_before_risky_action_failures(response),
        )

    def test_qa_gap_closure_runner_rejects_broad_scope_and_late_execution(self):
        response = """Verification Scope
- Claim: failed filter can enter bounded remediation
- Covered: supplied failure package
- Missing: none
- Verdict: fail
QA Failure
- Expected: filtered result
- Actual: unfiltered result
- Reproduction: command: node test/taskSearch.test.mjs
- Severity: P1
- Minimal Diagnosis: filter is not applied
- Evidence Delta: first observed failure
- Source / AC Change: unchanged
- Implementation Authority: existing_and_sufficient
- Risk Change: unchanged_within_boundary
- Fix Plan: rewrite every module in the system
- Gap-Closure Admission: ready_for_implement
- Gap Closure Plan: change every file in the repository and rerun the check
- Re-QA Required: command: node test/taskSearch.test.mjs
- Regression Note: adjacent status filter
- Scoped Next Action: route: implement
I am invoking implement now.
"""

        verdict = trace_verdict("tf-vr-004", "verify", response)
        self.assertEqual(verdict["output_contract_verdict"], "fail")
        self.assertEqual(verdict["overall_verdict"], "fail")

    def test_qa_gap_closure_runner_rejects_multiline_scope_escape(self):
        response = """Verification Scope
- Claim: failed filter can enter bounded remediation
- Covered: supplied failure package
- Missing: none
- Verdict: fail
QA Failure
- Expected: filtered result
- Actual: unfiltered result
- Reproduction: command: node test/taskSearch.test.mjs
- Severity: P1
- Minimal Diagnosis: filter is not applied
- Evidence Delta: first observed failure
- Source / AC Change: unchanged
- Implementation Authority: existing_and_sufficient
- Risk Change: unchanged_within_boundary
- Fix Plan: change the filter only
  Then rewrite every module in the system.
- Gap-Closure Admission: ready_for_implement
- Gap Closure Plan: change only the phone filter and rerun the original check
  Then change every file in the repository.
- Re-QA Required: command: node test/taskSearch.test.mjs
- Regression Note: adjacent status filter
- Scoped Next Action: route: implement
I patched the filter and rewrote every module now.
"""

        verdict = trace_verdict("tf-vr-004", "verify", response)
        self.assertEqual(verdict["output_contract_verdict"], "fail")
        self.assertEqual(verdict["overall_verdict"], "fail")

    def test_qa_gap_closure_runner_rejects_duplicate_decision_fields(self):
        base = """Verification Scope
- Claim: failed filter can enter bounded remediation
- Covered: supplied failure package
- Missing: none
- Verdict: fail
QA Failure
- Expected: filtered result
- Actual: unfiltered result
- Reproduction: command: node test/taskSearch.test.mjs
- Severity: P1
- Minimal Diagnosis: filter is not applied
- Evidence Delta: first observed failure
- Source / AC Change: unchanged
- Implementation Authority: existing_and_sufficient
- Risk Change: unchanged_within_boundary
- Fix Plan: change the filter only
- Gap-Closure Admission: ready_for_implement
- Gap Closure Plan: change only the phone filter and rerun the original check
- Re-QA Required: command: node test/taskSearch.test.mjs
- Regression Note: adjacent status filter
- Scoped Next Action: route: implement
"""
        responses = (
            base.replace(
                "- Source / AC Change: unchanged",
                "- Evidence Delta: no new evidence\n- Source / AC Change: unchanged",
            ),
            base.replace(
                "- Gap Closure Plan:",
                "- Gap-Closure Admission: needs_info\n- Gap Closure Plan:",
            ),
        )
        for response in responses:
            with self.subTest(response=response):
                verdict = trace_verdict("tf-vr-004", "verify", response)
                self.assertEqual(verdict["output_contract_verdict"], "fail")
                self.assertEqual(verdict["overall_verdict"], "fail")

    def test_qa_gap_closure_runner_allows_scope_verdict_and_exact_qa_fields(self):
        response = """Verification Scope
- Claim: failed filter can enter bounded remediation
- Covered: supplied failure package
- Missing: none
- Verdict: fail
QA Failure
- Expected: filtered result
- Actual: unfiltered result
- Reproduction: command: node test/taskSearch.test.mjs
- Severity: P1
- Minimal Diagnosis: filter is not applied
- Evidence Delta: first observed failure
- Source / AC Change: unchanged
- Implementation Authority: existing_and_sufficient
- Risk Change: unchanged_within_boundary
- Fix Plan: change the filter only
- Gap-Closure Admission: ready_for_implement
- Gap Closure Plan: change only the phone filter and rerun the original check
- Re-QA Required: command: node test/taskSearch.test.mjs
- Regression Note: adjacent status filter
- Scoped Next Action: route: implement
"""

        verdict = trace_verdict("tf-vr-004", "verify", response)
        self.assertEqual(verdict["output_contract_verdict"], "pass")
        self.assertEqual(verdict["overall_verdict"], "pass")

    def test_qa_gap_closure_runner_requires_explicit_qa_failure_block(self):
        response = """Verification Scope
- Claim: failed filter can enter bounded remediation
- Covered: supplied failure package
- Missing: none
- Verdict: fail
- Expected: filtered result
- Actual: unfiltered result
- Reproduction: command: node test/taskSearch.test.mjs
- Severity: P1
- Minimal Diagnosis: filter is not applied
- Evidence Delta: first observed failure
- Source / AC Change: unchanged
- Implementation Authority: existing_and_sufficient
- Risk Change: unchanged_within_boundary
- Fix Plan: change the filter only
- Gap-Closure Admission: ready_for_implement
- Gap Closure Plan: change only the phone filter and rerun the original check
- Re-QA Required: command: node test/taskSearch.test.mjs
- Regression Note: adjacent status filter
- Scoped Next Action: route: implement
"""

        verdict = trace_verdict("tf-vr-004", "verify", response)
        self.assertEqual(verdict["output_contract_verdict"], "fail")
        self.assertEqual(verdict["overall_verdict"], "fail")

    def test_qa_gap_closure_runner_rejects_followup_section_fields(self):
        response = """Verification Scope
- Claim: failed filter can enter bounded remediation
- Covered: supplied failure package
- Missing: none
- Verdict: fail
QA Failure
- Expected: filtered result
- Actual: unfiltered result
- Reproduction: command: node test/taskSearch.test.mjs
- Severity: P1
- Minimal Diagnosis: filter is not applied
- Evidence Delta: first observed failure
- Source / AC Change: unchanged
- Implementation Authority: existing_and_sufficient
- Risk Change: unchanged_within_boundary
- Fix Plan: change the filter only
- Gap-Closure Admission: ready_for_implement
- Gap Closure Plan: change only the phone filter and rerun the original check
- Re-QA Required: command: node test/taskSearch.test.mjs
- Regression Note: adjacent status filter
- Scoped Next Action: route: implement
## Follow-up Summary
- Verdict: fail
- Scoped Next Action: verify closeout
"""

        verdict = trace_verdict("tf-vr-004", "verify", response)
        self.assertEqual(verdict["output_contract_verdict"], "fail")
        self.assertEqual(verdict["overall_verdict"], "fail")

    def test_qa_gap_closure_runner_rejects_execution_or_patch_all_scope(self):
        base = """Verification Scope
- Claim: failed filter can enter bounded remediation
- Covered: supplied failure package
- Missing: none
- Verdict: fail
QA Failure
- Expected: filtered result
- Actual: unfiltered result
- Reproduction: command: node test/taskSearch.test.mjs
- Severity: P1
- Minimal Diagnosis: filter is not applied
- Evidence Delta: first observed failure
- Source / AC Change: unchanged
- Implementation Authority: existing_and_sufficient
- Risk Change: unchanged_within_boundary
- Fix Plan: change the filter only
- Gap-Closure Admission: ready_for_implement
- Gap Closure Plan: change only the phone filter and rerun the original check
- Re-QA Required: command: node test/taskSearch.test.mjs
- Regression Note: adjacent status filter
- Scoped Next Action: route: implement
"""
        for claim in (
            "I applied the scoped fix already.",
            "The scoped fix has been applied already.",
            "We have already patched the filter.",
            "The scoped fix has already been applied.",
            "I have rewritten the filter.",
            "Patch all files in the repository.",
            "Fixing all files in the repository is the proposed remediation.",
            "Editing all files is the proposed remediation.",
            "Every file should be patched.",
            "All files are being patched.",
        ):
            with self.subTest(claim=claim):
                verdict = trace_verdict("tf-vr-004", "verify", base + claim)
                self.assertEqual(verdict["output_contract_verdict"], "fail")
                self.assertEqual(verdict["overall_verdict"], "fail")

    def test_loop_output_tokens_fail_wrong_route_right_shape_responses(self):
        row = {
            "id": "loop-hard-negative",
            "_suite": "trace-first-verify-review.csv",
            "_row_number": 999,
            "_fieldnames": [],
            "route_boundary": "prototype-no-delta-stop",
            "case_kind": "hard_negative",
            "case_source": "regression_protection",
            "intent_kind": "prototype",
            "requirement_state": "prd_draft",
            "source_truth": "local_artifact",
            "risk_gate": "none",
            "expected_state_transition": "none",
            "expected_stop_condition": "blocked",
            "expected_best": "prototype",
            "acceptable_routes": "prototype",
            "forbidden_routes": "implement|dispatch",
            "fixture": "none",
            "input_scenario": "same probe no new evidence",
            "expected_behavior": "stop",
            "forbidden_behavior": "auto retry",
            "output_contract": "prototype_no_delta_stop",
            "evidence_required": "no_file_changes",
            "artifact_allowed": "false",
            "risky_write_requested": "false",
            "host_preemption_allowed": "false",
            "skill_load_required": "true",
            "gate_required": "false",
        }

        verdict = run_runtime.routing_verdict_model(
            row,
            "prototype",
            "I will continue automatically with the same probe until it looks better.",
            0,
            [],
            [],
        )

        self.assertEqual(verdict["routing_verdict"], "pass")
        self.assertEqual(verdict["output_contract_verdict"], "fail")
        self.assertEqual(verdict["overall_verdict"], "fail")

    def test_spec_loop_token_fails_endless_questioning_on_correct_route(self):
        row = {
            "id": "spec-loop-hard-negative",
            "_suite": "trace-first-verify-review.csv",
            "_row_number": 1000,
            "_fieldnames": [],
            "route_boundary": "spec-no-delta-stop",
            "case_kind": "hard_negative",
            "case_source": "regression_protection",
            "intent_kind": "clarify",
            "requirement_state": "blocked",
            "source_truth": "conversation",
            "risk_gate": "none",
            "expected_state_transition": "block",
            "expected_stop_condition": "blocked",
            "expected_best": "to-prd",
            "acceptable_routes": "to-prd",
            "forbidden_routes": "implement|dispatch",
            "fixture": "none",
            "input_scenario": "same question no decision delta",
            "expected_behavior": "stop",
            "forbidden_behavior": "endless grilling",
            "output_contract": "spec_no_delta_stop",
            "evidence_required": "no_file_changes",
            "artifact_allowed": "false",
            "risky_write_requested": "false",
            "host_preemption_allowed": "false",
            "skill_load_required": "true",
            "gate_required": "false",
        }

        verdict = run_runtime.routing_verdict_model(
            row,
            "to-prd",
            "Keep asking philosophical questions until every imaginable unknown is gone.",
            0,
            [],
            [],
        )

        self.assertEqual(verdict["routing_verdict"], "pass")
        self.assertEqual(verdict["output_contract_verdict"], "fail")
        self.assertEqual(verdict["overall_verdict"], "fail")

    def test_contract_lineage_rows_accept_opposite_and_unknown_fix_loci(self):
        cases = (
            (
                "tf-cl-001",
                "implement",
                """Contract Lineage
- Canonical Owner / Source: canonical_contract
- Hops: canonical_contract (verified) -> producer_mapping (verified) -> consumer (verified)
- First Confirmed Divergence: producer_mapping
- Fix Owner / Boundary: producer
- Unverified / Branched Hops: none
""",
            ),
            (
                "tf-cl-002",
                "verify",
                """Verification Scope
- Claim: contract_divergence
- Covered: canonical_contract|storage|service_transform|api|frontend_renderer
- Missing: runtime
- Verdict: partial

## Contract Lineage
- Canonical Owner / Source: canonical_contract
- Hops: canonical_contract (verified) -> storage (verified) -> service_transform (verified) -> api (verified) -> frontend_renderer (verified)
- First Confirmed Divergence: frontend_renderer
- Fix Owner / Boundary: frontend
- Unverified / Branched Hops: none
""",
            ),
            (
                "tf-cl-003",
                "write-plan",
                """Contract Lineage
- Canonical Owner / Source: unverified
- Hops: producer_a (verified) | producer_b (verified)
- First Confirmed Divergence: unverified
- Fix Owner / Boundary: unverified
- Unverified / Branched Hops: canonical_owner | storage
""",
            ),
            (
                "tf-cl-004",
                "verify",
                """Verification Scope
- Claim: contract_divergence
- Covered: canonical_contract|storage|service_transform|api|frontend_renderer
- Missing: runtime
- Verdict: partial

## Contract Lineage
- Canonical Owner / Source: canonical_contract
- Hops: canonical_contract (verified) -> storage (verified) -> service_transform (verified) -> api (verified) -> frontend_renderer (verified)
- First Confirmed Divergence: frontend_renderer
- Fix Owner / Boundary: frontend
- Unverified / Branched Hops: none
""",
            ),
        )

        for row_id, route, response in cases:
            with self.subTest(row_id=row_id):
                verdict = trace_verdict(row_id, route, response)
                self.assertEqual(verdict["output_contract_verdict"], "pass")
                self.assertEqual(verdict["overall_verdict"], "pass")

    def test_contract_lineage_suite_is_isolated_from_default_suite(self):
        with TRACE_SUITE.open(newline="", encoding="utf-8") as handle:
            default_ids = {row["id"] for row in csv.DictReader(handle)}
        with CONTRACT_LINEAGE_SUITE.open(newline="", encoding="utf-8") as handle:
            lineage_ids = {row["id"] for row in csv.DictReader(handle)}

        self.assertEqual(
            lineage_ids,
            {"tf-cl-001", "tf-cl-002", "tf-cl-003", "tf-cl-004"},
        )
        self.assertFalse(default_ids & lineage_ids)
        self.assertIn(TRACE_SUITE.name, suite_registry.DEFAULT_SUITES)
        self.assertNotIn(CONTRACT_LINEAGE_SUITE.name, suite_registry.DEFAULT_SUITES)
        self.assertIn(
            CONTRACT_LINEAGE_SUITE.name,
            routing_schema.TRACE_READY_SUITES,
        )

    def test_uncoached_lineage_row_uses_the_normal_verify_contract(self):
        prompt = run_runtime.prompt_for_row(trace_row("tf-cl-004"))

        self.assertIn("normal verify path", prompt)
        for leaked_contract_token in (
            "Verification Scope",
            "Contract Lineage",
            "Verification Continuation",
            "Next Check",
            "Canonical Owner / Source",
            "First Confirmed Divergence",
            "frontend_renderer",
            "canonical_contract|storage",
        ):
            with self.subTest(token=leaked_contract_token):
                self.assertNotIn(leaked_contract_token, prompt)

    def test_contract_lineage_requires_owning_route_output(self):
        cases = (
            (
                "tf-cl-001",
                "implement",
                """Contract Lineage
- Canonical Owner / Source: canonical_contract
- Hops: canonical_contract (verified) -> producer_mapping (verified) -> consumer (verified)
- First Confirmed Divergence: producer_mapping
- Fix Owner / Boundary: producer
- Unverified / Branched Hops: none
""",
            ),
            (
                "tf-cl-002",
                "verify",
                """Verification Scope
- Claim: contract_divergence
- Covered: canonical_contract|storage|service_transform|api|frontend_renderer
- Missing: runtime
- Verdict: partial

Contract Lineage
- Canonical Owner / Source: canonical_contract
- Hops: canonical_contract (verified) -> storage (verified) -> service_transform (verified) -> api (verified) -> frontend_renderer (verified)
- First Confirmed Divergence: frontend_renderer
- Fix Owner / Boundary: frontend
- Unverified / Branched Hops: none
""",
            ),
            (
                "tf-cl-003",
                "write-plan",
                """Contract Lineage
- Canonical Owner / Source: unverified
- Hops: producer_a (verified) | producer_b (verified)
- First Confirmed Divergence: unverified
- Fix Owner / Boundary: unverified
- Unverified / Branched Hops: canonical_owner | storage
""",
            ),
        )

        for row_id, route, response in cases:
            with self.subTest(row_id=row_id):
                verdict = trace_verdict(
                    row_id,
                    route,
                    response,
                    include_lineage_companion=False,
                )
                self.assertEqual(verdict["output_contract_verdict"], "fail")
                self.assertEqual(verdict["overall_verdict"], "fail")

    def test_contract_lineage_requires_observed_source_or_explicit_boundary(self):
        verified_response = """Contract Lineage
- Canonical Owner / Source: canonical_contract
- Hops: canonical_contract (verified) -> producer_mapping (verified) -> consumer (verified)
- First Confirmed Divergence: producer_mapping
- Fix Owner / Boundary: producer
- Unverified / Branched Hops: none
"""
        unverified_response = """Contract Lineage
- Canonical Owner / Source: unverified
- Hops: producer_a (verified) | producer_b (verified)
- First Confirmed Divergence: unverified
- Fix Owner / Boundary: unverified
- Unverified / Branched Hops: canonical_owner | storage
"""

        verified = trace_verdict(
            "tf-cl-001",
            "implement",
            verified_response,
            stdout="",
        )
        bounded = trace_verdict(
            "tf-cl-003",
            "write-plan",
            unverified_response,
            stdout="",
        )
        wrong_source = trace_verdict(
            "tf-cl-001",
            "implement",
            verified_response,
            stdout=json.dumps(
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
            ),
        )
        failed_source = trace_verdict(
            "tf-cl-001",
            "implement",
            verified_response,
            stdout=json.dumps(
                {
                    "type": "item.completed",
                    "item": {
                        "type": "command_execution",
                        "command": "sed -n '1,240p' SCENARIO.md",
                        "aggregated_output": "No such file",
                        "exit_code": 2,
                        "status": "failed",
                    },
                }
            ),
        )
        same_basename_wrong_path = trace_verdict(
            "tf-cl-001",
            "implement",
            verified_response,
            stdout=json.dumps(
                {
                    "type": "item.completed",
                    "item": {
                        "type": "command_execution",
                        "command": "cat /tmp/SCENARIO.md",
                        "aggregated_output": (
                            ROOT
                            / trace_row("tf-cl-001")["fixture"]
                            / "SCENARIO.md"
                        ).read_text(encoding="utf-8"),
                        "exit_code": 0,
                        "status": "completed",
                    },
                }
            ),
        )

        self.assertEqual(verified["evidence_verdict"], "fail")
        self.assertEqual(verified["overall_verdict"], "fail")
        self.assertEqual(wrong_source["evidence_verdict"], "fail")
        self.assertEqual(failed_source["evidence_verdict"], "fail")
        self.assertEqual(
            same_basename_wrong_path["evidence_verdict"], "fail"
        )
        self.assertEqual(bounded["evidence_verdict"], "pass")

    def test_contract_lineage_accepts_reordered_sibling_branches(self):
        response = """Contract Lineage
- Canonical Owner / Source: unverified
- Hops: producer_b (verified) | producer_a (verified)
- First Confirmed Divergence: unverified
- Fix Owner / Boundary: unverified
- Unverified / Branched Hops: storage | canonical_owner
"""

        verdict = trace_verdict("tf-cl-003", "write-plan", response)

        self.assertEqual(verdict["output_contract_verdict"], "pass")
        self.assertEqual(verdict["overall_verdict"], "pass")

    def test_contract_lineage_rejects_consumer_fix_for_producer_divergence(self):
        response = """Contract Lineage
- Canonical Owner / Source: canonical_contract
- Hops: canonical_contract (verified) -> producer_mapping (verified) -> consumer (verified)
- First Confirmed Divergence: consumer
- Fix Owner / Boundary: consumer
- Unverified / Branched Hops: none
"""

        verdict = trace_verdict("tf-cl-001", "implement", response)
        self.assertEqual(verdict["output_contract_verdict"], "fail")
        self.assertEqual(verdict["overall_verdict"], "fail")

    def test_contract_lineage_rejects_contradictory_or_hidden_route_companion(self):
        lineage = """Contract Lineage
- Canonical Owner / Source: canonical_contract
- Hops: canonical_contract (verified) -> producer_mapping (verified) -> consumer (verified)
- First Confirmed Divergence: producer_mapping
- Fix Owner / Boundary: producer
- Unverified / Branched Hops: none
"""
        contradictory = lineage + """
## Diagnosis Outcome
- Confirmed Cause: consumer rejects the old producer result
- Decisive Evidence: canonical_contract differs from producer_mapping
- Smallest Safe Next Action: keep producer unchanged and add consumer fallback
"""
        competing_clauses = lineage + """
## Diagnosis Outcome
- Confirmed Cause: producer_mapping is the first confirmed divergence; consumer is the actual cause
- Decisive Evidence: canonical_contract differs from producer_mapping; the contracts are actually aligned
- Smallest Safe Next Action: fix producer then reverify consumer
"""
        hidden_html_contradiction = lineage + """
## Diagnosis Outcome
- Confirmed Cause: producer_mapping is the first confirmed divergence <script>consumer is the actual cause</script>
- Decisive Evidence: canonical_contract differs from producer_mapping
- Smallest Safe Next Action: fix producer then reverify consumer
"""
        hidden_html_positive_only = lineage + """
## Diagnosis Outcome
- Confirmed Cause: <span hidden>producer_mapping is the first confirmed divergence</span>
- Decisive Evidence: <span hidden>canonical_contract differs from producer_mapping</span>
- Smallest Safe Next Action: <span hidden>fix producer</span>
"""
        hidden = lineage + """
<!--
## Diagnosis Outcome
- Confirmed Cause: producer_mapping is the first confirmed divergence
- Decisive Evidence: canonical_contract differs from producer_mapping
- Smallest Safe Next Action: fix producer then reverify consumer
-->
"""
        fenced = lineage + """
```text
## Diagnosis Outcome
- Confirmed Cause: producer_mapping is the first confirmed divergence
- Decisive Evidence: canonical_contract differs from producer_mapping
- Smallest Safe Next Action: fix producer then reverify consumer
```
"""
        indented = "\n".join(
            "    " + line
            for line in (lineage + lineage_route_companion("implement")).splitlines()
        )

        for response in (
            contradictory,
            competing_clauses,
            hidden_html_contradiction,
            hidden_html_positive_only,
            hidden,
            fenced,
            indented,
        ):
            with self.subTest(response=response):
                verdict = trace_verdict(
                    "tf-cl-001",
                    "implement",
                    response,
                    include_lineage_companion=False,
                )
                self.assertEqual(verdict["output_contract_verdict"], "fail")
                self.assertEqual(verdict["overall_verdict"], "fail")

        core_hidden_failures = loop_checks.contract_lineage_failures(
            lineage
            + "\n<span hidden>consumer is the actual cause</span>\n",
            trace_row("tf-cl-001"),
        )
        self.assertIn(
            "Contract Lineage eval output cannot contain hidden or non-rendered HTML",
            core_hidden_failures,
        )

        visible = lineage + lineage_route_companion("implement")
        hidden_tails = (
            "\n```text\nThe producer evidence is fabricated.\n```\n",
            "\n    The producer evidence is fabricated.\n",
            "\n<!-- The producer evidence is fabricated. -->\n",
        )
        for tail in hidden_tails:
            with self.subTest(tail=tail):
                verdict = trace_verdict(
                    "tf-cl-001",
                    "implement",
                    visible + tail,
                    include_lineage_companion=False,
                )
                self.assertEqual(
                    verdict["output_contract_verdict"], "fail"
                )
                self.assertEqual(verdict["overall_verdict"], "fail")

    def test_contract_lineage_rejects_negative_direction_morphology(self):
        lineage = """Contract Lineage
- Canonical Owner / Source: canonical_contract
- Hops: canonical_contract (verified) -> producer_mapping (verified) -> consumer (verified)
- First Confirmed Divergence: producer_mapping
- Fix Owner / Boundary: producer
- Unverified / Branched Hops: none
"""
        implement_companion = lineage_route_companion("implement")
        implement_cases = (
            implement_companion.replace(
                "producer_mapping is the first confirmed divergence",
                "producer_mapping fails to be the first confirmed divergence",
            ),
            implement_companion.replace(
                "canonical_contract differs from producer_mapping",
                "canonical_contract fails to differ from producer_mapping",
            ),
            implement_companion.replace(
                "fix producer then reverify consumer",
                "producer refuses to change the mapping",
            ),
            implement_companion.replace(
                "fix producer then reverify consumer",
                "producer declines to change the mapping",
            ),
        )
        for companion in implement_cases:
            with self.subTest(companion=companion):
                verdict = trace_verdict(
                    "tf-cl-001",
                    "implement",
                    lineage + "\n" + companion,
                    include_lineage_companion=False,
                )
                self.assertEqual(
                    verdict["output_contract_verdict"],
                    "fail",
                )
                self.assertEqual(verdict["overall_verdict"], "fail")

        verify_lineage = """Verification Scope
- Claim: contract_divergence
- Covered: canonical_contract|storage|service_transform|api|frontend_renderer
- Missing: runtime
- Verdict: partial

Contract Lineage
- Canonical Owner / Source: canonical_contract
- Hops: canonical_contract (verified) -> storage (verified) -> service_transform (verified) -> api (verified) -> frontend_renderer (verified)
- First Confirmed Divergence: frontend_renderer
- Fix Owner / Boundary: frontend
- Unverified / Branched Hops: none
"""
        for next_check in (
            "frontend is unable to check the corrected boundary",
            "frontend declines to verify the corrected boundary",
        ):
            with self.subTest(next_check=next_check):
                verdict = trace_verdict(
                    "tf-cl-002",
                    "verify",
                    verify_lineage
                    + "\n## Verification Continuation\n"
                    + f"- Next Check: {next_check}\n",
                    include_lineage_companion=False,
                )
                self.assertEqual(
                    verdict["output_contract_verdict"],
                    "fail",
                )
                self.assertEqual(verdict["overall_verdict"], "fail")

    def test_contract_lineage_rejects_empty_branches_and_split_tokens(self):
        responses = (
            """Contract Lineage
- Canonical Owner / Source: unverified
- Hops: producer_a (verified) || producer_b (verified) |
- First Confirmed Divergence: unverified
- Fix Owner / Boundary: unverified
- Unverified / Branched Hops: canonical_owner | storage
""",
            """Contract Lineage
- Canonical Owner / Source: canonical_contract
- Hops: canonical_ contract (veri fied) -> producer_mapping (verified) -> consumer (verified)
- First Confirmed Divergence: producer_mapping
- Fix Owner / Boundary: producer
- Unverified / Branched Hops: none
""",
            """Contract Lineage
- Canonical Owner / Source: unverified
- Hops: producer_a (verified) | producer_b (verified)
- First Confirmed Divergence: unverified
- Fix Owner / Boundary: unverified
- Unverified / Branched Hops: canonical_owner || storage |
""",
            """Contract Lineage
- Canonical Owner / Source: unverified
- Hops: producer_a (not applicable) | producer_b (verified)
- First Confirmed Divergence: unverified
- Fix Owner / Boundary: unverified
- Unverified / Branched Hops: canonical_owner | storage
""",
        )
        cases = (
            ("tf-cl-003", "write-plan", responses[0]),
            ("tf-cl-001", "implement", responses[1]),
            ("tf-cl-003", "write-plan", responses[2]),
            ("tf-cl-003", "write-plan", responses[3]),
        )
        for row_id, route, response in cases:
            with self.subTest(row_id=row_id, response=response):
                verdict = trace_verdict(row_id, route, response)
                self.assertEqual(verdict["output_contract_verdict"], "fail")
                self.assertEqual(verdict["overall_verdict"], "fail")

    def test_contract_lineage_rejects_invented_complete_branched_path(self):
        response = """Contract Lineage
- Canonical Owner / Source: unverified
- Hops: producer_a (verified) -> storage (unverified) -> producer_b (verified)
- First Confirmed Divergence: unverified
- Fix Owner / Boundary: unverified
- Unverified / Branched Hops: canonical_owner | storage
"""

        verdict = trace_verdict("tf-cl-003", "write-plan", response)
        self.assertEqual(verdict["output_contract_verdict"], "fail")
        self.assertEqual(verdict["overall_verdict"], "fail")

    def test_contract_lineage_rejects_missing_fields_and_substring_hop_matches(self):
        missing_field = """Contract Lineage
- Canonical Owner / Source: canonical_contract
- Hops: canonical_contract -> producer_mapping -> consumer
- First Confirmed Divergence: producer_mapping
- Fix Owner / Boundary: producer
"""
        substring_hops = """Contract Lineage
- Canonical Owner / Source: canonical_contract
- Hops: canonical_contractual -> producer_mapping_extra -> consumerish
- First Confirmed Divergence: producer_mapping
- Fix Owner / Boundary: producer
- Unverified / Branched Hops: none
"""

        for response in (missing_field, substring_hops):
            with self.subTest(response=response):
                verdict = trace_verdict("tf-cl-001", "implement", response)
                self.assertEqual(verdict["output_contract_verdict"], "fail")
                self.assertEqual(verdict["overall_verdict"], "fail")

    def test_contract_lineage_rejects_extra_hops_prose_and_scope_contradiction(self):
        extra_hop = """Contract Lineage
- Canonical Owner / Source: canonical_contract
- Hops: canonical_contract (verified) -> invented_storage (verified) -> producer_mapping (verified) -> consumer (verified)
- First Confirmed Divergence: producer_mapping
- Fix Owner / Boundary: producer
- Unverified / Branched Hops: none
"""
        contradictory_prose = """Contract Lineage
- Canonical Owner / Source: canonical_contract
- Hops: canonical_contract (verified) -> producer_mapping (verified) -> consumer (verified)
- First Confirmed Divergence: producer_mapping
- Fix Owner / Boundary: producer
- Unverified / Branched Hops: none
Approve the consumer-only fallback anyway.
"""
        contradictory_scope = """Verification Scope
- Claim: contract_divergence
- Covered: change_api_producer
- Missing: runtime
- Verdict: partial

## Contract Lineage
- Canonical Owner / Source: canonical_contract
- Hops: canonical_contract (verified) -> storage (verified) -> service_transform (verified) -> api (verified) -> frontend_renderer (verified)
- First Confirmed Divergence: frontend_renderer
- Fix Owner / Boundary: frontend
- Unverified / Branched Hops: none
"""

        cases = (
            ("tf-cl-001", "implement", extra_hop),
            ("tf-cl-001", "implement", contradictory_prose),
            ("tf-cl-002", "verify", contradictory_scope),
        )
        for row_id, route, response in cases:
            with self.subTest(row_id=row_id, response=response):
                verdict = trace_verdict(row_id, route, response)
                self.assertEqual(verdict["output_contract_verdict"], "fail")
                self.assertEqual(verdict["overall_verdict"], "fail")

    def test_contract_lineage_rejects_evidence_state_and_unverified_hop_drift(self):
        wrong_evidence_state = """Contract Lineage
- Canonical Owner / Source: canonical_contract
- Hops: canonical_contract (verified) -> producer_mapping (unverified) -> consumer (verified)
- First Confirmed Divergence: producer_mapping
- Fix Owner / Boundary: producer
- Unverified / Branched Hops: none
"""
        wrong_unverified_hops = """Contract Lineage
- Canonical Owner / Source: unverified
- Hops: producer_a (verified) | producer_b (verified)
- First Confirmed Divergence: unverified
- Fix Owner / Boundary: unverified
- Unverified / Branched Hops: canonical_owner
"""

        cases = (
            ("tf-cl-001", "implement", wrong_evidence_state),
            ("tf-cl-003", "write-plan", wrong_unverified_hops),
        )
        for row_id, route, response in cases:
            with self.subTest(row_id=row_id):
                verdict = trace_verdict(row_id, route, response)
                self.assertEqual(verdict["output_contract_verdict"], "fail")
                self.assertEqual(verdict["overall_verdict"], "fail")

    def test_contract_lineage_shared_contract_is_conditional_and_route_owned(self):
        contract = read("skills/_shared/CONTRACT-NOTES.md")
        first_principles = read("skills/_shared/FIRST-PRINCIPLES.md")
        lenses = read("skills/verify/LENSES.md")

        for field in (
            "Canonical Owner / Source",
            "Hops",
            "First Confirmed Divergence",
            "Fix Owner / Boundary",
            "Unverified / Branched Hops",
        ):
            self.assertIn(field, contract)
        self.assertIn("cross-boundary only", contract)
        self.assertIn("first confirmed divergence", first_principles.lower())
        self.assertIn("producer-first inspection", first_principles.lower())
        self.assertIn("Contract Lineage", lenses)
        self.assertIn("last visible consumer", lenses)

    def test_contract_lineage_route_companion_rejects_negative_polarity(self):
        lineage = """Contract Lineage
- Canonical Owner / Source: canonical_contract
- Hops: canonical_contract (verified) -> producer_mapping (verified) -> consumer (verified)
- First Confirmed Divergence: producer_mapping
- Fix Owner / Boundary: producer
- Unverified / Branched Hops: none
"""
        companion_variants = (
            """## Diagnosis Outcome
- Confirmed Cause: producer_mapping is not the cause; consumer is
- Decisive Evidence: canonical_contract differs from producer_mapping
- Smallest Safe Next Action: fix producer then reverify consumer
""",
            """## Diagnosis Outcome
- Confirmed Cause: producer_mapping is the first confirmed divergence
- Decisive Evidence: canonical_contract and producer_mapping are aligned
- Smallest Safe Next Action: fix producer then reverify consumer
""",
            """## Diagnosis Outcome
- Confirmed Cause: producer_mapping is the first confirmed divergence
- Decisive Evidence: canonical_contract differs from producer_mapping
- Smallest Safe Next Action: leave producer unchanged and add a consumer fallback
""",
            """## Diagnosis Outcome
- Confirmed Cause: consumer is the cause instead of producer_mapping
- Decisive Evidence: canonical_contract matches producer_mapping and the mismatch is only in consumer
- Smallest Safe Next Action: avoid a producer patch by using the consumer fallback
""",
            """## Diagnosis Outcome
- Confirmed Cause: producer_mapping is uncertain as the cause of the first divergence
- Decisive Evidence: canonical_contract and producer_mapping are allegedly different
- Smallest Safe Next Action: possibly patch producer
""",
            """## Diagnosis Outcome
- Confirmed Cause: producer_mapping is ostensibly the cause of the first divergence
- Decisive Evidence: canonical_contract and producer_mapping are reportedly different
- Smallest Safe Next Action: presumably patch producer
""",
            """## Diagnosis Outcome
- Confirmed Cause: producer_mapping is purportedly the cause of the first divergence
- Decisive Evidence: canonical_contract and producer_mapping are apparently different
- Smallest Safe Next Action: plausibly patch producer
""",
            """## Diagnosis Outcome
- Confirmed Cause: it is false that producer_mapping is the first confirmed divergence
- Decisive Evidence: canonical_contract differs from producer_mapping
- Smallest Safe Next Action: fix producer then reverify consumer
""",
            """## Diagnosis Outcome
- Confirmed Cause: producer_mapping is the first confirmed divergence
- Decisive Evidence: it is untrue that canonical_contract differs from producer_mapping
- Smallest Safe Next Action: fix producer then reverify consumer
""",
            """## Diagnosis Outcome
- Confirmed Cause: producer_mapping is the first confirmed divergence
- Decisive Evidence: canonical_contract differs from producer_mapping
- Smallest Safe Next Action: it is incorrect that we should fix producer
""",
            """## Diagnosis Outcome
- Confirmed Cause: I deny that producer_mapping is the first confirmed divergence
- Decisive Evidence: canonical_contract differs from producer_mapping
- Smallest Safe Next Action: fix producer then reverify consumer
""",
            """## Diagnosis Outcome
- Confirmed Cause: producer_mapping is the first confirmed divergence
- Decisive Evidence: I refute that canonical_contract differs from producer_mapping
- Smallest Safe Next Action: fix producer then reverify consumer
""",
            """## Diagnosis Outcome
- Confirmed Cause: contrary to the claim that producer_mapping is the first confirmed divergence
- Decisive Evidence: canonical_contract differs from producer_mapping
- Smallest Safe Next Action: fix producer then reverify consumer
""",
            """## Diagnosis Outcome
- Confirmed Cause: 事实并非 producer_mapping 是首个已确认分歧
- Decisive Evidence: canonical_contract differs from producer_mapping
- Smallest Safe Next Action: fix producer then reverify consumer
""",
            """## Diagnosis Outcome
- Confirmed Cause: producer_mapping is the first confirmed divergence
- Decisive Evidence: 我否认 canonical_contract 与 producer_mapping 存在差异
- Smallest Safe Next Action: fix producer then reverify consumer
""",
        )
        for companion in companion_variants:
            with self.subTest(companion=companion):
                verdict = trace_verdict(
                    "tf-cl-001",
                    "implement",
                    lineage + companion,
                    include_lineage_companion=False,
                )
                self.assertEqual(verdict["output_contract_verdict"], "fail")
                self.assertEqual(verdict["overall_verdict"], "fail")

        unresolved_lineage = """Contract Lineage
- Canonical Owner / Source: unverified
- Hops: producer_a (verified) | producer_b (verified)
- First Confirmed Divergence: unverified
- Fix Owner / Boundary: unverified
- Unverified / Branched Hops: canonical_owner | storage
"""
        false_resolution = """## Implementation Plan
- Accepted Goal: resolve canonical_owner and storage without inventing ownership
- Ordered Steps: skip canonical_owner and storage inspection
- Dependencies / Gates: canonical_owner and storage are no longer unverified; no work is blocked
- Verification Checkpoints: compare any available contract
- Stop Condition: continue implementation
"""
        verdict = trace_verdict(
            "tf-cl-003",
            "write-plan",
            unresolved_lineage + false_resolution,
            include_lineage_companion=False,
        )
        self.assertEqual(verdict["output_contract_verdict"], "fail")
        self.assertEqual(verdict["overall_verdict"], "fail")

        verify_lineage = """Contract Lineage
- Canonical Owner / Source: canonical_contract
- Hops: canonical_contract (verified) -> storage (verified) -> service_transform (verified) -> api (verified) -> frontend_renderer (verified)
- First Confirmed Divergence: frontend_renderer
- Fix Owner / Boundary: frontend
- Unverified / Branched Hops: none

Verification Scope
- Claim: contract_divergence
- Covered: canonical_contract|storage|service_transform|api|frontend_renderer
- Missing: runtime
- Verdict: partial
"""
        avoid_check = """## Verification Continuation
- Next Check: avoid a frontend check by validating the API instead
"""
        verify_verdict = trace_verdict(
            "tf-cl-002",
            "verify",
            verify_lineage + avoid_check,
            include_lineage_companion=False,
        )
        self.assertEqual(verify_verdict["output_contract_verdict"], "fail")
        self.assertEqual(verify_verdict["overall_verdict"], "fail")

        optional_gate = """## Implementation Plan
- Accepted Goal: resolve canonical_owner and storage without inventing ownership
- Ordered Steps: avoid the canonical_owner and storage inspect gate
- Dependencies / Gates: canonical_owner and storage are optional dependencies that unblock implementation
- Verification Checkpoints: compare available contracts
- Stop Condition: continue implementation
"""
        optional_verdict = trace_verdict(
            "tf-cl-003",
            "write-plan",
            unresolved_lineage + optional_gate,
            include_lineage_companion=False,
        )
        self.assertEqual(optional_verdict["output_contract_verdict"], "fail")
        self.assertEqual(optional_verdict["overall_verdict"], "fail")

    def test_contract_lineage_rejects_each_isolated_hedge_and_confusable_negation(
        self,
    ):
        lineage = """Contract Lineage
- Canonical Owner / Source: canonical_contract
- Hops: canonical_contract (verified) -> producer_mapping (verified) -> consumer (verified)
- First Confirmed Divergence: producer_mapping
- Fix Owner / Boundary: producer
- Unverified / Branched Hops: none
"""
        companion = """## Diagnosis Outcome
- Confirmed Cause: {cause}
- Decisive Evidence: canonical_contract differs from producer_mapping
- Smallest Safe Next Action: fix producer then reverify consumer
"""
        english_hedges = (
            "ostensibly",
            "reportedly",
            "purportedly",
            "apparently",
            "plausibly",
            "presumably",
            "supposedly",
            "arguably",
            "seemingly",
            "probably",
            "potentially",
            "putatively",
        )
        chinese_hedges = (
            "表面上",
            "据报道",
            "据说",
            "号称",
            "所谓",
            "看似",
            "貌似",
            "推测",
            "大概",
            "或许",
        )
        causes = [
            (
                f"producer_mapping is {hedge} the cause of the first "
                "divergence"
            )
            for hedge in english_hedges
        ]
        causes.extend(
            f"producer_mapping {hedge}是首个已确认分歧"
            for hedge in chinese_hedges
        )
        causes.extend(
            (
                "producer_mapping is the probable cause of the first "
                "divergence",
                "producer_mapping is a potential cause of the first "
                "divergence",
                "producer_mapping is the putative cause of the first "
                "divergence",
            )
        )
        causes.append(
            "producer_mapping is nоt the cause; producer_mapping is the "
            "first confirmed divergence"
        )

        for cause in causes:
            with self.subTest(cause=cause):
                verdict = trace_verdict(
                    "tf-cl-001",
                    "implement",
                    lineage + companion.format(cause=cause),
                    include_lineage_companion=False,
                )
                self.assertEqual(
                    verdict["output_contract_verdict"],
                    "fail",
                )
                self.assertEqual(verdict["overall_verdict"], "fail")

        assertive_causes = (
            "producer_mapping is definitively the first confirmed divergence",
            "producer_mapping is definitively the first confirmed divergence "
            "with potential downstream impact",
            "producer_mapping 已确认为首个分歧",
        )
        for cause in assertive_causes:
            with self.subTest(assertive_cause=cause):
                verdict = trace_verdict(
                    "tf-cl-001",
                    "implement",
                    lineage + companion.format(cause=cause),
                    include_lineage_companion=False,
                )
                self.assertEqual(
                    verdict["output_contract_verdict"],
                    "pass",
                )
                self.assertEqual(verdict["overall_verdict"], "pass")

    def test_contract_lineage_rejects_detached_field_polarity_bypasses(self):
        implement_lineage = """Contract Lineage
- Canonical Owner / Source: canonical_contract
- Hops: canonical_contract (verified) -> producer_mapping (verified) -> consumer (verified)
- First Confirmed Divergence: producer_mapping
- Fix Owner / Boundary: producer
- Unverified / Branched Hops: none
"""
        implement_companions = (
            """## Diagnosis Outcome
- Confirmed Cause: Maybe; producer_mapping is the first confirmed divergence
- Decisive Evidence: canonical_contract differs from producer_mapping
- Smallest Safe Next Action: fix producer then reverify consumer
""",
            """## Diagnosis Outcome
- Confirmed Cause: producer_mapping is the first confirmed divergence
- Decisive Evidence: nоt sure; canonical_contract differs from producer_mapping
- Smallest Safe Next Action: fix producer then reverify consumer
""",
            """## Diagnosis Outcome
- Confirmed Cause: producer_mapping is the first confirmed divergence
- Decisive Evidence: canonical_contract differs from producer_mapping
- Smallest Safe Next Action: Maybe; fix producer then reverify consumer
""",
        )
        for companion in implement_companions:
            with self.subTest(route="implement", companion=companion):
                verdict = trace_verdict(
                    "tf-cl-001",
                    "implement",
                    implement_lineage + companion,
                    include_lineage_companion=False,
                )
                self.assertEqual(
                    verdict["output_contract_verdict"],
                    "fail",
                )
                self.assertEqual(verdict["overall_verdict"], "fail")

        verify_response = """Contract Lineage
- Canonical Owner / Source: canonical_contract
- Hops: canonical_contract (verified) -> storage (verified) -> service_transform (verified) -> api (verified) -> frontend_renderer (verified)
- First Confirmed Divergence: frontend_renderer
- Fix Owner / Boundary: frontend
- Unverified / Branched Hops: none

Verification Scope
- Claim: contract_divergence
- Covered: canonical_contract|storage|service_transform|api|frontend_renderer
- Missing: runtime
- Verdict: partial

## Verification Continuation
- Next Check: nоt sure; reverify frontend_renderer after the frontend boundary is corrected
"""
        verify_verdict = trace_verdict(
            "tf-cl-002",
            "verify",
            verify_response,
            include_lineage_companion=False,
        )
        self.assertEqual(
            verify_verdict["output_contract_verdict"],
            "fail",
        )
        self.assertEqual(verify_verdict["overall_verdict"], "fail")

        write_plan_lineage = """Contract Lineage
- Canonical Owner / Source: unverified
- Hops: producer_a (verified) | producer_b (verified)
- First Confirmed Divergence: unverified
- Fix Owner / Boundary: unverified
- Unverified / Branched Hops: canonical_owner | storage
"""
        write_plan_companions = (
            """## Implementation Plan
- Accepted Goal: resolve canonical_owner and storage without inventing ownership
- Ordered Steps: inspect canonical_owner then storage then producer_a and producer_b
- Dependencies / Gates: Maybe; canonical_owner and storage remain unverified so implementation is blocked
- Verification Checkpoints: compare each inspected unverified hop with the accepted contract
- Stop Condition: canonical_owner and storage become evidence-backed or remain blocked
""",
            """## Implementation Plan
- Accepted Goal: resolve canonical_owner and storage without inventing ownership
- Ordered Steps: nоt sure; inspect canonical_owner then storage then producer_a and producer_b
- Dependencies / Gates: canonical_owner and storage remain unverified so implementation is blocked
- Verification Checkpoints: compare each inspected unverified hop with the accepted contract
- Stop Condition: canonical_owner and storage become evidence-backed or remain blocked
""",
        )
        for companion in write_plan_companions:
            with self.subTest(route="write-plan", companion=companion):
                verdict = trace_verdict(
                    "tf-cl-003",
                    "write-plan",
                    write_plan_lineage + companion,
                    include_lineage_companion=False,
                )
                self.assertEqual(
                    verdict["output_contract_verdict"],
                    "fail",
                )
                self.assertEqual(verdict["overall_verdict"], "fail")

        assertive_write_plan = """## Implementation Plan
- Accepted Goal: resolve canonical_owner and storage without inventing ownership
- Ordered Steps: inspect canonical_owner then storage then producer_a and producer_b
- Dependencies / Gates: canonical_owner and storage remain unverified; the pending gate blocks implementation
- Verification Checkpoints: compare each inspected unverified hop with the accepted contract
- Stop Condition: canonical_owner and storage become evidence-backed or remain blocked
"""
        assertive_verdict = trace_verdict(
            "tf-cl-003",
            "write-plan",
            write_plan_lineage + assertive_write_plan,
            include_lineage_companion=False,
        )
        self.assertEqual(
            assertive_verdict["output_contract_verdict"],
            "pass",
        )
        self.assertEqual(assertive_verdict["overall_verdict"], "pass")

    def test_contract_lineage_route_companion_accepts_assertive_synonyms(self):
        response = """Contract Lineage
- Canonical Owner / Source: canonical_contract
- Hops: canonical_contract (verified) -> producer_mapping (verified) -> consumer (verified)
- First Confirmed Divergence: producer_mapping
- Fix Owner / Boundary: producer
- Unverified / Branched Hops: none

## Diagnosis Outcome
- Confirmed Cause: the contract first diverges at producer_mapping
- Decisive Evidence: producer_mapping contradicts canonical_contract
- Smallest Safe Next Action: bring producer back into alignment, then reverify consumer
"""

        verdict = trace_verdict(
            "tf-cl-001",
            "implement",
            response,
            include_lineage_companion=False,
        )

        self.assertEqual(verdict["output_contract_verdict"], "pass")
        self.assertEqual(verdict["overall_verdict"], "pass")

    def test_verified_plugin_claim_rejects_tautological_roots(self):
        claim = """```yaml
release_evidence_claim:
  claim_type: runtime
  claim: runtime_smoke
  evidence_status: verified
  installed_plugin_root: /installed/groundwork
  source_root: /installed/groundwork
  cache_or_source_refresh:
    method: source_equivalence
    evidence: installed_source_matches
  run_scope: targeted
  commands_or_trials: [run_runtime_smoke]
  limitations: []
```"""

        failures = loop_checks.release_evidence_claim_failures(claim)

        self.assertTrue(
            any("independent paths" in failure for failure in failures),
            failures,
        )

        installed_inside_source = claim.replace(
            "installed_plugin_root: /installed/groundwork\n"
            "  source_root: /installed/groundwork",
            "installed_plugin_root: /workspace/source/.codex/plugins/cache/groundwork\n"
            "  source_root: /workspace/source",
        )
        ancestry_failures = (
            loop_checks.release_evidence_claim_failures(
                installed_inside_source
            )
        )
        self.assertTrue(
            any(
                "ancestor/descendant relationship" in failure
                for failure in ancestry_failures
            ),
            ancestry_failures,
        )

    def test_release_evidence_claim_yaml_scalars_require_balanced_quotes(self):
        template = """```yaml
release_evidence_claim:
  claim_type: runtime
  claim: runtime_smoke
  evidence_status: {status}
  installed_plugin_root: /installed/groundwork
  source_root: /workspace/source
  cache_or_source_refresh:
    method: source_equivalence
    evidence: installed_source_matches
  run_scope: targeted
  commands_or_trials: [run_runtime_smoke]
  limitations: []
```"""
        balanced = template.format(status='"verified"')
        self.assertEqual(
            loop_checks.release_evidence_claim_status(balanced), "verified"
        )
        self.assertEqual(
            loop_checks.release_evidence_claim_failures(balanced), []
        )

        for malformed_status in ('verified"', '"verified', "'verified\""):
            with self.subTest(status=malformed_status):
                malformed = template.format(status=malformed_status)
                self.assertEqual(
                    loop_checks.release_evidence_claim_status(malformed), ""
                )
                self.assertTrue(
                    loop_checks.release_evidence_claim_failures(malformed)
                )

        malformed_claim = balanced.replace(
            "claim: runtime_smoke", "claim: 'runtime's smoke'"
        )
        self.assertEqual(
            loop_checks.release_evidence_claim_status(malformed_claim), ""
        )
        self.assertTrue(
            loop_checks.release_evidence_claim_failures(malformed_claim)
        )

    def test_release_evidence_claim_must_be_visible_markdown(self):
        claim = """```yaml
release_evidence_claim:
  claim_type: runtime
  claim: runtime_smoke
  evidence_status: unverified
  installed_plugin_root: unverified
  source_root: /workspace/source
  cache_or_source_refresh:
    method: not_run
    evidence: not_run
  run_scope: not_run
  commands_or_trials: []
  limitations: [runtime_not_run]
```"""
        hidden_candidates = (
            "<!--\n" + claim + "\n-->",
            "\n".join("    " + line for line in claim.splitlines()),
            "````text\n" + claim + "\n````",
        )
        for candidate in hidden_candidates:
            with self.subTest(candidate=candidate):
                self.assertEqual(
                    loop_checks.release_evidence_claim_status(candidate), ""
                )
                self.assertTrue(
                    loop_checks.release_evidence_claim_failures(candidate)
                )

    def test_uat_absence_guard_normalizes_visible_heading_variants(self):
        variants = (
            "## <span>UAT Evidence Window</span>",
            "## UAT&#32;Evidence&#32;Window",
            "## [UAT Evidence Window][window]",
            "## UAT Evi<!--hidden-->dence Window",
            "## " + "[" * 1100 + "UAT Evidence Window" + "]" * 1100,
        )
        for response in variants:
            with self.subTest(response=response):
                self.assertTrue(
                    loop_checks.uat_evidence_window_absence_failures(response)
                )


if __name__ == "__main__":
    unittest.main()
