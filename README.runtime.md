# Groundwork Runtime Plugin

Target Reader: Codex users and maintainers inspecting the installed Groundwork plugin package.
Reader Action Needed: Use the installed runtime contracts without treating source-repository materials as bundled runtime evidence.
Decision Supported: Whether this installed package is the lightweight runtime plugin rather than the full maintainer repository.
Artifact Type: runtime package README
Source of Truth: `.codex-plugin/plugin.json`, bundled `skills/`, and the local marketplace build boundary.
Scope: Installed package contents, runtime contract boundary, and evidence limitations.
Out of Scope: Maintainer docs, evals, artifacts, research, schemas, scripts, examples, release readiness, UAT readiness, cache refresh, and marketplace publication.
Evidence Level: Package source contract only; this README does not prove runtime execution, cache/source equivalence, release readiness, UAT readiness, or customer readiness.
Safe to Share / Redaction Notes: Safe to share as-is; contains no secrets, credentials, PII, private logs, or production payloads.

Groundwork is a lightweight Codex workflow plugin for non-trivial R&D tasks that benefit from requirement shaping, scoped implementation, verification, compact handoff, dispatch packaging, or project wiki maintenance.

This installed package intentionally contains only runtime contracts:

- `.codex-plugin/`
- `skills/`
- `README.md`
- `LICENSE`

Repository-only materials such as docs, evals, artifacts, research, schemas, scripts, examples, baselines, hooks, and maintainer history are not packaged. They are available in the source repository and must not be treated as current runtime evidence unless the user explicitly asks for historical or maintainer evidence.

Use direct answers for small, obvious, low-risk requests. Use Groundwork only when context, risk, or reuse justifies a workflow.
