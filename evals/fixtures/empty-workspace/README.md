# Empty Workspace Fixture

This fixture is intentionally almost empty.

Use it to test that `write-plan` does not invent file paths, APIs, schemas,
commands, or tests when a task has no source evidence.

Expected behavior:

- report that no source files or tests are available
- avoid exact file paths beyond files that were actually inspected
- propose first inspection or validation steps instead of pretending the repo
  has a conventional layout
