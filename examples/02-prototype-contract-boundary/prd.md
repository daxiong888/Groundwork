# PRD: Prototype Contract Boundary

Target Reader: Groundwork maintainer reviewing prototype behavior and contract safety.
Reader Action Needed: Decide whether prototype outputs must classify contract facts, mock fields, and client-derived logic.
Decision Supported: Whether Groundwork should prevent prototypes from silently redefining backend API contracts.
Scope: Prototype outputs that touch data shape, payload examples, state labels, filters, or business rules.
Out of Scope: Confirming backend source truth, changing production APIs, or turning a throwaway prototype into an accepted integration contract.
Evidence Level: `skills/prototype/SKILL.md`, `skills/prototype/CONTRACT-BOUNDARY.md`, and v0.2.x changelog/runtime evidence.

## Problem

A prototype can make a rule easier to understand, but it can also imply backend fields, statuses, or derived client logic that do not exist.

## Goal

Make prototype artifacts clearly separate confirmed contract facts from mock display data and client-derived view logic.

## Acceptance Criteria

- AC-1: Prototype output identifies backend contract candidates and labels whether they are source-backed or proposed hypotheses.
- AC-2: Mock fields are marked `mock / illustrative / not backend contract`.
- AC-3: Client-derived logic is marked `derived / illustrative / not backend contract`.
- AC-4: Prototype output includes `Contract Status`, `Confirmed Backend Fields`, `Mock / Illustrative Fields`, `Client-derived Logic`, and `Contract Impact`.
- AC-5: Prototype output does not present a frontend contract unless claims are source-backed or explicitly confirmed.

## Non-Goals

- Do not verify backend contract truth from prototype evidence alone.
- Do not promote prototype convenience IDs, statuses, enums, or derived filters into implementation requirements.
- Do not keep throwaway prototype code after the decision is answered unless there is a temporary retention reason.

