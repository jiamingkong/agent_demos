import sys

sys.path.insert(0, ".")

from server import ai_suggest_code, analyze_dependencies

# Test analyze_dependencies
print("Testing analyze_dependencies...")
result = analyze_dependencies(".")
print(result)

# Test ai_suggest_code (requires OpenAI API key)
print("\nTesting ai_suggest_code...")
try:
    result = ai_suggest_code("Write a function that adds two numbers in Python")
    print(result)
except Exception as e:
    print(f"Error: {e}")
