---
name: os-manipulation
description: "File system operations including directory listing, bulk directory creation, batch file moves, and regex-based file moves. Use when organizing files, creating folder structures, moving files in bulk, or renaming files by pattern."
allowed-tools: "list_directory, create_directories, move_files, move_files_by_regex"
---

# OS Manipulation

Provides file system operations for listing, creating, and moving files and directories in bulk.

## Workflow

1. **Survey** — call `list_directory` to inspect the current file layout before making changes.
2. **Prepare structure** — call `create_directories` to set up any needed destination folders.
3. **Move files** — use `move_files` for explicit file lists or `move_files_by_regex` when a filename pattern selects the right files.

## Tools

### list_directory

Lists the contents of a directory.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `path` | string | yes | Absolute path to the directory |

### create_directories

Creates multiple directories at once (including intermediate parents).

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `paths` | list[string] | yes | Absolute paths of directories to create |

**Example:**
```json
{
  "paths": ["/home/user/project/src", "/home/user/project/tests"]
}
```

### move_files

Moves multiple files to a destination directory.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `sources` | list[string] | yes | Source file paths to move |
| `destination` | string | yes | Destination directory path |

### move_files_by_regex

Moves files whose names match a Python regex pattern from a source directory to a destination.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `source_dir` | string | yes | Directory to search for matching files |
| `destination` | string | yes | Destination directory path |
| `pattern` | string | yes | Python regex pattern to match filenames |

**Example:**
```json
{
  "source_dir": "/home/user/downloads",
  "destination": "/home/user/documents/pdfs",
  "pattern": ".*\\.pdf$"
}
```
