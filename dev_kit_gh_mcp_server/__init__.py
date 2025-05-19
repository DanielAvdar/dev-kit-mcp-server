"""Dev-Kit MCP Server package."""

from importlib.metadata import version

from .fastmcp_server import arun_server, run_server, start_server

__version__ = version("dev-kit-mcp-server")

__all__ = ["run_server", "start_server", "arun_server"]
