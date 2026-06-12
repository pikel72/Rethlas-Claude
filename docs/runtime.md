# Runtime Layout

Rethlas writes all run state to the current Claude project directory:

```text
.rethlas/runs/<run_id>/
```

Each run may contain:

- `input.md`
- `meta.json`
- `blueprint.md`
- `verification.json`
- `blueprint_verified.md`
- `attempts/<nnn>/blueprint.md`
- `attempts/<nnn>/verification.json`
- `memory/*.jsonl`
- `downloads/`
- `logs/`

`blueprint_verified.md` is the success marker. It must only be written after a verifier report with verdict `"correct"` and no critical errors or gaps.
