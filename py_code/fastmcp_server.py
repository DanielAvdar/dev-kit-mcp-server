"""MCP Server implementation using FastMCP."""

from mcp.server.fastmcp import FastMCP  # type: ignore

from .tools.code_editing import CreateDirOperation, MoveDirOperation, RemoveFileOperation
from .tools.commands_tool import authorized_commands
from .tools.tool_factory import ToolFactory


def start_server() -> FastMCP:
    """Start the FastMCP server."""
    # Create a FastMCP instance

    root_dir = None  # todo: argparse the root_dir
    fastmcp = FastMCP(
        name="Python Code MCP Server",
        instructions="This server provides tools for file operations (create_dir_or_file, move_dir_or_file, "
        "remove_dir_or_file) and running authorized makefile commands.",
    )

    # Create a tool factory instance
    tool_factory = ToolFactory(fastmcp)
    tool_factory([
        MoveDirOperation(root_dir=root_dir),
        CreateDirOperation(root_dir=root_dir),
        RemoveFileOperation(root_dir=root_dir),
        authorized_commands,
    ])
    return fastmcp


def run_server():
    """Run the FastMCP server."""
    fastmcp = start_server()
    fastmcp.run()
