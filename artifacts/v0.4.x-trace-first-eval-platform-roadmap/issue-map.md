# v0.4.x Trace-first Eval Platform Roadmap Issue Pack

Target Reader: Groundwork maintainers, implementation agents, eval harness authors, and follow-up verification threads executing the v0.4.x trace-first eval platform roadmap.
Reader Action Needed: Use these tracker-neutral issue drafts to plan, triage, or implement v0.4.2 through v0.4.5 slices one at a time.
Decision Supported: Which post-v0.4.1 eval-platform slices can proceed independently, which depend on schema/score contracts, and what evidence is required before release claims.
Artifact Type: issue map.
Source of Truth: `docs/prd-v0.4.x-trace-first-eval-platform-roadmap.md`.
Scope: Issue decomposition for schema-backed score foundation, deterministic checker modularization, trace artifacts/diagnostics, eval reports, patch suggestions, CI minimum gates, and release-evidence policy.
Out of Scope: Creating remote tracker issues, implementing these slices in this issue-pack change, executing Codex runtime evals, creating Codex worktrees, spawning subagents, creating automations, mutating plugin cache, claiming release readiness, opening PRs automatically, or changing public skill surface.
Evidence Level: Derived from the local v0.4.x roadmap PRD and current repository conventions. No runtime, CI, release, UAT, marketplace, cache-refresh, or Codex App evidence is added by this issue pack.
Safe to Share / Redaction Notes: Safe to share as a tracker-neutral planning artifact. It contains no secrets, credentials, private URLs, browser cookies, PII, logs, production data, or raw runtime traces.

---

## Issue Set Summary

Source:

- Canonical PRD: `docs/prd-v0.4.x-trace-first-eval-platform-roadmap.md`
- Requirement state: `roadmap_ready_for_issue_slicing` after maintainer acceptance
- Issue pack status: tracker-neutral local artifact
- Remote tracker status: not created

Version batching:

- v0.4.2: V042-001 through V042-004 — schema-backed score foundation.
- v0.4.3: V043-001 through V043-004 — modular deterministic checks and behavior hardening.
- v0.4.4: V044-001 through V044-004 — trace artifacts, diagnostics, reports, and patch suggestions.
- v0.4.5: V045-001 through V045-004 — CI minimum gate and release evidence policy.

Ordering:

1. Start with V042-001 and V042-002 so schema files stabilize before score JSON generation.
2. V042-003 should land before checker extraction because score shape needs a home for checker output.
3. V043-001 should preserve legacy runner behavior while extracting checks.
4. V043-002 should include the current v0.4.1 hard-negative checks as named deterministic checks.
5. V044-001 should define trace artifact layout before diagnostics and report generation.
6. V044-003 and V044-004 should not auto-apply patches.
7. V045-001 should start schema-only; runtime Codex eval remains opt-in.

Field semantics:

- Implementation Task Type Candidate is a planning recommendation only.
- Implementation Runtime Candidate is a later `triage` / `dispatch` input, not an execution command.
- Product Runtime Covered describes the Groundwork semantics being documented, constrained, or tested by the slice.
- Goal Contract Status is `not_generated_by_to_issues` for every slice.
- Ready-for-Agent Missing Fields name gaps for later `triage`; they do not block this tracker-neutral issue pack.

---

## v0.4.2 — Schema-backed Score Foundation

### V042-001: Common schema definitions

Goal:
Add the shared schema foundation for verdicts, workflow routes, execution primitives, evidence sources, severity, blocked reasons, checker result objects, and common score metadata.

Acceptance Criteria:

- Add `schemas/groundwork-common.schema.json` or accepted equivalent location.
- Define `overall_verdict: pass | partial | fail | blocked`.
- Define workflow route enum for existing public skill routes, direct fallback, runtime-safety-gate where appropriate, and unknown.
- Define execution primitive enum for local direct/artifact, worktree isolated/review-only, automation candidate, subagent review candidate, blocked no-execution, not applicable, and unknown.
- Define evidence source enum.
- Define severity enum.
- Define blocked reason taxonomy.
- Define checker result shape with checker id, verdict, notes, and fix locus.
- Prefer strict schemas with explicit extension points.

Evidence / Source:

- Roadmap PRD FR-421.
- `docs/skill-success-metrics.md` existing metric vocabulary.
- Current `evals/run_runtime.py` verdict fields.

Blockers:

- None.

Execution: AFK schema/docs slice.

Contract Impact:

- schema contract
- score JSON contract foundation
- metrics vocabulary

Verification Evidence Needed:

```bash
python -m json.tool schemas/groundwork-common.schema.json
git diff --check
```

Implementation Task Type Candidate: `write_implementation`.

Implementation Runtime Candidate: `main_thread_direct`.

Product Runtime Covered: `schema_foundation`.

Isolation Needed:

- context: `none`
- filesystem: `current_workspace`
- diff surface: `required`

Parallelization Candidate:

- eligible: yes
- conflict group: `v042-common-schema`
- dependency group: `v042-schema`
- merge order hint: first v0.4.2 slice.

Goal Contract Status: `not_generated_by_to_issues`.

Goal Contract Missing Fields:

- JSON Schema draft version.
- Whether schema files live under `schemas/` or `evals/schemas/`.

Runtime Missing Fields:

- None; runtime execution is out of scope.

Ready-for-Agent Missing Fields:

- Maintainer decision on schema directory.

Triage Recommendation Candidate: `ready-for-agent candidate`.

---

### V042-002: Product schemas for verify, review, routing, closeout, and eval score

Goal:
Add product-level JSON schemas that use the common schema definitions and cover the trace-ready score outputs.

Acceptance Criteria:

- Add `schemas/groundwork-verify.schema.json`.
- Add `schemas/groundwork-review.schema.json`.
- Add `schemas/groundwork-routing.schema.json`.
- Add `schemas/groundwork-closeout.schema.json`.
- Add `schemas/groundwork-eval-score.schema.json`.
- `review` remains a schema/lens output mode, not a new public skill.
- Routing schema supports expected/actual route and trace-ready route boundary.
- Closeout schema preserves no-merge-without-evidence, git boundary, review status, and known merge source requirements.
- Eval score schema can include output contract verdict, evidence verdict, behavior verdict, routing verdict, checker results, and notes.

Evidence / Source:

- Roadmap PRD FR-421 and FR-422.
- V042-001 common schema definitions.
- v0.4.0 closeout package safety.
- v0.4.1 trace-ready rows.

Blockers:

- V042-001.

Execution: AFK schema slice.

Contract Impact:

- verify schema
- review lens schema
- routing schema
- closeout schema
- score JSON schema

Verification Evidence Needed:

```bash
python -m json.tool schemas/groundwork-verify.schema.json
python -m json.tool schemas/groundwork-review.schema.json
python -m json.tool schemas/groundwork-routing.schema.json
python -m json.tool schemas/groundwork-closeout.schema.json
python -m json.tool schemas/groundwork-eval-score.schema.json
git diff --check
```

Implementation Task Type Candidate: `write_implementation`.

Implementation Runtime Candidate: `main_thread_direct`.

Product Runtime Covered: `schema_contracts`.

Isolation Needed:

- context: `none`
- filesystem: `current_workspace`
- diff surface: `required`

Parallelization Candidate:

- eligible: no
- conflict group: `v042-product-schemas`
- dependency group: `v042-schema`
- merge order hint: after V042-001.

Goal Contract Status: `not_generated_by_to_issues`.

Goal Contract Missing Fields:

- Exact required fields per schema.
- `$id` naming convention.

Runtime Missing Fields:

- None.

Ready-for-Agent Missing Fields:

- Confirm whether schema validation dependency is allowed.

Triage Recommendation Candidate: `ready-for-agent candidate after V042-001`.

---

### V042-003: Score JSON writer and schema validation helper

Goal:
Add a schema validation helper and score JSON writer that can validate per-case score output without requiring Codex runtime.

Acceptance Criteria:

- Add `evals/schema_validation.py` or accepted equivalent.
- Add `evals/scoring.py` or accepted equivalent.
- Add sample score fixture(s) under `evals/fixtures/score/` or equivalent.
- Score JSON includes route, evidence, output contract, behavior verdict, checker results, and normalized overall verdict.
- Schema errors are surfaced as fail/blocked, not silently ignored.
- `evals/run_runtime.py --validate-schema --suite trace-first-verify-review.csv` remains compatible.
- Existing `summary.json` and `routing_summary` are not removed or renamed.

Evidence / Source:

- Roadmap PRD FR-422 and FR-423.
- V042-002 product schemas.
- Current runner result model.

Blockers:

- V042-002.

Execution: AFK harness implementation slice.

Contract Impact:

- score JSON generation
- schema validation
- runner compatibility

Verification Evidence Needed:

```bash
python evals/run_runtime.py --validate-schema --suite trace-first-verify-review.csv
python -m unittest evals.test_run_runtime_scheduler
git diff --check
```

Implementation Task Type Candidate: `write_implementation`.

Implementation Runtime Candidate: `triage_required`.

Product Runtime Covered: `score_json_foundation`.

Isolation Needed:

- context: `none unless runner changes are broad`
- filesystem: `current_workspace`
- diff surface: `required`

Parallelization Candidate:

- eligible: limited
- conflict group: `v042-score-writer`
- dependency group: `v042-schema`
- merge order hint: after V042-002.

Goal Contract Status: `not_generated_by_to_issues`.

Goal Contract Missing Fields:

- Whether score JSON is written by default or behind a flag.

Runtime Missing Fields:

- Codex runtime not required for schema-only validation.

Ready-for-Agent Missing Fields:

- Decide sample fixture location.

Triage Recommendation Candidate: `ready-for-agent candidate after V042-002`.

---

### V042-004: Metrics docs and compatibility update

Goal:
Document the v0.4.2 score fields and preserve compatibility with current metrics consumers.

Acceptance Criteria:

- Update `docs/skill-success-metrics.md` with schema-backed score fields.
- Explain relationship between `trace_ready_rows`, legacy-compatible `routing_rows`, and `routing_summary`.
- Document `review` as lens/schema mode, not a public skill.
- Document that schema score is not runtime evidence.
- Add migration notes for any renamed or aliased fields.

Evidence / Source:

- Roadmap PRD FR-423.
- V042-001 through V042-003.
- Existing metrics docs.

Blockers:

- V042-003 recommended.

Execution: AFK docs slice.

Contract Impact:

- metrics vocabulary
- maintainer docs
- compatibility note

Verification Evidence Needed:

```bash
git diff --check
python evals/run_runtime.py --validate-schema --suite trace-first-verify-review.csv
```

Implementation Task Type Candidate: `write_implementation`.

Implementation Runtime Candidate: `main_thread_direct`.

Product Runtime Covered: `metrics_documentation`.

Isolation Needed:

- context: `none`
- filesystem: `current_workspace`
- diff surface: `required`

Parallelization Candidate:

- eligible: yes after V042-003 shape is stable
- conflict group: `v042-metrics-docs`
- dependency group: `v042-docs`
- merge order hint: after score fields are known.

Goal Contract Status: `not_generated_by_to_issues`.

Goal Contract Missing Fields:

- Final score field names.

Runtime Missing Fields:

- None.

Ready-for-Agent Missing Fields:

- None after V042-003.

Triage Recommendation Candidate: `ready-for-agent candidate after V042-003`.

---

## v0.4.3 — Modular Deterministic Checks and Behavior Hardening

### V043-001: Extract deterministic checks package

Goal:
Move high-value deterministic checks out of monolithic runner logic into reusable modules while preserving current behavior.

Acceptance Criteria:

- Add `evals/checks/` package or accepted equivalent.
- Preserve checks for verify scope, QA failure shape, gate fields, artifact header, `git add .`, lifecycle artifacts, route verdicts, and trace-ready hard negatives.
- Keep `evals/run_runtime.py` as the orchestrator rather than duplicating scoring logic.
- Add checker ids and notes that can later appear in score JSON.
- Existing unit tests continue to pass.

Evidence / Source:

- Roadmap PRD FR-431.
- Current `evals/run_runtime.py` inline checks.
- V042 score JSON contract.

Blockers:

- V042-003 should land first.

Execution: AFK harness refactor slice.

Contract Impact:

- deterministic checks
- runner internals
- score JSON checker output

Verification Evidence Needed:

```bash
python -m unittest evals.test_run_runtime_scheduler
python evals/run_runtime.py --validate-schema --suite trace-first-verify-review.csv
git diff --check
```

Implementation Task Type Candidate: `write_implementation`.

Implementation Runtime Candidate: `triage_required`.

Product Runtime Covered: `deterministic_eval_checks`.

Isolation Needed:

- context: `none unless triage selects isolation`
- filesystem: `current_workspace unless triage selects isolation`
- diff surface: `required`

Parallelization Candidate:

- eligible: no
- conflict group: `v043-check-extraction`
- dependency group: `v043-checks`
- merge order hint: first v0.4.3 slice.

Goal Contract Status: `not_generated_by_to_issues`.

Goal Contract Missing Fields:

- Exact module boundaries.

Runtime Missing Fields:

- Runtime eval optional.

Ready-for-Agent Missing Fields:

- Mapping of inline functions to target modules.

Triage Recommendation Candidate: `ready-for-agent candidate after V042-003`.

---

### V043-002: Named forbidden behavior checks for trace-ready rows

Goal:
Turn v0.4.1 hard-negative behavior checks into named, testable deterministic checks.

Acceptance Criteria:

- Add named checker for code-diff-only readiness pass claims.
- Add named checker for low-risk exception archive or branch cleanup readiness claims.
- Add named checker for invented contract fields if fixture support exists.
- Add named checker for missing target reader in durable artifacts.
- Add named checker for positive `git add .` suggestion if not already named.
- Checks handle negated and conditional safe wording.
- Checks return checker ids and failure notes.

Evidence / Source:

- Roadmap PRD FR-432.
- Codex review feedback from PR #63.
- Current tests added for v0.4.1 hard negatives.

Blockers:

- V043-001.

Execution: AFK checker implementation slice.

Contract Impact:

- behavior verdict
- checker ids
- regression coverage

Verification Evidence Needed:

```bash
python -m unittest evals.test_run_runtime_scheduler
python evals/run_runtime.py --validate-schema --suite trace-first-verify-review.csv
git diff --check
```

Implementation Task Type Candidate: `write_implementation`.

Implementation Runtime Candidate: `main_thread_direct`.

Product Runtime Covered: `forbidden_behavior_detection`.

Isolation Needed:

- context: `none`
- filesystem: `current_workspace`
- diff surface: `required`

Parallelization Candidate:

- eligible: yes after V043-001 module shape exists
- conflict group: `v043-forbidden-checks`
- dependency group: `v043-checks`
- merge order hint: after checker package exists.

Goal Contract Status: `not_generated_by_to_issues`.

Goal Contract Missing Fields:

- Checker id naming convention.

Runtime Missing Fields:

- None.

Ready-for-Agent Missing Fields:

- Decide whether invented-contract checker belongs in v0.4.3 or later fixture expansion.

Triage Recommendation Candidate: `ready-for-agent candidate after V043-001`.

---

### V043-003: Checker unit test expansion

Goal:
Add focused unit tests for deterministic check behavior, including positive, negative, negated, and conditional cases.

Acceptance Criteria:

- Add tests for code-diff-only readiness claim detection.
- Add tests for safe code-diff-only negative wording.
- Add tests for low-risk cleanup readiness claim detection.
- Add tests for safe downstream/conditional cleanup wording.
- Add tests for `git add .` positive and negated wording if coverage is incomplete.
- Add tests for target reader or artifact header check if coverage is incomplete.
- Test names reflect checker ids.

Evidence / Source:

- Roadmap PRD v0.4.3 exit criteria.
- Existing `evals/test_run_runtime_scheduler.py`.

Blockers:

- V043-001 and V043-002.

Execution: AFK test slice.

Contract Impact:

- test coverage
- checker behavior stability

Verification Evidence Needed:

```bash
python -m unittest evals.test_run_runtime_scheduler
git diff --check
```

Implementation Task Type Candidate: `write_implementation`.

Implementation Runtime Candidate: `main_thread_direct`.

Product Runtime Covered: `checker_regression_tests`.

Isolation Needed:

- context: `none`
- filesystem: `current_workspace`
- diff surface: `required`

Parallelization Candidate:

- eligible: yes after checker APIs stabilize
- conflict group: `v043-check-tests`
- dependency group: `v043-checks`
- merge order hint: after or alongside V043-002.

Goal Contract Status: `not_generated_by_to_issues`.

Goal Contract Missing Fields:

- Final checker module import paths.

Runtime Missing Fields:

- None.

Ready-for-Agent Missing Fields:

- None after V043-002.

Triage Recommendation Candidate: `ready-for-agent candidate after V043-002`.

---

### V043-004: Trace-ready checker docs and fixture notes

Goal:
Document deterministic checker semantics so future fixture authors know which failures are semantic and which are prose-only.

Acceptance Criteria:

- Update `docs/skill-success-metrics.md` or add `docs/eval-deterministic-checks.md`.
- Document checker ids, applies-to scope, pass/fail semantics, and examples.
- Explain that `forbidden_behavior` prose is not enough unless a deterministic checker or literal-match rule exists.
- Include guidance for adding future trace-ready rows.

Evidence / Source:

- V043-001 through V043-003.
- PR #63 bot feedback pattern.

Blockers:

- V043-002.

Execution: AFK docs slice.

Contract Impact:

- maintainer docs
- fixture authoring guidance

Verification Evidence Needed:

```bash
git diff --check
python evals/run_runtime.py --validate-schema --suite trace-first-verify-review.csv
```

Implementation Task Type Candidate: `write_implementation`.

Implementation Runtime Candidate: `main_thread_direct`.

Product Runtime Covered: `checker_documentation`.

Isolation Needed:

- context: `none`
- filesystem: `current_workspace`
- diff surface: `required`

Parallelization Candidate:

- eligible: yes after checker semantics are stable
- conflict group: `v043-check-docs`
- dependency group: `v043-docs`
- merge order hint: after checker ids are final.

Goal Contract Status: `not_generated_by_to_issues`.

Goal Contract Missing Fields:

- Final checker id list.

Runtime Missing Fields:

- None.

Ready-for-Agent Missing Fields:

- None after V043-002.

Triage Recommendation Candidate: `ready-for-agent candidate after V043-002`.

---

## v0.4.4 — Trace Artifacts, Diagnostics, Reports, and Patch Suggestions

### V044-001: Trace artifact layout and redaction policy

Goal:
Define and optionally implement the promoted artifact layout for raw traces, final outputs, score JSON, summaries, reports, and patch suggestions.

Acceptance Criteria:

- Add `docs/eval-trace-artifacts.md` or accepted equivalent.
- Define optional promoted layout under `artifacts/evals/<run-id>/`.
- Explain relationship to runtime scratch such as `.groundwork/harness/`.
- Define redaction status and promotion rules.
- Define forbidden content patterns for promoted traces.
- State that raw trace promotion is optional and not required for every local run.

Evidence / Source:

- Roadmap PRD FR-441.
- Existing nightly harness docs.
- Prior research recommendation for safe nightly evaluation.

Blockers:

- V042-003 score JSON contract recommended.

Execution: AFK docs/light implementation slice.

Contract Impact:

- eval artifact contract
- redaction boundary
- maintainer workflow

Verification Evidence Needed:

```bash
git diff --check
python evals/run_runtime.py --validate-schema --suite trace-first-verify-review.csv
```

Implementation Task Type Candidate: `write_implementation`.

Implementation Runtime Candidate: `main_thread_direct`.

Product Runtime Covered: `trace_artifact_governance`.

Isolation Needed:

- context: `none`
- filesystem: `current_workspace`
- diff surface: `required`

Parallelization Candidate:

- eligible: yes
- conflict group: `v044-trace-artifacts`
- dependency group: `v044-trace`
- merge order hint: first v0.4.4 slice.

Goal Contract Status: `not_generated_by_to_issues`.

Goal Contract Missing Fields:

- Whether runner writes directly to `artifacts/evals/` or copies promoted outputs there.

Runtime Missing Fields:

- Raw runtime trace examples optional.

Ready-for-Agent Missing Fields:

- Maintainer decision on artifact promotion path.

Triage Recommendation Candidate: `ready-for-agent candidate after V042-003`.

---

### V044-002: Trace diagnostics parser

Goal:
Parse available raw JSONL trace data into diagnostics without assuming stable event shapes.

Acceptance Criteria:

- Add `evals/checks/trace_diagnostics.py` or accepted equivalent.
- Parser tolerates unknown event shapes.
- Extract command count when events are recognizable.
- Extract duplicate command count when commands are recognizable.
- Extract failed command count when exit/result signals are recognizable.
- Compute evidence latency when evidence event or final-output marker is recognizable.
- Compute trace thrashing using a conservative heuristic.
- Emit `unknown` or `not_applicable` rather than failing when trace event shape is unsupported.

Evidence / Source:

- Roadmap PRD FR-442.
- V044-001 trace artifact policy.

Blockers:

- V044-001.

Execution: AFK parser implementation slice.

Contract Impact:

- diagnostics schema
- score JSON diagnostics
- report inputs

Verification Evidence Needed:

```bash
python -m unittest evals.test_trace_diagnostics
python evals/run_runtime.py --validate-schema --suite trace-first-verify-review.csv
git diff --check
```

Implementation Task Type Candidate: `write_implementation`.

Implementation Runtime Candidate: `main_thread_direct` for fixtures; `triage_required` for runtime-backed samples.

Product Runtime Covered: `trace_diagnostics`.

Isolation Needed:

- context: `none`
- filesystem: `current_workspace`
- diff surface: `required`

Parallelization Candidate:

- eligible: yes after V044-001
- conflict group: `v044-trace-diagnostics`
- dependency group: `v044-trace`
- merge order hint: before report generation.

Goal Contract Status: `not_generated_by_to_issues`.

Goal Contract Missing Fields:

- Sample trace fixtures.
- Initial thrashing thresholds.

Runtime Missing Fields:

- Real Codex trace variants can be backfilled later.

Ready-for-Agent Missing Fields:

- Decide fixture format for trace parser tests.

Triage Recommendation Candidate: `ready-for-agent candidate after V044-001`.

---

### V044-003: Eval report generator

Goal:
Generate a human-readable eval report from summary, results, score JSON, deterministic checks, and diagnostics.

Acceptance Criteria:

- Add `evals/report.py` or accepted equivalent.
- Report includes run metadata, suite list, counts, route metrics, score validation, deterministic failures, diagnostics, top regressions, and limitations.
- Report works from sample fixtures or a local run directory.
- Report does not edit skills, docs, evals, branches, remotes, PRs, or trackers.
- Report states whether runtime evidence is present, absent, or not applicable.

Evidence / Source:

- Roadmap PRD FR-443.
- V042 score JSON.
- V043 deterministic checks.
- V044 trace diagnostics.

Blockers:

- V042-003.
- V044-002 recommended.

Execution: AFK reporting slice.

Contract Impact:

- eval report artifact
- maintainer workflow

Verification Evidence Needed:

```bash
python evals/report.py <sample-run-or-summary>
git diff --check
```

Implementation Task Type Candidate: `write_implementation`.

Implementation Runtime Candidate: `main_thread_direct`.

Product Runtime Covered: `eval_reporting`.

Isolation Needed:

- context: `none`
- filesystem: `current_workspace`
- diff surface: `required`

Parallelization Candidate:

- eligible: yes after score JSON exists
- conflict group: `v044-eval-report`
- dependency group: `v044-reporting`
- merge order hint: after score shape is stable.

Goal Contract Status: `not_generated_by_to_issues`.

Goal Contract Missing Fields:

- CLI argument shape.
- Sample run fixture path.

Runtime Missing Fields:

- Runtime sample optional.

Ready-for-Agent Missing Fields:

- Decide whether report generation is separate or called by runner.

Triage Recommendation Candidate: `ready-for-agent candidate after V042-003`.

---

### V044-004: Patch suggestion artifact

Goal:
Emit safe patch suggestion artifacts from eval failures without modifying repository files automatically.

Acceptance Criteria:

- Add `patch-suggestions.json` output shape.
- Each suggestion includes id, triggering cases, failure type, fix locus, proposed summary, affected files, rollback, human decision, and `auto_apply: false`.
- Suggestions are generated only from reproducible fixtures or classified failures.
- Suggestions never mutate skills, docs, evals, branches, remotes, PRs, or trackers.
- Report links or summarizes patch suggestions.

Evidence / Source:

- Roadmap PRD FR-443.
- Existing patch proposal rule in `docs/skill-success-metrics.md`.
- Prior research recommendation for nightly evaluation plus proposal-only learning.

Blockers:

- V044-003.

Execution: AFK reporting/safety slice.

Contract Impact:

- safe learning loop
- patch suggestion artifact

Verification Evidence Needed:

```bash
python evals/report.py <sample-run-or-summary>
git diff --check
```

Implementation Task Type Candidate: `write_implementation`.

Implementation Runtime Candidate: `main_thread_direct`.

Product Runtime Covered: `patch_suggestion_artifacts`.

Isolation Needed:

- context: `none`
- filesystem: `current_workspace`
- diff surface: `required`

Parallelization Candidate:

- eligible: no
- conflict group: `v044-patch-suggestions`
- dependency group: `v044-reporting`
- merge order hint: after report generator.

Goal Contract Status: `not_generated_by_to_issues`.

Goal Contract Missing Fields:

- Suggestion schema fields after score/report contracts settle.

Runtime Missing Fields:

- None.

Ready-for-Agent Missing Fields:

- Decide whether `patch-suggestions.json` is emitted for pass runs with no suggestions.

Triage Recommendation Candidate: `ready-for-agent candidate after V044-003`.

---

## v0.4.5 — CI Minimum Gate and Release Evidence Policy

### V045-001: Schema-only CI gate

Goal:
Add or document a CI-equivalent gate that validates schemas and prompt CSVs without secrets or Codex runtime.

Acceptance Criteria:

- Add `.github/workflows/evals.yml` or `docs/ci-eval-gate.md` if workflow addition is deferred.
- CI or documented local gate runs schema validation without secrets.
- CI or documented local gate parses prompt CSVs.
- CI or documented local gate compiles Python runner files.
- Gate does not require Codex runtime.
- Gate does not claim runtime readiness.

Evidence / Source:

- Roadmap PRD FR-451.
- PR #63 validation commands.
- V042 schemas.

Blockers:

- V042-003.

Execution: AFK CI/docs slice.

Contract Impact:

- CI gate
- maintainer validation workflow

Verification Evidence Needed:

```bash
git diff --check
python -m py_compile evals/run_runtime.py
python evals/run_runtime.py --validate-schema --suite trace-first-verify-review.csv
```

Implementation Task Type Candidate: `write_implementation`.

Implementation Runtime Candidate: `main_thread_direct`.

Product Runtime Covered: `ci_schema_gate`.

Isolation Needed:

- context: `none`
- filesystem: `current_workspace`
- diff surface: `required`

Parallelization Candidate:

- eligible: yes after schema foundation
- conflict group: `v045-ci-schema`
- dependency group: `v045-ci`
- merge order hint: first v0.4.5 slice.

Goal Contract Status: `not_generated_by_to_issues`.

Goal Contract Missing Fields:

- Maintainer decision on GitHub Actions versus docs-only local gate.

Runtime Missing Fields:

- Runtime secrets intentionally not required.

Ready-for-Agent Missing Fields:

- Repository CI convention decision.

Triage Recommendation Candidate: `ready-for-agent candidate after V042-003`.

---

### V045-002: Optional runtime eval gate documentation

Goal:
Document how maintainers can run runtime Codex evals as opt-in evidence without making them required for default CI.

Acceptance Criteria:

- Add runtime eval command examples.
- Document required installed plugin root evidence.
- Document source/cache equivalence or supported refresh step.
- Document run scope, limitations, and missing evidence fields.
- State runtime eval is optional unless a release gate explicitly requires it.
- State runtime eval output must not be committed without redaction review.

Evidence / Source:

- Roadmap PRD FR-452.
- Existing release evidence claim boundaries from v0.4.0 work.

Blockers:

- V045-001 recommended.

Execution: AFK docs slice.

Contract Impact:

- runtime evidence policy
- release gate docs

Verification Evidence Needed:

```bash
git diff --check
```

Implementation Task Type Candidate: `write_implementation`.

Implementation Runtime Candidate: `main_thread_direct`.

Product Runtime Covered: `runtime_eval_evidence_policy`.

Isolation Needed:

- context: `none`
- filesystem: `current_workspace`
- diff surface: `required`

Parallelization Candidate:

- eligible: yes
- conflict group: `v045-runtime-docs`
- dependency group: `v045-release-evidence`
- merge order hint: after or alongside V045-001.

Goal Contract Status: `not_generated_by_to_issues`.

Goal Contract Missing Fields:

- Exact installed plugin path examples for supported environments.

Runtime Missing Fields:

- Real runtime evidence out of scope for docs-only slice.

Ready-for-Agent Missing Fields:

- Confirm supported runtime invocation examples.

Triage Recommendation Candidate: `ready-for-agent candidate`.

---

### V045-003: Release evidence claim template

Goal:
Add a structured template for release evidence claims so docs/schema/source checks cannot be mistaken for runtime or release readiness.

Acceptance Criteria:

- Add `docs/release-evidence-claim-boundary.md` or equivalent.
- Define required fields: claim type, evidence status, installed plugin root, source root, refresh/equivalence method, run scope, commands/trials, limitations, and missing evidence.
- State that docs/schema/source checks alone are `source_validation`, not `runtime_verified`.
- State that UAT/customer readiness requires separate UAT/customer evidence.
- Include a minimal example for v0.4.x eval release claims.

Evidence / Source:

- Roadmap PRD FR-452.
- v0.4.0 release evidence claim boundary.
- PR #63 evidence boundary notes.

Blockers:

- None, but best after V045-001/V045-002.

Execution: AFK docs slice.

Contract Impact:

- release evidence policy
- maintainer review workflow

Verification Evidence Needed:

```bash
git diff --check
```

Implementation Task Type Candidate: `write_implementation`.

Implementation Runtime Candidate: `main_thread_direct`.

Product Runtime Covered: `release_evidence_claims`.

Isolation Needed:

- context: `none`
- filesystem: `current_workspace`
- diff surface: `required`

Parallelization Candidate:

- eligible: yes
- conflict group: `v045-release-evidence-template`
- dependency group: `v045-release-evidence`
- merge order hint: before release docs finalization.

Goal Contract Status: `not_generated_by_to_issues`.

Goal Contract Missing Fields:

- Exact claim type enum.

Runtime Missing Fields:

- None for template.

Ready-for-Agent Missing Fields:

- None.

Triage Recommendation Candidate: `ready-for-agent candidate`.

---

### V045-004: v0.4.x release docs and changelog update

Goal:
Update docs and changelog to reflect the completed v0.4.x eval platform increment without overclaiming runtime readiness.

Acceptance Criteria:

- Update `CHANGELOG.md` only after implementation evidence exists.
- Update README current stage only if maintainers decide the eval platform is user-visible enough.
- Link to score/schema/check/report docs.
- State exact runtime evidence status.
- State deferred v0.5.0 promotion criteria if full platform promotion is not complete.
- Do not claim release readiness from local source checks alone.

Evidence / Source:

- V045-001 through V045-003.
- Actual implementation validation results.

Blockers:

- Should land last for v0.4.5.

Execution: AFK release docs slice.

Contract Impact:

- changelog
- README/current stage
- release notes

Verification Evidence Needed:

```bash
git diff --check
python evals/run_runtime.py --validate-schema --suite trace-first-verify-review.csv
```

Implementation Task Type Candidate: `write_implementation`.

Implementation Runtime Candidate: `main_thread_direct`.

Product Runtime Covered: `release_docs`.

Isolation Needed:

- context: `none`
- filesystem: `current_workspace`
- diff surface: `required`

Parallelization Candidate:

- eligible: no
- conflict group: `v045-release-docs`
- dependency group: `v045-release`
- merge order hint: final v0.4.5 slice.

Goal Contract Status: `not_generated_by_to_issues`.

Goal Contract Missing Fields:

- Final validation commands and evidence paths.

Runtime Missing Fields:

- Depends on whether runtime eval was performed.

Ready-for-Agent Missing Fields:

- Implementation evidence from prior slices.

Triage Recommendation Candidate: `needs-info recommendation until release evidence exists`.

---

## Cross-version Dependency Map

```text
V042-001 -> V042-002 -> V042-003 -> V042-004
                         |
                         v
                   V043-001 -> V043-002 -> V043-003 -> V043-004
                         |
                         v
                   V044-001 -> V044-002 -> V044-003 -> V044-004
                         |
                         v
                   V045-001 -> V045-002 -> V045-003 -> V045-004
```

---

## Minimal Next Step

Run `triage` on V042-001 and V042-002 together only if the maintainer is ready to decide schema location and JSON Schema draft. Otherwise start with V042-001 alone.

---

## Artifact Recommendation

Keep this issue pack as the local canonical planning artifact at `artifacts/v0.4.x-trace-first-eval-platform-roadmap/issue-map.md`. Do not create remote tracker issues until the maintainer decides which slices should become GitHub issues or implementation PRs.
