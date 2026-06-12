---
name: identify-key-failures
description: Synthesize the common stuck points across failed decomposition plans and recursive sub-agent reports. Use when the current batch of decomposition plans has failed.
---

## When to use

When the current batch of decomposition plans has failed.

## Output

Append to `failed_paths` a `key_failures_summary` record with `failed_plan_ids`, `plan_failures` (plan_id + stuck_points), `common_failures`, and `implications_for_next_plans`. If reports are too weak, append a `key_failures_inconclusive` event instead.

## Steps

1. Gather failed plan reports, sub-agent reports, and existing `failed_paths`.
2. List key stuck points per plan.
3. Identify common patterns: recurring obstructions, counterexamples, decomposition patterns that break, missing facts.
4. Summarize what the failures suggest for the next generation of plans.
5. Save synthesized failure knowledge to `failed_paths` and return control to `$propose-subgoal-decomposition-plans`.
