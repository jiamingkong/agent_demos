---
name: office_reader
description: Office document reading capabilities using the markitdown library.
allowed-tools:
  - read_office_file
  - list_supported_formats
---

# Office Reader Skill

This skill enables the agent to read office documents (PDF, DOCX, PPTX, XLSX, etc.) and convert them to Markdown using the markitdown library.

## Tools

### read_office_file
Convert an office/document file to Markdown.
- `file_path`: Absolute path to the file.

### list_supported_formats
List the supported file extensions for office/document conversion.
- No parameters.