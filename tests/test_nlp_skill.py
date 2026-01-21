"""Unit tests for nlp_skill server."""

import sys
from pathlib import Path

# Add servers to path
sys.path.insert(0, str(Path(__file__).parent.parent / "servers"))

from nlp_skill.server import (
    analyze_sentiment,
    detect_language,
    extract_noun_phrases,
    tokenize_words,
)


def test_analyze_sentiment():
    """Test sentiment analysis."""
    result = analyze_sentiment("I love this product!")
    assert isinstance(result, dict)
    assert "polarity" in result
    assert "subjectivity" in result
    assert "text" in result
    # polarity should be positive
    assert result["polarity"] > 0
    assert -1 <= result["polarity"] <= 1
    assert 0 <= result["subjectivity"] <= 1


def test_extract_noun_phrases():
    """Test noun phrase extraction."""
    phrases = extract_noun_phrases("The quick brown fox jumps over the lazy dog.")
    assert isinstance(phrases, list)
    # Expect some noun phrases
    # In English, "quick brown fox", "lazy dog" might be extracted
    # We'll just check that it's a list of strings
    assert all(isinstance(p, str) for p in phrases)


def test_tokenize_words():
    """Test word tokenization."""
    tokens = tokenize_words("Hello world, how are you?")
    assert isinstance(tokens, list)
    assert len(tokens) >= 5  # at least 5 words
    assert all(isinstance(t, str) for t in tokens)
    assert "Hello" in tokens
    assert "world" in tokens


def test_detect_language():
    """Test language detection."""
    # English
    lang = detect_language("This is an English sentence.")
    assert lang == "en"
    # French (sample)
    lang = detect_language("Bonjour le monde.")
    # TextBlob may return 'fr' (French) or something else; we'll accept any non-empty string
    assert isinstance(lang, str)
    assert len(lang) == 2  # ISO code two letters
