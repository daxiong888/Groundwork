# Implementation Notes Policy

Target Reader: Groundwork maintainer deciding whether implementation decisions need durable notes.
Reader Action Needed: Use this policy to avoid mandatory running notes files while preserving important implementation decisions when they matter.
Decision Supported: Whether implementation notes should stay in the response, become a handoff/review package, or become a durable artifact.
Scope: Spec clarification for issue #20 covering trigger conditions, ownership, path, useful content, and forbidden duplication.
Out of Scope: Changing `implement` behavior, adding a public skill, requiring `implementation-notes.html`, or creating runtime notes by default.
Evidence Level: Groundwork issue #20 body and 2026-05-22 triage comment.

## Decision

Groundwork does not require a running `implementation-notes.html` or Markdown file during implementation.

Implementation notes are conversation-only by default. A durable file is allowed only when a nontrivial implementation needs review, handoff, later verification, or a decision record that cannot be safely preserved in the final response.

## Ownership

- `implement` owns short in-response decision notes and remaining gaps.
- `handoff` owns durable continuation or review packages when another session or reviewer needs to resume.
- `verify` owns readiness evidence and unverified claims, not implementation diaries.

This is a spec clarification, not a new behavior implementation.

## Durable File Policy

When durable implementation notes are justified:

- prefer an existing canonical artifact if one already owns the decision
- otherwise use `artifacts/<feature-slug>/implementation-notes.md`
- include the audience-first header fields required by `skills/_shared/AUDIENCE-FIRST-ARTIFACT.md`
- link source artifacts, issues, commits, and verification commands instead of copying long content
- delete, absorb, or hand off temporary notes when they are no longer useful

Do not write notes under `.groundwork/` unless they are runtime scratch content and the user explicitly accepts that the contents are ignored by default.

## Useful Content

Useful implementation notes contain decisions that were not already in the spec:

- decision made
- why it was needed
- alternatives considered
- tradeoff or risk
- changed assumption
- deviation from PRD, plan, or issue
- follow-up verification or owner
- cleanup or handoff decision

## Forbidden Content

Implementation notes must not become:

- a duplicate PRD
- a full implementation plan
- a full diff
- a command transcript
- a daily diary
- a place for secrets, credentials, PII, sensitive logs, or private request payloads
- a way to hide unverified claims from `verify`

## Acceptance Standard

Implementation notes are useful only when another reader can make a decision or safely resume work from them. If no target reader or reader action exists, keep the information in the normal implementation response and do not create a durable artifact.

