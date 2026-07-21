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

## Conditional UAT Evidence Window

After the required `release_evidence_claim`, add this conditional block when UAT behavior is attributed to a fix/artifact/deployed version, the environment can change, the run crosses sessions, or a finding is fixed, redeployed, and rerun:

```text
UAT Evidence Window
- Claim / Delivery Scope:
- Relevant SUT Fingerprint:
- Preconditions:
- Window Stability:
- Coverage Basis:
- Result / Missing:
- Rerun Of / Supersedes:
```

Bind only the causally relevant SUT identities: scope comes from declared delivery scope (plans/diffs are inputs, not complete truth); fingerprint records expected/observed identity or `unverified`; preconditions are claim-relevant gates; stability uses exactly one finite production — `stable`, `changed|restart_required`, `unverified`, or `observed_at:<id>|stability_unverified`; coverage names inputs and exclusions; result distinguishes `pass`, `partial`, `fail`, `blocked`, and `observed_only`; rerun links the original check and superseded window. Do not mix stability productions or repeat `observed_at`. Partition or invalidate evidence after an identity change, and use a new fingerprint/window after redeploy. Omit the block for a one-shot current behavior observation already bound by ordinary scope/UI/runtime context with no broader version attribution, redeploy/rerun, mutable-window risk, or continuation need. The block binds evidence; it is not deployment, runtime, browser, UAT, or release evidence by itself.

Rules:

- Documentation, schema, fixture, PRD, issue-pack, implementation summary, handoff, wiki, or diff-only evidence must set runtime, cache, release, UAT, marketplace, and cache-refresh evidence to `unverified` or `not_applicable`.
- `evidence_status: verified` requires named qualifying evidence for the specific claim, including the installed plugin root for Groundwork runtime/cache/marketplace claims, source root, cache/source refresh or equivalence method, run scope, commands or trials, and limitations.
- `evidence_status: unverified` may use an empty `commands_or_trials` list when no qualifying trial ran, but it must name at least one concrete limitation. If a non-qualifying or incomplete trial ran, record it without upgrading the status.
- `claim_type: not_applicable` and `evidence_status: not_applicable` must appear together. Use `not_applicable` for installed root, source root, refresh method/evidence, and run scope; keep `commands_or_trials: []`.
- A verified Groundwork `runtime`, `cache`, `marketplace`, or `cache_refresh` claim requires one adjacent, terminal-success activity chain: (1) under the `CODEX_HOME` derived from an exact `.../plugins/cache/groundwork/groundwork/<version>` installed root, a supported `codex plugin list/show` inventory step for `source_equivalence`, or `codex plugin add` for `refresh_step`, must positively report that root; (2) the immediately next completed activity must recursively compare the complete installed root with an independent declared source root, with no ancestor/descendant or realpath alias, excludes, normalization, partial-file comparison, dry-run, or no-op behavior. A verified runtime claim additionally requires the immediately next completed activity to run the repository's canonical `evals/run_runtime.py` under the same `CODEX_HOME`, without `--validate-schema`, to match every named typed trial, and to emit a non-empty summary whose run scope, selectors, complete prompt-file sources, actual requested/executed case IDs, counts, types, and all-pass result agree exactly. Exact trial identities are `suite:<registered-suite.csv>`, `group:<exact-group>`, `case_id:<exact-id>`, and `prompt_file:<canonical-absolute-path>`; a registered suite may additionally use a legacy alias only when that alias is globally unique. A rerun-failures path or filename is not trial identity. `GROUNDWORK_REPO`, when explicitly present in a proof command, must be the canonical current repository path. Evaluator-owned child processes remove inherited execution-changing Groundwork, shell, loader, Git, Node/npm, Python/pytest, Cargo/Rust, Go, compiler, Java/Maven, and Gradle variables and replace `PATH` with a non-empty controlled proof path. They launch through each tool's captured absolute launcher; a missing trusted launcher blocks the command, and a non-existent absolute sentinel path prevents current-directory fallback when no trusted tool directory exists. `HOME` and XDG state are replaced by a neutral proof home bound to the selected run root. `CODEX_HOME` remains only when it resolves to a separately digested absolute safe control path; invalid explicit values are removed rather than inherited. Hook-trust bypass is accepted only through the explicit debug CLI selector, never from ambient environment; its effective value and digest are recorded, the run becomes `insufficient_evidence`, and it cannot support `evidence_status: verified`. Retained router-control key names, a digest of their non-secret values, enforced-environment metadata, and proof-policy digests are recorded without secret values. Proof executables are discovered only from evaluator-controlled directories, reject launchers, resolved files, and ancestors owned or writable by the evaluator identity, and must continue to match their captured launcher/resolved stat identity and SHA-256; Python aliases must resolve to `sys.executable`. Node test evidence accepts `--test` and reporter options only in the interpreter-option prefix before the first positional script target or `--`. If no qualifying Codex launcher or toolchain exists, proof-grade runtime launch or command evidence fails closed rather than trusting a user-managed root. Ambient startup `PATH` entries, arbitrary same-named paths, same-path replacement, delegated package-manager test scripts, direct or module-form pytest hooks, non-canonical runtime scripts, and git-status checks outside the canonical case workspace fail closed. This is launch-trust binding and tamper detection, not binary-signature or supply-chain attestation. Empty selections and zero-row summaries do not qualify.
- Test-command evidence accepts only Node `--test` under the default or explicit `--test-isolation=process` mode with trusted options and a native summary. `--test-isolation=none`, empty values, and unknown isolation modes fail closed because repository test files would share the runner process and could forge its output and termination. Python `unittest`, Go, Cargo, direct or module-form pytest, and delegated package-manager output remain unverified because repository-controlled discovery modules, `TestMain`, execution wrappers, custom harnesses, hooks, or scripts can forge runner-looking output and successful termination. Proof-grade support for these runners requires evaluator-owned execution telemetry that the tested repository cannot forge.
- Observed tool evidence must be a completed terminal-success result. Command results additionally require an integer, non-boolean zero exit code and a trusted baseline/live-resolved executable; an arbitrary same-named path or package override does not qualify. Structured fixture source must use a trusted server/tool pair and exact canonical content; browser command evidence must be observation-producing and return substantive non-error output. Tool names, acknowledgements, arbitrary providers, wrapped source substrings, `playwright open`, help/version, discovery/listing, all-skipped/zero-execution runs, and empty command output do not qualify.
- Generic `release` claims cannot be self-verified by the deterministic runner; they require a separate maintainer decision adapter. Generic `uat` claims likewise require a claim-specific canonical UAT evidence adapter. Until that evidence is available, use `unverified`.
- Non-plugin UAT evidence may use `installed_plugin_root: not_applicable` and `cache_or_source_refresh.method: not_applicable`, but it still requires a concrete source root, targeted/full scope, and named qualifying trials.
- The final response cannot create its own observed evidence merely by writing `passed`, `verified`, `browser`, `runtime`, or a command name. Observed evidence must come from user-provided source truth, an inspected canonical evidence record, or runner/tool activity outside the claim text.
- Release readiness is not inferred from PRD acceptance, issue-pack completion, fixture pass, clean review, source-validation checks, or package completeness alone.
- Codex App Handoff execution evidence is separate from Groundwork package/schema evidence and must appear under `commands_or_trials` or another direct trial record before it can support a handoff-readiness or release claim.
