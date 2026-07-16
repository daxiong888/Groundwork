# Consumer-side Display Divergence

Canonical owner token: `canonical_contract`.

- The `storage` hop intentionally stores `CORRECT` or `ERROR`.
- The `service_transform` hop intentionally maps those raw values to `正确` or `错误` for list display.
- The `api` hop returns the transformed Chinese display value.
- The `frontend_renderer` hop still expects only `CORRECT` or `ERROR`; any other value falls back to `-`.
- The inspected storage, transform, and API behavior satisfy the contract. Do not move the fix upstream merely because tracing began there.
