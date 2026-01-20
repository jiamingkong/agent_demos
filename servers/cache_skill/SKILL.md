---
name: cache
description: Redis cache operations.
allowed-tools:
  - redis_connect
  - redis_set
  - redis_get
  - redis_delete
  - redis_keys
  - redis_ping
---

# Cache Skill

This skill enables the agent to interact with a Redis server for caching and key‑value storage.

## Prerequisites

- Redis server running locally or reachable via network.
- The `redis` Python package (install via `pip install redis`).

## Tools

### redis_connect
Establish a connection to a Redis server.
- `host`: Redis host (default "localhost").
- `port`: Redis port (default 6379).
- `db`: Database number (default 0).
- `password`: Optional password.

Returns a connection ID that must be used in subsequent calls.

### redis_set
Set a key‑value pair, optionally with a TTL (expiration in seconds).
- `connection_id`: Connection ID returned by `redis_connect`.
- `key`: Key name.
- `value`: String value.
- `ttl`: Optional time‑to‑live in seconds.

### redis_get
Retrieve the value of a key.
- `connection_id`: Connection ID.
- `key`: Key name.

### redis_delete
Delete a key.
- `connection_id`: Connection ID.
- `key`: Key name.

### redis_keys
List keys matching a pattern (use `*` for all keys).
- `connection_id`: Connection ID.
- `pattern`: Pattern (default "*").

### redis_ping
Test the connection.
- `connection_id`: Connection ID.
