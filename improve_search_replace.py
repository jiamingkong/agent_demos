#!/usr/bin/env python3
import re
import sys

with open('servers/coder/server.py', 'r') as f:
    content = f.read()

# Pattern to match the entire search_and_replace function (including decorator)
pattern = r'(@mcp\.tool\(\)\s*\ndef search_and_replace\(.*?\) -> str:\s*""".*?"""\s*.*?)(?=\n@mcp\.tool|\nif __name__ == "__main__":)'
# Use DOTALL flag to match across lines
pat = re.compile(pattern, re.DOTALL)
match = pat.search(content)
if not match:
    sys.stderr.write("Could not find search_and_replace function\n")
    sys.exit(1)

old_func = match.group(1)
print(f"Found function of length {len(old_func)}")

# New function implementation
new_func = '''@mcp.tool()
def search_and_replace(
    folder_path: str,
    search_pattern: str,
    replace_pattern: str,
    file_pattern: str = "*",
    dry_run: bool = False,
    keep_backup: bool = False,
) -> str:
    """
    Search and replace across multiple files using grep and sed.

    Args:
        folder_path: Directory to search in.
        search_pattern: Regex pattern to search for.
        replace_pattern: Replacement string (supports backreferences).
        file_pattern: File pattern to filter (default "*").
        dry_run: If True, only show which files would be changed.
        keep_backup: If True, keep backup files (.bak) after replacement.

    Returns:
        Summary of replacements made.
    """
    try:
        import os
        import subprocess

        p = Path(folder_path).expanduser().resolve()
        if not p.exists():
            return f"Error: Path not found: {folder_path}"
        if not p.is_dir():
            return f"Error: Path is not a directory: {folder_path}"

        # Use grep to find files containing the pattern
        result = subprocess.run(
            ["grep", "-r", "-l", search_pattern, str(p)],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0 and result.returncode != 1:
            return f"Grep failed: {result.stderr}"
        files = result.stdout.strip().split("\\n")
        files = [f for f in files if f]
        if not files:
            return "No files matched the search pattern."

        if dry_run:
            lines = ["## Files that would be modified (dry run):", ""]
            for file in files:
                lines.append(f"- `{file}`")
            return "\\n".join(lines)

        # Perform replacement
        replaced_count = 0
        for file in files:
            # Use sed -i.bak for backup (macOS syntax)
            subprocess.run(
                ["sed", "-i.bak", f"s/{search_pattern}/{replace_pattern}/g", file],
                check=False,
            )
            # Remove backup unless keep_backup is True
            if not keep_backup:
                backup = file + ".bak"
                if os.path.exists(backup):
                    os.remove(backup)
            replaced_count += 1

        summary = f"Replaced pattern '{search_pattern}' with '{replace_pattern}' in {replaced_count} files."
        if keep_backup:
            summary += " Backup files (.bak) have been kept."
        return summary
    except Exception as e:
        return f"Error in search_and_replace: {str(e)}"
'''

# Replace old function with new function
new_content = content.replace(old_func, new_func)
# Verify that replacement occurred
if new_content == content:
    sys.stderr.write("Replacement failed: old function not found.\n")
    sys.exit(1)

with open('servers/coder/server.py', 'w') as f:
    f.write(new_content)

print("Successfully updated search_and_replace function.")
