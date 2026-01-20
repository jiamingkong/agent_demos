"""
Networking skill: Basic network diagnostics and utilities.
Uses standard command‑line tools (ping, traceroute, curl, etc.).
"""

import ipaddress
import json
import os
import socket
import subprocess
from typing import Optional

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("networking", log_level="ERROR")


@mcp.tool()
def ping_host(host: str, count: int = 4) -> str:
    """
    Ping a host and return the result.

    Args:
        host: Hostname or IP address.
        count: Number of ping packets (default 4).
    """
    try:
        # Use appropriate ping flags for OS
        if os.name == "nt":
            cmd = ["ping", "-n", str(count), host]
        else:
            cmd = ["ping", "-c", str(count), host]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            return result.stdout
        else:
            return f"Ping failed:\n{result.stderr}\n{result.stdout}"
    except subprocess.TimeoutExpired:
        return "Ping timed out."
    except Exception as e:
        return f"Error pinging host: {e}"


@mcp.tool()
def traceroute(host: str, max_hops: int = 30) -> str:
    """
    Perform a traceroute to a host.

    Args:
        host: Hostname or IP address.
        max_hops: Maximum number of hops (default 30).
    """
    try:
        if os.name == "nt":
            cmd = ["tracert", "-h", str(max_hops), host]
        else:
            cmd = ["traceroute", "-m", str(max_hops), host]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            return result.stdout
        else:
            return f"Traceroute failed:\n{result.stderr}\n{result.stdout}"
    except subprocess.TimeoutExpired:
        return "Traceroute timed out."
    except FileNotFoundError:
        return "Error: traceroute command not found. Install traceroute (Linux/macOS) or tracert (Windows)."
    except Exception as e:
        return f"Error during traceroute: {e}"


@mcp.tool()
def curl_url(url: str, method: str = "GET", headers: Optional[str] = None) -> str:
    """
    Fetch a URL using curl.

    Args:
        url: URL to fetch.
        method: HTTP method (GET, POST, etc.).
        headers: Optional JSON string of HTTP headers.
    """
    try:
        cmd = ["curl", "-X", method, "-s", "-i"]
        if headers:
            headers_dict = json.loads(headers)
            for k, v in headers_dict.items():
                cmd.extend(["-H", f"{k}: {v}"])
        cmd.append(url)
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        output = result.stdout
        if result.stderr:
            output += "\n" + result.stderr
        return output
    except FileNotFoundError:
        return "Error: curl command not found. Install curl."
    except Exception as e:
        return f"Error fetching URL: {e}"


@mcp.tool()
def resolve_dns(hostname: str, record_type: str = "A") -> str:
    """
    Resolve a DNS record.

    Args:
        hostname: Hostname to resolve.
        record_type: DNS record type (A, AAAA, CNAME, MX, TXT, etc.).
    """
    try:
        import dns.resolver
    except ImportError:
        return "Error: dnspython library not installed. Install with `pip install dnspython`."
    try:
        resolver = dns.resolver.Resolver()
        answers = resolver.resolve(hostname, record_type)
        records = [str(r) for r in answers]
        return json.dumps(records, indent=2)
    except dns.resolver.NoAnswer:
        return f"No {record_type} record found for {hostname}."
    except dns.resolver.NXDOMAIN:
        return f"Domain {hostname} does not exist."
    except Exception as e:
        return f"Error resolving DNS: {e}"


@mcp.tool()
def check_port(host: str, port: int, timeout: float = 5.0) -> str:
    """
    Check if a TCP port is open.

    Args:
        host: Hostname or IP address.
        port: Port number.
        timeout: Connection timeout in seconds.
    """
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return f"Port {port} on {host} is OPEN."
    except socket.timeout:
        return f"Port {port} on {host} timed out."
    except ConnectionRefusedError:
        return f"Port {port} on {host} is CLOSED (connection refused)."
    except Exception as e:
        return f"Error checking port: {e}"


@mcp.tool()
def ip_info(ip: str) -> str:
    """
    Get information about an IP address (network, version, etc.).

    Args:
        ip: IP address string.
    """
    try:
        ip_obj = ipaddress.ip_address(ip)
        info = {
            "version": ip_obj.version,
            "is_private": ip_obj.is_private,
            "is_multicast": ip_obj.is_multicast,
            "is_reserved": ip_obj.is_reserved,
            "exploded": ip_obj.exploded,
        }
        if ip_obj.version == 4:
            info["netmask"] = str(ipaddress.IPv4Network(f"{ip}/24").netmask)
        return json.dumps(info, indent=2)
    except ValueError:
        return f"Invalid IP address: {ip}"
    except Exception as e:
        return f"Error analyzing IP: {e}"


if __name__ == "__main__":
    mcp.run()
