"""Unit tests for configuration server."""

import json
import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest
import yaml

# Add servers to path
sys.path.insert(0, str(Path(__file__).parent.parent / "servers"))

from configuration.server import get_env_var, read_config, set_env_var, write_config


def test_read_config_env():
    """Test reading .env file."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as f:
        f.write("KEY1=value1\nKEY2=value2\n")
        env_path = f.name
    try:
        result = read_config(env_path, format="env")
        assert "KEY1" in result
        assert "value1" in result
    finally:
        os.unlink(env_path)


def test_read_config_json():
    """Test reading JSON file."""
    data = {"name": "test", "value": 42}
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(data, f)
        json_path = f.name
    try:
        result = read_config(json_path, format="json")
        assert "test" in result
        assert "42" in result
    finally:
        os.unlink(json_path)


def test_read_config_yaml():
    """Test reading YAML file."""
    data = {"name": "yaml", "list": [1, 2, 3]}
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        yaml.dump(data, f)
        yaml_path = f.name
    try:
        result = read_config(yaml_path, format="yaml")
        assert "yaml" in result
        assert "list" in result
    finally:
        os.unlink(yaml_path)


def test_write_config_env():
    """Test writing .env file."""
    with tempfile.NamedTemporaryFile(suffix=".env", delete=False) as f:
        env_path = f.name
    try:
        data = {"VAR1": "val1", "VAR2": "val2"}
        result = write_config(env_path, data, format="env")
        assert "Successfully" in result
        with open(env_path, "r") as f:
            content = f.read()
            assert "VAR1=val1" in content
    finally:
        os.unlink(env_path)


def test_write_config_json():
    """Test writing JSON file."""
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
        json_path = f.name
    try:
        data = {"key": "value"}
        result = write_config(json_path, data, format="json")
        assert "Successfully" in result
        with open(json_path, "r") as f:
            loaded = json.load(f)
            assert loaded["key"] == "value"
    finally:
        os.unlink(json_path)


def test_get_env_var():
    """Test getting environment variable."""
    os.environ["TEST_VAR"] = "test_value"
    result = get_env_var("TEST_VAR")
    assert "test_value" in result


def test_get_env_var_default():
    """Test getting environment variable with default."""
    result = get_env_var("NONEXISTENT", default="default_value")
    assert "default_value" in result


def test_set_env_var():
    """Test setting environment variable."""
    result = set_env_var("MY_VAR", "my_value")
    assert "Set environment variable" in result
    assert os.getenv("MY_VAR") == "my_value"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
