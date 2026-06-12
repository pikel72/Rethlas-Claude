---
name: search-math-results
description: Find math theorems, constructions, examples for subgoal proving.
---
# Search Math Results
## When to use
When a target statement needs external math references.
## Output
Append to `events` with useful refs; log stalled if none.
## Steps
1. Search arxiv with full statement.
2. Download papers to `downloads/`, extract and read.
3. Read proofs; extract techniques.
4. Expand definitions; check applicability.
5. Note partial-result obstructions.
6. Fall back to `WebSearch`.
Useful if: close to target, adaptable, relevant technique, or obstruction.
