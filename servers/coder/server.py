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
    other_files_summary = []

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
    report_content.append("## 2. Python Code High-Level Overview")
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
    report_content.append("## 4. Configuration & Documentation (Preview)")
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
def apply_edit_blocks(file_path: str, edits: str) -> str:
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
        generated = response.choices[0].message.content.strip()
        return f"Generated code ({language}):\n```{language}\n{generated}\n```"
    except ImportError:
        return "Error: openai package not installed. Install with 'pip install openai'."
    except Exception as e:
        return f"Error generating code: {str(e)}"


@mcp.tool()
def search_and_replace(
    folder_path: str, search_pattern: str, replace_pattern: str, file_pattern: str = "*"
) -> str:
    """
    Search and replace across multiple files using grep and sed.

    Args:
        folder_path: Directory to search in.
        search_pattern: Regex pattern to search for.
        replace_pattern: Replacement string (supports backreferences).
        file_pattern: File pattern to filter (default "*").

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

        # Use find + xargs + sed -i
        find_cmd = ["find", str(p), "-type", "f", "-name", file_pattern]
        # Exclude binary files
        find_cmd.extend(["!", "-exec", "file", "{}", ";", "|", "grep", "-q", "binary"])
        # Combine with xargs sed
        # We'll use a simpler approach: loop over files
        # For safety, we'll do a dry-run first
        result = subprocess.run(
            ["grep", "-r", "-l", search_pattern, str(p)],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0 and result.returncode != 1:
            return f"Grep failed: {result.stderr}"
        files = result.stdout.strip().split("\n")
        files = [f for f in files if f]
        if not files:
            return "No files matched the search pattern."

        # Perform replacement
        replaced_count = 0
        for file in files:
            # Use sed -i.bak for backup (macOS syntax)
            subprocess.run(
                ["sed", "-i.bak", f"s/{search_pattern}/{replace_pattern}/g", file],
                check=False,
            )
            # Remove backup
            backup = file + ".bak"
            if os.path.exists(backup):
                os.remove(backup)
            replaced_count += 1

        return f"Replaced pattern '{search_pattern}' with '{replace_pattern}' in {replaced_count} files."
    except Exception as e:
        return f"Error in search_and_replace: {str(e)}"


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
            messages=messages,
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
        generated = response.choices[0].message.content.strip()
        return f"Generated unit tests:\n```python\n{generated}\n```"
    except ImportError:
        return "Error: openai package not installed. Install with 'pip install openai'."
    except Exception as e:
        return f"Error generating unit tests: {str(e)}"


if __name__ == "__main__":
    mcp.run()
