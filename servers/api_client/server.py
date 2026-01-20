from mcp.server.fastmcp import FastMCP
import requests
import json

mcp = FastMCP("api_client", log_level="ERROR")

def _parse_optional_json(json_str: str):
    """Parse JSON string, return None if empty or invalid."""
    if not json_str:
        return None
    try:
        return json.loads(json_str)
    except json.JSONDecodeError:
        raise ValueError("Invalid JSON string")

def _make_request(method, url, headers=None, data=None, json_data=None):
    """Internal request helper."""
    try:
        parsed_headers = _parse_optional_json(headers) if headers else None
        parsed_data = _parse_optional_json(data) if data else None
        parsed_json = _parse_optional_json(json_data) if json_data else None
        response = requests.request(
            method=method,
            url=url,
            headers=parsed_headers,
            data=parsed_data,
            json=parsed_json,
            timeout=30
        )
        # Build result dict
        result = {
            "status_code": response.status_code,
            "headers": dict(response.headers),
            "text": response.text,
            "url": response.url
        }
        try:
            result["json"] = response.json()
        except:
            pass
        return json.dumps(result, indent=2)
    except requests.exceptions.Timeout:
        return json.dumps({"error": "Request timeout"})
    except requests.exceptions.ConnectionError:
        return json.dumps({"error": "Connection error"})
    except Exception as e:
        return json.dumps({"error": str(e)})

@mcp.tool()
def http_get(url: str, headers: str = None, params: str = None) -> str:
    """
    Perform an HTTP GET request.

    Args:
        url: The URL to request.
        headers: Optional HTTP headers (JSON string).
        params: Optional query parameters (JSON string).
    """
    parsed_params = _parse_optional_json(params) if params else None
    try:
        parsed_headers = _parse_optional_json(headers) if headers else None
        response = requests.get(url, headers=parsed_headers, params=parsed_params, timeout=30)
        result = {
            "status_code": response.status_code,
            "headers": dict(response.headers),
            "text": response.text,
            "url": response.url
        }
        try:
            result["json"] = response.json()
        except:
            pass
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})

@mcp.tool()
def http_post(url: str, headers: str = None, data: str = None, json_body: str = None) -> str:
    """
    Perform an HTTP POST request.

    Args:
        url: The URL to request.
        headers: Optional HTTP headers (JSON string).
        data: Optional request body data (JSON string).
        json: Optional JSON data (JSON string). If both data and json are provided, json takes precedence.
    """
    return _make_request("POST", url, headers, data, json_body)

@mcp.tool()
def http_put(url: str, headers: str = None, data: str = None, json_body: str = None) -> str:
    """
    Perform an HTTP PUT request.

    Args:
        url: The URL to request.
        headers: Optional HTTP headers (JSON string).
        data: Optional request body data (JSON string).
        json: Optional JSON data (JSON string). If both data and json are provided, json takes precedence.
    """
    return _make_request("PUT", url, headers, data, json_body)

@mcp.tool()
def http_delete(url: str, headers: str = None) -> str:
    """
    Perform an HTTP DELETE request.

    Args:
        url: The URL to request.
        headers: Optional HTTP headers (JSON string).
    """
    return _make_request("DELETE", url, headers, None, None)

@mcp.tool()
def http_request(method: str, url: str, headers: str = None, data: str = None, json_body: str = None) -> str:
    """
    Perform a custom HTTP request with any method.

    Args:
        method: HTTP method (e.g., GET, POST, PUT, DELETE, PATCH, HEAD, OPTIONS).
        url: The URL to request.
        headers: Optional HTTP headers (JSON string).
        data: Optional request body data (JSON string).
        json: Optional JSON data (JSON string).
    """
    return _make_request(method, url, headers, data, json_body)

if __name__ == "__main__":
    mcp.run()
