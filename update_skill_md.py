#!/usr/bin/env python3
import re

with open("servers/coder/SKILL.md", "r") as f:
    lines = f.readlines()

# Find the allowed-tools section
in_allowed = False
for i, line in enumerate(lines):
    if line.strip() == "allowed-tools:":
        in_allowed = True
        start = i
    if in_allowed and line.strip() == "---":
        end = i
        break

# Insert new tools after detect_code_smells
new_tools = ["find_unused_imports", "batch_format"]
for i in range(start, end):
    if "detect_code_smells" in lines[i]:
        # Insert after this line
        for tool in new_tools:
            lines.insert(i + 1, f"  - {tool}\n")
        break

# Also need to add generate_unit_tests if not already present (it is)
# Now add tool descriptions after the existing tools section
# Find the line with "### detect_code_smells" (or the last tool)
# We'll insert after the entire tools section, but easier: insert before "## Usage Strategy"
for i, line in enumerate(lines):
    if line.strip() == "## Usage Strategy: Reliable Code Editing":
        # Insert before this line
        new_sections = """
### find_unused_imports
Detect unused imports in a Python file using AST.
- `file_path`: Absolute path to the Python file.

### batch_format
Format all Python files in a directory using Black.
- `directory`: Path to the directory containing Python files.
- `file_pattern`: File pattern to match (default "*.py").

### search_and_replace (enhanced)
Search and replace across multiple files using grep and sed, with optional dry-run and backup retention.
- `folder_path`: Directory to search in.
- `search_pattern`: Regex pattern to search for.
- `replace_pattern`: Replacement string (supports backreferences).
- `file_pattern`: File pattern to filter (default "*").
- `dry_run`: If True, only show which files would be changed.
- `keep_backup`: If True, keep backup files (.bak) after replacement.
"""
        lines.insert(i, new_sections)
        break

with open("servers/coder/SKILL.md", "w") as f:
    f.writelines(lines)

print("Updated SKILL.md")
