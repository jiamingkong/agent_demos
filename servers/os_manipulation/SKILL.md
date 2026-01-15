---
name: os_manipulation
description: Operating System file manipulation capabilities (list, bulk create, bulk move, regex move).
allowed-tools:
  - list_directory
  - create_directories
  - move_files
  - move_files_by_regex
---

# OS Manipulation Skill

This skill allows the agent to interact with the file system.

## Tools

### list_directory
List contents of a directory.
- `path`: Absolute path to the directory.

### create_directories
Create multiple directories at once.
- `paths`: List of absolute paths to create.

### move_files
Move multiple files to a specific destination directory.
- `sources`: List of source file paths to move.
- `destination`: Destination directory path.

### move_files_by_regex
Move files matching a regex pattern from source directory to destination.
- `source_dir`: Directory to search files in.
- `destination`: Destination directory.
- `pattern`: Python regex pattern to match filenames.
