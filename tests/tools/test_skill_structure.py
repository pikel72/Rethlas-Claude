"""Static checks for skill SKILL.md files per spec §4.5."""

from pathlib import Path

import pytest


SKILL_DIRS = [
    "solver/skills",
    "verifier/skills",
    "skills",
]


def collect_skill_files() -> list[Path]:
    """Find all SKILL.md files under the skill directories."""
    project_root = Path(__file__).resolve().parents[2]
    files: list[Path] = []
    for d in SKILL_DIRS:
        sd = project_root / d
        if sd.is_dir():
            files.extend(sorted(sd.rglob("SKILL.md")))
    return files


def _extract_body(content: str) -> str:
    """Strip YAML frontmatter, returning body text."""
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            return parts[2]
    return content


def _token_count(text: str) -> int:
    """Rough token count: split on whitespace."""
    return len(text.split())


class TestSkillStructure:
    """Verify all SKILL.md files conform to spec §4.5."""

    TOKEN_BUDGET = 250

    @pytest.mark.parametrize("skill_path", collect_skill_files(), ids=lambda p: p.parent.name)
    def test_three_required_sections(self, skill_path: Path):
        """Must have ## When to use, ## Output, ## Steps in order."""
        content = skill_path.read_text(encoding="utf-8")
        body = _extract_body(content)

        assert "## When to use" in body, f"Missing '## When to use' in {skill_path}"
        assert "## Output" in body, f"Missing '## Output' in {skill_path}"
        assert "## Steps" in body, f"Missing '## Steps' in {skill_path}"

        pos_when = body.index("## When to use")
        pos_output = body.index("## Output")
        pos_steps = body.index("## Steps")
        assert pos_when < pos_output < pos_steps, (
            f"Sections out of order in {skill_path}"
        )

    @pytest.mark.parametrize("skill_path", collect_skill_files(), ids=lambda p: p.parent.name)
    def test_token_budget(self, skill_path: Path):
        """Body (excluding frontmatter) must stay under token budget."""
        content = skill_path.read_text(encoding="utf-8")
        body = _extract_body(content)
        tokens = _token_count(body)
        assert tokens <= self.TOKEN_BUDGET, (
            f"{skill_path}: {tokens} tokens exceeds budget of {self.TOKEN_BUDGET}"
        )
