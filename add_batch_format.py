#!/usr/bin/env python3
import re
import sys

with open("servers/coder/server.py", "r") as f:
    content = f.read()

# Find the position of git_status function (since we want to insert before it)
pattern = r"(@mcp\.tool\(\)\s*\ndef git_status)"
match = re.search(pattern, content)
if not match:
    sys.stderr.write("Could not find git_status function\n")
    sys.exit(1)

pos = match.start()

# New function source
new_func = '''
@mcp.tool()
def batch_format(directory: str, file_pattern: str = "*.py") -> str:
    """
    Format all Python files in a directory using Black.

    Args:
        directory: Path to the directory containing Python files.
        file_pattern: File pattern to match (default "*.py").

    Returns:
        Summary of formatted files.
    """
    try:
        import subprocess
        from pathlib import Path
        import fnmatch

        p = Path(directory).expanduser().resolve()
        if not p.exists():
            return f"Error: Directory not found: {directory}"
        if not p.is_dir():
            return f"Error: Path is not a directory: {directory}"

        # Collect matching files
        files = []
        for file in p.rglob(file_pattern):
            if file.is_file():
                files.append(str(file))

        if not files:
            return f"No files matching pattern '{file_pattern}' found."

        formatted_count = 0
        errors = []
        for file in files:
            try:
                result = subprocess.run(
                    ["black", file],
                    capture_output=True,
                    text=True,
                    timeout=30,
                )
                if result.returncode == 0:
                    formatted_count += 1
                else:
                    errors.append(f"{file}: {result.stderr}")
            except subprocess.TimeoutExpired:
                errors.append(f"{file}: Black formatting timed out.")
            except Exception as e:
                errors.append(f"{file}: {e}")

        summary_lines = [f"Formatted {formatted_count} out of {len(files)} files."]
        if errors:
            summary_lines.append("\\nErrors:")
            for err in errors[:5]:  # limit error output
                summary_lines.append(f"- {err}")
            if len(errors) > 5:
                summary_lines.append(f"... and {len(errors) - 5} more errors.")
        return "\\n".join(summary_lines)
    except Exception as e:
        return f"Error in batch_format: {str(e)}"

'''

# Insert new function before git_status
new_content = content[:pos] + new_func + content[pos:]

with open("servers/coder/server.py", "w") as f:
    f.write(new_content)

print("Successfully added batch_format function.")
