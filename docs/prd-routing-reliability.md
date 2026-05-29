# Groundwork PRD: Routing Reliability

Target Reader: Groundwork maintainer implementing and reviewing the next routing-reliability increment.
Reader Action Needed: Decide whether to add a narrow intent-to-workflow routing reliability contract, eval schema, hard-negative prompt suite, runner reporting upgrade, and release-gate metrics before changing runtime behavior.
Decision Supported: Whether Groundwork should improve skill/workflow routing as a docs-and-evals increment without adding public skills, learned routing services, hooks, MCP servers, task CRUD, or a standalone runtime.
Scope: Intent Frame, public-skill routing expectations, direct fallback boundaries, host preemption boundaries, trajectory signals, internal branch owner mapping, eval schema extensions, hard-negative prompt coverage, runner reporting, release-gate metrics, regression review, baseline evidence, cache/source equivalence, and documentation updates.
Out of Scope: New public skills, embedding/reranker services, model fine-tuning, ANN indexes, provider/model routing, autonomous orchestration, latent task graphs, full trace graphs, production observability platform, UI/dashboard work, public SLA, regulatory compliance program, tracker writes, task CRUD, runtime cache mutation by hand, and broad skill rewriting.
Evidence Level: Grounded in current Groundwork skill surface, `evals/run_runtime.py`, existing prompt CSV suites, v0.2.3/v0.3 runtime-baseline evidence, prior SkillRouter review, and the local deep-research report as advisory synthesis rather than Groundwork product truth.

## 1. Grill Before Write

### Target Reader

Groundwork maintainer deciding the next narrow product increment after lifecycle-state and runtime reliability hardening.

### Decision Supported

Whether to implement a routing reliability layer that makes skill selection measurable, debuggable, and regression-tested without expanding Groundwork's public skill surface.

### Known Facts

- Groundwork's public skill surface is intentionally small: `to-prd`, `to-issues`, `triage`, `write-plan`, `prototype`, `implement`, `verify`, and `handoff`.
- `docs/plugin-architecture.md` already says prompts should choose the lightest skill that answers the current intent, with direct fallback for small obvious work.
- Existing prompt suites use fields such as `expected_skill`, `skill_load_required`, `should_trigger`, `expected_behavior`, `forbidden_behavior`, `acceptance_standard`, `gate_required`, and `verify_scope_required`.
- `evals/run_runtime.py` currently treats wrong expected skill selection as failure, while allowing direct safety-gate behavior when `skill_load_required=false`.
- Existing baselines have already observed adjacent routing drift, including implementation/prototype review prompts over-routing to `verify`.
- Prior runtime work showed that frontmatter `description` materially affects runtime skill loading; changing body examples alone can be insufficient.
- The local deep-research report agrees that the current best path is a deterministic reliability layer first, followed by observability/error-budget hardening and only later lightweight retrieval or protocol-oriented pilots.
- Routing failures can be user-visible even when the system returns text, because the wrong workflow changes artifact type, evidence standard, approval behavior, and follow-on task state.

### Assumptions

- This increment should be versioned as a narrow v0.3.x or v0.4 candidate only after review; the PRD itself remains release-neutral.
- Groundwork should borrow SkillRouter's evaluation discipline, not its model-serving architecture.
- Backward-compatible optional CSV fields are preferred over replacing every existing prompt fixture at once.
- "Correct routing" means the selected route is useful and safe for the prompt, not that there is always exactly one acceptable route.
- Initial routing metrics are internal release guardrails, not an external customer SLA.
- External compliance, cost, and public-service assumptions from the research report remain contextual risk signals unless a future issue scopes them explicitly.

### Implementation Defaults

- The first routing reliability suite is targeted-only. It does not enter `DEFAULT_SUITES` until a targeted baseline passes the promotion gate in this PRD.
- Groundwork routing reliability is an intent-to-workflow contract, not a skill-name classification task.
- Every routing row has exactly one `expected_best`; it means the first owning workflow, not the whole task graph.
- `acceptable_routes` and `forbidden_routes` may contain multiple route names, separated with `|`, not raw commas.
- `blocked` is a verdict or task-state outcome, not a route.
- `runtime-safety-gate` is an eval-only host preemption classification for `actual_route` and host-preemption verdicts. It is not a product route or public skill.
- Skill-owned risky-write gates stay under their first owning public skill, with gate output checked as output/behavior contract.
- Internal branch names such as `scope`, `contract`, `diagnose`, `gate`, `artifact`, and `standards` are not allowed as `expected_best` routes.
- Output and evidence contracts use finite measurement tokens. Unknown contract tokens block the row instead of falling back to fuzzy text judgment.
- Frontmatter `description` is not expanded by default. A description change requires routing evidence that the discriminator belongs in frontmatter rather than fixture wording, body examples, shared docs, or runner logic.
- Routing regressions must produce a concrete owner, failure classification, and sample-backfill decision before they can be called closed.
- Trace-ready report fields are required in the runner output, but a production tracing backend or dashboard is deferred.

### Blocking Open Questions

None. Release label, issue numbering, and default-suite promotion are implementation metadata to decide during `to-issues` or release planning, not blockers for this PRD.

### Deferred Design Questions

These are intentionally outside the first implementation slice:

- whether a learned router, embedding reranker, or SkillRouter-style serving layer is useful after deterministic reliability is stable;
- whether Groundwork needs a durable intent graph, task graph, or trajectory graph beyond lightweight eval signals;
- whether routing failures should feed an automated skill-authoring data loop;
- whether an external compliance posture or public SLA is needed if Groundwork becomes a public service;
- whether repeated trajectory failures justify a dashboard, eval warehouse, or long-term run database.

## 2. Executive Summary

Groundwork needs a routing reliability increment because the product's correctness depends on choosing the right workflow before drafting, editing, verifying, handing off, or falling back directly.

The current eval model is useful but too coarse. It can say "expected skill loaded" or "wrong skill loaded," but it cannot cleanly express:

- one best route plus acceptable alternatives;
- routes that must never be selected;
- host/runtime safety preemption;
- output-contract pass/fail separated from skill routing pass/fail;
- evidence-contract pass/fail separated from behavior pass/fail;
- internal branch ownership without expanding public skills;
- hard-negative prompt groups that intentionally distinguish close workflows;
- internal reliability metrics that distinguish release-blocking regressions from acceptable variance.

This PRD adds a narrow intent-to-workflow routing reliability contract:

```text
prompt -> Intent Frame -> expected_best first owning workflow
       -> acceptable_routes -> forbidden_routes
       -> routing verdict -> host preemption verdict
       -> output contract verdict -> evidence verdict -> behavior verdict
```

The increment should improve eval quality and skill authoring feedback. It should not add new public skills or a SkillRouter-like model runtime.

The rollout path is deliberately staged:

```text
deterministic contract -> observability and regression governance -> retrieval/protocol pilots
```

Only the first stage is in implementation scope for this PRD. Later stages are allowed only when first-stage metrics show a real reliability gap that deterministic contracts cannot explain or fix.

## 3. Problem Statement

Groundwork has a deliberately small public surface, but its skills still overlap at boundaries:

- `implement` vs `verify` for implementation review versus readiness proof;
- `prototype` vs `verify` for prototype contract-boundary review versus source-truth verification;
- `to-prd` vs `write-plan` versus `to-issues` for raw, accepted, and sliced work;
- `triage` vs `to-issues` for readiness judgment versus task creation;
- `triage` vs `verify` for task-state decision versus evidence sufficiency report;
- `handoff` vs `verify` for continuation packages versus fresh-context review prompts;
- `direct` vs skill workflow for small one-off requests;
- host preemption vs skill-owned `gate` behavior for risky writes.

Current prompt rows can encode a single expected skill and expected behavior, but this makes several failure modes hard to diagnose:

1. **False strictness.** A useful route may be marked failed even when it is acceptable for the prompt.
2. **False leniency.** A route may be behaviorally useful but still wrong because it hides a boundary regression.
3. **Intent collapse.** Rows can look like skill-name classification while missing risk, evidence, artifact, and state-transition obligations.
4. **Mixed failure causes.** A row can fail because the wrong skill loaded, because the right skill output the wrong structure, because required evidence is missing, because host preemption was misclassified, or because the behavior was unsafe.
5. **Wrong trajectory after right route.** A prompt can load the right skill but skip source evidence, over-promote an artifact, bypass a gate, or turn a narrow review into a readiness claim.
6. **Weak hard negatives.** Adjacent prompts are scattered across suites instead of grouped around boundary questions and their source rationale.
7. **Frontmatter drift.** Runtime routing can regress when `description` changes or fails to carry the discriminating trigger language.
8. **Cache ambiguity.** Runtime evals are invalid as release evidence if the installed plugin cache is stale relative to the checkout.
9. **Branch owner ambiguity.** Internal branch names can be mistaken for public routes unless each row names the owning public skill.
10. **Governance gap.** A routing regression can be fixed once without leaving a durable sample, owner, or action trail, which makes the same boundary drift likely to recur.

## 4. Goals

1. Define an Intent Frame that maps user intent, risk, evidence, artifact, and state-transition obligations to the first owning workflow.
2. Define a product-level route vocabulary for Groundwork evals.
3. Distinguish best route, acceptable routes, and forbidden routes.
4. Split routing verdict, host-preemption verdict, output-contract verdict, evidence verdict, and behavior verdict.
5. Add a lightweight trajectory boundary that catches "right skill, wrong path" failures without requiring a full trace graph.
6. Add a hard-negative prompt suite for close skill boundaries.
7. Keep existing prompt CSVs backward-compatible while adding richer fields where needed.
8. Make runner summaries expose routing false positives, routing false negatives, forbidden-route hits, output-contract failures, evidence failures, host-preemption failures, and behavior failures separately.
9. Define internal release-gate metrics that measure user-relevant good events instead of raw skill-load events.
10. Require routing regressions to feed back into targeted samples, owner/action tracking, or an explicit non-backfill decision.
11. Ensure `direct` remains a first-class valid route for small low-risk work.
12. Ensure runtime safety-gate preemption remains valid only when row metadata and observed output support it.
13. Make frontmatter/body trigger consistency reviewable without encouraging phrase stuffing.
14. Preserve the current public skill surface.

## 5. Non-Goals

This increment does not add:

- public skills;
- a `routing` public skill;
- embedding models;
- reranker models;
- SkillRouter model weights;
- vector indexes;
- ANN search;
- provider/model routing;
- automatic prompt rewriting;
- automatic skill patching;
- learned routing;
- latent task graph storage;
- full trajectory graph evaluation;
- eval warehouses;
- production tracing backends;
- public error budgets or external SLA commitments;
- canary deployment infrastructure;
- automatic postmortem systems;
- hooks;
- MCP servers;
- UI dashboards;
- tracker writes;
- task CRUD;
- direct mutation of `~/.codex/plugins/cache`;
- a replacement for Codex host safety and approval enforcement.

## 6. Users / Actors

- **Groundwork maintainer**: reviews the PRD, implements docs/evals/runner changes, and decides release readiness.
- **Groundwork skill author**: uses routing failures to improve frontmatter, trigger contracts, and output boundaries.
- **Groundwork verifier**: runs targeted and full runtime baselines and reports whether routing drift is real or noise.
- **Codex runtime**: selects public skills, direct fallback, or host safety gates based on available plugin metadata and prompt context.

## 7. Core Concepts

### 7.1 Intent Frame

An Intent Frame is the semantic object Groundwork routes, before any skill name is chosen.

It describes the user's current work in terms of:

- `intent_kind`: direct answer, raw requirement, issue split, plan, prototype, implementation, verification, handoff, delivery, or remote mutation;
- `requirement_state`: raw, grilled, PRD draft, accepted, issue-ready, implementation-ready, verified, or blocked;
- `artifact_intent`: none, conversation-only, durable artifact, external source of truth, or handoff reference;
- `evidence_obligation`: none, source, tests, runtime, browser, git, cache/source equivalence, or explicit unavailability;
- `risk_gate`: none, git write, remote write, destructive, customer-visible, data write, secrets/PII, or blocked;
- `state_transition`: none, clarify, draft, accept, split, plan, implement, verify, handoff, block, or close.

The first implementation does not need a learned representation of the Intent Frame. It needs a deterministic, reviewable mapping from row metadata and prompt text to the first owning workflow, required output shape, required evidence, and allowed stop condition.

### 7.2 Reliability Event

A reliability event is one evaluated prompt row or captured regression sample.

It is a good event only when all required dimensions pass:

- the first owning workflow is best or explicitly acceptable;
- no forbidden route is selected;
- host preemption is absent or valid;
- output, evidence, and behavior contracts pass or are explicitly not applicable;
- trajectory signals prove the response did not bypass the required gate, artifact boundary, or evidence boundary.

This keeps routing metrics aligned with user-visible reliability instead of raw skill-load success.

### 7.3 Reliability Layer Map

Routing reliability spans several layers that must stay separate:

| Layer | Responsibility | First-slice representation |
| --- | --- | --- |
| Policy | Preserve public skill surface, direct fallback, and non-goals. | PRD requirements and route vocabulary. |
| Intent Representation | Encode what the user is actually asking for and what risk/evidence/state obligations follow. | Intent Frame fields and `route_boundary`. |
| Routing | Pick the first owning workflow for the prompt. | `expected_best`, `acceptable_routes`, `forbidden_routes`, `actual_route`. |
| Tool Selection | Observe what Codex actually loads or whether it falls back directly. | Runtime skill detection and direct fallback classification. |
| State Transition | Check whether the response moves the work to the right lifecycle state or stops correctly. | Output/evidence/behavior verdicts and trajectory signals. |
| Safety Gate | Distinguish skill-owned gates from host/runtime preemption. | Gate output tokens and `host_preemption_verdict`. |
| Evaluation | Explain failures without rewriting skills automatically. | Per-row verdicts, `failure_type`, and `fix_locus`. |
| Governance | Turn regressions into durable prevention work. | Release-gate metrics, owner/action fields, and sample-backfill decisions. |

### 7.4 Route

A route is the first owning workflow selected for a prompt.

Public workflow route values:

```text
direct
to-prd
to-issues
triage
write-plan
prototype
implement
verify
handoff
```

Eval-only host preemption classification:

```text
runtime-safety-gate
```

`runtime-safety-gate` is not a public skill and is not a product route. It may appear as `actual_route`, `acceptable_routes`, or `forbidden_routes` only to classify Codex host/runtime preemption for destructive, remote, data-write, filesystem-destructive, or approval-gated requests. It is acceptable only when row metadata allows host preemption and observed output proves a no-execution approval gate.

Skill-owned gates keep the owning public route as `expected_best`. For example, an implementation prompt that requires approval should still route to `implement`, then satisfy `gate_fields` through output/behavior checks.

`blocked` is not a route. It is an `overall_verdict`, `behavior_verdict`, or task-state recommendation when execution cannot complete because required evidence, approval, runtime, source context, or user decision is missing.

### 7.5 Expected Best Route

`expected_best` is the single first owning workflow that should be selected when the prompt is interpreted exactly as written.

It is not the whole task graph. Follow-on recommendations do not fail routing when the first owner remains correct. For example, a raw requirement may route first to `to-prd` and later recommend `to-issues`; that is not drift.

`expected_best` must be `direct` or one of the eight public skills. It must not be `runtime-safety-gate`; host preemption is represented through row metadata, `actual_route`, and `host_preemption_verdict`.

Backward-compatible expected-route precedence:

```text
expected_best
  -> expected_skill
  -> should_trigger=false route hint in expected_behavior
  -> skill
  -> direct
```

For existing rows, a route hint is the current `Should route to <route>` pattern in `expected_behavior`. If `should_trigger=false` and no route hint exists, `direct` is expected.

### 7.6 Acceptable Routes

`acceptable_routes` is a `|`-separated route list that can pass routing when the behavior remains safe and useful.

Examples:

```text
expected_best=direct
acceptable_routes=direct

expected_best=verify
acceptable_routes=verify|runtime-safety-gate

expected_best=implement
acceptable_routes=implement
```

Acceptable routes must not be used to hide unclear ownership. Every row still needs one `expected_best`.

### 7.7 Forbidden Routes

`forbidden_routes` is a `|`-separated route list that must fail routing even if the output looks plausible.

Examples:

```text
prototype contract-boundary prompt:
expected_best=prototype
forbidden_routes=verify

implementation conformance review without UAT:
expected_best=implement
forbidden_routes=verify
```

`acceptable_routes` and `forbidden_routes` must not overlap.

### 7.8 Internal Branch Owner Matrix

Internal branch names may appear in prompt text, expected behavior, notes, or reports, but they are not routes.

| Internal branch | Owning public routes | Routing rule |
| --- | --- | --- |
| `scope` | `to-prd`, `to-issues` | Use the public owner that is shaping requirements or splitting accepted work. |
| `contract` | `write-plan`, `prototype`, `implement`, `verify` | Use `prototype` for prototype-only contract boundary, `verify` for source-truth contract validation, and `implement` or `write-plan` when contract affects code work or planning. |
| `artifact` | any public skill or `direct` | Use the skill that owns the user-visible output; artifact policy is not a route. |
| `diagnose` | `implement` | Confirm-before-edit bug work belongs to `implement`, not `verify`, unless the user asks for readiness or release evidence. |
| `gate` | `implement`, `verify`, or `handoff` | Skill-owned gates keep the public skill as `expected_best`; host preemption is eval-only `actual_route=runtime-safety-gate` when allowed by row metadata. |
| `standards` | `verify`, `implement`, `direct` | Repo-local standards are a review lens, not a public route. Use the skill that owns the review or direct answer. |

Rows must not use `scope`, `contract`, `artifact`, `diagnose`, `gate`, or `standards` as `expected_best`.

### 7.9 Trajectory Evaluation Boundary

The first routing reliability increment does not attempt full trace-graph evaluation.

It only checks lightweight trajectory signals that prove the selected workflow stayed on the right path:

- correct first owning workflow or allowed direct fallback;
- host preemption observed only when metadata allows it;
- no file changes when `no_file_changes` is required;
- gate output observed when risk metadata requires a gate;
- evidence token satisfied or explicitly marked unavailable;
- durable artifact created only when artifact policy allows it;
- handoff references compact state rather than replacing it;
- direct fallback avoids PRD/issue/handoff ceremony for small low-risk work.

This catches "right skill, wrong path" failures without introducing a durable trajectory graph, run database, or autonomous orchestration layer.

### 7.10 Verdict Dimensions

Each evaluated row should produce separate dimensions:

- `routing_verdict`: `best`, `acceptable`, `forbidden`, `missing`, or `unexpected`.
- `host_preemption_verdict`: `pass`, `fail`, `blocked`, or `not_applicable`.
- `output_contract_verdict`: `pass`, `fail`, `blocked`, or `not_applicable`.
- `evidence_verdict`: `present`, `missing`, `explicitly_unavailable`, `blocked`, or `not_applicable`.
- `behavior_verdict`: `pass`, `fail`, `blocked`, or `not_applicable`.
- `overall_verdict`: `pass`, `partial`, `fail`, or `blocked`.

Overall pass requires no forbidden route, no invalid host preemption, no forbidden behavior, and no required output/evidence failure.

## 8. Product Requirements

### 8.1 Eval Schema

Routing reliability rows should support these fields:

```csv
id,route_boundary,case_kind,case_source,intent_kind,risk_gate,expected_state_transition,expected_best,acceptable_routes,forbidden_routes,fixture,input_scenario,expected_behavior,forbidden_behavior,output_contract,evidence_required,artifact_allowed,risky_write_requested,host_preemption_allowed,skill_load_required,gate_required
```

Field rules:

- `id` must be globally unique across all prompt CSVs. Routing reliability rows use the `rr-###` prefix.
- `route_boundary` names the hard-negative group, such as `implement-vs-verify`.
- `case_kind` is `positive`, `hard_negative`, or `host_preemption`.
- `case_source` is `real_drift`, `synthetic_hard_negative`, `regression_protection`, or `unverified_hypothesis`.
- `intent_kind` follows lifecycle preflight intent values: `direct`, `new_requirement`, `clarify`, `issue_split`, `plan`, `prototype`, `implement`, `verify`, `handoff`, `delivery`, or `remote_mutation`.
- `risk_gate` follows lifecycle preflight risk values: `none`, `git_write`, `remote_write`, `destructive`, `customer_visible`, `data_write`, `secrets_or_pii`, or `blocked`.
- `expected_state_transition` is `none`, `clarify`, `draft`, `accept`, `split`, `plan`, `implement`, `verify`, `handoff`, `block`, or `close`.
- `expected_best` is required for routing reliability rows.
- `expected_best` must be `direct` or one of the eight public skills; it must not be `runtime-safety-gate`.
- `acceptable_routes` and `forbidden_routes` use `|` as the list separator.
- Route list cells must contain only allowed route values.
- `acceptable_routes` defaults to `expected_best` when blank.
- Unknown routes, unknown Intent Frame tokens, overlapping acceptable/forbidden routes, missing `expected_best`, duplicate row ids, and malformed CSV rows must block validation before runtime execution.
- `runtime-safety-gate` may appear only as an eval-only route classification tied to `host_preemption_allowed=true` or `case_kind=host_preemption`; it must not be treated as a public skill.

Backward compatibility:

- Existing `expected_skill` maps to `expected_best` when the new field is absent.
- Existing `skill` maps to `expected_best` only after `should_trigger=false` route hints are honored.
- Existing `prompt` maps to `input_scenario`.
- Existing `acceptance_standard` remains supported as a behavior assertion.
- Existing `verify_scope_required` remains supported as an output-contract shortcut.
- Existing `skill_load_required=false` does not automatically mean `runtime-safety-gate`; it only allows a non-skill route when output and metadata prove direct fallback or host safety preemption.
- Existing rows without Intent Frame fields derive `intent_kind`, `risk_gate`, and `expected_state_transition` from legacy fields when possible and mark unknowns as `not_applicable` instead of blocking non-routing suites.

### 8.2 Output And Evidence Contract Tokens

`output_contract` and `evidence_required` are finite measurement-token fields, not arbitrary prose and not Groundwork's semantic ontology.

Initial `output_contract` tokens:

```text
none
verify_scope_full
gate_fields
qa_fix_qa
artifact_header
prototype_contract_boundary
implementation_conformance
handoff_compact_reference
route_failure_feedback
trajectory_signal
```

Initial `evidence_required` tokens:

```text
none
source_or_unverified
tests_or_unverified
runtime_or_unverified
browser_or_unverified
git_status
cache_equivalence
no_file_changes
gate_observed
direct_fallback_no_artifact
```

Cells may combine tokens with `|`. Unknown tokens block the row. The runner should use deterministic checks for known tokens and mark unimplemented tokens as `blocked`, not silently pass.

### 8.3 Runtime Safety Route Classification

The actual route may be classified as `runtime-safety-gate` only when all are true:

- no public Groundwork skill is detected;
- row metadata allows host/runtime safety preemption through `host_preemption_allowed=true`, `case_kind=host_preemption`, `acceptable_routes`, or `skill_load_required=false`;
- the prompt requests a destructive, remote, data-write, filesystem-destructive, or approval-gated action;
- the response includes the expected approval-gate fields or equivalent no-execution approval block;
- source snapshot comparison shows no files were changed by the row.

Otherwise, no skill hit remains `direct`.

Rows that load a public skill and emit a skill-owned approval gate must not be reclassified as `runtime-safety-gate`; they should keep the public route and satisfy gate requirements through output/behavior verdicts.

### 8.4 Hard-Negative Suite

Add a dedicated suite:

```text
evals/prompts/routing-reliability.csv
```

Minimum first-pass groups:

1. `implement` vs `verify`: implementation conformance review is not readiness/UAT verification.
2. `verify` vs `implement`: evidence sufficiency and UAT/readiness checks should start from `verify`.
3. `prototype` vs `verify`: prototype contract-boundary classification must not become backend source-truth verification.
4. `to-prd` vs `write-plan` vs `to-issues`: raw requirement, accepted plan, and task slicing must stay distinct.
5. `triage` vs `to-issues`: readiness/state judgment is not task generation.
6. `triage` vs `verify`: task-state decision is not the same as evidence sufficiency verification.
7. `handoff` vs lifecycle state: transfer package should reference state when present and avoid becoming durable state.
8. `handoff` vs `verify`: fresh-context review prompt belongs to `verify`; cross-session continuation belongs to `handoff`.
9. `direct` vs public skill: small one-off answers should avoid durable artifacts and skill ceremony.
10. `verify` vs `direct`: code-diff-only or no-command readiness questions must not become direct short answers.
11. `verify` vs `to-prd`: PRD acceptance clarity review differs from writing or refining the PRD.
12. `write-plan` vs `implement`: full implementation planning differs from implementation with an inline mini-plan.
13. `implement` diagnose vs `verify`: diagnose-before-edit belongs to `implement`; readiness/UAT/release evidence belongs to `verify`.
14. `runtime-safety-gate` vs skill-owned `gate`: host preemption differs from public-skill gate output.
15. `standards` branch ownership: repo-local standards prompts must route to the public owner or `direct`, never to `standards`.

Each group should include at least one positive row and one hard-negative row unless the row count is intentionally deferred in the issue slice.

Each group must also state why it exists through `case_source`. Row count is not the only coverage signal. A smaller group with real drift evidence or clear regression protection is stronger than many synthetic rows with unclear boundary rationale.

### 8.5 Runner Reporting

Update `evals/run_runtime.py` and `evals/run_runtime_parallel.py` only after this PRD is accepted.

The serial runner owns row parsing, route classification, deterministic contract checks, and per-row verdicts. The parallel wrapper should consume and aggregate serial per-row JSON instead of re-implementing routing logic.

The runner should report:

- total rows;
- Best-route Hit@1;
- acceptable coverage;
- forbidden route rate;
- host preemption precision;
- route-vs-execution separability;
- routing best / acceptable / fail;
- forbidden route hits;
- host-preemption pass / fail / blocked;
- output-contract pass / fail / blocked;
- evidence present / missing / explicitly unavailable / blocked;
- behavior pass / fail / blocked;
- overall pass / partial / fail / blocked;
- per-suite summary;
- per-route confusion matrix or compact route-pair table;
- per-boundary and per-route summary slices;
- route failure feedback with fix locus.

Per-row JSON should include:

```text
id
suite
route_boundary
case_kind
case_source
intent_kind
risk_gate
expected_state_transition
expected_best
acceptable_routes
forbidden_routes
actual_route
routing_verdict
host_preemption_verdict
output_contract_verdict
evidence_verdict
behavior_verdict
overall_verdict
notes
failure_type
fix_locus
```

The per-row JSON should be trace-ready: stable row id, suite, route boundary, expected route, actual route, verdict dimensions, and failure metadata must be sufficient to reconstruct what routing decision was evaluated without relying on prose logs.

### 8.6 Skill Authoring Feedback

Routing failures should produce scoped feedback:

- affected route boundary;
- prompt id;
- case source;
- intent kind and risk gate;
- expected best route;
- actual route;
- acceptable routes;
- forbidden routes hit, if any;
- failure type: `intent_ambiguity`, `route_boundary_ambiguity`, `frontmatter_recall_miss`, `body_instruction_drift`, `fixture_ambiguity`, `runner_false_positive`, `output_contract_drift`, `evidence_contract_drift`, `host_preemption_misclassified`, `cache_staleness`, or `unknown`;
- fix locus: `frontmatter`, `body_examples`, `shared_docs`, `fixture_wording`, `runner_logic`, `cache_or_install`, or `unknown`;
- whether the failure is likely routing-only, host-preemption, output-contract, evidence, behavior, or blocked.

`failure_type` explains what went wrong. `fix_locus` explains where a maintainer should consider changing something. They are separate because the same failure type can require different fixes depending on whether the row, runner, cache, or skill text is at fault.

Do not automatically patch skills from runner output. Patch proposals remain review artifacts.

### 8.7 Reliability Metrics And Release Gates

Routing reliability metrics are internal release guardrails. They are not public SLA commitments.

Initial metrics:

| Metric | Definition | Initial target or rule | Gate use |
| --- | --- | --- | --- |
| Best-route Hit@1 | `expected_best` selected over total evaluated routing rows. | Track trend; targeted suite should not regress versus accepted baseline. | Release blocker when a new P1 boundary regresses. |
| Acceptable coverage | Rows not best but still in `acceptable_routes`. | Track but do not optimize upward. | Review signal, not pass signal by itself. |
| Forbidden route rate | Rows whose actual route appears in `forbidden_routes`. | `0` for release-gating targeted rows unless explicitly waived. | Release blocker by default. |
| Host preemption precision | Host preemption rows that satisfy `runtime-safety-gate` rules. | No invalid host preemption in targeted safety rows. | Release blocker for safety rows. |
| Route-vs-execution separability | Non-pass rows with distinguishable routing, output, evidence, host-preemption, and behavior verdicts. | `100%` for updated runner output. | Release blocker when a failure cannot be classified. |
| MTTR for routing regressions | Time from accepted regression classification to merged or intentionally deferred fix. | Track after first release; no first-slice numeric SLO. | Operational trend metric. |
| Regression closure rate | Classified routing regressions with owner, action, and sample-backfill decision. | `100%` for accepted regressions. | Release blocker when a new P1 regression lacks owner/action. |

Error-budget style decisions should use forbidden route rate, invalid host preemption, and route-vs-execution separability first. Best-route Hit@1 is useful, but it must not incentivize hiding legitimate acceptable routes.

### 8.8 Regression Review And Sample Backfill

Every accepted routing regression should produce a short review record in the baseline, issue, PR, or release note that contains:

- prompt or row id;
- route boundary;
- observed actual route;
- expected best route;
- failure type;
- fix locus;
- owner;
- blocking level: `P1`, `P2`, or `non_blocking`;
- action: `fix_now`, `defer_with_reason`, `accept_as_expected`, or `needs_more_evidence`;
- sample-backfill decision: `add_row`, `update_row`, `covered_by_existing_row`, or `no_backfill_with_reason`;
- verification evidence after fix or deferral.

If the regression is fixed by changing frontmatter, body examples, shared docs, or runner logic, the review record must explain why that layer was the right locus. If the regression is not backfilled into `routing-reliability.csv`, the reason must be explicit.

### 8.9 Runtime Truth Alignment

Any runtime baseline used for acceptance must state whether the installed Groundwork plugin cache matches the checkout for the touched docs, skills, evals, and runner files.

Required baseline metadata:

- current branch;
- `git status --short`;
- intended file allowlist;
- installed plugin root;
- source package root;
- compared path list;
- source/cache diff result;
- raw runtime result path;
- whether the suite is targeted-only or in defaults;
- whether runner execution mutated the source repo.

Acceptance evidence may use either:

- explicit cache refresh through the package/marketplace install flow before runtime eval; or
- a source/package equivalence check that proves the runtime uses the intended package.

If equivalence is unknown, runtime routing results are evidence but not release-gate proof.

### 8.10 Default-Suite Promotion Gate

`routing-reliability.csv` remains targeted-only until all are true:

- targeted serial run completes with no P1 routing failures;
- targeted metrics show no new forbidden route hit, invalid host preemption, or unclassified route/execution failure;
- cache/source equivalence is proven or cache was refreshed through the supported install path;
- baseline is recorded under `evals/baselines/`;
- no new blocking failures appear in existing default suites;
- both `evals/run_runtime.py` and `evals/run_runtime_parallel.py` are updated together when promotion happens;
- `evals/runtime-trial-checklist.md` records the routing suite and promotion decision;
- parallel full/default runs remain serial or `--jobs 1` unless metadata proves concurrent execution is safe for the selected rows.

### 8.11 Public Surface Stability

The implementation must not add new public skill directories or rename current public skills.

Internal branch names may appear in documentation, but `expected_best` must still evaluate the owning public skill or `direct`. Host preemption is represented only through eval metadata and `actual_route=runtime-safety-gate`.

### 8.12 Deferred Roadmap And Pilots

This PRD supports a staged reliability path:

1. **Stage 1: deterministic contract layer.** Current scope. Implement route vocabulary, hard negatives, verdict dimensions, runner reporting, release-gate metrics, cache/source equivalence, and regression review.
2. **Stage 2: observability and error-budget hardening.** Deferred. Add trace emission, richer route slices, dashboards, canary-style release checks, and longer-term MTTR/error-budget reporting only after Stage 1 produces stable baseline data.
3. **Stage 3: retrieval or protocol pilots.** Deferred. Experiment with skill-text retrieval, context-aware filtering, MCP/A2A compatibility, or learned routing only when Stage 1/2 evidence shows deterministic contracts are insufficient.

Allowed future pilots after Stage 1:

- **High-ambiguity pressure test:** expand selected route boundaries to 20-40 hard-negative rows and test whether frontmatter/body/docs changes affect forbidden route rate.
- **Single-route semantics experiment:** evaluate whether stricter schema and no-parallel-route execution reduce ambiguity and diagnosis cost.
- **Lightweight retrieval pilot:** test skill-text retrieval or context-aware filtering only for a small number of high-confusion boundaries, measuring forbidden route rate, latency, and explainability.

These pilots must not be promoted into the default runtime path until they outperform the deterministic layer on Groundwork's own targeted suite and real regression samples.

## 9. Implementation Scope

Required update areas:

- `docs/prd-routing-reliability.md`
- `evals/prompts/routing-reliability.csv`
- `evals/run_runtime.py`
- `evals/run_runtime_parallel.py`
- `evals/runtime-trial-checklist.md`
- `docs/skill-success-metrics.md` or another existing metrics doc if the runner metrics vocabulary changes
- `evals/baselines/YYYY-MM-DD-routing-reliability.md` after targeted runtime validation
- a regression-review or baseline note section that records owner, action, and sample-backfill decision for accepted routing regressions

Conditionally update:

- public skill `description` fields only when runtime evidence shows the discriminator belongs in frontmatter;
- skill body trigger examples when the route boundary is correct but body examples are stale;
- shared docs when the rule is cross-skill and not a prompt-fixture issue.

Deferred:

- default-suite promotion until the promotion gate passes;
- broad rewrites of existing prompt suites;
- production tracing, dashboards, canary automation, or eval warehouses;
- public SLA/error-budget commitments;
- lightweight retrieval or rerank pilots until deterministic metrics show a remaining reliability gap;
- MCP/A2A compatibility work until local skill routing has stable gate evidence;
- SkillRouter-like model routing.

Forbidden:

- new public skills;
- manual mutation of `~/.codex/plugins/cache`;
- shared global skill edits;
- remote tracker writes without explicit approval;
- production data, deployment, or destructive filesystem changes;
- broad phrase-stuffing of all skill descriptions.

## 10. Acceptance Criteria

- AC-1: A routing reliability PRD exists under `docs/` and defines Intent Frame, reliability layer map, route vocabulary, implementation defaults, non-goals, implementation scope, and acceptance criteria.
- AC-2: The accepted design preserves the eight existing public skills and does not introduce a public `routing` skill.
- AC-3: The eval schema supports `intent_kind`, `risk_gate`, `expected_state_transition`, `expected_best`, `acceptable_routes`, `forbidden_routes`, `route_boundary`, `case_kind`, `case_source`, output contract tokens, and evidence tokens while remaining backward-compatible with existing CSV suites.
- AC-4: Route parsing honors this precedence: `expected_best`, `expected_skill`, `should_trigger=false` route hint or direct fallback, `skill`, then `direct`.
- AC-5: `acceptable_routes` and `forbidden_routes` use `|` list separators, reject unknown routes, reject overlaps, and reject malformed CSV rows before runtime execution.
- AC-6: `blocked` is not accepted as `expected_best`, `acceptable_routes`, or `forbidden_routes`.
- AC-7: `runtime-safety-gate` is treated as an eval-only host preemption classification, not a public skill or product route; skill-owned gates keep their public route.
- AC-8: `evals/prompts/routing-reliability.csv` exists with at least 16 rows across the hard-negative groups listed in this PRD, and each row has `route_boundary`, `case_kind`, `case_source`, and Intent Frame fields.
- AC-9: The runtime runner reports routing, host-preemption, output-contract, behavior, evidence, and overall verdict dimensions separately, with enough trace-ready row metadata to reconstruct the route decision being evaluated.
- AC-10: Lightweight trajectory signals catch right-route/wrong-path failures, including missing evidence, invalid host preemption, missing gate output, forbidden artifact promotion, and direct fallback ceremony.
- AC-11: Runner summaries expose Best-route Hit@1, acceptable coverage, forbidden route rate, host preemption precision, route-vs-execution separability, and at least one route-pair confusion table or equivalent compact route-drift report.
- AC-12: Routing failure output includes affected boundary, prompt id, expected/actual route, acceptable/forbidden routes, `failure_type`, `fix_locus`, and blocking level.
- AC-13: The parallel runner consumes and aggregates serial per-row verdict dimensions rather than re-implementing route judgment.
- AC-14: At least one targeted routing reliability baseline is recorded under `evals/baselines/` after cache/source equivalence is checked or cache refresh is performed through the supported install path.
- AC-15: Existing CSV suites still parse after schema additions.
- AC-16: Existing default runtime suites still run through the updated runner; any non-pass result must include case id, classification, owner, whether it is pre-existing or new, and whether it blocks release acceptance.
- AC-17: Documentation explains that SkillRouter is an external research input and that Groundwork is not adopting a model-serving routing runtime in this increment.
- AC-18: Accepted routing regressions have an owner, action, and sample-backfill decision before they are marked closed.
- AC-19: Default-suite promotion requires no new forbidden route hit, invalid host preemption, or unclassified route/execution failure in targeted gate evidence.
- AC-20: Deferred roadmap language keeps observability dashboards, retrieval/rerank pilots, MCP/A2A compatibility, learned routing, and public SLA/compliance work outside the first implementation scope.
- AC-21: No implementation mutates shared global skills, production systems, remote trackers, or installed plugin cache by hand.

## 11. Evidence

Local evidence:

- `docs/product-principles.md` defines small-task direct fallback, source-truth priority, verification discipline, and public skill surface.
- `docs/plugin-architecture.md` defines the eight public skills, direct fallback policy, and lightweight eval baseline.
- `docs/workflow-taxonomy.md` defines current skill boundaries, internal branch concepts, and direct route behavior.
- `docs/skill-success-metrics.md` defines current skill reliability metrics.
- `evals/run_runtime.py` and `evals/run_runtime_parallel.py` define current runtime row parsing and verdict behavior.
- `evals/prompts/*.csv` contains current prompt fixture fields and adjacent route examples.
- `evals/baselines/2026-05-25-v0.2.3-runtime-baseline.md` records prior adjacent routing drift and frontmatter-related routing fixes.
- `evals/baselines/2026-05-26-v0.3-runtime-baseline.md` provides cache/source equivalence evidence patterns.

External research input:

- Local advisory report: `/Users/daxiong/Downloads/Deep Research Report from ChatGPT.md`
- SkillRouter repository: `https://github.com/zhengyanzhao1997/SkillRouter`
- SkillRouter paper: `https://arxiv.org/abs/2603.22455`
- Research themes surfaced by the local advisory report: ToolScope-style redundant tool ambiguity, strict structured tool/function calling, SRE SLI/SLO and postmortem practice, OpenTelemetry-style observability, MCP/A2A protocol direction, and AI risk-management framing.

Groundwork uses these external inputs only as research evidence that hard negatives, clear schemas, full skill context, observability, and regression governance can matter for routing quality. This PRD does not treat them as Groundwork product truth and does not adopt their model-serving, protocol, dashboard, compliance, or operational architectures in this increment.

## 12. Risks And Mitigations

### Risk: The schema becomes too heavy

Mitigation: Keep new fields required only for `routing-reliability.csv` first and support old rows through explicit precedence rules.

### Risk: Intent Frame fields become another vague taxonomy

Mitigation: Keep the first slice limited to deterministic tokens already aligned with lifecycle preflight, and use them to explain routing and verdicts rather than to create new public workflow modes.

### Risk: Measurement tokens are mistaken for product semantics

Mitigation: Treat output and evidence tokens as runner handles only. Product semantics stay in the public skill contracts, Intent Frame, acceptance criteria, and source-truth docs.

### Risk: Host preemption is mistaken for a ninth route

Mitigation: Keep `runtime-safety-gate` out of public routes and `expected_best` ownership. Use it only as eval-only `actual_route` with a separate host-preemption verdict.

### Risk: Acceptable routes hide real regressions

Mitigation: Every row must still have one `expected_best`, and `forbidden_routes` must fail even when output is plausible.

### Risk: Frontmatter grows into noisy phrase stuffing

Mitigation: Route failures must identify whether the fix belongs in frontmatter, body examples, shared docs, fixture wording, or runner logic. Description edits require routing evidence and should stay minimal.

### Risk: Runtime evidence is stale because cache was not refreshed

Mitigation: Baselines must state cache/source equivalence or mark routing evidence as non-release-gating.

### Risk: The suite duplicates existing guardrail rows

Mitigation: Routing reliability rows should group close route boundaries and verdict dimensions. Existing guardrail rows can remain behavior/output-contract checks.

### Risk: Parallel runner diverges from serial runner

Mitigation: Serial runner owns route judgment. Parallel runner aggregates serial per-row JSON and does not duplicate route classification logic.

### Risk: Metrics become vanity KPIs

Mitigation: Treat metrics as release guardrails tied to user-visible reliability events. Do not optimize acceptable coverage upward, and do not let Best-route Hit@1 hide forbidden route hits or unclassified failures.

### Risk: Routing regressions are fixed without durable prevention

Mitigation: Every accepted regression needs an owner, blocking level, action, and sample-backfill decision before closeout.

### Risk: Learned routing is introduced before deterministic failures are understood

Mitigation: Keep retrieval, rerank, and learned router work deferred until deterministic contract metrics show a persistent gap and a small pilot proves lower forbidden-route rate without unacceptable latency or explainability cost.

### Risk: Protocol expansion adds security and maintenance surface

Mitigation: Keep MCP/A2A work out of this increment. Future protocol pilots need explicit approval, consent, tool filtering, auditability, and trace requirements.

### Risk: Compliance assumptions are overstated

Mitigation: Treat regulatory and public-SLA considerations as contextual risks only. Do not claim compliance readiness or public service obligations unless a future scoped issue defines jurisdiction, audience, data handling, and owner.

## 13. Next Action

Use `to-issues` after this PRD is accepted.

Recommended implementation slices:

1. **Routing fixture schema and hard-negative CSV**
   - Depends on: accepted PRD.
   - Touches: `evals/prompts/routing-reliability.csv`.
   - Stop condition: at least 16 rows exist across the hard-negative groups, using `rr-###`, `route_boundary`, `case_kind`, `case_source`, `intent_kind`, `risk_gate`, `expected_state_transition`, `expected_best`, `acceptable_routes`, and `forbidden_routes`.
   - Verification: CSV parse check and duplicate-id check.
   - Note: the later high-ambiguity pressure-test pilot may expand selected boundaries to 20-40 rows, but that is not required for first acceptance.

2. **Shared route parsing and deterministic schema validation**
   - Depends on: slice 1.
   - Touches: `evals/run_runtime.py`; optionally shared helper extraction only if it reduces duplication.
   - Stop condition: legacy expected route precedence, route list parsing, malformed CSV rejection, Intent Frame token validation, and eval-only host preemption classification rules are implemented.
   - Verification: targeted dry parse / unit-like runner checks where feasible, plus existing CSV parse.

3. **Serial verdict dimensions and route feedback**
   - Depends on: slice 2.
   - Touches: `evals/run_runtime.py`.
   - Stop condition: per-row JSON includes routing, host-preemption, output, evidence, behavior, overall verdicts, trace-ready row metadata, `failure_type`, `fix_locus`, and blocking level.
   - Verification: targeted rows produce separate verdict dimensions and route failure feedback.

4. **Parallel wrapper compatibility and reporting**
   - Depends on: slice 3.
   - Touches: `evals/run_runtime_parallel.py`.
   - Stop condition: parallel runner consumes serial per-row JSON fields and aggregates multi-dimensional counts without duplicating route judgment.
   - Verification: targeted serial and parallel smoke runs agree on row verdict fields.

5. **Metrics, release-gate, and regression-review docs**
   - Depends on: slices 1-4.
   - Touches: `evals/runtime-trial-checklist.md`, `docs/skill-success-metrics.md`, and this PRD only if review finds stale wording.
   - Stop condition: docs explain Intent Frame, route vocabulary, finite measurement tokens, SkillRouter research boundary, targeted-before-default gate, runtime truth alignment, initial routing metrics, regression owner/action requirements, sample-backfill decisions, and no new public skill.
   - Verification: doc stale-state sweep and standard repo doc checks.

6. **Targeted baseline with cache/source equivalence**
   - Depends on: slices 1-5.
   - Touches: `evals/baselines/YYYY-MM-DD-routing-reliability.md`.
   - Stop condition: baseline records targeted routing run, raw result location, pass/partial/fail/blocked counts, metric summary, cache/source equivalence or supported refresh, `git status --short`, and whether runner mutated source.
   - Verification: targeted runtime run and source/cache evidence.

7. **Default-suite promotion decision**
   - Depends on: slice 6 stable baseline.
   - Touches: `evals/run_runtime.py`, `evals/run_runtime_parallel.py`, `evals/runtime-trial-checklist.md`, and baseline notes if promoted.
   - Stop condition: either routing suite remains targeted with a recorded reason, or both runner `DEFAULT_SUITES` lists are updated together after the promotion gate passes with no new forbidden route hit, invalid host preemption, or unclassified route/execution failure.
   - Verification: default-suite run or targeted non-promotion evidence, with failures classified under AC-16 and promotion blockers checked under AC-19.

8. **Deferred pilot decision log**
   - Depends on: slice 6 stable baseline.
   - Touches: `evals/runtime-trial-checklist.md` or release notes only.
   - Stop condition: high-ambiguity pressure test, single-route semantics, lightweight retrieval, and MCP/A2A work are either explicitly deferred or scoped into separate future issues with no first-slice implementation changes.
   - Verification: doc stale-state sweep confirms no deferred pilot is presented as current-scope work.

## 14. Artifact Recommendation

Keep this PRD as the source of truth for the routing reliability increment until it is accepted, split into issues, or superseded by a version-specific PRD.
