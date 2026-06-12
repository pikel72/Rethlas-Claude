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
