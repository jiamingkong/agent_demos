import json
import requests
from typing import Optional, Dict, Any
from mcp.server import Server
import mcp.server.stdio
import mcp.types as types

app = Server("notification_skill")

@app.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """Return the list of tools provided by this skill."""
    return [
        types.Tool(
            name="send_slack_message",
            description="Send a message to a Slack channel.",
            inputSchema={
                "type": "object",
                "properties": {
                    "token": {"type": "string", "description": "Slack bot token"},
                    "channel": {"type": "string", "description": "Channel ID or name"},
                    "text": {"type": "string", "description": "Message text"},
                    "blocks": {"type": "string", "description": "Optional Slack blocks JSON"},
                },
                "required": ["token", "channel", "text"],
            },
        ),
        types.Tool(
            name="send_telegram_message",
            description="Send a message via a Telegram bot.",
            inputSchema={
                "type": "object",
                "properties": {
                    "bot_token": {"type": "string", "description": "Telegram bot token"},
                    "chat_id": {"type": "string", "description": "Target chat ID"},
                    "text": {"type": "string", "description": "Message text"},
                    "parse_mode": {"type": "string", "description": "Markdown or HTML"},
                },
                "required": ["bot_token", "chat_id", "text"],
            },
        ),
        types.Tool(
            name="send_discord_message",
            description="Send a message to a Discord channel via webhook.",
            inputSchema={
                "type": "object",
                "properties": {
                    "webhook_url": {"type": "string", "description": "Discord webhook URL"},
                    "content": {"type": "string", "description": "Message content"},
                    "username": {"type": "string", "description": "Override username"},
                    "avatar_url": {"type": "string", "description": "Override avatar URL"},
                },
                "required": ["webhook_url", "content"],
            },
        ),
        types.Tool(
            name="send_webhook",
            description="Send a generic HTTP POST request to a webhook URL.",
            inputSchema={
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "Target URL"},
                    "method": {"type": "string", "description": "HTTP method", "default": "POST"},
                    "payload": {"type": "string", "description": "JSON payload string"},
                    "headers": {"type": "string", "description": "JSON object of headers"},
                },
                "required": ["url", "payload"],
            },
        ),
    ]

@app.call_tool()
async def handle_call_tool(
    name: str, arguments: Dict[str, Any]
) -> list[types.TextContent]:
    """Execute the requested tool."""
    if name == "send_webhook":
        url = arguments["url"]
        method = arguments.get("method", "POST").upper()
        payload_str = arguments["payload"]
        headers_str = arguments.get("headers", "{}")
        try:
            payload = json.loads(payload_str)
            headers = json.loads(headers_str)
        except json.JSONDecodeError as e:
            return [types.TextContent(type="text", text=f"Error: Invalid JSON: {e}")]

        try:
            response = requests.request(method, url, json=payload, headers=headers, timeout=10)
            response.raise_for_status()
            return [types.TextContent(type="text", text=f"Success: {response.status_code} {response.text}")]
        except requests.exceptions.RequestException as e:
            return [types.TextContent(type="text", text=f"Error: {e}")]

    elif name == "send_slack_message":
        token = arguments["token"]
        channel = arguments["channel"]
        text = arguments["text"]
        blocks = arguments.get("blocks")
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        payload = {"channel": channel, "text": text}
        if blocks:
            try:
                payload["blocks"] = json.loads(blocks)
            except json.JSONDecodeError:
                return [types.TextContent(type="text", text="Error: Invalid blocks JSON")]
        try:
            response = requests.post("https://slack.com/api/chat.postMessage", json=payload, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            if data.get("ok"):
                return [types.TextContent(type="text", text=f"Message sent: {data.get('ts')}")]
            else:
                return [types.TextContent(type="text", text=f"Slack error: {data.get('error')}")]
        except requests.exceptions.RequestException as e:
            return [types.TextContent(type="text", text=f"Error: {e}")]

    elif name == "send_telegram_message":
        bot_token = arguments["bot_token"]
        chat_id = arguments["chat_id"]
        text = arguments["text"]
        parse_mode = arguments.get("parse_mode")
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        payload = {"chat_id": chat_id, "text": text}
        if parse_mode:
            payload["parse_mode"] = parse_mode
        try:
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()
            data = response.json()
            if data.get("ok"):
                return [types.TextContent(type="text", text=f"Message sent: message_id {data['result']['message_id']}")]
            else:
                return [types.TextContent(type="text", text=f"Telegram error: {data.get('description')}")]
        except requests.exceptions.RequestException as e:
            return [types.TextContent(type="text", text=f"Error: {e}")]

    elif name == "send_discord_message":
        webhook_url = arguments["webhook_url"]
        content = arguments["content"]
        username = arguments.get("username")
        avatar_url = arguments.get("avatar_url")
        payload = {"content": content}
        if username:
            payload["username"] = username
        if avatar_url:
            payload["avatar_url"] = avatar_url
        try:
            response = requests.post(webhook_url, json=payload, timeout=10)
            response.raise_for_status()
            return [types.TextContent(type="text", text=f"Discord webhook sent: {response.status_code}")]
        except requests.exceptions.RequestException as e:
            return [types.TextContent(type="text", text=f"Error: {e}")]

    else:
        return [types.TextContent(type="text", text=f"Unknown tool: {name}")]

async def main():
    """Run the server over stdio."""
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
