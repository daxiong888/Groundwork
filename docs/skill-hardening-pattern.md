# Skill Hardening Pattern

Target Reader: Groundwork maintainers hardening existing public skills.
Reader Action Needed: Apply a compact, repeatable pattern when adding skill guardrails.
Decision Supported: Whether a hardening rule belongs in the owning skill or in `skills/_shared/`, and what minimum verification is required.
Scope: Maintainer-facing pattern for `CHECKPOINTS`, `Failure Branches`, `Do Not`, ownership boundaries, issue references, and validation expectations.
Out of Scope: General skill authoring, new public skills, model-trial design, issue tracker mutation, and copying one skill's concrete guardrails into another skill.
Evidence Level: Derived from PR #35's `to-prd` hardening trial, issue #42 acceptance criteria, and existing hardening examples across Groundwork skills.

Use this pattern when a hardening issue improves an existing Groundwork skill by making real failure boundaries easier to scan and harder to bypass. The goal is not to make every skill longer. Each hardening increment for one skill should normally add only 15-30 lines, biased toward incident-backed guardrails that would have prevented or shortened a real failure.

## Placement

Keep this document as the maintainer-facing, normative pattern.

Put runtime text in `skills/_shared/` only when a hard rule is actually referenced by runtime skills. A rule qualifies for `_shared` when it is repeated in three or more owning skills, or when it is truly cross-skill and maintainers need one shared wording. High-risk anti-patterns that are specific to one workflow stay inside that owning skill, even if they look generally useful.

Do not move a rule to `_shared` just to make a skill file look shorter. Extraction must reduce duplicate runtime behavior without hiding a skill-specific stop condition.

## Section Pattern

### CHECKPOINTS

Use `CHECKPOINTS` for stop-before-action gates. A checkpoint should say:

- exactly when to stop;
- what evidence, source truth, or bounded plan is missing;
- what action is allowed next.

Write checkpoints as a short list of high-impact `STOP before...` rules. Prefer three to five concrete gates over a broad policy summary. Do not include generic virtues such as "be careful", and do not restate rules that already live in platform, repo, or shared guidance unless the skill needs a workflow-specific trigger.

### Failure Branches

Use `Failure Branches` for deterministic fallback paths when a checkpoint or workflow step cannot proceed. The table should normally include:

```text
| Trigger | Action | Output Requirement |
|---|---|---|
```

`Trigger` names the failure condition. `Action` says what the skill does instead. `Output Requirement` names what the agent must report so the failure is reviewable. Failure branches should prevent silent fallback, fake precision, and accidental scope expansion. Do not duplicate every checkpoint as a branch; add a branch only when maintainers need a specific if-then behavior.

### Do Not

Use `Do Not` for concrete forbidden behaviors that have meaningful workflow risk. Good entries name the dangerous action, not the desired virtue. For example, forbid inventing source truth, bypassing a gate, promoting mock data, or claiming a check passed when it was not run.

Keep broad safety or platform policy out of a skill unless the owning workflow creates a sharper local risk. Skill-specific high-risk anti-patterns stay in the owning skill because colocated warnings are easier to apply at the moment of action.

## Hardening Workflow

Before editing a skill, identify the real failure pattern: the incident, review finding, behavior failure, or maintainer correction that the new guardrail should catch. Then decide the smallest owning surface:

1. Start in the owning skill when the failure is workflow-specific.
2. Extract to `skills/_shared/` only after the three-skill repetition threshold or a true cross-skill runtime need is met.
3. Keep each increment compact, normally 15-30 lines per skill.
4. Prefer one strong checkpoint, one fallback branch, or one precise `Do Not` over several generic rules.
5. Avoid copying `to-prd` or any other skill's concrete content into another skill unless the same failure mode is proven for that workflow.

Future hardening issues for `verify`, `implement`, `prototype`, `handoff`, `to-issues`, `triage`, and `write-plan` should reference this document. Each issue should name the target skill, the failure mode being hardened, whether `_shared` is in scope, and the expected minimum validation.

## Minimum Validation

After a hardening change, run the fastest checks that prove the touched surface is internally consistent:

```bash
git diff --check
python3 -m json.tool .codex-plugin/plugin.json >/dev/null
python3 -m unittest <narrowest-tests.module>
```

Also run a link or path check for any new reference. For docs-only changes with no inbound reference, file existence is enough.

Run a runtime-neutrality check against the diff or changed files. The report must not claim installed plugin cache refresh, runtime evidence, model-trial coverage, browser evidence, or release readiness unless those checks actually ran.

Finally, get a clean subagent dry-run or equivalent read-only re-review focused on whether the pattern reduces duplication instead of adding ceremony. The reviewer should check that new rules are incident-backed, compact, owned by the right surface, and not copied from another skill without evidence.
