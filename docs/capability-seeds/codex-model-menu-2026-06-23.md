# Codex Model Menu Capability Seed - 2026-06-23

Target Reader: Groundwork maintainers, runtime capability policy implementers, dispatch authors, skill-audit reviewers, and verifier roles.
Reader Action Needed: Use this as a dated capability seed only; refresh or replace it before making current runtime/model availability claims.
Decision Supported: How v0.5 should seed model profile examples from a user-observed Codex model menu without overclaiming runtime execution, reasoning support, selector enforcement, or universal availability.
Artifact Type: capability seed.
Source of Truth: User-supplied review context and branch-local addenda describing a maintainer-observed Codex model menu on 2026-06-23.
Scope: Visible model labels, selected model, observed Codex UI thinking labels, provisional Groundwork model-profile mapping, and explicit not-proven boundaries.
Out of Scope: Official current model availability verification; API availability; per-subagent or per-worktree availability; selector enforcement; runtime execution; installed-plugin, release, marketplace, UAT, browser, or customer readiness.
Evidence Level: User-supplied observation seed. This file is not runtime/tool enforcement evidence and was not refreshed against official documentation in this PRD consolidation pass.
Safe to Share / Redaction Notes: Safe to share. No screenshot, credentials, private URLs, cookies, PII, logs, or production data are stored in this file.
Status: Supporting seed only; not an acceptance gate by itself.
Observed At: 2026-06-23.

---

## Observed Model Labels

The planning context recorded these visible Codex model menu labels:

```text
GPT-5.5
GPT-5.4
GPT-5.4-Mini
GPT-5.3-Codex-Spark
```

The context also recorded `GPT-5.5` as selected.

Screenshot status:

```text
screenshot_redacted_path_or_not_available: not_available_in_repo
source_type: user_supplied_observation
```

## Observed Thinking Labels

The planning context recorded these Codex UI thinking labels:

```text
Low
Medium
High
Extra high
```

Groundwork normalization:

| UI label | Groundwork canonical value |
| --- | --- |
| Low | `low` |
| Medium | `medium` |
| High | `high` |
| Extra high | `xhigh` |

These are Codex UI observed labels, not a universal API reasoning-effort list.

## Capability Seed

```yaml
runtime_capability_seed:
  observed_by: maintainer
  observed_at: 2026-06-23
  source_type: user_supplied_observation
  codex_surface: unknown_codex_ui_surface
  exact_visible_labels:
    - GPT-5.5
    - GPT-5.4
    - GPT-5.4-Mini
    - GPT-5.3-Codex-Spark
  selected_label: GPT-5.5
  observed_thinking_labels:
    - Low
    - Medium
    - High
    - Extra high
  screenshot_redacted_path_or_not_available: not_available_in_repo
  not_proven:
    - selector enforcement
    - reasoning selector enforcement
    - per-subagent model or thinking control
    - per-worktree model or thinking control
    - child-thread/worktree availability
    - subagent availability
    - runtime execution
    - current availability in every Codex surface
    - API availability
```

## Provisional Profile Mapping

Use only when current runtime capability evidence confirms the same or equivalent menu.

| Groundwork profile | Provisional model | Thinking preference | Boundary |
| --- | --- | --- | --- |
| `exhaustive_review` | `GPT-5.5` | `Extra high` or `High` | Not a substitute for role separation or evidence. |
| `strong_reasoning` | `GPT-5.5` | `High` | For ambiguous product, PRD, prototype-first, and public skill decisions. |
| `balanced_work` | `GPT-5.4` | `Medium`; raise to `High` for risk | For normal scoped work with accepted source truth. |
| `fast_scan` | `GPT-5.4-Mini` | `Low` or `Medium` | Not final authority for high-risk review/readiness. |
| `spark_iteration` | `GPT-5.3-Codex-Spark` | `Low` or `Medium`; `High` only for bounded loops | Bounded fast coding iteration only; not clean review, final verification, public skill approval, UAT, release, or customer authority. |

## Refresh Rules

Refresh or replace this seed when:

- the maintainer's Codex menu changes;
- implementation depends on a concrete model;
- dispatch or final reports would claim selector enforcement;
- subagent or child-thread runtime availability affects the route;
- a release/runtime readiness claim references model selection;
- official docs or runtime adapter reports provide stronger current evidence.
