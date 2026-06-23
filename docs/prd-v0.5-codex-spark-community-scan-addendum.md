# PRD Addendum v0.5: Codex Spark Community and Third-party Signal Scan

Target Reader: Groundwork maintainers, setup-groundwork implementers, dispatch authors, runtime adapter authors, and reviewers updating the v0.5 Spark routing policy.
Reader Action Needed: Use this scan as supporting evidence for Spark routing policy, but do not treat community commentary as runtime proof or final benchmark evidence.
Decision Supported: Whether community and third-party signals support using `GPT-5.3-Codex-Spark` for bounded fast coding iteration, and whether Groundwork should avoid using it as final review or verification authority.
Artifact Type: PRD addendum / external signal scan.
Source of Truth: Web search performed on 2026-06-23 over official OpenAI Codex docs, OpenAI Codex pricing docs, third-party press coverage, and targeted searches for Reddit, Hacker News, and OpenAI Community forum discussion using terms including `Codex Spark`, `GPT-5.3-Codex-Spark`, `Reddit`, `Hacker News`, and `community.openai.com`.
Scope: Public external signal scan for Spark's perceived use cases, strengths, and limitations.
Out of Scope: Claiming representative user sentiment from sparse search results; treating press summaries as independent benchmarks; claiming API availability; executing Spark; evaluating Spark against Groundwork fixtures; release, UAT, marketplace, browser, or installed-plugin readiness.
Evidence Level: External-source planning evidence only. Official docs provide product positioning; third-party press provides interpreted launch/usage framing; direct high-signal community forum evidence was sparse in search results.
Safe to Share / Redaction Notes: Safe to share. It contains no secrets, credentials, private URLs, browser cookies, PII, production data, or logs.
Status: Mandatory supporting addendum for maintainer review.
Version Track: v0.5.0 candidate.
Last Updated: 2026-06-23.
Branch: `prd/v0.5-prototype-first-skill-expansion`.

---

## 1. Executive Finding

External signal supports treating Spark as a fast coding-iteration model rather than an unknown model.

The strongest supported use cases are:

```text
- near-instant real-time coding iteration
- day-to-day coding tasks
- small scoped edits
- targeted test/edit loops
- interruptible coding tasks
- interactive code editing and testing workflows
- quota-aware fast implementation probes
```

The search did not find enough stable high-signal Reddit, Hacker News, or OpenAI Community forum threads to treat community sentiment as representative. Therefore Groundwork should use official positioning and third-party launch analysis for provisional routing, then add local Groundwork Spark characterization evals before making stronger claims.

---

## 2. Official Signal

OpenAI Codex model docs describe `gpt-5.3-codex-spark` as a text-only research preview model optimized for near-instant, real-time coding iteration and available to ChatGPT Pro users. The same docs recommend starting with `gpt-5.5` for most Codex tasks, using `gpt-5.4-mini` for lighter coding tasks or subagents, and using Spark for near-instant real-time coding iteration.

OpenAI Codex pricing docs describe Spark as a Pro research preview and say its usage is governed by a separate usage limit because it runs on specialized low-latency hardware. They also state Spark is not available in the API at launch.

Groundwork interpretation:

```text
Spark is a product-positioned fast coding loop model.
Spark is not a general replacement for GPT-5.5 or GPT-5.4.
Spark's separate quota is routing-relevant but not evidence-relevant.
Spark's research-preview status and API limitation must be visible in runtime capability output.
```

---

## 3. Third-party Signal

Third-party launch coverage frames Spark as:

```text
- lower-latency Codex variant
- fast, interruptible coding-task model
- interactive development workflow model
- useful for editing specific code sections and running targeted tests
- served on specialized low-latency Cerebras hardware
- capable of very high throughput under suitable conditions
```

Tom's Hardware reports that Spark supports interactive code editing and testing workflows, is tuned for fast interruptible coding tasks, defaults to minimal edits, and does not automatically execute commands unless prompted.

Business/press coverage around Codex capacity issues also suggests developers actively switch or are forced between Codex models when capacity changes. That is a general Codex model-routing signal, not Spark-specific usage evidence.

Groundwork interpretation:

```text
Spark should prefer minimal, bounded code edits.
Spark should pair with explicit commands/tests rather than autonomous broad refactors.
Spark should be especially useful when the user is actively supervising an edit/test loop.
Spark should not silently run commands or be assumed to have executed checks.
```

---

## 4. Direct Community Signal Boundary

Targeted searches for direct community discussion did not surface enough stable, high-signal results from:

```text
- Reddit
- Hacker News
- OpenAI Community forum
- query variants around Codex Spark, GPT-5.3-Codex-Spark, review, benchmark, and usage
```

This does not prove the community has no opinions. It means this PRD should not claim a representative community consensus yet.

Required next evidence:

```text
- collect maintainer's own Spark trials in Groundwork fixture repo
- collect high-signal posts when they appear
- run local A/B comparisons against GPT-5.4 and GPT-5.4-Mini
- separate latency, command success, patch size, regression rate, and review findings
```

---

## 5. Groundwork Routing Update

Add `spark_iteration` as a first-class profile:

```yaml
spark_iteration:
  model: GPT-5.3-Codex-Spark
  thinking_default: Low or Medium
  use_for:
    - bounded fast coding iteration
    - day-to-day code edits
    - edit/test loops
    - targeted bug fixes with fast reproduction
    - fixture or harness repair with clear failure command
    - quota-aware implementation probe
  evidence_boundary:
    - self-check only unless independently reviewed
    - not final clean review
    - not final verification
    - not release or UAT authority
  escalation:
    - GPT-5.4 for normal completion when Spark stalls or over-edits
    - GPT-5.5 for design uncertainty, high-risk review, or policy decisions
```

---

## 6. Community-informed Task Matrix

| Task | Spark fit | Reason |
| --- | --- | --- |
| Small accepted code edit with fast test | Strong | Matches low-latency edit/test loop. |
| Targeted bug fix with known reproduction | Strong | Fast interruptible loop plus clear command evidence. |
| Fixture/eval harness repair | Strong | Clear failure command and limited scope. |
| Prototype code polish | Medium | Good when throwaway and bounded; still needs contract boundary. |
| Broad refactor | Weak | Needs stronger planning/review and likely larger context. |
| Public skill design | Weak | Product/policy reasoning should use GPT-5.5. |
| Clean review | Weak | Spark can provide a cheap auxiliary pass but not final authority. |
| Final verification/readiness | Not allowed | Role separation and evidence requirements dominate model choice. |
| Security/privacy/schema/data correctness approval | Not allowed as final authority | High-risk review needs strongest reviewer and independent evidence. |

---

## 7. Eval Amendments

Add these Spark characterization evals before relying on Spark beyond the provisional routing policy:

| Case | Prompt shape | Metric | Expected boundary |
| --- | --- | --- | --- |
| spark-small-fix | accepted small bug with failing unit test | latency, patch size, test pass | self-check only, clean review required if material |
| spark-fixture-repair | broken eval fixture or schema fixture | command pass, minimal diff | no product truth creation |
| spark-targeted-regression | one known failing command | original command rerun | no broad refactor |
| spark-prototype-polish | throwaway UI prototype polish | visual packet boundary | no backend contract promotion |
| spark-broad-refactor-negative | broad architecture request | should route away from Spark | no Spark default |
| spark-final-review-negative | user asks Spark to approve high-risk work | block or route to GPT-5.5 clean reviewer | no final authority |

---

## 8. Fold-in Instructions

Fold this addendum into:

1. `docs/prd-v0.5-codex-spark-model-mapping-addendum.md` under Spark routing rules.
2. `docs/prd-v0.5-runtime-capability-model-router-addendum.md` under model policy and eval amendments.
3. Future `skills/_shared/COGNITIVE-BUDGET.md` as the `spark_iteration` profile rationale.
4. Future eval fixtures as local characterization cases.

This addendum should be refreshed when direct community evidence becomes more available or when Groundwork collects local Spark trial data.
