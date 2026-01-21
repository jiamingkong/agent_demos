import sys

sys.path.insert(0, ".")

import os
# Create a temporary file
import tempfile

from server import inline_variable

with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
    f.write("""
def foo():
    x = 5 + 3
    y = x * 2
    print(y)
""")
    fpath = f.name

try:
    result = inline_variable(fpath, "x", 2)
    print(result)
    # read file back
    with open(fpath, "r") as f:
        print("=== New content ===")
        print(f.read())
except Exception as e:
    print(f"Error: {e}")
finally:
    os.unlink(fpath)
