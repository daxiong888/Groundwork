# Handoff Review Package

Target Reader: Codex or a human reviewer continuing nontrivial Groundwork work.
Reader Action Needed: Resume review without rereading full PRDs, plans, diffs, or logs.
Decision Supported: What is done, what is evidenced, what remains risky, and what skill should run next.
Scope: Compact continuation packages for implementation review, verification review, or cross-session handoff.
Out of Scope: Full PRD rewrites, full diff copies, raw logs, sensitive data, or hidden unverified claims.
Evidence Level: Groundwork issue #11 acceptance criteria and existing handoff compactness rules.

Use this shape for review handoff:

```text
Review Package
- Audience:
- Goal:
- Current Decision:
- Current Status:
- Source Artifacts:
- Evidence:
- Open Risks:
- Lifecycle State:
- State Artifact:
- State Freshness:
- State Update Needed:
- State Reference Mode:
- Git Boundary:
- Allowed Files:
- Disallowed Files:
- Next Skill:
- Do-Not-Assume:
- Redaction Note:
```

For Codex-native Local to Worktree or Worktree to Local continuation, include this additional package before review or closeout claims:

```text
Native Handoff Package
- Direction: local_to_worktree / worktree_to_local
- Goal:
- Scope:
- Out Of Scope:
- Base:
- Native Context:
- Thread Ref:
- Thread Ref Availability: visible / unavailable_before_handoff / unavailable_in_current_surface / redacted
- Worktree Path:
- Worktree Path Availability: visible / unavailable_before_handoff / unavailable_in_current_surface / redacted
- Worktree Association:
- Worktree Association Availability: visible / unavailable_before_handoff / unavailable_in_current_surface / redacted
- Route Decision Ref:
- Relevant Artifacts:
- Changed Files:
- Evidence:
- Open Risks:
- Next Command:
- Stop Condition:
- Redaction Notes:
```

Rules:

- Reference artifacts, commits, checks, or issue IDs instead of copying long content.
- Do not paste long diffs.
- Do not rewrite full PRDs or implementation plans.
- Do not hide unverified claims; put them in `Open Risks` or `Do-Not-Assume`.
- Groundwork prepares the Native Handoff Package only. Official Codex Handoff owns moving the thread and code between Local and Worktree and owns native Handoff Git operations.
- Native handoff packages must cite canonical artifacts instead of copying full PRDs, full issue bodies, long diffs, logs, or transcripts.
- `Thread Ref Availability`, `Worktree Path Availability`, and `Worktree Association Availability` are always required when the native package is present.
- Local to Worktree packages prepared before native worktree creation or exposure must use `Worktree Path Availability: unavailable_before_handoff`; do not invent a path.
- Worktree to Local packages must include `Changed Files`, `Evidence`, `Open Risks`, `Stop Condition`, and visible native context when available before any closeout decision.
- Include `Git Boundary`, allowed files, and disallowed files when a future session may stage, commit, or continue edits.
- Never instruct a future reader to use `git add .`; name explicit pathspecs if staging or commit continuation is in scope.
- Redact secrets, tokens, credentials, PII, sensitive logs, and private request payloads.
- Include or reference lifecycle-state fields when the lifecycle threshold applies. Use `State Artifact`, `State Freshness`, `State Update Needed`, and `State Reference Mode` from the handoff output shape, but do not paste the full `STATE.md`.
- Use `State Freshness: unknown` and `State Update Needed: yes` unless freshness is evidenced by a readable `Last Updated`, readable `Canonical Sources`, and checked canonical sources with no unresolved conflict.
- If lifecycle threshold does not apply, write `Lifecycle State: not applicable` and keep the rest of the review package focused on source artifacts, evidence, risks, and next action.
