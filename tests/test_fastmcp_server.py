"""Tests for the FastMCP server implementation."""

from py_code.fastmcp_server import fastmcp


def test_mcp_server_tools():
    """Test that the FastMCP server has the expected tools."""
    # Check that the tools are registered with the MCP server
    # We can't directly access the tools, but we can check that the functions are defined
    from py_code.fastmcp_server import (
        authorized_commands,
        create_file_or_folder_tool,
        delete_file_or_folder_tool,
        move_file_or_folder_tool,
    )

    # Verify that the functions exist
    assert callable(create_file_or_folder_tool)
    assert callable(delete_file_or_folder_tool)
    assert callable(move_file_or_folder_tool)
    assert callable(authorized_commands)


def test_mcp_server_name_and_instructions():
    """Test that the FastMCP server has the expected name and instructions."""
    # Check server name
    assert fastmcp.name == "Python Code MCP Server"

    # Check server instructions
    assert "file operations" in fastmcp.instructions
    assert "create_dir_or_file" in fastmcp.instructions
    assert "move_dir_or_file" in fastmcp.instructions
    assert "remove_dir_or_file" in fastmcp.instructions
    assert "authorized makefile commands" in fastmcp.instructions
