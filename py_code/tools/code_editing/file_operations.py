"""Tools for file and folder operations like moving and deleting."""

import os
import shutil
from typing import Any, Dict, Optional

from fastmcp import Context

from ..utils import normalize_path


def move_file_or_folder(source_path: str, destination_path: str, ctx: Optional[Context] = None) -> Dict[str, Any]:
    """Move a file or folder to a new location within the workspace.

    Args:
        source_path: The path to the file or folder to move
        destination_path: The destination path where the file or folder will be moved
        ctx: Optional MCP context

    Returns:
        Dictionary containing the result of the operation

    """
    if ctx:
        ctx.info(f"Moving from {source_path} to {destination_path}")

    # Normalize paths and handle both absolute and relative paths
    workspace_root = os.getcwd()

    if not os.path.isabs(source_path):
        source_path = os.path.join(workspace_root, source_path)

    if not os.path.isabs(destination_path):
        destination_path = os.path.join(workspace_root, destination_path)

    source_path = normalize_path(source_path)
    destination_path = normalize_path(destination_path)

    # Verify source exists
    if not os.path.exists(source_path):
        return {
            "error": f"Source path not found: {source_path}",
            "source": source_path,
            "destination": destination_path,
        }

    # Verify destination parent directory exists
    destination_dir = os.path.dirname(destination_path)
    if not os.path.exists(destination_dir):
        return {
            "error": f"Destination directory not found: {destination_dir}",
            "source": source_path,
            "destination": destination_path,
        }

    # Check if destination already exists
    if os.path.exists(destination_path):
        return {
            "error": f"Destination already exists: {destination_path}",
            "source": source_path,
            "destination": destination_path,
        }

    try:
        # Move the file or directory
        shutil.move(source_path, destination_path)

        return {
            "success": True,
            "source": source_path,
            "destination": destination_path,
            "type": "directory" if os.path.isdir(destination_path) else "file",
        }
    except Exception as e:
        return {
            "error": f"Error moving file or folder: {str(e)}",
            "source": source_path,
            "destination": destination_path,
        }


def delete_file(file_path: str, ctx: Optional[Context] = None) -> Dict[str, Any]:
    """Delete a file from the workspace.

    Args:
        file_path: The path to the file to delete
        ctx: Optional MCP context

    Returns:
        Dictionary containing the result of the operation

    """
    if ctx:
        ctx.info(f"Deleting file: {file_path}")

    # Normalize path and handle both absolute and relative paths
    if not os.path.isabs(file_path):
        workspace_root = os.getcwd()
        file_path = os.path.join(workspace_root, file_path)

    file_path = normalize_path(file_path)

    # Verify file exists
    if not os.path.exists(file_path):
        return {"error": f"File not found: {file_path}", "path": file_path}

    # Verify it's a file, not a directory
    if os.path.isdir(file_path):
        return {
            "error": f"Cannot delete directory with this function, path is a directory: {file_path}",
            "path": file_path,
        }

    try:
        # Delete the file
        os.remove(file_path)

        return {"success": True, "path": file_path}
    except Exception as e:
        return {"error": f"Error deleting file: {str(e)}", "path": file_path}
