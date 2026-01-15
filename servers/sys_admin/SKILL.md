---
name: sys_admin
description: System administration tools for local OS info and remote SSH connection management.
allowed-tools:
  - get_system_info
  - ssh_connect
  - ssh_run_command
  - ssh_list_connections
  - ssh_disconnect
---

# SysAdmin Skill

This skill allows the agent to inspect the local system environment and manage persistent SSH connections to remote servers.

## Tools

### get_system_info
Retrieve details about the local operating system, including version, architecture, current date/time, and locale settings.

### ssh_connect
Establish a persistent SSH connection (session) to a remote host.
- `alias`: A unique name for the session (e.g., 'webserver').
- `host`: Hostname or IP.
- `user`: SSH username.
- `port`: (Optional) Port, default 22.
- `key_path`: (Optional) Path to private key file.

**Note:** This tool uses SSH ControlMaster with BatchMode. It requires key-based authentication (no password prompts).

### ssh_run_command
Execute a shell command on an active SSH session.
- `alias`: The session alias.
- `command`: The command string to run.

### ssh_list_connections
List all currently active SSH sessions.

### ssh_disconnect
Close an active SSH session and cleanup resources.
- `alias`: The session alias.
