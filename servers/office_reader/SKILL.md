---
name: office-reader
description: "Converts office documents (PDF, DOCX, PPTX, XLSX, CSV, HTML, images, audio) to clean Markdown using the markitdown library. Use when reading or extracting content from office files, converting documents to Markdown, processing spreadsheets, or listing supported document formats."
allowed-tools: "read_office_file, list_supported_formats"
---

# Office Reader

Converts office and document files into clean Markdown text using the `markitdown` library, enabling the agent to read and reason over diverse file formats.

## Workflow

1. **Check supported formats** — call `list_supported_formats` to confirm the target file type is supported before attempting conversion.
2. **Convert document** — call `read_office_file` with the absolute path to produce a Markdown representation of the file contents.
3. **Process output** — use the returned Markdown for summarization, extraction, or downstream analysis.

## Tools

### read_office_file

Converts an office or document file to Markdown.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `file_path` | string | yes | Absolute path to the document file |

**Example:**
```json
{
  "file_path": "/home/user/reports/quarterly.xlsx"
}
```

Returns the document content as Markdown text.

### list_supported_formats

Lists all file extensions supported for document-to-Markdown conversion.

- Takes no parameters.
- Returns a list of supported extensions (e.g., `.pdf`, `.docx`, `.pptx`, `.xlsx`, `.csv`, `.html`).