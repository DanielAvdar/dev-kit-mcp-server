"""MCP Server implementation using FastMCP."""

import asyncio
import sys

from .create_server import start_server

# from mcp.server.fastmcp import FastMCP  # type: ignore
# from fastmcp import FastMCP
from .custom_fastmcp import RepoFastMCPServerError as FastMCP

# from importlib import import_module


def run_server(fastmcp: FastMCP = None) -> None:
    """Run the FastMCP server.

    Args:
        fastmcp: Optional FastMCP instance to run. If None, a new instance will be created.

    """
    fastmcp = fastmcp or start_server()
    try:
        fastmcp.run()
        sys.exit(0)
    except KeyboardInterrupt:
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


def arun_server(fastmcp: FastMCP = None) -> None:
    """Run the FastMCP server asynchronously.

    Args:
        fastmcp: Optional FastMCP instance to run. If None, a new instance will be created.

    """
    fastmcp = fastmcp or start_server()
    try:
        asyncio.run(fastmcp.run_async())
        sys.exit(0)
    except KeyboardInterrupt:
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
