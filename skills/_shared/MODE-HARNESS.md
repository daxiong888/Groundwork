Target Reader: Groundwork skill authors, routers, implementers, reviewers, verifiers, and coordinators.
Reader Action Needed: Classify the host mode before durable writes, runtime claims, reviewer closeout, or artifact promotion.
Decision Supported: Whether a skill may write files, run runtime tools, mutate git or remotes, produce conversation-only output, or must stop with a boundary.
Artifact Type: shared guardrail
Source of Truth: Host-mode capability evidence, `skills/to-prd/SKILL.md`, `skills/_shared/GRILLING.md`, and Groundwork role-separation policy.
Scope: Host-mode detection, Plan Mode fallback behavior, read-only/chat-only boundaries, durable write gates, runtime execution gates, and skill-specific downgrade behavior.
Out of Scope: Implementing host tools, creating Plan Mode, executing runtimes, changing repository files by itself, approving release/UAT/customer readiness, or replacing skill-specific contracts.
Evidence Level: Source-validation policy only. This contract does not prove tool-enforced Plan Mode, runtime execution, marketplace behavior, cache refresh, browser evidence, UAT evidence, release evidence, or customer readiness.
Safe to Share / Redaction Notes: Safe to share as-is; contains no secrets, credentials, PII, private logs, or production payloads.

# Mode Harness

## Core Rule

Host mode is a gate on what Groundwork may do. It is not evidence that an action happened.

Use the strongest mode only when the current host or adapter exposes evidence for it. Without host/tool evidence, say `unknown`, `unavailable`, or `prompt_preference`; do not claim `tool_enforced` Plan Mode, runtime execution, selector enforcement, clean review, verification, cache refresh, or write completion from prompt text alone.

## Host Mode Snapshot

Use this transient shape when mode affects trust, durable writes, runtime execution, or closeout:

```yaml
host_mode:
  mode: plan_mode | read_only | write_capable | chat_only | unknown
  tool_enforcement: tool_enforced | prompt_preference | unavailable | unknown
  durable_writes_allowed: true | false | unknown
  git_writes_allowed: true | false | unknown
  runtime_execution_allowed: true | false | unknown
  remote_mutation_allowed: true | false | unknown
```

## Mode Rules

### `plan_mode`

Plan Mode may shape route, scope, evidence, artifact boundary, conversation drafts, and the highest-impact question. It must not create or update durable files, mutate git, mutate remote systems, execute runtime packages, or claim that a write-capable action occurred.

When Plan Mode is unavailable or not exposed, run the same entry decision as prompt-level planning and do not claim tool-enforced Plan Mode.

### `read_only`

Read-only mode may inspect supplied source, report findings, produce route decisions, and prepare packages. It must not edit files, stage changes, mutate git, execute write-capable runtime packages, or close remote state.

### `write_capable`

Write-capable mode may edit only after source truth, git topology, artifact promotion, and risk gates pass. Write-capable mode does not by itself prove tests, runtime behavior, clean review, independent verification, UAT, release, marketplace, or cache-refresh evidence.

### `chat_only`

Chat-only mode may produce direct answers, conversation drafts, package templates, route recommendations, and stop conditions. It must not claim durable artifact creation, file edits, runtime execution, git mutation, or remote mutation.

### `unknown`

Unknown mode must take the safer branch for durable writes and runtime claims. It may recommend the next write-capable or runtime-backed route, but it must not claim the action happened.

## Public Skill Downgrade Matrix

| Skill | In Plan Mode / read-only / chat-only |
| --- | --- |
| `to-prd` | Produce a conversation draft, artifact recommendation, route boundary, or one highest-impact question. Do not write durable PRD files. |
| `to-issues` | Produce an issue-map draft or source-gap report. Do not create tracker issues or durable issue artifacts unless write-capable artifact promotion is available. |
| `triage` | Produce readiness, blocker, severity, and AFK/HITL verdicts only. Do not mutate task state, trackers, or lifecycle artifacts. |
| `write-plan` | Produce the plan only. Do not edit implementation files. |
| `prototype` | Produce a throwaway spec, inline prototype draft, or prototype review. Without browser/runtime evidence, do not claim interaction was verified. |
| `implement` | Produce diagnosis, a lightweight plan, or read-only conformance review. Do not edit files unless write-capable gates pass. |
| `verify` | Produce scope-first evidence sufficiency results. Mark unavailable evidence as `unverified` or `blocked`; do not create missing evidence by assertion. |
| `handoff` | Produce a compact handoff package only. Do not claim native handoff execution, archive, branch cleanup, or remote mutation. |
| `dispatch` | Produce package-only routing, runtime recommendations, and execution gates. Do not spawn runtimes, create worktrees, or claim execution. |
| `wiki` | Query, audit, or recommend wiki changes only. Do not write wiki pages unless write-capable artifact promotion and wiki maintenance scope are explicit. |

## Hard Negatives

Fail or mark blocked when:

- Plan Mode output claims a durable file was created or updated;
- read-only or chat-only output claims file edits, git mutation, runtime execution, or remote mutation;
- package-only dispatch output claims a child thread, worktree, subagent, cache refresh, runtime run, archive, cleanup, or selector enforcement happened;
- a skill claims `tool_enforced` Plan Mode or selector enforcement without host/adapter evidence;
- verification passes readiness from Plan Mode, prompt text, package text, or same-session self-check alone;
- implementation proceeds from raw requirements in Plan Mode without accepted source truth or explicit PRD/spec bypass.
