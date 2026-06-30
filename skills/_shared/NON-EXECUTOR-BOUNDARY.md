# Non-Executor Boundary

Target Reader: Groundwork skills, coordinators, package authors, reviewers, and verifiers that need to preserve package-only or evidence-only boundaries.
Reader Action Needed: Decide what Groundwork may claim from source/package evidence and what requires separate tool, runtime, or human acceptance evidence.
Decision Supported: Whether a response may route, shape, package, verify evidence sufficiency, preserve continuation state, recommend an owner, or must stop before claiming execution.
Artifact Type: shared guardrail
Source of Truth: Lifecycle preflight mode boundaries, runtime capability evidence taxonomy, dispatch package-only contract, native handoff package contract, verify scope-first contract, and wiki source-truth boundary.
Scope: Framework-level non-executor invariant for Groundwork public skills and shared contracts.
Out of Scope: Runtime adapter implementation, Codex App thread execution, subagent execution, official Codex Handoff execution, branch cleanup execution, remote writes, release approval, UAT approval, and customer acceptance.
Evidence Level: Source-validation policy only. This contract does not prove runtime execution, tool execution, cache refresh, release readiness, UAT readiness, or customer acceptance.
Safe to Share / Redaction Notes: Safe to share as-is; contains no secrets, credentials, PII, private logs, or production payloads.

## Core Rule

Groundwork is not an executor by default.

Groundwork may produce structured decisions and packages, inspect or verify evidence sufficiency, and recommend the next owner. It must not claim an external action happened unless the response cites direct tool, runtime, or accepted human evidence for that specific action.

## Groundwork May

Groundwork may:

- route accepted work to the appropriate skill, role, runtime, or owner;
- shape requirements, scope, acceptance criteria, issue slices, and implementation plans;
- package source context, dispatch instructions, review expectations, handoff state, or result expectations;
- verify evidence sufficiency for a stated claim;
- preserve compact continuation state and do-not-assume boundaries;
- recommend the next owner, next skill, next command, or next human decision.

## Groundwork Must Not Claim Without Direct Evidence

Groundwork must not claim these actions or outcomes happened without tool, runtime, or accepted human evidence that specifically supports the claim:

- thread creation;
- subagent spawn;
- worktree creation;
- native Codex Handoff execution;
- runtime execution;
- validation execution;
- clean review completion;
- cache refresh;
- branch deletion;
- remote mutation;
- release readiness;
- UAT readiness;
- customer acceptance.

## Skill-Specific Deltas

Use this shared boundary first, then keep only the delta that is specific to the active skill:

- `dispatch`: may generate package-only runtime routing, execution matrixes, and Result Package expectations; it does not create threads, spawn subagents, create worktrees, execute packages, or validate results.
- `handoff`: may prepare native handoff packages and continuation state; it does not execute Codex Handoff, move code, create native worktrees, archive threads, or perform native Handoff Git operations.
- `verify`: may judge evidence sufficiency and recommend task-state next action; it does not close tasks, mutate remotes, approve merge-back, delete branches, or perform runtime execution.
- `wiki`: may maintain source-cited project knowledge; it does not mutate raw source truth or promote wiki synthesis into source, runtime, release, UAT, or customer truth.

## Evidence Rule

Package text, prompt text, route decisions, wiki pages, implementation summaries, visual packets, old baselines, and lifecycle state are not execution evidence by themselves.

Execution claims require specific supporting evidence, such as:

- a tool result showing the action completed;
- runtime or adapter output that names the completed action;
- current command output for the claimed repository or runtime state;
- accepted human confirmation that explicitly owns the claim.

If that evidence is missing, use `unverified`, `not_applicable`, `blocked`, `package_only`, `recommendation_only`, or `needs_human_decision` instead of past-tense execution wording.

## Approval Rule

This boundary does not remove existing approval gates. Destructive actions, data writes, remote mutation, branch deletion, native Handoff execution, runtime execution, cache refresh, release, UAT, and customer-facing acceptance still require the more specific gate or owner required by the active skill and shared guardrails.
