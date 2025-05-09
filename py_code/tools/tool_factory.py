"""Tool factory for dynamically decorating functions as MCP tools at runtime."""

import functools
import inspect
from typing import Any, Callable, List, TypeVar, Union, cast

from mcp.server.fastmcp import FastMCP  # type: ignore

F = TypeVar("F", bound=Callable[..., Any])


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

    def __call__(self, obj: Union[Callable[..., Any], List[Callable[..., Any]], type]) -> Any:
        """Make the factory callable to directly decorate functions, lists of functions, or classes.

        Args:
            obj: Function, list of functions, or class to decorate

        Returns:
            Decorated function, list of decorated functions, or class with decorated methods

        """
        if isinstance(obj, list):
            # Handle list of functions
            return [self._decorate_function(func) for func in obj]
        elif inspect.isclass(obj):
            # Handle class (decorate all methods)
            self.decorate_methods(obj)
            return obj
        else:
            # Handle single function
            return self._decorate_function(obj)

    def add_pre_hook(self, hook: Callable[..., Any]) -> None:
        """Add a hook to run before the decorated function.

        Args:
            hook: A function to call before the decorated function

        """
        self._pre_hooks.append(hook)

    def add_post_hook(self, hook: Callable[..., Any]) -> None:
        """Add a hook to run after the decorated function.

        Args:
            hook: A function to call after the decorated function

        """
        self._post_hooks.append(hook)

    def _decorate_function(self, func: F) -> F:
        """Decorate a function with MCP tool decorator and hooks.

        Args:
            func: Function to decorate

        Returns:
            Decorated function as an MCP tool

        """

        # Keep the original signature and documentation
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Run pre-execution hooks
            for hook in self._pre_hooks:
                hook_result = hook(*args, **kwargs)
                # If a hook returns a value, we can use it to modify args or kwargs
                if isinstance(hook_result, dict):
                    kwargs.update(hook_result)

            # Call the original function
            result = func(*args, **kwargs)

            # Run post-execution hooks
            for hook in self._post_hooks:
                hook_result = hook(result, *args, **kwargs)
                # If a hook returns a value, it replaces the result
                if hook_result is not None:
                    result = hook_result

            return result

        # Apply the MCP tool decorator
        decorated_func = self.mcp.tool()(wrapper)

        # Cast to maintain the original type for type checking
        return cast(F, decorated_func)

    def decorate_methods(self, cls: Any) -> None:
        """Decorate all public methods of a class as MCP tools.

        Args:
            cls: Class whose methods should be decorated

        """
        for name, method in inspect.getmembers(cls, inspect.isfunction):
            # Skip private and protected methods
            if name.startswith("_"):
                continue

            # Decorate the method and replace it on the class
            setattr(cls, name, self._decorate_function(method))
