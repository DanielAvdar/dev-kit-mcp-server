"""Implementation logic for MCP file and utility tools."""

import os
from typing import Any, Dict

from ...version import __version__


def read_code_from_path(repo_root: str, file_path: str) -> str:
    """Read code from a file path.

    Args:
        repo_root: Path to the root of the repository
        file_path: Path to the file or package to analyze, relative to repo_root

    Returns:
        The code as a string

    Raises:
        Exception: If the file cannot be read

    """
    full_path = os.path.join(repo_root, file_path)

    if not os.path.exists(full_path):
        raise Exception(f"Path does not exist: {full_path}")

    if os.path.isfile(full_path):
        # Read a single file
        try:
            with open(full_path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            raise Exception(f"Error reading file {full_path}: {str(e)}") from e
    elif os.path.isdir(full_path):
        # For a directory, read all Python files and concatenate them
        code_parts = []
        for root, _, files in os.walk(full_path):
            for file in files:
                if file.endswith(".py"):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            code_parts.append(f"# File: {os.path.relpath(file_path, repo_root)}\n")
                            code_parts.append(f.read())
                            code_parts.append("\n\n")
                    except Exception as e:
                        raise Exception(f"Error reading file {file_path}: {str(e)}") from e
        return "".join(code_parts)
    else:
        raise Exception(f"Path is neither a file nor a directory: {full_path}")


def get_server_info() -> Dict[str, Any]:
    """Get information about the MCP repository navigation server.

    Returns:
        Server information including name, version, and repository navigation capabilities

    """
    return {
        "name": "Python Code MCP Server",
        "version": __version__,
        "description": "Model Context Protocol server for turning repositories into navigable MCP systems",
    }
