"""Tests for the command-line interface."""

from unittest.mock import MagicMock, patch

import pytest

from py_code.cli import main


@pytest.fixture
def mock_start_server():
    """Mock the server start functions."""
    with (
        patch("py_code.cli.start_server") as mock_start,
        patch("py_code.cli.sys.exit") as mock_exit,
    ):
        # Create a mock FastMCP instance
        mock_fastmcp = MagicMock()
        mock_start.return_value = mock_fastmcp

        yield {
            "start": mock_start,
            "exit": mock_exit,
            "fastmcp": mock_fastmcp,
        }


class TestCLI:
    """Tests for the command-line interface."""

    @patch("sys.argv", ["py_code", "--host", "127.0.0.1", "--port", "9000"])
    def test_cli_with_custom_host_and_port(self, mock_start_server):
        """Test the CLI with custom host and port."""
        # Act
        main()

        # Assert
        mock_fastmcp = mock_start_server["fastmcp"]
        assert mock_fastmcp.host == "127.0.0.1"
        assert mock_fastmcp.port == 9000
        mock_fastmcp.run.assert_called_once()

    @patch("sys.argv", ["py_code"])
    def test_cli_with_defaults(self, mock_start_server):
        """Test the CLI with default values."""
        # Act
        main()

        # Assert
        mock_fastmcp = mock_start_server["fastmcp"]
        assert mock_fastmcp.host == "0.0.0.0"
        assert mock_fastmcp.port == 8000
        mock_fastmcp.run.assert_called_once()

    @patch("sys.argv", ["py_code", "--root-dir", "/nonexistent/directory"])
    def test_cli_with_nonexistent_root_dir(self, mock_start_server):
        """Test the CLI with a non-existent root directory."""
        # Arrange
        with patch("os.path.isdir", return_value=False):
            # Act
            main()

            # Assert
            mock_start_server["exit"].assert_called_once_with(1)
            mock_start_server["fastmcp"].run.assert_not_called()

    @patch("sys.argv", ["py_code"])
    def test_cli_with_keyboard_interrupt(self, mock_start_server):
        """Test the CLI with a keyboard interrupt."""
        # Arrange
        mock_start_server["fastmcp"].run.side_effect = KeyboardInterrupt()

        # Act
        main()

        # Assert
        mock_start_server["exit"].assert_called_once_with(0)
