import json

from servers.regex_skill.server import (
    regex_extract,
    regex_match,
    regex_replace,
    regex_search,
)


def test_regex_match():
    """Test regex_match."""
    pattern = r"\d+"
    text = "There are 123 apples and 456 bananas."
    result = regex_match(pattern, text)
    matches = json.loads(result)
    assert "123" in matches
    assert "456" in matches


def test_regex_search():
    """Test regex_search."""
    pattern = r"(\d+)\s+(\w+)"
    text = "Total 100 items"
    result = regex_search(pattern, text)
    data = json.loads(result)
    assert data["group"] == "100 items"
    assert data["groups"] == ["100", "items"]


def test_regex_replace():
    """Test regex_replace."""
    pattern = r"\d+"
    replacement = "#"
    text = "There are 123 apples and 456 bananas."
    result = regex_replace(pattern, replacement, text)
    assert result == "There are # apples and # bananas."


def test_regex_extract():
    """Test regex_extract with groups."""
    pattern = r"(\d+)\s+(\w+)"
    text = "Take 5 apples and 10 oranges"
    result = regex_extract(pattern, text)
    extracted = json.loads(result)
    # Expect flattened groups: ["5", "apples", "10", "oranges"]? Actually findall returns tuples.
    # Our implementation flattens tuples.
    assert "5" in extracted
    assert "apples" in extracted
    assert "10" in extracted
    assert "oranges" in extracted
