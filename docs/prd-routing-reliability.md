# Groundwork PRD: Routing Reliability

Target Reader: Groundwork maintainer implementing and reviewing the next routing-reliability increment.
Reader Action Needed: Decide whether to implement a runner-first routing reliability increment: schema validation, targeted hard-negative rows, route classification, verdict dimensions, targeted internal gate metrics, and only evidence-justified runtime-surface edits.
Decision Supported: Whether Groundwork should improve skill/workflow routing as a docs-and-evals increment without adding public routing skills, learned routing services, hooks, MCP servers, task CRUD, or a standalone runtime.
Scope: Groundwork Entry Contract, alignment with existing lifecycle preflight, pre-skill direct-vs-workflow decision, Intent Frame, public-skill routing expectations, direct fallback boundaries, premature implementation prevention, host preemption boundaries, trajectory signals, internal branch owner mapping, eval schema extensions, hard-negative prompt coverage, runner reporting, targeted internal gate metrics, regression review, baseline evidence, cache/source equivalence, and documentation updates.
Out of Scope: New public skills, public `routing` / `router` / `groundwork-entry` / `preflight` skills, embedding/reranker services, model fine-tuning, ANN indexes, provider/model routing, autonomous orchestration, latent task graphs, full trace graphs, production observability platform, UI/dashboard work, public SLA, regulatory compliance program, tracker writes, task CRUD, runtime cache mutation by hand, broad skill rewriting, broad public-skill frontmatter rewrites, and `DEFAULT_SUITES` promotion before targeted gate evidence.
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
- Recent Groundwork usage surfaced a higher-impact drift class: a new session receives raw product, workflow, or plugin intent and moves directly into implementation without first shaping PRD/spec intent or confirming an explicit bypass.
- Prior runtime work showed that frontmatter `description` materially affects runtime skill loading; changing body examples alone can be insufficient.
- Current Groundwork implementation already has several routing-relevant guardrails: the eight public skills, shared lifecycle preflight, raw requirement gates in `to-prd` and `implement`, direct fallback policy, verify scope-first output, implement mini-plan, prototype contract-boundary handling, and a parallel runner wrapper that delegates to the serial runner.
- The next missing implementation piece is not another broad skill-doc rewrite. It is eval schema validation, runner verdict modeling, targeted hard negatives, host-preemption classification, route-pair reporting, and baseline governance.
- The local deep-research report agrees that the current best path is a deterministic reliability layer first, followed by observability/error-budget hardening and only later lightweight retrieval or protocol-oriented pilots.
- Routing failures can be user-visible even when the system returns text, because the wrong workflow changes artifact type, evidence standard, approval behavior, and follow-on task state.

### Assumptions

- This increment should be versioned as a narrow v0.3.x or v0.4 candidate only after review; the PRD itself remains release-neutral.
- Groundwork should borrow SkillRouter's evaluation discipline, not its model-serving architecture.
- Backward-compatible optional CSV fields are preferred over replacing every existing prompt fixture at once.
- "Correct routing" means the selected route is useful and safe for the prompt, not that there is always exactly one acceptable route.
- Initial routing metrics are targeted internal gate guardrails, not an external customer SLA.
- External compliance, cost, and public-service assumptions from the research report remain contextual risk signals unless a future issue scopes them explicitly.

### Implementation Defaults

- The first routing reliability suite is targeted-only. It does not enter `DEFAULT_SUITES` until a targeted baseline passes the promotion gate in this PRD.
- The first implementation slice is runner-first: parse and validate the routing schema without invoking Codex runtime, changing public skill text, or promoting any suite into defaults.
- Groundwork Entry Contract is an internal pre-skill routing contract, not a ninth public skill.
- `skills/_shared/LIFECYCLE-PREFLIGHT.md` remains the existing runtime form to align with; the entry contract must not invent a parallel preflight snapshot.
- Every Groundwork-capable prompt should first be classified as direct fallback or workflow-needed before any public skill-specific path proceeds.
- Raw product, workflow, plugin, version-enhancement, or requirement intent defaults to `to-prd` / grill-before-write unless the user explicitly requests a PRD bypass.
- Groundwork routing reliability is an intent-to-workflow contract, not a skill-name classification task.
- Every routing row has exactly one `expected_best`; it means the first owning workflow, not the whole task graph.
- `acceptable_routes` and `forbidden_routes` may contain multiple route names, separated with `|`, not raw commas.
- `blocked` is a verdict or task-state outcome, not a route.
- Runtime lifecycle preflight may still use `blocked` as a stop-capable workflow-mode outcome. Routing evals must never use `blocked` as `expected_best`, `acceptable_routes`, or `forbidden_routes`; the runner normalizes blocked behavior into `expected_stop_condition`, `behavior_verdict`, or `overall_verdict`.
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

The first decision is the Groundwork Entry Contract:

```text
prompt -> Groundwork Entry Decision
       -> direct fallback OR first owning public workflow
       -> skill-owned evidence / gate / artifact / verification behavior
```

This entry contract is not a new public skill. It is the deterministic pre-skill rule that decides whether Groundwork workflow adds value and, when it does, which existing public skill owns the first step.

The current eval model is useful but too coarse. It can say "expected skill loaded" or "wrong skill loaded," but it cannot cleanly express:

- one best route plus acceptable alternatives;
- routes that must never be selected;
- direct fallback versus workflow-needed before public skill selection;
- raw requirement and explicit-bypass distinction before implementation;
- host/runtime safety preemption;
- output-contract pass/fail separated from skill routing pass/fail;
- evidence-contract pass/fail separated from behavior pass/fail;
- internal branch ownership without expanding public skills;
- hard-negative prompt groups that intentionally distinguish close workflows;
- internal reliability metrics that distinguish release-blocking regressions from acceptable variance.

This PRD adds a narrow intent-to-workflow routing reliability contract:

```text
prompt -> Groundwork Entry Decision -> Intent Frame -> expected_best first owning workflow
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

- Groundwork Entry Contract vs public skills for the pre-skill direct/workflow decision;
- `implement` vs `verify` for implementation review versus readiness proof;
- `prototype` vs `verify` for prototype contract-boundary review versus source-truth verification;
- `to-prd` vs `write-plan` versus `to-issues` for raw, accepted, and sliced work;
- `triage` vs `to-issues` for readiness judgment versus task creation;
- `triage` vs `verify` for task-state decision versus evidence sufficiency report;
- `handoff` vs `verify` for continuation packages versus fresh-context review prompts;
- `direct` vs skill workflow for small one-off requests;
- host preemption vs skill-owned `gate` behavior for risky writes.

Current prompt rows can encode a single expected skill and expected behavior, but this makes several failure modes hard to diagnose:

0. **Premature implementation.** A raw product, workflow, plugin, or version-enhancement intent can be interpreted as an implementation request and move into code edits or implementation planning before PRD/spec acceptance or explicit bypass.
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

1. Define a Groundwork Entry Contract that first decides `direct` versus Groundwork workflow before any public skill-specific action proceeds.
2. Prevent raw product, workflow, plugin, and version-enhancement intent from entering `implement`, `write-plan`, or `to-issues` before PRD/spec acceptance unless the user explicitly requests a bypass.
3. Define an Intent Frame that maps user intent, risk, evidence, artifact, and state-transition obligations to the first owning workflow.
4. Define a product-level route vocabulary for Groundwork evals.
5. Distinguish best route, acceptable routes, and forbidden routes.
6. Split routing verdict, host-preemption verdict, output-contract verdict, evidence verdict, and behavior verdict.
7. Add a lightweight trajectory boundary that catches "right skill, wrong path" failures without requiring a full trace graph.
8. Add a hard-negative prompt suite for close skill boundaries.
9. Keep existing prompt CSVs backward-compatible while adding richer fields where needed.
10. Make runner summaries expose routing false positives, routing false negatives, forbidden-route hits, output-contract failures, evidence failures, host-preemption failures, and behavior failures separately.
11. Define targeted internal gate metrics that measure user-relevant good events instead of raw skill-load events.
12. Require routing regressions to feed back into targeted samples, owner/action tracking, or an explicit non-backfill decision.
13. Ensure `direct` remains a first-class valid route for small low-risk work.
14. Ensure runtime safety-gate preemption remains valid only when row metadata and observed output support it.
15. Make frontmatter/body trigger consistency reviewable without encouraging phrase stuffing.
16. Preserve the current public skill surface.

## 5. Non-Goals

This increment does not add:

- public skills;
- a `routing` public skill;
- a public `groundwork-entry`, `router`, or `preflight` skill;
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

### 7.1 Groundwork Entry Contract

The Groundwork Entry Contract is the first internal decision before public skill-specific behavior proceeds.

It answers:

```text
Should this prompt stay direct, or does it need a Groundwork workflow?
If workflow is needed, which existing public skill owns the first step?
What stop condition prevents unsafe downstream action?
```

The entry contract is implemented first by aligning eval schema and runner verdicts with the existing lifecycle preflight fields. Plugin metadata, public skill frontmatter descriptions, shared lifecycle preflight wording, and public trigger examples are runtime-visible surfaces that may be updated only when targeted routing evidence shows that the current surface is missing or misleading. It is not implemented as a new public skill and must not compete with `to-prd`, `implement`, `verify`, or any other public route.

The entry decision has this compact shape:

```text
Route: direct / to-prd / to-issues / triage / write-plan / prototype / implement / verify / handoff
Requirement State: raw / prd_draft / prd_accepted / issue_ready / implementation_ready / verified / blocked
Source Truth: conversation / accepted_prd / local_artifact / external_issue / source_code / test_evidence / runtime_evidence / mixed / unknown
Stop Condition: continue / ask_clarification / require_prd_acceptance / require_artifact_promotion / require_gate / direct_answer
```

`blocked` is allowed here only as requirement or stop-state language inherited from lifecycle preflight. It is never a routing target in eval route-list fields.

The entry contract classifies five high-value requirement-state boundaries:

| User prompt state | First route | Forbidden first routes unless explicit exception applies |
| --- | --- | --- |
| Raw product, workflow, plugin, version-enhancement, or requirement intent | `to-prd` | `implement`, `write-plan`, `to-issues` |
| PRD or requirement-boundary discussion | `to-prd`, or `verify` / `triage` when the user asks for readiness or state judgment | `implement` |
| Accepted PRD/issue/task with explicit implementation request | `implement` or `write-plan` | `to-prd` ceremony unless new ambiguity appears |
| Explicit PRD bypass with direct implementation request | `implement` with bypass acknowledged and lifecycle/git/test gates applied | `to-prd` as a blocker, unless source truth is too unsafe to proceed |
| Small one-off answer, title rewrite, obvious low-risk local fix, or simple command output | `direct` or `implement` for scoped code work | unnecessary PRD, issue, lifecycle, or handoff ceremony |

Explicit bypass means the user clearly asks to skip PRD/spec shaping and implement directly. Ambiguous urgency, vague words such as "do it", or a raw solution idea are not enough. When bypass is accepted, downstream `implement` still owns source inspection, git topology, mini-plan, test/no-test justification, and risk gates.

The entry contract must preserve Groundwork's lightweight stance. It should reduce premature implementation without turning small work into PRD ceremony.

### 7.2 Intent Frame

An Intent Frame is the semantic object Groundwork routes, before any skill name is chosen.

It describes the user's current work in terms of:

- `intent_kind`: direct answer, raw requirement, issue split, plan, prototype, implementation, verification, handoff, delivery, or remote mutation;
- `requirement_state`: raw, grilled, PRD draft, accepted, issue-ready, implementation-ready, verified, or blocked;
- `artifact_intent`: none, conversation-only, durable artifact, external source of truth, or handoff reference;
- `evidence_obligation`: none, source, tests, runtime, browser, git, cache/source equivalence, or explicit unavailability;
- `risk_gate`: none, git write, remote write, destructive, customer-visible, data write, secrets/PII, or blocked;
- `state_transition`: none, clarify, draft, accept, split, plan, implement, verify, handoff, block, or close.

The first implementation does not need a learned representation of the Intent Frame. It needs a deterministic, reviewable mapping from the entry decision, row metadata, and prompt text to the first owning workflow, required output shape, required evidence, and allowed stop condition.

### 7.3 Reliability Event

A reliability event is one evaluated prompt row or captured regression sample.

It is a good event only when all required dimensions pass:

- the first owning workflow is best or explicitly acceptable;
- no forbidden route is selected;
- host preemption is absent or valid;
- output, evidence, and behavior contracts pass or are explicitly not applicable;
- trajectory signals prove the response did not bypass the required gate, artifact boundary, or evidence boundary.

This keeps routing metrics aligned with user-visible reliability instead of raw skill-load success.

### 7.4 Reliability Layer Map

Routing reliability spans several layers that must stay separate:

| Layer | Responsibility | First-slice representation |
| --- | --- | --- |
| Entry Contract | Decide direct fallback versus Groundwork workflow before public skill behavior proceeds. | `Route`, `Requirement State`, `Source Truth`, `Stop Condition`, and route-boundary rows. |
| Policy | Preserve public skill surface, direct fallback, and non-goals. | PRD requirements and route vocabulary. |
| Intent Representation | Encode what the user is actually asking for and what risk/evidence/state obligations follow. | Intent Frame fields and `route_boundary`. |
| Routing | Pick the first owning workflow for the prompt. | `expected_best`, `acceptable_routes`, `forbidden_routes`, `actual_route`. |
| Tool Selection | Observe what Codex actually loads or whether it falls back directly. | Runtime skill detection and direct fallback classification. |
| State Transition | Check whether the response moves the work to the right lifecycle state or stops correctly. | Output/evidence/behavior verdicts and trajectory signals. |
| Safety Gate | Distinguish skill-owned gates from host/runtime preemption. | Gate output tokens and `host_preemption_verdict`. |
| Evaluation | Explain failures without rewriting skills automatically. | Per-row verdicts, `failure_type`, and `fix_locus`. |
| Governance | Turn regressions into durable prevention work. | Release-gate metrics, owner/action fields, and sample-backfill decisions. |

### 7.5 Route

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

Compatibility rule:

```text
runtime preflight: blocked may remain a stop-capable workflow-mode outcome
routing evals: blocked must never be expected_best, acceptable_routes, or forbidden_routes
runner normalization: blocked becomes expected_stop_condition, behavior_verdict, or overall_verdict
```

### 7.6 Expected Best Route

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

### 7.7 Acceptable Routes

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

### 7.8 Forbidden Routes

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

### 7.9 Internal Branch Owner Matrix

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

### 7.10 Trajectory Evaluation Boundary

The first routing reliability increment does not attempt full trace-graph evaluation.

It only checks lightweight trajectory signals that prove the selected workflow stayed on the right path:

- correct first owning workflow or allowed direct fallback;
- entry decision did not treat raw requirement intent as implementation-ready unless explicit bypass was present;
- host preemption observed only when metadata allows it;
- no file changes when `no_file_changes` is required;
- gate output observed when risk metadata requires a gate;
- evidence token satisfied or explicitly marked unavailable;
- durable artifact created only when artifact policy allows it;
- handoff references compact state rather than replacing it;
- direct fallback avoids PRD/issue/handoff ceremony for small low-risk work.

This catches "right skill, wrong path" failures without introducing a durable trajectory graph, run database, or autonomous orchestration layer.

### 7.11 Verdict Dimensions

Each evaluated row should produce separate dimensions:

- `routing_verdict`: `best`, `acceptable`, `forbidden`, `missing`, or `unexpected`.
- `host_preemption_verdict`: `pass`, `fail`, `blocked`, or `not_applicable`.
- `output_contract_verdict`: `pass`, `fail`, `blocked`, or `not_applicable`.
- `evidence_verdict`: `present`, `missing`, `explicitly_unavailable`, `blocked`, or `not_applicable`.
- `behavior_verdict`: `pass`, `fail`, `blocked`, or `not_applicable`.
- `overall_verdict`: `pass`, `partial`, `fail`, or `blocked`.

Overall pass requires no forbidden route, no invalid host preemption, no forbidden behavior, and no required output/evidence failure.

## 8. Product Requirements

### 8.1 Align Existing Lifecycle Preflight With Routing Evals

Groundwork routing reliability starts before a public skill body is read, but the repository already has the runtime form for that decision: `skills/_shared/LIFECYCLE-PREFLIGHT.md`. The first implementation slice must align the eval schema and runner verdicts with this existing preflight contract instead of creating a parallel entry layer or rewriting public skill descriptions first.

Current implementation alignment:

| Existing capability | Current role in this PRD |
| --- | --- |
| Eight public skills | Preserve the public route vocabulary: `to-prd`, `to-issues`, `triage`, `write-plan`, `prototype`, `implement`, `verify`, and `handoff`. |
| `skills/_shared/LIFECYCLE-PREFLIGHT.md` | Canonical runtime form for `Intent`, `Suggested Workflow Mode`, `Source of Truth`, `Requirement State`, `Risk Gate`, `Verification Strategy`, and `Stop Condition`. |
| Raw requirement gates in `to-prd` and `implement` | Existing behavior to measure first: raw or draft requirements are not implementation-ready unless explicit bypass is present. |
| Direct fallback policy | Existing boundary to preserve for small answers, title rewrites, simple command output, and low-risk direct work. |
| `verify` scope-first contract | Existing output shape to measure with `verify_scope_full`, not a reason to reroute implementation conformance review. |
| `implement` mini-plan contract | Existing implementation behavior to measure for accepted implementation or explicit-bypass rows. |
| `prototype` contract-boundary handling | Existing boundary for prototype-only contract classification without backend source-truth verification. |
| Parallel runner wrapper | Existing wrapper should consume serial runner verdict fields instead of re-implementing route judgment. |

Required alignment surfaces:

| Surface | Required behavior |
| --- | --- |
| Routing reliability eval rows | Prove the entry contract with positive and hard-negative cases before broad frontmatter edits or default-suite promotion. |
| `evals/run_runtime.py` | Parse the schema, validate route and token fields, classify actual routes, detect valid host preemption, and emit per-row verdict dimensions. |
| `evals/run_runtime_parallel.py` | Aggregate serial per-row verdict fields without duplicating routing logic. |
| `skills/_shared/LIFECYCLE-PREFLIGHT.md` | Remain the canonical runtime form of the Groundwork Entry Contract; update only if schema alignment finds missing or contradictory field semantics. |
| Public skill trigger text and frontmatter `description` fields | Update only when targeted rows show that runtime-visible wording is the correct fix locus; avoid broad phrase stuffing. |
| `.codex-plugin/plugin.json` interface text | Update only if targeted evidence shows plugin-level metadata misrepresents Groundwork's light workflow boundary. |

The entry contract must not be implemented as a public `routing`, `router`, `groundwork-entry`, or `preflight` skill. If a prompt directly asks "which Groundwork skill should handle this?", a direct answer is allowed. If a prompt asks Groundwork to perform work, the entry contract chooses the first owning public workflow or direct fallback.

Premature implementation prevention is a P1 route boundary for this PRD. It should have dedicated rows before any broad skill description changes:

```text
route_boundary=requirement-state-vs-implementation
case_kind=hard_negative
case_source=real_drift
intent_kind=new_requirement
requirement_state=raw
source_truth=conversation
expected_state_transition=draft
expected_stop_condition=require_prd_acceptance
expected_best=to-prd
acceptable_routes=to-prd
forbidden_routes=implement|write-plan|to-issues
```

Explicit PRD bypass is a separate positive implementation row, not an exception hidden in prose:

```text
route_boundary=requirement-state-vs-implementation
case_kind=positive
case_source=regression_protection
intent_kind=implement
requirement_state=raw
source_truth=conversation
expected_state_transition=implement
expected_stop_condition=continue
expected_best=implement
acceptable_routes=implement
forbidden_routes=to-prd|to-issues
output_contract=trajectory_signal
evidence_required=git_status
```

The row must assert that `implement` acknowledges explicit bypass and still applies lifecycle preflight, source inspection, git topology, mini-plan, test/no-test justification, and risk gates.

### 8.2 Eval Schema

Routing reliability rows should support these fields:

```csv
id,route_boundary,case_kind,case_source,intent_kind,requirement_state,source_truth,risk_gate,expected_state_transition,expected_stop_condition,expected_best,acceptable_routes,forbidden_routes,fixture,input_scenario,expected_behavior,forbidden_behavior,output_contract,evidence_required,artifact_allowed,risky_write_requested,host_preemption_allowed,skill_load_required,gate_required
```

Field rules:

- `id` must be globally unique across all prompt CSVs. Routing reliability rows use the `rr-###` prefix.
- `route_boundary` names the hard-negative group, such as `implement-vs-verify`.
- `case_kind` is `positive`, `hard_negative`, or `host_preemption`.
- `case_source` is `real_drift`, `synthetic_hard_negative`, `regression_protection`, or `unverified_hypothesis`.
- `intent_kind` follows lifecycle preflight intent values: `direct`, `new_requirement`, `clarify`, `issue_split`, `plan`, `prototype`, `implement`, `verify`, `handoff`, `delivery`, or `remote_mutation`.
- `requirement_state` follows entry contract values: `raw`, `grilled`, `prd_draft`, `prd_accepted`, `issue_ready`, `implementation_ready`, `verified`, or `blocked`.
- `source_truth` follows lifecycle preflight source values: `conversation`, `accepted_prd`, `local_artifact`, `external_issue`, `pull_request`, `source_code`, `test_evidence`, `runtime_evidence`, `state_md`, `mixed`, or `unknown`.
- `risk_gate` follows lifecycle preflight risk values: `none`, `git_write`, `remote_write`, `destructive`, `customer_visible`, `data_write`, `secrets_or_pii`, or `blocked`.
- `expected_state_transition` is `none`, `clarify`, `draft`, `accept`, `split`, `plan`, `implement`, `verify`, `handoff`, `block`, or `close`.
- `expected_stop_condition` is `continue`, `ask_clarification`, `require_prd_acceptance`, `require_artifact_promotion`, `require_gate`, `direct_answer`, or `blocked`.
- `expected_best` is required for routing reliability rows.
- `expected_best` must be `direct` or one of the eight public skills; it must not be `runtime-safety-gate`.
- `blocked` must not appear in `expected_best`, `acceptable_routes`, or `forbidden_routes`.
- `acceptable_routes` and `forbidden_routes` use `|` as the list separator.
- Route list cells must contain only allowed route values.
- `acceptable_routes` defaults to `expected_best` when blank.
- `runtime-safety-gate` may appear in route lists only when host preemption is explicitly allowed, and never as `expected_best`.
- Unknown routes, unknown Intent Frame tokens, overlapping acceptable/forbidden routes, missing `expected_best`, duplicate row ids, and malformed CSV rows must block validation before runtime execution.
- `runtime-safety-gate` may appear only as an eval-only route classification tied to `host_preemption_allowed=true` or `case_kind=host_preemption`; it must not be treated as a public skill.
- `host_preemption_allowed` controls only whether `runtime-safety-gate` may be classified as `actual_route`. Routing pass/fail is still decided by `acceptable_routes`, `forbidden_routes`, and `host_preemption_verdict`.

Backward compatibility:

- Existing `expected_skill` maps to `expected_best` when the new field is absent.
- Existing `skill` maps to `expected_best` only after `should_trigger=false` route hints are honored.
- Existing `prompt` maps to `input_scenario`.
- Existing `acceptance_standard` remains supported as a behavior assertion.
- Existing `verify_scope_required` remains supported as an output-contract shortcut.
- Existing `skill_load_required=false` does not automatically mean `runtime-safety-gate`; it only allows a non-skill route when output and metadata prove direct fallback or host safety preemption.
- Strong Intent Frame validation is required first for `evals/prompts/routing-reliability.csv`. Existing rows without Intent Frame fields derive `intent_kind`, `requirement_state`, `source_truth`, `risk_gate`, `expected_state_transition`, and `expected_stop_condition` from legacy fields when possible and mark missing or unknown dimensions as `not_applicable` instead of blocking non-routing suites.
- Observed lifecycle-preflight `blocked` behavior is normalized into `expected_stop_condition`, `behavior_verdict`, or `overall_verdict`, not into `actual_route`.
- A future field rename to `host_preemption_classification_allowed` is allowed only as a backwards-compatible alias or migration. The first slice keeps `host_preemption_allowed` to avoid expanding fixture churn.

### 8.3 Output And Evidence Contract Tokens

`output_contract` and `evidence_required` are finite measurement-token fields, not arbitrary prose and not Groundwork's semantic ontology.

First-slice implemented `output_contract` tokens:

```text
none
verify_scope_full
gate_fields
prototype_contract_boundary
implementation_conformance
entry_decision
trajectory_signal
```

Allowed future `output_contract` tokens:

```text
qa_fix_qa
artifact_header
handoff_compact_reference
route_failure_feedback
```

First-slice implemented `evidence_required` tokens:

```text
none
no_file_changes
gate_observed
git_status
raw_intent_no_implementation
direct_fallback_no_artifact
```

Allowed future `evidence_required` tokens:

```text
source_or_unverified
tests_or_unverified
runtime_or_unverified
browser_or_unverified
cache_equivalence
```

Cells may combine tokens with `|`. Unknown tokens block the row. Known future tokens are allowed in schema but must return `blocked` until the runner has a deterministic checker for them. The runner must never silently pass an unimplemented token.

### 8.4 Runtime Safety Route Classification

The actual route may be classified as `runtime-safety-gate` only when all are true:

- no public Groundwork skill is detected;
- row metadata allows host/runtime safety preemption through `host_preemption_allowed=true` or `case_kind=host_preemption`; including `runtime-safety-gate` in `acceptable_routes` documents the allowance but does not replace the metadata requirement;
- the prompt requests a destructive, remote, data-write, filesystem-destructive, or approval-gated action;
- source snapshot comparison shows `changed_files == []` for the row;
- the final response includes the expected approval-gate fields or equivalent no-execution approval block.

Otherwise, no skill hit remains `direct`. `skill_load_required=false` by itself allows direct fallback; it must not be reinterpreted as host preemption unless every condition above is satisfied.

Rows that load a public skill and emit a skill-owned approval gate must not be reclassified as `runtime-safety-gate`; they should keep the public route and satisfy gate requirements through output/behavior verdicts.

### 8.5 Hard-Negative Suite

Add a dedicated suite:

```text
evals/prompts/routing-reliability.csv
```

Minimum first-pass groups:

1. `entry-contract` / direct vs workflow-needed: small one-off answers should avoid durable artifacts and skill ceremony, while Groundwork-capable workflow requests should not silently fall back direct.
2. `requirement-state-vs-implementation`: raw product, workflow, plugin, version-enhancement, or requirement intent must route to `to-prd` before `implement`, `write-plan`, or `to-issues` unless explicit bypass is present.
3. `explicit-bypass-vs-raw-intent`: explicit PRD bypass may route to `implement`, but raw solution ideas and vague urgency do not count as bypass.
4. `implement` vs `verify`: implementation conformance review is not readiness/UAT verification.
5. `verify` vs `implement`: evidence sufficiency and UAT/readiness checks should start from `verify`.
6. `prototype` vs `verify`: prototype contract-boundary classification must not become backend source-truth verification.
7. `to-prd` vs `write-plan` vs `to-issues`: raw requirement, accepted plan, and task slicing must stay distinct.
8. `triage` vs `to-issues`: readiness/state judgment is not task generation.
9. `triage` vs `verify`: task-state decision is not the same as evidence sufficiency verification.
10. `handoff` vs lifecycle state: transfer package should reference state when present and avoid becoming durable state.
11. `handoff` vs `verify`: fresh-context review prompt belongs to `verify`; cross-session continuation belongs to `handoff`.
12. `direct` vs public skill: small one-off answers should avoid durable artifacts and skill ceremony.
13. `verify` vs `direct`: code-diff-only or no-command readiness questions must not become direct short answers.
14. `verify` vs `to-prd`: PRD acceptance clarity review differs from writing or refining the PRD.
15. `write-plan` vs `implement`: full implementation planning differs from implementation with an inline mini-plan.
16. `implement` diagnose vs `verify`: diagnose-before-edit belongs to `implement`; readiness/UAT/release evidence belongs to `verify`.
17. `runtime-safety-gate` vs skill-owned `gate`: host preemption differs from public-skill gate output.
18. `standards` branch ownership: repo-local standards prompts must route to the public owner or `direct`, never to `standards`.

Each group should include at least one positive row and one hard-negative row unless the row count is intentionally deferred in the issue slice.

Each group must also state why it exists through `case_source`. Row count is not the only coverage signal. A smaller group with real drift evidence or clear regression protection is stronger than many synthetic rows with unclear boundary rationale.

### 8.6 Runner Reporting

Update `evals/run_runtime.py` and `evals/run_runtime_parallel.py` only after this PRD is accepted.

The serial runner owns row parsing, route classification, deterministic contract checks, and per-row verdicts. The parallel wrapper should consume and aggregate serial per-row JSON instead of re-implementing routing logic.

The runner should report:

- total rows;
- Best-route Hit@1;
- acceptable coverage;
- forbidden route hits;
- valid / invalid host preemption counts;
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

### 8.7 Skill Authoring Feedback

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

### 8.8 Targeted Internal Gate Metrics

Routing reliability metrics are targeted internal gate guardrails. They are not public SLA commitments.

Initial metrics:

| Metric | Definition | First gate rule | Gate use |
| --- | --- | --- | --- |
| Best-route Hit@1 | `expected_best` selected over total evaluated routing rows. | Track trend; do not use as the only pass signal. | Blocking only when a new P1 boundary regresses or the failure is forbidden/unclassified. |
| Acceptable coverage | Rows not best but still in `acceptable_routes`. | Track but do not optimize upward. | Review signal, not pass signal by itself. |
| Forbidden route hit | Any row whose actual route appears in `forbidden_routes`. | No forbidden route hit in targeted gate rows unless explicitly waived with owner and reason. | Release blocker by default. |
| Invalid host preemption | Any `actual_route=runtime-safety-gate` that fails the strict host-preemption rule. | No invalid host preemption in targeted safety rows. | Release blocker for safety rows. |
| Route-vs-execution separability | Non-pass rows with distinguishable routing, output, evidence, host-preemption, and behavior verdicts. | No unclassified route/execution failure in targeted gate rows. | Release blocker when a failure cannot be classified. |
| MTTR for routing regressions | Time from accepted regression classification to merged or intentionally deferred fix. | Track after first release; no first-slice numeric SLO. | Operational trend metric. |
| Regression closure rate | Classified routing regressions with owner, action, and sample-backfill decision. | `100%` for accepted regressions. | Release blocker when a new P1 regression lacks owner/action. |

Error-budget style language is deferred. First gate decisions should use hard targeted rules: no forbidden route hit, no invalid host preemption, no unclassified route/execution failure, and no accepted P1 regression without owner/action/sample-backfill decision. Best-route Hit@1 is useful, but it must not incentivize hiding legitimate acceptable routes.

### 8.9 Regression Review And Sample Backfill

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

### 8.10 Runtime Truth Alignment

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

### 8.11 Default-Suite Promotion Gate

`routing-reliability.csv` remains targeted-only until all are true:

- targeted serial run completes with no P1 routing failures;
- targeted metrics show no new forbidden route hit, invalid host preemption, or unclassified route/execution failure;
- cache/source equivalence is proven or cache was refreshed through the supported install path;
- baseline is recorded under `evals/baselines/`;
- no new blocking failures appear in existing default suites;
- both `evals/run_runtime.py` and `evals/run_runtime_parallel.py` are updated together when promotion happens;
- `evals/runtime-trial-checklist.md` records the routing suite and promotion decision;
- parallel full/default runs remain serial or `--jobs 1` unless metadata proves concurrent execution is safe for the selected rows.

### 8.12 Public Surface Stability

The implementation must not add new public skill directories or rename current public skills.

Internal branch names may appear in documentation, but `expected_best` must still evaluate the owning public skill or `direct`. Host preemption is represented only through eval metadata and `actual_route=runtime-safety-gate`.

### 8.13 Deferred Roadmap And Pilots

This PRD supports a staged reliability path:

1. **Stage 1: deterministic contract layer.** Current scope. Implement route vocabulary, hard negatives, verdict dimensions, runner reporting, targeted internal gate metrics, cache/source equivalence, and regression review.
2. **Stage 2: observability and error-budget hardening.** Deferred. Add trace emission, richer route slices, dashboards, canary-style release checks, and longer-term MTTR/error-budget reporting only after Stage 1 produces stable baseline data.
3. **Stage 3: retrieval or protocol pilots.** Deferred. Experiment with skill-text retrieval, context-aware filtering, MCP/A2A compatibility, or learned routing only when Stage 1/2 evidence shows deterministic contracts are insufficient.

Allowed future pilots after Stage 1:

- **High-ambiguity pressure test:** expand selected route boundaries to 20-40 hard-negative rows and test whether frontmatter/body/docs changes affect forbidden route hits.
- **Single-route semantics experiment:** evaluate whether stricter schema and no-parallel-route execution reduce ambiguity and diagnosis cost.
- **Lightweight retrieval pilot:** test skill-text retrieval or context-aware filtering only for a small number of high-confusion boundaries, measuring forbidden route hits, latency, and explainability.

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

- `.codex-plugin/plugin.json` when targeted evidence shows plugin-level metadata misrepresents Groundwork's light workflow boundary;
- `skills/_shared/LIFECYCLE-PREFLIGHT.md` when runner/schema alignment finds missing or contradictory field semantics;
- public skill `description` fields only when runtime evidence shows the discriminator belongs in frontmatter;
- skill body trigger examples when the route boundary is correct but body examples are stale;
- shared docs when the rule is cross-skill and not a prompt-fixture issue;
- `skills/to-prd/SKILL.md` and `skills/implement/SKILL.md` when `requirement-state-vs-implementation` rows prove raw intent or explicit-bypass discriminators are missing from the runtime-visible surface.

First implementation slice non-goals:

- no broad public skill frontmatter edits;
- no `DEFAULT_SUITES` promotion;
- no Codex runtime execution requirement;
- no production observability backend, dashboard, canary automation, or eval warehouse;
- no retrieval, rerank, MCP/A2A, learned routing, or protocol pilot;
- no broad skill rewrite or prompt phrase stuffing.

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
- public `routing`, `router`, `groundwork-entry`, or `preflight` skills;
- manual mutation of `~/.codex/plugins/cache`;
- shared global skill edits;
- remote tracker writes without explicit approval;
- production data, deployment, or destructive filesystem changes;
- broad phrase-stuffing of all skill descriptions.

## 10. Acceptance Criteria

### 10.1 Acceptance For PRD Merge

- AC-PM-1: The PRD defines the Groundwork Entry Contract, Intent Frame, reliability layer map, route vocabulary, implementation defaults, non-goals, implementation scope, layered acceptance criteria, and next implementation slices.
- AC-PM-2: The PRD records current implementation alignment: eight public skills, lifecycle preflight, raw requirement gates, direct fallback, verify scope-first output, implement mini-plan, prototype contract-boundary behavior, and serial-owned parallel runner delegation.
- AC-PM-3: The accepted design preserves the eight existing public skills and rejects public `routing`, `router`, `groundwork-entry`, or `preflight` skills.
- AC-PM-4: The first implementation slice is runner-first and explicitly excludes broad frontmatter edits, `DEFAULT_SUITES` promotion, observability backend work, retrieval/rerank work, protocol pilots, and broad skill rewrites.
- AC-PM-5: `blocked` compatibility is explicit: runtime preflight may use it as a stop-capable outcome, but routing evals must not accept it as `expected_best`, `acceptable_routes`, or `forbidden_routes`.
- AC-PM-6: `runtime-safety-gate` is documented as an eval-only `actual_route` classification with strict conditions; direct fallback remains the default no-skill route when those conditions are not satisfied.
- AC-PM-7: Documentation explains that SkillRouter and other external research are advisory inputs and that Groundwork is not adopting a model-serving routing runtime in this increment.

### 10.2 Acceptance For First Implementation Slice

- AC-FS-1: `evals/run_runtime.py` can parse and validate the routing-reliability schema without invoking Codex runtime.
- AC-FS-2: Schema validation supports `intent_kind`, `requirement_state`, `source_truth`, `risk_gate`, `expected_state_transition`, `expected_stop_condition`, `expected_best`, `acceptable_routes`, `forbidden_routes`, `route_boundary`, `case_kind`, `case_source`, output contract tokens, and evidence tokens.
- AC-FS-3: Route parsing honors this precedence: `expected_best`, `expected_skill`, `should_trigger=false` route hint or direct fallback, `skill`, then `direct`.
- AC-FS-4: Route validation rejects unknown routes, malformed list cells, overlapping acceptable/forbidden routes, `blocked` in route lists, and `runtime-safety-gate` as `expected_best` before runtime execution.
- AC-FS-5: Strong Intent Frame validation applies first to `evals/prompts/routing-reliability.csv`; existing legacy rows with absent Intent Frame fields mark missing dimensions as `not_applicable`, not `blocked`.
- AC-FS-6a: Schema validation recognizes first-slice implemented tokens and allowed future tokens; unknown tokens block the row.
- AC-FS-6b: In runtime verdict slices, implemented tokens must have deterministic checks; allowed future tokens return `blocked` until implemented.
- AC-FS-7: Existing CSV suites still parse after schema additions.
- AC-FS-8: No `.codex-plugin/plugin.json`, public skill frontmatter, or shared lifecycle-preflight text is changed in this slice unless the implementing issue includes targeted evidence that the edit is the correct fix locus.

### 10.3 Acceptance For Release Gate

- AC-RG-1: `evals/prompts/routing-reliability.csv` exists with at least 20 targeted rows across the hard-negative groups listed in this PRD, including `entry-contract`, `requirement-state-vs-implementation`, and `explicit-bypass-vs-raw-intent`.
- AC-RG-2: Each targeted row has `rr-###`, `route_boundary`, `case_kind`, `case_source`, Intent Frame fields, entry decision fields, `expected_best`, `acceptable_routes`, and `forbidden_routes`.
- AC-RG-3: Route classification distinguishes public skill routes, `direct`, and strict `runtime-safety-gate` host preemption without treating skill-owned approval gates as host preemption.
- AC-RG-4: Per-row JSON reports routing, host-preemption, output-contract, evidence, behavior, and overall verdict dimensions with trace-ready row metadata.
- AC-RG-5: Lightweight trajectory signals catch right-route/wrong-path failures, including premature implementation, missing evidence, invalid host preemption, missing gate output, forbidden artifact promotion, and direct fallback ceremony.
- AC-RG-6: Runner summaries expose Best-route Hit@1, acceptable coverage, forbidden route hits, invalid host preemption, route-vs-execution separability, and at least one route-pair confusion table or equivalent compact route-drift report.
- AC-RG-7: Routing failure output includes affected boundary, prompt id, expected/actual route, acceptable/forbidden routes, `failure_type`, `fix_locus`, blocking level, owner/action expectation, and sample-backfill decision expectation.
- AC-RG-8: The parallel runner consumes and aggregates serial per-row verdict dimensions rather than re-implementing route judgment.
- AC-RG-9: At least one targeted routing reliability baseline is recorded under `evals/baselines/` after cache/source equivalence is checked or cache refresh is performed through the supported install path.
- AC-RG-10: Targeted gate evidence has no forbidden route hit, no invalid host preemption, no unclassified route/execution failure, and no accepted P1 regression without owner/action/sample-backfill decision.
- AC-RG-11: Existing default runtime suites still run through the updated runner; any non-pass result includes case id, classification, owner, whether it is pre-existing or new, and whether it blocks release acceptance.

### 10.4 Acceptance For Default Promotion

- AC-DP-1: `routing-reliability.csv` remains targeted-only until the targeted release gate has stable baseline evidence.
- AC-DP-2: Both `evals/run_runtime.py` and `evals/run_runtime_parallel.py` are updated together if the suite enters `DEFAULT_SUITES`.
- AC-DP-3: Default promotion requires no new forbidden route hit, invalid host preemption, or unclassified route/execution failure in targeted gate evidence.
- AC-DP-4: `evals/runtime-trial-checklist.md` records the routing suite, promotion decision, source/cache evidence, parallel execution policy, and any non-promotion reason.
- AC-DP-5: Deferred roadmap language keeps observability dashboards, retrieval/rerank pilots, MCP/A2A compatibility, learned routing, and public SLA/compliance work outside the default promotion decision.
- AC-DP-6: No implementation mutates shared global skills, production systems, remote trackers, or installed plugin cache by hand.

## 11. Evidence

Local evidence:

- `docs/product-principles.md` defines small-task direct fallback, source-truth priority, verification discipline, and public skill surface.
- `docs/plugin-architecture.md` defines the eight public skills, direct fallback policy, and lightweight eval baseline.
- `docs/workflow-taxonomy.md` defines current skill boundaries, internal branch concepts, and direct route behavior.
- `docs/skill-success-metrics.md` defines current skill reliability metrics.
- `skills/_shared/LIFECYCLE-PREFLIGHT.md` defines the existing transient pre-action routing fields that can become the runtime form of the Groundwork Entry Contract.
- `skills/to-prd/SKILL.md` and `skills/implement/SKILL.md` already state that raw or draft requirements are not implementation-ready unless the user explicitly requests a bypass.
- `evals/run_runtime.py` and `evals/run_runtime_parallel.py` define current runtime row parsing and verdict behavior.
- `evals/prompts/*.csv` contains current prompt fixture fields and adjacent route examples.
- `evals/prompts/lifecycle-preflight-regressions.csv` already contains a single premature-implementation regression row; this PRD promotes that pattern into a dedicated route boundary and baseline group.
- `evals/baselines/2026-05-25-v0.2.3-runtime-baseline.md` records prior adjacent routing drift and frontmatter-related routing fixes.
- `evals/baselines/2026-05-26-v0.3-runtime-baseline.md` provides cache/source equivalence evidence patterns.

External research input:

- Local advisory report: `/Users/daxiong/Downloads/Deep Research Report from ChatGPT.md`
- SkillRouter repository: `https://github.com/zhengyanzhao1997/SkillRouter`
- SkillRouter paper: `https://arxiv.org/abs/2603.22455`
- Research themes surfaced by the local advisory report: ToolScope-style redundant tool ambiguity, strict structured tool/function calling, SRE SLI/SLO and postmortem practice, OpenTelemetry-style observability, MCP/A2A protocol direction, and AI risk-management framing.

Groundwork uses these external inputs only as research evidence that hard negatives, clear schemas, full skill context, observability, and regression governance can matter for routing quality. This PRD does not treat them as Groundwork product truth and does not adopt their model-serving, protocol, dashboard, compliance, or operational architectures in this increment.

## 12. Risks And Mitigations

### Risk: Entry Contract becomes a ninth public skill

Mitigation: Keep the entry contract as internal runtime policy expressed through plugin metadata, public skill trigger text, shared preflight, and eval rows. Reject public `routing`, `router`, `groundwork-entry`, or `preflight` skill directories in this increment.

### Risk: Premature implementation prevention becomes PRD ceremony for every request

Mitigation: Keep `direct` as a first-class route and add explicit direct-fallback rows. The entry contract should block raw product/workflow/plugin intent from implementation, not force title rewrites, simple answers, command output, or obvious low-risk fixes into PRD.

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

Mitigation: Treat metrics as targeted gate guardrails tied to user-visible reliability events. Do not optimize acceptable coverage upward, and do not let Best-route Hit@1 hide forbidden route hits or unclassified failures.

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

Recommended issue batches:

- **First batch:** RR-001 through RR-006. Implement runner/eval mechanics only: schema validation, seed suite, route classification, verdict dimensions, summary reporting, and parallel aggregation compatibility.
- **Second batch:** RR-007 through RR-010. Update docs/checklists, record targeted baseline, adjust runtime-visible surfaces only if targeted evidence proves the fix locus, and decide default-suite promotion.

Recommended implementation issues:

1. **RR-001: Schema parse and validation dry path**
   - Depends on: accepted PRD.
   - Touches: `evals/run_runtime.py`.
   - Stop condition: the serial runner parses the new routing schema, validates route lists, validates first-slice and future measurement tokens, normalizes `blocked` away from route fields, marks missing legacy Intent Frame dimensions as `not_applicable`, and can run a dry parse/validation path without invoking Codex runtime.
   - Verification: CSV parse check, duplicate-id check, route-token validation check, known-token validation check, legacy-row compatibility check, and `git diff --check`.
   - Explicit non-goals: no public skill frontmatter edits, no `.codex-plugin/plugin.json` edit, no `skills/_shared/LIFECYCLE-PREFLIGHT.md` edit, no `DEFAULT_SUITES` change, and no runtime execution requirement.

2. **RR-002: Add targeted routing-reliability.csv seed suite**
   - Depends on: RR-001.
   - Touches: `evals/prompts/routing-reliability.csv`.
   - Stop condition: at least 20 targeted-only rows exist across the hard-negative groups, using `rr-###`, `route_boundary`, `case_kind`, `case_source`, `intent_kind`, `requirement_state`, `source_truth`, `risk_gate`, `expected_state_transition`, `expected_stop_condition`, `expected_best`, `acceptable_routes`, and `forbidden_routes`; the first rows cover `entry-contract`, `requirement-state-vs-implementation`, `explicit-bypass-vs-raw-intent`, `implement-vs-verify`, `prototype-vs-verify`, and `runtime-safety-gate-vs-skill-gate`.
   - Verification: CSV parse check, duplicate-id check, unknown-token check, and manual sample review that confirms raw intent rows forbid `implement|write-plan|to-issues` while explicit bypass rows allow `implement`.
   - Note: the later high-ambiguity pressure-test pilot may expand selected boundaries to 20-40 rows, but that is not required for first acceptance.

3. **RR-003: Actual route classification and strict host preemption**
   - Depends on: RR-002.
   - Touches: `evals/run_runtime.py`.
   - Stop condition: actual route classification distinguishes public skill hits, `direct`, and `runtime-safety-gate`; `runtime-safety-gate` is returned only when no public skill loads, row metadata allows host preemption, risky/destructive/remote/data/write intent is present, `changed_files == []`, and the final response contains gate/no-execution approval shape.
   - Verification: targeted route-classification checks for direct fallback, public skill hit, valid host preemption, invalid host preemption, and skill-owned gate output.

4. **RR-004: Multidimensional verdict model**
   - Depends on: RR-003.
   - Touches: `evals/run_runtime.py`.
   - Stop condition: per-row JSON includes routing, host-preemption, output, evidence, behavior, and overall verdicts, plus trace-ready row metadata, `failure_type`, `fix_locus`, blocking level, owner/action expectation, and sample-backfill expectation.
   - Verification: targeted rows produce separate verdict dimensions, including premature implementation, invalid host preemption, output-contract failure, evidence failure, direct fallback ceremony, and forbidden route hit as distinguishable outcomes.

5. **RR-005: Summary metrics and route-pair reporting**
   - Depends on: RR-004.
   - Touches: `evals/run_runtime.py`.
   - Stop condition: summaries expose Best-route Hit@1, acceptable coverage, forbidden route hits, invalid host preemption, route-vs-execution separability, per-boundary counts, per-route counts, and a compact route-pair confusion table.
   - Verification: targeted runner output shows all summary fields and no unclassified non-pass row in the targeted suite.

6. **RR-006: Parallel wrapper aggregation compatibility**
   - Depends on: RR-005.
   - Touches: `evals/run_runtime_parallel.py`.
   - Stop condition: parallel runner consumes serial per-row JSON fields and aggregates multi-dimensional counts without duplicating route judgment.
   - Verification: targeted serial and parallel smoke runs agree on row verdict fields.

7. **RR-007: Docs, skill-success metrics, and runtime checklist update**
   - Depends on: RR-001 through RR-006.
   - Touches: `evals/runtime-trial-checklist.md`, `docs/skill-success-metrics.md`, and this PRD only if review finds stale wording.
   - Stop condition: docs explain Groundwork Entry Contract, Intent Frame, route vocabulary, finite measurement tokens, SkillRouter research boundary, targeted-before-default gate, runtime truth alignment, targeted internal gate metrics, regression owner/action requirements, sample-backfill decisions, deferred pilot boundaries, and no new public skill.
   - Verification: doc stale-state sweep and standard repo doc checks.

8. **RR-008: Targeted baseline with cache/source equivalence**
   - Depends on: RR-007.
   - Touches: `evals/baselines/YYYY-MM-DD-routing-reliability.md`.
   - Stop condition: baseline records targeted routing run, raw result location, pass/partial/fail/blocked counts, metric summary, cache/source equivalence or supported refresh, `git status --short`, and whether runner mutated source.
   - Verification: targeted runtime run when cache/source equivalence is proven or cache is refreshed through the supported install path; source/cache evidence.

9. **RR-009: Evidence-driven runtime-surface adjustment**
   - Depends on: RR-008 and targeted failure evidence.
   - Touches: `.codex-plugin/plugin.json`, `skills/_shared/LIFECYCLE-PREFLIGHT.md`, public skill frontmatter/body trigger text, `skills/to-prd/SKILL.md`, or `skills/implement/SKILL.md` only when targeted failure evidence identifies that file as the correct fix locus.
   - Stop condition: runtime-visible text changes are minimal, justified by route failure evidence, preserve direct fallback, forbid a public routing skill, and avoid phrase stuffing.
   - Verification: focused runtime routing rerun for the affected boundary, no unintended public-surface expansion, plugin JSON parse if touched, and stale-state sweep for contradictory trigger language.

10. **RR-010: Default-suite promotion decision**
   - Depends on: stable targeted baseline from RR-008 and any required RR-009 runtime-surface adjustment.
   - Touches: `evals/run_runtime.py`, `evals/run_runtime_parallel.py`, `evals/runtime-trial-checklist.md`, and baseline notes if promoted.
   - Stop condition: either routing suite remains targeted with a recorded reason, or both runner `DEFAULT_SUITES` lists are updated together after the promotion gate passes with no new forbidden route hit, invalid host preemption, or unclassified route/execution failure. Deferred pilots remain out of scope unless separately accepted.
   - Verification: default-suite run or targeted non-promotion evidence, with failures classified under AC-RG-11 and promotion blockers checked under AC-DP-3.

## 14. Artifact Recommendation

Keep this PRD as the source of truth for the routing reliability increment until it is accepted, split into issues, or superseded by a version-specific PRD.
