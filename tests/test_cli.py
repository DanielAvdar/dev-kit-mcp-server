"""Tests for the CLI module."""

import sys
from unittest.mock import patch

import pytest

from py_code.cli import main


@pytest.fixture
def mock_start_server():
    """Mock the server start functions."""
    with patch("py_code.fastmcp_server.start_server") as mock_fastmcp:
        yield {"fastmcp": mock_fastmcp}


def test_cli_with_working_dir(mock_start_server):
    """Test CLI with working directory."""
    # Simulate CLI call with working directory
    with patch.object(sys, "argv", ["py_code.cli", "--working-dir", "."]), patch("os.path.isdir", return_value=True):
        main()

    # Should run FastMCP server with working directory
    mock_start_server["fastmcp"].assert_called_once_with(host="0.0.0.0", port=8000, working_dir=".")


@pytest.mark.skip("Skipped because py_code.mcp_server has been removed")
def test_cli_mcp_server_explicit(mock_start_server):
    """Test CLI with explicit mcp server type."""
    # Simulate CLI call with server-type=mcp
    with patch.object(sys, "argv", ["py_code.cli", "--server-type", "mcp"]):
        main()

    # Should start the MCP server
    mock_start_server["mcp"].assert_called_once_with(host="0.0.0.0", port=8000)


def test_cli_custom_host_port(mock_start_server):
    """Test CLI with custom host and port."""
    # Simulate CLI call with custom host and port
    with (
        patch.object(sys, "argv", ["py_code.cli", "--host", "127.0.0.1", "--port", "9000", "--working-dir", "/tmp"]),
        patch("os.path.isdir", return_value=True),
    ):
        main()

    # Should run FastMCP server with custom host/port and working directory
    mock_start_server["fastmcp"].assert_called_once_with(host="127.0.0.1", port=9000, working_dir="/tmp")


def test_cli_keyboard_interrupt(mock_start_server):
    """Test CLI with KeyboardInterrupt."""
    # Make FastMCP server raise KeyboardInterrupt
    mock_start_server["fastmcp"].side_effect = KeyboardInterrupt()

    # Simulate CLI call with working directory
    with (
        patch.object(sys, "argv", ["py_code.cli", "--working-dir", "."]),
        patch("os.path.isdir", return_value=True),
        patch("sys.exit") as mock_exit,
    ):
        main()

    # Should call sys.exit(0)
    mock_exit.assert_called_once_with(0)
