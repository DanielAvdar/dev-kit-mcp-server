"""Tests for the FastMCP server."""

import asyncio
import os
import tempfile
from unittest.mock import MagicMock, patch

import pytest

from py_code.fastmcp_server import start_server


@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


class TestFastMCPServer:
    """Tests for the FastMCP server."""

    @patch("argparse.ArgumentParser.parse_args")
    def test_start_server_with_default_root_dir(self, mock_parse_args, temp_dir):
        """Test starting the server with the default root directory."""
        # Arrange
        mock_args = MagicMock()
        mock_args.root_dir = os.getcwd()
        mock_parse_args.return_value = mock_args

        # Act
        server = start_server()

        # Assert
        assert server is not None
        assert server.name == "Python Code MCP Server"

        # Check that the tools were registered
        # Since list_tools is a coroutine, we need to run it in an event loop
        tools = asyncio.run(server.list_tools())
        tool_names = [tool.name for tool in tools]
        assert "create_dir_tool" in tool_names
        assert "move_dir_tool" in tool_names
        assert "remove_file_tool" in tool_names

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
        assert server.name == "Python Code MCP Server"

        # Check that the tools were registered
        # Since list_tools is a coroutine, we need to run it in an event loop
        tools = asyncio.run(server.list_tools())
        tool_names = [tool.name for tool in tools]
        assert "create_dir_tool" in tool_names
        assert "move_dir_tool" in tool_names
        assert "remove_file_tool" in tool_names

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
