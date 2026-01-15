---
name: coder
description: Coding assistant capabilities including file investigation, reading, searching, editing, and command execution.
allowed-tools:
  - investigate_and_save_report
  - read_code_file
  - search_in_files
  - edit_code_file
  - apply_edit_blocks
  - run_terminal_command
  - create_file
---

# Coder Skill

This skill provides the agent with capabilities to act as a coding assistant, exploring projects, reading code, and making edits.

## Tools

### investigate_and_save_report
Investigates a folder structure and writes a markdown summary named ".test.Agent.md" in that folder.
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

### apply_edit_blocks
Apply multiple search/replace edits to a file in a single pass. This is PREFERRED over `edit_code_file` for complex changes.
- `file_path`: Absolute path to the file.
- `edits`: A string containing one or more edit blocks using the SEARCH/REPLACE format.

### create_file
Create a new file with optional content, overwrite existing file, or append.
- `file_path`: Absolute path to the file.
- `content`: Optional text content to write.
- `overwrite`: If True (default), overwrite existing file.
- `append`: If True, append content to existing file.

### run_terminal_command
Run terminal commands.
- `command`: The full shell command to execute.

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

