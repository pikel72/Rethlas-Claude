---
name: rethlas
description: Natural-language entry for Rethlas math agent.
allowed-tools: "Read, Write, Edit, Glob, Grep, Bash, WebSearch, WebFetch, Skill, Agent, mcp__*"
---

## When to use
User asks in natural language (Chinese or English) to solve, prove, or verify math with Rethlas.

## Output
Proof at `.rethlas/runs/<id>/blueprint_verified.md`.

## Steps
1. Infer `problem_file`, `reference_dir`, `max_attempts` (default 8).
2. Search `problems/`, `data/`, `theorems/`, cwd for markdown; ask if ambiguous.
3. Look for `<stem>.refs`, `refs`, `references` for refs.
4. Run `/rethlas-solve`.
