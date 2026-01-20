import argparse
import asyncio
import sys
from pathlib import Path

from dotenv import load_dotenv

from agent import DeepSeekMCPAgent


def get_api_key() -> str:
    # First, check environment variable
    import os

    env_key = os.getenv("DEEPSEEK_API_KEY")
    if env_key:
        return env_key.strip()

    # Second, check api_key.txt file
    key_path = Path(__file__).parent / "api_key.txt"
    if key_path.exists():
        return key_path.read_text(encoding="utf-8").strip()

    # Finally, prompt the user
    print(f"API Key file not found at {key_path}")
    key = input("Please enter your DeepSeek API Key: ").strip()
    if not key:
        print("Error: API Key is required.")
        sys.exit(1)

    key_path.write_text(key, encoding="utf-8")
    print(f"API Key saved to {key_path}")
    return key


async def process_single_input(agent, user_input):
    import platform
    import datetime
    import os
    import json
    import traceback
    from openai import OpenAIError
    from rich.console import Console
    from rich.live import Live
    from rich.markdown import Markdown
    from rich.panel import Panel

    console = Console()

    # Start logging (optional)
    if hasattr(agent, '_start_logging'):
        agent._start_logging()

    # Build system prompt (same as in chat_loop)
    skill_summaries = []
    for skill in agent.skills:
        skill_summaries.append(f"- {skill.config.name}: {skill.description}")

    current_os = platform.system()
    if current_os == "Darwin":
        current_os = "macOS"

    system_prompt = f"""You are an efficient autonomous agent capable of using tools and skills to solve complex tasks.

## Environment
- Operating System: {current_os}
- Current working directory: {os.getcwd()}
- Current date and time: {datetime.datetime.now().astimezone().strftime('%Y-%m-%d %H:%M:%S %Z')}

## Skill System
You have access to a dynamic skill system via MCP.
Initially, you only have access to "Loader Tools" (e.g., `skill_planner`).
To use specific tools (like `init_planning`), you must FIRST confirm you need that capability by checking the loader description, and then call the loader tool.

## Instructions
1. Analyze the user's request.
2. If you need a specific tool, check if its skill is loaded.
3. If not loaded, call the corresponding `skill_<name>` tool first.
4. Once loaded, you will receive detailed instructions and access to specialized tools in the next turn.
5. Use minimal steps or tool calls to achieve the user's goal.

Keep reasoning chain-of-thought light and concise, avoid overthinking. Focus on practical steps and efficient execution. Always use planner tools to break down complex tasks each time you are assigned something to do.

## Available Skills
{chr(10).join(skill_summaries)}
"""
    # Initialize messages if empty
    if not agent.messages:
        agent.messages.append({"role": "system", "content": system_prompt})
        if hasattr(agent, '_log'):
            agent._log("system", system_prompt)

    # Add user input
    agent.messages.append({"role": "user", "content": user_input})
    if hasattr(agent, '_log'):
        agent._log("user", user_input)

    tool_iterations = 0
    MAX_TOOL_ITERATIONS = 1000  # same as in agent

    while True:
        if tool_iterations >= MAX_TOOL_ITERATIONS:
            console.print(f"[red]Max tool iterations ({MAX_TOOL_ITERATIONS}) reached. Stopping execution.[/]")
            break

        # Check context length (optional)
        if hasattr(agent, '_condense_context'):
            await agent._condense_context()

        # Construct tools list dynamically based on loaded skills
        tools = []
        if hasattr(agent, 'list_tools'):
            tools = await agent.list_tools()

        # Capture reasoning_content for API compliance
        reasoning_storage = ""

        stream = agent.client.chat.completions.create(
            model="deepseek-reasoner",
            messages=agent.messages,
            tools=tools if tools else None,
            stream=True,
        )

        full_content = ""
        tool_calls = []
        current_tool_call = None

        console.print("[yellow]Reasoning:[/yellow]")

        reasoning_mode = True
        live_display = None

        try:
            for chunk in stream:
                # 1. Handle Reasoning
                if hasattr(chunk.choices[0], "delta") and hasattr(
                    chunk.choices[0].delta, "reasoning_content"
                ):
                    reasoning = chunk.choices[0].delta.reasoning_content
                    if reasoning:
                        console.print(reasoning, end="", style="italic dim")
                        reasoning_storage += reasoning

                # 2. Handle Content
                if chunk.choices[0].delta.content:
                    if reasoning_mode and reasoning_storage:
                        console.print("\n\n", end="")  # Switch with newlines
                        reasoning_mode = False

                    if live_display is None:
                        live_display = Live(
                            Markdown(""),
                            console=console,
                            refresh_per_second=4,
                        )
                        live_display.start()

                    content_chunk = chunk.choices[0].delta.content
                    full_content += content_chunk
                    live_display.update(Markdown(full_content))

                # 3. Handle Tool Calls
                if chunk.choices[0].delta.tool_calls:
                    if live_display:
                        live_display.stop()
                        live_display = None

                    for tc in chunk.choices[0].delta.tool_calls:
                        if tc.id:
                            if current_tool_call:
                                tool_calls.append(current_tool_call)
                            current_tool_call = {
                                "id": tc.id,
                                "type": "function",
                                "function": {
                                    "name": tc.function.name,
                                    "arguments": "",
                                },
                            }
                        if tc.function.arguments:
                            current_tool_call["function"][
                                "arguments"
                            ] += tc.function.arguments
        finally:
            if live_display:
                live_display.stop()

        if current_tool_call:
            tool_calls.append(current_tool_call)

        console.print()  # Newline

        # Store assistant message
        assistant_msg = {"role": "assistant", "content": full_content}
        if reasoning_storage:
            assistant_msg["reasoning_content"] = reasoning_storage

        if hasattr(agent, '_log'):
            agent._log(
                "assistant", full_content, reasoning_content=reasoning_storage
            )

        if tool_calls:
            # Reconstruct tool_calls object for history
            assistant_msg["tool_calls"] = [
                {
                    "id": tc["id"],
                    "type": "function",
                    "function": tc["function"],
                }
                for tc in tool_calls
            ]
            for tc in tool_calls:
                if hasattr(agent, '_log'):
                    agent._log(
                        "tool_call",
                        "",
                        tool_name=tc["function"]["name"],
                        arguments=tc["function"]["arguments"],
                    )

        agent.messages.append(assistant_msg)

        if not tool_calls:
            # No tool calls, we have the final answer
            break

        # Execute tools
        for tc in tool_calls:
            fn_name = tc["function"]["name"]
            fn_args_str = tc["function"]["arguments"]
            try:
                fn_args = json.loads(fn_args_str)
                result = await agent.call_tool(fn_name, fn_args)
            except (json.JSONDecodeError, RuntimeError, OpenAIError) as e:
                result = f"Error: {str(e)}"

            console.print(
                Panel(result, title=fn_name, border_style="cyan", height=5)
            )

            agent.messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tc["id"],
                    "content": result,
                }
            )
            if hasattr(agent, '_log'):
                agent._log("tool_result", result, tool_name=fn_name)

        tool_iterations += 1


async def main():
    load_dotenv()
    import sys

    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="DeepSeek MCP Agent with command line support."
    )
    parser.add_argument(
        "-c", "--command", type=str, help="Execute a single command and exit."
    )
    parser.add_argument(
        "-i", "--stdin", action="store_true", help="Read command from standard input."
    )
    args = parser.parse_args()

    # Determine user input
    user_input = None
    if args.stdin:
        # Read from stdin
        import sys

        user_input = sys.stdin.read().strip()
    elif args.command:
        user_input = args.command.strip()

    # 1. Setup Agent
    api_key = get_api_key()
    agent = DeepSeekMCPAgent(api_key=api_key)

    # 2. Setup Servers
    current_dir = Path(__file__).parent
    servers_dir = current_dir / "servers"

    # Scan for servers
    if servers_dir.exists():
        for item in servers_dir.iterdir():
            if item.is_dir():
                skill_path = item / "SKILL.md"
                server_path = item / "server.py"

                if skill_path.exists() and server_path.exists():
                    print(f"Loading server: {item.name}")
                    agent.add_server(
                        name=item.name,
                        skill_md_path=skill_path,
                        command=sys.executable,
                        args=[str(server_path)],
                    )

    # 3. Decide mode
    if user_input is None:
        # Interactive mode
        try:
            await agent.chat_loop()
        except KeyboardInterrupt:
            pass
    else:
        # Command mode: treat user_input as a conversational message
        # Use the same logic as chat_loop but for a single input
        await process_single_input(agent, user_input)
        await agent.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
