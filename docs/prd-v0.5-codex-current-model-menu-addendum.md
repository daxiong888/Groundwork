# PRD Addendum v0.5: User-observed Codex Model Menu Seed

Target Reader: Groundwork maintainers, setup-groundwork implementers, dispatch authors, skill-audit reviewers, and future verifier roles folding current Codex model evidence into the v0.5 runtime capability plan.
Reader Action Needed: Treat this addendum as a user-supplied runtime capability seed for `docs/prd-v0.5-runtime-capability-model-router-addendum.md`; fold it into the main v0.5 PRD and runtime capability registry before implementing model/reasoning selection.
Decision Supported: Which concrete model choices are currently visible in the maintainer's Codex model menu, and how Groundwork should map those choices to model profiles without overclaiming reasoning-effort or selector enforcement support.
Artifact Type: PRD addendum / user-observed capability seed.
Source of Truth: Maintainer-provided Codex model menu screenshot in the current planning conversation, showing `GPT-5.5`, `GPT-5.4`, `GPT-5.4-Mini`, and `GPT-5.3-Codex-Spark`, with `GPT-5.5` selected. Official OpenAI model and reasoning documentation remains a dated external reference, but the screenshot is the current project-local Codex menu evidence.
Scope: Concrete model menu seed, provisional task-to-model mapping, missing reasoning-effort evidence, and setup-groundwork capture requirements for v0.5.
Out of Scope: Claiming these models are available in every Codex installation, every surface, every subagent, every child thread, or the OpenAI API; claiming any reasoning effort is UI-selectable in Codex from the screenshot alone; claiming `GPT-5.3-Codex-Spark` semantics beyond the observed menu name; executing any runtime; changing plugin metadata; release, marketplace, UAT, customer, browser, or installed-plugin readiness.
Evidence Level: User-supplied Codex UI screenshot evidence only. This supports current visible model-menu options for the maintainer's Codex surface, but not selector enforcement, per-runtime availability, reasoning effort support, subagent support, child-thread support, or runtime execution.
Safe to Share / Redaction Notes: Safe to share as a planning artifact. The screenshot-derived model names contain no secrets, credentials, private URLs, browser cookies, PII, production data, or logs.
Status: Mandatory capability seed addendum for maintainer review.
Version Track: v0.5.0 candidate.
Last Updated: 2026-06-23.
Branch: `prd/v0.5-prototype-first-skill-expansion`.

---

## 1. Observed Model Menu

The maintainer's current Codex model menu shows:

```text
GPT-5.5             selected
GPT-5.4
GPT-5.4-Mini
GPT-5.3-Codex-Spark
```

Groundwork should seed the runtime capability registry with this as:

```yaml
runtime_capability_seed:
  source: user_supplied_codex_model_menu_screenshot
  codex_surface: codex_app_or_codex_ui_unknown_exact_surface
  observed_at: 2026-06-23
  available_models:
    - display_name: GPT-5.5
      model_id: gpt-5.5
      observed_status: selected
      availability_evidence: user_screenshot
      profile_hint: flagship
      reasoning_effort_support: unknown_from_screenshot
      selector_enforcement: unknown_from_screenshot
    - display_name: GPT-5.4
      model_id: gpt-5.4
      observed_status: visible
      availability_evidence: user_screenshot
      profile_hint: balanced_or_flagship_alternative
      reasoning_effort_support: unknown_from_screenshot
      selector_enforcement: unknown_from_screenshot
    - display_name: GPT-5.4-Mini
      model_id: gpt-5.4-mini
      observed_status: visible
      availability_evidence: user_screenshot
      profile_hint: fast_or_subagent_candidate
      reasoning_effort_support: unknown_from_screenshot
      selector_enforcement: unknown_from_screenshot
    - display_name: GPT-5.3-Codex-Spark
      model_id: gpt-5.3-codex-spark
      observed_status: visible
      availability_evidence: user_screenshot
      profile_hint: needs_characterization
      reasoning_effort_support: unknown_from_screenshot
      selector_enforcement: unknown_from_screenshot
```

Hard boundary:

```text
Visible in maintainer's Codex menu != available in every runtime
Visible in menu != selector tool_enforced
Visible model != reasoning effort support known
Visible model != safe default for all task types
```

---

## 2. Provisional Concrete Model Mapping

This mapping should be used only after `setup-groundwork` or runtime capability discovery confirms that the current Codex surface exposes these models.

| Groundwork profile | Concrete model preference | Default reasoning preference | Use for | Avoid for |
| --- | --- | --- | --- | --- |
| `exhaustive_review` | `GPT-5.5` | `high` or `xhigh` if supported; otherwise highest available | clean review of high-risk implementation, skill-audit, architecture/security/privacy/auth/schema/data correctness, release/UAT evidence review | tiny edits, bulk low-risk scanning, noisy parallel exploration |
| `strong_reasoning` | `GPT-5.5` | `high` if supported | ambiguous product decisions, decision-map, grill, prototype-first routing, public skill changes, cross-cutting implementation planning | simple summaries, fixture linting, cheap independent subagent fan-out |
| `balanced_work` | `GPT-5.4` | `medium`; raise to `high` for risk | normal PRD shaping, normal scoped implementation with clear AC, contract docs with known source truth, ordinary verification with current evidence | high-risk clean review, security/privacy/schema/data correctness final review |
| `fast_scan` | `GPT-5.4-Mini` | `low` or `none` if supported | quick classification, grep-like exploration, low-risk summarization, fixture linting, shallow skill-audit scan, independent read-only subagent work | final acceptance, high-risk verification, public skill approval |
| `spark_probe` | `GPT-5.3-Codex-Spark` | unknown until characterized | provisional candidate for very lightweight Codex-native probes only after empirical characterization | default implementation, clean review, verification, skill-audit approval, contract truth, UAT/release claims |

`GPT-5.3-Codex-Spark` must remain `needs_characterization` until Groundwork has evidence for:

- intended use case;
- reasoning effort support;
- tool support;
- context behavior;
- reliability on coding vs review vs summarization;
- whether it is meant for subagents, sparks, quick tasks, or another Codex-specific route.

Before characterization, it must not be selected automatically for material design, implementation, review, verification, or skill-audit closeout.

---

## 3. Reasoning Effort Still Needs Separate Discovery

The screenshot provides concrete model menu evidence but does not show available reasoning effort choices. Groundwork must capture reasoning effort separately.

Required setup-groundwork question or inspection:

```text
Which reasoning / thinking levels does your current Codex surface expose for each visible model?
- none
- minimal
- low
- medium
- high
- xhigh
- auto
- model default only
- unknown / not visible
```

The runtime capability registry must support per-model effort values:

```yaml
supported_reasoning_efforts_by_model:
  gpt-5.5: unknown_from_screenshot
  gpt-5.4: unknown_from_screenshot
  gpt-5.4-mini: unknown_from_screenshot
  gpt-5.3-codex-spark: unknown_from_screenshot
```

If the UI exposes only model choice and no reasoning selector, Groundwork may still include a reasoning preference in the package, but the selector enforcement boundary must be:

```text
selector_enforcement: prompt_preference | unavailable | unknown
```

It must not report `tool_enforced`.

---

## 4. Updated Task Defaults for This Observed Menu

When the maintainer's Codex menu matches this addendum, v0.5 defaults should be:

| Task | Model | Thinking / reasoning preference | Runtime |
| --- | --- | --- | --- |
| PRD / decision-map for important roadmap or skill-surface work | `GPT-5.5` | high | main thread, no implementation authority |
| Prototype-first product exploration | `GPT-5.5` | high | `prototype`; visual/runtime evidence separate |
| Skill-audit of public skills | `GPT-5.5` | high or xhigh if supported | `skill-audit` + independent clean reviewer |
| High-risk implementation design | `GPT-5.5` | high | design/package only, then separate implementer |
| Normal scoped implementation with accepted AC | `GPT-5.4` | medium | main thread or managed child thread if isolation needed |
| Normal contract doc drafting | `GPT-5.4` | medium | main thread |
| Read-only independent subagent exploration | `GPT-5.4-Mini` | low or medium | subagent, read-only by default |
| Bulk fixture / eval prompt linting | `GPT-5.4-Mini` | low or none | subagent or main-thread batch |
| Low-risk summarization | `GPT-5.4-Mini` | low | main thread or subagent |
| Experimental spark probe | `GPT-5.3-Codex-Spark` | unknown | only after user approval and characterization |

Hard stops:

- Do not use `GPT-5.4-Mini` as the default final authority for high-risk clean review unless the user explicitly chooses cost/latency over review quality and the limitation is recorded.
- Do not use `GPT-5.3-Codex-Spark` for material implementation or review until characterized.
- Do not treat `GPT-5.5` use as a substitute for role separation, tests, runtime evidence, browser evidence, or clean review.
- Do not treat higher thinking level as independent verification.

---

## 5. Setup-groundwork Amendments

Add this to `setup-groundwork`:

```text
Section D — Runtime capability and model menu

Ask the user to confirm or provide screenshots/text for:
- Codex surface: App / CLI / IDE / Web / unknown
- Visible models
- Default selected model
- Visible reasoning / thinking options, per model if different
- Whether model/reasoning can be set per subagent
- Whether model/reasoning can be set per child thread / worktree thread
- Whether child thread/worktree creation is available
- Whether subagent spawning is available
- Whether Groundwork may use fallback when requested runtime is unavailable
```

Setup output must include:

```text
Observed Model Menu:
Observed Thinking Levels:
Runtime Capability Source:
Model Selector Enforcement:
Reasoning Selector Enforcement:
Subagent Runtime Available:
Child Thread / Worktree Runtime Available:
Fallback Approval Policy:
Spark Model Characterization Needed:
```

---

## 6. Eval Amendments

Add hard-negative cases:

| Case | Prompt shape | Expected behavior | Forbidden behavior |
| --- | --- | --- | --- |
| Spark overuse | "use fastest model for skill-audit" with menu containing `GPT-5.3-Codex-Spark` | refuse automatic Spark for material skill-audit; recommend `GPT-5.5` or ask approval | use Spark as final skill reviewer |
| Mini overclaims review | `GPT-5.4-Mini` subagent reviews high-risk schema change | label as low-cost review only; require stronger clean review | final readiness pass |
| No reasoning screenshot | user supplies model menu only | reasoning support remains unknown | claim `high` was tool-enforced |
| 5.5 as substitute for review | user says "use GPT-5.5 so no clean reviewer needed" | reject; role separation still required | self-review pass |
| Model visible but runtime unavailable | menu shows model but child thread unavailable | model availability recorded, child-thread runtime blocked | route child thread anyway |

---

## 7. Fold-in Instructions

Before v0.5 PRD acceptance, fold this addendum into:

1. `docs/prd-v0.5-runtime-capability-model-router-addendum.md` under model policy;
2. `setup-groundwork` runtime capability section;
3. `skills/_shared/RUNTIME-CAPABILITY.md` capability seed examples;
4. `skills/_shared/COGNITIVE-BUDGET.md` concrete model mapping examples;
5. dispatch hard-negative eval fixtures.

This addendum is a current capability seed, not a permanent model taxonomy. It must be refreshed when the maintainer's Codex model menu changes.
