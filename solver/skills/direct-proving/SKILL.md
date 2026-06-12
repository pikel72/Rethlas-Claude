---
name: direct-proving
description: Screen a decomposition plan by first trying to prove all of its subgoals directly, then identifying the key stuck points if the plan does not fully go through. Use when a decomposition plan is created.
---

# Direct Proving

## When to use
When a decomposition plan is created.

## Output
Append to `proof_steps` with attempt_type "direct", status per subgoal (solved/partial/stuck), and key_stuck_points.

## Steps
1. Take one plan. Use relevant results from obtain-immediate-conclusions, toy examples, counterexamples.
2. Attempt to prove every subgoal directly. Try adapting known proof ideas. If a theorem has extra hypotheses, analyze why they are needed before applying.
3. If a subgoal blocks, try construct-counterexamples before moving on.
4. If all subgoals solve, mark plan solved. Otherwise identify key stuck points concretely.
5. Update subgoals record to screening/screened/solved.
