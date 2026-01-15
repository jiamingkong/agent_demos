---
name: git
description: Git version control operations for repositories.
allowed-tools:
  - git_status
  - git_diff
  - git_add
  - git_commit
  - git_log
  - git_branch
  - git_checkout
  - git_pull
  - git_push
  - git_init
  - git_clone
  - git_remote
---

# Git Skill

This skill provides the agent with capabilities to interact with Git repositories for version control.

## Tools

### git_status
Show the working tree status.
- `repo_path`: Path to the Git repository (defaults to current directory).

### git_diff
Show changes between commits, commit and working tree, etc.
- `repo_path`: Path to the Git repository (defaults to current directory).
- `args`: Additional diff arguments (optional).

### git_add
Add file contents to the index.
- `repo_path`: Path to the Git repository (defaults to current directory).
- `pathspec`: Files to add (defaults to '.' for all).

### git_commit
Record changes to the repository.
- `repo_path`: Path to the Git repository (defaults to current directory).
- `message`: Commit message.

### git_log
Show commit logs.
- `repo_path`: Path to the Git repository (defaults to current directory).
- `args`: Additional log arguments (optional).

### git_branch
List, create, or delete branches.
- `repo_path`: Path to the Git repository (defaults to current directory).
- `action`: Branch action: 'list', 'create', 'delete', 'rename'.
- `branch_name`: Branch name for create/delete/rename.
- `new_name`: New branch name for rename.

### git_checkout
Switch branches or restore working tree files.
- `repo_path`: Path to the Git repository (defaults to current directory).
- `target`: Branch, commit, or file to checkout.

### git_pull
Fetch from and integrate with another repository or local branch.
- `repo_path`: Path to the Git repository (defaults to current directory).
- `remote`: Remote name (defaults to 'origin').
- `branch`: Branch name (defaults to current branch).

### git_push
Update remote refs along with associated objects.
- `repo_path`: Path to the Git repository (defaults to current directory).
- `remote`: Remote name (defaults to 'origin').
- `branch`: Branch name (defaults to current branch).

### git_init
Create an empty Git repository or reinitialize an existing one.
- `repo_path`: Path where to initialize repository.

### git_clone
Clone a repository into a new directory.
- `repository_url`: URL of the repository to clone.
- `destination`: Directory to clone into.

### git_remote
Manage set of tracked repositories.
- `repo_path`: Path to the Git repository (defaults to current directory).
- `action`: Remote action: 'list', 'add', 'remove', 'rename'.
- `name`: Remote name.
- `url`: Remote URL for add.
- `new_name`: New name for rename.
