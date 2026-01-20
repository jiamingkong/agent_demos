---
name: websocket_skill
description: WebSocket client and server capabilities for real‑time communication.
tools:
  - websocket_connect
  - websocket_send
  - websocket_receive
  - websocket_close
  - websocket_server_start
  - websocket_server_stop
---

# WebSocket Skill

This skill enables the agent to interact with WebSocket servers (client side) and to host simple WebSocket servers.

## Prerequisites

- `websockets` library (install via `pip install websockets`)

## Tools

### websocket_connect
Establish a WebSocket connection to a remote server.

Args:
- `uri`: WebSocket URI (e.g., "ws://echo.websocket.org").
- `timeout`: Connection timeout in seconds (default 10).

Returns a connection ID that can be used in subsequent send/receive operations.

### websocket_send
Send a text message over an established WebSocket connection.

Args:
- `connection_id`: ID of the connection returned by `websocket_connect`.
- `message`: Text message to send.

### websocket_receive
Receive a message from a WebSocket connection (blocks until a message arrives or timeout).

Args:
- `connection_id`: ID of the connection.
- `timeout`: Receive timeout in seconds (default 10).

Returns the received message.

### websocket_close
Close a WebSocket connection.

Args:
- `connection_id`: ID of the connection.

### websocket_server_start
Start a simple WebSocket server that echoes received messages.

Args:
- `host`: Bind address (default "localhost").
- `port`: Bind port (default 8765).
- `path`: Optional path (default "/").

Returns a server ID that can be used to stop the server later.

### websocket_server_stop
Stop a running WebSocket server.

Args:
- `server_id`: ID of the server.

## Notes

- The skill maintains a dictionary of active connections and servers.
- For simplicity, the echo server only logs connections and echoes messages.
- More advanced server behavior can be added in future versions.
