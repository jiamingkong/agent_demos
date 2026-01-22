import json
import ssl
import urllib.parse
import urllib.request

import requests
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("web_fetch", log_level="ERROR")

# Context for SSL (ignore certificate verification errors for broader compatibility)
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE


@mcp.tool()
def read_url_jina(url: str) -> str:
    """
    Fetch the content of a URL using Jina Reader (r.jina.ai).
    This converts any web page into clean, LLM-friendly Markdown.

    Args:
        url: The target URL to read (must start with http/https).
    """
    if not url.startswith("http"):
        return "Error: URL must start with http:// or https://"

    # Jina Reader Endpoint
    jina_url = f"https://r.jina.ai/{url}"

    try:
        headers = {"User-Agent": "curl/7.68.0"}
        req = urllib.request.Request(jina_url, headers=headers)

        with urllib.request.urlopen(req, context=ctx, timeout=30) as response:
            content = response.read().decode("utf-8")
            return content

    except Exception as e:
        return f"Error fetching URL via Jina: {str(e)}"


@mcp.tool()
def search_web_jina(query: str) -> str:
    """
    Search the web using Jina Search (s.jina.ai).
    Returns a markdown summary of search results grounded in facts.

    Args:
        query: The search query.
    """
    safe_query = urllib.parse.quote(query)
    jina_url = f"https://s.jina.ai/{safe_query}"

    try:
        headers = {"User-Agent": "curl/7.68.0"}
        req = urllib.request.Request(jina_url, headers=headers)

        with urllib.request.urlopen(req, context=ctx, timeout=30) as response:
            content = response.read().decode("utf-8")
            return content

    except Exception as e:
        return f"Error searching via Jina: {str(e)}"


@mcp.tool()
def download_file(url: str, output_path: str, chunk_size: int = 8192) -> str:
    """
    Download a file from a URL to a local path with progress indication.

    Args:
        url: The URL of the file to download.
        output_path: Local file path to save the downloaded content.
        chunk_size: Size of chunks for streaming download (default 8192).

    Returns:
        Success message or error description.
    """
    try:
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()
        total_size = int(response.headers.get("content-length", 0))
        downloaded = 0
        with open(output_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=chunk_size):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
        return f"Download completed: {downloaded} bytes saved to {output_path}"
    except Exception as e:
        return f"Error downloading file: {str(e)}"


if __name__ == "__main__":
    mcp.run()
