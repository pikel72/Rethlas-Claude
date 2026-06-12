---
name: record-keeping
description: Guide for writing solver memory records that maximize reuse in subsequent loop iterations. Use before calling `memory_append`, especially on the first attempt or when a previous attempt's records were not useful.
---

# Record Keeping

Write records the next loop iteration can consume directly. The model decides whether to follow.

## When to use

Before a `memory_append` call whose record will be read by a future attempt.

## Output

A record another iteration can pattern-match without re-deriving context.

## Steps

1. State the claim or event in one short sentence.
2. Include minimum fields the next iteration needs: `id` for subgoals, `witness` for counterexamples, `why_failed` for failures, `source` for conclusions.
3. Prefer concrete nouns. Don't embed full proofs — the proof lives in `blueprint.md`; the record is a pointer.
4. For failures, write enough to avoid the path, not just note that it failed.

## Quick reference

- `subgoal`: `id`, `claim`, `dependencies`, optional `status`
- `failed_path`: `what_tried`, `why_failed`
- `counterexample`: `statement`, `witness`
- `proof_step`: `step`, `justification`
- `immediate_conclusion`: `claim`, `source`
- `toy_example`: `example`, `where_assumptions_take_effect`

This is a reference. No validation enforces record shapes; the model decides.
