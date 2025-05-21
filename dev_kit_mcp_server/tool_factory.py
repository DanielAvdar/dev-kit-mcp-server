"""Tool factory for dynamically decorating functions as MCP tools at runtime."""

from importlib import import_module
from pathlib import Path
from typing import Any, Callable, List

import tomllib
from fastmcp.tools import Tool
from fastmcp.utilities.logging import get_logger
from mcp.types import ToolAnnotations

from .core import AsyncOperation
from .custom_fastmcp import RepoFastMCPServerError, RepoTool

logger = get_logger(__name__)


class ToolFactory:
    """Factory for creating MCP tools at runtime by decorating functions.

    This factory allows for dynamically decorating functions with the MCP tool
    decorator, optionally adding behavior before and after the function execution.
    """

    factory_section = "factory"

    def __init__(self, mcp_instance: RepoFastMCPServerError):
        """Initialize the tool factory with an MCP instance.

        Args:
            mcp_instance: The FastMCP instance to use for decorating functions

        """
        self.mcp = mcp_instance
        self._pre_hooks: List[Callable[..., Any]] = []
        self._post_hooks: List[Callable[..., Any]] = []

    def __call__(self, obj: List[str], root_dir: str, commands_toml: str) -> None:
        """Make the factory callable to directly decorate functions, lists of functions, or classes.

        Args:
            obj: Sequence of AsyncOperation instances (FileOperation or AsyncOperation) to decorate
            root_dir: The root directory for file operations
            commands_toml: Path to TOML configuration file relative to root_dir

        """
        conf = self.get_configuration(root_dir, commands_toml)
        include = conf.get("include", [])
        exclude = conf.get("exclude", [])

        for module_str in obj:
            module = import_module(module_str)
            for func_name in module.__all__:
                # Check if the function is callable
                op = getattr(module, func_name)
                if include and op.name not in include:
                    continue
                if exclude and op.name in exclude:
                    continue

                func = op(root_dir=root_dir)
                self._decorate_function(func)
        logger.info(f"Staged server in local directory: {root_dir}")

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

    def get_configuration(self, root_dir: str, commands_toml: str) -> dict[str, Any]:
        """Get the configuration for the tool factory.

        Args:
            root_dir: The root directory for file operations
            commands_toml: Path to TOML configuration file relative to root_dir

        Returns:
            Dictionary containing factory configuration options

        """
        root_path = Path(root_dir)

        if commands_toml and (root_path / commands_toml).exists():
            path = root_path / commands_toml
        elif (root_path / "pyproject.toml").exists():
            path = root_path / "pyproject.toml"
        else:
            return {}

        try:
            with open(path, "rb") as f:
                toml_data = tomllib.load(f)
            commands = toml_data.get("tool", {}).get("dkmcp", {}).get("factory", {})
            if commands:
                return commands
            return {}

        except Exception as e:
            logger.warning("{" + f"Failed to load configuration from {path}: {e}" + "}")
            return {}
