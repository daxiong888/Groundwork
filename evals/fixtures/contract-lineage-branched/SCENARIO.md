# Branched Contract With Missing Authority

## Canonical Lineage Facts

- Canonical Owner / Source: unverified
- Hops: producer_a(verified)|producer_b(verified)
- First Confirmed Divergence: unverified
- Fix Owner / Boundary: unverified
- Unverified / Branched Hops: canonical_owner|storage

- `producer_a` emits `ACTIVE`.
- `producer_b` emits `1` for the same apparent business state.
- No accepted schema, API contract, or explicit owner identifies either producer as the canonical source.
- The storage or index path has not been inspected.
- The accepted task is to plan the first inspections, not to choose a mapping or fix owner from field names.
- Keep `canonical_owner` and `storage` unverified until source evidence resolves them.
