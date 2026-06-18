# `.worktreeinclude` Safety

Target Reader: Groundwork maintainers, implementation agents, and verification reviewers handling Codex-managed local worktrees.
Reader Action Needed: Use this note before creating, reviewing, staging, or verifying `.worktreeinclude` examples or private files.
Decision Supported: Whether a `.worktreeinclude` entry is safe for a committed Groundwork example, private local use only, or forbidden from git.
Artifact Type: maintainer doc
Source of Truth: `docs/prd-v0.4.0-codex-native-worktree-handoff-alignment.md` FR-402/AC-402, `artifacts/v0.4.0-codex-native-worktree-handoff/issue-map.md` V040-003, and official Codex worktree documentation as cited by the PRD.
Scope: `.worktreeinclude` copy semantics, conservative committed examples, private project-owner-only paths, forbidden examples, and git-boundary review.
Out of Scope: Codex App implementation details, remote worktrees, command-line Git worktrees outside Codex, runtime trials, cache refresh, or release readiness.
Evidence Level: Documentation and verification-policy guidance only; no runtime, cache, marketplace, release, UAT, or Codex App handoff evidence is claimed.
Safe to Share / Redaction Notes: Safe to share. This document contains forbidden category names and placeholder path examples only; it contains no secrets, credentials, private URLs, browser cookies, PII, logs, or production data.

## Official Copy Semantics

Codex `.worktreeinclude` is a repository-root file used by the Codex app when it creates local managed worktrees from a Git checkout. It lists ignored paths or `.gitignore`-style patterns that should be copied into the new local managed worktree.

The PRD source truth records these official semantics:

- `.worktreeinclude` applies to local Codex app managed worktrees, not remote worktrees or command-line Git worktrees created outside Codex.
- It should list ignored paths or patterns that are intentionally copied for local worktree execution.
- It should not list tracked files.
- Codex skips source symlinks and does not overwrite files already present in the new checkout.
- Ignored `AGENTS.override.md` is copied automatically and does not need to be listed.

## Committed Groundwork Examples

Groundwork committed examples must stay conservative. The root `.worktreeinclude.example` may contain only safe placeholder entries such as:

- redacted local runtime config templates with no secrets;
- bounded redacted fixtures needed for deterministic local checks;
- repo-specific ignored tool configuration that is safe to copy after redaction.

Committed examples must not normalize real secret-bearing path names, real credential locations, sensitive local logs, private URLs, browser cookies, PII, production data, or large generated caches.

## Private Project-Owner Paths

> [!WARNING]
> Official Codex documentation allows a project owner to list ignored files such as `.env`, `.env.local`, and `config/secrets.json` in a private local `.worktreeinclude` when local execution needs them. Groundwork committed examples remain conservative and must not include those paths as active example entries.

Private `.worktreeinclude` entries that name sensitive local files are a project-owner decision. They are not Groundwork defaults and they do not become safe to stage just because Codex can copy them into a local managed worktree.

When a private `.worktreeinclude` names `.env`, `.env.local`, `config/secrets.json`, browser cookies, tokens, secrets, PII, private logs, production data, `.groundwork`, `.trellis`, or large generated caches, `verify` must treat the file as a local runtime risk and report the redaction boundary.

## Forbidden Committed Examples

Groundwork committed examples and default recommendations must not include active entries for:

- `.env`, `.env.local`, `config/secrets.json`, or other secret-bearing local config paths;
- tokens, API keys, passwords, private keys, credential stores, browser cookies, or auth sessions;
- private URLs, customer PII, production data dumps, private request payloads, sensitive screenshots, or private logs;
- `.groundwork`, `.trellis`, build outputs, temporary test artifacts, or other runtime scratch unless an accepted issue creates a redacted fixture;
- large generated caches that are not required for a scoped deterministic check.

## Git Boundary

Private `.worktreeinclude` files that name sensitive local paths must remain unstaged and uncommitted unless explicitly approved by the project owner for that exact path set.

Before staging or commit-related review, apply the Groundwork git-boundary checklist:

- intended files changed;
- intended files staged;
- unrelated modified and untracked files left unstaged;
- explicit denylist including `.env`, `.env.*`, `.groundwork/*`, `.trellis/*`, logs, temporary files, production data dumps, and cache directories;
- `git status --short`, `git diff --name-only`, and `git diff --cached --name-only` evidence when staging or commit safety is in scope.

`git add .` is not an acceptable staging instruction for `.worktreeinclude` work.

## Verification Checklist

Use this checklist when reviewing `.worktreeinclude` examples or private-file guidance:

- Active entries in `.worktreeinclude.example` are placeholders only.
- Active committed entries do not contain `.env`, `.env.local`, `config/secrets.json`, cookies, tokens, secrets, PII, private logs, production data, `.groundwork`, `.trellis`, or large generated caches.
- The safety doc explains the difference between official Codex copy support and Groundwork committed example policy.
- Any private `.worktreeinclude` naming sensitive local paths is explicitly reported as unstaged/uncommitted unless approved.
- Runtime, cache, release, UAT, marketplace, or handoff readiness is not claimed from this documentation alone.
