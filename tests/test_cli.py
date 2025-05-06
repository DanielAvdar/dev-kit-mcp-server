"""Tests for the CLI module."""

import sys
from unittest.mock import patch

import pytest

from py_code.cli import main


@pytest.fixture
def mock_start_server():
    """Mock the server start functions."""
    with (
        patch("py_code.mcp_server.start_server") as mock_mcp,
    ):
        yield {"mcp": mock_mcp}


def test_cli_default_args(mock_start_server):
    """Test CLI with default arguments."""
    # Simulate CLI call with no arguments (uses defaults)
    with patch.object(sys, "argv", ["py_code.cli"]):
        main()

    # By default, should run MCP server on 0.0.0.0:8000
    mock_start_server["mcp"].assert_called_once_with(host="0.0.0.0", port=8000)


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
    with patch.object(sys, "argv", ["py_code.cli", "--host", "127.0.0.1", "--port", "9000"]):
        main()

    # Should run MCP server with custom host/port
    mock_start_server["mcp"].assert_called_once_with(host="127.0.0.1", port=9000)


def test_cli_keyboard_interrupt(mock_start_server):
    """Test CLI with KeyboardInterrupt."""
    # Make MCP server raise KeyboardInterrupt
    mock_start_server["mcp"].side_effect = KeyboardInterrupt()

    # Simulate CLI call
    with patch.object(sys, "argv", ["py_code.cli"]), patch("sys.exit") as mock_exit:
        main()

    # Should call sys.exit(0)
    mock_exit.assert_called_once_with(0)
