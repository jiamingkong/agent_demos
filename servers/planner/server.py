import datetime
import re
from pathlib import Path
from typing import List, Optional

from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("planner", log_level="ERROR")

# Cache directory for planner files
CACHE_DIR = Path.cwd() / "artifacts" / "cache"


@mcp.tool()
def init_planning(
    task_description: str, phases: List[str], phase_steps: List[List[str]]
) -> str:
    """
    Initialize the planning files (task_plan.md, findings.md, progress.md) for a new task.
    You MUST provide detailed steps for each phase.

    Args:
        task_description: Brief description of the task.
        phases: List of phases (e.g. ['Requirements', 'Implementation', 'Testing']).
        phase_steps: List of lists, where each inner list contains specific actionable steps for the corresponding phase.
                     Length of phase_steps must match length of phases.
                     Example: [['Req analysis', 'Check docs'], ['Setup env', 'Write code', 'Test']]
    """
    date_str = datetime.datetime.now().strftime("%Y-%m-%d")

    # Validation
    if len(phases) != len(phase_steps):
        return f"Error: Number of phrases ({len(phases)}) must match number of step lists ({len(phase_steps)})."

    # 1. task_plan.md
    phases_text = ""
    for i, p in enumerate(phases):
        phase_num = i + 1
        status = "in_progress" if i == 0 else "pending"

        # Build steps checklist
        steps_text = ""
        steps_list = phase_steps[i]

        if not steps_list:
            steps_text = "- [ ] Perform phase tasks (To be defined)\n"
        else:
            for step in steps_list:
                steps_text += f"- [ ] {step}\n"

        phases_text += (
            f"\n### Phase {phase_num}: {p}\n**Status:** {status}\n\n{steps_text}\n"
        )

    task_plan_content = f"""# Task Plan: {task_description}

## Goal
{task_description}

## Current Phase
Phase 1: {phases[0]}

## Detailed Phases
{phases_text}

## Key Questions
1. What are the main blockers?

## Decisions Made
| Decision | Rationale |
|----------|-----------|

## Errors Encountered
| Error | Attempt | Resolution |
|-------|---------|------------|
"""

    # 2. findings.md
    findings_content = """# Findings & Decisions

## Requirements
- [Captured from user request]

## Research Findings
- 

## Technical Decisions
| Decision | Rationale |
|----------|-----------|

## Resources
- 
"""

    # 3. progress.md
    progress_content = f"""# Progress Log

## Session: {date_str}

### Phase 1: {phases[0]}
- **Status:** in_progress
- **Started:** {datetime.datetime.now().strftime("%H:%M:%S")}
- Actions taken:
  - Initialized planning files
"""

    try:
        # Ensure cache directory exists
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        (CACHE_DIR / "task_plan.md").write_text(task_plan_content, encoding="utf-8")
        (CACHE_DIR / "findings.md").write_text(findings_content, encoding="utf-8")
        (CACHE_DIR / "progress.md").write_text(progress_content, encoding="utf-8")
        return f"Successfully initialized planning files in {CACHE_DIR}:\n- task_plan.md\n- findings.md\n- progress.md"
    except Exception as e:
        return f"Error creating files: {str(e)}"


@mcp.tool()
def resume_last_run() -> str:
    """
    Reads the existing planning files to resume work from the last state.
    Returns the content of task_plan.md, findings.md, and the last entry from progress.md.
    """
    if not (CACHE_DIR / "task_plan.md").exists():
        return "No previous run found. Please use `init_planning` to start a new task."

    try:
        task_plan = (CACHE_DIR / "task_plan.md").read_text(encoding="utf-8")

        findings = ""
        if (CACHE_DIR / "findings.md").exists():
            findings = (CACHE_DIR / "findings.md").read_text(encoding="utf-8")
        else:
            findings = "No findings recorded."

        progress_log = ""
        if (CACHE_DIR / "progress.md").exists():
            progress_full = (CACHE_DIR / "progress.md").read_text(encoding="utf-8")
            # Get the last 20 lines of progress
            progress_lines = progress_full.splitlines()[-20:]
            progress_log = "\n".join(progress_lines)

        return f"### Resuming Previous Task\n\n#### Current Plan Status:\n{task_plan}\n\n#### Current Findings:\n{findings}\n\n#### Recent Progress:\n{progress_log}"
    except Exception as e:
        return f"Error reading previous run files: {str(e)}"


@mcp.tool()
def read_plan() -> str:
    """
    Read the current status from planning files.
    """
    try:
        files = ["task_plan.md", "findings.md", "progress.md"]
        content = "current_planning_status:\n"

        for fname in files:
            p = CACHE_DIR / fname
            if p.exists():
                # Read partial content to save tokens
                full_text = p.read_text(encoding="utf-8")
                if fname == "task_plan.md":
                    # Read Goal, Current Phase, and Active Phase details
                    lines = full_text.split("\n")
                    relevant_lines = []
                    capture = True
                    for line in lines:
                        if line.startswith("## Decisions"):
                            capture = False
                        if capture:
                            relevant_lines.append(line)
                    content += (
                        f"\n--- {fname} (Summary) ---\n"
                        + "\n".join(relevant_lines)
                        + "\n"
                    )
                elif fname == "progress.md":
                    # Read last 20 lines
                    lines = full_text.split("\n")
                    content += (
                        f"\n--- {fname} (Last 20 lines) ---\n"
                        + "\n".join(lines[-20:])
                        + "\n"
                    )
                else:
                    content += f"\n--- {fname} (Exists) ---\n"
            else:
                content += f"\n{fname} does not exist."
        return content
    except Exception as e:
        return f"Error reading plan: {str(e)}"


@mcp.tool()
def update_plan_status(phase_name: str, status: str, notes: str) -> str:
    """
    Update the status of the current phase in task_plan.md.

    Args:
        phase_name: Name of the phase to update (partial match ok).
        status: New status (pending, in_progress, completed).
        notes: Optional notes/actions to log to progress.md.
    """
    try:
        task_plan_path = CACHE_DIR / "task_plan.md"
        progress_path = CACHE_DIR / "progress.md"

        if not task_plan_path.exists():
            return "Error: task_plan.md not found. Run init_planning first."

        # Update task_plan.md
        lines = task_plan_path.read_text(encoding="utf-8").split("\n")
        new_lines = []
        current_phase_updated = False

        for i, line in enumerate(lines):
            if f"Phase" in line and phase_name.lower() in line.lower():
                new_lines.append(line)
            elif (
                "**Status:**" in line
                and not current_phase_updated
                and phase_name.lower() in "".join(lines[max(0, i - 5) : i]).lower()
            ):
                new_lines.append(f"- **Status:** {status}")
                current_phase_updated = True
            else:
                new_lines.append(line)

        task_plan_path.write_text("\n".join(new_lines), encoding="utf-8")

        # Update progress.md
        if progress_path.exists() and notes:
            with open(progress_path, "a", encoding="utf-8") as f:
                timestamp = datetime.datetime.now().strftime("%H:%M:%S")
                f.write(f"\n- [{timestamp}] {notes} (Status: {status})")

        return f"Updated phase '{phase_name}' to '{status}' and logged notes."

    except Exception as e:
        return f"Error updating plan: {str(e)}"


@mcp.tool()
def mark_step_complete(phase_name: str, step_keyword: str) -> str:
    """
    Mark a step as complete in task_plan.md.

    Args:
        phase_name: The name of the phase containing the step (e.g. "Requirements").
        step_keyword: A unique keyword or substring to identify the step to check off.
    """
    try:
        task_plan_path = CACHE_DIR / "task_plan.md"
        if not task_plan_path.exists():
            return "Error: task_plan.md not found."

        lines = task_plan_path.read_text(encoding="utf-8").split("\n")
        new_lines = []

        in_correct_phase = False
        updated = False

        for line in lines:
            # Detect Phase Header
            if (
                line.strip().startswith("### Phase")
                and phase_name.lower() in line.lower()
            ):
                in_correct_phase = True
            elif line.strip().startswith("### Phase"):
                in_correct_phase = False

            # Check off step if in phase
            if (
                in_correct_phase
                and "- [ ]" in line
                and step_keyword.lower() in line.lower()
            ):
                new_lines.append(line.replace("- [ ]", "- [x]"))
                updated = True
            else:
                new_lines.append(line)

        if updated:
            task_plan_path.write_text("\n".join(new_lines), encoding="utf-8")
            return f"Marked step '{step_keyword}' as complete in phase '{phase_name}'."
        else:
            return f"Could not find step matching '{step_keyword}' in phase '{phase_name}'."

    except Exception as e:
        return f"Error marking step complete: {str(e)}"


@mcp.tool()
def add_finding(category: str, content: str) -> str:
    """
    Add a finding, decision, or resource to findings.md.

    Args:
        category: The section to add to. Options: "Requirements", "Research Findings", "Technical Decisions", "Resources", "Errors Encountered".
        content: The text to add. For "Technical Decisions", provide "Decision | Rationale" or just text.
    """
    try:
        findings_path = CACHE_DIR / "findings.md"
        if not findings_path.exists():
            return "Error: findings.md not found."

        text = findings_path.read_text(encoding="utf-8")

        # Map input category to partial header match
        header_map = {
            "requirements": "## Requirements",
            "research": "## Research Findings",
            "findings": "## Research Findings",
            "technical": "## Technical Decisions",
            "decisions": "## Technical Decisions",
            "resources": "## Resources",
            "errors": "## Errors Encountered",
        }

        target_header = header_map.get(category.lower())
        if not target_header:
            target_header = f"## {category}"

        # 1. Find the target section
        # We look for the header at the start of a line
        pattern = re.compile(
            f"^{re.escape(target_header)}", re.MULTILINE | re.IGNORECASE
        )
        match = pattern.search(text)

        if not match:
            # Try to append the section if it doesn't exist?
            # For now, just append to end of file if not found
            new_text = text + f"\n\n{target_header}\n- {content}"
            findings_path.write_text(new_text, encoding="utf-8")
            return f"Section '{target_header}' not found, created new section and added finding."

        start_idx = match.end()

        # 2. Find the start of the NEXT section
        # Look for any line starting with "## " after start_idx
        next_section_pattern = re.compile(r"^## ", re.MULTILINE)
        next_match = next_section_pattern.search(text, start_idx)

        if next_match:
            end_idx = next_match.start()
        else:
            end_idx = len(text)

        # 3. Insert content at end_idx (before next section)
        # Ensure we attach nicely
        section_content = text[start_idx:end_idx]

        # Prepare content to insert
        to_insert = content.strip()
        if not to_insert.startswith("-") and not to_insert.startswith("|"):
            to_insert = f"- {to_insert}"

        # If inserting into a table (starts with |), ensure newline
        if to_insert.startswith("|") and not section_content.strip().endswith("|"):
            # It might be the first row of a table?
            pass

        # Construct new text
        # We insert before end_idx
        # Add a newline if previous content doesn't end with one
        insertion = f"\n{to_insert}"
        if not section_content.endswith("\n"):
            insertion = f"\n{to_insert}"

        new_text = (
            text[:end_idx].rstrip() + insertion + "\n\n" + text[end_idx:].lstrip()
        )

        findings_path.write_text(new_text, encoding="utf-8")

        return f"Added finding to '{category}'."

    except Exception as e:
        return f"Error adding finding: {str(e)}"


@mcp.tool()
def erase_plans() -> str:
    """
    Quickly erase existing plans in artifacts/cache by deleting the three planning files.
    This is useful when you want to start fresh without any leftover plan files.

    Returns:
        Success or error message.
    """
    try:
        files = ["task_plan.md", "findings.md", "progress.md"]
        deleted = []
        for fname in files:
            p = CACHE_DIR / fname
            if p.exists():
                p.unlink()
                deleted.append(fname)
        if deleted:
            return f"Successfully erased plans: {', '.join(deleted)}."
        else:
            return "No plan files found to erase."
    except Exception as e:
        return f"Error erasing plans: {str(e)}"


if __name__ == "__main__":
    mcp.run()
