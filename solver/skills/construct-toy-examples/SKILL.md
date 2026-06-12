---
name: construct-toy-examples
description: Generate and analyze simpler examples that satisfy both the assumptions and the conclusion of a theorem statement or subgoal. Use when you are stuck in reasoning and need simpler examples to regain traction, when you need simpler examples that satisfy both assumptions and conclusion, or when you want to see where the assumptions take effect and gain intuition.
---

# Construct Toy Examples

## When to use
When stuck in reasoning and need simpler examples that satisfy both assumptions and conclusion to understand why the statement works. Opposite of construct-counterexamples: here the conclusion must hold, not fail.

## Output
Append to `toy_examples` — simple case description, why relevant, assumptions satisfied, conclusion verified, where each assumption takes effect, observed patterns.

## Steps
1. Construct simpler cases (low degree, small dimension, special forms, canonical objects) from current statement/subgoal.
2. Verify all assumptions hold and the conclusion follows.
3. Study where each assumption takes effect and what mechanism makes the conclusion true.
4. Identify repeated patterns or proof ideas.
5. If inconclusive, append `events` record with `event_type="toy_examples_inconclusive"`.
