"""Custom FastMCP and Tool classes with extended functionality for repository operations."""

from typing import Any

from fastmcp import FastMCP
from fastmcp.tools import Tool
from fastmcp.tools.tool import ToolResult
from mcp.types import TextContent


class RepoTool(Tool):
    """Custom tool class for RepoTool."""

    async def run(self, arguments: dict[str, Any]) -> ToolResult:
        """Run the tool with arguments.

        Args:
            arguments: Dictionary of arguments to pass to the tool

        Returns:
            A ToolResult containing the tool's output or error message

        """
        try:
            # Call the original run method
            result = await super().run(arguments)
            return result
        except Exception as e:
            # Handle exceptions and return an error message
            return ToolResult(content=[TextContent(text=f"Error: {str(e)}", type="text")])


class RepoFastMCPServerError(FastMCP):
    """Extended FastMCP class with additional tool management functionality."""

    def add_fast_tool(self, tool: Tool) -> None:
        """Add a tool to the server."""
        self._tool_manager.add_tool(tool)
