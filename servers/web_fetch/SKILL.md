---
name: web_fetch
description: Web retrieval capabilities using Jina AI's Reader and Search APIs, plus generic file download.
allowed-tools:
  - read_url_jina
  - search_web_jina
  - download_file
---

# Web Fetch Skill

This skill empowers the agent to access the internet using Jina AI's LLM-friendly APIs and download files.

## Tools

### read_url_jina
Fetches a webpage and converts it into clean Markdown using `https://r.jina.ai`.
- `url`: The complete URL to fetch.

### search_web_jina
Searches the internet and provides a Markdown summary of results using `https://s.jina.ai`.
- `query`: The search keywords.

### download_file
Download a file from a URL to a local path with progress indication.
- `url`: The URL of the file to download.
- `output_path`: Local file path to save the downloaded content.
- `chunk_size`: Size of chunks for streaming download (default 8192).
