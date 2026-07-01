# Groundwork Runtime Plugin

Target Reader: Codex users and maintainers inspecting the installed Groundwork plugin package.
Reader Action Needed: Use the installed runtime contracts without treating source-repository materials as bundled runtime evidence.
Decision Supported: Whether this installed package is the lightweight runtime plugin rather than the full maintainer repository.
Artifact Type: runtime package README
Source of Truth: `.codex-plugin/plugin.json`, bundled `skills/`, dormant hook runtime files, and the local marketplace build boundary.
Scope: Installed package contents, runtime contract boundary, and evidence limitations.
Out of Scope: Maintainer docs, evals, artifacts, research, schemas, examples, scripts outside `scripts/codex-hooks/`, release readiness, UAT readiness, cache refresh, and marketplace publication.
Evidence Level: Package source contract only; this README does not prove runtime execution, cache/source equivalence, release readiness, UAT readiness, or customer readiness.
Safe to Share / Redaction Notes: Safe to share as-is; contains no secrets, credentials, PII, private logs, or production payloads.

Groundwork is a lightweight Codex workflow plugin for non-trivial R&D tasks that benefit from requirement shaping, scoped implementation, verification, compact handoff, dispatch packaging, or project wiki maintenance.

This installed package intentionally contains only runtime contracts:

- `.codex-plugin/`
- `skills/`
- `hooks/hooks.json`
- `scripts/codex-hooks/`
- `README.md`
- `LICENSE`

The bundled hook files are dormant by default. They no-op unless a project explicitly opts in with `.groundwork/harness/router-observability/config.json`, or the current process force-enables the harness with `GROUNDWORK_ROUTER_OBSERVABILITY=1`. Plugin-bundled hooks still require the Codex hook trust path for the installed plugin version; automation that intentionally bypasses that review must do so explicitly for that invocation. `observe_only` does not inject route hints. `guided_hint_trial` may inject route hints, but those runs are behavior-shaping trial evidence and must not be counted as passive routing baselines.

Repository-only materials such as docs, evals, artifacts, research, schemas, maintainer scripts outside `scripts/codex-hooks/`, examples, baselines, and maintainer history are not packaged. They are available in the source repository and must not be treated as current runtime evidence unless the user explicitly asks for historical or maintainer evidence.

Use direct answers for small, obvious, low-risk requests. Use Groundwork only when context, risk, or reuse justifies a workflow.
