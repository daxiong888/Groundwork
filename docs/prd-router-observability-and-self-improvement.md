# PRD: Groundwork Router Telemetry and Improvement Loop

Target Reader: Groundwork maintainers and eval authors responsible for improving route boundaries without increasing runtime coupling.

Reader Action Needed: Maintain the telemetry/runtime boundary, use reviewed traces to design offline regressions, and reject changes that turn observability into a second router.

Decision Supported: Which signals belong in the installed runtime, which analyses belong in the Maintainer Lab, and what evidence is required before claiming routing improvement.

Artifact Type: accepted product and architecture contract.

Source of Truth: `scripts/codex-hooks/groundwork_router_event.py`, `scripts/codex-hooks/groundwork_route_registry.json`, `scripts/codex-hooks/groundwork_route_detection.py`, `scripts/codex-hooks/groundwork_router_telemetry.py`, `hooks/hooks.json`, `docs/router-observability-harness.md`, and `evals/verdict_model.py`.

Scope: dormant observe-only hooks, project opt-in, privacy controls, minimized telemetry, candidate signal separation, offline evaluation, human-reviewed regression promotion, and runtime complexity limits.

Out of Scope: a new public router skill, prompt injection, guided modes, live verdicts/cards, profile inference, learned routing, automatic skill mutation, automatic CSV/PR/issue writes, runtime execution, and readiness claims.

Evidence Level: current source contract. Installed-cache execution and real routing quality require separate runtime evidence.

Safe to Share / Redaction Notes: Safe to share as architecture. Local telemetry remains private until reviewed and redacted.

Status: implemented source contract; installed runtime verification remains a separate gate.

Last Updated: 2026-07-14.

## Problem

Groundwork needs usage signals to improve over time, but observability becomes counterproductive when it:

- reimplements route selection independently from public skill contracts;
- changes prompts while claiming to observe them;
- calls output-shape similarity an actual route;
- infers model/reasoning selectors from keywords;
- performs live scoring and card generation on every turn;
- expands the installed kernel faster than the behavior it measures.

The required product is therefore telemetry, not a live evaluator.

## Goals

1. Preserve a low-cost, opt-in signal path for real Groundwork usage.
2. Keep prompt, skill-load, response-shape, tool, and permission evidence distinct.
3. Default to hashes and metadata; require explicit opt-in for snippets or raw capture.
4. Keep hooks non-blocking and behavior-neutral.
5. Move scoring, profile analysis, cards, replay, and regression promotion into the Maintainer Lab.
6. Allow future authoritative host traces without changing the meaning of existing candidate fields.

## Runtime Contract

### Activation

- Hooks are dormant unless project config enables them or `GROUNDWORK_ROUTER_OBSERVABILITY=1` is set.
- All supported events use one lightweight entrypoint. Unless the environment force-enable is set, absent, invalid, or disabled config exits after parsing the event and checking activation, before importing telemetry or the route classifier.
- Installed hook availability is not hook trust or proof of execution.
- The only supported runtime behavior is `observe_only`.
- Runtime hooks never emit `additionalContext`.

### Prompt Signal

The prompt hook records a deterministic `prompt_route_candidate`. It is a route-only hypothesis from the shared registry/classifier, not evidence about requirement state, source truth, risk, lifecycle transition, actual route, or host skill loading.

When native turn identity is unavailable, prompt submission creates a unique session-scoped fallback turn id and subsequent captured events reuse it. Event-local ids must not fragment one turn or merge multiple prompts into one transcript-level record.

### Skill-Load Signal

Until Codex exposes an authoritative per-turn skill-load trace, runtime artifacts must record:

```json
{
  "authoritative_skill_load_trace": "unavailable",
  "skill_hits": []
}
```

No downstream metric may fill `skill_hits` from prompt classification or final output.

### Response Signal

The Stop hook may classify visible response shape, but must name it `response_shape_candidate` with `response_shape_source=response_shape_heuristic`. It must not emit `actual_route`.

### Tool And Permission Signals

Hooks may record minimized event metadata, hashes, command classes, risk/evidence markers, and per-record observation status. The resulting counts describe only records captured by the configured hook registrations and matchers. Among parsed records, `observed_supported` and `unsupported` form the classified-event denominator; malformed records and parsed records without a recognized status are counted separately. These counts must not be presented as all-host-event coverage, hook execution coverage, or host capability coverage.

### Privacy

- `snippet_capture=false` and `raw_capture=false` by default.
- Raw capture requires explicit project/process opt-in and is always redacted by runtime hooks; semantic reproduction that truly needs unredacted input belongs in a separately approved maintainer-only workflow.
- Local scratch stays under ignored `.groundwork/harness/router-observability/`.
- Secrets, credentials, cookies, PII, private payloads, and unreviewed raw text must not be promoted.

## Maintainer Lab Contract

Offline analysis may:

- replay natural prompts;
- compare source-backed expected behavior;
- score output contracts and evidence boundaries;
- measure visible-output UX;
- generate reviewed router cards or reports;
- draft regression rows after human review.

Offline analysis must keep three test concerns orthogonal:

| Concern | Question | Required Evidence |
| --- | --- | --- |
| Discovery | What did the host actually load? | Authoritative host skill-load trace; otherwise unknown. |
| Behavior | Was the answer/action safe and semantically correct? | Prompt, source-backed expectation, tool/result evidence. |
| Output UX | Was the answer concise, outcome-first, and free of empty scaffolding? | Full final response and explicit UX metrics. |

A behavior or output pass cannot substitute for discovery evidence.

## Single Route Truth

`scripts/codex-hooks/groundwork_route_registry.json` is the canonical machine-readable registry for:

- public route names;
- state acceptance/production contracts;
- prompt precedence;
- default forbidden routes;
- skill-description boundary fragments.

Classifier behavior, public metadata, state-machine docs, and eval expectations must validate against the registry. Regexes may implement language recognition, but they must not create an independent route taxonomy.

## Required Metrics

The telemetry layer should make these raw, non-judgmental measurements available:

- opted-in turn count;
- prompt and final lengths;
- prompt-route candidate distribution;
- response-shape candidate distribution;
- authoritative skill-trace availability rate;
- tool/permission event counts;
- captured-record, parsed-event, classified-event, observed-supported, observed-unsupported, unclassified, and malformed counts, scoped to captured hook records only;
- capture/redaction mode distribution.

Routing accuracy, false-positive rate, profile quality, or pass/fail verdicts are offline derived metrics and require evidence appropriate to their claim.

## Acceptance Criteria

- Hooks no-op without opt-in and do not create `.groundwork` scratch.
- Unless environment force-enable is set, disabled, absent, or invalid activation exits before importing runtime telemetry or the route classifier.
- Observe-only prompt hooks emit no model-visible context.
- Candidate fields are distinctly named and do not use `actual_route`.
- Missing skill-load evidence is represented as unavailable with empty hits.
- Stop hooks write metadata and coverage, not live scores/cards/profile recommendations.
- Tool and permission events have deterministic replay ordering plus captured-record diagnostics that separate observed-supported, observed-unsupported, unclassified, and malformed records.
- Secret redaction covers supported token/password/key patterns.
- Runtime hook files import no source-only `evals` package.
- Package boundary checks include every runtime telemetry dependency.
- Maintainer-side verdict/card helpers remain source-only.

## Non-Goals And Hard Negatives

- Do not restore `thin_prompt_trial` or `guided_hint_trial` in runtime hooks.
- Do not add route-specific prompt hints under another mode name.
- Do not infer model profile or reasoning effort from prompt keywords in the installed package.
- Do not generate `dispatch-decision.json`, `router-score.json`, or `router-card.md` at Stop.
- Do not call output markers actual skill use.
- Do not automatically mutate skills, eval CSV, GitHub, trackers, or automations.

## Verification

Source validation must cover:

- hook opt-in/no-op behavior;
- no additional context for historical behavior-shaping mode values;
- hash/redaction behavior;
- candidate naming and unavailable skill trace;
- tool/permission ordering and captured-record diagnostics, without host-wide coverage claims;
- absence of runtime score/card/profile artifacts;
- route registry parity;
- generated runtime package contents.

Installed runtime claims additionally require a supported package/cache refresh and a named installed plugin root.

## Remaining Unknowns

- Codex host support for authoritative skill-load traces.
- Real per-turn latency and disk cost across representative projects.
- Which public routes deliver the lowest user value; telemetry does not yet prove a removal candidate.
- Appropriate retention and aggregation policy for long-running local trials.
