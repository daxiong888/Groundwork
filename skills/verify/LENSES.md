# Verify Review Lenses

Target Reader: Codex running the Groundwork `verify` skill.
Reader Action Needed: Pick the narrowest verification lens that matches the user's claimed readiness question.
Decision Supported: Which evidence is required before `verify` can issue a pass, partial, fail, or blocked verdict.
Scope: Named review lenses for PRD, document, contract, implementation readiness evidence, UAT, UI, and git boundary review.
Out of Scope: A standalone public review skill, broad architecture review, or implementation work.
Evidence Level: Groundwork issue #5 acceptance criteria and existing PRD review requirements.

Use a named lens when the user asks for a specific kind of verification. If several lenses apply, state the primary lens and secondary lenses in `Verification Scope`.

| Lens | Use When | Required Evidence | Common Gaps / Fail Conditions |
| --- | --- | --- | --- |
| PRD review | Verifying whether requirements, acceptance, and open questions are ready. | PRD/spec text, source evidence behind claims, acceptance criteria, out-of-scope boundaries, decision owner. | Acceptance is vague, business fields are invented, open questions are hidden, or implementation details replace user value. |
| document review | Verifying docs intended for another reader. | Target reader, reader action, source artifacts, claims mapped to evidence, outdated/duplicate docs checked when relevant. | Audience is unclear, docs include internal noise, claims lack evidence, or artifact duplicates a better source. |
| contract review | Verifying API/DB/state/frontend/doc alignment. | Backend source/API/schema, request/response fields, error behavior, call rules, boundary conditions, consumer-facing docs. | Prototype/mock fields promoted as contract, frontend docs expose internal modules, or source truth is not inspected. |
| implementation readiness evidence review | Verifying whether an already-completed implementation has evidence for readiness, release, UAT, handoff, or claimed runtime behavior. | Task/PRD, diff, direct callers/callees, tests, local checks, stated risks, regression coverage, readiness claim being checked. | Diff summary only, missing evidence for claimed behavior, unrelated files mixed in, no test/no-test justification, or a plain conformance-review prompt that belongs to `implement`. |
| UAT review | Verifying whether work is ready for UAT/customer validation. | Source, tests, runtime behavior, data readiness, environment readiness, known customer/UAT criteria. | No runtime evidence, no data/environment proof, customer summary primary over engineering readiness. |
| UI review | Verifying visual, responsive, interaction, or browser-visible behavior. | URL/context, tool used, action, observation, screenshots or browser/runtime evidence when available, limitations. | Claims about layout/hover/focus/responsiveness without browser/runtime evidence. |
| git boundary review | Verifying commit/staging scope. | `git status --short`, intended allowlist, explicit denylist, `git diff --name-only`, `git diff --cached --name-only`. | `git add .`, ignored runtime dirs, unrelated files staged, or no statement of unrelated changes. |

Named lenses do not expand scope by themselves. If a lens would require migration, production access, destructive commands, remote tracker mutation, push, deploy, or shared skill mutation, use the gate rule before taking action.

Use `implement`, not `verify`, when the user asks whether a diff conforms to a PRD/task/plan but explicitly does not ask for readiness, UAT, release, runtime evidence, or final verification.
