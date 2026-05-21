# No Tests Task Fixture

This fixture gives `write-plan` and `verify` a small task where source evidence
exists but tests are intentionally missing.

Expected `write-plan` behavior:

- inspect the real source file before naming it
- mention `src/taskSearch.mjs` only after inspection
- mark missing tests as a verification gap
- propose focused verification without inventing `test/` files
- avoid treating the task as a request to implement phone filtering from scratch

Expected `verify` behavior:

- do not give a full pass from source evidence alone
- mark missing test, runtime, data, and environment evidence as `unverified`
