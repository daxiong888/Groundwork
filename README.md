# Groundwork

Groundwork is a Codex-native personal base for evidence-first R&D work.

It exists to make Codex more useful in real project work where correctness depends on PRD/spec clarity, task state, source code truth, runtime evidence, prototypes, integration contracts, UAT behavior, and careful handoff. It absorbs useful ideas from existing frameworks without requiring those frameworks or copying their full process.

The practical starting point is a curated base: use Superpowers as the Codex plugin packaging reference, use mattpocock/skills as the strongest lightweight workflow/skill reference, and keep Groundwork-specific choices tied to the user's R&D scenarios.

## How maintainers use Groundwork

Groundwork is a lightweight, evidence-first workflow for maintainers using Codex on real open-source work. It complements GitHub issues, CI, and human review; it does not replace them. It helps each change stay tied to a clear request, source-of-truth checks, fresh verification evidence, and a review-ready handoff.

A typical maintainer loop looks like this:

```text
rough request / bug / review concern
  -> to-prd
  -> implement
  -> verify
  -> handoff
  -> review / merge / next issue
```

Maintainers use Groundwork to:

| Maintainer task | Groundwork path | Output |
| --- | --- | --- |
| Clarify an ambiguous feature, bug, or review concern | `to-prd` | A small PRD/spec with known facts, assumptions, unresolved decisions, and acceptance criteria |
| Turn accepted work into scoped implementation | `implement` | Minimal edits, inspected evidence, check results, and remaining gaps |
| Check whether a change is actually supported | `verify` | Scope-first claim-to-evidence mapping across source, tests, runtime, docs, UAT, and unverified claims |
| Transfer work across sessions or reviewers | `handoff` | A compact review package with artifacts, evidence, risks, boundaries, and next action |

Groundwork stays conversation-first for small tasks. Durable artifacts are created only when they are useful for review, reuse, execution, verification, UAT, or handoff.

For Codex for Open Source reviewers, these docs show the maintainer work Groundwork supports: issue clarification, scoped implementation, evidence checks, review transfer, and release handoff.

See [`docs/maintainer-workflows.md`](docs/maintainer-workflows.md) and [`examples/`](examples/) for maintainer-facing workflows and real Groundwork maintenance case studies.

## Current Stage

The current repository contains the hardened public skill surface defined by `docs/prd.md` and later source-validation releases. The dispatch runtime router work introduced `dispatch` as a package-only public skill, scoped by `docs/prd-dispatch-runtime-router.md`, so Groundwork can package accepted work for the lightest appropriate runtime without executing that runtime itself.

The v0.3.3 contract layer hardens managed worktree lifecycle handling behind `dispatch` without adding public skills. It adds package-only contracts for runtime identity, Goal Mode evidence, clean review fan-out, merge-back, archive readiness, branch cleanup, and serial dispatch barriers. Runtime adapters still own execution evidence; Groundwork dispatch remains a package generator, not an executor.

The v0.3.4 governance baseline hardened the then-current nine public skills without adding another skill or runtime. It moved repository-level rules into `AGENTS.md`, expanded audience-first artifact headers, strengthened to-prd/prototype/implement/verify/handoff guardrails, and kept `dispatch` package-only while inheriting the shared done definition and smoke coverage.

The v0.4.0 native worktree handoff alignment shrinks Groundwork back toward route, policy, evidence, handoff, and closeout governance around Codex-native worktrees. It adds native handoff and closeout package contracts, `.worktreeinclude` safety guidance, release-evidence claim boundaries, and eval coverage while keeping Codex App/runtime adapters responsible for actual worktree creation, Handoff execution, runtime execution, and cleanup operations.

The v0.4.x trace-first eval platform work adds a source-validation layer for schema-backed score objects, deterministic checker ids, trace artifact policy, trace diagnostics, eval reports, proposal-only patch suggestions, schema/source CI, optional runtime eval guidance, and release evidence claim templates. Its current evidence status is `source_validation`: local schemas, fixtures, unit tests, source checks, reports, and patch suggestions support implementation review, but they are not runtime, cache, release, UAT, customer, marketplace, or package-readiness evidence.

The v0.5 public skill expansion policy shifts Groundwork from a fixed public-skill-count rule to quality-gated expansion. New public skills require accepted scope plus the shared [`skills/_shared/SKILL-QUALITY.md`](skills/_shared/SKILL-QUALITY.md) checklist, routing review, and positive, negative, and hard-negative eval expectations before merge. Behaviors that do not pass that bar should stay as shared references, branch/workflow lenses, router behavior, or one-off guides.

The v0.5.2 public wiki skill adds project-level LLM Wiki lifecycle support for init, ingest, query, audit, update, deprecate/archive, and repair. Wiki remains source-validation context and claim inventory only; it is not source truth, implementation authority, verification pass evidence, runtime evidence, release evidence, UAT evidence, marketplace evidence, installed-plugin evidence, or cache-refresh evidence.

The v0.5.5 router observability follow-up keeps the dormant plugin-bundled Codex hook definitions and project opt-in hook entrypoints from v0.5.3, while tightening review-fix behavior, score schema coverage, secret redaction, and plugin-cache refresh self-protection. These hooks are observe-only by default and write local scratch artifacts under `.groundwork/harness/router-observability/` only after a project explicitly opts in. Hook cards, scores, and local scratch output are source-validation and improvement evidence only; they are not release, UAT, customer, marketplace, installed-plugin, cache-refresh, or hook-trust evidence by themselves.

This repository currently contains:

- project vision and boundaries
- framework comparison research
- user work scenario analysis
- maintainer workflow documentation
- real maintenance case studies
- Codex plugin manifest
- ten public skills, including `dispatch` and `wiki`
- dormant Codex hook definitions for project opt-in router observability
- standard-library hook entrypoint scripts under `scripts/codex-hooks/`
- native Codex worktree/handoff governance contracts for v0.4.0
- v0.4.x trace-first eval platform source-validation docs, schemas, helpers, checker modules, reports, patch suggestions, CI workflow, and release evidence claim template
- v0.5 public skill expansion policy and shared skill-quality gate
- skill trigger fixtures
- structured smoke and safety fixtures
- skill reliability fixtures
- R&D workflow scenario fixtures
- spec-level, local discovery, runtime, fixture, and App runtime-safety baselines
- runtime trial checklist
- managed worktree lifecycle, clean review, merge-back, and serial barrier contracts for v0.3.3

It intentionally does not yet contain task tools, MCP servers, marketplace publishing flow, local task CRUD, automatic routing mutation, or default trace capture. New non-observability hooks or active runtime behavior should be added only after repeated real usage exposes a need.

## Local Installation

Target Reader: Someone who found this repository and wants to install Groundwork into their local Codex setup.
Reader Action Needed: Register the Groundwork marketplace, install the plugin, and enable it in Codex.
Decision Supported: Whether this repository can be used directly as a local Codex plugin.
Scope: Local personal installation from this repository through Codex's plugin marketplace flow.
Out of Scope: Public marketplace publishing, remote plugin distribution, task CRUD, MCP servers, production integrations, automatic trace capture, and hook-trust or runtime-readiness claims.
Evidence Level: `.agents/plugins/marketplace.json` exposes the plugin to Codex, and `.codex-plugin/plugin.json` declares the plugin metadata, bundled `skills/` path, and dormant hook definitions.

Groundwork is currently intended to be installed as a local personal Codex plugin. The recommended path is to add this repository as a Codex marketplace, then install the plugin from that marketplace:

```bash
codex plugin marketplace add daxiong888/Groundwork --ref main
codex plugin add groundwork@groundwork
```

If you already have Codex open, you can also ask Codex to install it for you:

```text
Install the Groundwork Codex plugin from GitHub. Please run:
codex plugin marketplace add daxiong888/Groundwork --ref main
codex plugin add groundwork@groundwork
Then verify that groundwork@groundwork is installed and enabled.
```

The same marketplace and plugin state is local to the machine. If you use both Codex CLI and the Codex desktop app on the same computer, restart the app or refresh the plugin list after installing from the CLI.

Router observability hooks remain dormant after installation. To opt a project into local observe-only trace capture, see [`docs/router-observability-harness.md`](docs/router-observability-harness.md). Downstream projects that opt in should ignore local scratch output, for example:

```bash
echo ".groundwork/harness/" >> .gitignore
```

If you are testing an unpublished local checkout, add the checkout path as the marketplace source instead:

```bash
git clone https://github.com/daxiong888/Groundwork.git ~/.codex/plugins/groundwork
codex plugin marketplace add ~/.codex/plugins/groundwork
codex plugin add groundwork@groundwork
```

You can also install interactively by running `codex`, opening `/plugins`, choosing the `Groundwork` marketplace, and selecting `Install plugin`. Codex should discover the plugin from `.codex-plugin/plugin.json` and load the public skills from `skills/`.

## Update

To update an installation that was added from GitHub:

```bash
codex plugin marketplace upgrade groundwork
codex plugin add groundwork@groundwork
```

To update an installation that was added from a local checkout:

```bash
cd ~/.codex/plugins/groundwork
git pull --ff-only
codex plugin add groundwork@groundwork
```

Restart Codex or refresh the plugin list after upgrading. You should not need to edit Codex's plugin cache manually; Codex installs plugins under `~/.codex/plugins/cache/<marketplace>/<plugin>/<version>/` and records enabled state in `~/.codex/config.toml`. Router observability hook commands are expected to no-op if an already-running thread still points at an old versioned plugin cache while the cache is being refreshed.

## Working Thesis

Groundwork should help Codex:

1. Turn product intent into PRD/spec and acceptance when the work needs it.
2. Resolve or create lightweight task context when durable state will help, preferring real issue/task sources over local fallback files.
3. Ground claims in local code, docs, runtime behavior, data, and user-provided evidence.
4. Choose the lightest execution path that can produce a trustworthy result.
5. Preserve reviewable artifacts, verification evidence, and handoff context.
6. Avoid turning every task into a heavy framework ceremony.

The target workflow is:

```text
PRD/spec -> task -> plan -> prototype/contract/design as needed -> implementation -> verification/UAT -> release/handoff
```

## Non-Goals

- Replace global `AGENTS.md`.
- Clone Trellis, Superpowers, gstack, GSD, or mattpocock/skills.
- Become a loose bundle of borrowed skills without a Groundwork workflow boundary.
- Compete with existing frameworks as a product-positioning exercise.
- Force every task into PRDs, issues, ADRs, or subagents.
- Treat integration contract as a substitute for PRD/spec.
- Mutate shared skills used by other coding agents.
- Hide uncertainty or skip verification for speed.

## Repository Map

- `PROJECT.md` - product definition and success criteria
- `docs/prd.md` - MVP PRD and review entry point
- `docs/borrowed-source-decisions.md` - borrowed source adoption decisions
- `research/framework-comparison.md` - source framework analysis
- `research/user-work-scenarios.md` - real work scenarios Groundwork must support
- `docs/product-principles.md` - principles that guide design
- `docs/maintainer-workflows.md` - maintainer-facing Groundwork workflow guide
- `docs/workflow-taxonomy.md` - proposed workflow modes and trigger policy
- `docs/plugin-architecture.md` - staged Codex plugin architecture
- `examples/` - real Groundwork maintenance case studies and draft previews
- `.codex-plugin/plugin.json` - Codex plugin manifest
- `skills/` - public skills, including `dispatch` and `wiki`
- `evals/` - prompt fixtures, scenario fixtures, fixture repo, baselines, and runtime trial checklist
