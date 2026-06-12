"""Shared pytest fixtures for the Rethlas plugin tests."""
from __future__ import annotations

import os
import shutil
import tempfile
from pathlib import Path
from typing import Iterator

import pytest

# Module-level: set RETHLAS_PROJECT_DIR before any test module imports server.py.
# (Test files do ``from solver.mcp import server`` at collection time, and
# server.py computes RUNS_ROOT at import time — we must set the env var first.)
_TMP_DIR = tempfile.mkdtemp(prefix="rethlas_test_")
os.environ["RETHLAS_PROJECT_DIR"] = str(_TMP_DIR)
os.environ.pop("CLAUDE_PROJECT_DIR", None)


def _cleanup() -> None:
    shutil.rmtree(_TMP_DIR, ignore_errors=True)
    os.environ.pop("RETHLAS_PROJECT_DIR", None)


import atexit
atexit.register(_cleanup)


@pytest.fixture
def tmp_project_root() -> Iterator[Path]:
    yield Path(_TMP_DIR)


@pytest.fixture
def runs_root(tmp_project_root: Path) -> Path:
    return tmp_project_root / ".rethlas" / "runs"
