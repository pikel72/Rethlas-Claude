---
name: check-referenced-statements
description: Verify cited theorems via arXiv then WebSearch.
---

## When to use
When a proof cites external theorems.

## Output
`reference_checks` per citation: matched, gap, or critical_error.

## Steps
1. Query `search_arxiv_theorems`; expand cited-paper definitions.
2. Compare wording across paper and proof contexts.
3. Classify: matched (aligns), gap (hand-wavy), critical_error (mismatch or not found).
4. Retry with `WebSearch` if arXiv comes back empty.
5. Persist via `memory_append` to `reference_checks`.
