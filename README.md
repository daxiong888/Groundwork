# Groundwork

Groundwork is a lightweight Codex plugin for evidence-first R&D work. It helps Codex handle non-trivial tasks without turning every request into a heavy process.

Use it when a task needs clearer requirements, scoped implementation, verification evidence, a compact handoff, dispatch packaging, or project wiki maintenance. Small, obvious, low-risk questions should stay direct.

Target Reader: Codex users evaluating or installing Groundwork.
Maintainer Docs: See [docs/maintainer-workflows.md](docs/maintainer-workflows.md), [docs/plugin-architecture.md](docs/plugin-architecture.md), and [AGENTS.md](AGENTS.md) for repository maintenance, architecture, and evidence rules.

## When To Use It

Groundwork is useful when correctness depends on more than the next code edit:

- turning rough intent into a small PRD/spec;
- splitting accepted work into scoped tasks;
- deciding whether work is ready, blocked, or needs human input;
- planning or implementing code changes with a clear evidence boundary;
- checking whether a claim is supported by source, tests, runtime evidence, docs, or UAT;
- packaging accepted ready work for another runtime without claiming that runtime executed;
- preserving compact handoff context across sessions;
- maintaining a source-cited project wiki.

Do not use Groundwork just to answer simple questions, make obvious one-line edits, replace human review, bypass CI, create release evidence from local docs, or automate remote writes.

## Skills

The installed plugin exposes ten public skills:

| Skill | Use it for |
| --- | --- |
| `to-prd` | Shape rough or ambiguous intent into a compact PRD/spec. |
| `to-issues` | Slice accepted scope into vertical task drafts. |
| `triage` | Classify readiness, blockers, severity, state, or closeout. |
| `write-plan` | Produce an implementation plan for accepted work before edits. |
| `prototype` | Build or review a throwaway UI, logic, state, or contract prototype. |
| `implement` | Make focused code or documentation changes against source truth. |
| `verify` | Map claims to evidence and report covered and missing proof. |
| `handoff` | Preserve compact continuation state for another session or reviewer. |
| `dispatch` | Produce package-only runtime instructions for accepted ready tasks. |
| `wiki` | Create, query, audit, update, or repair project-level LLM Wiki notes. |

## Package Boundary

Groundwork is split between a small installed runtime package and a larger maintainer repository.

What is packaged:

- `.codex-plugin/`
- `skills/`
- `hooks/hooks.json`
- `scripts/codex-hooks/`
- `README.md` generated from `README.runtime.md`
- `LICENSE`

What stays source-only:

- `AGENTS.md`
- `docs/`
- `evals/`
- `schemas/`
- `artifacts/`
- `examples/`
- `research/`
- maintainer scripts outside `scripts/codex-hooks/`
- local state such as `.git/`, `.codegraph/`, `.groundwork/`, `.trellis/`, `dist/`, and `refer/`

Bundled router-observability hooks are dormant by default. They no-op unless a project explicitly opts in or a controlled process force-enables them. Hook cards, local scores, docs, evals, and source checks are improvement evidence; they do not by themselves prove runtime behavior, cache refresh, release readiness, UAT readiness, customer readiness, marketplace readiness, or hook trust.

## Install Locally

Groundwork is currently intended for local personal installation through a generated Codex marketplace. Do not point Codex directly at this development checkout or a symlink to it.

From a local checkout:

```bash
python3 scripts/build_local_marketplace.py
codex plugin marketplace add ./dist/groundwork-local-marketplace
codex plugin add groundwork@groundwork
```

For an unpublished checkout cloned under your Codex plugin area:

```bash
git clone https://github.com/daxiong888/Groundwork.git ~/.codex/plugins/groundwork
cd ~/.codex/plugins/groundwork
python3 scripts/build_local_marketplace.py --output ~/.codex/plugins/groundwork-local-marketplace
codex plugin marketplace add ~/.codex/plugins/groundwork-local-marketplace
codex plugin add groundwork@groundwork
```

If Codex is already open, restart the app or refresh the plugin list after installation.

## Update Locally

For a local checkout:

```bash
cd ~/.codex/plugins/groundwork
git pull --ff-only
python3 scripts/build_local_marketplace.py --output ~/.codex/plugins/groundwork-local-marketplace
codex plugin add groundwork@groundwork
```

If the local marketplace was ever pointed directly at a working checkout, rebuild it with `scripts/build_local_marketplace.py`, re-add the generated marketplace path, and reinstall. A healthy installed cache should contain the runtime package only, not source-only docs, evals, artifacts, schemas, maintainer history, or local scratch state.

## Privacy

Groundwork is local-first. It has no service backend, analytics endpoint, account system, or telemetry sink. The bundled skills and scripts operate on local files and user-approved Codex tool actions. Network access, remote tracker changes, deployment, migrations, destructive operations, data writes, commits, pushes, and pull requests still require explicit user intent and the relevant evidence gates.

## Where To Go Next

- I want to use it: read [README.runtime.md](README.runtime.md) for the installed package contract, then install from the generated marketplace.
- I want to understand the workflow: read [docs/maintainer-workflows.md](docs/maintainer-workflows.md).
- I want to maintain or review it: read [AGENTS.md](AGENTS.md) and [docs/plugin-architecture.md](docs/plugin-architecture.md).
- I want evidence details: inspect [evals/baselines/](evals/baselines/) and the relevant eval docs, but keep source-validation, runtime, cache, release, UAT, and customer-readiness claims separate.
- I want version history: read [CHANGELOG.md](CHANGELOG.md).
