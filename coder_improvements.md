# Coder Skill Improvements

## Applied Changes

1. **Enhanced `apply_edit_blocks` error messages**
   - When a SEARCH block is not found, the tool now shows the first 500 characters of the file to help debugging.
   - Added a tip to use `read_code_file` for exact content.

2. **Added new tool `generate_unit_tests`**
   - Generates pytest unit tests for a given Python file using OpenAI.
   - Optional `function_name` parameter to focus on a specific function.
   - Returns generated test code as a formatted Python block.

3. **Refactored `add_missing_imports` function**
   - Split into helper functions to reduce cyclomatic complexity.
   - Improved maintainability and readability.

4. **Added TypeScript file analysis**
   - New internal function `_analyze_typescript_file` extracts functions, classes, interfaces, types, and enums.
   - Integrated into `investigate_and_save_report` for automatic analysis of `.ts` and `.tsx` files.

5. **Added `sort_imports` tool**
   - Sorts imports in a Python file using isort (if installed).
   - Provides clear error messages if isort is missing.

6. **Added `format_with_ruff` tool**
   - Formats a Python file using ruff formatter (if installed).
   - Alternative to Black for faster formatting.

7. **Added `extract_function` tool**
   - Extracts a block of code into a new function.
   - Supports explicit parameter and return variable specification.
   - Useful for refactoring.

8. **Added `inline_variable` tool**
   - Inlines a variable by replacing its usage with its assignment expression.
   - Supports optional line number to disambiguate assignments.
   - Useful for refactoring.

## Future Improvements (Suggested)

- Add `find_unused_imports` tool (using vulture or static analysis).
- Add `auto_import` tool to add missing imports.
- Improve `search_and_replace` with backup creation.
- Support for more languages (TypeScript, Java, C++).
- Add `code_review` tool using AI.

## Testing

All existing tests pass.

## Usage

To use the new tool, load the coder skill and call `generate_unit_tests` with a file path.

Example:
```python
generate_unit_tests("/path/to/file.py", "my_function")
```

## New Improvements (2026-01-21)

1. **Added `explain_code` tool**
   - Uses OpenAI to generate natural language explanation of a code block or file.
   - Parameters: `file_path` (optional), `code` (optional), `language` (default python).
   - Returns markdown explanation.

2. **Added `translate_code` tool**
   - Translates code between programming languages using AI.
   - Parameters: `source_code`, `source_language`, `target_language`, `file_path`.
   - Returns translated code with syntax highlighting.

3. **Added `suggest_dependency_upgrades` tool**
   - Checks for outdated Python dependencies in requirements.txt or pyproject.toml.
   - Uses pip index or PyPI API to fetch latest versions.
   - Returns markdown table with upgrade recommendations.

4. **Added `detect_duplicate_code` tool**
   - Detects duplicate code blocks within Python files in a directory.
   - Parameters: `folder_path`, `file_pattern` (default "*.py"), `min_lines` (default 5).
   - Returns markdown report of duplicate blocks.

5. **Added `generate_api_docs` tool**
   - Generates API documentation for a Python file.
   - Parameters: `file_path`.
   - Returns markdown documentation.

## Notes

The improvements are already applied to the source code. The skill needs to be reloaded for the changes to take effect (or restart the agent).
