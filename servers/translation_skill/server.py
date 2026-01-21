from googletrans import Translator
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("translation_skill", log_level="ERROR")

translator = Translator()


@mcp.tool()
def translate_text(text: str, src: str = "auto", dest: str = "zh-CN") -> str:
    """
    Translate text from one language to another.

    Args:
        text: The text to translate.
        src: Source language code (e.g., 'en', 'auto' for auto‑detect). Default 'auto'.
        dest: Destination language code (e.g., 'zh‑CN', 'es', 'fr'). Default 'zh‑CN'.

    Returns:
        Translated text and detected source language.
    """
    try:
        translation = translator.translate(text, src=src, dest=dest)
        result = f"Translated from '{translation.src}' to '{dest}': {translation.text}"
        return result
    except Exception as e:
        return f"Translation failed: {e}"


if __name__ == "__main__":
    mcp.run()
