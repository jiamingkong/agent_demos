import sys

sys.path.insert(0, "servers/coder")
from server import apply_edit_blocks

edits = '''<<<<<<< SEARCH
    return "\\n".join(report)


if __name__ == "__main__":
    mcp.run()
=======
    return "\\n".join(report)


@mcp.tool()
def generate_unit_tests(file_path: str, function_name: Optional[str] = None) -> str:
    """
    Generate unit tests for functions in a Python file using OpenAI.

    Args:
        file_path: Path to the Python file.
        function_name: Optional specific function to generate tests for. If None, generate for all functions.

    Returns:
        Generated test code as a string.
    """
    try:
        import os
        import openai
        from pathlib import Path

        p = Path(file_path).expanduser().resolve()
        if not p.exists():
            return f"Error: File not found: {file_path}"
        if p.suffix != ".py":
            return "Error: Only Python files are supported."

        content = p.read_text(encoding="utf-8")
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            return "Error: OPENAI_API_KEY environment variable not set."

        # Prepare prompt
        prompt = f"Generate pytest unit tests for the following Python code:\\n\\n```python\\n{content}\\n```\\n"
        if function_name:
            prompt += f"Focus on testing the function '{function_name}'.\\n"
        prompt += "Provide only the test code, no explanations. Use pytest style."

        client = openai.OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful coding assistant that writes unit tests."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
            max_tokens=1000,
        )
        generated = response.choices[0].message.content.strip()
        return f"Generated unit tests:\\n```python\\n{generated}\\n```"
    except ImportError:
        return "Error: openai package not installed. Install with 'pip install openai'."
    except Exception as e:
        return f"Error generating unit tests: {str(e)}"


if __name__ == "__main__":
    mcp.run()
>>>>>>> REPLACE'''

result = apply_edit_blocks("/Users/zdwalter/agent_ds/servers/coder/server.py", edits)
print(result)
