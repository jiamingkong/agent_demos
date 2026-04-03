---
name: sys-admin
description: "System administration tools for querying local OS information and managing persistent SSH connections to remote servers. Use when checking system details, connecting to remote hosts via SSH, running remote commands, or managing SSH sessions."
allowed-tools: "get_system_info, ssh_connect, ssh_run_command, ssh_list_connections, ssh_disconnect"
---

# Sys Admin

Inspects the local system environment and manages persistent SSH connections to remote servers using ControlMaster-based sessions.

## Workflow

1. **Inspect local system** — call `get_system_info` to retrieve OS version, architecture, date/time, and locale.
2. **Connect to remote host** — call `ssh_connect` with an alias, host, user, and optional key path to establish a persistent session. Requires key-based authentication (no password prompts).
3. **Run remote commands** — call `ssh_run_command` with the session alias and command string.
4. **Manage sessions** — use `ssh_list_connections` to see active sessions, and `ssh_disconnect` to close them.

## Tools

### get_system_info

Retrieves local OS details including version, architecture, current date/time, and locale settings.

- Takes no parameters.

### ssh_connect

Establishes a persistent SSH connection (ControlMaster session) to a remote host.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `alias` | string | yes | Unique name for the session (e.g., `webserver`) |
| `host` | string | yes | Hostname or IP address |
| `user` | string | yes | SSH username |
| `port` | integer | no | SSH port (default: 22) |
| `key_path` | string | no | Path to private key file |

**Example:**
```json
{
  "alias": "webserver",
  "host": "192.168.1.100",
  "user": "deploy",
  "key_path": "/home/user/.ssh/id_ed25519"
}
```

### ssh_run_command

Executes a shell command on an active SSH session.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `alias` | string | yes | The session alias from `ssh_connect` |
| `command` | string | yes | Shell command to execute remotely |

### ssh_list_connections

Lists all currently active SSH sessions.

- Takes no parameters.

### ssh_disconnect

Closes an active SSH session and cleans up resources.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `alias` | string | yes | The session alias to disconnect |
