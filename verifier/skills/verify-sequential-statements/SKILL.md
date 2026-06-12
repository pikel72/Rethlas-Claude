---
name: verify-sequential-statements
description: Check a proof statement by statement for local correctness and reasoning gaps.
---

## When to use
When verifying a paper-style proof.

## Output
Append findings to `statement_checks` via `memory_append`.

## Steps
1. Extract hypotheses from `Statement`.
2. Iterate through statements in order.
3. Per statement: check inference, theorem use, definition match.
4. Flag as `critical_error` (invalid logic) or `gap` (missing step, definition mismatch).
5. Persist each via `memory_append`.
