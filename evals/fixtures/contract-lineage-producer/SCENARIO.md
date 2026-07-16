# Producer-side Contract Divergence

Canonical owner token: `canonical_contract`.

- The accepted contract says any valid keypad value matching `[0-9#*]{1,5}` produces `callResult=connected`.
- The observed producer hop token is `producer_mapping`. It still maps keypad `11` to `connected_no_key` because it accepts only the literal keypad `1`.
- The consumer hop token is `consumer`. It already implements the accepted `connected` and `connected_no_key` meanings.
- The proposed consumer-only workaround would reinterpret every non-empty `connected_no_key` as success.
- This flow has no persistence or index hop. Do not invent one.
