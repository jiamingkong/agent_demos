"""
Integration tests for skill loading.
"""

import os
import tempfile
from pathlib import Path

import pytest

# This is a placeholder for future integration tests
# Will be expanded when we implement actual skill server testing


def test_skill_config_paths():
    """Test that skill configuration paths exist"""
    project_root = Path(__file__).parent.parent.parent
    skill_dirs = [
        "planner",
        "coder",
        "os_manipulation",
        "git",
        "sys_admin",
        "web_fetch",
        "file_compression",
    ]

    for skill in skill_dirs:
        skill_path = project_root / "servers" / skill
        assert skill_path.exists(), f"Skill directory {skill} not found"
        assert (skill_path / "SKILL.md").exists(), f"SKILL.md missing for {skill}"
        assert (skill_path / "server.py").exists(), f"server.py missing for {skill}"

    # If we reach here, all skill directories exist
    assert True


def test_requirements_file():
    """Test that requirements.txt exists and can be read"""
    project_root = Path(__file__).parent.parent.parent
    req_file = project_root / "requirements.txt"
    assert req_file.exists()

    content = req_file.read_text()
    assert "openai" in content
    assert "mcp" in content
    assert "rich" in content
    assert "python-dotenv" in content


if __name__ == "__main__":
    pytest.main([__file__])
