import os
import sys

from markitdown import MarkItDown
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("office_reader", log_level="ERROR")

SUPPORTED_FORMATS = [
    ".pdf",
    ".docx",
    ".pptx",
    ".xlsx",
    ".xls",
    ".jpg",
    ".jpeg",
    ".png",
    ".gif",
    ".bmp",
    ".tiff",
    ".html",
    ".htm",
    ".csv",
    ".json",
    ".xml",
    ".zip",
    ".epub",
    ".txt",
    ".mp3",
    ".wav",
    ".m4a",
    ".flac",
    ".ogg",
]


@mcp.tool()
def read_office_file(file_path: str) -> str:
    """
    Convert an office/document file to Markdown.

    Args:
        file_path: Absolute path to the file.

    Returns:
        Markdown content of the file, or error message.
    """
    if not os.path.exists(file_path):
        return f"Error: File not found at '{file_path}'."

    if not os.path.isfile(file_path):
        return f"Error: '{file_path}' is not a file."

    # Optional: check extension for quick unsupported format warning
    _, ext = os.path.splitext(file_path)
    ext = ext.lower()
    if ext not in SUPPORTED_FORMATS:
        # Still try conversion, as markitdown may support more formats
        pass

    try:
        md = MarkItDown(enable_plugins=False)
        result = md.convert(file_path)
        return result.text_content
    except ImportError as e:
        return f"Error: markitdown library or a required dependency is not installed. {str(e)}"
    except ValueError as e:
        # MarkItDown may raise ValueError for unsupported file types
        return f"Error: Unsupported file type or invalid file content. {str(e)}"
    except Exception as e:
        return f"Error converting file '{file_path}': {str(e)}"


@mcp.tool()
def list_supported_formats() -> str:
    """
    List the supported file extensions for office/document conversion.

    Returns:
        A markdown list of supported extensions.
    """
    lines = ["Supported file extensions:", ""]
    for fmt in SUPPORTED_FORMATS:
        lines.append(f"- `{fmt}`")
    lines.append("")
    lines.append("Note: MarkItDown may support additional formats beyond this list.")
    lines.append(
        "Some formats require additional system libraries (e.g., libreoffice for office files)."
    )
    return "\n".join(lines)


if __name__ == "__main__":
    mcp.run()
