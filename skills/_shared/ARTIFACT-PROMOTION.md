# Artifact Promotion Gate

Target Reader: Groundwork skills that turn conversation output, PRDs, issue drafts, verification findings, or handoff notes into durable sources of truth.
Reader Action Needed: Decide when a conversation artifact must become a durable canonical artifact, when an external source already owns truth, and how lifecycle state should reference it.
Decision Supported: Whether to keep output conversation-only, promote it to `artifacts/<workstream-slug>/`, or cite an external issue/PR as the source of truth.
Scope: PRD acceptance, issue splitting, implementation readiness, verification reports, handoff sources, source-of-truth promotion, and relationship to lifecycle state.
Out of Scope: Project-wide task databases, forced docs for small tasks, copying full external issues, duplicating complete PRDs into `STATE.md`, and creating artifacts for ordinary direct answers.
Evidence Level: Based on v0.3 lifecycle-state source-truth rules and observed Groundwork session failure where accepted PRD / issue source lived only in chat or remote issue context.
Related Issues: #30, #28, #33.

## Core Rule

Promote conversation output when it becomes a source of truth for future work.

Do not promote output merely because it looks polished, long, or professional.

## Canonical Artifacts vs Lifecycle State

Use this distinction:

```text
PRD / issue map / verification report / contract note
  -> canonical artifact

artifacts/<workstream-slug>/STATE.md
  -> compact recovery summary that references canonical artifacts
```

`STATE.md` must not contain full PRDs, full issue bodies, full plans, full diffs, command transcripts, or full verification reports. It should cite the canonical artifact and record only current recoverable facts.

## Promotion Required

Promotion is required, or an external source of truth must be explicitly named, when at least one is true:

1. a PRD has been accepted by the user;
2. an accepted PRD is about to be split into issues;
3. a PRD, issue map, or contract note is about to drive implementation;
4. an artifact will be used by another agent, session, PR, reviewer, or maintainer;
5. the artifact contains user-confirmed business decisions;
6. the artifact affects UAT, SIT, release, customer validation, or external handoff;
7. remote issues are about to be created from conversation-only source material;
8. the next session would need to rediscover decisions, evidence, gaps, risks, or next action;
9. a verification report creates a gap closure that must survive the session;
10. the user asks to save, resume, hand off, or continue later.

## Promotion Not Required

Do not promote for:

- small direct answers;
- simple rewrites;
- one-off explanations;
- low-risk edits with obvious verification;
- ordinary implementation plans that do not cross sessions;
- existing external issues or PRs that fully own source truth;
- verification with no remaining gap and no reuse need;
- handoff response that is sufficient and does not need durable continuation.

Weak signals are not enough:

- several artifacts exist;
- the task looks complex;
- the agent wants tidiness;
- the answer looks important;
- Groundwork habit suggests a file.

## Default Paths

Use the existing lifecycle artifact family:

```text
artifacts/<workstream-slug>/prd.md
artifacts/<workstream-slug>/issue-map.md
artifacts/<workstream-slug>/contract.md
artifacts/<workstream-slug>/verification.md
artifacts/<workstream-slug>/handoff.md
artifacts/<workstream-slug>/STATE.md
artifacts/<workstream-slug>/ROADMAP.md
```

Only create the files that are justified by the task. Do not create empty templates.

## Required Artifact Header

Durable artifacts should start with an audience-first header:

```md
Target Reader:
Reader Action Needed:
Decision Supported:
Artifact Type:
Source of Truth:
Scope:
Out of Scope:
Evidence Level:
Safe to Share / Redaction Notes:
```

Add task-specific fields as needed, such as `Last Updated`, `Related Issue`, `Verification Evidence`, or `Stop Condition`.
Use `Canonical Sources` as an optional task-specific field when the artifact needs multiple source pointers; it does not replace `Source of Truth`.

## Source-of-Truth Gate

Before `to-issues`, `implement`, `verify`, or `handoff`, decide:

```text
Does a canonical source already exist?
  yes -> cite it and do not duplicate it
  no  -> decide whether promotion is required

Will the current conversation output drive downstream work?
  yes -> promote or name an external source of truth
  no  -> keep conversation-only

Will future sessions need recovery state?
  yes -> use lifecycle-state threshold for STATE.md
  no  -> do not create STATE.md
```

## Skill Integration

### `to-prd`

A draft PRD may stay conversation-only. Once accepted and used for issues, implementation, or handoff, it must be promoted or assigned to an external source of truth.

### `to-issues`

Do not split a raw or unaccepted PRD into fake-precise issues. If the PRD is accepted but conversation-only, promote it first or explicitly cite an external issue/PR as canonical.

### `implement`

Before writing code, identify the source of truth: accepted PRD, issue, code truth, runtime evidence, or explicit user instruction. If implementation depends on a conversation-only accepted PRD, promote or cite it.

### `verify`

Verification reports may stay in the final response when no reuse is needed. Promote when the evidence supports UAT/release/customer readiness, creates a gap closure, or must be reused by another session.

### `handoff`

Handoff should reference existing canonical artifacts and `STATE.md` when present. It should not copy full artifacts into the handoff body.

## Forbidden Behavior

- Do not force every issue into local lifecycle state.
- Do not copy full PRDs into `STATE.md`.
- Do not duplicate full external issue bodies locally by default.
- Do not create root `STATE.md`, `PROJECT-STATE.md`, `.planning`, `.gsd`, or `.groundwork/tasks` as lifecycle artifacts.
- Do not create artifacts that have no target reader, action, scope, or evidence level.
