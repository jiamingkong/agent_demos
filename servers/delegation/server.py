import asyncio
import json
import logging
import os
import subprocess
import sys
import uuid
from pathlib import Path
from typing import Any, Dict, List

from mcp.server.fastmcp import FastMCP

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("orchestra_server")

# Initialize MCP Server
mcp = FastMCP("orchestra", log_level="ERROR")

# Global state to track sub-agent tasks
# Structure: { task_id: { status: "running"|"completed"|"failed", result: str, process: subprocess.Popen, log_file: Path } }
TASKS: Dict[str, Dict[str, Any]] = {}


@mcp.tool()
def list_available_skills() -> str:
    """
    List all available skills (servers) that can be used by sub-agents.
    Returns a markdown formatted list of server names and their SKILL.md paths.
    """
    try:
        current_dir = Path(__file__).parent.parent
        # Assuming we are in servers/delegation, we go up to servers/
        servers_dir = current_dir

        skills = []
        if servers_dir.exists():
            for item in servers_dir.iterdir():
                if (
                    item.is_dir()
                    and item.name != "delegation"
                    and item.name != "__pycache__"
                ):
                    skill_path = item / "SKILL.md"
                    if skill_path.exists():
                        skills.append(f"- {item.name}: {skill_path}")

        return "\n".join(skills) if skills else "No skills found."
    except Exception as e:
        return f"Error listing skills: {str(e)}"


@mcp.tool()
async def delegate_task(task_description: str, skills_needed: List[str]) -> str:
    """
    Delegate a task to a new sub-agent process asynchronously.

    Args:
        task_description: The detailed prompt/instruction for the sub-agent.
        skills_needed: A list of skill names (directories in servers/) the sub-agent needs.

    Returns:
        A task_id to track the progress.
    """
    task_id = f"task_{uuid.uuid4().hex[:8]}"

    # 1. Prepare Workspace for Sub-agent
    base_dir = Path(__file__).parent
    runners_dir = base_dir / "runners"
    runners_dir.mkdir(exist_ok=True)

    # We need to run a standalone agent script.
    # Since the main agent.py is designed to be interactive, we need a 'headless' version
    # or a way to pipe input. For simplicity, we'll create a purpose-built runner script
    # that imports the agent class but runs non-interactively.

    # However, reusing the existing `agent.py` might be complex if it's tightly coupled to CLI input.
    # A robust way is to generate a small python script that:
    # 1. Instantiates the agent
    # 2. Add requested servers
    # 3. Sends a single customized system message + user prompt
    # 4. Prints result to stdout/file

    # Let's locate the root agent.py
    # self is at /path/to/servers/delegation/server.py
    # agent is at /path/to/agent.py
    root_dir = base_dir.parent.parent
    agent_script_path = root_dir / "agent.py"

    # Create a temporary runner script for this task
    runner_script_content = f"""
import sys
import asyncio
import os
from pathlib import Path

# Add root to sys.path to allow importing agent
sys.path.append(str(Path("{root_dir}")))

from agent import DeepSeekMCPAgent

def get_api_key_local() -> str:
    key_path = Path("{root_dir}") / "api_key.txt"
    if key_path.exists():
        return key_path.read_text(encoding="utf-8").strip()
    return ""

async def run_task():
    try:
        api_key = get_api_key_local()
        if not api_key:
            print("Error: API Key not found in api_key.txt")
            return

        agent = DeepSeekMCPAgent(api_key=api_key)
        
        # Load requested skills
        servers_dir = Path("{root_dir}") / "servers"
        requested_skills = {json.dumps(skills_needed)}
        
        for skill_name in requested_skills:
            skill_dir = servers_dir / skill_name
            if skill_dir.exists():
                agent.add_server(
                    skill_name,
                    skill_dir / "SKILL.md",
                    sys.executable,
                    [str(skill_dir / "server.py")]
                )

        # We need to modify the agent to NOT use console.input loop but just run once.
        # But `agent.chat_loop` is an infinite loop.
        # We will bypass chat_loop and use internal methods directly.
        
        # 1. Start logging
        agent._start_logging()
        
        # 2. Add System Prompt (Simplified from agent.py)
        # We need to manually trigger skill loading if needed.
        # For this headless sub-agent, we can pre-load all requested skills.
        
        # Pre-connect to skills to ensure tools are available immediately
        # (This differs from the lazy loading in main agent, but helpful for headless)
        # However, the agent logic `call_tool` handles connection.
        
        # Construct messages
        sys_prompt = "You are a sub-agent delegated to perform a specific task. Do not ask for user input. Perform the task and then exit."
        agent.messages.append({{"role": "system", "content": sys_prompt}})
        agent.messages.append({{"role": "user", "content": '''{task_description}'''}})
        
        iteration = 0
        max_iter = 30
        
        final_result = ""
        
        while iteration < max_iter:
            # Condense context if needed
            await agent._condense_context()
            
            # Get tools
            tools = await agent.list_tools()
            
            # Call LLM
            # We need to capture the output to return it
            full_content = await agent.send_llm_request(
                 prompt="", # Prompt is already in history? No, send_llm_request is one-off. 
                 # We can't use send_llm_request easily because it doesn't update history.
                 # We have to replicate the loop logic from chat_loop but without rich console input.
            )
            
            # RE-IMPLEMENTING BASIC LOOP FOR HEADLESS EXECUTION
            # This is tricky because we want to reuse the agent logic.
            # Best approach: Use the client directly with history.
            
            response = agent.client.chat.completions.create(
                model="deepseek-reasoner",
                messages=agent.messages,
                tools=tools if tools else None,
                stream=False # No streaming for headless runner
            )
            
            msg = response.choices[0].message
            content = msg.content
            
            # Handle tool calls
            if msg.tool_calls:
                agent.messages.append(msg) # Add assistant msg with tool calls
                
                for tc in msg.tool_calls:
                    fn_name = tc.function.name
                    args = json.loads(tc.function.arguments)
                    result = await agent.call_tool(fn_name, args)
                    
                    agent.messages.append({{
                        "role": "tool",
                        "tool_call_id": tc.id,
                        "content": result
                    }})
            else:
                # No tool calls -> Task potentially done or asking a question (which we can't answer)
                # We assume if no tool calls, it's the final answer.
                final_result = content
                break
            
            iteration += 1

        print("TASK_RESULT_START")
        print(final_result)
        print("TASK_RESULT_END")
        
        await agent.cleanup()

    except Exception as e:
        print(f"Error: {{e}}")

if __name__ == "__main__":
    asyncio.run(run_task())
"""

    runner_file = runners_dir / f"runner_{task_id}.py"
    runner_file.write_text(runner_script_content, encoding="utf-8")

    # 2. Spawn Process
    # We redirect stdout/stderr to a log file to capture the output
    log_file = runners_dir / f"{task_id}.log"

    process = subprocess.Popen(
        [sys.executable, str(runner_file)],
        stdout=open(log_file, "w"),
        stderr=subprocess.STDOUT,
        cwd=str(root_dir),  # Execute from root to find api_key.txt etc
    )

    TASKS[task_id] = {
        "status": "running",
        "process": process,
        "log_file": log_file,
        "description": task_description[:50] + "...",
    }

    return f"Task started with ID: {task_id}. Use check_task_status('{task_id}') to monitor."


@mcp.tool()
def check_task_status(task_id: str) -> str:
    """
    Check the status and result of a delegated task.
    """
    if task_id not in TASKS:
        return "Error: Task ID not found."

    task_info = TASKS[task_id]
    process = task_info["process"]

    # Check if process is still running
    if process.poll() is None:
        return f"Task {task_id} is still RUNNING."

    # Process finished
    task_info["status"] = "completed"

    # Read Log
    try:
        with open(task_info["log_file"], "r") as f:
            log_content = f.read()

        # Extract Result
        if "TASK_RESULT_START" in log_content:
            _, part2 = log_content.split("TASK_RESULT_START", 1)
            result, _ = part2.split("TASK_RESULT_END", 1)
            return f"Task {task_id} COMPLETED.\n\nResult:\n{result.strip()}"
        else:
            return f"Task {task_id} FINISHED but no result extracted. Log tail:\n{log_content[-500:]}"

    except Exception as e:
        return f"Task finished but failed to read log: {e}"


if __name__ == "__main__":
    mcp.run()
