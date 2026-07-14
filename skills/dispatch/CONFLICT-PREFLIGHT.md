# Dispatch Conflict Preflight

## Target Reader

Groundwork dispatch users, coordinator threads, runtime adapter authors, and reviewers deciding whether multiple tasks can be routed in parallel.

## Reader Action Needed

Use this preflight before parallelizing dispatched tasks, especially write tasks, and record conflict group, dependency group, parallelization eligibility, and merge order hints in Dispatch Package v2.

## Decision Supported

Whether tasks can run in parallel, must be serialized, need approval, or must split into diagnosis and write subtasks before routing.

## Artifact Type

shared dispatch preflight reference

## Source of Truth

Dispatch Package v2 schema, managed-worktree routing contracts, and Groundwork conflict-isolation policy.

## Scope

This document defines conflict grouping and default parallelization rules for dispatch. It does not inspect a repository automatically, execute tasks, merge work, or resolve conflicts.

## Out of Scope

- Runtime execution.
- Git merge automation.
- Worktree creation.
- Remote writes.
- Product truth invention when source evidence is missing.

## Evidence Level

Source-validation policy only. This preflight does not prove runtime execution, worktree creation, merge safety, release readiness, UAT readiness, or customer readiness.

## Safe to Share / Redaction Notes

Safe to share as-is; contains no secrets, credentials, PII, private logs, or production payloads.

## Conflict Inputs

Before routing tasks in parallel, dispatch should inspect available issue text, source package, known files, first inspection steps, contracts, validation expectations, and user constraints for likely conflicts in:

- files
- modules
- routes
- API contracts
- DB schemas
- migrations
- generated artifacts
- shared fixtures
- public types/interfaces
- test snapshots
- state machines
- shared config

## Conflict Group Taxonomy

Use stable conflict group names when evidence points to one of these categories.

| Conflict Group | Signals | Default Write Parallelization |
|---|---|---|
| `shared-file` | Same likely source, test, doc, fixture, or config file. | serialize_or_ask_approval |
| `module` | Same module/package/service boundary even when exact files differ. | serialize_or_ask_approval |
| `route` | Same endpoint, route table, controller mapping, or URL surface. | serialize_or_ask_approval |
| `api-contract` | Same request/response schema, public endpoint behavior, or client/server contract. | serialize_or_ask_approval |
| `schema` | Same OpenAPI, GraphQL, JSON schema, validation schema, or other non-DB shared schema. | serialize_or_ask_approval |
| `db-schema` | Same table, column, index, constraint, or data correctness rule. | serialize_or_ask_approval |
| `migration` | Same migration chain, ordering, rollback path, or schema version. | serialize_or_ask_approval |
| `generated-artifact` | Same generated file, codegen output, snapshot, bundle, or derived artifact. | serialize_or_ask_approval |
| `fixture` | Same shared test fixture, seed data, mock, cassette, or example payload. | serialize_or_ask_approval |
| `public-type` | Same public interface, type, enum, protocol, exported shape, or shared DTO. | serialize_or_ask_approval |
| `state-machine` | Same lifecycle state, transition, guard, status enum, or workflow machine. | serialize_or_ask_approval |
| `shared-config` | Same runtime config, build config, environment key, feature flag, or plugin manifest. | serialize_or_ask_approval |
| `unknown` | Conflict evidence is incomplete or ambiguous. | serialize_or_ask_approval |
| `none` | Evidence shows independent files/contracts and no shared write surface. | parallel_allowed |

## Core Rules

- Same conflict group cannot be parallelized as write tasks without explicit approval.
- Read-only subagent reviews may run in parallel even when inspecting the same area.
- Hybrid tasks must split before write parallelization.
- Unknown conflict groups require serialization or explicit approval.
- Merge order hint is required for conflicting write tasks.
- Approval to parallelize a conflict must be explicit and scoped to the affected conflict group.
- Dispatch should prefer fewer parallel write tasks when source evidence is weak.

## Parallelization Field Rules

`runtime_policy.max_parallel_units` is the package-wide total concurrency ceiling. `parallelization.max_parallel_group_size` is the per-conflict-or-dependency-group ceiling for the task. Effective concurrency must satisfy both.

Each dispatched task must include:

```yaml
parallelization:
  eligible: true
  conflict_group: ""
  dependency_group: ""
  max_parallel_group_size: 1
  merge_order_hint: ""
```

For conflicting write tasks:

```yaml
parallelization:
  eligible: false
  conflict_group: "api-contract"
  dependency_group: "shared-contract"
  max_parallel_group_size: 1
  merge_order_hint: "merge API contract change before dependent client updates"
```

For read-only tasks:

```yaml
parallelization:
  eligible: true
  conflict_group: "api-contract"
  dependency_group: ""
  max_parallel_group_size: 3
  merge_order_hint: "not applicable for read-only review"
```

For unknown conflicts:

```yaml
parallelization:
  eligible: false
  conflict_group: "unknown"
  dependency_group: ""
  max_parallel_group_size: 1
  merge_order_hint: "serialize until conflict group is confirmed"
```

## Hybrid Split Rule

If a task combines investigation and possible edits, dispatch must not parallelize it as a write task. It should route the investigation first, then dispatch a concrete write subtask only after the write surface, source truth, AC, boundaries, and validation are known.

## Merge Order Hints

Merge order hints should name the dependency that makes ordering necessary.

Examples:

- "merge schema migration before ORM and API updates"
- "merge public type change before downstream callers"
- "merge generated artifact producer before generated output refresh"
- "merge state-machine transition change before UI status handling"

Do not use empty or generic hints such as "merge carefully" for conflicting write tasks.

## Selector Boundary

Conflict preflight may influence `reasoning_effort` and `cost_latency_bias`, but it does not prove selector enforcement. Selector status follows `skills/_shared/RUNTIME-CAPABILITY.md` and runtime adapter evidence.
