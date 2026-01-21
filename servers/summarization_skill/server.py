import nltk
from mcp.server.fastmcp import FastMCP
from sumy.nlp.stemmers import Stemmer
from sumy.nlp.tokenizers import Tokenizer
from sumy.parsers.plaintext import PlaintextParser
from sumy.summarizers.lsa import LsaSummarizer
from sumy.utils import get_stop_words

mcp = FastMCP("summarization_skill", log_level="ERROR")

# Ensure NLTK punkt tokenizer is available
try:
    nltk.data.find("tokenizers/punkt")
except LookupError:
    nltk.download("punkt", quiet=True)


@mcp.tool()
def summarize_text(
    text: str, sentence_count: int = 3, language: str = "english"
) -> str:
    """
    Summarize a text using the LSA (Latent Semantic Analysis) algorithm.

    Args:
        text: The text to summarize.
        sentence_count: Number of sentences in the summary (default 3).
        language: Language code for tokenization (e.g., 'english', 'chinese'). Default 'english'.

    Returns:
        The summary as a single string.
    """
    if not text.strip():
        return "Error: Text cannot be empty."

    try:
        parser = PlaintextParser.from_string(text, Tokenizer(language))
        stemmer = Stemmer(language)
        summarizer = LsaSummarizer(stemmer)
        summarizer.stop_words = get_stop_words(language)

        sentences = summarizer(parser.document, sentence_count)
        summary = " ".join(str(sentence) for sentence in sentences)
        return summary
    except Exception as e:
        return f"Summarization failed: {e}"


if __name__ == "__main__":
    mcp.run()
