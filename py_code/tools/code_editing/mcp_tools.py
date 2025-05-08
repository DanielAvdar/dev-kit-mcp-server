"""Implementation logic for MCP file and utility tools."""

from typing import Any, Dict

from ...version import __version__


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
