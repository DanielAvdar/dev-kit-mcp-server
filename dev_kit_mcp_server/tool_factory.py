"""Tool factory for dynamically decorating functions as MCP tools at runtime."""

from typing import Any, Callable, List, Sequence

from fastmcp.tools import Tool
from mcp.types import ToolAnnotations

from .core import AsyncOperation
from .custom_fastmcp import RepoFastMCPServerError, RepoTool

# RepoTool
# def exept_wrapper(fn: Callable[..., Any]):
#     """Wrapper to handle exceptions during function execution."""
#
#     def wrapper(*args, **kwargs):
#         try:
#             return fn(*args, **kwargs)
#         except Exception as e:
#             return dict(error=str(e))
#
#     return wrapper


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
        tool = self.create_tool(func)
        self.mcp.add_fast_tool(
            tool=tool,
        )

    def create_tool(self, func: AsyncOperation) -> Tool:
        """Create a Tool instance from an AsyncOperation.

        Args:
            func: The AsyncOperation instance to convert to a Tool

        Returns:
            A Tool instance configured with the operation's properties

        """
        description = f"Use instead of terminal:\n{func.docstring}"
        tool = RepoTool.from_function(
            fn=func.__call__,
            name=func.name,
            description=description,
            annotations=ToolAnnotations(
                destructiveHint=True,
            ),
        )

        return tool
