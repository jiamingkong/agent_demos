import sys

sys.path.insert(0, "servers/coder")
from server import apply_edit_blocks

edits = """<<<<<<< SEARCH
            if search_block not in new_content:
                return f"Error applying Edit #{i}: SEARCH block not found in file. Ensure exact match including indentation and whitespace."
=======
            if search_block not in new_content:
                # Provide a snippet of the file content for debugging
                snippet = content[:500] + ("..." if len(content) > 500 else "")
                return f"Error applying Edit #{i}: SEARCH block not found in file. Ensure exact match including indentation and whitespace.\\n\\nFirst 500 characters of file:\\n```\\n{snippet}\\n```\\n\\nTip: Use the read_code_file tool to see the exact content."
>>>>>>> REPLACE"""

result = apply_edit_blocks("/Users/zdwalter/agent_ds/servers/coder/server.py", edits)
print(result)
