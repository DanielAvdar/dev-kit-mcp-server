"""Tests for the MCP server __main__ module."""

import sys
from unittest.mock import MagicMock, patch

import pytest

from py_code.mcp_server.__main__ import find_available_port, main


def test_find_available_port_success():
    """Test finding an available port successfully."""
    # Mock socket.socket to simulate an available port
    mock_socket = MagicMock()
    mock_socket.__enter__.return_value = mock_socket

    with patch("socket.socket", return_value=mock_socket):
        port = find_available_port(8000)
        assert port == 8000
        mock_socket.bind.assert_called_once_with(("127.0.0.1", 8000))


def test_find_available_port_retry():
    """Test finding an available port after retries."""
    # Mock socket.socket to simulate first port is in use, second is available
    mock_socket1 = MagicMock()
    mock_socket1.__enter__.return_value = mock_socket1
    mock_socket1.bind.side_effect = OSError("Address already in use")

    mock_socket2 = MagicMock()
    mock_socket2.__enter__.return_value = mock_socket2

    with patch("socket.socket", side_effect=[mock_socket1, mock_socket2]):
        port = find_available_port(8000, max_attempts=2)
        assert port == 8001
        mock_socket1.bind.assert_called_once_with(("127.0.0.1", 8000))
        mock_socket2.bind.assert_called_once_with(("127.0.0.1", 8001))


def test_find_available_port_failure():
    """Test failure to find an available port."""
    # Mock socket.socket to simulate all ports are in use
    mock_socket = MagicMock()
    mock_socket.__enter__.return_value = mock_socket
    mock_socket.bind.side_effect = OSError("Address already in use")

    with patch("socket.socket", return_value=mock_socket), pytest.raises(RuntimeError) as excinfo:
        find_available_port(8000, max_attempts=3)

    assert "Could not find an available port in range 8000-8002" in str(excinfo.value)
    assert mock_socket.bind.call_count == 3


@pytest.fixture
def mock_run_server():
    """Mock the integrated_server.run_server function."""
    with patch("py_code.integrated_server.run_server") as mock:
        yield mock


def test_main_default_args(mock_run_server):
    """Test main function with default arguments."""
    with patch.object(sys, "argv", ["py_code.mcp_server.__main__"]), patch("sys.exit"):
        main()

    mock_run_server.assert_called_once_with(host="0.0.0.0", port=8000)


def test_main_custom_host_port(mock_run_server):
    """Test main function with custom host and port."""
    with (
        patch.object(sys, "argv", ["py_code.mcp_server.__main__", "--host", "127.0.0.1", "--port", "9000"]),
        patch("sys.exit"),
    ):
        main()

    mock_run_server.assert_called_once_with(host="127.0.0.1", port=9000)


def test_main_auto_port(mock_run_server):
    """Test main function with auto-port option."""
    # Mock find_available_port to return a specific port
    with (
        patch.object(sys, "argv", ["py_code.mcp_server.__main__", "--auto-port"]),
        patch("py_code.mcp_server.__main__.find_available_port", return_value=8001),
        patch("sys.exit"),
        patch("builtins.print") as mock_print,
    ):
        main()

    mock_run_server.assert_called_once_with(host="0.0.0.0", port=8001)
    mock_print.assert_any_call("Port 8000 is in use, using port 8001 instead")


def test_main_auto_port_failure(mock_run_server):
    """Test main function with auto-port option when no ports are available."""
    # Mock find_available_port to raise RuntimeError
    with (
        patch.object(sys, "argv", ["py_code.mcp_server.__main__", "--auto-port"]),
        patch("py_code.mcp_server.__main__.find_available_port", side_effect=RuntimeError("No ports available")),
        patch("sys.exit") as mock_exit,
        patch("builtins.print") as mock_print,
    ):
        main()

    # The error is caught and sys.exit is called, but run_server is not prevented from being called
    # This matches the actual behavior of the code
    mock_print.assert_any_call("Error: No ports available")
    mock_exit.assert_called_once_with(1)


def test_main_port_in_use(mock_run_server):
    """Test main function when the port is already in use."""
    # Mock run_server to raise OSError for port in use
    error_msg = "address already in use"
    mock_run_server.side_effect = OSError(error_msg)

    with (
        patch.object(sys, "argv", ["py_code.mcp_server.__main__"]),
        patch("sys.exit") as mock_exit,
        patch("builtins.print") as mock_print,
    ):
        main()

    mock_print.assert_any_call(
        "Error: Port 8000 is already in use. Try with --auto-port option or specify a different port."
    )
    mock_exit.assert_called_once_with(1)


def test_main_other_error(mock_run_server):
    """Test main function when another error occurs."""
    # Mock run_server to raise a different OSError
    error_msg = "some other error"
    mock_run_server.side_effect = OSError(error_msg)

    with (
        patch.object(sys, "argv", ["py_code.mcp_server.__main__"]),
        patch("sys.exit") as mock_exit,
        patch("builtins.print") as mock_print,
    ):
        main()

    mock_print.assert_any_call(f"Error starting server: {error_msg}")
    mock_exit.assert_called_once_with(1)


def test_main_keyboard_interrupt(mock_run_server):
    """Test main function when KeyboardInterrupt occurs."""
    # Mock run_server to raise KeyboardInterrupt
    mock_run_server.side_effect = KeyboardInterrupt()

    with (
        patch.object(sys, "argv", ["py_code.mcp_server.__main__"]),
        patch("sys.exit") as mock_exit,
        patch("builtins.print") as mock_print,
    ):
        main()

    mock_print.assert_any_call("\nServer stopped")
    mock_exit.assert_called_once_with(0)
