import os
import zipfile
import tarfile
import gzip
import bz2
import shutil
from pathlib import Path
from typing import List

from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("file_compression", log_level="ERROR")


def _normalize_path(path: str) -> Path:
    """Expand user and resolve to absolute path."""
    return Path(path).expanduser().resolve()


@mcp.tool()
def compress_file(source_path: str, archive_path: str, format: str = "zip") -> str:
    """
    Compress a single file into an archive.

    Args:
        source_path: Absolute path to the source file.
        archive_path: Absolute path for the output archive.
        format: Archive format: 'zip', 'tar', 'tar.gz', 'tar.bz2'. Default is 'zip'.
    """
    try:
        src = _normalize_path(source_path)
        dst = _normalize_path(archive_path)

        if not src.exists():
            return f"Error: Source file '{source_path}' not found."
        if not src.is_file():
            return f"Error: Source '{source_path}' is not a regular file."

        # Ensure parent directory exists
        dst.parent.mkdir(parents=True, exist_ok=True)

        if format == "zip":
            with zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED) as zf:
                zf.write(src, src.name)
        elif format == "tar":
            with tarfile.open(dst, "w") as tf:
                tf.add(src, src.name)
        elif format == "tar.gz":
            with tarfile.open(dst, "w:gz") as tf:
                tf.add(src, src.name)
        elif format == "tar.bz2":
            with tarfile.open(dst, "w:bz2") as tf:
                tf.add(src, src.name)
        else:
            return f"Error: Unsupported format '{format}'. Supported: zip, tar, tar.gz, tar.bz2."

        return f"Successfully compressed '{src}' into '{dst}'."
    except Exception as e:
        return f"Error: {str(e)}"


@mcp.tool()
def compress_directory(source_dir: str, archive_path: str, format: str = "zip") -> str:
    """
    Recursively compress a directory into an archive.

    Args:
        source_dir: Absolute path to the source directory.
        archive_path: Absolute path for the output archive.
        format: Archive format, same as compress_file. Default is 'zip'.
    """
    try:
        src = _normalize_path(source_dir)
        dst = _normalize_path(archive_path)

        if not src.exists():
            return f"Error: Source directory '{source_dir}' not found."
        if not src.is_dir():
            return f"Error: Source '{source_dir}' is not a directory."

        dst.parent.mkdir(parents=True, exist_ok=True)

        if format == "zip":
            with zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED) as zf:
                for root, dirs, files in os.walk(src):
                    for file in files:
                        file_path = Path(root) / file
                        arcname = file_path.relative_to(src)
                        zf.write(file_path, arcname)
        elif format == "tar":
            with tarfile.open(dst, "w") as tf:
                tf.add(src, src.name)
        elif format == "tar.gz":
            with tarfile.open(dst, "w:gz") as tf:
                tf.add(src, src.name)
        elif format == "tar.bz2":
            with tarfile.open(dst, "w:bz2") as tf:
                tf.add(src, src.name)
        else:
            return f"Error: Unsupported format '{format}'."

        return f"Successfully compressed directory '{src}' into '{dst}'."
    except Exception as e:
        return f"Error: {str(e)}"


@mcp.tool()
def decompress_archive(archive_path: str, extract_dir: str) -> str:
    """
    Extract an archive to a specified directory.

    Args:
        archive_path: Absolute path to the archive file.
        extract_dir: Absolute path to the extraction directory.
    """
    try:
        archive = _normalize_path(archive_path)
        extract_to = _normalize_path(extract_dir)

        if not archive.exists():
            return f"Error: Archive '{archive_path}' not found."
        if not archive.is_file():
            return f"Error: Archive '{archive_path}' is not a regular file."

        extract_to.mkdir(parents=True, exist_ok=True)

        # Determine format by extension
        suffix = archive.suffix.lower()
        if suffix == ".zip":
            with zipfile.ZipFile(archive, "r") as zf:
                zf.extractall(extract_to)
        elif suffix in [".tar", ".tar.gz", ".tgz", ".tar.bz2", ".tbz2", ".tbz"]:
            # tarfile can auto‑detect compression
            with tarfile.open(archive, "r:*") as tf:
                tf.extractall(extract_to)
        else:
            # Try to open as generic tar (auto‑detect)
            try:
                with tarfile.open(archive, "r:*") as tf:
                    tf.extractall(extract_to)
            except tarfile.ReadError:
                return f"Error: Unsupported archive format for '{archive_path}'."

        return f"Successfully extracted '{archive}' to '{extract_to}'."
    except Exception as e:
        return f"Error: {str(e)}"


@mcp.tool()
def list_archive_contents(archive_path: str) -> str:
    """
    List files and directories inside an archive.

    Args:
        archive_path: Absolute path to the archive file.
    """
    try:
        archive = _normalize_path(archive_path)
        if not archive.exists():
            return f"Error: Archive '{archive_path}' not found."
        if not archive.is_file():
            return f"Error: Archive '{archive_path}' is not a regular file."

        lines = []
        suffix = archive.suffix.lower()
        if suffix == ".zip":
            with zipfile.ZipFile(archive, "r") as zf:
                for info in zf.infolist():
                    lines.append(f"{info.filename} ({info.file_size} bytes)")
        else:
            # tar or compressed tar
            try:
                with tarfile.open(archive, "r:*") as tf:
                    for member in tf.getmembers():
                        lines.append(f"{member.name} ({member.size} bytes)")
            except tarfile.ReadError:
                return f"Error: Cannot read archive '{archive_path}' as ZIP or TAR."

        if not lines:
            return "Archive is empty."
        return "\n".join(lines)
    except Exception as e:
        return f"Error: {str(e)}"


@mcp.tool()
def get_archive_info(archive_path: str) -> str:
    """
    Get metadata about an archive: size, compression ratio, number of files, etc.

    Args:
        archive_path: Absolute path to the archive file.
    """
    try:
        archive = _normalize_path(archive_path)
        if not archive.exists():
            return f"Error: Archive '{archive_path}' not found."
        if not archive.is_file():
            return f"Error: Archive '{archive_path}' is not a regular file."

        total_files = 0
        total_uncompressed = 0
        total_compressed = 0
        suffix = archive.suffix.lower()

        if suffix == ".zip":
            with zipfile.ZipFile(archive, "r") as zf:
                for info in zf.infolist():
                    total_files += 1
                    total_uncompressed += info.file_size
                    total_compressed += info.compress_size
        else:
            # tar or compressed tar
            try:
                with tarfile.open(archive, "r:*") as tf:
                    for member in tf.getmembers():
                        total_files += 1
                        total_uncompressed += member.size
                # For tar, compressed size is the archive file size
                total_compressed = archive.stat().st_size
            except tarfile.ReadError:
                return f"Error: Cannot read archive '{archive_path}' as ZIP or TAR."

        archive_size = archive.stat().st_size
        compression_ratio = (
            (total_uncompressed - total_compressed) / total_uncompressed * 100
            if total_uncompressed > 0
            else 0
        )

        info_lines = [
            f"Archive: {archive.name}",
            f"Full path: {archive}",
            f"Size on disk: {archive_size} bytes",
            f"Number of files: {total_files}",
            f"Total uncompressed size: {total_uncompressed} bytes",
            f"Total compressed size: {total_compressed} bytes",
            f"Compression ratio: {compression_ratio:.2f}%",
        ]
        return "\n".join(info_lines)
    except Exception as e:
        return f"Error: {str(e)}"


if __name__ == "__main__":
    mcp.run()
