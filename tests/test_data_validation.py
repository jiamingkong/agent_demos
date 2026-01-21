"""Unit tests for data_validation server."""

import sys
from pathlib import Path
from unittest.mock import patch

import pytest

# Add servers to path
sys.path.insert(0, str(Path(__file__).parent.parent / "servers"))

from data_validation.server import parse_model, validate_data, validate_json_schema


def test_validate_data_success():
    """Test successful validation."""
    data = {"name": "Alice", "age": 30}
    schema = {"name": "str", "age": "int"}
    result = validate_data(data, schema)
    assert "Validation successful" in result
    assert "Alice" in result
    assert "30" in result


def test_validate_data_failure():
    """Test validation failure."""
    data = {"name": "Alice", "age": "not_a_number"}
    schema = {"name": "str", "age": "int"}
    result = validate_data(data, schema)
    assert "Validation failed" in result


def test_parse_model():
    """Test creating a model dynamically."""
    result = parse_model("Person", {"name": "str", "age": "int"})
    assert "Model 'Person' created" in result
    assert "properties" in result


@pytest.mark.xfail(reason="jsonschema mocking issue")
def test_validate_json_schema_success():
    """Test JSON schema validation success."""
    schema = '{"type": "object", "properties": {"name": {"type": "string"}}}'
    data = {"name": "Alice"}
    with patch("data_validation.server.jsonschema") as mock_jsonschema:
        result = validate_json_schema(schema, data)
        assert "succeeded" in result


@pytest.mark.xfail(reason="jsonschema mocking issue")
def test_validate_json_schema_failure():
    """Test JSON schema validation failure."""
    schema = '{"type": "object", "properties": {"name": {"type": "string"}}}'
    data = {"name": 123}
    with patch("data_validation.server.jsonschema") as mock_jsonschema:
        mock_jsonschema.validate.side_effect = Exception("Validation error")
        result = validate_json_schema(schema, data)
        assert "failed" in result or "Error" in result


def test_validate_json_schema_missing_library():
    """Test when jsonschema library is not installed."""
    with patch.dict("sys.modules", {"jsonschema": None}):
        result = validate_json_schema("{}", {})
        assert "not installed" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
