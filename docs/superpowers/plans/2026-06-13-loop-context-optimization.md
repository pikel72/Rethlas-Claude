# Loop Context Optimization Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Reduce token usage and improve loop quality in the Rethlas solver↔verifier workflow by tightening the model-visible context (memory return shapes, skill text, tool docstrings) and adding a `$record-keeping` reference skill — without adding any flow-control logic.

**Architecture:** A new `solver/mcp/envelope.py` module provides pure transformation helpers. Both MCP servers (`solver`, `verifier`) call into it at the response boundary to produce the new `kind`/`data` (read) and `kind`/`written`/`channel_count` (write) shapes. JSONL storage is unchanged. All 14 skills and 10 tool docstrings are rewritten in place. A new `$record-keeping` skill is added to the solver agent only.

**Tech Stack:** Python 3.10+, pytest, FastMCP, jsonschema, no new external dependencies.

**Spec:** `docs/superpowers/specs/2026-06-13-loop-context-optimization-design.md`

---

## File Structure

### New files

| Path | Responsibility |
| --- | --- |
| `solver/mcp/envelope.py` | Pure functions: `transform_item(record, channel)`, `transform_read_items(items, channel)`, `transform_append_result(channel, count)`, `channel_to_kind(channel)`. No I/O. |
| `solver/skills/record-keeping/SKILL.md` | Solver-only reference skill for writing reusable records. |
| `tests/__init__.py` | Empty. |
| `tests/conftest.py` | `pytest` fixtures: `tmp_project_root` (sets `RETHLAS_PROJECT_DIR`, builds `.rethlas/runs/<id>/memory/`), `channel_path` helper. |
| `tests/solver/__init__.py` | Empty. |
| `tests/solver/test_envelope.py` | Unit tests for `envelope.py` functions (pure, no I/O). |
| `tests/solver/test_memory_search_envelope.py` | Integration: `memory_search` returns enveloped items. |
| `tests/solver/test_memory_append_envelope.py` | Integration: `memory_append` returns enveloped result. |
| `tests/verifier/__init__.py` | Empty. |
| `tests/verifier/test_memory_query_envelope.py` | Integration: `memory_query` returns enveloped items. |
| `tests/tools/__init__.py` | Empty. |
| `tests/tools/test_skill_structure.py` | Static check: every skill file has the three required sections and is under 150 tokens. |
| `tests/tools/test_tool_docstrings.py` | Static check: every `@app.tool` docstring has the four required sections and is under 80 tokens. |
| `requirements-dev.txt` | `pytest>=7.0`. |

### Modified files

| Path | Change |
| --- | --- |
| `solver/mcp/server.py` | Import `envelope`; rewrite `memory_search` and `memory_append` returns; rewrite all `@app.tool` docstrings. |
| `verifier/mcp/server.py` | Add `sys.path` insertion; import `envelope`; rewrite `memory_query` return; rewrite all `@app.tool` docstrings. |
| `agents/solver.md` | Add `record-keeping` to the `skills:` frontmatter list. |
| `solver/skills/obtain-immediate-conclusions/SKILL.md` | Rewrite per §4.5. |
| `solver/skills/direct-proving/SKILL.md` | Rewrite per §4.5. |
| `solver/skills/construct-counterexamples/SKILL.md` | Rewrite per §4.5. |
| `solver/skills/construct-toy-examples/SKILL.md` | Rewrite per §4.5. |
| `solver/skills/identify-key-failures/SKILL.md` | Rewrite per §4.5. |
| `solver/skills/propose-subgoal-decomposition-plans/SKILL.md` | Rewrite per §4.5. |
| `solver/skills/query-memory/SKILL.md` | Rewrite per §4.5. |
| `solver/skills/recursive-proving/SKILL.md` | Rewrite per §4.5. |
| `solver/skills/search-math-results/SKILL.md` | Rewrite per §4.5. |
| `solver/skills/verify-proof/SKILL.md` | Rewrite per §4.5. |
| `verifier/skills/check-referenced-statements/SKILL.md` | Rewrite per §4.5. |
| `verifier/skills/synthesize-verification-report/SKILL.md` | Rewrite per §4.5. |
| `verifier/skills/verify-sequential-statements/SKILL.md` | Rewrite per §4.5. |
| `skills/rethlas/SKILL.md` | Rewrite per §4.5. |

**Files NOT changed:**

- `solver/mcp/__init__.py`, `verifier/mcp/__init__.py` — empty, unchanged.
- `solver/mcp/requirements.txt`, `verifier/mcp/requirements.txt` — unchanged.
- `.mcp.json`, `.claude-plugin/plugin.json` — unchanged.
- `agents/verifier.md` — unchanged.
- `agents/subgoal-prover.md` — unchanged.
- JSONL on-disk format — unchanged.

---

## Task 1: Test infrastructure

**Files:**
- Create: `tests/__init__.py`
- Create: `tests/conftest.py`
- Create: `tests/solver/__init__.py`
- Create: `tests/verifier/__init__.py`
- Create: `tests/tools/__init__.py`
- Create: `requirements-dev.txt`
- Create: `pytest.ini`

- [ ] **Step 1: Create empty test package files**

Create each of these files with no content (empty file):

- `tests/__init__.py`
- `tests/solver/__init__.py`
- `tests/verifier/__init__.py`
- `tests/tools/__init__.py`

- [ ] **Step 2: Create `requirements-dev.txt`**

`requirements-dev.txt`:
```
pytest>=7.0
```

- [ ] **Step 3: Create `pytest.ini`**

`pytest.ini`:
```
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -ra
```

- [ ] **Step 4: Create `tests/conftest.py`**

`tests/conftest.py`:
```python
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
```

- [ ] **Step 5: Verify pytest can be collected**

Run:
```bash
cd <plugin-root> && python -m pytest --collect-only -q
```

Expected: `no tests ran` (or similar), no collection errors. Exit code 0.

- [ ] **Step 6: Commit**

```bash
git add tests/__init__.py tests/conftest.py tests/solver/__init__.py tests/verifier/__init__.py tests/tools/__init__.py requirements-dev.txt pytest.ini
git commit -m "test: scaffold pytest infrastructure for envelope and static checks"
```

---

## Task 2: Envelope module — `channel_to_kind`

**Files:**
- Create: `solver/mcp/envelope.py`
- Create: `tests/solver/test_envelope.py`

- [ ] **Step 1: Write the failing test for `channel_to_kind`**

`tests/solver/test_envelope.py`:
```python
from solver.mcp.envelope import channel_to_kind


def test_channel_to_kind_known_channels():
    assert channel_to_kind("immediate_conclusions") == "immediate_conclusion"
    assert channel_to_kind("toy_examples") == "toy_example"
    assert channel_to_kind("counterexamples") == "counterexample"
    assert channel_to_kind("big_decisions") == "decision"
    assert channel_to_kind("subgoals") == "subgoal"
    assert channel_to_kind("proof_steps") == "proof_step"
    assert channel_to_kind("failed_paths") == "failed_path"
    assert channel_to_kind("verification_reports") == "verification_report"
    assert channel_to_kind("branch_states") == "branch_state"
    assert channel_to_kind("statement_checks") == "statement_check"
    assert channel_to_kind("reference_checks") == "reference_check"
    assert channel_to_kind("failed_checks") == "failed_check"
    assert channel_to_kind("events") == "event"


def test_channel_to_kind_unknown_channel_passes_through():
    # Unknown channels should still produce *something* (the model can read it).
    # The exact form is implementation-defined; we just require a non-empty str.
    result = channel_to_kind("future_channel_we_forgot")
    assert isinstance(result, str)
    assert result  # non-empty
```

- [ ] **Step 2: Run the test — expect FAIL (module does not exist yet)**

Run:
```bash
cd <plugin-root> && python -m pytest tests/solver/test_envelope.py::test_channel_to_kind_known_channels -v
```

Expected: `ModuleNotFoundError: No module named 'solver.mcp.envelope'`.

- [ ] **Step 3: Implement `channel_to_kind`**

`solver/mcp/envelope.py`:
```python
"""Pure transformation helpers for the memory envelope.

These functions shape what the *model* sees in tool returns. They never
read or write disk. The MCP server functions import from this module and
apply the transformations at the response boundary.
"""
from __future__ import annotations

from typing import Any, Dict, Iterable, List


_KIND_BY_CHANNEL: Dict[str, str] = {
    "immediate_conclusions": "immediate_conclusion",
    "toy_examples": "toy_example",
    "counterexamples": "counterexample",
    "big_decisions": "decision",
    "subgoals": "subgoal",
    "proof_steps": "proof_step",
    "failed_paths": "failed_path",
    "verification_reports": "verification_report",
    "branch_states": "branch_state",
    "statement_checks": "statement_check",
    "reference_checks": "reference_check",
    "failed_checks": "failed_check",
    "events": "event",
}


def channel_to_kind(channel: str) -> str:
    """Map a storage channel name to the model-facing ``kind`` label.

    Unknown channels are returned in a normalized form so the model can
    still read them.
    """
    if channel in _KIND_BY_CHANNEL:
        return _KIND_BY_CHANNEL[channel]
    # Fallback: strip trailing 's' and underscore-separate. This is best-effort.
    return channel.rstrip("s").replace("_", "_")
```

- [ ] **Step 4: Run the test — expect PASS**

Run:
```bash
cd <plugin-root> && python -m pytest tests/solver/test_envelope.py -v
```

Expected: 2 passed.

- [ ] **Step 5: Commit**

```bash
git add solver/mcp/envelope.py tests/solver/test_envelope.py
git commit -m "feat(envelope): add channel_to_kind helper"
```

---

## Task 3: Envelope module — `transform_item` and `transform_read_items`

**Files:**
- Modify: `solver/mcp/envelope.py`
- Modify: `tests/solver/test_envelope.py`

- [ ] **Step 1: Append failing tests to `tests/solver/test_envelope.py`**

Append to `tests/solver/test_envelope.py`:
```python
from solver.mcp.envelope import transform_item, transform_read_items


def test_transform_item_strips_envelope_and_adds_kind():
    item = {
        "score": 1.23,
        "item": {
            "timestamp_utc": "2026-06-13T08:14:22+00:00",
            "channel": "subgoals",
            "record": {"id": "sg-3", "claim": "x is even"},
        },
    }
    out = transform_item(item, "subgoals")
    assert out == {
        "kind": "subgoal",
        "score": 1.23,
        "data": {"id": "sg-3", "claim": "x is even"},
    }


def test_transform_item_passes_through_unknown_keys():
    item = {"score": 0.5, "extra": "ok", "item": {"channel": "x", "record": {"k": "v"}}}
    out = transform_item(item, "x")
    assert out == {"kind": "x", "score": 0.5, "data": {"k": "v"}}


def test_transform_item_handles_already_flat_input():
    # If the input is already the raw entry (no `item` wrapper), treat the
    # whole input as data. This keeps the function robust to internal callers.
    flat = {"timestamp_utc": "...", "channel": "subgoals", "record": {"k": "v"}}
    out = transform_item(flat, "subgoals")
    assert out == {"kind": "subgoal", "score": None, "data": {"k": "v"}}


def test_transform_read_items_applies_transform_to_each():
    items = [
        {"score": 0.1, "item": {"channel": "counterexamples", "record": {"a": 1}}},
        {"score": 0.2, "item": {"channel": "counterexamples", "record": {"a": 2}}},
    ]
    out = transform_read_items(items, "counterexamples")
    assert out == [
        {"kind": "counterexample", "score": 0.1, "data": {"a": 1}},
        {"kind": "counterexample", "score": 0.2, "data": {"a": 2}},
    ]


def test_transform_read_items_empty():
    assert transform_read_items([], "subgoals") == []
```

- [ ] **Step 2: Run the new tests — expect FAIL**

Run:
```bash
cd <plugin-root> && python -m pytest tests/solver/test_envelope.py -v
```

Expected: the new 5 tests fail with `ImportError` or `AttributeError`.

- [ ] **Step 3: Implement `transform_item` and `transform_read_items`**

Append to `solver/mcp/envelope.py`:
```python
def transform_item(item: Dict[str, Any], channel: str) -> Dict[str, Any]:
    """Return the model-facing envelope for one read item.

    The input is the current shape: ``{"score": float, "item": {"channel", "record", "timestamp_utc"}}``.
    The output is the new shape: ``{"kind": str, "score": float|None, "data": dict}``.

    If the input is already flat (no ``item`` wrapper, no ``score``), it is
    treated as the raw entry; ``score`` is set to ``None`` and the timestamp
    is dropped.
    """
    kind = channel_to_kind(channel)
    if "item" in item and isinstance(item["item"], dict):
        record = item["item"].get("record", {})
        score = item.get("score")
    else:
        record = item.get("record", item)
        score = item.get("score")
    return {"kind": kind, "score": score, "data": record}


def transform_read_items(items: Iterable[Dict[str, Any]], channel: str) -> List[Dict[str, Any]]:
    return [transform_item(item, channel) for item in items]
```

- [ ] **Step 4: Run the tests — expect PASS**

Run:
```bash
cd <plugin-root> && python -m pytest tests/solver/test_envelope.py -v
```

Expected: 7 passed.

- [ ] **Step 5: Commit**

```bash
git add solver/mcp/envelope.py tests/solver/test_envelope.py
git commit -m "feat(envelope): add transform_item and transform_read_items"
```

---

## Task 4: Envelope module — `transform_append_result`

**Files:**
- Modify: `solver/mcp/envelope.py`
- Modify: `tests/solver/test_envelope.py`

- [ ] **Step 1: Append failing tests**

Append to `tests/solver/test_envelope.py`:
```python
from solver.mcp.envelope import transform_append_result


def test_transform_append_result():
    out = transform_append_result("subgoals", 7)
    assert out == {"kind": "subgoal", "written": True, "channel_count": 7}


def test_transform_append_result_zero_count():
    out = transform_append_result("events", 0)
    assert out == {"kind": "event", "written": True, "channel_count": 0}
```

- [ ] **Step 2: Run — expect FAIL**

Run:
```bash
cd <plugin-root> && python -m pytest tests/solver/test_envelope.py -v
```

Expected: 2 new failures with `ImportError`.

- [ ] **Step 3: Implement**

Append to `solver/mcp/envelope.py`:
```python
def transform_append_result(channel: str, channel_count: int) -> Dict[str, Any]:
    """Return the model-facing envelope for a successful append."""
    return {
        "kind": channel_to_kind(channel),
        "written": True,
        "channel_count": int(channel_count),
    }
```

- [ ] **Step 4: Run — expect PASS**

Run:
```bash
cd <plugin-root> && python -m pytest tests/solver/test_envelope.py -v
```

Expected: 9 passed.

- [ ] **Step 5: Commit**

```bash
git add solver/mcp/envelope.py tests/solver/test_envelope.py
git commit -m "feat(envelope): add transform_append_result"
```

---

## Task 5: Wire envelope into solver `memory_search`

**Files:**
- Modify: `solver/mcp/server.py`
- Create: `tests/solver/test_memory_search_envelope.py`

- [ ] **Step 1: Write the failing integration test**

`tests/solver/test_memory_search_envelope.py`:
```python
from solver.mcp import server


def test_memory_search_returns_enveloped_items(tmp_project_root, runs_root):
    # Seed two records on the "subgoals" channel.
    problem_id = "demo_prob"
    server.memory_init(problem_id)
    server.memory_append(problem_id, "subgoals", {"id": "sg-1", "claim": "A"})
    server.memory_append(problem_id, "subgoals", {"id": "sg-2", "claim": "B"})

    out = server.memory_search(problem_id, "claim", channels=["subgoals"], limit_per_channel=10)

    assert out["problem_id"] == "demo_prob"
    assert out["query"] == "claim"
    assert "subgoals" in out["results_by_channel"]
    channel_block = out["results_by_channel"]["subgoals"]
    assert channel_block["count"] == 2
    for item in channel_block["results"]:
        # New shape: no `item` wrapper, no `timestamp_utc`, `channel` -> `kind`.
        assert set(item.keys()) == {"kind", "score", "data"}
        assert item["kind"] == "subgoal"
        assert "timestamp_utc" not in item["data"]
        assert "record" not in item
        assert "item" not in item
```

- [ ] **Step 2: Run — expect FAIL**

Run:
```bash
cd <plugin-root> && python -m pytest tests/solver/test_memory_search_envelope.py -v
```

Expected: the test fails because `memory_search` still returns the old shape (with `item` wrapper containing `timestamp_utc` and `record`).

- [ ] **Step 3: Modify `memory_search` in `solver/mcp/server.py`**

In `solver/mcp/server.py`, locate the function `memory_search` (currently returns `{problem_id, query, channels, limit_per_channel, count, results_by_channel}`).

Replace the loop that builds `ranked_results` so it stores enveloped items. Specifically, change the per-channel loop to call `envelope.transform_item` (which produces the `{kind, score, data}` shape from a `{score, item: raw_entry}` input):

```python
        for item, score in sorted(
            zip(items, scores),
            key=lambda pair: (
                -pair[1],
                pair[0].get("timestamp_utc", ""),
            ),
        ):
            if score <= 0:
                continue
            ranked_results.append(
                envelope.transform_item({"score": score, "item": item}, channel)
            )
            if len(ranked_results) >= limit_per_channel:
                break
```

At the top of the file, add the import (next to the existing `from solver.mcp import ...` / project root setup, or near the FastMCP import area):

```python
from solver.mcp import envelope
```

If the import causes a circular import (the envelope module imports nothing from server, so this should be fine), put the envelope module in a `solver/mcp/_envelope.py` or move both files to use a single shared location. The simplest path: confirm the import works, and if not, fall back to duplicating the small `channel_to_kind` function (no other code in `envelope.py` is used by `memory_search`).

- [ ] **Step 4: Run — expect PASS**

Run:
```bash
cd <plugin-root> && python -m pytest tests/solver/test_memory_search_envelope.py -v
```

Expected: 1 passed.

- [ ] **Step 5: Run the full test suite to ensure no regressions**

Run:
```bash
cd <plugin-root> && python -m pytest -v
```

Expected: all tests pass.

- [ ] **Step 6: Commit**

```bash
git add solver/mcp/server.py tests/solver/test_memory_search_envelope.py
git commit -m "feat(solver): envelope memory_search return shape"
```

---

## Task 6: Wire envelope into solver `memory_append`

**Files:**
- Modify: `solver/mcp/server.py`
- Create: `tests/solver/test_memory_append_envelope.py`

- [ ] **Step 1: Write the failing integration test**

`tests/solver/test_memory_append_envelope.py`:
```python
from solver.mcp import server


def test_memory_append_returns_enveloped_result(tmp_project_root, runs_root):
    problem_id = "demo_prob"
    server.memory_init(problem_id)

    out = server.memory_append(
        problem_id,
        "subgoals",
        {"id": "sg-1", "claim": "A"},
    )

    assert out == {"kind": "subgoal", "written": True, "channel_count": 1}
    # No `path`, no `entry` echo.
    assert "path" not in out
    assert "entry" not in out
    assert "status" not in out


def test_memory_append_counts_grow(tmp_project_root, runs_root):
    problem_id = "demo_prob"
    server.memory_init(problem_id)
    r1 = server.memory_append(problem_id, "subgoals", {"id": "sg-1"})
    r2 = server.memory_append(problem_id, "subgoals", {"id": "sg-2"})
    r3 = server.memory_append(problem_id, "subgoals", {"id": "sg-3"})

    assert r1["channel_count"] == 1
    assert r2["channel_count"] == 2
    assert r3["channel_count"] == 3


def test_memory_append_persists_record_unchanged(tmp_project_root, runs_root):
    problem_id = "demo_prob"
    server.memory_init(problem_id)
    server.memory_append(
        problem_id,
        "subgoals",
        {"id": "sg-1", "claim": "x is even", "dependencies": []},
    )

    # Read the raw JSONL on disk to confirm storage is unchanged.
    jsonl = (runs_root / "demo_prob" / "memory" / "subgoals.jsonl").read_text(
        encoding="utf-8"
    )
    assert '"timestamp_utc"' in jsonl  # on-disk format preserved
    assert '"record"' in jsonl
    assert '"x is even"' in jsonl
```

- [ ] **Step 2: Run — expect FAIL**

Run:
```bash
cd <plugin-root> && python -m pytest tests/solver/test_memory_append_envelope.py -v
```

Expected: all 3 fail because `memory_append` returns the old `{status, channel, path, entry}` shape.

- [ ] **Step 3: Modify `memory_append` in `solver/mcp/server.py`**

In `solver/mcp/server.py`, locate `memory_append`. Replace its tail (everything after `_append_jsonl(_channel_path(problem_id, "events"), event_entry)` — i.e., the auto-event side-effect — keep that) so the function returns the enveloped result.

The new return logic:

```python
    target = _channel_path(problem_id, channel)
    _append_jsonl(target, entry)

    if channel != "events":
        event_entry = {
            "timestamp_utc": _utc_now(),
            "event_type": "memory_append",
            "channel": channel,
        }
        _append_jsonl(_channel_path(problem_id, "events"), event_entry)

    # Compute the new channel_count by reading the file we just appended to.
    count = sum(1 for _ in _iter_jsonl(target))

    return envelope.transform_append_result(channel, count)
```

Note: the `entry` and `event_entry` are still constructed and written to disk exactly as before. Only the *return value* changes.

- [ ] **Step 4: Run — expect PASS**

Run:
```bash
cd <plugin-root> && python -m pytest tests/solver/test_memory_append_envelope.py -v
```

Expected: 3 passed.

- [ ] **Step 5: Run the full test suite**

Run:
```bash
cd <plugin-root> && python -m pytest -v
```

Expected: all pass.

- [ ] **Step 6: Commit**

```bash
git add solver/mcp/server.py tests/solver/test_memory_append_envelope.py
git commit -m "feat(solver): envelope memory_append return shape"
```

---

## Task 7: Verifier `sys.path` and import

**Files:**
- Modify: `verifier/mcp/server.py`

- [ ] **Step 1: Add `sys.path` insertion at the top of `verifier/mcp/server.py`**

At the very top of `verifier/mcp/server.py`, after the `from __future__ import annotations` line, add:

```python
from __future__ import annotations

import os
import sys
from pathlib import Path

# Ensure the plugin root is on sys.path so we can import from solver.mcp.
# (Both MCP servers run as `python <path>/server.py` which only puts the
# script's own directory on sys.path.)
_PLUGIN_ROOT = Path(__file__).resolve().parents[2]
if str(_PLUGIN_ROOT) not in sys.path:
    sys.path.insert(0, str(_PLUGIN_ROOT))
```

Then, after the existing imports, add:

```python
from solver.mcp import envelope
```

(If this import fails at runtime, fall back to duplicating `envelope.py` under `verifier/mcp/` and importing from the local copy. See the spec §5.2 decision.)

- [ ] **Step 2: Verify both MCP servers can import each other's modules in a smoke check**

Run:
```bash
cd <plugin-root> && python -c "from solver.mcp import envelope; from solver.mcp.envelope import channel_to_kind; print(channel_to_kind('subgoals'))"
```

Expected: `subgoal` (printed). Exit code 0.

Run:
```bash
cd <plugin-root> && python -c "from verifier.mcp import server; print(server.envelope.channel_to_kind('statement_checks'))"
```

Expected: `statement_check` (printed). Exit code 0.

- [ ] **Step 3: Commit**

```bash
git add verifier/mcp/server.py
git commit -m "feat(verifier): add sys.path fix and import shared envelope module"
```

---

## Task 8: Wire envelope into verifier `memory_query`

**Files:**
- Modify: `verifier/mcp/server.py`
- Create: `tests/verifier/test_memory_query_envelope.py`

- [ ] **Step 1: Write the failing integration test**

`tests/verifier/test_memory_query_envelope.py`:
```python
from verifier.mcp import server


def test_memory_query_returns_enveloped_items(tmp_project_root, runs_root):
    run_id = "demo_run"
    server.memory_init(run_id)
    server.memory_append(run_id, "statement_checks", {"location": "Lemma 1", "ok": True})
    server.memory_append(run_id, "statement_checks", {"location": "Lemma 2", "ok": False})

    out = server.memory_query(run_id, "statement_checks", limit=10)

    assert out["run_id"] == "demo_run"
    assert out["channel"] == "statement_checks"
    assert out["count"] == 2
    for item in out["items"]:
        # New shape: kind + data, no `timestamp_utc` / `channel` / `record` wrapping.
        assert set(item.keys()) == {"kind", "data"}
        assert item["kind"] == "statement_check"
        assert "timestamp_utc" not in item["data"]
        assert "record" not in item
        assert "channel" not in item
```

- [ ] **Step 2: Run — expect FAIL**

Run:
```bash
cd <plugin-root> && python -m pytest tests/verifier/test_memory_query_envelope.py -v
```

Expected: fail with the old shape keys present.

- [ ] **Step 3: Modify `memory_query` in `verifier/mcp/server.py`**

Locate the `memory_query` function. Just before `return { ... }`, transform the items list. Replace the final return block:

```python
    items = items[:limit]
    enveloped = [
        {"kind": envelope.channel_to_kind(channel), "data": item.get("record", item)}
        for item in items
    ]
    return {
        "run_id": resolved_run_id,
        "channel": channel,
        "count": len(enveloped),
        "items": enveloped,
    }
```

- [ ] **Step 4: Run — expect PASS**

Run:
```bash
cd <plugin-root> && python -m pytest tests/verifier/test_memory_query_envelope.py -v
```

Expected: 1 passed.

- [ ] **Step 5: Run full suite**

Run:
```bash
cd <plugin-root> && python -m pytest -v
```

Expected: all pass.

- [ ] **Step 6: Commit**

```bash
git add verifier/mcp/server.py tests/verifier/test_memory_query_envelope.py
git commit -m "feat(verifier): envelope memory_query return shape"
```

---

## Task 9: Static check infrastructure for skills and tool docstrings

**Files:**
- Create: `tests/tools/test_skill_structure.py`
- Create: `tests/tools/test_tool_docstrings.py`

- [ ] **Step 1: Write the skill structure check**

`tests/tools/test_skill_structure.py`:
```python
"""Static check: every SKILL.md has the three required sections and stays under 150 tokens."""
from __future__ import annotations

from pathlib import Path
from typing import List

import pytest

PLUGIN_ROOT = Path(__file__).resolve().parents[2]
REQUIRED_SECTIONS = ["## When to use", "## Output", "## Steps"]
TOKEN_BUDGET = 150


def _all_skill_files() -> List[Path]:
    roots = [
        PLUGIN_ROOT / "solver" / "skills",
        PLUGIN_ROOT / "verifier" / "skills",
        PLUGIN_ROOT / "skills",
    ]
    found: List[Path] = []
    for root in roots:
        if not root.exists():
            continue
        for path in sorted(root.rglob("SKILL.md")):
            found.append(path)
    return found


def _approx_token_count(text: str) -> int:
    # Rough: 1 token ~ 4 chars for English-ish text. Good enough as a budget check.
    return max(1, len(text) // 4)


@pytest.mark.parametrize("skill_path", _all_skill_files(), ids=lambda p: str(p.relative_to(PLUGIN_ROOT)))
def test_skill_has_required_sections(skill_path: Path):
    text = skill_path.read_text(encoding="utf-8")
    for section in REQUIRED_SECTIONS:
        assert section in text, f"{skill_path.name} missing section: {section}"


@pytest.mark.parametrize("skill_path", _all_skill_files(), ids=lambda p: str(p.relative_to(PLUGIN_ROOT)))
def test_skill_under_token_budget(skill_path: Path):
    text = skill_path.read_text(encoding="utf-8")
    tokens = _approx_token_count(text)
    assert tokens <= TOKEN_BUDGET, (
        f"{skill_path.name} is ~{tokens} tokens; budget is {TOKEN_BUDGET}"
    )
```

- [ ] **Step 2: Write the tool docstring check**

`tests/tools/test_tool_docstrings.py`:
```python
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
        pytest.skip(f"{module_name}: FastMCP not installed; skipping docstring check")
    tools = app._tool_manager._tools if hasattr(app, "_tool_manager") else {}
    if not tools:
        pytest.skip(f"{module_name}: no tools registered on app")
    for name, tool in tools.items():
        doc = (tool.description or "").strip()
        # FastMCP uses `description` for the docstring; fall back to fn __doc__.
        if not doc:
            fn = getattr(tool, "fn", None) or getattr(tool, "function", None)
            doc = (inspect.getdoc(fn) or "") if fn else ""
        assert doc, f"{module_name}.{name}: no docstring"
        for section in REQUIRED_SECTIONS:
            assert section in doc, (
                f"{module_name}.{name}: missing section '{section}' in docstring"
            )


@pytest.mark.parametrize("module_name", _server_modules())
def test_tool_docstrings_under_token_budget(module_name: str):
    import importlib
    mod = importlib.import_module(module_name)
    app = mod.APP
    if app is None:
        pytest.skip(f"{module_name}: FastMCP not installed")
    tools = app._tool_manager._tools if hasattr(app, "_tool_manager") else {}
    if not tools:
        pytest.skip(f"{module_name}: no tools registered on app")
    for name, tool in tools.items():
        doc = (tool.description or "").strip()
        if not doc:
            fn = getattr(tool, "fn", None) or getattr(tool, "function", None)
            doc = (inspect.getdoc(fn) or "") if fn else ""
        tokens = _approx_token_count(doc)
        assert tokens <= TOKEN_BUDGET, (
            f"{module_name}.{name}: ~{tokens} tokens, budget {TOKEN_BUDGET}"
        )
```

Note: the exact attribute path for accessing FastMCP's tool list (`app._tool_manager._tools`) may differ across versions. If the test fails with `AttributeError`, replace the introspection with iterating `app._tool_manager.list_tools()` (returns tool objects) and read `.description` from those. If that also fails, fall back to introspecting the module's `@app.tool` decorated functions via the decorator's wrapping. The goal of the test is to assert the docstring content; the exact FastMCP API can be substituted.

- [ ] **Step 3: Run — expect FAIL (skills don't yet have the new structure)**

Run:
```bash
cd <plugin-root> && python -m pytest tests/tools/ -v
```

Expected: many failures (skills don't have `## When to use` / `## Output` / `## Steps` yet; tool docstrings don't have `When to call:` etc. yet). This is expected — these tests are the acceptance criteria for the rewrite tasks that follow.

- [ ] **Step 4: Commit the failing test scaffold**

```bash
git add tests/tools/test_skill_structure.py tests/tools/test_tool_docstrings.py
git commit -m "test: add static checks for skill and tool-docstring structure"
```

---

## Task 10: Solver tool docstring rewrites

**Files:**
- Modify: `solver/mcp/server.py` (every `@app.tool` function)

- [ ] **Step 1: For each of the 5 solver tools, rewrite the function's docstring** to use the template:

```
When to call: <one sentence>
Args: <param list, with types>
Returns: <return shape>
Notes: <warnings, edge cases>
```

The 5 tools in `solver/mcp/server.py` are:

- `search_arxiv_theorems`
- `memory_init`
- `memory_append`
- `memory_search`
- `branch_update`

For `memory_append`, the Notes section must mention the `$record-keeping` skill by name (for cross-reference; that skill is added in Task 11).

For `memory_search` vs `memory_query` distinction (verifier tool), use Notes to point out the difference when both are relevant to the model.

Each docstring must keep its body under ~80 tokens. The static check in Task 9 verifies this.

- [ ] **Step 2: Run the tool docstring tests — expect PASS**

Run:
```bash
cd <plugin-root> && python -m pytest tests/tools/test_tool_docstrings.py -v
```

Expected: all pass for the solver module.

- [ ] **Step 3: Commit**

```bash
git add solver/mcp/server.py
git commit -m "refactor(solver): rewrite @app.tool docstrings to four-section template"
```

---

## Task 11: Verifier tool docstring rewrites

**Files:**
- Modify: `verifier/mcp/server.py` (every `@app.tool` function)

- [ ] **Step 1: For each of the 6 verifier tools, rewrite the docstring** to the four-section template:

- `search_arxiv_theorems`
- `memory_init`
- `memory_append`
- `memory_query`
- `validate_verification_output`
- `write_verification_output`

For `memory_query`, the Notes section must explicitly distinguish it from `memory_search` in the solver MCP (precise filter / substring vs fuzzy BM25).

Each docstring must keep its body under ~80 tokens.

- [ ] **Step 2: Run the tool docstring tests — expect PASS**

Run:
```bash
cd <plugin-root> && python -m pytest tests/tools/test_tool_docstrings.py -v
```

Expected: all pass for both modules.

- [ ] **Step 3: Commit**

```bash
git add verifier/mcp/server.py
git commit -m "refactor(verifier): rewrite @app.tool docstrings to four-section template"
```

---

## Task 12: Create `$record-keeping` skill

**Files:**
- Create: `solver/skills/record-keeping/SKILL.md`

- [ ] **Step 1: Draft the skill body**

`solver/skills/record-keeping/SKILL.md`:
```markdown
---
name: record-keeping
description: Guide for writing solver memory records that maximize reuse in subsequent loop iterations. Use before calling `memory_append`, especially on the first attempt of a problem or whenever a previous attempt's records were not useful.
---

# Record Keeping

Write records that the *next loop iteration* can use directly. The model decides whether to follow this guidance.

## When to use

Before any `memory_append` call where the record will be read by a future attempt.

## Output

A record shape that another iteration can pattern-match against without re-deriving the context.

## Steps

1. State the *claim* or *event* in one short sentence.
2. Capture the *minimum fields* the next iteration needs: a stable `id` if it's a subgoal / counterexample, a one-line `why_*` for failures, the witness for a counterexample, the source for an immediate conclusion.
3. Prefer concrete nouns over abstract prose. Avoid embedding full proof paragraphs into a record — the proof lives in `blueprint.md`; the record is a pointer.
4. If the record is a failure, write enough that the next iteration can *avoid* the path, not just note that it failed.

## Quick reference

- `subgoal`: `id`, `claim`, `dependencies`, optional `status`
- `failed_path`: `what_tried`, `why_failed`
- `counterexample`: `statement`, `witness`
- `proof_step`: `step`, `justification`
- `immediate_conclusion`: `claim`, `source`
- `toy_example`: `example`, `where_assumptions_take_effect`

## Notes

This skill is a reference. There is no validation that records match this shape; the model decides.
```

- [ ] **Step 2: Verify the static check accepts it**

Run:
```bash
cd <plugin-root> && python -m pytest "tests/tools/test_skill_structure.py" -v -k record-keeping
```

Expected: 2 passed (sections + token budget).

- [ ] **Step 3: Commit**

```bash
git add solver/skills/record-keeping/SKILL.md
git commit -m "feat(skills): add record-keeping reference skill"
```

---

## Task 13: Register `$record-keeping` in solver agent

**Files:**
- Modify: `agents/solver.md`

- [ ] **Step 1: Add `record-keeping` to the `skills:` list**

Open `agents/solver.md`. The `skills:` list currently contains:

```
skills:
  - construct-counterexamples
  - construct-toy-examples
  - direct-proving
  - identify-key-failures
  - obtain-immediate-conclusions
  - propose-subgoal-decomposition-plans
  - query-memory
  - recursive-proving
  - search-math-results
  - verify-proof
```

Add `- record-keeping` (alphabetical position, between `query-memory` and `recursive-proving`):

```
skills:
  - construct-counterexamples
  - construct-toy-examples
  - direct-proving
  - identify-key-failures
  - obtain-immediate-conclusions
  - propose-subgoal-decomposition-plans
  - query-memory
  - record-keeping
  - recursive-proving
  - search-math-results
  - verify-proof
```

- [ ] **Step 2: Verify the file parses as YAML (frontmatter is valid)**

Run:
```bash
cd <plugin-root> && python -c "import yaml; print(yaml.safe_load(open('agents/solver.md').read().split('---')[1]))"
```

Expected: a dict including `"skills": [...]` with `record-keeping` in the list.

- [ ] **Step 3: Commit**

```bash
git add agents/solver.md
git commit -m "feat(agent): register record-keeping skill in solver agent"
```

---

## Tasks 14-23: Rewrite solver skills (one task per skill)

**Universal recipe for each skill task below** (Tasks 14-23):

1. Read the current `SKILL.md` (the full current content is captured in §A below for reference; re-read at execution time to confirm).
2. Draft a new version that has exactly three sections (`## When to use`, `## Output`, `## Steps`) and stays under ~150 tokens.
3. Apply the rewrite rules from spec §4.5: delete restatements of the agent prompt, drop multi-line examples, remove meta-prose, collapse cross-skill duplication.
4. Write the new file.
5. Run the skill structure test:
   ```bash
   cd <plugin-root> && python -m pytest "tests/tools/test_skill_structure.py" -v -k <skill-name>
   ```
   Expected: 2 passed.
6. Commit:
   ```bash
   git add solver/skills/<skill-name>/SKILL.md
   git commit -m "refactor(skills): tighten <skill-name> per spec §4.5"
   ```

**Per-skill guidance** (in addition to the universal recipe):

- **Task 14 — `obtain-immediate-conclusions`**: collapse the "Input Contract" / "Procedure" / "Output Contract" / "MCP Tools" / "Failure Logging" sections into the three required sections. Move the per-channel `immediate_conclusions` record example into a one-line "record shape" hint inside `## Output` (or drop it — `$record-keeping` covers this).

- **Task 15 — `direct-proving`**: this is the longest skill. The 12-step procedure is mostly concrete and load-bearing; keep the structure but compress. Reference `$obtain-immediate-conclusions` rather than re-stating its premise. Drop the elaborate output JSON example to a one-liner.

- **Task 16 — `construct-counterexamples`**: collapse the procedure. Reference `$construct-toy-examples` for the toy-example shape. Output section should say "append to `counterexamples`; if status=`refuted` and kills a branch, also append to `failed_paths`."

- **Task 17 — `construct-toy-examples`**: collapse the procedure. Reference `$construct-counterexamples` for the relationship between the two skills.

- **Task 18 — `identify-key-failures`**: this is already relatively short. Compress procedurally; keep the "what gets saved to `failed_paths`" reference.

- **Task 19 — `propose-subgoal-decomposition-plans`**: compress the "what each plan states" bullet list. Output should say "append one record per plan to `subgoals`; hand to `$direct-proving`."

- **Task 20 — `query-memory`**: compress. Remove the elaborate `events` record example.

- **Task 21 — `recursive-proving`**: reference `$direct-proving` and `$identify-key-failures` rather than re-stating their protocols. Keep the per-subgoal-prover handoff list compact.

- **Task 22 — `search-math-results`**: this is also long. The 16-step procedure can be compressed into ~5-6 high-level steps. Keep the "Usefulness Test" as a sub-bullet under `## Steps`.

- **Task 23 — `verify-proof`**: reference the verifier MCP tool by name. Drop the elaborate "treat as failed if" enumeration into a one-liner. The verdict rules belong to the verifier, not the skill.

---

## Tasks 24-26: Rewrite verifier skills (one task per skill)

**Universal recipe** (same as for solver skills):

1. Read current `SKILL.md`.
2. Draft new version with the three required sections, ≤150 tokens.
3. Apply the rewrite rules.
4. Write the file.
5. Run the static check:
   ```bash
   cd <plugin-root> && python -m pytest "tests/tools/test_skill_structure.py" -v -k <skill-name>
   ```
6. Commit:
   ```bash
   git add verifier/skills/<skill-name>/SKILL.md
   git commit -m "refactor(skills): tighten <skill-name> per spec §4.5"
   ```

**Per-skill guidance**:

- **Task 24 — `check-referenced-statements`**: compress the 14-step procedure. The "no utility code" note can be a single line in `## Notes`. Keep the critical-error / gap classification.

- **Task 25 — `synthesize-verification-report`**: this is already tight. Compress `## Procedure` into the verdict rule. Drop the elaborate "Final output JSON" block (it duplicates the schema).

- **Task 26 — `verify-sequential-statements`**: compress the 9-step procedure. Keep the critical-error / gap classification compact.

---

## Task 27: Rewrite `rethlas` entry skill

**Files:**
- Modify: `skills/rethlas/SKILL.md`

- [ ] **Step 1: Read the current file and draft a new version**

The current file is ~50 lines and already follows a similar structure. Apply the same three-section rule (When to use / Output / Steps) — the current file does not have those exact headers, so this is a structural edit, not a length edit.

Draft should:
- Keep the natural-language entry intent.
- Keep the input-inference logic (problem file, refs dir, max_attempts).
- Reference `/rethlas-solve` for the workflow steps rather than duplicating the 8-step list.

Target: under ~150 tokens.

- [ ] **Step 2: Run the skill structure test**

Run:
```bash
cd <plugin-root> && python -m pytest "tests/tools/test_skill_structure.py" -v -k rethlas
```

Expected: 2 passed.

- [ ] **Step 3: Commit**

```bash
git add skills/rethlas/SKILL.md
git commit -m "refactor(skills): tighten rethlas entry skill per spec §4.5"
```

---

## Task 28: End-to-end smoke test on `example1.md`

**Files:**
- None (verification only)

- [ ] **Step 1: Confirm the plugin files are in place**

Run:
```bash
cd <plugin-root> && ls solver/mcp/envelope.py verifier/mcp/server.py solver/skills/record-keeping/SKILL.md
```

Expected: all three paths exist.

- [ ] **Step 2: Run the full test suite**

Run:
```bash
cd <plugin-root> && python -m pytest -v
```

Expected: all tests pass (envelope unit tests, memory_*_envelope integration tests, skill structure tests, tool docstring tests).

- [ ] **Step 3: Run a manual smoke test of the MCP servers**

In a fresh shell, with the project root set, start the solver MCP and confirm it responds to a tool call:

```bash
cd <plugin-root> && \
  RETHLAS_PROJECT_DIR=$(mktemp -d) \
  python -c "
from solver.mcp import server
result = server.memory_append('smoke', 'subgoals', {'id': 'sg-1', 'claim': 'x'})
print(result)
"
```

Expected output: `{'kind': 'subgoal', 'written': True, 'channel_count': 1}`

```bash
cd <plugin-root> && \
  RETHLAS_PROJECT_DIR=$(mktemp -d) \
  python -c "
from solver.mcp import server
server.memory_init('smoke')
server.memory_append('smoke', 'subgoals', {'id': 'sg-1', 'claim': 'x is even'})
result = server.memory_search('smoke', 'even', channels=['subgoals'])
print(result['results_by_channel'])
"
```

Expected output: a dict with `subgoals` key, whose `results` list contains one item shaped as `{'kind': 'subgoal', 'score': ..., 'data': {'id': 'sg-1', 'claim': 'x is even'}}` (no `item`, no `timestamp_utc`).

- [ ] **Step 4: (Optional, time-permitting) run `/rethlas-solve` on `example1.md`**

This is the deepest verification. It requires the Claude Code plugin runtime and a working LLM API. If the runtime is available:

```bash
cd <plugin-root>/..  # the parent of the plugin checkout, so .claude-plugin is resolvable
mkdir -p /tmp/rethlas-smoke
cp solver/data/example/example1.md /tmp/rethlas-smoke/problem.md
cd /tmp/rethlas-smoke
claude  # then in the session: /rethlas-solve problem.md
```

Confirm `.rethlas/runs/<run_id>/blueprint_verified.md` is produced. If it is not, the rewrite has regressed something — identify which skill or tool change and revert that task.

If the runtime is not available, skip this step and document it as deferred.

- [ ] **Step 5: Final commit if any cleanup was needed**

If step 3 surfaced no regressions and step 4 was not run, no commit is needed. If regressions were caught and fixed, commit them with:

```bash
git add -A
git commit -m "fix: address smoke-test regressions from context optimization"
```

---

## Task 29: Wrap up — verify spec coverage

- [ ] **Step 1: Walk through each spec requirement and confirm a task covers it**

| Spec section | Task(s) |
| --- | --- |
| §4.1 read envelope shape | Tasks 2, 3, 5, 8 |
| §4.2 write envelope shape | Tasks 2, 4, 6 |
| §4.3 channel → kind mapping | Task 2 |
| §4.4 `$record-keeping` skill | Tasks 12, 13 |
| §4.5 skill rewrite rules (10 solver + 3 verifier + rethlas) | Tasks 14-27 |
| §4.6 tool description template | Tasks 10, 11, 9 (static check) |
| §5.1 file changes | Tasks 5, 6, 7, 8, 10, 11, 12, 13, 14-27 |
| §5.2 sys.path fix | Task 7 |
| §5.3 backward compat (storage unchanged) | Task 6, Step 3 (asserts on-disk JSONL unchanged) |
| §6.1 static checks | Task 9 |
| §6.2 behavioral checks (token, smoke, read-back) | Task 28 |
| §6.3 quality check (attempt count) | Task 28, Step 4 (optional) |

- [ ] **Step 2: Commit the final state**

```bash
git status
# If clean, no commit needed. If there are uncommitted doc/notes, commit them.
git log --oneline -20
```

Expected: a clean working tree and a coherent commit history walking through the spec.
