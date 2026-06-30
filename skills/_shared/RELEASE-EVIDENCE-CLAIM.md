Target Reader: Groundwork verifiers, dispatch package authors, implementers, handoff authors, and reviewers.
Reader Action Needed: Use this shared object whenever a runtime, cache, release, UAT, marketplace, installed-plugin, or cache-refresh claim is made or explicitly scoped out.
Decision Supported: Whether a claim has named qualifying evidence or must remain unverified/not applicable.
Artifact Type: shared evidence claim schema.
Source of Truth: `skills/verify/SKILL.md`, `skills/dispatch/DISPATCH-PACKAGE.md`, and `skills/_shared/RUNTIME-CAPABILITY.md` evidence-boundary rules.
Scope: Machine-readable evidence object for runtime/cache/release/UAT/marketplace/cache-refresh claims.
Out of Scope: Running checks, refreshing plugin caches, publishing releases, approving UAT, or proving customer readiness by itself.
Evidence Level: Schema/source-validation contract only. A populated object is evidence inventory; only named commands, trials, cache/source checks, or release artifacts can verify a claim.
Safe to Share / Redaction Notes: Safe to share as-is; redact private paths, tokens, private URLs, credentials, customer data, and sensitive logs before embedding real evidence.

# Release Evidence Claim

Use this exact object when a material claim touches runtime, cache, release, UAT, marketplace, installed-plugin, or cache-refresh evidence:

```yaml
release_evidence_claim:
  claim_type: runtime | cache | release | uat | marketplace | cache_refresh | not_applicable
  claim: ""
  evidence_status: verified | unverified | not_applicable
  installed_plugin_root: ""
  source_root: ""
  cache_or_source_refresh:
    method: refresh_step | source_equivalence | not_run | not_applicable
    evidence: ""
  run_scope: targeted | full | not_run | not_applicable
  commands_or_trials: []
  limitations: []
```

Rules:

- Documentation, schema, fixture, PRD, issue-pack, implementation summary, handoff, wiki, or diff-only evidence must set runtime, cache, release, UAT, marketplace, and cache-refresh evidence to `unverified` or `not_applicable`.
- `evidence_status: verified` requires named qualifying evidence for the specific claim, including installed plugin root when plugin/cache behavior is claimed, source root, cache/source refresh or equivalence method, run scope, commands or trials, and limitations.
- Release readiness is not inferred from PRD acceptance, issue-pack completion, fixture pass, clean review, source-validation checks, or package completeness alone.
- Codex App Handoff execution evidence is separate from Groundwork package/schema evidence and must appear under `commands_or_trials` or another direct trial record before it can support a handoff-readiness or release claim.
