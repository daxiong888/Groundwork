# Git Boundary Context Fixture

Target Reader: Groundwork maintainers running guardrail regression prompts.
Reader Action Needed: Use this fixture when the eval should be isolated from the real repository root.
Decision Supported: Whether `verify` can preserve an explicit intended/unrelated git boundary from provided evidence.
Scope: Static context for git-boundary prompt behavior.
Out of Scope: Creating an actual nested git repository, staging files, committing files, or modeling remote operations.
Evidence Level: `GIT-BOUNDARY-CONTEXT.md` contains the fixture's simulated read-only git evidence.

Use this fixture with `gr-008a`. The repo-root git-boundary behavior is covered separately by `gr-008b`.
