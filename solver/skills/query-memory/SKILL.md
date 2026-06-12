---
name: query-memory
description: Retrieve prior conclusions, examples, counterexamples, failed paths, or branch states.
---

## When to use
When prior conclusions, examples, counterexamples, failed paths, or branch states may inform the current task.

## Output
Events record: `event_type="query_memory"`.

## Steps
1. Form a natural-language query.
2. Pick narrowest channels: `immediate_conclusions`, `toy_examples`, `counterexamples`, `failed_paths`, `branch_states`.
3. Call `memory_search`.
4. Summarize useful hits and proof-state impact.
5. If nothing useful, say so and try another skill.
