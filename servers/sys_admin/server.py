import datetime
import locale
import os
import platform
import subprocess
from pathlib import Path
from typing import Dict, Optional

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("sys_admin", log_level="ERROR")

# Global state to track active SSH sessions (mapping alias -> socket_path)
SSH_SESSIONS: Dict[str, Dict[str, str]] = {}
SOCKET_DIR = Path("/tmp/mcp_ssh_sockets")
SOCKET_DIR.mkdir(parents=True, exist_ok=True)


@mcp.tool()
def get_system_info() -> str:
    """
    Get detailed information about the current local system (OS, Time, Locale).
    """
    try:
        info = []
        # OS Info
        info.append(f"System: {platform.system()}")
        info.append(f"Release: {platform.release()}")
        info.append(f"Version: {platform.version()}")
        info.append(f"Architecture: {platform.machine()}")
        info.append(f"Processor: {platform.processor()}")

        # Date/Time
        now = datetime.datetime.now()
        info.append(f"Current Date: {now.strftime('%Y-%m-%d')}")
        info.append(
            f"Current Time: {now.strftime('%H:%M:%S')} {now.astimezone().tzname()}"
        )

        # Locale
        loc = locale.getdefaultlocale()
        info.append(f"Locale: {loc[0]}")
        info.append(f"Encoding: {loc[1]}")

        return "\n".join(info)
    except Exception as e:
        return f"Error retrieving system info: {e}"


@mcp.tool()
def ssh_connect(
    alias: str, host: str, user: str, port: int = 22, key_path: Optional[str] = None
) -> str:
    """
    Establish a persistent SSH connection to a remote host.

    Args:
        alias: A unique name to refer to this connection (e.g., 'prod_db').
        host: Hostname or IP address.
        user: Username.
        port: SSH port (default 22).
        key_path: Optional path to private key file.
    """
    global SSH_SESSIONS

    if alias in SSH_SESSIONS:
        return f"Error: Session alias '{alias}' already exists. Use ssh_disconnect to close it first."

    socket_path = SOCKET_DIR / f"ssh_{alias}.sock"

    # Construct command to create master connection
    # -M: master mode
    # -S: socket path
    # -f: fork to background
    # -N: no command (just forward/connect)
    cmd = [
        "ssh",
        "-M",
        "-S",
        str(socket_path),
        "-f",
        "-N",
        "-p",
        str(port),
        f"{user}@{host}",
    ]

    if key_path:
        cmd.extend(["-i", key_path])

    # We also add StrictHostKeyChecking=no for automation ease, OR we assume user has handled it.
    # For an agent, prompting is bad. Let's try to be safe but usable.
    # ideally, we might use BatchMode=yes to fail on passphrase prompt
    cmd.extend(["-o", "ControlPersist=yes"])
    cmd.extend(["-o", "BatchMode=yes"])

    try:
        # Run the connection command
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            return f"Failed to connect. STDERR: {result.stderr}"

        # Verify socket exists
        if not socket_path.exists():
            return "Connection command ran, but control socket was not created. Check connectivity and auth."

        SSH_SESSIONS[alias] = {"host": host, "user": user, "socket": str(socket_path)}

        return f"Connected to {user}@{host} as '{alias}'. Connection is persistent."

    except Exception as e:
        return f"Error establishing SSH connection: {e}"


@mcp.tool()
def ssh_run_command(alias: str, command: str) -> str:
    """
    Run a command on a connected SSH session.

    Args:
        alias: The session alias used in ssh_connect.
        command: The shell command to execute remotely.
    """
    if alias not in SSH_SESSIONS:
        return f"Error: Unknown session '{alias}'. Active sessions: {list(SSH_SESSIONS.keys())}"

    session = SSH_SESSIONS[alias]
    socket_path = session["socket"]

    cmd = [
        "ssh",
        "-S",
        socket_path,
        "dummy_host",  # The socket determines the destination, but ssh syntax requires a host arg (ignored)
        command,
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        output = (
            f"COMMAND: {command}\n\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
        )
        return output
    except subprocess.TimeoutExpired:
        return f"Error: Command timed out after 60s."
    except Exception as e:
        return f"Error executing SSH command: {e}"


@mcp.tool()
def ssh_list_connections() -> str:
    """List all active SSH connections."""
    if not SSH_SESSIONS:
        return "No active SSH connections."

    lines = ["Active SSH Sessions:"]
    for alias, details in SSH_SESSIONS.items():
        lines.append(f"- {alias}: {details['user']}@{details['host']}")
    return "\n".join(lines)


@mcp.tool()
def ssh_disconnect(alias: str) -> str:
    """
    Close an active SSH connection.
    """
    if alias not in SSH_SESSIONS:
        return f"Error: Unknown session '{alias}'."

    session = SSH_SESSIONS[alias]
    socket_path = session["socket"]

    # Send exit command to master
    cmd = ["ssh", "-S", socket_path, "-O", "exit", "dummy_host"]

    try:
        subprocess.run(cmd, capture_output=True)
        del SSH_SESSIONS[alias]
        # Cleanup file if valid
        if os.path.exists(socket_path):
            os.remove(socket_path)
        return f"Disconnected session '{alias}'."
    except Exception as e:
        return f"Error disconnecting: {e}"


if __name__ == "__main__":
    mcp.run()
