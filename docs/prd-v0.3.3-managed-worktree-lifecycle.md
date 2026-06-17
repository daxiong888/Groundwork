# PRD v0.3.3: Managed Worktree Lifecycle, Clean Review Fan-out, and Serial Dispatch Closeout

Target Reader: Groundwork maintainers, Codex App managed worktree adapter implementers, dispatch reviewers, and future implementation agents working from the v0.3.2 dispatch runtime router.
Reader Action Needed: Use this PRD to implement the v0.3.3 hardening layer for managed worktree thread lifecycle, review fan-out, merge-back, archive, branch cleanup, stable runtime identity, Goal Mode enforcement, and serial dispatch barriers.
Decision Supported: Whether Groundwork should add lifecycle and closeout protocols behind the existing `dispatch` runtime router without expanding the public skill surface.
Scope: Internal contracts, templates, schemas, checks, docs, and evals that make post-dispatch runtime execution safer and more reviewable.
Out of Scope: New public skills, automatic Codex App tool execution from `dispatch`, default automatic subagent spawning, remote writes, commits, pushes, PR creation, tracker mutation, destructive cleanup without approval, task CRUD, hooks, MCP servers, and marketplace publishing flow.
Evidence Level: Grounded in current v0.3.2 dispatch contracts, `GOAL-CONTRACT.md`, managed worktree adapter templates, runtime dispatch workflow docs, Groundwork lifecycle/git-boundary rules, and user-reported runtime pain points from real Codex App child-thread usage.
Status: Draft for implementation.
Version Target: 0.3.3.
Last Updated: 2026-06-17.

---

## 1. Executive Summary

Groundwork v0.3.2 correctly separates task semantics from runtime execution:

```text
Groundwork dispatch
  = runtime router / package generator

runtime adapters
  = execution-capable consumers of packages, only when explicitly approved and available
```

The remaining pain is not routing. The remaining pain is the lifecycle after a managed worktree child thread has been created.

Real usage now shows seven gaps:

1. Managed worktree child threads need an explicit closeout/ending path. Archiving the Codex App thread destroys the Codex-managed worktree, but temporary branches may remain and are not automatically handled.
2. The main coordinator thread becomes overloaded when it deeply reviews multiple child thread review packages. Repeated context compaction degrades the coordinator's ability to reason.
3. Dependent issues need a serial merge barrier: Issue 2 must often wait until Issue 1 is reviewed, merged back to the main worktree, and the base is refreshed.
4. Merge-back from child worktree to main worktree is inefficient when the agent rewrites changes from a summary instead of applying a reliable patch/checkout source.
5. Child thread names are unstable. They may be renamed by the child/runtime, forcing repeated list/recovery operations.
6. Goal Mode is not enforced strongly enough. A child write task can accidentally run as normal prompt work even when the package intended `/goal`.
7. Complex work should separate planning, implementation, review, verification, and coordination. The same agent should not plan, implement, and final-review complex changes.

v0.3.3 should add an internal runtime lifecycle layer behind `dispatch`:

```text
to-prd
  -> to-issues
  -> triage creates Goal Contract
  -> dispatch creates runtime package
  -> managed worktree adapter executes only if approved and supported
  -> child returns review_package
  -> clean reviewer / review subagent reviews from fresh context
  -> merge-back protocol applies verified changes to main worktree
  -> verify checks evidence sufficiency
  -> triage records next state / closeout
  -> adapter archives child thread when safe
  -> branch cleanup checklist handles temporary branches separately
```

The key product decision: **do not add a new public skill.** Add internal adapter contracts, shared result fields, templates, and evals that make the existing `dispatch` architecture operationally complete.

---

## 2. Current Source Basis

Current v0.3.2 sources already establish the correct boundaries:

- `.codex-plugin/plugin.json` declares Groundwork version `0.3.2` and describes the plugin as a Codex-native personal R&D workflow base for PRD, task slicing, planning, prototypes, implementation, verification, and handoff.
- `README.md` says current main contains the hardened public skill surface and that `dispatch` is the ninth public skill. It also states that Groundwork currently does not contain task tools, hooks, MCP servers, marketplace publishing flow, or local task CRUD.
- `docs/prd-dispatch-runtime-router.md` defines `dispatch` as a runtime router / execution planner / adapter package generator and keeps runtime execution outside Groundwork dispatch.
- `skills/dispatch/SKILL.md` says dispatch must classify tasks, select runtime routes, generate Dispatch Package v2, define Result Package expectations, and stop before execution unless explicit execution approval and tools are available.
- `skills/dispatch/RUNTIME-ADAPTERS.md` defines `codex_app_managed_worktree_thread`, `codex_subagent`, `main_thread_direct`, `main_thread_readonly`, and `clean_reviewer` capability profiles.
- `skills/dispatch/RESULT-PACKAGE.md` defines the unified result envelope for `review_package`, `findings_package`, `diagnosis_package`, `direct_result`, and `review_findings`.
- `skills/dispatch/adapters/codex_app_managed_worktree_thread/` already contains the internal managed worktree adapter contract, dispatch package contract, child prompt template, review package template, result package template, reject/no-op checklist, selector enforcement reference, and rationale.
- `skills/_shared/GOAL-CONTRACT.md` requires a complete executable `/goal` contract for ready implementation tasks.
- `skills/_shared/GIT-BOUNDARY.md` requires explicit pathspec staging and forbids `git add .`.
- `docs/runtime-dispatch-workflow.md` defines the end-to-end `to-prd -> to-issues -> triage -> dispatch -> runtime adapter -> verify/triage` workflow.

v0.3.3 should extend these files; it should not replace the v0.3.2 architecture.

---

## 3. Problem Statement

### 3.1 Closeout gap for managed worktree child threads

Managed worktree threads create isolated worktrees. When a child thread is archived in Codex App, the app may remove its managed worktree. But Groundwork currently has no explicit protocol for when a thread is safe to archive, whether its review package has been preserved, whether its work has been merged or discarded, and whether any temporary branch remains.

Without this lifecycle, a coordinator can accidentally:

- leave worktrees alive indefinitely;
- archive a thread before the review package is complete;
- lose the child worktree before merge-back is complete;
- forget temporary branches;
- conflate thread archive with branch cleanup.

### 3.2 Coordinator review overload

A main thread can create multiple child threads, but today the main thread often performs the full review of every returned review package. This makes the coordinator read large diffs, summaries, validation transcripts, and risk sections repeatedly. After context compaction, the coordinator becomes a weaker reviewer and a weaker router.

The coordinator should intake and route result packages, not deeply review every package itself.

### 3.3 Serial dependency and stale base problem

Many issues are not independent. A later issue may require the first issue's changed source, updated tests, new contract, or new generated artifact. Dispatch can currently mark conflict groups and merge-order hints, but it lacks a stronger `blocked_until_merge` barrier.

Dependent write work must not be dispatched from a stale base.

### 3.4 Inefficient merge-back

A review package is enough for clean review but not always enough for reliable merge-back. If the main thread only has a redacted diff summary or prose, the agent may rewrite changes manually into the main worktree, producing drift and extra risk.

Merge-back needs a reliable source strategy:

- Codex App checkout/apply changes;
- full patch bundle;
- visible child branch/head;
- pathspec checkout;
- manual review-only fallback when no reliable merge source exists.

### 3.5 Unstable child thread titles

Child thread names are display fields, not identity. If a child thread renames itself or the runtime changes the title, the coordinator must not lose the mapping between task, dispatch package, child runtime, review package, merge-back source, and closeout.

### 3.6 Weak Goal Mode enforcement

The v0.3.2 child prompt template places `goal_contract.goal_command` first and states that the coordinator does not enter Goal Mode. But this is still mostly prompt-level. v0.3.3 needs static lint and runtime evidence:

- the first non-empty child prompt line must start with `/goal`;
- the Goal Contract must have no placeholders;
- child result must report Goal Mode evidence when required;
- missing Goal Mode evidence cannot be `ready_for_review`.

### 3.7 Planner / implementer / reviewer collapse

For complex work, the same agent should not be trusted to plan, implement, and final-review its own change. Child implementation threads may self-check, but self-check is implementation evidence, not clean-review approval.

Complex work requires role separation:

```text
planner -> implementer -> clean reviewer -> verifier -> coordinator closeout
```

---

## 4. Product Goal

v0.3.3 should make managed worktree thread execution operationally safe by adding lifecycle protocols that preserve evidence, reduce coordinator overload, enforce serial dependencies, support reliable merge-back, and close child runtime resources intentionally.

Primary goals:

1. **Safe closeout**: a managed worktree child thread can be archived only after review evidence is collected and merge/discard decisions are complete.
2. **Branch clarity**: branch cleanup is separate from thread archive and requires its own checklist and approval gates.
3. **Fresh review**: completed child packages route to `clean_reviewer` or read-only `codex_subagent` for fresh-context review when review complexity exceeds coordinator intake.
4. **Serial correctness**: dependent write tasks remain blocked until prerequisite merge-back and base refresh are complete.
5. **Reliable merge-back**: the main worktree should apply changes from a reliable merge source, not rewrite from prose.
6. **Stable identity**: runtime correlation IDs, not thread titles, identify child runtime work.
7. **Hard Goal Mode**: executable child write tasks require static Goal Contract lint and runtime Goal Mode evidence.
8. **Complex work separation**: planning, implementation, clean review, verification, and coordination must be separable roles for nontrivial changes.

---

## 5. Non-Goals

v0.3.3 must not:

- add a public `archive`, `review`, `merge`, `cleanup`, or `lifecycle` skill;
- make `dispatch` execute Codex App thread tools;
- automatically spawn subagents by default;
- automatically create, archive, delete, commit, push, open PRs, close issues, or mutate trackers from package generation;
- treat `review_package` as a reliable merge source when only redacted or partial evidence is available;
- silently delete local or remote branches;
- claim Goal Mode, validation, merge-back, branch cleanup, or archive happened without adapter/runtime evidence;
- create project-global lifecycle state or a task database;
- replace `verify` or `triage` with adapter status.

---

## 6. Design Principles

### 6.1 Dispatch remains package-only

`dispatch` decides route, isolation, conflict groups, dependency barriers, execution profile, and expected result package. It does not execute.

### 6.2 Runtime adapters own execution evidence

Only an execution-capable adapter may report:

- child thread created;
- managed worktree created;
- prompt delivered;
- Goal Mode observed;
- validation run;
- merge-back attempted;
- archive completed;
- branch cleanup completed.

### 6.3 Archive is not branch cleanup

Archiving a thread may remove the Codex-managed worktree, but it must not be treated as proof that temporary branches are gone or safe to delete.

### 6.4 Review package is not merge source

A review package is source for review. Merge-back requires a complete patch, checkout/apply support, visible child branch/head, or other reliable source. A redacted partial patch is not mergeable.

### 6.5 Thread title is not identity

Every runtime package, child prompt, review package, result package, merge-back package, closeout package, and branch cleanup package must carry a stable `runtime_correlation_id`.

### 6.6 Coordinator does not become the reviewer of record

The coordinator may perform intake checks. Clean review should run as `clean_reviewer` or read-only `codex_subagent` when package size, risk, or parallel volume justifies fresh context.

### 6.7 Child implementer is not clean reviewer

A child implementation thread may self-check but must not output `review_passed`. Only the coordinator after clean review and verification may route closeout.

---

## 7. Proposed Architecture

```text
Layer 1 · Product Intent
  to-prd -> accepted source truth

Layer 2 · Task Slicing
  to-issues -> vertical work units with dependency/parallel candidates

Layer 3 · Readiness + Goal Contract
  triage -> ready-for-agent + Goal Contract + Preferred Runtime

Layer 4 · Dispatch
  dispatch -> Dispatch Package v2 + runtime lifecycle fields

Layer 5 · Execution-capable Runtime Adapter
  codex_app_managed_worktree_thread adapter
    -> child thread creation if approved and supported
    -> child prompt delivery
    -> result/review package collection
    -> selector/Goal Mode evidence
    -> lifecycle status

Layer 6 · Fresh Review
  clean_reviewer or codex_subagent
    -> review_findings / findings_package

Layer 7 · Merge Barrier
  merge-back protocol
    -> apply reliable changes to main worktree
    -> refresh base
    -> verify

Layer 8 · Closeout
  triage closeout decision
    -> archive-ready decision
    -> thread archive
    -> branch cleanup checklist
```

---

## 8. Functional Requirements

## FR-1: Add Managed Worktree Thread Lifecycle Protocol

### Required File

```text
skills/dispatch/adapters/codex_app_managed_worktree_thread/THREAD-LIFECYCLE.md
```

### Lifecycle States

```text
package_admitted
child_thread_created
prompt_delivered
running
review_package_returned
clean_review_pending
clean_review_passed
needs_remediation
blocked
merge_pending
discard_pending
merged_to_main_worktree
discarded
archive_ready
archived
branch_cleanup_pending
branch_cleaned
branch_retained_with_reason
closed
```

### Rules

- A child thread must not archive itself.
- A child thread must not delete branches.
- A child thread must not stage, commit, push, open PRs, close issues, mutate trackers, or change remote state unless separately approved.
- `archive_ready` is allowed only after one of:
  - `merged_to_main_worktree` with evidence;
  - `discarded` with reason;
  - `blocked` with preserved review/result evidence and a human decision that worktree retention is not needed.
- `review_package_returned` is not enough for `archive_ready`.
- `clean_review_pending` is not enough for `archive_ready`.
- `needs_remediation` is not enough for `archive_ready` unless remediation is explicitly moved to a new task and the current child worktree is intentionally discarded.
- `archived` does not imply `branch_cleaned`.

### Acceptance Criteria

- AC-1.1: Adapter docs define the lifecycle states and legal transitions.
- AC-1.2: Review/result templates expose lifecycle status.
- AC-1.3: A managed worktree result cannot recommend archive before merge/discard/blocked-with-decision.
- AC-1.4: Evals reject child prompts or results that ask the child to archive itself.

---

## FR-2: Add Closeout Package Template

### Required File

```text
skills/dispatch/adapters/codex_app_managed_worktree_thread/CLOSEOUT-PACKAGE-TEMPLATE.md
```

### Required Shape

```yaml
closeout_package:
  runtime_correlation_id: ""
  task_id: ""
  runtime_id: "codex_app_managed_worktree_thread"

  lifecycle:
    current_state: ""
    closeout_decision: archive | retain | discard | blocked | human_decision
    closeout_reason: ""
    archive_ready: true | false
    archive_blockers: []
    preserved_evidence:
      review_package: present | absent | incomplete
      result_package: present | absent | incomplete
      clean_review: passed | failed | not_run | not_applicable
      merge_back: completed | not_attempted | failed | not_applicable

  runtime:
    thread_identifier: ""
    initial_thread_title: ""
    current_thread_title: ""
    worktree_type: Codex-managed | none | unknown
    worktree_path: ""

  approval:
    archive_approval_required: true | false
    archive_approval_status: approved | not_requested | rejected | not_required
    reason: ""

  next:
    branch_cleanup_required: true | false | unknown
    recommended_next_route: branch_cleanup | triage | verify | done | human_decision
```

### Rules

- Closeout package is created after review/result package intake, not before.
- Closeout package must name preserved evidence before archive.
- `archive_approval_required` is `true` when the runtime operation is not already explicitly approved by the user or adapter policy.
- Closeout package may recommend archive but must not claim archive occurred unless adapter evidence exists.

### Acceptance Criteria

- AC-2.1: Closeout template includes lifecycle, preserved evidence, runtime identity, approval, and next route.
- AC-2.2: Archive-ready recommendations require review/result package evidence.
- AC-2.3: Archive and branch cleanup are separate fields.

---

## FR-3: Add Branch Cleanup Checklist

### Required File

```text
skills/dispatch/adapters/codex_app_managed_worktree_thread/BRANCH-CLEANUP-CHECKLIST.md
```

### Required Shape

```yaml
branch_cleanup:
  runtime_correlation_id: ""
  task_id: ""
  branch_detected: true | false | unknown
  branch_name: ""
  branch_scope: local | remote | both | unknown
  branch_created_by_child: true | false | unknown
  branch_checked_out_in_worktree: true | false | unknown
  branch_points_to_head: true | false | unknown
  merged_to_target: true | false | unknown
  protected_or_default_branch: true | false | unknown
  cleanup_recommendation: delete_local | delete_remote | retain | human_decision | no_branch_detected
  approval_required: true | false
  evidence:
    status_command: ""
    branch_command: ""
    merge_check: ""
  risk:
    reason_to_retain: ""
    blockers: []
```

### Rules

- Branch cleanup is never inferred from thread archive.
- Unknown branch state must route to `human_decision` or `retain`.
- Remote branch deletion always requires explicit approval.
- Force deletion requires explicit human decision.
- Protected/default/base branches must never be deleted.
- Local delete is recommended only when evidence shows the branch is local, task-scoped, not checked out, not protected/default/base, and merged or intentionally discarded.

### Acceptance Criteria

- AC-3.1: Checklist separates local and remote branch cleanup.
- AC-3.2: Checklist blocks deletion of unknown, unmerged, protected, default, or remote branches without explicit approval.
- AC-3.3: Evals cover archive-with-leftover-temp-branch and unknown-branch-state cases.

---

## FR-4: Add Merge-back Protocol

### Required File

```text
skills/dispatch/adapters/codex_app_managed_worktree_thread/MERGE-BACK-PROTOCOL.md
```

### Merge-back Strategies

Use this priority order:

```text
1. Codex App checkout/apply changes to local main worktree, when runtime supports it and evidence is available.
2. Complete patch bundle from child worktree, applied with pathspec / three-way support when safe.
3. Visible child branch or head commit, merged or checked out by explicit pathspec.
4. Manual review-only fallback when merge source is unavailable or incomplete.
```

### Required Shape

```yaml
merge_back:
  runtime_correlation_id: ""
  task_id: ""
  source:
    base_branch: ""
    base_commit: ""
    child_head_commit: ""
    child_branch: ""
    worktree_path: ""
    patch_bundle_path: ""
    patch_completeness: complete | redacted_complete | redacted_partial | unavailable

  strategy:
    selected: codex_checkout | git_apply_patch | git_merge_branch | git_checkout_pathspec | manual_review_only
    reason: ""
    approval_required: true | false

  preconditions:
    main_worktree_status_checked: true | false
    main_worktree_clean_enough: true | false | unknown
    base_matches: true | false | unknown
    intended_pathspecs: []
    denylist_checked: true | false
    conflicts_expected: true | false | unknown

  result:
    attempted: true | false
    applied: true | false | not_attempted
    conflicts_detected: true | false | unknown
    validation_required: true | false
    evidence: ""
    next_route: verify | triage | human_decision | blocked
```

### Rules

- Redacted partial patch must not be used for merge-back.
- Review package prose must not be used to rewrite changes manually into the main worktree.
- `git add .` must not be recommended or approved.
- Merge-back requires git boundary evidence when file changes enter the main worktree.
- Base commit mismatch must block automatic merge-back and route to human decision or rebase/merge plan.
- After merge-back, fastest relevant validation must run or be explicitly marked unverified.

### Acceptance Criteria

- AC-4.1: Merge-back protocol defines source, strategy, preconditions, result, and next route.
- AC-4.2: Evals reject manual rewrite from review package summary.
- AC-4.3: Evals reject merge-back from redacted partial patch.
- AC-4.4: Evals require git boundary before staging/commit-related review.

---

## FR-5: Add Stable Runtime Identity

### Required Updates

Update:

```text
skills/dispatch/DISPATCH-PACKAGE.md
skills/dispatch/RESULT-PACKAGE.md
skills/dispatch/adapters/codex_app_managed_worktree_thread/THREAD-PROMPT-TEMPLATE.md
skills/dispatch/adapters/codex_app_managed_worktree_thread/REVIEW-PACKAGE-TEMPLATE.md
skills/dispatch/adapters/codex_app_managed_worktree_thread/RESULT-PACKAGE-TEMPLATE.md
```

### Required Shape

```yaml
runtime_identity:
  runtime_correlation_id: "gw:<workstream>:<task_id>:<dispatch_seq>:<short_hash>"
  dispatch_id: ""
  task_id: ""
  parent_thread_identifier: ""
  child_thread_identifier: ""
  initial_thread_title: ""
  current_thread_title: ""
  title_mutation_detected: true | false | unknown
```

### Rules

- `runtime_correlation_id` is required for managed worktree packages.
- Thread title is display-only and must not be the primary identity.
- The child prompt must include the runtime correlation ID in the first identity block after `/goal`.
- The child review package and adapter result package must echo the runtime correlation ID.
- If the visible title changes, the adapter reports `title_mutation_detected` and continues correlation by ID.

### Acceptance Criteria

- AC-5.1: Dispatch package, child prompt, review package, result package, closeout package, merge-back package, and branch cleanup package all carry `runtime_correlation_id`.
- AC-5.2: Evals simulate child thread title mutation and still require successful correlation.
- AC-5.3: No protocol uses title as the source-of-truth identifier.

---

## FR-6: Harden Goal Mode Enforcement

### Required Updates

Update:

```text
skills/_shared/GOAL-CONTRACT.md
skills/dispatch/adapters/codex_app_managed_worktree_thread/THREAD-PROMPT-TEMPLATE.md
skills/dispatch/adapters/codex_app_managed_worktree_thread/DISPATCH-PACKAGE-CONTRACT.md
skills/dispatch/adapters/codex_app_managed_worktree_thread/RESULT-PACKAGE-TEMPLATE.md
scripts/lint_goal_contract.py
```

Add optional script if needed:

```text
scripts/lint_child_goal_prompt.py
```

### Hard Rules

- For managed worktree implementation packages, the first non-empty line of the child prompt must start with `/goal`.
- Do not wrap `/goal` in a fenced code block.
- Do not prepend prose before `/goal`.
- Do not use placeholder goal text such as `/goal <one executable task>`.
- Goal Contract lint must pass before a managed worktree child package is admissible.
- Child result must include `goal_mode_evidence` when the package required Goal Mode.
- Missing Goal Mode evidence means the result must be `blocked` or `needs_remediation`, not `ready_for_review`.
- Adapter may attempt one corrective resend only if explicitly supported; otherwise stop and report the failure.

### Required Result Field

```yaml
goal_mode:
  required: true | false
  goal_command_first_line: true | false | unknown
  lint_passed_before_delivery: true | false | unknown
  runtime_goal_mode_evidence: present | absent | unavailable | unknown
  evidence: ""
  failure_action: none | corrective_resend | blocked | needs_remediation
```

### Acceptance Criteria

- AC-6.1: Child prompt template makes `/goal` the first non-empty line.
- AC-6.2: Linter rejects placeholder Goal Contract fields and non-leading `/goal` prompts.
- AC-6.3: Result template blocks `ready_for_review` without Goal Mode evidence when required.
- AC-6.4: Evals cover normal prompt execution accidentally replacing Goal Mode.

---

## FR-7: Add Clean Review Fan-out Protocol

### Required Files

```text
skills/dispatch/CLEAN-REVIEW-FANOUT.md
skills/dispatch/adapters/codex_app_managed_worktree_thread/CLEAN-REVIEW-PACKAGE-TEMPLATE.md
```

### Routing Rules

Use clean review fan-out when any of these are true:

- multiple child review packages return to one coordinator;
- review package is large enough to risk coordinator context overload;
- changed files include public interfaces, schema, migration, generated artifacts, shared fixtures, state machines, or shared config;
- task is P0/P1 or high-risk;
- validation was skipped, failed, or only partially run;
- child performed validation-fix iterations;
- user asks for independent review;
- coordinator context has compacted or is managing multiple concurrent returns.

### Runtime Choice

```text
clean_reviewer
  best for: review_package inspection, diff conformance, product/security/QA lens, no edits

codex_subagent
  best for: read-only multi-perspective review, independent diagnosis, findings package, no edits by default

main_thread_readonly
  best for: low-cost coordinator intake and decision support, not full diff review
```

### Clean Review Package Shape

```yaml
clean_review_package:
  runtime_correlation_id: ""
  task_id: ""
  review_lens: product | spec | code_quality | security | qa | contract | git_boundary | evidence
  source:
    review_package: ""
    result_package: ""
    source_truth: ""
    acceptance_criteria: ""
    changed_files: []
    validation_evidence: ""
  allowed_actions:
    read_only: true
    file_edits_allowed: false
    spawn_more_agents_allowed: false
  output_required:
    output_type: review_findings
    severity_order: P0_P1_P2_P3
    cite_paths_or_package_sections: true
```

### Rules

- Reviewer must receive fresh context and must not rely on parent session memory.
- Reviewer must not modify files unless explicitly delegated, approved, and routed as a write task.
- Reviewer must not spawn more agents unless explicitly delegated.
- Reviewer must mark missing evidence as `unverified` or `blocked`.
- Child implementation self-review does not count as clean review.

### Acceptance Criteria

- AC-7.1: Clean review fan-out rules are documented and referenced from runtime dispatch workflow.
- AC-7.2: Package template supports review lens and read-only allowed actions.
- AC-7.3: Evals show main thread doing intake only and routing large/multiple packages to clean reviewer.
- AC-7.4: Evals reject clean reviewer outputs that edit files or rely on hidden parent context.

---

## FR-8: Add Serial Dispatch / Merge Barrier

### Required Updates

Update:

```text
skills/dispatch/DISPATCH-PACKAGE.md
skills/dispatch/CONFLICT-PREFLIGHT.md
skills/dispatch/ROUTING-PROFILES.md
docs/runtime-dispatch-workflow.md
```

### Required Shape

```yaml
dependency_barrier:
  depends_on_task_ids: []
  blocked_until:
    result_package_status: ready_for_review | not_required
    clean_review: passed | not_required
    merge_back: completed | not_required
    verification: pass | partial_allowed | not_required
    base_refresh: completed | not_required
  required_base:
    branch: ""
    commit_after_merge: ""
  re_triage_required_after_merge: true | false
  dispatch_allowed_now: true | false
  block_reason: ""
```

### Rules

- Dependent write tasks must not dispatch until prerequisite merge-back and base refresh are complete.
- Read-only preparation for future dependent tasks may run before merge-back if it does not assume unmerged code as truth.
- Goal Contracts for dependent write tasks must be generated or refreshed after the prerequisite merge.
- If dependency state is unknown, dispatch must serialize or block instead of parallelizing writes.
- Same conflict group cannot run parallel write work unless explicitly approved and serialized by merge-order hint.

### Acceptance Criteria

- AC-8.1: Dispatch packages can express `blocked_until` merge barriers.
- AC-8.2: Evals reject Issue 2 write dispatch before Issue 1 merge-back.
- AC-8.3: Evals allow read-only preparation while write dispatch remains blocked.
- AC-8.4: Evals require Goal Contract refresh after base-changing merge.

---

## FR-9: Add Complex Work Separation Policy

### Required File

```text
skills/dispatch/COMPLEX-WORK-SEPARATION.md
```

### Trigger Thresholds

Separation is required when any of these are true:

- P0/P1 risk;
- security/privacy/data correctness;
- DB schema, migration, public API, auth, permissions, or contract changes;
- cross-cutting feature or multi-module change;
- generated artifacts, shared fixtures, public interfaces, state machines, shared config;
- dependent issue chain;
- missing or weak validation evidence;
- UAT/release/customer-facing readiness;
- multiple child review packages returning to one coordinator;
- child performed validation-fix iterations;
- coordinator context has compacted or is overloaded.

### Required Role Boundaries

```text
Planner:
  read-only; outputs plan, source truth, AC mapping, risk, split recommendation

Implementer:
  managed worktree write thread; executes exactly one implementation goal; returns review_package

Clean Reviewer:
  fresh context; read-only; returns review_findings; does not edit files

Verifier:
  verify scope-first evidence sufficiency; pass/partial/fail/blocked

Coordinator:
  routes, intakes, decides next route, merge barrier, archive/cleanup decision
```

### Acceptance Criteria

- AC-9.1: Policy lists thresholds that require separation.
- AC-9.2: Evals reject a complex child implementer claiming final review approval.
- AC-9.3: Evals require fresh clean reviewer for P1 / public API / migration changes.
- AC-9.4: Evals allow small low-risk direct work to remain lightweight.

---

## FR-10: Extend Result and Review Package Schemas

### Required Updates

Update:

```text
skills/dispatch/RESULT-PACKAGE.md
skills/dispatch/adapters/codex_app_managed_worktree_thread/REVIEW-PACKAGE-TEMPLATE.md
skills/dispatch/adapters/codex_app_managed_worktree_thread/RESULT-PACKAGE-TEMPLATE.md
```

### Required New Sections

- `runtime_identity`
- `goal_mode`
- `lifecycle`
- `merge_back`
- `branch_cleanup`
- `clean_review`

### Backward Compatibility

Existing v0.3.2 packages remain readable. v0.3.3 fields are required for managed worktree lifecycle closeout but may be absent in older packages; missing fields should route to `needs_remediation`, `blocked`, or `human_decision` when lifecycle closeout is requested.

### Acceptance Criteria

- AC-10.1: Result template includes all new sections.
- AC-10.2: Review package template includes runtime identity, goal evidence, merge source, branch info, and lifecycle recommendation.
- AC-10.3: Backward compatibility note states how to handle older packages.

---

## FR-11: Update Child Thread Prompt Template

### Required Updates

Update:

```text
skills/dispatch/adapters/codex_app_managed_worktree_thread/THREAD-PROMPT-TEMPLATE.md
```

### Required Additions

After the first-line `/goal`, include:

```text
Runtime identity:
- Runtime Correlation ID: {runtime_identity.runtime_correlation_id}
- Dispatch ID: {runtime_identity.dispatch_id}
- Task ID: {task_id}
- Initial Thread Title: {runtime_package.thread_title_or_task_id_title}
- Do not rename this thread. If the visible title changes anyway, keep using Runtime Correlation ID in every result package.
```

Add rules:

```text
- Do not archive this thread yourself.
- Do not delete local or remote branches.
- Do not claim clean-review approval.
- Do not rewrite or broaden the Goal Contract.
- Report Goal Mode evidence in the final review package.
- Report merge-back source availability: worktree path, patch bundle, branch/head, or unavailable.
- Report any temporary branch you created or used.
```

### Acceptance Criteria

- AC-11.1: Template includes stable runtime identity.
- AC-11.2: Template prohibits child self-archive and branch deletion.
- AC-11.3: Template requires Goal Mode and merge source evidence.

---

## FR-12: Add Runtime Lifecycle Evals

### Required File

```text
evals/scenarios/managed-worktree-lifecycle.md
```

Add prompt fixtures under:

```text
evals/prompts/dispatch-managed-worktree-lifecycle.csv
evals/prompts/goal-mode-hardening.csv
evals/prompts/clean-review-fanout.csv
evals/prompts/serial-dispatch-barrier.csv
```

### Required Scenarios

1. Child returns `ready_for_review`; no clean review yet; archive must be blocked.
2. Clean review passed; merge/discard not decided; archive must be blocked.
3. Merge completed; archive recommended; temp branch unknown; branch cleanup routed to human decision.
4. Archive occurred; temp branch remains; branch cleanup checklist required.
5. Temp branch is remote; deletion requires explicit approval.
6. Temp branch is unmerged; retain or human decision required.
7. Child renamed thread; correlation succeeds by `runtime_correlation_id`.
8. Child prompt does not start with `/goal`; adapter rejects.
9. Goal Mode evidence missing; result cannot be `ready_for_review`.
10. Issue 2 depends on Issue 1; Issue 2 write dispatch blocked until Issue 1 merge-back and base refresh.
11. Read-only prep for Issue 2 allowed while write dispatch blocked.
12. Multiple child packages return; coordinator routes to clean reviewer instead of deep-reviewing all.
13. Review package contains only redacted partial patch; merge-back cannot apply patch.
14. Main worktree dirty with unrelated files; merge-back blocks or requires pathspec-safe plan.
15. Complex P1 API contract change; planner/implementer/reviewer separation required.
16. Small low-risk doc edit; no forced managed worktree lifecycle ceremony.

### Acceptance Criteria

- AC-12.1: Scenario file covers all listed cases.
- AC-12.2: Prompt fixtures check trigger behavior and no-execution boundaries.
- AC-12.3: Existing dispatch package-only behavior remains covered.

---

## 9. Implementation Issue Map

### Issue 1: Add managed worktree lifecycle and closeout docs

Files:

```text
skills/dispatch/adapters/codex_app_managed_worktree_thread/THREAD-LIFECYCLE.md
skills/dispatch/adapters/codex_app_managed_worktree_thread/CLOSEOUT-PACKAGE-TEMPLATE.md
skills/dispatch/adapters/codex_app_managed_worktree_thread/ADAPTER.md
```

Acceptance:

- Lifecycle states and legal transitions are documented.
- Closeout package template exists.
- Adapter doc references lifecycle and closeout files.
- No public skill frontmatter is added.

### Issue 2: Add branch cleanup checklist

Files:

```text
skills/dispatch/adapters/codex_app_managed_worktree_thread/BRANCH-CLEANUP-CHECKLIST.md
skills/dispatch/adapters/codex_app_managed_worktree_thread/REJECT-NOOP-CHECKLIST.md
```

Acceptance:

- Local/remote/default/protected/unmerged branch rules are explicit.
- Archive and branch cleanup are not conflated.
- Checklist blocks unknown and high-risk deletion.

### Issue 3: Add merge-back protocol

Files:

```text
skills/dispatch/adapters/codex_app_managed_worktree_thread/MERGE-BACK-PROTOCOL.md
skills/_shared/GIT-BOUNDARY.md
```

Acceptance:

- Merge strategy priority order is documented.
- Redacted partial patch is not mergeable.
- Manual rewrite from prose is forbidden.
- Git boundary is referenced.

### Issue 4: Add runtime identity fields

Files:

```text
skills/dispatch/DISPATCH-PACKAGE.md
skills/dispatch/RESULT-PACKAGE.md
skills/dispatch/adapters/codex_app_managed_worktree_thread/THREAD-PROMPT-TEMPLATE.md
skills/dispatch/adapters/codex_app_managed_worktree_thread/REVIEW-PACKAGE-TEMPLATE.md
skills/dispatch/adapters/codex_app_managed_worktree_thread/RESULT-PACKAGE-TEMPLATE.md
```

Acceptance:

- `runtime_correlation_id` appears in every package/template where runtime correlation is needed.
- Thread title is documented as display-only.
- Title mutation behavior is defined.

### Issue 5: Harden Goal Mode

Files:

```text
skills/_shared/GOAL-CONTRACT.md
skills/dispatch/adapters/codex_app_managed_worktree_thread/DISPATCH-PACKAGE-CONTRACT.md
skills/dispatch/adapters/codex_app_managed_worktree_thread/THREAD-PROMPT-TEMPLATE.md
skills/dispatch/adapters/codex_app_managed_worktree_thread/RESULT-PACKAGE-TEMPLATE.md
scripts/lint_goal_contract.py
scripts/lint_child_goal_prompt.py
```

Acceptance:

- Child prompt first non-empty line starts with `/goal`.
- Placeholder goal commands are rejected.
- Missing Goal Mode evidence prevents `ready_for_review`.

### Issue 6: Add clean review fan-out protocol

Files:

```text
skills/dispatch/CLEAN-REVIEW-FANOUT.md
skills/dispatch/adapters/codex_app_managed_worktree_thread/CLEAN-REVIEW-PACKAGE-TEMPLATE.md
skills/_shared/SUBAGENT-DELEGATION.md
```

Acceptance:

- Fresh-context review package shape exists.
- Coordinator intake vs deep review boundary is documented.
- Reviewer cannot edit files or rely on parent memory.

### Issue 7: Add serial dispatch / merge barrier

Files:

```text
skills/dispatch/DISPATCH-PACKAGE.md
skills/dispatch/CONFLICT-PREFLIGHT.md
skills/dispatch/ROUTING-PROFILES.md
docs/runtime-dispatch-workflow.md
```

Acceptance:

- `dependency_barrier` schema exists.
- Dependent write dispatch is blocked until merge-back/base refresh.
- Read-only preparation exception is documented.

### Issue 8: Add complex work separation policy

Files:

```text
skills/dispatch/COMPLEX-WORK-SEPARATION.md
skills/dispatch/ROUTING-PROFILES.md
skills/verify/SKILL.md
skills/handoff/SKILL.md
```

Acceptance:

- Separation thresholds and role boundaries are explicit.
- Child implementer self-check is not clean review.
- Small low-risk tasks remain lightweight.

### Issue 9: Extend result/review package templates

Files:

```text
skills/dispatch/RESULT-PACKAGE.md
skills/dispatch/adapters/codex_app_managed_worktree_thread/REVIEW-PACKAGE-TEMPLATE.md
skills/dispatch/adapters/codex_app_managed_worktree_thread/RESULT-PACKAGE-TEMPLATE.md
```

Acceptance:

- New sections appear in templates.
- Backward compatibility for v0.3.2 packages is documented.
- Status rules prevent unsupported claims.

### Issue 10: Add lifecycle evals and update runtime workflow docs

Files:

```text
docs/runtime-dispatch-workflow.md
evals/scenarios/managed-worktree-lifecycle.md
evals/prompts/dispatch-managed-worktree-lifecycle.csv
evals/prompts/goal-mode-hardening.csv
evals/prompts/clean-review-fanout.csv
evals/prompts/serial-dispatch-barrier.csv
```

Acceptance:

- Scenario docs cover all v0.3.3 critical behaviors.
- Prompt fixtures cover reject/no-op, lifecycle, merge-back, Goal Mode, fan-out, and serial dependency.
- Runtime workflow shows the new post-dispatch return path.

---

## 10. Global Acceptance Criteria

v0.3.3 is accepted when all of the following are true:

- GAC-1: No new public skill is added.
- GAC-2: `dispatch` remains package-only and no docs imply it executes thread tools or subagents by default.
- GAC-3: Managed worktree lifecycle states and closeout rules are documented.
- GAC-4: Archive is separated from branch cleanup.
- GAC-5: Branch cleanup has local/remote/unmerged/protected/default branch gates.
- GAC-6: Merge-back requires reliable source evidence and never rewrites from prose.
- GAC-7: Runtime correlation ID is used instead of thread title as identity.
- GAC-8: Goal Mode has static prompt/contract lint and runtime evidence requirements.
- GAC-9: Clean review fan-out exists and keeps coordinator review bounded.
- GAC-10: Serial dependency barriers block dependent write dispatch until prerequisite merge-back/base refresh.
- GAC-11: Complex work separation policy prevents child implementer from being the final reviewer.
- GAC-12: New eval scenarios cover lifecycle, archive, branch cleanup, merge-back, title mutation, Goal Mode, review fan-out, and serial barriers.
- GAC-13: Existing v0.3.2 package-only dispatch behavior still passes.

---

## 11. Verification Plan

### Static checks

- Run goal contract lint on valid and invalid Goal Contract fixtures.
- Run child prompt lint on valid and invalid managed worktree prompt fixtures.
- Inspect changed markdown files for accidental public skill frontmatter.
- Verify new adapter files are under `skills/dispatch/adapters/codex_app_managed_worktree_thread/` and not exposed as public skills.

### Scenario checks

Use `evals/scenarios/managed-worktree-lifecycle.md` to manually or automatically check:

- archive block before clean review;
- archive block before merge/discard;
- archive-ready after merge evidence;
- branch cleanup unknown routes to human decision;
- remote branch cleanup requires explicit approval;
- title mutation correlation;
- Goal Mode missing evidence rejection;
- dependent issue dispatch barrier;
- merge-back rejection for redacted partial patch;
- coordinator review fan-out.

### Regression checks

- Existing `dispatch` fixtures still route read-only review away from managed worktree.
- Existing managed worktree admissibility still requires `task_type = write_implementation`, `readiness = ready_for_agent`, complete Goal Contract, source package, validation package, and `expected_output = review_package`.
- Existing `verify` and `triage` ownership remains unchanged: verify owns evidence sufficiency; triage owns lifecycle state and next route.

---

## 12. Rollout Plan

### Phase 1: Contract docs only

Add the new lifecycle, closeout, branch cleanup, merge-back, clean review fan-out, and complex work separation docs. Update adapter references. No behavior claims.

### Phase 2: Schema/template updates

Extend Dispatch Package, Result Package, Review Package, Thread Prompt Template, and Result Package Template with v0.3.3 lifecycle fields.

### Phase 3: Lint and evals

Add or extend goal/prompt lint scripts and lifecycle eval fixtures.

### Phase 4: Workflow docs

Update `docs/runtime-dispatch-workflow.md` with the post-dispatch lifecycle path and serial merge barrier.

### Phase 5: Runtime trial

Use a real Codex App managed worktree child thread and manually verify:

- runtime correlation ID survives title changes;
- review package returns Goal Mode evidence;
- clean review fan-out works from package-only context;
- merge-back uses reliable source instead of prose rewrite;
- archive and branch cleanup are separate decisions.

---

## 13. Open Questions

1. Should `archive_approval_required` default to `true` for all runtime archive operations, or may an adapter archive automatically after explicit execution approval plus closeout completion?
2. What exact Codex App evidence is available for Goal Mode activation in child threads?
3. What exact Codex App evidence is available for branch/worktree path, thread ID, and title mutation?
4. Can Codex App expose a reliable checkout/apply changes operation that the adapter can cite as merge-back evidence?
5. Should branch cleanup be purely recommendation-only in Groundwork, or can an execution-capable adapter perform local branch cleanup after explicit approval?
6. Should clean review fan-out default to `clean_reviewer` or `codex_subagent` when both are available?
7. Should v0.3.3 keep `dispatch_version: 2` with `runtime_lifecycle_version: 1`, or bump to `dispatch_version: 3`?

Recommended default: keep `dispatch_version: 2` and add `runtime_lifecycle_version: 1` to avoid breaking existing v0.3.2 package readers.

---

## 14. Recommended Next Action

Start implementation with Issue 1, Issue 4, and Issue 6 first:

1. Lifecycle/closeout docs establish the safe ending model.
2. Runtime identity fields stabilize all later evidence.
3. Clean review fan-out immediately reduces coordinator overload.

Then implement merge-back, branch cleanup, Goal Mode hardening, serial barriers, complex-work separation, and evals.
