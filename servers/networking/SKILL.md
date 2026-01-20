---
name: networking
description: Basic network diagnostics and utilities (ping, traceroute, curl, DNS, port scanning).
allowed-tools:
  - ping_host
  - traceroute
  - curl_url
  - resolve_dns
  - check_port
  - ip_info
---

# Networking Skill

This skill provides tools for basic network diagnostics and operations.

## Prerequisites

- Standard command‑line tools available on the system:
  - `ping` (available on all OS)
  - `traceroute` (Linux/macOS) or `tracert` (Windows)
  - `curl` (optional but recommended)
- For DNS resolution, the `dnspython` library is required (optional). Install with:
  ```bash
  pip install dnspython
  ```
- Python's standard library (`socket`, `ipaddress`, `subprocess`) is used for other tools.

## Tools

### ping_host
Ping a hostname or IP address.
- `host`: Target hostname or IP address.
- `count`: Number of ping packets (default 4).
Returns the raw output of the ping command.

### traceroute
Perform a traceroute to a host.
- `host`: Target hostname or IP address.
- `max_hops`: Maximum number of hops (default 30).
Returns the raw output of the traceroute command. Note: the command name differs between OS (traceroute on Unix, tracert on Windows).

### curl_url
Fetch a URL using curl.
- `url`: URL to fetch.
- `method`: HTTP method (default GET).
- `headers`: Optional JSON string of HTTP headers (e.g., `{"User-Agent": "Agent"}`).
Returns the HTTP response headers and body.

### resolve_dns
Resolve a DNS record.
- `hostname`: Hostname to resolve.
- `record_type`: DNS record type (A, AAAA, CNAME, MX, TXT, etc., default A).
Requires the `dnspython` library. Returns a JSON list of resolved records.

### check_port
Check if a TCP port is open.
- `host`: Hostname or IP address.
- `port`: Port number.
- `timeout`: Connection timeout in seconds (default 5).
Returns a message indicating whether the port is open, closed, or timed out.

### ip_info
Get information about an IP address.
- `ip`: IP address string (IPv4 or IPv6).
Returns a JSON object with properties such as version, whether it is private, multicast, reserved, etc.

## Usage Example

1. **Ping a server**:
   ```
   ping_host("google.com", count=5)
   ```
2. **Traceroute**:
   ```
   traceroute("example.com", max_hops=20)
   ```
3. **Fetch a web page**:
   ```
   curl_url("https://httpbin.org/get", method="GET")
   ```
4. **Resolve DNS**:
   ```
   resolve_dns("google.com", "A")
   ```
5. **Check port**:
   ```
   check_port("scanme.nmap.org", 80)
   ```
6. **IP information**:
   ```
   ip_info("192.168.1.1")
   ```
