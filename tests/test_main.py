"""Tests for the __main__ module."""

from unittest.mock import MagicMock, patch

import pytest


# We need to patch argparse before importing the module
# to avoid issues with command-line arguments
@pytest.fixture
def mock_args():
    """Mock the command-line arguments."""
    mock_args = MagicMock()
    mock_args.root_dir = "/mock/root/dir"

    with patch("argparse.ArgumentParser.parse_args", return_value=mock_args):
        # Now we can safely import the module
        import py_code.__main__

        yield py_code.__main__


@pytest.fixture
def mock_fastmcp(mock_args):
    """Mock the FastMCP instance."""
    with patch("py_code.fastmcp_server.start_server") as mock_start:
        # Create a mock FastMCP instance
        mock_instance = MagicMock()
        mock_start.return_value = mock_instance

        # Reload the module to apply the mock
        import importlib

        import py_code.__main__

        importlib.reload(py_code.__main__)

        yield mock_instance


def test_main_module_creates_server(mock_fastmcp, mock_args):
    """Test that the __main__ module creates a server instance."""
    # The mock_fastmcp fixture already reloads the module, which creates the instance
    # Just verify that the instance exists and is the same as our mock
    import py_code.__main__

    assert py_code.__main__.fastmcp is mock_fastmcp
    assert py_code.__main__.mcp is mock_fastmcp


@patch("py_code.__main__.__name__", "__main__")
def test_main_module_runs_server_when_executed_directly(mock_fastmcp, mock_args):
    """Test that the __main__ module runs the server when executed directly."""
    # Reload the module with __name__ == "__main__" to trigger the run() call
    import importlib

    import py_code.__main__

    importlib.reload(py_code.__main__)

    # Verify that run() was called
    mock_fastmcp.run.assert_called_once()
