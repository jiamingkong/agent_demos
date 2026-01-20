"""
Logging skill: Structured logging to files, console, and remote services.
Uses Python's built-in logging module.
"""

import json
import logging
import logging.handlers
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("logging", log_level="ERROR")

# Global logger configuration
_logger = logging.getLogger("agent_logger")
_logger.setLevel(logging.INFO)
# Default console handler
_console_handler = logging.StreamHandler()
_console_handler.setLevel(logging.INFO)
_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
_console_handler.setFormatter(_formatter)
_logger.addHandler(_console_handler)
_file_handler = None


@mcp.tool()
def log_message(level: str, message: str, extra: Optional[str] = None) -> str:
    """
    Log a message with the specified severity level.

    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
        message: The log message.
        extra: Optional JSON string with additional key‑value pairs.
    """
    try:
        extra_dict = {}
        if extra:
            extra_dict = json.loads(extra)
        level_upper = level.upper()
        if level_upper == "DEBUG":
            _logger.debug(message, extra=extra_dict)
        elif level_upper == "INFO":
            _logger.info(message, extra=extra_dict)
        elif level_upper == "WARNING":
            _logger.warning(message, extra=extra_dict)
        elif level_upper == "ERROR":
            _logger.error(message, extra=extra_dict)
        elif level_upper == "CRITICAL":
            _logger.critical(message, extra=extra_dict)
        else:
            return f"Invalid log level '{level}'. Use DEBUG, INFO, WARNING, ERROR, CRITICAL."
        return f"Logged {level_upper}: {message}"
    except Exception as e:
        return f"Error logging message: {e}"


@mcp.tool()
def configure_logging(
    level: str = "INFO",
    log_file: Optional[str] = None,
    max_bytes: Optional[int] = 10485760,
    backup_count: Optional[int] = 5,
    enable_console: bool = True,
) -> str:
    """
    Configure the logging system.

    Args:
        level: Default log level.
        log_file: Path to a file for logging (rotates automatically).
        max_bytes: Maximum size per log file before rotation (default 10MB).
        backup_count: Number of backup files to keep.
        enable_console: Whether to keep console output.
    """
    try:
        # Remove existing file handler
        global _file_handler
        if _file_handler is not None:
            _logger.removeHandler(_file_handler)
            _file_handler = None

        # Set level
        level_upper = level.upper()
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if level_upper not in valid_levels:
            return f"Invalid log level '{level}'. Use {', '.join(valid_levels)}."
        _logger.setLevel(getattr(logging, level_upper))

        # Configure console handler
        if enable_console:
            if not any(isinstance(h, logging.StreamHandler) for h in _logger.handlers):
                _logger.addHandler(_console_handler)
        else:
            for handler in _logger.handlers[:]:
                if isinstance(handler, logging.StreamHandler):
                    _logger.removeHandler(handler)

        # Configure file handler
        if log_file:
            log_path = Path(log_file).resolve()
            log_path.parent.mkdir(parents=True, exist_ok=True)
            _file_handler = logging.handlers.RotatingFileHandler(
                log_path,
                maxBytes=max_bytes if max_bytes else 10485760,
                backupCount=backup_count if backup_count else 5,
            )
            _file_handler.setFormatter(_formatter)
            _file_handler.setLevel(getattr(logging, level_upper))
            _logger.addHandler(_file_handler)

        config_summary = f"Logging configured: level={level_upper}"
        if log_file:
            config_summary += f", file={log_file}"
        config_summary += f", console={enable_console}"
        return config_summary
    except Exception as e:
        return f"Error configuring logging: {e}"


@mcp.tool()
def list_logs(log_file: str, limit: int = 50) -> str:
    """
    Read recent log entries from a file.

    Args:
        log_file: Path to the log file.
        limit: Maximum number of lines to return.
    """
    try:
        log_path = Path(log_file)
        if not log_path.exists():
            return f"Log file '{log_file}' does not exist."
        with open(log_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        if limit > 0:
            lines = lines[-limit:]
        return "".join(lines)
    except Exception as e:
        return f"Error reading log file: {e}"


@mcp.tool()
def log_structured(event: str, data: str, level: str = "INFO") -> str:
    """
    Log a structured event with JSON data.

    Args:
        event: Event name.
        data: JSON string with key‑value pairs.
        level: Log level.
    """
    try:
        data_dict = json.loads(data)
        extra = {"event": event, **data_dict}
        return log_message(level, f"Event '{event}'", json.dumps(extra))
    except Exception as e:
        return f"Error logging structured event: {e}"


if __name__ == "__main__":
    mcp.run()
