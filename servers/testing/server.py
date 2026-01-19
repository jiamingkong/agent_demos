import os
import subprocess
import sys
from pathlib import Path

from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("testing", log_level="ERROR")

# Project root (assuming server runs from project root)
PROJECT_ROOT = Path(__file__).parent.parent.parent


@mcp.tool()
def run_pytest(args: str = "") -> str:
    """
    Run pytest with optional arguments.

    Args:
        args: Optional arguments to pass to pytest (e.g., "-v", "tests/test_agent.py").
    """
    try:
        cmd = ["python", "-m", "pytest"]
        if args:
            # Split arguments safely
            import shlex

            cmd.extend(shlex.split(args))

        # Run in project root
        result = subprocess.run(
            cmd, cwd=PROJECT_ROOT, capture_output=True, text=True, timeout=30
        )

        output = f"Exit code: {result.returncode}\n"
        if result.stdout:
            output += "STDOUT:\n" + result.stdout
        if result.stderr:
            output += "STDERR:\n" + result.stderr

        return output
    except subprocess.TimeoutExpired:
        return "Pytest timed out after 30 seconds."
    except Exception as e:
        return f"Error running pytest: {e}"


@mcp.tool()
def list_test_files() -> str:
    """
    List all test files in the project.
    """
    try:
        test_files = []
        for root, dirs, files in os.walk(PROJECT_ROOT / "tests"):
            for file in files:
                if file.endswith(".py") and file.startswith("test_"):
                    rel_path = os.path.relpath(os.path.join(root, file), PROJECT_ROOT)
                    test_files.append(rel_path)

        if not test_files:
            return "No test files found."

        return "Test files:\n" + "\n".join(f"- {f}" for f in sorted(test_files))
    except Exception as e:
        return f"Error listing test files: {e}"


@mcp.tool()
def run_test_file(file_path: str) -> str:
    """
    Run tests in a specific file.

    Args:
        file_path: Path to the test file (relative to project root).
    """
    try:
        # Ensure path is within project
        full_path = (PROJECT_ROOT / file_path).resolve()
        if not full_path.is_file():
            return f"File not found: {file_path}"

        cmd = ["python", "-m", "pytest", str(full_path), "-v"]

        result = subprocess.run(
            cmd, cwd=PROJECT_ROOT, capture_output=True, text=True, timeout=30
        )

        output = f"Exit code: {result.returncode}\n"
        if result.stdout:
            output += "STDOUT:\n" + result.stdout
        if result.stderr:
            output += "STDERR:\n" + result.stderr

        return output
    except subprocess.TimeoutExpired:
        return "Test timed out after 30 seconds."
    except Exception as e:
        return f"Error running test file: {e}"


@mcp.tool()
def get_test_coverage(path: str = ".") -> str:
    """
    Generate and display test coverage report (requires pytest-cov).

    Args:
        path: Optional path to measure coverage for (default is project root).
    """
    try:
        cmd = ["python", "-m", "pytest", "--cov=" + path, "--cov-report=term"]

        result = subprocess.run(
            cmd, cwd=PROJECT_ROOT, capture_output=True, text=True, timeout=60
        )

        output = f"Exit code: {result.returncode}\n"
        if result.stdout:
            output += "STDOUT:\n" + result.stdout
        if result.stderr:
            output += "STDERR:\n" + result.stderr

        # If coverage not installed, suggest installation
        if (
            "No module named pytest_cov" in result.stderr
            or "error: unrecognized arguments: --cov" in result.stderr
        ):
            output += (
                "\nNote: pytest-cov not installed. Install with: pip install pytest-cov"
            )

        return output
    except subprocess.TimeoutExpired:
        return "Coverage generation timed out after 60 seconds."
    except Exception as e:
        return f"Error generating coverage: {e}"


if __name__ == "__main__":
    mcp.run()
