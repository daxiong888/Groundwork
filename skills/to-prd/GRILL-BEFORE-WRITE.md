# GRILL-BEFORE-WRITE

Use this gate before drafting or revising any PRD output.

## Mandatory pre-write check

Do not write PRD content until all four buckets are explicitly listed:

1. **Known Facts** (verified from user input or cited evidence)
2. **Assumptions** (inferences not yet verified)
3. **Open Questions** (decision-blocking unknowns)
4. **Target Reader** (who must review/decide next)

If any bucket is missing, stop and add it first.

## Clarification hardening

- Never invent business state, policy, metrics, owner, timeline, or field values.
- Any unknown business state or missing field must be labeled **NEEDS CLARIFICATION**.
- If a required acceptance detail is unknown, mark it **NEEDS CLARIFICATION** instead of guessing.

## Write gate

You may proceed to PRD writing only when:

- the four buckets are present,
- assumptions are clearly separated from facts,
- unknown business details are tagged **NEEDS CLARIFICATION**.
