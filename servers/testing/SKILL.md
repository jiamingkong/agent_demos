---
name: testing
description: Testing capabilities including running pytest, listing tests, and generating coverage reports.
allowed-tools:
  - run_pytest
  - list_test_files
  - run_test_file
  - get_test_coverage
---

# Testing Skill

This skill provides the agent with capabilities to run and manage tests for the project.

## Tools

### run_pytest
Run pytest with optional arguments.
- `args`: Optional arguments to pass to pytest (e.g., "-v", "tests/test_agent.py").

### list_test_files
List all test files in the project.

### run_test_file
Run tests in a specific file.
- `file_path`: Path to the test file (relative to project root).

### get_test_coverage
Generate and display test coverage report (requires pytest-cov).
- `path`: Optional path to measure coverage for (default is project root).

## Usage

The testing skill enables the agent to:
- Run the full test suite
- Execute specific test files
- Discover available tests
- Monitor test coverage

This is particularly useful for continuous integration scenarios and ensuring code quality during development.