# Rethlas Claude Code Port

This port packages upstream `frenzymath/Rethlas` as a Claude Code plugin.

The port intentionally starts from upstream, not from the local modified fork at `C:/Users/Pikel/Code/Rethlas`. Fork-only features such as job control, viewer, LiteLLM presets, event streaming, and long-run control surfaces are out of scope for the first plugin version.

## Main Changes

- The user runs normal `claude` in a project directory and invokes `/rethlas-solve`.
- Runtime artifacts are project-local under `.rethlas/runs/<run_id>/`.
- The verifier is a Claude Code subagent, not a FastAPI service.
- The solver loop runs in the current main session so it can call verifier and subgoal agents.
- Codex configuration and metadata are removed.

## Preserved Behavior

The important upstream behavior remains: generate a proof blueprint, verify it independently, repair from verifier feedback, and repeat until a strict correct verdict or an attempt limit.
