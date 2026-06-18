# v0.4.0 Codex-native Worktree and Handoff Alignment Issue Pack

Target Reader: Groundwork maintainers, implementation agents, dispatch reviewers, and follow-up verification threads executing the v0.4.0 native alignment increment.
Reader Action Needed: Use these tracker-neutral issue drafts to plan, triage, or implement v0.4.0 slices one at a time.
Decision Supported: Which v0.4.0 slices can proceed independently, which slices must land before migration/removal, and what evidence is required before release claims.
Artifact Type: issue map
Source of Truth: `docs/prd-v0.4.0-codex-native-worktree-handoff-alignment.md`
Scope: Issue decomposition for FR-401 through FR-408, including compatibility mapping, route policy, `.worktreeinclude`, native handoff, closeout, dispatch shrink, eval migration, docs positioning, release evidence boundaries, and real handoff trial evidence planning.
Out of Scope: Creating remote tracker issues, implementing the slices, executing Codex App Handoff or Worktree operations, running real handoff trials, mutating plugin cache, claiming release readiness, committing, pushing, or opening a PR.
Evidence Level: Derived from the local PRD marked `prd_ready_for_issue_slicing` and current repository conventions; no runtime, release, UAT, marketplace, or cache-refresh evidence is added by this issue pack.
Safe to Share / Redaction Notes: Safe to share as a tracker-neutral planning artifact. It contains no secrets, credentials, private URLs, browser cookies, PII, logs, or production data.

## Issue Set Summary

Source:

- Canonical source: `docs/prd-v0.4.0-codex-native-worktree-handoff-alignment.md`
- Requirement state: `prd_ready_for_issue_slicing`
- Issue pack status: tracker-neutral local artifact
- Remote tracker status: not created

Batching:

- Batch 1: V040-001 through V040-004. These establish compatibility map, route policy, `.worktreeinclude` safety, and native handoff package shape.
- Batch 2: V040-005 through V040-007. These update closeout, dispatch schema, and fixture/eval coverage after the core package shapes are stable.
- Batch 3: V040-008 through V040-010. These finish docs positioning, release-evidence boundaries, and release-gate trial evidence planning.

Ordering:

- Start with V040-001 before removing or renaming any v0.3.3 adapter fields.
- V040-006 depends on V040-001, V040-002, V040-004, and V040-005 because dispatch shrink must reference the final compatibility, route, handoff, and closeout shapes.
- V040-007 should follow the contract slices it tests.
- V040-009 can draft the release claim schema and trial evidence plan early, but should not finalize references to native closeout fields until V040-005 lands.
- V040-010 owns real Local to Worktree and Worktree to Local handoff trial evidence and remains blocked until implementation packages exist and the user approves or performs Codex App Handoff operations.

Field semantics:

- Implementation Task Type Candidate is a `to-issues` recommendation only.
- Implementation Runtime Candidate is a later `triage` / `dispatch` input for implementing the issue, not an execution command and not a claim that Codex worktree must be used.
- Product Runtime Covered describes the Groundwork or Codex-native semantics being documented, constrained, or tested by the slice; it does not prescribe the implementation runtime.
- Goal Contract Status is `not_generated_by_to_issues` for every slice.
- Ready-for-Agent Missing Fields name gaps for later `triage`; they do not block this issue pack.

## Issue Drafts

### V040-001: Compatibility map for v0.3.3 managed-worktree adapter fields

Goal:
Create a compatibility and migration map for v0.3.3 managed-worktree lifecycle, identity, closeout, dispatch, and fixture fields before any removal or renaming.

Acceptance Criteria:

- Identify v0.3.3 files that contain custom managed-worktree runtime or lifecycle fields.
- Classify each field or section as `keep`, `deprecate_in_place`, `slim`, `rename`, `replace_with_native_alignment`, or `remove_after_eval_migration`.
- Decide whether `codex_app_managed_worktree_thread` remains the legacy adapter name during v0.4.0.
- Map runtime identity fields to either native evidence references or explicit `availability` markers.
- Separate compatibility fixtures from new native-alignment fixtures.
- Do not remove or rename files in this slice unless the map proves the change is local and non-breaking.

Evidence / Source:

- PRD Confirmed Decisions and Open Implementation Questions.
- PRD FR-405, FR-406, AC-405, AC-406.
- Existing files under `skills/dispatch/adapters/codex_app_managed_worktree_thread/`.
- Existing `evals/prompts/dispatch-managed-worktree-lifecycle.csv` and `evals/scenarios/managed-worktree-lifecycle.md`.

Blockers:

- None for mapping. Any deletion or rename is blocked until V040-007 proves fixture coverage.

Execution: AFK.

Contract Impact:

- docs
- adapter contract
- verification contract
- migration boundary

Verification Evidence Needed:

- `git diff --check`
- `git status --short`
- Field/section map cites every touched or planned v0.3.3 adapter file.
- No runtime, cache, release, or handoff-trial readiness claim is made.

Implementation Task Type Candidate: `write_implementation`

Implementation Runtime Candidate: `main_thread_direct`

Product Runtime Covered: `codex_app_managed_worktree_thread`

Isolation Needed:

- context: `none`
- filesystem: `current_workspace`
- diff surface: `required`

Parallelization Candidate:

- eligible: no
- conflict group: `v040-compatibility-map`
- dependency group: `v040-core`
- merge order hint: first slice; must land before schema shrink or fixture migration.

Goal Contract Status: `not_generated_by_to_issues`

Goal Contract Missing Fields:

- Concrete Goal Contract must be generated by `triage` or `write-plan` before execution.

Runtime Missing Fields:

- Exact file list to inspect must be confirmed from current source before edits.

Ready-for-Agent Missing Fields:

- None for a mapping artifact. Removal or rename work remains out of scope for this slice.

Triage Recommendation Candidate: `ready-for-agent candidate`

### V040-002: Worktree route policy schema and dispatch docs alignment

Goal:
Add the v0.4.0 route policy shape so Groundwork can distinguish `local_direct`, `local_with_artifact`, `worktree_isolated`, `worktree_review_only`, and `automation_candidate` without claiming runtime execution.

Acceptance Criteria:

- Route enum and route decision fields from FR-401 are represented in dispatch-facing docs or package schemas.
- Route decisions include workspace state, base state, conflict state, runtime surface availability, risk, setup requirements, rollback/archive path, and evidence required before closeout.
- Read-only review and planning-only work cannot route to `worktree_isolated`.
- Dirty workspace, unrelated staged files, stale base, shared-file conflicts, or serial dependencies can justify `worktree_isolated` only when the decision names the concrete input.
- `automation_candidate` remains recommendation-only and does not create or update automations.
- Existing dispatch docs preserve the package-only boundary.

Evidence / Source:

- PRD FR-401, AC-401.
- `skills/dispatch/DISPATCH-PACKAGE.md`
- `docs/runtime-dispatch-workflow.md`
- `skills/dispatch/RUNTIME-ADAPTERS.md`

Blockers:

- V040-001 should land first if route policy wording needs to deprecate old adapter fields.

Execution: AFK.

Contract Impact:

- dispatch package
- docs
- verification contract

Verification Evidence Needed:

- `git diff --check`
- CSV parse for eval prompt files if touched.
- Focused text search showing no route docs claim Codex App worktree creation occurred from package generation.
- New or updated eval rows for low-risk `local_direct` and isolation-justified `worktree_isolated`.

Implementation Task Type Candidate: `write_implementation`

Implementation Runtime Candidate: `triage_required`

Product Runtime Covered: `dispatch_core`

Isolation Needed:

- context: `none unless triage selects isolation`
- filesystem: `current_workspace unless triage selects isolation`
- diff surface: `required`

Parallelization Candidate:

- eligible: yes after V040-001
- conflict group: `dispatch-route-policy`
- dependency group: `v040-core`
- merge order hint: after V040-001; before V040-006 and V040-007.

Goal Contract Status: `not_generated_by_to_issues`

Goal Contract Missing Fields:

- Concrete file path allowlist.
- Focused validation command list.

Runtime Missing Fields:

- Current dispatch package schema owner file must be confirmed before edits.

Ready-for-Agent Missing Fields:

- Exact eval prompt file names for route policy rows.

Triage Recommendation Candidate: `ready-for-agent candidate after V040-001`

### V040-003: `.worktreeinclude` example, safety doc, and verify lens

Goal:
Add conservative `.worktreeinclude` guidance that aligns with official Codex semantics while preventing committed examples from normalizing secret-bearing local paths.

Acceptance Criteria:

- Add root `.worktreeinclude.example` with only safe placeholder entries.
- Add `docs/worktreeinclude-safety.md` explaining official copy semantics, project-owner-only private paths, forbidden committed examples, and git-boundary expectations.
- `verify` gains a worktreeinclude safety lens or equivalent documented checklist.
- The example contains no real secrets, credentials, private URLs, browser cookies, PII, private logs, production data, or large generated caches.
- The safety doc explains that official Codex docs allow `.env`, `.env.local`, and `config/secrets.json` in private `.worktreeinclude`, but Groundwork committed examples remain conservative.
- Git-boundary guidance says private `.worktreeinclude` files that name sensitive local paths must remain unstaged/uncommitted unless explicitly approved.

Evidence / Source:

- PRD FR-402, AC-402.
- Official docs reference map in PRD section 9.
- `skills/verify/SKILL.md`
- `skills/_shared/GIT-BOUNDARY.md`

Blockers:

- None.

Execution: AFK.

Contract Impact:

- docs
- verification contract
- git-boundary safety

Verification Evidence Needed:

- `git diff --check`
- Effective `.worktreeinclude.example` entries check: non-comment, non-empty lines must not contain `.env`, `.env.local`, `config/secrets.json`, cookies, tokens, secrets, PII, `.groundwork`, or `.trellis`.
- Safety documentation evidence search: `docs/worktreeinclude-safety.md` and `skills/verify/SKILL.md` must explain `.env`, `.env.local`, `config/secrets.json`, cookies, tokens, secrets, PII, `.groundwork`, and `.trellis` risk boundaries.
- Manual check that `.worktreeinclude.example` entries are placeholders only.
- CSV parse if eval prompt files are touched.

Implementation Task Type Candidate: `write_implementation`

Implementation Runtime Candidate: `main_thread_direct`

Product Runtime Covered: `none`

Isolation Needed:

- context: `none`
- filesystem: `current_workspace`
- diff surface: `required`

Parallelization Candidate:

- eligible: yes
- conflict group: `worktreeinclude-safety`
- dependency group: `v040-core`
- merge order hint: can run in parallel with V040-002 if `skills/verify/SKILL.md` ownership is coordinated.

Goal Contract Status: `not_generated_by_to_issues`

Goal Contract Missing Fields:

- Concrete validation commands.

Runtime Missing Fields:

- None.

Ready-for-Agent Missing Fields:

- Decide whether eval rows for `worktreeinclude_safety_violation_count` belong in an existing `verify.csv` or a new targeted suite.

Triage Recommendation Candidate: `ready-for-agent candidate`

### V040-004: Native handoff package contract and handoff docs update

Goal:
Define the `native_handoff_package` shape for Local to Worktree and Worktree to Local continuation without letting Groundwork claim it performs Codex App Handoff.

Acceptance Criteria:

- Add or update handoff docs with `native_handoff_package` fields from FR-403.
- `native_context.thread_ref`, `native_context.worktree_path`, and `native_context.worktree_association` include explicit `availability` values.
- Local to Worktree packages before native worktree creation mark worktree path as `unavailable_before_handoff`, not an invented path.
- Worktree to Local packages require changed files, evidence, open risks, stop condition, and `native_context` fields with explicit availability markers before closeout; visible native context must be recorded when available.
- Handoff package cites canonical artifacts instead of copying full PRDs, full issue bodies, long diffs, logs, or transcripts.
- Handoff docs state that official Codex Handoff owns moving the thread and code between Local and Worktree.
- Handoff packages never instruct `git add .`.

Evidence / Source:

- PRD FR-403, AC-403.
- `skills/handoff/SKILL.md`
- `skills/handoff/REVIEW-PACKAGE.md`
- Existing managed-worktree review/result templates where handoff context is currently implied.

Blockers:

- V040-001 should land first if legacy runtime identity fields are being remapped.

Execution: AFK.

Contract Impact:

- handoff package
- docs
- runtime evidence boundary

Verification Evidence Needed:

- `git diff --check`
- Search for handoff docs that imply Groundwork performs Codex App Handoff and update them.
- Fixture or scenario showing Local to Worktree unavailable native context.
- Fixture or scenario showing Worktree to Local visible native context.

Implementation Task Type Candidate: `write_implementation`

Implementation Runtime Candidate: `main_thread_direct`

Product Runtime Covered: `codex_handoff_semantics`

Isolation Needed:

- context: `none`
- filesystem: `current_workspace`
- diff surface: `required`

Parallelization Candidate:

- eligible: yes after V040-001
- conflict group: `native-handoff-contract`
- dependency group: `v040-core`
- merge order hint: before V040-006 and V040-007.

Goal Contract Status: `not_generated_by_to_issues`

Goal Contract Missing Fields:

- Exact docs and fixture paths.

Runtime Missing Fields:

- None. Runtime execution is out of scope.

Ready-for-Agent Missing Fields:

- Decide whether native handoff fixture lives under `evals/scenarios/` or adapter template examples.

Triage Recommendation Candidate: `ready-for-agent candidate after V040-001`

### V040-005: Native closeout contract and merge gate checks

Goal:
Replace broad lifecycle progression with a native closeout contract that separates merge decision from thread archive, worktree retention, and branch cleanup.

Acceptance Criteria:

- Add or update closeout template with `native_closeout_package`.
- Native closeout templates use `merge_decision` and `cleanup_decision`; any retained legacy `merge_recommendation` or `cleanup_action` fields must be explicitly marked legacy or deprecated according to V040-001.
- `merge_decision.recommendation: merge` is blocked when evidence, git boundary, passed review status, or known merge source is missing.
- `merge_decision.merge_source` supports `patch_bundle`, `visible_branch`, `codex_handoff`, `pathspec_checkout`, `none`, and `unknown`.
- `cleanup_decision.thread_action`, `cleanup_decision.worktree_action`, and `cleanup_decision.branch_action` are separate fields.
- Archive, worktree retention, and branch cleanup are cleanup decisions, not merge recommendations.
- Closeout docs do not claim archive, worktree cleanup, branch deletion, runtime execution, or release readiness without evidence.

Evidence / Source:

- PRD FR-404, AC-404.
- `skills/dispatch/adapters/codex_app_managed_worktree_thread/CLOSEOUT-PACKAGE-TEMPLATE.md`
- `skills/dispatch/adapters/codex_app_managed_worktree_thread/BRANCH-CLEANUP-CHECKLIST.md`
- `skills/verify/SKILL.md`

Blockers:

- V040-001 should land first to decide legacy closeout compatibility.

Execution: AFK.

Contract Impact:

- closeout package
- verification contract
- git boundary

Verification Evidence Needed:

- `git diff --check`
- Search confirms old field names are removed or explicitly marked legacy where retained.
- Eval fixture rejects merge with missing evidence.
- Eval fixture rejects merge with missing git boundary.
- Eval fixture rejects merge with unknown or missing merge source.
- Eval fixture separates cleanup decision from merge decision.

Implementation Task Type Candidate: `write_implementation`

Implementation Runtime Candidate: `main_thread_direct`

Product Runtime Covered: `closeout_contract_for_codex_worktree_results`

Isolation Needed:

- context: `none`
- filesystem: `current_workspace`
- diff surface: `required`

Parallelization Candidate:

- eligible: yes after V040-001
- conflict group: `native-closeout-contract`
- dependency group: `v040-core`
- merge order hint: before V040-006 and V040-007.

Goal Contract Status: `not_generated_by_to_issues`

Goal Contract Missing Fields:

- Concrete acceptance mapping to existing closeout fixtures.

Runtime Missing Fields:

- None for docs/schema. Real closeout execution evidence is out of scope.

Ready-for-Agent Missing Fields:

- Decide whether legacy closeout template is replaced in place or paired with a native template during migration.

Triage Recommendation Candidate: `ready-for-agent candidate after V040-001`

### V040-006: Dispatch runtime surface reduction and native alignment schema

Goal:
Shrink dispatch output to route decision, policy, source package, handoff expectation, closeout expectation, verification expectation, approval requirements, and runtime evidence ownership.

Acceptance Criteria:

- Dispatch package docs add or migrate to `dispatch_native_alignment`.
- Dispatch output no longer models execution-layer lifecycle details owned by Codex-native runtime.
- Deprecated custom lifecycle, registry, child-thread identity, selector enforcement, and background-run fields are marked according to V040-001.
- Dispatch keeps expected handoff and expected closeout package references.
- Dispatch schema uses `merge_gate: evidence_git_boundary_review_and_merge_source_required` where merge readiness is in scope.
- Dispatch docs keep remote writes and destructive actions disabled by default.
- Dispatch package generation does not claim Codex App worktree creation, Handoff execution, archive, cleanup, runtime success, cache refresh, or release readiness.

Evidence / Source:

- PRD FR-405, AC-405.
- `skills/dispatch/DISPATCH-PACKAGE.md`
- `skills/dispatch/SKILL.md`
- `docs/runtime-dispatch-workflow.md`
- V040-001 compatibility map.
- V040-002 route policy shape.
- V040-004 native handoff contract.
- V040-005 native closeout contract.

Blockers:

- V040-001, V040-002, V040-004, and V040-005 should land first or be implemented in the same tightly scoped branch with clear ordering.

Execution: AFK.

Contract Impact:

- dispatch package
- runtime evidence boundary
- docs
- verification contract

Verification Evidence Needed:

- `git diff --check`
- CSV parse for eval prompt files.
- Focused search for old runtime-owned state claims.
- Targeted eval rows showing package-only dispatch with expected handoff/closeout but no runtime execution claim.

Implementation Task Type Candidate: `write_implementation`

Implementation Runtime Candidate: `triage_required`

Product Runtime Covered: `dispatch_core`

Isolation Needed:

- context: `none unless triage selects isolation`
- filesystem: `current_workspace unless triage selects isolation`
- diff surface: `required`

Parallelization Candidate:

- eligible: no
- conflict group: `dispatch-native-alignment`
- dependency group: `v040-core`
- merge order hint: after V040-001, V040-002, V040-004, and V040-005.

Goal Contract Status: `not_generated_by_to_issues`

Goal Contract Missing Fields:

- Concrete Goal Contract must define the exact dispatch files to edit.

Runtime Missing Fields:

- Compatibility map from V040-001.
- Final route policy shape from V040-002.
- Final native handoff and closeout shapes from V040-004 and V040-005.

Ready-for-Agent Missing Fields:

- Upstream contract slices not yet merged.

Triage Recommendation Candidate: `needs-info recommendation until dependencies land`

### V040-007: Native alignment fixture and eval migration

Goal:
Migrate v0.3.3 lifecycle fixture intent into native alignment fixtures without losing safety coverage.

Acceptance Criteria:

- Preserve compatibility coverage for v0.3.3 lifecycle fixture intent.
- Add native-alignment fixture coverage for `local_direct` versus `worktree_isolated` route decisions.
- Add `.worktreeinclude.example` pass/fail fixture coverage.
- Add Local to Worktree handoff fixture that uses `availability: unavailable_before_handoff`.
- Add Worktree to Local handoff fixture with visible native context, changed files, evidence, open risks, and stop condition.
- Add closeout fixtures rejecting merge when evidence, git boundary, review status, or merge source is missing.
- Add dispatch artifact fixture proving Groundwork does not own execution runtime fields that conflict with Codex-native ownership.
- Add fixture coverage showing local environment setup requirements are represented as route setup requirements or manual/Codex setup evidence, not as Groundwork-executed worktree setup.
- Fixture/eval docs state whether each migrated row is compatibility coverage or native-alignment coverage.

Evidence / Source:

- PRD FR-406, AC-401 through AC-406, and AC-409 for local environment setup representation.
- Existing `evals/prompts/dispatch-managed-worktree-lifecycle.csv`.
- Existing `evals/scenarios/managed-worktree-lifecycle.md`.
- V040-002 through V040-006.

Blockers:

- Contract slices V040-002 through V040-006 must be stable enough to test.

Execution: AFK.

Contract Impact:

- eval fixtures
- verification contract
- release gate evidence

Verification Evidence Needed:

- `git diff --check`
- CSV parse for all eval prompt CSVs.
- Focused runtime/eval validation command, if existing runner supports the touched suite.
- Manual row review mapping each native alignment fixture to FR-406 fixture classes and AC-401 through AC-406, with AC-409 covered here or explicitly delegated to V040-008.
- State explicitly that local fixture checks are not real Codex App runtime evidence.

Implementation Task Type Candidate: `write_implementation`

Implementation Runtime Candidate: `triage_required`

Product Runtime Covered: `native_alignment_eval_coverage`

Isolation Needed:

- context: `none unless triage selects isolation`
- filesystem: `current_workspace unless triage selects isolation`
- diff surface: `required`

Parallelization Candidate:

- eligible: no
- conflict group: `native-alignment-evals`
- dependency group: `v040-fixtures`
- merge order hint: after V040-002 through V040-006.

Goal Contract Status: `not_generated_by_to_issues`

Goal Contract Missing Fields:

- Exact suite names and runner command.

Runtime Missing Fields:

- Stable contract shapes from upstream slices.

Ready-for-Agent Missing Fields:

- Upstream contract files and expected fixture schema must be present.

Triage Recommendation Candidate: `needs-info recommendation until dependencies land`

### V040-008: Documentation positioning and release-gate checklist

Goal:
Update maintainer and workflow docs so Groundwork's v0.4.0 boundary is visible: Groundwork governs route, policy, evidence, handoff, and closeout gates, while Codex-native runtime owns worktree creation, Handoff Git mechanics, retention/deletion, automations, and subagent orchestration.

Acceptance Criteria:

- Docs include the v0.4.0 boundary statement from FR-407.
- Docs do not claim Groundwork replaces the Codex worktree runtime.
- README positioning is updated only if this slice explicitly includes it.
- Runtime-dispatch workflow docs separate package generation, handoff package preparation, closeout package evaluation, and real Codex runtime evidence.
- Docs mention that local environments are the native setup-script mechanism for worktrees.
- Docs mention that automations are Codex automation concerns and not created by Groundwork route recommendation alone.
- Docs mention subagents are explicit and not a default Groundwork behavior.
- Release-gate checklist names real Local to Worktree and Worktree to Local handoff trials as promotion/release evidence, not initial contract/schema merge blockers.

Evidence / Source:

- PRD FR-407, AC-407, release gates.
- `docs/runtime-dispatch-workflow.md`
- `docs/prd-dispatch-runtime-router.md`
- `README.md`
- V040-002 through V040-007.

Blockers:

- Upstream contract wording should be stable before broad docs positioning.

Execution: AFK.

Contract Impact:

- docs
- release gate
- maintainer workflow

Verification Evidence Needed:

- `git diff --check`
- Search for stale wording such as "Groundwork creates worktrees", "Groundwork performs Handoff", or runtime readiness claims from package generation.
- Manual link/source review against PRD official docs reference map.
- Plugin JSON validation only if plugin metadata is touched.

Implementation Task Type Candidate: `write_implementation`

Implementation Runtime Candidate: `main_thread_direct`

Product Runtime Covered: `none`

Isolation Needed:

- context: `none`
- filesystem: `current_workspace`
- diff surface: `required`

Parallelization Candidate:

- eligible: yes after core contracts stabilize
- conflict group: `v040-doc-positioning`
- dependency group: `v040-docs`
- merge order hint: after V040-002 through V040-007.

Goal Contract Status: `not_generated_by_to_issues`

Goal Contract Missing Fields:

- Concrete docs file allowlist.

Runtime Missing Fields:

- None.

Ready-for-Agent Missing Fields:

- Decide whether README is in scope for the implementation PR.

Triage Recommendation Candidate: `needs-info recommendation until docs scope is confirmed`

### V040-009: Release evidence claim boundary schema and docs

Goal:
Add the release evidence claim boundary schema and documentation without claiming runtime/cache/release readiness from docs or schema changes alone.

Acceptance Criteria:

- Add or update verification docs with `release_evidence_claim`.
- Any runtime, cache, release, UAT, marketplace, or cache-refresh claim must include claim type, evidence status, installed plugin root, source root, refresh/equivalence method, run scope, commands/trials, and limitations.
- Documentation and schema edits alone set runtime/cache/release/UAT/marketplace evidence to `unverified` or `not_applicable`.
- Release readiness is not inferred from PRD acceptance, issue-pack completion, or fixture pass alone.
- Add a real handoff trial evidence plan that defines required trial fields and explicitly delegates actual trial execution to V040-010.
- The evidence plan states that Codex App Handoff execution evidence is separate from Groundwork package/schema evidence.

Evidence / Source:

- PRD FR-408, AC-408, release gates.
- `skills/verify/SKILL.md`
- `docs/runtime-dispatch-workflow.md`
- `evals/baselines/` conventions for evidence snapshots.

Blockers:

- V040-005 should land first if release evidence docs reference native closeout fields.

Execution: AFK.

Contract Impact:

- verification contract
- release gate
- baseline/evidence policy

Verification Evidence Needed:

- `git diff --check`
- CSV parse if eval files are touched.
- Search showing no docs/schema path claims release readiness without `release_evidence_claim`.
- Evidence plan review showing actual real handoff trials are delegated to V040-010.

Implementation Task Type Candidate: `write_implementation`

Implementation Runtime Candidate: `main_thread_direct`

Product Runtime Covered: `none`

Isolation Needed:

- context: `none`
- filesystem: `current_workspace`
- diff surface: `required`

Parallelization Candidate:

- eligible: yes after V040-005
- conflict group: `release-evidence-boundary`
- dependency group: `v040-release`
- merge order hint: after V040-005; before V040-010.

Goal Contract Status: `not_generated_by_to_issues`

Goal Contract Missing Fields:

- Concrete docs/schema file allowlist.

Runtime Missing Fields:

- None for docs/schema. Runtime/cache/release evidence remains unverified until V040-010 or later release evidence exists.

Ready-for-Agent Missing Fields:

- None for docs/schema.

Triage Recommendation Candidate: `ready-for-agent candidate after V040-005`

### V040-010: Real Local to Worktree and Worktree to Local handoff trial evidence

Goal:
Collect real v0.4.0 Local to Worktree and Worktree to Local handoff trial evidence for release-gate evaluation without treating local docs, schema, or fixture evidence as Codex App runtime evidence.

Acceptance Criteria:

- Execute or collect evidence for at least one real Local to Worktree handoff trial.
- Execute or collect evidence for at least one real Worktree to Local handoff trial.
- Each real handoff trial records direction, base ref/commit, available native context, handoff package path, changed files when applicable, evidence, open risks, and closeout result.
- Trial evidence names installed plugin root, source root, refresh/equivalence method, run scope, commands or Codex App operations performed, and limitations.
- Trial evidence separates Codex App Handoff execution evidence from Groundwork package/schema evidence.
- No release readiness claim is made when required trial evidence, git boundary, review status, installed plugin root, or source/cache boundary is missing.

Evidence / Source:

- PRD FR-408, AC-408, release gates.
- Release evidence claim schema from V040-009.
- `evals/baselines/` conventions for evidence snapshots.

Blockers:

- V040-009 should land first to define the evidence claim shape and trial plan.
- Real trial execution is blocked until the implementation packages exist and the user approves or performs Codex App Handoff operations.

Execution: HITL.

Contract Impact:

- release gate
- baseline/evidence policy
- handoff trial evidence

Verification Evidence Needed:

- Real Local to Worktree trial evidence.
- Real Worktree to Local trial evidence.
- Installed plugin root and source/cache refresh or equivalence evidence.
- Git boundary and closeout evidence for any changed files.
- Explicit limitations for any missing native context or unavailable Codex App surface.

Implementation Task Type Candidate: `verification`

Implementation Runtime Candidate: `triage_required`

Product Runtime Covered: `codex_handoff_semantics`

Isolation Needed:

- context: `thread for Codex App Handoff evidence, subject to trial route and available Codex surface`
- filesystem: `unknown until trial route is selected`
- diff surface: `optional`

Parallelization Candidate:

- eligible: no
- conflict group: `real-handoff-trial-evidence`
- dependency group: `v040-release`
- merge order hint: after V040-009 and after implementation packages are runnable.

Goal Contract Status: `not_generated_by_to_issues`

Goal Contract Missing Fields:

- Concrete trial target tasks.
- User-approved Codex App Handoff operation boundary.

Runtime Missing Fields:

- Installed plugin root and cache/source refresh or equivalence evidence.
- Real Local to Worktree and Worktree to Local trial availability.

Ready-for-Agent Missing Fields:

- User approval or user-performed Codex App Handoff operation for real trials.
- Runnable implementation package paths.

Triage Recommendation Candidate: `needs-info recommendation until real trial prerequisites exist`

## Ordering Notes

1. V040-001 is the first slice because it protects compatibility and prevents premature deletion of v0.3.3 safety coverage.
2. V040-002, V040-003, V040-004, and V040-005 can proceed in parallel only when file ownership does not overlap.
3. V040-006 should wait for compatibility, route, handoff, and closeout shapes to stabilize.
4. V040-007 should wait for contract slices so eval rows do not chase unstable schemas.
5. V040-008 and V040-009 close documentation and release-evidence boundaries after the package contracts are coherent.
6. V040-010 is HITL release-gate evidence and should not be treated as an ordinary docs/schema implementation issue.

## Next Action

Run `triage` on V040-001 to create the first concrete Goal Contract, then implement V040-001 before any v0.3.3 adapter file removal, rename, or schema shrink.

## Artifact Recommendation

Keep this issue pack as the local canonical planning artifact at `artifacts/v0.4.0-codex-native-worktree-handoff/issue-map.md`. Do not create remote tracker issues until the maintainer decides which slices should become GitHub issues or PRs.
