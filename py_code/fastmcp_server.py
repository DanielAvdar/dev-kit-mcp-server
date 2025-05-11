"""MCP Server implementation using FastMCP."""

import argparse
import asyncio
import os
import sys
from pathlib import Path
from typing import Dict

# from mcp.server.fastmcp import FastMCP  # type: ignore
from fastmcp import FastMCP

from .tools import CreateDirOperation, MoveDirOperation, RemoveFileOperation
from .tools.commands_tool import ExecMakeTarget
from .tools.tool_factory import ToolFactory


def start_server(root_dir: str = None) -> FastMCP:
    """Start the FastMCP server.

    Args:
        root_dir: Root directory for file operations (default: current working directory)

    Returns:
        A FastMCP instance configured with file operation tools
    """
    # Parse command line arguments
    root_dir = root_dir or method_name()

    # Create a FastMCP instance
    fastmcp = FastMCP(
        name="Python Code MCP Server",
        instructions="This server provides tools for file operations (create_dir_or_file, move_dir_or_file, "
        "remove_dir_or_file) and running authorized makefile commands.",
    )

    def move_dir_tool(path1: str, path2: str) -> Dict[str, str]:
        """Tool to move directories or files.

        Args:
            path1: Source path
            path2: Destination path

        Returns:
            A dictionary containing the status and paths of the moved file or folder
        """
        return MoveDirOperation(root_dir=root_dir)(path1, path2)

    # move_dir_tool.name = "move_dir_tool"
    # move_dir_tool.__name__ = "move_dir_tool"
    # Create a tool factory instance
    # fastmcp.add_tool(move_dir_tool)
    tool_factory = ToolFactory(fastmcp)
    tool_factory([
        # move_dir_tool,
        MoveDirOperation(root_dir=root_dir),
        CreateDirOperation(root_dir=root_dir),
        RemoveFileOperation(root_dir=root_dir),
        ExecMakeTarget(root_dir=root_dir),
    ])
    return fastmcp


def method_name() -> str:
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
    return root_dir


def run_server(fastmcp: FastMCP = None) -> None:
    """Run the FastMCP server."""
    fastmcp = fastmcp or start_server()
    try:
        fastmcp.run()
        sys.exit(0)
    except KeyboardInterrupt:
        sys.exit(0)


def arun_server(fastmcp: FastMCP = None) -> None:
    """Run the FastMCP server."""
    fastmcp = fastmcp or start_server()
    try:
        asyncio.run(fastmcp.run_async())
        sys.exit(0)
    except KeyboardInterrupt:
        sys.exit(0)
