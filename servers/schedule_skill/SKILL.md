---
name: schedule_skill
description: Task scheduling capabilities using APScheduler.
tools:
  - schedule_task
  - schedule_cron
  - list_scheduled_tasks
  - cancel_task
  - pause_scheduler
  - resume_scheduler
---

# Schedule Skill

This skill enables the agent to schedule tasks to run at specific times or on cron schedules.

## Prerequisites

- `apscheduler` library (install via `pip install apscheduler`)
- The skill manages a background scheduler that runs tasks asynchronously.

## Tools

### schedule_task
Schedule a one-time task to run at a specific datetime.

Args:
- `task_id`: Unique identifier for the task.
- `run_at`: ISO 8601 datetime string (e.g., "2026-01-21T10:00:00").
- `command`: Command to execute (shell command or Python function reference).

### schedule_cron
Schedule a recurring task using cron‑like expressions.

Args:
- `task_id`: Unique identifier for the task.
- `cron_expression`: Cron string (e.g., "0 9 * * *" for daily at 09:00).
- `command`: Command to execute.

### list_scheduled_tasks
List all currently scheduled tasks.

Returns a table of task IDs, next run times, and commands.

### cancel_task
Cancel a scheduled task.

Args:
- `task_id`: ID of the task to cancel.

### pause_scheduler
Temporarily pause the scheduler (no tasks will run).

### resume_scheduler
Resume a paused scheduler.

## Notes

- The scheduler runs in a background thread; tasks are executed in a separate process.
- Tasks that are shell commands are executed via `subprocess`.
- Python function tasks must be importable and picklable.
- The scheduler persists across skill reloads (in‑memory only).
