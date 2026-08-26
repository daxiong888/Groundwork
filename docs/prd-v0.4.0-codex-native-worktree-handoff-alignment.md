# PRD v0.4.0: Codex-native Worktree and Handoff Alignment

> [!IMPORTANT]
> 本文保留 v0.4.0 功能决策与实现历史。文中 `evals/` 路径、旧 Eval 命令和 suite 要求已由 `docs/prd-plugin-candidate-trial-migration-v1.md` 的减法迁移废止，只能作为历史事实，不能作为当前架构、命令或 Candidate authority。

Target Reader: Groundwork maintainers, dispatch reviewers, runtime adapter authors, and future implementation agents planning the v0.4.0 worktree alignment release.
Reader Action Needed: Review, confirm, and use this PRD as the source truth for issue slicing and implementation planning.
Decision Supported: Whether Groundwork should shrink managed worktree ownership into Codex-native governance, handoff, evidence, and closeout contracts for v0.4.0.
Artifact Type: PRD
Source of Truth: User-provided v0.4.0 draft, official OpenAI Codex Worktrees/App/Automations/Local Environments/Subagents documentation checked on 2026-06-18, plus local Groundwork v0.3.3 PRD, dispatch package contract, runtime workflow, handoff skill contract, and closeout template.
Scope: Route policy, `.worktreeinclude` guidance, Local to Worktree and Worktree to Local handoff packages, closeout gating, dispatch runtime-surface reduction, release evidence claim boundary, docs, fixtures, and eval coverage.
Out of Scope: Codex App internal UI automation, automatic thread or worktree creation, remote writes, automation scheduling, public skill expansion, copying secrets or local runtime files into git, and claiming runtime/cache/release readiness from documentation edits alone.
Evidence Level: Draft requirement grounded in official Codex documentation and existing local contracts; no current runtime trial, release, UAT, marketplace, or cache-refresh evidence is claimed.
Safe to Share / Redaction Notes: Safe to share as a design artifact. It contains no secrets, credentials, private URLs, browser cookies, PII, logs, or production data.
Status: Draft for maintainer review.
Version Target: 0.4.0.
Last Updated: 2026-06-18.

---

## 1. Lifecycle Preflight

Intent: new_requirement.
Suggested Workflow Mode: to-prd.
Locale: Chinese user-facing discussion, English identifiers and schema fields.
Source of Truth: mixed, with user draft as product intent, official Codex documentation as product-behavior evidence, and local Groundwork docs/contracts as current-state evidence.
Requirement State: prd_draft.
Artifact Promotion: required, because this PRD should become the source for issue slicing and implementation.
Execution Topology: branch_required, satisfied by the current feature branch.
Risk Gate: git_write for this PRD artifact only.
Verification Strategy: scoped documentation checks.
Lifecycle State: not_needed for this bounded PRD draft.
Stop Condition: PRD is coherent enough for maintainer review and later `to-issues` slicing, without claiming runtime readiness.

## 2. Grill Before Write

### Target Reader

Groundwork maintainers and future agents who will decide how much v0.3.3 managed-worktree protocol should remain after aligning with Codex-native worktree and handoff semantics.

### Decision Supported

Whether v0.4.0 should:

- keep Groundwork as a governance and evidence layer;
- remove or deprecate self-managed execution protocol fields that duplicate Codex worktree runtime behavior;
- introduce native handoff and closeout package checks that are inspectable by `verify` and evals.

### Known Facts

- Official Codex documentation defines Worktree as a Git worktree created from the local checkout in the Codex app, and Handoff as the flow that moves a thread between Local and Worktree while Codex handles the required Git operations.
- Official Codex documentation says Codex-managed worktrees are created under `$CODEX_HOME/worktrees`, usually start in detached HEAD, may apply selected branch local changes, and are lightweight/disposable by default.
- Official Codex documentation defines `.worktreeinclude` as a repository-root file that lists ignored paths or `.gitignore`-style patterns to copy into local Codex-managed worktrees.
- Official Codex documentation says Codex automatically copies ignored `AGENTS.override.md` into local managed worktrees, so it does not need to be listed in `.worktreeinclude`.
- Official Codex documentation says Codex-managed worktrees are dedicated to a thread by default and can be returned to the same associated worktree after Handoff.
- Official Codex documentation says local environments configure setup scripts and actions for worktrees.
- Official Codex documentation says automations in Git repositories can run either in the local project or on dedicated background worktrees.
- Official Codex documentation says subagents are explicit, not automatic; parallel write-heavy workflows need care because they can create conflicts.
- Groundwork v0.3.3 already documents `dispatch` as package-only, not a runtime executor.
- v0.3.3 added internal managed-worktree lifecycle, closeout, merge-back, clean-review, branch-cleanup, Goal Mode, and runtime identity contracts under `skills/dispatch/adapters/codex_app_managed_worktree_thread/`.
- `docs/runtime-dispatch-workflow.md` already says Codex App thread creation, lifecycle monitoring, selector enforcement, archive, and branch cleanup require adapter or runtime evidence.
- `skills/handoff/SKILL.md` already treats handoff as compact continuation state, not a runtime executor, clean reviewer, verifier, closeout owner, merge-back owner, archive owner, branch cleanup owner, commit path, push path, PR path, or tracker mutation path.
- The user-provided v0.4.0 direction is to "borrow instead of reimplement": Groundwork should align with Codex-native worktree and handoff semantics instead of maintaining a separate abstract lifecycle runtime.

### Assumptions

- "Codex-native" means Groundwork should define policy, package shape, safety gates, evidence requirements, and closeout checks, while Codex App or another execution-capable adapter owns actual worktree/thread operations and native Handoff Git operations.
- Existing v0.3.3 adapter docs may be migrated, slimmed, or marked superseded, but the final implementation choice should be made during issue slicing and source inspection.
- Route decisions should remain deterministic enough for eval prompts even when runtime execution is not performed.
- `.worktreeinclude` is an official Codex App mechanism for local Codex-managed worktrees; Groundwork should add safety policy and verification around its use, not redefine the mechanism.

### Confirmed Decisions

- v0.4.0 should deprecate conflicting v0.3.3 adapter/runtime fields first, then remove them only after evals and docs show the native alignment schema fully preserves the old safety intent.
- The required real Local to Worktree and Worktree to Local handoff trials are v0.4.0 promotion/release blockers, not blockers for merging the initial docs and schema changes.
- Groundwork should provide both a root `.worktreeinclude.example` for discoverability and a `docs/worktreeinclude-safety.md` maintainer note for the safety policy and `verify` lens.
- Public README positioning does not need to be updated in the first contract/schema PR. It belongs in the docs positioning and release-gate slice unless an implementation issue explicitly expands scope.

### Open Implementation Questions

- Which v0.3.3 adapter files should be deprecated in place, slimmed, renamed, or removed after the native alignment contracts exist?
- Should `codex_app_managed_worktree_thread` remain as the legacy adapter name during v0.4.0, or should implementation introduce a new native-alignment package name and migration map?
- Which runtime identity fields remain as evidence references, and which become `availability` markers when Codex-native IDs or paths are unavailable in the current surface?
- Which closeout and dispatch fixtures are compatibility fixtures versus new native-alignment fixtures?

### Needs Confirmation

- None for PRD direction. The open questions above are implementation-slicing questions and must be resolved before removal or migration of v0.3.3 adapter files.

## 3. Executive Summary

v0.3.3 made Groundwork managed worktree execution safer by adding lifecycle, closeout, review, merge-back, branch-cleanup, and runtime identity contracts. That solved important coordination gaps, but it also expanded Groundwork toward execution-layer protocol ownership.

v0.4.0 should reverse that pressure. Groundwork should not become a second worktree runtime. It should become the governance layer around Codex-native worktrees and handoffs:

```text
Groundwork decides:
  route, risk, evidence, handoff package, closeout gate, eval expectations

Codex-native runtime owns:
  worktree creation, thread execution, worktree lifecycle, native handoff mechanics
```

The product outcome is a smaller, more explicit contract:

- decide whether a task belongs in local direct work, local artifact work, isolated worktree work, review-only worktree context, or automation candidacy;
- preserve enough handoff context for Local to Worktree and Worktree to Local transitions without inventing unavailable native IDs or paths;
- protect ignored local files through `.worktreeinclude` guidance without copying secrets into committed examples;
- make merge recommendations impossible when evidence, git boundary, merge source, or review status is missing;
- separate merge readiness from archive, worktree retention, and branch cleanup decisions;
- remove or deprecate custom runtime states that duplicate Codex-native semantics.

## 4. Problem Statement

Groundwork currently contains strong managed-worktree safety contracts, but those contracts risk becoming a parallel runtime model. If Groundwork continues to own worktree thread identity, lifecycle states, handoff mechanics, background run assumptions, and closeout progression as first-class execution protocol, it duplicates Codex-native responsibilities and increases maintenance cost.

The core problem is not whether worktrees are useful. The problem is ownership:

- Codex should own worktree runtime behavior.
- Groundwork should own governance around when and how to use worktrees safely.
- Handoff should be a compact, redacted, self-contained transfer package, not hidden parent-session memory.
- Closeout should decide whether the result can merge, hold, archive, retain, or remain blocked based on evidence.

## 5. Goals

1. Align Groundwork worktree flow with Codex-native worktree and handoff semantics.
2. Let users move safely from Local to Worktree and from Worktree to Local without relying on hidden parent-session history, while recognizing that Codex Handoff owns the Git operations.
3. Provide `.worktreeinclude` safety guidance for ignored files that Codex may copy into local managed worktrees but that must not be staged or committed accidentally.
4. Shrink `dispatch` to route decisions, package schemas, policy, artifact paths, and expected closeout contracts.
5. Make closeout packages structurally checkable by `verify` and evals.
6. Preserve v0.3.3 safety intent while removing or deprecating custom states that conflict with native Codex ownership.
7. Define a release-evidence claim boundary so docs/schema changes cannot imply runtime/cache/release readiness.

## 6. Non-Goals

v0.4.0 must not:

- wrap, simulate, or automate the Codex App worktree UI;
- automatically execute Codex App tools;
- create default automatic subagents;
- stage or commit `.env`, secrets, browser cookies, private tokens, production data, PII, or local runtime scratch;
- implement automation scheduling;
- claim runtime, release, UAT, marketplace, or cache-refresh readiness from local docs or schema changes alone;
- add new public Groundwork skills unless a separate accepted issue explicitly expands the public skill surface.

## 7. Users and Actors

- Developer: needs a route decision that says whether the current task should remain local or move to an isolated worktree.
- Handoff recipient: needs enough redacted context to continue from Local to Worktree or Worktree to Local without reading hidden parent history.
- Maintainer: needs a closeout package that blocks unsafe merge recommendations and separates archive, cleanup, and release readiness.
- Dispatch reviewer: needs a smaller route contract that does not pretend Groundwork owns runtime execution.
- Runtime adapter author: needs clear boundaries for what Codex-native runtime evidence must provide back to Groundwork.

## 8. Functional Requirements

### FR-401 Worktree Route Policy

Add a route policy that chooses the lightest safe execution topology.

Required route enum:

```text
local_direct
local_with_artifact
worktree_isolated
worktree_review_only
automation_candidate
```

Route definitions:

| Route | Use When | Must Not Claim |
| --- | --- | --- |
| `local_direct` | Small, low-risk work can run in the current workspace with clear git boundary. | Worktree isolation, runtime execution, or background handoff. |
| `local_with_artifact` | Durable PRD, issue map, plan, verify report, or handoff artifact is needed but isolated execution is not. | Isolated runtime safety. |
| `worktree_isolated` | Concrete write work benefits from filesystem isolation, clean diff boundaries, dirty-workspace separation, stale-base control, or parallelizable implementation. | That Codex App worktree creation happened without runtime evidence. |
| `worktree_review_only` | A returned or external worktree result needs read-only inspection, clean review, or merge-readiness evaluation. | That review can mutate files or that reviewed work is merged. |
| `automation_candidate` | Recurring monitoring, reminders, scheduled checks, or wakeups may be useful. | Automation creation, unless the user separately approves and the automation tool executes. |

Every route decision must include enough explicit inputs for evals to distinguish low-risk local work from worktree-worthy isolation:

```yaml
route_decision:
  route: local_direct | local_with_artifact | worktree_isolated | worktree_review_only | automation_candidate
  reason: ""
  why_not_worktree: ""
  why_worktree_if_selected: ""
  expected_touched_files: []
  workspace_state:
    current_branch: ""
    dirty_files: []
    unrelated_dirty_files: []
    staged_files: []
    untracked_files: []
    status_checked: true | false
  base_state:
    base_ref: ""
    base_commit: ""
    base_stale: true | false | unknown
    base_refresh_required: true | false | unknown
  conflict:
    conflict_group: ""
    shared_files: []
    serial_dependency: none | blocked_until_merge | human_decision
  runtime_surface:
    codex_app_worktree_available: true | false | unknown
    local_environment_required: true | false | unknown
    automation_surface_available: true | false | unknown
  risk:
    git_write: true | false
    remote_write: true | false
    destructive: true | false
    secrets_or_pii: true | false
    customer_visible: true | false
  setup_requirements: []
  required_local_files: []
  rollback_or_archive_path: ""
  evidence_required_before_closeout: []
```

Policy rules:

- Read-only review and planning-only work must not route to `worktree_isolated`.
- Concrete write work may route to `worktree_isolated` only when scope, intended files, acceptance criteria, and verification expectations are known enough to hand off.
- Dirty workspace, unrelated staged files, stale base, shared-file conflict, or serial dependency can justify `worktree_isolated`, but the route decision must name the concrete input that changed the route.
- Hybrid work must split before the write portion can select `worktree_isolated`.
- `automation_candidate` is only a recommendation until a separate automation tool action is requested and approved.

### FR-402 `.worktreeinclude` Guidance

Add root `.worktreeinclude.example` and `docs/worktreeinclude-safety.md` for ignored local files that may be needed when a local Codex-managed worktree starts from a Git checkout.

Official alignment:

- `.worktreeinclude` lives at repository root.
- It lists ignored paths or `.gitignore`-style patterns that Codex copies when creating a local managed worktree.
- It applies to local Codex app managed worktrees, not remote worktrees or command-line Git worktrees created outside Codex.
- It should not list tracked files.
- Codex skips source symlinks and does not overwrite files already present in the new checkout.
- Ignored `AGENTS.override.md` is copied automatically and does not need to be listed.

Allowed categories for committed Groundwork examples:

- environment sample files with no secrets;
- local runtime config templates with placeholders only;
- fixture cache or generated reference data that is non-sensitive, bounded, and needed for deterministic local checks;
- repo-specific tool config that is ignored locally but safe to copy when redacted.

Project-owner-only categories for private, local `.worktreeinclude` files:

- ignored environment files needed for local execution, only when the project owner intentionally accepts the local-copy risk;
- secret-bearing ignored files that official Codex documentation permits a project to copy locally, but that Groundwork must not place in committed examples.

Forbidden categories for Groundwork examples and default recommendations:

- tokens, API keys, passwords, private keys, browser cookies, auth sessions, or credential stores;
- customer PII, production data dumps, private request payloads, sensitive logs, or screenshots with sensitive data;
- large generated caches that are not required for scoped verification;
- runtime scratch such as `.groundwork`, `.trellis`, build outputs, and temporary test artifacts unless an accepted issue explicitly creates a redacted fixture.

> [!WARNING]
> Official Codex documentation allows `.worktreeinclude` to copy ignored files such as `.env`, `.env.local`, or `config/secrets.json` into local managed worktrees when the project needs them. Groundwork committed examples must not include those real secret-bearing paths by default. If a project deliberately lists secret-bearing ignored files in its private local `.worktreeinclude`, `verify` must treat that as a local runtime risk, ensure the file remains unstaged/uncommitted unless explicitly approved, and report the redaction boundary.

Root example shape:

```text
# .worktreeinclude.example
# Copy this file to .worktreeinclude only after reviewing every line.
# Do not stage or commit .worktreeinclude if it names private local files.
# Do not add cookies, credential stores, PII, private logs, real secrets, or large generated caches.

# Safe placeholder examples:
.env.example
config/local.example.json
fixtures/cache/redacted-smoke-fixture.json

# Forbidden examples for committed Groundwork templates:
# .env
# .env.local
# config/secrets.json
# **/cookies*
# **/*token*
# .groundwork/
# .trellis/
```

`docs/worktreeinclude-safety.md` must separately explain that official Codex docs allow project-owner-only paths such as `.env`, `.env.local`, or `config/secrets.json`, but Groundwork examples are conservative because committed examples should not normalize secret-bearing path names.

`verify` must gain a worktreeinclude safety lens that checks:

- whether example entries are safe placeholders;
- whether forbidden patterns are documented;
- whether any real secrets or sensitive values are exposed in committed examples or artifacts;
- whether `.worktreeinclude` itself names private local files that should remain unstaged and uncommitted;
- whether ignored runtime scratch is excluded from git boundary and staging guidance.

### FR-403 Native Handoff Package

Define a compact handoff package that supports both directions:

- Local to Worktree: hand a prepared task from the current workspace into a Codex-native worktree.
- Worktree to Local: hand a completed, partial, blocked, or abandoned worktree result back to the local coordinator.

Required shape:

```yaml
native_handoff_package:
  direction: local_to_worktree | worktree_to_local
  goal: ""
  scope: []
  out_of_scope: []
  base:
    base_ref: ""
    base_commit: ""
    branch: ""
  native_context:
    thread_ref:
      value: ""
      availability: visible | unavailable_before_handoff | unavailable_in_current_surface | redacted
    worktree_path:
      value: ""
      availability: visible | unavailable_before_handoff | unavailable_in_current_surface | redacted
    worktree_association:
      value: ""
      availability: visible | unavailable_before_handoff | unavailable_in_current_surface | redacted
  route_decision_ref: ""
  relevant_artifacts: []
  changed_files: []
  evidence:
    commands_run: []
    checks_passed: []
    checks_failed: []
    not_run: []
  open_risks: []
  next_command: ""
  stop_condition: ""
  redaction_notes: ""
```

Rules:

- A handoff package must be self-contained enough for a new session to continue without reading hidden parent-session history.
- The package must not claim to perform Handoff; official Codex Handoff owns moving the thread and code between Local and Worktree.
- It must cite canonical artifacts instead of copying full PRDs, full issue bodies, long diffs, logs, or transcripts.
- It must state redaction notes even when no sensitive data was present.
- It must not ask the next reader to stage with `git add .`.
- For Local to Worktree before Codex creates or exposes the worktree, `native_context.worktree_path.availability` must be `unavailable_before_handoff`, not a blank invented path.
- For Worktree to Local, `changed_files`, evidence, open risks, stop condition, and any visible native context are required before any closeout decision.
- Because Codex can return a handed-off thread to the same associated worktree later, package identity should reference the thread/worktree association when visible, but must not invent native IDs when they are unavailable.

### FR-404 Closeout Contract

Replace broad lifecycle progression with a native closeout contract focused on verdict, merge decision, evidence, git boundary, review status, and cleanup decision.

Required shape:

```yaml
native_closeout_package:
  task_verdict: done | partial | blocked | abandoned
  evidence_summary: []
  git_boundary_status:
    status_checked: true | false
    intended_files: []
    unrelated_dirty_files: []
    staged_files: []
    explicit_denylist: []
    safe_to_stage_or_merge: true | false
  review_findings_status: passed | findings_open | not_run | not_required
  merge_decision:
    recommendation: merge | do_not_merge | hold | not_applicable | human_decision
    reason: ""
    merge_source: patch_bundle | visible_branch | codex_handoff | pathspec_checkout | none | unknown
  cleanup_decision:
    thread_action: archive_thread | retain_thread | human_decision | not_applicable
    worktree_action: retain_worktree | allow_codex_managed_cleanup | human_decision | not_applicable
    branch_action: delete_local_branch | retain_branch | human_decision | not_applicable
  blockers: []
  next_route: verify | triage | handoff | done | human_decision
```

Hard gates:

- `merge_decision.recommendation: merge` is forbidden when evidence summary is empty.
- `merge_decision.recommendation: merge` is forbidden when `git_boundary_status.safe_to_stage_or_merge` is not `true`.
- `merge_decision.recommendation: merge` is forbidden when review findings are open, unless the package explicitly routes to human decision and does not claim readiness.
- `merge_decision.recommendation: merge` is forbidden when `merge_decision.merge_source` is `none` or `unknown`.
- `cleanup_decision.branch_action: delete_local_branch` requires separate branch evidence and must not be inferred from archive readiness.
- `cleanup_decision.thread_action: archive_thread` must not claim the thread was archived unless Codex runtime evidence exists.
- Archive, worktree retention, and branch cleanup are cleanup decisions, not merge recommendations.

### FR-405 Dispatch Runtime Surface Reduction

Shrink dispatch output so it no longer models execution-layer lifecycle details owned by Codex-native runtime.

Keep:

- route decision;
- policy and risk gates;
- source package and redaction status;
- artifact path;
- expected handoff package;
- expected closeout package;
- verification expectations;
- approval requirements.

Deprecate or remove after compatibility review:

- custom lifecycle states that duplicate Codex worktree runtime state;
- Groundwork-owned child thread identity fields when Codex-native evidence can provide the native identifier;
- registry fields that pretend Groundwork is the runtime source of truth;
- selector enforcement claims stronger than "requested" or "adapter-evidenced";
- background-run states not backed by Codex-native runtime evidence.

Slim dispatch schema target:

```yaml
dispatch_native_alignment:
  route_decision: {}
  source_package: {}
  policy:
    remote_writes_allowed: false
    destructive_actions_allowed: false
    approval_required: true | false
  handoff_expected:
    required: true | false
    direction: local_to_worktree | worktree_to_local | not_applicable
    artifact_path: ""
  closeout_expected:
    required: true | false
    merge_gate: evidence_git_boundary_review_and_merge_source_required | not_applicable
  runtime_evidence:
    codex_native_required: true | false
    evidence_owner: codex_runtime | adapter | user_supplied | not_applicable
```

### FR-406 Eval and Fixture Migration

Migrate v0.3.3 lifecycle fixtures into native alignment fixtures without losing safety coverage.

Required fixture classes:

- same task can reasonably route to `local_direct` when low risk and scoped;
- same task can reasonably route to `worktree_isolated` when write risk, parallelism, dirty workspace, stale base, or serial dependency conditions justify isolation;
- `.worktreeinclude.example` safety check passes with placeholders and fails with real-looking secrets or forbidden categories;
- handoff package can resume without parent session history;
- Local to Worktree handoff before native worktree creation marks worktree path availability as `unavailable_before_handoff` instead of inventing a path;
- Worktree to Local handoff with visible native context records that context and required changed-file/evidence/open-risk fields;
- closeout with missing evidence cannot recommend merge;
- closeout with missing git boundary cannot recommend merge;
- closeout with unknown or missing merge source cannot recommend merge;
- dispatch artifact no longer contains Groundwork-owned execution runtime fields that conflict with Codex-native ownership;
- local environment setup requirements are represented as setup evidence or route requirements, not as Groundwork-executed worktree setup.

### FR-407 Documentation and Positioning

Docs must state the new boundary plainly:

> [!IMPORTANT]
> Groundwork does not replace the Codex worktree runtime. Groundwork decides route, policy, evidence, handoff, and closeout gates. Codex-native runtime or an execution-capable adapter owns worktree creation, execution, lifecycle observation, and native operation evidence.

Update candidates:

- `docs/runtime-dispatch-workflow.md`
- `docs/prd-dispatch-runtime-router.md`
- `skills/dispatch/DISPATCH-PACKAGE.md`
- `skills/dispatch/RUNTIME-ADAPTERS.md`
- `skills/handoff/SKILL.md`
- `skills/verify/SKILL.md`
- `evals/scenarios/managed-worktree-lifecycle.md`
- `evals/prompts/dispatch-managed-worktree-lifecycle.csv`

The final implementation issue map should decide exact file edits after inspecting each source file.

### FR-408 Release Evidence Claim Boundary

Define how any runtime, cache, release, UAT, marketplace, or cache-refresh claim must be represented.

Required release evidence claim shape:

```yaml
release_evidence_claim:
  claim_type: runtime | cache | release | uat | marketplace | cache_refresh | not_applicable
  claim: ""
  evidence_status: verified | unverified | not_applicable
  installed_plugin_root: ""
  source_root: ""
  cache_or_source_refresh:
    method: refresh_step | source_equivalence | not_run | not_applicable
    evidence: ""
  run_scope: targeted | full | not_run | not_applicable
  commands_or_trials: []
  limitations: []
```

Rules:

- Documentation and schema edits alone must set runtime/cache/release/UAT/marketplace claims to `unverified` or `not_applicable`.
- A verified runtime or cache claim must name the installed plugin root, source root, refresh step or equivalence evidence, and whether the run was targeted or full.
- Release readiness must not be inferred from PRD acceptance. It requires separate release-gate evidence.
- UAT readiness must not be inferred from handoff or closeout package completeness unless UAT evidence exists.

## 9. Official Documentation Alignment

The v0.4.0 direction is supported by official Codex documentation:

- Worktrees are a Codex App feature for isolated local Git worktrees, not a Groundwork runtime.
- Handoff is a native Codex App flow that moves a thread and code between Local and Worktree while handling the Git operations.
- `.worktreeinclude` is an official repository-root mechanism for copying ignored files into local Codex-managed worktrees.
- Codex-managed worktrees are normally lightweight, dedicated to one thread by default, can be returned to the same associated worktree after Handoff, and are created under `$CODEX_HOME/worktrees`.
- Automations can run on dedicated background worktrees in Git repositories, but scheduling and unattended execution remain Codex automation concerns.
- Local environment setup scripts are the native way to prepare worktrees.
- Subagents are explicitly requested workflows and should not become Groundwork's default worktree behavior.

### Official Docs Reference Map

| Topic | Official doc | Checked date | PRD dependency |
| --- | --- | --- | --- |
| Worktrees, Handoff, `.worktreeinclude` | `https://developers.openai.com/codex/app/worktrees` | 2026-06-18 | FR-401, FR-402, FR-403, FR-404 |
| Local Environments | `https://developers.openai.com/codex/app/local-environments` | 2026-06-18 | FR-401, FR-402, AC-409 |
| Automations | `https://developers.openai.com/codex/app/automations` | 2026-06-18 | `automation_candidate`, release gates |
| Subagents | `https://developers.openai.com/codex/concepts/subagents` | 2026-06-18 | Non-goals, no default subagents |

This confirms the main v0.4.0 product move: Groundwork should define route, policy, redaction, evidence, handoff package, and closeout gates; Codex-native features should own worktree creation, Handoff Git mechanics, worktree retention/deletion, automation scheduling, and subagent orchestration.

## 10. Acceptance Criteria

- AC-401: The same task fixture can produce a defensible `local_direct` route when scope is small and risk is low, and a defensible `worktree_isolated` route when isolation risk, dirty workspace, stale base, serial dependency, or conflict conditions justify it.
- AC-402: Root `.worktreeinclude.example` aligns with official repository-root `.worktreeinclude` semantics, contains no real secrets or sensitive values, includes only safe placeholder examples, documents explicit forbidden categories, and warns against staging or committing cookies, tokens, PII, production data, runtime scratch, or large generated caches.
- AC-403: A native handoff package lets a new session continue from Local to Worktree or Worktree to Local without reading parent-session history, while marking unavailable native thread/worktree fields with explicit `availability` values instead of inventing IDs or paths.
- AC-404: A closeout package that lacks evidence, git boundary, passed review status, or known merge source cannot set `merge_decision.recommendation: merge`.
- AC-405: Dispatch artifacts do not contain Groundwork-owned execution runtime fields that conflict with Codex-native worktree or handoff ownership.
- AC-406: v0.3.3 lifecycle fixture intent is preserved as native alignment fixture coverage.
- AC-407: Docs explicitly state that Groundwork does not replace Codex worktree runtime.
- AC-408: Any runtime/cache/release claim names the installed plugin root, source root, cache/source refresh or equivalence evidence, and whether the run was targeted or full; otherwise the claim remains unverified.
- AC-409: Local environment setup requirements are represented as Codex App local-environment setup expectations or manual setup evidence, not as Groundwork-owned worktree setup execution.

## 11. Metrics

- `worktree_route_precision`: percentage of route fixtures whose route and reason match expected policy.
- `worktree_handoff_success_rate`: percentage of handoff trials where a new session can continue without parent history.
- `closeout_contract_completeness`: percentage of closeout packages with verdict, evidence, git boundary, review status, merge decision, cleanup decision, blockers, and next route.
- `worktreeinclude_safety_violation_count`: number of forbidden or secret-like entries detected in `.worktreeinclude.example` or related fixtures.
- `runtime_protocol_surface_reduction`: count of deprecated or removed Groundwork-owned runtime lifecycle fields versus v0.3.3.
- `merge_gate_false_positive_count`: number of packages that incorrectly recommend merge with missing evidence, git boundary, review status, or merge source.
- `native_context_invention_count`: number of handoff packages that invent unavailable native IDs, thread refs, or worktree paths instead of marking availability.

## 12. Release Gates

- v0.3.3 lifecycle fixtures are migrated or mapped to native alignment schema fixtures.
- At least one documented Local to Worktree handoff trial and one documented Worktree to Local handoff trial complete successfully.
- Each real handoff trial records direction, base ref/commit, available native context, handoff package path, changed files if applicable, evidence, open risks, and closeout result.
- Docs clearly state "Groundwork does not replace Codex worktree runtime."
- Root `.worktreeinclude.example` and `docs/worktreeinclude-safety.md` pass safety review and contain no real secrets or sensitive data.
- Dispatch schema/eval coverage proves that package generation no longer claims runtime execution.
- `verify` can structurally reject closeout packages that recommend merge without evidence, git boundary, review status, or merge source.
- Runtime evidence, if claimed for release, names installed plugin root, source root, cache/source equivalence or supported refresh step, and targeted versus full suite scope.
- Official-doc alignment is rechecked before release if Codex App worktree, Handoff, `.worktreeinclude`, automation, local environment, or subagent docs change.

## 13. Risks and Mitigations

| Risk | Impact | Mitigation |
| --- | --- | --- |
| Removing v0.3.3 fields too quickly breaks existing evals or downstream docs. | Compatibility churn and unclear migration. | Deprecate first, preserve fixture intent, remove only after native fixtures cover the same safety gates. |
| `.worktreeinclude` is misunderstood as a permission to stage or commit ignored files. | Secrets or local runtime files could leak. | Align with official copy semantics, keep committed examples conservative, move secret-bearing path discussion to safety docs, add verify lens, and keep git-boundary denylist explicit. |
| Handoff packages become too large. | They duplicate PRDs, diffs, or logs and stop being usable. | Cite canonical artifacts and summarize only continuation-critical context. |
| Handoff packages invent native context before Codex exposes it. | Future sessions may rely on false thread IDs or worktree paths. | Require explicit native-context availability markers and eval failures for invented IDs/paths. |
| Closeout package claims merge readiness from narrative summary. | Unsafe merge recommendation. | Enforce evidence, git-boundary, review-status, and merge-source gates before `merge`. |
| Archive, worktree cleanup, and branch cleanup are conflated with merge readiness. | Work can be lost or branches can be deleted unsafely. | Keep merge decision and cleanup decision as separate structured fields. |
| Groundwork still implies it created or observed native worktrees. | False runtime readiness claim. | Require runtime evidence owner and explicitly mark package-only outputs as unverified runtime. |

## 14. Suggested Issue Slices

1. Route policy schema and dispatch docs alignment.
2. Root `.worktreeinclude.example`, `docs/worktreeinclude-safety.md`, and safety lens in `verify`.
3. Native handoff package shape and handoff docs update.
4. Native closeout package schema and merge gate checks.
5. Dispatch runtime surface reduction and compatibility/deprecation mapping.
6. Fixture and eval migration from v0.3.3 lifecycle to native alignment.
7. Docs positioning and release gate evidence checklist.
8. Release evidence claim boundary and verification support.

## 15. Next Action

Review and accept or correct this PRD. After acceptance, use `to-issues` to split the eight suggested slices into implementation-ready tasks with file scopes, acceptance criteria, and verification commands.

## 16. Current Verification Plan

For this PRD artifact only:

- run `git diff --check`;
- scan the new document for stale unresolved-state terms and contradictory runtime readiness claims;
- confirm `.worktreeinclude.example` contains only safe placeholder examples and no real secret-bearing paths;
- confirm native handoff unavailable IDs/paths use `availability` markers instead of blank invented values;
- confirm closeout uses split `merge_decision` and `cleanup_decision` fields;
- run broad CSV/plugin JSON checks only if later implementation touches eval CSVs or plugin metadata.
