# Audience-First Artifact Contract

Target Reader: Groundwork skill authors, artifact authors, maintainers, implementers, reviewers, verifiers, and coordinators.
Reader Action Needed: Decide which durable artifacts must carry audience-first header fields and which native formats are exempt.
Decision Supported: Whether a new or materially updated artifact has enough reader, action, source, evidence, scope, and redaction context to be reused safely.
Artifact Type: shared guardrail
Source of Truth: Groundwork artifact hygiene policy and shared documentation conventions.
Scope: Audience-first header applicability, required exact field names, durable artifact exceptions, and redaction reminders.
Out of Scope: Public skill trigger design, machine-readable schema design, runtime execution, release approval, UAT approval, or customer readiness.
Evidence Level: Source-validation policy only. This contract does not prove runtime, browser, UAT, release, marketplace, installed-plugin, cache-refresh, or customer readiness.
Safe to Share / Redaction Notes: Safe to share as-is; contains no secrets, credentials, PII, private logs, or production payloads.

Use this contract whenever a skill creates or materially updates a durable artifact.

## Applicability

This contract applies to:

- user-facing durable artifacts produced by Groundwork skills;
- maintainer-facing durable docs under `docs/`, `artifacts/`, and `skills/_shared/`;
- contract notes, verification reports, handoffs, lifecycle state, baselines, issue maps, PRDs, maintainer guides, and other reviewable files that are meant to be reused after the current conversation.

This contract does not by itself require every public `skills/<public-skill>/SKILL.md` source file to carry the artifact header. Public skill source contracts are governed by `skills/_shared/SKILL-QUALITY.md` and `skills/_shared/SKILL-AUDIT.md`; they must follow this audience-first header only when a maintainer explicitly classifies the skill source file or a material update to it as a durable artifact requiring the header.

Helper indexes, templates, examples, generated fixtures, and machine-readable schemas may use their native shape when adding the header would reduce machine readability. In those cases, the owning maintainer doc or adjacent shared contract must state the audience, source truth, evidence level, and redaction boundary.

Runtime instruction references and reasoning lenses are source contracts, not user-facing durable artifacts. They may replace the nine-field header with one compact purpose/evidence-boundary sentence when the owning `SKILL.md` already supplies routing and scope. Do not copy audience metadata into model-visible output.

## Required Header Fields (exact)

Every new or materially updated durable artifact must include these fields exactly:

- Target Reader
- Reader Action Needed
- Decision Supported
- Artifact Type
- Source of Truth
- Scope
- Out of Scope
- Evidence Level
- Safe to Share / Redaction Notes

## Notes

- Keep each field concise and decision-oriented.
- `Artifact Type` should name the artifact family, such as PRD, issue map, contract note, verification report, handoff, lifecycle state, baseline, or maintainer doc.
- `Source of Truth` should name the canonical source type or path when known. Use `mixed` or `unknown` only when the uncertainty is intentional and visible.
- `Safe to Share / Redaction Notes` must say whether the artifact can be shared as-is or what was redacted or excluded.
- If the user requests a different layout, preserve their layout but keep these exact field names present.
- Do not add sensitive values (secrets, credentials, tokens, PII, sensitive logs) into headers or artifact bodies.
