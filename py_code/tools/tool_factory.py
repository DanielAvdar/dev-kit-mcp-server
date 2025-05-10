"""Tool factory for dynamically decorating functions as MCP tools at runtime."""

from typing import Any, Callable, List

from mcp.server.fastmcp import FastMCP  # type: ignore


class ToolFactory:
    """Factory for creating MCP tools at runtime by decorating functions.

    This factory allows for dynamically decorating functions with the MCP tool
    decorator, optionally adding behavior before and after the function execution.
    """

    def __init__(self, mcp_instance: FastMCP):
        """Initialize the tool factory with an MCP instance.

        Args:
            mcp_instance: The FastMCP instance to use for decorating functions

        """
        self.mcp = mcp_instance
        self._pre_hooks: List[Callable[..., Any]] = []
        self._post_hooks: List[Callable[..., Any]] = []

    def __call__(self, obj: List[Callable]) -> None:
        """Make the factory callable to directly decorate functions, lists of functions, or classes.

        Args:
            obj: Function, list of functions, or class to decorate

        Returns:
            Decorated function, list of decorated functions, or class with decorated methods

        """
        [self._decorate_function(func) for func in obj]

    def _decorate_function(self, func: Callable) -> None:
        """Decorate a function with MCP tool decorator and hooks.

        Args:
            func: Function to decorate

        """
        self.mcp.tool(
            func.__name__,
            description=func.__doc__ or "No description provided",
        )(func)
