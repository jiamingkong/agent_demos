---
name: template
description: Generate files from Jinja2 templates or simple string templates.
allowed-tools:
  - render_template
  - render_template_file
  - list_template_variables
  - generate_from_schema
---

# Template Skill

This skill enables the agent to generate text or files from templates, with support for multiple template engines.

## Prerequisites

- **Jinja2** library (optional, only required for the `jinja2` engine). Install with:
  ```bash
  pip install Jinja2
  ```
- For the `simple` and `python` engines, no extra libraries are needed (they use Python's standard library).

## Tools

### render_template
Render a template string with the provided data.

- `template`: Template string.
- `data`: JSON string of variables to substitute (must be a dictionary).
- `engine`: Template engine (`jinja2`, `simple`, or `python`).
  - `jinja2`: Full Jinja2 syntax (requires Jinja2 installed).
  - `simple`: Python's `string.Template` syntax (`$variable` or `${variable}`).
  - `python`: Python's `str.format()` syntax (`{variable}`).
- `output_file`: Optional path to write the rendered content. If omitted, the rendered text is returned.

### render_template_file
Same as `render_template`, but read the template from a file.

- `template_file`: Path to the template file.
- `data`: JSON string of variables.
- `engine`: Template engine.
- `output_file`: Optional output file.

### list_template_variables
Extract variable names from a template string.

- `template`: Template string.
- `engine`: Template engine.
Returns a JSON list of variable names that the template expects.

### generate_from_schema
Generate a file from a simple JSON schema using a built‑in template (or a custom template).

- `schema`: JSON schema describing the structure. Currently supports:
  - A list of field names, e.g., `["name", "age", "email"]`.
  - A JSON schema object with a `properties` object (field names are taken from the keys).
- `output_file`: Path where the generated file will be written.
- `template`: Optional custom template string. If not provided, a simple Python class is generated.

## Usage Example

1. **Render a Jinja2 template**:
   ```
   render_template(
       template="Hello {{ name }}! You have {{ count }} messages.",
       data='{"name": "Alice", "count": 5}',
       engine="jinja2"
   )
   ```
2. **Render a template from a file**:
   ```
   render_template_file(
       template_file="/path/to/template.j2",
       data='{"title": "Report", "items": [1,2,3]}',
       output_file="/path/to/output.txt"
   )
   ```
3. **List variables**:
   ```
   list_template_variables("{{ user }} has {{ count }} items.", engine="jinja2")
   ```
4. **Generate a Python class from a schema**:
   ```
   generate_from_schema(
       schema='["id", "name", "email"]',
       output_file="model.py"
   )
   ```
