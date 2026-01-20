"""
Template skill: Generate files from Jinja2 templates or simple string templates.
Requires Jinja2 library (optional, install via `pip install Jinja2`).
"""

import json
import os
import string
from pathlib import Path
from typing import Any, Dict, Optional

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("template", log_level="ERROR")

# Try to import Jinja2
try:
    from jinja2 import Template as JinjaTemplate

    _JINJA_AVAILABLE = True
except ImportError:
    _JINJA_AVAILABLE = False


@mcp.tool()
def render_template(
    template: str,
    data: str,
    engine: str = "jinja2",
    output_file: Optional[str] = None,
) -> str:
    """
    Render a template with the provided data.

    Args:
        template: Template string.
        data: JSON string of variables to substitute.
        engine: Template engine ('jinja2', 'simple', or 'python').
        output_file: If provided, write rendered content to this file.
    """
    try:
        variables = json.loads(data)
        if not isinstance(variables, dict):
            return "Error: data must be a JSON object (dictionary)."
        rendered = ""
        if engine == "jinja2":
            if not _JINJA_AVAILABLE:
                return "Error: Jinja2 not installed. Install with `pip install Jinja2` or use engine='simple'."
            jinja_template = JinjaTemplate(template)
            rendered = jinja_template.render(**variables)
        elif engine == "simple":
            # Simple placeholders like {key}
            t = string.Template(template)
            # Convert variables to strings
            vars_str = {k: str(v) for k, v in variables.items()}
            rendered = t.safe_substitute(**vars_str)
        elif engine == "python":
            # Python's str.format()
            rendered = template.format(**variables)
        else:
            return f"Error: unknown engine '{engine}'. Use 'jinja2', 'simple', or 'python'."

        if output_file:
            out_path = Path(output_file).resolve()
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_text(rendered, encoding="utf-8")
            return f"Rendered content written to {output_file}"
        else:
            return rendered
    except Exception as e:
        return f"Error rendering template: {e}"


@mcp.tool()
def render_template_file(
    template_file: str,
    data: str,
    engine: str = "jinja2",
    output_file: Optional[str] = None,
) -> str:
    """
    Render a template from a file.

    Args:
        template_file: Path to the template file.
        data: JSON string of variables to substitute.
        engine: Template engine ('jinja2', 'simple', or 'python').
        output_file: If provided, write rendered content to this file.
    """
    try:
        template_path = Path(template_file)
        if not template_path.exists():
            return f"Error: template file '{template_file}' does not exist."
        template_content = template_path.read_text(encoding="utf-8")
        return render_template(template_content, data, engine, output_file)
    except Exception as e:
        return f"Error reading template file: {e}"


@mcp.tool()
def list_template_variables(template: str, engine: str = "jinja2") -> str:
    """
    Extract variable names from a template.

    Args:
        template: Template string.
        engine: Template engine ('jinja2', 'simple', or 'python').
    """
    try:
        variables = []
        if engine == "jinja2":
            if not _JINJA_AVAILABLE:
                return "Error: Jinja2 not installed. Install with `pip install Jinja2`."
            jinja_template = JinjaTemplate(template)
            # Accessing undocumented attribute; fallback to parsing
            # Instead we'll use a simple regex approach (limited).
            import re

            # Find {{ ... }} and {% ... %}
            pattern = r"\{\{.*?\}\}|\{% .*? %\}"
            matches = re.findall(pattern, template)
            # Extract variable names from {{ var }} (simplistic)
            var_set = set()
            for m in matches:
                if m.startswith("{{"):
                    inner = m[2:-2].strip()
                    # Remove filters
                    if "|" in inner:
                        inner = inner.split("|")[0].strip()
                    var_set.add(inner)
            variables = list(var_set)
        elif engine == "simple":
            import string

            t = string.Template(template)
            variables = list(t.get_identifiers())
        elif engine == "python":
            import string

            formatter = string.Formatter()
            variables = [
                field_name
                for _, field_name, _, _ in formatter.parse(template)
                if field_name
            ]
        else:
            return f"Error: unknown engine '{engine}'."
        return json.dumps(variables, indent=2)
    except Exception as e:
        return f"Error extracting variables: {e}"


@mcp.tool()
def generate_from_schema(
    schema: str,
    output_file: str,
    template: Optional[str] = None,
) -> str:
    """
    Generate a file from a JSON schema using a built‑in template.

    Args:
        schema: JSON schema describing the structure (currently only supports list of field names).
        output_file: Path where the generated file will be written.
        template: Optional custom template string. If not provided, a simple Python class is generated.
    """
    try:
        schema_data = json.loads(schema)
        # For simplicity, assume schema is a list of field names
        if isinstance(schema_data, list):
            fields = schema_data
        elif isinstance(schema_data, dict) and "properties" in schema_data:
            fields = list(schema_data["properties"].keys())
        else:
            return "Error: schema must be a list of field names or a JSON schema with 'properties'."

        if template is None:
            # Default template: Python class
            template_lines = ["class GeneratedClass:", "    def __init__(self):"]
            for field in fields:
                template_lines.append(f"        self.{field} = None")
            template_content = "\n".join(template_lines)
        else:
            template_content = template

        data = {"fields": fields}
        return render_template(
            template_content, json.dumps(data), engine="simple", output_file=output_file
        )
    except Exception as e:
        return f"Error generating from schema: {e}"


if __name__ == "__main__":
    mcp.run()
