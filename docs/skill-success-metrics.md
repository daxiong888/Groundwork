# Skill Success Metrics

Target Reader: Groundwork maintainer reviewing skill reliability and future harness output.
Reader Action Needed: Use these metrics consistently in manual baselines and future automated reports.
Decision Supported: Whether a skill prompt passed, partially passed, failed, or was blocked and what follow-up is justified.
Artifact Type: canonical maintainer metrics vocabulary.
Source of Truth: this document, `evals/routing_schema.py`, `evals/verdict_model.py`, and `docs/quarantined-learnings.md` for maintainer-learning fields.
Scope: Metrics vocabulary for prompt fixtures, guardrail regression checks, nightly harness reports, and learning proposals.
Out of Scope: A required JSON schema, database model, dashboard, or automatic patch acceptance.
Evidence Level: Groundwork issue #15 acceptance criteria and current eval prompt fields.
Safe to Share / Redaction Notes: Safe to share as a field vocabulary; raw prompts, traces, and private payloads still require review/redaction.

## Metrics

Record these fields for each evaluated prompt:

- `triggered_skill`: skill proven by authoritative skill-load trace; use `unknown` when that evidence is unavailable. Do not infer it from final-answer shape.
- `expected_skill`: skill expected by the fixture, or `direct`.
- `false_positive`: `true` when a skill workflow ran but should not have.
- `false_negative`: `true` when the expected skill did not load.
- `artifact_target_reader_present`: `true` when a durable artifact has a clear target reader.
- `verify_scope_present`: `true` when `verify` starts with the required scope block.
- `evidence_present`: `true` when the output cites source, test, runtime, data, environment, UAT, or git-boundary evidence appropriate to the prompt.
- `forbidden_behavior_detected`: `true` when the output violates fixture forbidden behavior or skill safety rules.
- `verdict`: `pass`, `partial`, `fail`, or `blocked`.
- `patch_proposal_generated`: `true` when the run suggests a skill/doc/eval patch.
- `human_decision`: `none`, `accepted`, `rejected`, `needs-info`, or `defer`. `quarantined` is a `learning_status`, not a human decision.
- `learning_status`: `observed`, `reproduced`, `quarantined`, `accepted`, `rejected`, or `promoted` for a Maintainer Lab proposal; omit for ordinary prompt rows.
- `promotion_target`: `none`, `scoped_issue`, `eval_regression`, `source_patch`, or `default_suite` for a Maintainer Lab proposal.
- `evidence_delta`: the new observation or changed hypothesis since the prior occurrence; `none` means the same remediation must not automatically repeat.

Normalize `blocked` as a stop state, not as evidence of success. A blocked row means the harness could not establish the requested behavior, even when the selected skill and prompt shape were otherwise correct.

## Routing Reliability Targeted Gate Metrics

Routing reliability metrics are targeted internal gate guardrails, not public SLA, customer SLA, or numeric first-slice SLO commitments.

Use these metrics only for `evals/prompts/routing-reliability.csv` and other rows that emit routing metadata. Legacy prompt suites may continue to use the skill-level fields above without producing `routing_summary`.

Per-row routing fields:

- `expected_route`: the single best first owning workflow, derived from `expected_best`.
- `actual_route`: the first route supported by authoritative skill-load evidence. Use `unknown` when the runtime does not expose that evidence. `response_shape_candidate` is a separate diagnostic and never substitutes for `actual_route`.
- `acceptable_routes`: safe alternatives separated by `|` in CSV and emitted as a list in JSON.
- `forbidden_routes`: routes that fail even if the output appears plausible.
- `route_boundary`: the boundary under test, such as `entry-contract`, `implement-vs-verify`, or `runtime-safety-gate-vs-skill-gate`.
- `routing_verdict`: whether route selection was best, acceptable, forbidden, missing, unexpected, pass, fail, or blocked according to runner classification.
- `host_preemption_verdict`: `pass`, `fail`, `blocked`, or `not_applicable`.
- `output_contract_verdict`: `pass`, `fail`, `blocked`, or `not_applicable`.
- `evidence_verdict`: `pass`, `fail`, `blocked`, or `not_applicable` in runner output, with legacy reports allowed to use `present`, `missing`, or `explicitly_unavailable` when they are not routing rows.
- `behavior_verdict`: `pass`, `fail`, `blocked`, or `not_applicable`.
- `overall_verdict`: `pass`, `partial`, `fail`, `blocked`, or timeout-equivalent failure.
- `failure_type`: the classified reason, such as `route_evidence_missing`, `forbidden_route`, `invalid_host_preemption`, `output_contract_failure`, `evidence_failure`, `direct_fallback_ceremony`, or `premature_implementation`.
- `fix_locus`: likely owner layer, such as routing surface, runtime safety gate, skill output contract, evidence collection, requirement-state gate, or direct fallback boundary.
- `owner`: the team or maintainer responsible for the regression record.
- `action`: one of `fix_now`, `defer_with_reason`, `accept_as_expected`, or `needs_more_evidence`.
- `sample_backfill`: one of `add_row`, `update_row`, `covered_by_existing_row`, or `no_backfill_with_reason`.

Summary route-hit metrics in `routing_summary` include only rows with authoritative route evidence and eligible scoring. Output/behavior verdict counts remain independently useful when routing is blocked:

- `best_route_hit_at_1`: count and rate where `actual_route == expected_route`.
- `acceptable_route_coverage`: count and rate where `actual_route` is in `acceptable_routes`.
- `forbidden_route_hits`: count and rate where `actual_route` is forbidden or the failure type is forbidden-route.
- `invalid_host_preemption`: count and rate of strict host-preemption failures.
- `routing_outcomes`: counts for best, acceptable, forbidden, missing, unexpected, and related route outcomes.
- `route_boundaries`: per-boundary row/pass/fail/blocking counts.
- `per_route_counts`: expected and actual route distributions.
- `route_pair_confusion`: compact expected-to-actual route drift table.
- `verdict_dimension_counts`: counts for routing, host-preemption, output, evidence, behavior, and overall verdict dimensions.
- `failure_type_counts`: classified non-pass reasons.
- `unclassified_nonpass`: non-pass ids that lack `failure_type`.

Use these fields to keep regression handling concrete: every accepted routing failure should say who owns it, what action is taken, whether the row set needs backfill, and why.

Targeted gate interpretation:

- No forbidden route hit in targeted gate rows unless an explicit review waives it with owner and reason.
- No invalid host preemption in targeted safety rows.
- No unclassified route/execution failure in targeted gate rows.
- No accepted P1 routing regression without owner, action, and sample-backfill decision.
- Best-route Hit@1 is a trend signal. It must not hide forbidden route hits, invalid host preemption, unclassified failures, or legitimate acceptable-route behavior.
- Acceptable coverage is a review signal, not a reason to broaden acceptable routes until ownership becomes meaningless.

Regression records for accepted routing failures must include:

- prompt or row id;
- route boundary;
- observed actual route;
- expected best route;
- failure type;
- fix locus;
- owner;
- action: `fix_now`, `defer_with_reason`, `accept_as_expected`, or `needs_more_evidence`;
- sample-backfill decision: `add_row`, `update_row`, `covered_by_existing_row`, or `no_backfill_with_reason`;
- verification evidence after fix or deferral.

## v0.4.2 Schema-backed Score Fields

Schema-backed scores are optional per-case score artifacts for trace-ready eval work. They document score shape and adapter vocabulary; they do not replace legacy `results.jsonl`, `summary.json`, or `routing_summary` outputs.

Schema files:

- `schemas/groundwork-common.schema.json`
- `schemas/groundwork-verify.schema.json`
- `schemas/groundwork-review.schema.json`
- `schemas/groundwork-routing.schema.json`
- `schemas/groundwork-closeout.schema.json`
- `schemas/groundwork-eval-score.schema.json`

Per-case score wrapper fields:

- `metadata`
- `case_id`
- `suite`
- `score_subject`
- `expected_skill`
- `triggered_skill`
- `expected_execution_primitive`
- `selected_execution_primitive`
- `output_contract_verdict`
- `evidence_verdict`
- `behavior_verdict`
- `routing_verdict`
- `host_preemption_verdict`
- `overall_verdict`
- `failure_type`
- `fix_locus`
- `checker_results`
- `notes`

`score_subject` classifies the score lens as `verify`, `review`, `routing`, `closeout`, or `generic`. It is not a skill route. `review` is a schema/lens vocabulary value only and must not be advertised as a public Groundwork skill.

`evals/scoring.py` provides a pure adapter from current runner result dictionaries to this score wrapper. It does not change `evals/run_runtime.py` default output, write score artifacts by default, introduce runtime eval, or require new dependencies.

## Trace-ready Rows and Routing Compatibility

- `trace_ready_rows` is the preferred count for rows using the routing/trace-ready verdict model.
- `routing_rows` remains a legacy-compatible alias for existing consumers.
- `routing_summary` remains the run-level summary for trace-ready route/verdict rows.
- Legacy prompt suites may continue to omit trace-ready routing fields and may continue using the skill-level metrics above.
- The score adapter uses `expected_skill` and `triggered_skill` as score wrapper field names, while runner route fields remain `expected_route` and `actual_route`.

## Schema Score Evidence Boundary

Schema validation proves only that a score artifact follows the expected shape. It is source/schema validation evidence, not runtime, cache-refresh, release, UAT, or customer-readiness evidence.

Runtime or release evidence must name the installed plugin root, source root, refresh or source/cache equivalence method, run scope, commands or trials, limitations, and missing evidence. Score schemas, score fixtures, adapter tests, and local CSV/schema checks must not be used alone to claim runtime behavior, release readiness, UAT readiness, customer readiness, plugin-cache freshness, or marketplace equivalence.

## Measurement Token Rules

Routing rows use finite measurement tokens for `output_contract` and `evidence_required`. They are not arbitrary prose and must not silently pass through fuzzy text judgment.

Current implemented `output_contract` tokens:

- `none`
- `verify_scope`
- `gate_fields`
- `prototype_contract_boundary`
- `implementation_result`
- `implementation_conformance`
- `entry_decision`
- `trajectory_signal`
- `qa_fix_qa`
- `qa_gap_closure_gate`
- `contract_lineage`
- `annotation_presentation_decision`
- `annotation_handoff_reference`
- `annotation_carrythrough_verification`
- `release_evidence_claim`
- `uat_evidence_window`
- `uat_evidence_window_forbidden`
- `uat_handoff_reference`
- `prototype_iteration_checkpoint`
- `prototype_no_delta_stop`
- `prototype_one_shot`
- `spec_single_question`
- `spec_writeback`
- `spec_no_delta_stop`
- `spec_clear_fast_path`
- `spec_gap_list`
- `checkpoint_before_risky_action`
- `artifact_header`
- `dispatch_compact_default`
- `dispatch_complete_or_split`

`spec_single_question` mechanically checks exactly one question plus a non-empty `Impact / Next route` field. It does not infer semantic materiality from question keywords; the row's expected behavior and the shared question-quality gate retain that judgment.

`contract_lineage` mechanically checks one optional cross-boundary lineage block, its canonical owner, strict ordered/branched hop graph and evidence-state markers, first confirmed divergence, fix owner, unresolved branches, and route-owned diagnosis/verification/plan companion. Canonical source files reject non-empty or malformed comments, ordinary fences, and indented hidden payloads. Every clause of each structured route-companion field is polarity-checked, so an independent hedge or confusable negation cannot be separated from a later token-bearing positive clause. Empty branches, split tokens, duplicate hop IDs, hidden fields or hidden extra output, competing causes, simultaneous alignment claims, reverse/fallback actions, cross-script or explicit negation, modal/adjectival/adverbial hedges applied to a "confirmed" divergence/cause/evidence/action, owner drift, and contradictory extra sections fail closed. Explicit `unverified`, `pending`, `blocked`, or `unresolved` dependency/gate states remain valid. It does not make the lineage runtime, UAT, release, or customer evidence.

`evals/prompts/contract-lineage.csv` is the trace-ready targeted-only gate for the `implement`, `verify`, and `write-plan` lineage companions. It includes an uncoached verify row whose user prompt does not disclose the structured section names, field names, fixture tokens, or scope oracle, so passing that row depends on the normal conditional `verify` load path rather than prompt-provided answer formatting. Its rows do not belong to the default `trace-first-verify-review.csv` suite and `contract-lineage.csv` must remain outside `DEFAULT_SUITES` until a separate default-suite promotion decision is evidence-backed.

`annotation_presentation_decision` checks the complete stable ID set plus exact per-ID purpose, disposition, audience-facing source, or companion reference. The ID/purpose root map is parsed only from renderable elements inside canonical `index.html` body content and must align with every annotation row and downstream decision target; `head`, metadata, hidden, and non-presentational ancestry such as `defs`, `symbol`, or `datalist` cannot provide a valid annotation. It rejects comments/fences/indented shadow facts in canonical sources; hidden or non-rendered HTML in contract output; empty-but-present conditional fields; purpose/disposition drift; prohibited internal-aid retention; competing, double-negated, or visually mixed Latin/Cyrillic/Greek assertions; actualized target/production UI claims based only on source decisions; and implementation/browser/runtime/UAT/release/customer-readiness promotion. An explicitly authorized retained audience-content candidate remains legal when it stays candidate-scoped. The token measures an explicitly requested targeted contract-only fragment consisting of the decision blocks and `Prototype Evidence Boundary`; that fragment is not a complete ordinary `prototype` or `handoff` output and does not waive either route's canonical required fields.

`annotation_handoff_reference` checks an explicitly requested targeted contract-only reference fragment against one resolvable canonical decision-source section, the exact complete stable ID set, and a `source_reference_only` boundary. Inline contract-only handoff is measured with `annotation_presentation_decision`. Ordinary handoffs still follow `skills/handoff/SKILL.md`; neither token represents a complete handoff package.

`annotation_carrythrough_verification` checks one source-backed verification block per annotation ID, including exact purpose, disposition, conditional field, row-declared observed target/reference, and row-declared `covered | gap | unverified` verdict. Its `Verification Scope` must match the per-ID aggregate exactly: all covered is `pass`; any gap is `fail`; no gap with at least one unverified item is `partial`; `Covered` lists only covered IDs and `Missing` lists gap/unverified IDs. The targeted annotation suite exercises prototype output, inline and reference handoff preservation, and per-ID verify carry-through without treating source inspection as browser/runtime/UAT/release evidence.

`release_evidence_claim` mechanically checks the exact shared evidence object, row-specific claim/status/root/refresh/run-scope tokens, named commands or trials, and limitations. A verified Groundwork plugin-bound claim needs adjacent terminal-success activities: supported `codex plugin list/show` inventory or `codex plugin add` refresh under the `CODEX_HOME` derived from an exact `.../plugins/cache/groundwork/groundwork/<version>` root; positive output naming that root; and the immediately next completed activity performing a complete recursive comparison with an independent source root. Identical, either-direction ancestor/descendant, and existing realpath-alias roots fail closed, as do excludes, normalization, partial-file, dry-run, and no-op behavior. A verified runtime claim additionally needs the immediately next completed activity to invoke the repository's canonical `evals/run_runtime.py` under the same `CODEX_HOME`, without `--validate-schema`, matching every named typed trial and emitting a non-empty summary whose run scope, selectors, complete prompt-file sources, actual requested/executed case IDs, counts, types, and all-pass result agree exactly. Exact identities are `suite:<registered-suite.csv>`, `group:<exact-group>`, `case_id:<exact-id>`, and `prompt_file:<canonical-absolute-path>`; only globally unique registered-suite aliases remain compatible, and per-case result paths use reversible ID encoding with collision checks. Rerun-failure filenames do not become trial aliases. `GROUNDWORK_REPO`, if explicitly supplied by a proof command, must resolve to the current canonical repo; inherited execution-changing Groundwork, shell, loader, Git, Node/npm, Python/pytest, Cargo/Rust, Go, compiler, Java/Maven, and Gradle variables are removed from evaluator-owned child processes. `HOME` and XDG state are replaced by a neutral per-run proof home, and `CODEX_HOME` remains a separately resolved and digested control path. Retained router-control key names, a digest of their non-secret values, enforced-environment metadata, and proof-policy digests are recorded without secret values. Proof executables are discovered only from evaluator-controlled directories, then bound to launcher/resolved stat identity and SHA-256; Python aliases must also resolve to `sys.executable`. Ambient startup `PATH` entries, arbitrary same-named paths, same-path replacement, delegated package-manager test scripts, direct or module-form pytest hooks, and non-canonical runtime scripts fail closed. `git_status` is bound to the canonical case workspace, and test evidence is limited to runner-native invocations and summaries. This is launch-trust binding and tamper detection, not binary-signature or supply-chain attestation. Empty selections and zero-row summaries fail closed. Generic release and UAT claims cannot self-verify without their separate maintainer/canonical evidence adapters.

The proof-environment sub-boundary also rejects inherited keys that are not ordinary identifiers, exported Bash-function entries such as `BASH_FUNC_node%%`, and function-shaped values. Codex tool subprocesses use `shell_environment_policy.inherit="none"` with only evaluator-owned proof values and declared router controls; runtime selectors cannot override that policy. The proof context records the tool-shell inherit mode, exact key set, and non-secret value digest.

`uat_evidence_window` mechanically checks the conditional UAT binding block and exact scope oracle for declared delivery scope, relevant SUT fingerprint, finite precondition/stability grammar, result/missing boundary, coverage basis, and rerun/supersedes link. Stability accepts exactly `stable`, `changed|restart_required`, `unverified`, or one `observed_at:<id>|stability_unverified` production; mixed or repeated productions fail closed, and verified UAT requires `stable`, an attributed non-placeholder fingerprint, concrete claim/covered/coverage values, `source_or_unverified`, and a direct canonical-record check. The canonical records file is checked as a whole: non-empty/malformed comments, ordinary fences, indented hidden payloads, and hidden/non-rendered HTML fail; each UAT section may contain only its single canonical `release_evidence_claim` YAML fence. Schema validation requires every UAT row oracle and release-claim field to match its canonical section, so reading one record cannot support a contradictory CSV/final claim. The suite remains targeted-only until the repository's separate default-suite promotion gate is satisfied. Its rows must inspect the matching canonical user-provided fixture record; same-basename files from other directories, output-generating read scripts, and hidden extra output do not qualify. No hidden evaluator oracle is appended to the prompt. The check does not prove that the current run performed deployment, browser work, runtime observation, UAT, artifact writeback, or release action.

`uat_evidence_window_forbidden` requires `verify_scope` plus `release_evidence_claim`, conflicts with `uat_evidence_window`, and mechanically rejects exact, annotated, separator-variant, or cross-script-confusable window headings, orphan window fields in bullets/tables/definition lists/bold or plain visible forms, and mutually exclusive strict sections in both output and canonical source for a bounded immutable/current-behavior observation. This prevents partial or malformed blocks from bypassing conditionality through a missing field marker.

`uat_handoff_reference` mechanically checks the compact canonical reference, scope, fingerprint, stability, closeout gap, rerun/supersedes link, next owner action, and non-executor boundary. It does not perform or prove deployment, rerun, browser/DB work, canonical writeback, or closeout.

Current allowed future `output_contract` tokens:

- `handoff_compact_reference`
- `route_failure_feedback`

Current implemented `evidence_required` tokens:

- `none`
- `no_file_changes`
- `gate_observed`
- `git_status`
- `raw_intent_no_implementation`
- `direct_fallback_no_artifact`
- `source_or_unverified`
- `tests_or_unverified`
- `runtime_or_unverified`
- `browser_or_unverified`

`no_file_changes` means no production/source changes for rows that require no artifact evidence. It may ignore narrowly recognized throwaway prototype artifacts when `artifact_allowed=true` and the actual route is `prototype`, such as `prototype.html`, root `index.html`, or `artifacts/*prototype*/index.html`. This is not a general source-change waiver.

`raw_intent_no_implementation` forbids raw or draft requirement rows from entering implementation-ready routes or writing code implementation artifacts. It may allow `to-prd` requirement-shaping Markdown artifacts, such as `README.md`, `docs/*.md`, or `artifacts/*/prd.md`, when the response clearly frames the output as draft PRD/spec/acceptance shaping rather than implementation.

Observed evidence tokens require attributable terminal-success activity, not command/tool names alone. Structured activities accept only `completed|ok|success|succeeded`; commands also require an integer, non-boolean zero exit code and a trusted baseline/live-resolved executable. The only failed-command exception is the QA adapter's exact scenario/final `Reproduction` command under its two named QA route boundaries; it must be one test invocation with terminal `failed`, nonzero integer exit, and expected-vs-actual or standard assertion/TAP failure output. Collection/import/setup/teardown/zero-test failures do not qualify, while an asserted expected/actual `TypeError` or `ReferenceError` remains valid test evidence. Output-dependent source/browser evidence requires one invocation, so `&&` siblings cannot lend aggregate output. Fixture-bound source accepts only passive canonical-path reads or trusted server/tool results whose extracted content equals the canonical source exactly; standard MCP resources require one request-URI-matched text item, while arbitrary providers, multiple resources, blobs, URI drift, and prefix/suffix wrappers fail. Browser commands must produce a substantive observation, bind URLs, paths, and opaque target IDs by exact string identity after option-arity parsing, and reject arbitrary same-named paths or package replacement; `playwright open`, help/version, listing/discovery/no-test modes, all-skipped/zero-execution results, empty output, acknowledgements, and errors do not qualify, while a mixed run with at least one executed pass may qualify. Structured browser evidence uses an exact trusted server/tool allowlist; console/network empty collections and scalar evaluate values remain valid observations, while lifecycle/control calls do not.

Prompt CSV headers are validated before rows are read: headers and row IDs must use canonical ASCII identifiers without NFKC/default-ignorable drift; Unicode lookalikes, invisible/control characters, duplicate normalized names or IDs, and non-canonical reserved-field spellings fail closed. Trace-ready rows require every `ROUTING_SCHEMA_FIELDS` header exactly once, while declared ASCII legacy extras remain allowed. Header-only/zero-row prompt suites fail closed. `--validate-schema --all-prompts` validates targeted-only and fixture-only rows before the runtime execution filter. The sole legacy internal-route exception is the registered, non-symlink canonical repository `evals/prompts/goal-contract.csv + goal-contract` fixture combination; external same-basename files, external symlinks, and a symlinked canonical suite do not inherit it, and the exception does not bypass ordinary `blocked`, overlap, host-preemption, token, or contract invariants. Pipe-token fields reject duplicates, and `none` is an exclusive empty-semantic token. These checks prevent schema-bearing columns, identities, or contracts from being silently shadowed.

Current allowed future `evidence_required` tokens:

- `cache_equivalence`

Unknown measurement tokens block the row. Allowed future tokens are schema-valid but return `blocked` until a deterministic checker exists.

`blocked` is a verdict, stop condition, or normalization outcome. It is not a route-list token and must not appear in `expected_best`, `acceptable_routes`, or `forbidden_routes`.

`runtime-safety-gate` is an eval-only actual-route classification for strict host/runtime preemption. It is never `expected_best` and is not a public skill route. Direct fallback remains the default no-skill route when strict host-preemption conditions are not met.

Deferred pilot boundaries remain deferred until a targeted gate proves otherwise. Do not use these metrics to imply learned routing, retrieval/rerank pilots, MCP/A2A pilots, public SLA commitments, or a broader runtime-visible surface.

## Deferred Boundaries

The targeted gate does not approve broad runtime or public surface changes by itself.

Deferred unless later targeted evidence proves the need:

- runtime-visible surface adjustment;
- docs or shared-rule changes outside the scoped fix locus;
- learned routing;
- retrieval or rerank pilots;
- MCP/A2A or protocol pilots;
- observability dashboards and error-budget programs;
- default-suite promotion.

## Verdict Definitions

- `pass`: expected behavior is present, forbidden behavior is absent, and required evidence is adequate.
- `partial`: core direction is right, but a nonblocking required field, evidence type, or boundary statement is missing.
- `fail`: expected behavior is absent, wrong skill selected, forbidden behavior appears, or a required gate is bypassed.
- `blocked`: the check cannot finish because required runtime, source evidence, approval, or user decision is missing.

## Minimum Report Row

```text
| ID | Expected Skill | Triggered Skill | Verdict | Evidence Present | Forbidden Behavior | Notes |
| --- | --- | --- | --- | --- | --- | --- |
```

## Observed Suggestion And Patch Proposal Rule

A classified non-pass may generate an advisory `observed` suggestion before reproduction. That generated record must remain `learning_status=observed`, `promotion_target=none`, `human_decision=none`, and `auto_apply=false`; it is a signal to investigate, not a patch proposal ready for acceptance.

An observed suggestion may advance to a reproducible patch proposal only when:

- the observed failure is reproducible from a fixture or baseline
- the affected skill or doc is named
- the proposed patch is scoped
- rollback is clear
- human review can accept or reject it

Reproduction, quarantine, acceptance, implementation, clean review, validation, and promotion follow `docs/quarantined-learnings.md`; metrics, report rendering, occurrence counts, or artifact promotion never advance those states automatically.

Patch proposals remain proposals. They do not mutate `main`, push, open PRs, write trackers, edit runtime directories, accept themselves, or promote themselves automatically.
