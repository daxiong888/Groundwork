Target Reader: Groundwork maintainers, clean reviewers, verifiers, and any future HITL publicization decision owners.
Reader Action Needed: Use this issue map as the canonical source-state and conditional-gate index. All default slices are source-implemented, the feature-branch Git boundary is committed, and clean-checkout source/package validation has passed; post-integration fresh read-only review and PR/CI evidence remain open alongside the optional publicization decisions. Do not treat this file as runtime, release, UAT, marketplace, or installed-plugin evidence.
Decision Supported: Which default slices have completed source implementation and clean-checkout validation, which post-integration Git-delivery evidence remains open, which optional publicization gates remain blocked, and what evidence is still required before any stronger readiness or public-surface claim.
Artifact Type: issue map.
Source of Truth: `docs/prd-v0.5-prototype-first-skill-expansion.md` plus maintainer-supplied recommended implementation order captured in the review conversation on 2026-06-24 and maintainer directive GW-PROT-ANNOT-001 supplied on 2026-07-16.
Scope: Issue decomposition for Groundwork v0.5 public skill expansion policy, skill-quality gate, role separation, lazy runtime capability boundary, setup/capability seed guidance, Prototype Lab references, annotation presentation carry-through, visual handoff packet, shared skill-audit, shared grilling, shared decision mapping, and v0.5 regression coverage.
Out of Scope: Treating this issue map itself as implementation evidence, reopening completed default slices without new source evidence, creating remote tracker issues, creating branches, committing, pushing, opening PRs, mutating plugin metadata, refreshing installed plugin cache, claiming runtime execution, claiming selector enforcement, claiming UAT/release/customer readiness, or creating public `grill`, `decision-map`, or `skill-audit` skills by default.
Evidence Level: Planning and source-validation issue map derived from local PRD/source inspection and the supplied recommended order. This file is not runtime evidence and does not prove installed plugin, marketplace, browser, worktree, subagent, selector, UAT, release, or customer readiness.
Safe to Share / Redaction Notes: Safe to share as a public planning artifact. It contains no secrets, credentials, private URLs, cookies, PII, production data, raw traces, or sensitive logs.
Last Updated: 2026-07-17.

# v0.5 Prototype-first Skill Expansion Issue Map

## Issue 集合摘要

本 issue map 记录 `docs/prd-v0.5-prototype-first-skill-expansion.md` 各垂直 slice 的当前 canonical 状态。默认实施 slice 已全部达到 `implemented_source_validated`；九个此前未跟踪的必需源码文件已纳入 feature-branch Git boundary，committed implementation snapshot 的 clean-checkout source/package validation 已通过；由于当前快照又融合了已合并的 dispatch 测试简化并删除了评审发现的死代码，旧 clean-review 结论已被取代，仍需 fresh read-only source review 与 PR/CI 证据；只有 V050-003B、V050-004B、V050-006B 保持 HITL-gated `missing_fields`。

历史默认实施顺序（当前均已完成 source implementation / local source validation）：

1. V050-001: Public Skill Expansion Policy and Skill-quality Gate
2. V050-001A: Role Separation Hard Gate
3. V050-001B: Lazy Runtime Capability and Selector Boundary
4. V050-002: Setup Guidance and Capability Seed Handling
5. V050-005A: Prototype Decision Capture and Contract Boundary
6. V050-005C: Visual Handoff Packet and Verify Lens
7. GW-PROT-ANNOT-001: Annotation Presentation Decision Carry-through
8. V050-005B: UI Variants and Logic Lab
9. V050-006A: Shared Skill-audit Workflow / Reference
10. V050-003A: Shared Grilling Loop and Route Negatives
11. V050-004A: Shared Decision Mapping Reference
12. V050-007: v0.5 Regression Suite

`V050-003B`、`V050-004B`、`V050-006B` 是条件 publicization slices，不是默认必做项。其 shared-reference 前置 slice 已 source-implemented；它们仍须获得明确 maintainer public exposure acceptance 和独立 skill-quality review，才能进入实现。

## 来源

- Canonical PRD: `docs/prd-v0.5-prototype-first-skill-expansion.md`
- PRD status: accepted canonical v0.5.x baseline; all default slices are implemented and locally source-validated. The feature-branch Git boundary is committed and clean-checkout source/package validation passed; post-integration fresh read-only review plus PR/CI evidence remain open, and the three optional publicization slices remain HITL-gated.
- AC source: PRD section `14. Acceptance Criteria`, AC-A through AC-D.
- Recommended order source: maintainer-supplied pasted text file, read on 2026-06-24.
- Annotation follow-up source: PRD requirement FR-533 and section `GW-PROT-ANNOT-001`, accepted by maintainer directive on 2026-07-16.
- Artifact promotion: satisfied; this issue map is the canonical source-state and future conditional-gate index.

## Field Semantics

- `Scope`: the bounded behavior/documentation/eval surface for the slice.
- `Primary files`: files expected to be owned by the slice. Implementers must inspect current files before editing.
- `Explicit non-goals`: work that must not be bundled into the slice.
- `Hard-negative evals`: dangerous overclaims or routing failures the slice must cover or preserve.
- `Checks`: fastest relevant local checks expected for closeout. Runtime/cache claims require separate installed-plugin evidence and are not implied.
- `Verification Evidence Needed`: retained acceptance-evidence contract. For completed slices, actual unresolved items are listed only under `Goal Contract Missing Fields`, `Runtime Missing Fields`, `Ready-for-Agent Missing Fields`, `Git Delivery Missing Fields`, or an explicit clean-review status.
- `Role separation / evidence boundary`: how self-check, clean review, independent verification, runtime evidence, and readiness claims must be separated.
- `Goal Mode independence`: historical decomposition rationale for completed slices, or the remaining bounded gate for conditional slices.
- `Implementation Runtime Candidate`: used only by unresolved conditional slices; completed slices instead record source implementation history without inferring runtime evidence.
- `Product Runtime Policy Surface`: product runtime policy or routing surfaces touched by the slice.
- `Product Runtime Execution Covered`: concrete product/runtime execution evidence covered by the slice. For this issue map, this is normally `none`.
- `Goal Contract Status`: `source_implementation_complete` for completed default slices and `missing_fields` for HITL-gated conditional publicization slices.

## Issue 草案

### V050-001: Public Skill Expansion Policy and Skill-quality Gate

Goal: Replace fixed public-skill-count thinking with a quality-gated public skill expansion policy and a shared skill-quality checklist before any new public skill is added.

Current State: `implemented_source_validated`.

Execution: Source implementation and deterministic local validation are complete.

Source Implementation History: commit `2549e08` (`docs(v050): 增加公共技能质量门禁`).

Contract Impact: docs / shared guardrail / verification contract.

Dependencies:
- Satisfied: accepted PRD source.

Scope:
- Update repo guidance so public skill expansion is allowed only under accepted scope, quality gates, routing gates, and eval gates.
- Define the difference between public skill, shared reference, branch/workflow lens, router behavior, and one-off guide.
- Add the first shared `SKILL-QUALITY.md` checklist and minimum eval bar.

Primary files:
- `AGENTS.md`
- `README.md`
- `docs/maintainer-workflows.md`
- `skills/_shared/SKILL-QUALITY.md`

Explicit non-goals:
- Do not create any new public skill.
- Do not implement `grill`, `decision-map`, `skill-audit`, `setup-groundwork`, or `visual-handoff`.
- Do not bump plugin metadata or release/package state.
- Do not claim installed-plugin runtime, marketplace, UAT, release, or customer readiness.

Acceptance Criteria:
- PRD FR-501, FR-502, FR-503, FR-504 are reflected in source guidance or shared policy.
- PRD AC-A1, AC-A2, AC-A3 are preserved in repo-facing guidance.
- PRD AC-B1 is satisfied by a shared skill-quality reference.
- Public-surface language changes from absolute prohibition to quality-gated expansion.
- Minimum eval bar includes positive, negative, and hard-negative expectations before public skill merge.

Hard-negative evals:
- A candidate public skill without distinct invocation moment is approved.
- A shared-reference candidate is incorrectly promoted to `skills/<name>/SKILL.md`.
- A skill-quality change is approved without routing and hard-negative eval expectations.

Checks:
- `git diff --check`
- `python3 -m json.tool .codex-plugin/plugin.json >/dev/null`
- `python3 -c "import csv, pathlib; [list(csv.DictReader(open(p, newline=''))) for p in pathlib.Path('evals/prompts').glob('*.csv')]; print('csv ok')"`
- Focused `rg` check for stale absolute "do not add public skills" wording that contradicts gated expansion.

Verification Evidence Needed:
- Command output for the checks above.
- Source diff showing gated expansion language and `SKILL-QUALITY.md` minimum eval bar.
- Focused search evidence that no new public skill directory was created by this slice.

Role separation / evidence boundary:
- Implementer may self-check wording and run local checks.
- Clean review must be separate before treating the public-skill policy as accepted implementation evidence.
- Runtime / Plugin Evidence should be reported as `Not claimed. Source-validation only.` unless cache/source equivalence is separately refreshed and named.

Goal Mode independence:
- This foundation slice had no implementation dependency beyond PRD acceptance and this issue map.
- Its source implementation is complete without creating a public skill or claiming runtime execution.

Implementation Task Type: `completed_source_implementation`
Implementation Runtime Evidence: `not_claimed`; commit/source history is not runtime evidence.
Product Runtime Covered: `none`
Isolation Record: Historical implementation topology is not used as current evidence.
Parallelization Status:
- eligible: not applicable; source implementation is complete.
- conflict group: `v050-foundation-policy`
- dependency group: none
- merge order status: satisfied before dependent slices.
Goal Contract Status: `source_implementation_complete`
Goal Contract Missing Fields:
- None for source closeout.
Runtime Missing Fields:
- Installed plugin cache/source refresh is not required for source-validation closeout; required only if runtime claims are made.
Ready-for-Agent Missing Fields:
- None for source closeout; a stable remote issue ID remains optional.
Triage Recommendation Candidate: `source-closeout complete`

Next action:
- Preserve the public-surface gate and its regression coverage; collect separate qualifying evidence only for stronger runtime or release claims.

### V050-001A: Role Separation Hard Gate

Goal: Define material role separation so self-check, clean review, independent verification, and closeout authority cannot be collapsed into one role/session for material changes.

Current State: `implemented_source_validated`.

Execution: Source implementation and deterministic local validation are complete.

Source Implementation History: commit `980ed2c` (`docs(v050): 增加角色分离硬门禁`).

Contract Impact: shared guardrail / skill closeout contract / eval contract.

Dependencies:
- Satisfied: V050-001 source implementation.

Scope:
- Add role identity and authority for designer/planner, implementer, clean reviewer, verifier, and coordinator.
- Define materiality threshold and evidence taxonomy.
- Update affected skills so final reports distinguish self-check, clean review, independent verification, runtime evidence, browser evidence, UAT evidence, and release evidence.
- Add role-separation hard-negative eval coverage.

Primary files:
- `skills/_shared/ROLE-SEPARATION.md`
- `skills/implement/SKILL.md`
- `skills/verify/SKILL.md`
- `skills/dispatch/SKILL.md`
- `skills/handoff/SKILL.md`
- `skills/prototype/SKILL.md`
- `evals/prompts/v0.5-role-separation.csv`

Explicit non-goals:
- Do not implement real subagent/runtime reviewer execution.
- Do not let the same session become clean reviewer or final verifier for its own material change.
- Do not create public skills.
- Do not broaden dispatch into an executor.

Acceptance Criteria:
- PRD FR-510 through FR-514 are reflected in shared guardrail and affected skill closeout fields.
- PRD AC-C1 and AC-C2 have focused hard-negative fixtures.
- PRD AC-D1 is represented in final report fields.
- Required output fields include `Role`, `Design Source`, `Self-check Evidence`, `Clean Review Evidence`, `Independent Verification Evidence`, `Readiness Boundary`, and `Required Next Independent Role`.

Hard-negative evals:
- Same-session self-check is treated as independent readiness.
- Reviewer fixes its own finding and declares clean review passed.
- Same-session designer implements and verifies its own material design.
- Skill author approves its own skill-quality change.

Checks:
- `git diff --check`
- CSV parse smoke for all `evals/prompts/*.csv`
- Targeted inspection of `evals/prompts/v0.5-role-separation.csv`
- Focused `rg` checks for final-report fields in touched skill files.

Verification Evidence Needed:
- Command output for the checks above.
- Source diff showing shared role separation guardrail and affected skill closeout fields.
- Targeted fixture evidence for same-session self-check, reviewer self-fix, designer self-verify, and author self-approval hard negatives.

Role separation / evidence boundary:
- Implementation self-check can prove local consistency only.
- Clean review must be read-only or, if reassigned to fix, followed by a new clean reviewer.
- `verify` must block or mark unverified when material readiness depends only on same-session evidence.

Goal Mode independence:
- Its V050-001 dependency is satisfied.
- Its completed source/eval verification did not require runtime adapter execution.

Implementation Task Type: `completed_source_implementation`
Implementation Runtime Evidence: `not_claimed`; commit/source history is not runtime evidence.
Product Runtime Covered: `none`
Isolation Record: Historical implementation topology is not used as current evidence.
Parallelization Status:
- eligible: not applicable; source implementation is complete.
- conflict group: `v050-role-separation`
- dependency group: `v050-foundation-policy`
- merge order status: satisfied after V050-001 and before dependent slices.
Goal Contract Status: `source_implementation_complete`
Goal Contract Missing Fields:
- None for source closeout.
Runtime Missing Fields:
- None for source-validation checks.
Ready-for-Agent Missing Fields:
- None for source closeout; a stable remote issue ID remains optional.
Triage Recommendation Candidate: `source-closeout complete`

Next action:
- Preserve role-separation regressions and require a fresh reviewer for future material clean-review claims.

### V050-001B: Lazy Runtime Capability and Selector Boundary

Goal: Define lazy runtime capability discovery, selector-enforcement evidence, model profiles, and runtime mismatch handling without assuming requested runtime/model support.

Current State: `implemented_source_validated`.

Execution: Source implementation and deterministic local validation are complete.

Source Implementation History: commit `fe588c6` (`docs(v050): 增加运行时能力边界`).

Contract Impact: runtime routing contract / shared guardrail / eval contract.

Dependencies:
- Satisfied: V050-001 and V050-001A source implementations.

Scope:
- Add `capability_status` and `selector_enforcement` statuses.
- Define model profile routing before concrete model mapping.
- Separate prompt preference, runtime/tool evidence, user-observed model menu seed, official docs, and community evidence.
- Prevent silent substitution between subagents and child-thread/worktree runtimes.

Primary files:
- `skills/_shared/RUNTIME-CAPABILITY.md`
- `skills/_shared/COGNITIVE-BUDGET.md`
- `skills/_shared/SUBAGENT-DELEGATION.md`
- `skills/dispatch/SKILL.md`
- `skills/implement/SKILL.md`
- `skills/verify/SKILL.md`
- `evals/prompts/v0.5-runtime-capability.csv`

Explicit non-goals:
- Do not maintain a permanent global model table as runtime truth.
- Do not claim selector enforcement from prompt text.
- Do not implement model/router automation beyond lazy capability boundary.
- Do not use Spark or any fast profile as final clean reviewer, final verifier, public skill approver, release/UAT authority, or customer authority.

Acceptance Criteria:
- PRD FR-520 through FR-524 are represented in shared references and affected skills.
- PRD AC-C5, AC-C6, and AC-C7 have hard-negative coverage.
- PRD AC-D2 is reflected in runtime/cache claim language.
- Capability seed facts are kept separate from runtime/tool enforcement evidence.

Hard-negative evals:
- Prompt says "use strongest model" and output claims `tool_enforced`.
- User asks for child thread and output silently routes to subagent.
- User asks for subagents and output silently routes to managed worktree.
- Model menu seed is treated as universal runtime truth.
- Spark is used as final verifier, final clean reviewer, public skill approver, or release/UAT authority.

Checks:
- `git diff --check`
- CSV parse smoke for all `evals/prompts/*.csv`
- Targeted inspection of `evals/prompts/v0.5-runtime-capability.csv`
- Focused `rg` checks for `capability_status`, `selector_enforcement`, `Runtime mismatch`, and `tool_enforced` language.

Verification Evidence Needed:
- Command output for the checks above.
- Source diff showing lazy capability statuses, selector-enforcement statuses, model profile boundary, and runtime mismatch fields.
- Targeted fixture evidence for prompt preference overclaim, subagent/child-thread substitution, model seed universalization, and Spark final-authority misuse.

Role separation / evidence boundary:
- Runtime preference and runtime execution evidence must be reported separately.
- Runtime/cache claims must name installed plugin root and cache/source refresh or equivalence evidence, or explicitly state not claimed.
- This slice may add routing recommendations, but not execution evidence.

Goal Mode independence:
- Its V050-001 and V050-001A dependencies are satisfied.
- Its source implementation and self-contained runtime-capability fixtures are complete without claiming a concrete runtime execution.

Implementation Task Type: `completed_source_implementation`
Implementation Runtime Evidence: `not_claimed`; commit/source history is not runtime evidence.
Product Runtime Covered: `none`
Product Runtime Policy Surface: `dispatch / implement / verify routing policy only`
Product Runtime Execution Covered: `none`
Isolation Record: Historical implementation topology is not used as current evidence.
Parallelization Status:
- eligible: not applicable; source implementation is complete.
- conflict group: `v050-runtime-capability`
- dependency group: `v050-foundation-policy`, `v050-role-separation`
- merge order status: satisfied before V050-002 and V050-004A.
Goal Contract Status: `source_implementation_complete`
Goal Contract Missing Fields:
- None for source closeout.
Runtime Missing Fields:
- Runtime selector availability remains intentionally unknown unless a separate qualifying runtime run inspects a concrete tool/runtime.
Ready-for-Agent Missing Fields:
- None for source closeout; a stable remote issue ID remains optional.
Triage Recommendation Candidate: `source-closeout complete`

Next action:
- Preserve selector-evidence and runtime-mismatch regressions; do not upgrade source validation into runtime enforcement evidence.

### V050-002: Setup Guidance and Capability Seed Handling

Goal: Add lightweight setup guidance and dated capability seed handling without creating public `setup-groundwork` skill surface.

Current State: `implemented_source_validated`.

Execution: Source implementation and deterministic local validation are complete.

Source Implementation History: commit `41c70fa` (`docs(v050): 增加能力种子处理指南`).

Contract Impact: docs / capability seed evidence boundary.

Dependencies:
- Satisfied: V050-001B source implementation.

Scope:
- Document how capability seeds are recorded as dated user-supplied observations.
- Add or update capability seed README guidance.
- Ensure model menu seed remains evidence input, not runtime/tool enforcement evidence.
- Keep setup guidance lightweight and non-mandatory.

Primary files:
- `docs/maintainer-workflows.md`
- `docs/capability-seeds/README.md`
- `docs/capability-seeds/codex-model-menu-2026-06-23.md`
- `skills/_shared/RUNTIME-CAPABILITY.md`

Explicit non-goals:
- Do not create `skills/setup-groundwork/SKILL.md`.
- Do not require every repo to run setup.
- Do not turn dated model menu seed into universal current runtime truth.
- Do not claim official current OpenAI/Codex behavior without current official-doc verification.

Acceptance Criteria:
- PRD FR-543 is represented as guide/reference first.
- The 2026-06-23 model menu seed is documented as `user_supplied` dated evidence.
- `selector_enforcement` remains `unknown` or `prompt_preference` unless tool/runtime evidence exists.
- No public setup skill is created.

Hard-negative evals:
- Dated model menu seed cited as universal availability.
- Setup guide required before ordinary Groundwork use.
- Prompt preference or setup note treated as selector enforcement evidence.

Checks:
- `git diff --check`
- `python3 -m json.tool .codex-plugin/plugin.json >/dev/null`
- CSV parse smoke if eval files are touched.
- Focused `rg` check confirming no `skills/setup-groundwork/SKILL.md`.

Verification Evidence Needed:
- Command output for the checks above.
- Source diff showing capability seed guidance as dated user-supplied evidence.
- Focused search evidence that no public `setup-groundwork` skill was created.

Role separation / evidence boundary:
- This is documentation/source-validation only.
- Current official-doc or runtime behavior is not claimed unless separately verified and cited.
- Runtime / Plugin Evidence should be `Not claimed. Source-validation only.` by default.

Goal Mode independence:
- Its V050-001B dependency is satisfied.
- Source validation remains limited to documentation consistency and absence of a public setup skill surface.

Implementation Task Type: `completed_source_implementation`
Implementation Runtime Evidence: `not_claimed`; commit/source history is not runtime evidence.
Product Runtime Covered: `none`
Isolation Record: Historical implementation topology is not used as current evidence.
Parallelization Status:
- eligible: not applicable; source implementation is complete.
- conflict group: `v050-capability-seeds`
- dependency group: `v050-runtime-capability`
- merge order status: satisfied after V050-001B.
Goal Contract Status: `source_implementation_complete`
Goal Contract Missing Fields:
- None for source closeout.
Runtime Missing Fields:
- Current official-doc verification remains required only for a future current-behavior claim.
Ready-for-Agent Missing Fields:
- None for source closeout; a stable remote issue ID remains optional.
Triage Recommendation Candidate: `source-closeout complete`

Next action:
- Preserve dated-source labeling and continue to treat capability seeds as inputs rather than current runtime truth.

### V050-005A: Prototype Decision Capture and Contract Boundary

Goal: Make `prototype` capture decisions and contract boundaries so prototype-only mock fields or client-derived logic are not promoted to backend/API truth.

Current State: `implemented_source_validated`.

Execution: Source implementation and deterministic local validation are complete. Any future runtime/browser/UAT/release claim requires a separate evidence run.

Source Implementation History: commit `f744259` (`docs(v050): 增加原型决策与合同边界`).

Contract Impact: prototype output contract / frontend-backend evidence boundary / eval contract.

Dependencies:
- The V050-001A role-separation contract is present in current source and remains the governing authority boundary.

Scope:
- Add focused prototype references for decision capture and contract-boundary handling.
- Update `prototype` skill to label confirmed decisions, rejected variants, unverified assumptions, mock fields, client-derived logic, contract impact, open questions, and next route.
- Add hard negatives for prototype mock promotion and client-derived logic overclaim.

Primary files:
- `skills/prototype/DECISION-CAPTURE.md`
- `skills/prototype/CONTRACT-BOUNDARY.md`
- `skills/prototype/SKILL.md`
- `evals/prompts/prototype.csv`

Explicit non-goals:
- Do not create public `visual-handoff` skill.
- Do not implement UI variant or logic lab references in this slice.
- Do not turn prototype artifacts into API/schema/source truth.
- Do not claim browser/runtime evidence without actual run and recorded evidence.

Acceptance Criteria:
- PRD FR-530 is represented in focused prototype references and `prototype/SKILL.md`.
- PRD AC-C3 has hard-negative coverage.
- Prototype output template includes confirmed decisions, rejected variants, unverified assumptions, mock/illustrative fields, client-derived logic, contract impact, open questions, and next route.

Hard-negative evals:
- Prototype mock field promoted to backend/API contract.
- Client-derived logic presented as server truth.
- Visual artifact used as runtime/browser evidence without a run.

Checks:
- `git diff --check`
- CSV parse smoke for all `evals/prompts/*.csv`
- Targeted inspection of `evals/prompts/prototype.csv`
- Focused `rg` checks for `Mock / Illustrative Fields`, `Client-derived Logic`, and `Contract Impact`.

Verification Evidence Needed:
- Command output for the checks above.
- Source diff showing decision-capture and contract-boundary references plus `prototype/SKILL.md` integration.
- Targeted fixture evidence that mock fields, client-derived logic, and unrun visual artifacts are not promoted to source/runtime truth.

Role separation / evidence boundary:
- Prototype author may record decisions and assumptions but cannot confirm API/backend truth without source evidence or user confirmation.
- `verify` or clean review must separately check any material contract impact.
- Browser/run/UAT/release claims remain out of scope.

Goal Mode independence:
- Its V050-001A dependency is satisfied.
- Its focused source and eval implementation is complete under `skills/prototype/`.

Implementation Task Type: `completed_source_implementation`
Implementation Runtime Evidence: `not_claimed`; commit/source history is not runtime evidence.
Product Runtime Covered: `none`
Isolation Record: Historical implementation topology is not used as current evidence.
Parallelization Status:
- eligible: not applicable; source implementation is complete.
- conflict group: `v050-prototype-boundary`
- dependency group: `v050-role-separation`
- merge order status: satisfied for V050-005B and V050-005C.
Goal Contract Status: `source_implementation_complete`
Goal Contract Missing Fields:
- None for the current source implementation.
Runtime Missing Fields:
- None for source-validation checks.
Ready-for-Agent Missing Fields:
- None for source closeout; a stable remote issue ID remains optional.
Triage Recommendation Candidate: `source-closeout complete`

Next action:
- Preserve focused regression coverage and collect separate qualifying evidence only when a stronger runtime/browser/UAT/release claim is requested.

### V050-005C: Visual Handoff Packet and Verify Lens

Goal: Add visual handoff packet rules and verification lens while preserving the boundary that visual packets are communication/review artifacts, not readiness evidence.

Current State: `implemented_source_validated`.

Execution: Shared packet, public-entry routing, handoff, and verify source contracts plus deterministic local coverage are complete. Browser/runtime evidence remains separate.

Source Implementation History: commit `39a7fd9` (`docs(v050): 增加视觉交接包边界`).

Contract Impact: visual handoff contract / verification evidence boundary.

Dependencies:
- V050-005A is present and locally source-validated, so visual handoff rules reuse its prototype contract-boundary terminology.

Scope:
- Add shared visual handoff packet guidance.
- Update `prototype`, `handoff`, and `verify` references so visual packets carry evidence boundaries.
- Require packet sections for state/flow, UI surface, API contract mapping, mock vs confirmed fields, open questions, and do-not-assume guidance.

Primary files:
- `skills/_shared/VISUAL-HANDOFF-PACKET.md`
- `skills/handoff/SKILL.md`
- `skills/verify/SKILL.md`
- `skills/prototype/SKILL.md`

Explicit non-goals:
- Do not create public `visual-handoff` skill.
- Do not treat HTML packet, screenshots, generated images, or prototype output as browser/runtime/UAT/release evidence.
- Do not implement browser automation or runtime proof in this slice.
- Do not add UI variants or logic lab references here unless strictly needed for cross-links.

Acceptance Criteria:
- PRD FR-532 and AC-B5 are represented in shared packet guidance.
- PRD AC-C4 has explicit hard-negative coverage or preserved route expectation.
- PRD AC-D1 separates visual packet evidence from browser/runtime/UAT/release evidence.

Hard-negative evals:
- Visual packet output treated as browser evidence without browser run.
- Visual packet treated as runtime, UAT, release, or customer readiness.
- Mock fields in visual packet treated as confirmed API/schema truth.

Checks:
- `git diff --check`
- CSV parse smoke if eval files are touched.
- Focused `rg` checks for `communication artifact`, `browser evidence`, `UAT`, `release`, `Mock vs Confirmed`, and `Do Not Implement / Do Not Assume`.

Verification Evidence Needed:
- Command output for the checks above.
- Source diff showing visual packet guidance and `prototype` / `handoff` / `verify` integration.
- Focused evidence that HTML packets, screenshots, and visual artifacts remain communication/review artifacts unless browser/runtime/source evidence is actually produced.

Role separation / evidence boundary:
- Visual handoff is a communication artifact.
- Browser evidence exists only when an actual browser run is performed and recorded.
- API/schema/source truth exists only when inspected and named.
- UAT/customer readiness is a separate verification claim.

Goal Mode independence:
- Its V050-005A dependency is satisfied.
- Its completed shared guidance and skill references did not require a public skill surface change.

Implementation Task Type: `completed_source_implementation`
Implementation Runtime Evidence: `not_claimed`; commit/source history is not runtime evidence.
Product Runtime Covered: `none`
Isolation Record: Historical implementation topology is not used as current evidence.
Parallelization Status:
- eligible: not applicable; source implementation is complete.
- conflict group: `v050-visual-handoff`
- dependency group: `v050-prototype-boundary`
- merge order status: satisfied after V050-005A.
Goal Contract Status: `source_implementation_complete`
Goal Contract Missing Fields:
- None for the current source implementation.
Runtime Missing Fields:
- Browser/runtime evidence is intentionally not produced by this source-validation slice.
Ready-for-Agent Missing Fields:
- None for source closeout; a stable remote issue ID remains optional.
Triage Recommendation Candidate: `source-closeout complete`

Next action:
- Preserve prototype/handoff/verify carry-through regressions and collect separate browser/runtime evidence only for a matching readiness claim.

### GW-PROT-ANNOT-001: Annotation Presentation Decision Carry-through

Goal: Close the prototype annotation contract gap by making presentation decisions conditional, repeatable, stable by ID, and traceable through visual packet, handoff, and UI verification.

Current State: `implemented_source_validated`.

Execution: Source implementation and deterministic local validation are complete for the current hardening worktree.

Source Implementation Baseline: commit `b6aef26` (`feat(prototype): 增加批注展示边界`); current canonical source includes the subsequent hardening and post-review integration changes in this feature-branch snapshot.

Clean Review Status: `superseded_by_post_review_integration`; the earlier reviewer result does not cover the current snapshot after integrating the already-merged dispatch-test simplification and removing review-identified dead helpers. A new fresh read-only source review is required.

Git Delivery Status: `committed_snapshot_clean_checkout_validated`; the nine previously untracked source files referenced by tracked tests, coverage, or CI are included in the feature-branch Git boundary, and the committed implementation snapshot passed clean-checkout source/package validation. Delivery closeout still requires fresh post-integration read-only review, PR publication, and CI evidence.

Evidence Boundary: Local source, schema, unit, coverage-manifest, CSV/JSON, whitespace, and runtime-package-boundary checks only. No installed-plugin, runtime execution, browser, UAT, marketplace, release, customer, selector-enforcement, or cache/source-refresh readiness is claimed.

Dependencies:
- V050-005A and V050-005C source contracts, both present and locally source-validated.

Scope:
- Add the conditional, repeatable `Annotation Presentation Decision` to the formal prototype output template and visual handoff required sections.
- Require one stable `Annotation ID`, `Annotation Purpose`, and `Presentation Disposition` per annotation item or homogeneous group.
- Require a same-block `Audience-facing Source` for `retain_as_audience_content_candidate` and a same-block `Companion Reference` for `separate_review_companion`.
- Require handoff to preserve every decision block inline or cite one resolvable canonical decision reference plus the complete ID set.
- Require UI verification to compare carry-through and conditional fields per ID.

Primary files:
- `skills/prototype/DECISION-CAPTURE.md`
- `skills/_shared/VISUAL-HANDOFF-PACKET.md`
- `skills/handoff/COMPLEX-HANDOFF-BRANCHES.md`
- `skills/verify/UI-READINESS-BRANCH.md`
- `evals/prompts/prototype-annotation.csv`
- `evals/fixtures/prototype-annotation/`
- `evals/test_prototype_annotation.py`
- the smallest shared evaluator/schema files required to wire the finite annotation contract

Explicit non-goals:
- Do not create a public `visual-handoff` or annotation skill.
- Do not treat prototype, packet, handoff, or source-validation output as browser/runtime/UAT/release evidence.
- Do not broaden unrelated prototype, routing, runtime, or release behavior.

Acceptance Criteria:
- The prototype `Output Template` and visual packet `Required Sections` expose the conditional, repeatable block.
- Every applicable block has a stable ID, purpose, and disposition, with the required same-block conditional field for retain or separate.
- Handoff preserves blocks inline or provides a resolvable canonical reference and complete ID set.
- Verify emits one carry-through check per source ID and identifies missing, renamed, duplicated, or mismatched fields.
- The trace-ready annotation suite rejects missing same-block authority, sibling-source promotion, purpose/disposition drift, invalid or empty conditional fields, incomplete ID sets, internal-aid retention, hidden structured content, and readiness overclaim across prototype, handoff, and per-ID verify carry-through rows.
- The PRD and this issue map contain an exact, searchable `GW-PROT-ANNOT-001` definition.

Checks:
- `git diff --check`
- Focused source-text check for the ID, three required fields, both disposition-specific fields, handoff inline/reference modes, and per-ID verification table.
- `python3 -B -m unittest evals.test_prototype_annotation`
- `python3 -B evals/run_runtime.py --validate-schema --suite prototype-annotation.csv`
- Existing focused documentation/unit tests that read the touched branch references; no runtime or installed-cache claim.

Role separation / evidence boundary:
- Implementer checks source consistency only.
- The earlier fresh read-only review is recorded as superseded because it predates the post-review integration changes; a new read-only reviewer must inspect the committed snapshot without becoming an implementer.
- A later verifier must not upgrade this source diff into browser/runtime/UAT/release or customer-readiness evidence.

Goal Mode independence:
- Its V050-005A and V050-005C dependencies are satisfied.
- The source implementation, Git boundary, and committed-snapshot clean-checkout source/package validation are complete; post-integration fresh review and PR/CI evidence remain separate and open.

Implementation Task Type: `completed_source_implementation`
Implementation Runtime Evidence: `not_claimed`; commit/source history is not runtime evidence.
Product Runtime Covered: `none`
Isolation Record: Historical implementation topology is not used as current evidence.
Parallelization Status:
- eligible: post-integration source review can run after the committed snapshot is available; source implementation itself is complete.
- conflict group: `gw-prototype-annotation`
- dependency group: `v050-prototype-boundary`, `v050-visual-handoff`
- merge order status: source implementation complete after V050-005A and V050-005C.
Goal Contract Status: `source_implementation_complete`
Goal Contract Missing Fields:
- None for source implementation.
Runtime Missing Fields:
- Installed-plugin, runtime, browser, UAT, marketplace, release, and cache/source equivalence evidence remain intentionally unclaimed.
Ready-for-Agent Missing Fields:
- None for source implementation; post-integration review is an evidence-closeout step, not an implementation-input gap.
Git Delivery Missing Fields:
- None for source-file inclusion; the four prototype-annotation fixtures, canonical UAT record, two prompt suites, and two test modules are in the intended feature-branch boundary.
- None for committed-snapshot clean-checkout source/package validation.
- Pending evidence: fresh post-integration read-only review, PR publication, and CI result.
Triage Recommendation Candidate: `source and clean-checkout validation complete; post-integration review and PR/CI evidence pending`

Next action:
- Obtain a fresh post-integration read-only review, publish the reviewable PR, and record its CI result without upgrading the evidence layer.

### V050-005B: UI Variants and Logic Lab

Goal: Add focused prototype references for UI variants and logic/state lab without turning exploratory prototype output into backend contract truth or runtime tooling.

Current State: `implemented_source_validated`.

Execution: Source implementation and deterministic local validation are complete.

Source Implementation History: commit `20479e1` (`docs(v050): 增加原型变体与逻辑实验`).

Contract Impact: prototype branch contract / exploratory artifact boundary.

Dependencies:
- Satisfied: the V050-005A prototype contract-boundary source is present and locally source-validated.

Historical File Conflict Check:
- Satisfied during implementation; no current prerequisite remains.

Scope:
- Define when UI variants are appropriate: material visual design uncertainty.
- Define when logic/state lab is appropriate: state machine, reducer, or business-rule uncertainty.
- Update `prototype` references so these modes remain bounded exploration tools.

Primary files:
- `skills/prototype/UI-VARIANTS.md`
- `skills/prototype/LOGIC-LAB.md`
- `skills/prototype/SKILL.md`

Explicit non-goals:
- Do not implement a prototype runner.
- Do not implement runtime tooling.
- Do not create backend/API contract truth from lab output.
- Do not create public `visual-handoff` skill.

Acceptance Criteria:
- PRD FR-531 is represented in focused prototype references.
- UI variants and logic/state lab have clear trigger boundaries and should-not-trigger cases.
- Existing V050-005A mock/contract boundary remains intact.

Hard-negative evals:
- UI variant output treated as final frontend implementation commitment.
- Logic/state lab output treated as server truth without source evidence.
- Lab artifact treated as runtime/browser/UAT evidence.

Checks:
- `git diff --check`
- CSV parse smoke if eval files are touched.
- Focused `rg` checks for `UI variants`, `Logic/state lab`, `Mock`, `Contract Impact`, and should-not-trigger language.

Verification Evidence Needed:
- Command output for the checks above.
- Source diff showing UI variant and logic/state lab trigger boundaries.
- Focused evidence that variant/lab output is not described as backend contract truth, runtime evidence, or final implementation commitment.

Role separation / evidence boundary:
- Prototype/lab output clarifies decisions; it does not verify source truth by itself.
- Material frontend/backend contract changes need independent source/API review.
- Runtime and browser readiness are not claimed.

Goal Mode independence:
- Its V050-005A dependency is satisfied.
- Its bounded source/eval implementation is complete without creating backend contract truth.

Implementation Task Type: `completed_source_implementation`
Implementation Runtime Evidence: `not_claimed`; commit/source history is not runtime evidence.
Product Runtime Covered: `none`
Isolation Record: Historical implementation topology is not used as current evidence.
Parallelization Status:
- eligible: not applicable; source implementation is complete.
- conflict group: `v050-prototype-lab`
- dependency group: `v050-prototype-boundary`
- merge order status: satisfied after V050-005A.
Goal Contract Status: `source_implementation_complete`
Goal Contract Missing Fields:
- None for source closeout.
Runtime Missing Fields:
- None for source-validation checks.
Ready-for-Agent Missing Fields:
- None for source closeout; a stable remote issue ID remains optional.
Triage Recommendation Candidate: `source-closeout complete`

Next action:
- Preserve the UI-variant and logic-lab boundaries and their hard-negative coverage.

### V050-006A: Shared Skill-audit Workflow / Reference

Goal: Add skill-audit as a required shared workflow/reference for public skill additions and material skill changes without creating a public `skill-audit` skill.

Current State: `implemented_source_validated`.

Execution: Source implementation and deterministic local validation are complete.

Source Implementation History: commit `9602611` (`docs(v050): 增加技能审计共享流程`).

Contract Impact: shared audit contract / skill-quality verification contract / eval contract.

Dependencies:
- Satisfied: V050-001 and V050-001A source implementations.

Scope:
- Extend skill-quality reference with audit workflow expectations.
- Add shared `SKILL-AUDIT.md` covering invocation class, trigger description, workflow, hierarchy, progressive disclosure, duplication, failure branches, evidence boundary, and eval coverage.
- Add skill-audit eval prompts or hard negatives that prove authors cannot approve their own material skill changes.

Primary files:
- `skills/_shared/SKILL-QUALITY.md`
- `skills/_shared/SKILL-AUDIT.md`
- `evals/prompts/v0.5-skill-audit.csv`

Explicit non-goals:
- Do not create `skills/skill-audit/SKILL.md`.
- Do not create public skill-audit templates under `skills/skill-audit/`.
- Do not let a skill author be final authority for its own material skill-quality change.

Acceptance Criteria:
- PRD FR-542 is satisfied as shared workflow/reference first.
- PRD AC-A3 classifies `skill-audit` as required workflow/reference before public candidate.
- Skill-quality checklist references the shared audit lens.
- Hard negatives cover self-approval and public surface promotion without gates.

Hard-negative evals:
- Skill author audits and approves its own public skill change.
- Shared audit reference is treated as public skill before maintainer acceptance.
- Public skill addition skips trigger, should-not-trigger, and hard-negative eval review.

Checks:
- `git diff --check`
- CSV parse smoke for all `evals/prompts/*.csv`
- Targeted inspection of `evals/prompts/v0.5-skill-audit.csv`
- Focused `rg` check confirming no `skills/skill-audit/SKILL.md`.

Verification Evidence Needed:
- Command output for the checks above.
- Source diff showing shared audit workflow/reference and skill-quality integration.
- Focused search evidence that no public `skill-audit` skill was created.
- Targeted fixture evidence that author self-approval and ungated public skill promotion are blocked.

Role separation / evidence boundary:
- Audit can be performed as clean review only by a separate role/session.
- Author self-audit is self-check evidence only.
- Public skill approval remains blocked without independent quality review and maintainer acceptance where required.

Goal Mode independence:
- Its V050-001 and V050-001A dependencies are satisfied.
- Its shared audit source and eval implementation is complete without creating a public `skill-audit` skill.

Implementation Task Type: `completed_source_implementation`
Implementation Runtime Evidence: `not_claimed`; commit/source history is not runtime evidence.
Product Runtime Covered: `none`
Isolation Record: Historical implementation topology is not used as current evidence.
Parallelization Status:
- eligible: not applicable; source implementation is complete.
- conflict group: `v050-skill-audit-shared`
- dependency group: `v050-foundation-policy`, `v050-role-separation`
- merge order status: satisfied before any optional publicization decision.
Goal Contract Status: `source_implementation_complete`
Goal Contract Missing Fields:
- None for source closeout.
Runtime Missing Fields:
- None for source-validation checks.
Ready-for-Agent Missing Fields:
- None for source closeout; a stable remote issue ID remains optional.
Triage Recommendation Candidate: `source-closeout complete`

Next action:
- Preserve the shared audit and self-approval hard negatives; optional public exposure remains a separate HITL decision.

### V050-003A: Shared Grilling Loop and Route Negatives

Goal: Add shared grilling behavior and route negatives without creating a public `grill` skill.

Current State: `implemented_source_validated`.

Execution: Source implementation and deterministic local validation are complete, including later feedback-loop hardening.

Source Implementation History: commits `be93506` (`docs(v050): 增加共享 grilling 边界`) and `e609100` (`feat(workflow): 增强证据循环与反馈闭环`).

Contract Impact: routing contract / shared workflow reference / eval contract.

Dependencies:
- Satisfied: V050-001 and V050-001A source implementations.
- Historical prototype-file overlap was resolved during implementation.

Scope:
- Define grilling as the route for material ambiguity where unknowns are not yet enumerable.
- Add one-question-at-a-time behavior and route boundaries against direct answer, `to-prd`, decision mapping, and prototype.
- Update `to-prd` and `prototype` references to use shared grilling behavior when appropriate.

Primary files:
- `skills/_shared/GRILLING.md`
- `skills/to-prd/SKILL.md`
- `skills/prototype/SKILL.md`
- `evals/prompts/v0.5-grill.csv`

Explicit non-goals:
- Do not create `skills/grill/SKILL.md`.
- Do not over-question tiny direct tasks.
- Do not route enumerable option comparison to grilling when decision mapping is the better lens.
- Do not use grilling as a bypass for accepted PRD/implementation work.

Acceptance Criteria:
- PRD FR-540 is represented as public candidate only after shared route negatives.
- PRD AC-A3 keeps `grill` as public candidate, not default public skill.
- `v0.5-grill.csv` covers explicit "grill me", raw ambiguous planning, tiny direct task negative, and repo-doc-answerable question behavior.

Hard-negative evals:
- "fix typo in README" triggers grilling instead of direct edit/answer.
- Question answerable from repo docs asks unnecessary user questions without inspection.
- "grill me" fails to trigger shared grilling behavior.
- `to-prd` carries all grilling without clear shared boundary.

Checks:
- `git diff --check`
- CSV parse smoke for all `evals/prompts/*.csv`
- Targeted inspection of `evals/prompts/v0.5-grill.csv`
- Focused `rg` check confirming no `skills/grill/SKILL.md`.

Verification Evidence Needed:
- Command output for the checks above.
- Source diff showing shared grilling reference and `to-prd` / `prototype` integration.
- Targeted fixture evidence for explicit "grill me", ambiguous planning, tiny direct task negative, and repo-doc-answerable question behavior.
- Focused search evidence that no public `grill` skill was created.

Role separation / evidence boundary:
- Grilling produces clarification, not acceptance or implementation evidence.
- It may prepare PRD/prototype/decision-map routes but cannot mark implementation readiness.
- Clean review is needed before public `grill` exposure is accepted later.

Goal Mode independence:
- Its V050-001 and V050-001A dependencies are satisfied.
- Its shared reference and route eval implementation is complete without creating a public `grill` skill.

Implementation Task Type: `completed_source_implementation`
Implementation Runtime Evidence: `not_claimed`; commit/source history is not runtime evidence.
Product Runtime Covered: `none`
Isolation Record: Historical implementation topology is not used as current evidence.
Parallelization Status:
- eligible: not applicable; source implementation is complete.
- conflict group: `v050-shared-grilling`
- dependency group: `v050-foundation-policy`, `v050-role-separation`
- merge order status: satisfied with prototype routing integration.
Goal Contract Status: `source_implementation_complete`
Goal Contract Missing Fields:
- None for source closeout.
Runtime Missing Fields:
- None for source-validation checks.
Ready-for-Agent Missing Fields:
- None for source closeout; a stable remote issue ID remains optional.
Triage Recommendation Candidate: `source-closeout complete`

Next action:
- Preserve shared grilling route negatives; public `grill` exposure remains a separate HITL decision.

### V050-004A: Shared Decision Mapping Reference

Goal: Add decision mapping as shared reference and route-conflict evals without creating a public `decision-map` skill.

Current State: `implemented_source_validated`.

Execution: Source implementation and deterministic local validation are complete.

Source Implementation History: commit `d822907` (`docs(v050): 增加共享决策映射边界`).

Contract Impact: routing contract / shared workflow reference / cognitive-budget guidance / eval contract.

Dependencies:
- Satisfied: V050-001B source implementation.
- Historical `COGNITIVE-BUDGET.md` ownership overlap was resolved during implementation.

Scope:
- Define decision mapping for enumerable options, tradeoffs, dependencies, and decision criteria.
- Preserve direct answer, `to-prd`, `write-plan`, and `dispatch` routes when they are more appropriate.
- Add or update cognitive-budget guidance where decision mapping affects model/profile recommendations.

Primary files:
- `skills/_shared/DECISION-MAPPING.md`
- `skills/_shared/COGNITIVE-BUDGET.md`
- `skills/to-prd/SKILL.md`
- `skills/write-plan/SKILL.md`
- `skills/dispatch/SKILL.md`
- `evals/prompts/v0.5-decision-map.csv`

Explicit non-goals:
- Do not create `skills/decision-map/SKILL.md`.
- Do not add a public `decision-map` template.
- Do not route bounded direct questions or accepted implementation plans into decision mapping.
- Do not let decision mapping replace dispatch for accepted ready runtime packages.

Acceptance Criteria:
- PRD FR-541 is represented as shared reference first.
- Route-conflict negatives distinguish direct answer, `to-prd`, `write-plan`, `dispatch`, and decision mapping.
- Decision mapping uses runtime capability language from V050-001B without claiming selector enforcement.

Hard-negative evals:
- Tiny direct question is routed into decision mapping.
- Accepted issue implementation plan is routed to decision mapping instead of `write-plan`.
- Accepted runtime package routing is routed to decision mapping instead of `dispatch`.
- Clear PRD-writing task is routed to decision mapping instead of `to-prd`.

Checks:
- `git diff --check`
- CSV parse smoke for all `evals/prompts/*.csv`
- Targeted inspection of `evals/prompts/v0.5-decision-map.csv`
- Focused `rg` check confirming no `skills/decision-map/SKILL.md`.

Verification Evidence Needed:
- Command output for the checks above.
- Source diff showing shared decision mapping reference and affected route integrations.
- Targeted fixture evidence for route conflicts against direct answer, `to-prd`, `write-plan`, and `dispatch`.
- Focused search evidence that no public `decision-map` skill was created.

Role separation / evidence boundary:
- Decision mapping supports choosing a path; it does not implement or verify the chosen path.
- Model/profile recommendations are prompt preferences unless tool/runtime evidence proves enforcement.
- Public decision-map exposure requires later independent route review.

Goal Mode independence:
- Its V050-001B dependency is satisfied.
- Its shared reference and route-conflict eval implementation is complete without creating a public `decision-map` skill.

Implementation Task Type: `completed_source_implementation`
Implementation Runtime Evidence: `not_claimed`; commit/source history is not runtime evidence.
Product Runtime Covered: `none`
Isolation Record: Historical implementation topology is not used as current evidence.
Parallelization Status:
- eligible: not applicable; source implementation is complete.
- conflict group: `v050-shared-decision-mapping`
- dependency group: `v050-runtime-capability`
- merge order status: satisfied before any optional public `decision-map` decision.
Goal Contract Status: `source_implementation_complete`
Goal Contract Missing Fields:
- None for source closeout.
Runtime Missing Fields:
- Selector enforcement evidence is not required unless final report claims it.
Ready-for-Agent Missing Fields:
- None for source closeout; a stable remote issue ID remains optional.
Triage Recommendation Candidate: `source-closeout complete`

Next action:
- Preserve decision-map route-conflict negatives; public exposure remains a separate HITL decision.

### V050-007: v0.5 Regression Suite

Goal: Aggregate and broaden cross-suite positive, negative, and hard-negative fixtures for v0.5 routes and evidence boundaries after foundation and shared-reference slices land.

Current State: `implemented_source_validated`.

Execution: Source implementation and deterministic local validation are complete.

Source Implementation History: commit `f01e166` (`test(v050): 增加回归覆盖聚合套件`) plus source regression additions for prototype annotation carry-through, UAT evidence windows, and cross-boundary contract lineage.

Contract Impact: eval contract / regression coverage map.

Dependencies:
- Satisfied: all default foundation, prototype, shared-reference, and annotation source slices.
- Optional publicization slices remain excluded because none has received the required HITL acceptance.

Scope:
- Gather hard negatives added by V050-001A, V050-001B, V050-005A/C, V050-003A, V050-004A, and V050-006A.
- Add cross-skill route-conflict fixtures.
- Ensure V050-007 is not the only place where foundational hard negatives land.
- Include optional publicization slices only if they have been accepted into v0.5.

Primary files:
- `evals/prompts/v0.5-skill-expansion.csv`
- `evals/prompts/v0.5-runtime-capability.csv`
- `evals/prompts/v0.5-role-separation.csv`
- `evals/prompts/v0.5-prototype-lab.csv`
- Existing touched route CSVs as needed.

Explicit non-goals:
- Do not use this slice to compensate for missing per-slice hard negatives.
- Do not require optional publicization slices by default.
- Do not claim runtime, installed plugin, release, UAT, browser, or selector evidence from CSV/source validation.

Acceptance Criteria:
- PRD FR-550 and FR-551 are represented across eval prompts.
- PRD AC-C1 through AC-C7 are covered by hard negatives.
- PRD AC-D1 through AC-D3 remain preserved in final report and evidence-boundary prompts.
- Dependencies reflect foundation plus shared-reference slices and accepted publicization slices only.

Hard-negative evals:
- Self-check treated as independent readiness.
- Reviewer self-fix treated as clean review pass.
- Prototype mock field promoted to backend/API contract.
- Visual packet treated as browser/runtime/UAT/release evidence.
- Prompt text triggers `tool_enforced` overclaim.
- Child-thread/subagent runtimes silently substituted.
- Spark used as final authority.

Checks:
- `git diff --check`
- `python3 -c "import csv, pathlib; [list(csv.DictReader(open(p, newline=''))) for p in pathlib.Path('evals/prompts').glob('*.csv')]; print('csv ok')"`
- Targeted source/eval inspection for every AC-C hard negative.
- Runtime eval only if a separate qualifying evidence run explicitly refreshes or proves installed plugin cache/source equivalence; otherwise report runtime evidence as not claimed.

Verification Evidence Needed:
- Command output for the checks above.
- Coverage map from PRD AC-C1 through AC-C7 to concrete fixtures.
- Evidence that V050-007 aggregates, rather than replaces, per-slice hard negatives from role/runtime/prototype/shared-reference slices.
- Explicit statement that runtime/cache evidence is not claimed unless installed plugin root and cache/source equivalence are named.

Role separation / evidence boundary:
- Regression source-validation can show prompt coverage and schema consistency.
- It cannot prove installed plugin behavior unless run against the installed plugin root with cache/source equivalence named.
- Independent verification should map AC-C/AC-D coverage to concrete fixtures and command output.

Goal Mode independence:
- Its default-slice dependencies are satisfied.
- Its eval prompts and coverage mapping are source-implemented without requiring optional publicization.

Implementation Task Type: `completed_source_implementation`
Implementation Runtime Evidence: `not_claimed`; schema/source checks are not installed-plugin runtime evidence.
Product Runtime Covered: `none`
Isolation Record: Historical implementation topology is not used as current evidence.
Parallelization Status:
- eligible: not applicable; source implementation is complete.
- conflict group: `v050-regression-suite`
- dependency group: `v050-default-shared-references`
- merge order status: satisfied after all default slices.
Goal Contract Status: `source_implementation_complete`
Goal Contract Missing Fields:
- None for source closeout; no optional publicization slice is included.
Runtime Missing Fields:
- Installed plugin root and cache/source equivalence are required only if runtime eval evidence is claimed.
Ready-for-Agent Missing Fields:
- None for source closeout; a stable remote issue ID remains optional.
Triage Recommendation Candidate: `source-closeout complete`

Next action:
- Preserve cross-suite regression coverage and keep installed-plugin runtime claims separate from source/schema validation.

## 条件 Publicization Slices

### V050-003B: Public `grill` Skill

Default Status: conditional, not default v0.5 work.

Current State: `hitl_gated_missing_fields`.

Execution: HITL-gated candidate. Maintainer public exposure acceptance is required before Goal Contract generation.

Contract Impact: public skill surface / routing contract / eval contract.

Blockers:
- V050-003A is source-implemented and locally validated; its dependency is satisfied.
- Maintainer must explicitly accept public `grill` exposure.
- Independent skill-quality audit evidence must exist.

Entry Gate:
- Satisfied locally: V050-003A has landed and its route-negative suite is source-validated.
- Maintainer explicitly accepts public `grill` exposure.
- Skill-quality and independent audit evidence are available.

Scope:
- Create public `grill` skill only after shared grilling behavior proves distinct invocation and avoids over-questioning.

Primary files:
- `skills/grill/SKILL.md`
- `evals/prompts/v0.5-grill.csv`

Explicit non-goals:
- Do not add public skill before maintainer acceptance.
- Do not duplicate `to-prd`, `prototype`, direct answer, or decision mapping routes.

Hard-negative evals:
- Simple direct work over-asks.
- Repo-answerable question asks before inspection.
- Raw ambiguity fails to ask a focused question.

Checks:
- `git diff --check`
- CSV parse smoke
- Targeted route eval evidence as supported by current runner
- Skill-quality audit evidence from a separate role/session

Verification Evidence Needed:
- Command output for the checks above.
- Evidence that V050-003A route negatives passed before public exposure.
- Independent skill-quality audit result and maintainer acceptance.

Role separation / evidence boundary:
- The shared-reference author cannot be final authority for public exposure.
- Public exposure needs separate skill-quality audit and maintainer acceptance.
- Runtime/plugin evidence remains not claimed unless separately refreshed and named.

Implementation Task Type Candidate: `write_implementation`
Implementation Runtime Candidate: `codex_app_managed_worktree_thread after entry gate`
Product Runtime Covered: `none`
Isolation Needed:
- context: `thread`
- filesystem: `codex_managed_worktree`
- diff surface: `required`
Parallelization Candidate:
- eligible: no until entry gate is met.
- conflict group: `v050-public-grill`
- dependency group: `v050-shared-grilling`
- merge order hint: land only after V050-003A and independent audit.

Goal Contract Status: `missing_fields`
Goal Contract Missing Fields:
- Maintainer acceptance of public exposure.
- Independent skill-quality audit result.
Runtime Missing Fields:
- Runtime/cache evidence only if claimed.
Ready-for-Agent Missing Fields:
- Maintainer acceptance of public exposure.
- Independent skill-quality audit result.
Triage Recommendation Candidate: `needs-info recommendation until entry gate is met`

Next action:
- Do not generate an implementation Goal Contract until maintainer acceptance and an independent skill-quality audit are present; keep as conditional HITL needs-info slice.

### V050-004B: Public `decision-map` Skill

Default Status: conditional, not default v0.5 work.

Current State: `hitl_gated_missing_fields`.

Execution: HITL-gated candidate. Maintainer public exposure acceptance is required before Goal Contract generation.

Contract Impact: public skill surface / routing contract / eval contract.

Blockers:
- V050-004A is source-implemented and locally validated; its dependency is satisfied.
- Maintainer must explicitly accept public `decision-map` exposure.
- Independent skill-quality audit evidence must exist.

Entry Gate:
- Satisfied locally: V050-004A has landed and its route-conflict suite is source-validated.
- Maintainer explicitly accepts public `decision-map` exposure.
- Skill-quality and independent audit evidence are available.

Scope:
- Create public `decision-map` skill only after shared reference proves it is not duplicating existing routes.

Primary files:
- `skills/decision-map/SKILL.md`
- `skills/decision-map/DECISION-MAP-TEMPLATE.md`
- `evals/prompts/v0.5-decision-map.csv`

Explicit non-goals:
- Do not create public skill before route-conflict negatives pass.
- Do not turn direct answers or accepted implementation plans into decision-map ceremony.

Hard-negative evals:
- Tiny direct question routed to decision mapping.
- Accepted implementation plan routed away from `write-plan`.
- Accepted runtime package routed away from `dispatch`.

Checks:
- `git diff --check`
- CSV parse smoke
- Targeted route eval evidence as supported by current runner
- Skill-quality audit evidence from a separate role/session

Verification Evidence Needed:
- Command output for the checks above.
- Evidence that V050-004A route-conflict negatives passed before public exposure.
- Independent skill-quality audit result and maintainer acceptance.

Role separation / evidence boundary:
- The shared-reference author cannot be final authority for public exposure.
- Public exposure needs separate skill-quality audit and maintainer acceptance.
- Runtime/profile recommendations remain prompt preferences unless tool/runtime evidence proves enforcement.

Implementation Task Type Candidate: `write_implementation`
Implementation Runtime Candidate: `codex_app_managed_worktree_thread after entry gate`
Product Runtime Covered: `none`
Isolation Needed:
- context: `thread`
- filesystem: `codex_managed_worktree`
- diff surface: `required`
Parallelization Candidate:
- eligible: no until entry gate is met.
- conflict group: `v050-public-decision-map`
- dependency group: `v050-shared-decision-mapping`
- merge order hint: land only after V050-004A and independent audit.

Goal Contract Status: `missing_fields`
Goal Contract Missing Fields:
- Maintainer acceptance of public exposure.
- Independent skill-quality audit result.
Runtime Missing Fields:
- Runtime/cache evidence only if claimed.
Ready-for-Agent Missing Fields:
- Maintainer acceptance of public exposure.
- Independent skill-quality audit result.
Triage Recommendation Candidate: `needs-info recommendation until entry gate is met`

Next action:
- Do not generate an implementation Goal Contract until maintainer acceptance and an independent skill-quality audit are present; keep as conditional HITL needs-info slice.

### V050-006B: Public `skill-audit` Skill

Default Status: conditional, not default v0.5 work.

Current State: `hitl_gated_missing_fields`.

Execution: HITL-gated candidate. Maintainer public exposure acceptance is required before Goal Contract generation.

Contract Impact: public skill surface / skill-quality verification contract / eval contract.

Blockers:
- V050-006A is source-implemented and locally validated; its dependency is satisfied.
- Maintainer must explicitly accept public `skill-audit` exposure.
- Independent review must confirm author self-approval is blocked.

Entry Gate:
- Satisfied locally: V050-006A has landed and its direct-invocation/routing negatives are source-validated.
- Maintainer explicitly accepts public `skill-audit` exposure.
- Independent role confirms author self-approval is blocked.

Scope:
- Create public `skill-audit` skill only if the shared workflow has proven repeated direct invocation value.

Primary files:
- `skills/skill-audit/SKILL.md`
- `skills/skill-audit/SKILL-AUDIT-TEMPLATE.md`
- `evals/prompts/v0.5-skill-audit.csv`

Explicit non-goals:
- Do not create public skill before maintainer acceptance.
- Do not allow skill author to be final authority over its own material skill change.

Hard-negative evals:
- Author self-approves material skill-quality change.
- Public skill addition skips skill-quality audit.
- Shared audit reference is treated as public route before acceptance.

Checks:
- `git diff --check`
- CSV parse smoke
- Targeted route eval evidence as supported by current runner
- Independent skill-quality audit evidence

Verification Evidence Needed:
- Command output for the checks above.
- Evidence that V050-006A direct-invocation/routing negatives justify public exposure.
- Independent review result showing author self-approval remains blocked and maintainer acceptance is present.

Role separation / evidence boundary:
- The shared-reference author cannot be final authority for public exposure.
- Skill author self-audit remains self-check only.
- Public exposure needs maintainer acceptance and independent review that self-approval is blocked.

Implementation Task Type Candidate: `write_implementation`
Implementation Runtime Candidate: `codex_app_managed_worktree_thread after entry gate`
Product Runtime Covered: `none`
Isolation Needed:
- context: `thread`
- filesystem: `codex_managed_worktree`
- diff surface: `required`
Parallelization Candidate:
- eligible: no until entry gate is met.
- conflict group: `v050-public-skill-audit`
- dependency group: `v050-shared-skill-audit`
- merge order hint: land only after V050-006A and independent audit.

Goal Contract Status: `missing_fields`
Goal Contract Missing Fields:
- Maintainer acceptance of public exposure.
- Independent skill-quality audit result.
Runtime Missing Fields:
- Runtime/cache evidence only if claimed.
Ready-for-Agent Missing Fields:
- Maintainer acceptance of public exposure.
- Independent skill-quality audit result.
Triage Recommendation Candidate: `needs-info recommendation until entry gate is met`

Next action:
- Do not generate an implementation Goal Contract until maintainer acceptance and an independent review are present; keep as conditional HITL needs-info slice.

## Ordering Notes

- The historical default order was satisfied: V050-001 established the quality gate, V050-001A established role separation, and V050-001B established runtime/model evidence boundaries before dependent slices.
- V050-005A, V050-005C, V050-005B, V050-006A, V050-003A, V050-004A, and V050-007 are all source-implemented and locally validated.
- GW-PROT-ANNOT-001 is source-implemented and locally validated; its feature-branch Git boundary is committed and clean-checkout source/package validation passed, while post-integration fresh review and PR/CI evidence remain separate and open.
- V050-003A and V050-004A remain shared-reference implementations by default; their publicization slices are not implicitly accepted.
- V050-003B, V050-004B, and V050-006B remain HITL-gated `missing_fields` until explicit maintainer acceptance and independent skill-quality review are present.
- No default implementation ordering action remains open. Any runtime, installed-plugin, UAT, release, or customer-readiness claim requires a separate qualifying evidence chain.

## 每个实现 PR 的固定完成标准

每个 implementation PR 的 final report 应包含：

```text
Scope:
Changed Files:
Source Truth Inspected:
Implementation Self-check:
Clean Review Evidence:
Independent Verification Evidence:
Runtime / Plugin Evidence:
Not Covered:
Hard-negative Fixtures Added:
Commands Run:
Readiness Boundary:
Next Independent Role:
```

默认 `Runtime / Plugin Evidence` 写法：

```text
Not claimed. Source-validation only.
```

只有当实现线程实际命名 installed plugin root、local source root、cache/source refresh 或 equivalence evidence、run scope、commands/trials 和 limitations 时，才能升级为 runtime/cache evidence。

## Next Action

对整合后的 diff 完成 fresh read-only source review，发布可评审 PR，并记录 CI 结果后，再声明 Git-delivery closeout。继续把这些证据与 installed runtime、release、UAT、customer readiness 分开。不要从本 issue map 直接创建 public `grill`、`decision-map` 或 `skill-audit`；三个 publicization slices 仍需明确 maintainer acceptance 和独立 skill-quality review。
