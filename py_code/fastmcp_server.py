"""MCP Server implementation using FastMCP."""

import os
import subprocess
from typing import Any, Dict, List, Optional

from mcp.server.fastmcp import Context, FastMCP  # type: ignore

from .tools.code_editing.file_operations import (
    create_file_or_folder,
    delete_file_or_folder,
    move_file_or_folder,
)
from .tools.tool_factory import ToolFactory

# Create the FastMCP server
fastmcp = FastMCP(
    name="Python Code MCP Server",
    instructions="This server provides tools for file operations (create_dir_or_file, move_dir_or_file, "
    "remove_dir_or_file) and running authorized makefile commands.",
)

# Create a tool factory instance
tool_factory = ToolFactory(fastmcp)


# Create named wrappers for functions that we want to expose with specific names


@fastmcp.tool(name="move_file_or_folder")
def move_file_or_folder_tool(source_path: str, destination_path: str, ctx: Optional[Context] = None) -> Dict[str, Any]:
    """Move a file or folder to a new location within the workspace.

    Args:
        source_path: The path to the file or folder to move
        destination_path: The destination path where the file or folder will be moved
        ctx: Optional context for logging

    Returns:
        A dictionary containing the result of the operation

    """
    return move_file_or_folder(source_path, destination_path, ctx)


@fastmcp.tool(name="delete_file_or_folder")
def delete_file_or_folder_tool(path: str, ctx: Optional[Context] = None) -> Dict[str, Any]:
    """Delete a file or folder from the workspace.

    Args:
        path: The path to the file or folder to delete
        ctx: Optional context for logging

    Returns:
        A dictionary containing the result of the operation

    """
    return delete_file_or_folder(path, ctx)


@fastmcp.tool(name="create_file_or_folder")
def create_file_or_folder_tool(
    path: str, content: Optional[str] = None, ctx: Optional[Context] = None
) -> Dict[str, Any]:
    """Create a file or folder in the workspace.

    Args:
        path: The path to the file or folder to create
        content: Optional content for the file (if None and path has no extension, a folder is created)
        ctx: Optional context for logging

    Returns:
        A dictionary containing the result of the operation

    """
    return create_file_or_folder(path, content, ctx)


@fastmcp.tool(name="authorized_commands")
def authorized_commands(
    commands: List[str], makefile_dir: Optional[str] = None, ctx: Optional[Context] = None
) -> Dict[str, Any]:
    """Run authorized makefile commands.

    Args:
        commands: List of makefile commands to run (e.g. ["test", "lint"])
        makefile_dir: Optional directory containing the Makefile (defaults to current working directory)
        ctx: Optional context for logging

    Returns:
        A dictionary containing the command output and status

    """
    if ctx:
        ctx.info(f"Running makefile commands: {commands}")

    # Set default makefile directory if not provided
    workspace_root = os.getcwd()
    if makefile_dir is None:
        makefile_dir = workspace_root
    elif not os.path.isabs(makefile_dir):
        makefile_dir = os.path.join(workspace_root, makefile_dir)

    # Normalize path
    makefile_dir = os.path.normpath(makefile_dir)

    # Verify makefile directory is within the working directory
    if not makefile_dir.startswith(workspace_root):
        return {
            "error": f"Makefile directory must be within the working directory: {makefile_dir}",
            "commands": commands,
            "makefile_dir": makefile_dir,
        }

    # Validate makefile exists
    makefile_path = os.path.join(makefile_dir, "Makefile")
    if not os.path.exists(makefile_path):
        return {
            "error": f"Makefile not found at {makefile_path}",
            "commands": commands,
            "makefile_dir": makefile_dir,
        }

    # Construct the make command
    make_cmd = ["make", "-C", makefile_dir] + commands

    try:
        # Run the command and capture output
        result = subprocess.run(
            make_cmd,
            capture_output=True,
            text=True,
            check=False,  # Don't raise an exception on non-zero exit code
        )

        return {
            "success": result.returncode == 0,
            "commands": commands,
            "makefile_dir": makefile_dir,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode,
        }
    except Exception as e:
        return {
            "error": f"Error running makefile commands: {str(e)}",
            "commands": commands,
            "makefile_dir": makefile_dir,
        }


def start_server(host: str = "0.0.0.0", port: int = 8000, working_dir: Optional[str] = None) -> None:
    """Start the MCP server with the specified transport.

    Args:
        host: Host to bind the server to
        port: Port to bind the server to
        working_dir: Optional working directory for the server

    """
    # Change to the working directory if specified
    if working_dir:
        os.chdir(working_dir)

    fastmcp.run(transport="sse", host=host, port=port)


if __name__ == "__main__":
    # This allows running the module directly
    start_server(host="127.0.0.1", port=9090)
