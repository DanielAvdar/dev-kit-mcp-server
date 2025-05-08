"""Tests for the code_editing.mcp_tools module."""

from py_code.tools.code_editing.mcp_tools import get_server_info
from py_code.version import __version__


def test_get_server_info():
    """Test the get_server_info function."""
    info = get_server_info()

    assert isinstance(info, dict)
    assert info["name"] == "Python Code MCP Server"
    assert info["version"] == __version__
    assert "description" in info
