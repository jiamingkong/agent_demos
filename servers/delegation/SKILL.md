---
name: delegation
description: Agent delegation and orchestration capabilities to split tasks and run them in parallel.
allowed-tools:
  - list_available_skills
  - delegate_task
  - check_task_status
---

# Delegation & Orchestration Skill

This skill allows the main agent to act as an orchestrator, dispatching sub-tasks to independent sub-agents. This is useful for parallelizing work or isolating complex sub-problems.

## Tools

### list_available_skills
View which skills (servers) can be assigned to sub-agents.
- returns: A list of available skills.

### delegate_task
Spawns a new autonomous sub-agent process to handle a specific task. The sub-agent runs asynchronously.
- `task_description`: Clear instructions for the sub-agent.
- `skills_needed`: List of skill names the sub-agent requires (e.g., `["web_fetch", "office_reader"]`).
- returns: A `task_id` for tracking.

### check_task_status
Retrieves the status (RUNNING/COMPLETED) and the final output of a delegated task.
- `task_id`: The ID returned by `delegate_task`.
- returns: Status message and result content if finished.

## Usage Pattern

1. **Analyze** the user's complex request.
2. **Break down** the request into sub-tasks.
3. **List skills** to see what's available for sub-agents.
4. **Delegate** each sub-task using `delegate_task`.
5. **Monitor** progress using `check_task_status`.
6. **Integrate** the results from sub-agents into a final answer.
