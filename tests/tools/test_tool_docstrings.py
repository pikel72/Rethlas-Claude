"""Static check: every @app.tool docstring has the four required sections
and stays under 80 tokens. Also smoke-checks that the MCP app builds."""
from __future__ import annotations

import inspect
from pathlib import Path
from typing import List

import pytest

PLUGIN_ROOT = Path(__file__).resolve().parents[2]
REQUIRED_SECTIONS = ["When to call:", "Args:", "Returns:", "Notes:"]
TOKEN_BUDGET = 80


def _server_modules() -> List[str]:
    return ["solver.mcp.server", "verifier.mcp.server"]


def _approx_token_count(text: str) -> int:
    return max(1, len(text) // 4)


@pytest.mark.parametrize("module_name", _server_modules())
def test_tool_docstrings_have_required_sections(module_name: str):
    import importlib
    mod = importlib.import_module(module_name)
    app = mod.APP
    if app is None:
        pytest.skip(f"{module_name}: FastMCP not installed")
    tools = app._tool_manager._tools if hasattr(app, "_tool_manager") else {}
    if not tools:
        pytest.skip(f"{module_name}: no tools registered")
    for name, tool in tools.items():
        doc = (tool.description or "").strip()
        if not doc:
            fn = getattr(tool, "fn", None) or getattr(tool, "function", None)
            doc = (inspect.getdoc(fn) or "") if fn else ""
        assert doc, f"{module_name}.{name}: no docstring"
        for section in REQUIRED_SECTIONS:
            assert section in doc, f"{module_name}.{name}: missing '{section}'"


@pytest.mark.parametrize("module_name", _server_modules())
def test_tool_docstrings_under_token_budget(module_name: str):
    import importlib
    mod = importlib.import_module(module_name)
    app = mod.APP
    if app is None:
        pytest.skip(f"{module_name}: FastMCP not installed")
    tools = app._tool_manager._tools if hasattr(app, "_tool_manager") else {}
    if not tools:
        pytest.skip(f"{module_name}: no tools registered")
    for name, tool in tools.items():
        doc = (tool.description or "").strip()
        if not doc:
            fn = getattr(tool, "fn", None) or getattr(tool, "function", None)
            doc = (inspect.getdoc(fn) or "") if fn else ""
        tokens = _approx_token_count(doc)
        assert tokens <= TOKEN_BUDGET, f"{module_name}.{name}: ~{tokens} tokens, budget {TOKEN_BUDGET}"
