---
name: ai
description: OpenAI API capabilities (chat, image generation, transcription, embeddings).
allowed-tools:
  - openai_chat_completion
  - openai_generate_image
  - openai_transcribe_audio
  - openai_embedding
---

# AI Skill

This skill enables the agent to call OpenAI's APIs for various AI tasks.

## Prerequisites

- OpenAI API key set as environment variable `OPENAI_API_KEY`.
- The `openai` Python package (already installed).

## Tools

### openai_chat_completion
Generate a chat completion using OpenAI's Chat API.
- `model`: Model name (e.g., "gpt-4", "gpt-3.5-turbo").
- `messages`: JSON string representing a list of message objects (role, content).
- `temperature`: Sampling temperature (0–2).
- `max_tokens`: Maximum tokens to generate.

### openai_generate_image
Generate images using DALL‑E.
- `prompt`: Text description of the desired image.
- `size`: Image size ("256x256", "512x512", "1024x1024", "1792x1024", "1024x1792").
- `quality`: Quality ("standard" or "hd").
- `n`: Number of images (1‑10).

### openai_transcribe_audio
Transcribe audio to text using Whisper.
- `file_path`: Path to audio file (mp3, wav, m4a, etc.).
- `model`: Whisper model ("whisper-1").

### openai_embedding
Get embedding vector for a text.
- `text`: Input text.
- `model`: Embedding model ("text-embedding-3-small", "text-embedding-3‑large", etc.).
