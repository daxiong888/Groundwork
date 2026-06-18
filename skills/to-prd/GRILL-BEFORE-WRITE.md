# GRILL-BEFORE-WRITE

Use this gate before drafting or revising any PRD output.

## Mandatory pre-write check

Do not write PRD content until all six buckets are explicitly listed:

1. **Target Reader** (who must review or decide next)
2. **Decision Supported** (the decision or action the PRD must enable)
3. **Known Facts** (verified from user input or cited evidence)
4. **Assumptions** (inferences not yet verified)
5. **Open Questions** (decision-blocking unknowns)
6. **Needs Confirmation** (unknown business facts, fields, states, permissions, user behaviors, or acceptance details that must not be invented)

If any bucket is missing, stop and add it first.

## Evidence-first clarification

- Inspect local code, docs, tickets, data, or prototype notes first when they can answer a question without user input.
- Ask the user only for unknowns that remain after available evidence has been checked.
- Ask at most 5 high-impact clarification questions.
- In interactive work, ask one question at a time.
- Include a recommended answer or default decision and the impact of the answer for each clarification question when evidence supports one.

## Clarification hardening

- Never invent backend fields, business states, policy, metrics, owner, timeline, field values, or unsupported abilities.
- Any unknown backend field, business state, unsupported ability, or missing acceptance detail must be labeled **NEEDS CLARIFICATION**.
- If a required acceptance detail is unknown, mark it **NEEDS CLARIFICATION** instead of guessing.
- Do not mutate product truth based on prototype-only mock data.

## Write gate

You may proceed to PRD writing only when:

- the six buckets are present,
- assumptions are clearly separated from facts,
- remaining questions are limited to the highest-impact unknowns,
- each listed question has a recommended answer or default and impact when possible,
- unknown business details are tagged **NEEDS CLARIFICATION**.
