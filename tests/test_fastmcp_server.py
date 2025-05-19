"""Tests for the FastMCP server."""

import asyncio
import os
from unittest.mock import MagicMock, patch

import pytest

from dev_kit_mcp_server.fastmcp_server import arun_server, run_server, start_server


@pytest.mark.parametrize(
    "root_dir_type,expected_error",
    [
        ("valid", None),
        ("nonexistent", "Root directory does not exist"),
        ("file", "Root directory is not a directory"),
    ],
    ids=["valid_dir", "nonexistent_dir", "file_as_dir"],
)
@patch("argparse.ArgumentParser.parse_args")
def test_start_server(mock_parse_args, root_dir_type, expected_error, temp_dir):
    """Test starting the server with different root directory configurations."""
    # Arrange
    mock_args = MagicMock()
    if root_dir_type == "valid":
        mock_args.root_dir = temp_dir
    elif root_dir_type == "nonexistent":
        mock_args.root_dir = "/nonexistent/directory"
    elif root_dir_type == "file":
        test_file = os.path.join(temp_dir, "test_file.txt")
        with open(test_file, "w") as f:
            f.write("Test content")
        mock_args.root_dir = test_file
    mock_parse_args.return_value = mock_args

    # Act & Assert
    if expected_error:
        with pytest.raises(ValueError, match=expected_error):
            start_server()
    else:
        server = start_server()
        assert server is not None
        assert server.name == "Dev-Kit MCP Server"
        # Check that the tools were registered
        tools = asyncio.run(server.get_tools())
        tool_names = [tool.name for tool in tools.values()]
        assert all(name in tool_names for name in ["create_dir", "move_dir", "remove_file"])


@pytest.mark.parametrize(
    "instance_provided,side_effect",
    [(False, None), (True, None), (False, KeyboardInterrupt())],
    ids=["normal", "with_instance", "keyboard_interrupt"],
)
@patch("dev_kit_mcp_server.fastmcp_server.start_server")
@patch("sys.exit")
def test_run_server(mock_exit, mock_start_server, instance_provided, side_effect):
    """Test running the server with different scenarios."""
    # Arrange
    mock_fastmcp = MagicMock()
    if side_effect:
        mock_fastmcp.run.side_effect = side_effect
    mock_start_server.return_value = mock_fastmcp

    # Act & Assert
    run_server(mock_fastmcp if instance_provided else None)
    assert mock_start_server.called != instance_provided
    mock_fastmcp.run.assert_called_once()
    mock_exit.assert_called_once_with(0)


@pytest.mark.parametrize(
    "instance_provided,side_effect,exit_code",
    [(False, None, 0), (True, None, 0), (False, KeyboardInterrupt(), 0), (False, Exception("Test error"), 1)],
    ids=["normal", "with_instance", "keyboard_interrupt", "exception"],
)
@patch("dev_kit_mcp_server.fastmcp_server.start_server")
@patch("asyncio.run")
@patch("sys.exit")
@patch("builtins.print")
def test_arun_server(
    mock_print, mock_exit, mock_asyncio_run, mock_start_server, instance_provided, side_effect, exit_code
):
    """Test running the server asynchronously with different scenarios."""
    # Arrange
    mock_fastmcp = MagicMock()
    if side_effect:
        mock_asyncio_run.side_effect = side_effect
    mock_start_server.return_value = mock_fastmcp

    # Act & Assert
    arun_server(mock_fastmcp if instance_provided else None)
    assert mock_start_server.called != instance_provided
    mock_fastmcp.run_async.assert_called_once()
    if isinstance(side_effect, Exception) and not isinstance(side_effect, KeyboardInterrupt):
        mock_print.assert_called_once_with(f"Error: {side_effect}")
    mock_exit.assert_called_once_with(exit_code)
