import os
import shlex
import subprocess
from pathlib import Path
from typing import Optional

from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("git", log_level="ERROR")


def run_git_command(repo_path: str, args: list, timeout: int = 30) -> str:
    """
    Run a git command in the specified repository directory.
    Returns combined stdout/stderr.
    """
    try:
        # Resolve path
        path = Path(repo_path).expanduser().resolve()
        if not path.exists():
            return f"Error: Repository path does not exist: {repo_path}"

        # Check if it's a git repository (except for git init and git clone)
        if not args[0] in ["init", "clone"]:
            git_dir = path / ".git"
            if not git_dir.exists():
                # Check if path itself is a .git directory
                if path.name == ".git" and path.is_dir():
                    pass
                else:
                    return f"Error: Not a git repository: {repo_path}"

        # Run git command
        result = subprocess.run(
            ["git"] + args,
            cwd=str(path),
            capture_output=True,
            text=True,
            timeout=timeout,
        )

        output = []
        if result.stdout:
            output.append(result.stdout)
        if result.stderr:
            output.append(result.stderr)

        # Include exit code if non-zero
        if result.returncode != 0:
            output.append(f"\nExit code: {result.returncode}")

        return "\n".join(output).strip()

    except subprocess.TimeoutExpired:
        return f"Error: Git command timed out after {timeout} seconds."
    except Exception as e:
        return f"Error executing git command: {str(e)}"


@mcp.tool()
def git_status(repo_path: str = ".") -> str:
    """
    Show the working tree status.

    Args:
        repo_path: Path to the Git repository (defaults to current directory).
    """
    return run_git_command(repo_path, ["status"])


@mcp.tool()
def git_diff(repo_path: str = ".", args: str = "") -> str:
    """
    Show changes between commits, commit and working tree, etc.

    Args:
        repo_path: Path to the Git repository (defaults to current directory).
        args: Additional diff arguments (optional).
    """
    git_args = ["diff"]
    if args:
        # Split args string into list, handling quotes properly
        git_args.extend(shlex.split(args))
    return run_git_command(repo_path, git_args)


@mcp.tool()
def git_add(repo_path: str = ".", pathspec: str = ".") -> str:
    """
    Add file contents to the index.

    Args:
        repo_path: Path to the Git repository (defaults to current directory).
        pathspec: Files to add (defaults to '.' for all).
    """
    return run_git_command(repo_path, ["add", pathspec])


@mcp.tool()
def git_commit(repo_path: str = ".", message: str = "") -> str:
    """
    Record changes to the repository.

    Args:
        repo_path: Path to the Git repository (defaults to current directory).
        message: Commit message.
    """
    if not message:
        return "Error: Commit message is required."
    return run_git_command(repo_path, ["commit", "-m", message])


@mcp.tool()
def git_log(repo_path: str = ".", args: str = "") -> str:
    """
    Show commit logs.

    Args:
        repo_path: Path to the Git repository (defaults to current directory).
        args: Additional log arguments (optional).
    """
    git_args = ["log"]
    if args:
        git_args.extend(shlex.split(args))
    else:
        git_args.extend(["--oneline", "-n", "20"])  # Default to brief log
    return run_git_command(repo_path, git_args)


@mcp.tool()
def git_branch(
    repo_path: str = ".",
    action: str = "list",
    branch_name: str = "",
    new_name: str = "",
) -> str:
    """
    List, create, or delete branches.

    Args:
        repo_path: Path to the Git repository (defaults to current directory).
        action: Branch action: 'list', 'create', 'delete', 'rename'.
        branch_name: Branch name for create/delete/rename.
        new_name: New branch name for rename.
    """
    if action == "list":
        return run_git_command(repo_path, ["branch", "-v"])
    elif action == "create":
        if not branch_name:
            return "Error: branch_name is required for create action."
        return run_git_command(repo_path, ["branch", branch_name])
    elif action == "delete":
        if not branch_name:
            return "Error: branch_name is required for delete action."
        return run_git_command(repo_path, ["branch", "-d", branch_name])
    elif action == "rename":
        if not branch_name or not new_name:
            return "Error: branch_name and new_name are required for rename action."
        return run_git_command(repo_path, ["branch", "-m", branch_name, new_name])
    else:
        return f"Error: Unknown action '{action}'. Use 'list', 'create', 'delete', or 'rename'."


@mcp.tool()
def git_checkout(repo_path: str = ".", target: str = "") -> str:
    """
    Switch branches or restore working tree files.

    Args:
        repo_path: Path to the Git repository (defaults to current directory).
        target: Branch, commit, or file to checkout.
    """
    if not target:
        return "Error: target is required (branch, commit, or file)."
    return run_git_command(repo_path, ["checkout", target])


@mcp.tool()
def git_pull(repo_path: str = ".", remote: str = "origin", branch: str = "") -> str:
    """
    Fetch from and integrate with another repository or local branch.

    Args:
        repo_path: Path to the Git repository (defaults to current directory).
        remote: Remote name (defaults to 'origin').
        branch: Branch name (defaults to current branch).
    """
    args = ["pull", remote]
    if branch:
        args.append(branch)
    return run_git_command(repo_path, args)


@mcp.tool()
def git_push(repo_path: str = ".", remote: str = "origin", branch: str = "") -> str:
    """
    Update remote refs along with associated objects.

    Args:
        repo_path: Path to the Git repository (defaults to current directory).
        remote: Remote name (defaults to 'origin').
        branch: Branch name (defaults to current branch).
    """
    args = ["push", remote]
    if branch:
        args.append(branch)
    return run_git_command(repo_path, args)


@mcp.tool()
def git_init(repo_path: str = ".") -> str:
    """
    Create an empty Git repository or reinitialize an existing one.

    Args:
        repo_path: Path where to initialize repository.
    """
    return run_git_command(repo_path, ["init"])


@mcp.tool()
def git_clone(repository_url: str, destination: str = "") -> str:
    """
    Clone a repository into a new directory.

    Args:
        repository_url: URL of the repository to clone.
        destination: Directory to clone into.
    """
    try:
        # If destination is empty, clone to default location
        args = ["clone", repository_url]
        if destination:
            args.append(destination)

        # Clone doesn't have a repo_path, run in current directory
        result = subprocess.run(
            ["git"] + args, capture_output=True, text=True, timeout=60
        )

        output = []
        if result.stdout:
            output.append(result.stdout)
        if result.stderr:
            output.append(result.stderr)

        if result.returncode != 0:
            output.append(f"\nExit code: {result.returncode}")

        return "\n".join(output).strip()

    except subprocess.TimeoutExpired:
        return "Error: Clone operation timed out."
    except Exception as e:
        return f"Error executing git clone: {str(e)}"


@mcp.tool()
def git_remote(
    repo_path: str = ".",
    action: str = "list",
    name: str = "",
    url: str = "",
    new_name: str = "",
) -> str:
    """
    Manage set of tracked repositories.

    Args:
        repo_path: Path to the Git repository (defaults to current directory).
        action: Remote action: 'list', 'add', 'remove', 'rename'.
        name: Remote name.
        url: Remote URL for add.
        new_name: New name for rename.
    """
    if action == "list":
        return run_git_command(repo_path, ["remote", "-v"])
    elif action == "add":
        if not name or not url:
            return "Error: name and url are required for add action."
        return run_git_command(repo_path, ["remote", "add", name, url])
    elif action == "remove":
        if not name:
            return "Error: name is required for remove action."
        return run_git_command(repo_path, ["remote", "remove", name])
    elif action == "rename":
        if not name or not new_name:
            return "Error: name and new_name are required for rename action."
        return run_git_command(repo_path, ["remote", "rename", name, new_name])
    else:
        return f"Error: Unknown action '{action}'. Use 'list', 'add', 'remove', or 'rename'."


if __name__ == "__main__":
    mcp.run()
