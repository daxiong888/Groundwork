# Groundwork v0.1 Plugin Discovery Baseline

Status: completed as local packaging/discovery validation.

This baseline checks local plugin structure and skill discoverability from files. It does not prove Codex App runtime installation or implicit trigger behavior.

## Scope

- `.codex-plugin/plugin.json`
- `skills/*/SKILL.md`
- `evals/prompts/*.csv`

## Checks

- plugin manifest parses as JSON
- plugin name is `groundwork`
- manifest `skills` path is `./skills/`
- manifest `skills` path exists
- version and description are present
- `interface.defaultPrompt` has at most 3 entries and each is within 128 characters
- exactly eight public skill folders contain `SKILL.md`
- each skill frontmatter has matching `name`
- each skill frontmatter has a `description` with trigger wording
- each skill description is under 1024 characters
- each public skill has a matching prompt fixture CSV
- each prompt fixture CSV has the expected columns and 5 rows

## Result

```text
plugin discovery validation passed
WARN: homepage empty
WARN: repository empty

Skill quick validation: 8/8 passed
Prompt fixture validation: passed
```

## Notes

`homepage` and `repository` are publication metadata warnings, not blockers for local v0.1 runtime trials.

No repo-root `.agents/plugins/marketplace.json` was created in this pass. The repository itself is the plugin root; generating a marketplace entry now would introduce the `./plugins/<plugin-name>` convention and is better deferred until the actual installation path is chosen.

## Next Step

Run a runtime-oriented trial against the actual Codex plugin loading environment. Capture whether Codex installs/enables the local plugin, discovers the eight skills, selects the expected skill for representative prompts, falls back directly for tiny work, avoids artifacts, and gates risky writes.
