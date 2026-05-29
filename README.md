# Groundwork

Groundwork is a Codex-native personal base for evidence-first R&D work.

It exists to make Codex more useful in real project work where correctness depends on PRD/spec clarity, task state, source code truth, runtime evidence, prototypes, integration contracts, UAT behavior, and careful handoff. It absorbs useful ideas from existing frameworks without requiring those frameworks or copying their full process.

The practical starting point is a curated base: use Superpowers as the Codex plugin packaging reference, use mattpocock/skills as the strongest lightweight workflow/skill reference, and keep Groundwork-specific choices tied to the user's R&D scenarios.

## Current Stage

Current `main` contains v0.2.0 Skill Reliability Hardening. `docs/prd.md` remains the product source of truth; v0.2.0 hardens the existing eight public skills instead of expanding the public surface.

This repository currently contains:

- project vision and boundaries
- framework comparison research
- user work scenario analysis
- Codex plugin manifest
- eight first-cut public skills
- skill trigger fixtures
- structured smoke and safety fixtures
- skill reliability fixtures
- R&D workflow scenario fixtures
- spec-level, local discovery, runtime, fixture, and App runtime-safety baselines
- runtime trial checklist

It intentionally does not yet contain task tools, hooks, MCP servers, marketplace publishing flow, or local task CRUD. Those should be added only after repeated real usage exposes a need.

## Local Installation

Target Reader: Someone who found this repository and wants to install Groundwork into their local Codex setup.
Reader Action Needed: Register the Groundwork marketplace, install the plugin, and enable it in Codex.
Decision Supported: Whether this repository can be used directly as a local Codex plugin.
Scope: Local personal installation from this repository through Codex's plugin marketplace flow.
Out of Scope: Public marketplace publishing, remote plugin distribution, task CRUD, hooks, MCP servers, and production integrations.
Evidence Level: `.agents/plugins/marketplace.json` exposes the plugin to Codex, and `.codex-plugin/plugin.json` declares the plugin metadata and bundled `skills/` path.

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

If you are testing an unpublished local checkout, add the checkout path as the marketplace source instead:

```bash
git clone https://github.com/daxiong888/Groundwork.git ~/.codex/plugins/groundwork
codex plugin marketplace add ~/.codex/plugins/groundwork
codex plugin add groundwork@groundwork
```

You can also install interactively by running `codex`, opening `/plugins`, choosing the `Groundwork` marketplace, and selecting `Install plugin`. Codex should discover the plugin from `.codex-plugin/plugin.json` and load the eight public skills from `skills/`.

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

Restart Codex or refresh the plugin list after upgrading. You should not need to edit Codex's plugin cache manually; Codex installs plugins under `~/.codex/plugins/cache/<marketplace>/<plugin>/<version>/` and records enabled state in `~/.codex/config.toml`.

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
- `docs/workflow-taxonomy.md` - proposed workflow modes and trigger policy
- `docs/plugin-architecture.md` - staged Codex plugin architecture
- `.codex-plugin/plugin.json` - Codex plugin manifest
- `skills/` - eight shallow public skills
- `evals/` - prompt fixtures, scenario fixtures, fixture repo, baselines, and runtime trial checklist
