"""Unit tests for os_manipulation server."""

import os
import shutil
import sys
import tempfile
from pathlib import Path

# Add servers to path
sys.path.insert(0, str(Path(__file__).parent.parent / "servers"))

from os_manipulation.server import (
    create_directories,
    list_directory,
    move_files,
    move_files_by_regex,
)


def test_list_directory():
    """Test listing directory contents."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create some files
        (Path(tmpdir) / "file1.txt").write_text("hello")
        (Path(tmpdir) / "file2.txt").write_text("world")
        os.makedirs(Path(tmpdir) / "subdir")

        result = list_directory(tmpdir)
        # Should list both files and subdirectory
        assert "file1.txt" in result
        assert "file2.txt" in result
        assert "subdir" in result


def test_create_directories():
    """Test creating multiple directories."""
    with tempfile.TemporaryDirectory() as tmpdir:
        dirs = [
            os.path.join(tmpdir, "dir1"),
            os.path.join(tmpdir, "dir2", "nested"),
        ]
        result = create_directories(dirs)
        assert "created" in result.lower()
        # Verify directories exist
        for d in dirs:
            assert os.path.exists(d)
            assert os.path.isdir(d)


def test_move_files():
    """Test moving files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        src = Path(tmpdir) / "source.txt"
        src.write_text("content")
        dest_dir = Path(tmpdir) / "dest"
        dest_dir.mkdir()

        result = move_files([str(src)], str(dest_dir))
        assert "moved" in result.lower() or "success" in result.lower()
        assert (dest_dir / "source.txt").exists()
        assert not src.exists()


def test_move_files_by_regex():
    """Test moving files by regex pattern."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create files matching pattern
        (Path(tmpdir) / "test_001.txt").write_text("1")
        (Path(tmpdir) / "test_002.txt").write_text("2")
        (Path(tmpdir) / "other.txt").write_text("3")

        dest_dir = Path(tmpdir) / "backup"
        result = move_files_by_regex(
            source_dir=str(tmpdir), destination=str(dest_dir), pattern=r"test_\d+.txt"
        )
        assert "moved" in result.lower()
        # Verify moved files
        assert (dest_dir / "test_001.txt").exists()
        assert (dest_dir / "test_002.txt").exists()
        assert (Path(tmpdir) / "other.txt").exists()  # not moved
        assert not (Path(tmpdir) / "test_001.txt").exists()
