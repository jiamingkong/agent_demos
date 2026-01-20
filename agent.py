import asyncio
import datetime
import json
import os
import platform
import traceback
from contextlib import AsyncExitStack
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, cast

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from openai import OpenAI, OpenAIError
from openai.types.chat import (ChatCompletionChunk, ChatCompletionMessageParam,
                               ChatCompletionToolParam)
from rich.console import Console
from rich.live import Live
from rich.markdown import Markdown
from rich.panel import Panel

console = Console()


@dataclass
class MCPSkillConfig:
    name: str  # e.g. "os_manipulation"
    command: str
    args: List[str]
    skill_md_path: Path
    env: Optional[Dict[str, str]] = None


class MCPSkillWrapper:
    def __init__(self, config: MCPSkillConfig):
        self.config = config
        self.loaded = False
        self.session: Optional[ClientSession] = None
        self.tools_cache: List[Dict[str, Any]] = []
        self._description: str = ""
        self._load_metadata()

    def _load_metadata(self):
        """Parse description and prepare context from SKILL.md"""
        if self.config.skill_md_path is None:
            self._description = f"Tools for {self.config.name}"
            self._full_instructions = f"Tools for {self.config.name}"
            return

        if self.config.skill_md_path.exists():
            content = self.config.skill_md_path.read_text(encoding="utf-8")
            self._full_instructions = content

            # Extract description from frontmatter
            desc = ""
            if content.startswith("---"):
                _, frontmatter, _ = content.split("---", 2)
                for line in frontmatter.splitlines():
                    if line.strip().startswith("description:"):
                        desc = line.split(":", 1)[1].strip()
                        break
            self._description = desc or f"Tools for {self.config.name}"
        else:
            self._description = f"Tools for {self.config.name}"
            self._full_instructions = f"Tools for {self.config.name}"

    @property
    def description(self) -> str:
        return self._description

    def get_loader_tool_def(self) -> Dict[str, Any]:
        """Generate the synthetic loader tool definition"""
        # Loading context logic (simplified)
        context = []
        lines = self._full_instructions.split("\n")
        for line in lines:
            if line.strip() == "---":
                continue
            if (
                line.strip().startswith("name:")
                or line.strip().startswith("description:")
                or line.strip().startswith("allowed-tools:")
            ):
                continue
            if line.strip().startswith("##") and ("Tool" in line or "工具" in line):
                break
            context.append(line)

        loading_context = "\n".join(context).strip()
        if len(loading_context) < 10:
            loading_context = self.description

        return {
            "type": "function",
            "function": {
                "name": f"skill_{self.config.name}",
                "description": f"Load {self.config.name} capabilities.\n{loading_context}",
                "parameters": {"type": "object", "properties": {}, "required": []},
            },
        }


class DeepSeekMCPAgent:
    def __init__(self, api_key: str):
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com",
        )
        self.messages: List[Dict[str, Any]] = []
        self.skills: List[MCPSkillWrapper] = []
        self.exit_stack = AsyncExitStack()
        # Logging setup
        self.log_dir = Path(__file__).parent / "artifacts" / "logs"
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.session_id = None
        self.jsonl_file = None
        self.md_file = None
        self.jsonl_handle = None

    CONTEXT_CHAR_LIMIT = 1000000
    CONTEXT_KEEP_LAST_MESSAGES = 10
    MAX_TOOL_ITERATIONS = 1000
    SUMMARY_MODEL = "deepseek-chat"

    def _start_logging(self):
        """Initialize logging for the session"""
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        self.session_id = f"session_{timestamp}"
        self.jsonl_file = self.log_dir / f"{self.session_id}.jsonl"
        self.md_file = self.log_dir / f"{self.session_id}.md"

        assert self.jsonl_file is not None
        self.jsonl_handle = open(self.jsonl_file, "a", encoding="utf-8")

        # Initialize MD file
        assert self.md_file is not None
        with open(self.md_file, "w", encoding="utf-8") as f:
            f.write(f"# Conversation Log: {self.session_id}\n\n")

    def _log(self, role: str, content: str, **kwargs):
        """Log a message to both JSONL and Markdown"""
        entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "role": role,
            "content": content,
            **kwargs,
        }

        # JSONL
        if self.jsonl_handle:
            self.jsonl_handle.write(json.dumps(entry, ensure_ascii=False) + "\n")
            self.jsonl_handle.flush()

        # Markdown
        assert self.md_file is not None
        with open(self.md_file, "a", encoding="utf-8") as f:
            if role == "system":
                f.write(f"## System Prompt\n\n{content}\n\n")
            elif role == "user":
                f.write(f"## User\n\n{content}\n\n")
            elif role == "assistant":
                reasoning = kwargs.get("reasoning_content", "")
                if reasoning:
                    f.write(
                        f"### Reasoning\n> {reasoning.replace(chr(10), chr(10)+'> ')}\n\n"
                    )
                f.write(f"## Assistant\n\n{content}\n\n")
            elif role == "tool_call":
                tool_name = kwargs.get("tool_name")
                args = kwargs.get("arguments")
                f.write(
                    f"### Tool Call: `{tool_name}`\n\nArguments:\n```json\n{args}\n```\n\n"
                )
            elif role == "tool_result":
                tool_name = kwargs.get("tool_name")
                f.write(f"### Tool Output ({tool_name})\n\n```\n{content}\n```\n\n")

    def add_server(
        self,
        name: str,
        skill_md_path: Path,
        command: str,
        args: List[str],
        env: Optional[Dict[str, str]] = None,
    ):
        """Register a server/skill."""
        # Check for duplicate skill names
        for existing in self.skills:
            if existing.config.name == name:
                console.print(
                    f"[yellow]Skill '{name}' already registered, skipping.[/]"
                )
                return
        config = MCPSkillConfig(name, command, args, skill_md_path, env)
        wrapper = MCPSkillWrapper(config)
        self.skills.append(wrapper)

    async def connect_server(self, wrapper: MCPSkillWrapper):
        """Connect to a specific skill's MCP server."""
        if wrapper.session:
            return  # Already connected

        params = StdioServerParameters(
            command=wrapper.config.command,
            args=wrapper.config.args,
            env=wrapper.config.env,
        )

        try:
            read, write = await self.exit_stack.enter_async_context(
                stdio_client(params)
            )
            session = await self.exit_stack.enter_async_context(
                ClientSession(read, write)
            )
            await session.initialize()
            wrapper.session = session
            console.print(f"[green]Connected to MCP skill: {wrapper.config.name}[/]")

            # Cache tools immediately
            mcp_tools = await session.list_tools()
            for tool in mcp_tools.tools:
                tool_def = {
                    "type": "function",
                    "function": {
                        "name": tool.name,
                        "description": tool.description,
                        "parameters": tool.inputSchema,
                    },
                }
                wrapper.tools_cache.append(tool_def)

        except (OSError, RuntimeError, ConnectionError) as e:
            console.print(
                f"[red]Failed to connect to skill {wrapper.config.name}: {e}[/]"
            )

    async def list_tools(self) -> List[Dict[str, Any]]:
        """Query tools based on loading state."""
        combined_tools = []

        for skill in self.skills:
            if not skill.loaded:
                # 1. Not loaded: Show Loader Tool only
                combined_tools.append(skill.get_loader_tool_def())
            else:
                # 2. Loaded: Show actual tools
                # Ensure connected
                if not skill.session:
                    await self.connect_server(skill)
                combined_tools.extend(skill.tools_cache)

        return combined_tools

    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> str:
        """Execute tool (Loader or MCP)."""

        # 1. Check for Loader Tools
        if tool_name.startswith("skill_"):
            skill_name = tool_name.replace("skill_", "")
            for skill in self.skills:
                if skill.config.name == skill_name:
                    # Execute Loading Logic
                    skill.loaded = True
                    await self.connect_server(skill)  # Connect eagerly
                    return skill._full_instructions
            return f"Error: Skill '{skill_name}' not found."

        # 2. Check for MCP Tools
        for skill in self.skills:
            if skill.loaded and skill.session:
                # Check if this skill owns the tool
                # Simple check: name match
                for t in skill.tools_cache:
                    if t["function"]["name"] == tool_name:
                        try:
                            console.print(
                                f"[cyan]{skill.config.name}::{tool_name}({arguments})[/]"
                            )
                            call_result = await skill.session.call_tool(
                                tool_name, arguments
                            )
                            text_content = []
                            for content in call_result.content:
                                if content.type == "text":
                                    text_content.append(content.text)
                            return "\n".join(text_content)
                        except (RuntimeError, KeyError) as e:
                            return f"Error executing {tool_name}: {e}"

        return f"Error: Tool '{tool_name}' not found or skill not loaded."

    async def send_llm_request(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        model: str = "deepseek-reasoner",
    ) -> str:
        """Send a one-off request to LLM without using conversation context.

        Args:
            prompt: The user prompt.
            system_prompt: Optional system prompt. If None, uses a generic one.
            tools: Optional list of tool definitions.
            model: The model to use (default: deepseek-reasoner).

        Returns:
            The LLM's text response (content only). If tool calls are generated,
            they are ignored and only the text content is returned.
        """
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        reasoning_storage = ""
        full_content = ""

        messages_param: List[ChatCompletionMessageParam] = cast(
            List[ChatCompletionMessageParam], messages
        )
        tools_param: Optional[List[ChatCompletionToolParam]] = (
            cast(Optional[List[ChatCompletionToolParam]], tools) if tools else None
        )
        stream = self.client.chat.completions.create(
            model=model,
            messages=messages_param,
            tools=tools_param,  # type: ignore
            stream=True,
        )

        for chunk in stream:  # type: ignore
            chunk = cast(ChatCompletionChunk, chunk)
            # Handle reasoning
            if hasattr(chunk.choices[0], "delta") and hasattr(
                chunk.choices[0].delta, "reasoning_content"
            ):
                reasoning = chunk.choices[0].delta.reasoning_content
                if reasoning:
                    reasoning_storage += reasoning
            # Handle content
            if chunk.choices[0].delta.content:
                content_chunk = chunk.choices[0].delta.content
                full_content += content_chunk

        # If there's reasoning content, we could optionally log it, but ignore for now.
        return full_content

    async def _condense_context(self):
        """Condense message history if it exceeds limit."""
        LIMIT = self.CONTEXT_CHAR_LIMIT
        KEEP_LAST = (
            self.CONTEXT_KEEP_LAST_MESSAGES
        )  # Keep last N messages (approx 5 turns)

        total_chars = sum(
            len(str(m.get("content", ""))) + len(str(m.get("reasoning_content", "")))
            for m in self.messages
        )

        if total_chars > LIMIT and len(self.messages) > KEEP_LAST + 2:
            console.print(
                f"[yellow]Context length ({total_chars}) exceeds limit. Condensing...[/]"
            )

            # Keep system prompt (index 0)
            system_prompt = self.messages[0]

            # Messages to summarize
            to_summarize = self.messages[1:-KEEP_LAST]
            to_keep = self.messages[-KEEP_LAST:]

            # Create summarization text
            text_block = ""
            for msg in to_summarize:
                role = msg.get("role")
                content = msg.get("content", "")
                text_block += f"{role}: {content}\n"

            summary_prompt = f"Summarize the following interaction history concisely, focusing on completed actions, key findings, and current state. Ignore minor details.\n\n{text_block}"

            try:
                # Use a lightweight request for summarization
                summary = await self.send_llm_request(
                    summary_prompt, model=self.SUMMARY_MODEL
                )
            except (OpenAIError, RuntimeError) as e:
                console.print(f"[red]Condensing failed: {e}[/]")
                return

            summary_msg = {
                "role": "user",  # Using user role for summary injection to avoid confusion
                "content": f"## Previous Conversation Summary\n{summary}\n\n(Resume task based on this summary)",
            }

            self.messages = [system_prompt, summary_msg] + to_keep
            console.print("[green]Context condensed successfully.[/]")

    async def chat_loop(self):
        self._start_logging()
        # Initial System Prompt Construction
        skill_summaries = []
        for skill in self.skills:
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
        self.messages.append({"role": "system", "content": system_prompt})
        self._log("system", system_prompt)

        console.print(
            Panel(system_prompt, title="System Prompt", border_style="yellow")
        )
        console.rule("[bold green]DeepSeek Agent (MCP Mode with Dynamic Loading)[/]")

        while True:
            try:
                user_input = console.input("[bold blue]You:[/bold blue] ")
                if user_input.lower() in ["exit", "quit"]:
                    break

                self.messages.append({"role": "user", "content": user_input})
                self._log("user", user_input)

                tool_iterations = 0

                while True:
                    if tool_iterations >= self.MAX_TOOL_ITERATIONS:
                        console.print(
                            f"[red]Max tool iterations ({self.MAX_TOOL_ITERATIONS}) reached. Stopping execution.[/]"
                        )
                        break

                    # Check context length
                    await self._condense_context()

                    # Construct tools list dynamically based on loaded skills
                    tools = await self.list_tools()

                    # Capture reasoning_content for API compliance
                    reasoning_storage = ""

                    stream = self.client.chat.completions.create(
                        model="deepseek-reasoner",
                        messages=self.messages,
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
                                    console.print(
                                        "\n\n", end=""
                                    )  # Switch with newlines
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
                    # Important: For DeepSeek API, if we consumed reasoning, we must include it in history to avoid 400 error
                    assistant_msg = {"role": "assistant", "content": full_content}
                    if reasoning_storage:
                        assistant_msg["reasoning_content"] = reasoning_storage

                    self._log(
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
                            self._log(
                                "tool_call",
                                "",
                                tool_name=tc["function"]["name"],
                                arguments=tc["function"]["arguments"],
                            )

                    self.messages.append(assistant_msg)

                    if not tool_calls:
                        break

                    # Execute tools
                    for tc in tool_calls:
                        fn_name = tc["function"]["name"]
                        fn_args_str = tc["function"]["arguments"]
                        try:
                            fn_args = json.loads(fn_args_str)
                            result = await self.call_tool(fn_name, fn_args)
                        except (json.JSONDecodeError, RuntimeError, OpenAIError) as e:
                            result = f"Error: {str(e)}"

                        console.print(
                            Panel(result, title=fn_name, border_style="cyan", height=5)
                        )

                        self.messages.append(
                            {
                                "role": "tool",
                                "tool_call_id": tc["id"],
                                "content": result,
                            }
                        )
                        self._log("tool_result", result, tool_name=fn_name)

                    tool_iterations += 1
            except Exception as e:
                console.print(f"[red]Error: {traceback.format_exc()}[/]")

    async def cleanup(self):
        if self.jsonl_handle:
            self.jsonl_handle.close()
        await self.exit_stack.aclose()
