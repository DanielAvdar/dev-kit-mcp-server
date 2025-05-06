"""MCP Server Python implementation."""  # Updated package description

from importlib.metadata import version

from py_code_mcp_server.analyzer import CodeAnalyzer
from py_code_mcp_server.fastmcp_server import mcp as fastmcp, start_server as start_fastmcp_server
from py_code_mcp_server.integrated_server import app as integrated_app, run_server as start_integrated_server
from py_code_mcp_server.server import app as fastapi_app, start_server as start_fastapi_server

__version__ = version("py-code-mcp-server")  # Updated package name

__all__ = [
    "CodeAnalyzer",
    "fastapi_app",
    "start_fastapi_server",
    "fastmcp",
    "start_fastmcp_server",
    "integrated_app",
    "start_integrated_server",
]
