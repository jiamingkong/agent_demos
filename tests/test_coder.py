"""Unit tests for coder server."""

import os
import sys
import tempfile
from pathlib import Path

# Add servers to path
sys.path.insert(0, str(Path(__file__).parent.parent / "servers"))

from coder.server import (
    _analyze_python_file,
    detect_code_smells,
    investigate_and_save_report,
)


def test_analyze_python_file():
    """Test parsing a Python file."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write('''"""Module docstring."""
CONST = 42

def foo():
    """Foo function."""
    pass

class MyClass:
    def method(self):
        pass
''')
        f.flush()
        try:
            result = _analyze_python_file(Path(f.name))
            assert "Docstring:" in result
            assert "Constant: CONST" in result
            assert "Function: foo" in result
            assert "Class: MyClass (method)" in result
        finally:
            os.unlink(f.name)


def test_investigate_and_save_report(tmp_path):
    """Test folder investigation."""
    # Create a dummy folder with a Python file
    sub = tmp_path / "subdir"
    sub.mkdir()
    (sub / "test.py").write_text('print("hello")')
    (tmp_path / "README.md").write_text("# Project")

    result = investigate_and_save_report(str(tmp_path))
    # Expect a success message
    assert "complete" in result.lower() or "saved" in result.lower()
    # Check that report file exists
    report = tmp_path / ".test.Agent.md"
    assert report.exists()
    content = report.read_text()
    assert "Project Context Report" in content


def test_detect_code_smells():
    """Test code smell detection."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write("""
def simple():
    pass

def complex_func():
    if True:
        if False:
            for i in range(10):
                while i:
                    i -= 1
    return 0

def long_func():
    # many lines
    a = 1
    a = 2
    a = 3
    a = 4
    a = 5
    a = 6
    a = 7
    a = 8
    a = 9
    a = 10
    a = 11
    a = 12
    a = 13
    a = 14
    a = 15
    a = 16
    a = 17
    a = 18
    a = 19
    a = 20
    return a
""")
        f.flush()
        try:
            result = detect_code_smells(f.name, cc_threshold=2, loc_threshold=15)
            # Should detect high complexity and long function
            assert "high cyclomatic complexity" in result
            assert "long function" in result
            # Ensure no error
            assert "Error" not in result
        finally:
            os.unlink(f.name)


def test_extract_function():
    """Test extracting a code block into a new function."""
    import tempfile
    import os
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent / "servers"))
    from coder.server import extract_function

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write("""def main():
    a = 5
    b = 3
    # block start
    x = a + b
    print(x)
    # block end
    return x
""")
        f.flush()
        try:
            result = extract_function(
                file_path=f.name,
                start_line=5,
                end_line=7,
                new_function_name="add",
                params="a,b",
                return_var="x"
            )
            assert "Successfully extracted" in result
            # Check file content
            with open(f.name, 'r') as rf:
                content = rf.read()
                assert "def add(a, b):" in content
                assert "x = add(a, b)" in content
        finally:
            os.unlink(f.name)
