"""Shared pytest fixtures for the Rethlas plugin tests."""
from __future__ import annotations

import os
from pathlib import Path
from typing import Iterator

import pytest


@pytest.fixture
def tmp_project_root(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Iterator[Path]:
    """Create a fresh project root with `.rethlas/runs/` and point the
    MCP servers at it via `RETHLAS_PROJECT_DIR`.

    Yields the project root. The runs directory is created lazily by the
    memory functions on first call.
    """
    project_root = tmp_path / "project"
    project_root.mkdir()
    monkeypatch.setenv("RETHLAS_PROJECT_DIR", str(project_root))
    monkeypatch.delenv("CLAUDE_PROJECT_DIR", raising=False)
    yield project_root


@pytest.fixture
def runs_root(tmp_project_root: Path) -> Path:
    return tmp_project_root / ".rethlas" / "runs"