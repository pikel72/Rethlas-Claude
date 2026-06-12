---
name: construct-counterexamples
description: Test whether a conjecture, lemma, or intermediate claim can be refuted by constructing counterexamples.
---

# Construct Counterexamples

## When to use

When a proposed conjecture, lemma, or intermediate claim feels fragile or unproved — test whether the assumptions can hold while the claimed conclusion fails.

## Output

Append to `counterexamples`: `target_claim`, `candidate_counterexample`, `status` (`refuted`|`not_refuted`|`inconclusive`), `assumptions_satisfied`, `failed_conclusion`, `impact`. If refuted, also append to `failed_paths`. For informative non-refuting examples, use construct-toy-examples.

## Steps

1. Identify the assumptions that must hold and the conclusion to fail.
2. Search for standard obstructions, pathological constructions, or previously known counterexamples.
3. Classify status as `refuted` (claim fails), `not_refuted` (none found), or `inconclusive` (search space unclear).
4. If refuted, mark impacted branches/lemmas as invalid. If not refuted, treat as evidence only, not proof.
