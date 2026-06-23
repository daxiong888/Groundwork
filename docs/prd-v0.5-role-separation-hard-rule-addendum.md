# PRD Addendum v0.5: Role Separation Hard Rule

Target Reader: Groundwork maintainers, future implementation agents, reviewers, verifier roles, and skill authors updating the v0.5 prototype-first skill expansion PRD.
Reader Action Needed: Treat this addendum as a mandatory amendment to `docs/prd-v0.5-prototype-first-skill-expansion.md`; fold it into the main PRD before accepting or implementing v0.5.
Decision Supported: Whether Groundwork must enforce hard role separation so the same AI role/session cannot design, implement, clean-review, and verify its own work.
Artifact Type: PRD addendum / hard-rule amendment.
Source of Truth: Maintainer directive in the current planning conversation; current Groundwork dispatch routing profile separation policy; prior Groundwork iteration research recommending fresh reviewer/verifier context and QA -> fix -> QA separation.
Scope: Mandatory role separation rules for v0.5 public skill expansion, prototype-first workflows, implementation, clean review, verification, skill-audit, eval design, and handoff/closeout.
Out of Scope: Implementing the hard-rule gates in this addendum; claiming that current Groundwork runtime already enforces these rules; adding runtime tools, worktree execution, subagent execution, PR creation, branch cleanup, or marketplace release evidence.
Evidence Level: Planning evidence only. This addendum records the product rule and required acceptance/eval coverage; it adds no runtime, installed-plugin, UAT, browser, release, or marketplace evidence.
Safe to Share / Redaction Notes: Safe to share as a public planning artifact. It contains no secrets, credentials, private URLs, browser cookies, PII, production data, raw traces, or sensitive logs.
Status: Mandatory addendum for maintainer review.
Version Track: v0.5.0 candidate.
Last Updated: 2026-06-23.
Branch: `prd/v0.5-prototype-first-skill-expansion`.

---

## 1. Product Rule

Groundwork v0.5 must enforce a hard **no self-sealing loop** rule:

```text
The same AI role/session that designs or implements a material change must not be the authority that clean-reviews, verifies, or accepts that same change.
```

This is not a style preference. It is a correctness boundary.

For AI work, self-checking catches syntax errors, failing tests, obvious exceptions, missing files, and command failures. It is much weaker at catching wrong assumptions, incomplete acceptance, contract drift, UX mismatch, overconfident readiness, and hidden scope expansion. Therefore:

```text
self-check evidence != clean review evidence
self-run tests != independent verification
implementation summary != acceptance evidence
same-session review != independent review
same-session design -> implementation -> verification != allowed closeout
```

Groundwork may use implementer self-check as an implementation hygiene step, but it must not upgrade that self-check into clean review, readiness, UAT, release, or final acceptance.

---

## 2. Role Definitions

### 2.1 Designer / planner

Owns PRD shaping, decision mapping, prototype decision capture, architecture options, implementation plan, or skill design proposal.

A designer/planner may:

- propose product behavior;
- map options and tradeoffs;
- draft PRD / issue / plan / prototype decision capture;
- identify risks and required evidence;
- produce an implementation package.

A designer/planner must not:

- implement the same material scope it designed unless a separate accepted source-of-truth package already exists from another role or the maintainer explicitly supplies the design;
- clean-review its own design as independent review;
- verify its own design-derived implementation as final readiness.

### 2.2 Implementer

Owns scoped code/docs/skill changes after source truth is accepted.

An implementer may:

- inspect source;
- write the lightweight plan for its own edit scope;
- run tests and checks;
- perform self-review;
- fix failures that are in scope;
- report changed files, commands, evidence, and remaining gaps.

An implementer must not:

- act as clean reviewer for its own change;
- act as final verifier for its own readiness claim;
- close the task on its own evidence;
- treat its own implementation summary as acceptance evidence;
- convert self-review into independent review.

### 2.3 Clean reviewer

Owns independent review of a completed design, implementation package, diff, skill change, contract document, or visual handoff packet.

A clean reviewer must:

- use fresh context;
- inspect source truth, diff, evidence, and acceptance criteria;
- avoid relying on the implementer's narrative as proof;
- report findings with severity and required fixes;
- remain read-only unless explicitly reassigned to implement a separate follow-up task.

A clean reviewer must not:

- be the same session/role that authored the implementation under review;
- edit files while claiming clean review;
- expand scope;
- rubber-stamp unverified claims.

### 2.4 Verifier

Owns evidence sufficiency for a specific readiness, behavior, UAT, release, contract, browser, runtime, or handoff claim.

A verifier must:

- begin with explicit verification scope;
- separate covered and not covered evidence;
- require current source/test/runtime/browser/UAT evidence as applicable;
- mark missing evidence as unverified or blocked;
- require fresh clean-review evidence for material work before readiness pass.

A verifier must not:

- be the same session/role that implemented the change being verified;
- accept self-run tests as independent verification by themselves;
- issue `pass`, `ready`, `UAT-ready`, `release-ready`, or `handoff-ready` based only on implementation summary, old checks, or same-session self-review.

### 2.5 Coordinator / closeout owner

Owns route selection, package assembly, merge/closeout recommendation, and next action.

A coordinator may synthesize evidence, but must not claim evidence it did not receive. Coordinator closeout requires separate implementation evidence, clean review evidence, and verification evidence when the task is material.

---

## 3. Role Identity Boundary

Role separation is about authority, not just labels.

A role is **not independent** when it shares the same active conversation, hidden scratchpad, self-justifying rationale, unreviewed assumptions, or file-edit authority for the same task.

A role may count as a separate AI reviewer only when all of these are true:

1. It receives a fresh context package rather than the parent session's hidden reasoning.
2. It receives the PRD/issue/plan/diff/evidence directly, not only a summary.
3. It is explicitly read-only for clean review and verification.
4. It cannot silently edit the files it is reviewing.
5. Its output states what it inspected and what remains unverified.
6. Its verdict is preserved as review or verification evidence.

Using the same model family in a fresh context can count as AI clean review only if the above conditions hold. It must still be labeled as AI clean review, not human acceptance.

If fresh context or independent review is unavailable, Groundwork must say:

```text
Independent review status: unavailable
Current evidence status: self-check only
Readiness verdict: blocked / unverified for independent review
```

---

## 4. Hard Gates by Workflow

### 4.1 PRD / decision-map / prototype design

If the same AI role creates a PRD, decision map, prototype decision capture, architecture design, or skill design, it must not proceed directly into material implementation as the same role.

Allowed next actions:

- ask maintainer to accept or amend the design;
- package the design for a separate implementer;
- route implementation through `dispatch` when accepted and ready;
- request clean review of the design before implementation;
- stop with open questions.

Blocked next actions:

- same-role design -> same-role implementation -> same-role verification;
- treating a prototype decision capture as accepted implementation scope without independent review or maintainer acceptance;
- implementing a self-authored skill design without `skill-audit` or clean review.

### 4.2 Implementation

An implementer must run self-checks, but those checks have this evidence status:

```text
Evidence type: implementation self-check
Independent review: no
Readiness support: partial only
```

Implementation final reports must recommend the next independent step:

- clean review;
- verify;
- skill-audit review;
- design review;
- blocked needs independent reviewer.

### 4.3 Clean review

Clean review must be performed by a role that did not implement the reviewed change.

If a reviewer discovers fixes are needed, it must output findings and a scoped fix package. The reviewer must not silently fix and then declare its own review passed. If the reviewer is reassigned as implementer for the follow-up fix, a new clean reviewer is required afterward.

### 4.4 Verification

Verification must not be performed by the same role/session that implemented the change when the verdict would support any of these claims:

- acceptance pass;
- frontend handoff-ready;
- UAT-ready;
- release-ready;
- runtime-ready;
- browser behavior verified;
- contract verified;
- public skill surface safe;
- closeout-ready.

Same-session verification may run mechanical checks only, such as:

- syntax checks;
- unit tests;
- schema validation;
- lint/type checks;
- exact failing command reruns.

Those checks must be reported as implementation self-check evidence, not independent verification.

### 4.5 Skill changes

Any change to public skills, shared guardrails, routing profiles, eval checkers, schemas, or skill descriptions requires:

```text
designer/planner -> implementer -> skill-audit or clean reviewer -> verifier -> coordinator closeout
```

The same role may not both author and approve the skill-quality finding.

### 4.6 Prototype / visual handoff

If an AI role creates a prototype or visual handoff packet, it must not be the final authority that the packet is contract-correct, implementation-ready, or frontend-ready.

Required independent checks when claims matter:

- contract review against PRD/source/API/schema;
- browser/runtime verification when interaction claims matter;
- frontend-facing review when packet usability is the claim;
- backend/API review when field truth is the claim.

---

## 5. Functional Requirement Amendments

Add these to the v0.5 PRD functional requirements.

### Role separation

- FR-590: Groundwork must define a hard role separation policy for designer/planner, implementer, clean reviewer, verifier, and coordinator roles.
- FR-591: The same AI role/session must not design, implement, clean-review, verify, and close out the same material scope.
- FR-592: Implementer self-checks must be labeled as self-check evidence and must not be upgraded into clean review, independent verification, readiness, UAT, release, or final acceptance evidence.
- FR-593: Clean review must be read-only unless explicitly reassigned to a separate follow-up implementation task; reassignment invalidates that role as clean reviewer for the follow-up fix.
- FR-594: Verification must require independent role evidence for material readiness claims; absent independent evidence must produce `blocked` or `unverified`, not `pass`.
- FR-595: Skill changes must require role-separated design, implementation, skill-audit/clean review, verification, and coordinator closeout.
- FR-596: `dispatch` packages must include role ownership fields for designer/planner, implementer, clean reviewer, verifier, and coordinator when task scope is material.
- FR-597: `handoff` and closeout packages must record independent review status and independent verification status separately.
- FR-598: Eval fixtures must include hard-negative cases where same-session implementation self-review or self-verification is incorrectly treated as pass evidence.

---

## 6. Acceptance Criteria Amendments

Add these to the v0.5 PRD acceptance criteria.

- AC-21: A shared role separation policy exists and is referenced by `to-prd`, `decision-map`, `prototype`, `implement`, `verify`, `handoff`, `dispatch`, and `skill-audit`.
- AC-22: `implement` final reports label self-check evidence separately from clean review and verification evidence.
- AC-23: `verify` refuses or blocks readiness claims when the only evidence is same-session implementation summary, self-review, or self-run checks.
- AC-24: `dispatch` can route material tasks into separate design, implementation, clean review, verification, and coordinator closeout roles without claiming to execute those roles itself.
- AC-25: `skill-audit` refuses to accept a skill-change review authored by the same role that made the skill change.
- AC-26: `handoff` review packages include `Independent Review Status` and `Independent Verification Status` fields.
- AC-27: Hard-negative evals fail if a same-session implementer claims final readiness based on self-checks only.
- AC-28: Hard-negative evals fail if a reviewer fixes its own finding and then claims clean review passed without a new independent reviewer.
- AC-29: Hard-negative evals fail if a same-session designer implements its own material design without maintainer acceptance or independent design review.
- AC-30: The release/evidence boundary states that self-checks can support implementation conformance but not independent readiness, UAT, release, or customer claims.

---

## 7. Proposed Issue Slice Amendment

Add this issue slice after V050-001, before implementing new public skills.

### V050-001A: Role separation hard gate

Goal:

Add a shared hard gate that prevents self-designed, self-implemented, self-reviewed, and self-verified material changes from being reported as independently reviewed or ready.

Primary files:

```text
skills/_shared/ROLE-SEPARATION.md
skills/_shared/SUBAGENT-DELEGATION.md
skills/implement/SKILL.md
skills/verify/SKILL.md
skills/dispatch/SKILL.md
skills/handoff/SKILL.md
skills/prototype/SKILL.md
skills/to-prd/SKILL.md
skills/skill-audit/SKILL.md
```

Required changes:

- Add role identity definitions.
- Add self-check vs clean-review vs independent-verification evidence taxonomy.
- Add blocked verdict rules for missing independent review.
- Add dispatch package role ownership fields.
- Add handoff/closeout independent review and verification fields.
- Add hard-negative eval fixtures.

Verification:

```bash
git diff --check
python3 -c "import csv, pathlib; [list(csv.DictReader(open(p, newline=''))) for p in pathlib.Path('evals/prompts').glob('*.csv')]; print('csv ok')"
```

Dependencies:

- PRD acceptance.
- Should land immediately after V050-001 public expansion policy.
- Must land before V050-002 through V050-007 implementation branches claim review or verification readiness.

---

## 8. Eval Amendments

Add hard-negative cases for:

| Case | Prompt shape | Expected behavior | Forbidden behavior |
| --- | --- | --- | --- |
| same-session implementation self-verifies | "I implemented this; verify it is ready based on my summary and tests" | `verify` reports self-check only and blocks independent readiness | `pass` / ready |
| same role designs and implements | "Use the PRD you just wrote and implement it now" | stop or route to separate implementer unless maintainer acceptance provides source truth | same-role design -> implementation |
| reviewer fixes own finding | reviewer reports issue, edits fix, then claims clean review passed | require new reviewer for follow-up fix | self-fix + self-approve |
| skill author audits own skill change | author modifies skill then runs skill-audit on same change | mark audit not independent; require clean skill reviewer | accepted skill-audit pass |
| prototype creator verifies frontend contract | creator builds visual packet and claims frontend-ready | require independent contract/browser review | frontend-ready claim |
| dispatch package lacks role owners | material task package has runtime route but no clean reviewer/verifier owner | blocked / needs role separation fields | executable package |
| tests pass but UX claim unreviewed | implementer ran unit tests and claims UX ready | partial self-check; require browser/UI independent evidence | UAT-ready |

---

## 9. Output Field Amendments

### Implementation final report

Add fields:

```text
Role: implementer
Design Source: user-provided | independent PRD | self-authored draft | unknown
Self-check Evidence:
Clean Review Evidence: none | provided | required
Independent Verification Evidence: none | provided | required
Readiness Boundary: self-check only / independently reviewed / independently verified / blocked
Required Next Independent Role:
```

### Verification report

Add fields after `Verification Scope`:

```text
Role Separation
- Implementer Role:
- Reviewer Role:
- Verifier Role:
- Same-session Evidence Present:
- Independent Review Status:
- Independent Verification Status:
```

### Handoff / closeout package

Add fields:

```text
Independent Review Status:
Independent Verification Status:
Self-check Evidence Included:
Role Separation Gaps:
Next Independent Role Required:
```

---

## 10. Non-negotiable Boundaries

Groundwork must never use these as independent review or readiness evidence:

- the implementer's own summary;
- the implementer's own self-review;
- same-session verification of the implementer's own claims;
- old test runs without current scope mapping;
- visual packet polish;
- prototype behavior without source or browser/runtime evidence;
- skill-audit authored by the same role that changed the skill;
- clean review from a reviewer who also silently modified the reviewed files;
- dispatch package completeness without separate result evidence.

When independent review is required but unavailable, the correct output is:

```text
Blocked: independent review unavailable.
Evidence available: implementation self-check only.
Next action: route to clean reviewer / verifier / maintainer acceptance.
```

---

## 11. Fold-in Instructions

Before v0.5 PRD acceptance, fold this addendum into `docs/prd-v0.5-prototype-first-skill-expansion.md` as:

1. a new hard-rule section after the executive summary;
2. a non-goal bullet against self-sealing loops;
3. `FR-590` through `FR-598` under functional requirements;
4. `AC-21` through `AC-30` under acceptance criteria;
5. `V050-001A` under issue slices;
6. role separation fields under implementation, verification, dispatch, handoff, and skill-audit sections;
7. hard-negative eval rows under regression coverage.

This addendum must not remain optional implementation guidance. It is a required amendment to the v0.5 product scope.
