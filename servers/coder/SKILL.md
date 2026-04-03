---
name: coder
description: "Coding assistant with tools for project investigation, incremental file reading, grep-based search, exact-match code editing, multi-block batch edits, file creation, and terminal command execution. Use when exploring codebases, reading source files, searching for patterns, editing code, creating files, or running shell commands."
allowed-tools: "investigate_and_save_report, read_code_file, search_in_files, edit_code_file, apply_edit_blocks, run_terminal_command, create_file"
---

# Coder

Provides coding assistant capabilities for exploring projects, reading code, making precise edits, and executing commands.

## Workflow

1. **Investigate** — call `investigate_and_save_report` on a folder to generate a structural overview (`.test.Agent.md`).
2. **Read** — call `read_code_file` to inspect specific file sections by line range.
3. **Search** — call `search_in_files` to grep for patterns across a directory.
4. **Edit** — use `apply_edit_blocks` (preferred for multi-part changes) or `edit_code_file` (single replacement) to modify code. Always read the file first to get exact text for SEARCH blocks.
5. **Create** — call `create_file` to write new files or append to existing ones.
6. **Execute** — call `run_terminal_command` to run shell commands.

## Tools

### investigate_and_save_report

Investigates a folder structure and writes a Markdown summary (`.test.Agent.md`) in that folder.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `folder_path` | string | yes | Absolute path of the folder to investigate |

### read_code_file

Reads a code file incrementally by line range.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `file_path` | string | yes | Absolute path to the file |
| `start_line` | integer | no | Starting line number, 1-based (default: 1) |
| `end_line` | integer | no | Ending line number, 1-based (default: -1 for end of file) |

### search_in_files

Searches for text or regex patterns in files within a directory using grep.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `folder_path` | string | yes | Directory to search in |
| `pattern` | string | yes | Text or regex pattern to search for |

### edit_code_file

Replaces an exact text block in a file. Use `apply_edit_blocks` instead for multiple changes.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `file_path` | string | yes | Absolute path to the file |
| `old_string` | string | yes | Exact string to find |
| `new_string` | string | yes | Replacement string |

### apply_edit_blocks

Applies multiple search/replace edits to a file in a single pass. **Preferred over `edit_code_file`** for complex or multi-part changes.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `file_path` | string | yes | Absolute path to the file |
| `edits` | string | yes | One or more edit blocks in SEARCH/REPLACE format |

**Edit block format:**
```
<<<<<<< SEARCH
exact text to find (use sed to extract exact lines)
=======
replacement text
>>>>>>> REPLACE
```

**Rules:**
- SEARCH blocks must match the file content exactly (whitespace-sensitive). Use `sed -n '10,15p' <file>` to extract exact text.
- Include 3–5 lines of surrounding context for unique matching.
- Multiple SEARCH/REPLACE blocks can appear in a single `edits` string.

**Example — change a print statement on line 42:**

```bash
# Step 1: Extract exact text
sed -n '40,45p' main.py
```

```json
{
  "file_path": "/abs/main.py",
  "edits": "<<<<<<< SEARCH\n    if x > 0:\n        print(\"Positive\")\n        return True\n=======\n    if x > 0:\n        print(\"Found positive value\")\n        return True\n>>>>>>> REPLACE"
}
```

### create_file

Creates a new file with optional content, or overwrites/appends to an existing file.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `file_path` | string | yes | Absolute path to the file |
| `content` | string | no | Text content to write |
| `overwrite` | boolean | no | Overwrite existing file (default: true) |
| `append` | boolean | no | Append content to existing file |

### run_terminal_command

Executes a shell command and returns the output.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `command` | string | yes | Full shell command to execute |

