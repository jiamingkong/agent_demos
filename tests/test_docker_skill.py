"""Unit tests for docker_skill server."""

import sys
from pathlib import Path

# Add servers to path
sys.path.insert(0, str(Path(__file__).parent.parent / "servers"))

from docker_skill.server import (
    docker_images,
    docker_logs,
    docker_ps,
    docker_run,
    docker_stop,
)


def test_docker_ps():
    """Test listing containers."""
    result = docker_ps()
    assert isinstance(result, dict)
    assert "success" in result
    assert "stdout" in result
    assert "stderr" in result
    assert "returncode" in result
    # If Docker is not installed, success should be False
    # but we don't assume either way


def test_docker_images():
    """Test listing images."""
    result = docker_images()
    assert isinstance(result, dict)
    assert "success" in result
    if result["success"] and result["stdout"]:
        # If there are images, there should be an 'images' key
        assert "images" in result
        assert isinstance(result["images"], list)


def test_docker_run():
    """Test running a container (should fail without image)."""
    # Without a valid image, Docker will fail but we still get a dict
    result = docker_run(image="nonexistent_image_xyz123")
    assert isinstance(result, dict)
    assert "success" in result
    # Likely false because image doesn't exist
    # But we only check structure


def test_docker_stop():
    """Test stopping a container (invalid container)."""
    result = docker_stop("nonexistent_container")
    assert isinstance(result, dict)
    assert "success" in result


def test_docker_logs():
    """Test fetching logs (invalid container)."""
    result = docker_logs("nonexistent_container", tail=5)
    assert isinstance(result, dict)
    assert "success" in result
