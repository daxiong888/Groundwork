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
- Continuation Goal:
- Current Status:
- Source Artifacts:
- Evidence:
- Open Risks:
- Allowed Files:
- Disallowed Files:
- Next Skill:
- Do-Not-Assume:
- Redaction Note:
```

Rules:

- Reference artifacts, commits, checks, or issue IDs instead of copying long content.
- Do not paste long diffs.
- Do not rewrite full PRDs or implementation plans.
- Do not hide unverified claims; put them in `Open Risks` or `Do-Not-Assume`.
- Include file boundaries when a future session may stage, commit, or continue edits.
- Redact secrets, tokens, credentials, PII, sensitive logs, and private request payloads.

