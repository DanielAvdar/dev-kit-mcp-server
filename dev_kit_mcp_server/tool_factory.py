"""Tool factory for dynamically decorating functions as MCP tools at runtime."""

from typing import Any, Callable, List, Sequence

from fastmcp import FastMCP
from fastmcp.tools import Tool
from mcp.types import ToolAnnotations

from .tools.core import AsyncOperation


class RepoFastMCPServerError(FastMCP):
    """Extended FastMCP class with additional tool management functionality."""

    def add_fast_tool(self, tool: Tool) -> None:
        """Add a tool to the server."""
        self._tool_manager.add_tool(tool)


class ToolFactory:
    """Factory for creating MCP tools at runtime by decorating functions.

    This factory allows for dynamically decorating functions with the MCP tool
    decorator, optionally adding behavior before and after the function execution.
    """

    def __init__(self, mcp_instance: RepoFastMCPServerError):
        """Initialize the tool factory with an MCP instance.

        Args:
            mcp_instance: The FastMCP instance to use for decorating functions

        """
        self.mcp = mcp_instance
        self._pre_hooks: List[Callable[..., Any]] = []
        self._post_hooks: List[Callable[..., Any]] = []

    def __call__(self, obj: Sequence[AsyncOperation]) -> None:
        """Make the factory callable to directly decorate functions, lists of functions, or classes.

        Args:
            obj: Sequence of AsyncOperation instances (FileOperation or AsyncOperation) to decorate

        """
        for func in obj:
            self._decorate_function(func)

    def _decorate_function(self, func: AsyncOperation) -> None:
        """Decorate a function with MCP tool decorator and hooks.

        Args:
            func: AsyncOperation instance (FileOperation or AsyncOperation) to decorate

        """
        # Get the wrapper function from the operation
        # Set the name attribute for compatibility with FastMCP
        description = f"Use instead of terminal:\n{func.docstring}"
        tool = Tool.from_function(
            fn=func.__call__,
            name=func.name,
            description=description,
            annotations=ToolAnnotations(
                destructiveHint=True,
            ),
        )
        self.mcp.add_fast_tool(
            tool=tool,
        )
