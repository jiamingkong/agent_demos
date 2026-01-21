#!/usr/bin/env python3
import sys
import re

with open('servers/coder/server.py', 'r') as f:
    content = f.read()

# Find the position of generate_unit_tests function
# We'll insert before the @mcp.tool() decorator of generate_unit_tests
pattern = r'(@mcp\.tool\(\)\s*\ndef generate_unit_tests)'
match = re.search(pattern, content)
if not match:
    sys.stderr.write("Could not find generate_unit_tests function\n")
    sys.exit(1)

pos = match.start()

# New function source
new_func = '''@mcp.tool()
def find_unused_imports(file_path: str) -> str:
    """
    Detect unused imports in a Python file using AST.

    Args:
        file_path: Absolute path to the Python file.

    Returns:
        Markdown list of unused imports or success message.
    """
    try:
        import ast
        import builtins
        from pathlib import Path

        p = Path(file_path).expanduser().resolve()
        if not p.exists():
            return f"Error: File not found: {file_path}"
        if p.suffix != ".py":
            return "Error: Only Python files are supported."

        content = p.read_text(encoding="utf-8")
        tree = ast.parse(content)

        # Collect imported names
        imported_names = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imported_names.add(alias.name)
                    if alias.asname:
                        imported_names.add(alias.asname)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    # For 'from module import x', we track x, not module
                    for alias in node.names:
                        imported_names.add(alias.name)
                        if alias.asname:
                            imported_names.add(alias.asname)

        # Collect all names used in the code (excluding imports)
        used_names = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
                used_names.add(node.id)

        # Remove builtins and special names
        builtin_names = set(dir(builtins))
        used_names -= builtin_names

        # Find unused imports
        unused = imported_names - used_names
        if not unused:
            return "No unused imports found."

        # Format output
        lines = ["## Unused Imports", ""]
        for name in sorted(unused):
            lines.append(f"- `{name}`")
        return "\\n".join(lines)
    except SyntaxError as e:
        return f"Syntax error in file: {e}"
    except Exception as e:
        return f"Error analyzing imports: {str(e)}"

'''

# Insert new function before the matched pattern
new_content = content[:pos] + new_func + content[pos:]

with open('servers/coder/server.py', 'w') as f:
    f.write(new_content)

print("Successfully added find_unused_imports function.")
