---
name: api_client
description: General-purpose HTTP API client for making requests (GET, POST, PUT, DELETE, etc.).
allowed-tools:
  - http_get
  - http_post
  - http_put
  - http_delete
  - http_request
---

# API Client Skill

This skill enables the agent to interact with RESTful APIs using HTTP methods.

## Tools

### http_get
Perform an HTTP GET request.
- `url`: The URL to request.
- `headers`: Optional HTTP headers (JSON string).
- `params`: Optional query parameters (JSON string).

### http_post
Perform an HTTP POST request.
- `url`: The URL to request.
- `headers`: Optional HTTP headers (JSON string).
- `data`: Optional request body data (JSON string).
- `json`: Optional JSON data (JSON string). If both data and json are provided, json takes precedence.

### http_put
Perform an HTTP PUT request.
- `url`: The URL to request.
- `headers`: Optional HTTP headers (JSON string).
- `data`: Optional request body data (JSON string).
- `json`: Optional JSON data (JSON string). If both data and json are provided, json takes precedence.

### http_delete
Perform an HTTP DELETE request.
- `url`: The URL to request.
- `headers`: Optional HTTP headers (JSON string).

### http_request
Perform a custom HTTP request with any method.
- `method`: HTTP method (e.g., GET, POST, PUT, DELETE, PATCH, HEAD, OPTIONS).
- `url`: The URL to request.
- `headers`: Optional HTTP headers (JSON string).
- `data`: Optional request body data (JSON string).
- `json`: Optional JSON data (JSON string).
