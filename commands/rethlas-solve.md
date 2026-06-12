---
description: Run the Rethlas proof-generation and verification workflow on a project-local math problem.
argument-hint: <problem.md> [--refs <reference-dir>] [--max-attempts <n>]
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, WebSearch, WebFetch, Skill, Agent, mcp__*
---

# Rethlas Solve

Run the Rethlas workflow in the current Claude Code session. This command is invoked as `/rethlas-solve`. Do not spawn a `solver` subagent and do not start a nested Claude process.

## Inputs

Parse the command arguments as:

- the project-local markdown problem file path
- optional `--refs <reference-dir>` containing user-provided references
- optional `--max-attempts <n>`, default `8`

Resolve paths relative to the current project directory. Reject absolute paths outside the project and any path containing `..`.

## Runtime

Create one run directory under:

```text
.rethlas/runs/<run_id>/
```

Use a stable readable `run_id`, based on the problem file stem plus a UTC timestamp. Store:

- `input.md`
- `meta.json`
- `blueprint.md`
- `verification.json`
- `blueprint_verified.md` only after verification passes
- `attempts/<nnn>/blueprint.md`
- `attempts/<nnn>/verification.json`
- `memory/*.jsonl`
- `downloads/`
- `logs/`

Use the solver MCP tools for memory and branch state. Use the same `run_id` as the solver `problem_id`.

## Workflow

Follow the Rethlas solver protocol:

1. Read the problem markdown completely.
2. Read supported reference files from the refs directory if provided. Supported direct files are `.md`, `.tex`, and `.txt`. If PDFs are present, record that they need text extraction before use unless extracted text is already available.
3. Initialize project-local memory using `memory_init`.
4. Work adaptively with the Rethlas solver skills: immediate conclusions, search, examples, counterexamples, decomposition, direct proving, recursive/subgoal work, failure analysis, and proof verification.
5. Produce a complete candidate proof blueprint before verification.
6. For every verification attempt:
   - write `attempts/<nnn>/blueprint.md`
   - invoke `Agent(rethlas:verifier)` with the original statement, full proof markdown, run id, attempt number, and expected output path
   - require the verifier to write `attempts/<nnn>/verification.json`
   - copy the latest attempt artifacts to `blueprint.md` and `verification.json`
   - append the verifier report to solver memory
7. If `verdict` is `"wrong"` or any critical errors/gaps are present, repair the proof and verify again.
8. Stop successfully only when the verifier returns `"correct"` with no critical errors and no gaps; then write `blueprint_verified.md`.
9. If `max-attempts` is reached, stop without writing `blueprint_verified.md` and report the best current blueprint plus the latest repair hints.

## Verification Contract

The verifier is authoritative for acceptance. Never claim the theorem is solved unless `.rethlas/runs/<run_id>/blueprint_verified.md` exists and was produced after a correct verifier report.

When using external mathematical results, preserve complete statements and source identifiers in memory and in the proof text.
