from mcp.server.fastmcp import FastMCP
import urllib.request
import urllib.parse
import json
import ssl

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
    if not url.startswith('http'):
        return "Error: URL must start with http:// or https://"
    
    # Jina Reader Endpoint
    jina_url = f"https://r.jina.ai/{url}"
    
    try:
        headers = {
            'User-Agent': 'curl/7.68.0' 
        }
        req = urllib.request.Request(jina_url, headers=headers)
        
        with urllib.request.urlopen(req, context=ctx, timeout=30) as response:
            content = response.read().decode('utf-8')
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
        headers = {
            'User-Agent': 'curl/7.68.0'
        }
        req = urllib.request.Request(jina_url, headers=headers)
        
        with urllib.request.urlopen(req, context=ctx, timeout=30) as response:
            content = response.read().decode('utf-8')
            return content
            
    except Exception as e:
        return f"Error searching via Jina: {str(e)}"

if __name__ == "__main__":
    mcp.run()
