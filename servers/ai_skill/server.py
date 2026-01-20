"""
AI skill: OpenAI API wrappers.
Requires openai library (version >= 1.0).
"""

import json
import os
from typing import Optional

from mcp.server.fastmcp import FastMCP
from openai import OpenAI

mcp = FastMCP("ai", log_level="ERROR")

# Initialize OpenAI client with API key from environment
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    print("WARNING: OPENAI_API_KEY environment variable not set.")
client = OpenAI(api_key=api_key)


@mcp.tool()
def openai_chat_completion(
    model: str,
    messages: str,
    temperature: Optional[float] = 1.0,
    max_tokens: Optional[int] = None,
) -> str:
    """
    Generate a chat completion.

    Args:
        model: Model identifier.
        messages: JSON string of message objects, e.g.
            '[{"role": "user", "content": "Hello"}]'
        temperature: Sampling temperature.
        max_tokens: Maximum tokens to generate.
    """
    try:
        messages_list = json.loads(messages)
        response = client.chat.completions.create(
            model=model,
            messages=messages_list,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error in chat completion: {e}"


@mcp.tool()
def openai_generate_image(
    prompt: str,
    size: Optional[str] = "1024x1024",
    quality: Optional[str] = "standard",
    n: Optional[int] = 1,
) -> str:
    """
    Generate images with DALL‑E.

    Args:
        prompt: Text prompt.
        size: Image size.
        quality: "standard" or "hd".
        n: Number of images.
    """
    try:
        response = client.images.generate(
            prompt=prompt, size=size, quality=quality, n=n
        )
        urls = [img.url for img in response.data]
        return f"Generated {len(urls)} image(s):\n" + "\n".join(urls)
    except Exception as e:
        return f"Error generating image: {e}"


@mcp.tool()
def openai_transcribe_audio(file_path: str, model: Optional[str] = "whisper-1") -> str:
    """
    Transcribe audio to text.

    Args:
        file_path: Path to audio file.
        model: Whisper model.
    """
    try:
        with open(file_path, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                file=audio_file, model=model
            )
        return transcript.text
    except Exception as e:
        return f"Error transcribing audio: {e}"


@mcp.tool()
def openai_embedding(text: str, model: Optional[str] = "text-embedding-3-small") -> str:
    """
    Get embedding vector.

    Args:
        text: Input text.
        model: Embedding model.
    """
    try:
        response = client.embeddings.create(input=text, model=model)
        embedding = response.data[0].embedding
        # Return first 5 values as preview
        preview = embedding[:5]
        return f"Embedding dimension: {len(embedding)}\nFirst 5 values: {preview}"
    except Exception as e:
        return f"Error generating embedding: {e}"
