#!/usr/bin/env python3
import sys
import re

with open('servers/coder/server.py', 'r') as f:
    content = f.read()

# Find the position of find_unused_imports function
pattern = r'(@mcp\.tool\(\)\s*\ndef find_unused_imports)'
match = re.search(pattern, content)
if not match:
    sys.stderr.write("Could not find find_unused_imports function\n")
    sys.exit(1)

pos = match.end()  # end of the matched pattern, i.e., after the def line
# We need to find the end of the function (the line before next @mcp.tool or end of file)
# Simpler: insert after the entire function block. We'll search for the next @mcp.tool
# after this position.
next_tool = re.search(r'\n@mcp\.tool\(\)', content[pos:])
if not next_tool:
    # fallback: insert before the if __name__ block
    next_tool = re.search(r'\nif __name__ == "__main__":', content[pos:])
    if not next_tool:
        sys.stderr.write("Could not find next tool or main block\n")
        sys.exit(1)
insert_pos = pos + next_tool.start()
else:
    insert_pos = pos + next_tool.start()

# New function source
new_func = '''
@mcp.tool()
def auto_import(file_path: str, dry_run: bool = False) -> str:
    """
    Attempt to add missing imports for unresolved names in a Python file.

    Args:
        file_path: Absolute path to the Python file.
        dry_run: If True, only report what would be added without modifying the file.

    Returns:
        Summary of imports added or suggested.
    """
    try:
        import ast
        from pathlib import Path
        import importlib

        p = Path(file_path).expanduser().resolve()
        if not p.exists():
            return f"Error: File not found: {file_path}"
        if p.suffix != ".py":
            return "Error: Only Python files are supported."

        content = p.read_text(encoding="utf-8")
        tree = ast.parse(content)

        # Collect defined names (functions, classes, variables, parameters)
        defined_names = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                defined_names.add(node.name)
                # parameters
                for arg in node.args.args:
                    defined_names.add(arg.arg)
            elif isinstance(node, ast.ClassDef):
                defined_names.add(node.name)
            elif isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        defined_names.add(target.id)
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    defined_names.add(alias.name)
                    if alias.asname:
                        defined_names.add(alias.asname)
            elif isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    defined_names.add(alias.name)
                    if alias.asname:
                        defined_names.add(alias.asname)

        # Collect all name usages
        used_names = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
                used_names.add(node.id)

        # Remove builtins
        import builtins
        builtin_names = set(dir(builtins))
        used_names -= builtin_names
        # Remove defined names
        unresolved = used_names - defined_names

        # Mapping of common names to import statements
        STANDARD_LIB_MAP = {
            "datetime": "import datetime",
            "time": "import time",
            "json": "import json",
            "os": "import os",
            "sys": "import sys",
            "re": "import re",
            "math": "import math",
            "random": "import random",
            "pathlib": "from pathlib import Path",
            "Path": "from pathlib import Path",
            "List": "from typing import List",
            "Dict": "from typing import Dict",
            "Optional": "from typing import Optional",
            "Union": "from typing import Union",
            "Any": "from typing import Any",
            "Tuple": "from typing import Tuple",
            "Callable": "from typing import Callable",
            "logging": "import logging",
            "subprocess": "import subprocess",
            "shutil": "import shutil",
            "tempfile": "import tempfile",
            "datetime": "import datetime",
            "date": "from datetime import date",
            "timedelta": "from datetime import timedelta",
            "Decimal": "from decimal import Decimal",
            "fractions": "from fractions import Fraction",
            "collections": "import collections",
            "itertools": "import itertools",
            "functools": "import functools",
            "hashlib": "import hashlib",
            "base64": "import base64",
            "csv": "import csv",
            "xml": "import xml.etree.ElementTree",
            "html": "import html",
        }

        # Determine which unresolved names can be mapped
        imports_to_add = []
        for name in sorted(unresolved):
            if name in STANDARD_LIB_MAP:
                import_stmt = STANDARD_LIB_MAP[name]
                # Avoid duplicate imports
                if import_stmt not in imports_to_add:
                    imports_to_add.append(import_stmt)

        if not imports_to_add:
            return "No missing imports detected for unresolved names."

        # If dry_run, just report
        if dry_run:
            lines = ["## Suggested imports (dry run):", ""]
            for stmt in imports_to_add:
                lines.append(f"- `{stmt}`")
            return "\\n".join(lines)

        # Modify file: add imports at the top after any existing imports or module docstring
        lines = content.splitlines()
        insert_line = 0
        # Skip shebang and module docstring
        while insert_line < len(lines) and (lines[insert_line].startswith('#!') or lines[insert_line].startswith('"""') or lines[insert_line].startswith("'''")):
            insert_line += 1
        # Skip existing imports
        while insert_line < len(lines) and (lines[insert_line].startswith('import ') or lines[insert_line].startswith('from ')):
            insert_line += 1

        # Prepare import lines
        import_lines = []
        for stmt in imports_to_add:
            if stmt not in content:  # simple duplicate check
                import_lines.append(stmt)

        if not import_lines:
            return "All suggested imports already present."

        # Insert
        for stmt in reversed(import_lines):
            lines.insert(insert_line, stmt)

        new_content = "\\n".join(lines)
        p.write_text(new_content, encoding="utf-8")

        summary = ["## Added imports:", ""]
        for stmt in import_lines:
            summary.append(f"- `{stmt}`")
        return "\\n".join(summary)
    except SyntaxError as e:
        return f"Syntax error in file: {e}"
    except Exception as e:
        return f"Error auto-importing: {str(e)}"

'''

# Insert new function before the insert position
new_content = content[:insert_pos] + new_func + content[insert_pos:]

with open('servers/coder/server.py', 'w') as f:
    f.write(new_content)

print("Successfully added auto_import function.")
