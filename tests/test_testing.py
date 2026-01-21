"""Unit tests for testing server."""

import os
import sys
from pathlib import Path
from unittest.mock import Mock, patch

# Add servers to path
sys.path.insert(0, str(Path(__file__).parent.parent / "servers"))

from testing.server import get_test_coverage, list_test_files, run_pytest, run_test_file


def test_run_pytest():
    """Test running pytest (mocked)."""
    with patch("testing.server.subprocess.run") as mock_run:
        mock_run.return_value.stdout = "pytest output"
        mock_run.return_value.stderr = ""
        mock_run.return_value.returncode = 0
        result = run_pytest("-v")
        # Should contain output
        assert "pytest output" in result


def test_list_test_files():
    """Test listing test files (real)."""
    result = list_test_files()
    # Should list at least some known test files
    assert "test_agent.py" in result
    assert "test_" in result  # generic check


def test_run_test_file():
    """Test running a specific test file (mocked)."""
    with patch("testing.server.subprocess.run") as mock_run, patch(
        "testing.server.os.path.exists", return_value=True
    ), patch("testing.server.os.stat") as mock_stat:
        # Mock stat to return a regular file
        import stat

        mock_stat.return_value.st_mode = stat.S_IFREG
        mock_run.return_value.stdout = "test passes"
        mock_run.return_value.stderr = ""
        mock_run.return_value.returncode = 0
        result = run_test_file("tests/test_example.py")
        assert "test passes" in result


def test_get_test_coverage():
    """Test generating coverage report (mocked)."""
    with patch("testing.server.subprocess.run") as mock_run:
        mock_run.return_value.stdout = "Coverage report"
        mock_run.return_value.stderr = ""
        mock_run.return_value.returncode = 0
        result = get_test_coverage(".")
        assert "Coverage report" in result
