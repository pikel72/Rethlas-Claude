# Rethlas Claude Code Plugin

Rethlas is a Claude Code plugin for project-local mathematical proof blueprint generation and verification.

It ports upstream `frenzymath/Rethlas` to Claude Code as a plugin. The workflow keeps the important Rethlas loop:

1. generate a candidate proof blueprint
2. verify it with an independent verifier agent
3. repair from the verifier report
4. repeat until the verifier returns a strict `correct` verdict or the attempt limit is reached

This repository intentionally does not include local fork features such as job control, LiteLLM presets, long-run viewers, or event streaming.

## Use

Install or load the plugin, then run Claude in your math project directory:

```bash
claude
```

Invoke Rethlas from the Claude session in natural language:

```text
用 Rethlas 解决 problems/foo.md，参考资料在 problems/foo.refs
```

Claude should infer the Rethlas workflow, use a sibling refs directory when it is unambiguous, and default to 8 verification attempts.

For an explicit entrypoint, use:

```text
/rethlas-solve problems/foo.md --refs problems/foo.refs --max-attempts 8
```

Both paths run inside the current Claude session. They do not start another Claude process and do not require a separate verifier service.

## Runtime Output

Rethlas writes run state to the current project:

```text
.rethlas/runs/<run_id>/
```

Important files:

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

`blueprint_verified.md` is the success marker. It is written only after the verifier returns `correct` with no critical errors and no gaps.

## Development Load

From this repository:

```bash
claude --plugin-dir .
```

Then ask naturally in a test project, for example `用 Rethlas 解决 problems/foo.md`. For plugin validation:

```bash
claude plugin validate . --strict
```

## Dependencies

The MCP servers use Python:

```bash
pip install -r solver/mcp/requirements.txt
pip install -r verifier/mcp/requirements.txt
```

The plugin MCP config invokes `python` from the environment that launches Claude. For development, activate a project-local `.venv` or make sure `python` on `PATH` is the interpreter where these requirements are installed.

## Layout

- `.claude-plugin/plugin.json`: plugin manifest
- `.mcp.json`: solver and verifier MCP server configuration
- `skills/rethlas/SKILL.md`: natural-language Rethlas trigger
- `commands/rethlas-solve.md`: `/rethlas-solve` entrypoint
- `agents/verifier.md`: proof verifier subagent
- `agents/subgoal-prover.md`: decomposition branch helper
- `solver/skills/`: proof-generation skills
- `solver/mcp/`: solver memory and theorem-search MCP tools
- `verifier/skills/`: proof-verification skills
- `verifier/mcp/`: verifier memory and JSON output MCP tools
- `docs/runtime.md`: project-local runtime layout
- `docs/port.md`: porting notes
