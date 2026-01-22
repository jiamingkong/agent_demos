---
name: coder
description: Coding assistant capabilities including file investigation, reading, searching, editing, and command execution.
allowed-tools:
  - investigate_and_save_report
  - read_code_file
  - search_in_files
  - search_in_files_advanced
  - edit_code_file
  - apply_edit_blocks
  - run_terminal_command
  - create_file
  - format_code_with_black
  - analyze_code_complexity
  - lint_python_file
  - generate_code
  - code_snippet_generate
  - code_completion
  - code_style_check
  - search_and_replace
  - git_status
  - git_diff
  - git_commit
  - git_log
  - type_check_with_mypy
  - lint_with_pylint
  - ai_suggest_code
  - analyze_dependencies
  - refactor_rename
  - debug_insert_breakpoint
  - profile_python_file
  - detect_code_smells
  - batch_format
  - extract_variable
  - find_references
  - auto_fix_lint_issues
  - find_unused_imports
  - remove_unused_imports
  - suggest_imports
  - generate_unit_tests
  - generate_docstring
  - code_stats
  - code_review
  - security_scan
  - add_missing_imports
  - test_coverage
  - sort_imports
  - format_with_ruff
  - format_code
  - extract_function
  - inline_variable
  - explain_code
  - translate_code
  - suggest_dependency_upgrades
  - list_functions
  - detect_duplicate_code
  - generate_api_docs
  - assess_code_quality
  - visualize_complexity
  - count_lines
---

# Coder Skill

This skill provides the agent with capabilities to act as a coding assistant, exploring projects, reading code, and making edits.

## Tools

### investigate_and_save_report
Investigates a folder structure and writes a markdown summary named ".test.Agent.md" in that folder.
Automatically analyzes Python, JavaScript, and TypeScript files to extract high-level structure.
- `folder_path`: The absolute path of the folder to investigate.

### read_code_file
Read a code file incrementally.
- `file_path`: Absolute path to the file.
- `start_line`: Starting line number (1-based, inclusive). Default is 1.
- `end_line`: Ending line number (1-based, inclusive). Default is -1 (end of file).

### search_in_files
Use grep to search for patterns in files within a directory.
- `folder_path`: The directory to search in.
- `pattern`: The text or regex pattern to search for.

### edit_code_file
Edit a code file by replacing an exact text block.
- `file_path`: Absolute path to the file.
- `old_string`: The exact string to find and replace.
- `new_string`: The string to replace it with.
- `dry_run`: If True, only preview changes without writing file (default: False).

### apply_edit_blocks
Apply multiple search/replace edits to a file in a single pass. This is PREFERRED over `edit_code_file` for complex changes.
- `file_path`: Absolute path to the file.
- `edits`: A string containing one or more edit blocks using the SEARCH/REPLACE format.
- `dry_run`: If True, only preview changes without writing file (default: False).

### create_file
Create a new file with optional content, overwrite existing file, or append.
- `file_path`: Absolute path to the file.
- `content`: Optional text content to write.
- `overwrite`: If True (default), overwrite existing file.
- `append`: If True, append content to existing file.

### run_terminal_command
Run terminal commands.
- `command`: The full shell command to execute.

### format_code_with_black
Format a Python file using Black code formatter.
- `file_path`: Absolute path to the Python file to format.

### analyze_code_complexity
Analyze code complexity of a Python file using Radon.
- `file_path`: Absolute path to the Python file to analyze.

### lint_python_file
Lint a Python file using flake8.
- `file_path`: Absolute path to the Python file to lint.

### search_in_files_advanced
Search for a pattern in files with advanced options.
- `folder_path`: The directory to search in.
- `pattern`: The text or regex pattern to search for.
- `ignore_case`: If True, perform case-insensitive search (default: False).
- `file_pattern`: File pattern to filter files (e.g., "*.py", "*.txt") (default: "*").
- `max_depth`: Maximum depth of directories to search (default: unlimited).

### generate_code
Generate code based on a natural language prompt using OpenAI.
- `prompt`: Natural language description of the code to generate.
- `language`: Programming language (default: "python").

### code_completion
Provide code completion suggestions based on identifiers in the file.
- `file_path`: Path to the source file.
- `prefix`: Optional prefix to filter suggestions.

### code_style_check
Check code style using black and isort.
- `file_path`: Path to the Python file.

### git_status
Show git status of a repository.
- `repo_path`: Path to the git repository (default current directory).

### git_diff
Show git diff of a repository or specific file.
- `repo_path`: Path to the git repository.
- `file_path`: Optional specific file to diff.

### git_commit
Commit changes in a git repository.
- `repo_path`: Path to the git repository.
- `message`: Commit message.
- `files`: List of files to commit (empty for all changes).

### git_log
Show git log.
- `repo_path`: Path to the git repository.
- `count`: Number of commits to show.

### type_check_with_mypy
Run mypy type checking on a Python file.
- `file_path`: Path to the Python file.

### lint_with_pylint
Run pylint on a Python file.
- `file_path`: Path to the Python file.

### ai_suggest_code
Generate code suggestions using OpenAI's API.
- `prompt`: Natural language description of the desired code or improvement.
- `code`: Optional existing code snippet to be improved or extended.
- `language`: Programming language (default: "python").

### analyze_dependencies
Analyze Python dependencies in a project.
- `project_path`: Path to the project root (default current directory).

### refactor_rename
Rename a variable, function, class, or method in a Python file.
- `file_path`: Absolute path to the file.
- `old_name`: The identifier to rename.
- `new_name`: The new identifier.
- `line_number`: Optional line number where the identifier appears (to disambiguate). If not provided, renames all occurrences in the file (global rename).

### debug_insert_breakpoint
Insert a breakpoint at a specific line in a Python file.
- `file_path`: Absolute path to the file.
- `line_number`: Line number where to insert the breakpoint (1-based).
- `use_breakpoint`: If True, use `breakpoint()` (Python 3.7+). If False, use `import pdb; pdb.set_trace()`.

### profile_python_file
Profile a Python script using cProfile and return a summary.
- `file_path`: Absolute path to the Python script.
- `sort_by`: Sorting criterion for profiling output (e.g., "time", "calls", "cumulative").

### detect_code_smells
Detect potential code smells in a Python file using radon metrics.
- `file_path`: Absolute path to the Python file.
- `cc_threshold`: Cyclomatic complexity threshold (default 10).
- `loc_threshold`: Lines of code per function threshold (default 50).


### find_unused_imports
Detect unused imports in a Python file using AST.
- `file_path`: Absolute path to the Python file.

### add_missing_imports
Add missing imports to a Python file.
- `file_path`: Absolute path to the Python file.

### batch_format
Format all Python files in a directory using Black.
- `directory`: Path to the directory containing Python files.
- `file_pattern`: File pattern to match (default "*.py").

### generate_unit_tests
Generate unit tests for functions in a Python file using OpenAI.
- `file_path`: Path to the Python file.
- `function_name`: Optional specific function to generate tests for. If None, generate for all functions.

### generate_docstring
Generate a docstring for a Python function or class using AI.
- `file_path`: Path to the Python file.
- `target_name`: Name of the function or class. If None, generate for all functions and classes.
- `style`: Docstring style ("google", "numpy", "sphinx").
- `dry_run`: If True, only return the generated docstring without modifying the file.

### code_stats
Compute basic statistics for a Python file.
- `file_path`: Path to the Python file.

### search_and_replace
Search and replace across multiple files using grep and sed, with optional dry-run and backup retention.
- `folder_path`: Directory to search in.
- `search_pattern`: Regex pattern to search for.
- `replace_pattern`: Replacement string (supports backreferences).
- `file_pattern`: File pattern to filter (default "*").
- `dry_run`: If True, only show which files would be changed.
- `keep_backup`: If True, keep backup files (.bak) after replacement.
- `max_files`: Maximum number of files to process (optional).

### code_review
Run static analysis tools (pylint, flake8, bandit) on a Python file or directory.
- `path`: Absolute path to a Python file or directory.
Returns a summary report of issues found.

### security_scan
Run security scanning with bandit on a Python file or directory.
- `path`: Absolute path to a Python file or directory.
Returns security issues found by bandit.

### test_coverage
Run test coverage analysis using coverage.py and pytest.
- `path`: Absolute path to the project root directory.
Returns coverage report summary.

### extract_function
Extract a block of code into a new function.
- `file_path`: Absolute path to the Python file.
- `start_line`: Starting line number (1-based, inclusive).
- `end_line`: Ending line number (1-based, inclusive).
- `new_function_name`: Name of the new function.
- `params`: Comma-separated list of parameter names (optional). If empty, attempt to infer.
- `return_var`: Name of variable to return (optional). If empty, no return statement.
Returns success message or error description.

### inline_variable
Inline a variable by replacing its usage with its assignment expression.
- `file_path`: Absolute path to the Python file.
- `variable_name`: Name of the variable to inline.
- `assignment_line`: Line number of the assignment statement (optional). If 0, the first assignment found in the file will be used.
Returns success message or error description.

### list_functions
List functions, classes, and other top-level definitions in a file. Supports Python, JavaScript, TypeScript, Java, and C++ files.
- `file_path`: Absolute path to the file.
Returns a markdown list of definitions or error message.

### explain_code
Generate a natural language explanation of the given code using AI.
- `file_path`: Optional path to a code file. If provided, code is read from file.
- `code`: Optional code string. If file_path is not provided, this code is used.
- `language`: Programming language of the code (default "python").
Returns explanation as a markdown string.

### translate_code
Translate code from one programming language to another using AI.
- `source_code`: Source code string (optional if file_path provided).
- `source_language`: Language of the source code (optional, can be auto-detected).
- `target_language`: Target programming language (required).
- `file_path`: Optional path to a source code file. If provided, source_code is read from file.
Returns translated code as a string.

### suggest_dependency_upgrades
Check for outdated Python dependencies and suggest upgrades.
- `project_path`: Path to the project root directory (default current directory).
Returns markdown table with current version, latest version, and upgrade recommendation.

### detect_duplicate_code
Detect duplicate code blocks within Python files in a directory.
- `folder_path`: Directory to scan.
- `file_pattern`: File pattern to match (default "*.py").
- `min_lines`: Minimum number of lines in a block to consider (default 5).
Returns markdown report of duplicate blocks.

### generate_api_docs
Generate API documentation for a Python file.
- `file_path`: Absolute path to the Python file.
Returns markdown documentation.

### extract_variable
Extract a block of code into a new variable.
- `file_path`: Absolute path to the Python file.
- `start_line`: Starting line number (1-based, inclusive).
- `end_line`: Ending line number (1-based, inclusive).
- `variable_name`: Name of the new variable.
- `type_hint`: Optional type hint for the variable (e.g., "List[int]").
Returns success message or error description.

### find_references
Find references to a symbol in a project.
- `project_path`: Root directory of the project.
- `symbol`: Symbol name to search for.
- `symbol_type`: Type of symbol ('function', 'class', 'variable', 'any').
- `file_pattern`: File pattern to search (default "*.py").
Returns markdown list of references with file paths and line numbers.

### auto_fix_lint_issues
Automatically fix lint issues using specified linter.
- `file_path`: Path to the file or directory to lint.
- `linter`: Linter to use ('ruff', 'black', 'isort').
- `apply_fix`: If True, apply fixes; otherwise, only report issues.
Returns summary of fixes applied or issues found.

### assess_code_quality
Assess the quality of a Python file by analyzing complexity, duplication,
static analysis issues, and security vulnerabilities.
- `file_path`: Absolute path to the Python file.
Returns a markdown report with metrics and suggestions.

### visualize_complexity
Visualize cyclomatic complexity of functions in a Python file.
- `file_path`: Absolute path to the Python file.
- `output_file`: Optional path to save the plot image (PNG). If empty, a temporary file will be created.
Returns success message with path to generated image, or error description.

## Usage Strategy: Reliable Code Editing

To edit files efficiently and correctly using `apply_edit_blocks`, follow this distinct workflow. This method prevents "SEARCH block not found" errors by ensuring you have the exact text.

### Standard Workflow

1. **Locate**: Read the file (`read_code_file`) to find the approximate location of the code you want to change.
2. **Extract Exact Context**:
   - Once you identify the lines (e.g., lines 10-15), use `sed` to extract exactly those lines.
   - Command: `sed -n '10,15p' <filename>`
   - This output provides the **perfect** text for your `SEARCH` block, guaranteeing a match.
3. **Apply Edit**:
   - Copy the output from step 2 into the `<<<<<<< SEARCH` block.
   - Write your new code in the `=======` ... `>>>>>>> REPLACE` block.
   - Call `apply_edit_blocks`.

### Rules for `apply_edit_blocks`

1. **SEARCH Blocks Must Be Exact**: The tool performs a string find. Any difference in whitespace or indentation will cause it to fail. Using `sed` or `cat` to get the raw text is safer than remembering it. Note: Avoid using `cat -a` on Windows or macOS, as the `-a` flag is not available. Use `sed` or plain `cat` instead.
2. **Use Sufficient Context**: Include 3-5 lines of context in your `SEARCH` block to ensure it is unique within the file.
3. **Multiple Edits**: You can pass multiple `SEARCH`/`REPLACE` blocks in one tool call to perform several edits at once.

### Example

**Goal**: Change a print statement on line 42.

1. **Check Content**:
   ```bash
   sed -n '40,45p' main.py
   ```
   *Output:*
   ```python
       if x > 0:
           print("Positive")
           return True
   ```

2. **Call Tool**:
   ```json
   {
     "file_path": "/abs/main.py",
     "edits": "<<<<<<< SEARCH\n    if x > 0:\n        print(\"Positive\")\n        return True\n=======\n    if x > 0:\n        print(\"Found positive value\")\n        return True\n>>>>>>> REPLACE"
   }
   ```
