---
name: planner
description: File-based planning system.
allowed-tools:
  - init_planning
  - resume_last_run
  - read_plan
  - update_plan_status
  - mark_step_complete
  - add_finding
  - erase_plans
---

# Planner Skill

This skill implements a persistent planning pattern using markdown files.

## Files Managed
- `task_plan.md`: Tracks phases, progress, and high-level goal.
- `findings.md`: Records research, technical decisions, and resources.
- `progress.md`: Detailed session log of actions and thoughts.

## Tools

### init_planning
Initialize the planning files in the current working directory. For coding task, you do not have to provide rigorous testing.
- `task_description`: What needs to be done.
- `phases`: List of high-level phases.
- `phase_steps`: REQUIRED. List of lists of strings. Each inner list provides the detailed checklist steps for the corresponding phase.
  - Example: `[["Research the official API documentation for authentication methods", "Read the developer guides on rate limiting strategies"], ["Set up the initial project structure using Python Poetry and git", "Implement the core logic for the connection manager class"]]`

### resume_last_run
Reads existing planning files to allow the agent to resume an interrupted task.
Returns the content of `task_plan.md` and the recent log from `progress.md`.

### read_plan
Read the current status from the planning files.

### update_plan_status
Update the status of a phase in `task_plan.md` and log a note in `progress.md`.
- `phase_name`: Name of the phase.
- `status`: New status (pending, in_progress, completed).
- `notes`: Optional note to append to progress log.

### mark_step_complete
Mark a specific step in `task_plan.md` as complete ([x]).
- `phase_name`: The name of the phase containing the step.
- `step_keyword`: A unique substring to identify the step line.

### add_finding
Record a finding, decision, or resource in `findings.md`.
- `category`: Target section ("Requirements", "Research", "Technical Decisions", "Resources").
- `content`: The text to add. For technical decisions, you can use markdown table row format `| Decision | Rationale |`.

### erase_plans
Quickly erase existing plans in `artifacts/cache` by deleting the three planning files.
- This is useful when you want to start fresh without any leftover plan files.
- No parameters needed.

## Best Practices for Agents

1. **Start Strong**: Always begin complex tasks with `init_planning`. Break down phases into granular, actionable steps in `phase_steps` rather than broad goals.
2. **Update Frequently**: As you complete sub-tasks, use `mark_step_complete` IMMEDIATELY. This acts as a "save point" and keeps your reasoning grounded.
3. **Log Discoveries**: Don't rely on conversation history for long-term facts. Use `add_finding` to record important URLs, file paths, or architectural decisions.
4. **Transition Phases**: When a phase is done, explicitly use `update_plan_status` to mark it as `completed` and the next one as `in_progress`.
5. **Resume Smart**: If you see existing plan files, prefer `resume_last_run` over starting from scratch.


