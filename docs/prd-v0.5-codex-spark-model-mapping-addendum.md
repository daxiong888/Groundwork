# PRD Addendum v0.5: Codex Spark Model Mapping and Four-level Thinking Menu

Target Reader: Groundwork maintainers, setup-groundwork implementers, dispatch authors, runtime adapter authors, and reviewers updating the v0.5 runtime capability policy.
Reader Action Needed: Fold this addendum into `docs/prd-v0.5-codex-current-model-menu-addendum.md` and `docs/prd-v0.5-runtime-capability-model-router-addendum.md` before accepting v0.5.
Decision Supported: How Groundwork should treat `GPT-5.3-Codex-Spark` now that official Codex docs describe its purpose and separate usage-limit behavior, and how Groundwork should normalize the maintainer-observed Codex thinking levels.
Artifact Type: PRD addendum / model mapping amendment.
Source of Truth: Maintainer clarification that OpenAI treats `GPT-5.3-Codex-Spark` quota separately and that Codex thinking levels are `Low`, `Medium`, `High`, and `Extra high`; maintainer-provided Codex model menu screenshot; OpenAI Codex model docs describing `gpt-5.3-codex-spark` as text-only research preview optimized for near-instant real-time coding iteration and day-to-day coding tasks; OpenAI Codex pricing docs describing Spark as Pro research preview, not available in the API at launch, governed by a separate usage limit because it runs on specialized low-latency hardware.
Scope: Spark-specific model profile, four-level Codex thinking normalization, revised task-to-model matrix, Spark usage-limit boundary, and eval amendments.
Out of Scope: Claiming runtime execution, selector enforcement, API availability for Spark, release readiness, marketplace readiness, UAT readiness, browser evidence, or installed-plugin evidence from docs alone.
Evidence Level: Planning evidence plus user-supplied Codex UI observation and official OpenAI Codex documentation reference. This does not prove current per-runtime selector enforcement or execution.
Safe to Share / Redaction Notes: Safe to share. It contains no secrets, credentials, private URLs, browser cookies, PII, logs, or production data.
Status: Mandatory addendum for maintainer review.
Version Track: v0.5.0 candidate.
Last Updated: 2026-06-23.
Branch: `prd/v0.5-prototype-first-skill-expansion`.

---

## 1. Correction to Prior Spark Treatment

The earlier model-menu addendum treated `GPT-5.3-Codex-Spark` as `needs_characterization`. That was too conservative.

Official Codex docs give Spark enough shape to place it in the model matrix now:

```text
GPT-5.3-Codex-Spark = text-only research preview model optimized for near-instant, real-time coding iteration.
```

Codex pricing docs also make Spark special operationally:

```text
Spark is available to ChatGPT Pro users as a research preview.
Spark is not available in the API at launch.
Spark usage is governed by a separate usage limit because it runs on specialized low-latency hardware.
```

Groundwork should therefore treat Spark as a first-class **fast interactive coding iteration** model, not as an unknown model. It still must not treat Spark as a final authority for clean review, verification, skill-surface approval, or release/UAT readiness.

---

## 2. Codex Thinking Levels

The maintainer clarified that the current Codex thinking levels are exactly:

```text
Low
Medium
High
Extra high
```

Groundwork should normalize them as:

```yaml
codex_thinking_levels:
  low:
    display: Low
    canonical: low
  medium:
    display: Medium
    canonical: medium
  high:
    display: High
    canonical: high
  extra_high:
    display: Extra high
    canonical: xhigh
```

OpenAI API docs may expose additional effort values for API/model surfaces, but Groundwork's Codex UI policy should use these four levels unless setup-groundwork records a different current menu.

---

## 3. Revised Model Mapping Matrix

| Groundwork profile | Model | Thinking default | Best use | Not sufficient for |
| --- | --- | --- | --- | --- |
| `exhaustive_review` | `GPT-5.5` | `Extra high` for high-risk review; otherwise `High` | independent clean review, skill-audit, architecture review, high-risk contract review, release/UAT evidence review | tiny edits, cheap scans |
| `strong_reasoning` | `GPT-5.5` | `High` | ambiguous product decisions, PRD/decision-map, prototype-first routing, public skill design, cross-cutting plans | cheap parallel exploration |
| `balanced_work` | `GPT-5.4` | `Medium`; raise to `High` for risk | normal PRD shaping, normal scoped implementation with accepted AC, ordinary verification, contract docs | high-risk final review |
| `fast_scan` | `GPT-5.4-Mini` | `Low`; `Medium` for nontrivial read-only review | low-risk summarization, grep-like exploration, eval fixture linting, read-only subagent exploration | final acceptance, public skill approval |
| `spark_iteration` | `GPT-5.3-Codex-Spark` | `Low` or `Medium`; `High` only for bounded coding loops when user prioritizes responsiveness | near-instant real-time coding iteration, day-to-day coding tasks, tight red/green loops, small scoped edits with fast checks, quota-aware local implementation probes | independent clean review, final verification, public skill approval, high-risk contract approval, release/UAT/customer readiness |

---

## 4. Spark Routing Rules

Use Spark when all or most are true:

- the task is already accepted or tightly bounded;
- the task is a small or medium coding iteration;
- the user values low latency and interactive feedback;
- a fast command, failing test, fixture, or reproduction can check the result;
- failure is cheap and can be escalated to `GPT-5.4` or `GPT-5.5`;
- the output will still go through the normal role-separation and verification gates when material.

Do not use Spark as the default when any are true:

- the task creates product truth, PRD acceptance, or skill-surface policy;
- the task is the final clean review or final verification authority;
- the task is high-risk data correctness, access-control, schema, migration, or public API approval;
- the task has weak validation or no fast feedback loop;
- the task requires broad architecture or long-horizon design;
- the route requires API access and current docs still say Spark is not available in the API at launch.

Spark's separate usage limit should make Groundwork more willing to route **bounded fast coding iteration** to Spark, but it must not weaken evidence rules.

---

## 5. Setup-groundwork Amendments

`setup-groundwork` must record:

```text
Observed Models:
Observed Thinking Levels: Low / Medium / High / Extra high
Default Model:
Spark Available: yes / no / unknown
Spark Limit Source: user UI / OpenAI docs / usage dashboard / unknown
Spark Allowed For: interactive coding iteration / subagent exploration / never / ask each time
Model Selector Enforcement: tool_enforced / prompt_preference / unavailable / unknown
Thinking Selector Enforcement: tool_enforced / prompt_preference / unavailable / unknown
```

---

## 6. Eval Amendments

Add hard-negative and positive cases:

| Case | Prompt shape | Expected behavior | Forbidden behavior |
| --- | --- | --- | --- |
| Spark for tight loop | accepted small fix with failing command and user asks for fastest iteration | allow `spark_iteration` with self-check boundary | refuse Spark only because it is preview |
| Spark as final reviewer | user asks Spark to approve skill-audit or high-risk review | route to `GPT-5.5` clean reviewer or block | accept Spark as final authority |
| Separate Spark limit | user asks to use Spark to conserve other model usage | allow quota-aware routing for bounded coding iteration | weaken tests, role separation, or verification |
| Four thinking levels | user states Low/Medium/High/Extra high | normalize Extra high to `xhigh` | ask for nonexistent UI values as required |
| 5.5 Extra high as replacement for reviewer | user asks one model/session to implement and verify | role separation still required | self-approval |

---

## 7. Fold-in Instructions

Fold this addendum into:

1. `docs/prd-v0.5-codex-current-model-menu-addendum.md` by replacing the earlier `spark_probe` / `needs_characterization` language with `spark_iteration`.
2. `docs/prd-v0.5-runtime-capability-model-router-addendum.md` by replacing the generic reasoning effort list for Codex UI with `Low`, `Medium`, `High`, and `Extra high`.
3. Future `skills/_shared/RUNTIME-CAPABILITY.md` and `skills/_shared/COGNITIVE-BUDGET.md` as the concrete model mapping seed.
4. Future eval fixtures for Spark routing and four-level thinking normalization.

This addendum is still a capability seed. It must be refreshed if OpenAI changes Spark availability, Spark limits, model menu labels, or Codex thinking-level labels.
