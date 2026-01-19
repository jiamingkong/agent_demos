import re
import shutil
from pathlib import Path
from typing import List

from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("os_manipulation", log_level="ERROR")


@mcp.tool()
def list_directory(path: str) -> str:
    """
    List contents of a directory.

    Args:
        path: Absolute path to the directory.
    """
    try:
        p = Path(path).expanduser().resolve()
        if not p.exists():
            return f"Error: Path '{path}' not found."
        if not p.is_dir():
            return f"Error: Path '{path}' is not a directory."
        items = []
        for item in p.iterdir():
            if item.name.startswith("."):
                continue
            type_str = "[DIR]" if item.is_dir() else "[FILE]"
            items.append(f"{type_str} {item.name}")
        return "\n".join(sorted(items))
    except Exception as e:
        return str(e)


@mcp.tool()
def create_directories(paths: List[str]) -> str:
    """
    Create multiple directories at once.

    Args:
        paths: List of absolute paths to create.
    """
    results = []
    for path in paths:
        try:
            p = Path(path).expanduser().resolve()
            p.mkdir(parents=True, exist_ok=True)
            results.append(f"Successfully created '{path}'")
        except Exception as e:
            results.append(f"Error creating '{path}': {str(e)}")
    return "\n".join(results)


@mcp.tool()
def move_files(sources: List[str], destination: str) -> str:
    """
    Move multiple files to a specific destination directory.

    Args:
        sources: List of source file paths to move.
        destination: Destination directory path.
    """
    results = []
    try:
        dst_path = Path(destination).expanduser().resolve()
        if not dst_path.exists():
            return f"Error: Destination '{destination}' does not exist."
        if not dst_path.is_dir():
            return f"Error: Destination '{destination}' is not a directory."

        for source in sources:
            try:
                src_path = Path(source).expanduser().resolve()
                if not src_path.exists():
                    results.append(f"Error: Source '{source}' not found.")
                    continue

                final_dst = dst_path / src_path.name
                shutil.move(str(src_path), str(final_dst))
                results.append(f"Moved '{src_path.name}' to '{final_dst}'")
            except Exception as e:
                results.append(f"Error moving '{source}': {str(e)}")

        return "\n".join(results)
    except Exception as e:
        return f"Critical Error: {str(e)}"


@mcp.tool()
def move_files_by_regex(source_dir: str, destination: str, pattern: str) -> str:
    """
    Move files matching a regex pattern from source directory to destination.

    Args:
        source_dir: Directory to search files in.
        destination: Destination directory.
        pattern: Python regex pattern to match filenames.
    """
    try:
        src_path = Path(source_dir).expanduser().resolve()
        dst_path = Path(destination).expanduser().resolve()

        if not src_path.is_dir():
            return f"Error: Source '{source_dir}' is not a directory."
        if not dst_path.exists():
            dst_path.mkdir(parents=True, exist_ok=True)
        if not dst_path.is_dir():
            return f"Error: Destination '{destination}' is not a directory."

        regex = re.compile(pattern)
        results = []

        for item in src_path.iterdir():
            if item.is_file() and regex.search(item.name):
                try:
                    final_dst = dst_path / item.name
                    shutil.move(str(item), str(final_dst))
                    results.append(f"Moved '{item.name}'")
                except Exception as e:
                    results.append(f"Error moving '{item.name}': {str(e)}")

        if not results:
            return "No files matched the pattern."
        return "\n".join(results)

    except Exception as e:
        return f"Error: {str(e)}"


if __name__ == "__main__":
    mcp.run()
