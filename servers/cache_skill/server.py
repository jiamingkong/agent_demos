"""
Cache skill: Redis operations.
Requires redis library.
"""

import json
import uuid
from typing import Dict, Optional

import redis
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("cache", log_level="ERROR")

# In‑memory store for Redis connections
_connections: Dict[str, redis.Redis] = {}


def _get_connection(connection_id: str) -> redis.Redis:
    """Retrieve a Redis connection by ID."""
    if connection_id not in _connections:
        raise ValueError(f"Connection {connection_id} not found.")
    return _connections[connection_id]


@mcp.tool()
def redis_connect(
    host: str = "localhost",
    port: int = 6379,
    db: int = 0,
    password: Optional[str] = None,
) -> str:
    """
    Connect to a Redis server.

    Args:
        host: Redis host.
        port: Redis port.
        db: Database number.
        password: Optional password.
    """
    try:
        conn = redis.Redis(
            host=host, port=port, db=db, password=password, decode_responses=True
        )
        # Test connection
        conn.ping()
        connection_id = str(uuid.uuid4())[:8]
        _connections[connection_id] = conn
        return f"Connected to Redis at {host}:{port} (db {db}). Connection ID: {connection_id}"
    except Exception as e:
        return f"Error connecting to Redis: {e}"


@mcp.tool()
def redis_set(
    connection_id: str, key: str, value: str, ttl: Optional[int] = None
) -> str:
    """
    Set a key‑value pair.

    Args:
        connection_id: Connection ID.
        key: Key name.
        value: String value.
        ttl: Optional expiration in seconds.
    """
    try:
        conn = _get_connection(connection_id)
        if ttl is not None:
            conn.setex(key, ttl, value)
        else:
            conn.set(key, value)
        return f"Set '{key}' -> '{value}'" + (f" with TTL {ttl}s." if ttl else ".")
    except Exception as e:
        return f"Error setting key: {e}"


@mcp.tool()
def redis_get(connection_id: str, key: str) -> str:
    """
    Get the value of a key.

    Args:
        connection_id: Connection ID.
        key: Key name.
    """
    try:
        conn = _get_connection(connection_id)
        value = conn.get(key)
        if value is None:
            return f"Key '{key}' does not exist."
        return f"'{key}' = '{value}'"
    except Exception as e:
        return f"Error getting key: {e}"


@mcp.tool()
def redis_delete(connection_id: str, key: str) -> str:
    """
    Delete a key.

    Args:
        connection_id: Connection ID.
        key: Key name.
    """
    try:
        conn = _get_connection(connection_id)
        deleted = conn.delete(key)
        if deleted:
            return f"Deleted key '{key}'."
        else:
            return f"Key '{key}' did not exist."
    except Exception as e:
        return f"Error deleting key: {e}"


@mcp.tool()
def redis_keys(connection_id: str, pattern: str = "*") -> str:
    """
    List keys matching a pattern.

    Args:
        connection_id: Connection ID.
        pattern: Pattern (default '*').
    """
    try:
        conn = _get_connection(connection_id)
        keys = conn.keys(pattern)
        if keys:
            return f"Keys matching '{pattern}':\n" + "\n".join(keys)
        else:
            return f"No keys matching '{pattern}'."
    except Exception as e:
        return f"Error listing keys: {e}"


@mcp.tool()
def redis_ping(connection_id: str) -> str:
    """
    Ping the Redis server.

    Args:
        connection_id: Connection ID.
    """
    try:
        conn = _get_connection(connection_id)
        result = conn.ping()
        return f"PONG – connection is alive."
    except Exception as e:
        return f"Error pinging Redis: {e}"
