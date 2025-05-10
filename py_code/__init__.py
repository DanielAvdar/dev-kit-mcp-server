"""Python Code MCP Server package."""

from importlib.metadata import version

from .fastmcp_server import start_server, run_server

__version__ = version("py-code-mcp-server")

__all__ = [ "run_server"]
