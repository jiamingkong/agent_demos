import sys

sys.path.insert(0, "/Users/zdwalter/agent_ds/servers/coder")
import os
import tempfile

from server import code_review, security_scan, test_coverage

# Create a temporary Python file with some issues
with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
    f.write('def foo():\n    x = 1\n    y = 2\n    print("hello")\n')
    temp_path = f.name

try:
    print("Testing code_review...")
    result = code_review(temp_path)
    print(result[:500])
    print("\nTesting security_scan...")
    result2 = security_scan(temp_path)
    print(result2[:500])
finally:
    os.unlink(temp_path)

print("\nTesting test_coverage on current directory...")
result3 = test_coverage("/Users/zdwalter/agent_ds/test_coder")
print(result3[:500])
