# Verify Review Lenses

Target Reader: Codex running the Groundwork `verify` skill.
Reader Action Needed: Pick the narrowest verification lens that matches the user's claimed readiness question.
Decision Supported: Which evidence is required before `verify` can issue a pass, partial, fail, or blocked verdict.
Scope: Named review lenses for PRD, document, contract, implementation readiness evidence, UAT, UI, and git boundary review.
Out of Scope: A standalone public review skill, broad architecture review, or implementation work.
Evidence Level: Derived from v0.4.0 PRD FR-402 / FR-404 / FR-408 plus existing verify scope-first requirements.

Use a named lens when the user asks for a specific kind of verification. If several lenses apply, state the primary lens and secondary lenses in `Verification Scope`.

| Lens | Use When | Required Evidence | Common Gaps / Fail Conditions |
| --- | --- | --- | --- |
| PRD review | Verifying whether requirements, acceptance, and open questions are ready. | PRD/spec text, source evidence behind claims, acceptance criteria, out-of-scope boundaries, decision owner. | Acceptance is vague, business fields are invented, open questions are hidden, or implementation details replace user value. |
| document review | Verifying docs intended for another reader. | Target reader, reader action, artifact type, source of truth, source artifacts, scope/out-of-scope, evidence level, safe-to-share/redaction notes, claims mapped to evidence, outdated/duplicate docs checked when relevant. | Audience is unclear, required audience-first header fields are missing, docs include internal noise, claims lack evidence, or artifact duplicates a better source. |
| contract review | Verifying API/DB/state/frontend/doc alignment. | Backend source/API/schema, request/response fields, error behavior, call rules, boundary conditions, consumer-facing docs. | Prototype/mock fields promoted as contract, frontend docs expose internal modules, or source truth is not inspected. |
| implementation review / implementation readiness evidence review | Verifying whether an already-completed implementation has evidence for readiness, release, UAT, handoff, or claimed runtime behavior. | Task/PRD, diff, direct callers/callees, tests, local checks, stated risks, regression coverage, readiness claim being checked. | Diff summary only, missing evidence for claimed behavior, unrelated files mixed in, no test/no-test justification, or a plain conformance-review prompt that belongs to `implement`. |
| UAT review | Verifying whether work is ready for UAT/customer validation. | Source, tests, runtime behavior, data readiness, environment readiness, known customer/UAT criteria. | No runtime evidence, no data/environment proof, customer summary primary over engineering readiness. |
| UI review | Verifying visual, responsive, interaction, or browser-visible behavior. | URL/context, tool used, action, observation, screenshots or browser/runtime evidence when available, limitations. | Claims about layout/hover/focus/responsiveness without browser/runtime evidence. |
| git boundary review | Verifying commit/staging scope. | `git status --short`, intended allowlist, explicit denylist, `git diff --name-only`, `git diff --cached --name-only`. | `git add .`, ignored runtime dirs, unrelated files staged, or no statement of unrelated changes. |
| worktreeinclude safety review | Verifying `.worktreeinclude.example`, private `.worktreeinclude` guidance, or worktree-local ignored-file copy safety. | PRD FR-402/AC-402, `docs/worktreeinclude-safety.md`, active non-comment example entries, official-copy-semantics wording, forbidden-category wording, git-boundary evidence when staging or commit safety is in scope. | Active committed examples include `.env`, `.env.local`, `config/secrets.json`, cookies, tokens, secrets, PII, private logs, production data, `.groundwork`, `.trellis`, or large generated caches; private `.worktreeinclude` files that name sensitive local paths are staged or not reported as unstaged/uncommitted unless explicitly approved. |
| adversarial evidence sufficiency review | Verifying whether a conclusion survives likely counterexamples, missing evidence, edge states, hidden assumptions, or scope creep. | Current claim, source/evidence set, explicit `Covered` / `Not Covered`, strongest counterexample, missing evidence, edge cases not covered, and downgraded claims. | Diff summary becomes readiness, self-check becomes clean review, source-only evidence becomes runtime/UAT/release/cache evidence, or unsupported claims are left as pass/ready. |

Named lenses do not expand scope by themselves. If a lens would require migration, production access, destructive commands, remote tracker mutation, push, deploy, or shared skill mutation, use the gate rule before taking action.

When the adversarial evidence sufficiency lens is used, the final report still begins with the exact `Verification Scope` block required by `skills/verify/SKILL.md`. Any `Adversarial Findings` block comes after scope and claim/evidence summary.

Use `implement`, not `verify`, when the user asks whether a diff conforms to a PRD/task/plan but explicitly does not ask for readiness, UAT, release, runtime evidence, or final verification.

For durable artifact header review, use the document review lens and treat missing `Target Reader`, `Reader Action Needed`, `Decision Supported`, `Artifact Type`, `Source of Truth`, `Scope`, `Out of Scope`, `Evidence Level`, or `Safe to Share / Redaction Notes` as a gap. Missing `Target Reader` or `Reader Action Needed` is at least P1 when the artifact is intended to drive implementation, review, verification, handoff, UAT, release, or another agent/session.

## Worktreeinclude Safety Checklist

Use the `worktreeinclude safety review` lens when the claim depends on `.worktreeinclude` examples or private ignored-file copy guidance.

- Confirm active committed example entries are placeholders only and do not contain `.env`, `.env.local`, `config/secrets.json`, cookies, tokens, secrets, PII, private logs, production data, `.groundwork`, `.trellis`, or large generated caches.
- Confirm the safety documentation explains that official Codex docs allow project-owner-only private `.worktreeinclude` entries such as `.env`, `.env.local`, and `config/secrets.json`, while Groundwork committed examples remain conservative.
- Confirm browser cookies, credential stores, tokens, secrets, PII, private logs, production data, `.groundwork`, `.trellis`, and large generated caches are forbidden in committed examples and default recommendations.
- Confirm private `.worktreeinclude` files that name sensitive local paths remain unstaged/uncommitted unless explicitly approved, and report that boundary under `Git Boundary`.
- Do not upgrade documentation-only evidence into runtime, cache, marketplace, release, UAT, or Codex App handoff readiness.
