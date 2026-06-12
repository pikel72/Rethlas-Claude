---
name: verify-proof
description: Verify candidate proofs by invoking the Rethlas verifier agent. Use only when a full candidate proof of the entire problem has been assembled in markdown, and before publishing the final verified blueprint.
---

## When to use
When a full candidate proof of the entire problem has been assembled in `blueprint.md`.

## Output
`blueprint_verified.md` on success; raw `verification.json` otherwise.

## Steps
1. Read `blueprint.md` as plain markdown text.
2. Invoke `Agent(rethlas:verifier)` with `run_id`, `attempt`, `statement`, and `proof` from the blueprint.
3. Read `verification.json` returned by the verifier.
4. If `verdict` is `"wrong"` or `critical_errors` or `gaps` are non-empty, treat as failed. Otherwise write `blueprint_verified.md`.
