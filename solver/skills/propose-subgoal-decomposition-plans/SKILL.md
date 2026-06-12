---
name: propose-subgoal-decomposition-plans
description: Propose multiple subgoal decomposition plans for the current theorem using the information already gathered.
---

# Propose Subgoal Decomposition Plans

## When to use
When enough context exists to propose materially different decomposition plans for the current theorem.

## Output
Append one `decomposition_plan` record per plan to `subgoals` (see schema). One-line JSON: `{"plan_id","record_type":"decomposition_plan","goal","plan_summary","subgoals":[...],"motivation":[...],"uses_information_from":{...},"status":"proposed|screening|screened|selected|failed|solved"}`. Also append an `events` summary.

## Steps
1. Gather constraints: examples, counterexamples, failed_paths, search results.
2. Propose materially different plans. Per plan: main idea, ordered subgoals, motivation from current information, which failures it avoids.
3. Hand each plan to `$direct-proving` for quick screening.
4. If no meaningful plans possible, append `decomposition_plans_not_ready` event with missing info and blockers.
