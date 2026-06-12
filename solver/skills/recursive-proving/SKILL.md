---
name: recursive-proving
description: Delegate plans to subgoal-prover agents when direct-proving hits stuck points.
---

## When to use

When `$direct-proving` fails on all plans.

## Output

Append `recursive_proving_round` event. Call `$identify-key-failures` on failure.

## Steps

1. Confirm all plans tried with `$direct-proving`.
2. Per plan, invoke `Agent(rethlas:subgoal-prover)` with target theorem, plan, its stuck points and peer stuck points. No nested subagents.
3. Gather results; assemble proof draft if any succeed.
4. Route failure reports to `$identify-key-failures`.
