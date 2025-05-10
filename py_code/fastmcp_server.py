"""MCP Server implementation using FastMCP."""

from mcp.server.fastmcp import FastMCP  # type: ignore

from .tools.code_editing.file_operations import (
    delete_file_or_folder,
    move_file_or_folder,
    create_file_or_folder,
)
from .tools.commands_tool import authorized_commands
from .tools.tool_factory import ToolFactory


def start_server()-> FastMCP:
    """Start the FastMCP server."""
    # Create a FastMCP instance
    fastmcp = FastMCP(
        name="Python Code MCP Server",
        instructions="This server provides tools for file operations (create_dir_or_file, move_dir_or_file, "
        "remove_dir_or_file) and running authorized makefile commands.",
    )

    # Create a tool factory instance
    tool_factory = ToolFactory(fastmcp)
    tool_factory([
        create_file_or_folder,
        delete_file_or_folder,
        move_file_or_folder,
        authorized_commands,
    ])
    return fastmcp

def run_server():
    """Run the FastMCP server."""
    fastmcp = start_server()
    fastmcp.run()