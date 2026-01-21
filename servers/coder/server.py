import ast
import os
import re
import subprocess
from pathlib import Path
from typing import Dict, List, Optional

from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("coder", log_level="ERROR")


def _analyze_python_file(path: Path) -> str:
    """Extracts high-level structure (classes, functions, docstrings) from a Python file."""
    try:
        content = path.read_text(encoding="utf-8", errors="replace")
        tree = ast.parse(content)
        summary = []

        # Module Docstring
        docstring = ast.get_docstring(tree)
        if docstring:
            summary.append(f'Docstring: """{docstring.strip().splitlines()[0]}..."""')

        for node in tree.body:
            if isinstance(node, ast.ClassDef):
                methods = [n.name for n in node.body if isinstance(n, ast.FunctionDef)]
                summary.append(f"Class: {node.name} ({', '.join(methods)})")
            elif isinstance(node, ast.FunctionDef):
                summary.append(f"Function: {node.name}")
            elif isinstance(node, ast.Assign):
                # Try to catch uppercase constants
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id.isupper():
                        summary.append(f"Constant: {target.id}")

        return "\n".join(summary)
    except Exception as e:
        return f"Error parsing Python file: {e}"


def _analyze_javascript_file(path: Path) -> str:
    """Extracts high-level structure (functions, classes) from a JavaScript file."""
    try:
        content = path.read_text(encoding="utf-8", errors="replace")
        summary = []
        # Simple regex for function declarations
        import re

        # Match function declarations: function name(...) { ... }
        func_pattern = r"function\s+(\w+)\s*\([^)]*\)\s*{"
        for match in re.finditer(func_pattern, content):
            summary.append(f"Function: {match.group(1)}")
        # Match arrow functions assigned to const/let/var
        arrow_pattern = r"(?:const|let|var)\s+(\w+)\s*=\s*\([^)]*\)\s*=>"
        for match in re.finditer(arrow_pattern, content):
            summary.append(f"Arrow Function: {match.group(1)}")
        # Match class declarations
        class_pattern = r"class\s+(\w+)"
        for match in re.finditer(class_pattern, content):
            summary.append(f"Class: {match.group(1)}")
        return "\n".join(summary) if summary else "No functions/classes found."
    except Exception as e:
        return f"Error parsing JavaScript file: {e}"


def _analyze_typescript_file(path: Path) -> str:
    """Extracts high-level structure from a TypeScript file."""
    try:
        content = path.read_text(encoding="utf-8", errors="replace")
        summary = []
        import re

        # Match function declarations (including TypeScript syntax)
        func_pattern = r"function\s+(\w+)\s*\([^)]*\)\s*(?::[^{]*)?\s*{"
        for match in re.finditer(func_pattern, content):
            summary.append(f"Function: {match.group(1)}")
        # Arrow functions
        arrow_pattern = r"(?:const|let|var)\s+(\w+)\s*=\s*\([^)]*\)\s*=>"
        for match in re.finditer(arrow_pattern, content):
            summary.append(f"Arrow Function: {match.group(1)}")
        # Classes
        class_pattern = r"class\s+(\w+)"
        for match in re.finditer(class_pattern, content):
            summary.append(f"Class: {match.group(1)}")
        # Interfaces
        interface_pattern = r"interface\s+(\w+)"
        for match in re.finditer(interface_pattern, content):
            summary.append(f"Interface: {match.group(1)}")
        # Type aliases
        type_pattern = r"type\s+(\w+)\s*="
        for match in re.finditer(type_pattern, content):
            summary.append(f"Type Alias: {match.group(1)}")
        # Enums
        enum_pattern = r"enum\s+(\w+)"
        for match in re.finditer(enum_pattern, content):
            summary.append(f"Enum: {match.group(1)}")

        return "\n".join(summary) if summary else "No functions/classes found."
    except Exception as e:
        return f"Error parsing TypeScript file: {e}"


def _analyze_java_file(path: Path) -> str:
    """Extracts high-level structure from a Java file."""
    try:
        content = path.read_text(encoding="utf-8", errors="replace")
        summary = []
        import re

        # Match class definitions (including public, abstract, etc.)
        class_pattern = (
            r"(?:public\s+|private\s+|protected\s+|abstract\s+)*class\s+(\w+)"
        )
        for match in re.finditer(class_pattern, content):
            summary.append(f"Class: {match.group(1)}")
        # Method declarations (simplified)
        method_pattern = r"(?:public\s+|private\s+|protected\s+|static\s+)*\w+\s+(\w+)\s*\([^)]*\)\s*(?:\{|\s*throws)"
        for match in re.finditer(method_pattern, content):
            summary.append(f"Method: {match.group(1)}")
        # Interface definitions
        interface_pattern = r"interface\s+(\w+)"
        for match in re.finditer(interface_pattern, content):
            summary.append(f"Interface: {match.group(1)}")
        # Enum definitions
        enum_pattern = r"enum\s+(\w+)"
        for match in re.finditer(enum_pattern, content):
            summary.append(f"Enum: {match.group(1)}")

        return "\n".join(summary) if summary else "No classes/methods found."
    except Exception as e:
        return f"Error parsing Java file: {e}"


def _analyze_cpp_file(path: Path) -> str:
    """Extracts high-level structure from a C++ file."""
    try:
        content = path.read_text(encoding="utf-8", errors="replace")
        summary = []
        import re

        # Match class/struct definitions
        class_pattern = r"(?:class|struct)\s+(\w+)\s*(?::[^{]*)?\s*\{"
        for match in re.finditer(class_pattern, content):
            summary.append(f"Class/Struct: {match.group(1)}")
        # Function definitions (including return type)
        func_pattern = r"\w+\s+\w+\s*\([^)]*\)\s*(?:const\s*)?\{"
        for match in re.finditer(func_pattern, content):
            # Extract function name (simplified)
            # This regex is simplistic; better to parse properly.
            # We'll just capture the word before '(' that is not a type.
            # For simplicity, we'll skip for now.
            pass
        # Namespace
        namespace_pattern = r"namespace\s+(\w+)\s*\{"
        for match in re.finditer(namespace_pattern, content):
            summary.append(f"Namespace: {match.group(1)}")

        return "\n".join(summary) if summary else "No classes/namespaces found."
    except Exception as e:
        return f"Error parsing C++ file: {e}"


def _analyze_rust_file(path: Path) -> str:
    """Extracts high-level structure from a Rust file."""
    try:
        content = path.read_text(encoding="utf-8", errors="replace")
        summary = []
        import re

        # Function definitions: fn name(...) -> ...
        fn_pattern = r"fn\s+(\w+)\s*\([^)]*\)(?:\s*->[^{]*)?\s*\{"
        for match in re.finditer(fn_pattern, content):
            summary.append(f"Function: {match.group(1)}")
        # Struct definitions
        struct_pattern = r"struct\s+(\w+)\s*(?:\{[^}]*\})?"
        for match in re.finditer(struct_pattern, content):
            summary.append(f"Struct: {match.group(1)}")
        # Enum definitions
        enum_pattern = r"enum\s+(\w+)\s*\{"
        for match in re.finditer(enum_pattern, content):
            summary.append(f"Enum: {match.group(1)}")
        # Trait definitions
        trait_pattern = r"trait\s+(\w+)\s*\{"
        for match in re.finditer(trait_pattern, content):
            summary.append(f"Trait: {match.group(1)}")
        # Impl blocks
        impl_pattern = r"impl\s+(\w+)\s*\{"
        for match in re.finditer(impl_pattern, content):
            summary.append(f"Impl: {match.group(1)}")
        # Module declarations
        mod_pattern = r"mod\s+(\w+)\s*\{"
        for match in re.finditer(mod_pattern, content):
            summary.append(f"Module: {match.group(1)}")

        return "\n".join(summary) if summary else "No functions/structs found."
    except Exception as e:
        return f"Error parsing Rust file: {e}"


def _analyze_go_file(path: Path) -> str:
    """Extracts high-level structure from a Go file."""
    try:
        content = path.read_text(encoding="utf-8", errors="replace")
        summary = []
        import re

        # Function definitions: func name(...) ... { or func (receiver) name(...) ... {
        # Match both regular functions and methods
        func_pattern = (
            r"func\s+(?:\(\w+\s+\*?\w+\)\s+)?(\w+)\s*\([^)]*\)(?:\s+[^{]*)?\s*\{"
        )
        for match in re.finditer(func_pattern, content):
            summary.append(f"Function: {match.group(1)}")
        # Struct definitions
        struct_pattern = r"type\s+(\w+)\s+struct\s*\{"
        for match in re.finditer(struct_pattern, content):
            summary.append(f"Struct: {match.group(1)}")
        # Interface definitions
        interface_pattern = r"type\s+(\w+)\s+interface\s*\{"
        for match in re.finditer(interface_pattern, content):
            summary.append(f"Interface: {match.group(1)}")
        # Type aliases (non-struct/interface)
        type_pattern = r"type\s+(\w+)\s+(?!struct|interface)\w+"
        for match in re.finditer(type_pattern, content):
            summary.append(f"Type Alias: {match.group(1)}")
        # Package declaration
        package_match = re.search(r"package\s+(\w+)", content)
        if package_match:
            summary.append(f"Package: {package_match.group(1)}")
        # Import block detection (optional)
        import_match = re.search(r"import\s*\((.*?)\)", content, re.DOTALL)
        if import_match:
            # Count imports
            import_lines = re.findall(r'"(.*?)"', import_match.group(1))
            summary.append(f"Imports: {len(import_lines)} packages")

        return "\n".join(summary) if summary else "No functions/structs found."
    except Exception as e:
        return f"Error parsing Go file: {e}"


def _analyze_html_file(path: Path) -> str:
    """Extracts high-level structure from an HTML file."""
    try:
        content = path.read_text(encoding="utf-8", errors="replace")
        summary = []
        import re

        # Extract tag names (simplified)
        # Match opening tags like <div>, <script>, etc.
        tag_pattern = r"<(\w+)(?:\s+[^>]*)?>"
        tags = re.findall(tag_pattern, content)
        # Count unique tags
        from collections import Counter

        tag_counts = Counter(tags)
        for tag, count in tag_counts.most_common():
            summary.append(f"Tag: {tag} (appears {count} times)")
        # Extract script and style blocks
        if "<script" in content:
            summary.append("Contains JavaScript")
        if "<style" in content:
            summary.append("Contains CSS")
        # Detect common meta tags
        meta_pattern = r"<meta\s+[^>]*>"
        if re.search(meta_pattern, content):
            summary.append("Contains meta tags")
        # Detect title
        title_match = re.search(r"<title>(.*?)</title>", content)
        if title_match:
            summary.append(f"Title: {title_match.group(1)}")
        return "\n".join(summary) if summary else "No significant HTML elements found."
    except Exception as e:
        return f"Error parsing HTML file: {e}"


def _search_files_python(
    folder_path: str,
    pattern: str,
    ignore_case: bool = False,
    file_pattern: str = "*",
    max_depth: Optional[int] = None,
) -> str:
    """
    Search for pattern in files using pure Python.
    """
    import re
    from pathlib import Path

    p = Path(folder_path).expanduser().resolve()
    if not p.exists():
        return f"Error: Path not found: {folder_path}"
    if not p.is_dir():
        return f"Error: Path is not a directory: {folder_path}"

    # Compile regex
    flags = re.IGNORECASE if ignore_case else 0
    try:
        regex = re.compile(pattern, flags)
    except re.error as e:
        return f"Error in regex pattern: {e}"

    # Prepare file pattern matching
    from fnmatch import fnmatch

    matches = []
    # Walk directory
    for root, dirs, files in os.walk(str(p)):
        # Apply max_depth
        if max_depth is not None:
            current_depth = Path(root).relative_to(p).parts
            if len(current_depth) >= max_depth:
                dirs.clear()  # don't go deeper
        for file in files:
            if not fnmatch(file, file_pattern):
                continue
            file_path = Path(root) / file
            try:
                content = file_path.read_text(encoding="utf-8", errors="replace")
                lines = content.splitlines()
                for i, line in enumerate(lines, start=1):
                    if regex.search(line):
                        matches.append(f"{file_path}:{i}:{line}")
            except UnicodeDecodeError:
                # Skip binary files
                continue
            except Exception as e:
                matches.append(f"{file_path}:0:Error reading file: {e}")

    if not matches:
        return "No matches found."

    output = "\n".join(matches)
    if len(output) > 5000:
        output = output[:5000] + "\n... (output truncated)"
    return output


@mcp.tool()
def investigate_and_save_report(folder_path: str) -> str:
    """
    Investigates a folder structure to create a comprehensive context report for LLM agents.
    Scans structure, reads key configuration/dependency files, and existing documentation.
    Saves the report to '.test.Agent.md'.

    Args:
        folder_path: The absolute path of the folder to investigate.
    """
    import datetime

    p = Path(folder_path).expanduser().resolve()
    if not p.exists() or not p.is_dir():
        return f"Error: {folder_path} is not a valid directory."

    report_path = p / ".test.Agent.md"

    # Configuration for exploration
    IGNORE_DIRS = {
        ".git",
        "__pycache__",
        "node_modules",
        "venv",
        ".env",
        "dist",
        "build",
        ".idea",
        ".vscode",
        "target",
    }
    IGNORE_FILES = {
        ".DS_Store",
        "package-lock.json",
        "yarn.lock",
        "pnpm-lock.yaml",
        ".test.Agent.md",
    }

    # Generate Tree Structure
    structure_lines = []
    python_analyses = []
    javascript_analyses = []
    typescript_analyses = []
    java_analyses = []
    cpp_analyses = []
    rust_analyses = []
    go_analyses = []
    html_analyses = []
    other_files_summary = []

    # Statistics
    file_count = 0
    line_count = 0
    language_counts: Dict[str, int] = {}

    for root, dirs, files in os.walk(str(p)):
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]

        rel_path = os.path.relpath(root, str(p))
        if rel_path == ".":
            level = 0
            prefix = ""
        else:
            level = rel_path.count(os.sep) + 1
            prefix = rel_path + "/"

        indent = "  " * level
        structure_lines.append(f"{indent}{os.path.basename(root)}/")

        subindent = "  " * (level + 1)
        for f in sorted(files):
            if f in IGNORE_FILES:
                continue
            structure_lines.append(f"{subindent}{f}")

            # Update statistics
            file_count += 1
            ext = f.split(".")[-1].lower() if "." in f else ""
            if ext:
                language_counts[ext] = language_counts.get(ext, 0) + 1

            file_path = Path(root) / f
            file_rel_path = prefix + f

            # Analyze Python Files
            if f.endswith(".py"):
                analysis = _analyze_python_file(file_path)
                if analysis:
                    python_analyses.append(
                        f"- **{file_rel_path}**\n```text\n{analysis}\n```"
                    )

            # Analyze JavaScript Files
            elif f.endswith(".js"):
                analysis = _analyze_javascript_file(file_path)
                if analysis:
                    javascript_analyses.append(
                        f"- **{file_rel_path}**\n```text\n{analysis}\n```"
                    )

            # Analyze TypeScript Files
            elif f.endswith(".ts") or f.endswith(".tsx"):
                analysis = _analyze_typescript_file(file_path)
                if analysis:
                    typescript_analyses.append(
                        f"- **{file_rel_path}**\n```text\n{analysis}\n```"
                    )

            # Analyze Java Files
            elif f.endswith(".java"):
                analysis = _analyze_java_file(file_path)
                if analysis:
                    java_analyses.append(
                        f"- **{file_rel_path}**\n```text\n{analysis}\n```"
                    )

            # Analyze C++ Files
            elif (
                f.endswith(".cpp")
                or f.endswith(".hpp")
                or f.endswith(".h")
                or f.endswith(".cc")
                or f.endswith(".cxx")
            ):
                analysis = _analyze_cpp_file(file_path)
                if analysis:
                    cpp_analyses.append(
                        f"- **{file_rel_path}**\n```text\n{analysis}\n```"
                    )

            # Analyze Rust Files
            elif f.endswith(".rs"):
                analysis = _analyze_rust_file(file_path)
                if analysis:
                    rust_analyses.append(
                        f"- **{file_rel_path}**\n```text\n{analysis}\n```"
                    )

            # Analyze Go Files
            elif f.endswith(".go"):
                analysis = _analyze_go_file(file_path)
                if analysis:
                    go_analyses.append(
                        f"- **{file_rel_path}**\n```text\n{analysis}\n```"
                    )

            # Analyze HTML Files
            elif f.endswith(".html") or f.endswith(".htm"):
                analysis = _analyze_html_file(file_path)
                if analysis:
                    html_analyses.append(
                        f"- **{file_rel_path}**\n```text\n{analysis}\n```"
                    )

            # Summarize Config/Readmes (Keep it short)
            elif f.upper().startswith("README") or f in [
                "requirements.txt",
                "package.json",
                "Dockerfile",
            ]:
                try:
                    content = file_path.read_text(encoding="utf-8", errors="replace")
                    preview = content[:500].strip() + (
                        "..." if len(content) > 500 else ""
                    )
                    other_files_summary.append(
                        f"- **{file_rel_path}**\n```text\n{preview}\n```"
                    )
                except Exception:
                    pass

    # Construct the report
    report_content = [
        f"# Project Context Report: {p.name}",
        f"Generated: {datetime.datetime.now().isoformat()}",
        "",
        "## 1. Project Structure",
        "```text",
    ]
    report_content.extend(structure_lines)
    report_content.append("```")
    report_content.append("")
    # Project Statistics
    report_content.append("## 2. Project Statistics")
    report_content.append(f"- Total files: {file_count}")
    # Summarize language counts
    if language_counts:
        report_content.append("- Files by extension:")
        for ext, count in sorted(language_counts.items()):
            report_content.append(f"  - .{ext}: {count}")
    report_content.append("")
    report_content.append("## 3. Python Code High-Level Overview")
    report_content.append(
        "Generated by parsing AST. Shows classes, methods, and docstrings."
    )
    report_content.extend(python_analyses)
    report_content.append("")
    if javascript_analyses:
        report_content.append("## 3. JavaScript Code Overview")
        report_content.append("Extracted using regex. Shows functions, classes.")
        report_content.extend(javascript_analyses)
        report_content.append("")
    if typescript_analyses:
        report_content.append("## 4. TypeScript Code Overview")
        report_content.append(
            "Extracted using regex. Shows functions, classes, interfaces, types, enums."
        )
        report_content.extend(typescript_analyses)
        report_content.append("")
    if java_analyses:
        report_content.append("## 5. Java Code Overview")
        report_content.append(
            "Extracted using regex. Shows classes, methods, interfaces, enums."
        )
        report_content.extend(java_analyses)
        report_content.append("")
    if cpp_analyses:
        report_content.append("## 6. C++ Code Overview")
        report_content.append(
            "Extracted using regex. Shows classes, structs, namespaces."
        )
        report_content.extend(cpp_analyses)
        report_content.append("")
    if go_analyses:
        report_content.append("## 7. Go Code Overview")
        report_content.append(
            "Extracted using regex. Shows functions, structs, interfaces, packages."
        )
        report_content.extend(go_analyses)
        report_content.append("")
    report_content.append("## 8. Configuration & Documentation (Preview)")
    report_content.extend(other_files_summary)

    final_report = "\n".join(report_content)

    try:
        report_path.write_text(final_report, encoding="utf-8")
        return f"Investigation complete. Context report saved to {report_path}."
    except Exception as e:
        return f"Error investigating folder: {str(e)}"


@mcp.tool()
def read_code_file(file_path: str, start_line: int = 1, end_line: int = -1) -> str:
    """
    Read a code file, optionally reading specific lines.

    Args:
        file_path: Absolute path to the file.
        start_line: Starting line number (1-based, inclusive).
        end_line: Ending line number (1-based, inclusive). Set to -1 for end of file.
    """
    try:
        p = Path(file_path).expanduser().resolve()
        if not p.exists():
            return f"Error: File not found at {file_path}"
        if not p.is_file():
            return f"Error: Path is not a file: {file_path}"

        with open(p, "r", encoding="utf-8", errors="replace") as f:
            lines = f.readlines()

        total_lines = len(lines)
        if start_line < 1:
            start_line = 1
        if end_line == -1 or end_line > total_lines:
            end_line = total_lines

        if start_line > total_lines:
            return "File has fewer lines than start_line."

        selected_lines = lines[start_line - 1 : end_line]

        content = "".join(selected_lines)
        return f"--- {file_path} (Lines {start_line}-{end_line} of {total_lines}) ---\n{content}"
    except OSError as e:
        return f"OS error reading {file_path}: {e}"
    except UnicodeDecodeError as e:
        return f"Unicode decode error in {file_path}: {e}. Try specifying a different encoding."
    except Exception as e:
        return f"Unexpected error reading {file_path}: {e}"


@mcp.tool()
def search_in_files(folder_path: str, pattern: str) -> str:
    """
    Search for a pattern in files within a folder using grep.

    Args:
        folder_path: The directory to search in.
        pattern: The text or regex pattern to search for.
    """
    try:
        return _search_files_python(
            folder_path, pattern, ignore_case=False, file_pattern="*", max_depth=None
        )
    except Exception as e:
        return f"Error executing search: {str(e)}"


@mcp.tool()
def edit_code_file(file_path: str, old_string: str, new_string: str) -> str:
    """
    Edit a file by replacing an exact string with a new string.

    Args:
        file_path: Absolute path to the file.
        old_string: The exact string to find and replace.
        new_string: The string to replace it with.
    """
    try:
        p = Path(file_path).expanduser().resolve()
        if not p.exists():
            return f"Error: File not found: {file_path}"

        content = p.read_text(encoding="utf-8")

        if old_string not in content:
            return "Error: old_string not found in file. Please ensure exact match including whitespace."

        # Check if multiple occurrences
        if content.count(old_string) > 1:
            return "Error: old_string matches multiple locations. Please Provide more context in old_string to make it unique."

        new_content = content.replace(old_string, new_string)
        p.write_text(new_content, encoding="utf-8")

        return "File updated successfully."
    except Exception as e:
        return f"Error editing file: {str(e)}"


@mcp.tool()
def apply_edit_blocks(file_path: str, edits: str, dry_run: bool = False) -> str:
    """
    Apply multiple search/replace edits to a file using the following format:

    <<<<<<< SEARCH
    (original code to replace)
    =======
    (new code)
    >>>>>>> REPLACE

    Args:
        file_path: Absolute path to the file.
        edits: A string containing one or more edit blocks.
        dry_run: If True, only preview changes without writing file.
    """
    try:
        p = Path(file_path).expanduser().resolve()
        if not p.exists():
            return f"Error: File not found: {file_path}"

        content = p.read_text(encoding="utf-8")

        # Regex to find blocks. We assume markers are on their own lines.
        # Captures content between markers.
        pattern = re.compile(
            r"<<<<<<< SEARCH\s*\n(.*?)=======\s*\n(.*?)>>>>>>> REPLACE", re.DOTALL
        )

        changes = pattern.findall(edits)
        if not changes:
            return "Error: No valid SEARCH/REPLACE blocks found. Ensure you use the exact format:\n<<<<<<< SEARCH\n...\n=======\n...\n>>>>>>> REPLACE"

        new_content = content

        for i, (search_block, replace_block) in enumerate(changes, 1):
            if search_block not in new_content:
                # Provide a snippet of the file content for debugging
                snippet = content[:500] + ("..." if len(content) > 500 else "")
                return f"Error applying Edit #{i}: SEARCH block not found in file. Ensure exact match including indentation and whitespace.\n\nFirst 500 characters of file:\n```\n{snippet}\n```\n\nTip: Use the read_code_file tool to see the exact content."

            if new_content.count(search_block) > 1:
                return f"Error applying Edit #{i}: SEARCH block matches multiple locations (count: {new_content.count(search_block)}). Include more context."

            new_content = new_content.replace(search_block, replace_block, 1)

        # Optional syntax validation for Python files
        if p.suffix == ".py":
            try:
                ast.parse(new_content)
            except SyntaxError as syn_err:
                # Provide more helpful error message
                return f"Error applying edits: Resulting Python file has syntax error: {syn_err}. Changes were not applied."

        if dry_run:
            # Compute diff
            import difflib

            diff = difflib.unified_diff(
                content.splitlines(keepends=True),
                new_content.splitlines(keepends=True),
                fromfile="original",
                tofile="modified",
                lineterm="",
            )
            diff_text = "".join(diff)
            if diff_text:
                return f"Dry-run: preview of changes (file not written):\n```diff\n{diff_text}\n```"
            else:
                return "Dry-run: No changes would be made (SEARCH block already matches REPLACE block?)."
        else:
            p.write_text(new_content, encoding="utf-8")
            return f"Successfully applied {len(changes)} edits to {p.name}."

    except Exception as e:
        return f"Error applying edits: {str(e)}"


@mcp.tool()
def run_terminal_command(command: str) -> str:
    """
    Run a terminal command.
    Warning: This allows execution of arbitrary shell commands.

    Args:
        command: The command execution string.
    """
    # Note: User confirmation is typically handled by the client/UI invoking this tool.
    # The agent should be cautious.
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=60,  # Default timeout
        )

        output = (
            f"COMMAND: {command}\n\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
        )
        return output
    except subprocess.TimeoutExpired:
        return f"Error: Command '{command}' timed out."
    except Exception as e:
        return f"Error running command: {str(e)}"


@mcp.tool()
def create_file(
    file_path: str,
    content: Optional[str] = None,
    overwrite: bool = True,
    append: bool = False,
) -> str:
    """
    Create a new file with optional content, overwrite existing file, or append.

    Args:
        file_path: Absolute path to the file.
        content: Optional text content to write. If None, creates an empty file.
        overwrite: If True (default), overwrite existing file; if False, raise error when file exists.
        append: If True, append content to existing file (creates file if doesn't exist).
                When append is True, overwrite is ignored.

    Returns:
        Success message or error description.
    """
    try:
        p = Path(file_path).expanduser().resolve()

        if p.exists() and not overwrite and not append:
            return f"Error: File already exists at {file_path} and overwrite is False."

        mode = "a" if append else "w"
        encoding = "utf-8"

        # Ensure parent directories exist
        p.parent.mkdir(parents=True, exist_ok=True)

        with open(p, mode, encoding=encoding) as f:
            if content is not None:
                f.write(content)

        action = (
            "Appended to" if append else "Created" if not p.exists() else "Overwritten"
        )
        return f"Success: {action} file at {p}"
    except Exception as e:
        return f"Error creating file: {str(e)}"


@mcp.tool()
def format_code_with_black(file_path: str) -> str:
    """
    Format a Python file using Black code formatter.

    Args:
        file_path: Absolute path to the Python file to format.
    """
    try:
        p = Path(file_path).expanduser().resolve()
        if not p.exists():
            return f"Error: File not found at {file_path}"
        if not p.is_file():
            return f"Error: Path is not a file: {file_path}"
        if not p.suffix == ".py":
            return f"Error: Not a Python file (missing .py extension)."

        # Run black on the file
        result = subprocess.run(
            ["black", str(p)], capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0:
            return f"Successfully formatted {p.name} with Black."
        else:
            return f"Black formatting failed:\nSTDOUT: {result.stdout}\nSTDERR: {result.stderr}"
    except subprocess.TimeoutExpired:
        return "Error: Black formatting timed out."
    except Exception as e:
        return f"Error running Black: {str(e)}"


@mcp.tool()
def analyze_code_complexity(file_path: str) -> str:
    """
    Analyze code complexity of a Python file using Radon.

    Args:
        file_path: Absolute path to the Python file to analyze.
    """
    try:
        p = Path(file_path).expanduser().resolve()
        if not p.exists():
            return f"Error: File not found at {file_path}"
        if not p.is_file():
            return f"Error: Path is not a file: {file_path}"
        if not p.suffix == ".py":
            return f"Error: Not a Python file (missing .py extension)."

        # Run radon cc (cyclomatic complexity)
        result = subprocess.run(
            ["radon", "cc", "-s", str(p)], capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0:
            return f"Complexity analysis for {p.name}:\n{result.stdout}"
        else:
            return f"Radon analysis failed:\nSTDOUT: {result.stdout}\nSTDERR: {result.stderr}"
    except subprocess.TimeoutExpired:
        return "Error: Radon analysis timed out."
    except Exception as e:
        return f"Error running Radon: {str(e)}"


@mcp.tool()
def lint_python_file(file_path: str) -> str:
    """
    Lint a Python file using flake8.

    Args:
        file_path: Absolute path to the Python file to lint.
    """
    try:
        p = Path(file_path).expanduser().resolve()
        if not p.exists():
            return f"Error: File not found at {file_path}"
        if not p.is_file():
            return f"Error: Path is not a file: {file_path}"
        if not p.suffix == ".py":
            return f"Error: Not a Python file (missing .py extension)."

        # Run flake8
        import subprocess

        result = subprocess.run(
            ["flake8", str(p)], capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0:
            return f"No linting issues found in {p.name}."
        else:
            # flake8 outputs issues to stdout
            output = result.stdout if result.stdout else result.stderr
            return f"Linting issues in {p.name}:\n{output}"
    except subprocess.TimeoutExpired:
        return "Error: Flake8 linting timed out."
    except FileNotFoundError:
        return "Error: flake8 not installed. Install with 'pip install flake8'."
    except Exception as e:
        return f"Error running flake8: {str(e)}"


@mcp.tool()
def search_in_files_advanced(
    folder_path: str,
    pattern: str,
    ignore_case: bool = False,
    file_pattern: str = "*",
    max_depth: Optional[int] = None,
) -> str:
    """
    Search for a pattern in files within a folder with advanced options.

    Args:
        folder_path: The directory to search in.
        pattern: The text or regex pattern to search for.
        ignore_case: If True, perform case-insensitive search.
        file_pattern: File pattern to filter files (e.g., "*.py", "*.txt").
        max_depth: Maximum depth of directories to search (None for unlimited).
    """
    try:
        return _search_files_python(
            folder_path, pattern, ignore_case, file_pattern, max_depth
        )
    except subprocess.TimeoutExpired:
        return "Error: Search timed out."
    except Exception as e:
        return f"Error executing search: {str(e)}"


@mcp.tool()
def generate_code(prompt: str, language: str = "python") -> str:
    """
    Generate code based on a natural language prompt using OpenAI.

    Args:
        prompt: Natural language description of the code to generate.
        language: Programming language (default: "python").

    Returns:
        Generated code or error message.
    """
    try:
        import os

        import openai

        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            return "Error: OPENAI_API_KEY environment variable not set."

        client = openai.OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": f"You are a helpful coding assistant. Generate code in {language}.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
            max_tokens=1000,
        )
        content = response.choices[0].message.content  # type: ignore
        if content is None:
            return "Error: No content generated."
        generated = content.strip()
        return f"Generated code ({language}):\n```{language}\n{generated}\n```"
    except ImportError:
        return "Error: openai package not installed. Install with 'pip install openai'."
    except Exception as e:
        return f"Error generating code: {str(e)}"


@mcp.tool()
def search_and_replace(
    folder_path: str,
    search_pattern: str,
    replace_pattern: str,
    file_pattern: str = "*",
    dry_run: bool = False,
    keep_backup: bool = False,
    max_files: Optional[int] = None,
) -> str:
    """
    Search and replace across multiple files using pure Python (no grep/sed).

    Args:
        folder_path: Directory to search in.
        search_pattern: Regex pattern to search for.
        replace_pattern: Replacement string (supports backreferences).
        file_pattern: File pattern to filter (default "*").
        dry_run: If True, only show which files would be changed.
        keep_backup: If True, keep backup files (.bak) after replacement.
        max_files: Maximum number of files to process (optional).

    Returns:
        Summary of replacements made.
    """
    try:
        import fnmatch
        import re
        import shutil
        from pathlib import Path

        p = Path(folder_path).expanduser().resolve()
        if not p.exists():
            return f"Error: Path not found: {folder_path}"
        if not p.is_dir():
            return f"Error: Path is not a directory: {folder_path}"

        # Compile regex
        try:
            regex = re.compile(search_pattern)
        except re.error as e:
            return f"Invalid regex pattern: {e}"

        # Collect matching files
        matched_files = []
        for root, dirs, files in os.walk(str(p)):
            for f in files:
                if not fnmatch.fnmatch(f, file_pattern):
                    continue
                file_path = Path(root) / f
                try:
                    content = file_path.read_text(encoding="utf-8", errors="replace")
                    if regex.search(content):
                        matched_files.append(file_path)
                except UnicodeDecodeError:
                    # Skip binary files
                    continue
                except Exception as e:
                    # Log error but continue
                    pass

        if max_files is not None:
            matched_files = matched_files[:max_files]

        if not matched_files:
            return "No files matched the search pattern."

        if dry_run:
            lines = ["## Files that would be modified (dry run):", ""]
            for file_path in matched_files:
                lines.append(f"- `{file_path}`")
            return "\n".join(lines)

        # Perform replacement
        replaced_count = 0
        for file_path in matched_files:
            # Read content
            content = file_path.read_text(encoding="utf-8", errors="replace")
            # Replace all occurrences
            new_content, num_replacements = regex.subn(replace_pattern, content)
            if num_replacements == 0:
                continue
            # Create backup if requested
            if keep_backup:
                backup_path = file_path.with_suffix(file_path.suffix + ".bak")
                shutil.copy2(file_path, backup_path)
            # Write new content
            file_path.write_text(new_content, encoding="utf-8")
            replaced_count += 1

        summary = f"Replaced pattern '{search_pattern}' with '{replace_pattern}' in {replaced_count} files."
        if keep_backup:
            summary += " Backup files (.bak) have been kept."
        return summary
    except Exception as e:
        return f"Error in search_and_replace: {str(e)}"


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
        import fnmatch
        import subprocess
        from pathlib import Path

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
        for f in files:
            try:
                result = subprocess.run(
                    ["black", f],
                    capture_output=True,
                    text=True,
                    timeout=30,
                )
                if result.returncode == 0:
                    formatted_count += 1
                else:
                    errors.append(f"{f}: {result.stderr}")
            except subprocess.TimeoutExpired:
                errors.append(f"{f}: Black formatting timed out.")
            except Exception as e:
                errors.append(f"{f}: {e}")

        summary_lines = [f"Formatted {formatted_count} out of {len(files)} files."]
        if errors:
            summary_lines.append("\nErrors:")
            for err in errors[:5]:  # limit error output
                summary_lines.append(f"- {err}")
            if len(errors) > 5:
                summary_lines.append(f"... and {len(errors) - 5} more errors.")
        return "\n".join(summary_lines)
    except Exception as e:
        return f"Error in batch_format: {str(e)}"


@mcp.tool()
def git_status(repo_path: str = ".") -> str:
    """
    Show git status of a repository.

    Args:
        repo_path: Path to the git repository (default current directory).
    """
    try:
        import subprocess

        result = subprocess.run(
            ["git", "-C", repo_path, "status", "--short"],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            return f"Error running git status: {result.stderr}"
        return result.stdout if result.stdout else "No changes."
    except Exception as e:
        return f"Error: {str(e)}"


@mcp.tool()
def git_diff(repo_path: str = ".", file_path: Optional[str] = None) -> str:
    """
    Show git diff of a repository or specific file.

    Args:
        repo_path: Path to the git repository.
        file_path: Optional specific file to diff.
    """
    try:
        import subprocess

        cmd = ["git", "-C", repo_path, "diff"]
        if file_path:
            cmd.append(file_path)
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            return f"Error running git diff: {result.stderr}"
        return result.stdout if result.stdout else "No differences."
    except Exception as e:
        return f"Error: {str(e)}"


@mcp.tool()
def git_commit(repo_path: str = ".", message: str = "", files: List[str] = []) -> str:
    """
    Commit changes in a git repository.

    Args:
        repo_path: Path to the git repository.
        message: Commit message.
        files: List of files to commit (empty for all changes).
    """
    try:
        import subprocess

        if not message:
            return "Error: commit message is required."
        cmd = ["git", "-C", repo_path, "commit", "-m", message]
        if files:
            cmd.extend(files)
        else:
            cmd.append("-a")  # commit all changes
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            return f"Error running git commit: {result.stderr}"
        return result.stdout if result.stdout else "Committed successfully."
    except Exception as e:
        return f"Error: {str(e)}"


@mcp.tool()
def git_log(repo_path: str = ".", count: int = 10) -> str:
    """
    Show git log.

    Args:
        repo_path: Path to the git repository.
        count: Number of commits to show.
    """
    try:
        import subprocess

        result = subprocess.run(
            ["git", "-C", repo_path, "log", f"-{count}", "--oneline"],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            return f"Error running git log: {result.stderr}"
        return result.stdout if result.stdout else "No commits."
    except Exception as e:
        return f"Error: {str(e)}"


@mcp.tool()
def type_check_with_mypy(file_path: str) -> str:
    """
    Run mypy type checking on a Python file.

    Args:
        file_path: Path to the Python file.
    """
    try:
        import subprocess

        result = subprocess.run(
            ["mypy", file_path],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            return "No type errors found."
        else:
            return f"Type checking results:\n{result.stdout}\n{result.stderr}"
    except FileNotFoundError:
        return "Error: mypy not installed. Install with 'pip install mypy'."
    except Exception as e:
        return f"Error running mypy: {str(e)}"


@mcp.tool()
def lint_with_pylint(file_path: str) -> str:
    """
    Run pylint on a Python file.

    Args:
        file_path: Path to the Python file.
    """
    try:
        import subprocess

        result = subprocess.run(
            ["pylint", file_path],
            capture_output=True,
            text=True,
        )
        # pylint returns non-zero when there are issues, which is fine
        return result.stdout if result.stdout else "No output from pylint."
    except FileNotFoundError:
        return "Error: pylint not installed. Install with 'pip install pylint'."
    except Exception as e:
        return f"Error running pylint: {str(e)}"


@mcp.tool()
def ai_suggest_code(prompt: str, code: str = "", language: str = "python") -> str:
    """
    Generate code suggestions using OpenAI's API.

    Args:
        prompt: Natural language description of the desired code or improvement.
        code: Optional existing code snippet to be improved or extended.
        language: Programming language (default: "python").

    Returns:
        Suggested code or explanation.
    """
    try:
        import openai

        # Prepare messages
        messages = []
        if code:
            messages.append(
                {
                    "role": "user",
                    "content": f"Here is my {language} code:\n```{language}\n{code}\n```\n{prompt}",
                }
            )
        else:
            messages.append({"role": "user", "content": prompt})

        # Call OpenAI API
        response = openai.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=messages,  # type: ignore
            temperature=0.7,
            max_tokens=1000,
        )
        suggestion = response.choices[0].message.content
        return f"## AI Suggestion\n\n{suggestion}"
    except Exception as e:
        return f"Error generating AI suggestion: {str(e)}"


@mcp.tool()
def analyze_dependencies(project_path: str = ".") -> str:
    """
    Analyze Python dependencies in a project.

    Args:
        project_path: Path to the project root (default current directory).

    Returns:
        Markdown report of dependencies and their status.
    """
    import subprocess
    from pathlib import Path

    p = Path(project_path).expanduser().resolve()
    if not p.exists():
        return f"Error: Path not found: {project_path}"

    # Look for dependency files
    requirements_file = p / "requirements.txt"
    pyproject_file = p / "pyproject.toml"
    pipfile = p / "Pipfile"
    has_deps = False
    report = []

    # Read requirements.txt
    if requirements_file.exists():
        has_deps = True
        content = requirements_file.read_text(encoding="utf-8", errors="replace")
        lines = [line.strip() for line in content.splitlines() if line.strip()]
        report.append("### requirements.txt")
        for line in lines:
            report.append(f"- `{line}`")

    # Read pyproject.toml (simple extraction)
    if pyproject_file.exists():
        has_deps = True
        import tomli

        try:
            data = tomli.loads(pyproject_file.read_text(encoding="utf-8"))
            deps = data.get("tool", {}).get("poetry", {}).get("dependencies", {})
            if deps:
                report.append("### pyproject.toml (Poetry dependencies)")
                for name, spec in deps.items():
                    if isinstance(spec, str):
                        report.append(f"- `{name} = {spec}`")
                    else:
                        report.append(f"- `{name} = {spec.get('version', '?')}`")
        except Exception as e:
            report.append(f"Note: Could not parse pyproject.toml: {e}")

    # Check outdated packages (optional)
    try:
        result = subprocess.run(
            ["pip", "list", "--outdated", "--format=json"],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            import json

            outdated = json.loads(result.stdout)
            if outdated:
                report.append("### Outdated Packages")
                for pkg in outdated:
                    report.append(
                        f"- `{pkg['name']}`: {pkg['version']} -> {pkg['latest_version']}"
                    )
            else:
                report.append("### All packages are up‑to‑date.")
        else:
            report.append("### Unable to check outdated packages.")
    except Exception as e:
        report.append(f"### Outdated check failed: {e}")

    if not has_deps:
        return "No dependency files found (requirements.txt, pyproject.toml, Pipfile)."

    return "\n".join(report)


@mcp.tool()
def refactor_rename(
    file_path: str, old_name: str, new_name: str, line_number: Optional[int] = None
) -> str:
    """
    Rename a variable, function, class, or method in a Python file.

    Args:
        file_path: Absolute path to the file.
        old_name: The identifier to rename.
        new_name: The new identifier.
        line_number: Optional line number where the identifier appears (to disambiguate).
                     If not provided, renames all occurrences in the file (global rename).
    Returns:
        Success message or error description.
    """
    try:
        import ast
        from pathlib import Path

        p = Path(file_path).expanduser().resolve()
        if not p.exists():
            return f"Error: File not found: {file_path}"

        content = p.read_text(encoding="utf-8")
        tree = ast.parse(content, filename=str(p))

        # Find nodes to rename
        renamed = 0
        for node in ast.walk(tree):
            if isinstance(node, ast.Name) and node.id == old_name:
                # If line_number is given, check node location
                if line_number is not None:
                    if hasattr(node, "lineno") and node.lineno != line_number:
                        continue
                node.id = new_name
                renamed += 1

        if renamed == 0:
            return f"Error: No identifier '{old_name}' found" + (
                f" at line {line_number}." if line_number else "."
            )

        # Convert back to source
        try:
            new_content = ast.unparse(tree)
        except AttributeError:
            return "Error: ast.unparse not available (requires Python 3.9+)."

        p.write_text(new_content, encoding="utf-8")
        return f"Renamed {renamed} occurrence(s) of '{old_name}' to '{new_name}'."
    except Exception as e:
        return f"Error during rename: {str(e)}"


@mcp.tool()
def debug_insert_breakpoint(
    file_path: str, line_number: int, use_breakpoint: bool = True
) -> str:
    """
    Insert a breakpoint at a specific line in a Python file.

    Args:
        file_path: Absolute path to the file.
        line_number: Line number where to insert the breakpoint (1-based).
        use_breakpoint: If True, use `breakpoint()` (Python 3.7+). If False, use `import pdb; pdb.set_trace()`.
    Returns:
        Success message or error description.
    """
    try:
        from pathlib import Path

        p = Path(file_path).expanduser().resolve()
        if not p.exists():
            return f"Error: File not found: {file_path}"

        lines = p.read_text(encoding="utf-8").splitlines()
        if line_number < 1 or line_number > len(lines) + 1:
            return f"Error: line_number {line_number} out of range (file has {len(lines)} lines)."

        # Prepare breakpoint line
        if use_breakpoint:
            bp_line = "breakpoint()"
        else:
            bp_line = "import pdb; pdb.set_trace()"

        # Insert the breakpoint line (adjust for 0‑based index)
        lines.insert(line_number - 1, bp_line)
        new_content = "\n".join(lines)
        p.write_text(new_content, encoding="utf-8")
        return f"Inserted breakpoint at line {line_number}."
    except Exception as e:
        return f"Error inserting breakpoint: {str(e)}"


@mcp.tool()
def profile_python_file(file_path: str, sort_by: str = "time") -> str:
    """
    Profile a Python script using cProfile and return a summary.

    Args:
        file_path: Absolute path to the Python script.
        sort_by: Sorting criterion for profiling output (e.g., "time", "calls", "cumulative").

    Returns:
        Profiling report as a string.
    """
    try:
        import subprocess
        from pathlib import Path

        p = Path(file_path).expanduser().resolve()
        if not p.exists():
            return f"Error: File not found: {file_path}"

        # Run cProfile
        cmd = ["python", "-m", "cProfile", "-s", sort_by, str(p)]
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30,  # seconds
        )
        if result.returncode != 0:
            return f"Error running profiler: {result.stderr}"

        # Limit output length
        output = result.stdout
        if len(output) > 2000:
            output = output[:2000] + "\n... (output truncated)"

        return f"## Profiling Report for {p.name}\n\n```\n{output}\n```"
    except subprocess.TimeoutExpired:
        return "Error: Profiling timed out after 30 seconds."
    except Exception as e:
        return f"Error during profiling: {str(e)}"


@mcp.tool()
def detect_code_smells(
    file_path: str, cc_threshold: int = 10, loc_threshold: int = 50
) -> str:
    """
    Detect potential code smells in a Python file using radon metrics.

    Args:
        file_path: Absolute path to the Python file.
        cc_threshold: Cyclomatic complexity threshold (default 10).
        loc_threshold: Lines of code per function threshold (default 50).

    Returns:
        Markdown report listing functions that exceed thresholds.
    """
    try:
        from radon.complexity import cc_visit
        from radon.raw import analyze
    except ImportError:
        return "Error: radon library not installed. Install with 'pip install radon'."

    from pathlib import Path

    p = Path(file_path).expanduser().resolve()
    if not p.exists():
        return f"Error: File not found: {file_path}"
    if p.suffix != ".py":
        return "Error: Only Python files are supported."

    content = p.read_text(encoding="utf-8")
    # Raw metrics
    raw = analyze(content)
    # Cyclomatic complexity
    blocks = cc_visit(content)

    report = []
    report.append(f"# Code Smell Analysis for {p.name}")
    report.append(f"Cyclomatic complexity threshold: {cc_threshold}")
    report.append(f"Lines of code threshold: {loc_threshold}")
    report.append("")

    smells = []
    for block in blocks:
        if block.complexity > cc_threshold:
            smells.append((block.name, block.complexity, "high cyclomatic complexity"))
        # Estimate lines of code (endline - startline + 1)
        loc = block.endline - block.lineno + 1
        if loc > loc_threshold:
            smells.append((block.name, loc, "long function"))

    if not smells:
        report.append("✅ No code smells detected.")
    else:
        report.append("## Potential Code Smells")
        report.append("| Function | Value | Issue |")
        report.append("|----------|-------|-------|")
        for name, value, issue in smells:
            report.append(f"| {name} | {value} | {issue} |")

    return "\n".join(report)


@mcp.tool()
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
        return "\n".join(lines)
    except SyntaxError as e:
        return f"Syntax error in file: {e}"
    except Exception as e:
        return f"Error analyzing imports: {str(e)}"


@mcp.tool()
def remove_unused_imports(file_path: str) -> str:
    """
    Remove unused imports from a Python file.

    Args:
        file_path: Absolute path to the Python file.

    Returns:
        Summary of removed imports or success message.
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

        # Map each import node to its imported names
        import_info = []  # list of (node, names list)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                names = [alias.name for alias in node.names]
                import_info.append((node, names))
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    names = [alias.name for alias in node.names]
                    import_info.append((node, names))  # type: ignore
                else:
                    # from . import something
                    import_info.append((node, []))  # type: ignore

        # Collect used names
        used_names = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
                used_names.add(node.id)
        used_names -= set(dir(builtins))

        # Determine which import nodes to keep
        removed_names = []
        kept_nodes = []
        for node, names in import_info:
            # if any name is used, keep the whole import node
            if any(name in used_names for name in names):
                kept_nodes.append(node)
            else:
                removed_names.extend(names)

        if not removed_names:
            return "No unused imports found."

        # Create new module body filtering out removed nodes (top‑level only)
        new_body = []
        for item in tree.body:
            remove = False
            for node, names in import_info:
                if item is node and not any(name in used_names for name in names):
                    remove = True
                    break
            if not remove:
                new_body.append(item)

        new_tree = ast.Module(body=new_body, type_ignores=[])
        new_content = ast.unparse(new_tree)
        p.write_text(new_content)

        lines = ["## Removed Unused Imports", ""]
        for name in sorted(set(removed_names)):
            lines.append(f"- `{name}`")
        lines.append(f"\nFile updated successfully.")
        return "\n".join(lines)
    except SyntaxError as e:
        return f"Syntax error in file: {e}"
    except Exception as e:
        return f"Error analyzing imports: {str(e)}"


@mcp.tool()
def suggest_imports(file_path: str) -> str:
    """
    Detect missing imports in a Python file and suggest import statements.

    Args:
        file_path: Absolute path to the Python file.

    Returns:
        Markdown list of suggested imports or success message.
    """
    try:
        import ast
        import importlib.util
        import sys
        from pathlib import Path

        p = Path(file_path).expanduser().resolve()
        if not p.exists():
            return f"Error: File not found: {file_path}"
        if p.suffix != ".py":
            return "Error: Only Python files are supported."

        content = p.read_text(encoding="utf-8")
        tree = ast.parse(content)

        # Collect all names used in the code
        used_names = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
                used_names.add(node.id)

        # Remove builtins
        import builtins

        builtin_names = set(dir(builtins))
        used_names -= builtin_names

        # Remove names that are already imported
        imported_names = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imported_names.add(alias.name)
                    if alias.asname:
                        imported_names.add(alias.asname)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    for alias in node.names:
                        imported_names.add(alias.name)
                        if alias.asname:
                            imported_names.add(alias.asname)
        used_names -= imported_names

        if not used_names:
            return "No missing imports detected."

        # Try to find which names correspond to importable modules
        suggestions = []
        for name in sorted(used_names):
            # Check if it's a standard library module
            if hasattr(sys, "stdlib_module_names"):
                if name in sys.stdlib_module_names:
                    suggestions.append(f"import {name}")
                    continue
            # Try to find spec
            spec = importlib.util.find_spec(name)
            if spec is not None:
                suggestions.append(f"import {name}")
                continue
            # Could be from a submodule (e.g., pandas.DataFrame)
            # We'll skip for now

        if not suggestions:
            return "Could not find importable modules for the missing names."

        lines = ["## Suggested Imports", ""]
        lines.extend(f"- `{s}`" for s in suggestions)
        lines.append("\nAdd these import statements at the top of the file.")
        return "\n".join(lines)
    except SyntaxError as e:
        return f"Syntax error in file: {e}"
    except Exception as e:
        return f"Error analyzing imports: {str(e)}"


@mcp.tool()
def generate_unit_tests(file_path: str, function_name: Optional[str] = None) -> str:
    """
    Generate unit tests for functions in a Python file using OpenAI.

    Args:
        file_path: Path to the Python file.
        function_name: Optional specific function to generate tests for. If None, generate for all functions.

    Returns:
        Generated test code as a string.
    """
    try:
        import os
        from pathlib import Path

        import openai

        p = Path(file_path).expanduser().resolve()
        if not p.exists():
            return f"Error: File not found: {file_path}"
        if p.suffix != ".py":
            return "Error: Only Python files are supported."

        content = p.read_text(encoding="utf-8")
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            return "Error: OPENAI_API_KEY environment variable not set."

        # Prepare prompt
        prompt = f"Generate pytest unit tests for the following Python code:\n\n```python\n{content}\n```\n"
        if function_name:
            prompt += f"Focus on testing the function '{function_name}'.\n"
        prompt += "Provide only the test code, no explanations. Use pytest style."

        client = openai.OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful coding assistant that writes unit tests.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
            max_tokens=1000,
        )
        content = response.choices[0].message.content  # type: ignore
        if content is None:
            return "Error: No content generated."
        generated = content.strip()
        return f"Generated unit tests:\n```python\n{generated}\n```"
    except ImportError:
        return "Error: openai package not installed. Install with 'pip install openai'."
    except Exception as e:
        return f"Error generating unit tests: {str(e)}"


@mcp.tool()
def code_stats(file_path: str) -> str:
    """
    Compute basic statistics for a Python file.

    Args:
        file_path: Path to the Python file.

    Returns:
        Statistics as a formatted string.
    """
    try:
        import ast
        from pathlib import Path

        p = Path(file_path).expanduser().resolve()
        if not p.exists():
            return f"Error: File not found: {file_path}"
        if p.suffix != ".py":
            return "Error: Only Python files are supported."

        content = p.read_text(encoding="utf-8")
        lines = content.splitlines()
        line_count = len(lines)
        char_count = len(content)
        non_empty_lines = [line for line in lines if line.strip()]
        non_empty_count = len(non_empty_lines)

        # Parse AST
        tree = ast.parse(content)
        function_count = sum(
            1 for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)
        )
        class_count = sum(
            1 for node in ast.walk(tree) if isinstance(node, ast.ClassDef)
        )
        import_count = sum(
            1
            for node in ast.walk(tree)
            if isinstance(node, (ast.Import, ast.ImportFrom))
        )

        stats = f"Statistics for {file_path}:\n"
        stats += f"  Lines: {line_count} (non-empty: {non_empty_count})\n"
        stats += f"  Characters: {char_count}\n"
        stats += f"  Functions: {function_count}\n"
        stats += f"  Classes: {class_count}\n"
        stats += f"  Imports: {import_count}\n"
        return stats
    except Exception as e:
        return f"Error computing statistics: {str(e)}"


@mcp.tool()
def code_review(path: str) -> str:
    """
    Run static analysis tools (pylint, flake8, bandit) on a Python file or directory.

    Args:
        path: Absolute path to a Python file or directory.

    Returns:
        A summary report of issues found.
    """
    import subprocess
    import sys
    from pathlib import Path

    p = Path(path).expanduser().resolve()
    if not p.exists():
        return f"Error: Path not found: {path}"

    issues = []

    # Run pylint
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pylint", "--output-format=text", str(p)],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.stdout:
            issues.append("=== Pylint ===\n" + result.stdout.strip())
        if result.stderr:
            issues.append("Pylint stderr: " + result.stderr.strip())
    except subprocess.TimeoutExpired:
        issues.append("Pylint timed out.")
    except Exception as e:
        issues.append(f"Pylint error: {e}")

    # Run flake8
    try:
        result = subprocess.run(
            [sys.executable, "-m", "flake8", str(p)],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.stdout:
            issues.append("=== Flake8 ===\n" + result.stdout.strip())
        if result.stderr:
            issues.append("Flake8 stderr: " + result.stderr.strip())
    except subprocess.TimeoutExpired:
        issues.append("Flake8 timed out.")
    except Exception as e:
        issues.append(f"Flake8 error: {e}")

    # Run bandit
    try:
        result = subprocess.run(
            [sys.executable, "-m", "bandit", "-r", str(p), "-f", "txt"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.stdout:
            issues.append("=== Bandit ===\n" + result.stdout.strip())
        if result.stderr:
            issues.append("Bandit stderr: " + result.stderr.strip())
    except subprocess.TimeoutExpired:
        issues.append("Bandit timed out.")
    except Exception as e:
        issues.append(f"Bandit error: {e}")

    if not issues:
        return "No issues found or all tools failed."

    return "\n\n".join(issues)


@mcp.tool()
def security_scan(path: str) -> str:
    """
    Run security scanning with bandit on a Python file or directory.

    Args:
        path: Absolute path to a Python file or directory.

    Returns:
        Security issues found by bandit.
    """
    import subprocess
    import sys
    from pathlib import Path

    p = Path(path).expanduser().resolve()
    if not p.exists():
        return f"Error: Path not found: {path}"

    try:
        result = subprocess.run(
            [sys.executable, "-m", "bandit", "-r", str(p), "-f", "txt"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        output = []
        if result.stdout:
            output.append(result.stdout.strip())
        if result.stderr:
            output.append("Stderr: " + result.stderr.strip())
        if not output:
            output.append("No output from bandit.")
        return "\n".join(output)
    except subprocess.TimeoutExpired:
        return "Bandit timed out."
    except Exception as e:
        return f"Bandit error: {e}"


@mcp.tool()
def test_coverage(path: str) -> str:
    """
    Run test coverage analysis using coverage.py and pytest.

    Args:
        path: Absolute path to the project root directory.

    Returns:
        Coverage report summary.
    """
    import subprocess
    import sys
    from pathlib import Path

    p = Path(path).expanduser().resolve()
    if not p.exists():
        return f"Error: Path not found: {path}"
    if not p.is_dir():
        return "Error: Path must be a directory."

    # Run coverage
    try:
        # First, ensure coverage is installed
        import coverage
    except ImportError:
        return (
            "Error: coverage module not installed. Install with 'pip install coverage'."
        )

    # Run coverage run -m pytest
    try:
        result = subprocess.run(
            [sys.executable, "-m", "coverage", "run", "-m", "pytest"],
            cwd=str(p),
            capture_output=True,
            text=True,
            timeout=60,
        )
        if result.returncode != 0:
            # pytest may have failures, but coverage data may still be generated
            pass
    except subprocess.TimeoutExpired:
        return "Test execution timed out."

    # Generate coverage report
    try:
        report_result = subprocess.run(
            [sys.executable, "-m", "coverage", "report"],
            cwd=str(p),
            capture_output=True,
            text=True,
            timeout=30,
        )
        output = []
        if report_result.stdout:
            output.append(report_result.stdout.strip())
        if report_result.stderr:
            output.append("Stderr: " + report_result.stderr.strip())
        if not output:
            output.append("No coverage output.")
        return "\n".join(output)
    except subprocess.TimeoutExpired:
        return "Coverage report generation timed out."
    except Exception as e:
        return f"Coverage report error: {e}"


def _collect_used_names(tree: ast.AST) -> set[str]:
    """Collect all names used in the code (excluding builtins)."""
    import builtins

    used_names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
            used_names.add(node.id)
    # Remove builtins
    builtin_names = set(dir(builtins))
    used_names -= builtin_names
    return used_names


def _collect_imported_names(tree: ast.AST) -> set[str]:
    """Collect all names that are already imported."""
    imported_names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imported_names.add(alias.name)
                if alias.asname:
                    imported_names.add(alias.asname)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                for alias in node.names:
                    imported_names.add(alias.name)
                    if alias.asname:
                        imported_names.add(alias.asname)
    return imported_names


def _find_importable_modules(names: set[str]) -> list[str]:
    """Find which names correspond to importable modules."""
    import importlib.util
    import sys

    imports_to_add = []
    for name in sorted(names):
        # Check if it's a standard library module
        if hasattr(sys, "stdlib_module_names"):
            if name in sys.stdlib_module_names:
                imports_to_add.append(f"import {name}")
                continue
        # Try to find spec
        spec = importlib.util.find_spec(name)
        if spec is not None:
            imports_to_add.append(f"import {name}")
            continue
        # Could be from a submodule (e.g., pandas.DataFrame)
        # We'll skip for now
    return imports_to_add


def _determine_insertion_point(lines: list[str]) -> int:
    """Determine the line number where new imports should be inserted."""
    insert_line = 0
    in_docstring = False
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith('"""') or stripped.startswith("'''"):
            in_docstring = not in_docstring
            continue
        if not in_docstring and (
            stripped.startswith("import ") or stripped.startswith("from ")
        ):
            insert_line = i + 1  # insert after this line
        elif not in_docstring and stripped and not stripped.startswith("#"):
            # First non-import, non-comment, non-empty line
            if insert_line == 0:
                insert_line = i
            break
    # If no imports found, insert at line 0 (top of file)
    if insert_line == 0:
        insert_line = 0
    return insert_line


@mcp.tool()
def add_missing_imports(file_path: str) -> str:
    """
    Add missing imports to a Python file.

    Args:
        file_path: Absolute path to the Python file.

    Returns:
        Summary of imports added or error message.
    """
    try:
        import ast
        import sys
        from pathlib import Path

        p = Path(file_path).expanduser().resolve()
        if not p.exists():
            return f"Error: File not found: {file_path}"
        if p.suffix != ".py":
            return "Error: Only Python files are supported."

        content = p.read_text(encoding="utf-8")
        lines = content.splitlines()
        tree = ast.parse(content)

        used_names = _collect_used_names(tree)
        imported_names = _collect_imported_names(tree)
        missing_names = used_names - imported_names

        if not missing_names:
            return "No missing imports detected."

        imports_to_add = _find_importable_modules(missing_names)

        if not imports_to_add:
            return "Could not find importable modules for the missing names."

        insert_line = _determine_insertion_point(lines)

        # Insert imports
        for imp in reversed(imports_to_add):
            lines.insert(insert_line, imp)

        new_content = "\n".join(lines) + ("\n" if lines else "")
        p.write_text(new_content, encoding="utf-8")

        summary = f"Added {len(imports_to_add)} import(s):\n"
        for imp in imports_to_add:
            summary += f"- {imp}\n"
        return summary.strip()
    except SyntaxError as e:
        return f"Syntax error in file: {e}"
    except Exception as e:
        return f"Error adding imports: {str(e)}"


@mcp.tool()
def sort_imports(file_path: str) -> str:
    """
    Sort imports in a Python file using isort.

    Args:
        file_path: Absolute path to the Python file.

    Returns:
        Success message or error description.
    """
    try:
        import subprocess
        from pathlib import Path

        p = Path(file_path).expanduser().resolve()
        if not p.exists():
            return f"Error: File not found: {file_path}"
        if p.suffix != ".py":
            return "Error: Only Python files are supported."

        # Run isort
        result = subprocess.run(
            ["isort", str(p)],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode == 0:
            return f"Successfully sorted imports in {p.name} using isort."
        else:
            return f"isort failed:\nSTDOUT: {result.stdout}\nSTDERR: {result.stderr}"
    except subprocess.TimeoutExpired:
        return "Error: isort timed out."
    except FileNotFoundError:
        return "Error: isort not installed. Install with 'pip install isort'."
    except Exception as e:
        return f"Error sorting imports: {str(e)}"


@mcp.tool()
def format_with_ruff(file_path: str) -> str:
    """
    Format a Python file using ruff.

    Args:
        file_path: Absolute path to the Python file.

    Returns:
        Success message or error description.
    """
    try:
        import subprocess
        from pathlib import Path

        p = Path(file_path).expanduser().resolve()
        if not p.exists():
            return f"Error: File not found: {file_path}"
        if p.suffix != ".py":
            return "Error: Only Python files are supported."

        # Run ruff format
        result = subprocess.run(
            ["ruff", "format", str(p)],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode == 0:
            return f"Successfully formatted {p.name} using ruff."
        else:
            return (
                f"ruff format failed:\nSTDOUT: {result.stdout}\nSTDERR: {result.stderr}"
            )
    except subprocess.TimeoutExpired:
        return "Error: ruff timed out."
    except FileNotFoundError:
        return "Error: ruff not installed. Install with 'pip install ruff'."
    except Exception as e:
        return f"Error formatting with ruff: {str(e)}"


@mcp.tool()
def format_code(file_path: str, formatter: str = "", options: str = "") -> str:
    """
    Format a code file using an appropriate formatter based on file extension.

    Supported languages:
      - Python: uses black (default) or ruff (if formatter='ruff')
      - Rust: uses rustfmt
      - HTML/JavaScript/TypeScript: uses prettier (must be installed)
      - Others: attempts to use prettier if available.

    Args:
        file_path: Absolute path to the file.
        formatter: Optional specific formatter (black, ruff, rustfmt, prettier).
                   If empty, auto‑detect based on extension.
        options: Additional command‑line options passed to the formatter.

    Returns:
        Success message or error description.
    """
    import subprocess
    from pathlib import Path

    p = Path(file_path).expanduser().resolve()
    if not p.exists():
        return f"Error: File not found: {file_path}"
    if not p.is_file():
        return f"Error: Path is not a file: {file_path}"

    suffix = p.suffix.lower()
    # Determine formatter
    if formatter:
        fmt = formatter
    else:
        # Auto‑detect
        if suffix == ".py":
            fmt = "black"
        elif suffix == ".rs":
            fmt = "rustfmt"
        elif suffix in (".html", ".htm", ".js", ".ts", ".tsx", ".json", ".css"):
            fmt = "prettier"
        else:
            fmt = "prettier"  # fallback

    # Build command
    if fmt == "black":
        cmd = ["black", str(p)]
    elif fmt == "ruff":
        cmd = ["ruff", "format", str(p)]
    elif fmt == "rustfmt":
        cmd = ["rustfmt", str(p)]
    elif fmt == "prettier":
        cmd = ["prettier", "--write", str(p)]
    else:
        return f"Error: Unknown formatter '{fmt}'."

    if options:
        # Split options string into list (simple splitting by spaces, no quoting)
        cmd.extend(options.split())

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            return f"Successfully formatted {p.name} using {fmt}."
        else:
            return f"Formatter {fmt} failed:\nSTDOUT: {result.stdout}\nSTDERR: {result.stderr}"
    except subprocess.TimeoutExpired:
        return f"Error: {fmt} timed out."
    except FileNotFoundError:
        return f"Error: {fmt} not installed. Please install it and ensure it's in PATH."
    except Exception as e:
        return f"Error running {fmt}: {str(e)}"


@mcp.tool()
def list_functions(file_path: str) -> str:
    """
    List functions, classes, and other top-level definitions in a file.

    Supports Python, JavaScript, TypeScript, Java, and C++ files.

    Args:
        file_path: Absolute path to the file.

    Returns:
        Markdown list of definitions or error message.
    """
    from pathlib import Path

    p = Path(file_path).expanduser().resolve()
    if not p.exists():
        return f"Error: File not found: {file_path}"
    suffix = p.suffix.lower()

    analysis = ""
    if suffix == ".py":
        analysis = _analyze_python_file(p)
    elif suffix == ".js":
        analysis = _analyze_javascript_file(p)
    elif suffix in (".ts", ".tsx"):
        analysis = _analyze_typescript_file(p)
    elif suffix == ".java":
        analysis = _analyze_java_file(p)
    elif suffix in (".cpp", ".hpp", ".h", ".cc", ".cxx"):
        analysis = _analyze_cpp_file(p)
    elif suffix == ".rs":
        analysis = _analyze_rust_file(p)
    elif suffix == ".go":
        analysis = _analyze_go_file(p)
    else:
        return f"Error: Unsupported file type. Supported: .py, .js, .ts, .tsx, .java, .cpp, .hpp, .h, .cc, .cxx, .rs, .go"

    if not analysis or analysis.startswith("Error"):
        return f"No definitions found or error analyzing file: {analysis}"

    # Format nicely
    lines = analysis.split("\n")
    if lines:
        return (
            "## Definitions in "
            + p.name
            + "\n\n"
            + "\n".join(f"- {line}" for line in lines if line.strip())
        )
    else:
        return "No definitions found."


if __name__ == "__main__":
    mcp.run()
