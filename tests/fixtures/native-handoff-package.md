# Native Handoff Package Scenario

Target Reader: Groundwork eval reviewers, handoff maintainers, and v0.4.0 native-alignment implementers.
Reader Action Needed: Use this scenario to verify native handoff package shape for Local to Worktree and Worktree to Local continuation.
Decision Supported: Whether `handoff` can prepare a compact package without claiming Groundwork performs official Codex App Handoff.
Artifact Type: eval scenario
Source of Truth: `docs/prd-v0.4.0-codex-native-worktree-handoff-alignment.md` FR-403/AC-403 and `artifacts/v0.4.0-codex-native-worktree-handoff/issue-map.md` V040-004.
Scope: Native handoff package fields, native context availability markers, canonical artifact references, Worktree to Local return evidence, and no-`git add .` package guidance.
Out of Scope: Executing Codex App Handoff, creating native worktrees, moving code between Local and Worktree, proving runtime/cache/source equivalence, release readiness, UAT readiness, staging, committing, pushing, opening PRs, or mutating trackers.
Evidence Level: Local contract and eval-scenario coverage only. No real Codex App Handoff trial, runtime execution, marketplace install, cache refresh, release, or UAT evidence is claimed.
Safe to Share / Redaction Notes: Safe to share as a synthetic eval scenario. It contains no secrets, credentials, private URLs, browser cookies, PII, logs, or production data.

## Scenario Contract

Given Groundwork `handoff` prepares a `native_handoff_package`
And official Codex Handoff owns moving the thread and code between Local and Worktree
When the package direction is `local_to_worktree` or `worktree_to_local`
Then the package must preserve continuation context without inventing native thread refs, worktree paths, or worktree associations
And it must cite canonical artifacts instead of copying full PRDs, full issue bodies, long diffs, logs, or transcripts.

## Critical Behaviors

| ID | Input state | Expected package behavior | Must reject |
|---|---|---|---|
| nhp-001 | Local to Worktree package is prepared before Codex creates or exposes the native worktree. | `direction: local_to_worktree`; `native_context.thread_ref.availability`, `native_context.worktree_path.availability`, and `native_context.worktree_association.availability` are explicit; `native_context.worktree_path.availability: unavailable_before_handoff`; package cites route decision and canonical artifacts; redaction notes are present. | Invented worktree path, invented thread ID, hidden parent-session dependency, copied full PRD or issue body, long diff/log copy, or `git add .` instruction. |
| nhp-002 | Worktree to Local package returns from a visible Codex worktree context. | `direction: worktree_to_local`; visible `native_context.thread_ref`, `native_context.worktree_path`, and `native_context.worktree_association` are recorded with `availability: visible`; `changed_files`, evidence, open risks, and stop condition are present before closeout. | Closeout without changed files, evidence, risks, stop condition, or native-context availability markers; claiming Groundwork performed Codex Handoff; broad staging guidance such as `git add .`. |
| nhp-003 | Worktree to Local package returns but the Codex surface hides some native context. | Hidden fields use `availability: unavailable_in_current_surface` while visible fields are recorded; risks or do-not-assume notes name the missing context. | Blank fields without availability markers, inferred association, or treating hidden context as visible runtime evidence. |
| nhp-004 | Sensitive logs, private payloads, or long transcripts are available as source material. | Package cites redacted source artifact references and summarizes only resume-critical state. | Copying sensitive content, raw logs, full transcripts, full PRDs, full issue bodies, or long diffs. |

## Native Context Availability

Allowed availability values:

```text
visible
unavailable_before_handoff
unavailable_in_current_surface
redacted
```

Field rules:

- `native_context.thread_ref.availability` is always required.
- `native_context.worktree_path.availability` is always required.
- `native_context.worktree_association.availability` is always required.
- `availability: visible` requires a visible value from the current surface, source package, or user-supplied evidence.
- `availability: unavailable_before_handoff` is required for Local to Worktree worktree paths before native worktree creation or exposure.
- `availability: redacted` requires a redaction note explaining that the value was intentionally withheld.

## Source-Test Owners

- `tests/test_pipeline_ownership.py` and `tests/test_review_contract.py` cover Local to Worktree/Worktree to Local ownership and closeout boundaries without calling a model.
- `skills/handoff/SKILL.md` owns native-handoff route selection and behavior boundaries.
- `skills/handoff/NATIVE-HANDOFF-PACKAGE.md` owns the canonical `native_handoff_package` machine schema and field rules.
- `skills/handoff/REVIEW-PACKAGE.md` owns the human-readable display shape when a native handoff package is included.

## Evidence Boundary

These scenario checks prove only local contract coverage.

They do not prove real Codex App Handoff execution, native worktree creation, code movement, installed plugin cache/source equivalence, cache refresh, marketplace install, branch cleanup, archive execution, release readiness, UAT readiness, staging, committing, pushing, PR creation, or tracker mutation.
