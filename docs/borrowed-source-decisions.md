# Borrowed Source Decisions

Groundwork records borrowed sources before implementing public skills so the plugin does not become a loose bundle.

| Groundwork area | Source | Decision | Reason | Groundwork-specific changes |
| --- | --- | --- | --- | --- |
| `to-prd` | `mattpocock/skills` `to-prd`; Spec Kit; Trellis PRD discipline | adapt | These sources reinforce compact product intent and acceptance criteria. | Keep conversation-first output and avoid automatic file creation. |
| `to-issues` | `mattpocock/skills` `to-issues`; Spec Kit task slices | adapt | Vertical slicing is useful without adopting a tracker runtime. | Keep tracker-neutral markdown and no API calls in MVP. |
| `triage` | `mattpocock/skills` `triage` and `AGENT-BRIEF.md` | adapt | Readiness and AFK/HITL routing are central to Groundwork. | Use Groundwork readiness contracts; defer `OUT-OF-SCOPE.md`. |
| `write-plan` | Superpowers `writing-plans` | adapt | Planning discipline is useful but the source is heavier than Groundwork MVP needs. | Keep plan concise and avoid commit-heavy or subagent-first defaults. |
| `prototype` | `mattpocock/skills` `prototype`, `LOGIC.md`, `UI.md` | keep and adapt | The throwaway prototype branch model fits Groundwork directly. | Add static HTML review, browser evidence fallback, feedback-to-PRD/task/contract, and cleanup decision. |
| `implement` | Trellis implement/check; Superpowers execution discipline; mattpocock diagnose/review signals | merge | Groundwork needs scoped execution without adopting a peer runtime. | Require diagnosis before speculative bug fixes and stop before final readiness claims. |
| `verify` | Superpowers verification; gstack QA; GSD UAT evidence | merge | Evidence-first readiness is Groundwork's quality lever. | Make verification skeptical and separate claimed behavior from evidence and unverified claims. |
| `handoff` | `mattpocock/skills` `handoff` | adapt | Compact continuation fits long-running R&D sessions. | Reference artifacts instead of duplicating PRDs, plans, issues, commits, or diffs. |
| skill authoring and eval | Codex `skill-creator`; Claude Code create-skill style workflows; mattpocock `write-a-skill` | use as authoring helper | These improve skill description, progressive disclosure, validation, and forward-testing discipline. | Use for authoring review and fixture baseline; do not expose as public Groundwork skills. |

License and usage boundaries must be rechecked before publishing or vendoring substantial source text.
