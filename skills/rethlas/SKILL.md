---
name: rethlas
description: >
  Use when the user asks in natural language to solve, prove, verify, attack,
  or run Rethlas on a mathematical problem, theorem, conjecture, markdown file,
  or reference folder. Examples include Chinese or English requests such as
  using Rethlas to solve a problem, running the math agent, proving a markdown
  file, or using a refs directory as supporting context.
argument-hint: "[problem file or statement] [references]"
allowed-tools: "Read, Write, Edit, Glob, Grep, Bash, WebSearch, WebFetch, Skill, Agent, mcp__*"
---

# Rethlas Natural Language Entry

Use this skill to turn a natural-language request into the Rethlas workflow. The user should not need to remember `/rethlas-solve` or its flags.

## Intent

Trigger this workflow when the user asks to use Rethlas or a math agent to solve, prove, verify, or work on a math problem. Accept Chinese or English phrasing.

Common natural-language forms:

- "用 Rethlas 解决这个问题"
- "让数学 agent 证明 `problems/foo.md`"
- "用 `problems/foo.refs` 作为参考跑一下"
- "prove this theorem with Rethlas"
- "try Rethlas on the selected markdown file"

## Infer Inputs

Infer these values from the user's message and project context:

- `problem_file`: a markdown file path if one is mentioned or selected
- `reference_dir`: an optional sibling refs directory
- `max_attempts`: default `8` unless the user asks for a different limit

If no problem file is explicit, search likely project locations such as `problems/`, `data/`, `theorems/`, and the current directory for markdown files. If there is exactly one plausible candidate, use it. If there are multiple plausible candidates and the user did not identify one, ask a concise clarification.

If no refs directory is explicit, look for a sibling directory named `<stem>.refs`, `<filename>.refs`, `refs`, or `references`. Use it when the match is unambiguous; otherwise proceed without refs.

## Run Workflow

Run the same workflow as `/rethlas-solve` in the current Claude Code session:

1. Do not spawn a `solver` subagent and do not start a nested Claude process.
2. Create `.rethlas/runs/<run_id>/` in the current project.
3. Read the problem and references.
4. Initialize solver memory with MCP tools.
5. Generate a candidate proof blueprint.
6. Invoke `Agent(rethlas:verifier)` for each complete candidate proof.
7. Repair from verifier feedback until success or `max_attempts`.
8. Write `blueprint_verified.md` only after a verifier report with verdict `"correct"` and no critical errors or gaps.

If the user explicitly invokes `/rethlas-solve`, follow that command. If they ask naturally, execute this workflow directly without requiring the slash command.
