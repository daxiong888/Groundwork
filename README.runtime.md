# Groundwork Runtime Plugin

Target Reader: Codex users and maintainers inspecting the installed Groundwork plugin package.
Reader Action Needed: Use the installed runtime contracts without treating source-repository materials as bundled runtime evidence.
Decision Supported: Whether this installed package is the lightweight runtime plugin rather than the full maintainer repository.
Artifact Type: runtime package README
Source of Truth: `.codex-plugin/plugin.json`, bundled `skills/`, dormant hook runtime files, and the local marketplace build boundary.
Scope: Installed package contents, runtime contract boundary, and evidence limitations.
Out of Scope: Maintainer docs, tests, Candidate Trial transport, artifacts, research, scripts outside `scripts/codex-hooks/`, release readiness, UAT readiness, cache refresh, and marketplace publication.
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

The bundled hook files are dormant by default. All supported hook events enter through one lightweight event entrypoint, which exits before importing telemetry or the route classifier unless a project explicitly opts in with `.groundwork/harness/router-observability/config.json`, or the current process force-enables telemetry with `GROUNDWORK_ROUTER_OBSERVABILITY=1`. Plugin-bundled hooks still require the Codex hook trust path for the installed plugin version. Runtime hooks are observe-only: they never inject route hints or prompt context, score routes, infer model profiles, or claim skill loads. They record minimized prompt/response candidates, hashes, optional redacted capture, and ordered captured tool/permission event diagnostics for offline maintainer analysis. Counts describe only records captured by the configured hooks and matchers; they are not a denominator for all host events or host capability coverage. These artifacts are improvement telemetry only, not runtime, cache-refresh, release, UAT, marketplace, or customer-readiness evidence.

Repository-only materials such as docs, tests, Candidate Trial transport, artifacts, research, maintainer scripts outside `scripts/codex-hooks/`, and maintainer history are not packaged. They are available in the source repository and must not be treated as current runtime evidence unless the user explicitly asks for historical or maintainer evidence.

Use direct answers for small, obvious, low-risk requests. Use Groundwork only when context, risk, or reuse justifies a workflow.
