"""Tests for the FastMCP server."""

import asyncio
import os
from unittest.mock import MagicMock, patch

import pytest

from dev_kit_mcp_server.fastmcp_server import start_server

# @pytest.fixture
# def temp_dir(tmp_path) -> str:
#     """Create a temporary directory for testing."""
#     Repo.init(tmp_path)
#     return Path(tmp_path).as_posix()


class TestFastMCPServer:
    """Tests for the FastMCP server."""

    @patch("argparse.ArgumentParser.parse_args")
    def test_start_server_with_default_root_dir(self, mock_parse_args, temp_dir):
        """Test starting the server with the default root directory."""
        # Arrange
        mock_args = MagicMock()
        mock_args.root_dir = temp_dir
        mock_parse_args.return_value = mock_args

        # Act
        server = start_server()

        # Assert
        assert server is not None
        assert server.name == "Dev-Kit MCP Server"

        # Check that the tools were registered
        # Since list_tools is a coroutine, we need to run it in an event loop
        tools = asyncio.run(server.get_tools())
        tool_names = [tool.name for tool in tools.values()]
        assert "create_dir" in tool_names
        assert "move_dir" in tool_names
        assert "remove_file" in tool_names

    @patch("argparse.ArgumentParser.parse_args")
    def test_start_server_with_custom_root_dir(self, mock_parse_args, temp_dir):
        """Test starting the server with a custom root directory."""
        # Arrange
        mock_args = MagicMock()
        mock_args.root_dir = temp_dir
        mock_parse_args.return_value = mock_args

        # Act
        server = start_server()

        # Assert
        assert server is not None
        assert server.name == "Dev-Kit MCP Server"

        # Check that the tools were registered
        # Since list_tools is a coroutine, we need to run it in an event loop
        tools = asyncio.run(server.get_tools())
        tool_names = [tool.name for tool in tools.values()]
        assert "create_dir" in tool_names
        assert "move_dir" in tool_names
        assert "remove_file" in tool_names

    @patch("argparse.ArgumentParser.parse_args")
    def test_start_server_with_nonexistent_root_dir(self, mock_parse_args):
        """Test starting the server with a non-existent root directory."""
        # Arrange
        mock_args = MagicMock()
        mock_args.root_dir = "/nonexistent/directory"
        mock_parse_args.return_value = mock_args

        # Act & Assert
        with pytest.raises(ValueError, match="Root directory does not exist"):
            start_server()

    @patch("argparse.ArgumentParser.parse_args")
    def test_start_server_with_file_as_root_dir(self, mock_parse_args, temp_dir):
        """Test starting the server with a file as the root directory."""
        # Arrange
        test_file = os.path.join(temp_dir, "test_file.txt")
        with open(test_file, "w") as f:
            f.write("Test content")

        mock_args = MagicMock()
        mock_args.root_dir = test_file
        mock_parse_args.return_value = mock_args

        # Act & Assert
        with pytest.raises(ValueError, match="Root directory is not a directory"):
            start_server()
