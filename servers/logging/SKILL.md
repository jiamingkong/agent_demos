---
name: logging
description: Structured logging to files, console, and remote services.
allowed-tools:
  - log_message
  - configure_logging
  - list_logs
  - log_structured
---

# Logging Skill

This skill enables the agent to perform structured logging using Python's built‑in logging module.

## Features

- Log messages at different severity levels (DEBUG, INFO, WARNING, ERROR, CRITICAL).
- Configure logging destinations: console, rotating file, or both.
- Read back log entries from a file.
- Log structured events with JSON metadata.

## Prerequisites

- No external dependencies beyond Python's standard library.

## Tools

### log_message
Log a plain text message with a given severity.
- `level`: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
- `message`: The log message.
- `extra`: Optional JSON string with additional key‑value pairs (merged into the log record).

### configure_logging
Configure the logging system globally.
- `level`: Default log level (default "INFO").
- `log_file`: Path to a file for logging (optional). If provided, logs are written to this file with automatic rotation.
- `max_bytes`: Maximum size per log file before rotation (default 10 MB).
- `backup_count`: Number of backup files to keep (default 5).
- `enable_console`: Whether to keep console output (default True).

### list_logs
Read recent log entries from a specified log file.
- `log_file`: Path to the log file.
- `limit`: Maximum number of lines to return (default 50). The most recent lines are returned.

### log_structured
Log a structured event with JSON data.
- `event`: Event name.
- `data`: JSON string with key‑value pairs to attach to the log.
- `level`: Log level (default "INFO").

## Usage Example

1. **Configure logging to a file**:
   ```
   configure_logging(level="DEBUG", log_file="/tmp/agent.log")
   ```
2. **Log an informational message**:
   ```
   log_message(level="INFO", message="Task started")
   ```
3. **Log a structured event**:
   ```
   log_structured(event="user_login", data='{"user_id": 123, "ip": "192.168.1.1"}')
   ```
4. **Read back logs**:
   ```
   list_logs(log_file="/tmp/agent.log", limit=10)
   ```
