"""Tests for the command-line interface."""

from unittest.mock import MagicMock, patch

import pytest

from dev_kit_mcp_server.cli import main


@pytest.fixture
def mock_start_server():
    """Mock the server start functions."""
    with (
        patch("dev_kit_mcp_server.fastmcp_server.start_server") as mock_start,
        patch("dev_kit_mcp_server.cli.sys.exit") as mock_exit,
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

    @patch("sys.argv", ["dev_kit_mcp_server", "--root-dir", "."])
    def test_cli_with_root_dir(self, mock_start_server):
        """Test the CLI with root directory specified."""
        # Act
        main()

        # Assert
        mock_fastmcp = mock_start_server["fastmcp"]
        mock_fastmcp.run.assert_called_once()

    @patch("sys.argv", ["dev_kit_mcp_server"])
    def test_cli_with_defaults(self, mock_start_server):
        """Test the CLI with default values."""
        # Act
        main()

        # Assert
        mock_fastmcp = mock_start_server["fastmcp"]
        mock_fastmcp.run.assert_called_once()

    @patch("sys.argv", ["dev_kit_mcp_server", "--root-dir", "/nonexistent/directory"])
    def test_cli_with_nonexistent_root_dir(self, mock_start_server):
        """Test the CLI with a non-existent root directory."""
        # Arrange
        # Make sys.exit raise a custom exception that we can catch
        mock_start_server["exit"].side_effect = SystemExit

        with patch("os.path.isdir", return_value=False):
            # Act & Assert
            with pytest.raises(SystemExit):
                main()

            # The server should not be started if the root directory doesn't exist
            mock_start_server["start"].assert_not_called()

    @patch("sys.argv", ["dev_kit_mcp_server"])
    def test_cli_with_keyboard_interrupt(self, mock_start_server):
        """Test the CLI with a keyboard interrupt."""
        # Arrange
        mock_start_server["fastmcp"].run.side_effect = KeyboardInterrupt()

        # Act
        main()

        # Assert
        mock_start_server["exit"].assert_called_once_with(0)
