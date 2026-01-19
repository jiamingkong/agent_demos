"""Unit tests for main.py."""

import asyncio
import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest

# Import the module to test
sys.path.insert(0, str(Path(__file__).parent.parent))
from main import get_api_key, main


def test_get_api_key_file_exists():
    """Test get_api_key when api_key.txt exists."""
    with patch("main.Path") as MockPath:
        # Create a mock that simulates Path(__file__).parent / "api_key.txt"
        mock_file_path = MagicMock()
        mock_file_path.exists.return_value = True
        mock_file_path.read_text.return_value = "fake-api-key-123\n"

        mock_parent = MagicMock()
        mock_parent.__truediv__.return_value = mock_file_path

        mock_path_instance = MagicMock()
        mock_path_instance.parent = mock_parent
        MockPath.return_value = mock_path_instance

        result = get_api_key()

        assert result == "fake-api-key-123"
        mock_file_path.read_text.assert_called_once_with(encoding="utf-8")
        mock_file_path.exists.assert_called_once()


def test_get_api_key_file_not_exists():
    """Test get_api_key when api_key.txt does not exist, with user input."""
    with patch("main.Path") as MockPath:
        # Simulate file not existing
        mock_file_path = MagicMock()
        mock_file_path.exists.return_value = False
        mock_file_path.write_text = MagicMock()

        mock_parent = MagicMock()
        mock_parent.__truediv__.return_value = mock_file_path

        mock_path_instance = MagicMock()
        mock_path_instance.parent = mock_parent
        MockPath.return_value = mock_path_instance

        with patch("builtins.input", return_value="user-input-key"):
            result = get_api_key()

            assert result == "user-input-key"
            mock_file_path.write_text.assert_called_once_with(
                "user-input-key", encoding="utf-8"
            )


def test_get_api_key_empty_input():
    """Test get_api_key when user input is empty (should exit)."""
    with patch("main.Path") as MockPath:
        mock_file_path = MagicMock()
        mock_file_path.exists.return_value = False

        mock_parent = MagicMock()
        mock_parent.__truediv__.return_value = mock_file_path

        mock_path_instance = MagicMock()
        mock_path_instance.parent = mock_parent
        MockPath.return_value = mock_path_instance

        with patch("builtins.input", return_value=""):
            with patch("sys.exit") as mock_exit:
                get_api_key()
                mock_exit.assert_called_once_with(1)


@pytest.mark.asyncio
async def test_main_without_servers_dir():
    """Test main function when servers directory does not exist."""
    with patch("main.load_dotenv"):
        with patch("main.get_api_key", return_value="fake-key"):
            with patch("main.DeepSeekMCPAgent") as MockAgent:
                mock_agent = AsyncMock()
                MockAgent.return_value = mock_agent

                # Mock Path for current directory and servers directory
                with patch("main.Path") as MockPath:
                    # Create mock for current_dir
                    mock_current = MagicMock()
                    # Create mock for servers_dir
                    mock_servers = MagicMock()
                    mock_servers.exists.return_value = False
                    mock_current.__truediv__.return_value = mock_servers
                    MockPath.return_value = mock_current

                    await main()

                    # Verify agent.chat_loop was called (async)
                    mock_agent.chat_loop.assert_awaited_once()


@pytest.mark.asyncio
async def test_main_with_servers():
    """Test main function with existing servers."""
    with patch("main.load_dotenv"):
        with patch("main.get_api_key", return_value="fake-key"):
            with patch("main.DeepSeekMCPAgent") as MockAgent:
                mock_agent = AsyncMock()
                mock_agent.add_server = Mock()
                MockAgent.return_value = mock_agent

                with patch("main.Path") as MockPath:
                    # Mock Path(__file__) -> parent -> / "servers"
                    mock_servers_dir = MagicMock()
                    mock_servers_dir.exists.return_value = True

                    # Mock directory item
                    mock_item = MagicMock()
                    mock_item.is_dir.return_value = True
                    mock_item.name = "planner"

                    mock_skill_path = MagicMock()
                    mock_skill_path.exists.return_value = True
                    mock_server_path = MagicMock()
                    mock_server_path.exists.return_value = True

                    # Simulate __truediv__ calls for item / "SKILL.md" and item / "server.py"
                    def side_effect_div(arg):
                        if arg == "SKILL.md":
                            return mock_skill_path
                        elif arg == "server.py":
                            return mock_server_path
                        else:
                            raise ValueError(f"Unexpected argument: {arg}")

                    mock_item.__truediv__.side_effect = side_effect_div
                    mock_servers_dir.iterdir.return_value = [mock_item]

                    # Now create the chain: Path(__file__) -> parent -> / "servers"
                    mock_path_instance = MagicMock()
                    mock_parent = MagicMock()
                    mock_parent.__truediv__.return_value = mock_servers_dir
                    mock_path_instance.parent = mock_parent
                    MockPath.return_value = mock_path_instance

                    with patch("sys.executable", "/usr/bin/python"):
                        await main()

                        # Verify agent.add_server called with correct args
                        mock_agent.add_server.assert_called_once_with(
                            name="planner",
                            skill_md_path=mock_skill_path,
                            command="/usr/bin/python",
                            args=[str(mock_server_path)],
                        )
                        # Additional checks
                        mock_skill_path.exists.assert_called_once()
                        mock_server_path.exists.assert_called_once()
                        mock_agent.chat_loop.assert_awaited_once()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
