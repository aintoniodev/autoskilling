"""Fixtures compartidos: los tests leen SKILL.md/executor.md desde un directorio
que puede sobrescribirse con DELEGATE_SKILL_DIR (lo usa scripts/mutate.py para
ejecutar la suite contra una copia mutada del skill)."""

import os
import pathlib

import pytest

REPO_DELEGATE = pathlib.Path(__file__).resolve().parent.parent


@pytest.fixture
def skill_root() -> pathlib.Path:
    override = os.environ.get("DELEGATE_SKILL_DIR")
    return pathlib.Path(override) if override else REPO_DELEGATE


@pytest.fixture
def skill_md(skill_root) -> str:
    p = skill_root / "SKILL.md"
    assert p.exists(), f"SKILL.md not found at {p}"
    return p.read_text(encoding="utf-8")


@pytest.fixture
def executor_md(skill_root) -> str:
    p = skill_root / "agents" / "executor.md"
    assert p.exists(), f"agents/executor.md not found at {p}"
    return p.read_text(encoding="utf-8")
