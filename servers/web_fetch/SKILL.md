---
name: web_fetch
description: Web retrieval capabilities using Jina AI's Reader and Search APIs.
allowed-tools:
  - read_url_jina
  - search_web_jina
---

# Web Fetch Skill

This skill empowers the agent to access the internet using Jina AI's LLM-friendly APIs.

## Tools

### read_url_jina
Fetches a webpage and converts it into clean Markdown using `https://r.jina.ai`.
- `url`: The complete URL to fetch.

### search_web_jina
Searches the internet and provides a Markdown summary of results using `https://s.jina.ai`.
- `query`: The search keywords.
