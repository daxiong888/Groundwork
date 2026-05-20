# Groundwork

Groundwork is a Codex-native personal base for evidence-first R&D work.

It exists to make Codex more useful in real project work where correctness depends on PRD/spec clarity, task state, source code truth, runtime evidence, prototypes, integration contracts, UAT behavior, and careful handoff. It absorbs useful ideas from existing frameworks without requiring those frameworks or copying their full process.

The practical starting point is a curated base: use Superpowers as the Codex plugin packaging reference, use mattpocock/skills as the strongest lightweight workflow/skill reference, and keep Groundwork-specific choices tied to the user's R&D scenarios.

## Current Stage

Groundwork is in the v0.1 review-package stage. `docs/prd.md` is the product source of truth for this cut.

This repository currently contains:

- project vision and boundaries
- framework comparison research
- user work scenario analysis
- Codex plugin manifest
- eight first-cut public skills
- skill trigger fixtures
- R&D workflow scenario fixtures
- spec-level and local discovery baselines
- runtime trial checklist

It intentionally does not yet contain production-hardened skill behavior, runtime trial results, task tools, hooks, MCP servers, or local task CRUD. Those should be added only after the v0.1 runtime trial exposes a real need.

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
- `skills/` - eight shallow public skills for v0.1
- `evals/` - prompt fixtures, scenario fixtures, baselines, and runtime trial checklist
