# Router Telemetry Harness

Target Reader: Groundwork maintainers, Codex hook reviewers, and eval authors using local traces to improve routing and output contracts.

Reader Action Needed: Decide whether to opt a project into observe-only telemetry, inspect its minimized artifacts, and promote only reviewed evidence into offline eval work.

Decision Supported: Whether a local trace is safe and sufficient for a maintainer investigation; never whether a route, runtime, release, UAT, or customer claim passed.

Artifact Type: canonical maintainer harness guide.

Source of Truth: `hooks/hooks.json`, `scripts/codex-hooks/groundwork_router_telemetry.py`, `scripts/codex-hooks/groundwork_route_detection.py`, `scripts/codex-hooks/groundwork_route_registry.json`, and `evals/verdict_model.py`.

Scope: dormant plugin-bundled hooks, project opt-in, hash/redaction policy, prompt-route candidates, response-shape candidates, ordered tool/permission events, coverage diagnostics, and offline promotion.

Out of Scope: prompt injection, guided modes, live scoring, model/profile inference, router cards, authoritative skill-load claims, automatic eval mutation, automatic dispatch/execution, release/UAT/customer readiness, and cache equivalence.

Evidence Level: source implementation and local telemetry contract. Trace artifacts are improvement evidence only.

Safe to Share / Redaction Notes: The guide is safe to share. Trace directories are private scratch until reviewed and redacted; do not promote secrets, PII, private payloads, raw prompts, or raw final responses.

## Architecture

```mermaid
flowchart TD
  A["Dormant plugin hooks"] --> B{"Project opted in?"}
  B -- "no" --> C["No-op"]
  B -- "yes" --> D["Prompt hash + prompt route candidate"]
  D --> E["Ordered tool and permission events"]
  E --> F["Final hash + response-shape candidate + coverage"]
  F --> G["Offline maintainer analysis"]
  G --> H{"Reviewed reproducible gap?"}
  H -- "yes" --> I["Add or update eval case"]
  H -- "no" --> J["Keep scratch local"]
```

The runtime and Maintainer Lab have separate responsibilities:

| Layer | Responsibilities | Must Not Do |
| --- | --- | --- |
| Runtime telemetry | Opt-in detection, hashing, redaction, event ordering, coverage, prompt-route candidate, response-shape candidate. | Inject prompts, score pass/fail, infer execution profile, generate router cards, or call response shape an actual route. |
| Maintainer Lab | Replay, scoring, behavior checks, output UX checks, reviewed eval backfill, trend reporting. | Upgrade telemetry into runtime/release/UAT truth without stronger evidence. |

## Opt-In

Create the ignored project-local file:

```json
{
  "enabled": true,
  "mode": "observe_only",
  "raw_capture": false,
  "snippet_capture": false
}
```

Path:

```text
.groundwork/harness/router-observability/config.json
```

For one local process, `GROUNDWORK_ROUTER_OBSERVABILITY=1` force-enables the same observe-only behavior. Historical values such as `thin_prompt_trial` or `guided_hint_trial` may be preserved as `requested_mode` for diagnosis, but the runtime always records `decision_mode=observe_only` and emits no `additionalContext`.

Hook trust remains a separate Codex runtime boundary. Availability or local source validity does not prove an installed hook was trusted or executed.

## Recorded Signals

Prompt stage records:

- prompt hash and length;
- optional redacted snippet;
- `prompt_route_candidate` from the deterministic classifier;
- classifier source and explicit candidate-only limitation.

Tool and permission stages record:

- event identity and stable ordering fields;
- tool/command class;
- input and response hashes/lengths;
- supported/unsupported coverage status;
- risk and evidence markers.

Stop stage records:

- final hash and length;
- optional redacted snippet;
- `response_shape_candidate`;
- `response_shape_source=response_shape_heuristic`;
- `authoritative_skill_load_trace=unavailable` and `skill_hits=[]` until the host supplies stronger evidence;
- ordered event coverage and malformed-line counts.

These are three distinct concepts:

```text
prompt_route_candidate != authoritative_skill_load_trace != response_shape_candidate
```

No hit rate may treat them as interchangeable.

## Scratch Layout

```text
.groundwork/harness/router-observability/<session-id>/<turn-id>/
  prompt-metadata.json
  router-decision.json
  tool-events.jsonl              # when tool hooks fire
  permission-events.jsonl        # when permission hooks fire
  final-metadata.json
  coverage.json
  prompt.raw.json                # optional raw_capture
  final.raw.txt                  # optional raw_capture
  final.raw.meta.json            # optional raw_capture
```

Runtime hooks do not write `dispatch-decision.json`, `router-score.json`, or `router-card.md`.

## Privacy

`snippet_capture` and `raw_capture` default to `false`. Raw capture, when explicitly enabled, is redacted by default. Unredacted capture additionally requires `GROUNDWORK_ROUTER_OBSERVABILITY_ALLOW_UNREDACTED_RAW_CAPTURE=1` and should be used only in a reviewed private environment.

Hashes reduce exposure but do not make an artifact public. Keep `.groundwork/harness/` ignored and local.

## Offline Improvement Loop

1. Inspect the candidate fields and coverage diagnostics.
2. Reproduce the prompt with a natural eval case; do not copy secrets or private raw content.
3. Obtain authoritative skill-load evidence when the host exposes it; otherwise evaluate behavior and output UX without claiming routing accuracy.
4. Use `evals/verdict_model.py` only in the Maintainer Lab to create reviewed scores or cards.
5. Add a regression row only when the failure is reproducible and the expected route/behavior is source-backed.

## Disable And Failure Behavior

Remove/disable the project config and unset `GROUNDWORK_ROUTER_OBSERVABILITY` to stop capture. Hook entrypoints return success on missing or partial package files and do not interrupt normal Codex use. Set `GROUNDWORK_ROUTER_OBSERVABILITY_DEBUG=1` only for local stderr diagnostics.

## Evidence Boundary

Telemetry does not prove:

- the host loaded a Groundwork skill;
- the response followed that skill causally;
- selector/model/profile enforcement;
- installed-cache/source equivalence;
- hook trust;
- runtime, release, UAT, marketplace, or customer readiness.
