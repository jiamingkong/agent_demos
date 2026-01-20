---
name: notification_skill
description: Send notifications to various platforms (Slack, Telegram, Discord, webhooks).
tools:
  - send_slack_message
  - send_telegram_message
  - send_discord_message
  - send_webhook
---

# Notification Skill

This skill enables the agent to send notifications to messaging platforms and webhooks.

## Prerequisites

- `requests` library (already installed)
- For Slack: a Slack app token with `chat:write` permission.
- For Telegram: a bot token obtained via BotFather.
- For Discord: a webhook URL from Discord channel settings.
- For generic webhooks: a target URL.

## Tools

### send_slack_message
Send a message to a Slack channel.

Args:
- `token`: Slack bot token (or app-level token).
- `channel`: Channel ID or name (e.g., "#general").
- `text`: Message text.
- `blocks`: Optional JSON string of Slack blocks.

### send_telegram_message
Send a message via a Telegram bot.

Args:
- `bot_token`: Telegram bot token.
- `chat_id`: Target chat ID (numeric or @username).
- `text`: Message text.
- `parse_mode`: Optional, "Markdown" or "HTML".

### send_discord_message
Send a message to a Discord channel via webhook.

Args:
- `webhook_url`: Discord webhook URL.
- `content`: Message content (text).
- `username`: Optional override of the webhook username.
- `avatar_url`: Optional override of the avatar URL.

### send_webhook
Send a generic HTTP POST request to a webhook URL.

Args:
- `url`: Target URL.
- `method`: HTTP method (default "POST").
- `payload`: JSON payload as a string.
- `headers`: Optional JSON object of HTTP headers.

## Notes

- Tokens and secrets should be provided by the user; the skill does not store them.
- Error responses are returned as plain text.
- For Slack and Telegram, the skill uses the official API endpoints.
- For Discord, the skill uses the webhook API.
