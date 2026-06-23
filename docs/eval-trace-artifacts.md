# Eval Trace Artifacts

Target Reader: Groundwork maintainers, eval harness authors, trace diagnostics authors, report authors, and reviewers promoting trace-first eval evidence.
Reader Action Needed: Use this policy before creating, promoting, reviewing, or committing trace-first eval artifacts.
Decision Supported: Whether eval output stays local scratch, can be promoted into `artifacts/evals/<run-id>/`, or must be blocked until redaction and review are complete.
Artifact Type: maintainer doc
Source of Truth: `docs/prd-v0.4.x-trace-first-eval-platform-roadmap.md`, `artifacts/v0.4.x-trace-first-eval-platform-roadmap/issue-map.md`, `docs/nightly-harness.md`, and shared artifact directory/redaction policies.
Scope: Trace-first eval scratch layout, promoted artifact layout, promotion rules, redaction status, forbidden promoted content, artifact relationships, and evidence boundaries for V044-001.
Out of Scope: Trace parser implementation, report generator implementation, patch suggestion generation, CI gates, default runner output changes, runtime execution, cache refresh, release readiness, UAT readiness, or customer readiness.
Evidence Level: Documentation and policy only. This file defines safe artifact handling before trace diagnostics, reports, patch suggestions, or CI are implemented.
Safe to Share / Redaction Notes: Safe to share as maintainer documentation. It contains layout examples, schema-shaped field examples, and policy text only; no secrets, credentials, PII, raw traces, logs, or private payloads.

## Core Decision

Trace-first eval output has two distinct locations:

```text
.groundwork/harness/<run-id>/       # local scratch, ignored by default
artifacts/evals/<run-id>/           # promoted, reviewable, redacted-only
```

`.groundwork/harness/<run-id>/` is for local runtime scratch. It may contain raw runtime output while a run is being inspected locally. It is ignored by default and must not be committed unless a maintainer explicitly approves a specific, redacted promotion path.

`artifacts/evals/<run-id>/` is for promoted review artifacts. Promoted artifacts are durable and reviewable, so they must have a target reader, a reader action, and a redaction status. Raw trace material must not be copied there unless it has been redacted and reviewed.

Not every local run needs promotion. Promotion is optional and should happen only when another reviewer, session, issue, PR, report, or release discussion needs durable evidence.

## Runtime Scratch Layout

The local scratch layout may vary by runner implementation, but V044 trace work should treat this shape as the policy target:

```text
.groundwork/harness/<run-id>/
  raw/
    trace/
      <case-id>.jsonl
    final/
      <case-id>.txt
    results.jsonl
    summary.json
  score/
    <case-id>.score.json
  logs/
  tmp/
```

Rules:

- Raw JSONL trace belongs in local scratch by default.
- Raw command output, browser logs, tool transcripts, and private local paths stay in scratch unless explicitly redacted and promoted.
- Scratch output does not need audience-first headers because it is not a durable artifact.
- Scratch output is not release, UAT, cache, marketplace, or customer-readiness evidence by itself.
- Scratch output must not be staged through broad staging commands.

## Promoted Layout

Promoted eval artifacts should use:

```text
artifacts/evals/<run-id>/
  README.md
  summary.json
  results.jsonl
  score/
    <case-id>.score.json
  final/
    <case-id>.txt
  trace/
    <case-id>.redacted.jsonl
  report.md
  patch-suggestions.json
  redaction-notes.md
```

`trace/` contains only redacted trace files. Do not put raw trace files in this directory.

Promoted files have these roles:

- `README.md`: target reader, review action, run scope, source root, run source, redaction status, and limitations.
- `summary.json`: redacted run-level summary suitable for review.
- `results.jsonl`: redacted per-case result records.
- `score/<case-id>.score.json`: optional schema-backed score wrapper for a case.
- `final/<case-id>.txt`: final response text for a case, redacted when needed.
- `trace/<case-id>.redacted.jsonl`: redacted trace excerpts only.
- `report.md`: human-readable report generated or assembled from redacted artifacts.
- `patch-suggestions.json`: non-applying patch suggestion artifact. Suggestions must include `auto_apply: false`.
- `redaction-notes.md`: what was reviewed, what was removed, what remains unknown, and who reviewed it.

## Promotion Rules

Promote only the minimum artifact set needed for review.

Promotion requires:

- a target reader;
- a reader action;
- run scope;
- source root or source ref;
- scratch source path or run id;
- redaction status;
- redaction reviewer;
- limitations and missing evidence;
- explicit statement that promoted artifacts are not runtime, release, UAT, or customer-readiness proof unless separate evidence is supplied.

Promotion is blocked when:

- redaction status is `failed`;
- redaction status is `not_reviewed` for any artifact that may include trace, command output, browser logs, private payloads, cookies, or credentials;
- a promoted trace file is not clearly marked `.redacted.jsonl`;
- a reviewer cannot tell whether raw trace content was copied;
- the artifact would expose secrets, PII, production payloads, or unapproved private URLs.

Promotion is optional when:

- a local run is exploratory;
- the run only supports local debugging;
- the result can be summarized in a final response without durable reuse;
- no future reviewer needs trace, final output, score, summary, report, or patch suggestion artifacts.

## Redaction Status

Use this object shape in promoted JSON metadata when possible:

```json
{
  "redaction": {
    "status": "not_needed | applied | failed | not_reviewed",
    "reviewer": "human | tool | unknown",
    "notes": []
  }
}
```

Status meanings:

- `not_needed`: the artifact was reviewed and contains no sensitive material requiring redaction.
- `applied`: sensitive or noisy content was found and redacted before promotion.
- `failed`: redaction could not be completed; the artifact must not be promoted.
- `not_reviewed`: redaction review has not happened; only non-sensitive metadata may be promoted.

Reviewer meanings:

- `human`: a human reviewed the promoted content.
- `tool`: a deterministic or scripted redaction check reviewed the promoted content.
- `unknown`: reviewer identity is not known; use this only when the artifact remains non-sensitive metadata or when the limitation is explicitly documented.

`redaction-notes.md` should use the same vocabulary and explain any `unknown`, `failed`, or `not_reviewed` status.

## Forbidden Promoted Content

Promoted artifacts must not contain:

- secrets;
- credentials;
- tokens;
- Authorization headers;
- cookies;
- private keys;
- PII;
- production payloads;
- private URLs unless explicitly approved;
- raw browser logs with user data;
- unredacted command output containing sensitive paths or payloads;
- raw database rows;
- raw request or response bodies from private systems;
- local-only config values that reveal secrets, hosts, usernames, or private paths beyond what the reviewer needs.

If any forbidden content is present, keep the artifact in scratch, redact it, or summarize it without copying the sensitive payload.

## Artifact Relationships

Trace-first eval artifacts should be treated as a chain, not as interchangeable proof:

```text
scratch trace
  -> redacted trace excerpt
  -> final output
  -> score JSON
  -> summary
  -> report
  -> patch suggestions
```

Relationship rules:

- `trace` explains what happened inside a run; it is sensitive by default.
- `final` records model-visible output for a case; it may still contain private context and needs review.
- `score` normalizes case-level verdict shape; it does not prove runtime correctness.
- `summary` aggregates redacted results; it does not replace trace or final evidence when a case needs inspection.
- `report` is a reviewer-facing interpretation of redacted artifacts; it must cite source artifacts and limitations.
- `patch-suggestions.json` is advisory only. It must not auto-apply patches and must include rollback or review context when implemented in a later slice.

## Evidence Boundary

Local trace artifacts are not runtime readiness.

Score JSON is not release readiness.

Reports are not UAT or customer readiness.

Patch suggestions are not accepted patches.

Runtime or release claims still must name:

- installed plugin root;
- source root;
- refresh or source/cache equivalence method;
- run scope;
- commands or trials;
- limitations;
- missing evidence.

Promoted artifacts can support a review claim only to the extent that their source, scope, redaction status, and limitations are explicit.

## Deferred Implementation

V044-001 is documentation only. It does not implement:

- trace parser;
- trace diagnostics;
- report generator;
- patch suggestion generator;
- CI workflow;
- default runner output changes;
- automatic promotion from `.groundwork/harness/` into `artifacts/evals/`;
- raw trace commits;
- runtime/cache/release/UAT evidence.

V044-002 should implement trace diagnostics only after this artifact layout and redaction policy are accepted.
