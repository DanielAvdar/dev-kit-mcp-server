"""MCP Server implementation using FastMCP."""

import argparse
import os
from pathlib import Path

from mcp.server.fastmcp import FastMCP  # type: ignore

from .tools.code_editing import CreateDirOperation, MoveDirOperation, RemoveFileOperation
from .tools.tool_factory import ToolFactory


def start_server() -> FastMCP:
    """Start the FastMCP server."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Start the FastMCP server")
    parser.add_argument(
        "--root-dir",
        type=str,
        default=os.getcwd(),
        help="Root directory for file operations (default: current working directory)",
    )
    args = parser.parse_args()

    # Validate root directory
    root_dir = args.root_dir
    root_path = Path(root_dir)
    if not root_path.exists():
        raise ValueError(f"Root directory does not exist: {root_dir}")
    if not root_path.is_dir():
        raise ValueError(f"Root directory is not a directory: {root_dir}")

    # Create a FastMCP instance
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
        # authorized_commands,
    ])
    return fastmcp


def run_server():
    """Run the FastMCP server."""
    fastmcp = start_server()
    fastmcp.run()
