"""Tool factory for dynamically decorating functions as MCP tools at runtime."""

from typing import Any, Callable, List

from fastmcp import FastMCP
from mcp.types import ToolAnnotations

from .tools.core import _Operation


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

    def __call__(self, obj: List[_Operation]) -> None:
        """Make the factory callable to directly decorate functions, lists of functions, or classes.

        Args:
            obj: List of _Operation instances (FileOperation or AsyncOperation) to decorate

        """
        for func in obj:
            self._decorate_function(func)

    def _decorate_function(self, func: _Operation) -> None:
        """Decorate a function with MCP tool decorator and hooks.

        Args:
            func: _Operation instance (FileOperation or AsyncOperation) to decorate

        """
        # Get the wrapper function from the operation
        wrapper = func.self_warpper()
        # Set the name attribute for compatibility with FastMCP
        wrapper.__name__ = func.name
        description = f"Preferred from the terminal:\n{func.docstring}"
        self.mcp.tool(
            func.name,
            description=description,
            annotations=ToolAnnotations(
                destructiveHint=True,
            ),
        )(wrapper)
