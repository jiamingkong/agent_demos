import os
import tempfile
from pathlib import Path

from servers.file_compression.server import (compress_directory, compress_file,
                                             decompress_archive,
                                             get_archive_info,
                                             list_archive_contents)


def test_compress_file():
    """Test compressing a single file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        src = Path(tmpdir) / "test.txt"
        src.write_text("hello world")
        archive = Path(tmpdir) / "test.zip"
        result = compress_file(str(src), str(archive))
        # returns success message containing the path
        assert str(archive) in result
        assert archive.exists()


def test_compress_directory():
    """Test compressing a directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        dir_path = Path(tmpdir) / "mydir"
        dir_path.mkdir()
        (dir_path / "file1.txt").write_text("content1")
        (dir_path / "file2.txt").write_text("content2")
        archive = Path(tmpdir) / "dir.zip"
        result = compress_directory(str(dir_path), str(archive))
        assert str(archive) in result
        assert archive.exists()
        listing = list_archive_contents(str(archive))
        # listing includes file names
        assert "file1.txt" in listing
        assert "file2.txt" in listing


def test_decompress_archive():
    """Test decompressing an archive."""
    with tempfile.TemporaryDirectory() as tmpdir:
        src = Path(tmpdir) / "original.txt"
        src.write_text("data")
        archive = Path(tmpdir) / "archive.zip"
        compress_file(str(src), str(archive))
        extract_dir = Path(tmpdir) / "extracted"
        result = decompress_archive(str(archive), str(extract_dir))
        assert str(extract_dir) in result
        assert (extract_dir / "original.txt").exists()
        assert (extract_dir / "original.txt").read_text() == "data"


def test_list_archive_contents():
    """Test listing archive contents."""
    with tempfile.TemporaryDirectory() as tmpdir:
        src = Path(tmpdir) / "list_test.txt"
        src.write_text("test")
        archive = Path(tmpdir) / "list.zip"
        compress_file(str(src), str(archive))
        listing = list_archive_contents(str(archive))
        assert "list_test.txt" in listing
        # optional: check size info
        assert "bytes" in listing


def test_get_archive_info():
    """Test getting archive info."""
    with tempfile.TemporaryDirectory() as tmpdir:
        src = Path(tmpdir) / "info_test.txt"
        src.write_text("x" * 100)
        archive = Path(tmpdir) / "info.zip"
        compress_file(str(src), str(archive))
        info = get_archive_info(str(archive))
        assert "info.zip" in info
        assert "100" in info  # original size
        assert "Compression" in info
