"""Tests for the CLI module."""

import sys
from unittest.mock import patch

import pytest

from py_code.cli import main


@pytest.fixture
def mock_start_server():
    """Mock the server start functions."""
    with (
        patch("py_code.server.start_server") as mock_fastapi,
        patch("py_code.fastmcp_server.start_server") as mock_fastmcp,
        patch("py_code.integrated_server.run_server") as mock_integrated,
    ):
        yield {"fastapi": mock_fastapi, "fastmcp": mock_fastmcp, "integrated": mock_integrated}


def test_cli_default_args(mock_start_server):
    """Test CLI with default arguments."""
    # Simulate CLI call with no arguments (uses defaults)
    with patch.object(sys, "argv", ["py_code.cli"]):
        main()

    # By default, should run integrated server on 0.0.0.0:8000
    mock_start_server["integrated"].assert_called_once_with(host="0.0.0.0", port=8000)
    mock_start_server["fastapi"].assert_not_called()
    mock_start_server["fastmcp"].assert_not_called()


def test_cli_fastapi_server(mock_start_server):
    """Test CLI with fastapi server type."""
    # Simulate CLI call with server-type=fastapi
    with patch.object(sys, "argv", ["py_code.cli", "--server-type", "fastapi"]):
        main()

    # Should start the FastAPI server
    mock_start_server["fastapi"].assert_called_once_with(host="0.0.0.0", port=8000)
    mock_start_server["integrated"].assert_not_called()
    mock_start_server["fastmcp"].assert_not_called()


def test_cli_fastmcp_server(mock_start_server):
    """Test CLI with fastmcp server type."""
    # Simulate CLI call with server-type=fastmcp
    with patch.object(sys, "argv", ["py_code.cli", "--server-type", "fastmcp"]):
        main()

    # Should start the FastMCP server
    mock_start_server["fastmcp"].assert_called_once_with(host="0.0.0.0", port=8000)
    mock_start_server["integrated"].assert_not_called()
    mock_start_server["fastapi"].assert_not_called()


def test_cli_custom_host_port(mock_start_server):
    """Test CLI with custom host and port."""
    # Simulate CLI call with custom host and port
    with patch.object(sys, "argv", ["py_code.cli", "--host", "127.0.0.1", "--port", "9000"]):
        main()

    # Should run integrated server with custom host/port
    mock_start_server["integrated"].assert_called_once_with(host="127.0.0.1", port=9000)


def test_cli_keyboard_interrupt(mock_start_server):
    """Test CLI with KeyboardInterrupt."""
    # Make integrated_server.run_server raise KeyboardInterrupt
    mock_start_server["integrated"].side_effect = KeyboardInterrupt()

    # Simulate CLI call
    with patch.object(sys, "argv", ["py_code.cli"]), patch("sys.exit") as mock_exit:
        main()

    # Should call sys.exit(0)
    mock_exit.assert_called_once_with(0)
