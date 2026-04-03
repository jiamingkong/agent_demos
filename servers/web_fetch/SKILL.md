---
name: web-fetch
description: "Fetches web pages and searches the internet using Jina AI's LLM-friendly Reader and Search APIs, returning clean Markdown. Use when reading web page content, fetching URLs, searching the web, or retrieving online information."
allowed-tools: "read_url_jina, search_web_jina"
---

# Web Fetch

Accesses the internet through Jina AI's Reader and Search APIs, converting web content into clean Markdown suitable for LLM consumption.

## Workflow

1. **Fetch a known URL** — call `read_url_jina` to retrieve and convert a specific web page to Markdown.
2. **Search the web** — call `search_web_jina` with keywords to find relevant pages and get a Markdown summary of results.

## Tools

### read_url_jina

Fetches a web page and converts it into clean Markdown via `https://r.jina.ai`.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `url` | string | yes | The complete URL to fetch |

**Example:**
```json
{
  "url": "https://docs.python.org/3/library/asyncio.html"
}
```

Returns the page content as Markdown text.

### search_web_jina

Searches the internet and returns a Markdown summary of results via `https://s.jina.ai`.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `query` | string | yes | Search keywords |

**Example:**
```json
{
  "query": "Python asyncio best practices 2024"
}
```

Returns a Markdown-formatted summary of search results.
