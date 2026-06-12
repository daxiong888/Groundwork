# Groundwork Routing Reliability Issue Pack

Target Reader: Groundwork maintainer or Codex agent executing the routing-reliability increment one goal at a time.
Reader Action Needed: Use these tracker-neutral RR issue drafts as the source for implementation goals, local planning, or manual tracker entry.
Decision Supported: Which RR slice is ready for an implementation goal, what it may touch, what it must not touch, and what evidence closes it.
Scope: RR-001 through RR-010 for the accepted routing reliability PRD.
Out of Scope: Creating remote tracker issues, committing code, changing public skill surfaces without targeted evidence, default-suite promotion before a targeted baseline, learned routing, retrieval/rerank pilots, MCP/A2A pilots, observability backends, and installed plugin cache mutation by hand.
Evidence Level: Derived from accepted `docs/prd-routing-reliability.md`; no runtime evidence is added by this issue pack.

## Issue Set Summary

Source:

- Canonical source: `docs/prd-routing-reliability.md`
- Requirement state: `prd_accepted / issue_ready`
- Issue pack status: tracker-neutral local artifact

Batching:

- First batch: RR-001 through RR-006. These are runner/eval mechanics and can each be used as one Codex goal.
- Second batch: RR-007 through RR-010. These depend on first-batch evidence and cover docs, baseline, conditional runtime-surface adjustment, and default-suite promotion.

Execution rule:

- Start with RR-001.
- Do not merge RR-002 into RR-001 unless schema validation cannot be tested without a seed row.
- Do not start RR-009 unless RR-008 or targeted reruns prove a runtime-visible surface is the correct fix locus.
- Do not start RR-010 until the targeted baseline is stable and promotion is explicitly under review.

## Issue Drafts

### RR-001: Schema parse and validation dry path

Goal:
Implement routing-reliability schema parsing and validation in `evals/run_runtime.py` without invoking Codex runtime or changing public skill/runtime-visible text.

Acceptance Criteria:

- `evals/run_runtime.py` can parse and validate routing-reliability rows through a dry validation path.
- Schema validation recognizes `intent_kind`, `requirement_state`, `source_truth`, `risk_gate`, `expected_state_transition`, `expected_stop_condition`, `expected_best`, `acceptable_routes`, `forbidden_routes`, `route_boundary`, `case_kind`, `case_source`, `output_contract`, and `evidence_required`.
- Route precedence is implemented: `expected_best`, then `expected_skill`, then `should_trigger=false` route hint or direct fallback, then `skill`, then `direct`.
- Route validation rejects unknown routes, malformed route list cells, overlapping acceptable/forbidden routes, `blocked` in route-list fields, and `runtime-safety-gate` as `expected_best`.
- `host_preemption_allowed` controls only whether `runtime-safety-gate` may be classified as `actual_route`; pass/fail remains owned by route lists and `host_preemption_verdict`.
- Missing legacy Intent Frame fields are marked `not_applicable`, not `blocked`, outside `routing-reliability.csv`.
- Schema validation recognizes first-slice implemented tokens and allowed future tokens; unknown tokens block the row.
- No `.codex-plugin/plugin.json`, public skill frontmatter, shared lifecycle-preflight text, or `DEFAULT_SUITES` entry is changed.

Evidence / Source:

- `docs/prd-routing-reliability.md` AC-FS-1 through AC-FS-8.
- `docs/prd-routing-reliability.md` sections 8.2, 8.3, 8.4, and 13.

Blockers:

- None known.

Execution: AFK.

Contract Impact:

- Verification contract: routing fixture schema and runner validation behavior.
- Public skill surface: none.

Verification Evidence Needed:

- `git diff --check`
- CSV parse for existing prompt suites.
- Focused runner dry validation covering valid route lists, malformed route lists, `blocked` route-list rejection, `runtime-safety-gate` expected-best rejection, unknown token blocking, and legacy-row `not_applicable` behavior.
- `git status --short` before and after edits.

Ready-for-Agent Missing Fields:

- None. The implementer may choose the dry validation flag/name if no existing runner pattern fits, but the choice must be visible in runner help or output.

Triage Recommendation Candidate:

- ready-for-agent candidate

### RR-002: Add targeted routing-reliability.csv seed suite

Goal:
Add a targeted-only `evals/prompts/routing-reliability.csv` seed suite with enough rows to exercise the first route boundaries and the new schema.

Acceptance Criteria:

- `evals/prompts/routing-reliability.csv` exists and is not added to `DEFAULT_SUITES`.
- The file has at least 20 targeted rows using `rr-###` ids.
- Rows include `route_boundary`, `case_kind`, `case_source`, Intent Frame fields, entry decision fields, `expected_best`, `acceptable_routes`, and `forbidden_routes`.
- Seed coverage includes `entry-contract`, `requirement-state-vs-implementation`, `explicit-bypass-vs-raw-intent`, `implement-vs-verify`, `prototype-vs-verify`, and `runtime-safety-gate-vs-skill-gate`.
- Raw requirement rows forbid `implement|write-plan|to-issues`.
- Explicit PRD bypass rows allow `implement` and still require lifecycle/git/test/risk-gate behavior.
- Host-preemption rows distinguish `runtime-safety-gate` from skill-owned gate output.

Evidence / Source:

- `docs/prd-routing-reliability.md` AC-RG-1 and AC-RG-2.
- `docs/prd-routing-reliability.md` sections 8.1, 8.5, and 13.

Blockers:

- RR-001 should land first if the new CSV needs automated validation.

Execution: AFK.

Contract Impact:

- Verification contract: new targeted prompt suite.
- Runtime/default suite: none.

Verification Evidence Needed:

- CSV parse check.
- Duplicate id check across prompt CSVs.
- RR-001 dry validation, if available.
- Manual sample review confirming raw intent and explicit bypass route boundaries.
- `git diff --check`

Ready-for-Agent Missing Fields:

- None. Exact prompt wording is implementer-owned but must stay grounded in PRD route boundaries.

Triage Recommendation Candidate:

- ready-for-agent candidate after RR-001

### RR-003: Actual route classification and strict host preemption

Goal:
Extend actual-route classification so runner output distinguishes public skill hits, direct fallback, and strict `runtime-safety-gate` host preemption.

Acceptance Criteria:

- Public skill hits remain the public route and are not reclassified as host preemption.
- No-skill rows remain `direct` unless all strict host-preemption conditions pass.
- `actual_route=runtime-safety-gate` is allowed only when no public skill loads, row metadata allows host-preemption classification, risky/destructive/remote/data/write intent is present, `changed_files == []`, and the final response contains gate/no-execution approval shape.
- `skill_load_required=false` alone does not imply `runtime-safety-gate`.
- Skill-owned approval gate output remains under the owning public route and is judged by output/behavior verdicts.

Evidence / Source:

- `docs/prd-routing-reliability.md` AC-PM-6 and AC-RG-3.
- `docs/prd-routing-reliability.md` sections 7.5, 8.2, 8.4, and 13.

Blockers:

- RR-002 seed rows should exist for targeted host-preemption and skill-owned gate cases.

Execution: AFK.

Contract Impact:

- Verification contract: actual-route classification.
- Public skill surface: none.

Verification Evidence Needed:

- Targeted checks for public skill hit, direct fallback, valid host preemption, invalid host preemption, and skill-owned gate output.
- Source snapshot or changed-file detection evidence for host-preemption rows.
- `git diff --check`

Ready-for-Agent Missing Fields:

- Requires RR-002 rows or equivalent local fixtures to exercise the five classification cases.

Triage Recommendation Candidate:

- ready-for-agent candidate after RR-002

### RR-004: Multidimensional verdict model

Goal:
Emit separate routing, host-preemption, output, evidence, behavior, and overall verdict dimensions for each evaluated row.

Acceptance Criteria:

- Per-row JSON includes `routing_verdict`, `host_preemption_verdict`, `output_contract_verdict`, `evidence_verdict`, `behavior_verdict`, and `overall_verdict`.
- Per-row JSON includes trace-ready metadata: id, suite, route boundary, case kind, case source, expected route, actual route, acceptable routes, forbidden routes, notes, `failure_type`, and `fix_locus`.
- Implemented output/evidence tokens have deterministic checks in runtime verdict slices.
- Allowed future tokens return `blocked` until implemented.
- Premature implementation, invalid host preemption, output-contract failure, evidence failure, direct fallback ceremony, and forbidden route hit are distinguishable outcomes.
- Overall pass requires no forbidden route, no invalid host preemption, no forbidden behavior, and no required output/evidence failure.

Evidence / Source:

- `docs/prd-routing-reliability.md` AC-FS-6b, AC-RG-4, AC-RG-5, and AC-RG-7.
- `docs/prd-routing-reliability.md` sections 7.10, 7.11, 8.3, 8.6, and 8.7.

Blockers:

- RR-003 should land first so host-preemption verdicts can consume correct `actual_route` classification.

Execution: AFK.

Contract Impact:

- Verification contract: per-row verdict model and failure feedback.
- Runner output contract: JSON field shape.

Verification Evidence Needed:

- Targeted rows producing each verdict dimension.
- At least one non-pass row that proves `failure_type` and `fix_locus` are populated.
- Checks proving future tokens return `blocked` rather than pass.
- `git diff --check`

Ready-for-Agent Missing Fields:

- None after RR-003, assuming RR-002 includes enough targeted rows.

Triage Recommendation Candidate:

- ready-for-agent candidate after RR-003

### RR-005: Summary metrics and route-pair reporting

Goal:
Add summary reporting for targeted routing reliability runs, including route-pair confusion and targeted internal gate metrics.

Acceptance Criteria:

- Runner summaries expose Best-route Hit@1, acceptable coverage, forbidden route hits, invalid host preemption, route-vs-execution separability, per-boundary counts, per-route counts, and a compact route-pair confusion table.
- Summary output distinguishes best, acceptable, forbidden, missing, and unexpected routing outcomes.
- Summary output distinguishes host-preemption, output-contract, evidence, behavior, and overall verdict counts.
- No unclassified non-pass row is allowed in targeted gate output.
- Metrics remain internal gate guardrails and do not introduce public SLA or numeric first-slice SLO language.

Evidence / Source:

- `docs/prd-routing-reliability.md` AC-RG-6 and AC-RG-10.
- `docs/prd-routing-reliability.md` sections 8.6 and 8.8.

Blockers:

- RR-004 should land first because summary output depends on per-row verdict fields.

Execution: AFK.

Contract Impact:

- Verification contract: run summary and metrics output.
- Public skill surface: none.

Verification Evidence Needed:

- Targeted runner output showing all summary fields.
- Route-pair table or equivalent route-drift report.
- Check showing non-pass rows are classified.
- `git diff --check`

Ready-for-Agent Missing Fields:

- None after RR-004.

Triage Recommendation Candidate:

- ready-for-agent candidate after RR-004

### RR-006: Parallel wrapper aggregation compatibility

Goal:
Keep serial runner as the owner of route judgment while making `evals/run_runtime_parallel.py` aggregate the new per-row verdict dimensions.

Acceptance Criteria:

- Parallel wrapper consumes serial per-row verdict fields.
- Parallel wrapper aggregates routing, host-preemption, output, evidence, behavior, and overall verdict counts without duplicating route judgment.
- Targeted serial and parallel smoke runs agree on row verdict fields for the same input rows.
- Parallel/default execution policy remains conservative unless metadata proves selected rows are concurrency-safe.

Evidence / Source:

- `docs/prd-routing-reliability.md` AC-RG-8.
- `docs/prd-routing-reliability.md` sections 8.6 and 13.

Blockers:

- RR-005 should land first so the serial output fields and summary vocabulary are stable enough to aggregate.

Execution: AFK.

Contract Impact:

- Verification contract: parallel wrapper aggregation.
- Runtime/default suite: none unless explicitly scoped later.

Verification Evidence Needed:

- Targeted serial smoke output.
- Targeted parallel smoke output.
- Comparison showing row verdict fields agree.
- `git diff --check`

Ready-for-Agent Missing Fields:

- None after RR-005.

Triage Recommendation Candidate:

- ready-for-agent candidate after RR-005

### RR-007: Docs, skill-success metrics, and runtime checklist update

Goal:
Update maintainer-facing docs so the new routing reliability schema, verdicts, metrics, and regression governance are documented after runner behavior exists.

Acceptance Criteria:

- `evals/runtime-trial-checklist.md` documents targeted-before-default routing suite behavior, runtime truth alignment, source/cache evidence expectations, and default-promotion decision handling.
- `docs/skill-success-metrics.md` or an existing metrics doc documents targeted internal gate metrics without public SLA language.
- Docs explain finite measurement tokens, `blocked` normalization, strict host-preemption classification, regression owner/action/sample-backfill decisions, and deferred pilot boundaries.
- Docs preserve the no-new-public-skill rule and direct fallback boundary.

Evidence / Source:

- `docs/prd-routing-reliability.md` AC-DP-4 and AC-DP-5.
- `docs/prd-routing-reliability.md` sections 8.8, 8.9, 8.10, 8.11, and 13.

Blockers:

- RR-001 through RR-006 should land first so docs reflect actual runner behavior.

Execution: AFK.

Contract Impact:

- Documentation and verification contract.
- Public skill surface: none.

Verification Evidence Needed:

- `git diff --check`
- Plugin JSON parse if touched, though it should not be touched in this issue.
- CSV parse check.
- Stale-state sweep for old metric names, old acceptance ids, unsupported `blocked` route wording, and deferred pilot language.

Ready-for-Agent Missing Fields:

- Exact doc section placement can be chosen during implementation based on current file structure.

Triage Recommendation Candidate:

- ready-for-agent candidate after RR-006

### RR-008: Targeted baseline with cache/source equivalence

Goal:
Record a targeted routing reliability baseline with runtime evidence and cache/source equivalence proof or supported cache refresh.

Acceptance Criteria:

- A baseline file under `evals/baselines/` records the targeted routing run.
- Baseline includes current branch, `git status --short`, intended file allowlist, installed plugin root, source package root, compared path list, source/cache diff result or supported refresh, raw runtime result path, whether the suite is targeted-only, and whether runner execution mutated source.
- Baseline records pass/partial/fail/blocked counts and targeted metric summary.
- Baseline states whether runtime evidence is release-gating or non-release-gating based on cache/source equivalence.

Evidence / Source:

- `docs/prd-routing-reliability.md` AC-RG-9 and AC-RG-10.
- `docs/prd-routing-reliability.md` sections 8.10 and 13.
- Existing baseline patterns under `evals/baselines/`.

Blockers:

- RR-007 should land first.
- Supported cache refresh or equivalence check must be available before claiming release-gating runtime evidence.

Execution: HITL if cache refresh or external approval is needed; otherwise AFK.

Contract Impact:

- Baseline evidence and release gate.
- Runtime execution evidence.

Verification Evidence Needed:

- Targeted runtime run.
- Source/cache equivalence or supported refresh evidence.
- `git status --short`.
- Raw result path.
- Statement on whether source was mutated.

Ready-for-Agent Missing Fields:

- Exact installed plugin root and cache/source comparison command must be determined during execution.

Triage Recommendation Candidate:

- needs-info recommendation until RR-007 is complete and runtime/cache path is confirmed

### RR-009: Evidence-driven runtime-surface adjustment

Goal:
Make minimal runtime-visible text changes only if targeted routing evidence proves the fix locus is plugin metadata, lifecycle preflight, public skill frontmatter, or trigger text.

Acceptance Criteria:

- No runtime-visible surface changes are made without targeted failure evidence.
- Any touched file is explicitly justified by `failure_type` and `fix_locus`.
- Allowed touch targets are limited to `.codex-plugin/plugin.json`, `skills/_shared/LIFECYCLE-PREFLIGHT.md`, public skill frontmatter/body trigger text, `skills/to-prd/SKILL.md`, or `skills/implement/SKILL.md`.
- Changes preserve direct fallback, do not add a public routing skill, avoid phrase stuffing, and keep `runtime-safety-gate` eval-only.
- Focused rerun shows the affected boundary improved or records a deferred/blocked reason.

Evidence / Source:

- `docs/prd-routing-reliability.md` AC-FS-8 and AC-PM-4.
- `docs/prd-routing-reliability.md` sections 8.1, 8.7, 8.12, and 13.

Blockers:

- Requires targeted failure evidence from RR-008 or a later focused rerun.

Execution: HITL if the fix changes public runtime wording or plugin metadata in a way that affects release behavior.

Contract Impact:

- Potential public skill routing surface or plugin metadata.

Verification Evidence Needed:

- Focused runtime routing rerun for the affected boundary.
- `git diff --check`.
- Plugin JSON parse if `.codex-plugin/plugin.json` is touched.
- Stale-state sweep for contradictory trigger language.

Ready-for-Agent Missing Fields:

- Targeted failure evidence and fix locus are not available yet.

Triage Recommendation Candidate:

- needs-info recommendation

### RR-010: Default-suite promotion decision

Goal:
Decide whether `routing-reliability.csv` should remain targeted-only or enter default runtime suites after stable targeted baseline evidence.

Acceptance Criteria:

- Promotion decision is recorded in `evals/runtime-trial-checklist.md` or baseline notes.
- If promoted, both `evals/run_runtime.py` and `evals/run_runtime_parallel.py` are updated together.
- If not promoted, the reason is recorded.
- Default promotion requires no new forbidden route hit, invalid host preemption, or unclassified route/execution failure in targeted gate evidence.
- Deferred pilots remain out of scope unless separately accepted.

Evidence / Source:

- `docs/prd-routing-reliability.md` AC-DP-1 through AC-DP-6.
- `docs/prd-routing-reliability.md` sections 8.11 and 13.

Blockers:

- Requires stable RR-008 targeted baseline.
- Requires RR-009 only when targeted failure evidence proves runtime-surface adjustment is needed before promotion.

Execution: HITL for promotion decision; AFK for documented non-promotion when evidence clearly fails the gate.

Contract Impact:

- Runtime default suite behavior.
- Release gate.

Verification Evidence Needed:

- Targeted baseline reference.
- Default-suite run if promoted.
- Targeted non-promotion evidence if not promoted.
- Failure classification under AC-RG-11 when default suites produce non-pass results.

Ready-for-Agent Missing Fields:

- Stable targeted baseline and promotion decision are not available yet.

Triage Recommendation Candidate:

- ready-for-human recommendation after RR-008 evidence; needs-info recommendation now

## Ordering Notes

1. RR-001 through RR-006 should be executed in order and can each be a single Codex goal.
2. RR-007 should wait until runner behavior exists, so docs describe implemented behavior rather than intended behavior.
3. RR-008 is the first slice that needs runtime/cache truth evidence.
4. RR-009 is conditional. Do not open it as an implementation goal until targeted failure evidence identifies a runtime-visible surface as the fix locus.
5. RR-010 is a promotion decision, not a default implementation step.

## Next Action

Start with RR-001 as the next implementation goal.

Recommended goal statement:

```text
Implement RR-001 schema parse and validation dry path for routing reliability, without runtime execution or public skill text changes.
```

## Artifact Recommendation

Use this issue pack as the local tracker-neutral source until the work is copied into a remote tracker or superseded by a newer accepted issue pack.
